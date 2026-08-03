# ADS 自动仿真项目重构任务进度追踪与回溯

Status: Active
Domain: ARCH
Canonical: `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
Related: `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/arch/ADS版图自动仿真项目框架设计.md`, `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
Last updated: 2026-08-03
Owner: ADS Automation

本文档记录 ADS 自动仿真项目重构的正式任务进度。TODO 细分以 `ARCH_REFACTOR_TODO.md` 为准；架构原则以 `ADS版图自动仿真项目框架设计.md` 和 `ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md` 为准。

## 记录规则

- 每个正式重构任务使用独立编号：`ARCH-REFACTOR-TASK-YYYYMMDD-NNN`。
- 每条记录必须写明任务目标、完成内容、验证结果、还需完成、关联文件和下一步。
- 最新记录追加在“任务记录”章节顶部。
- 如果只完成文档或 dry-run，状态应写为 `进行中`，不能写成完整 ADS/FEM 闭环完成。
- 涉及 Python 脚本修改时，至少执行 `py_compile`；涉及 ADS API 时，至少执行 profile/API smoke test。
- 涉及真实 ADS workspace 写入、FEM 仿真或历史结果覆盖时，必须在记录中写明 profile、workspace、library、template cell、candidate cell 和输出目录。

## 状态定义

| 状态 | 含义 |
|---|---|
| `完成` | 当前任务目标已经达成，并完成必要编译、dry-run、profile/API smoke 或仿真验证。 |
| `进行中` | 已完成阶段性工作，但还未完成完整数据追溯、真实 ADS/FEM 或后续 gate。 |
| `阻塞` | 当前无法继续，需要 ADS 环境、license、文件、仪器、用户决策或外部状态变化。 |
| `暂停` | 暂时不推进，但不是技术阻塞。 |

## 记录模板

```markdown
### ARCH-REFACTOR-TASK-YYYYMMDD-NNN - 任务标题

- 状态：进行中 / 完成 / 阻塞 / 暂停
- 日期：YYYY-MM-DD
- 任务目标：
  - ...
- 完成内容：
  - ...
- 验证结果：
  - ...
- 还需完成：
  - ...
- 关联文件：
  - `path/to/file`
- 下一步：
  - ...
```

## 当前目标

当前重构已进入 P2 阶段：外部 ADS workspace 不移动，仓库内 ADS 项目资产以 `projects/<project_id>/` 为有效边界。P0/P1 的数据契约、manifest、score/summary 追溯、baseline freeze、workspace 写入安全 gate、run state machine、结果治理、制造鲁棒性和报告发布 gate 已落地；当前重点是将旧脚本内部逻辑逐步收敛到 `src/simads` 模块，并保证新增器件分支使用独立项目目录。

## 任务记录

### ARCH-REFACTOR-TASK-20260803-002 - HFSS Microstrip Connector Joint Simulation Plan

- 状态：进行中
- 日期：2026-08-03
- 任务目标：
  - 将标准 50 ohm 微带线 + 两端连接器 launch 的 HFSS 联合仿真拆成独立方案。
  - 当前阶段不加入滤波器、谐振器或其他功能结构，只迭代连接器与微带 launch 处版图。
  - 用户后续会提供连接器 HFSS 模型，Route C 高保真复核以该模型为准。
  - 最终合并验证复杂度较高，作为最后事项处理，不作为微带线+连接器联合仿真闭环的前置条件。
  - 仅做方案和 TODO 登记，不修改仿真代码，不启动 ADS/HFSS。
- 完成内容：
  - 新增并更新 `docs/flow/FLOW_HFSS_CONNECTOR_LAYOUT_OPTIMIZATION.md`。
  - 在 `ARCH_REFACTOR_TODO.md` 新增 `P1-15 HFSS Connector Layout Optimization Extension`。
  - 在 README 的 FLOW 主文档、分支阅读规则和快速查找规则中增加 HFSS 微带线+连接器联合仿真方案入口。
  - 将方案拆分为 Route A/B/C、连接器 launch 参数、自动化流程、评分 delta、数据契约、实施阶段和风险。
  - 将整板/滤波器合并验证下沉为 Phase 5 最后事项。
- 验证结果：
  - 本次仅新增/更新 Markdown 文档。
  - 未修改 Python 脚本，未启动 ADS、HFSS/AEDT 或 FEM 仿真。
- 还需完成：
  - 固定连接器 footprint、50R 微带线尺寸、板边位置、端口参考面和求解频段。
  - 登记用户提供的连接器 HFSS 模型路径、版本、hash、端口定义、坐标基准和参考面。
  - 建立 connector launch 参数 schema 和 microstrip+connector generator。
  - 扩展 HFSS workflow/manifest，并用 3-5 个 smoke 候选验证 build 和 score delta。
- 关联文件：
  - `docs/flow/FLOW_HFSS_CONNECTOR_LAYOUT_OPTIMIZATION.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
  - `docs/README.md`
- 下一步：
  - 先冻结连接器 footprint、50R 微带线尺寸与端口参考面，再做 microstrip+connector layout JSON schema 和只读 gate；整板合并验证放到最后阶段。

### ARCH-REFACTOR-TASK-20260803-001 - HFSS Standard Backend TODO Registration

- 状态：进行中
- 日期：2026-08-03
- 任务目标：
  - 将 HFSS 3D Layout 从 ADS/RFPro 裁决复核路径提升为标准仿真 backend 的后续工作纳入 TODO。
  - 保持现有 ADS 单候选和 sweep 闭环稳定，不在本次登记中修改代码或启动仿真。
- 完成内容：
  - 在 `ARCH_REFACTOR_TODO.md` 新增 `P1-14 HFSS Standard Simulation Backend`。
  - 明确后续需要补齐 pipeline backend 配置、统一 candidate runner、backend-neutral state machine、HFSS manifest artifact、HFSS backend 文档口径、只读 gate 和 summary 字段。
  - 保留 `FLOW_HFSS_PYAEDT_VERDICT.md` 作为当前 HFSS 复核/排查记录，后续再按 backend 文档口径调整。
- 验证结果：
  - 本次仅登记文档待办，未修改 Python 脚本。
  - 未启动 ADS、HFSS/AEDT 或 FEM 仿真。
- 还需完成：
  - 实现 pipeline config 的 HFSS 段和 `--backend ads|hfss|both` 编排入口。
  - 泛化 run state machine 与 run/artifact manifest schema。
  - 将 HFSS 文档从 verdict-only 口径调整为标准 backend 口径，并保留 ADS/HFSS compare workflow。
- 关联文件：
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
  - `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`
  - `docs/flow/FLOW_HFSS_PYAEDT_VERDICT.md`
  - `src/simads/hfss/workflow.py`
- 下一步：
  - 先扩展 pipeline schema 和只读 check，再新增薄封装 runner 调用现有 ADS/HFSS 后端。

### ARCH-REFACTOR-TASK-20260801-053 - Pixel QR Independent No-Gap Branch

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 将二维码像素化滤波器作为独立项目维护，不再挂在 `projects/bfp_6_8g_i7_fr4/` 下。
  - 将相邻黑色像素的连接方式改为共边无间隙，不使用 `conn_h/conn_v` 补充连接图形。
  - 重新生成 R0 版图产物，并通过标准 pipeline 和 layout contract gate。
- 完成内容：
  - 更新 `tools/layout/generate_pixel_qr_bpf_layout.py`：`connect_adjacent_pixels=true` 时矩阵 pitch 等于 `pixel_mm`，相邻黑色像素天然共边贴合；删除相邻像素补充连接矩形生成逻辑。
  - no-gap 模式下馈线实际重叠量至少覆盖完整第一列像素，避免馈线和第二列像素之间出现小于 4 mil 的残缝。
  - 更新 `projects/pixel_qr_bpf_fr4_210um/plans/pixel_qr_bpf_fr4_210um_r0.csv`，候选改为 `pixel_qr8_fr4_210um_seed0_nogap` 与 `pixel_qr10_fr4_210um_seed1_nogap`。
  - 重新生成独立项目下的 DXF/SVG/layout JSON/params JSON/DRC。
  - 清理独立项目 layouts 目录中旧 `_conn` 补桥生成产物，避免后续 ADS 导入误选。
  - 清理 `projects/bfp_6_8g_i7_fr4/` 下误放的 `pixel_qr` layout/result/run 产物；未删除外部 ADS workspace 数据。
  - 更新 `docs/devices/二维码像素化带通滤波器设计报告.md`、`docs/README.md`、`docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md` 和 TODO。
- 验证结果：
  - `python -m py_compile tools\layout\generate_pixel_qr_bpf_layout.py tools\generate_pixel_qr_bpf_layout.py` 通过。
  - `python -m json.tool config\projects\pixel_qr_bpf_fr4_210um.json` 通过。
  - `python -m json.tool config\pipelines\pixel_qr_bpf_fr4_210um_v1.json` 通过。
  - `python tools\check_pipeline_contract.py --project-id pixel_qr_bpf_fr4_210um --pipeline-id pixel_qr_bpf_fr4_210um_v1 --profile company` 全部 PASS。
  - `python tools\check_layout_contract.py --project-id pixel_qr_bpf_fr4_210um --sweep-id pixel_qr_bpf_fr4_210um_r0 --pipeline-id pixel_qr_bpf_fr4_210um_v1 --candidate pixel_qr8_fr4_210um_seed0_nogap pixel_qr10_fr4_210um_seed1_nogap` 全部 PASS；最小分离间距分别为 `0.32 mm` 和 `0.24 mm`。
  - `rg` 检查确认独立项目当前 R0 layouts 中不再包含 `adjacent_pixel_bridge`、`conn_h_`、`conn_v_`、旧 `_conn` 产物或 `bridged` metadata。
  - `rg` 检查确认 `projects/bfp_6_8g_i7_fr4/` 下不再保留 `pixel_qr` 产物。
  - 未启动 ADS/FEM，未修改外部 ADS workspace。
- 还需完成：
  - 以 no-gap R0 候选执行单候选 ADS/FEM，判断是否形成带通雏形。
  - 根据 R0 FEM 响应决定 R1 是先调整 mask 开窗，还是引入接地/短路线像素以增加阻带零点。
- 关联文件：
  - `tools/layout/generate_pixel_qr_bpf_layout.py`
  - `tools/generate_pixel_qr_bpf_layout.py`
  - `config/projects/pixel_qr_bpf_fr4_210um.json`
  - `config/pipelines/pixel_qr_bpf_fr4_210um_v1.json`
  - `projects/pixel_qr_bpf_fr4_210um/plans/pixel_qr_bpf_fr4_210um_r0.csv`
  - `projects/pixel_qr_bpf_fr4_210um/layouts/pixel_qr_bpf_fr4_210um_r0/`
  - `docs/devices/二维码像素化带通滤波器设计报告.md`
  - `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 使用 `pixel_qr_bpf_fr4_210um` 独立 pipeline 选择一个 no-gap 候选执行 ADS/FEM 单点验证。

### ARCH-REFACTOR-TASK-20260801-052 - Pixel QR Topology Layout Gate

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 在通用 layout contract gate 之外，为 pixel QR BPF 分支增加拓扑专项机器检查。
  - 保证独立 checker 和 sweep runner 使用同一套 gate 口径。
  - 不启动 ADS/FEM，不修改外部 ADS workspace。
- 完成内容：
  - `src/simads/geometry/validation.py` 新增 `validate_pixel_qr_bpf_layout()`，检查 `topology`、`mask_rows`、matrix/source_map 完整性、P1/P2 馈线、边缘像素耦合、最小金属间距和孤岛统计。
  - `tools/check_layout_contract.py` 新增 `--topology-check`、`--min-metal-spacing-mm`、`--max-island-components`，pixel QR 分支默认自动追加专项检查。
  - `tools/run_ads_filter_sweep.py` 的内嵌 layout gate 同步执行 pixel QR 拓扑专项检查。
  - 重新生成 `projects/bfp_6_8g_i7_fr4/layouts/pixel_qr_bpf_fr4_210um_r0/` 下两个 R0 样例，使 `_layout.json` 携带 `layer_map_version=profile-default-v1`。
  - 更新 `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`、`docs/arch/PYTHON_SCRIPT_MANAGEMENT.md` 和 TODO。
- 验证结果：
  - `python -m py_compile src\simads\geometry\validation.py src\simads\geometry\__init__.py tools\check_layout_contract.py tools\run_ads_filter_sweep.py` 通过。
  - `python tools\check_layout_contract.py --project-id bfp_6_8g_i7_fr4 --sweep-id pixel_qr_bpf_fr4_210um_r0 --pipeline-id bfp_6_8g_pixel_qr_fr4_v1 --candidate pixel_qr8_fr4_210um_seed0 pixel_qr10_fr4_210um_seed1` 通过。
  - `python tools\run_ads_filter_sweep.py --project-id bfp_6_8g_i7_fr4 --sweep-id pixel_qr_bpf_fr4_210um_r0 --pipeline-id bfp_6_8g_pixel_qr_fr4_v1 --skip-generate --skip-fem --dry-run --candidates pixel_qr8_fr4_210um_seed0` 通过，dry-run 输出包含 `pixel_qr.*` 专项检查项。
  - 检查结果显示 R0 样例最小间距分别约为 `0.12 mm` 和 `0.102 mm`，均不低于当前默认 `0.1016 mm`；孤岛数量仅统计和输出，正式阈值待 FEM 和工艺策略确定后再收紧。
  - 未启动 ADS/FEM，未修改外部 ADS workspace。
- 还需完成：
  - 根据第一次 pixel QR FEM 响应和板厂制造策略设置 `max_island_components` 推荐阈值。
  - 为 folded SIR、高低阻抗 SIR、RO4350 高抑制分支建立独立 pipeline config 和对应 topology-specific layout gate。
- 关联文件：
  - `src/simads/geometry/validation.py`
  - `src/simads/geometry/__init__.py`
  - `tools/check_layout_contract.py`
  - `tools/run_ads_filter_sweep.py`
  - `projects/bfp_6_8g_i7_fr4/layouts/pixel_qr_bpf_fr4_210um_r0/`
  - `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`
  - `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 继续把 folded SIR、高低阻抗 SIR、RO4350 高抑制分支纳入独立 pipeline config，并按拓扑补专用 gate。

### ARCH-REFACTOR-TASK-20260801-051 - Standard Pipeline Layout Contract Gate

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 将标准 pipeline 的 layout JSON 规则纳入机器校验。
  - 在 sweep 流程中把 layout contract gate 放到候选生成之后、ADS 导入之前。
  - 保持 `--skip-generate`、`--dry-run` 等旧产物调试路径可诊断。
- 完成内容：
  - 新增 `src/simads/geometry/validation.py`，检查 `units`、声明层、已使用层、`source_map/generator`、`P1/P2`、端口落铜、过孔层、过孔焊盘/落铜和 `layer_map_version`。
  - 新增 `tools/check_layout_contract.py`，支持直接检查 `_layout.json` 或按 candidate/out-dir 自动定位。
  - `config/pipelines/bfp_6_8g_i7_fr4_interdigital_v1.json` 新增 `layer_map_version=profile-default-v1`。
  - `tools/layout/generate_interdigital_filter_layout.py` 输出 layout metadata 中记录 `layer_map_version`。
  - `tools/run_ads_filter_sweep.py` 新增默认 layout gate，并提供 `--skip-layout-check` 与 `--strict-layout-check`。
  - `tools/run_ads_filter_candidate.py` 在 run manifest/artifact manifest 中记录 `layout_json` 输入。
  - 更新 `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`、`docs/data/DATA_RUN_MANIFEST_SCHEMA.md`、`docs/arch/PYTHON_SCRIPT_MANAGEMENT.md` 和 TODO。
- 验证结果：
  - `python -m py_compile src\simads\config\pipelines.py src\simads\geometry\__init__.py src\simads\geometry\validation.py tools\check_layout_contract.py tools\run_ads_filter_sweep.py tools\run_ads_filter_candidate.py tools\layout\generate_interdigital_filter_layout.py tools\layout\generate_pixel_qr_bpf_layout.py tools\layout\generate_stub_bpf_layout.py tools\layout\generate_folded_sir_bpf_layout.py tools\layout\generate_hilo_sir_bpf_layout.py tools\layout\generate_paper_mixed_sir_bpf_layout.py` 通过。
  - `python tools\check_pipeline_contract.py --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1` 全部 PASS。
  - `python tools\check_pipeline_contract.py --project-id bfp_6_8g_i7_fr4 --sweep-id pixel_qr_bpf_fr4_210um_r0 --pipeline-id bfp_6_8g_pixel_qr_fr4_v1 --profile company` 全部 PASS。
  - 临时生成 `layout_contract_smoke_layout.json` 后，`python tools\check_layout_contract.py .tmp\layout_contract_smoke\layout_contract_smoke_layout.json --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1` 全部 PASS。
  - 临时生成 pixel QR R0 layout JSON 后，`python tools\check_layout_contract.py --project-id bfp_6_8g_i7_fr4 --sweep-id pixel_qr_bpf_fr4_210um_r0 --pipeline-id bfp_6_8g_pixel_qr_fr4_v1 --out-dir .tmp\pixel_qr_layout_contract_smoke --candidate pixel_qr8_fr4_210um_seed0 pixel_qr10_fr4_210um_seed1` 全部 PASS。
  - `python tools\run_ads_filter_sweep.py --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1 --skip-generate --skip-fem --dry-run --candidates i7_fr4_r7_bo04` 通过，旧候选缺 `_layout.json` 时输出 WARN 后继续 dry-run。
  - 未启动 ADS/FEM，未修改外部 ADS workspace。
- 还需完成：
  - 为 folded SIR、高低阻抗 SIR、RO4350 高抑制分支建立独立 pipeline config 和拓扑专用 layout gate。
- 关联文件：
  - `src/simads/geometry/validation.py`
  - `src/simads/geometry/__init__.py`
  - `tools/check_layout_contract.py`
  - `tools/run_ads_filter_sweep.py`
  - `tools/run_ads_filter_candidate.py`
  - `tools/layout/generate_interdigital_filter_layout.py`
  - `config/pipelines/bfp_6_8g_i7_fr4_interdigital_v1.json`
  - `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`
  - `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
