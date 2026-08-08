# SP8T 仿真文件总索引

Status: Active
Domain: PROJECT_INDEX
Canonical: `projects/SP8T_INDEX.md`
Related: `projects/hfss_sma_connector/microstrip_connector/README.md`, `projects/sp8t_real_board_hfss/README.md`, `../archive/README.md`, `archive/sp8t/README.md`, `archive/sp8t/20260808/README.md`, `projects/hfss_sma_connector/reports/SP8T开关连接器设计优化报告/`, `archive/sp8t/20260808/reports/SP8T开关连接器设计优化报告_架构重构_20260808/`
Last updated: 2026-08-08

本文档把仓库里所有 SP8T 相关 HFSS 资产放到同一入口下，避免把连接器分支和实板分支当成两个无关项目。

## 分支映射

| 分支 | 角色 | 入口 |
|---|---|---|
| 连接器分支 | SMA 夹具、单端/双端连接器、端口和 launch 调试 | `projects/hfss_sma_connector/microstrip_connector/README.md` |
| 实板分支 | SP8T 实板导入、RF_IN/RF_OUT/Core 相关板端仿真、基线和评分 | `projects/sp8t_real_board_hfss/README.md` |

## 当前资产

### 连接器分支

- 主报告：`projects/hfss_sma_connector/reports/SP8T开关连接器设计优化报告/`
- 架构重构报告：`archive/sp8t/20260808/reports/SP8T开关连接器设计优化报告_架构重构_20260808/`
- 备份和过程文件：`projects/hfss_sma_connector/backups/`
- 结果和检查文件：`projects/hfss_sma_connector/results/`
- 运行目录：`projects/hfss_sma_connector/simulations/`

### 实板分支

- 设计读入和基线：`projects/sp8t_real_board_hfss/README.md`
- 报告和检查：`projects/sp8t_real_board_hfss/reports/`
- 基线结果：`projects/sp8t_real_board_hfss/results/baselines/`
- 归档快照：`archive/sp8t/20260808/`
- 评分和批量结果：`projects/sp8t_real_board_hfss/results/`
- 候选计划：`projects/sp8t_real_board_hfss/plans/`
- 任务清单：`projects/sp8t_real_board_hfss/TODO.md`

## 目录约定

- `reports/` 放结论、检查和报告文本。
- `results/` 放 S 参数、评分、TDR、SVG、检查 JSON 和 run 事件。
- `plans/` 放待跑候选和后续动作。
- `results/baselines/` 放冻结基线和无效归档。
- `runs/` 放构建与执行清单。
- `archive/` 放冻结后的整项目快照，不放活跃迭代目录。

## 读取顺序

1. 先看本文件。
2. 再看连接器分支 README。
3. 再看实板分支 README。
4. 最后进入对应 `reports/` 或 `results/` 定位具体 run。

## 约束

- AEDT 文件只通过 API 流程处理，不直接改文档式工程文件。
- 连接器分支和实板分支可以共享方法论，但结果目录必须分开。
