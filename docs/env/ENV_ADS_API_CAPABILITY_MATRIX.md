# ADS API 能力矩阵

Status: Draft
Domain: ENV
Canonical: `docs/env/ENV_ADS_API_CAPABILITY_MATRIX.md`
Related: `docs/arch/ADS版图自动仿真项目框架设计.md`, `projects/bfp_6_8g_i7_fr4/docs/ADS自动仿真流程说明.md`
Last updated: 2026-08-03
Owner: ADS Automation

本文档登记本机 ADS 2026 Update 1 的 API 文档源、Python 包、示例和项目验证状态。任何自动化能力进入批量仿真前，都应先在这里登记并完成 smoke test。

## 1. 当前环境

| 项 | home 配置 |
|---|---|
| ADS root | `D:\Hardware\Keysight\ADS2026_Update1` |
| ADS workspace | `D:\Work\ADS\BFP\BFP` |
| ADS library | `BFP_lib` |
| Template cell | `BFP` |
| Substrate | `BFP_lib:substrate4` |
| ADS Python | `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe` |
| Host uv Python | `D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe` |
| 当前 profile | `home` |

## 2. 本地文档源

| 类型 | 路径 | 已发现内容 | 状态 |
|---|---|---|---|
| Python API 总入口 | `D:\Hardware\Keysight\ADS2026_Update1\doc\python` | `ael`、`ann`、`dataset`、`dds`、`de`、`DesignCloud`、`edatoolbox`、`hsd`、`pwdatatools`、`quantum` | 已定位 |
| DE Python | `doc\python\de\html\index.html` | ADS Design Environment、OpenAccess、workspace、Pcell、pypde、pysubst | 待逐项验证 |
| AEL Python | `doc\python\ael\html\index.html` | Python 调 AEL、AEL 互操作、类型转换、venv、`keysight.ads.ael` | 已定位 |
| Dataset Python | `doc\python\dataset\html\index.html` | ADS dataset、DataFrame、dataset 合并和创建 | 待验证 |
| EDA Toolbox | `doc\python\edatoolbox\html\index.html` | ADS、Circuit API、Dataset、xxPro、SIPro/RFPro 示例 | 待验证 |
| PathWave Data Tools | `doc\python\pwdatatools\html\index.html` | ADS 数据、S 参数、CSV、Touchstone、MDIF、DataFrame | 待验证 |
| ADS 传统帮助 | `doc\ads\Content\ads2026update1` | AEL 函数、workspace、layout、substrate、Momentum、RFPro/FEM | 已定位 |
| 示例目录 | `examples` | DesignKit、AEL、artwork、bitmaps、RFPro/SIPro、filter/circuit 示例 | 已定位 |

## 3. Python 包和 wheel

| 包/目录 | 路径 | 用途 | 状态 |
|---|---|---|---|
| ADS bridge packages | `tools\python\packages\keysight\ads` | `keysight.ads.ael`、`keysight.ads.de`、`keysight.ads.dds` 等 ADS 内部桥接 | 待 import smoke test |
| ADS site-packages | `tools\python\Lib\site-packages\keysight` | `keysight.ads.dataset`、`keysight.edatoolbox`、`keysight.pwdatatools` | 已定位 |
| wheelhouse | `tools\python\wheelhouse` | 外部 venv 安装 Keysight wheel | 已定位 |
| venv requirements | `tools\python\wheelhouse\venv_requirements.txt` | `keysight-ads-de[app]`、`keysight-ads-ael`、`keysight-ads-subst`、`keysight-ads-dataset` 等 | 已读取 |

已发现的重点 wheel：

```text
keysight_ads_ael-635-cp313-cp313-win_amd64.whl
keysight_ads_de-635-cp313-cp313-win_amd64.whl
keysight_ads_subst-635-cp313-cp313-win_amd64.whl
keysight_ads_dataset-635-cp313-cp313-win_amd64.whl
keysight_ads_emtools-635-cp313-cp313-win_amd64.whl
keysight_edatoolbox-1.2.5-py3-none-any.whl
keysight_pwdatatools-0.12.1-cp313-cp313-win_amd64.whl
numpy-2.2.3-cp313-cp313-win_amd64.whl
pandas-2.3.0-cp313-cp313-win_amd64.whl
scipy-1.16.0-cp313-cp313-win_amd64.whl
```

## 4. 能力登记表

