# SIM 仿真自动化框架架构

Status: Draft
Domain: ARCH
Last updated: 2026-08-02

## 目标

把 ADS、HFSS、神经网络和后续自动优化从“脚本堆叠”升级为可复用的仿真自动化框架。核心原则是：公共域模型只描述版图、端口、层叠、扫频和结果；ADS/HFSS 作为 backend adapter；搜索、裁决、数据集生成和 NN 闭环作为 workflow。

## 推荐分层

```text
src/simads/
  common/        # 命令计划、路径、运行清单、通用状态
  domain/        # Layout / Stackup / Port / Sweep / Result 等仿真无关模型
  ads/           # ADS workspace、layout import、emSetup、RFPro backend
  hfss/          # HFSS 3D Layout backend、端口策略、AEDT 项目运行
  nn/            # surrogate 模型、特征、训练和预测
  workflows/     # 候选生成、ADS 并发、HFSS 裁决、NN 闭环编排
tools/
  ads/           # ADS 薄 CLI
  hfss/          # HFSS 薄 CLI
  workflows/     # 端到端流程 CLI
projects/
  <project_id>/
    layouts/     # 候选版图输入
    results/     # 可长期引用的仿真结果和 SVG
    runs/        # 单次运行 manifest、log、临时状态
```

`tools` 不再承载业务逻辑，只负责：

- 解析 CLI 参数。
- 调用 `src/simads/...` 中的 plan/workflow。
- 打印 JSON 结果或写 manifest。

这样做的直接收益是：同一套 ADS/HFSS 能力可以被命令行、批量搜索、NN 闭环和测试代码复用。

## 为什么不是只分三块

`common / ADS / HFSS / 自动化流程` 是合适的工作目录，但还需要明确一个 `domain` 层。否则端口、层叠、扫频点、S 参数指标会在 ADS 和 HFSS 各写一遍，后续比较结果时容易出现口径漂移。

更稳的关系是：

```text
domain spec -> backend adapter -> result artifact -> workflow decision
```

ADS 与 HFSS 都消费同一个 spec，产出同一种 result manifest。NN 也只读 result manifest，不直接理解 ADS/HFSS 的私有文件格式。

## 当前可靠 HFSS 路线

当前七阶交指滤波器的 HFSS 主路线固定为：

- Backend：HFSS 3D Layout。
- Geometry：读取 SIM layout JSON，TOP/GND/FR4_CORE 三层。
- GND：`port-edges`，左右边界对齐 P1/P2 端口截面。
- Port：AEDT 原生 `create_edge_port()`，`is_circuit_port=False`。
- Port property：`HFSS Type=Gap`、`Orientation=Vertical`、`Reference=GND:GND:hfss_ground_plane`、`Renormalize=50ohm`。
- Sweep：默认 4-10 GHz / 40 points。
- Output：Touchstone、score CSV、trace CSV、S11/S21/S22 SVG。

pyEDB `edge-gap` 端口只保留为诊断路线，因为它可以写入 AEDB，但 AEDT 重新打开后求解不稳定。

## 模块职责

| 模块 | 职责 | 不应承担 |
|---|---|---|
| `common` | 命令计划、路径、manifest、通用错误类型 | ADS/HFSS API 细节 |
| `domain` | layout、port、stackup、sweep、result 的规范化数据结构 | 启动仿真器 |
| `ads` | ADS workspace、layout import、emSetup、RFPro FEM | 优化策略 |
| `hfss` | AEDT/HFSS 工程、stackup、端口、求解、导出 | 候选搜索策略 |
| `nn` | 数据集、特征、surrogate 训练/预测 | 直接操作 ADS/HFSS 工程 |
| `workflows` | ADS 并发、HFSS 抽检、NN 闭环、结果排名 | 低层 API 兼容补丁 |

## 核心 domain 模型

第一阶段只需要小而稳定的数据结构，不需要引入复杂框架。

```python
@dataclass(frozen=True)
class PortSpec:
    name: str
    number: int
    x_mm: float
    y_mm: float
    width_mm: float
    layer: str
    role: Literal["input", "output"]


@dataclass(frozen=True)
class StackupSpec:
    name: str
    er: float
    loss_tangent: float
    dielectric_height_mm: float
    copper_thickness_mm: float
    top_layer: str = "TOP"
    bottom_layer: str = "GND"


@dataclass(frozen=True)
class SweepSpec:
    start_ghz: float
    stop_ghz: float
    points: int
    sweep_type: str = "Interpolating"


@dataclass(frozen=True)
class ResultArtifact:
    s2p: Path
    score_csv: Path
    trace_csv: Path
    svg: Path | None
```

