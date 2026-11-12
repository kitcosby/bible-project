import psycopg2

DB = "bible_greek_bridge_test_20261106"
c = psycopg2.connect(dbname=DB, user="postgres", host="/tmp")
q = c.cursor()

q.execute("""select y.verse_id, gv.gnt_verse_id
from public.ylt_verses y
join public.verses v using (verse_id)
join public.gnt_books b on b.book_id=v.book_id
join public.gnt_verses gv on gv.book_id=v.book_id and gv.chapter=v.chapter and gv.verse=v.verse
where b.code='RE' and v.chapter=7 and v.verse=2""")
ylt_id, greek_id = q.fetchone()
q.execute("""select gnt_verse_id from public.gnt_verses
where book_id=(select book_id from public.gnt_books where code='RE')
and chapter=7 and verse=3""")
greek_id_3 = q.fetchone()[0]

expected = [
    (5, 6, "content_word", "RE-7:2-going-up", ("66:8",)),
    (5, 7, "phrase_member", "RE-7:2-going-up", ("66:8",)),
    (7, 10, "content_word", "RE-7:2-rising-of-sun", ()),
    (8, 11, "phrase_member", "RE-7:2-rising-of-sun", ()),
    (8, 13, "phrase_member", "RE-7:2-rising-of-sun", ()),
    (14, 23, "phrase_member", "RE-7:2-he-did-cry", ()),
    (14, 24, "phrase_member", "RE-7:2-he-did-cry", ()),
    (16, 27, "phrase_member", "RE-7:2-with-a-great-voice", ()),
    (23, 39, "phrase_member", "RE-7:2-to-injure-land", ()),
    (25, 41, "phrase_member", "RE-7:2-to-injure-land", ()),
    (1, 45, "cross_verse", "RE-7:2-saying-crossverse", ()),
]
q.execute("""select gnt_verse_id, gnt_position, ylt_word_pos, alignment_kind,
review_status, alignment_group_id, variant_dependency_groups
from ylt_profile_shadow.ylt_greek_alignment
where alignment_profile_id=4 and sequence_profile_id=3
and source_artifact='REVELATION_7_2_DENSE_PHRASE_ALIGNMENT_CASE_20261107'
and review_status='proposed'
order by gnt_verse_id, gnt_position, ylt_word_pos""")
rows = q.fetchall()
actual = []
for gv, gp, yp, kind, status, group, deps in rows:
    if gv == greek_id:
        actual.append((gp, yp, kind, group, tuple(deps)))
    elif gv == greek_id_3:
        actual.append((gp, yp, kind, group, tuple(deps)))
    else:
        raise AssertionError(("unexpected Greek verse", gv))
assert actual == expected, (actual, expected)
assert len(rows) == 11

# The two YLT-only supplied articles remain explicit alignment-level non-expression.
q.execute("""select ylt_word_pos, alignment_kind, review_status, confidence
from ylt_profile_shadow.ylt_greek_alignment
where alignment_profile_id=4 and ylt_verse_id=%s
and source_artifact='REVELATION_7_2_DENSE_PHRASE_ALIGNMENT_CASE_20261107'
and review_status='not_expressed'
order by ylt_word_pos""", (ylt_id,))
assert q.fetchall() == [
    (9, "unaligned_ylt", "not_expressed", "moderate"),
    (15, "unaligned_ylt", "not_expressed", "moderate"),
]

# Preserve three legacy conflicts; do not overwrite the original associations.
q.execute("""select ylt_word_pos, alignment_kind, review_status
from ylt_profile_shadow.ylt_greek_alignment
where alignment_profile_id=4 and ylt_verse_id=%s
and source_artifact='REVELATION_7_2_DENSE_PHRASE_ALIGNMENT_CASE_20261107'
and review_status='legacy_overlap_review'
order by ylt_word_pos, alignment_kind""", (ylt_id,))
assert q.fetchall() == [
    (12, "unaligned_ylt", "legacy_overlap_review"),
    (25, "phrase_member", "legacy_overlap_review"),
    (26, "phrase_member", "legacy_overlap_review"),
]

# Only the "going up" phrase endpoints directly depend on group 66:8.
q.execute("""select count(*) from ylt_profile_shadow.ylt_greek_alignment
where alignment_profile_id=4 and ylt_verse_id=%s
and variant_dependency_groups @> '["66:8"]'::jsonb""", (ylt_id,))
assert q.fetchone()[0] == 2

# The cross-verse anchor is stable; the rest of Rev 7:3 is deliberately not materialized.
q.execute("""select position, surface, beta, strongs, morph, sequence_status
from ylt_profile_shadow.gnt_sequence_word
where sequence_profile_id=3 and gnt_verse_id=%s""", (greek_id_3,))
assert q.fetchall() == [
    (1, "λεγων", "legwn", "G3004", "V-PAP-NSM", "provisional_inherited")
]
q.execute("""select selected_branch, decision_status
from ylt_profile_shadow.profile_variant_selection
where profile_id=3 and group_key='66:9'""")
assert q.fetchone() == (None, "unresolved")

# Production baseline: read-only.
p = psycopg2.connect(dbname="bible", user="postgres", host="/tmp")
z = p.cursor()
production = {}
for table in ("gnt_words", "gnt_ylt_renderings", "ylt_verses", "ylt_verses_embedding_store"):
    z.execute("select count(*) from public." + table)
    production[table] = z.fetchone()[0]
z.execute("select count(*) from public.ylt_verses_embedding_store where embedding is not null")
production["non_null_embeddings"] = z.fetchone()[0]
p.close()
assert production == {
    "gnt_words": 141009,
    "gnt_ylt_renderings": 143227,
    "ylt_verses": 31102,
    "ylt_verses_embedding_store": 31102,
    "non_null_embeddings": 31102,
}, production

c.close()
print("Revelation 7:2 endpoint audit: PASS")
print("proposed endpoints:", len(rows), "(8 phrase-member + 2 content-word + 1 cross-verse)")
print("supplied YLT articles: 2 not_expressed")
print("legacy overlaps preserved: 3")
print("direct dependency rows for 66:8:", 2)
print("Revelation 7:3 anchor only; group 66:9 remains unresolved")
print("production baseline unchanged:", production)
