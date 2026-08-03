# 二维码像素滤波器 S21 神经网络代理模型方案

日期：2026-08-02

## 1. 目标

当前目标不是一次性用神经网络替代 ADS/RFPro，而是建立一个能持续反馈的 S 参数代理模型：

- 输入：16x16 二值像素矩阵，必要时附加 via 通道、几何标量和坐标通道。
- 输出：1-10 GHz 采样点上的 S11/S21/S22(dB)。
- 主反馈：从 S21 曲线计算 6-8 GHz 带通、5 GHz 带阻和高边阻带特征，用于筛选下一批像素增删候选。
- 辅助反馈：S11/S22 保留进训练，但只作为低权重回波上下文，不主导候选排序。
- ADS 角色：保留为最终判定器，持续给网络补充真实 FEM 样本。

当前 loss 权重约定为 `S11:S21:S22 = 0.1:1.0:0.1`。也就是说，S11/S22 的惩罚响应明显低于 S21，只帮助网络识别端口匹配/反射背景，最终 6-8 GHz 带通滤波器反馈仍以 S21 为主。

## 2. 为什么不用普通 MLP

原论文像素矩阵为 13x13，即 169 个二值变量。本项目已经进入 16x16，即 256 个二值变量，搜索空间从 `2^169` 增至 `2^256`。如果直接展平后接 MLP，模型需要从样本里自己学会相邻像素连通、边缘耦合、局部 stub、横向通道等结构关系；当前 ADS 样本量远远不够。

因此第一版使用卷积先验：

- 3x3 卷积：捕捉相邻像素、短 stub、局部断裂和桥接。
- depthwise separable conv：参数少，适合小样本。
- dilation=2 block：在 16x16 内扩大感受野，捕捉较长电流路径。
- coordinate channels：让模型知道像素处于左边缘、右边缘、中心馈线附近还是角落；这对端口耦合非常重要。

不采用论文级 14 层 CNN 作为起点。当前样本少，深网络更容易记忆已有样本；先用小型 residual separable CNN，等 R3/R4 样本达到 80-150 个后再加深。

## 3. 当前实现

已新增：

- `src/simads/nn/pixel_qr_surrogate.py`
- `tools/build_pixel_qr_nn_dataset.py`
- `tools/train_pixel_qr_surrogate.py`
- `tools/make_pixel_qr_r3_pixel_mutation_candidates.py`
- `tools/make_pixel_qr_r4_notch_combo_candidates.py`
- `tools/rank_pixel_qr_surrogate_candidates.py`
- `tools/plot_filter_s_curves_svg.py`
- `config/pipelines/pixel_qr_bpf_fr4_210um_home_r3_pixel_mutation_1to10.json`

当前虚拟环境：

```powershell
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe
```

已安装：

```text
torch 2.13.0+cpu
numpy available
```

## 4. 数据集格式

数据集输出：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_s21_nn_dataset.npz
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_s21_nn_dataset.manifest.csv
```

NPZ 字段：

| 字段 | shape | 说明 |
|---|---:|---|
| `x_mask` | `[N, 2, 16, 16]` | 金属 mask + via 直径归一化通道 |
| `x_geom` | `[N, 5]` | pixel、cell pitch、feed width、overlap、via diameter 归一化标量 |
| `freq_ghz` | `[19]` | 默认 1.0, 1.5, ..., 10.0 GHz |
| `y_s_db` | `[N, 3, 19]` | S11/S21/S22(dB) 目标 |
| `y_s21_db` | `[N, 19]` | S21(dB) 目标 |
| `valid_s_mask` | `[N, 3, 19]` | 标记 S11/S21/S22 各频点是否有效 |
| `y_s21_complex` | `[N, 19, 2]` | S21 real/imag，当前保留不用作主 loss |
| `valid_freq_mask` | `[N, 19]` | 标记该样本实际覆盖的频点 |
| `candidate_names` | `[N]` | 候选名 |
| `mask_rows` | `[N]` | 16 行 0/1 mask |

兼容字段 `y_s21_db` 和 `valid_freq_mask` 保留给旧工具使用；新训练优先读取 `y_s_db` 和 `valid_s_mask`。R1 数据原始频段是 4-10 GHz，后续 sweep 是 1-10 GHz；mask 会让训练 loss 忽略缺失频点。

## 5. 网络算子

第一版模型：`PixelQrS21Surrogate`

```text
input mask: [B,2,16,16]
append x/y coordinate channels -> [B,4,16,16]
3x3 conv stem, GroupNorm, SiLU
ResidualSeparableConvBlock dilation=1
ResidualSeparableConvBlock dilation=1
ResidualSeparableConvBlock dilation=2
ResidualSeparableConvBlock dilation=1
global average pooling + max pooling
concat x_geom
MLP curve head -> [B,3,19] S11/S21/S22(dB)
MLP aux head -> [B,7] S21-derived guard features
```

loss：

```text
masked weighted MSE on S11/S21/S22(dB), with S21 primary
S11:S21:S22 = 0.1:1.0:0.1
aux feature loss and curve-derived feature loss use S21 only
```

频点权重：

- 6-8 GHz：最高权重，保证通带拟合。
- 8.5-10 GHz：高权重，保证高边阻带判断。
- 1-5.5 GHz：中高权重，保证低边泄漏判断。
- 5 GHz：额外加权，当前作为低边带阻/notch 观察点。
- 6 GHz / 8 GHz 边缘点额外加权，避免通带边缘塌陷。

## 6. S21 带通反馈指标

从预测曲线计算：

- `passband_min_s21_db`：6-8 GHz 最差 S21，越高越好。
- `passband_avg_s21_db`：6-8 GHz 平均 S21，越高越好。
- `passband_ripple_db`：6-8 GHz 波纹，越低越好。
- `s21_5g_db`：5 GHz 低边抑制，当前希望逐步接近 -20 dB。
- `low_stop_max_s21_db`：1-5.5 GHz 最大泄漏，越低越好。
- `high_stop_max_s21_db`：8.5-10 GHz 最大泄漏，越低越好。
- `bandpass_score_s21`：上述指标合成的代理反馈分数。

当前目标值先按探索级设置：

```text
passband_min_s21_db >= -5 dB
passband_ripple_db <= 3.5 dB
low/high stop max S21 <= -20 dB
```

这不是最终产品指标，只是让模型能朝 6-8 GHz 带通方向筛选。

## 7. R3 并行迭代流程

R3 从 R1 最佳基准出发：

```text
pixel_qr16_fr4_210um_seed0_p035_ov10_fw038_ol045
matrix_n = 16
pixel_mm = 0.35
feed_w_mm = 0.38
coupling_overlap_mm = 0.45
```

候选生成：

- `add02/add04`：左右镜像成对增加像素。
- `remove02/remove04`：左右镜像成对删除像素。
- `toggle02/toggle04`：左右镜像成对翻转像素。
- 第一批 24 个候选，每类 4 个。
- 锁定输入/输出馈线边缘耦合像素，避免完全断开端口。

运行方式：

```powershell
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\make_pixel_qr_r3_pixel_mutation_candidates.py --count-per-mode 4
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\generate_pixel_qr_bpf_layout.py --plan projects\pixel_qr_bpf_fr4_210um\plans\pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10.csv --out-dir projects\pixel_qr_bpf_fr4_210um\layouts\pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10
```

ADS 可以先跑 4-8 个代表候选。每完成一批 RFPro CSV，就重建数据集并训练：

```powershell
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\build_pixel_qr_nn_dataset.py --project-id pixel_qr_bpf_fr4_210um --sweep-id pixel_qr_bpf_fr4_210um_r1 --sweep-id pixel_qr_bpf_fr4_210um_r2_arch_1to10 --sweep-id pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10 --out projects\pixel_qr_bpf_fr4_210um\results\pixel_qr_s21_nn_dataset.npz

D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\train_pixel_qr_surrogate.py --dataset projects\pixel_qr_bpf_fr4_210um\results\pixel_qr_s21_nn_dataset.npz --out projects\pixel_qr_bpf_fr4_210um\results\pixel_qr_s21_surrogate.pt --epochs 500
```

训练后对未仿真的 R3 plan 排序：

```powershell
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe tools\rank_pixel_qr_surrogate_candidates.py --checkpoint projects\pixel_qr_bpf_fr4_210um\results\pixel_qr_s21_surrogate.pt --plan projects\pixel_qr_bpf_fr4_210um\plans\pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10.csv --out projects\pixel_qr_bpf_fr4_210um\results\pixel_qr_r3_surrogate_ranking.csv
```

## 8. R3 当前迭代状态

截至 2026-08-02 home run，R3 已完成 24/24 个候选的 1-10 GHz ADS/RFPro FEM。`run_ads_filter_sweep.py` 已改为每批结束后自动从全部 score CSV 重建全量 summary，避免分批 sweep 覆盖历史结果。训练集已更新为 34 个候选：

```text
R1 8 + R2 2 + R3 24 = 34
```

完整 R3 数据集 300 epoch 重训结果：

```text
epoch=0001 train_loss=75.677 val_loss=70.7015
epoch=0050 train_loss=30.3694 val_loss=29.8447
epoch=0100 train_loss=29.5203 val_loss=29.466
epoch=0150 train_loss=19.0632 val_loss=24.1076
epoch=0200 train_loss=11.774 val_loss=19.353
epoch=0250 train_loss=11.4287 val_loss=17.298
epoch=0300 train_loss=9.43658 val_loss=17.8008
```

结论：34 个样本让验证损失明显低于 26 样本阶段，但仍不足以精准替代 1-10 GHz RFPro 真值。当前 surrogate 的正确角色仍是粗排序、负样本识别和补样建议。R3 的最大信息量在于揭示 5G 抑制和 6-8G 通带之间的冲突：加像素可加深 5G 衰减，但经常破坏 6G 或 8G；轻量 toggle/remove 可保住通带，但 5G 仍只有约 -5 到 -6.6 dB。

R3 S 曲线 SVG 已生成：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r3_pixel_mutation_1to10/svg/
```

