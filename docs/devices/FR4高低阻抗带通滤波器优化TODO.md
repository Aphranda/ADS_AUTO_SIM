# FR4 高低阻抗带通滤波器优化 TODO

Status: Active
Domain: DEVICE
Canonical: `docs/devices/FR4高低阻抗带通滤波器优化TODO.md`
Related: `docs/README.md`, `docs/layout/LAYOUT_RECONSTRUCTION_CHECKLIST.md`, `docs/opt/OPT_OBJECTIVE_FUNCTION_DESIGN.md`, `projects/bfp_6_8g_i7_fr4/docs/fr4_stub_bpf_l3_reference.md`
Last updated: 2026-08-01
Owner: ADS Automation

更新时间：2026-07-30

## 1. 当前目标

设计低成本 FR4 6-8 GHz 带通滤波器，阻带抑制要求先按 20 dB 以上评估。当前板层参考为 L1 信号、L2 避让、L3 地，等效介质厚度 h = 1.2906 mm。加工能力按 6 mil 控制，最小线宽/间隙优先不低于 0.1524 mm，工程上优先保留到 0.16 mm 以上。

## 2. 当前自动化状态

高低阻抗 SIR 版图已接入现有 ADS 自动闭环流程：

1. 由 CSV 参数表生成 DXF、JSON、SVG、DRC 文件。
2. 自动导入 ADS Layout。
3. 根据 JSON 放置 P1/P2 端口。
4. 从模板 `DA_SSBFilter1_Step_R` 克隆 EM Setup。
5. 使用 RFPro/FEM API 自动仿真。
6. 导出 S 参数 CSV。
7. 自动计算关键频点和通带评分。

相关脚本：

- `SIM/tools/generate_hilo_sir_bpf_layout.py`
- `SIM/tools/ads_import_dxf_add_ports.py`
- `SIM/tools/ads_clone_emsetup_template.py`
- `SIM/tools/ads_run_rfpro_fem.py`
- `SIM/tools/analyze_ads_dataset.py`
- `SIM/tools/run_ads_filter_candidate.py`

## 3. 已完成改动

`generate_hilo_sir_bpf_layout.py` 已支持非均匀级间耦合间隙：

```text
coupling_gaps_mm = 0.16;0.24;0.24;0.16
```

对于 5 阶结构，对应 4 个相邻谐振器间隙。旧的统一间隙 `coupling_gap_mm` 仍兼容。

第三轮参数表：

```text
SIM/projects/bfp_6_8g_i7_fr4/plans/hilo_sir_bpf_l3_round3.csv
```

第三轮版图输出：

```text
SIM/projects/bfp_6_8g_i7_fr4/layouts/hilo_sir_bpf_l3_round3/
```

第三轮仿真结果：

```text
SIM/projects/bfp_6_8g_i7_fr4/results/hilo_sir_bpf_l3_round3/
```

## 4. 当前仿真结论

### 4.1 Round2 基准

`hilo_sir_l3_r2_l107_g020_f016`

- S21@5G = -33.91 dB
- S21@6G = -18.57 dB
- S21@7G = -4.20 dB
- S21@8G = -14.55 dB
- S21@9G = -21.81 dB

判断：5 GHz 与高边抑制有基础，但 6 GHz 和 8 GHz 未打开，通带不成立。

`hilo_sir_l3_r2_l107_g018_f016`

- S21@5G = -34.55 dB
- S21@6G = -18.07 dB
- S21@7G = -4.65 dB
- S21@8G = -23.58 dB
- S21@9G = -45.43 dB

判断：统一缩小级间间隙会让高边更早截止，不能解决 6-8 GHz 通带打开问题。

### 4.2 Round3 非均匀耦合

`hilo_sir_l3_r3_edge016_mid024_f016`

- S21@5G = -30.62 dB
- S21@6G = -11.72 dB
- S21@7G = -10.49 dB
- S21@8G = -11.93 dB
- S21@9G = -33.22 dB

判断：外侧强耦合、中心弱耦合方向有效，6 GHz 和 8 GHz 明显抬升，但 7 GHz 出现通带凹陷，说明耦合分布仍不合理。

`hilo_sir_l3_r3_edge016_mid020_f016`

- S21@5G = -33.41 dB
- S21@6G = -15.92 dB
- S21@7G = -8.91 dB
- S21@8G = -13.58 dB
- S21@9G = -36.70 dB

判断：中心间隙从 0.24 mm 收到 0.20 mm 后，整体没有改善，外部耦合/馈电仍可能是主要限制。

`hilo_sir_l3_r3_edge016_mid026_fg152`

- S21@5G = -30.81 dB
- S21@6G = -12.35 dB
- S21@7G = -9.31 dB
- S21@8G = -23.66 dB
- S21@9G = -47.49 dB

判断：馈电间隙压到 0.1524 mm 工艺下限后，8 GHz 反而明显恶化，高边抑制增强。单纯增强外部耦合不是充分条件。

## 5. 明日优先 TODO

1. 生成 round3 汇总文件 `sweep_summary.csv`，统一比较 round2/round3 结果。
2. 以 `hilo_sir_l3_r3_edge016_mid024_f016` 作为下一轮基础，因为它在 6 GHz 和 8 GHz 两侧抬升最明显。
3. 下一轮重点调整馈电结构，而不是继续单调缩小间隙：
   - 扫描 `feed_overlap_mm`
   - 扫描馈电相对谐振器的垂直位置
   - 检查输入/输出耦合线长度
   - 评估是否需要从端部耦合改为更明确的抽头或平行耦合输入
4. 优先做单候选烟雾测试，再做小批量扫描，避免多组异常卡住 ADS。
5. 如果继续无法把 6-8 GHz 通带拉到 -3~-5 dB 以内，停止当前 U 型高低阻抗 SIR 版图拓扑，转向更标准的 FR4 可加工带通结构：
   - 平行耦合线带通
   - 梳状/发夹类带通
   - 降阶宽带耦合结构

## 6. 下一轮建议参数方向

优先从以下方向建立 round4：

```text
base = hilo_sir_l3_r3_edge016_mid024_f016
coupling_gaps_mm = 0.16;0.24;0.24;0.16
feed_gap_mm = 0.16
```

建议扫描：

- `feed_overlap_mm`: 3.2 / 3.6 / 4.0 / 4.4 mm
- `arm_l_mm`: 4.45 / 4.55 / 4.65 mm
- `bridge_l_mm`: 2.55 / 2.62 / 2.70 mm
- `coupling_gaps_mm`: `0.16;0.22;0.22;0.16`、`0.18;0.24;0.24;0.18`

判断标准：

- 5 GHz 抑制优先满足 20 dB 以上。
- 9 GHz 抑制优先满足 20 dB 以上。
- 6-8 GHz 内优先把最差 S21 提升到 -5 dB 以内。
- 若通带仍存在深凹陷，优先判断为拓扑问题，不再继续细调当前结构。