| 能力 | API/模块/脚本 | 文档依据 | 当前等级 | home 状态 | fallback |
|---|---|---|---|---|---|
| Python 环境导入 | `keysight.ads.de`、`keysight.ads.ael`、`keysight.ads.dataset` | `doc\python\de`、`doc\python\ael`、`doc\python\dataset` | L3 前置 | 待 smoke test | ADS 自带 Python |
| 从 Python 调 AEL | `keysight.ads.ael.call`、`keysight.ads.ael.decl` | `doc\python\ael\html\reference\ael.html` | L3 | 待 smoke test | 直接 AEL 脚本 |
| workspace 打开/检查 | DE Python / AEL `de_open_workspace` | `doc\python\de`、`doc\ads\...\ael\Workspace_Management_Functions.html` | L3 | 待 smoke test | 手动打开 ADS workspace |
| library/cell/view 检查 | DE Python OpenAccess 对象 | `doc\python\de\html\pypde\docs\reference\index.html` | L3 | 待 smoke test | 手动 ADS GUI 检查 |
| DXF 导入 | `tools\ads_import_dxf_add_ports.py` / ADS import AEL | `doc\ads\...\ael\Examples_DXF_Import.html` | L3 | 需回归确认 | 手动 Import DXF |
| 端口放置 | 当前 ADS import 脚本 / DE layout API | `doc\python\de` | L3 | 需回归确认 | 手动 layout port |
| OA 对象属性读写 | `db_uu.StringProp.create(owner, name, value)` / `owner.find_prop(name)` | DE Python OpenAccess 对象探测；`tools\ads\ads_set_port_gnd_layer_prop.py` | L3 | 已验证 `Term.portGndLayer` | 手动 ADS GUI 设置属性后重新探测 |
| layer/unit 检查 | DE/Pysubst/AEL technology 函数 | `doc\python\de\html\pysubst`、`tech_get_layout_units()` | L3 | 待验证 | 手动 layer map 检查 |
| substrate 读取 | `keysight-ads-subst` / AEL substrate 函数 | `doc\python\de\html\pysubst`、`Technology_Functions_-_Substrate.html` | L3 | 待验证 | 手动 substrate editor |
| substrate 从零生成 | `SubstrateModel`、`SubstrateStack` 等 | `keysight.edatoolbox.ads`、pysubst 文档 | L1/L2 | 待研究 | 模板 substrate 复制 |
| emSetup 克隆 | `tools\ads_clone_emsetup_template.py` | 当前项目脚本和模板工程 | L2/L3 | 需日志增强 | 手动复制 view |
| RFPro/FEM 启动 | `tools\ads_run_rfpro_fem.py` / EDA Toolbox xxPro | `doc\python\edatoolbox\html\Examples\ex_odbpp_simulate_rfpro.html`、本机 API probe | L3 | 已验证 `Analysis.fromEmSetup()` + `runAnalysis()` | GUI EMSetup/RFPro 复测 |
| dataset 导出 | `keysight.ads.dataset`、`pwdatatools`、`export_ads_fem_dataset.py` | `doc\python\dataset`、`doc\python\pwdatatools` | L4 | 需双通道复核 | RFPro CSV 导出 |
| S 参数评分 | host Python / numpy/pandas | 项目评分脚本 | L4 | 已可用 | 手动 CSV 复核 |

### 4.1 OA 对象属性写入确认

`db_uu.StringProp.create(owner, name, value)` 已确认是 ADS OpenAccess 对象的通用字符串属性写入入口，不应只理解为端口参考层专用函数。当前已验证的 owner 类型是 layout `Term`，后续可继续用同一机制探测 cell、view、shape、pin、term 等对象上 GUI 操作留下的属性差异。

已验证场景：

```python
existing = term.find_prop("portGndLayer")
if existing is None:
    db_uu.StringProp.create(term, "portGndLayer", "ETCH_INNER1")
else:
    existing.value = "ETCH_INNER1"
```

在 `i7_r13_ref_script_20260803_mm` 上写入后，ADS GUI 可保持端口参考层设置；与手动设置参考层的 `i7_r13_ref_manual_20260803_mm` 对比，`P1/P2` 的关键属性一致：

```text
portFeedType = Auto
portGndLayer = ETCH_INNER1
portType = None
```

结论：