- 下一步：
  - 继续把标准 pipeline contract 扩展为多分支配置，优先处理 folded SIR 和高低阻抗 SIR。

### ARCH-REFACTOR-TASK-20260801-050 - QR-like Pixelated BPF R0 Branch

- 状态：进行中
- 日期：2026-08-01
- 任务目标：
  - 调研二维码式二值像素化微带滤波器资料，形成 FR4 210um 设计报告。
  - 建立 8x8、10x10 初版版图生成能力，并纳入标准 pipeline 分支。
  - 不启动 ADS/FEM，不修改外部 ADS workspace。
- 完成内容：
  - 新增 `docs/devices/二维码像素化带通滤波器设计报告.md`，归纳 pixelated / binary-coded / inverse-designed microstrip filter 文献路线。
  - 新增 `tools/layout/generate_pixel_qr_bpf_layout.py`，支持 `qr_seed`、`checker`、`diag`、`edge_coupled`、`symmetric_random` 二值 mask，输出 DXF/SVG/layout JSON/params JSON/DRC。
  - 新增根目录兼容入口 `tools/generate_pixel_qr_bpf_layout.py`。
  - 新增 `config/pipelines/bfp_6_8g_pixel_qr_fr4_v1.json`，固定 mm、`cond/pcvia1/EM_BOUNDARY`、P1/P2、4-10 GHz 和 `fr4_25db_rl6` 评分 profile。
  - 新增 `projects/bfp_6_8g_i7_fr4/plans/pixel_qr_bpf_fr4_210um_r0.csv`。
  - `config/projects/bfp_6_8g_i7_fr4.json` 登记 `pixel_qr_bpf_fr4_210um_r0` sweep。
  - `src/simads.devices` 登记 `filter.pixel_qr_bpf` device plugin。
  - `src/simads.config.pipelines.validate_pipeline()` 支持同一 project 下默认 pipeline 与注册 sweep pipeline 并存。
  - 生成 `pixel_qr8_fr4_210um_seed0` 和 `pixel_qr10_fr4_210um_seed1` 两个 R0 样例。
- 验证结果：
  - `python -m py_compile src\simads\devices\__init__.py src\simads\config\pipelines.py tools\layout\generate_pixel_qr_bpf_layout.py tools\generate_pixel_qr_bpf_layout.py` 通过。
  - `python -m json.tool config\projects\bfp_6_8g_i7_fr4.json` 通过。
  - `python -m json.tool config\pipelines\bfp_6_8g_pixel_qr_fr4_v1.json` 通过。
  - `python tools\generate_pixel_qr_bpf_layout.py --plan projects\bfp_6_8g_i7_fr4\plans\pixel_qr_bpf_fr4_210um_r0.csv --out-dir projects\bfp_6_8g_i7_fr4\layouts\pixel_qr_bpf_fr4_210um_r0` 通过。
  - `python tools\check_pipeline_contract.py --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1 --profile company` 通过。
  - `python tools\check_pipeline_contract.py --project-id bfp_6_8g_i7_fr4 --sweep-id pixel_qr_bpf_fr4_210um_r0 --pipeline-id bfp_6_8g_pixel_qr_fr4_v1 --profile company` 通过。
  - 未启动 ADS/FEM，未修改外部 ADS workspace。
- 还需完成：
  - 对 R0 样例执行 ADS 导入和单候选 FEM，确认是否形成带通响应。
  - 通用 layout contract gate 已覆盖 `port_on_metal`、`source_map/generator`、层、端口和过孔焊盘/落铜；还需新增像素化分支专用 layout/DRC 机器校验，覆盖孤岛统计、最小间距、feed/pixel 连通性和 matrix `source_map` 完整性。
  - 根据 FEM 结果决定后续 DBS/GA 二值翻转或先调整 feed overlap、pixel/gap。
- 关联文件：
  - `docs/devices/二维码像素化带通滤波器设计报告.md`
  - `tools/layout/generate_pixel_qr_bpf_layout.py`
  - `tools/generate_pixel_qr_bpf_layout.py`
  - `config/pipelines/bfp_6_8g_pixel_qr_fr4_v1.json`
  - `config/projects/bfp_6_8g_i7_fr4.json`
  - `projects/bfp_6_8g_i7_fr4/plans/pixel_qr_bpf_fr4_210um_r0.csv`
  - `projects/bfp_6_8g_i7_fr4/layouts/pixel_qr_bpf_fr4_210um_r0/`
  - `src/simads/devices/__init__.py`
  - `src/simads/config/pipelines.py`
- 下一步：
  - 先用 10x10 样例做 ADS 导入和短 FEM，再决定是否进入 R1 参数扫描。

### ARCH-REFACTOR-TASK-20260801-049 - Standard Pipeline Contract

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 统一 SIM 项目中的版图生成器、ADS 导入脚本、emSetup/RFPro FEM、数据导出和评分器。
  - 固定模板、层映射、单位、端口规则、频段和评分 profile。
  - 将 pipeline 约束写入 TODO，并开始接入 runner 和校验脚本。
- 完成内容：
  - 新增 `config/pipelines/bfp_6_8g_i7_fr4_interdigital_v1.json`，固定 `mm`、`cond/pcvia1/EM_BOUNDARY`、`P1/P2`、`em%Setup/emSetup`、`4-10 GHz`、`fr4_25db_rl6` 和标准脚本路径。
  - `config/projects/bfp_6_8g_i7_fr4.json` 与 active sweep 新增 `pipeline_id`。
  - 新增 `src/simads/config/pipelines.py`，提供 pipeline dataclass、loader、id 解析和校验函数。
  - `tools/run_ads_filter_candidate.py` 新增 `--pipeline-id`，从 pipeline contract 解析脚本路径、模板、view、层名、target profile 和 score version，并写入 `run_manifest`。
  - `tools/run_ads_filter_sweep.py` 新增 `--pipeline-id`，传递 pipeline 到 candidate runner，并在 summary/失败记录中保留 `pipeline_id`。
  - `tools/analyze_ads_dataset.py` 新增 `--pipeline-id`，score CSV 可回填 pipeline 元数据。
  - 新增 `tools/check_pipeline_contract.py`，只读检查标准 pipeline，不启动 ADS/FEM。
  - 新增 `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`，并更新 README、TODO 和 Python 脚本管理文档。
- 验证结果：
  - `python -m py_compile src\simads\config\projects.py src\simads\config\pipelines.py src\simads\config\__init__.py tools\run_ads_filter_candidate.py tools\run_ads_filter_sweep.py tools\analyze_ads_dataset.py tools\check_pipeline_contract.py` 通过。
  - `python tools\check_pipeline_contract.py --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1` 全部 PASS。
  - `python tools\run_ads_filter_sweep.py --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1 --skip-generate --skip-fem --dry-run --candidates i7_fr4_r7_bo04` 通过，命令已传递 `--pipeline-id`。
  - `python tools\run_ads_filter_candidate.py i7_fr4_r7_bo04 --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1 --skip-fem --dry-run` 通过，内部命令已使用 `tools/ads/` 标准脚本路径。
  - 未启动 ADS/FEM，未修改外部 ADS workspace。
- 还需完成：
  - 为 folded SIR、高低阻抗 SIR、RO4350 高抑制分支建立独立 pipeline config。
- 关联文件：
  - `config/pipelines/bfp_6_8g_i7_fr4_interdigital_v1.json`
  - `config/projects/bfp_6_8g_i7_fr4.json`
  - `src/simads/config/pipelines.py`
  - `src/simads/config/projects.py`
  - `src/simads/config/__init__.py`
  - `tools/check_pipeline_contract.py`
  - `tools/run_ads_filter_candidate.py`
  - `tools/run_ads_filter_sweep.py`
  - `tools/analyze_ads_dataset.py`
  - `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
  - `docs/README.md`
- 下一步：
  - 为 folded SIR、高低阻抗 SIR、RO4350 高抑制分支建立独立 pipeline config。

### ARCH-REFACTOR-TASK-20260801-048 - Tools Phase 1 Script Split

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 将首批 `tools` 脚本按功能域迁移到 `tools/ads/` 和 `tools/layout/`。
  - 保留根目录兼容 wrapper，避免现有 CLI 调用断裂。
  - 同步更新 TODO 和任务记录，明确 tools 迁移已经进入物理分拆阶段。
- 完成内容：
  - 迁移 `ads_import_dxf_add_ports.py`、`ads_clone_emsetup_template.py`、`ads_run_rfpro_fem.py`、`export_ads_fem_dataset.py` 到 `tools/ads/`。
  - 迁移 `generate_stub_bpf_layout.py`、`generate_interdigital_filter_layout.py`、`generate_folded_sir_bpf_layout.py`、`generate_hilo_sir_bpf_layout.py`、`generate_paper_mixed_sir_bpf_layout.py` 到 `tools/layout/`。
  - 在根目录保留同名兼容 wrapper，保持旧命令可继续调用。
  - 修正迁移后脚本的 `src/` 路径注入，使子目录脚本可直接运行。
  - 更新 `ARCH_REFACTOR_TODO.md`，把 P2-01/P2-02 的首批物理迁移标记为完成。
- 验证结果：
  - 已完成文档更新和代码迁移，未启动 ADS/FEM，未修改外部 ADS workspace。
  - 新旧入口均保留，迁移后脚本可继续通过原路径调用。
- 还需完成：
  - 继续把剩余 `tools` 脚本按 `maintenance/`、`opt/`、`scoring/`、`ads/`、`layout/` 分批拆分。
  - 后续评估是否将 `ads_profiles.py` 等兼容模块也整理进更明确的包边界。
- 关联文件：
  - `tools/ads/ads_import_dxf_add_ports.py`
  - `tools/ads/ads_clone_emsetup_template.py`
  - `tools/ads/ads_run_rfpro_fem.py`
  - `tools/ads/export_ads_fem_dataset.py`
  - `tools/layout/generate_stub_bpf_layout.py`
  - `tools/layout/generate_interdigital_filter_layout.py`
  - `tools/layout/generate_folded_sir_bpf_layout.py`
  - `tools/layout/generate_hilo_sir_bpf_layout.py`
  - `tools/layout/generate_paper_mixed_sir_bpf_layout.py`
- 下一步：
  - 继续迁移 remaining utility、scoring 和 optimizer 脚本。

### ARCH-REFACTOR-TASK-20260801-047 - Docs Phase 4 Root Cleanup

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 将 `docs/` 根目录收敛为仅保留 `README.md` 和子文件夹。
  - 把旧路径说明、兼容 CSV 和历史快照归档到 `docs/archive/`。
  - 不启动 ADS/FEM，不修改外部 ADS workspace。
- 完成内容：
  - 将 `docs/` 根目录除 `README.md` 外的文件整体迁入 `docs/archive/`。
  - 更新 `docs/README.md`，明确根目录仅保留主索引和子目录。
  - 更新 `ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`、`ARCH_DIRECTORY_GOVERNANCE.md` 和 `ARCH_REFACTOR_TODO.md` 的 Phase 4 口径。
- 验证结果：
  - 本任务仅修改文档和目录结构，未启动 ADS/FEM，未修改外部 ADS workspace。
  - `docs/` 根目录现仅保留 `README.md` 和子文件夹。
  - 旧路径引用扫描无新增命中，迁移表统计保持不变。
- 还需完成：
  - 继续维护 `docs/archive/` 中的历史说明和兼容快照。
  - 后续新增文档只进入目标子目录，不再回填 `docs/` 根目录。
- 关联文件：
  - `docs/README.md`
  - `docs/arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`
  - `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 视需要继续整理 `docs/archive/` 的历史材料索引。

### ARCH-REFACTOR-TASK-20260801-046 - Docs Phase 3 Architecture Migration

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 将主框架、`ARCH_*.md` 和 `PYTHON_SCRIPT_MANAGEMENT.md` 迁移到 `docs/arch/`。
  - 保留旧根路径兼容入口，并逐步更新历史引用。
  - 不启动 ADS/FEM，不修改外部 ADS workspace。
- 完成内容：
  - 创建 `docs/arch/`。
  - 迁移 `ADS版图自动仿真项目框架设计.md`、`ARCH_*.md`、`PYTHON_SCRIPT_MANAGEMENT.md` 到 `docs/arch/`。
  - 旧 Markdown 路径改为 Deprecated stub，指向新 Canonical。
  - `ARCH_ADS_ASSET_MIGRATION_20260801.csv` 和 `ARCH_DOCS_MIGRATION_20260801.csv` 的 canonical 版本进入 `docs/arch/`，旧路径保留同字段兼容 CSV 指针。
  - 更新 README 的 canonical 主文档、项目阅读树、分支阅读规则、进度记录路由和快速查找规则。
  - 更新架构规划和 TODO，将 Phase 3 标记为完成，下一步切换为 Phase 4 准备。
  - 修复 `docs/arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md` 的迁移替换污染，恢复为 UTF-8 正文并补回 Phase 3 状态。
  - 修复 `docs/arch/ARCH_DOCS_MIGRATION_20260801.csv` 的 `old_path` 追溯字段，保留迁移前根目录路径。
  - 主文档、项目文档和已迁移文档中的架构文档旧根路径引用执行第一轮保守替换，统一指向 `docs/arch/`。
- 验证结果：
  - 本任务仅修改文档和迁移索引，未启动 ADS/FEM，未修改外部 ADS workspace。
  - 已按 UTF-8 读取和修改 Markdown/CSV 文档。
  - `docs/arch/ARCH_DOCS_MIGRATION_20260801.csv` 状态统计为 `moved+stubbed=28`、`moved+compat_csv=2`、`kept=1`。
  - 污染词扫描无命中；非兼容文件中的架构文档旧根路径引用扫描无命中。
  - 旧 Markdown 根路径均保留 Deprecated stub；旧 CSV 根路径保留同字段兼容指针。
- 还需完成：
  - Phase 4：完成一个优化周期后，确认无旧路径直接引用再清理 stub 和兼容 CSV。
  - 后续可评估是否拆分 `ARCH_REFACTOR_TASK_PROGRESS.md` 为阶段日志。
