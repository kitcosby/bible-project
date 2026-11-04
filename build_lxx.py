#!/usr/bin/env python3
"""Load the Septuagint (CenterBLC/LXX, Rahlfs 1935, Text-Fabric) into
bible_v2.db as Greek-side tables keyed by a verse crosswalk to the MT
corpus. Kit's rulings (2026-11-03): dataset accepted on its permissive
terms (his own work stays Unlicense); FULL Greek canon incl.
deuterocanon; witness layer first; Daniel primary = Theodotion
(DanTh) -- the tradition matching the role found by the Nabonidus
cylinders, i.e. the MT-shaped Daniel of the printed KJV -- with the
Old Greek (Dan) carried as alternate.

Tables (all rebuilt from scratch on every run):
  lxx_books    one row per dataset book (57), with mt_book_id where a
               Masoretic counterpart exists, tradition + note.
  lxx_verses   every verse (30,371) with assembled Greek text.
  lxx_words    every word (623,693): surface, lemma, Strong's G,
               glosses, SBL transliteration, morphology decomposition.
  lxx_crosswalk  MT verse <-> LXX verse by NUMBERING (basis
               'numbering-v1') for mapped books: relations 'same',
               'mt_only', 'lxx_only'. Numbering schemes that diverge
               structurally (Psalms, Jeremiah) are stamped as such in
               lxx_books.note; content-based realignment is later work.

Provenance: CATSS -> Eliran Wong RLXX1935 -> CenterBLC (repo MIT);
see LXX_AUDIT_2026-11-03.md. Verse text is assembled by joining the
dataset's word surfaces with single spaces (the dataset carries no
punctuation-only tokens and no separate punctuated text) -- labeled
assembled, never presented as an edition's printed text.
"""
import sqlite3
import time

from tf.fabric import Fabric  # run under tf-venv/bin/python

DB = 'bible_v2.db'
FEATS = ('book,chapter,verse,word,lex,gloss,bol_gloss,strongs,'
         'translit_SBL,sp,ps,gn,nu,tense,mood,voice,case,degree,'
         'morphology')

