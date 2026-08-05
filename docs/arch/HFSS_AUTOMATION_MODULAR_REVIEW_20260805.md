# HFSS 自动化模块化评审与优化方案

Status: Active
Domain: ARCH/HFSS
Last updated: 2026-08-06

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

6. HFSS 代码改动实测
   每次修改 HFSS API、AEDT 生命周期、版图构建、端口、求解或后处理相关代码后，除了纯 Python 测试，还必须启动 AEDT 做 API smoke。默认使用 non-graphical/new desktop，不附着 GUI；测试工程固定隔离在 `.simads/aedt_smoke/`，不触碰业务 `.aedt`。

## 待办

- [x] P0: 将 existing-project solve 后处理从 `tools/hfss/run_existing_hfss3dlayout_verdict.py` 收敛到 `src/simads/hfss/results.py`。
- [x] P0: connector postprocess profile 输出 Smith 图，并让 `solve.py` 根据 fixture_type 自动选择 connector/filter profile。
- [x] P0: 增加 `hfss.session`，把 `aedt_automation_lock + prepare_aedt_project_lock + Hfss3dLayout + wait_for_hfss3dlayout_ready + reaper + release` 封装为上下文管理器。
- [x] P0: 给 `replace_hfss3dlayout_layout_primitives.py` 改用 `hfss.session`，保持默认 non-graphical/new desktop。
- [x] P1: 建立 `PortPlan` / `ConnectorPinPortPlan` dataclass，固化“connector pin Create + schematic connect + validate”流程。
- [x] P1: 将稳定端口代码从 `try_official_port_create_elements.py` 抽入 `src/simads/hfss/port_plans.py`，probe 脚本只调用库函数或保留为诊断。
- [x] P1: 将 `rebuild_connector_pin_iports.py` 收敛到 `hfss.port_plans`，保留为多端口批量 wrapper。
- [x] P1: 新增独立 AEDT API smoke 工程脚本 `tools/hfss/create_hfss3dlayout_smoke_project.py`，用于 HFSS 代码修改后的真实 AEDT 启动和最小工程创建验证。
- [x] P1: 增加端口验收报告：layout ports、schematic IPorts、connection points、boundary warning、port count。
- [x] P1: 建立 `tools/hfss/probes/` 或文档标签，把 `try_*`/`probe_*` 与生产 CLI 分开。
- [x] P1: 建立统一 HFSS gate wrapper，按 profile 自动选择 host Python，并串联 py_compile、pytest、AEDT smoke。
- [x] P2: 将 `workflow.py` 中 manifest/connector metadata 派生拆到 `hfss.manifest` / `hfss.connector_contract`。
- [x] P2: 把 report 生成从手工 HTML patch 演进成读取 manifest/artifacts 的可重复报告流程。
- [x] P2: 固化 `layout.py` 不在 HFSS 中执行 reference-ground cutout/negative/subtract 操作；候选差异只能通过删除旧 layout primitives 后加载新生成 layout 表达。

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

## 当前第三步修改

本轮完成连接器 pin 端口生产流程固化：

- 新增 `src/simads/hfss/port_plans.py`
  - `ConnectorPinPortPlan` 固化单个 connector pin port 的创建计划。
  - `execute_connector_pin_port_plan` 执行：删除旧 schematic IPort、调用官方 `CreatePortsOnComponents`、验证 layout port、移动 schematic IPort 到安全空白位置、创建 wire 连接 connector pin、按需保存。
  - 验收条件明确拒绝 `ConnectionPoints=NONE` 的 component-pin-only 伪成功端口，也拒绝仍连到 `InterfacePort` 的错误对象。
- `tools/hfss/recreate_connector_component_pin_port.py`
  - 从 probe wrapper 改为生产入口。
  - 默认使用 `hfss.session`，保持 non-graphical/new desktop。
  - 不附着 GUI，不直接编辑 AEDT/AEDB 文本。
- 新增 `tests/test_hfss_port_plans.py`
  - 覆盖 ConnectionPoints 验收。
  - 覆盖删除旧 IPort、创建 connector pin edge port、移动 IPort、连线、保存的成功路径。

已验证：

```text
python -m py_compile src\simads\hfss\port_plans.py src\simads\hfss\__init__.py tools\hfss\recreate_connector_component_pin_port.py tests\test_hfss_port_plans.py
python -m pytest tests\test_hfss_port_plans.py
```

结果：2 passed。

## 当前第四步修改

本轮建立 HFSS AEDT API smoke 工程入口：

