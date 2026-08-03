# ADS 自动仿真目录治理方案

Status: Active
Domain: ARCH
Canonical: `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`
Related: `docs/README.md`, `docs/arch/ADS版图自动仿真项目框架设计.md`, `docs/arch/ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`, `docs/arch/ARCH_REFACTOR_TODO.md`, `docs/arch/PYTHON_SCRIPT_MANAGEMENT.md`
Last updated: 2026-08-03
Owner: ADS Automation

本文档定义 `docs/` 和 `tools/` 的分层治理策略。目标是让文档和脚本可以继续增长，但不再依赖平铺文件名和人工记忆管理。

## 1. 结论

`docs/` 和 `tools/` 都需要细分，但迁移节奏不同：

| 目录 | 是否需要细分 | 推荐节奏 | 原因 |
|---|---|---|---|
| `docs/` | 需要 | 可先逻辑分层，再物理分层 | 文档增长快，适合先建立领域索引、状态、命名和归档规则。 |
| `tools/` | 需要 | 暂缓大规模移动，先模块化 | 现有 CLI 被流程和报告引用，直接搬迁容易破坏自动化闭环。 |
| `src/simads/` | 需要优先扩展 | 逐步承接复用逻辑 | 真正的框架能力应进入包模块，`tools/` 只保留命令入口。 |

当前阶段不建议一次性把所有 `tools/*.py` 挪到子目录。更稳妥的路径是：先把复用代码沉淀到 `src/simads`，再保留旧 CLI shim，最后按功能域整理 `tools`。

当前已开始首批物理分拆：`tools/ads/` 和 `tools/layout/` 已落地，根目录继续保留同名兼容 wrapper，其余脚本仍按薄 CLI 入口运行。

## 2. `docs/` 推荐分层

短期可以先保持文件在 `docs/` 根目录，但按领域前缀、README 索引和状态字段治理；中期按 `ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md` 分批做物理子目录迁移。

### 2.1 逻辑领域

| 领域 | 前缀 | 内容 |
|---|---|---|
| 架构 | `ARCH_` | 顶层架构、目录治理、评审、迁移、验收。 |
| 数据 | `DATA_` | schema、manifest、字段契约、数据版本。 |
| 流程 | `FLOW_` | ADS 运行流程、状态机、调度、人工介入、错误处理。 |
| 环境 | `ENV_` | home/company profile、ADS API 能力、license、路径。 |
| 优化 | `OPT_` | 目标函数、搜索算法、代理模型、round 策略。 |
| 结果 | `RESULT_` | round 索引、baseline freeze、漂移复测。 |
| 制造 | `MFG_` | 板厂能力、容差、可制造性、鲁棒性。 |
| 报告 | `REPORT_` | HTML/PDF 模板、发布 gate、报告规范。 |
| 设备分支 | `DEVICE_` 或项目 docs | folded SIR、interdigital、stub 等器件分支规则。 |
| 测试 | `TEST_` | 测试矩阵、smoke、baseline full run、golden。 |

### 2.2 中期物理目录

当前 `docs/` 已达到需要规划物理分层的规模。目标结构如下：

```text
docs/
  README.md
  arch/
  data/
  env/
  flow/
  layout/
  devices/
  opt/
  result/
  mfg/
  report/
  test/
  archive/
```

迁移节奏：

| 阶段 | 目标 |
|---|---|
| Phase 0 | 冻结目录规划和映射表规则，不移动文件。 |
| Phase 1 | 迁移低风险辅助文档，例如 `ENV_`、`MFG_`、`REPORT_`、`TEST_`、`LAYOUT_`。 |
| Phase 2 | 迁移 `DATA_`、`FLOW_`、`OPT_`、`RESULT_` 等被流程引用的核心规范。 |
| Phase 3 | 迁移主框架、`ARCH_`、重构进度和脚本管理文档。 |
| Phase 4 | 清理旧路径并归档历史说明。 |

迁移时必须生成路径映射表，并在 README 或 `docs/archive/` 中保留旧名索引，避免历史引用断裂。详细目录职责、当前文件目标归属、归档规则和验收 gate 见 `ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md`。

## 3. `tools/` 推荐分层

`tools/` 的长期目标是“薄 CLI 入口”，不承担核心业务逻辑。可复用能力逐步进入 `src/simads/`。

### 3.1 当前阶段

当前阶段保持 `tools/*.py` 可直接运行，避免破坏已有命令：

```text
python tools\run_ads_filter_candidate.py ...
python tools\run_ads_filter_sweep.py ...
python tools\analyze_ads_dataset.py ...
```

新增能力优先进入 `src/simads`，旧脚本只做参数解析和调用。

### 3.2 目标分层

中期可按以下方式管理：

```text
tools/
  ads/
    import_dxf_add_ports.py
    clone_emsetup_template.py
    run_rfpro_fem.py
    export_fem_dataset.py
  layout/
    generate_interdigital_filter_layout.py
    generate_folded_sir_bpf_layout.py
    generate_hilo_sir_bpf_layout.py
    generate_stub_bpf_layout.py
  opt/
    build_i7_fr4_optimization_dataset.py
    propose_i7_fr4_surrogate_candidates.py
  scoring/
    analyze_ads_dataset.py
  maintenance/
    check_ads_profile.py
    check_ads_python_env.py
```

但物理迁移前必须先提供旧路径兼容 shim，例如旧的 `tools/run_ads_filter_sweep.py` 仍可运行，只转发到新模块或新脚本。

## 4. `src/simads/` 推荐分层

