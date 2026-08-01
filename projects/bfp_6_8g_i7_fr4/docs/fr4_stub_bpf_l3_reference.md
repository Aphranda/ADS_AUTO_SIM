# FR4 短路支节滤波器 L3 参考地设置说明

本文档用于 6-8 GHz 低成本 FR4 短路支节带通滤波器的 L3 参考地版本。

## 1. 参考层选择

目标层叠：

```text
L1: 顶层信号，1 oz Cu，0.0350 mm
PP: 7628 RC49%，0.2104 mm
L2: 滤波器区域避空
Core: 1.0650 mm
L3: 完整参考地
PP: 0.2104 mm
L4: 地/屏蔽
```

L1 到 L3 的近似参考高度：

```text
h_L1_L3 = 0.2104 + 0.0152 + 1.0650 = 1.2906 mm
```

原理图一阶综合时可把 substrate 厚度近似设置为：

```text
Er   = 4.6
B    = 1.2906 mm
T    = 0.035 mm
TanD = 0.02
Cond = 5.8E7
```

该近似用于把主线宽度拉回可加工范围。最终结果必须以 EM 为准。

## 2. ADS EM Setup 要求

EM 层叠不能只改原理图参数，必须满足：

```text
top cond  = L1 signal metal
L2 metal  = filter keepout / no solid reference ground below filter
L3 metal  = continuous reference ground
L4 metal  = optional ground/shield
via layer = L1 to L3 grounded via
```

如果 L2 在滤波器下方仍然是完整地，结构仍会参考 L2，主线不会变宽，且与 L3 参考版本不一致。

建议在 ADS 中新建一个模板 Cell：

```text
DA_SSBFilter1_Step_R_L3
```

该模板应包含：

```text
layout
emSetup
substrate: L1 signal / L2 keepout / L3 ground
frequency: 4-10 GHz
ports: P1/P2
via: L1 to L3
```

后续自动仿真命令使用：

```powershell
python SIM\tools\run_ads_filter_candidate.py <candidate> `
  --template-cell DA_SSBFilter1_Step_R_L3 `
  --overwrite-setup
```

## 3. 版图边界和避空建议

L2 避空区域不能只覆盖金属线本体，应覆盖完整滤波器和周边场区。

建议初始避空边界：

```text
滤波器金属外形外扩 >= 2.0 mm
优先外扩 >= 2.5-3.0 mm
```

原因：

```text
h_L1_L3 ≈ 1.29 mm
边缘场明显扩展
L2 地如果离信号太近，会形成局部 L1-L2 参考，导致阻抗突变
```

## 4. 过孔注意事项

L3 参考会让短路支节接地 via 变长：

```text
via length ≈ 1.29 mm
```

6-8 GHz 下该 via 电感不可忽略，因此建议：

```text
每个短路支节末端至少 1 个 L1-L3 via
空间允许时用 2 个并联 via
via 直径 >= 0.20 mm
stub 末端金属宽度 >= via 直径 + 工艺余量
```

如果 EM 出现低端偏移或通带陷波，需要优先检查 via 电感和短路点布局。

## 5. 自动化接入

当前自动化链路可以复用：

```text
Python 生成 DXF/params JSON
ADS 导入 DXF
放置 P1/P2
克隆 L3 emSetup 模板
RFPro/FEM 4-10 GHz
导出 CSV
评分
```

需要区别于 L2 参考版本的部分：

```text
1. 原理图综合 substrate 使用 B=1.2906 mm
2. EM 模板 Cell 使用 L3 reference ground
3. via layer 定义为 L1 to L3
4. L2 在滤波器区域避空
```

## 6. 初始目标

FR4 低成本版本建议评分目标：

```text
S21 @ 5 GHz <= -20 dB
S21 @ 6 GHz >= -4.5 dB
S21 @ 8 GHz >= -4.5 dB
6-8 GHz ripple <= 3.5 dB
6-8 GHz worst S11/S22 <= -8 dB
minimum line width >= 0.1524 mm
preferred line width >= 0.20 mm
```

若 L3 参考后插损明显增加或短路点频偏严重，应优先考虑 SIR/发夹结构，而不是继续提高短路支节阶数。