其中 `r3_s21_overlay.svg` 是 24 个候选的 S21 叠加图；每个候选另有独立 `*_s_curves.svg`，包含 S11/S21/S22，并标出 5G、6-8G 通带、-5 dB 和 -20 dB 参考线。

当前 R3 真值中最有价值的候选：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值 |
|---|---:|---:|---:|---:|---:|---|
| `r3_toggle02_03` | -5.27 | -2.32 | -0.75 | -3.27 | -14.79 | 当前较强的 6-8G 通带候选，高边 9G 抑制优于 R1。 |
| `r3_toggle02_01` | -5.33 | -3.38 | -0.64 | -2.51 | -7.67 | 通带最平滑，适合作为轻量 toggle 家族参考。 |
| `r3_remove02_01` | -5.56 | -3.79 | -0.99 | -1.78 | -7.04 | 新增 remove02 样本，通带可用但高边抑制一般。 |
| `r3_toggle04_02` | -5.67 | -4.02 | -1.20 | -1.54 | -7.01 | 4 对翻转未明显破坏通带，可作为中等扰动样本。 |
| `r3_add02_02` | -6.64 | -4.64 | -1.34 | -1.17 | -10.21 | add02 中最均衡，通带仍可用并保留一定高边抑制。 |
| `r3_toggle04_03` | -6.40 | -4.21 | -0.94 | -1.72 | -4.71 | 通带可传但高边很差，不宜作为主优化方向。 |
| `r3_toggle02_02` | -6.44 | -4.39 | -1.21 | -1.12 | -8.69 | 6G 边缘偏低，但高边略好于普通 toggle。 |
| `r3_remove02_03` | -6.50 | -5.16 | -2.79 | -0.68 | -15.25 | 高边抑制强，但 6G 已偏低，适合学习高边滚降代价。 |
| `r3_remove02_00` | -6.77 | -5.52 | -3.31 | -1.10 | -9.56 | 6G 边缘过低，作为 remove02 边界样本保留。 |

5G 抑制最强但通带代价过大的样本：

- `r3_add04_02`：5G -9.99 dB，但 6G -15.45 dB，通带被严重损坏。
- `r3_add02_01`：5G -9.19 dB，但 6/7/8G 为 -9.05/-8.33/-7.04 dB，整体偏阻带。
- `r3_add04_01`：5G -9.17 dB，但 6/7/8G 为 -8.99/-8.19/-6.78 dB，通带不足。
- `r3_add04_03`：5G -8.27 dB，8G 尚可但 6G 只有 -7.23 dB，高边也差。

不宜继续作为主优化方向的模式：

- `remove04_*`：真实结果显示 7-8G 大面积塌陷，适合作为负样本，不宜作为当前 BPF 主方向。
- `add04_*`：能增强 5G 衰减，但大多伴随 6G 或 8G 通带崩塌，只能作为低边 notch 机制参考。
- `toggle02_00` / `toggle04_00`：8G 深陷，证明普通 toggle 对位置高度敏感。

R4 不应继续盲目 add/remove/toggle。下一批应从 `toggle02_03` 或 `remove02_03` 出发，只在少数局部区域引入 add02/add04 中导致 5G 衰减的像素/stub 机制，并设置 6G guard：候选在代理模型中若预测 S21@6G 低于约 -5.5 dB，则不优先送 RFPro。

## 9. R4 notch-combo 计划

已新增 R4 确定性组合生成器：

```text
tools/make_pixel_qr_r4_notch_combo_candidates.py
```

R4 不再随机翻转像素，而是用 R3 真值筛出的结构关系生成候选：

- 通带母版：`r3_toggle02_03`、`r3_remove02_03`、`r3_add02_02`。
- notch donor：`r3_add04_02`、`r3_add02_01`、`r3_add04_01`、`r3_add02_00`。
- 操作方式：计算 donor 相对 R1 基准新增的镜像像素组，只向通带母版加入 1-3 组；对 `remove02_03` 额外提供 1-2 组 R1 restore，用于补偿 6G 边缘。
- 候选数：24 个。

当前产物：

```text
projects/pixel_qr_bpf_fr4_210um/plans/pixel_qr_bpf_fr4_210um_r4_notch_combo_1to10.csv
projects/pixel_qr_bpf_fr4_210um/layouts/pixel_qr_bpf_fr4_210um_r4_notch_combo_1to10/
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_r4_notch_combo_surrogate_ranking.csv
config/pipelines/pixel_qr_bpf_fr4_210um_home_r4_notch_combo_1to10.json
```

`rank_pixel_qr_surrogate_candidates.py` 已增加：

```text
--sort-mode guarded-r4 --guard-db -5.5
```

guarded R4 排序会先筛 `pred_guard_pass=true`，即预测 `S21@6G`、`S21@8G` 和 6-8G 最差 S21 都不低于 -5.5 dB，再按 guarded score 排序。当前 surrogate 推荐优先送 ADS 的前 8 个 R4 候选为：

| 排名 | 候选 | guard | pred S21@5G | pred S21@6G | pred S21@8G | 说明 |
|---:|---|---|---:|---:|---:|---|
| 1 | `r4_04_toggle02_03_add02_01_keep_a01` | true | -6.42 | -5.02 | -4.24 | 通带母版 `toggle02_03`，加入 1 组 `add02_01` notch 像素。 |
| 2 | `r4_07_toggle02_03_add04_01_keep_a02` | true | -6.53 | -5.12 | -4.01 | 加 2 组 `add04_01` notch 像素，5G 略深。 |
| 3 | `r4_01_toggle02_03_add04_02_keep_a01` | true | -6.50 | -5.09 | -4.00 | 从最强 5G donor 只取 1 组像素，避免整体照搬。 |
| 4 | `r4_02_toggle02_03_add04_02_keep_a02` | true | -6.76 | -5.34 | -3.48 | 5G 更深，但 6G 已接近 guard 下限。 |
| 5 | `r4_11_remove02_03_add04_02_keep_a01` | true | -6.77 | -5.36 | -3.29 | 高边母版 `remove02_03`，加入 1 组最强 notch donor。 |
| 6 | `r4_20_remove02_03_add02_01_keep_a01` | true | -6.73 | -5.33 | -3.29 | `remove02_03` + `add02_01`，用于对比 donor 类型。 |
| 7 | `r4_14_remove02_03_add04_02_repair1_a01` | true | -6.88 | -5.47 | -2.97 | restore 1 组 R1 像素后再加 notch，6G 接近下限。 |
| 8 | `r4_22_remove02_03_add02_01_repair1_a01` | true | -6.86 | -5.45 | -2.94 | repair 版本对照，适合验证补 6G 的代价。 |

layout/pipeline gate：

- `check_pipeline_contract.py` 对 R4 sweep 已 PASS。
- 前 4 个 guarded 排名候选的 `check_layout_contract.py` 已 PASS。
- 抽检最小分离间距为 0.1425 mm，高于 0.1016 mm 约束。

## 10. 待办

P0 已完成：

- [x] 安装 PyTorch 到 `D:\Microsoft\uv-venvs\ads-automation`。
- [x] 建立 S 参数 dataset builder，并保留 S21 兼容字段。
- [x] 建立小型 CNN surrogate 和训练入口。
- [x] 合并 R1/R2 数据集，当前 10 个候选。
- [x] 完成 5 epoch 训练 smoke。
- [x] 建立 R3 24 个像素增删/翻转候选，并通过 pipeline/layout 抽样 gate。
- [x] 建立 surrogate ranking CLI，用于训练后对 plan 候选排序。
- [x] 用 ADS/RFPro 跑完 R3 24 个候选，并把训练集扩展到 34 个样本。
- [x] 修正 `run_ads_filter_sweep.py` 分批 sweep 覆盖 summary 的问题，结束时自动重建全量 summary。
- [x] 将 5 GHz notch 观察点加入 surrogate 特征、loss 权重和 ranking 输出。
- [x] 生成 R3 SVG S 曲线，包括 24 个单候选曲线和 `r3_s21_overlay.svg`。
- [x] 建立 R4 notch-combo 候选生成器，生成 24 个局部组合候选。
- [x] 为 R4 增加 guarded ranking，优先保留 6G/8G/passband guard 通过的候选。
- [x] 生成 R4 版图并通过 pipeline contract；前 4 个候选 layout contract 已抽检通过。

P1 下一步：

- [ ] 先送 R4 guarded 排名前 4-8 个候选进入 ADS/RFPro。
- [ ] 持续记录 `filter_features.csv` 中 1-3G、5G、6-8G、8.5-10G 分段特征。
- [ ] 增加 collapse 分类头或分层验证集，避免 surrogate 把 `remove04` 类断裂结构排到前面。
- [ ] 当样本达到 40 个后，评估留出集 6-8G 平均误差是否低于 2 dB。
- [ ] 评估是否引入短路像素/接地过孔/via-aware schema；纯二值像素目前未能在保住 6-8G 的同时把 5G 拉到 -20 dB。

P2 后续：

