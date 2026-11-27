# Metadata 初始化失败：继承的 native owner 清理风险

**独立源码复核确认：integrated05 原代码存在可导致第二次 native owner release 的异常路径，74917fd4 池候选保持了这段原字节。** 这不是已执行的失败或地址复用复现；不得把后续测试故障挪到 owner 构造前，随后声称覆盖了原 Metadata 失败分支。本报告追加到首个产品窄审之后，原审查仅证明池改动没有改变旧清理语句，不代表该分支已经安全实测。

## 可直接从源码证明的链条

1. `Seal` 使用 `plan = new(Source, Plan, result) { QueryPlan = Metadata() }`。C#对象初始化先完成构造，再求值并设置init属性，最后把完整表达式赋给plan。
2. `DatabaseOwner` 派生SafeHandle，base参数ownsHandle=true，构造函数最后SetHandle(result)。因此Metadata开始时，这个临时SafeHandle已经负责native result，而plan尚未接收到它。
3. 若Metadata抛错，现catch直接调用raw `nw_db_owner_release_v1(result)`。它没有对那个临时SafeHandle设置invalid或Dispose。Metadata本身会分配dictionary/parameter array，正常资源耗尽是可抛错来源；本审查没有制造真实OOM。
4. 锁定VMR的SafeHandle构造建立refcount1和fullyInitialized；finalizer在对象可回收时调用Dispose(false)，经InternalRelease检查ownsHandle及IsInvalid后调用ReleaseHandle。raw native release不改变这些managed状态；DatabaseOwner.IsInvalid只判断handle==0。因此该finalizer以后仍可第二次调用同一raw地址。
5. 原生`publish`以新分配Stored的地址为registry key。`release<shared_ptr<Owner>>`取出并擦除该地址，释放Stored；没有generation/tombstone。若第二次调用前该地址尚未复用，release找不到而不操作；若地址已被新Owner复用，type检查只区分Owner/Operation/Buffer，第二次调用会删除新Owner。这里只证明条件性的误退休风险，没有声称地址复用已实际发生。

`CreateCte`有同构结构：构造SafeHandle后才求值`new(model.Table, Metadata())`，catch同样rawrelease。它不参与本次pool范围，但属于同一已确认的清理问题。应单独记录其修复，不能默默把它写成“08顺手优化”。

## 最小修正方向，尚未实施

可在原raw-owner保护的try/catch中，先完整构造metadata（CTE包括QueryCteMetadata），然后才创建DatabaseOwner并用已经完成的metadata做不分配的auto-init赋值。当前DatabaseOwner构造SetHandle是最后操作，之前失败时handle仍为0；将所有可能失败的metadata工作放到adoption前，可使每个时刻只有raw catch或SafeHandle之一负责释放。

这会改变metadata相对于managed wrapper构造/分配的次序，需要明确作为独立cold cleanup修正审查，不能宣称完全没有控制流变化。现源码的source/null/owner-release要求在有效命令上下文中已成立；仍应检查错误顺序的实际约束。无需改native registry/ABI、引入heap Func、改缓存或扩大public API。另一种显式adoption helper也可行，但变更面更大，不是本报告已经选择的实现。

Root应先在Plan/Design记录并授权该独立前置修正。池化A/B必须使用相同cleanup基线，或明确分开原05→cleanup与cleanup→pool的身份，不能把错误修复混算为pool分配收益。当前749产品保持冻结，未改动。

## 有意义的最小控制

用单独local故障构建，在真正Metadata求值位置注入确定性managed异常，保留原owner构造顺序；记录精确目标handle的release次数，离开不内联局部作用域后有限GC/finalizer控制可证原路径是否二次调用。负控应保留原05/749身份和失败范围；不需要制造真实OOM，也不必尝试破坏性地址重用才能说明源码风险。

修正后在同一真实位置注入，验证原异常保持、目标handle仅释放一次，后续计划/源仍可用；Seal与同构CTE各覆盖一次即可。不得从UnmanagedCallersOnly回调跨ABI抛managed异常；只能在managed Metadata位置注入。租约finally仍另核一次归还，与native owner释放不是同一计数。普通shipping产品不增加全局可变故障callback，测试原始结果和插桩身份独立保留。

本报告不授权构建、执行或产品编辑，也不要求广泛新矩阵。实际复现、修正选择和测试结果仍由root下一步安排。

## 来源

- 2ea与749的`src/Query.Binding/QueryCommand.Submission.cs`、`Owners.cs`、`QueryCommand.cs`以及`native/cpp/src/host_abi.cpp`，精确SHA列于findings.json。
- 官方锁定VMR297acf的[SafeHandle.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Runtime/InteropServices/SafeHandle.cs)，原始字节保存在upstream，Git blob 2d1f9313b485c57afab1f187e00a180df7fad3ba。