- 新增 `tools/hfss/create_hfss3dlayout_smoke_project.py`
  - 复用 `hfss.session`，默认 non-graphical/new desktop，不附着 GUI。
  - 通过 API 创建最小 HFSS 3D Layout 工程：材料、三层 stackup、GND、信号铜皮、extents、setup/sweep。
  - 工程固定输出到 `.simads/aedt_smoke/hfss3dlayout_api_smoke.aedt`，结果 JSON 和 lifecycle JSONL 也写入 `.simads/aedt_smoke/`。
  - 不创建业务端口、不求解、不直接编辑 `.aedt/.aedb` 文本。

已验证：

```text
python -m py_compile tools\hfss\create_hfss3dlayout_smoke_project.py
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\hfss\create_hfss3dlayout_smoke_project.py --output .simads\aedt_smoke\latest_smoke.json
```

结果：AEDT 2026.1 non-graphical/new desktop 启动通过，`start_hfss3dlayout` 15.083 s，总耗时 20.09 s；创建并保存 `.simads/aedt_smoke/hfss3dlayout_api_smoke.aedt`，setup 为 `Setup_4to10G`，sweep 为 `Sweep_4to10G_21pt`。

## 当前第五步修改

本轮建立统一 HFSS gate wrapper：

- 新增 `tools/hfss/run_hfss_quality_gate.py`
  - 读取 `config/hfss_profiles.json`，按 profile 自动选择 `host_python`。
  - 串联 `py_compile`、HFSS 相关 pytest、AEDT API smoke。
  - pytest 的 `basetemp/cache_dir` 固定到 `.simads/`，避免写用户 Temp 导致权限不稳定。
  - 子进程输出按 UTF-8 收集，结果写 `.simads/gates/hfss_quality_gate_latest.json`。
- `tools/hfss/create_hfss3dlayout_smoke_project.py`
  - 默认每次从 fresh AEDT project 创建，再保存覆盖 smoke 工程；只有显式 `--reuse-project` 才打开旧 smoke project。
  - 保存前检查目标 `.aedt.lock`，记录到 `smoke_output_lock`。

已验证：

```text
python -m py_compile tools\hfss\run_hfss_quality_gate.py tests\test_hfss_quality_gate.py
python -m pytest tests\test_hfss_quality_gate.py
python tools\hfss\run_hfss_quality_gate.py --profile home --output .simads\gates\hfss_quality_gate_latest.json
```

结果：完整 gate 通过；host Python 为 `D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe`，HFSS 相关 pytest `20 passed`，AEDT smoke 18.532 s。

## 当前第六步修改

本轮将批量连接器 pin IPort 重建脚本收敛到生产端口计划：

- `tools/hfss/rebuild_connector_pin_iports.py`
  - 改为复用 `hfss.session`，默认 non-graphical/new desktop，不附着 GUI。
  - 批量构造 `ConnectorPinPortPlan`，执行统一的 connector pin Create、schematic IPort 移动、wire 连接和端口验收逻辑。
  - 兼容旧的 `--delete-port`、`--component-id`、`--expected-port` 参数，并支持显式 `--component`、`--component-def`、`--raw-component`、`--pin`。
  - 旧 `create-iport-*` 坐标建端口路径只保留为非生产兼容检查，不再执行。
- `tools/hfss/run_hfss_quality_gate.py`
  - 默认 py_compile/pytest 清单加入批量端口 wrapper 和对应测试。
- `tests/test_hfss_rebuild_connector_pin_iports.py`
  - 覆盖从 schematic component instance 推导 `ConnectorPinPortPlan`。
  - 覆盖批量执行每个 plan，最后统一保存一次。

已验证：

```text
python -m py_compile tools\hfss\run_hfss_quality_gate.py tools\hfss\rebuild_connector_pin_iports.py tests\test_hfss_quality_gate.py tests\test_hfss_rebuild_connector_pin_iports.py
python -m pytest tests\test_hfss_quality_gate.py tests\test_hfss_port_plans.py tests\test_hfss_rebuild_connector_pin_iports.py
python tools\hfss\run_hfss_quality_gate.py --profile home --output .simads\gates\hfss_quality_gate_latest.json
```

结果：快速测试 7 passed；完整 gate 通过，默认 HFSS pytest `22 passed`，AEDT smoke 18.622 s。

## 当前第七步修改

本轮增加 connector port 验收报告：

- `src/simads/hfss/port_plans.py`
  - 新增 `connector_port_acceptance_report()`，输出 layout ports、schematic IPorts、wire ids、ConnectionPoints、端口计数、boundary/port warning 和 rejected 列表。
  - `execute_connector_pin_port_plan()` 的 dry-run、成功、失败结果均附带 `acceptance_report`。
  - 明确列出 `component_pin_only_rejected`，用于识别 `ConnectionPoints=NONE` 的伪成功端口。