- 关联文件：
  - `docs/arch/ADS版图自动仿真项目框架设计.md`
  - `docs/arch/ARCH_ADS_ASSET_MIGRATION_20260801.md`
  - `docs/arch/ARCH_ADS_ASSET_MIGRATION_20260801.csv`
  - `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`
  - `docs/arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`
  - `docs/arch/ARCH_DOCS_MIGRATION_20260801.csv`
  - `docs/arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
  - `docs/README.md`
- 下一步：
  - 执行 Phase 4 前的旧路径引用巡检，并持续从新路径维护文档。
### ARCH-REFACTOR-TASK-20260801-045 - Docs Phase 2 Core/Branch Migration

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 继续 `docs/` 物理分层迁移，完成数据、流程、优化、结果和器件分支文档迁移。
  - 保留旧路径 Deprecated stub，同时逐步更新 README、Related、主框架和项目文档中的历史引用。
  - 不启动 ADS/FEM，不修改外部 ADS workspace。
- 完成内容：
  - 创建 `docs/data/`、`docs/flow/`、`docs/opt/`、`docs/result/`、`docs/devices/`。
  - 迁移 `DATA_`、`FLOW_`、`OPT_`、`RESULT_` 文档到主应目标目录。
  - 迁移 `FR4高低阻抗带通滤波器优化TODO.md`、`FR4折叠SIR带通滤波器分支.md`、`交指带通滤波器回波损耗影响因素.md` 到 `docs/devices/`。
  - 在旧路径创建 Deprecated stub，指向新 Canonical。
  - 补齐三份器件分支文档的 Status、Domain、Canonical、Related 元数据。
  - 更新 `README.md` 主入口、项目阅读树、分支阅读规则和快速查找规则。
  - 更新 `ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`，将 Phase 2 标记为完成并把下一步切换为 Phase 3 准备。
  - 更新 `ARCH_REFACTOR_TODO.md`，标记 P1-11 的 Phase 2 完成。
  - 主文档和项目文档中的旧根目录引用执行第一轮保守替换；迁移 CSV 的 `old_path` 字段保持旧路径不变。
- 验证结果：
  - 本任务仅修改文档，未启动 ADS/FEM，未修改外部 ADS workspace。
  - 已按 UTF-8 读取和修改 Markdown/CSV 文档。
  - `ARCH_DOCS_MIGRATION_20260801.csv` 状态统计为 `moved+stubbed=20`、`planned=10`、`kept=1`。
  - Phase 2 新路径文档均已保留正文，旧路径均为 Deprecated stub。
- 还需完成：
  - Phase 3：迁移 `ARCH_*.md`、主框架和 `PYTHON_SCRIPT_MANAGEMENT.md`。
  - Phase 4：完成一个优化周期后，确认无旧路径引用再清理 stub。
- 关联文件：
  - `docs/data/DATA_SCHEMA_REGISTRY.md`
  - `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
  - `docs/flow/FLOW_RUN_STATE_MACHINE.md`
  - `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`
  - `docs/flow/FLOW_JOB_SCHEDULING_POLICY.md`
  - `docs/flow/FLOW_MANUAL_INTERVENTION_LOG.md`
  - `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`
  - `docs/opt/ROUND_SCRIPT_MIGRATION_PLAN.md`
  - `docs/opt/FR4交指滤波器搜索算法改进方案.md`
  - `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`
  - `docs/result/RESULT_BASELINE_FREEZE_POLICY.md`
  - `docs/devices/FR4高低阻抗带通滤波器优化TODO.md`
  - `docs/devices/FR4折叠SIR带通滤波器分支.md`
  - `docs/devices/交指带通滤波器回波损耗影响因素.md`
  - `docs/README.md`
  - `docs/arch/ARCH_DOCS_MIGRATION_20260801.csv`
  - `docs/arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 先评审 Phase 3 架构文档的迁移顺序，再迁移高频入口。

### ARCH-REFACTOR-TASK-20260801-044 - Docs Phase 1 Low-Risk Migration

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 开始 `docs/` 物理分层迁移。
  - 先迁移低风险辅助文档，不移动主框架、TODO、任务记录、DATA/FLOW/OPT/RESULT 核心规范。
  - 保留旧路径 stub，保护历史引用。
- 完成内容：
  - 创建 `docs/env/`、`docs/mfg/`、`docs/report/`、`docs/test/`、`docs/layout/`。
  - 迁移 `env/ENV_ADS_API_CAPABILITY_MATRIX.md` 和 `env/ENV_UV_COMPANY_20260801.md` 到 `docs/env/`。
  - 迁移 `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md` 到 `docs/mfg/`。
  - 迁移 `report/REPORT_TEMPLATE_PLAYBOOK.md` 到 `docs/report/`。
  - 迁移 `test/TEST_STRATEGY.md` 到 `docs/test/`。
  - 迁移 `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md` 到 `docs/layout/`。
  - 在旧路径创建 Deprecated stub，指向新 Canonical。
  - 更新新文件 `Canonical` 元数据，并修正 Phase 1 文档之间的部分 `Related` 引用。
  - 更新 `README.md` 中的主入口、项目阅读树、分支阅读规则和快速查找规则。
  - 更新 `ARCH_DOCS_MIGRATION_20260801.csv`，将 6 份文档标记为 `moved+stubbed`。
  - 更新 `ARCH_REFACTOR_TODO.md`，标记 Phase 1 第一批完成。
- 验证结果：
  - 本任务未启动 ADS/FEM，未修改外部 ADS workspace。
  - 已按 UTF-8 读取和修改 Markdown/CSV 文档。
  - 旧路径仍可打开 stub，新路径保留完整正文。
  - `ARCH_DOCS_MIGRATION_20260801.csv` 状态统计：`moved+stubbed=6`、`planned=24`、`kept=1`。
  - README 中已迁移文档的主入口已切换到 `env/`、`mfg/`、`report/`、`test/`、`layout/` 新路径。
- 还需完成：
  - 后续 Phase 2 再迁移 `DATA_`、`FLOW_`、`OPT_`、`RESULT_` 和器件分支文档。
  - 全局旧路径引用仍由 stub 兼容；Phase 2/3 时再逐步更新所有 Related 和正文引用。
- 关联文件：
  - `docs/env/ENV_ADS_API_CAPABILITY_MATRIX.md`
  - `docs/env/ENV_UV_COMPANY_20260801.md`
  - `docs/mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md`
  - `docs/report/REPORT_TEMPLATE_PLAYBOOK.md`
  - `docs/test/TEST_STRATEGY.md`
  - `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`
  - `docs/README.md`
  - `docs/arch/ARCH_DOCS_MIGRATION_20260801.csv`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 执行引用检查，确认 README 主入口、新旧路径 stub 和迁移映射表一致。

### ARCH-REFACTOR-TASK-20260801-043 - Docs Internal Architecture Planning

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 规划 `docs/` 内部目录架构，解决所有文档平铺在同一目录下不易管理的问题。
  - 先冻结目标结构、迁移阶段、旧路径保护和验收 gate，不立即物理移动文件。
  - 不启动 ADS/FEM，不修改外部 ADS workspace。
- 完成内容：
  - 新增 `ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`，定义 `arch/data/env/flow/layout/devices/opt/result/mfg/report/test/archive` 目标目录。
  - 在规划文档中为当前 28 个 docs 文件逐一登记目标目录和迁移优先级。
  - 定义 Phase 0-4 迁移路线：规划冻结、低风险文档迁移、核心规范迁移、架构文档迁移、旧路径清理。
  - 定义 docs 迁移映射表字段和旧路径 stub 模板。
  - 新增 `ARCH_DOCS_MIGRATION_20260801.csv`，登记当前 docs 文件到目标子目录的 planned/kept 映射。
  - 在 `README.md` 中新增“项目阅读树”，按平台总纲、环境、自动化闭环、数据契约、器件分支、优化制造测试、结果报告串联全项目。
  - 在 `ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md` 中规定每个分支必须具备 Branch entry、Layout source、Config binding、Automation flow、Data trace、Optimization trace、Decision/report 链路。
  - 更新 `ARCH_DIRECTORY_GOVERNANCE.md`，将原来的中期分层建议升级为引用本规划的分批迁移策略。
  - 更新 `ARCH_REFACTOR_TODO.md`，新增 P1-11 Docs Internal Architecture 待办。
  - 更新 `README.md`，加入本规划入口、目标目录结构和快速查找规则。
- 验证结果：
  - 本任务仅修改文档，未移动现有 docs 文件，未启动 ADS/FEM。
  - 已按 UTF-8 读取和修改 Markdown 文档。
- 还需完成：
  - Phase 1：从 `ENV_`、`MFG_`、`REPORT_`、`TEST_`、`LAYOUT_` 低风险文档开始迁移。
  - 每批迁移后执行引用检查，并为旧路径保留 stub。
- 关联文件：
  - `docs/arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`
  - `docs/arch/ARCH_DOCS_MIGRATION_20260801.csv`
  - `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/README.md`
- 下一步：
  - 决定是否开始 Phase 1 物理迁移；建议先迁 `ENV_`、`MFG_`、`REPORT_`、`TEST_`、`LAYOUT_` 低风险文档。

### ARCH-REFACTOR-TASK-20260801-042 - Framework Compliance Documentation Alignment

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 将框架符合性评审发现的文档偏差加入 TODO。
  - 修正公司电脑独立 SIM 目录后的主框架路径、环境说明、进度路由和 run 目录策略。
  - 不启动 ADS/FEM，不修改外部 ADS workspace。
- 完成内容：
  - `ARCH_REFACTOR_TODO.md` 新增 P1-10 Framework Compliance Alignment，登记路径漂移、run 目录过渡、generator 默认路径、device plugin contract、layout/source_map/DRC gate 等待办。
  - `docs/README.md` 当前根目录改为 `E:\OneDrive\4.Code\SIM`，进度记录路由改为现有 canonical 文档。
  - `ADS版图自动仿真项目框架设计.md` 增加 company ADS 环境说明，明确 `config/ads_profiles.json` 是 home/company 环境的唯一机器可读来源。
  - 主框架明确当前实现仍使用 `projects/<project_id>/results/<round>/runs/<run_id>/`，P1 再迁移到标准 `projects/<project_id>/runs/<run_id>/`。
  - 主框架 device contract 增补 `optimizer_bounds(project_context)`、`score_adapters(target_profile)`，并标记为 P1 contract 待办。
  - `data/DATA_RUN_MANIFEST_SCHEMA.md` 明确当前 runner 的兼容 run 目录和 P1 迁移方向。
- 验证结果：
  - 本任务仅修改文档，未启动 ADS/FEM，未写入外部 ADS workspace。
  - 已按 UTF-8 读取和修改 Markdown 文档。
- 还需完成：
  - 更新非交指 layout generator 默认输出目录。
  - 形式化 `DEVICE_PLUGIN_CONTRACT.md`。
  - 将 layout/source_map/DRC 机器 gate 接入 schema 检查。
  - P1 阶段将新 run 默认输出迁移到 `projects/<project_id>/runs/<run_id>/`。
- 关联文件：
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/README.md`
  - `docs/arch/ADS版图自动仿真项目框架设计.md`
  - `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
- 下一步：
  - 优先处理 generator 默认路径和 device plugin contract 文档，继续保持不启动真实仿真。

### ARCH-REFACTOR-TASK-20260801-041 - Deterministic Variant Config Probe

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 为历史 `make_i7_fr4_round*.py` 的经验扫描逻辑建立配置化迁移入口。
  - 先完成 deterministic variant schema、解释器和 validate-only CLI，不生成正式新候选，不启动 ADS/FEM。
- 完成内容：
  - 新增 `src/simads/optimizer/variants.py`，支持读取 deterministic variant 配置、加载 seed params、应用参数更新、生成 plan CSV 行。
  - 支持 `gaps_mm[0]`、`gaps_mm[5]` 等索引字段，用于迁移旧脚本中的主称/局部 gap 调整。
  - 新增 `tools/propose_filter_candidates.py`，作为统一候选生成入口的第一步，当前支持 `--validate-only`、`--dry-run` 和 `--out-plan`。
  - 新增 `config/optimizer/i7_fr4_deterministic_variant_probe.json`，用 round3 baseline 和 tw020 seed 表达 4 个代表性迁移探针。
  - 更新 `config/round_script_migration.json`，将 `tools/propose_filter_candidates.py` 登记为 deterministic variant 迁移入口。
  - 更新 `docs/opt/ROUND_SCRIPT_MIGRATION_PLAN.md`、`docs/README.md`、`docs/arch/PYTHON_SCRIPT_MANAGEMENT.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace，未生成正式候选版图。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m json.tool config\optimizer\i7_fr4_deterministic_variant_probe.json` 通过。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m py_compile src\simads\optimizer\variants.py src\simads\optimizer\__init__.py tools\propose_filter_candidates.py` 通过。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\propose_filter_candidates.py --validate-only` 通过，展开 4 个代表性变体。
- 还需完成：
  - 将 round2-round6 的完整历史变体逐项迁移到 deterministic variant 配置。
  - 将 unified CLI 与 active sweep optimizer 配置进一步打通，使 `strategy=deterministic_variants` 和 `strategy=surrogate_trust_region` 共用同一入口。
- 关联文件：
  - `src/simads/optimizer/variants.py`
  - `src/simads/optimizer/__init__.py`
  - `tools/propose_filter_candidates.py`
  - `config/optimizer/i7_fr4_deterministic_variant_probe.json`
  - `config/round_script_migration.json`
  - `docs/opt/ROUND_SCRIPT_MIGRATION_PLAN.md`
  - `docs/README.md`
  - `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 把 round2-round6 中仍有价值的手工变体分批搬入 deterministic variant 配置，并用 validate-only 做回归检查。

### ARCH-REFACTOR-TASK-20260801-040 - Round Script Migration Index Guard

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 将历史 round 候选脚本迁移索引变成可执行的静态检查 gate。
  - 在不启动 ADS/FEM、不移动旧脚本的前提下，约束后续迁移或归档动作。
- 完成内容：
  - 新增 `tools/check_round_script_migration.py`，读取 `config/round_script_migration.json`。
  - 检查 `scripts` 列表、必填字段、状态枚举、重复脚本和脚本路径存在性。
  - 自动扫描 `tools/make_*round*.py` 与 `tools/make_next_filter_candidates.py`，主未登记脚本输出 warning。
  - 更新 `docs/README.md`、`docs/arch/PYTHON_SCRIPT_MANAGEMENT.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`，将该检查纳入 optimizer/script governance gate。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace，未生成新候选文件。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m json.tool config\round_script_migration.json` 通过。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m py_compile tools\check_round_script_migration.py` 通过。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\check_round_script_migration.py` 通过，输出 `round script migration index: ok`。
- 还需完成：
  - 将 FR4 7 阶 round2-round6 的手工变体迁移为 deterministic variant config。
  - RO4350B 9 阶脚本后续按高抑制参考分支单独归档。
- 关联文件：
  - `config/round_script_migration.json`
  - `tools/check_round_script_migration.py`
  - `docs/opt/ROUND_SCRIPT_MIGRATION_PLAN.md`
  - `docs/README.md`
  - `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 设计 deterministic variant config schema，使历史 round2-round6 的经验扫描逻辑从专用脚本转为配置数据。

### ARCH-REFACTOR-TASK-20260801-039 - Active Sweep Optimizer Configuration

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 为 active sweep 增加候选生成器和 surrogate optimizer 配置入口。
  - 让当前 FR4 7 阶交指 round7 的 surrogate 候选脚本可从 project/sweep config 推导默认参数。
  - 不启动 ADS/FEM，不生成新候选文件。
- 完成内容：
  - `src/simads/config/projects.py` 的 `SweepConfig` 新增 `generator` 和 `optimizer` 字段。
  - project loader 主 `generator.script`、`generator.layout_generator`、`optimizer.script`、`optimizer.dataset`、`optimizer.seed_params`、`optimizer.prediction_report` 做 root-relative 路径解析。
  - `config/projects/bfp_6_8g_i7_fr4.json` 的 active sweep 新增 generator 配置：`tools/generate_filter_sweep.py` 和 `tools/generate_interdigital_filter_layout.py`。
  - active sweep 新增 optimizer 配置：`surrogate_trust_region`、training dataset、seed params、round name、count、pool count、random seed、exploration 和 prediction report。
  - `tools/propose_i7_fr4_surrogate_candidates.py` 新增 `--project-id` 和 `--sweep-id`。
  - surrogate 脚本的 dataset、seed params、out dir、plan、prediction report、round name、count、pool count、random seed、exploration 默认值改为从 active sweep optimizer 配置读取。
  - surrogate 脚本候选命名由 `round_name` 推导，例如 `round7 -> r7`，不再固定写死 `r7`。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，记录 active sweep optimizer 配置入口已完成，剩余 round 专用脚本迁移仍未完成。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace，未生成新候选文件。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m py_compile src\simads\config\projects.py tools\propose_i7_fr4_surrogate_candidates.py tools\run_ads_filter_sweep.py` 通过。
  - `load_project("bfp_6_8g_i7_fr4").get_sweep().optimizer` 正确读取 `surrogate_trust_region`、training dataset 和 `count=8`。
  - `tools\propose_i7_fr4_surrogate_candidates.py --help` 通过。
  - surrogate 模块默认值 smoke 通过：dataset、seed params、out dir、plan、prediction report、round name、count/pool/seed/exploration 均从 active sweep 推导。
  - `python -m json.tool config\projects\bfp_6_8g_i7_fr4.json` 通过。
  - sweep runner dry-run 仍通过，未显式传 target 时继续使用 `fr4_25db_rl6`。
- 还需完成：
  - 迁移或归档剩余 `make_i7_fr4_round*.py` 等 round 专用脚本。
  - 后续可将 surrogate 脚本中的参数列、目标列、bounds 和 targets 也放入 device/optimizer 配置。
- 关联文件：
  - `src/simads/config/projects.py`
  - `config/projects/bfp_6_8g_i7_fr4.json`
  - `tools/propose_i7_fr4_surrogate_candidates.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 整理 legacy round scripts，确定保留、迁移或归档策略。

