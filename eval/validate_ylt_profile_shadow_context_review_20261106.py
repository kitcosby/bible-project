import psycopg2,json
c=psycopg2.connect(dbname='bible_greek_bridge_test_20261106',user='postgres',host='/tmp');q=c.cursor()
def count(t):
 q.execute('select count(*) from ylt_profile_shadow.'+t);return q.fetchone()[0]
tables={t:count(t) for t in ['profile','textual_variant_group','textual_variant_branch','profile_variant_selection','gnt_sequence_word','ylt_token','alignment_group','ylt_greek_alignment','ylt_token_review','gnt_token_review','witness_bundle','witness_bundle_member','gnt_word_analysis']}
assert tables=={'profile':4,'textual_variant_group':261,'textual_variant_branch':522,'profile_variant_selection':783,'gnt_sequence_word':2444,'ylt_token':3171,'alignment_group':30,'ylt_greek_alignment':598,'ylt_token_review':3171,'gnt_token_review':570,'witness_bundle':0,'witness_bundle_member':0,'gnt_word_analysis':0},tables
q.execute("select p.profile_code,s.decision_status,count(*) from ylt_profile_shadow.profile_variant_selection s join ylt_profile_shadow.profile p using(profile_id) group by 1,2")
selection={(a,b):n for a,b,n in q.fetchall()}
assert selection[('crosswire_kjv_candidate_sequence','algorithmically_selected')]==242
assert selection[('crosswire_kjv_candidate_sequence','unresolved')]==19
assert selection[('robinson_source_unselected','unreviewed')]==261
assert selection[('ylt_candidate_sequence','inherited_provisional')]==224
assert selection[('ylt_candidate_sequence','proposed')]==5
assert selection[('ylt_candidate_sequence','reviewed_against_translation')]==17
assert selection[('ylt_candidate_sequence','not_applicable_to_verse_alignment')]==14
assert selection[('ylt_candidate_sequence','unresolved')]==1
# Branch selections for all three proposed YLT variant cases.
q.execute("select g.source_group_id,s.selected_branch,s.decision_status from ylt_profile_shadow.profile_variant_selection s join ylt_profile_shadow.textual_variant_group g using(group_key) where s.profile_id=3 and ((g.book_id=(select book_id from public.gnt_books where code='MR') and g.source_group_id in (12,13)) or (g.book_id=(select book_id from public.gnt_books where code='2CO') and g.source_group_id in (4,5,7))) order by g.book_id,g.source_group_id")
branches=q.fetchall()
assert branches==[(12,'A','proposed'),(13,'B','proposed'),(4,'B','proposed'),(5,'B','proposed'),(7,'B','proposed')],branches
# Materialized YLT sequence exact tokens.
q.execute("select gb.code,gv.chapter,gv.verse,w.position,w.surface,w.strongs,w.morph,w.source_base_position,w.source_variant_groups from ylt_profile_shadow.gnt_sequence_word w join public.gnt_verses gv using(gnt_verse_id) join public.gnt_books gb using(book_id) where (gb.code='MR' and gv.chapter=8 and gv.verse=24 and w.position in (10,11)) or (gb.code='2CO' and ((gv.chapter=7 and gv.verse=12 and w.position in (20,23)) or (gv.chapter=11 and gv.verse=10 and w.position=11))) order by gb.code,gv.chapter,w.position")
seq=q.fetchall()
assert ('MR',8,24,10,'ορω','G3708','V-PAI-1S',None,['41:12','41:13']) in seq
assert ('MR',8,24,11,'περιπατουντας','G4043','V-PAP-APM',10,['41:12','41:13']) in seq
assert ('2CO',7,12,20,'ημων','G1473','P-1GP',20,['47:4']) in seq
assert ('2CO',7,12,23,'υμων','G4771','P-2GP',23,['47:5']) in seq
assert ('2CO',11,10,11,'φραγήσεται','G5420','V-2FPI-3S',11,['47:7']) in seq
# Mark 8:24 phrase and shifted walking.
q.execute("select a.ylt_word_pos,t.surface,a.gnt_position,g.surface,a.review_status,a.variant_dependency_groups from ylt_profile_shadow.ylt_greek_alignment a join ylt_profile_shadow.ylt_token t on t.ylt_verse_id=a.ylt_verse_id and t.ylt_word_pos=a.ylt_word_pos join ylt_profile_shadow.gnt_sequence_word g on g.sequence_profile_id=a.sequence_profile_id and g.gnt_verse_id=a.gnt_verse_id and g.position=a.gnt_position where a.source_record_key like 'MR8:%' order by a.ylt_word_pos")
mr=q.fetchall()
assert {(x[0],x[1],x[2],x[3]) for x in mr}=={(11,'I',10,'ορω'),(12,'see',10,'ορω'),(14,'walking',11,'περιπατουντας')}
assert all(x[4]=='proposed' and x[5]==['41:13'] for x in mr)
# 2 Corinthians 7:12 pronouns.
q.execute("select a.ylt_word_pos,t.surface,a.gnt_position,g.surface,a.variant_dependency_groups from ylt_profile_shadow.ylt_greek_alignment a join ylt_profile_shadow.ylt_token t on t.ylt_verse_id=a.ylt_verse_id and t.ylt_word_pos=a.ylt_word_pos join ylt_profile_shadow.gnt_sequence_word g on g.sequence_profile_id=a.sequence_profile_id and g.gnt_verse_id=a.gnt_verse_id and g.position=a.gnt_position where a.source_record_key='2CO712:our-to-hemon'")
our=q.fetchone();assert our[0:4]==(25,'our',20,'ημων') and our[4]==['47:4']
q.execute("select a.ylt_word_pos,t.surface,a.gnt_position,g.surface,a.variant_dependency_groups from ylt_profile_shadow.ylt_greek_alignment a join ylt_profile_shadow.ylt_token t on t.ylt_verse_id=a.ylt_verse_id and t.ylt_word_pos=a.ylt_word_pos join ylt_profile_shadow.gnt_sequence_word g on g.sequence_profile_id=a.sequence_profile_id and g.gnt_verse_id=a.gnt_verse_id and g.position=a.gnt_position where a.ylt_word_pos=28 and a.gnt_verse_id=(select gnt_verse_id from public.gnt_verses where book_id=(select book_id from public.gnt_books where code='2CO') and chapter=7 and verse=12)")
your=q.fetchone();assert your[0:4]==(28,'your',23,'υμων') and your[4]==['47:5']
# 2 Corinthians 11:10 “shall be stopped” phrase.
q.execute("select a.ylt_word_pos,t.surface,a.gnt_position,g.surface,a.variant_dependency_groups from ylt_profile_shadow.ylt_greek_alignment a join ylt_profile_shadow.ylt_token t on t.ylt_verse_id=a.ylt_verse_id and t.ylt_word_pos=a.ylt_word_pos join ylt_profile_shadow.gnt_sequence_word g on g.sequence_profile_id=a.sequence_profile_id and g.gnt_verse_id=a.gnt_verse_id and g.position=a.gnt_position where a.source_record_key like '2CO1110:%' order by a.ylt_word_pos")
stopped=q.fetchall()
assert [(x[0],x[1],x[2],x[3],x[4]) for x in stopped]==[(11,'shall',11,'φραγήσεται',['47:7']),(13,'be',11,'φραγήσεται',['47:7']),(14,'stopped',11,'φραγήσεται',['47:7'])]
# All alignment endpoints and profile references resolve.
assert count('ylt_greek_alignment')==598
q.execute("select count(*) from ylt_profile_shadow.ylt_greek_alignment where alignment_profile_id<>4 or sequence_profile_id<>3");assert q.fetchone()[0]==0
q.execute("select count(*) from ylt_profile_shadow.ylt_greek_alignment where review_status='proposed' and (ylt_verse_id is null or ylt_word_pos is null or gnt_verse_id is null or gnt_position is null)");assert q.fetchone()[0]==0
q.execute("select count(*) from ylt_profile_shadow.ylt_greek_alignment a left join ylt_profile_shadow.alignment_group g using(alignment_group_id) where a.alignment_group_id is not null and g.alignment_group_id is null");assert q.fetchone()[0]==0
q.execute("select review_status,count(*) from ylt_profile_shadow.ylt_greek_alignment group by 1 order by 1");align_status=q.fetchall()
assert align_status==[('legacy_overlap_review',3),('not_expressed',21),('proposed',563),('unresolved',11)]
q.execute("select review_status,count(*) from ylt_profile_shadow.ylt_token_review group by 1 order by 1");ylt_status=q.fetchall()
assert ylt_status==[('legacy_only',2112),('legacy_overlap_review',40),('pending_review',505),('proposed',514)]
q.execute("select review_status,count(*) from ylt_profile_shadow.gnt_token_review group by 1 order by 1");gnt_status=q.fetchall()
assert gnt_status==[('legacy_overlap_review',28),('pending_review',32),('proposed',510)]
q.execute("select source_kind,review_status,count(*) from ylt_profile_shadow.ylt_greek_alignment group by 1,2 order by 1,2");source_status=q.fetchall()
q.execute("select variant_dependency_groups,count(*) from ylt_profile_shadow.ylt_greek_alignment where variant_dependency_groups<>'[]'::jsonb group by 1 order by 1");deps=q.fetchall()

