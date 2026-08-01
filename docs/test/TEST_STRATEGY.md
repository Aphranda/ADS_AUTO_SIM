# ADS 自动仿真测试策略

Status: Active
Domain: TEST
Canonical: `docs/test/TEST_STRATEGY.md`
Related: `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/data/DATA_SCHEMA_REGISTRY.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/env/ENV_ADS_API_CAPABILITY_MATRIX.md`, `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义 ADS 自动仿真项目的最小测试矩阵。目标是在不每次启动长耗时 FEM 的前提下，尽早发现路径、profile、schema、版图、ADS API、评分和 summary 追溯问题。

## 1. 测试分层

| 层级 | 名称 | 是否需要 ADS | 目的 |
|---|---|---|---|
| T0 | Python 编译和导入检查 | 否 | 防止脚本语法错误、模块路径错误。 |
| T1 | 数据 schema / JSON 检查 | 否 | 确认配置、manifest、baseline freeze 可读。 |
| T2 | 纯 Python 功能 smoke | 否 | 验证 score metadata、summary manifest 合并、训练集构建。 |
| T3 | Profile 路径检查 | 否 | 确认 ADS root、workspace、library、template cell 路径存在。 |
| T4 | ADS Python API smoke | 是，短耗时 | 验证 ADS Python、`keysight.ads`、dataset/API 包可用。 |
| T5 | 单候选 dry-run / skip-fem | 是，可能写 ADS | 验证 DXF 导入、端口、emSetup patch 命令链。 |
| T6 | Baseline full run | 是，长耗时 | 环境变更后复跑冻结 baseline，判断漂移。 |
| T7 | Round batch run | 是，长耗时 | 对正式候选批量 FEM 仿真并生成 summary。 |

## 2. 当前公司环境

当前电脑按 `company` profile 运行：

```text
SIM root      : E:\OneDrive\4.Code\SIM
ADS workspace : D:\Work\ADS\6-8G_Fillter\6-8G_Fillter
ADS root      : D:\Hardware\Keysight\ADS2026_Update1
ADS Python    : D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
Host Python   : D:\Microsoft\Miniconda\python.exe
Library       : 6-8G_Fillter_lib
Template cell : interdigital_9o_ro4350b_508um_v3_wide_mm_coords
```

运行真实 ADS/FEM 前必须确认当前 profile 与实际电脑一致。

## 3. 必跑 Gate

### T0 Python 编译

触发条件：

- 修改 `tools/*.py`。
- 修改 `src/simads/**/*.py`。
- 修改脚本根目录、profile、run/manifest、评分或 summary 逻辑。

命令：

```powershell
python -m py_compile tools\analyze_ads_dataset.py tools\run_ads_filter_candidate.py tools\run_ads_filter_sweep.py tools\build_i7_fr4_optimization_dataset.py tools\propose_i7_fr4_surrogate_candidates.py
```

通过标准：

```text
exit code = 0
```

### T1 JSON 可读性

触发条件：

- 修改 `config/*.json`。
- 修改 `projects/.../results/baselines/*.json`。
- 修改 manifest schema 或 baseline freeze。

命令：

```powershell
python -m json.tool config\ads_profiles.json
python -m json.tool config\projects\bfp_6_8g_i7_fr4.json
python -m json.tool config\targets\fr4_25db_rl6.json
python -m json.tool projects\bfp_6_8g_i7_fr4\results\baselines\i7_fr4_baseline_freeze_20260801.json
```

通过标准：

```text
所有 JSON 可解析，关键字段与 DATA_SCHEMA_REGISTRY.md 一致。
```

### T2 Score Metadata Smoke

触发条件：

- 修改 `tools/analyze_ads_dataset.py`。
- 修改 target profile、score_version 或 score CSV 字段。

命令：

```powershell
python tools\analyze_ads_dataset.py projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_210um_r0_marki_10_14mil_via_mm_coords_rfpro.csv --out .tmp\score_metadata_smoke.csv --target-profile fr4_25db_rl6 --run-id smoke_run --project-id bfp_6_8g_i7_fr4 --round-id smoke --candidate-id smoke_candidate --profile-id company --elapsed-s 1.234
```

通过标准：

```text
.tmp\score_metadata_smoke.csv 存在。
表头包含 run_id、project_id、round_id、candidate_id、profile_id、target_profile_id、score_version、elapsed_s 和 margin 字段。
```

### T2 Summary Manifest Smoke

触发条件：

- 修改 `tools/run_ads_filter_sweep.py`。
- 修改 run manifest、state 或 summary 字段合并逻辑。

通过标准：

```text
临时 summary 能从 run_manifest.json/state.json 合并 run_id、profile_id、target_profile_id、score_version、elapsed_s、run_dir。
```

当前已验证输出：

```text
run_id=run123
profile_id=company
target_profile_id=fr4_25db_rl6
score_version=fr4_i7_score_v1
elapsed_s=12.345
```

### T2 Training Dataset Smoke

触发条件：

- 修改 plan/result 目录。
- 修改 summary 字段。
- 修改训练集构建脚本。

命令：

```powershell
python tools\build_i7_fr4_optimization_dataset.py --out .tmp\training_dataset_smoke.csv
```

当前通过标准：

```text
输出 43 measurements / 39 unique geometries。
Top rows 中 baseline 为 i7_fr4_r3_base/r4_base/r5_base/r6_base。
```

### T3 Company Profile Check

触发条件：

- 当前电脑从 home 切换到 company。
- 修改 `config/ads_profiles.json` 或 `src/simads/config/profiles.py`。
- 启动真实 ADS/FEM 前。

命令：

```powershell
python tools\check_ads_profile.py --profile company --require-template
```

通过标准：

```text
ads_root、ads_python、host_python、workspace、library、layer_map、template_cell 全部 OK。
```

### T4 ADS Python API Smoke

触发条件：

- ADS 安装路径变化。
- ADS 升级。
- 首次在当前电脑运行真实 ADS 自动化。
- ADS API 相关脚本修改。

命令：

```powershell
& "D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe" tools\check_ads_python_env.py --profile company
```

通过标准：

```text
ADS Python 可启动。
keysight.ads.de/ael/dataset 相关 import 通过。
能读取 ADS version。
```

### T5 单候选 Dry-Run

触发条件：

- 修改 runner、路径、profile、template、target profile。
- 批量 FEM 前。

命令：

```powershell
python tools\run_ads_filter_sweep.py --profile company --target-profile fr4_25db_rl6 --skip-generate --skip-fem --dry-run --candidates i7_fr4_r7_bo04
```

通过标准：

```text
命令中路径指向 E:\OneDrive\4.Code\SIM\projects\...
命令中包含预生成 --run-id 和 --run-dir。
profile=company，workspace/library/template 正确。
不启动 ADS/FEM。
```

### T6 Baseline Full Run

触发条件：

- profile 从 home/company 切换。
- ADS root、workspace、library、template cell、substrate 或 emSetup 变化。
- ADS 升级或 license/solver 配置变化。
- 准备发布 release candidate。

基准：

```text
baseline_id = i7_fr4_baseline_freeze_20260801
representative_candidate = i7_fr4_r3_base
```

通过标准：

```text
复跑指标不超过 baseline freeze 中 drift_tolerance。
若超过，先排查环境漂移，不直接比较新候选。
```

### T7 Round Batch Run

触发条件：

- T0-T5 通过。
- 如环境有变化，T6 已通过。
- 用户确认启动真实 ADS/FEM。

round7 当前建议命令：

```powershell
python tools\run_ads_filter_sweep.py --profile company --template-cell interdigital_9o_ro4350b_508um_v3_wide_mm_coords --target-profile fr4_25db_rl6 --plan projects\bfp_6_8g_i7_fr4\plans\filter_opt_i7_fr4_round7.csv --out-dir projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round7 --results-dir projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_210um_round7 --summary projects\bfp_6_8g_i7_fr4\results\interdigital_7o_fr4_210um_round7\sweep_summary.csv --skip-generate --continue-on-error --candidates i7_fr4_r7_bo04 i7_fr4_r7_bo01 i7_fr4_r7_bo03 i7_fr4_r7_bo05
```

## 4. 写入安全测试

普通候选流程不得写入 template cell。

命令：

```powershell
python tools\run_ads_filter_candidate.py interdigital_9o_ro4350b_508um_v3_wide_mm_coords --profile company --template-cell interdigital_9o_ro4350b_508um_v3_wide_mm_coords --reuse-layout --skip-setup --dry-run
```

通过标准：

```text
拒绝运行，并提示 target cell equals template cell。
```

## 5. 测试记录规则

涉及真实 ADS workspace 写入、FEM 仿真或 baseline 复跑时，必须在 `ARCH_REFACTOR_TASK_PROGRESS.md` 或对应任务进度文档中记录：

```text
profile
workspace
library
template_cell
candidate_cell
target_profile
run_id
run_dir
summary
验证结果
```

dry-run、py_compile、JSON 和纯 Python smoke 可在任务记录中简要列出命令和通过结论。
