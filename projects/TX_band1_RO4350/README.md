# TX_band1_RO4350

7 阶交指 Chebyshev 带通滤波器参数化工程。

- 通带：17.70–19.35 GHz，纹波 0.10 dB
- 扫频：14–23 GHz（121 点）
- 基板：RO4350，`er=3.66`，介质厚度 254 µm，铜厚 35 µm
- 输入/输出：50 Ω，馈线宽度 0.5225 mm
- 锥形过渡：长度 0.60 mm，尖端宽度 0.20 mm，插入重叠 0.05 mm
- 输入/输出 tap：距底部 1.55 mm，位于谐振器中上部，远离底部接地过孔

版图输出位于 `layouts/nominal/`。ADS 公司路径 dry-run 命令：

```powershell
D:\Microsoft\Python\ads-automation\Scripts\python.exe tools/run_ads_filter_candidate.py TX_band1_RO4350 --project-id TX_band1_RO4350 --profile company --target-profile ro4350_tx_band1 --dry-run
```

当前 DRC 唯一提示是 45.74 µm 开路端间隙小于 0.5 mm 顶层过孔焊盘外形；这来自原始尺寸组合，实际投板前需按工艺规则缩小焊盘或增大端隙。
