import psycopg2

c = psycopg2.connect(dbname="bible_greek_bridge_test_20261106",user="postgres",host="/tmp")
q = c.cursor()
q.execute("""select y.verse_id,gv.gnt_verse_id from public.ylt_verses y
join public.verses v using(verse_id) join public.gnt_books b on b.book_id=v.book_id
join public.gnt_verses gv on gv.book_id=v.book_id and gv.chapter=v.chapter and gv.verse=v.verse
where b.code='AC' and v.chapter=4 and v.verse=32""")
ylt_id,gnt_id=q.fetchone()
artifact="ACTS_4_32_DENSE_PHRASE_ALIGNMENT_CASE_20261107"

expected=[
 (1,2,"phrase_member","proposed","moderate","AC-4:32-genitive-multitude"),
 (3,2,"phrase_member","proposed","moderate","AC-4:32-genitive-multitude"),
 (4,6,"phrase_member","proposed","high","AC-4:32-articular-participle-believers"),
 (5,8,"phrase_member","proposed","moderate","AC-4:32-articular-participle-believers"),
 (7,10,"phrase_member","proposed","high","AC-4:32-heart-article"),
 (10,13,"phrase_member","proposed","high","AC-4:32-soul-article"),
 (18,28,"phrase_member","proposed","moderate","AC-4:32-things-he-had"),
 (20,20,"phrase_member","proposed","high","AC-4:32-was-saying"),
 (25,36,"phrase_member","proposed","high","AC-4:32-to-them"),
 (27,38,"phrase_member","proposed","moderate","AC-4:32-in-common"),
]
q.execute("""select gnt_position,ylt_word_pos,alignment_kind,review_status,confidence,alignment_group_id
from ylt_profile_shadow.ylt_greek_alignment
where alignment_profile_id=4 and sequence_profile_id=3 and source_artifact=%s
and review_status='proposed' order by gnt_position,ylt_word_pos""",(artifact,))
rows=q.fetchall()
assert rows==expected,(rows,expected)
assert len(rows)==10

# “Who” is a supplied relative marker for the substantival articular participle.
q.execute("""select gnt_verse_id,gnt_position,ylt_word_pos,alignment_kind,review_status,confidence
from ylt_profile_shadow.ylt_greek_alignment where source_artifact=%s
and source_record_key='ac4:32:y7:who-not-expressed'""",(artifact,))
assert q.fetchone()==(None,None,7,"unaligned_ylt","not_expressed","high")

# Preserve the candidate αὐτῷ→“he” as an overlap; do not replace legacy associations.
q.execute("""select gnt_position,ylt_word_pos,alignment_kind,review_status,confidence,legacy_greek_positions
from ylt_profile_shadow.ylt_greek_alignment
where source_record_key='ac4:32:g19:y27:he-legacy-overlap'""")
assert q.fetchone()==(19,27,"phrase_member","legacy_overlap_review","moderate",[17,18])

# Exact phrase-group inventory.
q.execute("""select alignment_group_id from ylt_profile_shadow.alignment_group
where left(alignment_group_id,8)='AC-4:32-' order by alignment_group_id""")
assert q.fetchall()==[
 ("AC-4:32-articular-participle-believers",),
 ("AC-4:32-genitive-multitude",),
 ("AC-4:32-heart-article",),
 ("AC-4:32-in-common",),
 ("AC-4:32-soul-article",),
 ("AC-4:32-things-he-had",),
 ("AC-4:32-to-them",),
 ("AC-4:32-was-saying",),
]

# The YLT branch selection for Robinson group 44:4 is unchanged.
q.execute("""select selected_branch,decision_status from ylt_profile_shadow.profile_variant_selection
where profile_id=3 and group_key='44:4'""")
assert q.fetchone()==("A","inherited_provisional")
q.execute("""select branch_a_normalized,branch_b_normalized from ylt_profile_shadow.textual_variant_group
where group_key='44:4'""")
assert q.fetchone()==("oude 3761 {CONJ-N}","oud 3761 {CONJ-N}")

# The one pending “who” token has an alignment-level not_expressed disposition.
q.execute("""select r.review_status,r.proposed_alignment_count,r.reason,t.legacy_gnt_positions
from ylt_profile_shadow.ylt_token_review r join ylt_profile_shadow.ylt_token t using(ylt_verse_id,ylt_word_pos)
where r.profile_id=4 and t.ylt_verse_id=%s and t.ylt_word_pos=7""",(ylt_id,))
row=q.fetchone()
assert row[0]=="pending_review" and row[1]==0 and "no separate Greek relative pronoun" in row[2] and row[3]==[]

# The dative possessor overlap is explicitly visible in both review layers.
q.execute("""select review_status,legacy_gnt_positions from ylt_profile_shadow.ylt_token_review r
join ylt_profile_shadow.ylt_token t using(ylt_verse_id,ylt_word_pos)
where r.profile_id=4 and t.ylt_verse_id=%s and t.ylt_word_pos=27""",(ylt_id,))
assert q.fetchone()==("legacy_overlap_review",[17,18])
q.execute("""select review_status,proposed_alignment_count,legacy_ylt_positions
from ylt_profile_shadow.gnt_token_review where profile_id=4 and sequence_profile_id=3
and gnt_verse_id=%s and gnt_position=19""",(gnt_id,))
assert q.fetchone()==("legacy_overlap_review",0,[30])

# Existing “was saying” and “to them” targets now have two phrase-member endpoints each.
q.execute("""select gnt_position,proposed_alignment_count from ylt_profile_shadow.gnt_token_review
where profile_id=4 and sequence_profile_id=3 and gnt_verse_id=%s and gnt_position in (20,25)
order by gnt_position""",(gnt_id,))
assert q.fetchall()==[(20,2),(25,2)]

# Production row counts and stored embeddings remain unchanged.
p=psycopg2.connect(dbname="bible",user="postgres",host="/tmp")
z=p.cursor()
prod={}
for table in ("gnt_words","gnt_ylt_renderings","ylt_verses","ylt_verses_embedding_store"):
 z.execute("select count(*) from public."+table);prod[table]=z.fetchone()[0]
z.execute("select count(*) from public.ylt_verses_embedding_store where embedding is not null")
prod["non_null_embeddings"]=z.fetchone()[0]
p.close()
assert prod=={"gnt_words":141009,"gnt_ylt_renderings":143227,"ylt_verses":31102,
              "ylt_verses_embedding_store":31102,"non_null_embeddings":31102},prod
c.close()
print("Acts 4:32 endpoint audit: PASS")
print("proposed phrase-member endpoints:",len(rows))
print("alignment-level not_expressed:",1,"(who)")
print("legacy overlap preserved:",1,"(he ← αὐτῷ candidate)")
print("variant group 44:4 selection preserved:",("A","inherited_provisional"))
print("production baseline unchanged:",prod)
