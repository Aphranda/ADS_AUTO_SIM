# Python 脚本管理方案

Status: Draft
Domain: PY
Canonical: `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
Related: `docs/arch/ADS版图自动仿真项目框架设计.md`, `docs/env/ENV_ADS_API_CAPABILITY_MATRIX.md`, `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`
Last updated: 2026-08-06
Owner: ADS Automation

本文档用于管理 SIM 项目中的 Python 脚本。目标不是立即重构目录，而是先把脚本分层、可复用模块、运行环境和输入输出契约固定下来。

## 1. 管理原则

```text
模块保存能力。
CLI 编排流程。
配置表达差异。
数据文件记录实验。
文档登记状态。
```

后续新增脚本前必须先判断：是否可以扩展已有模块，是否只是新增配置，是否会变成一次性 round 脚本。

## 2. 当前脚本状态

| 脚本 | Runtime | 状态 | 定位 | 可复用处理 |
|---|---|---|---|---|
| `ads_profiles.py` | host/ads | candidate | ADS profile 配置 | 提升为配置模块。 |
| `check_ads_python_env.py` | ads/both | stable | ADS Python 环境检查 | 纳入 smoke test。 |
| `ads_probe_ael_words.py` | ads | experimental | AEL 探测 | 登记到 API 能力矩阵。 |
| `check_editable_install.py` | host | stable | 检查 `sim-ads-automation` editable 安装和常用依赖 | 纳入 host 环境 smoke，不执行安装。 |
| `check_round_script_migration.py` | host | stable | 检查历史 round 脚本迁移索引、状态枚举和脚本覆盖 | 纳入 optimizer/script governance gate，不启动 ADS/FEM。 |
| `check_pipeline_contract.py` | host | stable | 检查标准 pipeline contract、项目/sweep/profile 一致性、固定模板、层、单位、端口、频段和评分规则 | 纳入 round 执行前 gate，不启动 ADS/FEM。 |
| `check_layout_contract.py` | host | stable | 检查 `_layout.json` 的单位、层、端口落铜、过孔落点、layer map 版本和拓扑专项 DRC | 纳入 sweep 生成后、ADS 导入前 gate，不启动 ADS/FEM；pixel QR 分支自动检查 mask/source_map/min spacing/feed coupling/island count。 |
| `ads_import_dxf_add_ports.py` | ads | stable | DXF 导入和端口放置 | 抽成 `ads.layout`。 |
| `ads_clone_emsetup_template.py` | ads | stable | emSetup 克隆 | 抽成 `ads.emsetup`。 |
| `ads_run_rfpro_fem.py` | ads | stable | RFPro/FEM 运行 | 抽成 `ads.rfpro`，增加阶段日志。 |
| `export_ads_fem_dataset.py` | ads/both | stable | 结果导出 | 抽成 `ads.dataset`。 |
| `run_ads_filter_candidate.py` | host | stable | 单候选流程入口 | 保持 CLI，内部调用 workflow。 |
| `run_ads_filter_sweep.py` | host | stable | 批量 sweep 入口 | 保持 CLI，内部调用 scheduler。 |
| `generate_interdigital_filter_layout.py` | host | stable | 交指滤波器版图生成 | 抽出几何 primitive。 |
| `generate_folded_sir_bpf_layout.py` | host | experimental | 折叠 SIR 版图生成 | 复用几何 primitive。 |
| `generate_hilo_sir_bpf_layout.py` | host | experimental | 高低阻抗 SIR 版图生成 | 复用几何 primitive。 |
| `generate_stub_bpf_layout.py` | host | experimental | stub BPF 版图生成 | 复用几何 primitive。 |
| `generate_paper_mixed_sir_bpf_layout.py` | host | experimental | 论文 mixed SIR 复现 | 保留论文假设，复用几何 primitive。 |
| `generate_filter_sweep.py` | host | candidate | 批量生成 sweep 版图 | 改为调用器件生成器。 |
| `analyze_ads_dataset.py` | host/both | candidate | ADS dataset 分析 | 抽成 dataset reader。 |
| `analyze_filter_s2p.py` | host | stable | S 参数评分 | 抽成通用 scoring。 |
| `build_i7_fr4_optimization_dataset.py` | host | candidate | I7 FR4 训练集构建 | 参数字段配置化。 |
| `propose_i7_fr4_surrogate_candidates.py` | host | candidate | 代理模型候选生成 | 抽成 optimizer。 |
| `propose_filter_candidates.py` | host | candidate | 统一候选生成入口，当前支持 deterministic variants 配置迁移探针 | 后续承接 deterministic/surrogate 多策略入口。 |
| `make_filter_round*.py` | host | deprecated | 历史候选生成 | 收敛为 optimizer 配置。 |
| `make_i7_fr4_round*.py` | host | deprecated | 历史候选生成 | 收敛为 optimizer 配置。 |
| `make_next_filter_candidates.py` | host | experimental | 下一轮候选生成 | 与 optimizer 合并。 |
| `patch_ads_substrate_pcvia.py` | ads | maintenance | substrate/via 修补 | 默认禁用，保留审计日志。 |
| `tools/layout/generate_microstrip_connector_layout.py` | host | stable | 生成 50R CPWG、单端/双端 SMA launch、L2 cutout、L3 reference plane 的连接器候选版图 | 支持 `--project-config` + `--layout-candidate` 从 `config/projects/hfss_sma_connector.json` 读取候选参数；当前单端优化必须让 `fixture_type=microstrip_single_connector_50r` 从配置或 params 继承，避免 CLI 漏参退回双端。 |
| `tools/hfss/audit_connector_parameters.py` | host/pyaedt | candidate | HFSS 连接器 source/project/instance 参数审计和工程 `$sma_` 变量同步 | 保留为 HFSS connector gate；禁止文本写 `.aedt`，写入只能通过 PyAEDT/API 的 `--sync-project-variables --execute --save`。 |
| `tools/hfss/replace_hfss3dlayout_layout_primitives.py` | host/pyaedt | stable | 在既有 HFSS 3D Layout 工程中统一删除并重绘 PCB 源版图，不触碰 schematic connector instance 和连接器 pin IPort | 当前用于 `SINGLE_END_SMA_CPW_30MM` 连接器 launch 优化；默认 dry-run，真实写入需 `--execute --save`，只允许 `delete source layout -> draw new layout -> recreate PCB output port`；禁止候选级增量 cutout/direct void/局部布尔补丁，`reference_ground_cutout` 只作为旧对象清理名或评审元数据，新缺口必须由 layout generator 输出真实参考地几何，并必须使用 PyAEDT/API，不允许文本修改 `.aedt`。 |
| `tools/hfss/run_existing_hfss3dlayout_verdict.py` | host/pyaedt | stable | 对既有 HFSS 3D Layout design 执行 solve/export/postprocess，不重建版图 | 当前连接器仿真使用 `Setup_0p5to10G` / `Sweep_0p5to10G_96pt` 和 `connector_fullband_v1`；使用 `OperationLifecycle` 记录 ready/solve/export/postprocess/release 耗时，后处理 Python 子进程使用隐藏启动参数；失败时输出 AEDT messages 和诊断 JSON。 |
| `tools/hfss/reap_aedt_processes.py` | host | stable | 监控并回收本脚本启动的 non-graphical AEDT 生命周期 | 自动化入口通过 `start_aedt_reaper()` 写入 owner record，按本脚本登记的目标 PID、父 PID 和 create time 拉起隐藏生命周期监控，Windows 优先 `pythonw.exe` 防止 cmd 弹窗；脚本结束后只回收 owner record 中登记且 create time 匹配的无窗口 AEDT，未登记的 AEDT、用户 GUI 和 attach-existing 会话一律不处理，输出 summary JSON 和 JSONL event log，`--keep-open/--keep-attached` 场景不执行回收。 |
| `tools/hfss/check_aedt_non_graphical_startup.py` | host/pyaedt | stable | 检查 AEDT non-graphical gRPC 启动、版本和项目/design 加载 | 使用 `aedt_startup.py` 的 gRPC 兼容入口和 reaper；输出启动参数、进程前后状态和错误栈。 |
| `tools/hfss/check_hfss_script_classes.py` | host | stable | 检查 HFSS tool 脚本分类登记 | 读取 `tools/hfss/script_classes.json`，要求所有 `tools/hfss/*.py` 登记 runtime/class，禁止 `try_*`、`probe_*`、`scan_*` 进入 production，禁止 text unsafe 脚本作为生产路径。 |
| `tools/hfss/create_hfss3dlayout_smoke_project.py` | host/pyaedt | stable | HFSS 代码修改后的真实 AEDT API smoke gate | 使用 `hfss.session` 默认 non-graphical/new desktop，在 `.simads/aedt_smoke/` 创建独立最小 HFSS 3D Layout 工程、setup/sweep 并保存；不触碰业务工程，不直接编辑 `.aedt/.aedb` 文本。 |
| `tools/hfss/run_hfss_quality_gate.py` | host/pyaedt | stable | HFSS 代码修改统一 gate | 按 HFSS profile 选择 host Python，串联 py_compile、HFSS pytest、AEDT API smoke；pytest 临时目录和 gate/smoke 输出固定在 `.simads/`，作为每次 HFSS 修改后的默认实测入口。 |
| `tools/hfss/rebuild_connector_pin_iports.py` | host/pyaedt | stable | 批量重建 connector pin IPort | 作为 `hfss.port_plans.ConnectorPinPortPlan` 的多端口 wrapper，默认 non-graphical/new desktop；支持从 schematic component instance 推导 component/raw/pin，执行 delete old IPort、CreatePortsOnComponents、schematic connect、validate，统一保存。 |
| `tools/hfss/inspect_aedt_project.py` | host/pyaedt | stable | 只读审计 AEDT project/design/port/object 信息 | `--backend file` 只读解析已保存 `.aedt`；`--backend pyaedt` 可非图形读取 live project，不得写回工程。 |
| `tools/reports/build_report_manifest.py` | host | stable | 生成并校验 HTML 报告资产 manifest | 读取报告目录内 HTML，抽取本地 `src`/`href`/CSS `url(...)` 依赖，生成 `report_manifest.json`；缺失 assets 或目录外引用默认失败，避免报告文件和依赖散落。 |
| `tools/plot_connector_s_curves_svg.py` | host | stable | 绘制连接器全频带 S11/S21/S22 SVG | 使用连接器 0.5-10 GHz 全频带口径，不再标注滤波器 6-8 GHz passband。 |
| `tools/plot_connector_smith_svg.py` | host | stable | 绘制连接器 S11/S22 Smith 圆图 SVG | 使用 Touchstone 复数 S 参数生成 50 ohm 归一化阻抗轨迹，用于判断 L2 cutout 长度/宽度、pad 电容和串联补偿方向。 |
| `tools/plot_connector_before_after_svg.py` | host | candidate | 生成未优化/已优化 S 参数叠加 SVG | 未优化曲线使用淡色虚线，优化曲线使用实线；用于连接器报告，不用于滤波器报告。 |
| `tools/analyze_connector_s2p.py` | host | stable | 连接器 S2P 独立评分和 Smith 指标提取 | 输出 `connector_fullband_v1`、`optimization_cost`、`connector_score`、`smith_z_*` 和 `smith_tuning_hint`，作为后续参数优化器主输入。 |

## 3. 可复用模块清单

| 模块 | 优先级 | 来源脚本 | 职责 |
|---|---|---|---|
| `simads.config` | P0 | `ads_profiles.py` | profile、路径、workspace、library、template、substrate。 |
| `simads.config.pipelines` | P1 | `check_pipeline_contract.py`、`run_ads_filter_candidate.py`、`run_ads_filter_sweep.py` | pipeline contract、脚本绑定、单位、层、端口、频段和评分配置。 |
| `simads.logging` | P0 | `run_ads_filter_candidate.py`、`run_ads_filter_sweep.py`、`ads_run_rfpro_fem.py` | 阶段日志、耗时、错误分类。 |
| `simads.scoring` | P0 | `analyze_filter_s2p.py` | S 参数指标、目标函数、评分权重。 |
| `simads.data` | P0 | `analyze_ads_dataset.py`、`export_ads_fem_dataset.py` | CSV、dataset、Touchstone、summary。 |
| `simads.geometry` | P1 | `generate_*_layout.py`、`check_layout_contract.py` | Point、BBox、Rect、Path、Polygon、Via、Port、Transform、通用 layout contract 和拓扑专项 layout gate。 |
| `simads.exporters` | P1 | `generate_*_layout.py` | DXF、SVG、params.json、DRC、dimension check。 |
| `simads.ads.workspace` | P1 | `ads_import_dxf_add_ports.py`、`ads_profiles.py` | workspace/library/cell/view 门禁。 |
| `simads.ads.layout` | P1 | `ads_import_dxf_add_ports.py` | DXF/GDS 导入、端口、pin、layer、unit。 |
| `simads.ads.emsetup` | P2 | `ads_clone_emsetup_template.py` | emSetup 模板复用。 |
| `simads.ads.rfpro` | P2 | `ads_run_rfpro_fem.py` | RFPro/FEM 启动、等待、超时、结果定位。 |
| `simads.optimizer` | P2 | `propose_i7_fr4_surrogate_candidates.py`、`make_*` | 参数空间、候选生成、代理模型、EI。 |
| `simads.optimizer.variants` | P2 | `make_i7_fr4_round*.py` | deterministic variant 配置读取、seed 参数更新和 plan CSV 行生成。 |
| `simads.reports` | P2 | 报告生成脚本和模板 | HTML/PDF 报告、图片资产、公式表。 |

## 4. 运行时规则

每个脚本必须声明运行时：

| Runtime | 说明 |
|---|---|
| `host` | 使用 uv venv，适合生成器、评分、优化、报告。 |
| `ads` | 使用 ADS Python，适合 `keysight.ads.de`、AEL、RFPro/FEM。 |
| `both` | 两边都可运行，但必须说明功能差异。 |

脚本登记模板：

```text
script:
runtime:
status:
inputs:
outputs:
profile fields:
writes workspace: yes/no
safe to rerun: yes/no
log path:
failure classes:
replacement plan:
```

## 5. 禁止继续扩散的模式

```text
禁止把 round 编号写成新的长期脚本。
禁止在生成器里写死 ADS 安装路径或 workspace 路径。
禁止在 ADS API 脚本里静默 patch 工程文件。
禁止评分脚本只服务于某一个候选文件名。
禁止没有日志阶段的长时间仿真脚本。
禁止新增脚本但不登记 runtime/status/input/output。
```

## 6. 近期动作

```text
P0 给现有 tools/*.py 建立脚本登记表。
P0 给 ADS 相关脚本补阶段日志和错误分类。
P0 把评分函数从 analyze_filter_s2p.py 中抽成通用 scoring 模块。
P1 把 generate_*_layout.py 中重复的 DXF/SVG/几何函数抽出。
P1 把 round 专用候选脚本改为配置驱动。
P1 新增 round 脚本迁移索引检查 gate，迁移或归档前必须通过。
P2 建立 src/simads 包和兼容 CLI。
```
## 7. 已落地的第一批重构

Last updated: 2026-08-04

本轮开始按框架执行 P0 级重构，但不移动旧目录、不删除旧脚本，先建立兼容模块和可追溯运行产物。

已完成：

| 项 | 内容 |
|---|---|
| `src/simads/config` | 新增 profile 配置模块，集中管理 home/company ADS 路径、workspace、library、template cell、substrate、ADS Python 和 host Python。 |
| `tools/ads_profiles.py` | 改为兼容转发层，旧脚本继续使用原导入方式。 |
| `src/simads/runtime` | 新增 run id、state、run manifest、artifact manifest、文件 hash 和错误分类 helper。 |
| `tools/run_ads_filter_candidate.py` | 保持旧 CLI 兼容，新增 `--project-id`、`--round-id`、`--run-id`、`--run-dir`，并输出 `run_manifest.json`、`artifact_manifest.json`、`state.json`。 |
| `tools/run_ads_filter_sweep.py` | 保持旧 CLI 兼容，向单候选入口传递 project/round，并在 summary 中规划 `status/error_class/failed_step/elapsed_s/run_id/profile_id/score_version` 字段。 |
| `tools/check_ads_profile.py` | 新增 profile 快速校验入口，不启动 ADS/FEM。 |
| `tools/check_ads_python_env.py` | 增加 `--profile`，作为 ADS API import smoke test 入口。 |
| `pyproject.toml` | 新增 `sim-ads-automation` 包配置，支持后续 uv/pip editable 管理。 |

已验证：

```text
py_compile tools/*.py + src/simads/*.py 通过。
run_ads_filter_candidate.py --dry-run 通过。
run_ads_filter_sweep.py --dry-run 通过。
check_ads_profile.py --profile home --require-template 通过；layer_map 缺失为 WARN，导入脚本已有 generated-DXF fallback。
ADS Python check_ads_python_env.py --profile home 通过，keysight.ads.de/ael/dataset、keysight.edatoolbox、keysight.pwdatatools 均可导入。
```

后续动作：

```text
1. 把 run manifest 中的 run_id 回填到 score.csv 和 sweep_summary.csv。
2. 把 manifest/state 输出扩展到失败候选和 prepare-only/skip-fem 场景的完整 artifact 记录。
3. 建立 DATA_SCHEMA_REGISTRY.md，固定 profile/candidate/run/artifact/score/training dataset 字段。
4. 再抽 geometry/exporters/scoring 模块，不急于移动 ADS API 子脚本。
```