# Five additional YLT-profile variant sequences materialized after the 116-verse fixture.
sequence_specs=[('JOH',8,6,20,0,0,['43:6']),('AC',3,3,13,0,0,['44:3']),('RO',16,27,13,2,1,['45:7']),('EPH',6,24,14,0,0,['49:3']),('1JO',2,23,17,1,0,['62:3'])]
for code,ch,vs,ng,ny_unmapped,ng_unmapped,deps_expected in sequence_specs:
 q.execute("select gnt_verse_id,corpus_verse_id from public.gnt_verses where book_id=(select book_id from public.gnt_books where code=%s) and chapter=%s and verse=%s",(code,ch,vs))
 gid,cid=q.fetchone()
 q.execute("select position,surface,source_base_position,source_variant_groups,sequence_status from ylt_profile_shadow.gnt_sequence_word where sequence_profile_id=3 and gnt_verse_id=%s order by position",(gid,))
 words=q.fetchall()
 assert len(words)==ng and [x[0] for x in words]==list(range(1,ng+1)),(code,ch,vs,words)
 assert all(not x[1].startswith('[') and not x[1].endswith(']') for x in words),(code,ch,vs,'paratext present')
 assert all(x[3]==deps_expected for x in words),(code,ch,vs,'dependency mismatch')
 q.execute("select count(*) from ylt_profile_shadow.ylt_token where ylt_verse_id=%s",(cid,));assert q.fetchone()[0]==(27 if code=='JOH' else 18 if code=='AC' else 16 if code=='RO' else 12 if code=='EPH' else 22)
 q.execute("select count(*) from ylt_profile_shadow.ylt_token_review where profile_id=4 and ylt_verse_id=%s and review_status='pending_review'",(cid,));assert q.fetchone()[0]==ny_unmapped,(code,ch,vs,'YLT pending mismatch')
 q.execute("select count(*) from ylt_profile_shadow.gnt_token_review where profile_id=4 and sequence_profile_id=3 and gnt_verse_id=%s and review_status='pending_review'",(gid,));assert q.fetchone()[0]==ng_unmapped,(code,ch,vs,'Greek pending mismatch')
 q.execute("select count(*) from ylt_profile_shadow.ylt_greek_alignment where alignment_profile_id=4 and sequence_profile_id=3 and gnt_verse_id=%s and source_kind='variant_sequence_materialization' and review_status='pending_review'",(gid,));assert q.fetchone()[0]==0,(code,ch,vs,'stale alignment placeholder')
