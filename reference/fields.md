# Study JSON

Start with examples/study.example.json (fictional; cannot recruit with it). Missing text stays TO CONFIRM and appears in checks. The renderer does not translate, assess risk or certify compliance.

Shared fields: schema=1; route="capstone"; example (boolean); in_hong_kong, school_based, human_participants (explicit booleans); recording_modes (explicit array of audio/video or []); student {name, programme, university_number, email, optional phone}; supervisor {name,email,phone,phone_confirmed}; title {en,zh-Hant,zh-Hans}; start_date,end_date,prepared_date (ISO); source_map [{field,source,location}].

summary: {en,zh-Hant,zh-Hans}. English is used for the application summary. Describe goal, proposed action, participants if relevant, ordered methods and safeguards; render to verify one page.

documents: list of {audience, consent_mode, texts}. Audiences adult/teacher/principal/parent/student. texts has en,zh-Hant,zh-Hans; each needs purpose,procedures,risks,benefits,compensation,privacy,storage,retention,withdrawal,power_safeguards,matching. Add recording_rights only if recording. Do not declare N/A without a reason from the study. Procedures include duration, occasions, language, location, data sources and pilot/main scope; all versions express identical facts.

consent_mode="active" unless a parent notice has a justified passive route. For passive parent notice provide source-backed consent_route_decision and per-language reply_override (actual deadline/contact/opt-out method). The script never chooses the parental route. For student assent set reading_level and use genuinely age-appropriate sections.

instruments: [{name,kind:"interview"|"questionnaire",language,path}] referring to private local files. checklist_evidence: [{item:1..19,status:"to_check"|"evidence"|"not_applicable",location,reason}]. Evidence means a location was recorded, not that the official item is Done. Human checks verify truth, language consistency and N/A. consent_route_decision records the source-backed audience/parental route and supervisor decisions still needed.

FE54/926 Part A fields 1–10: name, programme, university number, HKU email, supervisor name/email, project title, commencement/completion, human Yes/No. Optional filler writes these only; no declarations/signatures. No-human projects produce field sheet/summary/tracker without consent files; approval route still applies.

An audience may set recording_modes to an explicit subset of the shared modes (including []); use this when, for example, teachers are recorded but children are not. Principal permission does not replace separate individual recording consent.