- [ ] 加入不确定性估计：小型 ensemble 或 MC dropout。
- [ ] 新增 GA/交叉/变异提案脚本：网络先筛，再交给 ADS 验证。
- [ ] 若断连候选太多，增加 mask 连通性过滤和孤岛上限。
- [ ] 若低边抑制仍无改善，引入短路像素/接地过孔规则，单独建 via-aware mask schema。
- [ ] 样本达到 80-150 后，评估更深 CNN 或 frequency-query head。

## 11. 判断标准

神经网络进入可用状态的最低条件：

- 样本数不少于 40，且包含 add/remove/toggle、edge_stubs、qr_sparse 三类机制。
- 留出验证集上 6-8 GHz 通带 S21 平均误差小于 1.5-2.0 dB。
- 对 R2 高边阻带模型的排序不能反向：`qr_sparse_s1` 的 8.5-10 GHz 抑制应明显优于 R1 基准。
- 网络推荐的前 5 个候选中，至少 1 个 ADS 结果在 `bandpass_score_s21` 上优于 R1 基准。

## 12. R4 16/24 ADS 状态与模型修正

截至 2026-08-02 01:15 home run，R4 已完成 16/24 个候选的 1-10 GHz ADS/RFPro。R4 SVG 已刷新到：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r4_notch_combo_1to10/svg/
```

其中包含 16 个单候选 `*_s_curves.svg` 和 1 个 overlay。当前训练集为：

```text
R1 8 + R2 2 + R3 24 + R4 16 = 50
```

R4 真值中最有价值的模型：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 通带最差 | 判断 |
|---|---:|---:|---:|---:|---:|---:|---|
| `r4_06_toggle02_03_add04_01_keep_a01` | -5.84 | -3.21 | -0.47 | -3.35 | -14.54 | -3.44 | 通带最稳，9G 抑制保持在约 -14.5 dB。 |
| `r4_03_toggle02_03_add04_02_keep_a03` | -6.06 | -3.54 | -0.46 | -2.49 | -14.98 | -3.54 | 当前最均衡模型，5G 略深、8G 边缘好、9G 约 -15 dB。 |
| `r4_02_toggle02_03_add04_02_keep_a02` | -5.63 | -2.61 | -0.80 | -3.02 | -18.19 | -3.64 | 高侧阻带最好的一档，9G 接近 -18 dB。 |
| `r4_07_toggle02_03_add04_01_keep_a02` | -6.35 | -4.00 | -0.56 | -3.39 | -14.15 | -4.00 | 5G 比 `r4_06` 深约 0.5 dB，但 6G 代价更大。 |
| `r4_01_toggle02_03_add04_02_keep_a01` | -5.61 | -2.59 | -0.87 | -3.47 | -18.52 | -4.02 | 高侧 9G 最深之一，但 8G 边缘略差。 |
| `r4_04_toggle02_03_add02_01_keep_a01` | -6.98 | -5.04 | -1.20 | -3.85 | -14.06 | -5.04 | 5G 更深，但已经贴近 6G guard 下限。 |

失败但有训练价值的模型：

- `r4_08` / `r4_05`：5G 分别到 -8.51/-8.92 dB，但 6G/7G 被一起压低，通带最差为 -8.08/-8.51 dB；这是“5G 变深但 BPF 失效”的关键负样本。
- `remove02_03` repair 组：`r4_17/r4_13/r4_14/r4_19` 的 5G 约 -7.4 到 -7.7 dB，但 6G 仍约 -5.9 到 -6.3 dB，repair 没有有效补回 6G。

神经网络算子已修正：

- `PixelQrS21Surrogate` 从单一 global average pooling 改为 average pooling + max pooling 拼接。原因是少数局部像素可能导致通带塌陷，average pooling 会稀释这种局部破坏。
- 训练脚本加入多任务监督：19 点 S21 曲线回归 + 辅助特征 head + 从预测曲线派生的特征 loss。
- 辅助特征包括 `passband_min`、`passband_ripple`、`S21@5G`、`S21@6G`、`S21@8G`、`S21@9G`、`high_stop_max`。

50 样本模型 300 epoch 训练记录：

```text
epoch=0001 train_loss=94.9028 curve=70.1859 aux=83.9948 feat=79.1794 val_loss=90.8041
epoch=0050 train_loss=33.1169 curve=23.166 aux=31.4278 feat=36.6535 val_loss=37.1132
epoch=0100 train_loss=15.7246 curve=11.3289 aux=14.4572 feat=15.0421 val_loss=38.2044
epoch=0150 train_loss=7.73575 curve=5.71668 aux=6.69054 feat=6.80968 val_loss=34.7054
epoch=0200 train_loss=5.04091 curve=3.69073 aux=4.43701 feat=4.6278 val_loss=33.6679
epoch=0250 train_loss=3.16445 curve=2.15498 aux=3.63499 feat=2.82471 val_loss=35.6544
epoch=0300 train_loss=2.23601 curve=1.55858 aux=2.46594 feat=1.8424 val_loss=36.2824
```

脚本会保存 best validation state。当前模型已能把 `r4_08/r4_05` 的 6G 预测压到约 -6 dB，方向上学到了这类局部组合的通带破坏风险。最终 R4 ranking 前 6 名全部回到已验证的 `toggle02_03` 正样本：

```text
r4_03, r4_02, r4_07, r4_06, r4_04, r4_01
```

下一步判断：

1. `r4_03` 可作为当前最好的平衡基底；`r4_02/r4_01` 可作为高侧 9G 深阻带基底。
2. 纯悬浮像素组合仍不能把 5G 推向 -20 dB，同时保住 6-8G 通带。
3. 下一轮应新建 via-aware/shorted-stub 候选族，把 5G notch 机制从普通像素填充中分离出来。
4. 未仿真的 8 个 R4 候选可作为补充负样本跑完，但不应继续把 R4 普通悬浮像素作为主路线。

## 13. R6-R8 via-aware 迭代状态

截至 2026-08-02 02:49 home run，数据集已经扩展为：

```text
R1 8 + R2 2 + R3 24 + R4 16 + R5/R6/R7/R8 via-aware samples = 99
```

当前神经网络输入已经不是单通道金属图，而是双通道：

- channel 0：16x16 金属像素 mask。
- channel 1：16x16 via mask，并按 `via_diameter_mm / 0.18` 归一化。

这使代理模型能学习接地过孔位置和直径，而不是把所有 via-aware 样本误当成同一个金属 mask。当前训练已经升级为 S11/S21/S22 三通道曲线，其中 S21 是主反馈，S11/S22 以低权重辅助模型保留回波上下文。

R6/R7 真值给出的关键结构规律：

| 结构 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 判断 |
|---|---:|---:|---:|---:|---:|---|
| `r6_08_r4_02_via_r08c04_d0p18` | -15.26 | -2.89 | -1.75 | -2.23 | -16.13 | row8 c04/c11 接地过孔对是当前最有价值的 5G notch 机制。 |
| `r6_09_r4_02_via_r08c04_d0p22` | -16.08 | -3.69 | -1.58 | -2.49 | -16.32 | 更深 5G，但 6G 代价更大。 |
| `r7_04_d0p18_add_r09c04` | -15.25 | -2.84 | -1.93 | -2.12 | -16.12 | 下侧 r09c04 加金属可保持 notch，同时不损坏通带。 |
| `r7_05_d0p18_add_r09c05` | -15.55 | -3.31 | -2.06 | -2.01 | -16.34 | 下侧内肩部略加深 5G，6G 代价可接受。 |
| `r7_16_d0p22_add_r09c04` | -16.92 | -4.78 | -2.01 | -1.60 | -15.95 | 5G 最强但接近 6G guard。 |
| `r7_02_d0p18_add_r07c03` | -26.61 | -19.46 | -8.08 | -3.17 | -6.94 | 上侧加金属会把 5G 陷波拖入通带，是重要负样本。 |

R8 已建立：

- generator: `tools/make_pixel_qr_r8_lower_shoulder_via_refine_candidates.py`
- pipeline: `config/pipelines/pixel_qr_bpf_fr4_210um_home_r8_lower_shoulder_via_refine_1to10.json`
- plan: `projects/pixel_qr_bpf_fr4_210um/plans/pixel_qr_bpf_fr4_210um_r8_lower_shoulder_via_refine_1to10.csv`
- layouts: `projects/pixel_qr_bpf_fr4_210um/layouts/pixel_qr_bpf_fr4_210um_r8_lower_shoulder_via_refine_1to10/`
- SVG: `projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r8_lower_shoulder_via_refine_1to10/svg/`

R8 已完成 14/20 个候选的 ADS/RFPro：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值 |
|---|---:|---:|---:|---:|---:|---|
| `r8_11_d0p20_add_r09c04` | -16.26 | -3.89 | -2.10 | -1.76 | -16.02 | 当前最好的直径插值样本，接近 d0.22 的 5G，6G 好于 `r7_16`。 |
| `r8_15_d0p20_add_r09c04_r10c04` | -16.21 | -3.88 | -2.05 | -1.77 | -15.95 | row10 下延与 `r8_11` 近似等价，没有明显额外收益。 |
| `r8_13_d0p20_add_r09c04_r09c05` | -16.04 | -3.87 | -1.93 | -1.97 | -16.18 | d0.20 双肩部组合与 `r8_11/r8_15` 同级，但没有更优。 |
| `r8_14_d0p20_add_r10c04` | -16.01 | -3.68 | -1.73 | -2.13 | -16.07 | 单独 row10 外肩部可用，但不优于 r09c04。 |
| `r8_12_d0p20_add_r09c05` | -15.95 | -3.79 | -1.88 | -1.94 | -15.97 | d0.20 内肩部可用，略弱于外肩部。 |
| `r8_20_d0p22_add_r09c04_r10c04` | -16.84 | -4.70 | -1.94 | -1.59 | -15.71 | d0.22 组合可加深 5G，但主通带最差约 -6 dB，6G guard 风险高。 |
| `r8_18_d0p22_add_r09c04_r09c05` | -16.77 | -4.77 | -1.93 | -1.72 | -16.10 | 与 d0.22 单肩部同类，强 notch 伴随低边通带下沉。 |
| `r8_19_d0p22_add_r10c04` | -16.32 | -3.97 | -1.65 | -2.36 | -16.34 | d0.22 肩部远离 via 后 6G 可恢复，但 5G 不优于 d0.20 平衡点。 |
| `r8_08_d0p18_add_r09c04_r09c05` | -15.56 | -3.39 | -1.95 | -2.02 | -16.30 | 0.18 mm 组合肩部比单肩略深，但收益有限。 |
| `r8_10_d0p18_add_r09c04_r10c04` | -15.56 | -3.19 | -2.05 | -1.91 | -16.14 | 0.18 mm 纵向外肩部扩展，未显著优于 R7 单肩部。 |
| `r8_09_d0p18_add_r10c04` | -15.43 | -3.04 | -1.84 | -2.27 | -16.40 | row10 外肩部单独可作为弱对照。 |
| `r8_05_d0p16_add_r09c04_r10c04` | -14.84 | -2.44 | -2.09 | -2.05 | -16.18 | d0.16 组合通带好，但 5G notch 不足。 |
| `r8_03_d0p16_add_r09c04_r09c05` | -14.66 | -2.48 | -2.00 | -2.19 | -16.26 | d0.16 双肩部仍不能达到 d0.18/d0.20 的 5G 抑制。 |
| `r8_01_d0p16_add_r09c04` | -14.51 | -2.06 | -1.95 | -2.63 | -16.87 | 弱 via 可恢复 6G，但 5G notch 明显变浅。 |

当前代理模型使用 99 样本全量训练：

```text
epoch=0001 train_loss=297.748 curve=258.814 aux=128.327 feat=132.677 val_loss=282.903
epoch=0050 train_loss=92.1533 curve=76.8348 aux=50.6311 feat=51.9229 val_loss=90.6347
epoch=0100 train_loss=42.9516 curve=30.8537 aux=39.307 feat=42.3646 val_loss=41.0982
epoch=0150 train_loss=28.1262 curve=20.0087 aux=26.575 feat=28.0245 val_loss=24.6595
epoch=0200 train_loss=17.9607 curve=13.0698 aux=16.476 feat=15.9574 val_loss=16.23
epoch=0250 train_loss=13.0027 curve=9.34174 aux=12.414 feat=11.7816 val_loss=11.9146
epoch=0300 train_loss=7.68468 curve=5.76434 aux=6.54274 feat=6.11787 val_loss=6.11502
```

注意：这里的 `val_loss` 是 `--val-fraction 0` 下的全量监控值，不是独立验证集。当前阶段 ADS/RFPro 仍然是验证器，surrogate 只负责候选排序和负样本识别。

更新后的 R8 ranking 已调整为更保守的通带优先评分：`tools/rank_pixel_qr_surrogate_candidates.py` 的 guarded score 现在直接奖励 `passband_min` 余量、惩罚 ripple，并降低 5G 深 notch 的相对权重。这个 ranking 更适合作为“补样选择器”；最终最佳结构仍以 ADS 真值为准，目前为 `r8_11/r8_15/r8_13` 这一组 d0.20 下侧肩部近邻。

## 14. 更新后的待办

P0 已完成：

- [x] 引入 via mask/diameter 输入通道。
- [x] 建立 R7 固定 via + 局部金属 trim 候选。
- [x] 建立 R8 lower-shoulder/via-refine 候选。
- [x] 为 R7/R8 生成 S11/S21/S22 单曲线 SVG 和 S21 overlay SVG。
- [x] 将 R1-R8 合并为 99 样本 S21 训练集。

P1 下一步：

- [ ] R8 不重复仿真与 R7 等价的 `d0p18/d0p22 add_r09c04/add_r09c05` 单肩部候选。
- [x] 已补 `r8_03_d0p16_add_r09c04_r09c05`、`r8_05_d0p16_add_r09c04_r10c04`、`r8_18_d0p22_add_r09c04_r09c05`、`r8_20_d0p22_add_r09c04_r10c04`，确认 d0.16 notch 不足、d0.22 通带边界风险高。
- [x] 继续补 `r8_13_d0p20_add_r09c04_r09c05`、`r8_19_d0p22_add_r10c04`，确认 d0.20 组合接近饱和、d0.22 远肩部不优于 d0.20。
- [x] 修正 guarded ranking：提高 `passband_min` 和 ripple 权重，降低单纯追深 5G 的排序优势。
- [ ] 新建 R9 时不要继续只做 row7/row8 去金属；R7 已证明这类操作容易把 5G 陷波拖进 6G。
- [ ] R9 应考虑第二个可控自由度：feed overlap 小幅补偿、via 位置半格/相邻列扫描，或引入独立短路 stub，而不是继续堆同一区域像素。
- [ ] 增加“等价候选过滤”，避免跨 sweep 重复仿真同一 metal/via mask。

P2 后续：

- [ ] 建立独立验证切分策略：按结构族分层，而不是随机抽样。
- [ ] 增加不确定性估计，优先仿真代理分歧大的候选。
- [ ] 若 5G 仍卡在 -16 到 -17 dB，转向双 notch / 双接地 stub 机制，而不是继续加深单 via 对。

## 15. R9 feed/overlap 补偿闭环

截至 2026-08-02 05:46 home run，R9 已完成 8/14 个候选的 1-10 GHz ADS/RFPro。R9 固定 `r8_11_d0p20_add_r09c04` 的金属 mask、row8 c04/c11 过孔对和 0.20 mm via，只扫描：

```text
feed_w_mm = 0.36, 0.38, 0.40
coupling_overlap_mm = 0.40, 0.43, 0.45, 0.47, 0.50
```

新增脚本与产物：

- `tools/make_pixel_qr_r9_feed_overlap_comp_candidates.py`
- `config/pipelines/pixel_qr_bpf_fr4_210um_home_r9_feed_overlap_comp_1to10.json`
- `projects/pixel_qr_bpf_fr4_210um/plans/pixel_qr_bpf_fr4_210um_r9_feed_overlap_comp_1to10.csv`
- `projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r9_feed_overlap_comp_1to10/svg/`

R9 真实结果：

| 候选 | feed/overlap | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 判断 |
|---|---|---:|---:|---:|---:|---:|---|
| `r9_04_fw0p36_ol0p47` | 0.36 / 0.47 | -16.34 | -3.90 | -2.14 | -2.07 | -16.79 | R9 最有价值平衡点；5G 略深于 R8_11，高边 9G 明显更深，但 7/8G 稍弱。 |
| `r9_05_fw0p36_ol0p50` | 0.36 / 0.50 | -16.61 | -4.34 | -2.11 | -1.72 | -16.28 | 5G 更深，但 6G 下沉，作为强耦合边界样本。 |
| `r9_08_fw0p38_ol0p47` | 0.38 / 0.47 | -16.27 | -3.96 | -1.98 | -1.79 | -15.97 | 与 R8_11 很接近，没有明显新增收益。 |
| `r9_09_fw0p38_ol0p50` | 0.38 / 0.50 | -16.48 | -4.24 | -2.04 | -1.62 | -15.82 | 5G 加深但 6G 代价增大。 |
| `r9_11_fw0p40_ol0p43` | 0.40 / 0.43 | -16.05 | -3.78 | -1.93 | -1.71 | -15.60 | 6G 恢复一点，但 5G/9G 变浅。 |
| `r9_12_fw0p40_ol0p45` | 0.40 / 0.45 | -16.10 | -3.83 | -1.97 | -1.62 | -15.47 | 宽 feed 可改善通带边缘，但削弱阻带。 |
| `r9_13_fw0p40_ol0p47` | 0.40 / 0.47 | -16.24 | -4.02 | -1.91 | -1.67 | -15.61 | 介于 `r9_11` 和 `r9_14` 之间。 |
| `r9_14_fw0p40_ol0p50` | 0.40 / 0.50 | -16.03 | -3.80 | -1.82 | -1.70 | -15.39 | 通带均值最好，但低边/高边阻带变浅。 |

R9 结论：

1. feed/overlap 是有用的补偿自由度，但不是突破 5G -20 dB 的主机制。
2. 窄 feed + 中高 overlap 可稍微加深 5G 和 9G，代表样本为 `r9_04`。
3. 宽 feed 可恢复 6G，但通常牺牲 5G notch 和 9G 高边抑制，代表样本为 `r9_11/r9_14`。
4. R9 没有推翻当前首选：若重视整体平衡仍看 `r8_11`；若更重视高边 9G，可把 `r9_04` 作为备选。

神经网络也已更新为 geometry-aware 输入。当前 dataset 字段新增：

```text
x_geom: [N,5]
pixel_mm/0.35, cell_pitch_mm/0.35, feed_w_mm/0.38, coupling_overlap_mm/0.45, via_diameter_mm/0.18
```

最终训练集规模：

```text
R1-R8 99 + R9 8 = 107 samples
```

107 样本全量训练记录：

```text
epoch=0300 train_loss=7.56948 curve=5.71686 aux=6.03827 feat=6.44962 val_loss=4.94007
```

注意：`--val-fraction 0` 下的 `val_loss` 仍是全量监控，不是独立验证。

## 16. 下一轮 R10 建议

R10 不建议继续大批扫描 feed/overlap，也不建议继续堆 row9/row10 下侧肩部像素。当前需要第二个可控 notch 自由度：

- 以 `r8_11` 或 `r9_04` 为基底。
- 保留 row8 c04/c11 主 via pair。
- 小规模扫描第二 via pair 或独立短路 stub，优先放在已存在金属肩部，例如 row9 c04/c11 或 row10 内侧已有金属点。
- 第二 via 直径先从 0.12/0.14/0.16 mm 起步，避免一开始把 5G notch 拖入 6G。
- 必须保留 6G guard：S21@6G 不低于约 -5.0 到 -5.5 dB。

未仿真的 R9 低 overlap 点可暂不补跑，除非需要完整 feed response surface；它们预计更可能恢复 6G、同时削弱 5G/9G。

## 17. R10/R11 二过孔机制结论

R10/R11 已把训练集扩展到 115 个 ADS/RFPro 真值样本，并验证了 `via_diameter_rows` 的必要性：同一版图内可以同时存在 0.20 mm 主过孔和 0.105-0.16 mm 弱过孔，神经网络数据集也已经按逐像素 via diameter 编码。

R10 的第二弱过孔能把 5 GHz notch 推到约 -19 dB，但 6 GHz 同时跌到 -7 dB 量级；R11 把第二过孔降到 0.105 mm 并尝试 feed recovery 后，5 GHz 仍可到 -18 dB 左右，但最佳 `r11_07` 的 6 GHz 仍只有 -6.28 dB。结论是：第二过孔机制有价值，但当前耦合太强，不能作为平衡 BPF 主线；它应保留为负样本/边界样本，帮助模型识别“5G 深但 6G 被拖垮”的结构。

当前最佳真实模型仍是：

| 层级 | 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G |
|---|---|---:|---:|---:|---:|---:|
| 平衡首选 | `r8_11_d0p20_add_r09c04` | -16.26 | -3.89 | -2.10 | -1.76 | -16.02 |
| 高边备选 | `r9_04_fw0p36_ol0p47` | -16.34 | -3.90 | -2.14 | -2.07 | -16.79 |
| R11 最好但未过 guard | `r11_07_fw0p40_ol0p43_r10c05_d0p105` | -18.22 | -6.28 | -1.64 | -1.78 | -15.88 |

最终 115 样本全量训练记录：

```text
epoch=0300 train_loss=5.64499 curve=4.17959 aux=4.82248 feat=5.00905 val_loss=4.28996
```

注意：`--val-fraction 0` 下 `val_loss` 是全量监控，不是独立验证。

R10/R11 SVG：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r10_second_weak_via_1to10/svg/
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r11_ultra_weak_via_feed_recovery_1to10/svg/
```