`LayoutSpec` 可以先保持 “SIM layout JSON dict + helper functions”，等 HFSS/ADS 两边都稳定后再升级成完整 dataclass。这样不会阻塞当前仿真迭代。

## Backend Adapter 接口

目标不是做过度抽象，而是把 ADS/HFSS 的共同生命周期统一：

```python
class SimulatorBackend(Protocol):
    name: str

    def build(self, plan: SimulationPlan) -> BuildResult:
        ...

    def solve(self, plan: SimulationPlan) -> SolveResult:
        ...

    def export(self, plan: SimulationPlan) -> ResultArtifact:
        ...
```

ADS backend 的实现：

- `build`: 导入 DXF/layout，克隆 emSetup。
- `solve`: 运行 RFPro/FEM。
- `export`: 输出 CSV，重建 summary，生成 SVG。

HFSS backend 的实现：

- `layout_io`: 读取 SIM layout JSON，解析配置化 layout id，生成版图摘要。
- `artifacts`: 从 layout id / stackup token / CLI 参数推导 AEDT、S2P、CSV、SVG 输出路径。
- `layout`: 把版图 JSON 转成 HFSS primitives，包含 GND 铜皮和信号/via 图形。
- `build`: 新建 AEDT/HFSS 3D Layout 工程，建 stackup、geometry、port、airbox/setup/sweep，并保存工程。
- `solve`: 执行 `analyze_setup()`，导出 Touchstone，并触发后处理。
- `results`: Touchstone -> score CSV -> trace CSV -> SVG。

现阶段可以不创建正式抽象基类，只先保持 plan/result manifest 字段一致。等 ADS/HFSS 都接入 workflow 后，再把 Protocol 固化。

## 工作流设计

### 1. 单候选裁决

```text
layout_json
  -> build HFSS reliable plan
  -> HFSS build-only optional check
  -> HFSS solve/export
  -> analyze S2P
  -> write result manifest
```

用于当前 `i7_fr4_r13_retest_base_l555_taper` 这类关键候选复核。

### 2. ADS 并发筛选 + HFSS 抽检

```text
candidate_plan.csv
  -> generate layout JSON/DXF
  -> ADS parallel RFPro quick solve
  -> rank by S21 primary score + weaker S11/S22 penalty
  -> select top N / uncertain N
  -> HFSS reliable route verdict
  -> update dataset and ranking
```

这里 HFSS 不需要跑所有候选，优先跑：

- ADS 排名前 3-5。
- ADS 与 surrogate 分歧大的候选。
- 结构变化大的候选。
- 即将作为 baseline/release 的候选。

### 3. NN 闭环

```text
ADS/HFSS result manifest
  -> build dataset
  -> train surrogate
  -> propose candidates
  -> ADS fast screen
  -> HFSS verdict on selected candidates
  -> append high-value labels
```

NN 不直接调用 ADS/HFSS。它只读统一 result manifest，输出候选参数或 layout mutation plan。

## Result Manifest

建议每次仿真输出一个 JSON manifest，字段统一：

```json
{
  "run_id": "hfss_i7_fr4_r13_aedt_edge_port_gnd_20260802",
  "backend": "hfss3dlayout",
  "route": "aedt_edge_port_gnd",
  "candidate": "i7_fr4_r13_retest_base_l555_taper",
  "layout": "...layout.json",
  "project": "...aedt",
  "sweep": {"start_ghz": 4.0, "stop_ghz": 10.0, "points": 40},
  "stackup": {"name": "FR4_210UM", "er": 4.6, "tanD": 0.02, "h_mm": 0.21},
  "ports": {"type": "aedt-edge", "hfss_type": "Gap", "gnd_boundary_mode": "port-edges"},
  "artifacts": {"s2p": "...", "score_csv": "...", "trace_csv": "...", "svg": "..."},
  "metrics": {"s21_5g_db": -20.38, "s21_8g_db": -9.64, "worst_s11_6_8_db": -6.78},
  "status": "TUNE"
}
```

后续 ADS 和 HFSS 的对比不再从散落的 CSV/SVG 路径中猜，而是聚合 manifest。

## 配置化命名约束

后续新增版图、层叠和仿真结果命名必须从配置派生，不再在脚本中继续写死 `fr4_210um`、`ro4350b_508um` 这类旧栈叠 token。