- `portGndLayer=<reference layer>` 是当前 ADS layout port 参考层持久化的核心属性。
- `emStateFile.xml` 和界面 XML 更像 GUI 状态或缓存，不足以作为端口参考层的主写入点。
- `secondary_term_info` 已测试，不是本场景中 ADS GUI 端口参考层的持久化机制。
- 该属性写入函数的价值在于“先人工操作，再对象探测，再脚本复刻”。后续遇到 ADS GUI 有能力但公开 API 不明确的配置项，应优先比较对象属性，而不是直接 patch XML。

### 4.2 EMSetup 仿真启动确认

2026-08-03 已按同样的 API 探测方法确认：当前未发现稳定的 ADS DE 侧 `EMSetup.simulate()` 或 GUI Simulate 按钮直接 API。可自动化、可复测的启动入口在 RFPro/xxPro Python 上下文中：

```python
xxpro.use_workspace(workspace_path)
xxpro.load_pro_view(ads.LibraryCellView(library=library_name, cell=cell_name, view=rfpro_view_name))
analysis = empro.analysis.Analysis.fromEmSetup("emSetup")
empro.toolkit.analysis.runAnalysis(analysis, waitForConfirmation=False, saveProject=True)
empro.toolkit.simulation.wait(empro.activeProject.simulations[-1])
```

其中 `emSetup` 是 RFPro/EMPro 项目内部识别的 EM setup 名称；物理 ADS view 目录仍可能是 `em%Setup`。标准流程仍是：

1. 用 ADS Python `keysight.ads.emtools.create_empro_view()` 或 `update_empro_view()` 由 layout + substrate 创建 RFPro view。
2. 进入 `keysight.edatoolbox.multi_python.xxpro_context()`。
3. 在 xxPro 子进程中 `load_pro_view()`。
4. 在同一 xxPro 子进程中 `Analysis.fromEmSetup("emSetup")`。
5. 用 `runAnalysis()` 启动，并用 `simulation.wait()` 等待完成。

重要边界：

- `empro` 模块必须在 `xxpro_context()` 子进程内导入和使用，不应在父 ADS Python 进程里导入后把枚举值传入子进程。
- 若需要接近 GUI EMSetup Simulate 的结果回写行为，可在子进程内设置 `analysis.onResultsAction = empro.analysis.Analysis.OaEmdataViewORA`。
- `--plan-type Adaptive --points 40` 不保证导出 40 个频点；本次验证实际导出 20 点。若需要固定点数，应使用 `--plan-type Linear`。

验证记录：

```text
cell = SIMADS_EM_PAR_lib:i7_r13_ref_script_20260803_mm
rfpro_view = rfpro_emsetup_start_probe3_20260803
analysis = emsetup_start_probe3_4to10_40
command = tools\ads\ads_run_rfpro_fem.py --on-results-action oa-emdata
requested = 4-10 GHz, Adaptive, 40 points, max_passes=8
actual = 20 exported points, finished in about 3 minutes
csv = projects\bfp_6_8g_i7_fr4\results\emsetup_start_probe_i7_r13_ref_script_20260803\rfpro_emsetup_start_probe3_40pt.csv
log = projects\bfp_6_8g_i7_fr4\reports\ads_emsetup_start_probe3_40pt_20260803.log
```

## 5. Smoke Test 清单

### 5.1 import smoke test

必须输出：

```text
sys.executable
sys.version
profile-selected HPEESOF_DIR
keysight.ads.de import result
keysight.ads.ael import result
keysight.ads.dataset import result
keysight.edatoolbox import result
keysight.pwdatatools import result
```

### 5.2 workspace smoke test

必须输出：

```text
workspace exists
library exists
template cell exists
layout view exists
em setup view exists
substrate exists
layout unit / resolution
available layer names
```

### 5.3 workflow smoke test

必须输出：

```text
candidate cell created or reused
DXF imported
ports placed
emSetup cloned
RFPro/FEM run started
RFPro/FEM run finished or failed with classified error
dataset or CSV exported
score CSV generated
```

## 6. 待办

```text
P0 建立 ads_api_import_smoke_test.py，优先验证 home profile。
P0 把 home/company 两套 profile 的 API smoke test 结果分别登记到本文件。
P0 把 RFPro/FEM 脚本日志拆成 prepare/import/setup/solve/export/score 阶段。
P1 验证 DE Python 直接创建 layout 图元、pin、port 的 API 调用模式。
P1 验证 pysubst / keysight-ads-subst 是否可安全读取当前 BFP_lib:substrate4。
P1 从 ADS Python exporter 导出一个简单 cell，作为后续 Python Pcell/直接绘图参考。
P2 评估是否将论文参数化版图封装为 ADS Python Pcell。
```