## 18. R12 当前执行计划

R12 不再增加第二过孔，改为弱金属-only notch perturbation：

- 基底：`r8_11` 和 `r9_04`。
- 保持：row8 c04/c11 主接地过孔对，直径 0.20 mm。
- 操作：仅在 row10-row12、col4-col6 附近做 1-2 组镜像金属增加/减少。
- 目的：寻找比 R10/R11 更弱的 5G notch 扰动，优先保住 `S21@6G >= -5.5 dB`。

本轮待办：

- [x] 生成 R12 plan/layout。
- [x] 用 surrogate 做 guarded ranking。
- [x] ADS/RFPro 首跑 6 个 guard 通过或最有信息量的候选。
- [x] 输出 R12 `filter_features.csv` 和 SVG S 曲线。
- [x] 将 R12 真值并入数据集并重训 surrogate。

## 19. S11/S22 低权重辅助训练状态

截至 2026-08-02，代理模型已经从 S21-only 升级为三通道 S 参数曲线模型：

- 数据集：`projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_s21_nn_dataset.npz`
- 样本数：145 个候选，包含 R1-R16 已完成仿真。
- 输入：`x_mask=[N,2,16,16]`，金属通道 + via 直径归一化通道；`x_geom=[N,5]`。
- 输出：`y_s_db=[N,3,19]`，顺序为 `S11/S21/S22`。
- 训练权重：`S11:S21:S22 = 0.1:1.0:0.1`。
- 排序反馈：`rank_pixel_qr_surrogate_candidates.py` 仍只使用预测 S21 派生 5G、6-8G、9G 特征和 guard；S11/S22 仅作为低权重回波上下文。

