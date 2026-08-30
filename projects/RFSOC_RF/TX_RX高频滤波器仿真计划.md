# TX/RX 高频滤波器仿真计划

Status: Draft
Project: RFSOC_RF
Source: `projects/RFSOC_RF/RFSOC_RF频率规划与滤波器详细设计.html`
ADS profile: `home_2027` / `home_simads_em_parallel_2027`

## 1. 仿真目标

本计划覆盖 RFSOC_RF 项目的 TX 输出高频滤波器和 RX RF 预选高频滤波器。RX IF 与 DPD IF 当前优先采用成品 IF BPF，不作为本轮定制高频滤波器 EM 设计主线。

总体目标：

- 建立 TX-F1 首个 ADS 2027 RFPro/FEM 可复现仿真闭环。
- 基于 TX-F1 拓扑复制并调谐 TX-F2/F3/F4。
- 建立 RX-L/RX-H 两段预选滤波器基线。
- 完成单滤波器 EM、开关级联、公差、温漂和交付物闭环。

## 2. TX 输出滤波器指标

TX 滤波组件位于 Mixer 后 LNA 与 PA 之间，采用前后各一只 SP4T，中间四路窄带带通滤波器。

| 支路 | 通带 GHz | 关联 LO 阻带 GHz | Image 阻带 GHz | 首版目标 |
|---|---:|---:|---:|---|
| TX-F1 | 17.700-19.325 | 14.400-15.025 | 10.1-13.6 | IL <= 2.5 dB, RL >= 15 dB, Stop >= 40 dB |
| TX-F2 | 18.325-19.950 | 15.025-15.650 | 10.1-13.6 | IL <= 2.5 dB, RL >= 15 dB, Stop >= 40 dB |
| TX-F3 | 18.950-20.575 | 15.650-16.275 | 10.1-13.6 | IL <= 2.5 dB, RL >= 15 dB, Stop >= 40 dB |
| TX-F4 | 19.575-21.200 | 16.275-16.900 | 10.1-13.6 | IL <= 2.5 dB, RL >= 15 dB, Stop >= 40 dB |

补充要求：

- 单只滤波器目标插损：typ <= 2.0 dB，max <= 2.5 dB。
- 通带波动：<= 0.5 dB p-p。
- S11/S22：>= 15 dB。
- 群时延波动：<= 0.25 ns p-p。
- 功率：CW >= +27 dBm，Peak >= +30 dBm。
- 首版拓扑：0.2 dB Chebyshev，N=5 起步；若阻带不足，优先引入传输零点。

## 3. RX RF 预选滤波器指标

RX 预选组件位于天线/保护网络与 MDB-44H+ RF 输入之间，采用前后 SP2T，中间两路 RF 预选带通滤波器。

| 支路 | 通带 GHz | 关联 LO 泄漏 GHz | 镜像 GHz | 首版目标 |
|---|---:|---:|---:|---|
| RX-L | 27.0-29.5 | 23.8-25.3 | 19.6-23.6 | IL <= 2.5 dB, RL >= 15 dB, Image >= 40 dB, LO >= 25-30 dB |
| RX-H | 28.5-31.0 | 25.3-26.8 | 19.6-23.6 | IL <= 2.5 dB, RL >= 15 dB, Image >= 40 dB, LO >= 25-30 dB |

补充要求：

- 单只滤波器目标插损：typ <= 2.0 dB，max <= 2.5 dB。
- 通带波动：<= 0.5 dB p-p。
- S11/S22：>= 15 dB。
- 群时延波动：<= 0.25 ns p-p。
- 功率：CW >= +20 dBm，P1dB >= +23 dBm。
- RX 优先低插损和系统 NF，不应一开始为了 LO 40 dB 盲目堆阶数。

## 4. 仿真阶段

### 4.1 环境与基板冻结

先确认 ADS 2027 profile 可用：

```powershell
python tools/check_ads_profile.py --profile home_2027 --require-mcp --strict
python tools/check_ads_profile.py --profile home_simads_em_parallel_2027 --require-template --require-mcp --strict
```

冻结输入：

- ADS 版本和 profile。
- workspace、library、template cell。
- 基板介电常数、厚度、铜厚、金属粗糙度。
- 最小线宽、最小间距、最小过孔、板厂能力。
- 端口定义和参考地层。

### 4.2 TX-F1 首个基线

TX-F1 作为第一条打通链路：

```text
通带：17.700-19.325 GHz
LO 阻带：14.400-15.025 GHz
Image 阻带：10.1-13.6 GHz
扫频：8-24 GHz
拓扑：5 阶交指起步，允许准椭圆/传输零点优化
```

通过门限：

- 通带 IL <= 2.5 dB。
- 通带 S11/S22 >= 15 dB。
- LO 与 Image 阻带 >= 40 dB。
- 群时延波动 <= 0.25 ns p-p。

若 TX-F1 未达到 40 dB 阻带，优先调整耦合、端部加载、交叉耦合或传输零点位置；不要直接进入 TX-F2/F3/F4。

### 4.3 TX-F2/F3/F4 频移复用

在 TX-F1 拓扑稳定后，复制为 TX-F2/F3/F4 并重综合尺寸。

重点检查相邻通带重叠区：

| 相邻状态 | 重叠区 GHz |
|---|---:|
| F1/F2 | 18.325-19.325 |
| F2/F3 | 18.950-19.950 |
| F3/F4 | 19.575-20.575 |

