# Round Script Migration Plan

Status: Active
Domain: OPT
Canonical: `docs/opt/ROUND_SCRIPT_MIGRATION_PLAN.md`
Related: `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/arch/ARCH_REFACTOR_TASK_PROGRESS.md`, `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`, `config/round_script_migration.json`
Last updated: 2026-08-01
Owner: ADS Automation

本文档记录历史 round 候选生成脚本的迁移策略。当前目标不是删除旧脚本，而是把有效流程逐步收敛到 project active sweep 和 optimizer 配置，避免后续新增轮次继续复制 `make_*round*.py`。

## 当前原则

| 原则 | 说明 |
|---|---|
| 不移动 ADS workspace | 外部 ADS workspace 仍由 `config/ads_profiles.json` 管理。 |
| 不破坏旧 CLI | 历史脚本先保留，迁移完成前不移动、不重命名。 |
| 新轮次走配置 | 新 round 优先登记到 `config/projects/bfp_6_8g_i7_fr4.json` 的 `sweeps`。 |
| 7 阶和 9 阶分离 | FR4 7 阶低成本分支与 RO4350B 9 阶高抑制参考分开维护。 |
| 先索引再迁移 | 所有脚本先进入 `config/round_script_migration.json`，再决定迁移或归档。 |

## 状态分类

| 状态 | 含义 | 当前处理 |
|---|---|---|
| `active_configured` | 已被 project active sweep 或 generator/optimizer 配置引用。 | 保持为可执行 CLI。 |
| `legacy_candidate_generator` | 历史 FR4 7 阶候选生成脚本，仍包含有效经验扫描逻辑。 | 后续转为 deterministic variant config 或归档。 |
| `legacy_reference` | 历史 RO4350B 9 阶候选生成脚本，属于高抑制参考方案。 | 保留为参考，不进入 FR4 active sweep。 |

## 脚本索引

| 脚本 | 分支 | 策略 | 状态 | 迁移建议 |
|---|---|---|---|---|
| `tools/propose_i7_fr4_surrogate_candidates.py` | FR4 7 阶 | surrogate trust-region | active_configured | 保留为 active optimizer CLI。 |
| `tools/generate_filter_sweep.py` | FR4 7 阶 | CSV plan -> layout | active_configured | 保留为 active generator CLI。 |
| `tools/propose_filter_candidates.py` | FR4 7 阶 | deterministic variants | active_configured | 作为 legacy round 配置化迁移入口。 |
| `tools/make_i7_fr4_round2_candidates.py` | FR4 7 阶 | tap/taper/outer gap 手工扫描 | legacy_candidate_generator | 可迁移为 deterministic variant config。 |
| `tools/make_i7_fr4_round3_candidates.py` | FR4 7 阶 | feed transition 细调 | legacy_candidate_generator | 可迁移为 deterministic variant config。 |
| `tools/make_i7_fr4_round4_candidates.py` | FR4 7 阶 | 非对称 outer gap | legacy_candidate_generator | 可迁移为 deterministic variant config。 |
| `tools/make_i7_fr4_round5_candidates.py` | FR4 7 阶 | feed impedance 扫描 | legacy_candidate_generator | 可迁移为 deterministic variant config。 |
| `tools/make_i7_fr4_round6_candidates.py` | FR4 7 阶 | baseline/tw020 理论导向补偿 | legacy_candidate_generator | 可迁移为 deterministic variant config。 |
| `tools/make_next_filter_candidates.py` | RO4350B 9 阶 | 早期启发式扫描 | legacy_reference | 作为 9 阶参考归档。 |
| `tools/make_filter_round2_candidates.py` | RO4350B 9 阶 | round2 细化 | legacy_reference | 作为 9 阶参考归档。 |
| `tools/make_filter_round3_candidates.py` | RO4350B 9 阶 | round3 细化 | legacy_reference | 作为 9 阶参考归档。 |
| `tools/make_filter_round3_l600_candidates.py` | RO4350B 9 阶 | r2e_l600 分支细化 | legacy_reference | 作为 9 阶参考归档。 |

## 推荐迁移路线

1. 保持 `propose_i7_fr4_surrogate_candidates.py` 和 `generate_filter_sweep.py` 为 active CLI。
2. 将 FR4 7 阶 round2-round6 的手工变体提取为 deterministic variant 配置，字段至少包含 seed、variant name、notes、参数更新和输出 plan/layout。
3. 在 `src/simads.optimizer` 增加 deterministic variant builder，复用现有 `FilterParams` 加载、row 写出和 layout 输出能力。
4. 新增统一 CLI，例如 `tools/propose_filter_candidates.py --strategy deterministic_variants|surrogate_trust_region`。
5. RO4350B 9 阶脚本不参与 FR4 active sweep，后续按 9 阶报告和 reference 分支单独归档。

## Deterministic Variant 配置框架

当前已新增配置迁移探针：

```text
config/optimizer/i7_fr4_deterministic_variant_probe.json
```

该配置不是 round2-round6 的完整迁移结果，只用于验证以下 schema 能覆盖历史脚本的主要模式：

| 字段 | 说明 |
|---|---|
| `strategy` | 当前为 `deterministic_variants`。 |
| `seeds` | seed 参数 JSON 映射，路径相对 SIM root。 |
| `output_fields` | 输出 plan CSV 字段顺序。 |
| `field_sources` | plan 字段到 seed 参数字段的映射，支持 `gaps_mm[0]` 形式索引。 |
| `variants` | 每个候选的 `name`、`seed`、`notes` 和 `updates`。 |

新增解释器：

```text
src/simads/optimizer/variants.py
tools/propose_filter_candidates.py
```

当前入口支持：

```text
python tools/propose_filter_candidates.py --validate-only
python tools/propose_filter_candidates.py --dry-run
python tools/propose_filter_candidates.py --out-plan <plan.csv>
```

`--validate-only` 和 `--dry-run` 不写 ADS workspace、不启动 FEM。正式写 plan 后仍需通过 `generate_filter_sweep.py` 生成版图，再进入现有 sweep runner。

## 验证规则

迁移或归档前必须通过：

| Gate | 命令/检查 |
|---|---|
| 清单有效 | `python tools/check_round_script_migration.py` |
| JSON 有效 | `python -m json.tool config/round_script_migration.json` |
| deterministic 配置有效 | `python tools/propose_filter_candidates.py --validate-only` |
| CLI 编译 | `python -m py_compile tools/<script>.py` |
| 配置 smoke | 不启动 ADS/FEM，仅检查 project active sweep 能解析默认值。 |

## 当前结论

active sweep 已经覆盖 round7 的 generator 和 surrogate optimizer。历史 round2-round6 仍有工程经验价值，但不再作为新 round 的默认入口；后续优先迁移为配置化 deterministic variants，而不是继续新增 round 专用 Python 脚本。