145 样本、300 epoch 全量训练监控：

```text
epoch=0300 train_loss=7.16575 curve=5.50437 aux=5.6298 feat=5.35421 val_loss=5.21454
```

注意：`--val-fraction 0` 下 `val_loss` 是全量监控，不是独立验证。checkpoint 位于：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_s21_surrogate.pt
```

R12 重新排序后，surrogate 前两名仍是已仿真的 `rm_r10c05` 结构：

| 排名 | 候选 | 预测 S21@5G | 预测 S21@6G | 预测 S21@8G | 判断 |
|---:|---|---:|---:|---:|---|
| 1 | `r12_08_r8b_rm_r10c05` | -15.88 | -3.73 | -2.46 | 通带恢复/高边稳定样本，不是更深 5G notch。 |
| 2 | `r12_18_r9h_rm_r10c05` | -15.88 | -3.74 | -2.46 | 与 R12 已仿真结论一致，保通带优先。 |
| 3 | `r12_02_r8b_add_r11c05` | -16.08 | -3.95 | -2.21 | 预测略增强 5G，但真实样本显示 6G 代价更明显。 |

R12 的价值结论：弱金属-only 扰动没有突破 R8/R9 的 5G 抑制上限，主要贡献是补充“通带恢复”和“弱 notch 代价”的监督样本。下一轮不应继续大批量扫同类弱金属，而应寻找能把 5G notch 与 6G 下边沿解耦的新算子。

## 20. R13 远端弱短路 pad 结果

R13 新增 `remote_weak_shorted_pad_notch_probe` 算子，用于验证介于 R12 metal-only 和 R10/R11 second-via 之间的机制：

- 基底：`r8_11_d0p20_add_r09c04` 和 `r9_04_fw0p36_ol0p47`。
- 保持：row8 c04/c11 主接地过孔对，直径 0.20 mm。
- 新增：row11-row12、col4-col6 远端小金属 pad/stub，并用 0.105 mm 弱接地过孔短路。
- 目标：寻找比 R12 更强、但比 R10/R11 更不伤 6G 的 5G notch 算子。

R13 已完成 6 个 ADS/RFPro 真值样本，SVG 位于：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r13_remote_shorted_pad_1to10/svg/
```

关键结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值判断 |
|---|---:|---:|---:|---:|---:|---|
| `r13_01_r8b_pad_r11c05_via` | -19.43 | -8.52 | -1.03 | -2.13 | -14.76 | 5G 接近目标，但 6G 严重失守。 |
| `r13_02_r8b_pad_r11c06_via` | -19.39 | -8.57 | -1.02 | -2.27 | -15.15 | surrogate 曾误判为 guard 通过，实测证明仍过耦合。 |
| `r13_04_r8b_pad_r12c04_via` | -19.37 | -8.46 | -1.10 | -1.96 | -14.73 | 远端外侧 pad 仍会把 notch 拖入 6G。 |
| `r13_05_r8b_stub_r11c05_r12c05_via_r12` | -19.50 | -8.69 | -1.07 | -1.99 | -14.91 | 两像素 stub 更强，6G 代价更大。 |
| `r13_10_r9h_pad_r11c06_via` | -19.58 | -8.75 | -1.07 | -2.30 | -15.38 | R9 feed 条件不能恢复 6G。 |
| `r13_15_r9h_shift_r10c05_to_r11c05_via` | -19.57 | -8.68 | -1.11 | -2.12 | -15.13 | 平移 second via 不能解耦 5G/6G。 |

R13 结论：0.105 mm 远端短路 pad 仍然过强，所有实测样本都把 5G 拉深到约 -19.4 到 -19.6 dB，同时把 6G 拉到约 -8.5 到 -8.8 dB。该家族不应继续作为主线扩展，但非常适合训练网络识别“5G 接近目标但 6G 失守”的负样本。

并入 R13 后，surrogate 已将 R13 全部候选重新判为 `guard=false`；最终 R13 ranking 前几名的预测 passband min 也低于 -6.6 dB。这说明新样本已纠正模型对远端弱短路 pad 的乐观误判。

## 21. R14 浮置开路 stub/slit 结果

R14 新增 `floating_stub_slit_notch_probe` 算子，用于验证“不新增第二接地过孔”的 5G notch 机制：

- 基底：`r8_11_d0p20_add_r09c04` 和 `r9_04_fw0p36_ol0p47`。
- 保持：row8 c04/c11 主接地过孔对，直径 0.20 mm。
- 新增/修改：row10-row12、col5-col6 附近的浮置开路 stub、远端金属 pad、局部 slit，并少量增加 overlap 作为 6G 恢复补偿。
- 训练/排序原则：S21 是主反馈；S11/S22 只以 0.1 权重作为回波上下文。

