# YLT Lexicon Issue Log

**Updated:** 2026-11-06  
**Repository:** `kitcosby/bible-project`  
**GitHub open issues at start:** 0

| Local ID | GitHub issue | Title | Severity | Classification | Status |
|---|---|---|---|---|---|
| YLT-GNT-001 | Pending | Greek TR/KJV positional bridge creates incorrect YLT mappings | High | Confirmed software/data alignment defect | Reproduced at John 9:21 and Colossians 4:10; repair not started |
| YLT-GNT-002 | Pending | SBL Greek lemma/gloss lookup fails across transliteration representations | High | Confirmed API/data integration defect | Reproduced by representation inspection; repair not started |
| YLT-GNT-003 | Pending | Preserve Greek lexical provenance in PWA word detail | Medium | Confirmed frontend integration defect | API field exists; adapter drops it |
| YLT-GNT-004 | Pending | Verify G0 Strong's sentinel values in TR source | Medium | Suspected source-data anomaly | Requires source-level verification |
| YLT-MORPH-001 | Pending | Resolve or document unparsed Aramaic morphology segment | Low | Unresolved linguistic metadata | Raw value preserved; no guessed parse |
| YLT-DB-001 | Pending | Add integrity constraints to Byzantine alignment bridge | Medium | Structural integrity risk | Initial duplicate/orphan checks clean; no DDL proposed |
| YLT-API-001 | Pending | Define and implement Greek variant YLT API coverage | Medium | Integration gap | Desired TR/Byzantine/SBL behavior requires design |

## Status vocabulary

- **Confirmed:** Reproducible defect supported by code/data evidence.
- **Suspected:** Anomaly requiring upstream/source verification.
- **Needs review:** Linguistic or product decision not safely inferable from current evidence.
- **Fixed:** Minimal change merged and regression tests pass.
- **Closed/documented:** Deliberately retained with documented reason and evidence.

No production repair has been applied. GitHub issue URLs are added after the issues are created.
