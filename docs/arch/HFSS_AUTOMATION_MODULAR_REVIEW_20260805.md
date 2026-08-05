# HFSS 自动化模块化评审与优化方案

Status: Active
Domain: ARCH/HFSS
Last updated: 2026-08-05

## 评审目标

把 HFSS 相关代码从“脚本可用”推进到“自动化仿真流水线可长期复用”。AI 后续应主要操作配置、候选参数、运行计划和标准 CLI/API 流程，不直接临时改 AEDT 工程、不依赖 GUI 附着、不把一次性 probe 混入生产路径。

## 开源参考

- PyAEDT / PyAnsys：把 Desktop/AEDT app、EDB、modeler、setup、post-processing 分成独立 API 层，推荐用 Python API 驱动 AEDT 与 EDB，而不是文本修改工程文件。
  参考：https://github.com/ansys/pyaedt
- PyAEDT Hfss3dLayout 文档：HFSS 3D Layout app 负责 create/open project、layout API、setup/solve/export 等高层动作。
  参考：https://aedt.docs.pyansys.com/
- PyEDB 文档：EDB 侧适合做 layout database、primitive、stackup、port terminal 等底层修改，适合作为保存后端口属性 patch/诊断路线。
  参考：https://edb.docs.pyansys.com/
- GDSFactory：组件、端口、settings、netlist 分离，几何生成是纯函数式/声明式输入，流程编排读取组件元数据。
  参考：https://gdsfactory.github.io/gdsfactory/

从这些项目可借鉴的颗粒度不是“大而全 backend 类”，而是稳定的小模块：会话生命周期、版图数据库、端口策略、仿真设置、结果后处理、manifest/缓存分别演进。

## 当前代码状态

当前 HFSS 代码已经有较好的初步拆分：

- `src/simads/hfss/aedt_startup.py`：非 GUI 启动兼容、项目锁、自动 reaper、ready 等生命周期能力。
- `src/simads/hfss/layout.py`：SIM layout JSON 到 HFSS primitive。
- `src/simads/hfss/ports.py`：边推断、GND boundary、AEDT/EDB 端口创建与属性 patch。
- `src/simads/hfss/build.py`：stackup、geometry、ports、setup/sweep、save。
- `src/simads/hfss/solve.py`：analyze、Touchstone export、post-process。
- `src/simads/hfss/results.py`：S2P 后处理。
- `src/simads/hfss/workflow.py`：CLI 编排、manifest、异常处理。
- `tools/hfss/*.py`：生产 CLI 与 API 探索脚本混在同一目录。

## 主要问题

1. `workflow.py` 仍然过重  
   同时承担 args 派生、connector metadata、manifest、AEDT 启动、build/solve 分支和 EDB patch 编排。长期看会阻碍 AI 稳定调用，因为任何新增候选流程都容易再次改动大文件。

2. `tools/hfss` 中生产脚本与 probe 脚本边界不清  
   `run_existing_hfss3dlayout_verdict.py`、`replace_hfss3dlayout_layout_primitives.py` 已是生产能力；`try_*`、`probe_*` 是探索能力。两者应在文档和代码入口上明确区分，避免自动流程误用 probe。

3. 端口流程需要固化成 PortPlan  
   当前端口能力分散在 `ports.py`、`replace_hfss3dlayout_layout_primitives.py` 和若干 probe 脚本中。连接器 pin port 的正确流程已经被人工确认：选中连接器本身激励端口并 Create，随后在 schematic 中连接 IPort 和 connector。这个动作应成为可验证的 `ConnectorPinPortPlan`，而不是脚本内散落参数。

4. 后处理 profile 需要统一  
   同一个 HFSS solve 可能是 filter 或 connector。connector 必须输出 Smith 图，并使用 connector scoring。后处理逻辑不能只存在于某个 CLI 脚本中。

5. AI 可操作对象还不够显式  
   AI 应修改的是：
   - 候选参数 JSON/CSV；
   - layout generator 参数；
   - run plan；
   - workflow CLI 参数；
   - report assets/HTML。
   AI 不应操作的是：
   - AEDT/AEDB 文本内容；
   - GUI 状态；
   - 一次性 probe 发现的半成品端口对象。

## 目标架构

```text
config / candidate params
  -> layout generator
  -> LayoutContract
  -> HfssRunPlan
  -> HfssSession
  -> BuildPipeline
      -> StackupApplier
      -> GeometryBuilder
      -> PortPlanExecutor
      -> SetupSweepBuilder
  -> SolveExporter
  -> ResultPostProcessor
  -> Manifest + Report Assets
```

推荐模块边界：

| 模块 | 责任 | 输入 | 输出 |
|---|---|---|---|
| `hfss.session` | AEDT 启动、锁、ready、release、reaper | project/design/runtime settings | app context + lifecycle |
| `hfss.project` | project/design action、锁文件策略、保存策略 | project path/action | project state |
| `hfss.layout` | layout JSON -> primitives | layout dict + GeometryBuildOptions | created object names |
| `hfss.ports` | 纯端口几何推断与底层 API helper | layout + PortOptions | edge/pin/EDB port data |
| `hfss.port_plans` | 生产端口策略 | PortPlan | validated port result |
| `hfss.build` | stackup/geometry/ports/setup/sweep 顺序 | HfssBuildPlan | build result |
| `hfss.solve` | analyze/export | HfssSolvePlan | s2p path |
| `hfss.results` | score/trace/svg/Smith | s2p + profile | artifacts |
| `hfss.workflow` | CLI 到 plan，manifest，错误归档 | argparse/config | JSON payload |

