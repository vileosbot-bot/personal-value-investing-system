# 腾讯 2021 队列 A 区 JSON 独立复算报告

- request-id：trial-tencent2021-recalc-20261118
- 复算日期：2026-11-18
- 仓库：vileosbot-bot/personal-value-investing-system
- 基线分支：validation/phase1-historical
- 基线 HEAD：95b5b1f9986a0887086463e11074567a0f0ddaaf
- 目标文件：docs/validation/phase1/a-zone/2021/00700.HK.json
- 目标 JSON Blob SHA：52f6f5bc58d1eaee1b6e37779f85ad7998a4d6fb
- 目标状态：DRAFT（本报告不改变状态）

## 1. 复算方法

### 1.1 冻结函数与执行边界

- 前向估值使用基线 src/pvis/valuation.py 中的 growth_dcf，按默认 5 年稳定增长段、10 年总预测期计算经营价值、终值、内在价值及第五年退出价值。
- 五年 IRR 与目标入场价使用同文件中的冻结辅助函数 five_year_return_profile；它调用 src/pvis/finance.py 中冻结的 irr 与 target_entry_price。五年 IRR 的现金流为初始买入价、前五年模型现金流及第五年退出价值；目标入场价按辅助函数默认 15% 目标收益率折现。
- solve_growth_dcf_rate 只用于反向诊断：以 JSON 已记录的情景内在价值反求隐含初始增长率，不把反向结果当作前向复算值。
- value_driver_fcff 未调用：目标 JSON 的 route 为 dcf_sotp，腾讯对应的是 growth_dcf + SOTP 路线，不是价值驱动 FCFF 路线。
- 未修改、替换或重新拟合任何冻结模型函数；计算在临时隔离环境执行，仓库中没有模型代码改动。

函数与规则来源：
- src/pvis/valuation.py，Blob SHA 40864d006919a734402a6d633ded66cf9a74d5e5；growth_dcf 第 102 行起，value_driver_fcff 第 173 行起，five_year_return_profile 第 349 行起，solve_growth_dcf_rate 第 420 行起。
- src/pvis/finance.py，Blob SHA f64906a4df6f6493ca2aeec37fc25830d6a10c9b；irr 第 16 行起，target_entry_price 第 50 行起。
- docs/validation-input-rules.md，Blob SHA b6472c3088915074f3e1cd58da08676e19e7926f；Type 7 情景规则第 24–44 行，腾讯 DCF + SOTP 规则第 173–208 行，五年 IRR 口径第 386–398 行。

### 1.2 使用的 JSON 输入字段

基准情景直接使用目标 JSON 的 model_inputs：
- starting_core_fcff_per_share = 13.859691 HKD/股
- initial_growth = 0.535491
- wacc = 0.049435
- perpetual_growth = 0.029435
- non_operating_value_per_share = 74.9174 HKD/股
- entry_price_hkd = 485 HKD/股

目标队列为 2021，信息集截至最近完整财年 2020。WACC、永续增长率、SOTP 每股非经营性价值及基准现金流均按 JSON 已保存字段使用；本轮不重新估计 Beta、ERP、Ke、WACC 或 GDP。

### 1.3 三情景输入重建

JSON 未单独保存悲观、乐观情景的完整输入。按冻结输入规则，从 financial_series 的 2015–2020 六个连续年度水平值计算 2016–2020 五个同比增长率；FCFF 利润率按 2016–2020 五个完整年度计算。两组序列均排序后使用 Hyndman–Fan Type 7 线性插值分位数。

FCFF 同比增长率：
- 2016：0.599856251429
- 2017：0.535491117010
- 2018：-0.344220871624
- 2019：0.629040762523
- 2020：0.401329548850

FCFF / Revenue：
- 2016：0.322302518132
- 2017：0.316255888291
- 2018：0.157694103501
- 2019：0.212908407083
- 2020：0.233508413821

| 情景 | 增长率分位数 | FCFF 利润率分位数 | 起始 FCFF（HKD/股） |
|---|---:|---:|---:|
| 悲观 | 0.401329548850 | 0.212908407083 | 12.636995379 |
| 基准 | 0.535491（JSON 原值） | 0.233508413821 | 13.859691（JSON 原值） |
| 乐观 | 0.599856251429 | 0.316255888291 | 18.771096237 |

