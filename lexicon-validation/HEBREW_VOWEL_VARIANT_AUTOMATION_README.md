# Hebrew vowel-variant review automation

## Purpose
Prepare repeatable, evidence-rich review queues for pending cross-root Hebrew/Aramaic vowel-only candidate groups.

## Safety boundary
- All database queries target only `bible_hebrew_variant_shadow_20261107`.
- All database sessions are read-only.
- No script changes production or shadow lexical data.
- No script approves semantic equivalence or merges roots, Strong’s IDs, morphology, or alignments.
- Review status changes are made only by the explicit batch-review step after evidence inspection.

## Current state
- 153 groups have member-level review notes (three initial three-root cases plus batches 1–10).
- 219 groups remain pending.
- Full context extraction currently covers all 249 pending groups and 1,459 verse occurrences.
- Remaining review queue: batches 11–24 (15 groups each), batch 25 (9 groups).

## Run the evidence preparation pipeline
From Windows PowerShell:
  wsl.exe -d lampy -e bash -lc 'runuser -u postgres -- python3 /mnt/c/Temp/build_pending_hebrew_review_packets.py && runuser -u postgres -- python3 /mnt/c/Temp/extract_all_remaining_hebrew_contexts.py && python3 /mnt/c/Temp/verify_remaining_hebrew_contexts.py'

## Inputs
- `C:\Temp\hebrew-crossroot-review-status-20261107.csv` — latest review index; synchronize from the GitHub working branch before starting a new run.
- `/tmp/hebrew-vowel-variants-20261107.summary.json` — inventory summary.
- PostgreSQL isolated shadow DB `bible_hebrew_variant_shadow_20261107`.

## Outputs
- `hebrew_crossroot_pending_evidence_20261107.jsonl` and `.md`: per-group root/Strong’s/morphology evidence.
- `hebrew_crossroot_remaining_contexts_20261107.jsonl`: all pending-group occurrence contexts, grouped by verse, with target words bracketed.
- `HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH<N>_REVIEW_20261107.md`: human review reports.

## Review procedure
1. Start with the next unreviewed batch in the evidence/context queue.
2. Inspect the Hebrew verse word sequences, member assignments, morphology, Strong’s, and any lexical-source references available.
3. Record observations and uncertainty. Do not infer equivalence from a shared consonantal signature.
4. Change only that batch's index rows to `reviewed_member_level` after inspection; do not use `approved`.
5. Regenerate pending evidence and contexts. Queue numbering is calculated from the highest completed batch number in the review CSV.
6. Commit the report and updated CSV to the working GitHub branch.

Member-level review is not exhaustive contextual lexicographic adjudication. Preserve ambiguous cases as pending or flag them for specialist review.
