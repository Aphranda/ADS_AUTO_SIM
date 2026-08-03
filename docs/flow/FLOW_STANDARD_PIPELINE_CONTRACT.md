# ADS 标准 Pipeline 契约

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_STANDARD_PIPELINE_CONTRACT.md`
Related: `docs/flow/FLOW_RUN_STATE_MACHINE.md`, `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`, `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
Last updated: 2026-08-03
Owner: ADS Automation

本文档定义 SIM 项目中版图生成、ADS 导入、emSetup/RFPro FEM、数据导出和评分的标准 pipeline 契约。目标是让后续滤波器迭代只改变候选参数，不再临时改变模板、层映射、单位、端口和评分口径。

## 1. 当前标准 Pipeline

```text
pipeline_id = bfp_6_8g_i7_fr4_interdigital_v1
config      = config/pipelines/bfp_6_8g_i7_fr4_interdigital_v1.json
project     = bfp_6_8g_i7_fr4
device      = filter.interdigital
profile     = company
units       = mm
```

该 pipeline 当前绑定 FR4 7 阶交指 BPF 分支。其他拓扑或材料分支应新增独立 pipeline config，不应复用本 pipeline 后再临时覆盖核心规则。

## 2. 固定契约

| 类别 | 固定值 | 说明 |
|---|---|---|
| 单位 | `mm` | DXF、params JSON、layout JSON、端口坐标统一使用毫米。 |
| 模板 cell | `interdigital_9o_ro4350b_508um_v3_wide_mm_coords` | 仅作为 emSetup/RFPro 模板来源，候选流程不得覆盖 template cell。 |
| setup view | `em%Setup` | emSetup 文件夹视图。 |
| RFPro view | `emSetup` | RFPro FEM 运行入口视图名。 |
| 频段 | `4-10 GHz` | 自动仿真和评分检查范围。 |
| 通带 | `6-8 GHz` | 当前目标通带。 |
| 金属层 | `cond` | DXF fallback import 和端口 pin 放置层。 |
| via 层 | `pcvia1` | 圆孔/过孔层。 |
| 边界层 | `EM_BOUNDARY` | EM 边界矩形层。 |
| 层映射版本 | `profile-default-v1` | 记录生成器与 ADS profile 默认层映射假设。 |
| 端口 | `P1`, `P2` | 端口坐标来自 params/layout JSON，端口必须落在金属层。 |
| ADS 端口参考层 | `portGndLayer=<reference layer>` | 端口参考层必须写入 layout `Term` 的 OA 字符串属性；当前 JLC clean layout 使用 `ETCH_INNER1`。 |
| 评分目标 | `fr4_25db_rl6` | 当前低成本 FR4 分支评分 profile。 |
| 评分版本 | `fr4_i7_score_v1` | 与 target profile 绑定。 |

## 3. 标准脚本绑定

| 阶段 | 脚本 |
|---|---|
| 批量版图生成 | `tools/generate_filter_sweep.py` |
| 单版图生成器 | `tools/generate_interdigital_filter_layout.py` |
| ADS DXF 导入和 P1/P2 | `tools/ads/ads_import_dxf_add_ports.py` |
| emSetup 克隆/patch | `tools/ads/ads_clone_emsetup_template.py` |
| RFPro/FEM | `tools/ads/ads_run_rfpro_fem.py` |
| FEM dataset/TXT 导出 | `tools/ads/export_ads_fem_dataset.py` |
| S 参数评分 | `tools/analyze_ads_dataset.py` |

根目录同名 wrapper 只作为兼容入口保留；标准 pipeline 优先绑定子目录中的正式脚本。

## 4. 校验入口

只读检查命令：

```text
python tools/check_pipeline_contract.py --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1
```

layout JSON 检查命令：

```text
python tools/check_layout_contract.py --project-id bfp_6_8g_i7_fr4 --pipeline-id bfp_6_8g_i7_fr4_interdigital_v1 --candidate i7_fr4_r7_bo04
```

检查内容包括：

- project/sweep/pipeline/profile 的 id 一致性。
- 单位、端口、层名、模板、view、频段和评分版本。
- 标准脚本路径和 layout/params 输出目录是否存在。
- device plugin 是否已注册。
- `_layout.json` 的单位、声明层、已使用层、`P1/P2`、端口落铜、过孔层、过孔焊盘/落铜和 `layer_map_version`。
- 拓扑专项检查；pixel QR 分支当前自动检查 `mask_rows`、matrix/source_map 完整性、馈线与边缘像素耦合、最小金属间距和孤岛数量统计。

这些检查不会启动 ADS，不会导入 DXF，不会运行 FEM，也不会修改 workspace。

## 5. Runner 接入规则

`tools/run_ads_filter_sweep.py` 和 `tools/run_ads_filter_candidate.py` 已支持 `--pipeline-id`。默认解析顺序：

```text
CLI override -> project active sweep pipeline_id -> project pipeline_id -> legacy default
```

