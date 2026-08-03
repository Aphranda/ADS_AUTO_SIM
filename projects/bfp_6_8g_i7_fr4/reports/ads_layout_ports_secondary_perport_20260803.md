# ADS Layout Port Inspection

Generated: `2026-08-03T00:45:01`
Target: `SIMADS_EM_PAR_lib:i7_fr4_r13_port_secondary_perport_20260803_mm:layout`
Python: `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe`

## Layout Terms

- `P1`: net=`P1`, pins=1, delta_gap=`True`, secondary=[{"repr": "<keysight.ads.de.db_uu._db_x.SecondaryTermInfo object at 0x00000269426E2510>", "term_name": "P1_GND", "is_positive": false}]
  - pin `P__0`: angle=`180.0`, snap=`{'x': -3.54, 'y': 1.95, '_repr': 'PointF(x=-3.54, y=1.95)'}`, pinfigs=1
    - fig type=`<ApolloType 13>`, layer=`1000`, purpose=`4294967295`, layer_id=`{'repr': '<LayerId 1000>', 'layer': 1000, 'purpose': -1}`
- `P2`: net=`P2`, pins=1, delta_gap=`True`, secondary=[{"repr": "<keysight.ads.de.db_uu._db_x.SecondaryTermInfo object at 0x0000026942739E50>", "term_name": "P2_GND", "is_positive": false}]
  - pin `P__1`: angle=`0.0`, snap=`{'x': 7.05, 'y': 1.95, '_repr': 'PointF(x=7.05, y=1.95)'}`, pinfigs=1
    - fig type=`<ApolloType 13>`, layer=`1000`, purpose=`4294967295`, layer_id=`{'repr': '<LayerId 1000>', 'layer': 1000, 'purpose': -1}`
- `P1_GND`: net=`P1_GND`, pins=1, delta_gap=`False`, secondary=[]
  - pin `P__2`: angle=`0.0`, snap=`{'x': -3.54, 'y': 1.95, '_repr': 'PointF(x=-3.54, y=1.95)'}`, pinfigs=1
    - fig type=`<ApolloType 13>`, layer=`1001`, purpose=`4294967295`, layer_id=`{'repr': '<LayerId 1001>', 'layer': 1001, 'purpose': -1}`
- `P2_GND`: net=`P2_GND`, pins=1, delta_gap=`False`, secondary=[]
  - pin `P__3`: angle=`0.0`, snap=`{'x': 7.05, 'y': 1.95, '_repr': 'PointF(x=7.05, y=1.95)'}`, pinfigs=1
    - fig type=`<ApolloType 13>`, layer=`1001`, purpose=`4294967295`, layer_id=`{'repr': '<LayerId 1001>', 'layer': 1001, 'purpose': -1}`

## EM Setup XML

### `canonical_em_state`

- path: `D:\Work\ADS\SIMADS_EM_PAR\SIMADS_EM_PAR\SIMADS_EM_PAR_lib\i7_fr4_r13_port_secondary_perport_20260803_mm\em%Setup\emStateFile.xml`
- exists: `True`
- port `P1`: gndLayer=`1001`
- port `P2`: gndLayer=`1001`

### `gui_layout_state`

- path: `D:\Work\ADS\SIMADS_EM_PAR\SIMADS_EM_PAR\undefined\state\SIMADS_EM_PAR_lib\i7_fr4_r13_port_secondary_perport_20260803_mm\layout\emSetup.xml`
- exists: `True`
- port `P1`: gndLayer=`ETCH_INNER1`
- port `P2`: gndLayer=`ETCH_INNER1`