q.execute("select count(distinct gnt_verse_id) from ylt_profile_shadow.gnt_sequence_word where sequence_profile_id=3");assert q.fetchone()[0]==122
q.execute("select count(distinct ylt_verse_id) from ylt_profile_shadow.ylt_token");assert q.fetchone()[0]==121
# The eight-token 1 John 2:23 branch-B clause is the only inserted sequence segment.
q.execute("select position,surface,strongs,morph,source_base_position,source_variant_groups,sequence_status from ylt_profile_shadow.gnt_sequence_word where sequence_profile_id=3 and gnt_verse_id=(select gnt_verse_id from public.gnt_verses where book_id=(select book_id from public.gnt_books where code='1JO') and chapter=2 and verse=23) and position>=10 order by position")
added=q.fetchall()
assert [(x[0],x[1],x[2],x[3]) for x in added]==[(10,'ο','G3588','T-NSM'),(11,'ομολογων','G3670','V-PAP-NSM'),(12,'τον','G3588','T-ASM'),(13,'υιον','G5207','N-ASM'),(14,'και','G2532','CONJ'),(15,'τον','G3588','T-ASM'),(16,'πατερα','G3962','N-ASM'),(17,'εχει','G2192','V-PAI-3S')],added
assert all(x[4] is None and x[5]==['62:3'] and x[6]=='proposed_ylt_branch' for x in added),added
# The five selected groups are materialized; Revelation 7:3 remains unmaterialized.
for key,branch in [('43:6','A'),('44:3','A'),('45:7','A'),('49:3','A'),('62:3','B')]:
 q.execute("select selected_branch,decision_status from ylt_profile_shadow.profile_variant_selection where profile_id=3 and group_key=%s",(key,))
 assert q.fetchone()==(branch,'reviewed_against_translation'),key
