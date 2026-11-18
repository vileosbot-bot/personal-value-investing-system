# Phase 1 批 A 中期回报：A 区草稿落袋

- request-id：`pvis-phase1-execution-20261115-01`
- 分支：`validation/phase1-historical`
- 本次提交前分支 HEAD：`8a921077de58c736a21f01be02716698d7b57435`
- main 当前 HEAD：`98f4b0b5483c72b92977813005ae33bbcf49e2ac`（本步骤不把 main 合入本分支）
- 本文件只记录 A 区草稿状态；不包含 B 区实现回报，不生成组合排序或收益结论。

## 1. 九份草稿状态

本次使用远程工作目录 `deliverable/data/phase1/a-zone/` 下的原始草稿，并映射到仓库规定的 `docs/validation/phase1/a-zone/<年度>/<security_id>.json`。未使用后续 v2 目录中的副本；本步骤不计算招行信号。

| 公司 | 2016 | 2017 | 2018 |
|---|---|---|---|
| 贵州茅台（600519.SH） | NA：`NA_required_delta_nwc_input` | NA：同左 | NA：同左 |
| 比亚迪（002594.SZ） | NA：`NA_initial_growth_rule_failed` | NA：同左 | NA：同左 |
| 招商银行（600036.SH） | `READY_CORE_INPUTS` | NA：`NA_ERP_below_3pct` | `READY_CORE_INPUTS` |

- 茅台：原始年报中的“往来款”未能按冻结规则拆分，ΔNWC 不可分类，Owner Earnings 输入记 NA。
- 比亚迪：冻结规则要求五个有效正 NOPAT 同比增长观测；现有六年序列不足，不作平滑、截断或后续比较期替代，记 NA。
- 招行：2016、2018 仅表示核心模型输入已齐备；`valuation_outputs` 仍为 null，本步骤没有计算或提交招行估值／信号。2017 因 ERP 低于 3.00% 记 NA。

九份文件均标记 `status: DRAFT`，并保留两项已知缺陷：
1. `model_inputs.entry_price_rmb` 误用了下一交易日开盘价，须改为形成参考日收盘价。
2. `valuation_outputs` 仍为空（null），冻结 V1.1 估值输出与 `five_year_irr` 尚未生成。

## 2. 已取得的数据与来源记录

- 原始年度报告 PDF：23 份（茅台 8 份、比亚迪 7 份〔含 2010 年 HKEX 原始年报〕、招行 8 份）。
- 沪深 300 全收益指数 H00300：中证指数官方 `index-perf` 原始序列，3,325 条日记录，覆盖 2005-01-01 至 2018-08-31。
- CCDC：中债官方 10 年期国债收益率曲线历史页，覆盖 2005–2018。
- FX：CFETS HKD/CNY 来源规格与入口已登记（https://www.chinamoney.com.cn/english/bmkcpr/?tab=2），但来源清单明确标记本批 CNY 股票模型未使用，且未下载原始 FX 数据；错误响应文件不作为 FX 数据。

## 3. 待总管裁决／核对的来源不一致

### 招行 2013 年配股日期

两种日期说法均保留，不在本步骤选择：

- **2013-08-28**：现有批次记录中的 vendor-side action-date claim。工作文件 `market_inputs_batchA_final.json` 的 `companies.600036.rights_issue_event_note` 原文为：`2013-08 vendor action-date anomaly retained NA; official SSE ex-date 2013-09-05 also excluded`。该摘要没有附出底层 vendor event 原始行；本步骤不补造该记录。
- **2013-09-05**：CNINFO 原始公告 `CMB_2013_rights_issue_CNINFO.pdf`，公告 URL：https://static.cninfo.com.cn/finalpage/2013-08-28/63008058.PDF，SHA-256：`b09ea54ca08bca4ff24ee89345c4f091a4a97b1cc5d3711393e313f690336448`。第 3 页写明 2013-09-05（T+7）为发行成功时的“除权基准日”；同一公告将 2013-08-28 至 2013-09-03 列为配股缴款期。

本步骤仅并列保存两项记录，不判断哪一日期应作为除权日。

### 2017 队列 ERP 精度写法

现有工作记录出现 **1.3737%**、**1.3738%**、**1.373786%** 三种显示精度，均指向约 **1.373786%** 的同一 ERP 估计；底层原始值记录约为 `0.013737862451563942`（旧中间文件的末位存在浮点尾差）。无论采用哪种显示精度，均低于冻结的 3.00% 门槛，结论一致为 `NA_ERP_below_3pct`，不作抬高或替代。

## 4. 本步骤边界

本次只提交九份带 DRAFT 标记的 A 区 JSON 与本中期回报文件；不修正价格、不计算招行信号、不生成 top-2、不启动批 B、不同步 main、不创建 PR、不修改冻结参数或模型代码。
