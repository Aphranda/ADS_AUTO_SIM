# ADS 自动仿真闭环流程说明

本文档用于维护 6-8 GHz 滤波器版图参数化、ADS 导入、FEM 仿真、结果评分和优化迭代流程。当前稳定自动化路径以 RFPro/FEM API 为主；EMSETUP 图形界面 `simulate` 按钮尚未找到稳定的公开自动化接口，适合作为关键候选项的人工复测和最终确认路径。

## 1. 固定环境

路径配置集中在：

```text
SIM\tools\ads_profiles.py
```

当前维护两套 ADS profile：

| profile | ADS 工作目录 | ADS 根目录 | ADS Python | ADS Library | Substrate Library |
|---|---|---|---|---|---|
| `company` | `D:\Work\ADS\6-8G_Fillter\6-8G_Fillter` | `D:\Hardware\Keysight\ADS2026_Update1` | `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe` | `6-8G_Fillter_lib` | 同库 |
| `home` | `D:\Work\ADS\BFP\BFP` | `D:\Hardware\Keysight\ADS2026_Update1` | `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe` | `BFP_lib` | 同库 |

家里电脑的普通主控 Python 使用专用 uv 虚拟环境：

```text
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe
```

该环境用于运行普通脚本、CSV 处理、JSON/XML patch、评分和批量 wrapper，已安装 `numpy`，并通过 `ads_path.pth` 指向 ADS Python 包目录。实际 ADS OA/RFPro API 仍由 ADS 自带 Python 运行：

```text
D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
```

家里模板 cell 为：

```text
BFP_lib:BFP
```

家里层叠文件默认使用：

```text
BFP_lib:substrate4.subst
```

注意 ADS 物理 view 目录名是 `em%Setup`，RFPro API 逻辑 view 名是 `emSetup`。自动化命令默认用 `--setup-view em%Setup`，不应写成 `emSetup`，除非确认物理目录就是该名称。

脚本默认使用 `company`。在家里电脑运行时加：

```powershell
--profile home
```

如果家里 ADS 工程里的 Library 名不是 `BFP_lib`，运行时用 `--library <实际Library名>` 覆盖，或修改 `SIM\tools\ads_profiles.py`。

公司 ADS 工作目录：

```text
D:\Work\ADS\6-8G_Fillter\6-8G_Fillter
```

ADS Python：

```text
D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
```

ADS Library：

```text
6-8G_Fillter_lib
```

本仓库自动化脚本目录：

```text
SIM\tools
```

结果输出目录：

```text
SIM\ADS\results
```

## 2. 脚本清单

| 脚本 | 作用 | 运行环境 |
|---|---|---|
| `generate_interdigital_filter_layout.py` | 生成当前九阶交指滤波器 DXF、SVG、参数 JSON、DRC 检查文件 | 普通 Python |
| `generate_filter_sweep.py` | 按 CSV 参数表批量生成候选版图文件 | 普通 Python |
| `ads_import_dxf_add_ports.py` | 导入 DXF 到 ADS Layout，并放置 P1/P2 端口 | ADS Python |
| `ads_clone_emsetup_template.py` | 从已验证模板 Cell 克隆并修正 FEM EM Setup | 普通 Python |
| `ads_run_rfpro_fem.py` | 创建/更新 RFPro view，设置 4-10 GHz FEM 频率计划并启动仿真 | ADS Python / RFPro context |
| `analyze_ads_dataset.py` | 读取 RFPro CSV 或 ADS `.ds` 数据集并输出评分 | 普通 Python 或 ADS Python |
| `export_ads_fem_dataset.py` | 将 ADS FEM `.ds` 数据集导出为文本 | ADS Python |
| `run_ads_filter_candidate.py` | 单个候选项的一站式流程入口 | 普通 Python，内部调用 ADS Python |
| `run_ads_filter_sweep.py` | 批量闭环入口，生成、仿真、评分、汇总 | 普通 Python，内部调用 ADS Python |

## 3. 输入文件

候选参数表采用 CSV 格式。当前示例：

```text
SIM\ADS\filter_sweep_plan.csv
SIM\ADS\filter_opt_round1.csv
SIM\ADS\filter_opt_round2b.csv
SIM\ADS\filter_opt_round3.csv
SIM\ADS\filter_opt_round3_l600.csv
```

CSV 字段：

```text
name,L_mm,tap_mm,Egap_mm,S1_mm,S2_mm,S3_mm,S4_mm,S5_mm,S6_mm,S7_mm,S8_mm,via_diameter_mm,metal_layer,via_layer,notes
```

当前字段对应九阶交指滤波器：