基准情景保留 JSON 中已存的基准输入；Q50 计算结果与其在所存精度下相符。悲观与乐观起始现金流按 Revenue_latest × Margin_s 计算，再除以最新稀释加权平均股数 9,650 百万股。

### 1.4 汇率与单位

- 财务序列原始单位为人民币百万元；FY2020 的 CFETS HKD/CNY 中间价为 0.84164 CNY/HKD。
- 按 JSON fx_conversion 约定，HKD = RMB / 0.84164，换算后的金额按 2 位小数保存。FY2020 收入为 572,767.45 HKD 百万元，FCFF 为 133,746.02 HKD 百万元。
- 每股现金流以 HKD 百万元除以稀释股数（百万股），得到 HKD/股；情景利润率作用于 FY2020 HKD 收入后再除以 9,650 百万股。
- SOTP 非经营性价值使用 JSON 已存的 74.9174 HKD/股；模型输出的内在价值、经营价值、终值、第五年退出价值及目标入场价均按 HKD/股理解。IRR 为小数比例，不是百分数数值。
- 差值定义为：复算值 − JSON 原值。

### 1.5 一致性判定口径

按各 JSON 数值字段实际保存的小数位数比较：估值金额字段按 6 位小数；IRR 字段按 JSON 自身精度（通常 6 位，乐观情景为 4 位）四舍五入后比较。表中同时保留未按字段精度截断的复算差值，以免把浮点残差隐藏为零。

## 2. 逐项核对表

| 估值字段 | JSON 原值 | 复算值 | 差值（复算−原值） | 一致性 |
|---|---:|---:|---:|---|
| valuation_outputs.intrinsic_value | 11510.050415 | 11510.058278 | +0.007863 | 不一致 |
| valuation_outputs.five_year_irr | 0.996441 | 0.996440378 | -0.000000622 | 不一致 |
| valuation_outputs.target_entry_price | 7294.748174 | 7294.745934 | -0.002240 | 不一致 |
| scenario_outputs.pessimistic.intrinsic_value | 5494.898661 | 5494.905578 | +0.006917 | 不一致 |
| scenario_outputs.pessimistic.operating_value | 5419.981261 | 5419.988178 | +0.006917 | 不一致 |
| scenario_outputs.pessimistic.terminal_value | 7821.373233 | 7821.367583 | -0.005650 | 不一致 |
| scenario_outputs.pessimistic.year_five_exit_value | 6765.869801 | 6765.871743 | +0.001942 | 不一致 |
| scenario_outputs.pessimistic.five_year_irr | 0.720053 | 0.720053149 | +0.000000149 | 一致（6 位小数） |
| scenario_outputs.baseline.intrinsic_value | 11510.050415 | 11510.058278 | +0.007863 | 不一致 |
| scenario_outputs.baseline.operating_value | 11435.133015 | 11435.140878 | +0.007863 | 不一致 |
| scenario_outputs.baseline.terminal_value | 16692.904473 | 16692.882374 | -0.022099 | 不一致 |
| scenario_outputs.baseline.year_five_exit_value | 14312.163952 | 14312.159551 | -0.004401 | 不一致 |
| scenario_outputs.baseline.five_year_irr | 0.996441 | 0.996440378 | -0.000000622 | 不一致 |
| scenario_outputs.optimistic.intrinsic_value | 20915.363492 | 20915.390290 | +0.026798 | 不一致 |
| scenario_outputs.optimistic.operating_value | 20840.446092 | 20840.472890 | +0.026798 | 不一致 |
| scenario_outputs.optimistic.terminal_value | 30553.240149 | 30553.218189 | -0.021960 | 不一致 |
| scenario_outputs.optimistic.year_five_exit_value | 26099.335371 | 26099.343005 | +0.007634 | 不一致 |
| scenario_outputs.optimistic.five_year_irr | 1.2552 | 1.255199989 | -0.000000011 | 一致（4 位小数） |

共核对 18 个数值字段：16 项在 JSON 保存精度下不一致，2 项一致。所有差值均为复算值减 JSON 原值。

