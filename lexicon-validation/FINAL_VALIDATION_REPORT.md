# YLT Lexicon Final Validation Report

**Status:** NOT COMPLETE — initial discovery only  
**Report date:** 2026-11-06

## Readiness assessment

The current computed YLT lexicon is **not yet validated for release as a fully correct word-level lexicon**. The Hebrew path has an existing manual gold baseline and substantial computed coverage, but remains best-effort. The Greek path has confirmed positional alignment and SBL lookup defects.

## Completed

- Identified live PostgreSQL as the current authoritative store.
- Recorded selected table sizes and baseline counts.
- Identified Hebrew and Greek source/build paths.
- Traced the PWA and legacy Flask API consumption path.
- Reproduced two Greek positional alignment anomalies.
- Identified the SBL lemma representation mismatch and lost PWA provenance.
- Specified an initial representative validation dataset and safe repair gates.

## Not completed

- Current PostgreSQL backup verification and isolated restore test. (Blocking; not established.)
- Full table/constraint/FK inventory and data fingerprints.
- Source archive checksum and exact source-version pinning.
- Machine-executable Greek gold dataset.
- Full OT/NT alignment coverage analysis.
- Independent linguistic review of proposed expected word mappings.
- Repair implementation and regression run.
- Full PWA/API end-to-end validation after correction.

## Known limitations

- Computed YLT word associations are hypotheses derived from alignment, not publisher-provided interlinear data.
- LXX-derived glosses are not direct NT lexical definitions.
- Greek textual witnesses must remain separate.
- Some source/edition and morphology questions remain unresolved.

## Release recommendation

**Not ready for validated release.** Preserve the current production data, complete backup/restore verification, build executable regression tests on a snapshot, then repair the Greek positional bridge and SBL lookup in isolation. Do not regenerate the lexicon or modify production data as part of this phase.
