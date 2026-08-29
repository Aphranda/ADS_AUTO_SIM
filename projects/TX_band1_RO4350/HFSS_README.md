# HFSS 3D Layout

由 `TX_band1_RO4350_layout.json` 可直接生成 HFSS 3D Layout 工程。使用自定义 RO4350 两层叠层（254 µm 介质、35 µm 铜、εr=3.66），并建立 14–23 GHz 扫频。

```powershell
D:\Microsoft\Python\ads-automation\Scripts\python.exe tools/hfss/run_hfss3dlayout_filter_verdict.py `
  --profile company `
  --layout projects/TX_band1_RO4350/layouts/nominal/TX_band1_RO4350_layout.json `
  --out-dir projects/TX_band1_RO4350/hfss `
  --project-name TX_band1_RO4350_HFSS `
  --design TX_band1_RO4350 `
  --route reliable `
  --stackup-config config/stackups/RO4350_254UM_2L.json `
  --start-ghz 14 --stop-ghz 23 --points 121 `
  --adaptive-frequency-ghz 18.525 `
  --setup Setup_14to23G --sweep Sweep_14to23G_121pt `
  --build-only --project-id TX_band1_RO4350 --write-manifest
```

本机已通过 dry-run 验证几何、7 个接地过孔、2 个端口和 RO4350 叠层映射。实际 AEDT 启动受公司许可证/API 初始化耗时影响，未在本次会话中完成保存 `.aedt`。
