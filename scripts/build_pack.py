#!/usr/bin/env python3
"""Render source-backed draft content locally. Python 3 standard library only."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile

LANGS = ('en', 'zh-Hant', 'zh-Hans')
ROLES = ('adult', 'teacher', 'principal', 'parent', 'student')
INVALID_XML = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]')
SECTIONS = ('purpose', 'procedures', 'risks', 'benefits', 'compensation', 'privacy',
            'storage', 'retention', 'withdrawal', 'power_safeguards', 'matching')
LABELS = {
 'en': ['Purpose', 'Procedures', 'Risks and safeguards', 'Potential benefits', 'Compensation',
        'Privacy and confidentiality limits', 'Storage and access', 'Retention and destruction',
        'Voluntary participation and withdrawal', 'Power relationships and safeguards', 'Data matching',
        'Recording and choices', 'Research contacts', 'Reply slip'],
 'zh-Hant': ['研究目的', '研究程序', '風險與保障', '可能效益', '參與補償', '私隱與保密限制',
             '儲存與存取', '保存與銷毀', '自願參與及退出', '權力關係與保障', '資料配對',
             '錄製及選擇', '研究聯絡資料', '回條'],
 'zh-Hans': ['研究目的', '研究程序', '风险与保障', '可能效益', '参与补偿', '隐私与保密限制',
             '存储与访问', '保存与销毁', '自愿参与及退出', '权力关系与保障', '数据匹配',
             '录制及选择', '研究联系信息', '回执']}
ROLE_NAMES = {
 'en': dict(zip(ROLES, ['Adult consent', 'Teacher consent', 'Principal school permission', 'Parent or guardian permission', 'Student assent'])),
 'zh-Hant': dict(zip(ROLES, ['成人同意書', '教師同意書', '校長學校參與許可', '家長或監護人許可', '學生須知及同意書'])),
 'zh-Hans': dict(zip(ROLES, ['成人知情同意书', '教师知情同意书', '校长学校参与许可', '家长或监护人许可', '学生须知及同意书']))}

def value(x):
    return str(x).strip() if x is not None and str(x).strip() else '[TO CONFIRM]'

def xml_text(text):
    return escape(INVALID_XML.sub(' ', str(text)))

def object_value(x, name):
    if x is None:
        return {}
    if not isinstance(x, dict):
        raise ValueError(name + ' must be a JSON object or null')
    return x

def recording_modes(study, doc):
    return doc.get('recording_modes', study['recording_modes'])

def paragraphs(markdown):
    """Only headings/paragraphs are emitted; raw Markdown styling is not copied to Word."""
    result = []
    for block in markdown.split('\n\n'):
        block = block.strip()
        if not block:
            continue
        if block.startswith('# '):
            result.append(('Title', block[2:]))
        elif block.startswith('## '):
            result.append(('Heading1', block[3:]))
        else:
            result.extend(('Normal', line) for line in block.splitlines() if line)
    return result

def docx_bytes(markdown):
    ps = []
    for style, text in paragraphs(markdown):
        ps.append(f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t xml:space="preserve">{xml_text(text)}</w:t></w:r></w:p>')
    body = ''.join(ps) + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1000" w:right="1100" w:bottom="1000" w:left="1100"/></w:sectPr>'
    ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{ns}"><w:body>{body}</w:body></w:document>'
    styles = f'''<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="{ns}">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Microsoft JhengHei"/><w:sz w:val="23"/><w:color w:val="000000"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="100" w:line="300" w:lineRule="auto"/><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:after="220"/></w:pPr><w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="000000"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="160" w:after="80"/></w:pPr><w:rPr><w:b/><w:sz w:val="25"/><w:color w:val="000000"/></w:rPr></w:style></w:styles>'''
    import io
    out = io.BytesIO()
    with ZipFile(out, 'w', ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/_rels/document.xml.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr('word/document.xml', document)
        z.writestr('word/styles.xml', styles)
    return out.getvalue()

def check(study, base):
    errors = []
    if not isinstance(study, dict):
        raise ValueError('Study must be a JSON object')
    def check_text(x, path='study'):
        if isinstance(x, str) and INVALID_XML.search(x):
            errors.append(f'Non-XML control character in {path}; replaced with a space in Word drafts')
        elif isinstance(x, dict):
            for k, v in x.items(): check_text(v, path + '.' + k)
        elif isinstance(x, list):
            for i, v in enumerate(x): check_text(v, path + f'[{i}]')
    check_text(study)
    for name in ('student', 'supervisor', 'title', 'summary'):
        study[name] = object_value(study.get(name), name)
    for name in ('documents', 'instruments', 'checklist_evidence'):
        if study.get(name) is None: study[name] = []
        if not isinstance(study[name], list): raise ValueError(name + ' must be an array')
        for item in study[name]:
            if not isinstance(item, dict): raise ValueError(name + ' entries must be JSON objects')
    if study.get('schema') != 1:
        raise ValueError('Unsupported study schema; expected 1')
    if study.get('route') != 'capstone':
        raise ValueError('FE54/926 supports Capstone/independent projects only; use the separate dissertation route')
    for key in ('example', 'in_hong_kong', 'school_based', 'human_participants'):
        if type(study.get(key)) is not bool:
            raise ValueError(f'{key} must be an explicit JSON boolean')
    modes = study.get('recording_modes')
    if not isinstance(modes, list) or any(m not in ('audio', 'video') for m in modes) or len(set(modes)) != len(modes):
        raise ValueError('recording_modes must be an explicit list of unique audio/video entries, or []')
    if study['example']:
        errors.append('Teaching example; never use its fictional facts or contacts for recruitment')
    def required(obj, key, prefix=''):
        if not obj.get(key) or re.search(r'TO CONFIRM|待確認|待确认|\{\{|example\.invalid', str(obj.get(key)), re.I):
            errors.append(f'Missing/unconfirmed: {prefix}{key}')
    for role, keys in [('student', ('name', 'programme', 'university_number', 'email')), ('supervisor', ('name', 'email'))]:
        for key in keys:
            required(study.get(role, {}), key, role + '.')
    for lang in LANGS:
        required(study.get('title', {}), lang, 'title.')
        required(study.get('summary', {}), lang, 'summary.')
    dates = {}
    for key in ('start_date', 'end_date', 'prepared_date'):
        try:
            dates[key] = dt.date.fromisoformat(study[key])
        except (KeyError, TypeError, ValueError):
            errors.append(f'Missing/invalid ISO date: {key}')
    if dates.get('end_date', dt.date.max) < dates.get('start_date', dt.date.min):
        errors.append('Completion date is before commencement')
    if dates.get('start_date', dt.date.max) <= dt.date.today():
        errors.append('Commencement is not in the future; confirm project status and approval route')
    sup = study.get('supervisor', {})
    if study['in_hong_kong'] and study['human_participants']:
        required(sup, 'phone', 'supervisor.')
        if sup.get('phone_confirmed') is not True:
            errors.append('Confirm supervisor telephone owner and reachability (official item 18)')
        if sup.get('phone') and sup.get('phone') == study.get('student', {}).get('phone'):
            errors.append('Supervisor and student phone are identical; verify correct contact')
    docs = study.get('documents', [])
    if not isinstance(docs, list):
        raise ValueError('documents must be an array')
    for d in docs:
        if not isinstance(d, dict): raise ValueError('Each document must be a JSON object')
        d['texts'] = object_value(d.get('texts'), 'document.texts')
        d['reply_override'] = object_value(d.get('reply_override'), 'document.reply_override')
        for lang in LANGS:
            d['texts'][lang] = object_value(d['texts'].get(lang), 'document.texts.' + lang)
    roles = [d.get('audience') for d in docs]
    if len(set(roles)) != len(roles) or any(a not in ROLES for a in roles):
        raise ValueError('Each supported audience may appear once only')
    if study['human_participants'] and not docs:
        errors.append('Human-participant study needs applicable consent/permission documents')
    if not study['human_participants'] and docs:
        raise ValueError('No-human project cannot silently generate participant consent files; resolve study scope')
    if study['school_based'] and study['human_participants'] and 'principal' not in roles:
        errors.append('School-based study needs principal permission (official item 5)')
    for d in docs:
        role = d['audience']
        local_modes = recording_modes(study, d)
        if not isinstance(local_modes, list) or any(m not in modes for m in local_modes) or len(set(local_modes)) != len(local_modes):
            raise ValueError(f'{role}: recording_modes must be a unique subset of the study modes')
        if d.get('consent_mode') not in ('active', 'passive'):
            raise ValueError(f'{role}: explicitly choose active/passive consent mode')
        if d.get('consent_mode') == 'passive':
            if role != 'parent':
                raise ValueError('Passive mode supported for parent notices only, with a confirmed route')
            required(study, 'consent_route_decision')
            for lang in LANGS:
                required(d.get('reply_override', {}), lang, 'parent.reply_override.')
        if role == 'student':
            required(d, 'reading_level', 'student-assent.')
        for lang in LANGS:
            t = d.get('texts', {}).get(lang, {})
            for key in SECTIONS + (('recording_rights',) if local_modes else ()):
                required(t, key, role + '.' + lang + '.')
    if not study.get('source_map'):
        errors.append('Add source locations for extracted facts; translations alone are not evidence')
    for i in study.get('instruments', []):
        path = Path(i.get('path') or '')
        if not path.is_absolute():
            path = base / path
        if not i.get('path') or not path.is_file():
            errors.append('Missing instrument file: ' + str(i.get('name', 'unnamed')))
    if study['human_participants'] and not study.get('instruments'):
        errors.append('Confirm applicable interview/questionnaire attachments and English/original languages')
    seen = set()
    for item in study.get('checklist_evidence', []):
        n = item.get('item')
        if type(n) is not int or n not in range(1, 20) or n in seen:
            raise ValueError('Checklist evidence needs unique item numbers 1–19')
        seen.add(n)
        if item.get('status') not in ('to_check', 'evidence', 'not_applicable'):
            raise ValueError('Checklist status must be to_check/evidence/not_applicable; never automatic Done')
        if item['status'] == 'evidence' and not item.get('location'):
            errors.append(f'Checklist {n}: evidence location absent')
        if item['status'] == 'not_applicable' and not item.get('reason'):
            errors.append(f'Checklist {n}: N/A requires a reason')
    return errors

def common_contacts(study, lang):
    a, b = study.get('student', {}), study.get('supervisor', {})
    fields = [value(a.get('name')), value(a.get('programme')), value(a.get('email')),
              value(b.get('name')), value(b.get('email')), value(b.get('phone'))]
    if lang == 'en':
        return f'Student researcher: {fields[0]}; programme: {fields[1]}; email: {fields[2]}.\nSupervisor: {fields[3]}; email: {fields[4]}; telephone: {fields[5]}.\nParticipant rights: Human Research Ethics Committee, HKU; hrec@hku.hk; +852 3917 5267 (verify current contact before use).'
    if lang == 'zh-Hant':
        return f'學生研究者：{fields[0]}；課程：{fields[1]}；電郵：{fields[2]}。\n導師：{fields[3]}；電郵：{fields[4]}；電話：{fields[5]}。\n參與者權益：香港大學研究操守委員會；hrec@hku.hk；+852 3917 5267（使用前核對最新聯絡資料）。'
    return f'学生研究者：{fields[0]}；课程：{fields[1]}；电子邮箱：{fields[2]}。\n导师：{fields[3]}；电子邮箱：{fields[4]}；电话：{fields[5]}。\n参与者权益：香港大学研究操守委员会；hrec@hku.hk；+852 3917 5267（使用前核对最新联系信息）。'

def reply(study, doc, lang):
    override = doc.get('reply_override', {}).get(lang)
    if override:
        return override
    role = doc['audience']
    if lang == 'en':
        action = {'principal': 'allow my school to take part as described', 'parent': 'allow my child to take part as described'}.get(role, 'take part as described')
        lines = [f'Participation: [ ] I agree to {action}.   [ ] I do not agree.']
        for mode in recording_modes(study, doc) if role != 'principal' else []:
            lines.append(f'{mode.title()} recording: [ ] I agree.   [ ] I do not agree.')
        lines += ['Name: __________________   Signature: __________________   Date: __________']
        if role == 'principal': lines.append('School name: __________________   School chop: __________')
        if role == 'principal': lines.append('School permission does not replace individual participant consent or child assent.')
        if role == 'parent': lines.append('Child name: __________________')
    else:
        hant = lang == 'zh-Hant'
        action = {'principal': '本校參與上述研究' if hant else '本校参与上述研究', 'parent': '子弟參與上述研究' if hant else '孩子参与上述研究'}.get(role, '參與上述研究' if hant else '参与上述研究')
        lines = [f'[ ] 我同意{action}。   [ ] 我不同意。']
        for mode in recording_modes(study, doc) if role != 'principal' else []:
            label = ('錄音' if hant else '录音') if mode == 'audio' else ('錄影' if hant else '录像')
            lines.append(f'{label}：[ ] 我同意。   [ ] 我不同意。')
        lines.append('姓名：__________________   簽署：__________________   日期：__________' if hant else '姓名：__________________   签署：__________________   日期：__________')
        if role == 'principal': lines.append('學校名稱：__________________   校印：__________' if hant else '学校名称：__________________   校印：__________')
        if role == 'principal': lines.append('學校許可不代替個別參與者同意或學生本人的同意。' if hant else '学校许可不代替个别参与者同意或学生本人的同意。')
        if role == 'parent': lines.append('子弟姓名：__________________' if hant else '孩子姓名：__________________')
    return '\n'.join(lines)

def consent(study, doc, lang):
    title = ROLE_NAMES[lang][doc['audience']]
    notice = {'en': 'DRAFT — verify with your supervisor before use', 'zh-Hant': '草稿　使用前須與導師核對', 'zh-Hans': '草稿　使用前须与导师核对'}[lang]
    if study['example']:
        notice += ' | FICTIONAL TEACHING EXAMPLE / 虛構教學示例 / 虚构教学示例'
    parts = [f'# {title}', notice, value(study.get('title', {}).get(lang))]
    t = doc.get('texts', {}).get(lang, {})
    for n, key in enumerate(SECTIONS):
        parts += ['## ' + LABELS[lang][n], value(t.get(key))]
    if recording_modes(study, doc):
        parts += ['## ' + LABELS[lang][11], value(t.get('recording_rights'))]
    parts += ['## ' + LABELS[lang][12], common_contacts(study, lang),
              '## ' + LABELS[lang][13], reply(study, doc, lang)]
    refs = {'en': 'Ethics reference number: __________________\nApproval expiry (if applicable): __________________',
            'zh-Hant': '倫理審批參考編號：__________________\n批准有效期（如適用）：__________________',
            'zh-Hans': '伦理审批参考编号：__________________\n批准有效期（如适用）：__________________'}
    parts += [refs[lang], 'Prepared / 擬備日期 / 拟备日期: ' + value(study.get('prepared_date'))]
    return '\n\n'.join(parts) + '\n'

FIELDS = [('Name of student investigator:', 'student.name'), ('Programme:', 'student.programme'),
          ('U. No.:', 'student.university_number'), ('HKU email address:', 'student.email'),
          ('Name of supervisor:', 'supervisor.name'), ('Supervisor’s email address:', 'supervisor.email'),
          ('Project title:', 'title.en'), ('Expected commencement date of this project:', 'start_date'),
          ('Expected completion date of this project:', 'end_date'),
          ('Does your project involve human participants?', 'human_participants')]

def field(study, path):
    x = study
    for part in path.split('.'):
        x = x.get(part, {}) if isinstance(x, dict) else {}
    if path == 'human_participants':
        return 'Yes' if x is True else 'No' if x is False else '[TO CONFIRM]'
    return value(x if not isinstance(x, dict) else None)

def fill_official(template, study):
    """Only replace label text runs in Part A, keeping other OOXML parts unchanged."""
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with ZipFile(template) as z:
        original = z.read('word/document.xml')
        root = ET.fromstring(original)
        alltext = ''.join(root.itertext())
        if 'FE54/926' not in alltext or 'PART A' not in alltext or 'PART B' not in alltext or 'PART C' not in alltext:
            raise ValueError('Official template is not recognised as FE54/926 Part A–C')
        ps = root.findall('.//w:p', ns)
        start = next((i for i,p in enumerate(ps) if 'PART A' in ''.join(p.itertext())), None)
        end = next((i for i,p in enumerate(ps) if i > (start or 0) and 'Declaration:' in ''.join(p.itertext())), None)
        if start is None or end is None:
            raise ValueError('Cannot locate Part A field region; no output written')
        region = ps[start:end]
        additions = []
        for label, key in FIELDS:
            hits = [p for p in region if label in ''.join(t.text or '' for t in p.findall('.//w:t', ns))]
            if len(hits) != 1:
                raise ValueError('Expected exactly one Part A label: ' + label)
            additions.append((hits[0], label, field(study, key)))
        # Preserve every original namespace, attribute and other part byte-for-byte.
        # Locate each paragraph byte span using the original qualified prefix.
        xml = original.decode('utf-8')
        matches = list(re.finditer(r'<(?:\w+:)?p(?:\s[^>]*)?>[\s\S]*?</(?:\w+:)?p>', xml))
        para_by_text = {}
        for m in matches:
            try:
                # Compare with the already parsed paragraphs, avoiding reparsing namespaces.
                texts = re.findall(r'<(?:\w+:)?t(?:\s[^>]*)?>([\s\S]*?)</(?:\w+:)?t>', m.group())
                import html
                para_by_text.setdefault(''.join(html.unescape(t) for t in texts), []).append(m)
            except ValueError:
                continue
        edits = {}
        for p, label, answer in additions:
            ptext = ''.join(t.text or '' for t in p.findall('.//w:t', ns))
            candidates = para_by_text.get(ptext, [])
            if len(candidates) != 1:
                raise ValueError('Ambiguous template paragraph; fill manually: ' + label)
            m = candidates[0]
            fragment = edits.get(m.start(), m.group())
            close = re.search(r'</((?:\w+:)?p)>$', fragment).group(0)
            prefix_match = re.match(r'<((?:\w+:)?)p', fragment)
            prefix = prefix_match.group(1)
            run = f'<{prefix}r><{prefix}t xml:space="preserve"> [DRAFT {xml_text(label)} {xml_text(answer)}]</{prefix}t></{prefix}r>'
            edits[m.start()] = fragment[:-len(close)] + run + close
        for m in reversed(matches):
            if m.start() in edits:
                xml = xml[:m.start()] + edits[m.start()] + xml[m.end():]
        ET.fromstring(xml)
        import io
        result = io.BytesIO()
        with ZipFile(result, 'w', ZIP_DEFLATED) as out:
            for info in z.infolist():
                out.writestr(info, xml.encode('utf-8') if info.filename == 'word/document.xml' else z.read(info.filename))
        return result.getvalue()

def build(study_path, out, template=None):
    study = json.loads(study_path.read_text(encoding='utf-8'))
    errors = check(study, study_path.parent)
    official = fill_official(template, study) if template else None
    # Validate before any output is created; do not overwrite or merge versions.
    out.mkdir(parents=True, exist_ok=False)
    def write(stem, text):
        (out / (stem + '.md')).write_text(text, encoding='utf-8')
        (out / (stem + '.docx')).write_bytes(docx_bytes(text))
    for doc in study.get('documents', []):
        for lang in LANGS:
            write('consent-' + doc['audience'] + '-' + lang, consent(study, doc, lang))
    answers = '\n\n'.join(f'{i}. {label}\n{field(study, key)}' for i, (label, key) in enumerate(FIELDS, 1))
    write('application-part-a-draft', '# FE54/926 Part A draft\n\nDRAFT. Copy to the current official form; student checks the declaration and checkbox personally. All signatures remain blank.\n\n' + answers + '\n\nSupervisor endorsement and reviewer approval: NOT COMPLETED BY THIS TOOL.\n\nSubmit the full endorsed pack to Office of Research; data collection only after its approval email.\n')
    write('research-summary-draft', '# Research summary draft\n\n' + value(study.get('title', {}).get('en')) + '\n\n' + value(study.get('summary', {}).get('en')) + '\n\nDRAFT — render and verify that the research summary fits one page.\n')
    evidence = {i['item']:i for i in study.get('checklist_evidence', [])}
    tracker = '# Official checklist evidence tracker\n\nCompanion to FE33/226 amended, not a replacement form. No item is automatically marked Done. Verify actual content and justified N/A with the supervisor.\n\n'
    for n in range(1,20):
        i = evidence.get(n, {})
        tracker += f'## Item {n}\n\nStatus: {i.get("status", "to_check")}\nLocation: {value(i.get("location"))}\nReason / outstanding decision: {value(i.get("reason"))}\n\n'
    tracker += '## Instruments\n\n' + ('\n'.join(f'{i.get("name")}: {i.get("language")} — {i.get("path")}' for i in study.get('instruments', [])) or '[TO CONFIRM: applicable instruments]')
    write('checklist-evidence-tracker', tracker)
    if official:
        (out / 'FE54-926-filled-part-a-DRAFT.docx').write_bytes(official)
    report = {'status':'DRAFT_REQUIRES_HUMAN_REVIEW', 'issues':errors,
              'not_checked':['truth/source accuracy','cross-language meaning','ethical risk/consent route','Word page layout','one-page summary length','approval/submission'],
              'source_sha256':hashlib.sha256(study_path.read_bytes()).hexdigest(),
              'official_template_sha256':hashlib.sha256(template.read_bytes()).hexdigest() if template else None,
              'source_map':study.get('source_map', []), 'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    (out/'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (out/'READ-FIRST.txt').write_text('DRAFTS ONLY.\n' + '\n'.join(errors) + '\n\nCheck every language, official form, declaration and checklist with your supervisor. Never recruit or collect project data based on a generated pack. No email/submission/signatures are performed.\n', encoding='utf-8')
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('study', type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--official-template', type=Path)
    a = p.parse_args()
    try:
        report = build(a.study.resolve(), a.out.resolve(), a.official_template)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, BadZipFile) as e:
        p.exit(2, f'Cannot build draft pack: {e}\n')
    print(json.dumps({'output':str(a.out), 'status':report['status'], 'issues':len(report['issues'])}, ensure_ascii=False))

if __name__ == '__main__':
    main()
