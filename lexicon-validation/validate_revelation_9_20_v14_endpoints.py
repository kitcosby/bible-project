import psycopg2
c=psycopg2.connect(dbname='bible_greek_bridge_test_20261106',user='postgres',host='/tmp');q=c.cursor()
q.execute("""select gv.gnt_verse_id,y.verse_id,b.book_id from public.gnt_verses gv join public.gnt_books b using(book_id)
join public.verses v on v.book_id=b.book_id and v.chapter=gv.chapter and v.verse=gv.verse join public.ylt_verses y using(verse_id)
where b.code='RE' and gv.chapter=9 and gv.verse=20""")
gid,yid,bid=q.fetchone()
expected=[(14,14),(23,24),(23,26),(23,27),(28,32),(31,36),(32,37),(34,40),(35,41),(37,44),(38,45),(40,48),(44,55),(47,58),(49,61)]
for gp,yp in expected:
 q.execute("""select count(*) from ylt_profile_shadow.ylt_greek_alignment where alignment_profile_id=4 and sequence_profile_id=3
 and gnt_verse_id=%s and gnt_position=%s and ylt_verse_id=%s and ylt_word_pos=%s
 and alignment_kind='phrase_member' and review_status='proposed' and variant_dependency_groups='[]'::jsonb""",(gid,gp,yid,yp))
 n=q.fetchone()[0];assert n==1,(gp,yp,n)
print('phrase endpoints exact/unique/stable',len(expected))
q.execute("""select selected_branch,decision_status from ylt_profile_shadow.profile_variant_selection where profile_id=3 and group_key='66:18'""")
assert q.fetchone()==('A','proposed')
q.execute("""select surface,beta,strongs,morph,sequence_status from ylt_profile_shadow.gnt_sequence_word where sequence_profile_id=3 and gnt_verse_id=%s and position=13""",(gid,))
assert q.fetchone()==('ουτε','oute','G3777','CONJ-N','proposed_ylt_branch')
q.execute("""select count(*) from ylt_profile_shadow.ylt_greek_alignment where alignment_profile_id=4 and ylt_verse_id=%s and variant_dependency_groups @> '[\"66:18\"]'::jsonb""",(yid,))
assert q.fetchone()[0]==1
q.execute("""select count(*) from ylt_profile_shadow.ylt_greek_alignment where alignment_profile_id=4 and ylt_verse_id=%s and source_record_key='re9:20:y52:unaligned' and review_status='not_expressed'""",(yid,))
assert q.fetchone()[0]==1
print('branch A selection, sequence token, sole direct dependency, supplied copula: PASS')
q.execute("""select count(*) from public.gnt_ylt_renderings where gnt_verse_id=%s""",(gid,))
print('production legacy rendering rows at verse',q.fetchone()[0])
for t in ['gnt_words','gnt_ylt_renderings','ylt_verses','ylt_verses_embedding_store']:
 q.execute('select count(*) from public.'+t);print('production',t,q.fetchone()[0])
q.execute("select count(*) from public.ylt_verses_embedding_store where embedding is not null");print('non_null_embeddings',q.fetchone()[0])
c.close()