R14 已生成 24 个候选，完成 6 个 ADS/RFPro 真值样本，SVG 位于：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r14_floating_stub_slit_1to10/svg/
```

关键结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值判断 |
|---|---:|---:|---:|---:|---:|---|
| `r14_03_r8b_open_stub_r11c05_r12c05_basefeed` | -15.98 | -4.55 | -1.61 | -1.96 | -14.57 | 通带可守住，但 5G 比 R8/R9 略浅。 |
| `r14_05_r8b_open_stub_r11c06_r12c06_basefeed` | -16.07 | -4.56 | -1.57 | -2.02 | -14.44 | 浮置内侧 stub 仍偏弱。 |
| `r14_13_r8b_slot_rm_r10c05_stub_r11c05_r12c05_basefeed` | -15.65 | -4.11 | -1.71 | -1.97 | -14.60 | slit 能恢复 6G，但牺牲 5G notch。 |
| `r14_14_r8b_slot_rm_r10c05_stub_r11c05_r12c05_recover_olp03` | -15.66 | -4.10 | -1.68 | -2.03 | -14.62 | overlap 补偿没有带来新传输零点。 |
| `r14_21_r9h_open_stub_r11c05_r12c05_basefeed` | -16.32 | -4.98 | -1.75 | -1.67 | -14.65 | 最接近 R8/R9 的 5G，但 6G 和 9G 代价明显。 |
| `r14_24_r9h_open_stub_r11c06_r12c06_recover_olp03` | -16.17 | -4.44 | -1.70 | -2.59 | -15.52 | 高边不如 R9，未形成更有价值模型。 |

R14 结论：浮置开路 stub/slit 不会像 R13 短路 pad 那样把 6G 拉到 -8 dB，但 notch 也偏弱，当前没有超过 `r8_11`/`r9_04`。它的主要价值是补充“非短路浮置结构偏弱但通带可守住”的训练样本，帮助 surrogate 区分三类机制：

1. R12：弱金属-only，5G 不够深。
2. R13：远端短路 pad，5G 深但 6G 崩。
3. R14：浮置开路 stub/slit，6G 可守但 5G 没明显突破。

并入 R14 后，数据集为 133 个样本。新 checkpoint 仍为三通道输出，loss 权重保持 `S11:S21:S22 = 0.1:1.0:0.1`。R14 重新排序后，模型把已验证的 r11c05/r12c05 和 slit+stub 分支整体降权，高边阻带预测也更保守，说明反馈已经进入代理模型。

## 22. R15 d0.22 feed/path compensation 结果

R15 回到 R7/R8 中最有价值的 d0.22 主过孔家族，验证“更强 5G notch 基底 + 保守 feed/path 补偿”是否优于 R8/R9：

- 基底：`r7_16_d0p22_add_r09c04`、`r8_20_d0p22_add_r09c04_r10c04`、`r8_18_d0p22_add_r09c04_r09c05`。
- 固定：row8 c04/c11 主接地过孔对，直径 0.22 mm；不增加第二接地过孔。
- 操作：保留基底、增加 `r09c05/r10c05` 内侧 lower shoulder、组合 `feed_w=0.36 mm` 与 `overlap=0.50 mm`。
- 排序/训练原则：S21 仍是候选排序主反馈，S11/S22 继续以 0.1 权重进入训练。

R15 生成 8 个去重候选，完成 6 个 ADS/RFPro 真值样本，SVG 位于：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r15_d0p22_feed_path_1to10/svg/
```

关键结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值判断 |
|---|---:|---:|---:|---:|---:|---|
| `r15_01_r7d22a_keep_basefeed` | -16.92 | -4.78 | -2.01 | -1.60 | -15.95 | 等同 R7 best，确认 d0.22 单 lower shoulder 仍是稳定平衡基底。 |
| `r15_02_r7d22a_keep_fw0p36_ol0p50` | -17.07 | -4.79 | -2.14 | -1.79 | -16.48 | feed compensation 加深 5G/9G，但 7-8G 略差。 |
| `r15_03_r7d22a_add_r09c05_r10c05_basefeed` | -16.77 | -4.77 | -1.93 | -1.72 | -16.10 | lower shoulder 加强没有超过 keep 结构，更多是边界样本。 |
| `r15_05_r8d22v_keep_basefeed` | -16.84 | -4.70 | -1.94 | -1.59 | -15.71 | 等同 R8 best，通带最稳但 9G 不如 feed compensation。 |
| `r15_06_r8d22v_keep_fw0p36_ol0p50` | -16.98 | -4.67 | -2.11 | -1.85 | -16.48 | R15 内最有价值：5G/9G 改善，同时 6G 仍守住。 |
| `r15_07_r8d22v_add_r09c05_r10c05_basefeed` | -16.58 | -4.57 | -1.83 | -1.94 | -16.45 | 通带边缘更稳但 5G 变浅，可作为“保通带但 notch 不够”的样本。 |

R15 结论：R15 没有找到新的强传输零点，但确认当前最好的工程折中仍在 d0.22 主过孔 + lower shoulder 家族。`r15_06` 值得保留为新平衡候选，因为它在不牺牲 6G 的情况下把 5G 和 9G 都略微加深；但整体仍卡在 5G 约 -17 dB，距离 -20 dB 需要新的弱耦合自由度，而不是继续重复同一 lower shoulder 像素。

并入 R15 后，数据集为 139 个样本。最新 checkpoint 配置：

```text
x_mask=(139, 2, 16, 16)
y_s_db=(139, 3, 19)
num_sparams=3
mask_channels=2
geom_features=5
S11:S21:S22 = 0.1:1.0:0.1
```

最新训练记录：

```text
epoch=0300 train_loss=6.57374 curve=5.1598 aux=4.6971 feat=4.74524 val_loss=4.7266
```

下一轮待办：

- [ ] 扩展 R16 算子，避免重复 R15 中已去重为等效结构的 lower-shoulder 操作。
- [ ] 优先尝试连续参数或亚像素自由度：开路 stub 长度、间隙、电容加载 pad 尺寸，而不是只增删 16x16 主网格像素。
- [ ] 保留 `r15_06`、`r15_02` 作为 d0.22 feed compensation 正样本，保留 `r15_07` 作为“通带好但 5G 浅”的边界样本。
- [ ] 每轮继续生成 `filter_features.csv` 与 SVG，并重训 S11/S21/S22 三通道代理模型。

## 23. R16 d0.22 连续几何调参结果

R16 不再改变 16x16 主 mask 拓扑，而是在 R15 最有价值的 d0.22 家族上扫描连续几何变量：

- 基底：`r15_05_r8d22v_keep_basefeed` 和 `r15_01_r7d22a_keep_basefeed`。
- 变量：主 row8 过孔直径 `0.210/0.215/0.220/0.225/0.230 mm`，feed width `0.34/0.36/0.38 mm`，overlap `0.47/0.50/0.53 mm`。
- 目的：验证 surrogate 已有的 `x_geom` 和 via-diameter 通道是否能指导连续参数，而不仅是像素增删。

R16 生成 16 个候选，完成 6 个 ADS/RFPro 真值样本，SVG 位于：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r16_d0p22_continuous_tune_1to10/svg/
```

关键结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值判断 |
|---|---:|---:|---:|---:|---:|---|
| `r16_02_r8d22v_d0p215_fw0p34_ol0p50` | -17.13 | -4.90 | -2.20 | -1.70 | -16.49 | 弱 via/窄 feed 并没有按预测变浅，说明连续局部需要更多真值校准。 |
| `r16_04_r8d22v_d0p225_fw0p36_ol0p50` | -17.14 | -4.87 | -2.09 | -1.88 | -16.60 | 0.225 mm 主 via 是可用增强点，6G 仍守住。 |
| `r16_05_r8d22v_d0p225_fw0p36_ol0p53` | -17.37 | -5.14 | -2.10 | -1.84 | -16.67 | 当前新 best：5G/9G 更深，6G 仍高于 -5.5 dB guard。 |
| `r16_08_r8d22v_d0p230_fw0p38_ol0p50` | -17.07 | -4.90 | -1.86 | -1.80 | -16.01 | 加粗 via 后用宽 feed 恢复通带，但 5G 没继续变深。 |
| `r16_13_r7d22a_d0p225_fw0p36_ol0p53` | -17.18 | -4.94 | -2.00 | -1.88 | -16.52 | R7 mask 也受益于 0.225/0.53，但不如 r8d22v。 |
| `r16_15_r7d22a_d0p230_fw0p36_ol0p50` | -17.33 | -5.16 | -2.08 | -1.68 | -16.31 | 5G 接近 r16_05，但 6G 代价略大，高边也弱一些。 |

R16 结论：连续几何调参比 R15 的单纯 lower-shoulder 像素微调更有价值，`r16_05_r8d22v_d0p225_fw0p36_ol0p53` 成为当前最佳平衡样本。它仍没有达到 -20 dB 5G 阻带，但把 d0.22 家族从约 -17.0 dB 推到 -17.37 dB，且 6G 仍保在 -5.14 dB。下一轮应围绕 `r16_05` 做更细的连续局部扫描：`via_diameter=0.222-0.228 mm`、`overlap=0.51-0.55 mm`、`feed_w=0.35-0.37 mm`，并考虑把 `pixel_overfill_ratio` 或局部 gap 作为显式几何特征加入神经网络。

并入 R16 后，数据集为 145 个样本。最新 checkpoint：

```text
x_mask=(145, 2, 16, 16)
y_s_db=(145, 3, 19)
S11:S21:S22 = 0.1:1.0:0.1
best_val_loss=5.214541912078857
```

注意：R16 重训后 surrogate 对 R16 真实 5G 深度仍偏保守，说明连续参数区域的数据密度不足；但它已经学到更大 via 会压低 passband margin。R17 应优先补足 `r16_05` 周边连续样本，而不是切换到全新拓扑。

## 24. R17 r16_05 局部连续调参结果

R17 固定 `r16_05_r8d22v_d0p225_fw0p36_ol0p53` 的 16x16 metal/via 拓扑，只扫描神经网络已经显式看到的连续几何量：

- `via_diameter=0.222/0.225/0.228 mm`
- `feed_w=0.35/0.36/0.37 mm`
- `coupling_overlap=0.51/0.53/0.55 mm`

R17 生成 18 个候选，完成 6 个 ADS/RFPro 代表样本，SVG 位于：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r17_local_continuous_tune_1to10/svg/
```