### ARCH-REFACTOR-TASK-20260801-038 - Sweep Runner Defaults from Active Sweep

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 继续减少 `tools/run_ads_filter_sweep.py` 内部 round7 专用硬编码。
  - 让 sweep runner 的默认 plan、layout、result、summary、target 和 setup 信息从 project active sweep 读取。
  - 明确 OneDrive 共享环境下 project config 与 machine profile 的优先级，避免 home/company 配置混用。
- 完成内容：
  - `tools/run_ads_filter_sweep.py` 的 `--plan`、`--out-dir`、`--results-dir`、`--summary` 默认值改为 `None`，由 `apply_project_defaults()` 统一补齐。
  - 新增 `default_project_paths()`，仅在 project/sweep config 缺失时保留旧 round7 fallback。
  - 新增 `apply_project_defaults()`，按 active sweep 推导 plan、layout、result、summary、device、target、template、setup 和 RFPro emSetup view。
  - 补充 `tools/run_ads_filter_sweep.py` 的脚本自定位路径，使其既可直接运行，也可作为模块导入做 smoke。
  - 明确默认优先级：CLI 显式参数 > active sweep > current machine profile > project ads fallback > hardcoded fallback。
  - `--profile` 仍默认 `company`，不自动使用项目 JSON 中的 `default_profile=home`，避免公司电脑真实运行时被共享配置切换到家里环境。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，将 P2-06 中 sweep 默认值和 profile/project 优先级子项标记完成。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m py_compile tools\run_ads_filter_sweep.py` 通过。
  - 模块导入 smoke 通过：默认解析出 active sweep 的 `filter_opt_i7_fr4_round7.csv`、`fr4_25db_rl6`、`interdigital_9o_ro4350b_508um_v3_wide_mm_coords`、`em%Setup`、`emSetup` 和 `filter.interdigital`。
  - `tools\run_ads_filter_sweep.py --profile company --skip-generate --skip-fem --dry-run --candidates i7_fr4_r7_bo04` 通过；未显式传 plan/target/template 时仍生成 round7 命令，并传入 `--target-profile fr4_25db_rl6`。
  - 显式传入 `--target-profile ro4350_strict` 的 dry-run 通过，确认 CLI 参数仍可覆盖 active sweep 默认值。
- 还需完成：
  - P2-06 仍需建立独立 round/sweep 配置文件或 optimizer config，让 round 专用候选生成脚本逐步收敛。
  - 后续可将 `apply_project_defaults()` 继续拆入 `src/simads`，让 CLI 保持更薄。
- 关联文件：
  - `tools/run_ads_filter_sweep.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 设计 round/sweep 配置 schema，把候选生成器、参数边界、采样策略和结果目录纳入配置。

### ARCH-REFACTOR-TASK-20260801-037 - Project Config Loader and Sweep Device Propagation

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 继续推进 workflow 配置化，让 `config/projects/<project_id>.json` 成为项目资产目录的统一读取入口。
  - 保持单候选和 sweep runner CLI 兼容，不启动 ADS/FEM。
  - 将 sweep runner 的 device plugin 信息传递到 candidate runner 和后续 manifest。
- 完成内容：
  - 新增 `src/simads/config/projects.py`。
  - 新增 `ProjectConfig`、`ProjectFrequency`、`ProjectAdsConfig`、`SweepConfig`、`load_project()`、`project_names()`、`default_project_config_path()` 和 `root_relative_path()`。
  - project config 读取使用 `utf-8-sig`，兼容 UTF-8/BOM 文档。
  - `config/projects/bfp_6_8g_i7_fr4.json` 新增 `active_sweep` 和 `sweeps.interdigital_7o_fr4_round7`，登记 round7 的 plan、layout、result、summary、target、device 和 setup 默认值。
  - `src/simads/config/__init__.py` 导出 project config loader API。
  - `tools/run_ads_filter_candidate.py` 的 `project_dirs()` 改为调用 `load_project()`，仍保留配置缺失时的旧 fallback。
  - `tools/run_ads_filter_sweep.py` 新增 `--sweep-id` 和 `--device-id`，choices 来自 `simads.devices.list_devices()`；未显式指定 device 时读取 active sweep 的 `device_id`，再 fallback 到 project config 的 `primary_device_type` 和 `filter.interdigital`。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，新增 P2-06 Workflow / Project Config 配置化待办。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m py_compile src\simads\config\projects.py src\simads\config\__init__.py tools\run_ads_filter_candidate.py tools\run_ads_filter_sweep.py` 通过。
  - `load_project("bfp_6_8g_i7_fr4")` 正确解析 `projects/bfp_6_8g_i7_fr4` 下的 plans/layouts/results/runs/reports/references 目录，并读取 active sweep。
  - `tools\run_ads_filter_sweep.py --profile company --target-profile fr4_25db_rl6 --skip-generate --skip-fem --dry-run --candidates i7_fr4_r7_bo04` 通过，输出命令包含 `--device-id filter.interdigital`，且未启动 FEM。
  - `tools\run_ads_filter_candidate.py smoke_candidate --score-only --dry-run --profile company --target-profile fr4_25db_rl6` 通过，默认 run/results 目录仍来自项目配置。
  - `tools\run_ads_filter_sweep.py --help` 和 `tools\run_ads_filter_candidate.py --help` 通过。
- 还需完成：
  - sweep runner 的 plan/out/results/summary 默认值仍有 round7 专用硬编码，后续应由 project config + round config 推导。
  - `config/projects/bfp_6_8g_i7_fr4.json` 中 `ads` 块仍保留 home/BFP 默认；在公司电脑真实运行时应继续以 `company` profile 为准，后续需要明确优先级或环境覆盖策略。
  - P2-03 中 `round 专用脚本收敛为 optimizer 配置` 仍未完成。
- 关联文件：
  - `src/simads/config/projects.py`
  - `src/simads/config/__init__.py`
  - `config/projects/bfp_6_8g_i7_fr4.json`
  - `tools/run_ads_filter_candidate.py`
  - `tools/run_ads_filter_sweep.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 增加 round/sweep config schema，把 plan/out/results/summary 和 target profile 从 CLI 默认值进一步收敛到配置。
  - 再处理 project config 的 ADS 块与 machine profile 的优先级，避免 home/company 共享配置误导真实运行。

### ARCH-REFACTOR-TASK-20260801-036 - Profile Config File as Source of Truth

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 消除 `config/ads_profiles.json` 与 `src/simads/config/profiles.py` 同时维护 profile 的漂移风险。
  - 保持旧 `tools/ads_profiles.py` wrapper 和现有 profile API 兼容。
- 完成内容：
  - `src/simads/config/profiles.py` 新增 `load_profile_data()`、`load_profiles()`、`profile_from_mapping()`、`default_config_path()`。
  - `profiles.py` 优先读取 `config/ads_profiles.json`，源码默认 profile 仅作为配置文件缺失时的 fallback。
  - profile JSON 使用 `utf-8-sig` 读取，兼容带 BOM 的 UTF-8 配置文件。
  - `AdsProfile` 新增 `ads_python_path`，支持显式配置 ADS Python；未配置时仍回退到 `ads_root/tools/python/python.exe`。
  - `substrate_library` 支持从 `substrate` 的 `library:name` 格式自动推导。
  - `src/simads/config/__init__.py` 导出新增 config loader API。
  - 更新 `docs/env/ENV_UV_COMPANY_20260801.md`，明确后续公司/家里电脑切换优先维护 `config/ads_profiles.json`。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m py_compile src\simads\config\profiles.py tools\ads_profiles.py tools\check_ads_profile.py tools\run_ads_filter_candidate.py` 通过。
  - `profile_names()` 返回 `company/home`。
  - `get_ads_profile("company").to_dict()` 正确读取公司 UV host Python：`D:\Microsoft\Python\ads-automation\Scripts\python.exe`。
  - `get_ads_profile("company").to_dict()` 正确从 `6-8G_Fillter_lib:substrate1` 推导 `substrate_library=6-8G_Fillter_lib`。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\check_ads_profile.py --profile company` 通过。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\run_ads_filter_candidate.py smoke_candidate --score-only --dry-run --profile company --target-profile fr4_25db_rl6` 通过；host_python 仍指向公司 UV 环境。
  - 在公司电脑检查 `home` profile 时，home host/workspace/library/layer_map 为 WARN，符合家里电脑独立环境的预期。
- 还需完成：
  - 如未来需要在不同电脑自动选择 profile，可增加 host identity/环境变量选择策略。
  - 后续 profile schema 可加入 `machine_id` 或 `environment_id`，避免 OneDrive 共享配置误用于错误电脑。
- 关联文件：
  - `config/ads_profiles.json`
  - `src/simads/config/profiles.py`
  - `src/simads/config/__init__.py`
  - `docs/env/ENV_UV_COMPANY_20260801.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 继续推进 workflow 配置化：让 project config、device_id、target profile、layout/result/run 目录成为单候选和 sweep runner 的统一来源。

### ARCH-REFACTOR-TASK-20260801-035 - Company UV Editable Environment

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 按公司电脑环境要求，在 `D:\Microsoft\Python` 下建立 UV host Python 环境。
  - 保持家里电脑原有 UV 环境配置不变。
  - 将 company profile 切换到新的 UV 环境，并完成 editable install 验证。
- 完成内容：
  - 新建 UV 环境：`D:\Microsoft\Python\ads-automation`。
  - 执行 editable 安装：`uv pip install --python D:\Microsoft\Python\ads-automation\Scripts\python.exe -e ".[optimizer,reports]"`。
  - 安装依赖：`numpy`、`scipy`、`scikit-learn`、`pandas`、`matplotlib` 及其依赖。
  - 更新 `config/ads_profiles.json`：`company.host_python` 改为 `D:/Microsoft/Python/ads-automation/Scripts/python.exe`。
  - 更新 `src/simads/config/profiles.py`：company `automation_python` 改为 `D:\Microsoft\Python\ads-automation\Scripts\python.exe`。
  - 新增 `docs/env/ENV_UV_COMPANY_20260801.md`，记录创建命令、配置差异、验证结果和 `uv pip freeze` 清单。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，将 P2-05 editable 安装、版本记录和兼容验证标记为完成。
- 验证结果：
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\check_editable_install.py --require-editable` 通过。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\check_ads_profile.py --profile company` 通过。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe -m py_compile tools\run_ads_filter_candidate.py src\simads\config\profiles.py src\simads\devices\__init__.py` 通过。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\run_ads_filter_candidate.py smoke_candidate --score-only --dry-run --profile company --target-profile fr4_25db_rl6` 通过；host_python 指向新 UV 环境，未启动 ADS/FEM。
  - `D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\propose_i7_fr4_surrogate_candidates.py --help` 通过。
  - `uv pip freeze --python D:\Microsoft\Python\ads-automation\Scripts\python.exe` 通过，清单已写入 `docs/env/ENV_UV_COMPANY_20260801.md`。
- 还需完成：
  - 后续真实 ADS/FEM 运行前，如切换回家里电脑，应确认 `home` profile 仍指向家里既有 UV 环境。
  - 当前公司 venv 未安装 `pip` 模块，包管理以 `uv pip ... --python D:\Microsoft\Python\ads-automation\Scripts\python.exe` 为准。
- 关联文件：
  - `config/ads_profiles.json`
  - `src/simads/config/profiles.py`
  - `docs/env/ENV_UV_COMPANY_20260801.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - P2 主体已完成到 editable 环境闭环；后续可进入 runner workflow 配置化或 ADS Python profile/API smoke。

### ARCH-REFACTOR-TASK-20260801-034 - P2-05 Editable Install Preflight Check

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 在不修改 Python 环境的前提下，补充 P2-05 editable install 的预检查入口。
  - 识别当前公司电脑 host Python 的包安装状态和常用依赖缺口。
- 完成内容：
  - 新增 `tools/check_editable_install.py`。
  - 检查当前 Python、项目根、`simads` import、`sim-ads-automation` distribution、PEP 660 editable `direct_url.json` 和常用依赖 import。
  - 输出当前 Python 主应的 editable install 建议命令，但脚本本身不执行安装。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，新增 P2-05 无副作用检查脚本子项。
  - 更新 `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`，登记 `check_editable_install.py` 为 host stable smoke 脚本。
- 验证结果：
  - 本任务未安装依赖，未修改 Python/uv/conda 环境。
  - `python -m py_compile tools\check_editable_install.py` 通过。
  - `python tools\check_editable_install.py` 通过并输出当前公司环境：
    - Python：`D:\Microsoft\Miniconda\python.exe`
    - `simads` import：missing
    - `sim-ads-automation` installed：no
    - `numpy/scipy/pandas/matplotlib` 可导入
    - `sklearn` 缺失
    - 建议安装命令：`"D:\Microsoft\Miniconda\python.exe" -m pip install -e "E:\OneDrive\4.Code\SIM"`
- 还需完成：
  - 目标 host/uv 环境 editable install 已在 `ARCH-REFACTOR-TASK-20260801-035` 完成。
- 关联文件：
  - `tools/check_editable_install.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 由用户决定是否在公司电脑当前 Miniconda 或指定 uv venv 中执行 editable install；未确认前继续避免修改环境。

### ARCH-REFACTOR-TASK-20260801-033 - Candidate Runner Device Registry and Project Defaults

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 将 `run_ads_filter_candidate.py` 接入只读 device registry 校验。
  - 修正 candidate runner 的历史默认输出路径，优先使用项目配置中的 `projects/<project_id>/...` 资产边界。
- 完成内容：
  - `tools/run_ads_filter_candidate.py` 新增 `--device-id`，默认 `filter.interdigital`，choices 来自 `simads.devices.list_devices()`。
  - run manifest 新增 `device_id` 和 `device_plugin` 快照，记录 family、端口、默认 layer、builder module、params class、layout builder 和 output writer。
  - candidate flow 日志增加 `device_id`。
  - 新增 `project_dirs()`，读取 `config/projects/<project_id>.json` 的 `layouts_dir/results_dir/runs_dir`。
  - 配置 JSON 使用 `utf-8-sig` 读取，兼容带 BOM 的 UTF-8 文件。
  - 默认 DXF/params 查找优先走 `projects/bfp_6_8g_i7_fr4/layouts`，旧 `ADS/` 仅作为历史 fallback。
  - 默认 RFPro CSV、score CSV 和 run 目录改为项目配置下的 `results` 和 `runs`。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\run_ads_filter_candidate.py` 通过。
  - `python tools\run_ads_filter_candidate.py --help` 通过，CLI 保持兼容并新增 `--device-id {filter.folded_sir,filter.hilo_sir,filter.interdigital,filter.stub}`。
  - `--score-only --dry-run --device-id filter.folded_sir` 通过；打印的默认路径为 `projects\bfp_6_8g_i7_fr4\results` 和 `projects\bfp_6_8g_i7_fr4\runs`，不再默认写向旧 `ADS\results`。
- 还需完成：
  - 后续让 candidate runner 通过 device plugin 的 `normalize_params()` 或 adapter 统一调用版图生成器。
  - 旧 `default_candidate_files()` 的 recursive glob 只是兼容查找，后续应由 project manifest 或 plan 明确指向 layout artifact。
- 关联文件：
  - `tools/run_ads_filter_candidate.py`
  - `src/simads/devices/__init__.py`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 评估 P2-05 editable install；若暂不改环境，则先补充安装检查脚本或文档化 company/home Python 配置差异。

### ARCH-REFACTOR-TASK-20260801-032 - P2-04 Additional Filter Plugin Registration

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 继续完成 P2-04，让已有 folded SIR、high-low SIR 和 stub 版图生成器进入同一 Device Plugin Registry。
  - 仅登记 plugin 元数据和 adapter 入口，不迁移生成器实现，不启动 ADS/FEM。
- 完成内容：
  - 在 `src/simads/devices/__init__.py` 中新增 `filter.folded_sir` plugin。
  - 在 `src/simads/devices/__init__.py` 中新增 `filter.hilo_sir` plugin。
  - 在 `src/simads/devices/__init__.py` 中新增 `filter.stub` plugin。
  - 四个 filter plugin 统一记录 `device_id`、`family`、参数 schema、端口、默认 layer、target profile 和旧生成器 adapter 元数据。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，将 P2-04 全部子项标记为完成。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile src\simads\devices\__init__.py` 通过。
  - normal-Python registry smoke 通过：`list_devices()` 返回 `filter.folded_sir`、`filter.hilo_sir`、`filter.interdigital`、`filter.stub`。
  - plugin 元数据 smoke 通过：四个 plugin 均有 builder module、params class 和 parameter schema；folded/high-low/stub 兼容旧生成器默认参数习惯，只提供 `name` 时不误报。
- 还需完成：
  - 将主流程 `run_ads_filter_candidate.py` 接入只读 device registry 校验。
  - 后续如要真正用 registry 调用生成器，需要建立统一 `params_from_row()` 或 `normalize_params()` adapter。
