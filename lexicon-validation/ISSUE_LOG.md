# YLT Lexicon Issue Log

**Updated:** 2026-11-06  
**Repository:** `kitcosby/bible-project`  
**GitHub open issues at start:** 0

| Local ID | GitHub issue | Title | Severity | Classification | Status |
|---|---|---|---|---|---|
| YLT-GNT-001 | [#1](https://github.com/kitcosby/bible-project/issues/1) | TR parser drops pipe-delimited variant tokens before Greek alignment | High | Confirmed software/data alignment defect | Root cause traced to pipe-delimited Robinson TR source records skipped by parse_tr(); source token counts 24/21 vs stored 23/20; repair not started |
| YLT-GNT-002 | [#2](https://github.com/kitcosby/bible-project/issues/2) | SBL Greek lemma/gloss lookup fails across transliteration representations | High | Confirmed API/data integration defect | Reproduced by representation inspection; repair not started |
| YLT-GNT-003 | [#3](https://github.com/kitcosby/bible-project/issues/3) | Preserve Greek lexical provenance in PWA word detail | Medium | Confirmed frontend integration defect | API field exists; adapter drops it |
| YLT-GNT-004 | Pending | Verify G0 Strong's sentinel values in TR source | Medium | Suspected source-data anomaly | Requires source-level verification |
| YLT-MORPH-001 | Pending | Resolve or document unparsed Aramaic morphology segment | Low | Unresolved linguistic metadata | Raw value preserved; no guessed parse |
| YLT-DB-001 | [#4](https://github.com/kitcosby/bible-project/issues/4) | Add integrity constraints to Byzantine alignment bridge | Medium | Structural integrity risk | Initial duplicate/orphan checks clean; no DDL proposed |
| YLT-API-001 | Pending | Define and implement Greek variant YLT API coverage | Medium | Integration gap | Desired TR/Byzantine/SBL behavior requires design |

## Status vocabulary

- **Confirmed:** Reproducible defect supported by code/data evidence.
- **Suspected:** Anomaly requiring upstream/source verification.
- **Needs review:** Linguistic or product decision not safely inferable from current evidence.
- **Fixed:** Minimal change merged and regression tests pass.
- **Closed/documented:** Deliberately retained with documented reason and evidence.

Four actionable GitHub issues are open: [#1 positional bridge](https://github.com/kitcosby/bible-project/issues/1), [#2 SBL lemma/gloss lookup](https://github.com/kitcosby/bible-project/issues/2), [#3 PWA provenance](https://github.com/kitcosby/bible-project/issues/3), and [#4 Byzantine bridge integrity](https://github.com/kitcosby/bible-project/issues/4). An accidental duplicate issue #5 was closed as duplicate. The read-only validator now reports 3 out-of-range TR bridge rows and 3 orphan TR YLT renderings; Byzantine and Hebrew structural checks passed. No production repair has been applied. Backup/restore test completed locally; cloud sync and recovery metadata remain incomplete. Restored-snapshot validator output has an unresolved discrepancy with the independent table-count check.
