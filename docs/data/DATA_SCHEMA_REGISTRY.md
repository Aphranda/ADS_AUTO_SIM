# ADS 自动仿真数据 Schema Registry

Status: Active
Domain: DATA
Canonical: `docs/data/DATA_SCHEMA_REGISTRY.md`
Related: `docs/arch/ADS版图自动仿真项目框架设计.md`, `docs/arch/ARCH_FRAMEWORK_REVIEW_GAP_ANALYSIS.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/arch/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义 ADS 版图自动仿真平台当前可执行数据契约。所有被多个脚本读写、进入 sweep summary、training dataset 或正式报告的数据文件，都必须登记 schema version、字段、单位和追溯规则。

## 1. 通用规则

- 所有 JSON/CSV 文档使用 UTF-8 编码。
- 所有 schema 必须包含 `schema_version`。
- 物理量字段应在字段名中包含单位，例如 `_mm`、`_ghz`、`_hz`、`_db`、`_s`。
- 新增字段必须向后兼容；删除字段或改变字段语义必须升级 major version。
- 评分结果必须能追溯到 `target_profile_id` 和 `score_version`。
- 报告只能引用通过本 registry 登记的数据字段。

## 2. Profile Schema

文件：

```text
config/ads_profiles.json
```

当前版本：

```text
schema_version = 0.1.0
```

必填字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `schema_version` | string | - | profile 配置 schema 版本。 |
| `profiles` | object | - | profile 字典，key 为 `profile_id`。 |
| `profiles.<id>.ads_root` | string | path | ADS 安装根目录。 |
| `profiles.<id>.workspace` | string | path | ADS workspace 路径。 |
| `profiles.<id>.library` | string | - | ADS library 名。 |
| `profiles.<id>.template_cell` | string | - | emSetup 模板 cell。 |
| `profiles.<id>.setup_view` | string | - | 物理 EM setup view 目录名，通常为 `em%Setup`。 |
| `profiles.<id>.rfpro_emsetup_view` | string | - | RFPro API 逻辑 setup view 名，通常为 `emSetup`。 |
| `profiles.<id>.substrate` | string | ADS lib:cell | substrate 引用。 |

可选字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `profiles.<id>.ads_python` | string | path | ADS Python 路径。未配置时由 `ads_root` 推导。 |
| `profiles.<id>.host_python` | string | path | host/control Python 路径。未配置时使用当前 Python。 |

校验规则：

- `profile_id` 只能包含字母、数字、下划线和短横线。
- `workspace`、`library`、`template_cell`、`substrate` 必须在 run manifest 中快照记录。
- profile 切换后必须先运行 profile/API smoke test。

## 3. Project Schema

文件：

```text
config/projects/<project_id>.json
```

当前版本：

```text
schema_version = 0.1.0
```

必填字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `schema_version` | string | - | project 配置 schema 版本。 |
| `project_id` | string | - | 项目唯一 ID。 |
| `name` | string | - | 项目名称。 |
| `device_family` | string | - | 器件大类。 |
| `primary_device_type` | string | - | device plugin 类型，例如 `filter.interdigital`。 |
| `default_profile` | string | - | 默认 ADS profile。 |
| `target_profile` | string | - | 默认目标 profile。 |
| `project_root` | string | path | 项目资产根目录。 |
| `plans_dir` | string | path | plan CSV 目录。 |
| `layouts_dir` | string | path | 版图产物目录。 |
| `results_dir` | string | path | 仿真结果目录。 |
| `runs_dir` | string | path | 标准 run 输出目录。 |
| `reports_dir` | string | path | 报告目录。 |
| `references_dir` | string | path | 参考资料目录。 |
| `frequency.start_ghz` | number | GHz | 仿真起始频率。 |
| `frequency.stop_ghz` | number | GHz | 仿真终止频率。 |
| `frequency.passband_start_ghz` | number | GHz | 通带起始频率。 |
| `frequency.passband_stop_ghz` | number | GHz | 通带终止频率。 |
| `ads.library` | string | - | 项目默认 ADS library。 |
| `ads.template_cell` | string | - | 项目默认模板 cell。 |
| `ads.substrate` | string | ADS lib:cell | 项目默认 substrate。 |

## 4. Target Profile Schema

文件：

```text
config/targets/<target_profile_id>.json
```

当前版本：

```text
schema_version = 0.1.0
```

必填字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `schema_version` | string | - | target profile schema 版本。 |
| `target_profile_id` | string | - | 目标 profile ID。 |
| `name` | string | - | 目标说明。 |
| `score_version` | string | - | 评分函数版本。 |
| `frequency_ghz.stop_low_probe` | number | GHz | 低边阻带探测点。 |
| `frequency_ghz.passband_start` | number | GHz | 通带入口。 |
| `frequency_ghz.passband_center` | number | GHz | 通带中心。 |
| `frequency_ghz.passband_stop` | number | GHz | 通带出口。 |
| `frequency_ghz.stop_high_probe` | number | GHz | 高边阻带探测点。 |
| `hard_constraints.s21_5g_db_max` | number | dB | 5 GHz S21 上限。 |
| `hard_constraints.s21_6g_db_min` | number | dB | 6 GHz S21 下限。 |
| `hard_constraints.s21_8g_db_min` | number | dB | 8 GHz S21 下限。 |
| `hard_constraints.passband_min_s21_db_min` | number | dB | 通带最差 S21 下限。 |
| `hard_constraints.passband_ripple_db_max` | number | dB | 通带纹波上限。 |
| `return_loss_targets.worst_s11_6_8_db_max` | number | dB | 通带最差 S11 上限。 |
| `return_loss_targets.worst_s22_6_8_db_max` | number | dB | 通带最差 S22 上限。 |

## 5. Candidate Plan Schema

文件：

```text
projects/<project_id>/plans/filter_opt_i7_fr4_round*.csv
```

当前版本：

```text
schema_version = 0.1.0
```

当前 CSV 尚未强制写入 `schema_version` 列；P0 期间按文件级 schema 处理，P1 起建议新增该列。

必填字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `name` | string | - | 候选 ID，也是 DXF/ADS cell 命名基础。 |
| `L_mm` | number | mm | 谐振器长度。 |
| `tap_mm` | number | mm | 输入/输出抽头高度。 |
| `Egap_mm` | number | mm | 开路端间隙。 |
| `S1_mm` | number | mm | 相邻谐振器间隙。 |
| `S2_mm` | number | mm | 相邻谐振器间隙。 |
| `S3_mm` | number | mm | 相邻谐振器间隙。 |
| `S4_mm` | number | mm | 相邻谐振器间隙。 |
| `S5_mm` | number | mm | 相邻谐振器间隙。 |
| `S6_mm` | number | mm | 相邻谐振器间隙。 |
| `via_diameter_mm` | number | mm | 接地孔钻孔直径。 |
| `metal_layer` | string | ADS layer | 顶层金属层。 |
| `via_layer` | string | ADS layer | 过孔层。 |
| `notes` | string | - | 候选生成意图。 |

可选字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `W0_mm` | number | mm | 50 ohm 馈线宽度。 |
| `feed_len_mm` | number | mm | 馈线长度。 |
| `feed_taper_len_mm` | number | mm | 锥形过渡长度。 |
| `feed_tip_w_mm` | number | mm | 锥形尖端宽度。 |
| `feed_overlap_mm` | number | mm | 锥形与谐振器搭接量。 |
| `round_id` | string | - | 候选轮次。P0 后建议写入。 |
| `candidate_source` | string | - | `manual`、`grid`、`surrogate_ei`、`baseline_repeat` 等。 |
| `parent_candidate_id` | string | - | 父候选。 |

## 6. Layout Params Schema

文件：

```text
projects/<project_id>/layouts/<round>/<candidate>_params.json
```

当前版本：

```text
schema_version = 0.1.0
```

必填信息：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `name` 或 `candidate_id` | string | - | 候选名称。 |
| `units` | string | - | 坐标单位，当前应为 `mm`。 |
| `ports` | array/object | mm/ohm | P1/P2 端口位置、方向和阻抗。 |
| `substrate` 或 `stackup` | object/string | - | 层叠或 substrate 信息。 |
| `metal_layer` | string | ADS layer | 金属层。 |
| `via_layer` | string | ADS layer | 过孔层。 |
| `boundary` | object | mm | EM 边界或版图包围盒。 |
| `drc` | object | mixed | 最小线宽、间距、孔径、焊盘等 DRC 派生值。 |

P1 建议新增：

```text
layout_id
geometry_hash
source_map_path
layer_map
shapes[]
vias[]
ports[].attached_shape
ports[].orientation
```

## 7. Score Schema

文件：

```text
projects/<project_id>/results/<round>/<candidate>_score.csv
```

当前版本：

```text
schema_version = 1.0
```

当前已输出字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `source` | string | path/ref | 评分数据来源，RFPro CSV 或 ADS dataset block。 |
| `target_profile` | string | - | 当前评分目标。P0-04 后改为 `target_profile_id` 并保留兼容别名。 |
| `status` | string | - | `PASS_CANDIDATE` 或 `TUNE`。 |
| `s21_5g_db` | number | dB | 5 GHz 插损/抑制。 |
| `s21_6g_db` | number | dB | 6 GHz S21。 |
| `s21_7g_db` | number | dB | 7 GHz S21。 |
| `s21_8g_db` | number | dB | 8 GHz S21。 |
| `s21_9g_db` | number | dB | 9 GHz S21。 |
| `passband_min_s21_db` | number | dB | 6-8 GHz 通带最差 S21。 |
| `passband_ripple_db` | number | dB | 6-8 GHz 通带纹波。 |
| `worst_s11_6_8_db` | number | dB | 6-8 GHz 最差 S11。 |
| `worst_s22_6_8_db` | number | dB | 6-8 GHz 最差 S22。 |

P0-04 必须补齐字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `run_id` | string | - | 关联 run。 |
| `project_id` | string | - | 关联项目。 |
| `round_id` | string | - | 关联轮次。 |
| `candidate_id` | string | - | 候选 ID。 |
| `profile_id` | string | - | ADS profile。 |
| `target_profile_id` | string | - | 目标 profile。 |
| `score_version` | string | - | 评分函数版本。 |
| `error_class` | string | - | 失败分类；成功为空。 |
| `failed_step` | string | - | 失败阶段；成功为空。 |
| `elapsed_s` | number | s | 当前 run 总耗时。 |

约束余量字段建议：

```text
margin_s21_5g_db
margin_s21_6g_db
margin_s21_8g_db
margin_passband_min_s21_db
margin_passband_ripple_db
margin_worst_s11_6_8_db
margin_worst_s22_6_8_db
```

## 8. Sweep Summary Schema

文件：

```text
projects/<project_id>/results/<round>/sweep_summary.csv
```

当前版本：

```text
schema_version = 1.0
```

必填字段：

| 字段 | 类型 | 单位 | 说明 |
|---|---|---|---|
| `candidate` | string | - | 候选名称。 |
| `status` | string | - | 候选最终状态。成功可为 `PASS_CANDIDATE`/`TUNE`，失败为 `FAILED`。 |
| `run_id` | string | - | 预生成或实际 run ID。 |
| `profile_id` | string | - | ADS profile。 |
| `score_version` | string | - | 评分版本。 |
| `target_profile_id` | string | - | 目标 profile。 |
| `error_class` | string | - | 失败分类。 |
| `failed_step` | string | - | 失败阶段。 |
| `elapsed_s` | number | s | 单候选耗时。 |
| score 指标字段 | number | dB | 与 Score Schema 保持一致。 |

规则：

- 成功和失败候选都必须进入 summary。
- `run_id` 应在 sweep 调用单候选脚本前预生成。
- summary 合并时优先读取 `state.json` 和 `run_manifest.json`，再读取 score CSV。

## 9. Training Dataset Schema

文件：

```text
projects/<project_id>/results/interdigital_7o_fr4_training_dataset.csv
```

当前版本：

```text
schema_version = 0.1.0
```

字段分组：

| 分组 | 字段 | 说明 |
|---|---|---|
| identity | `candidate`、`round`、`source_plan`、`source_score` | 样本身份和来源。 |
| features | `L_mm`、`tap_mm`、`Egap_mm`、`S*_mm`、`feed_*_mm` | 优化器输入特征。 |
| metrics | `s21_*_db`、`passband_*`、`worst_s11_6_8_db`、`worst_s22_6_8_db` | 仿真指标。 |
| constraints | margin 字段、`status` | 约束判断和余量。 |
| optimizer | 综合分、排名、可行性标记 | 代理模型训练和候选筛选。 |

P1 建议新增：

```text
run_id
profile_id
target_profile_id
score_version
layout_hash
excluded_reason
dataset_schema_version
```

## 10. 兼容策略

- P0 阶段允许旧 score CSV 缺少 run metadata，但新生成结果必须逐步补齐。
- 读取旧字段 `target_profile` 时，应映射为 `target_profile_id`。
- 旧路径 `ADS/` 仅作为迁移来源；新增数据默认写入 `projects/<project_id>/...`。
- 当同一候选存在多次 baseline repeat 时，training dataset 必须保留全部测量点，并用 `unique_geometry_id` 或 `layout_hash` 区分几何重复与环境漂移。