- 栈叠唯一来源：`config/stackups/<stackup_id>.json`。
- 项目默认栈叠入口：`config/projects/<project_id>.json` 的 `ads.stackup_config`。
- 生成器读取 `stackup_config.naming.token`，当前为 `jlc04161h_7628_1p6mm`。
- 新生成 layout id、DXF/SVG/params/layout JSON 文件名、默认 sweep 输出目录、HFSS 默认工程名和 S2P/SVG 输出名都应包含该 token。
- 已冻结 baseline 和历史结果不重命名；后续 NN/优化只能引用 baseline index，不能静默覆盖。
- 明确旧 token 可由 `stackup_config.naming.replace_tokens` 替换；没有明确匹配时追加 token，保留原候选语义。

## 日志和结果归属

日志、结果和中间文件按“生命周期”分类，而不是按 ADS/HFSS 代码模块分类。

| 类型 | 推荐位置 | 生命周期 | 说明 |
|---|---|---|---|
| 输入版图 | `projects/<project_id>/layouts/<sweep_id>/` | 长期保留 | layout JSON、DXF、参数 JSON。 |
| 仿真结果 | `projects/<project_id>/results/<run_id>/` | 长期保留 | S2P、score CSV、trace CSV、SVG、ranking CSV。 |
| 运行日志 | `projects/<project_id>/runs/<run_id>/logs/` | 中期保留 | stdout/stderr、AEDT/ADS wrapper log、耗时记录。 |
| 运行清单 | `projects/<project_id>/runs/<run_id>/manifest.json` | 长期保留 | 输入、backend、route、状态、artifact 路径、指标。 |
| 外部工程 | `D:\Work\ADS\...` 或 profile.workspace | 可重建，按需保留 | ADS workspace、AEDT project、AEDB、aedtresults。 |
| 临时缓存 | `projects/<project_id>/runs/<run_id>/tmp/` | 可删除 | 中间转换文件、临时脚本、锁文件副本。 |

关键原则：

- `src/simads/ads` 和 `src/simads/hfss` 不决定最终目录结构，只返回 artifact 路径和运行状态。
- `workflows` 决定 `run_id`，创建 `runs/<run_id>`，把 backend 输出登记到 manifest。
- `results/<run_id>` 保存可比较、可长期引用的数据；`runs/<run_id>/logs` 保存排查过程。
- 外部 ADS/HFSS 工程可以很大，不一定纳入 Git，但 manifest 必须记录其绝对路径、工程名、设计名和仿真 route。

建议 run_id 命名：

```text
<backend>_<project-short>_<candidate-or-sweep>_<route>_<YYYYMMDD_HHMMSS>

hfss_i7_fr4_r13_base_aedt_edge_port_gnd_20260802_1738
ads_i7_fr4_round13_retest_rfpro_fem_20260802_1430
nn_i7_fr4_surrogate_round12_h64b2_20260802_1015
```

当前已经生成的结果路径仍可保留：

```text
projects/bfp_6_8g_i7_fr4/results/hfss_verdict_i7_fr4_r13_aedt_edge_port_gnd/
```

后续新增 workflow 时，再同步生成：

```text
projects/bfp_6_8g_i7_fr4/runs/hfss_i7_fr4_r13_base_aedt_edge_port_gnd_20260802_1738/manifest.json
projects/bfp_6_8g_i7_fr4/runs/hfss_i7_fr4_r13_base_aedt_edge_port_gnd_20260802_1738/logs/run.log
```

## 目录迁移建议

当前已有 ADS 模块，HFSS 侧按同等粒度补齐：

```text
src/simads/hfss/
  __init__.py
  plans.py       # Hfss3dLayoutVerdictPlan / reliable route defaults
  layout_io.py   # SIM layout JSON 读取、layout id、摘要
  artifacts.py   # AEDT/S2P/CSV/SVG 默认命名和路径推导
  build.py       # stackup + geometry + ports + extents + setup/sweep + save
  solve.py       # analyze_setup + Touchstone export + post-process trigger
  workflow.py    # CLI 编排、manifest、异常处理、AEDT 生命周期
  layout.py      # layout JSON -> HFSS geometry primitives
  stackup.py     # materials/layers/extents
  ports.py       # aedt-edge 主路线 + pyEDB 诊断路线
  results.py     # s2p parse/score/trace/svg post-process helpers
```

迁移顺序要从低风险到高风险：