- 关联文件：
  - `src/simads/devices/__init__.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 推进 P2-05 editable 安装记录；或先把 candidate runner 加入 device_id 校验，但保持旧 CLI 参数兼容。

### ARCH-REFACTOR-TASK-20260801-031 - P2-04 Device Plugin Registry Skeleton

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-04，将 Device Plugin Contract 落到代码层。
  - 先注册现有交指滤波器器件，不迁移 ADS/FEM 主流程，不破坏旧版图生成 CLI。
- 完成内容：
  - 新增 `src/simads/devices/__init__.py`。
  - 定义 `ParameterSpec`、`DevicePlugin`、`DeviceRegistry`、`get_device()` 和 `list_devices()`。
  - 注册第一个内置 plugin：`filter.interdigital`。
  - `filter.interdigital` 记录端口名、默认 layer、target profile、优化边界，以及旧生成器 adapter 元数据：`generate_interdigital_filter_layout.FilterParams/build_layout/write_outputs`。
  - 参数 schema 兼容现有 round plan：候选向量字段为必填，完整 `FilterParams` 的材料/层叠/DRC 字段作为可选字段登记。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，将 P2-04 中 `simads.devices` 和 `filter.interdigital` 注册项标记为完成。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile src\simads\devices\__init__.py` 通过。
  - normal-Python registry smoke 通过：`list_devices()` 返回 `filter.interdigital`，参数 schema 共 `37` 项，默认 metal layer 为 `cond`。
  - 使用现有 FR4 交指优化参数列构造的候选行通过 `validate_parameter_row()`，无误报。
- 还需完成：
  - `filter.folded_sir`、`filter.hilo_sir`、`filter.stub` 等生成器按同一接口注册已在 `ARCH-REFACTOR-TASK-20260801-032` 完成。
  - 后续把 `run_ads_filter_candidate.py` 的 device selection 接入 registry，让主流程通过 `device_id` 查找 layout writer。
  - 进一步把旧交指生成器内部的重复几何 helper 收敛到 `simads.geometry/exporters/devices`。
- 关联文件：
  - `src/simads/devices/__init__.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 注册 folded SIR、high-low SIR、stub 的 device plugin 元数据；或先把 `run_ads_filter_candidate.py` 增加只读 device registry 校验，不改变候选运行行为。

### ARCH-REFACTOR-TASK-20260801-030 - P2-03 Scoring and Optimizer Extraction

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-03，将 S 参数评分和候选优化中的普通 Python 逻辑抽入 `src/simads`。
  - 保持旧 CLI 入口兼容，不启动 ADS/FEM，不写入外部 ADS workspace。
- 完成内容：
  - 新增 `src/simads/scoring/__init__.py`，集中 `TARGET_PROFILES`、score version、频率列/S 参数列识别、dB 转换、插值和 target profile 评分逻辑。
  - `tools/analyze_ads_dataset.py` 转接到 `simads.scoring`，ADS `.ds` 读取仍保留在脚本内的 ADS-only 函数中。
  - 修正 RFPro CSV 读取兼容性：使用 `utf-8-sig` 读取，并通过列名识别支持带 BOM 或非严格 `frequency_hz/s21_db` 表头。
  - 新增 `src/simads/optimizer/__init__.py`，抽出 FR4 交指滤波器候选优化所需的参数列、指标列、目标、边界、几何去重、标准化、bootstrap ridge ensemble、EI/PI、可行 gate 和候选筛选。
  - `tools/propose_i7_fr4_surrogate_candidates.py` 转接到 `simads.optimizer.select_surrogate_candidates()`，保留原 CSV 读写、版图生成和 CLI 参数。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，将 P2-03 中 scoring 和 optimizer 模块化子项标记为完成。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile src\simads\scoring\__init__.py tools\analyze_ads_dataset.py` 通过。
  - RFPro CSV 评分 smoke 通过：临时 UTF-8/BOM CSV 输出完整 score 行，`status=PASS_CANDIDATE`，run/project/round/candidate/profile/target/score_version 元数据均写入。
  - `python -m py_compile src\simads\optimizer\__init__.py tools\propose_i7_fr4_surrogate_candidates.py` 通过。
  - `python tools\propose_i7_fr4_surrogate_candidates.py --help` 通过，CLI 参数保持兼容。
  - 纯内存 optimizer smoke 通过：使用假训练样本完成 best 识别和 1 个候选选择，不生成 DXF、不写项目结果。
- 还需完成：
  - 将 round 专用脚本继续收敛为 optimizer 配置，减少 `propose_i7_fr4_surrogate_candidates.py` 内的器件专用常量和遗留重复函数。
  - 后续如引入 EI/PI、可行概率的多器件配置，需要纳入 device plugin contract。