- `tools/hfss/rebuild_connector_pin_iports.py`
  - 批量执行完成后输出整个批次的最终 `acceptance_report`。
- `tests/test_hfss_port_plans.py`
  - 覆盖验收报告状态、ConnectionPoints 读回、schematic wire id 和 component-pin-only rejected 列表。

已验证：

```text
python -m py_compile src\simads\hfss\port_plans.py tools\hfss\rebuild_connector_pin_iports.py tests\test_hfss_port_plans.py tests\test_hfss_rebuild_connector_pin_iports.py
python -m pytest tests\test_hfss_port_plans.py tests\test_hfss_rebuild_connector_pin_iports.py
python tools\hfss\run_hfss_quality_gate.py --profile home --output .simads\gates\hfss_quality_gate_latest.json
```

结果：端口相关测试 5 passed；完整 gate 通过，默认 HFSS pytest `23 passed`，AEDT smoke 27.354 s。

## 当前第八步修改

本轮建立 HFSS 脚本分类治理：

- 新增 `tools/hfss/script_classes.json`
  - 覆盖当前 `tools/hfss/*.py` 共 38 个脚本。
  - 明确区分 `production`、`diagnostic`、`probe`、`maintenance`、`legacy_text_unsafe`。
  - `try_*`、`probe_*`、`scan_*` 全部标记为 `probe` 且 `production_allowed=false`。
  - `rename_aedt_design_ports_text.py` 标记为 `legacy_text_unsafe`，继续禁止作为 HFSS 工程修改路径。
- 新增 `tools/hfss/check_hfss_script_classes.py`
  - 检查每个 HFSS tool 脚本都已登记。
  - 检查 probe 前缀不能进入 production。
  - 检查 probe 和 legacy text unsafe 不能 `production_allowed=true`。
- `tools/hfss/run_hfss_quality_gate.py`
  - 默认 py_compile/pytest 清单加入脚本分类检查。
- 新增 `tests/test_hfss_script_classes.py`。

已验证：

```text
python tools\hfss\check_hfss_script_classes.py
python -m py_compile tools\hfss\check_hfss_script_classes.py tools\hfss\run_hfss_quality_gate.py tests\test_hfss_script_classes.py
python -m pytest tests\test_hfss_script_classes.py tests\test_hfss_quality_gate.py
python tools\hfss\run_hfss_quality_gate.py --profile home --output .simads\gates\hfss_quality_gate_latest.json
```

结果：分类检查 `script_count=38`、无 missing/stale/errors；完整 gate 通过，默认 HFSS pytest `25 passed`，AEDT smoke 18.777 s。

## 当前第九步修改

本轮拆分 `workflow.py` 的 manifest 与 connector contract 逻辑：

- 新增 `src/simads/hfss/connector_contract.py`
  - `connector_fixture_metadata()` 负责从 layout metadata、CLI args 和旁路 params JSON 派生连接器 fixture 合同。
  - `connector_port_reference_name()` 固化 `GND:<layer>:<primitive>` 参考名派生。
  - `is_connector_fixture()` 统一判断连接器 fixture 类型。
- 新增 `src/simads/hfss/manifest.py`
  - 承接 `stackup_config_from_args()`、`infer_round_id()`、`default_candidate_id()`。
  - 承接 `build_hfss_manifest_payload()`、`write_hfss_manifests()`、`completed_hfss_stage()`。
- `src/simads/hfss/workflow.py`
  - 删除 manifest/connector metadata 具体实现，保留 CLI 编排、dry-run payload 和 `run_hfss()`。
  - 通过导入保持原 `simads.hfss.workflow.build_hfss_manifest_payload` 等兼容入口。
- `src/simads/hfss/__init__.py`
  - 导出 connector contract 和 manifest helper。
- 新增 `tests/test_hfss_manifest_contracts.py`，覆盖拆分模块与 workflow 兼容导入。

已验证：

```text
python -m py_compile src\simads\hfss\__init__.py src\simads\hfss\workflow.py src\simads\hfss\manifest.py src\simads\hfss\connector_contract.py tools\hfss\run_hfss_quality_gate.py tests\test_hfss_manifest_contracts.py
python -m pytest tests\test_hfss_manifest_contracts.py tests\test_hfss_connector.py tests\test_hfss_quality_gate.py
python tools\hfss\run_hfss_quality_gate.py --profile home --output .simads\gates\hfss_quality_gate_latest.json
```

结果：manifest/connector 快速测试 20 passed；完整 gate 通过，默认 HFSS pytest `27 passed`，AEDT smoke 27.484 s。