# OSIS -> (mt_book_id or None, tradition, display name, note)
BOOKS = {
    'Gen':   (1, '', 'Genesis', ''),
    'Exod':  (2, '', 'Exodus', ''),
    'Lev':   (3, '', 'Leviticus', ''),
    'Num':   (4, '', 'Numbers', ''),
    'Deut':  (5, '', 'Deuteronomy', ''),
    'Josh':  (6, '', 'Joshua', ''),
    'Judg':  (7, '', 'Judges', ''),
    'Ruth':  (8, '', 'Ruth', ''),
    '1Sam':  (9, '', '1 Samuel', ''),
    '2Sam':  (10, '', '2 Samuel', ''),
    '1Kgs':  (11, '', '1 Kings', ''),
    '2Kgs':  (12, '', '2 Kings', ''),
    '1Chr':  (13, '', '1 Chronicles', ''),
    '2Chr':  (14, '', '2 Chronicles', ''),
    '1Esdr': (None, '', '1 Esdras', 'Greek canon only'),
    '2Esdr': (None, '', '2 Esdras', 'Esdras B: covers Ezra + Nehemiah; '
              'no single MT counterpart, crosswalk not built'),
    'Esth':  (17, '', 'Esther', 'Greek additions integrated in the text'),
    'Jdt':   (None, '', 'Judith', 'Greek canon only'),
    'TobBA': (None, 'BA', 'Tobit (BA)', 'Tobit, Codex Vaticanus recension'),
    'TobS':  (None, 'S', 'Tobit (S)', 'Tobit, Codex Sinaiticus recension'),
    '1Mac':  (None, '', '1 Maccabees', 'Greek canon only'),
    '2Mac':  (None, '', '2 Maccabees', 'Greek canon only'),
    '3Mac':  (None, '', '3 Maccabees', 'Greek canon only'),
    '4Mac':  (None, '', '4 Maccabees', 'Greek canon only'),
    'Ps':    (19, '', 'Psalms', 'numbering diverges from MT (151 psalms, '
              'offset after Ps 9/10); crosswalk is numbering-v1 only'),
    'Od':    (None, '', 'Odes', 'Greek canon only'),
    'Prov':  (20, '', 'Proverbs', ''),
    'Qoh':   (21, '', 'Ecclesiastes', ''),
    'Cant':  (22, '', 'Song of Songs', ''),
    'Job':   (18, '', 'Job', 'LXX Job is substantially shorter than MT'),
    'Wis':   (None, '', 'Wisdom of Solomon', 'Greek canon only'),
    'Sir':   (None, '', 'Sirach', 'Greek canon only'),
    'PsSol': (None, '', 'Psalms of Solomon', 'Greek canon only'),
    'Hos':   (28, '', 'Hosea', ''),
    'Mic':   (33, '', 'Micah', ''),
    'Amos':  (30, '', 'Amos', ''),
    'Joel':  (29, '', 'Joel', ''),
    'Jonah': (32, '', 'Jonah', ''),
    'Obad':  (31, '', 'Obadiah', ''),
    'Nah':   (34, '', 'Nahum', ''),
    'Hab':   (35, '', 'Habakkuk', ''),
    'Zeph':  (36, '', 'Zephaniah', ''),
    'Hag':   (37, '', 'Haggai', ''),
    'Zech':  (38, '', 'Zechariah', ''),
    'Mal':   (39, '', 'Malachi', ''),
    'Isa':   (23, '', 'Isaiah', ''),
    'Jer':   (24, '', 'Jeremiah', 'LXX Jeremiah is shorter and reordered '
              'vs MT; crosswalk is numbering-v1 only'),
    'Bar':   (None, '', 'Baruch', 'Greek canon only'),
    'EpJer': (None, '', 'Epistle of Jeremiah', 'Baruch 6 in some editions'),
    'Lam':   (25, '', 'Lamentations', ''),
    'Ezek':  (26, '', 'Ezekiel', ''),
    'Bel':   (None, 'OG', 'Bel and the Dragon (OG)', 'Daniel addition, '
              'Old Greek form'),
    'BelTh': (None, 'Th', 'Bel and the Dragon (Th)', 'Daniel addition, '
              'Theodotion form'),
    'Dan':   (27, 'OG', 'Daniel (Old Greek)', 'alternate tradition; '
              'primary Daniel is DanTh per Kit ruling 2026-11-03'),
    'DanTh': (27, 'Th', 'Daniel (Theodotion)', 'PRIMARY Daniel per Kit '
              'ruling 2026-11-03 (matches the found/MT-shaped Daniel)'),
    'Sus':   (None, 'OG', 'Susanna (OG)', 'Daniel addition, Old Greek form'),
    'SusTh': (None, 'Th', 'Susanna (Th)', 'Daniel addition, '
              'Theodotion form'),
}


