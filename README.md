# HKU MEd Ethics Toolkit

給教育碩士學生使用：提供研究計畫與訪談提綱／問卷，準備**英文、繁中、簡中 Word 同意書**、MEd Capstone 申請草稿、一頁研究摘要及缺件清單。

Prof. Lin 的教學用開源工具，改編自 [hku-consent-form](https://github.com/chinhsi/hku-consent-form)。研究決定由學生和導師確認；這不是 HKU 官方審批系統，不會上傳研究、寄信、代簽或提交。

## 最快開始

下載 ZIP 解壓，將資料夾及你的研究計畫／訪談提綱交給能讀檔與產 Word 的 AI 助理，貼上：

> 請讀 SKILL.md，依我的研究文件準備 MEd Capstone 倫理申請。先列有來源的資訊與矛盾／缺漏，不假設風險、保存期或已獲批准。我要英繁簡三語，每個適用對象各一份 Word；另要 FE54/926 Part A 草稿、一頁摘要及官方 checklist 的證據／缺件表。香港研究請核對導師可聯絡電話，不能用我的電話代替。最後交我和導師核對，不要代簽或寄出。

若聊天工具不能讀資料夾，可上傳 SKILL.md、reference/ 和研究文件；若不能產 Word，先要可複製的文件內容，不要把文字回覆當成已檢查的 Word。

## 看實際示範

以下皆為虛構教學示例，含待確認電話，不能用於招募：

- [英文 Word](examples/generated/consent-teacher-en.docx)
- [繁中 Word](examples/generated/consent-teacher-zh-Hant.docx)
- [簡中 Word](examples/generated/consent-teacher-zh-Hans.docx)
- [Part A 欄位草稿](examples/generated/application-part-a-draft.docx)與[一頁摘要](examples/generated/research-summary-draft.docx)

## 安裝為 skill

```bash
git clone https://github.com/chinhsi/hku-med-ethics-toolkit.git ~/.codex/skills/hku-med-ethics-toolkit
# Claude Code：目的地改為 ~/.claude/skills/hku-med-ethics-toolkit
```

不需付費 API。研究文件、聯絡資料和產出請放在 repo 外的私人資料夾。

## 產出

| 內容 | 支援 |
|---|---|
| 成人／教師、校長、家長、學生 assent | 按角色與年齡寫作；EN／繁中／簡中分檔 |
| Word 與 Markdown | AI 填 study.json；Python 3 標準函式庫批次產生 |
| FE54/926 Part A | 欄位草稿；有官方 DOCX 可填入草稿副本，簽署欄保持空白 |
| 一頁摘要 | 產生草稿，渲染後確認真的一頁 |
| 缺件與一致性 | 附件存在性、必要欄位、checklist 證據位置；不是自動批准 |

2026-11-26 更新：依官方 2026-10-30 版，Capstone 用 FE54/926＋FE33/226 amended。第18項要求香港 consent forms 提供**導師可聯絡電話**。Dissertation 有另一套表格。見 [來源與適用範圍](reference/current-med-rules.md)。

## 本機批次產生

由 AI 根據你的文件建立 study.json，格式參照 [欄位說明](reference/fields.md)。示例完全虛構，不能招募。

```bash
python3 scripts/build_pack.py examples/study.example.json --out /private/path/example-pack
python3 scripts/build_pack.py /private/path/study.json --out /private/path/new-draft
```

輸出資料夾須是新資料夾。僅用最新、未填寫及未簽署的官方樣板。官方 .doc 請在 Word 另存 DOCX 副本，再使用：

```bash
python3 scripts/build_pack.py /private/path/study.json --out /private/path/new-draft --official-template /private/path/FE54-926.docx
```

只填 Part A；Yes/No 插入標示為 draft 的答案，學生仍須核對官方 checkbox、聲明與版面。版本／標籤不符會停止。從 [官方頁面](https://web.edu.hku.hk/research/ethics-application) 下載表格；本 repo 不附官方表格。

## 送審前

核對三語事實、導師電話、程序與附件，移除示例與待確認文字。學生親讀及簽署自己的聲明，取得導師及 reviewer 簽署，再交 Office of Research。**收到 Office of Research 批准電郵後才可收集資料；研究 pilot 也需在批准範圍內。**

English: Drafts multilingual consent and MEd independent/Capstone application materials from a proposal. Does not determine ethical eligibility, replace institutional forms, sign, submit or approve. See SKILL.md and current source rules.

## Licence and provenance

MIT, derived from chinhsi/hku-consent-form at 5618a10f783aafafa4253e060139fd5cd2fb7823. Original copyright retained in LICENSE. Upstream language banks are examples whose old defaults are overridden by current MEd rules. Official HKU documents remain under their own terms and are linked rather than relicensed.
