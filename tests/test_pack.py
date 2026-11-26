import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pack', ROOT/'scripts/build_pack.py')
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)

class PackTests(unittest.TestCase):
    def setUp(self):
        self.study = json.loads((ROOT/'examples/study.example.json').read_text())

    def test_supervisor_phone_is_never_replaced_with_student_phone(self):
        self.study['student']['phone'] = '+852 6000 0000'
        self.study['supervisor']['phone'] = ''
        issues = pack.check(self.study, ROOT/'examples')
        self.assertTrue(any('supervisor.phone' in e for e in issues))
        for lang in pack.LANGS:
            text = pack.consent(self.study, self.study['documents'][0], lang)
            self.assertNotIn('+852 6000 0000', text)
            self.assertIn('[TO CONFIRM]', text)

    def test_recording_choices_follow_each_audience(self):
        d = self.study['documents'][0]
        d['recording_modes'] = []
        text = pack.consent(self.study, d, 'en')
        self.assertNotIn('Audio recording: [ ]', text)
        d['recording_modes'] = ['video']
        with self.assertRaises(ValueError):
            pack.check(self.study, ROOT/'examples')

    def test_no_human_project_still_has_application_and_summary(self):
        self.study.update(human_participants=False, school_based=False, recording_modes=[], documents=[], instruments=[])
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'study.json'
            source.write_text(json.dumps(self.study))
            out = Path(tmp)/'pack'
            pack.build(source, out)
            self.assertTrue((out/'application-part-a-draft.docx').is_file())
            self.assertTrue((out/'research-summary-draft.docx').is_file())
            self.assertEqual(list(out.glob('consent*')), [])
            with self.assertRaises(FileExistsError):
                pack.build(source, out)

    def test_three_languages_are_editable_valid_ooxml(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'study.json'
            source.write_text(json.dumps(self.study))
            out = Path(tmp)/'pack'
            report = pack.build(source, out)
            self.assertNotEqual(report['status'], 'APPROVED')
            self.assertEqual(len(list(out.glob('consent-*.docx'))), 3)
            for p in out.glob('*.docx'):
                with ZipFile(p) as z:
                    self.assertIsNone(z.testzip())
                    for name in z.namelist():
                        if name.endswith('.xml') or name.endswith('.rels'):
                            ET.fromstring(z.read(name))

    def test_wrong_official_form_is_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'study.json'
            source.write_text(json.dumps(self.study))
            template = Path(tmp)/'not-fe54.docx'
            template.write_bytes(pack.docx_bytes('# Dissertation form\n\nOther route'))
            out = Path(tmp)/'pack'
            with self.assertRaises(ValueError):
                pack.build(source, out, template)
            self.assertFalse(out.exists())

    def test_official_declarations_and_other_parts_are_preserved(self):
        body = '# FE54/926\n\nPART A – TO BE COMPLETED BY THE STUDENT\n\n'
        body += '\n\n'.join(label for label, key in pack.FIELDS)
        body += '\n\nDeclaration: personally confirm this.\n\nSignature of Student Investigator\n\nPART B\n\nSignature of Supervisor\n\nPART C\n\nSignature of Reviewer\n'
        with tempfile.TemporaryDirectory() as tmp:
            template = Path(tmp)/'official.docx'
            template.write_bytes(pack.docx_bytes(body))
            import io
            filled = pack.fill_official(template, self.study)
            with ZipFile(template) as original, ZipFile(io.BytesIO(filled)) as output:
                for name in original.namelist():
                    if name != 'word/document.xml':
                        self.assertEqual(original.read(name), output.read(name))
                a = original.read('word/document.xml').decode()
                b = output.read('word/document.xml').decode()
                self.assertEqual(a[a.index('Declaration:'):], b[b.index('Declaration:'):])
                self.assertEqual(b.count('[DRAFT '), 10)

    def test_dissertation_and_ambiguous_boolean_are_rejected(self):
        self.study['route'] = 'dissertation'
        with self.assertRaises(ValueError): pack.check(self.study, ROOT/'examples')
        self.study['route'] = 'capstone'
        self.study['human_participants'] = 'false'
        with self.assertRaises(ValueError): pack.check(self.study, ROOT/'examples')

    def test_null_missing_objects_produce_missing_fields_not_traceback(self):
        self.study['student'] = None
        self.study['documents'][0]['texts']['en'] = None
        self.study['documents'][0]['reply_override'] = None
        self.study['instruments'][0]['path'] = None
        issues = pack.check(self.study, ROOT/'examples')
        self.assertTrue(any('student.name' in e for e in issues))
        self.assertTrue(any('teacher.en.purpose' in e for e in issues))
        self.assertTrue(any('Missing instrument file' in e for e in issues))
        self.assertIn('[TO CONFIRM]', pack.consent(self.study, self.study['documents'][0], 'en'))

    def test_xml_control_characters_cannot_break_word(self):
        import io
        self.study['title']['en'] = 'A\x00B'
        issues = pack.check(self.study, ROOT/'examples')
        self.assertTrue(any('control character' in e for e in issues))
        data = pack.docx_bytes('# Draft\n\nA\x00B\n\nC\x0bD')
        with ZipFile(io.BytesIO(data)) as z:
            xml = z.read('word/document.xml')
            ET.fromstring(xml)
            self.assertIn(b'A B', xml)

if __name__ == '__main__':
    unittest.main()
