# 新增Delivery任务模板（不可作为已接受产物）

模板状态：is_template=true。复制为独立任务后，填具体内容；没有源码/接口依据时保持planned_candidate，不批量创建空任务。

## 身份、目的与版本

Task ID、phase、title、revision、真实author/owner、用户需求ID、设计/研究引用。说明这项工作提供什么可观察能力、为什么需要、有什么明确非目标。

## 契约与真正依赖

列每个contract的ID、精确version、accepted要求；列实际产品依赖ID及revision；区分start和acceptance依赖。对可选引擎/协议用conditional_dependencies，未选不阻塞其他任务。禁止制造所有阶段B等整个阶段A的门槛。

## 实现边界与接口

精确write_scopes、outputs、禁止修改共享文件；具体模块、类型、函数/ABI布局、线程/所有权和状态转换。列可与哪些任务并行、哪些真实设备/端口/基准资源需局部租约。

## 正常、异常和竞争路径

列正常操作、分配者/释放者、错误/取消/关闭/重入路径。对本机制提出可检验不变量与线性化点；数据库明确commit unknown/rollback/pool状态；查询明确NULL和方言；stream明确backpressure/容量。

## 验证与成本

具体unit/integration/属性/fuzz/model/故障注入需求及为何适用。每个支持目标列OS/arch/RID、工具链与Native AOT消费端命令、失败判定。记录FFI/copy/alloc/handle/线程/启动/RSS/尾延迟成本和基准依据。无基线不编造百分比目标。

## 交付与验收

源码、测试、日志、锁文件、制品hash、工具链/平台、输入种子、可重放结果、证据manifest。packet_sha256绑定任务正文；独立Review绑定当前subject和证据；未执行保留blocked/partially_verified。明确受上游改变影响的重验范围。

按规范生成实际节点、prompt和独立PR；更新graph通过整合者fragment，不重写无关任务。accepted之前必须有实质证据，模板不参与验收。