| 字段 | 含义 |
|---|---|
| `name` | 候选项名称，也是 DXF/ADS Cell 命名基础 |
| `L_mm` | 谐振器长度，用于整体频率平移 |
| `tap_mm` | 输入/输出抽头高度，主要影响匹配和边缘插损 |
| `Egap_mm` | 端部间隙，影响端部加载和阻带/边缘折中 |
| `S1_mm`-`S8_mm` | 相邻谐振器间隙，影响耦合强度、带宽、纹波和阻带 |
| `via_diameter_mm` | 接地孔直径 |
| `metal_layer` | ADS 金属层名，当前为 `cond` |
| `via_layer` | ADS 孔层名，当前为 `pcvia1` |
| `notes` | 本轮优化意图说明 |

DXF 单位采用 mm。导入 ADS 时应选择 mm，不能选 mil。

## 4. 单候选项测试流程

建议先用一个候选项跑通，避免批量任务被异常候选项卡住。

```powershell
python SIM\tools\run_ads_filter_candidate.py r3b_t190 --overwrite-setup
```

家里电脑：

```powershell
python SIM\tools\run_ads_filter_candidate.py r3b_t190 --profile home --overwrite-setup
```

FR4 L3 首轮 `-5 dB / -25 dB` 目标，家里 BFP 模板 dry-run/准备命令示例：

```powershell
python SIM\tools\run_ads_filter_candidate.py ssb_l3_25_len108_stubp15 --profile home --template-cell BFP --target-profile fr4_25db --dxf SIM\ADS\fr4_stub_bpf_l3_25db_round1\ssb_l3_25_len108_stubp15_mm_coords.dxf --params SIM\ADS\fr4_stub_bpf_l3_25db_round1\ssb_l3_25_len108_stubp15_params.json --cell ssb_l3_25_len108_stubp15_mm_coords --overwrite-setup --skip-fem
```

该命令会依次执行：

```text
1. 查找候选项 DXF 和参数 JSON
2. 导入 DXF 到 ADS Layout
3. 根据参数 JSON 放置 P1/P2 端口
4. 克隆并修正 FEM EM Setup
5. 创建或更新 RFPro view
6. 设置 FEM 频率范围为 4-10 GHz
7. 启动 FEM 仿真
8. 导出 S 参数 CSV
9. 计算关键指标并写入 score CSV
```

常用调试参数：

```text
--dry-run        只打印命令，不实际运行
--prepare-only   只准备 RFPro view，不启动 FEM
--skip-fem       导入和设置完成后停止
--reuse-layout   复用已有 ADS Layout，跳过 DXF 导入和端口放置
--skip-setup     复用已有 emSetup
--score-only     只对已有结果重新评分
```

输出文件示例：

```text
SIM\ADS\results\r3b_t190_mm_coords_rfpro.csv
SIM\ADS\results\r3b_t190_mm_coords_score.csv
```

## 5. 批量闭环流程

批量入口：

```powershell
python SIM\tools\run_ads_filter_sweep.py --plan SIM\ADS\filter_opt_round3_l600.csv --out-dir SIM\ADS\opt_round3_l600 --results-dir SIM\ADS\results\opt_round3_l600 --summary SIM\ADS\results\opt_round3_l600\sweep_summary.csv
```

家里电脑：

```powershell
python SIM\tools\run_ads_filter_sweep.py --profile home --plan SIM\ADS\filter_opt_round3_l600.csv --out-dir SIM\ADS\opt_round3_l600 --results-dir SIM\ADS\results\opt_round3_l600 --summary SIM\ADS\results\opt_round3_l600\sweep_summary.csv
```

如果版图文件已经生成，可跳过生成步骤：

```powershell
python SIM\tools\run_ads_filter_sweep.py --plan SIM\ADS\filter_opt_round3_l600.csv --out-dir SIM\ADS\opt_round3_l600 --results-dir SIM\ADS\results\opt_round3_l600 --summary SIM\ADS\results\opt_round3_l600\sweep_summary.csv --skip-generate
```

只跑一个候选项：

```powershell
python SIM\tools\run_ads_filter_sweep.py --plan SIM\ADS\filter_opt_round3_l600.csv --out-dir SIM\ADS\opt_round3_l600 --results-dir SIM\ADS\results\opt_round3_l600 --summary SIM\ADS\results\opt_round3_l600\sweep_summary.csv --skip-generate --candidates r3b_t190
```

批量流程输出：

```text
SIM\ADS\results\<round>\<candidate>_mm_coords_rfpro.csv
SIM\ADS\results\<round>\<candidate>_mm_coords_score.csv
SIM\ADS\results\<round>\sweep_summary.csv
```

## 6. FEM 设置策略

当前自动化 FEM 设置来自已验证模板：

```text
interdigital_9o_ro4350b_508um_v3_wide_mm_coords:emSetup
```

克隆脚本会自动修正：

```text
topLibCellView
dataset/display cell names
cosim intermediate cell name
P1/P2 snapshot coordinates
start frequency = 4 GHz
stop frequency  = 10 GHz
points          = 50 (max)
MaxRefineFrequency = 10 GHz
```

RFPro 运行脚本会设置：

