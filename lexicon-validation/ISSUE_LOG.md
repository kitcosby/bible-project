# YLT Lexicon Issue Log

**Updated:** 2026-11-06  
**Repository:** `kitcosby/bible-project`  
**GitHub open issues at start:** 0

| Local ID | GitHub issue | Title | Severity | Classification | Status |
|---|---|---|---|---|---|
| YLT-GNT-001 | [#1](https://github.com/kitcosby/bible-project/issues/1) | TR parser drops pipe-delimited variant tokens before Greek alignment | High | Confirmed software/data alignment defect | Root cause traced to missing Robinson first/second variant parsing; 27 UTR files contain 431 pipe-marked lines; 41 shorthand pattern matches; John/Colossians undercounts confirmed; repair not started |
| YLT-GNT-002 | [#2](https://github.com/kitcosby/bible-project/issues/2) | SBL normalized word forms are incorrectly treated as LXX lexical lemmas | High | Confirmed API/data integration defect | Confirmed field-semantics mismatch in build_gnts_bridge.py; zero exact SBL/LXX matches; repair not started |
| YLT-GNT-003 | [#3](https://github.com/kitcosby/bible-project/issues/3) | Preserve Greek lexical provenance in PWA word detail | Medium | Confirmed frontend integration defect | API field exists; adapter drops it |
| YLT-GNT-004 | Pending | Verify G0 Strong's sentinel values in TR source | Medium | Suspected source-data anomaly | Requires source-level verification |
| YLT-MORPH-001 | Pending | Resolve or document unparsed Aramaic morphology segment | Low | Unresolved linguistic metadata | Raw value preserved; no guessed parse |
| YLT-DB-001 | [#4](https://github.com/kitcosby/bible-project/issues/4) | Add integrity constraints to Byzantine alignment bridge | Medium | Structural integrity risk | Initial duplicate/orphan checks clean; no DDL proposed |
| YLT-API-001 | [#6](https://github.com/kitcosby/bible-project/issues/6) | Define and expose existing Byzantine and SBL YLT bridge data through the API | Medium | Integration/design gap | Bridge tables exist; row counts, API behavior and intended witness support require verification |

## Status vocabulary

- **Confirmed:** Reproducible defect supported by code/data evidence.
- **Suspected:** Anomaly requiring upstream/source verification.
- **Needs review:** Linguistic or product decision not safely inferable from current evidence.
- **Fixed:** Minimal change merged and regression tests pass.
- **Closed/documented:** Deliberately retained with documented reason and evidence.

Five actionable GitHub issues are open: [#1 TR parser/positional bridge](https://github.com/kitcosby/bible-project/issues/1), [#2 SBL lexical lookup](https://github.com/kitcosby/bible-project/issues/2), [#3 PWA provenance](https://github.com/kitcosby/bible-project/issues/3), [#4 Byzantine bridge integrity](https://github.com/kitcosby/bible-project/issues/4), and [#6 Greek variant API integration](https://github.com/kitcosby/bible-project/issues/6). An accidental duplicate issue #5 was closed as duplicate. The read-only validator now reports 3 out-of-range TR bridge rows and 3 orphan TR YLT renderings; Byzantine and Hebrew structural checks passed. No production repair has been applied. Backup/restore test completed locally; cloud sync and recovery metadata remain incomplete. Restored-snapshot validator output has an unresolved discrepancy with the independent table-count check.


## 2026-11-06 update — Issue #1 (Greek positional alignment)

The root cause is now traced to unhandled Robinson pipe-delimited variant groups in the current parser. A source-driven per-group reconstruction passed the isolated test for resolved references: 99.90% lemma agreement and zero out-of-range positions. The known John 9:21 and Colossians 4:10 failures are corrected in the shadow sequence. Nineteen groups across 17 references remain unresolved, and ten legacy Colossians 4:18 mappings are colophon-only. Issue #1 remains open; no production migration has been made. Full evidence is in [ROBINSON_VARIANT_REBUILD_REPORT.md](ROBINSON_VARIANT_REBUILD_REPORT.md).


## 2026-11-06 update — YLT-specific profile and parser metrics

A new review found that existing YLT renderings inherit Greek positions through KJV word alignment. This is a provenance limitation, not proof that every existing row is wrong. The low-margin packet contains 3,076 YLT tokens: 2,101 mapped (68.3%), 975 without a Greek-position row, and 389 mapped tokens with multiple Greek positions. Added a separate YLT shadow profile with 15 proposed group selections; no branch was applied. Acts 26:18 and 2 John 1:5 proposals were withdrawn after closer syntax review; Acts 15:32 and 19:27 remain unresolved.

Parser equivalence now has corrected common-key counts: first variant 7,954/7,954 exact (plus empty Luke 17:36 key omitted by port), second variant 7,947/7,947 exact. Revelation 17:7–8 remains a documented exclusion. Production remains unchanged.


## 2026-11-06 update — Issue #9 (YLT-specific alignment provenance)

Opened [#9](https://github.com/kitcosby/bible-project/issues/9) to separate YLT-specific Greek alignment from the legacy KJV-mediated bridge. The current rendering path is YLT→KJV→Greek, so it is not independent evidence for YLT lexical or branch decisions. Initial low-margin audit: 3,076 YLT tokens, 2,101 mapped (68.3%), 975 without a Greek-position row, and 389 mapped tokens with multiple Greek positions. The new issue tracks an additive profile-aware design, explicit many-to-many mappings, and reason-coded unaligned tokens. Production remains unchanged.