- 关联文件：
  - `src/simads/scoring/__init__.py`
  - `src/simads/optimizer/__init__.py`
  - `tools/analyze_ads_dataset.py`
  - `tools/propose_i7_fr4_surrogate_candidates.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 进入 P2-04：建立 `simads.devices` plugin contract；或继续清理 round 专用脚本，把参数列、目标、边界、候选命名和输出路径改为配置驱动。

### ARCH-REFACTOR-TASK-20260801-029 - P2-02 Main CLI Consolidated Smoke

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 主 P2-02 主流程旧 ADS CLI 的薄转接做集中验证。
  - 明确 `ads_probe_ael_words.py` 作为 ADS-only 诊断脚本保留，不纳入普通 Python helper 转接范围。
- 完成内容：
  - 集中验证 layout import、emSetup clone、RFPro FEM、dataset export 四类命令计划均可由 `simads.ads` 构造。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`：主流程旧 ADS CLI 的纯路径/计划/解析 helper 已转接到 `simads.ads`。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\ads_import_dxf_add_ports.py tools\ads_clone_emsetup_template.py tools\ads_run_rfpro_fem.py tools\export_ads_fem_dataset.py src\simads\ads\__init__.py src\simads\ads\workspace.py src\simads\ads\layout.py src\simads\ads\emsetup.py src\simads\ads\rfpro.py src\simads\ads\dataset.py` 通过。
  - normal-Python smoke 通过：解析临时 interdigital DXF 得到 `33` 个 DXF entity，从 `_layout.json` 读取 P1/P2，并构造四类命令计划：`ads_import_dxf_add_ports`、`ads_clone_emsetup_template`、`ads_run_rfpro_fem`、`export_ads_fem_dataset`。
  - `tools` 中现有 `ads_*.py` 为 `ads_clone_emsetup_template.py`、`ads_import_dxf_add_ports.py`、`ads_probe_ael_words.py`、`ads_profiles.py`、`ads_run_rfpro_fem.py`；其中 `ads_profiles.py` 已是兼容转发层，`ads_probe_ael_words.py` 为 ADS-only 探测脚本。
- 还需完成：
  - 在 ADS Python 环境中增加 profile/API smoke，不启动 FEM。
  - P2-02 若后续继续深化，应把 Keysight API 调用放入 ADS-only adapter 层，普通 Python 模块继续保持无 Keysight 依赖。
- 关联文件：
  - `src/simads/ads/*`
  - `tools/ads_import_dxf_add_ports.py`
  - `tools/ads_clone_emsetup_template.py`
  - `tools/ads_run_rfpro_fem.py`
  - `tools/export_ads_fem_dataset.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 进入 P2-03：抽出 scoring/optimizer；或先按环境条件补 ADS Python profile/API smoke。

### ARCH-REFACTOR-TASK-20260801-028 - RFPro CLI Helper Adapter

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-02，将 `tools/ads_run_rfpro_fem.py` 中可普通 Python 验证的 cell/substrate/XML helper 转接到 `simads.ads`。
  - 保持 RFPro view 创建、更新、FEM 运行和 CSV 导出主流程不变。
- 完成内容：
  - `src/simads/ads/rfpro.py` 新增 `substrate_file_exists()`、`normalize_substrate_info()` 和 `patch_rfpro_setup_xml()`。
  - `src/simads/ads/__init__.py` 导出 RFPro substrate/XML helper。
  - `tools/ads_run_rfpro_fem.py` 改用 `simads.ads.workspace.find_cell_dir()` 解析 ADS cell 目录。
  - `tools/ads_run_rfpro_fem.py` 改用 `simads.ads.rfpro.normalize_substrate_info()` 处理 substrate library fallback。
  - `tools/ads_run_rfpro_fem.py` 改用 `simads.ads.rfpro.patch_rfpro_setup_xml()` 修改已有 RFPro setup XML。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-02 转接状态。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\ads_run_rfpro_fem.py src\simads\ads\rfpro.py src\simads\ads\workspace.py src\simads\ads\__init__.py` 通过。
  - `python tools\ads_run_rfpro_fem.py --help` 通过，CLI 参数保持原样。
  - 纯 Python XML fixture smoke 通过：`patch_rfpro_setup_xml()` 将 substrate lib/name 从旧值改为新值并返回 `True`。
- 还需完成：
  - ADS Python 环境 smoke 仍未执行；后续应只检查 import/profile/API 可用性，不启动 FEM。
  - 真实 RFPro/FEM 调用仍在旧脚本中，后续如需进一步模块化，应放入 ADS-only adapter，避免普通 Python import Keysight 包失败。
- 关联文件：
  - `tools/ads_run_rfpro_fem.py`
  - `src/simads/ads/rfpro.py`
  - `src/simads/ads/workspace.py`
  - `src/simads/ads/__init__.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 主 P2-02 做一次集中 py_compile/smoke；随后可进入 P2-03 scoring/optimizer 抽象，或先补 ADS Python profile/API smoke。

### ARCH-REFACTOR-TASK-20260801-027 - DXF Import CLI Helper Adapter

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-02，将 `tools/ads_import_dxf_add_ports.py` 中可普通 Python 验证的 DXF parser 和端口读取 helper 转接到 `simads.ads.layout`。
  - 保持 ADS 导入、fallback layout 创建和 pin 添加主流程不变。
- 完成内容：
  - `src/simads/ads/layout.py` 新增 `dxf_group_pairs()` 和 `parse_generated_dxf_subset()`。
  - `src/simads/ads/__init__.py` 导出 `parse_generated_dxf_subset()`。
  - `tools/ads_import_dxf_add_ports.py` 移除本地 DXF group parser 和 generated-DXF subset parser。
  - `tools/ads_import_dxf_add_ports.py` 改用 `load_p1_p2_locations()` 读取端口坐标，兼容旧 params JSON 和新 `_layout.json`。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-02 转接状态。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\ads_import_dxf_add_ports.py src\simads\ads\layout.py src\simads\ads\__init__.py` 通过。
  - `python tools\ads_import_dxf_add_ports.py --help` 通过，CLI 参数保持原样。
  - 纯 Python smoke 通过：解析临时 interdigital DXF，得到 `solid=11`、`circle=18`、`line=4`。
- 还需完成：
  - 将 ADS layout 创建、padstack 和 pin 添加适配层进一步隔离到 ADS-only module。
  - 后续可让导入流程优先读取 `_layout.json`，减少主 DXF 反解析的依赖。
- 关联文件：
  - `tools/ads_import_dxf_add_ports.py`
  - `src/simads/ads/layout.py`
  - `src/simads/ads/__init__.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 转接 `tools/ads_run_rfpro_fem.py` 中可普通 Python 验证的 workspace/cell/substrate XML helper，真实 RFPro 调用继续留在 ADS/RFPro 上下文中。

### ARCH-REFACTOR-TASK-20260801-026 - EM Setup Clone Helper Adapter

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-02，将 `tools/ads_clone_emsetup_template.py` 中可普通 Python 验证的 helper 转接到 `simads.ads`。
  - 不改变 emSetup XML patch 主流程、文件复制行为和 CLI 参数。
- 完成内容：
  - `src/simads/ads/layout.py` 新增 `load_p1_p2_locations()`，兼容旧 params JSON 和新 `_layout.json` 的端口读取。
  - `src/simads/ads/__init__.py` 导出 `load_p1_p2_locations()`。
  - `tools/ads_clone_emsetup_template.py` 改用 `simads.ads.workspace.find_cell_dir()` 解析 ADS cell 目录。
  - `tools/ads_clone_emsetup_template.py` 改用 `simads.ads.layout.load_p1_p2_locations()` 读取 P1/P2。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-02 转接状态。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\ads_clone_emsetup_template.py src\simads\ads\layout.py src\simads\ads\workspace.py src\simads\ads\__init__.py` 通过。
  - `python tools\ads_clone_emsetup_template.py --help` 通过，CLI 参数保持原样。
  - 纯 Python smoke 通过：从临时 interdigital `_layout.json` 读取 `P1=(-3.0, 2.143)`、`P2=(16.4126, 2.143)`。
- 还需完成：
  - 将 XML patch 字段规则进一步抽到 `simads.ads.emsetup`，并建立 XML fixture smoke。
  - ADS Python 环境 smoke 仍未执行，后续只做 API/profile 检查，不启动 FEM。
- 关联文件：
  - `tools/ads_clone_emsetup_template.py`
  - `src/simads/ads/layout.py`
  - `src/simads/ads/workspace.py`
  - `src/simads/ads/__init__.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 转接 `tools/ads_import_dxf_add_ports.py` 的 DXF subset parser 和端口读取 helper，后续让 layout import 优先消费 `_layout.json`。

### ARCH-REFACTOR-TASK-20260801-025 - Dataset Export CLI Thin Adapter

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-02，将最容易纯 Python 验证的 ADS dataset 导出 CLI 转接到 `simads.ads.dataset`。
  - 保持 `tools/export_ads_fem_dataset.py` 旧 CLI 参数和输出格式兼容。
- 完成内容：
  - `src/simads/ads/dataset.py` 新增 `delimiter_text()`、`write_full_table()`、`write_ads_display_like_table()` 和 `write_dataset_export()`。
  - `tools/export_ads_fem_dataset.py` 移除重复的 `db_from_mag()`、`phase_deg()`、`dataset_path()` 和表格写出函数，改为从 `simads.ads.dataset` 导入。
  - `tools/export_ads_fem_dataset.py` 保留 ADS dataset 读取逻辑，Keysight API import 仍只发生在 `read_fem_data()` 内部。
  - `src/simads/ads/__init__.py` 补充导出 dataset helper。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-02 转接状态。
- 验证结果：
  - 本任务未启动 ADS/FEM，未读取真实 ADS `.ds`。
  - `python -m py_compile tools\export_ads_fem_dataset.py src\simads\ads\dataset.py src\simads\ads\__init__.py` 通过。
  - `python tools\export_ads_fem_dataset.py --help` 通过，CLI 参数保持原样。
  - 纯 Python smoke 通过：构造假 S 参数行，`write_dataset_export()` 成功输出 ADS display 风格 txt 和 full CSV。
- 还需完成：
  - 将 `tools/ads_import_dxf_add_ports.py`、`tools/ads_clone_emsetup_template.py`、`tools/ads_run_rfpro_fem.py` 的纯路径/计划逻辑逐步转接到 `simads.ads`。
  - ADS Python 环境 smoke 仍未执行，后续只做 API/profile 检查，不启动 FEM。
- 关联文件：
  - `tools/export_ads_fem_dataset.py`
  - `src/simads/ads/dataset.py`
  - `src/simads/ads/__init__.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 优先转接 `tools/ads_clone_emsetup_template.py` 中 ADS cell 目录查找和端口读取 helper，降低 emSetup clone 脚本内的重复逻辑。

### ARCH-REFACTOR-TASK-20260801-024 - ADS API Planning Submodules Skeleton

- 状态：进行中
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-02，建立 ADS API 相关子模块的 normal-Python 计划层。
  - 不启动 ADS，不导入 Keysight API，不写入外部 ADS workspace。
- 完成内容：
  - 新增 `src/simads/ads/workspace.py`：`AdsCellRef`、`AdsCommandPlan`、ADS 大写 cell 目录编码和 cell 目录解析。
  - 新增 `src/simads/ads/layout.py`：`LayoutImportPlan`、layout JSON 读取、端口位置读取和 DXF 导入命令计划。
  - 新增 `src/simads/ads/emsetup.py`：`EmSetupClonePlan` 和 emSetup clone 命令计划。
  - 新增 `src/simads/ads/rfpro.py`：`RfproFemPlan` 和 RFPro FEM 命令计划。
  - 新增 `src/simads/ads/dataset.py`：FEM dataset 路径规则、导出计划、dB/phase helper 和 dataset 导出命令计划。
  - 新增 `src/simads/ads/__init__.py` 统一导出计划层 API。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-02 骨架状态，并保留旧 CLI 转接和 ADS Python smoke 后续项。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile src\simads\ads\__init__.py src\simads\ads\workspace.py src\simads\ads\layout.py src\simads\ads\emsetup.py src\simads\ads\rfpro.py src\simads\ads\dataset.py` 通过。
  - normal-Python smoke 通过：从 `_layout.json` 读取 P1/P2，构造 layout import、emSetup clone、RFPro FEM 和 dataset export 四类命令计划。
  - 主照现有旧 CLI 参数后，已将 emSetup 参数保持为 `--points-text`，RFPro 参数保持为 `--start/--stop/--out`。
- 还需完成：
  - 将 `tools/ads_import_dxf_add_ports.py`、`tools/ads_clone_emsetup_template.py`、`tools/ads_run_rfpro_fem.py`、`tools/export_ads_fem_dataset.py` 内部纯逻辑逐步转接到 `simads.ads`。
  - 在 ADS Python 环境中执行 profile/API smoke，但仍不启动 FEM。
  - 后续真实 ADS API 适配层应显式隔离 Keysight import，避免普通 Python 环境导入失败。
- 关联文件：
  - `src/simads/ads/__init__.py`
  - `src/simads/ads/workspace.py`
  - `src/simads/ads/layout.py`
  - `src/simads/ads/emsetup.py`
  - `src/simads/ads/rfpro.py`
  - `src/simads/ads/dataset.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 选择一个旧 ADS CLI 做薄入口转接，建议从 `tools/export_ads_fem_dataset.py` 开始，因为 dataset 路径和导出格式最容易纯 Python 验证。

### ARCH-REFACTOR-TASK-20260801-023 - Remaining SIR Generators Geometry Adapter

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 收口 P2-01，将剩余 SIR layout generator 接入通用 geometry。
  - 保持 legacy DXF/SVG 输出兼容，同时为后续 ADS API 放置端口、制造检查和数据集构建提供统一 `_layout.json`。
- 完成内容：
  - `tools/generate_hilo_sir_bpf_layout.py` 新增 `src` 路径注入和 `build_layout()`。
  - `hilo` 生成器将矩形金属、EM 边界和 P1/P2 端口转换为 `LayoutRect`、`Boundary`、`Port`。
  - `tools/generate_paper_mixed_sir_bpf_layout.py` 新增 `src` 路径注入和 `build_layout()`。
  - `paper_mixed` 生成器将方形 via pad 保留为 `rect`，将 `ground_via_*` 转换为 `Via`，并输出 P1/P2 端口。
  - 两个脚本的 `write_outputs()` 均新增 `_layout.json` 输出。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，P2-01 已完成。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\generate_stub_bpf_layout.py tools\generate_interdigital_filter_layout.py tools\generate_folded_sir_bpf_layout.py tools\generate_hilo_sir_bpf_layout.py tools\generate_paper_mixed_sir_bpf_layout.py src\simads\geometry\__init__.py src\simads\exporters\json.py` 通过。
  - `python tools\generate_hilo_sir_bpf_layout.py --out-dir $env:TEMP\simads_hilo_sir_migrate_smoke` 通过，输出包含 `hilo_sir_l3_base_layout.json`。
  - `python tools\generate_paper_mixed_sir_bpf_layout.py --out-dir $env:TEMP\simads_paper_sir_migrate_smoke` 通过，输出包含 `paper_sir_ro4350_r0_base_layout.json`。
  - 抽查 `_layout.json`：`hilo` 为 `rect=17`、`boundary=1`、`ports=2`；`paper_mixed` 为 `rect=16`、`via=3`、`boundary=1`、`ports=2`。
- 还需完成：
  - P2-01 已收口；legacy DXF writer 尚未替换为 common DXF writer，后续需要 golden/hash 主比后再做。
  - 下一阶段可推进 P2-02 ADS API 子模块，优先读取 `_layout.json` 作为自动导入、端口放置和 FEM setup 的结构化输入。
- 关联文件：
  - `tools/generate_hilo_sir_bpf_layout.py`
  - `tools/generate_paper_mixed_sir_bpf_layout.py`
  - `src/simads/geometry/__init__.py`
  - `src/simads/exporters/json.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 推进 P2-02：建立 `simads.ads.workspace/layout/emsetup/rfpro` 子模块骨架，并让 ADS 自动流程优先消费 `_layout.json`。

### ARCH-REFACTOR-TASK-20260801-022 - Folded SIR Generator Geometry Adapter

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-01，将 folded SIR 分支生成器接入通用 layout geometry。
  - 保留 folded SIR 的独立方形 via pad 语义，避免和交指滤波器的圆形 via pad 规则混淆。
- 完成内容：
  - `tools/generate_folded_sir_bpf_layout.py` 新增 `src` 路径注入，支持直接运行。
  - 新增 `build_layout()`，将旧 `Rect`、`Quad` 和 ports 转换为 `LayoutRect`、`Polygon`、`Via`、`Port` 和 `Boundary`。
  - 方形 via pad 保留为 top-metal `rect`；钻孔单独表达为 `via`。
  - `write_outputs()` 新增 `_layout.json` 输出，使用 `simads.exporters.json.write_layout_json()`。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-01 迁移状态。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\generate_folded_sir_bpf_layout.py src\simads\geometry\__init__.py src\simads\exporters\json.py` 通过。
  - `python tools\generate_folded_sir_bpf_layout.py --help` 通过。
  - `python tools\generate_folded_sir_bpf_layout.py --out-dir $env:TEMP\simads_folded_sir_migrate_smoke` 通过，输出包含 `folded_sir_l3_base_layout.json`。
  - 抽查 `_layout.json`：`rect=16`、`via=3`、`polygon=2`、`boundary=1`、`ports=2`，三处接地孔和三处方形 pad 均保留。
- 还需完成：
  - 迁移 `tools/generate_hilo_sir_bpf_layout.py` 和 `tools/generate_paper_mixed_sir_bpf_layout.py`。
  - 后续可把方形 via pad、圆形 via pad、half-outside via 等 pad 规则收敛为制造规则 helper。
- 关联文件：
  - `tools/generate_folded_sir_bpf_layout.py`
  - `src/simads/geometry/__init__.py`
  - `src/simads/exporters/json.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 迁移剩余 SIR generator，并评估是否可以提取 `legacy_shapes_to_layout()` 公共转换 helper。

### ARCH-REFACTOR-TASK-20260801-021 - Interdigital Generator Geometry Adapter

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-01，将当前主线使用价值较高的交指滤波器 layout generator 接入通用几何主象。
  - 保留原有 ADS DXF/SVG/params/drc/tuning 输出，先新增结构化 layout JSON，不直接替换 legacy DXF writer。
- 完成内容：
  - `tools/generate_interdigital_filter_layout.py` 新增 `src` 路径注入，支持直接运行。
  - 新增 `build_layout()`，将旧 `Rect`、`Quad` 转换为 `LayoutRect`、`Polygon`、`Via`、`Port` 和 `Boundary`。
  - via pad 在通用几何中表达为 `Via.pad_diameter/pad_layer`，避免在 layout JSON 里继续把孔焊盘伪装成矩形。
  - 新增 P1/P2 端口主象，记录端口号、坐标、线宽和金属层。
  - `write_outputs()` 新增 `_layout.json` 输出，使用 `simads.exporters.json.write_layout_json()`。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-01 迁移状态。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\generate_interdigital_filter_layout.py src\simads\geometry\__init__.py src\simads\exporters\json.py` 通过。
  - `python tools\generate_interdigital_filter_layout.py --help` 通过。
  - 默认参数临时输出通过，生成 `interdigital_9o_ro4350b_508um_layout.json`；抽查包含 `rect=11`、`via=9`、`boundary=1`、`ports=2`。
  - taper 临时输出通过，`Quad` 正确进入 layout JSON，抽查包含 `polygon=2`。
- 还需完成：
  - 迁移 `tools/generate_folded_sir_bpf_layout.py`、`tools/generate_hilo_sir_bpf_layout.py` 和 `tools/generate_paper_mixed_sir_bpf_layout.py`。
  - 后续可把端口和 via 规则抽为设备无关 helper，供 ADS API 自动放置和制造检查复用。
- 关联文件：
  - `tools/generate_interdigital_filter_layout.py`
  - `src/simads/geometry/__init__.py`
  - `src/simads/exporters/json.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 继续迁移 folded SIR 生成器，优先保留 legacy DXF writer 并新增结构化 `_layout.json`。

### ARCH-REFACTOR-TASK-20260801-020 - Stub BPF Generator Geometry Adapter

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-01 的旧 layout generator 迁移试点。
  - 在不改变 `tools/generate_stub_bpf_layout.py` 原有 CLI 和 ADS DXF 输出路径的前提下，接入通用 `simads.geometry.Layout`。
- 完成内容：
  - `tools/generate_stub_bpf_layout.py` 新增 `src` 路径注入，支持直接从仓库根目录运行。
  - 新增 `build_layout()`，将旧 `Rect` 列表转换为通用 `LayoutRect`、`Via` 和 `Boundary`。
  - 新增 `LayerMap` 和 layout metadata，记录 generator、topology、substrate、Er、介质厚度和铜厚。
  - `write_outputs()` 新增 `_layout.json` 输出，使用 `simads.exporters.json.write_layout_json()`。
  - 保留原有 DXF/SVG/params/drc/dimension_check 输出逻辑，避免影响已验证过的 ADS 导入路径。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-01 迁移状态。
- 验证结果：
  - 本任务未启动 ADS/FEM，未写入外部 ADS workspace。
  - `python -m py_compile tools\generate_stub_bpf_layout.py src\simads\geometry\__init__.py src\simads\exporters\json.py` 通过。
  - `python tools\generate_stub_bpf_layout.py --help` 通过。
  - `python tools\generate_stub_bpf_layout.py --out-dir $env:TEMP\simads_stub_migrate_smoke` 通过，输出包含 `fr4_ssb_step_r_base_layout.json`。
  - 抽查 `_layout.json`：主线和支节为 `rect`，接地孔为 `via`，边界层进入 `layers`。
- 还需完成：
  - 迁移 `tools/generate_interdigital_filter_layout.py`、`tools/generate_folded_sir_bpf_layout.py`、`tools/generate_hilo_sir_bpf_layout.py` 和 `tools/generate_paper_mixed_sir_bpf_layout.py`。
  - 后续可建立 legacy DXF 与 common DXF 的 golden/hash 主比，再决定是否统一替换 DXF writer。
- 关联文件：
  - `tools/generate_stub_bpf_layout.py`
  - `src/simads/geometry/__init__.py`
  - `src/simads/exporters/json.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 继续迁移一个复杂度中等的 generator，建议选择 `tools/generate_interdigital_filter_layout.py` 并先保留 legacy DXF writer。

### ARCH-REFACTOR-TASK-20260801-019 - Geometry / Exporters Skeleton

- 状态：进行中
- 日期：2026-08-01
- 任务目标：
  - 推进 P2-01，建立通用 geometry 和 exporters 模块。
  - 先新增可复用基础能力，不改动现有 `tools/generate_*_layout.py` 行为。
- 完成内容：
  - 新增 `src/simads/geometry/__init__.py`。
  - 定义 `LayerMap`、`Rect`、`Polygon`、`Path`、`Via`、`Port`、`Boundary`、`Layout` 和通用 `bounds/min_feature/to_dict` helper。
  - 新增 `src/simads/exporters/__init__.py`。
  - 新增 DXF、SVG、JSON exporter。
  - 新增可选 GDS exporter；未安装 `gdstk` 时明确抛出 `ExportDependencyError`，不伪造 GDS 输出。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md` 中 P2-01 前两项。
- 验证结果：
  - 本任务未启动 ADS/FEM，未修改旧 CLI 默认行为。
  - `python -m py_compile src\simads\geometry\__init__.py src\simads\exporters\__init__.py src\simads\exporters\dxf.py src\simads\exporters\svg.py src\simads\exporters\json.py src\simads\exporters\gds.py` 通过。
  - 纯 Python geometry/export smoke 通过：临时样例成功导出 `smoke.json`、`smoke.dxf`、`smoke.svg`。
- 还需完成：
  - 将 `tools/generate_interdigital_filter_layout.py`、`tools/generate_stub_bpf_layout.py`、`tools/generate_folded_sir_bpf_layout.py` 等逐步迁移到通用 geometry/exporters。
  - 为 DXF/SVG 输出建立 golden 或 hash 测试，避免迁移时改变版图。
- 关联文件：
  - `src/simads/geometry/__init__.py`
  - `src/simads/exporters/__init__.py`
  - `src/simads/exporters/dxf.py`
  - `src/simads/exporters/svg.py`
  - `src/simads/exporters/json.py`
  - `src/simads/exporters/gds.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 选择一个最小生成器进行兼容迁移，建议先从 `tools/generate_stub_bpf_layout.py` 开始。

### ARCH-REFACTOR-TASK-20260801-018 - Report Template Playbook

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P1-08，建立 HTML/PDF 报告模板、发布 gate、导出检查和冻结规则。
  - 让报告必须引用 manifest、score、曲线、版图资产、target profile、baseline 和制造 gate。
- 完成内容：
  - 新增 `docs/report/REPORT_TEMPLATE_PLAYBOOK.md`。
  - 定义报告类型、报告目录、必填元数据、内容结构和 REPORT-GATE-01 到 REPORT-GATE-12。
  - 定义 HTML 模板要求、PDF 导出流程、`report_manifest.json` 草案、勘误和版本规则。
  - 明确不同材料、阶数、拓扑或目标约束不得混写到同一报告结论。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - 本任务只涉及文档和索引更新，未启动 ADS/FEM，也未导出 PDF。
  - `report/REPORT_TEMPLATE_PLAYBOOK.md` 已加入 README 主文档入口和快速查找规则。
  - P1-08 TODO 已勾选。
- 还需完成：
  - P2 阶段可实现 report manifest 生成器、HTML/PDF 链接检查和 score/plot 一致性检查脚本。
  - 后续正式报告导出时，应按该 playbook 和外部模板打印规则执行。
- 关联文件：
  - `docs/report/REPORT_TEMPLATE_PLAYBOOK.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - P1 文档 gate 基本补齐，后续可转向 P2 模块化迁移或先实现 report/manifest lint。

### ARCH-REFACTOR-TASK-20260801-017 - Manual GUI Intervention Log

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P1-07，建立 ADS GUI 人工介入记录模板。
  - 记录人工操作的时间、主象、动作、原因、截图/导出文件和复现影响。
- 完成内容：
  - 新增 `docs/flow/FLOW_MANUAL_INTERVENTION_LOG.md`。
  - 定义人工介入适用场景：手动导入、端口/via 修正、emSetup/RFPro 修改、点击 simulate、DDS/TXT/CSV 导出和残留清理。
  - 定义 `L0_readonly_review/L1_manual_export/L2_manual_patch/L3_destructive_cleanup` 四级介入等级。
  - 提供 `manual_intervention.md` Markdown 模板和 JSON schema 草案。
  - 定义 run manifest 中 `manual_intervention` 兼容字段建议，以及训练集和报告影响规则。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - 本任务只涉及文档和索引更新，未启动 ADS/FEM。
  - `flow/FLOW_MANUAL_INTERVENTION_LOG.md` 已加入 README 主文档入口和快速查找规则。
  - P1-07 TODO 已勾选。
- 还需完成：
  - P2 阶段可把 manual intervention 字段写入 `run_manifest.json`，并让训练集构建脚本识别 `affects_training_dataset`。
  - 后续真实 GUI 介入时，应在 run 目录或项目 intervention 目录落地实例记录。
- 关联文件：
  - `docs/flow/FLOW_MANUAL_INTERVENTION_LOG.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 推进 P1-08：建立 report release gate，HTML/PDF 报告引用 manifest、score、曲线、版图资产和 target profile。

### ARCH-REFACTOR-TASK-20260801-016 - Manufacturing Tolerance Robustness Plan

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P1-06，建立制造容差和材料漂移鲁棒性检查计划。
  - 明确 FR4 分支 release candidate 前必须区分 nominal pass 和 robust pass。
- 完成内容：
  - 新增 `docs/mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md`。
  - 定义制造和材料扰动变量：Er、tanD、介质厚度、铜厚、线宽、间距、长度、过渡、via 和主位。
  - 定义 DRC gate、one-at-a-time sensitivity、corner sweep 和 Monte Carlo 四级扫描。
  - 定义 `nominal_fail/nominal_pass/robust_warn/robust_pass/robust_fail` 状态。
  - 固化 FR4 7 阶交指分支的 robust gate、参数影响方向、输出产物和自动化接入建议。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - 本任务只涉及文档和索引更新，未启动 ADS/FEM。
  - `mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md` 已加入 README 主文档入口和快速查找规则。
  - P1-06 TODO 已勾选。
- 还需完成：
  - P2 阶段实现 `src/simads.mfg` 和 tolerance sweep 脚本。
  - 后续 release candidate 报告应引用 nominal 与 worst-case 指标，未做 tolerance sweep 时不得标记为 release candidate。
- 关联文件：
  - `docs/mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 推进 P1-07：建立 manual GUI intervention log，记录人工 ADS GUI 操作、截图、原因和复现影响。

### ARCH-REFACTOR-TASK-20260801-015 - Baseline Freeze Policy

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P1-05，建立 baseline freeze、复测、漂移判定和勘误规则。
  - 将当前 FR4 7 阶交指 frozen baseline 抽象为后续项目可复用的治理流程。
- 完成内容：
  - 新增 `docs/result/RESULT_BASELINE_FREEZE_POLICY.md`。
  - 读取现有 `i7_fr4_baseline_freeze_20260801.md/json`，将已冻结主象、漂移容差和 legacy run 说明纳入通用规则。
  - 定义 baseline 状态：`Draft`、`Proposed`、`Frozen`、`Superseded`、`Deprecated`。
  - 定义冻结前置条件、冻结记录字段、复测触发条件、baseline repeat 流程、漂移判定、候选比较和勘误规则。
  - 明确不同材料、阶数或拓扑分支不得混用 baseline 结论。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - 本任务只涉及文档和索引更新，未启动 ADS/FEM。
  - `result/RESULT_BASELINE_FREEZE_POLICY.md` 已加入 README 主文档入口和快速查找规则。
  - P1-05 TODO 已勾选。
- 还需完成：
  - 后续 P2 可实现 baseline repeat 的自动比主脚本，读取 frozen JSON 并输出 `repeat_pass/repeat_warn/repeat_drifted/repeat_invalid`。
  - 后续报告发布 gate 应强制引用 baseline_id、baseline_repeat_id、target_profile_id 和 score_version。
- 关联文件：
  - `docs/result/RESULT_BASELINE_FREEZE_POLICY.md`
  - `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md`
  - `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.json`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 推进 P1-06：建立 manufacturing tolerance robustness plan，定义 FR4 Er、板厚、铜厚、线宽、间距和长度扰动规则。

### ARCH-REFACTOR-TASK-20260801-014 - Job Scheduling Policy

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P1-04，建立 ADS 自动仿真任务调度策略。
  - 固定 license、并发、workspace 锁、超时、失败熔断、候选优先级、resume 和残留处理规则。
- 完成内容：
  - 新增 `docs/flow/FLOW_JOB_SCHEDULING_POLICY.md`。
  - 定义任务类型：docs/schema、layout 生成、score/plot、ADS profile/API smoke、layout 导入、emSetup clone/patch、FEM/RFPro、dataset export。
  - 定义同一 ADS workspace 默认串行写入，FEM/RFPro 默认 `1/workspace`。
  - 定义候选优先级：baseline drift check、smoke candidate、feasible improvement、diversity candidate、risky exploration。
  - 定义阶段超时建议、连续同类失败熔断规则、resume 复用表和残留处理原则。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - 本任务只涉及文档和索引更新，未启动 ADS/FEM。
  - `flow/FLOW_JOB_SCHEDULING_POLICY.md` 已加入 README 主文档入口和快速查找规则。
  - P1-04 TODO 已勾选。
- 还需完成：
  - P2 阶段实现 workspace lock、license probe、timeout monitor 和 scheduler manifest 字段写入。
  - 后续真实 batch 前，应按该策略先跑 profile/API smoke、必要时复跑 baseline，再从 1 个候选放大。
- 关联文件：
  - `docs/flow/FLOW_JOB_SCHEDULING_POLICY.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 推进 P1-05：建立 baseline freeze policy，补齐 frozen 状态、复测流程、漂移判据和勘误规则。

### ARCH-REFACTOR-TASK-20260801-013 - Layout Reconstruction Checklist

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P1-03，建立论文、公式、截图、示意版图或 ADS 原理图模型到参数化版图的统一审查清单。
  - 在 ADS 导入和 FEM 仿真前固定拓扑、层叠、单位、端口、via、接地、耦合、DRC、制造限制和结果追溯检查。
- 完成内容：
  - 新增 `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`。
  - 定义输入冻结、拓扑等价、层叠和参考地、单位坐标、参数映射、端口和接地、via 和焊盘、耦合和零点、DRC、ADS 导入和 EM 设置的检查表。
  - 补充常见失败特征，例如原理图带通但版图低通、频率整体偏移、通带变窄、回损恶化、阻带不足和仿真耗时异常。
  - 定义新 layout 首版生成时的最小执行记录字段和 `draft/layout_checked/sim_ready/rework_required` 状态。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - 本任务只涉及文档和索引更新，未启动 ADS/FEM。
  - `layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md` 已加入 README 主文档入口和快速查找规则。
  - P1-03 TODO 已勾选。
- 还需完成：
  - 后续生成 folded SIR、interdigital、hilo SIR 等新分支 layout 时，应把本清单作为首版 layout review gate。
  - P2 阶段可把部分检查代码化到 `simads.geometry`、`simads.exporters` 和 DRC 规则中。
- 关联文件：
  - `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 推进 P1-04：建立 job scheduling policy，定义 ADS license、并发、workspace 锁、超时和失败熔断规则。

### ARCH-REFACTOR-TASK-20260801-012 - Objective / Target Profile 设计

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P1-02，固化 ADS 自动仿真目标函数、target profile、硬约束、软目标和评分版本规则。
  - 明确滤波器专用指标不得继续硬编码到通用框架。
- 完成内容：
  - 新增 `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`。
  - 读取并引用 `config/targets/fr4_25db_rl6.json` 的 target profile 配置。
  - 主照 `tools/analyze_ads_dataset.py`，记录当前硬约束、回损目标、margin 公式和 `PASS_CANDIDATE` / `TUNE` 判定。
  - 定义 FR4 7 阶交指滤波器的 hard filter、soft ranking、baseline 改善和 release candidate 判据。
  - 明确 P2 阶段迁移方向：新增 `src/simads.scoring`，保留 `tools/analyze_ads_dataset.py` 作为兼容 CLI。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - `opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md` 已加入 README 主文档入口和快速查找规则。
  - P1-02 TODO 已勾选。
  - 文档明确当前 `tools/analyze_ads_dataset.py` 仍含硬编码 `TARGET_PROFILES`，后续需迁移到配置驱动。
- 还需完成：
  - P2 阶段实现 `src/simads.scoring` target profile loader、S 参数插值、margin 计算和 status 判定。
  - 后续如修改评分权重或发布判据，必须升级 `score_version` 并更新 round index。
- 关联文件：
  - `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`
  - `config/targets/fr4_25db_rl6.json`
  - `tools/analyze_ads_dataset.py`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 推进 P1-03：建立 layout reconstruction checklist，固化论文/公式/图片到参数化版图的审查清单。

### ARCH-REFACTOR-TASK-20260801-011 - FR4 7 阶交指 Round 结果索引

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P1-01，建立 FR4 7 阶交指滤波器 round 结果统一索引。
  - 明确 round2-round7 的 plan、result、summary、代表候选、baseline 关系和当前结论。
- 完成内容：
  - 新增 `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`。
  - 只读扫描 `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round*.csv`。
  - 只读扫描 `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round*/` 下的 `*_score.csv` 与 `sweep_summary*.csv`。
  - 按统一硬约束口径记录 round2-round7 的计划数量、已评分数量、状态、代表候选和结论。
  - 记录 frozen baseline `i7_fr4_baseline_freeze_20260801` 与 round3/4/5/6 重复点的关系。
  - 标记 round7 为部分公司环境探索数据，不作为 release candidate。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - round2-round7 plan 与 result 目录均已定位。
  - `result/RESULT_I7_FR4_ROUND_INDEX.md` 已加入 README 主文档入口和快速查找规则。
  - P1-01 TODO 已勾选。
- 还需完成：
  - 后续新增 round8 或重新跑完整 round7 时，必须追加本索引。
  - 若 score schema 再升级，应保留旧 score 的原始指标判定口径。
- 关联文件：
  - `docs/result/RESULT_I7_FR4_ROUND_INDEX.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `projects/bfp_6_8g_i7_fr4/plans/filter_opt_i7_fr4_round*.csv`
  - `projects/bfp_6_8g_i7_fr4/results/interdigital_7o_fr4_210um_round*/`