1. `plans.py`：先固定命令参数和可靠路线。
2. `layout_io.py` / `artifacts.py`：拆 JSON 读取、layout id、输出路径推导。
3. `results.py`：拆 Touchstone/CSV/SVG 后处理，容易测试。
4. `layout.py`：拆纯 geometry/GND 计算，dry-run 可验证。
5. `ports.py`：拆端口策略，必须用 build-only + AEDB 读回验证。
6. `build.py`：把 stackup、geometry、ports、setup/sweep/save 组成可独立调用的构建阶段。
7. `solve.py`：把 analyze/export/post-process 从 workflow 中移出。
8. `workflow.py`：最后只保留 CLI 编排、manifest、AEDT 生命周期和错误处理。

## 可靠路线与诊断路线

主路线只保留已验证可求解的组合：

```text
hfss3dlayout.reliable:
  port_type = aedt-edge
  gnd_boundary_mode = port-edges
  configure_extents = true
  start/stop/points = 4/10/40
  output = s2p + score + trace + svg
```

诊断路线不参与自动优化默认流程：

```text
hfss3dlayout.diagnostic.edge_gap_pyedb:
  用于研究 pyEDB create_edge_port_on_polygon
  当前 AEDT reopen/solve 不稳定

hfss3dlayout.diagnostic.wave:
  用于排查端口类型影响

hfss3dlayout.diagnostic.manual_saved:
  用于读取人工端口项目并导出结果
```

## 自动化流程边界

`workflows` 只处理策略，不写仿真器细节：

- 候选池如何产生。
- 哪些候选交给 ADS 快速筛。
- 哪些候选交给 HFSS 裁决。
- 如何合并 ADS/HFSS/NN 的结果。
- 何时扩大搜索半径，何时回到 baseline 附近。

`workflows` 不应该调用 `app.modeler.create_rectangle()` 或 ADS 私有 API；这些只能出现在 backend 模块。

## 近期落地计划

第一阶段，目标是稳定 HFSS 自动化主路线：

- [x] 把 HFSS 入口从 `tools` 迁到 `src/simads/hfss/workflow.py`。
- [x] 保留 `tools/hfss/run_hfss3dlayout_filter_verdict.py` 兼容入口。
- [x] 新增 `simads.hfss.plans`，把可靠路线参数固化为 plan。
- [x] 新增 `simads.hfss.layout_io`，承接 layout JSON 读取、layout id、摘要。
- [x] 新增 `simads.hfss.artifacts`，承接 AEDT/S2P/CSV/SVG 路径推导。
- [x] 新增 `simads.hfss.results`，承接 S2P/CSV/SVG/post-process。
- [x] 新增 `simads.hfss.layout`，承接 GND boundary、geometry creation。
- [x] 新增 `simads.hfss.ports`，承接 AEDT edge port 主路线和 pyEDB 诊断路线。
- [x] 新增 `simads.hfss.build`，承接独立 HFSS 工程/版图构建阶段。
- [x] 新增 `simads.hfss.solve`，承接 AEDT 求解、Touchstone 导出和后处理触发。
- [x] CLI 增加 `--route reliable`，自动展开为 `hfss3dlayout_aedt_edge_gap_gnd_port_edges`。

第二阶段，目标是统一 ADS/HFSS 结果：

- [ ] 定义 result manifest schema。
- [ ] ADS RFPro 输出 manifest。
- [ ] HFSS verdict 输出 manifest。
- [ ] 增加 `tools/workflows/compare_ads_hfss_verdict.py`。

第三阶段，目标是 NN 闭环：

- [ ] 从 manifest 构建训练集。
- [ ] surrogate 预测输出候选 plan。
- [ ] ADS 并发快速筛选。
- [ ] HFSS 抽检高价值候选。

## 演进待办

- [x] 把 HFSS 长脚本迁入 `src/simads/hfss/workflow.py`，`tools/hfss` 保留兼容 CLI。
- [x] 增加 `simads.common.CommandPlan`，给 ADS/HFSS/工作流统一命令计划形态。
- [x] 增加 `simads.hfss.plans`，固化当前可靠 HFSS verdict route。
- [ ] 增加 `simads.domain`：`LayoutSpec`、`PortSpec`、`StackupSpec`、`SweepSpec`、`SParamResult`。
- [x] 把 `workflow.py` 内的纯 layout/GND/port 推导移动到 `simads.hfss.layout`、`simads.hfss.layout_io`、`simads.hfss.artifacts` 和 `simads.hfss.ports`。
- [x] 把 `layout.py` 的 `argparse.Namespace` 入参收窄为显式 `GeometryBuildOptions`，进一步降低对 CLI 的耦合。
- [ ] 增加 `simads.workflows.hfss_verdict`，支持从候选 CSV 批量生成 HFSS verdict plan。
- [ ] 增加统一 result manifest，让 ADS RFPro 和 HFSS 的 score/trace/SVG 可直接比较。