q.execute("select count(*) from ylt_profile_shadow.gnt_sequence_word where sequence_profile_id=3 and gnt_verse_id=(select gnt_verse_id from public.gnt_verses where book_id=(select book_id from public.gnt_books where code='RE') and chapter=7 and verse=3)")
assert q.fetchone()[0]==0

# Contextual review of the five newly materialized verses.
q.execute("select review_status,count(*) from ylt_profile_shadow.ylt_greek_alignment where source_kind='variant_sequence_context_review' group by 1 order by 1")
context_status=q.fetchall()
assert context_status==[('legacy_overlap_review',3),('not_expressed',1),('proposed',42)],context_status
q.execute("select count(*) from ylt_profile_shadow.alignment_group where profile_id=4 and alignment_group_id in ('JOH-8:6-writing','AC-3:3-seeing','AC-3:3-begging','AC-3:3-kindness','AC-3:3-receive','RO-16:27-to-him','EPH-6:24-those-loving','EPH-6:24-undecayingly','1JO-2:23-denying','1JO-2:23-confessing','JOH-8:6-having-stooped','JOH-8:6-with-the-finger','RO-16:27-to-god','EPH-6:24-the-grace')")
assert q.fetchone()[0]==14
# Two Romans 16:27 targets remain explicit legacy-overlap cases, not overwritten.
q.execute("select t.surface,t.legacy_gnt_positions,r.review_status from ylt_profile_shadow.ylt_token t join ylt_profile_shadow.ylt_token_review r using(ylt_verse_id,ylt_word_pos) where t.ylt_verse_id=(select corpus_verse_id from public.gnt_verses where book_id=(select book_id from public.gnt_books where code='RO') and chapter=16 and verse=27) and t.ylt_word_pos in (9,14) order by t.ylt_word_pos")
assert q.fetchall()==[('to',[13],'legacy_overlap_review'),('the',[22,25],'legacy_overlap_review')]
# Supplemental phrase-member proposals and the additional Romans Amen overlap.
q.execute("select b.code,v.chapter,v.verse,a.ylt_word_pos,t.surface,a.gnt_position,g.surface,a.review_status,a.alignment_group_id from ylt_profile_shadow.ylt_greek_alignment a join public.gnt_verses v on v.gnt_verse_id=a.gnt_verse_id join public.gnt_books b on b.book_id=v.book_id join ylt_profile_shadow.ylt_token t on t.ylt_verse_id=a.ylt_verse_id and t.ylt_word_pos=a.ylt_word_pos join ylt_profile_shadow.gnt_sequence_word g on g.sequence_profile_id=a.sequence_profile_id and g.gnt_verse_id=a.gnt_verse_id and g.position=a.gnt_position where a.source_record_key in ('variant-context:JOH:8:6:g14:y16','variant-context:JOH:8:6:g15:y20','variant-context:RO:16:27:g3:y5','variant-context:RO:16:27:g13:y16','variant-context:EPH:6:24:g1:y1') order by b.code,v.chapter,v.verse,a.gnt_position")
assert q.fetchall()==[
 ('EPH',6,24,1,'The',1,'η','proposed','EPH-6:24-the-grace'),
 ('JOH',8,6,16,'having',14,'κυψας','proposed','JOH-8:6-having-stooped'),
 ('JOH',8,6,20,'the',15,'τω','proposed','JOH-8:6-with-the-finger'),
 ('RO',16,27,5,'God',3,'θεω','proposed','RO-16:27-to-god'),
 ('RO',16,27,16,'Amen',13,'αμην','legacy_overlap_review',None)]