- 下一步：
  - 推进 P1-02：建立 objective / target profile 文档，避免评分逻辑继续散落在脚本和口头约束中。

### ARCH-REFACTOR-TASK-20260801-010 - Run State Machine 固化

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 补齐 ADS 自动仿真 run state machine，统一 `state.json` 和 `run_manifest.json` 的 `stage/status/error_class` 语义。
  - 防止后续 resume、summary 和报告流程混用 stage 与 status。
- 完成内容：
  - 新增 `src/simads/runtime/state_machine.py`。
  - 定义 `ads_run_state_machine_v1`，包含允许 stage、status、terminal status、error_class 和 failed_step -> resume stage 映射。
  - `src/simads/runtime/manifest.py` 的 `write_state()` 和 `write_run_manifest()` 接入 `stage/status/error_class` 校验。
  - `tools/run_ads_filter_candidate.py` 最终 manifest 状态由 `scored` 修正为 `completed`，保留 `stage=scored`。
  - 新增 `docs/flow/FLOW_RUN_STATE_MACHINE.md`。
  - 更新 `docs/README.md`、`docs/data/DATA_RUN_MANIFEST_SCHEMA.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - `python -m py_compile src\simads\runtime\state_machine.py src\simads\runtime\manifest.py src\simads\runtime\__init__.py tools\run_ads_filter_candidate.py tools\run_ads_filter_sweep.py` 通过。
  - 正常候选 `i7_fr4_r7_bo04 --skip-fem --dry-run` 通过，未启动 ADS/FEM。
- 还需完成：
  - 后续实现自动 resume 时，应直接复用 `resume_stage_for_failed_step()`。
  - 若新增 stage/status/error_class，必须同步更新 `flow/FLOW_RUN_STATE_MACHINE.md` 和 `data/DATA_RUN_MANIFEST_SCHEMA.md`。
- 关联文件：
  - `src/simads/runtime/state_machine.py`
  - `src/simads/runtime/manifest.py`
  - `src/simads/runtime/__init__.py`
  - `tools/run_ads_filter_candidate.py`
  - `docs/flow/FLOW_RUN_STATE_MACHINE.md`
  - `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 推进 P1-01 round 结果索引，或开始 P2 的 `simads.ads.*` 薄模块抽取。

### ARCH-REFACTOR-TASK-20260801-009 - ADS Workspace 写入安全 Gate

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P0-06，把 template cell、emSetup 覆盖和 substrate 修改的写入安全策略代码化。
  - 将写入安全策略纳入 run manifest 和正式文档。
- 完成内容：
  - 新增 `src/simads/safety/__init__.py`，提供 `AdsWriteContext`、`validate_ads_cell_write()`、`guard_directory_delete()` 和 `validate_substrate_patch()`。
  - `tools/run_ads_filter_candidate.py` 接入 safety gate，普通候选流程拒绝 target cell 等于 template cell，并在 `run_manifest.json` 写入 `write_safety`。
  - `tools/ads_clone_emsetup_template.py` 接入 safety gate，直接调用底层脚本时也拒绝覆盖 template cell；覆盖 emSetup 前检查删除目录边界。
  - `tools/patch_ads_substrate_pcvia.py` 接入 substrate 写入保护；会修改 `.subst` 文件时必须显式 `--force`，并新增 `--check-only`。
  - `src/simads/runtime/manifest.py` 新增 `SAFETY_ERROR` 分类。
  - 新增 `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`。
  - 更新 `docs/README.md`、`docs/arch/ARCH_REFACTOR_TODO.md` 和 `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`。
- 验证结果：
  - `python -m py_compile src\simads\safety\__init__.py src\simads\runtime\manifest.py tools\run_ads_filter_candidate.py tools\ads_clone_emsetup_template.py tools\patch_ads_substrate_pcvia.py` 通过。
  - candidate runner 写 template cell 的 dry-run 被 `AdsWriteSafetyError` 拦截。
  - 底层 emSetup clone 覆盖 template cell 的命令在文件复制/删除前被 `AdsWriteSafetyError` 拦截。
  - 正常候选 `i7_fr4_r7_bo04` 的 `--skip-fem --dry-run` 通过，未被 safety gate 误拦，未启动 ADS/FEM。
- 还需完成：
  - 后续若新增 ADS cell 删除、library 清理或结果清理脚本，必须复用 `src/simads.safety`。
  - 后续可在 P2 模块化时把 ADS workspace 操作继续抽到 `src/simads.ads.*`。
- 关联文件：
  - `src/simads/safety/__init__.py`
  - `src/simads/runtime/manifest.py`
  - `tools/run_ads_filter_candidate.py`
  - `tools/ads_clone_emsetup_template.py`
  - `tools/patch_ads_substrate_pcvia.py`
  - `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`
  - `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 推进 P1-01 round 结果索引或 P1-02 objective/target profile 文档。

### ARCH-REFACTOR-TASK-20260801-008 - Docs/Tools 目录治理方案

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 判断 `docs/` 和 `tools/` 是否需要细分目录。
  - 固化目录治理原则，避免过早移动脚本导致自动化闭环断裂。
- 完成内容：
  - 新增 `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`。
  - 明确 `docs/` 先按领域前缀和 README 索引做逻辑分层，中期再物理拆分。
  - 明确 `tools/` 暂不大规模移动，先将复用逻辑沉淀到 `src/simads`，旧 CLI 保持兼容入口。
  - 定义 `docs/` 领域前缀、文档状态、目标目录结构和迁移 gate。
  - 定义 `tools/` 长期分层建议：`ads/`、`layout/`、`opt/`、`scoring/`、`maintenance/`。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - README 已加入 `ARCH_DIRECTORY_GOVERNANCE.md` 的主文档入口和快速查找规则。
  - TODO 已新增 P1-09 Directory Governance，并记录后续 `src/simads.safety` 完成后再评估 `tools/ads/` 迁移。
- 还需完成：
  - 新增 `src/simads.safety`，把 ADS workspace 写入安全 gate 代码化。
  - 后续如执行物理迁移，需要生成迁移映射表并保留旧 CLI shim。
- 关联文件：
  - `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 推进 `src/simads.safety` 和 P0-06 剩余写入安全 gate。

### ARCH-REFACTOR-TASK-20260801-007 - ADS 自动仿真测试策略文档

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P0-08，形成 ADS 自动仿真项目的最小测试矩阵。
  - 固化 host Python、ADS Python、profile check、dry-run、baseline full run 和 batch run 的验证入口。
- 完成内容：
  - 新增 `docs/test/TEST_STRATEGY.md`。
  - 定义 T0-T7 测试分层：Python 编译、JSON/schema 检查、纯 Python smoke、profile check、ADS Python API smoke、单候选 dry-run、baseline full run、round batch run。
  - 记录公司环境 profile 的当前路径：SIM root、ADS workspace、ADS root、ADS Python、Host Python、library 和 template cell。
  - 写入当前可复用验证命令和通过标准。
  - 写入 template cell 写入安全测试和真实 ADS/FEM 记录规则。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - 文档内容已覆盖 host Python 与 ADS Python 的测试入口区分。
  - P0-08 TODO 项已勾选，README 已加入 TEST 文档入口和快速查找规则。
  - `python tools\check_ads_profile.py --profile company --require-template` 通过。
  - `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe tools\check_ads_python_env.py --profile company` 通过，ADS API version 为 `635`。
  - `python tools\run_ads_filter_sweep.py --profile company --target-profile fr4_25db_rl6 --skip-generate --skip-fem --dry-run --candidates i7_fr4_r7_bo04` 通过，命令链包含预生成 `run_id/run_dir`，未启动 FEM。
- 还需完成：
  - 若后续新增几何 golden 或 short FEM 专用脚本，需要补充到 `test/TEST_STRATEGY.md`。
  - 若 profile/substrate/emSetup 相比 baseline 冻结条件变化，真实 round7 前应先复跑 baseline。
- 关联文件：
  - `docs/test/TEST_STRATEGY.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`
- 下一步：
  - 按 `test/TEST_STRATEGY.md` 执行 company profile/API smoke。
  - 若 smoke 通过，先考虑 baseline 复跑或单候选 round7 测试。

### ARCH-REFACTOR-TASK-20260801-006 - FR4 7 阶交指 Baseline Freeze

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P0-07，冻结当前 FR4 7 阶交指 baseline。
  - 为 round7 及后续候选提供固定比较基准和环境漂移判据。