每一路都必须独立输出完整 S 参数、群时延和阻带评分。相邻重叠区需要比较幅度、相位和群时延一致性。

### 4.4 TX 开关级联仿真

TX 级联链路：

```text
SP4T 输入开关 -> TX-Fx -> SP4T 输出开关 -> PA 输入端
```

候选开关：`M4SWA4-34DR+`。

必须注意：

- 当前记录中本地 S5P 型号曾标注为 27DR，不能代替 34DR 验收。
- 开关隔离不能和滤波器导通支路阻带直接相加作为验收结论。
- 两只 SP4T 典型插损约 3.6 dB，必须回填 PA 驱动功率预算。

级联输出：

- 四个 TX 状态总插损。
- 四个 TX 状态 S11/S22。
- 非选支路隔离。
- LO/Image 抑制。
- PA 输入端功率余量。

### 4.5 RX-L/RX-H 单滤波器设计

RX 先以 N=5 交指作为低损耗基线。

扫频：

```text
18-33 GHz
```

RX-L 重点窗口：

- 镜像：19.6-23.6 GHz。
- LO：23.8-25.3 GHz。
- 通带：27.0-29.5 GHz。

RX-H 重点窗口：

- 镜像：19.6-23.6 GHz。
- LO：25.3-26.8 GHz。
- 通带：28.5-31.0 GHz。

优化策略：

- 镜像维持 >= 40 dB 目标。
- LO 泄漏先按 25-30 dB 目标推进。
- 若 LO 泄漏预算后续要求提高，再评估传输零点或提高阶数。
- RX 设计优先保护系统 NF，不把阻带目标孤立地放在插损前面。

### 4.6 RX 开关级联与 NF 预算

RX 级联链路：

```text
ADRF5300 输入 SP2T -> RX-L/H -> ADRF5300 输出 SP2T -> MDB-44H+ RF 输入
```

候选开关：`ADRF5300BCCZN-R7`。

级联验证：

- 两个状态总插损。
- 两个状态 S11/S22。
- 镜像抑制。
- LO 反向泄漏。
- 级联噪声系数预算。
- 反射式非选端导致的驻波风险。

## 5. 公差与温漂仿真

每个冻结候选至少做以下参数扫描：

| 参数 | 建议扫描 |
|---|---|
| 线宽 | nominal, min, max |
| 间距 | nominal, min, max |
| 介电常数 | nominal, low, high |
| 介质厚度 | nominal, low, high |
| 铜厚 | nominal, low, high |
| 金属粗糙度 | nominal, pessimistic |
| 端口/焊盘寄生 | nominal, pessimistic |

输出 worst-case：

- 通带最差 IL。
- 通带最差 S11/S22。
- 阻带最差衰减。
- 中心频率偏移。
- 带宽偏移。
- 群时延波动。

## 6. 成品候选对照

成品器件只作为对照或备选，不替代定制 EM 闭环。

| 链路 | 候选 | 初筛结论 | 必须补充 |
|---|---|---|---|
| TX-F1/F2 | BFCG-1902+ | 标称覆盖 17.0-20.4 GHz，可与定制交指比较 | 完整 S2P、LO/Image、功率、温漂、重叠区 |
| TX-F3/F4 | 定制交指 / 继续筛选 | BFCG-1902+ 不能完整覆盖 | 传输零点、40 dB 阻带、EM 闭环 |
| RX-L | ABF-28G+ | 可覆盖目标通带 | 23.8-25.3 GHz LO、19.6-23.6 GHz 镜像 |
| RX-H | BFHKI-3142+ | 仅作宽带备选，IL/RL 风险较大 | 31 GHz 边缘、NF、开关级联损耗 |

所有成品候选必须导入 S2P，按系统通带、LO/镜像阻带、群时延、功率、温度和批次公差进行级联仿真。

## 7. 交付物

每个单滤波器候选必须输出：

- ADS workspace cell。
- RFPro/FEM setup。
- EM S2P。
- S11/S21/S22 曲线。
- 群时延曲线。
- 评分 CSV。
- 版图 SVG 或截图。
- 参数 JSON。
- 一页设计结论。

最终组件必须输出：

- `TX_SP4T_4STATE_cascade` 四状态级联结果。
- `RX_SP2T_2STATE_cascade` 两状态级联结果。
- TX/RX 指标汇总表。
- 公差 worst-case 表。
- 是否进入打样的冻结结论。

## 8. 第一轮执行建议

第一轮只做 TX-F1 R0：

```text
candidate_id: tx_f1_r0
passband: 17.700-19.325 GHz
lo_stopband: 14.400-15.025 GHz
image_stopband: 10.1-13.6 GHz
sweep: 8-24 GHz
topology: 5-order interdigital BPF, 0.2 dB Chebyshev start
target: IL <= 2.5 dB, RL >= 15 dB, LO/Image >= 40 dB
```

TX-F1 通过后再进入：

```text
tx_f2_r0
tx_f3_r0
tx_f4_r0
rx_l_r0
rx_h_r0
```

## 9. 冻结门限

进入打样前必须满足：

- 单滤波器指标达标。
- 开关级联后系统预算可接受。
- 公差 worst-case 未跨出关键门限。
- 端口、地参考、过孔和边界条件已复核。
- 所有 S2P、CSV、版图和报告文件可追溯到同一 run id。