```text
solver preset = FEM
frequency plan = Adaptive
frequency range = 4-10 GHz
points = 50
maximum adaptive passes = 15
field storage = disabled
far field = disabled
```

## 7. 评分规则

当前 RO4350 九阶方案评分目标：

```text
S21 @ 5 GHz <= -45 dB
S21 @ 6 GHz >= -3 dB
S21 @ 8 GHz >= -3 dB
6-8 GHz passband minimum S21 >= -3.5 dB
6-8 GHz ripple <= 3 dB
6-8 GHz worst S11/S22 <= -10 dB
```

脚本输出字段：

```text
status
s21_5g_db
s21_6g_db
s21_7g_db
s21_8g_db
s21_9g_db
passband_min_s21_db
passband_ripple_db
worst_s11_6_8_db
worst_s22_6_8_db
```

对于低成本 FR4 高低阻抗带通版本，可将评分目标调整为：

```text
S21 @ 5 GHz <= -20 dB
S21 @ 6 GHz >= -4.5 dB
S21 @ 8 GHz >= -4.5 dB
6-8 GHz passband ripple <= 3.5 dB
6-8 GHz worst S11/S22 <= -8 dB
minimum line/gap >= 0.1524 mm，建议设计值 >= 0.20 mm
```

对于当前 7 阶 FR4 交指/梳状版本，常用评分 profile：

```text
fr4_25db      : 5 GHz <= -25 dB, 6/8 GHz >= -5 dB, S11/S22 <= -5 dB
fr4_25db_rl6  : 5 GHz <= -25 dB, 6/8 GHz >= -5 dB, S11/S22 <= -6 dB
fr4_25db_rl10 : 5 GHz <= -25 dB, 6/8 GHz >= -5 dB, S11/S22 <= -10 dB
```

## 8. EMSETUP 复测边界

RFPro API 批量流程目前稳定，适合进行参数扫频和初筛。EMSETUP 图形界面的 `simulate` 按钮尚未确认有稳定公开 API，可作为最终候选项人工复测路径。

可用数据路径：

```text
D:\Work\ADS\6-8G_Fillter\6-8G_Fillter\data\<cell>_FEM_a.ds
```

对 `.ds` 数据集评分：

```powershell
& "D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe" SIM\tools\analyze_ads_dataset.py "D:\Work\ADS\6-8G_Fillter\6-8G_Fillter\data\r3b_t190_mm_coords_FEM_a.ds" --inspect
```

导出文本：

```powershell
& "D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe" SIM\tools\export_ads_fem_dataset.py --dataset "D:\Work\ADS\6-8G_Fillter\6-8G_Fillter\data\r3b_t190_mm_coords_FEM_a.ds" --out SIM\ADS\results\r3b_t190_FEM_a.txt
```

## 9. 优化闭环建议

当前九阶交指结构的优化顺序：

```text
1. 先调整 tap_mm，改善 S11/S22 和通带边缘插损。
2. 再调整 S1/S8，平衡 5 GHz 抑制和 6/8 GHz 边缘。
3. 再调整 S2/S7、S3/S6、S4/S5，控制带宽和通带纹波。
4. 最后调整 L_mm，进行整体频率平移。
5. 每轮保留 1 个基准项、2-4 个单变量项、2-4 个组合项。
```

FR4 高低阻抗带通结构接入时，建议保持相同自动化接口：

```text
CSV 参数表
  -> Python 版图生成器
  -> DXF + params JSON
  -> ADS 导入和端口放置
  -> FEM setup 克隆/修正
  -> RFPro/FEM
  -> score CSV
  -> sweep_summary.csv
```

需要新增或替换的部分：

```text
generate_hilo_bpf_layout.py
```

该脚本应输出与现有流程兼容的文件：

```text
<candidate>_mm_coords.dxf
<candidate>_params.json
<candidate>_drc.txt
<candidate>.svg
```

并在 params JSON 中提供：

```text
P1/P2 端口坐标
基板参数
关键线宽/间距
边界尺寸
最小加工约束检查结果
```

这样后续只需要修改版图生成器和评分目标，ADS 导入、FEM 设置、仿真和结果汇总流程可以继续复用。

## 10. 推荐执行规范

每一轮优化建议按以下顺序执行：

```text
1. 修改或生成本轮 CSV 参数表。
2. 单候选项 dry-run 检查路径。
3. 单候选项 prepare-only 检查 ADS view 是否生成。
4. 单候选项完整 FEM 测试。
5. 批量运行本轮候选项。
6. 检查 sweep_summary.csv。
7. 选择 2-3 个候选项用 EMSETUP 人工复测。
8. 将最终结论写入 6-8G滤波器设计优化报告。
```

建议批量运行前先执行：

```powershell
python SIM\tools\run_ads_filter_sweep.py --plan <plan.csv> --out-dir <layout_dir> --results-dir <results_dir> --summary <summary.csv> --dry-run
```

确认路径无误后，再执行单候选项测试。单项通过后再运行整批。
