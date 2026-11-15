# Phase 0 试验台账（v0.4.7）

本台账由 v0.4.5 新建，v0.4.6 续记，v0.4.7 续记；汇总截至 v0.4.7 的试验链；后续试验追加，不得删除旧行。事项与结果以仓库 Plan.md 验证轨记录为准；标'总管核对'的行由总管按裁决文件核对填入；仍标'待总管核对'的内容不作推断。本轮简报供数的四项直接填入；其他历史未决项不作推断。

| request-id | 日期 | 事项（一句话） | 结果（以 Plan.md 为准） |
|---|---|---|---|
| pvis-phase0-design-20261113-01 | 2026-11-13 | 建立 Phase 0 设计框架，固定四家公司、历史候选形成日及 V1.1 输入／数据契约规则 | Plan 记录设计框架与五项决定；尚未执行数据抓取、历史重算、回测、统计检验或模型估值 |
| pvis-phase0-revise-20261113-01 | 2026-11-13 | 按对抗评审 revise 裁决修订预注册、输入规则和数据契约 | Plan 仅将其列为设计节的修订请求，未单列验收结论；待总管核对 |
| pvis-review-verify-20261113-01 | 2026-11-13 | GPT 方法论全文复核 | verdict 有保留不通过（revise）；裁决见总管本地 gpt-review-pvis-review-20261113-01.md；以仓库 Plan.md 验证轨记录核对一致。
| pvis-phase0-revise2-20261114-01 | 2026-11-14 | 验证轨第二轮修订校正 | 文档校正后等待独立复核；冻结门槛记录为 BLOCKED；未运行回测、统计检验或估值，未实际注册、冻结或执行第三方时间戳 |
| pvis-phase0-monitor-20261114-01 | 2026-11-14 | 将 Phase 0 从确认性验证改为预注册监测与重大失败停止规则 | Plan 记录负责人批准监测定位变更；本轮未执行冻结或外部注册 |
| pvis-phase0-monitor-fix-20261114-01 | 2026-11-14 | 监测统计与数据质量 A–K 修订 | Plan 记录 verdict 为 proceed to independent review only；PR #6 当时 Open、未合并 |
| pvis-phase0-monitor-opus-20261114-01 | 2026-11-14 | Opus 第一轮挑刺监测稿 | verdict 有保留同意；总管逐条复算全部采纳（Bartlett(4) 总体目标仅 3.4σ²、t_19 不对应 HAC 统计量等）（总管核对） |
| pvis-phase0-monitor-fix-opus-20261114-01 | 2026-11-14 | Opus 第二次复核小修稿 | verdict 有保留同意；新发现 HH 去均值下偏、误差表应为非中心 t 等，总管全部采纳（总管核对） |
| pvis-phase0-monitor-fix2-20261114-01 | 2026-11-14 | 验证轨监测第二轮小修，更新统计口径、校准脚本及事件／NA 规则 | Plan 记录第二轮小修完成并等待独立复核；未实际冻结、注册或执行第三方时间戳 |
| pvis-phase0-freeze-opus-20261114-01 | 2026-11-14 | Opus 独立复核 v0.4.2 冻结包 | verdict 有保留同意；S-1/S-2/S-3 须以 v0.4.3 重新冻结解决（总管核对） |
| pvis-phase0-refreeze-v043-20261114-01 | 2026-11-14 | Phase 0 v0.4.3 文档层重新冻结 | Plan 记录该轮文档修订及 PR #8 创建时 Open、未合并；后续最终状态未在该节单列，待总管核对。PR #8 已于 2026-11-14 22:49:48 CST 合并（29eb7dd4）。 |
| pvis-phase0-refreeze-v043-opus-20261114-01 | 2026-11-14 | Opus 复核 v0.4.3 | verdict 有保留同意；S-1（文档层/数据层区分）须以 v0.4.4 解决（总管核对） |
| pvis-phase0-refreeze-v044-20261114-01 | 2026-11-14 | Phase 0 v0.4.4 文档层重新冻结 | Plan 记录版本修订、参数不变及执行边界；未在该节单列 PR #9 最终状态，待总管核对。PR #9 已于 2026-11-15 08:10:13 CST 合并（5a71143a）。 |
| pvis-phase0-refreeze-v044-opus-20261114-01 | 2026-11-15 | Opus 复核 v0.4.4 | verdict 有保留同意；S-候选-1/S-候选-2、M-1～M-10 须以 v0.4.5 解决（总管核对） |
| pvis-phase0-refreeze-v045-20261115-01 | 2026-11-15 | v0.4.5 执行 | PR #10 已合并（00cb9b1e）。
| pvis-phase0-refreeze-v045-opus-20261115-01 | 2026-11-15 | Opus 复核 v0.4.5 | verdict 不通过（revise）；裁决见总管本地 opus-adjudication-pvis-phase0-refreeze-v045-20261115-01.md。
| pvis-phase0-refreeze-v046-20261115-01 | 2026-11-15 | v0.4.6 执行 | PR #11，执行中。
| pvis-phase0-refreeze-v046-opus-20261115-01 | 2026-11-15 | Opus 复核 v0.4.6 | verdict 有保留同意；S-1/S-2 已修好，数字全部一致；M-1～M-6、L-1～L-12 见总管裁决 opus-adjudication-pvis-phase0-refreeze-v046-20261115-01.md；条件 1 为 OTS 证明（待确认），条件 2 为 M-1～M-4 进 v0.4.7。（总管核对）
