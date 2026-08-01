# ADS Workspace 写入安全策略

Status: Active
Domain: FLOW
Canonical: `docs/flow/FLOW_ADS_WORKSPACE_WRITE_POLICY.md`
Related: `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`, `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`
Last updated: 2026-08-01
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
| score-only 流程 | 只读 | 不触发 ADS workspace 写入 gate。 |

## 3. 已接入脚本

| 脚本 | 已接入 gate | 行为 |
|---|---|---|
| `tools/run_ads_filter_candidate.py` | `validate_ads_cell_write()` | 普通候选流程拒绝写入 template cell；manifest 写入 `write_safety`。 |
| `tools/ads_clone_emsetup_template.py` | `validate_ads_cell_write()` / `guard_directory_delete()` | 直接调用底层脚本时也拒绝覆盖 template cell；覆盖 emSetup 时检查删除目录边界。 |
| `tools/patch_ads_substrate_pcvia.py` | `validate_substrate_patch()` | substrate 文件会变化时必须 `--force`；支持 `--check-only`。 |

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

