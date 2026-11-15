# Phase 0 v0.4.8 冻结记录

- request-id: pvis-phase0-refreeze-v048-20261115-01
- repository: vileosbot-bot/personal-value-investing-system
- baseline: main@cc97e5978b440ab96159b1969f9cb25ac245b6b7
- branch: validation/phase0-refreeze-v048
- PR: #13 — https://github.com/vileosbot-bot/personal-value-investing-system/pull/13
- PR state: Open; merged=false; merge prohibited
- PR creation head: 3991b20c8502d24d485335b1718c20ea83ab78a0
- PR creation CI run: 197 (workflow ci, conclusion success; run id 43733249494; head 3991b20c8502d24d485335b1718c20ea83ab78a0)
- Latest verified PR CI at this record update: run 213 (workflow ci, conclusion success; run id 43734616335; head 6dd8e54333e94a02b22976fe1d17b4ac76e82ec0)
- owner authorization: 负责人于 2026-11-15 22:12 CST 授权更换基准并重冻；总管确认采用 Kenneth R. French Asia Pacific ex Japan 3 Factors（月度 Mkt-RF + RF）

## 基准与计算口径

港股主基准采用 French APAC ex Japan 3 Factors 月度市场组合。原始 Mkt-RF、RF 均为百分数，先按 R_m,USD=(Mkt-RF+RF)/100 恢复 USD 市场总收益，再按 DEXHKUS（HKD per USD）月末最后有效观测以 R_m,HKD=(1+R_m,USD)×(X_t/X_(t-1))-1 转换为 HKD。Beta 个股与市场回报同为 HKD；ERP 使用 HKD 市场总收益与原 HKD 月度无风险收益。French RF 仅用于恢复市场总收益，不替代 HKMA 10 年期 HKD Rf。

## 局限与可比性

新基准是包含澳大利亚、香港、新西兰和新加坡的区域市值加权市场代理，不是香港本地指数，不是恒生指数公司官方 Gross TRI 1006800，也不与其等价。Phase 1 历史队列 2016–2021 与 2027 前瞻队列统一使用新基准。v0.4.7 及以前 1006800 设计下的结果与本版结果不可直接比较。

MSCI Hong Kong Net Total Return 不采用：完整月度历史文件未实际取得；官方使用条款限制 AI Agent 自动化抓取。官方页面虽有查询／下载入口，但 HKD 序列本身未取得；Local 选项是否等于 HKD 未证实，因此不将该选项状态作为决定性理由。恒生价格指数加股息率自建序列也不采用，因为无法证明可免费完整复现官方 Gross TRI。

## 原始数据快照状态

- French APAC ex Japan 3 Factors 原始月度 CSV ZIP：NOT_RETRIEVED；SHA-256、实际首末月份、逐月缺失检查均为 null／待完成。
- FRED DEXHKUS 原始日频 CSV：RETRIEVED；获取时间 2026-11-16 00:49 CST（2026-11-15 16:49 UTC）；SHA-256 `1ca275bd1691abf6d4d3d4552719401d8684355ce5e14a78fdd22aee7c79f6d7`；11,961 行数据，首末日期 1981-01-02 至 2026-11-06，日期升序且无重复；空缺值日 456 天；2006-07 至 2021-08 共 182 个月的月末映射全部覆盖，无缺失，抽查 2006-07-31=7.7703、2006-08-31=7.7767、2021-08-31=7.7779。来源：FRED Max 全历史下载 https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXHKUS&cosd=1981-01-02&coed=2026-11-16。已由总管取得并验讫。
- DEXHKUS 快照已由总管取得并验讫；French APAC ex Japan 3 Factors 原始快照仍 NOT_RETRIEVED。Phase 1 新基准重算必须等 French 原始快照封存并完成逐月检查后启动。
- 仅保存下载链接不构成快照。French 数据库历史值会修订，必须保存原始文件本体、获取日期和 SHA-256。

## 文档 SHA-256

- docs/validation-phase0-preregistration.md: c90741b63ed4661a3b24c4d1d4ddfbd167c29327a5f96d1aa2e6af604e973370
- docs/validation-data-contract.md: faa11dc7f299cd56771e5f8e51c2e2b899d502aed3b1bde192a37b3f6fc0b407
- docs/validation-input-rules.md: 52d45dac518f7fcb977312e375df0810a9833f12d0c6e2f00a7807b74f4e1c6d
- Plan.md: a8687c33b511576b2c665bfb76fbc05efb702cac59a53b7908129ce44d66b7f6
- docs/validation/trial-ledger-entry-v048.md: af708f31964834383356ec867fcc7f75c0d2071477495c6718a1ab450517b1aa

