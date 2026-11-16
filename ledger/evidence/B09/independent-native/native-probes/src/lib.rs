#[cfg(test)]
mod tests {
    use nativeweave_data_contracts::{Codec, Model, Profile, Projection, wire::{Batch, Descriptor, Expectation}};
    use nativeweave_query_binding::*;
    use std::sync::Arc;
    type Field = (u16, u16, Vec<u8>);
    fn u32f(id:u16, value:u32) -> Field { (id, 1, value.to_le_bytes().to_vec()) }
    fn u64f(id:u16, value:u64) -> Field { (id, 2, value.to_le_bytes().to_vec()) }
    fn text(id:u16, value:&str) -> Field { (id, 4, value.as_bytes().to_vec()) }
    fn blob(id:u16, value:Vec<u8>) -> Field { (id, 5, value) }
    fn record(kind:u16, fields:Vec<Field>) -> Vec<u8> {
        let start=16+16*fields.len();
        let mut bytes=vec![0;start+fields.iter().map(|f|f.2.len()).sum::<usize>()];
        bytes[0..2].copy_from_slice(&1u16.to_le_bytes());
        bytes[2..4].copy_from_slice(&kind.to_le_bytes());
        let length=bytes.len() as u32;
        bytes[4..8].copy_from_slice(&length.to_le_bytes());
        bytes[8..12].copy_from_slice(&(fields.len() as u32).to_le_bytes());
        let mut cursor=start;
        for (i,(id,ty,data)) in fields.into_iter().enumerate() {
            let at=16+i*16;
            bytes[at..at+2].copy_from_slice(&id.to_le_bytes());
            bytes[at+2..at+4].copy_from_slice(&ty.to_le_bytes());
            bytes[at+4..at+8].copy_from_slice(&(data.len() as u32).to_le_bytes());
            bytes[at+8..at+16].copy_from_slice(&(cursor as u64).to_le_bytes());
            bytes[cursor..cursor+data.len()].copy_from_slice(&data);
            cursor+=data.len();
        }
        bytes
    }
    fn sequence(records:Vec<Vec<u8>>) -> Vec<u8> {
        let mut bytes=(records.len() as u32).to_le_bytes().to_vec();
        for item in records { bytes.extend_from_slice(&(item.len() as u32).to_le_bytes()); bytes.extend(item); }
        bytes
    }
    struct Context { parent:ModelBinding, child:ModelBinding, registry:Arc<ParameterRegistry> }
    impl Context {
        fn new() -> Self {
            let source=SourceIdentity {engine:72,source:5,generation:1,profile:Profile::PostgreSql};
            let codecs=Arc::new(CodecBindings::new(source.profile,&[]).unwrap());
            let parent=ModelBinding::new(source,Arc::new(Model::parse(include_bytes!("../fixtures/parent-model.json"),source.profile).unwrap()),codecs.clone()).unwrap();
            let child=ModelBinding::new(source,Arc::new(Model::parse(include_bytes!("../fixtures/child-model.json"),source.profile).unwrap()),codecs).unwrap();
            Self { parent, child, registry:Arc::new(ParameterRegistry::new(source,4096).unwrap()) }
        }
        fn query(&self) -> QueryArena {
            QueryArena::new(self.parent.clone(),self.registry.clone(),self.parent.model.table_id(),Limits::default(),Capabilities::from_mask((1u64<<25)-1,self.parent.source.profile).unwrap(),1_000_000).unwrap()
        }
        fn restricted(&self, absent_bit:u32) -> QueryArena {
            let caps=Capabilities::from_mask(((1u64<<25)-1)&!(1u64<<absent_bit),self.parent.source.profile).unwrap();
            QueryArena::new(self.parent.clone(),self.registry.clone(),self.parent.model.table_id(),Limits::default(),caps,1_000_000).unwrap()
        }
        fn select(&self,q:&mut QueryArena) {
            let mut values=Vec::new();
            for name in ["Id","Name"] {
                let id=self.parent.model.columns().iter().find(|c|c.name==name).unwrap().id;
                values.extend_from_slice(&q.column(0,id).unwrap().to_le_bytes());
            }
            q.clause(6,&record(6,vec![(1,8,values),blob(2,include_bytes!("../fixtures/parent-projection.bin").to_vec())])).unwrap();
        }
        fn id(model:&ModelBinding) -> u32 { model.model.columns().iter().find(|c|c.name=="Id").unwrap().id }
    }
    #[test]
    fn case_inside_reserved_on_and_transitive_invalidation() {
        let c=Context::new(); let mut q=c.query();
        let left=q.column(0,Context::id(&c.parent)).unwrap();
        let model=q.import_model(c.child.clone()).unwrap();
        let alias=q.clause(18,&record(6,vec![u64f(1,model),u32f(2,c.child.model.table_id()),text(3,"child_alias"),u32f(4,1)])).unwrap();
        let right=q.column(alias,Context::id(&c.child)).unwrap();
        let equal=q.binary(1,left,right).unwrap();
        let nested=q.clause(15,&record(6,vec![u64f(1,equal),u64f(2,right),u64f(3,right)])).unwrap();
        let on=q.binary(1,left,nested).unwrap();
        assert_eq!(q.clause(7,&record(6,vec![u64f(1,alias),u64f(2,on)])).unwrap(),alias);
        for stale in [right,equal,nested,on] { assert!(q.expression_type(stale).is_err()); }
        let fresh=q.column(alias,Context::id(&c.child)).unwrap();
        assert!(q.expression_type(fresh).unwrap().codec.nullable);
    }
    #[test]
    fn matching_profile_aggregate_list_cannot_enter_where() {
        let c=Context::new(); let mut q=c.query();
        let value=q.column(0,Context::id(&c.parent)).unwrap();
        let sum=q.clause(13,&record(6,vec![u32f(1,2),u64f(2,value),u32f(3,0),u32f(5,3)])).unwrap();
        let expected=Expectation {kind:3,profile:c.parent.source.profile,hash:[0;32],entity_id:0,projection_id:0,descriptors:vec![Descriptor {id:1,codec:Codec{id:3,configuration:None,nullable:false},bound_codec:3}],exact_rows:Some(1)};
        let cell=9i64.to_le_bytes(); let wire=Batch::encode(&expected,1,&[Some(&cell)]).unwrap();
        let predicate=q.list(1,sum,&wire).unwrap();
        assert!(q.expression_type(predicate).unwrap().aggregate);
        let before=q.counts();
        assert_eq!(q.clause(1,&record(6,vec![u64f(1,predicate)])).unwrap_err().status,3);
        assert_eq!(q.counts(),before);
    }
    #[test]
    fn scalar_sentinel_only_registered_single_field_not_inline_query() {
        let c=Context::new();
        let canonical=br#"{"version":1,"fields":[{"ordinal":0,"name":"","codec":3,"codec_config":null,"nullable":false}]}"#;
        let projection=Projection::parse_scalar(canonical,c.parent.source.profile).unwrap();
        let field=record(22,vec![u32f(1,0),text(2,""),u32f(3,3),u32f(4,0)]);
        let shape=record(13,vec![blob(1,sequence(vec![field.clone()])),blob(2,projection.hash().to_vec())]);
        assert!(projection_record(&shape,c.parent.source,9,c.parent.codecs.clone(),None).is_ok());
        assert!(projection_record(&shape,c.parent.source,9,c.parent.codecs.clone(),Some(&[1])).is_err());
        let second=record(22,vec![u32f(1,1),text(2,"Id"),u32f(3,3),u32f(4,0)]);
        let malformed=record(13,vec![blob(1,sequence(vec![field,second])),blob(2,projection.hash().to_vec())]);
        assert!(projection_record(&malformed,c.parent.source,9,c.parent.codecs.clone(),None).is_err());
    }
    #[test]
    fn exact_missing_capability_guards_before_publication() {
        let c=Context::new();
        assert!(Capabilities::from_mask(1u64<<25,c.parent.source.profile).is_err());
        assert!(!Capabilities::from_mask(1u64<<11,Profile::Sqlite).unwrap().row_lock);
        for bit in [0,1,23] {
            let caps=Capabilities::from_mask(((1u64<<25)-1)&!(1u64<<bit),c.parent.source.profile).unwrap();
            assert_eq!(QueryArena::new(c.parent.clone(),c.registry.clone(),c.parent.model.table_id(),Limits::default(),caps,1_000_000).err().unwrap().status,6);
        }
        let mut no_join=c.restricted(17);
        let imported=no_join.import_model(c.child.clone()).unwrap();
        let before=no_join.counts();
        assert_eq!(no_join.clause(18,&record(6,vec![u64f(1,imported),u32f(2,c.child.model.table_id()),text(3,"j"),u32f(4,0)])).unwrap_err().status,6);
        assert_eq!(no_join.counts(),before);
        let mut source=c.query(); c.select(&mut source); let plan=source.seal(8).unwrap();
        let mut no_set=c.restricted(22); c.select(&mut no_set); let imported=no_set.import_plan(plan).unwrap();
        let before=no_set.counts();
        assert_eq!(no_set.clause(9,&record(6,vec![u64f(1,imported),u32f(2,0)])).unwrap_err().status,6);
        assert_eq!(no_set.counts(),before);
        let mut no_recursive=c.restricted(21); c.select(&mut no_recursive);
        assert_eq!(CteReference::create(c.parent.clone(),c.parent.model.table_id(),&no_recursive,1).unwrap_err().status,6);
        CteReference::create(c.parent.clone(),c.parent.model.table_id(),&no_recursive,0).unwrap();
        let mut no_prepare=c.restricted(18); c.select(&mut no_prepare); let plan=no_prepare.seal(8).unwrap();
        let args=Batch::encode(&plan.parameter_expectation(),1,&[]).unwrap();
        assert_eq!(plan.execution_arguments(c.parent.source,&args,Limits::default()).unwrap_err().status,6);
        c.query().import_plan(plan).unwrap();
    }

}
