---
name: hku-med-ethics-toolkit
description: 從教育碩士研究計畫準備英繁簡三語 Word 同意書與 MEd Capstone 倫理申請草稿，核對導師電話、程序及附件一致性；不代替倫理審批。
---

# MEd ethics toolkit

Read [current rules](reference/current-med-rules.md) first. This derives from hku-consent-form; MEd independent/Capstone uses **FE54/926 Part A–C**, not the upstream general HREC Part A–E.

Read the proposal and instruments; extract [fields](reference/fields.md) with source locations. Unknown or conflicting facts stay TO CONFIRM. Do not assume minimal risk, retention, compensation, storage, spoken language from location, prior permission, or approval. Ask one combined set of necessary questions while preparing supported parts.

Determine Capstone versus dissertation. The bundled official-template filler supports Capstone only. For dissertation obtain its separate current template/checklist; do not rename FE54/926.

Choose the actual audiences: adult/teacher, principal school permission, parent permission, age-appropriate student assent. School studies need principal permission even if principals are not data sources. Consult checklist item 6 with the supervisor before selecting active/passive parental consent; never default to opt-out. School/parent permission does not override a child's refusal.

## One consistent pack

Unless otherwise requested generate **en, zh-Hant, zh-Hans**, separate Word files per audience. The upstream [English](reference/language-en.md) and [Chinese](reference/language-zh.md) banks are wording examples; **current rules and supplied facts override old defaults**. Do not copy staff-PI introductions, automatic minimal-risk/3-year-retention claims, absolute confidentiality, unlimited deletion promises, future reuse, or claims that parental permission is already obtained.

Write complete role-specific sections: purpose; procedures (duration, occasions, location, language, data and pilot/main scope); risks/mitigation; benefits; compensation; privacy/legal limits; storage/location/access; retention/destruction; voluntary participation, withdrawal/deletion method/cut-off; power safeguards; matching if any. Principal letters describe permitted school activities, parents read about their child, assent uses the child's reading level.

Recording choices must match actual audio/video plans, include review/erasure rights and what happens if declined. For classroom video explain exclusion from capture; later blurring alone does not prevent collection. Do not offer named reporting if the study promises de-identified reports.

**Hong Kong: every consent/permission/assent form includes the supervisor's name, email and readily reachable telephone. Confirm the owner/reachability; a student's number or faculty switchboard does not satisfy this check.**

## Generate

Create private study.json using the [schema](reference/fields.md) and [fictional example](examples/study.example.json). Supply source-backed section text in all three languages; the renderer does not translate or assess risk.

Run `python3 scripts/build_pack.py /private/path/study.json --out /private/path/new-draft`. The folder must be new. It outputs editable Word/Markdown, Part A field sheet, summary draft and attachment/checklist evidence tracker. Render all Word files with an available renderer, fix Chinese wrapping/page breaks, and make the summary actually one page. Report missing rendering capability honestly.

Optionally add `--official-template /private/path/FE54-926.docx`. Use a fresh blank official template, never an already signed application. Download the official .doc and save a DOCX copy in Word first. Filler checks version/labels, fills only Part A and inserts an explicit draft human-participants answer; it leaves declarations and all signatures untouched. Student manually confirms the official checkbox, declaration and layout. On template mismatch stop; do not guess fields.

Keep proposals/identities/generated packs outside the public repository. No upload, email, submission, signatures or sharing changes without the student's instruction.

## Handoff

Deliver three-language forms, Part A draft, one-page summary, English/original-language instruments and evidence/missing-item tracker for official FE33/226. Never auto-tick Done because a file exists. Record exact locations, unresolved decisions and reasons for N/A. A clean script report is not ethics approval or proof of readiness.

Route: student discussion/declaration → supervisor endorsement → designated reviewer → Office of Research. No project data collection/analysis before required approval; data collection starts **only after the Office of Research approval email**. Research pilots need approval; fictional classroom practice is not a research pilot permission.