- 完成内容：
  - 新增 `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.json`。
  - 新增 `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md`。
  - baseline 覆盖 `i7_fr4_r3_base/r4_base/r5_base/r6_base`，代表候选为 `i7_fr4_r3_base`。
  - 记录代表 layout params、DXF、SVG、score CSV 的 SHA256。
  - 记录关键指标：`S21@5G=-27.15 dB`、`S21@6G=-2.13 dB`、`S21@8G=-4.28 dB`、`passband_min=-4.28 dB`、`ripple=2.83 dB`、`worst S11=-5.55 dB`、`worst S22=-5.98 dB`。
  - 定义漂移容差：`S21@5G ±1.0 dB`，通带关键点、通带最差、纹波和回损 `±0.5 dB`。
  - 更新 `docs/README.md` 和 `docs/arch/ARCH_REFACTOR_TODO.md`。
- 验证结果：
  - `python -m json.tool projects\bfp_6_8g_i7_fr4\results\baselines\i7_fr4_baseline_freeze_20260801.json` 通过。
  - 训练集确认 `i7_fr4_r3_base/r4_base/r5_base/r6_base` 四个重复点指标一致。
- 还需完成：
  - 后续真实公司环境复跑 round7 前，若 profile/substrate/emSetup 有变更，应先复跑代表 baseline。
  - P1 阶段仍需建立通用 `result/RESULT_BASELINE_FREEZE_POLICY.md`。
- 关联文件：
  - `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.json`
  - `projects/bfp_6_8g_i7_fr4/results/baselines/i7_fr4_baseline_freeze_20260801.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 推进 P0-08：新增 `test/TEST_STRATEGY.md`，把 profile check、ADS API smoke、score metadata smoke、summary manifest smoke 和 baseline full run 写成固定测试 gate。

### ARCH-REFACTOR-TASK-20260801-005 - Sweep Summary 合并 State 与 Manifest

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 完成 P0-05 剩余项，让 `sweep_summary.csv` 不只依赖 score CSV 和文件名。
  - summary 写入时读取候选级 `state.json` 和 `run_manifest.json`，补齐 run 元数据、失败阶段和耗时。
- 完成内容：
  - `tools/run_ads_filter_sweep.py` 新增 `read_json()` 和 `run_context()`。
  - `write_summary()` 输入从 score path 列表扩展为 run info 列表，包含 `candidate/cell/run_id/run_dir/score_path`。
  - 主成功候选，summary 从 manifest/state 合并 `run_id/project_id/round_id/candidate_id/profile_id/target_profile_id/score_version/elapsed_s`。
  - 主失败候选，summary 保留预生成 `run_id/run_dir`，并保留失败分类字段。
  - 合并优先级按文档收敛为 `state/manifest` 优先于 score/plan。
- 验证结果：
  - `python -m py_compile tools\run_ads_filter_sweep.py tools\run_ads_filter_candidate.py tools\analyze_ads_dataset.py` 通过。
  - 离线 summary/manifest smoke 通过：临时 summary 输出包含 `run_id=run123`、`profile_id=company`、`target_profile_id=fr4_25db_rl6`、`score_version=fr4_i7_score_v1`、`elapsed_s=12.345` 和 `run_dir`。
  - `python tools\run_ads_filter_sweep.py --profile company --target-profile fr4_25db_rl6 --skip-generate --skip-fem --dry-run --candidates i7_fr4_r7_bo04` 通过，仍正确传递预生成 `--run-id` 和 `--run-dir`。
- 还需完成：
  - baseline freeze 尚未建立。
  - 删除 cell、覆盖 template、修改 substrate 等破坏性操作还需要更完整的 `--force` 审计。
- 关联文件：
  - `tools/run_ads_filter_sweep.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
- 下一步：
  - 推进 P0-07：冻结当前 FR4 7 阶交指 baseline，记录关键指标和漂移容差。

### ARCH-REFACTOR-TASK-20260801-004 - Score 元数据回填、独立目录修正与写入安全 Gate

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 推进 P0-04，让 score CSV 能直接追溯 run/profile/target/score_version。
  - 推进 P0-05，让 sweep 入口为每个候选预生成 run_id。
  - 推进 P0-06，阻止普通候选流程误写 template cell。
  - 修正独立 `SIM` 目录后主脚本根目录推导错误。
- 完成内容：
  - `tools/analyze_ads_dataset.py` 新增 `--run-id --project-id --round-id --candidate-id --profile-id --target-profile-id --score-version --error-class --failed-step --elapsed-s`。
  - score CSV 新增 `run_id/project_id/round_id/candidate_id/profile_id/target_profile_id/score_version/error_class/failed_step/elapsed_s` 和约束 margin 字段。
  - `tools/run_ads_filter_candidate.py` 调用评分脚本时传入 run 元数据，并在 manifest `flags` 中记录 `force/skip_fem/reuse_layout/overwrite_setup` 等开关。
  - `tools/run_ads_filter_sweep.py` 为候选预生成 `run_id` 和 `run_dir`，并传入单候选 runner；失败行记录 run_id、run_dir、profile_id、target_profile_id 和 score_version。
  - 单候选 runner 增加 `--force`，普通流程中 `target_cell == template_cell` 时拒绝运行。
  - 修正 `run_ads_filter_candidate.py`、`run_ads_filter_sweep.py`、`build_i7_fr4_optimization_dataset.py`、`propose_i7_fr4_surrogate_candidates.py` 的独立目录根路径，不再把 `E:\OneDrive\4.Code` 当根目录拼 `SIM`。
- 验证结果：
  - `python -m py_compile tools\analyze_ads_dataset.py tools\run_ads_filter_candidate.py tools\run_ads_filter_sweep.py tools\build_i7_fr4_optimization_dataset.py tools\propose_i7_fr4_surrogate_candidates.py` 通过。
  - `python tools\build_i7_fr4_optimization_dataset.py --out .tmp\training_dataset_smoke.csv` 通过，输出 43 条测量 / 39 个唯一几何。
  - `python tools\analyze_ads_dataset.py ... --run-id smoke_run ...` 通过，临时 score CSV 表头包含 run metadata 和 margin 字段。
  - `python tools\run_ads_filter_sweep.py --profile company --target-profile fr4_25db_rl6 --skip-generate --skip-fem --dry-run --candidates i7_fr4_r7_bo04` 通过，命令中包含预生成 `--run-id` 和 `--run-dir`。
  - 单候选 dry-run 显示评分命令已携带 `--target-profile-id fr4_25db_rl6 --score-version fr4_i7_score_v1 --run-id ... --profile-id company`。
  - template 写入安全 gate 验证通过：普通流程中 target cell 等于 template cell 时拒绝运行。
- 还需完成：
  - `run_ads_filter_sweep.py` summary 尚未主动读取 `state.json` 和 `run_manifest.json` 合并失败阶段细节。
  - 删除 cell、覆盖 template、修改 substrate 等破坏性操作还需要更完整的 `--force` 审计。
  - baseline freeze 尚未建立。
- 关联文件：
  - `tools/analyze_ads_dataset.py`
  - `tools/run_ads_filter_candidate.py`
  - `tools/run_ads_filter_sweep.py`
  - `tools/build_i7_fr4_optimization_dataset.py`
  - `tools/propose_i7_fr4_surrogate_candidates.py`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
- 下一步：
  - 补齐 P0-05：summary 合并时读取 state/manifest。
  - 推进 P0-07：冻结当前 FR4 7 阶交指 baseline，并定义漂移容差。

### ARCH-REFACTOR-TASK-20260801-003 - P0 数据契约与公司环境配置修正

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 落地 P0-02 Data Schema Registry。
  - 落地 P0-03 Run/Artifact Manifest Schema。
  - 识别当前电脑为公司环境，并修正 company profile 的机器可读配置。
- 完成内容：
  - 新增 `docs/data/DATA_SCHEMA_REGISTRY.md`，登记 profile、project、target profile、candidate plan、layout params、score、sweep summary 和 training dataset 的最小字段契约。
  - 新增 `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`，冻结 `run_manifest.json`、`artifact_manifest.json` 和 `state.json` 的 P0 最小字段、run_id 规则、artifact 类型和 resume 规则。
  - 更新 `docs/README.md`，加入 DATA 文档入口和快速查找规则。
  - 更新 `docs/arch/ARCH_REFACTOR_TODO.md`，将 P0-02/P0-03 文档项标记为完成，并保留 P0-04/P0-05 代码回填任务。
  - 修正 `config/ads_profiles.json` 中 company profile：ADS root 改为 `D:/Hardware/Keysight/ADS2026_Update1`，ADS Python 和 host Python 显式记录，template cell 改为 `interdigital_9o_ro4350b_508um_v3_wide_mm_coords`。
- 验证结果：
  - `tools/check_ads_profile.py --profile company --require-template` 通过。
  - 公司环境识别结果：workspace 为 `D:\Work\ADS\6-8G_Fillter\6-8G_Fillter`，library 为 `6-8G_Fillter_lib`，template cell 目录存在。
  - 当前 `C:\Program Files\Keysight\ADS2026_Update1` 不存在，`D:\Hardware\Keysight\ADS2026_Update1` 存在。
- 还需完成：
  - `analyze_ads_dataset.py` 尚未按 schema 写入 run metadata。
  - `run_ads_filter_sweep.py` 尚未为每个候选预生成 run_id 并合并 state/manifest。
  - workspace 写入安全 gate 和 baseline freeze 仍未完成。
- 关联文件：
  - `docs/data/DATA_SCHEMA_REGISTRY.md`
  - `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
  - `docs/README.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
  - `config/ads_profiles.json`
- 下一步：
  - 推进 P0-04：修改 `tools/analyze_ads_dataset.py` 和 `tools/run_ads_filter_candidate.py`，让 score CSV 写入 `run_id/profile_id/score_version/target_profile_id/status/error_class/failed_step/elapsed_s`。
  - 推进 P0-05：修改 `tools/run_ads_filter_sweep.py`，让成功和失败候选都能进入 summary。

### ARCH-REFACTOR-TASK-20260801-002 - ADS 项目资产按新架构迁移

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 修正旧框架边界，不再把 `SIM/ADS` 作为项目资产根。
  - 把 ADS 相关 plan、layout、result、reference、report 和项目流程文档迁入 `projects/bfp_6_8g_i7_fr4/`。
  - 保留旧 `ADS/` 目录的迁移说明，避免历史路径无法追溯。
- 完成内容：
  - 新增 `config/ads_profiles.json`、`config/projects/bfp_6_8g_i7_fr4.json`、`config/targets/fr4_25db_rl6.json`。
  - 迁入 plan CSV 到 `projects/bfp_6_8g_i7_fr4/plans/`。
  - 迁入 DXF/SVG/params/DRC 等版图产物到 `projects/bfp_6_8g_i7_fr4/layouts/`。
  - 迁入 RFPro/FEM/score/summary/training dataset 到 `projects/bfp_6_8g_i7_fr4/results/`。
  - 迁入 6G 文章分析和图片资产到 `projects/bfp_6_8g_i7_fr4/references/6g_bpf_report/`。
  - 迁入 6-8G 旧报告到 `projects/bfp_6_8g_i7_fr4/reports/legacy/`。
  - 旧 `ADS/` 目录保留 `README.md`，说明新路径和迁移索引。
  - 更新 `tools/build_i7_fr4_optimization_dataset.py` 和 `tools/propose_i7_fr4_surrogate_candidates.py` 的默认路径。
  - 新增 `docs/arch/ARCH_ADS_ASSET_MIGRATION_20260801.md` 和 `docs/arch/ARCH_ADS_ASSET_MIGRATION_20260801.csv`。
  - 更新 `docs/README.md`、`docs/arch/ARCH_REFACTOR_TODO.md`、`docs/arch/ADS版图自动仿真项目框架设计.md` 中的当前边界。
- 验证结果：
  - 迁移索引生成 199 条记录。
  - `py_compile` 通过：`tools/*.py` 和 `src/simads/**/*.py`。
  - 训练集构建 dry-run 通过：默认输入读取 `projects/bfp_6_8g_i7_fr4/plans` 和 `projects/bfp_6_8g_i7_fr4/results`，输出 43 条测量 / 39 个唯一几何。
  - sweep dry-run 通过：`run_ads_filter_sweep.py` 使用新 plan/layout/results 路径生成单候选命令，未启动 FEM。
- 还需完成：
  - 迁移记录和任务记录中保留 `SIM/ADS` 作为旧边界说明；新增命令和默认路径不得再写回旧目录。
  - run manifest/schema、score run_id 回填、workspace 写入安全 gate、baseline freeze 仍未完成。
- 关联文件：
  - `config/ads_profiles.json`
  - `config/projects/bfp_6_8g_i7_fr4.json`
  - `config/targets/fr4_25db_rl6.json`
  - `projects/bfp_6_8g_i7_fr4/`
  - `ADS/README.md`
  - `docs/arch/ARCH_ADS_ASSET_MIGRATION_20260801.md`
  - `docs/arch/ARCH_ADS_ASSET_MIGRATION_20260801.csv`
  - `tools/build_i7_fr4_optimization_dataset.py`
  - `tools/propose_i7_fr4_surrogate_candidates.py`
- 下一步：
  - 建立 `data/DATA_SCHEMA_REGISTRY.md` 和 `data/DATA_RUN_MANIFEST_SCHEMA.md`。
  - 修改 score/sweep 元数据回填，让新目录下的结果具备 run_id 追溯。

### ARCH-REFACTOR-TASK-20260801-001 - 第一批兼容重构与 P0 运行追溯骨架

- 状态：完成
- 日期：2026-08-01
- 任务目标：
  - 按框架开始项目重构，但不移动 ADS workspace、不删除旧脚本、不破坏现有 `tools` CLI。
  - 建立 `src/simads` 可复用包骨架。
  - 把 home/company profile、run state、run manifest、artifact manifest 和 smoke test 入口先落到代码。
- 完成内容：
  - 新增 `src/simads/config/profiles.py`，集中管理 home/company ADS 路径、workspace、library、template cell、substrate、ADS Python 和 host Python。
  - `tools/ads_profiles.py` 改为兼容转发层，旧脚本仍可 `from ads_profiles import ...`。
  - 新增 `src/simads/runtime/manifest.py`，提供 run id、JSON 写入、artifact hash、state、manifest 和错误分类 helper。
  - 重构 `tools/run_ads_filter_candidate.py`，保持旧 CLI 兼容，新增 `--project-id`、`--round-id`、`--run-id`、`--run-dir`，非 dry-run 时输出 `state.json`、`run_manifest.json`、`artifact_manifest.json`。
  - 重构 `tools/run_ads_filter_sweep.py`，保持旧 CLI 兼容，向单候选入口传递 project/round，并为 summary 预留 `status/error_class/failed_step/elapsed_s/run_id/profile_id/score_version` 字段。
  - 新增 `tools/check_ads_profile.py`，用于 profile 快速路径校验。
  - 更新 `tools/check_ads_python_env.py`，支持 `--profile home`，并检查 `keysight.ads.de/ael/dataset`、`keysight.edatoolbox`、`keysight.pwdatatools`。
  - 新增 `pyproject.toml`，定义 `sim-ads-automation` 包和基础依赖。
  - 更新 `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`，登记第一批重构落地项。
- 验证结果：
  - `D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe -m py_compile tools/*.py src/simads/**/*.py` 通过。
  - `tools/run_ads_filter_candidate.py --skip-fem --dry-run` 通过；只打印导入和 emSetup 命令，不启动 FEM。
  - `tools/run_ads_filter_sweep.py --skip-fem --dry-run --candidates i7_fr4_r7_bo04` 通过；正确传递 `--project-id bfp_6_8g_i7_fr4` 和 `--round-id round7`。
  - `tools/check_ads_profile.py --profile home --require-template` 通过；`setup_dxf.opt` 缺失为 WARN，模板 cell 识别为 `BFP_lib\%B%F%P`。
  - `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe tools\check_ads_python_env.py --profile home` 通过；ADS DE version 为 `635`。
- 还需完成：
  - `score.csv` 尚未写入 `run_id/profile_id/score_version`。
  - `sweep_summary.csv` 尚未从 state/manifest 自动合并 run_id。
  - manifest 字段尚未由独立 schema 文档冻结。
  - workspace 写入安全 gate 尚未阻止 target cell 等于 template cell。
  - baseline 尚未 frozen。
- 关联文件：
  - `src/simads/config/profiles.py`
  - `src/simads/runtime/manifest.py`
  - `tools/ads_profiles.py`
  - `tools/run_ads_filter_candidate.py`
  - `tools/run_ads_filter_sweep.py`
  - `tools/check_ads_profile.py`
  - `tools/check_ads_python_env.py`
  - `pyproject.toml`
  - `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
  - `docs/arch/ARCH_REFACTOR_TODO.md`
- 下一步：
  - 建立 `data/DATA_SCHEMA_REGISTRY.md` 和 `data/DATA_RUN_MANIFEST_SCHEMA.md`。
  - 修改 `analyze_ads_dataset.py`，把 run 元数据写入 score CSV。
  - 修改 sweep 入口预生成 run_id，并把失败候选也写入 summary。