## 当前第十步修改

本轮建立报告资产 manifest 和依赖校验流程：

- 新增 `src/simads/reports/manifest_report.py`
  - 从 HTML 抽取本地 `src`、`href`、`poster` 和 CSS `url(...)` 依赖。
  - 统一输出 POSIX 风格相对路径，便于 home/company 环境复现。
  - 拒绝缺失 assets 和指向报告目录外的本地引用。
- 新增 `tools/reports/build_report_manifest.py`
  - 对报告目录生成 `report_manifest.json`。
  - 默认 strict 校验，缺失或越界引用返回失败。
- `tools/hfss/run_hfss_quality_gate.py`
  - 将报告 manifest 模块、CLI 和测试纳入 HFSS 模块化 gate。
- 当前 SP8T 报告目录已生成 `report_manifest.json`，HTML 引用的本地 assets 均存在且位于报告目录内。

已验证：

```text
python -m py_compile src\simads\reports\__init__.py src\simads\reports\manifest_report.py tools\reports\build_report_manifest.py tests\test_report_manifest.py tools\hfss\run_hfss_quality_gate.py
python -m pytest tests\test_report_manifest.py tests\test_hfss_quality_gate.py
python tools\reports\build_report_manifest.py --report-dir projects\hfss_sma_connector\reports\SP8T开关连接器设计优化报告
```

结果：报告快速测试 6 passed；SP8T 报告 manifest 状态为 `ok`。

## 当前第十一步修改

本轮按生产约束纠偏 HFSS 版图替换策略：

- `src/simads/hfss/layout.py`
  - `reference_ground_cutout` 不再创建 negative 工具图形，也不调用 `modeler.subtract`。
  - HFSS builder 只负责从 layout JSON 创建实际铜皮、过孔、参考地平面等 primitives。
  - 如果候选需要 L2/L3/L4 缺口，必须由上游 layout generator 输出真实的参考地铜皮/平面形状，而不是让 HFSS 对已有平面做局部挖空。
- `tools/hfss/replace_hfss3dlayout_layout_primitives.py`
  - dry-run policy 明确 `allowed_geometry_boolean_scope=none`。
  - `reference_ground_cutout` 只允许作为旧对象删除名或评审元数据，不允许作为新建 HFSS cutout 操作。
- `tests/test_hfss_layout.py` / `tests/test_hfss_replace_layout.py`
  - 覆盖 `reference_ground_cutout` 被跳过且不会触发 boolean/subtract。
  - 覆盖 replace policy 固化为完整删除旧 primitives、重载新 layout。

已验证：

```text
python -m py_compile src\simads\hfss\layout.py tools\hfss\replace_hfss3dlayout_layout_primitives.py tools\hfss\create_hfss3dlayout_smoke_project.py tools\hfss\run_hfss_quality_gate.py tests\test_hfss_layout.py tests\test_hfss_replace_layout.py
python -m pytest tests\test_hfss_layout.py tests\test_hfss_replace_layout.py tests\test_hfss_quality_gate.py
```

结果：layout/replace/policy 快速测试 11 passed。

## 当前第十二步修改

本轮完成连接器参考地缺口实体化：

- `src/simads/hfss/connector.py`
  - 新增 reference-ground 正向切片逻辑，把 L2 cutout 候选转换为 `reference_ground_plane` 分片。
  - 保留 `reference_ground_cutout` 作为报告/评审和旧对象清理元数据，不交给 HFSS 执行 subtract。
  - L3 在配置 cutout 时同样使用正向参考地分片；L4 仍按配置输出完整参考地平面。
- `src/simads/hfss/layout.py`
  - 当 layout JSON 已显式提供当前 reference layer 的 `reference_ground_plane` 时，不再自动铺一整板默认 GND，避免盖掉 generator 已实体化的缺口。
- `tests/test_hfss_connector.py` / `tests/test_hfss_layout.py`
  - 覆盖 L2 cutout-enabled connector layout 会输出 `hfss_ground_plane` 分片。
  - 覆盖显式 L2 reference plane 会抑制默认整板 GND。
  - 覆盖 HFSS builder 不创建 cutout、不执行 subtract。

已验证：

```text
python -m pytest tests\test_hfss_layout.py tests\test_hfss_connector.py tests\test_hfss_replace_layout.py tests\test_hfss_quality_gate.py
python tools\hfss\run_hfss_quality_gate.py --profile home --output .simads\gates\hfss_quality_gate_latest.json
```

结果：快速测试 27 passed；完整 gate 通过，HFSS 相关 pytest 53 passed，AEDT 2026.1 non-graphical smoke 通过，完整 gate elapsed 20.049 s。