# The third overlap is the reverse side of the Romans 16:27 “to”/ἀμήν legacy mismatch.
q.execute("select t.surface,t.legacy_gnt_positions,r.review_status from ylt_profile_shadow.ylt_token t join ylt_profile_shadow.ylt_token_review r using(ylt_verse_id,ylt_word_pos) where t.ylt_verse_id=(select corpus_verse_id from public.gnt_verses where book_id=(select book_id from public.gnt_books where code='RO') and chapter=16 and verse=27) and t.ylt_word_pos=16")
assert q.fetchone()==('Amen',[],'legacy_overlap_review')
# Three remaining pending YLT tokens are intentionally not force-linked.
q.execute("select b.code,v.chapter,v.verse,t.ylt_word_pos,t.surface from ylt_profile_shadow.ylt_token t join ylt_profile_shadow.ylt_token_review r using(ylt_verse_id,ylt_word_pos) join public.ylt_verses y on y.verse_id=t.ylt_verse_id join public.verses v using(verse_id) join public.gnt_books b on b.book_id=v.book_id where r.profile_id=4 and r.review_status='pending_review' and ((b.code='JOH' and v.chapter=8 and v.verse=6) or (b.code='RO' and v.chapter=16 and v.verse=27) or (b.code='EPH' and v.chapter=6 and v.verse=24) or (b.code='1JO' and v.chapter=2 and v.verse=23)) order by b.code,t.ylt_word_pos")
assert q.fetchall()==[('1JO',2,23,10,'he'),('RO',16,27,2,'the'),('RO',16,27,11,'be')]
# Five existing 1 John first-clause legacy associations are preserved unchanged.
q.execute("select ylt_word_pos,legacy_gnt_positions,review_status from ylt_profile_shadow.ylt_token t join ylt_profile_shadow.ylt_token_review r using(ylt_verse_id,ylt_word_pos) where t.ylt_verse_id=(select corpus_verse_id from public.gnt_verses where book_id=(select book_id from public.gnt_books where code='1JO') and chapter=2 and verse=23) and t.ylt_word_pos in (6,7,9,11,12) order by t.ylt_word_pos")
assert q.fetchall()==[(6,[4,5],'legacy_only'),(7,[4,5],'legacy_only'),(9,[9],'legacy_only'),(11,[7,8],'legacy_only'),(12,[7,8],'legacy_only')]
# Eight newly materialized YLT tokens remain pending rather than being force-linked.
q.execute("select b.code,v.chapter,v.verse,t.ylt_word_pos,t.surface from ylt_profile_shadow.ylt_token t join ylt_profile_shadow.ylt_token_review r using(ylt_verse_id,ylt_word_pos) join public.ylt_verses y on y.verse_id=t.ylt_verse_id join public.verses v using(verse_id) join public.gnt_books b on b.book_id=v.book_id where r.profile_id=4 and r.review_status='pending_review' and ((b.code='JOH' and v.chapter=8 and v.verse=6) or (b.code='RO' and v.chapter=16 and v.verse=27) or (b.code='EPH' and v.chapter=6 and v.verse=24) or (b.code='1JO' and v.chapter=2 and v.verse=23)) order by b.code,t.ylt_word_pos")
assert q.fetchall()==[('1JO',2,23,10,'he'),('RO',16,27,2,'the'),('RO',16,27,11,'be')]

c.close()
# Production read-only counts.
p=psycopg2.connect(dbname='bible',user='postgres',host='/tmp');z=p.cursor();prod={}
for t in ['gnt_words','gnt_ylt_renderings','ylt_verses','ylt_verses_embedding_store']:
 z.execute('select count(*) from public.'+t);prod[t]=z.fetchone()[0]
z.execute('select count(*) from public.ylt_verses_embedding_store where embedding is not null');prod['non_null_embeddings']=z.fetchone()[0]
p.close()
assert prod=={'gnt_words':141009,'gnt_ylt_renderings':143227,'ylt_verses':31102,'ylt_verses_embedding_store':31102,'non_null_embeddings':31102}
print('YLT PROFILE SHADOW FINAL VALIDATION PASS')
print('tables',tables)
print('branch selections',branches)
print('alignment statuses',align_status)
print('new verse context review statuses',context_status)
print('source/status',source_status)
print('YLT token statuses',ylt_status)
print('Greek token statuses',gnt_status)
print('dependency groups',deps)
print('production read-only counts',prod)
