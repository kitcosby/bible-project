#!/usr/bin/env python3
"""Independent read-only validator for the Hebrew variant shadow build."""
import collections
import json
import unicodedata
import psycopg2

SOURCE_DB = "bible"
SHADOW_DB = "bible_hebrew_variant_shadow_20261107"
SOURCE_SNAPSHOT_ID = "sha256:2ea0a1b12a4335d11393c1baddd1d0e0327f67f70059973f82f52c9bb557a540"
ALGORITHM_VERSION = "nfc-remove-u05b0-u05bb-u05c7-v1"
VOWEL_POINTS = set(range(0x05B0, 0x05BC)) | {0x05C7}
TABLES = ["words","root_vowel","lexicon","root_form","root_entry","word_variants","books","verses","morph_patterns"]

def signature(form):
    return "".join(ch for ch in form if ord(ch) not in VOWEL_POINTS)


def distinct_nfc_forms(forms):
    return {
        unicodedata.normalize("NFC", form)
        for form in forms
        if form is not None and form != ""
    }


def assert_min_two_distinct_pointed_forms(forms, group_id=None):
    distinct = distinct_nfc_forms(forms)
    if len(distinct) < 2:
        label = f" for group {group_id}" if group_id is not None else ""
        raise AssertionError(
            f"Expected at least two distinct NFC pointed forms{label}; found {len(distinct)}"
        )
    return distinct