关键结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值判断 |
|---|---:|---:|---:|---:|---:|---|
| `r17_01_d0p222_fw0p35_ol0p51` | -17.01 | -4.60 | -2.10 | -2.13 | -16.89 | 最稳守 6G，适合作为低 via/低耦合安全边界。 |
| `r17_04_d0p222_fw0p36_ol0p55` | -17.16 | -4.86 | -2.09 | -1.94 | -16.70 | 0.222 mm via 加 overlap 可略加深 5G，同时仍有 6G margin。 |
| `r17_10_d0p225_fw0p36_ol0p53` | -17.37 | -5.14 | -2.10 | -1.84 | -16.67 | R16 best 复现，结果一致，可作为中心校准点。 |
| `r17_14_d0p225_fw0p37_ol0p55` | -17.32 | -5.25 | -1.92 | -1.57 | -15.84 | 宽 feed/high overlap 改善 7-8G，但 9G 变浅，6G 代价更大。 |
| `r17_15_d0p228_fw0p35_ol0p53` | -17.31 | -5.07 | -2.08 | -1.83 | -16.49 | 高 via + 窄 feed 没超过 R16 best，可作为高 via 边界。 |
| `r17_18_d0p228_fw0p36_ol0p55` | -17.55 | -5.45 | -2.13 | -1.56 | -16.27 | 当前 5G 最深，但 6G 已接近/低于 guard，不适合作为平衡 best。 |

R17 结论：

- via 加大确实加深 5G，但会快速吃掉 6G margin。
- overlap 增大可以恢复 8G 附近传输，但对 6G 的保护有限。
- 当前工程 best 仍是 `r16_05/r17_10`；若允许 6G 边缘更差，`r17_18` 是最深 5G 样本。
- R17 的主要价值是给神经网络补足连续几何局部斜率，而不是产生明显新拓扑。

并入 R17 后，数据集和模型状态：

```text
samples: 151
x_mask: (151, 2, 16, 16)
x_geom: (151, 7)
y_s_db: (151, 3, 19)
freq: 1.0-10.0 GHz, 0.5 GHz step
loss weights: S11:S21:S22 = 0.1:1.0:0.1
checkpoint: projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_s21_surrogate.pt
epoch=0800 train_loss=2.39306 curve=1.92823 aux=1.56769 feat=1.51294 val_loss=1.65478
best_val_loss=1.5893127918243408
geom_features=pixel_mm, cell_pitch_mm, pixel_overfill_ratio, gap_mm, feed_w_mm, coupling_overlap_mm, via_diameter_mm
```

`--val-fraction 0` 下 `val_loss` 仍是全数据监控。重训后的 R17 排序把 `0.222 mm` via 局部排在最前，说明模型已学习到“守住 6G 比进一步加深 5G 更重要”的 guarded score 方向。

下一轮待办：

- [ ] 若继续围绕当前拓扑，优先补跑未仿真的 `r17_02/r17_03/r17_05`，它们是 0.222 mm via 的高分安全区。
- [ ] 新算子应引入神经网络尚未充分覆盖的自由度：`pixel_overfill_ratio`、局部 gap、stub/pad 的亚像素长度或宽度。
- [ ] 若引入 overfill/gap，先扩展 `x_geom`，否则 surrogate 只能从 mask/via/feed/overlap/pitch 间接推断，无法稳定学习这些变量。
- [ ] 继续保持三通道输出训练；S21 是主反馈，S11/S22 以 0.1 权重保留为低惩罚回波上下文。

## 25. R18 pixel overfill 调参结果

R18 使用已经扩展到 7 维的 `x_geom`，固定 `r16_05/r17_10` 拓扑，只扫描 `pixel_overfill_ratio`。由于当前 connected grid 使用 `cell_pitch_mm>0`，`gap_mm` 不改变真实版图，因此 R18 不扫 gap，避免无效参数样本。

R18 生成 15 个候选，完成 6 个 ADS/RFPro 代表样本，SVG 位于：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r18_overfill_tune_1to10/svg/
```

关键结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值判断 |
|---|---:|---:|---:|---:|---:|---|
| `r18_01_of0p04_d0p222_fw0p35_ol0p51` | -17.56 | -5.61 | -1.87 | -1.63 | -16.35 | 5G 深，但 6G 已跌破 guard；低 overfill 不是安全方向。 |
| `r18_02_of0p04_d0p225_fw0p36_ol0p53` | -17.77 | -5.98 | -1.76 | -1.43 | -15.80 | R18 5G 最深，但 6G 明显失守。 |
| `r18_04_of0p08_d0p222_fw0p35_ol0p51` | -17.54 | -5.63 | -2.04 | -1.22 | -15.31 | 仍过度牺牲 6G/9G。 |
| `r18_10_of0p12_d0p222_fw0p35_ol0p51` | -17.29 | -5.20 | -2.19 | -1.31 | -15.43 | 6G 回到可接受附近，但高边不如 R16/R17 best。 |
| `r18_13_of0p16_d0p222_fw0p35_ol0p51` | -16.93 | -4.64 | -2.28 | -1.47 | -15.83 | 6G 最稳，但 5G 退回 R15 水平。 |
| `r18_15_of0p16_d0p228_fw0p36_ol0p55` | -17.58 | -5.69 | -2.19 | -1.10 | -15.19 | 强 via + 大 overfill 仍无法守住 6G，高边也弱。 |

R18 结论：

- overfill 是有效算子，但不是当前拓扑的突破口。
- 降低 overfill 会加深 5G，同时把 6G 快速拉低；这与 R18 前 surrogate 的初始排序相反，说明新增几何维度必须靠真值校准。
- 增大 overfill 可以恢复 6G，但会牺牲 5G notch。当前最平衡点仍是 `r16_05/r17_10`，不是 R18。
- R18 的主要价值是给 7 维 surrogate 提供第一批 overfill 真值斜率。

并入 R18 后，数据集和模型状态：

```text
samples: 157
x_mask: (157, 2, 16, 16)
x_geom: (157, 7)
y_s_db: (157, 3, 19)
loss weights: S11:S21:S22 = 0.1:1.0:0.1
epoch=0800 train_loss=2.76021 curve=2.1487 aux=2.10586 feat=1.90336 val_loss=1.41813
best_val_loss=1.3637856245040894
```

下一轮建议：不要继续单独扫 overfill。更好的 R19 算子是“局部亚像素 stub/pad”或“局部 cell pitch/overfill 联合微调”，并且只在真实会改变版图的参数上采样。

## 26. R19 local pixel guard 结果

R19 先没有引入隐藏的亚像素版图参数，而是选择当前神经网络能直接编码的局部金属像素算子：

- 输入可见：16x16 metal mask、via 直径通道、7D 全局几何。
- 操作：围绕 `r16_05/r17_10` lower-shoulder 区域做镜像 add/remove/shift。
- 几何锚点：`center`、`safe`、`recover` 三组 via/feed/overlap/overfill。
- 排序原则：S21 主反馈，S11/S22 保留为 `0.1` 权重训练上下文。

R19 生成 33 个候选，完成 11 个 ADS/RFPro 真值样本，并刷新 SVG：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r19_local_pixel_guard_1to10/svg/
```

关键结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值 |
|---|---:|---:|---:|---:|---:|---|
| `r19_20_safe_slot_rm_r10c05` | -17.14 | -4.78 | -2.18 | -2.07 | -17.05 | R19 最有价值；高边平均约 -19.43 dB，且 6G 安全。 |
| `r19_09_center_slot_rm_r10c05` | -17.38 | -5.31 | -1.99 | -1.72 | -16.52 | 5G 最深之一，但 6G 接近 guard。 |
| `r19_01_center_add_r10c05` | -17.37 | -5.14 | -2.10 | -1.84 | -16.67 | 基本复现 `r16_05/r17_10`，说明该像素自由度已饱和。 |
| `r19_12_safe_add_r10c05` | -17.01 | -4.60 | -2.10 | -2.13 | -16.89 | safe geometry 校准点，高边较好。 |
| `r19_28_recover_add_r12c05` | -16.90 | -5.56 | -1.69 | -1.62 | -14.52 | 远端 r12c05 伤 6G/9G，不宜继续主线扩展。 |

R19 后的结论：

- `slot_rm_r10c05` 是比远端 pad/stub 更好的网络可见算子，主要价值在高边阻带和 6G guard。
- `add_r10c05` 没有形成新自由度，中心几何下接近已有 best。
- `add_r12c05` 证明远端弱加载不可靠，容易牺牲 6G/9G。
- 若下一步要做真正亚像素 stub/pad 长宽，必须先扩展输入 schema，例如增加局部连续 loading map 通道或局部 rectangle 参数表；否则代理模型无法从 ADS 真值中学习这个算子。

并入 R19 后，数据集和模型状态：

