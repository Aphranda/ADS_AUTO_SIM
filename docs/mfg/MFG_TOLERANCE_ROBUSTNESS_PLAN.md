# Manufacturing Tolerance Robustness Plan

Status: Active
Domain: MFG
Canonical: `docs/mfg/MFG_TOLERANCE_ROBUSTNESS_PLAN.md`
Related: `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`, `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`, `docs/result/RESULT_BASELINE_FREEZE_POLICY.md`, `docs/flow/FLOW_JOB_SCHEDULING_POLICY.md`, `docs/arch/ARCH_REFACTOR_TODO.md`
Last updated: 2026-08-01
Owner: ADS Automation

本文档定义滤波器候选进入 release candidate 前的制造容差和材料漂移鲁棒性检查规则。单点 FEM 最优不等于可制造最优；FR4、铜厚、蚀刻误差、孔、层叠和介电常数漂移都会影响 6-8 GHz 带通滤波器的中心频率、带宽、回损和阻带。

## 1. 目标

| 目标 | 说明 |
|---|---|
| 防止单点最优 | 候选不能只在 nominal 条件下满足目标。 |
| 识别敏感参数 | 找出对 5 GHz 阻带、6/8 GHz 通带和回损影响最大的制造变量。 |
| 建立入围 gate | release candidate 前必须通过制造和材料扰动检查。 |
| 支持低成本 FR4 | FR4 分支应使用可采购、可制造、可复测的容差假设，不用高频板材标准代替。 |
| 保留追溯 | tolerance sweep 的每个角点都要能追溯到 nominal candidate。 |

## 2. 适用阶段

| 阶段 | 是否执行 | 说明 |
|---|---|---|
| 初始拓扑探索 | 否 | 先验证带通机理和主要零极点。 |
| 小批量参数搜索 | 可选 | 对接近目标的候选做少量关键扰动。 |
| 入围候选 | 必须 | 进入报告或打样建议前执行。 |
| 材料/层叠变化 | 必须 | 新 FR4 工艺、板厚、参考层或铜厚变化后重新执行。 |
| 正式发布 | 必须 | 报告中必须说明 nominal 和 worst-case 结果。 |

## 3. 当前 FR4 分支制造基准

当前 7 阶 FR4 交指分支按低成本普通 FR4 工艺推进。报告或 plan 中应记录实际板厂能力；未冻结前可采用以下项目基准作为检查入口：

| 项 | 当前项目基准 |
|---|---|
| 材料分支 | FR4 低成本分支。 |
| 工艺参考 | 普通 JLC06161H-7628 级别可制造能力。 |
| 最小间距 | 4 mil 作为严格版图下限；优化建议保留余量。 |
| 过孔 | 圆孔圆焊盘；当前讨论过 `10/14 mil` 规则。 |
| 参考层 | 必须由 layout params 指明，例如 L1/L3 reference。 |
| 版图单位 | `mm`。 |

实际下单前应以板厂最新规则和所选叠层为准；本文档只定义自动化验证框架。

## 4. 扰动变量

| 类别 | 变量 | 建议扰动 | 主要影响 |
|---|---|---:|---|
| 介电常数 | `Er` | ±0.2 或供应商容差 | 中心频率、电长度、带宽。 |
| 损耗角 | `tanD` | nominal / high-loss | 插损、通带平坦度。 |
| 介质厚度 | `h` | ±5% 或供应商容差 | 50 Ω 线宽、耦合强度、频偏。 |
| 铜厚 | `t_cu` | nominal / high / low | 阻抗、损耗、边缘场。 |
| 线宽 | `W` | ±25 um 或板厂蚀刻容差 | 阻抗、谐振频率、回损。 |
| 间距 | `S` | ±25 um，且不低于最小间距 | 耦合强度、带宽、传输零点。 |
| 长度 | `L` | ±25 um 或 ±0.5% | 中心频率、零点位置。 |
| 过渡 | taper/overlap | ±25 um | 端口匹配、外部 Q。 |
| via | drill/pad | 工艺上下限 | 短路电感、短路端电长度。 |
| 对位 | layer registration | 供应商容差 | 多层参考、via 与支节连接。 |

若板厂给出更严格或更宽松的能力，应以实际报价和叠层文件更新扰动范围。

## 5. 扫描层级

### 5.1 DRC Gate

纯几何检查，不启动 ADS/FEM。

| 检查 | 要求 |
|---|---|
| min_width | 所有线宽大于等于工艺下限，并记录最小余量。 |
| min_gap | 所有间距大于等于工艺下限，并记录最小余量。 |
| via_rule | 孔径、焊盘、孔到线、孔到边满足规则。 |
| sliver | 不存在极窄铜皮、碎片铜或尖角。 |
| port_clearance | 端口附近无无意短接。 |

### 5.2 One-at-a-time Sensitivity

对入围候选先做单变量扰动，判断灵敏度。

```text
nominal
Er_low / Er_high
h_low / h_high
W_narrow / W_wide
S_narrow / S_wide
L_short / L_long
```

### 5.3 Corner Sweep