- docs/validation/freeze-manifest-v048-2026-12-15.json: 2c2c89118329308b76ace4da7711e0d3826984e9955d00d9eb6470b688556ae4

## 冻结清单格式说明

未在 main@cc97e597、phase0-freeze-v047-2026-12-15 或 validation/phase0-refreeze-v047 分支文件树中找到 v0.4.7 JSON 清单。因此本版使用显式自描述 JSON 结构，不声称与未找到的 v0.4.7 文件逐字段相同；如总管持有该清单原件，后续应按原件 schema 复核。

## OTS

待总管确认；本轮未执行 OTS 锚定。


## 复核意见落实与文本澄清（Opus 有保留同意后，总管裁决）

### 1. Beta 回归措辞澄清

输入规则 §3.2 的 Beta prose 行补充说明：按下方既有 Beta 公式对超额收益 (R_i−r_f, R_m−r_f) 做 OLS。Beta 公式本身未改；数据契约 §11.3 原已明确构造超额收益，本次仅使输入规则 prose 与公式表达一致，不构成计算规则变更。

### 2. 无风险收益率单位澄清

输入规则 §3.2 与数据契约 §11.3 两处均补充：y_m 以小数表示（例如 4.00% 记为 0.04）；月有效收益公式保持原样。v0.4.7 已存在同式及同一单位歧义，本次属于单位澄清。Phase 1 在任一版本下均未执行计算，因此不存在违背既成计算做法的问题。

### 3. DEXHKUS 月末回溯边界

数据契约 §11.3 与输入规则 §3.2 增加 guardrail：若某月内无任何有效 DEXHKUS 观测（回溯会跨入上一个月），该月记 NA。此为缺失值边界处理，不改变既有窗口、参数或汇率公式。

### 4. French 月度文件解析及版本锁定

数据契约 §11.3 增加四项程序规则：只解析月度数据段并在首个空行或年度段标题处停止；哨兵值（例如 −99.99）按缺失处理；实际文件名不符预期时停止并转人工，不得自动替换；原始 ZIP 快照取得后以 SHA-256 锁定版本，后续官网历史修订不追溯、不覆盖已锁定快照。该规则明确解析与版本控制程序，不改变市场收益公式。

### 5. 事后更换基准的事实说明

冻结口径下的 Phase 1 计算从未在旧基准上执行。批 A 在 0/12 处 blocked，未产出任何 A 区 JSON；因此不存在基于 1006800 的冻结口径 Phase 1 结果可供查看。2021 队列此前确有一次 Phase 1 之前的探索性复演，揭示日为 2026-08-28；该复演口径与冻结方案不同，本方案结果日为 2026-08-31。故 2021 队列定为已知结果复核，必须按新方案重建，不得移植旧结果。2026-11-15 22:12 CST 更换基准决定的唯一理由，是 1006800 Gross TRI 免费完整历史不可得（已核实 blocked）；作出决定时尚未算出任何基于 French 的结果，且 French 原始文件至今未取得。

### 6. 既有文本与提交区间说明

- 6dd8e543 至 305e3cd1 区间共 20 个提交、5 个文件（Plan.md、预注册、冻结清单、冻结记录、台账行）。该区间改动仅涉及 CI 引用数字、文档 SHA-256 同步、DEXHKUS 快照字段及一处 note 的行为主体措辞。
- 数据契约与输入规则在该区间内字节未变，SHA-256 两端分别保持 eae55d03d6e3306844048deb7b6f293f0903d879512f999cea83145ba5f7fb2f 与 8d1a015e42878f347611193c33df4e876a80af98c64c12d91313fa8ee5ff9add。预注册在该区间仅修改版本表中的 CI 行，没有规则变化。
- “不以 60–119 个月降级值替代主输入”是 v0.4.7 原文，在 main@cc97e597 的输入规则 §3.2 中一字不差；不是 v0.4.8 新增规则。

### 7. 2021 队列与历史结果边界

2021 队列的 Phase 1 之前探索性复演仅作为已知结果提示，不作为冻结口径的计算结果、输入、参数或可移植证据。新方案须按本版数据契约、输入规则及队列定义重新构建；任何旧探索性结果均不得填入新队列结果。