## 3. 不符项清单

以下 16 项不一致：
1. valuation_outputs.intrinsic_value
2. valuation_outputs.five_year_irr
3. valuation_outputs.target_entry_price
4. scenario_outputs.pessimistic.intrinsic_value
5. scenario_outputs.pessimistic.operating_value
6. scenario_outputs.pessimistic.terminal_value
7. scenario_outputs.pessimistic.year_five_exit_value
8. scenario_outputs.baseline.intrinsic_value
9. scenario_outputs.baseline.operating_value
10. scenario_outputs.baseline.terminal_value
11. scenario_outputs.baseline.year_five_exit_value
12. scenario_outputs.baseline.five_year_irr
13. scenario_outputs.optimistic.intrinsic_value
14. scenario_outputs.optimistic.operating_value
15. scenario_outputs.optimistic.terminal_value
16. scenario_outputs.optimistic.year_five_exit_value

一致的两项为悲观情景五年 IRR（按 6 位小数）及乐观情景五年 IRR（按 4 位小数）。

## 4. 无法复算的项目与限制

- 18 个已保存估值输出字段均已执行前向复算；没有因缺少模型输入而完全无法计算的输出字段。
- 不能从当前 JSON 恢复生成原始估值时所有未四舍五入的上游输入。model_inputs 中起始现金流、增长率、WACC、永续增长率和 SOTP 每股价值均只保存有限小数位；市场序列、财务序列和换汇金额本身也按 JSON 载荷精度保存。因此无法仅凭当前载荷证明 16 项小差值究竟全部由上游精度截断造成，还是另有未记录的输入差异。
- solve_growth_dcf_rate 对 JSON 已记录情景内在价值反向求得的隐含初始增长率约为：悲观 0.401329297078、基准 0.535490853508、乐观 0.599855967652。与按 Type 7 规则重建的增长率差异分别约为 -0.000000252、-0.000000146、-0.000000284。这是反向诊断，不替代前向复算，也不能单独证明原始输出可复现。
- JSON 没有悲观、乐观情景的 target_entry_price 字段，因此不存在对应的原值可核对；本报告不新增或推测这些字段。
- 本轮没有重新下载或逐项审计年报原始文件、French 原始数据、DEXHKUS 原始快照或 HKMA 原始工作簿；使用的是目标 JSON 已封存的输入载荷及其规则说明。

## 5. 结论

该 JSON 的估值数字不能按当前载荷保存精度严格复现：18 项中 16 项不一致、2 项按字段精度一致；差值较小，但不能据此将整组估值标记为完全可复现。

历史队列中的估值和五年 IRR 是模型预测值，不代表实际赚到的收益。本报告不构成买卖建议，也不提供当前目标价。

## 交付与治理记录

1. **复用了什么：**目标 JSON Blob 52f6f5bc58d1eaee1b6e37779f85ad7998a4d6fb；冻结估值函数 growth_dcf、solve_growth_dcf_rate；冻结收益辅助函数 five_year_return_profile 及 finance.py 中的 irr、target_entry_price；冻结输入规则 docs/validation-input-rules.md。未使用其他估值方法。
2. **改动量：**0 代码、1 报告；本次只新增本 Markdown 文件。
3. **跳过／未检查：**其余五份腾讯 A 区 JSON 未读取；未重新审计原始外部数据及年报文件；未修改 main；最终核验时仅只读获取 main HEAD=98f4b0b5483c72b92977813005ae33bbcf49e2ac；未执行投资决策分析。
4. **风险：**JSON 输入精度不足以恢复全部生成时的未舍入参数，16 项差异的具体来源不能仅凭本载荷定因；所有六份腾讯 JSON 的状态不因本报告改变，目标 JSON 仍为 DRAFT，未标 VERIFIED。
5. **捷径账本：**未用替代估值模型或手工指定情景值；基准参数直接使用 JSON 保存值，悲观／乐观参数按冻结 Type 7 规则从已保存财务序列重建；WACC 与永续增长率未从原始外部数据重新估计，沿用 JSON 保存值；未改 JSON、模型、其他仓库文件，未开 PR、未合并。
