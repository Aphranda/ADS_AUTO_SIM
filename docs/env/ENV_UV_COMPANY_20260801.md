# 公司电脑 UV 环境记录

Status: Active
Domain: ENV
Canonical: `docs/env/ENV_UV_COMPANY_20260801.md`
Related: `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`, `config/ads_profiles.json`
Last updated: 2026-08-05
Owner: ADS Automation

本文档记录公司电脑 ADS 自动化 host Python 环境。家里电脑继续使用既有 `D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe`，不在本文档中修改。

## 环境路径

```text
UV: uv 0.8.10
Project root: E:\OneDrive\4.Code\SIM
Company host Python: D:\Microsoft\Python\ads-automation\Scripts\python.exe
ADS Python: D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe
ADS workspace: D:\Work\ADS\6-8G_Fillter\6-8G_Fillter
ADS library: 6-8G_Fillter_lib
```

## 创建和安装命令

```powershell
uv venv D:\Microsoft\Python\ads-automation --python 3.12
uv pip install --python D:\Microsoft\Python\ads-automation\Scripts\python.exe -e ".[optimizer,reports]"
```

## 配置变更

`company` profile 的 `host_python` 已更新为：

```text
D:\Microsoft\Python\ads-automation\Scripts\python.exe
```

`home` profile 保持：

```text
D:\Microsoft\uv-venvs\ads-automation\Scripts\python.exe
```

从 `2026-08-01` 起，`src/simads/config/profiles.py` 优先读取 `config/ads_profiles.json`，源码中的 profile 数据只作为配置文件缺失时的兜底默认值。公司/家里电脑切换时，应优先维护 `config/ads_profiles.json`，避免 JSON 和源码双写漂移。

## HFSS/PyAEDT 版本口径

当前公司 HFSS 连接器自动化环境固定为：

```text
AEDT: 2026.1
Python: D:\Microsoft\Python\ads-automation\Scripts\python.exe
pyaedt==1.3.0
pyedb==0.81.0
ansys-edb-core==0.3.3
grpcio==1.83.0
protobuf==6.33.6
```

`pyaedt 1.3.0` 是当前稳定版；项目 `pyproject.toml` 的 `hfss` extra 固定该版本，避免后续环境重建时 PyAEDT 自动漂移。AEDT 2026.1 non-graphical 启动默认使用 SIMADS 兼容入口：

```text
PYAEDT_USE_PRE_GRPC_ARGS=True
grpc_secure_mode=False
SIMADS_AEDT_WAIT_FOR_LICENSE=True
SIMADS_AEDT_DESKTOP_TIMEOUT_S=300
```

该入口会把 PyAEDT gRPC transport 从 WNUA 切到 INSECURE，避免公司机 non-graphical gRPC server 启动失败。

2026-08-05 连接器 HFSS 自动化补充：

- `src/simads/hfss/aedt_startup.py` 是公司机 non-graphical AEDT 启动唯一兼容入口；新脚本必须先调用 `apply_grpc_startup_compat()`，再导入或创建 PyAEDT AEDT app。
- 每次创建 `Hfss3dLayout` 后应调用 `start_aedt_reaper(app, label=...)`，拉起隐藏生命周期监控。普通自动化退出后允许回收无可见窗口的目标 AEDT PID；`--keep-open` / `--keep-attached` 调试场景只记录，不执行回收。
- 当前 reaper dry-run 报告为 `projects\hfss_sma_connector\reports\aedt_reaper_dry_run_20260805.json`，结果 `candidates=[]`、`eligible_pids=[]`。
- 当前连接器仿真禁止启动 GUI，避免影响公司电脑其它工作；如需人工 GUI 确认，必须先在相关 workflow 文档或 manual intervention log 中记录原因、范围和影响。

## 验证结果

```text
D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\check_editable_install.py --require-editable
结果：通过，sim-ads-automation 为 editable 安装。

D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\check_ads_profile.py --profile company
结果：通过，ads_root、ads_python、host_python、workspace、library、layer_map 均为 OK。

D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\run_ads_filter_candidate.py smoke_candidate --score-only --dry-run --profile company --target-profile fr4_25db_rl6
结果：通过，dry-run 中 host_python 已指向公司 UV 环境，未启动 ADS/FEM。

D:\Microsoft\Python\ads-automation\Scripts\python.exe tools\propose_i7_fr4_surrogate_candidates.py --help
结果：通过。
```

## 包版本记录

`uv pip freeze --python D:\Microsoft\Python\ads-automation\Scripts\python.exe` 输出：

```text
contourpy==1.3.3
cycler==0.12.1
fonttools==4.63.0
joblib==1.5.3
kiwisolver==1.5.0
matplotlib==3.11.1
narwhals==2.24.0
numpy==2.5.1
packaging==26.2
pandas==3.0.5
pillow==12.3.0
pyparsing==3.3.2
python-dateutil==2.9.0.post0
scikit-learn==1.9.0
scipy==1.18.0
-e file:///E:/OneDrive/4.Code/SIM
six==1.17.0
threadpoolctl==3.6.0
tzdata==2026.3
```

## 注意事项

`uv pip list --python ...` 在普通沙箱权限下读取 uv cache 曾出现权限拒绝；提升权限后 `uv pip freeze --python ...` 可正常导出。当前 venv 未安装 `pip` 模块，包版本记录使用 uv 管理命令。