def test_distinct_form_invariant():
    # Negative fixture: two different member keys that resolve to the same form
    # must not qualify as a vowel-only variant group.
    duplicate_form_fixture = ["בְּנֵיהֶם֙", "בְּנֵיהֶם֙"]
    try:
        assert_min_two_distinct_pointed_forms(duplicate_form_fixture, "negative-fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError("Negative distinct-form fixture was incorrectly accepted")

    # Positive fixture: the Ezekiel 27:32 candidate has two distinct NFC forms.
    positive_fixture = ["בְּנֵיהֶם֙", "בְּנִיהֶם֙"]
    if len(assert_min_two_distinct_pointed_forms(positive_fixture, "positive-fixture")) != 2:
        raise AssertionError("Positive distinct-form fixture did not retain two forms")

def scan_source(conn):
    groups=collections.defaultdict(lambda:{
        "forms":set(),"members":set(),"occurrences":0,"root_forms":set(),
        "strongs":set(),"morphologies":set()
    })
    member_languages=collections.defaultdict(set)
    total=0
    with conn.cursor(name="validator_source_scan") as cur:
        cur.itersize=5000
        cur.execute("""SELECT word_id,pointed,is_aramaic,root_id,root_form_seq,root_vowel_seq,
                              strongs,morph_pattern_id
                       FROM public.words ORDER BY word_id""")
        while True:
            batch=cur.fetchmany(5000)
            if not batch: break
            for word_id,raw,aramaic,root_id,form_seq,vowel_seq,strongs,morph_id in batch:
                total+=1
                if aramaic not in (0,1): raise AssertionError(f"Unexpected language flag on {word_id}")
                member_key=(root_id,form_seq,vowel_seq)
                member_languages[member_key].add(bool(aramaic))
                if raw is None or raw=="": continue
                normalized=unicodedata.normalize("NFC",raw)
                sig=signature(normalized)
                if not sig: continue
                g=groups[(bool(aramaic),sig)]
                g["forms"].add(normalized)
                g["members"].add(member_key)
                g["root_forms"].add((root_id,form_seq))
                g["occurrences"]+=1
                g["strongs"].add(strongs)
                g["morphologies"].add(morph_id)
    return total,{k:v for k,v in groups.items() if len(v["forms"])>=2},member_languages

def table_counts(conn):
    out={}
    with conn.cursor() as c:
        for table in TABLES:
            c.execute(f"SELECT count(*) FROM public.{table}")
            out[table]=c.fetchone()[0]
    return out

def main():
    test_distinct_form_invariant()
    src=psycopg2.connect(dbname=SOURCE_DB,user="postgres",host="127.0.0.1")
    sh=psycopg2.connect(dbname=SHADOW_DB,user="postgres",host="127.0.0.1")
    src.set_session(readonly=True,autocommit=False)
    sh.set_session(readonly=True,autocommit=False)
    try:
        scanned,expected,member_languages=scan_source(src)
        source_counts=table_counts(src)
        shadow_counts=table_counts(sh)
        if source_counts!=shadow_counts:
            raise AssertionError(f"Clone source-table counts differ: {source_counts} != {shadow_counts}")

        with sh.cursor() as c:
            c.execute("""SELECT variant_group_id,is_aramaic,non_vowel_signature,
                                algorithm_version,source_snapshot_id
                         FROM public.hebrew_vowel_variant_group""")
            actual_groups={}
            id_to_key={}
            for gid,language,sig,algorithm,snapshot in c.fetchall():
                key=(language,sig)
                if key in actual_groups: raise AssertionError(f"Duplicate group {key}")
                actual_groups[key]=gid
                id_to_key[gid]=key
                if algorithm!=ALGORITHM_VERSION or snapshot!=SOURCE_SNAPSHOT_ID:
                    raise AssertionError(f"Wrong algorithm/snapshot on group {gid}")
            if set(actual_groups)!=set(expected):
                raise AssertionError(f"Group set mismatch: expected {len(expected)}, actual {len(actual_groups)}")

            c.execute("""SELECT variant_group_id,is_aramaic,algorithm_version,source_snapshot_id,
                                root_id,root_form_seq,vowel_seq
                         FROM public.hebrew_vowel_variant_member""")
            actual_members=collections.defaultdict(set)
            for gid,language,algorithm,snapshot,r,f,v in c.fetchall():
                if gid not in id_to_key: raise AssertionError(f"Orphan group id {gid}")
                key=id_to_key[gid]
                if language!=key[0] or algorithm!=ALGORITHM_VERSION or snapshot!=SOURCE_SNAPSHOT_ID:
                    raise AssertionError(f"Member/group language or version mismatch: {gid}")
                actual_members[key].add((r,f,v))
            for key,g in expected.items():
                if actual_members[key]!=g["members"]:
                    raise AssertionError(f"Member mismatch for {key}: expected {len(g['members'])}, actual {len(actual_members[key])}")

            member_group_languages=collections.defaultdict(set)
            for (language,sig),members in actual_members.items():
                for member in members: member_group_languages[member].add(language)
            member_keys_in_both_candidate_populations=sum(len(v)>1 for v in member_group_languages.values())
            all_members=sorted({m for g in expected.values() for m in g["members"]})
            c.execute("""SELECT root_id,root_form_seq,vowel_seq,vowel_pattern
                         FROM public.root_vowel
                         WHERE (root_id,root_form_seq,vowel_seq) IN %s""",(tuple(all_members),))
            rv={(r,f,v):pattern for r,f,v,pattern in c.fetchall()}
            if set(rv)!=set(all_members): raise AssertionError("Missing root_vowel member")

            # Assert the invariant against the actual shadow membership, not
            # merely against the independently reconstructed source candidate set.
            c.execute("""SELECT m.variant_group_id,rv.vowel_pattern
                         FROM public.hebrew_vowel_variant_member m
                         JOIN public.root_vowel rv
                           ON (rv.root_id,rv.root_form_seq,rv.vowel_seq)=
                              (m.root_id,m.root_form_seq,m.vowel_seq)
                         ORDER BY m.variant_group_id""")
            forms_by_group=collections.defaultdict(list)
            for gid,pointed_form in c.fetchall():
                forms_by_group[gid].append(pointed_form)
            if set(forms_by_group)!=set(id_to_key):
                raise AssertionError("Distinct-form check did not cover every shadow group")
            distinct_form_sets={
                gid:assert_min_two_distinct_pointed_forms(forms,gid)
                for gid,forms in forms_by_group.items()
            }
            distinct_form_counts=[len(forms) for forms in distinct_form_sets.values()]
            minimum_distinct_nfc_forms=min(distinct_form_counts)
            maximum_distinct_nfc_forms=max(distinct_form_counts)

            c.execute("""SELECT root_id,root_form_seq,vowel_seq FROM public.lexicon
                         WHERE (root_id,root_form_seq,vowel_seq) IN %s""",(tuple(all_members),))
            lex=set(c.fetchall())
            if lex!=set(all_members): raise AssertionError("Missing lexicon member")
            for key,g in expected.items():
                for member in g["members"]:
                    if signature(unicodedata.normalize("NFC",rv[member]))!=key[1]:
                        raise AssertionError(f"Stored root_vowel signature mismatch: {member}")

            group_count=len(expected)
            member_count=sum(len(g["members"]) for g in expected.values())
            occurrence_count=sum(g["occurrences"] for g in expected.values())
            cross_root=sum(len(g["root_forms"])>1 for g in expected.values())
            multiple_strongs=sum(len({x for x in g["strongs"] if x is not None})>1 for g in expected.values() if len(g["root_forms"])>1)
            multiple_morphology=sum(len({x for x in g["morphologies"] if x is not None})>1 for g in expected.values() if len(g["root_forms"])>1)
            cross_root_member_keys={m for g in expected.values() if len(g["root_forms"])>1 for m in g["members"]}
            shared_language_keys=sum(len(member_languages.get(m,set()))>1 for m in cross_root_member_keys)

            if (group_count,member_count,occurrence_count,cross_root)!=(3349,7148,32676,372):
                raise AssertionError("Expected snapshot inventory counts changed")
            if (multiple_strongs,multiple_morphology,shared_language_keys,member_keys_in_both_candidate_populations)!=(185,370,8,3):
                raise AssertionError(f"Language-scoped divergence mismatch: {multiple_strongs}, {multiple_morphology}, {shared_language_keys}")

            c.execute("""SELECT count(*) FROM public.word_variants
                         WHERE variant_type='qere' AND witness='MT'""")
            qere_count=c.fetchone()[0]
            c.execute("""SELECT count(*) FROM public.hebrew_vowel_variant_group
                         WHERE review_status='candidate'""")
            candidate_status_count=c.fetchone()[0]
            c.execute("""SELECT count(*) FROM public.hebrew_vowel_variant_member m
                         JOIN public.hebrew_vowel_variant_group g USING (variant_group_id)
                         WHERE m.is_aramaic IS DISTINCT FROM g.is_aramaic""")
            language_mismatches=c.fetchone()[0]

        result={
            "validation_passed":True,
            "source_database":SOURCE_DB,
            "shadow_database":SHADOW_DB,
            "source_snapshot_id":SOURCE_SNAPSHOT_ID,
            "algorithm_version":ALGORITHM_VERSION,
            "source_rows_scanned":scanned,
            "group_count":group_count,
            "member_count_language_scoped":member_count,
            "unique_root_vowel_keys":len(all_members),
            "member_keys_in_both_candidate_populations":member_keys_in_both_candidate_populations,
            "candidate_occurrences":occurrence_count,
            "cross_root_groups":cross_root,
            "cross_root_multiple_strongs":multiple_strongs,
            "cross_root_multiple_morphology":multiple_morphology,
            "cross_root_member_keys_shared_across_languages":shared_language_keys,
            "qere_mt_rows_separate":qere_count,
            "candidate_status_rows":candidate_status_count,
            "groups_with_at_least_two_distinct_nfc_forms":len(distinct_form_sets),
            "minimum_distinct_nfc_forms":minimum_distinct_nfc_forms,
            "maximum_distinct_nfc_forms":maximum_distinct_nfc_forms,
            "distinct_form_negative_fixture_passed":True,
            "member_language_mismatches":language_mismatches,
            "all_members_have_root_vowel":len(rv)==len(all_members),
            "all_members_have_lexicon":len(lex)==len(all_members),
            "source_table_counts_match_clone":True,
            "source_table_counts":source_counts,
            "database_modified":False,
            "production_database_modified":False
        }
        if qere_count!=1204 or candidate_status_count!=3349 or language_mismatches!=0:
            raise AssertionError("Apparatus or language-scope validation failed")
        if len(distinct_form_sets)!=group_count or minimum_distinct_nfc_forms<2:
            raise AssertionError("Distinct pointed-form invariant failed")
        print(json.dumps(result,ensure_ascii=False,indent=2))
        src.commit();sh.commit()
    finally:
        src.close();sh.close()

if __name__=="__main__":
    main()