## AI 固化流程

AI 后续只走这几类入口：

1. 生成候选  
   修改配置或调用 layout generator，输出 layout JSON、params JSON、SVG。

2. 替换当前 HFSS 版图  
   调用生产 API/CLI：删除源 PCB primitives、重建 layout、只重建 PCB 远端口。不创建 P1 PCB port，不触碰 connector pin IPort。

3. 修复连接器端口  
   调用固化后的 `ConnectorPinPortPlan`：删除指定旧 IPort、按 connector component/pin 创建端口、schematic 连接、验证 layout port info 与 schematic ports。

4. 求解和后处理  
   默认 non-graphical/new desktop，不附着 GUI；解锁逻辑在生命周期中处理；connector profile 必须输出 score、trace、S 曲线、Smith 图。

5. 报告更新  
   从 manifest 和 artifacts 生成报告资产，HTML 引用报告目录内 assets；不把工程文件当文档编辑。

## 待办

- [x] P0: 将 existing-project solve 后处理从 `tools/hfss/run_existing_hfss3dlayout_verdict.py` 收敛到 `src/simads/hfss/results.py`。
- [x] P0: connector postprocess profile 输出 Smith 图，并让 `solve.py` 根据 fixture_type 自动选择 connector/filter profile。
- [x] P0: 增加 `hfss.session`，把 `aedt_automation_lock + prepare_aedt_project_lock + Hfss3dLayout + wait_for_hfss3dlayout_ready + reaper + release` 封装为上下文管理器。
- [x] P0: 给 `replace_hfss3dlayout_layout_primitives.py` 改用 `hfss.session`，保持默认 non-graphical/new desktop。
- [ ] P1: 建立 `PortPlan` / `ConnectorPinPortPlan` dataclass，固化“connector pin Create + schematic connect + validate”流程。
- [ ] P1: 将稳定端口代码从 `try_official_port_create_elements.py` 抽入 `src/simads/hfss/port_plans.py`，probe 脚本只调用库函数或保留为诊断。
- [ ] P1: 增加端口验收报告：layout ports、schematic IPorts、connection points、boundary warning、port count。
- [ ] P1: 建立 `tools/hfss/probes/` 或文档标签，把 `try_*`/`probe_*` 与生产 CLI 分开。
- [ ] P2: 将 `workflow.py` 中 manifest/connector metadata 派生拆到 `hfss.manifest` / `hfss.connector_contract`。
- [ ] P2: 把 report 生成从手工 HTML patch 演进成读取 manifest/artifacts 的可重复报告流程。
- [ ] P2: 对 `layout.py` reference_ground_cutout 行为增加真实 AEDT/单元双层验证，确认 negative primitive 与 subtract 语义是否一致。

## 当前第一步修改

本轮已完成低风险模块化改动：

- `src/simads/hfss/results.py`
  - 支持 `profile="filter"` 与 `profile="connector"`。
  - connector profile 使用 `analyze_connector_s2p.py`、`plot_connector_s_curves_svg.py`、`plot_connector_smith_svg.py`。
  - 支持 lifecycle 计时，子进程默认 hidden。
- `tools/hfss/run_existing_hfss3dlayout_verdict.py`
  - 删除重复后处理逻辑，改为调用库函数。
- `src/simads/hfss/solve.py`
  - 根据 layout metadata 的 fixture_type 自动选择 connector/filter 后处理 profile。

已验证：

```text
python -m py_compile src\simads\hfss\results.py src\simads\hfss\solve.py tools\hfss\run_existing_hfss3dlayout_verdict.py
python -m pytest tests\test_run_existing_hfss3dlayout_verdict.py tests\test_aedt_lifecycle.py
```

结果：9 passed。

## 当前第二步修改

本轮完成 HFSS AEDT 生命周期收敛：

- 新增 `src/simads/hfss/session.py`
  - `Hfss3dLayoutSessionConfig` 固化 project/design/version、默认 non-graphical/new desktop、ready、reaper、release 策略。
  - `open_hfss3dlayout_session` 统一执行 PyAEDT settings、自动化锁、工程锁检查/解锁、Hfss3dLayout 启动、ready 等待、reaper 启动和 release。
  - 支持单元测试注入 fake app，不在测试中启动 AEDT。
- `tools/hfss/run_existing_hfss3dlayout_verdict.py`
  - 移除脚本内重复 lock/project lock/start/ready/reaper/release 编排。
  - 保留原有 analyze、Touchstone export、connector/filter postprocess 行为。
- `tools/hfss/replace_hfss3dlayout_layout_primitives.py`
  - 改用 `hfss.session`，继续默认 non-graphical/new desktop。
  - 保留“不碰 connector 对象，只删重建源 PCB 版图，只按需重建 P2 PCB output port”的生产策略。

已验证：

```text
python -m py_compile src\simads\hfss\session.py src\simads\hfss\__init__.py tools\hfss\run_existing_hfss3dlayout_verdict.py tools\hfss\replace_hfss3dlayout_layout_primitives.py tests\test_aedt_lifecycle.py
python -m pytest tests\test_aedt_lifecycle.py tests\test_run_existing_hfss3dlayout_verdict.py tests\test_hfss_replace_layout.py
```

结果：11 passed。
