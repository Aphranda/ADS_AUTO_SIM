# 仿真自动化框架 TODO

Status: Active
Domain: ARCH
Related: `docs/arch/ARCH_SIM_AUTOMATION_FRAMEWORK.md`, `docs/data/DATA_RUN_MANIFEST_SCHEMA.md`
Last updated: 2026-08-02

本文档把 ADS、HFSS、NN 联合演进拆成可编码任务。执行顺序以稳定数据闭环为优先：先把每次仿真的输入、输出、日志和运行状态记录清楚，再继续拆 ADS/HFSS 后端和神经网络数据集。

## P0 当前批次

- [x] 建立 simulator-independent domain 基础模型。
  - `SweepSpec`: 频率起止、点数、扫频类型。
  - `StackupSpec`: 层叠名称、介质参数、铜厚。
  - `PortSpec`: 端口名称、端口类型、信号边、参考地边、参考对象。
  - `SimulationResultSpec`: S 参数、trace CSV、score CSV、SVG、外部工程引用。

- [x] 建立通用 simulation manifest 构建器。
  - 复用 `src/simads/runtime/manifest.py` 的 `write_run_manifest`、`write_artifact_manifest`、`write_state`。
  - 统一记录 `project_id`、`round_id`、`candidate_id`、`profile_id`、`simulator`、`sweep`、`stackup`、`inputs`、`outputs`、`flags`。
  - 支持外部 ADS/HFSS workspace 路径只记录引用，不强制搬进 repo。

- [x] HFSS workflow 写入 run/artifact manifest。
  - 增加 `--write-manifest`、`--project-id`、`--round-id`、`--candidate-id`、`--profile-id`、`--run-id`、`--run-dir`。
  - 成功时写 `completed/completed`。
  - 失败时写 `failed/failed`，并保留错误分类和异常摘要。
  - artifacts 至少包含 layout JSON、AEDT project、S2P、trace CSV、score CSV、SVG、state。

- [x] 给纯 Python 逻辑加 pytest。
  - 覆盖 domain spec 序列化。
  - 覆盖 simulation manifest 构建器。
  - 覆盖 HFSS 端口边推断和 GND 边界对齐。
  - 不在单元测试中启动 ADS、AEDT 或 pyAEDT。

- [x] 后续版图/层叠/仿真输出采用配置化命名。
  - 栈叠 token 来自 `config/stackups/<stackup_id>.json` 的 `naming.token`。
  - ADS sweep 生成、并发生成、candidate manifest 和 HFSS 默认工程/输出名已接入 stackup token。
  - 历史 baseline 不重命名、不覆盖。

## P1 HFSS 模块拆分

- [x] 将 `src/simads/hfss/workflow.py` 拆成更细模块。
  - [x] `layout_io.py`: layout JSON 读取、配置化 layout id、摘要。
  - [x] `artifacts.py`: AEDT/S2P/CSV/SVG 默认命名和路径推导。
  - [x] `layout.py`: 版图 JSON 到 HFSS primitives。
  - [x] `stackup.py`: 材料、层叠、空气盒子/开放区域。
  - [x] `ports.py`: AEDT edge port、EDB diagnostic port、端口读回。
  - [x] `results.py`: Touchstone 导出、CSV/SVG 后处理、指标摘要。
  - [x] `build.py`: stackup、geometry、ports、extents、setup/sweep、save project 的独立构建阶段。
  - [x] `solve.py`: AEDT analyze、Touchstone export、post-process trigger。
  - [x] `workflow.py`: 只保留 CLI 编排和异常/manifest。

- [x] 进一步降低 HFSS 版图生成对 CLI 的耦合。
  - `layout.py` 已支持显式 `GeometryBuildOptions`。
  - `build.py` 显式构造 geometry options 后再调用版图生成。
  - 单元测试继续使用 fake app，不启动 AEDT。

- [x] 固化可靠 HFSS route。
  - route 名称：`hfss3dlayout_aedt_edge_gap_gnd_port_edges`。
  - 默认端口：AEDT native edge port。
  - 默认参考：GND 边界正下方，GND left/right 对齐 P1/P2 cross section。
  - 默认扫频：4-10 GHz，40 点；细化裁决可切到 91 点或 200 MHz 间隔。
  - CLI：`--route reliable` 会展开到完整 route 名称和可靠端口/GND/extents 参数。

## P2 ADS/HFSS 裁决和对照

- [x] 增加 ADS/HFSS compare workflow。
  - 输入同一个 layout JSON。
  - [x] ADS 输出和 HFSS 输出统一进入 manifest。
  - [x] 生成同频点对齐后的 S21/S11/S22 对比 CSV 和 SVG。
  - 当前 CLI：`tools/compare_ads_hfss_sparams.py`。
  - 当前模块：`src/simads/workflows/sparam_compare.py`。

- [x] 建立 baseline freeze。
  - 对 `i7_fr4_r13_retest_base_l555_taper`、round13 retest baseline 建立不可覆盖 run。
  - 记录 ADS EMSETUP、HFSS AEDT、手动端口版本之间的差异。
  - 当前 baseline index: `projects/bfp_6_8g_i7_fr4/baselines/i7_fr4_r13_l555_taper/baseline_index.json`。
  - 当前 baseline summary: `projects/bfp_6_8g_i7_fr4/baselines/i7_fr4_r13_l555_taper/baseline_summary.csv`。
  - 冻结策略：已有 index 默认只校验、不重写；同一 baseline 的 artifact hash 改变时拒绝登记。

## P3 NN 数据闭环

- [ ] 从 manifest 构建 NN 数据集索引。
  - 以 layout JSON/参数向量为输入。
  - 输出 S11/S21/S22 全频 trace，训练权重以 S21 为主。
  - S11/S22 保留训练但反馈惩罚较低。

- [ ] 为 7 阶交指滤波器建立细化参数网络。
  - 输入：理论模型参数 + 局部细化参数。
  - 输出：4-10 GHz S 参数。
  - 目标：6-8 GHz 通带、5 GHz 带阻、8 GHz 以上带外抑制。

- [ ] ADS 并发仿真和 NN 迭代并行。
  - ADS/HFSS 后端继续产出高可信样本。
  - NN 用新 manifest 自动发现新样本并增量训练。
  - 排名结果只作为候选生成依据，最终用 EM 仿真裁决。