未显式传入模板、层名、target profile 或脚本路径时，runner 使用 pipeline contract。CLI 仍可用于临时诊断，但用于正式优化轮次时应保留 pipeline 默认值，并在 run manifest 中记录 `pipeline_id` 和 `pipeline_snapshot`。

`tools/run_ads_filter_sweep.py` 已将 pipeline contract 检查作为默认前置 gate。该 gate 在候选生成、ADS 导入和 FEM 启动前执行；如需临时排查旧流程，可显式使用：

```text
--skip-pipeline-check
```

正式优化轮次不得跳过该 gate。

`tools/run_ads_filter_sweep.py` 还会在候选生成之后、ADS 导入之前执行 layout contract 检查。正式 round 中，pipeline 要求 `require_layout_json=true` 时，缺失 `_layout.json` 或检查失败会停止流程。为了兼容历史产物：

```text
--skip-layout-check
```

可显式跳过 layout gate；`--skip-generate` 或 `--dry-run` 遇到旧候选缺 `_layout.json` 时默认只给出 WARN。需要在调试时强制检查旧产物，可增加：

```text
--strict-layout-check
```


拓扑专项 gate 默认自动执行：`check_layout_contract.py` 使用 `--topology-check auto`，`run_ads_filter_sweep.py` 使用 `--layout-topology-check auto`。pixel QR 分支可用 `--min-metal-spacing-mm` 固定最小金属间距，用 `--max-island-components` 在正式工艺策略确定后收紧孤岛数量。

## 5. ADS 端口参考层契约

ADS layout 导入后，端口参考层不能只依赖 GUI 状态、`emStateFile.xml` 或 `secondary_term_info`。已确认 ADS GUI 对 layout port 参考层的持久化位置是端口 `Term` 上的 OpenAccess 字符串属性：

```text
portGndLayer = <reference layer name>
```

自动导入脚本必须满足：

- `P1/P2` 均存在 layout `Term`。
- `P1/P2` 的 `Term` 均有 `portGndLayer` 属性。
- `portGndLayer` 指向端口所在信号层的参考导体层；当前干净 ADS 试验版图为 `ETCH_INNER1`。
- 参考层必须存在实际铜皮，并按当前层叠口径作为 GND 平面参与 EM。
- 若 stackup 中存在 L3/L4 等更深 GND 层，但快速 clean layout 只画 L1+L2，则 L3/L4 保留在层叠配置中，不默认画进 layout 几何。

推荐 ADS API 写法：

```python
existing = term.find_prop("portGndLayer")
if existing is None:
    db_uu.StringProp.create(term, "portGndLayer", reference_layer)
else:
    existing.value = reference_layer
```

该模式属于通用 OA 属性写入能力。后续 ADS GUI 中可手动完成但 API 不清楚的设置，应优先使用“人工基准 cell 和脚本 cell 对象属性 diff”的方式定位真实持久化字段。

## 6. 多分支扩展规则

当前已登记 pipeline：

| pipeline_id | sweep_id | device_id | 状态 |
|---|---|---|---|
| `bfp_6_8g_i7_fr4_interdigital_v1` | `interdigital_7o_fr4_round7` | `filter.interdigital` | 标准 FR4 7 阶交指 BPF pipeline，已接入 pipeline/layout gate。 |
| `pixel_qr_bpf_fr4_210um_v1` | `pixel_qr_bpf_fr4_210um_r0` | `filter.pixel_qr_bpf` | 二维码像素化 BPF 独立项目，已接入通用 layout gate 和 pixel QR 拓扑专项 gate；R0 采用相邻黑色像素共边无间隙规则。 |

新增 folded SIR、高低阻抗 SIR 或 RO4350 高抑制分支时，应新建独立 `config/pipelines/<pipeline_id>.json`，并在 `config/projects/<project_id>.json` 的 `sweeps` 中登记。不得通过正式 round 的 CLI 临时覆盖以下核心约束：单位、层名、端口名、频段、评分 profile、模板 cell、setup view、layout 输出目录和 score 版本。

每个新增 pipeline 至少需要完成：

- pipeline contract 检查通过。
- layout generator 输出 DXF/SVG、params JSON 和 `_layout.json`。
- `_layout.json` 通过通用 layout contract gate。
- 若拓扑包含特殊结构，补充 topology-specific layout gate，例如 folded SIR 的接地过孔和 U 形谐振器连通性，高低阻抗 SIR 的阻抗段宽度/长度边界；像素化分支已具备孤岛、最小间距和 feed 连通性检查。
- 首个真实 ADS/FEM 结果必须写入 run manifest、artifact manifest、state、score CSV 和 sweep summary。

## 7. 后续完善项

- 将 layout contract 检查扩展到 folded SIR、高低阻抗 SIR 等非交指分支的专用规则。
- 为 folded SIR、高低阻抗 SIR 等分支建立独立 pipeline config。