def main():
    t0 = time.time()
    TF = Fabric(locations='sources/lxx/tf', modules=['1935'], silent='deep')
    TF.load(FEATS)
    F, L = TF.api.F, TF.api.L

    db = sqlite3.connect(DB)
    db.executescript("""
    DROP TABLE IF EXISTS lxx_crosswalk;
    DROP TABLE IF EXISTS lxx_words;
    DROP TABLE IF EXISTS lxx_verses;
    DROP TABLE IF EXISTS lxx_books;
    CREATE TABLE lxx_books (
      osis TEXT PRIMARY KEY, lxx_order INTEGER, name TEXT,
      mt_book_id INTEGER, tradition TEXT, note TEXT);
    CREATE TABLE lxx_verses (
      verse_id INTEGER PRIMARY KEY, osis TEXT, chapter INTEGER,
      verse INTEGER, text TEXT);
    CREATE INDEX idx_lxx_verses_ref ON lxx_verses(osis, chapter, verse);
    CREATE TABLE lxx_words (
      verse_id INTEGER, position INTEGER, surface TEXT, lemma TEXT,
      strongs TEXT, gloss TEXT, bol_gloss TEXT, translit TEXT,
      sp TEXT, morph TEXT, ps TEXT, gn TEXT, nu TEXT, tense TEXT,
      mood TEXT, voice TEXT, case_ TEXT, degree TEXT,
      PRIMARY KEY (verse_id, position));
    CREATE INDEX idx_lxx_words_strongs ON lxx_words(strongs);
    CREATE INDEX idx_lxx_words_lemma ON lxx_words(lemma);
    CREATE TABLE lxx_crosswalk (
      mt_verse_id INTEGER, lxx_verse_id INTEGER, osis TEXT,
      relation TEXT, basis TEXT,
      PRIMARY KEY (osis, relation, mt_verse_id, lxx_verse_id));
    """)

    verse_id = 0
    n_words = 0
    n_strongs = 0
    lxx_by_ref = {}   # (osis, ch, v) -> verse_id, for mapped books
    order = 0
    for b in F.otype.s('book'):
        osis = F.book.v(b)
        order += 1
        mt_id, trad, name, note = BOOKS.get(
            osis, (None, '', osis, 'UNMAPPED in loader - review'))
        db.execute("INSERT INTO lxx_books VALUES (?,?,?,?,?,?)",
                   (osis, order, name, mt_id, trad, note))
        for c in sorted(L.d(b, otype='chapter'), key=lambda n: F.chapter.v(n)):
            ch = F.chapter.v(c)
            for v in sorted(L.d(c, otype='verse'), key=lambda n: F.verse.v(n)):
                vn = F.verse.v(v)
                verse_id += 1
                surfaces = []
                pos = 0
                for w in L.d(v, otype='word'):
                    pos += 1
                    surf = F.word.v(w)
                    surfaces.append(surf)
                    st = F.strongs.v(w)
                    if st:
                        n_strongs += 1
                    db.execute(
                        "INSERT INTO lxx_words VALUES (?,?,?,?,?,?,?,?,?,"
                        "?,?,?,?,?,?,?,?,?)",
                        (verse_id, pos, surf, F.lex.v(w), st,
                         F.gloss.v(w), F.bol_gloss.v(w),
                         F.translit_SBL.v(w), F.sp.v(w),
                         F.morphology.v(w), F.ps.v(w), F.gn.v(w),
                         F.nu.v(w), F.tense.v(w), F.mood.v(w),
                         F.voice.v(w), F.case.v(w), F.degree.v(w)))
                    n_words += 1
                db.execute("INSERT INTO lxx_verses VALUES (?,?,?,?,?)",
                           (verse_id, osis, ch, vn, ' '.join(surfaces)))
                if mt_id is not None:
                    lxx_by_ref[(osis, ch, vn)] = verse_id
        print(f'  {osis}: cumulative verses {verse_id}, words {n_words} '
              f'({time.time()-t0:.0f}s)', flush=True)

    # Crosswalk by numbering for books with an MT counterpart.
    mt_verses = {}
    for vid, bid, ch, vn in db.execute(
            "SELECT verse_id, book_id, chapter, verse FROM verses"):
        mt_verses[(bid, ch, vn)] = vid
    xw = {'same': 0, 'mt_only': 0, 'lxx_only': 0}
    used = set()
    for osis, (mt_id, trad, name, note) in BOOKS.items():
        if mt_id is None:
            continue
        for (o, ch, vn), lvid in lxx_by_ref.items():
            if o != osis:
                continue
            mvid = mt_verses.get((mt_id, ch, vn))
            if mvid is not None:
                db.execute("INSERT INTO lxx_crosswalk VALUES (?,?,?,"
                           "'same','numbering-v1')", (mvid, lvid, osis))
                xw['same'] += 1
                used.add(lvid)
            else:
                db.execute("INSERT INTO lxx_crosswalk VALUES (NULL,?,?,"
                           "'lxx_only','numbering-v1')", (lvid, osis))
                xw['lxx_only'] += 1
                used.add(lvid)
        for (bid, ch, vn), mvid in mt_verses.items():
            if bid == mt_id and (osis, ch, vn) not in lxx_by_ref:
                db.execute("INSERT INTO lxx_crosswalk VALUES (?,NULL,?,"
                           "'mt_only','numbering-v1')", (mvid, osis))
                xw['mt_only'] += 1
    db.commit()
    print()
    print(f'books {order} | verses {verse_id} | words {n_words} | '
          f'with Strong\'s {n_strongs} '
          f'({100.0*n_strongs/n_words:.1f}%)')
    print('crosswalk:', xw)
    print(f'elapsed {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
