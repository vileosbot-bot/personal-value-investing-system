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

MSCI Hong Kong Net Total Return 不采用：官方页面有公开查询／下载入口，但 HKD 币种选项禁用、完整月度历史文件未实际取得，且官方使用条款限制自动化抓取。恒生价格指数加股息率自建序列也不采用，因为无法证明可免费完整复现官方 Gross TRI。

## 原始数据快照状态

- French APAC ex Japan 3 Factors 原始月度 CSV ZIP：NOT_RETRIEVED；SHA-256、实际首末月份、逐月缺失检查均为 null／待完成。
- FRED DEXHKUS 原始日频 CSV：NOT_RETRIEVED；SHA-256、实际首末日期、缺失观测及月末映射检查均为 null／待完成。
- 不得将未取得的数据标记 VERIFIED；Phase 1 新基准重算必须等原始快照封存并完成逐月检查后启动。
- 仅保存下载链接不构成快照。French 数据库历史值会修订，必须保存原始文件本体、获取日期和 SHA-256。

## 文档 SHA-256

- docs/validation-phase0-preregistration.md: 3ff883b6dae6db6252fd865abd312400ab8ea2d3665c61b8f3d619d741d61049
- docs/validation-data-contract.md: eae55d03d6e3306844048deb7b6f293f0903d879512f999cea83145ba5f7fb2f
- docs/validation-input-rules.md: 8d1a015e42878f347611193c33df4e876a80af98c64c12d91313fa8ee5ff9add
- Plan.md: de6d6e5093b1ae89b76b240ad72e4107c77f8c71b154a0a4dbc4cdc7ed2569c3
- docs/validation/trial-ledger-entry-v048.md: dc3573fa25fe34555361be663ea51b9dee2c8059bed9b5d34254575e77417645

- docs/validation/freeze-manifest-v048-2026-12-15.json: 3972b26ab140197225480c4e377a275a2a60f13b5990a765da7b64efb93327d3

## 冻结清单格式说明

未在 main@cc97e597、phase0-freeze-v047-2026-12-15 或 validation/phase0-refreeze-v047 分支文件树中找到 v0.4.7 JSON 清单。因此本版使用显式自描述 JSON 结构，不声称与未找到的 v0.4.7 文件逐字段相同；如总管持有该清单原件，后续应按原件 schema 复核。

## OTS

待总管确认；本轮未执行 OTS 锚定。