```text
samples: 168
x_mask: (168, 2, 16, 16)
x_geom: (168, 7)
y_s_db: (168, 3, 19)
loss weights: S11:S21:S22 = 0.1:1.0:0.1
epoch=0800 train_loss=2.82346 curve=2.23782 aux=1.95587 feat=1.94462 val_loss=1.64162
checkpoint: projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_s21_surrogate.pt
```

`--val-fraction 0` 下 `val_loss` 是全量监控，不是独立验证。R19 重训后，surrogate ranking 前两名变为已实测的 `safe/recover slot_rm_r10c05`，说明模型已经把该类开槽样本的真实反馈吸收进去。

## 27. R20 两级单元与二级通道状态

R20 将二维码像素结构升级为两级单元：

- 一级：原 `16x16` QR-like metal/via 主网格，继续决定主耦合路径和 via 拓扑。
- 二级：只在热点区域引入局部连续子单元，包括 open stub、attached pad、in-pixel slot。

神经网络输入从 2 通道扩展为 6 通道：

```text
channel 0: metal
channel 1: ground_via_diameter_norm_0.18mm
channel 2: sub_stub_len_norm_0.35mm
channel 3: sub_stub_w_norm_0.35mm
channel 4: sub_pad_side_norm_0.35mm
channel 5: sub_slot_gap_norm_0.1016mm
```

R20 生成 18 个候选，全部通过 layout contract。已完成 6 个 ADS/RFPro 首批真值样本，SVG 输出：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r20_subcell_loading_1to10/svg/
```

关键结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 价值 |
|---|---:|---:|---:|---:|---:|---|
| `r20_01_r19slot_stub_r10c05_l0p105_w0p105` | -17.12 | -4.70 | -2.22 | -2.06 | -17.00 | 高边平均约 -19.28 dB，6G 安全，是二级 stub 的首个正样本。 |
| `r20_02_r19slot_stub_r10c05_l0p14_w0p105` | -17.21 | -4.89 | -2.19 | -1.86 | -16.66 | stub 加长会加深 5G，但开始吃 6G/9G margin。 |
| `r20_07_r19slot_slot_r10c04_g0p105` | -17.34 | -5.22 | -2.11 | -1.60 | -16.25 | slot 能保持 5G，但 6G 接近 guard。 |
| `r20_10_r16best_stub_r10c05_l0p105_w0p105` | -17.34 | -5.19 | -2.08 | -1.64 | -16.28 | R16 基底加短 stub 后 5G 深，但 6G margin 下降。 |
| `r20_06_r19slot_pad_r12c05_s0p105` | -17.28 | -5.04 | -2.15 | -1.76 | -16.52 | far pad 是弱可调样本，没有明显突破。 |
| `r20_14_r16best_pad_r11c05_s0p105` | -17.23 | -4.94 | -2.07 | -1.93 | -16.66 | attached pad 保持 6G，可作为 pad 通道校准样本。 |

R20 结论：二级子单元通道是可行的，ADS/RFPro 导入和 layout contract 均通过；但首批样本还没有把 5G 从约 -17 dB 推向 -20 dB。当前价值主要是给神经网络提供第一批“连续局部加载”的真实斜率：短 stub 和小 pad 是弱可调正样本，slot 会更快消耗 6G guard。

并入 R20 后，当前模型状态：

```text
samples: 174
x_mask: (174, 6, 16, 16)
x_geom: (174, 7)
y_s_db: (174, 3, 19)
loss weights: S11:S21:S22 = 0.1:1.0:0.1
epoch=0800 train_loss=3.6085 curve=2.87006 aux=2.35302 feat=2.67836 val_loss=1.99519
```

`--val-fraction 0` 下 `val_loss` 仍是全量监控。R20 重训后 ranking 前列回到已验证的 `r16best_pad_r11c05` 与 `r19slot_stub_r10c05`，说明模型已经开始吸收二级通道反馈。下一步应继续补少量 R20 未仿真候选，优先覆盖 `pad_r12c05`、`slot_r10c04` 和 `stub_r11c05` 的位置/长度斜率。

## 28. R20 全量与 R21 子单元组合状态

R20 已补完 18/18 个 ADS/RFPro 样本，并刷新全量 SVG：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r20_subcell_loading_1to10/svg/
```

R20 全量结论：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 高边均值 | 判断 |
|---|---:|---:|---:|---:|---:|---:|---|
| `r20_11_r16best_stub_r10c05_l0p14_w0p105` | -17.46 | -5.34 | -2.06 | -1.62 | -16.28 | -18.67 | R20 最深 5G，但 6G margin 明显下降。 |
| `r20_17_r16best_slot_r10c05_g0p105` | -17.44 | -5.29 | -2.19 | -1.51 | -16.11 | -18.39 | 5G 深，6G 接近 guard，高边一般。 |
| `r20_18_r16best_slot_r11c05_g0p105` | -17.37 | -5.14 | -2.10 | -1.84 | -16.67 | -19.04 | R16 slot 中较平衡。 |
| `r20_08/r20_09_r19slot_slot_*` | -17.14 | -4.78 | -2.18 | -2.07 | -17.05 | -19.43 | 高边最好且 6G 安全，但 5G 未加深。 |
| `r20_01_r19slot_stub_r10c05_l0p105_w0p105` | -17.12 | -4.70 | -2.22 | -2.06 | -17.00 | -19.28 | 6G 安全、高边好，是二级 stub 的安全正样本。 |

R20 并入后完整训练状态：

```text
samples: 186
x_mask: (186, 6, 16, 16)
x_geom: (186, 7)
y_s_db: (186, 3, 19)
loss weights: S11:S21:S22 = 0.1:1.0:0.1
epoch=0800 train_loss=3.15673 curve=2.51223 aux=2.14447 feat=2.1561 val_loss=2.07528
```

R21 使用同一 6 通道 schema，不增加全局二维码密度，只组合或轻微调整已验证的二级 stub/pad/slot。已新增并注册：

```text
tools/make_pixel_qr_r21_subcell_combo_candidates.py
config/pipelines/pixel_qr_bpf_fr4_210um_home_r21_subcell_combo_1to10.json
projects/pixel_qr_bpf_fr4_210um/plans/pixel_qr_bpf_fr4_210um_r21_subcell_combo_1to10.csv
projects/pixel_qr_bpf_fr4_210um/layouts/pixel_qr_bpf_fr4_210um_r21_subcell_combo_1to10/
```

R21 生成 18 个候选，全部通过 layout gate；最低金属间距为 `0.102 mm`，仍高于 4 mil / `0.1016 mm`。首批 ADS/RFPro 已完成 8 个样本，SVG 输出：

```text
projects/pixel_qr_bpf_fr4_210um/results/pixel_qr_bpf_fr4_210um_r21_subcell_combo_1to10/svg/
```

R21 首批结果：

| 候选 | S21@5G | S21@6G | S21@7G | S21@8G | S21@9G | 高边均值 | 判断 |
|---|---:|---:|---:|---:|---:|---:|---|
| `r21_15_r16slot_g0p12` | -17.37 | -5.14 | -2.10 | -1.84 | -16.67 | -19.04 | 基本等价/复现 R20_18，说明远端 slot 放大未形成突破。 |
| `r21_04_r19high_slot_pad_r12` | -17.28 | -5.04 | -2.15 | -1.76 | -16.52 | -18.85 | pad 组合略加深 5G，但吃掉 6G/高边 margin。 |
| `r21_10_r19stub_pad_r11` | -17.26 | -5.12 | -2.08 | -1.69 | -16.38 | -18.78 | stub+pad 没有明显优于单算子。 |
| `r21_07_r19stub_l0p122` | -17.26 | -5.01 | -2.18 | -1.71 | -16.41 | -18.69 | 中间 stub 长度加深 5G 有限，6G 代价上升。 |
| `r21_01_r19high_slot_g0p12` | -17.14 | -4.78 | -2.18 | -2.07 | -17.05 | -19.43 | 与 R20 高边 best 基本一致，说明该方向已饱和。 |
| `r21_09_r19stub_slot_r11` | -17.12 | -4.70 | -2.22 | -2.06 | -17.00 | -19.28 | 与 R20_01 基本一致，组合没有产生新零点。 |

R21 首批没有把 5G notch 推向 -20 dB，也没有明显改善 R20 高边 best。当前二维码分支的价值已经从“寻找最终滤波器”转为“复杂拓扑/局部加载样本库”。若继续做二维码，应优先引入更物理的谐振机制，而不是继续在同一 lower-shoulder 热点做弱 stub/pad/slot 组合。

## 29. 主线迁移建议：交指 NN 优先

基于 R20/R21 结果，当前自动优化资源建议转向 FR4 7 阶交指滤波器神经网络代理。理由：

- 交指分支已有 legacy 最佳基点 `i7_fr4_r1_l555_taper`，5G 阻带和 6/8G 通带边缘已达阶段目标。
- 交指参数是低维连续变量，神经网络比二维码像素拓扑更容易学习有效梯度。
- 当前主要瓶颈是 `S11/S22` 约 `-6 dB` 的匹配优化，适合围绕 `tap/taper/feed/gap` 做信赖域主动学习。

交指 NN 计划已写入：

```text
docs/opt/FR4交指滤波器搜索算法改进方案.md
```

二维码分支后续仅建议保留两类动作：

- [ ] 将 R21 剩余 10 个候选暂缓，不作为主线消耗 ADS 时间，除非需要补充二级通道负样本。
- [ ] 若恢复二维码主线，先定义新的强谐振机制，例如更明确的短路 stub、可控接地支路或多级局部谐振单元，再同步扩展神经网络输入 schema。