框架化重点应落在 `src/simads/`：

```text
src/simads/
  config/
  runtime/
  safety/
  geometry/
  exporters/
  ads/
    workspace.py
    layout.py
    emsetup.py
    rfpro.py
    dataset.py
  scoring/
  optimizer/
  devices/
    interdigital/
    folded_sir/
    hilo_sir/
    stub/
```

迁移原则：

- `tools` 解析 CLI 参数。
- `src/simads` 承担可复用逻辑。
- ADS Python 专用逻辑尽量薄封装，复杂计算留在 host Python。
- 每次迁移一个功能域，不跨域大改。

## 5. 命名和状态规则

新增正式文档必须包含元数据块：

```text
Status: Draft / Active / Frozen / Deprecated
Domain: ARCH / DATA / FLOW / ENV / OPT / RESULT / MFG / REPORT / TEST
Canonical: `docs/arch/ARCH_DIRECTORY_GOVERNANCE.md`
Related: `path1`, `path2`
Last updated: YYYY-MM-DD
Owner: ADS Automation
```

状态定义：

| 状态 | 含义 |
|---|---|
| Draft | 设计中，不能作为自动化实现依据。 |
| Active | 当前依据，可被脚本和流程引用。 |
| Frozen | 冻结基线或正式报告，只补勘误。 |
| Deprecated | 已替代，保留迁移说明。 |

## 6. 迁移 Gate

移动 `docs/` 或 `tools/` 文件前必须满足：

- 已确认所有引用位置。
- 已生成迁移映射表。
- README 已更新。
- 旧 CLI 入口仍可运行，或明确写入 Deprecated 说明。
- 测试策略中的 T0/T1/T2/T3 gate 通过。
- 涉及 ADS API 的移动必须重新运行 ADS Python API smoke。


## 7. `projects/` Git 产物治理

`projects/` 下的文件按“能否复现”和“是否作为冻结证据”分级管理。Git 不应保存每轮优化产生的全量候选池、全量版图侧文件和全量仿真原始导出；这些文件会随 ADS/RFPro/HFSS/NN 迭代快速膨胀，并且可以由计划表、生成器、pipeline 配置和仿真脚本重新生成。

推荐保留到 Git 的内容：

| 类型 | 示例 | 原因 |
|---|---|---|
| 项目源配置 | `config/projects/*.json`、`config/pipelines/*.json`、`config/stackups/*.json`、`config/ads_profiles.json` | 定义项目、层叠、profile、模板、频段和流程契约。 |
| 生成器和流程脚本 | `src/simads/**`、`tools/**` | 复现候选、导入 ADS/HFSS、评分和训练的代码源。 |
| 精简候选计划 | `projects/*/plans/*.csv`，但不含 `*_pool.csv` | 非 pool 计划表是一次迭代的可复现入口。 |
| 汇总结果 | `projects/*/results/**/sweep_summary.csv`、baseline summary | 便于快速比较轮次，不需要提交每个候选的原始曲线。 |
| baseline/release 证据 | `projects/*/baselines/**`、正式 reports | 作为冻结结论、报告引用和跨电脑复核依据。 |
| 文档和报告 | `docs/**`、`projects/*/reports/**` | 记录设计判断、流程和发布结论。 |

默认不进入 Git 的内容：

| 类型 | 示例 | 处理方式 |
|---|---|---|
| 候选池计划 | `plans/*_pool.csv` | 由生成器和随机种子复现；只提交筛选后的 top/round 计划。 |
| 版图侧文件 | `layouts/**/*_layout.json`、`*_params.json`、`*_tuning_table.csv`、`*.svg`、`*.dxf` | 由 plan + generator 生成；关键候选需要冻结时复制到 `baselines/` 或 `git add -f`。 |
| 原始仿真导出 | `results/**/*_rfpro.csv`、`*_score.csv`、`*.s2p`、结果 SVG | 本地保留用于分析；Git 只保存 summary/baseline/report。 |
| NN 派生产物 | `*.npz`、`*.pt`、`*_ranking.csv`、`*_predictions.csv` | 可由已有样本和训练脚本再生成；正式模型另行做 release/baseline。 |
| run 临时状态 | `projects/*/runs/**`、`projects/*/results/**/runs/**` | 本地排障用；长期证据进入 baseline manifest。 |

如果某个被 ignore 的文件确实需要作为正式证据提交，应满足以下条件之一：

- 它是 baseline/release 的唯一输入，且无法由已提交的 plan + generator 重建。
- 它被正式报告直接引用，并且报告不能接受重新生成版本。
- 它用于跨 ADS/HFSS/backend 对照，且需要冻结当时工具版本和文件 hash。

此时优先把文件归档到 `projects/<project_id>/baselines/<baseline_id>/` 或 `projects/<project_id>/reports/`；必要时使用 `git add -f <path>` 明确标记为例外，避免全量候选目录误入 Git。

## 8. 当前建议

近期执行顺序：

1. 先补 `src/simads.safety`，把 workspace 写入安全 gate 代码化。
2. 再补 `flow/FLOW_RUN_STATE_MACHINE.md`，明确 resume、幂等和失败恢复。
3. 再补 P1 的 round 结果索引和报告发布 gate。
4. 暂不大规模移动 `tools/`，只在新增模块后逐步抽薄 CLI。
5. `docs/` 先按 `ARCH_DOCS_INTERNAL_STRUCTURE_PLAN.md` 完成 Phase 0；之后从低风险文档开始分批物理迁移。
