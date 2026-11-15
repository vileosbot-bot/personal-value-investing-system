# Phase 0 v0.4.8 台账行（待总管集成）

request-id: pvis-phase0-refreeze-v048-20261115-01  
date: 2026-11-15  
item: 香港市场基准替补重冻  
decision: 负责人于 2026-11-15 22:12 CST 授权更换基准；总管确认采用 Kenneth R. French Data Library Fama/French Asia Pacific ex Japan 3 Factors（月度 Mkt-RF + RF）作为港股市场代理  
result: 文档层规则更新已起草；MSCI Hong Kong Net TR 因 HKD 选项禁用、完整月度历史未取得及自动化抓取使用限制而不采用；恒生 1006800 Gross TRI 免费历史不可得，不再作为主基准  
new_rule: 市场总收益按 (Mkt-RF + RF)/100 恢复 USD；使用 DEXHKUS（HKD per USD）月末最后有效观测按 (1+R_USD,t)×(X_t/X_t-1)-1 转换为 HKD；Beta 个股与市场收益同为 HKD；ERP 使用 HKD 市场收益与原 HKD 10 年期 Rf  
scope: 同时适用于 Phase 1 2016–2021 历史队列和 2027 前瞻队列；Phase 1 需按新规则重算  
limitations: APAC ex Japan 是包含香港的区域市值加权市场代理，不是香港本地指数，不是恒生官方 Gross TRI 1006800，不与其等价；旧版 1006800 设计结果与新基准结果不可直接比较  
snapshot_status: NOT_RETRIEVED；French 原始 ZIP 与 DEXHKUS CSV 未取得，SHA-256、实际覆盖及逐月缺失检查待完成；不得标 VERIFIED  
pr: PR #13 https://github.com/vileosbot-bot/personal-value-investing-system/pull/13（Open；merged=false；只开 PR，不合并）  
ci: GitHub Actions run 213（run id 43734616335，workflow ci）success；验证提交 6dd8e54333e94a02b22976fe1d17b4ac76e82ec0  
next_action: Phase 1 新基准重算前保存两份原始文件快照、获取时间、SHA-256、起止月份／日期和缺失检查；总管合并时将本行集成进 trial-ledger.md

> 本文件仅提供单独台账行文本。按并发写入约束，本轮不直接修改 docs/validation/trial-ledger.md。