对关键变量做小角点组合，建议先控制在 9-17 组。

| 角点 | 含义 |
|---|---|
| fast_freq | `Er_low + h_high + L_short`，频率偏高风险。 |
| slow_freq | `Er_high + h_low + L_long`，频率偏低风险。 |
| weak_coupling | 间距变大、线宽变窄，通带变窄风险。 |
| strong_coupling | 间距变小、线宽变宽，回损和阻带变化风险。 |
| high_loss | `tanD_high + copper_loss_high`，插损风险。 |
| via_high_L | via 等效电感偏大，短路端频偏风险。 |

### 5.4 Monte Carlo

只有在入围候选很接近目标、且角点检查通过后再做。建议先 50-100 点，不作为早期搜索默认步骤。

## 6. 鲁棒判据

候选分为 nominal pass 和 robust pass。

| 状态 | 判据 |
|---|---|
| `nominal_fail` | nominal 不满足 target profile 硬约束。 |
| `nominal_pass` | nominal 满足硬约束，但未做 tolerance sweep。 |
| `robust_warn` | 大多数角点满足，但个别角点 margin 过小或轻微失败。 |
| `robust_pass` | 所有必选角点满足硬约束，且关键 margin 保留余量。 |
| `robust_fail` | 任一关键角点明显破坏阻带、通带或回损。 |

FR4 7 阶交指分支建议 robust gate：

| 指标 | nominal 要求 | robust 建议 |
|---|---:|---:|
| `S21@5GHz` | <= -25 dB | worst-case <= -24 dB 可列 warn；正式发布建议 <= -25 dB。 |
| `S21@6GHz` | >= -5 dB | worst-case >= -5 dB。 |
| `S21@8GHz` | >= -5 dB | worst-case >= -5 dB。 |
| `passband_min_s21` | >= -5 dB | worst-case >= -5 dB。 |
| `passband_ripple` | <= 4 dB | worst-case <= 4.5 dB 可列 warn；正式发布建议 <= 4 dB。 |
| `worst_s11_6_8` | <= -6 dB | worst-case <= -6 dB；若目标仅为探索可暂列 tune。 |
| `worst_s22_6_8` | <= -6 dB | worst-case <= -6 dB；若目标仅为探索可暂列 tune。 |

## 7. 参数影响方向

| 参数变化 | 常见影响 | 优化提示 |
|---|---|---|
| `Er` 增大 | 频率降低，电长度变长。 | 设计频点不要贴边，需预留频偏余量。 |
| 板厚增大 | 阻抗和耦合变化，线间场分布改变。 | L1/L3 参考变化必须重算 50 Ω 线宽。 |
| 线宽变宽 | 阻抗降低，局部电长度和耦合变化。 | 宽线会影响回损和外部 Q。 |
| 间距变小 | 耦合增强，通带可能变宽，回损和零点可能移动。 | 接近 4 mil 时制造风险显著增加。 |
| 谐振器变长 | 中心频率降低。 | 用全局长度缩放校正频偏时要同步检查零点。 |
| via 电感增大 | 短路端等效变长，零点和谐振点偏移。 | 短路支节需要 via 补偿。 |
| taper 改变 | 外部 Q 和端口匹配变化。 | 过渡不要覆盖关键耦合区域。 |

## 8. 输出产物

每个 tolerance sweep 至少输出：

```text
tolerance_plan.json
tolerance_summary.csv
corner_<id>_params.json
corner_<id>_score.csv
corner_<id>_run_manifest.json
robustness_report.md
```

summary 建议字段：

| 字段 | 说明 |
|---|---|
| `nominal_candidate_id` | nominal 候选。 |
| `corner_id` | 扰动角点编号。 |
| `variation_type` | `Er_high`、`slow_freq` 等。 |
| `parameter_delta` | 变量变化。 |
| `run_id` | 对应仿真 run。 |
| `target_profile_id` | 目标 profile。 |
| `score_version` | 评分版本。 |
| `status` | nominal/robust 状态。 |
| `worst_margin` | 最差约束余量。 |
| `failure_reason` | 失败原因。 |

## 9. 自动化接入建议

P2 阶段建议新增：

```text
src/simads/mfg/tolerance.py
tools/propose_tolerance_corners.py
tools/run_tolerance_sweep.py
tools/summarize_tolerance_sweep.py
```

实现顺序：

1. 先从 `params.json` 派生扰动角点，不直接改 DXF。
2. 复用现有 layout generator 重新生成每个角点 layout。
3. 复用 candidate runner，确保每个角点有独立 `run_id`。
4. 复用 target profile evaluator，输出统一 score。
5. 把 robust status 回填 round index 和报告。

## 10. Release Gate

候选进入正式报告或打样建议前，必须说明：

```text
nominal_status:
robust_status:
manufacturing_rule:
min_width_margin:
min_gap_margin:
via_rule:
required_corner_runs:
passed_corner_runs:
failed_corner_runs:
worst_case_metrics:
known_risks:
```

未执行 tolerance sweep 的候选只能标记为 `nominal_pass` 或 `tune`，不得标记为 `release_candidate`。
