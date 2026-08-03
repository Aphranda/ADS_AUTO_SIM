# ADS Workspace 写入安全策略

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`
Related: `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`
Last updated: 2026-08-02
Owner: ADS Automation

本文档定义 ADS 自动仿真脚本对 workspace、library、cell、emSetup 和 substrate 文件的写入安全策略。目标是防止模板 cell、冻结 baseline、历史结果和 ADS substrate 被普通候选流程误覆盖。

## 1. 策略版本

```text
policy_version = ads_write_safety_v1
```

当前代码入口：

```text
src/simads/safety/__init__.py
```

## 2. 保护对象

| 对象 | 默认策略 | 允许条件 |
|---|---|---|
| template cell | 只读 | 只有显式 `--force` 才允许作为 target cell。 |
| candidate cell | 可写 | target cell 不等于 template cell，且写入路径在当前 library 下。 |
| target emSetup | 可覆盖 | 只允许删除 target cell 下的 setup view，不允许越界删除。 |
| ADS substrate `.subst` | 受保护 | 会修改文件时必须显式 `--force`。 |
| ADS technology Layer Definitions | 受保护 | 自定义孔层必须通过 `tools/ads_sync_stackup.py --sync-tech-layers` 写入为 physical layer，并校验 `Process Role` 与 `Binding`。 |
| library Master Substrate | 受保护 | 必须与当前 stackup config 的目标 substrate 一致；否则自定义 via 可能按旧层叠解释并出现红叉。 |
| score-only 流程 | 只读 | 不触发 ADS workspace 写入 gate。 |
| DXF import target | 可写 | 当前 import 路线要求 DXF 文件 stem 与 `--cell` 一致；若要写入独立 smoke cell，应先复制/重命名 DXF，避免覆盖原始候选 cell。 |

## 3. 已接入脚本

| 脚本 | 已接入 gate | 行为 |
|---|---|---|
| `tools/run_ads_filter_candidate.py` | `validate_ads_cell_write()` | 普通候选流程拒绝写入 template cell；manifest 写入 `write_safety`。 |
| `tools/ads_clone_emsetup_template.py` | `validate_ads_cell_write()` / `guard_directory_delete()` | 直接调用底层脚本时也拒绝覆盖 template cell；覆盖 emSetup 时检查删除目录边界。 |
| `tools/patch_ads_substrate_pcvia.py` | `validate_substrate_patch()` | substrate 文件会变化时必须 `--force`；支持 `--check-only`。 |
| `tools/ads_sync_stackup.py` | `validate_substrate_patch()` + ADS tech API | 同步 substrate/material/display 文件，并通过 ADS Python 校验 Layer Definitions 与 Master Substrate。 |

## 3.1 ADS 层叠一致性门禁

自定义 via 不能只出现在 layout 或 `.subst` 中。一次可用于仿真的 ADS 层叠同步必须同时满足：

| 项 | 通过标准 |
|---|---|
| Substrate XML | `.subst` 中 via 层号、上下 interface index 与目标 stackup 一致。 |
| Technology Layer Definitions | 自定义 via layer 作为 physical layer 存在，`Process Role = CONDUCTOR_VIA`，`Binding` 指向目标导体层，例如 `ETCH_TOP ETCH_BOTTOM`。 |
| Library Master Substrate | `tech.master_substrate_name` 等于目标 substrate，例如 `SIMADS_EM_PAR_lib:JLC04161H_7628_1P6MM`。 |
| Layout params | 生成的 `via_layer` 与当前 stackup 的 `ads.drill_layer` 一致。 |

当前 JLC 试验层叠使用：

```text
substrate = SIMADS_EM_PAR_lib:JLC04161H_7628_1P6MM
via layer = DRILL_TOP_BOTTOM
via layer id = 1005
process role = CONDUCTOR_VIA
binding = ETCH_TOP ETCH_BOTTOM
```

同步命令：

```powershell
python tools\ads_sync_stackup.py --profile home_simads_em_parallel --stackup-config config\stackups\JLC04161H_7628_1P6MM.json --apply --force --sync-tech-layers --verify-tech-layer-ids
```

通过标准：输出中的 `tech_layer_sync.master_substrate.ok` 为 `true`，且 `DRILL_TOP_BOTTOM` 的 `definition_ok` 为 `true`。

## 4. Manifest 记录

`run_manifest.json` 中新增 `write_safety` 字段：

```json
{
  "policy_version": "ads_write_safety_v1",
  "profile_id": "company",
  "workspace": "...",
  "library": "6-8G_Fillter_lib",
  "template_cell": "interdigital_9o_ro4350b_508um_v3_wide_mm_coords",
  "target_cell": "i7_fr4_r7_bo04_mm_coords",
  "target_is_template": false,
  "force": false,
  "operation": "candidate_flow",
  "allowed": true
}
```

## 5. 验证命令

Python 编译：

```powershell
python -m py_compile src\simads\safety\__init__.py src\simads\runtime\manifest.py tools\run_ads_filter_candidate.py tools\ads_clone_emsetup_template.py tools\patch_ads_substrate_pcvia.py
```

候选入口模板保护：

```powershell
python tools\run_ads_filter_candidate.py interdigital_9o_ro4350b_508um_v3_wide_mm_coords --profile company --template-cell interdigital_9o_ro4350b_508um_v3_wide_mm_coords --reuse-layout --skip-setup --dry-run
```

通过标准：

```text
抛出 AdsWriteSafetyError，提示 target cell equals template cell。
```

底层 emSetup clone 模板保护：

```powershell
python tools\ads_clone_emsetup_template.py --profile company --template-cell interdigital_9o_ro4350b_508um_v3_wide_mm_coords --target-cell interdigital_9o_ro4350b_508um_v3_wide_mm_coords --overwrite
```

通过标准：

```text
抛出 AdsWriteSafetyError，且在进入文件复制/删除前停止。
```

正常候选 dry-run：

```powershell
python tools\run_ads_filter_candidate.py i7_fr4_r7_bo04 --profile company --template-cell interdigital_9o_ro4350b_508um_v3_wide_mm_coords --dxf projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round7\i7_fr4_r7_bo04_mm_coords.dxf --params projects\bfp_6_8g_i7_fr4\layouts\interdigital_7o_fr4_210um_round7\i7_fr4_r7_bo04_params.json --cell i7_fr4_r7_bo04_mm_coords --out .tmp\safety_r7_bo04_rfpro.csv --score-out .tmp\safety_r7_bo04_score.csv --target-profile fr4_25db_rl6 --skip-fem --dry-run
```

通过标准：

```text
正常打印 import/setup dry-run 命令，不启动 ADS/FEM，不被 safety gate 误拦。
```

## 6. 后续扩展

- 后续增加 ADS cell 删除、library 清理、result cleanup 时，必须复用 `src/simads.safety`。
- 若未来允许批量删除候选 cell，必须增加 run manifest 备份记录和显式 `--force`。
- 若未来移动 `tools/ads/`，旧 CLI shim 仍必须保留安全 gate。
- `--stackup-config` 当前已进入 manifest 和命名，但 ADS RFPro 实际 substrate 仍来自 profile/template emSetup；在 ADS substrate 生成或 patch 完成前，不能把 ADS/HFSS 结果当作完全相同物理层叠。
