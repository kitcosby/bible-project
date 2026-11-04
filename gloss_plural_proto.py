#!/usr/bin/env python3
"""Prototype: number-aware API gloss (2026-11-03).

The API gloss (_api_gloss in website/app_v2.py) is the lemma's most
frequent KJV phrase — number-blind, so a plural form like Eccl 1:2's
הֲבָלִים (H1892, plural) displays the singular gloss "vanity".

This prototype tests the conservative fix that ships in app_v2.py:
when the word's own morphology is a PLURAL noun and the gloss's last
word is on a curated allowlist of ordinary countable nouns, pluralize
that last word in place. Everything else is left untouched — the census
(2026-11-03) showed the unrestricted version would corrupt Elohim
("God", 2,587 occ.), panim ("before", 2,042), mayim ("water", 562),
hayyim ("of life"), and hundreds of junk/already-plural glosses.

Run against the local SQLite corpus (bible_v2.db). Prints the Eccl 1:2
specimen, regression verses, and a corpus-wide change census.
"""
import re
import sqlite3
import sys
from collections import Counter, defaultdict

# --- the exact block intended for app_v2.py -------------------------------
_PLURAL_ALLOW = {
    # curated 2026-11-03 from the plural-noun gloss census: ordinary
    # countable common nouns only. Divine names (God, Lord), mass nouns
    # (water, blood, bread), pluralia tantum with singular sense (life,
    # heaven, youth), proper/ethnic names, adjectives, and already-
    # plural forms (men, children, brethren) are deliberately absent.
    'adder', 'altar', 'ant', 'arm', 'arrow', 'basket', 'bason', 'bat',
    'beast', 'bed', 'bell', 'blessing', 'board', 'bolster',
    'book', 'border', 'bowl', 'breach', 'breast', 'brick', 'bullock',
    'buryingplace', 'cake', 'calf', 'camp', 'captain', 'cedar', 'censer',
    'chamber', 'chariot', 'child', 'city', 'cloud', 'coat', 'congregation',
    'corner', 'cornet', 'course', 'court', 'crown', 'cup', 'curse',
    'damsel', 'decree', 'disease', 'dog', 'door', 'dream', 'duke',
    'dunghill', 'eagle', 'enemy', 'feast', 'field', 'finger', 'fir',
    'firebrand', 'flame', 'flock', 'flower', 'fool', 'forest', 'fountain',
    'garden', 'garment', 'gate', 'goat', 'governor', 'grasshopper',
    'hammer', 'hand', 'handmaid', 'hart', 'heap', 'heel', 'heifer',
    'helmet', 'highway', 'hill', 'house', 'image', 'judgment', 'kid',
    'king', 'knife', 'knop', 'land', 'laver', 'law', 'lion', 'locust',
    'lot', 'magician', 'man', 'moment', 'month', 'mouse', 'multitude',
    'neighbour', 'nest', 'net', 'network', 'night', 'oak', 'offering',
    'olive', 'oppressor', 'oven', 'ox', 'parable', 'parlour', 'part',
    'passover', 'path', 'piece', 'pigeon', 'pillar', 'pitcher', 'pit',
    'place', 'plain', 'plant', 'plague', 'pool', 'portion', 'pound',
    'priest', 'prince', 'queen', 'raven', 'reproach', 'riddle', 'river',
    'robber', 'rock', 'roof', 'ruler', 'sabbath', 'sacrifice', 'sanctuary',
    'scribe', 'secret', 'serpent', 'sheaf', 'shield', 'shoe',
    'side', 'sign', 'sin', 'sister', 'snare', 'sojourner', 'spear',
    'spoon', 'spot', 'spouse', 'standard', 'stranger', 'sword', 'table',
    'tabernacle', 'temple', 'thanksgiving', 'thief', 'threshingfloor',
    'thistle', 'throne', 'time', 'tithe', 'tongue', 'top', 'tortoise',
    'tower', 'treasure', 'tree', 'tribe', 'trumpet', 'unicorn', 'vanity',
    'vow', 'wafer', 'wall', 'watch', 'web', 'well', 'whirlwind', 'widow',
    'wife', 'wolf', 'wound', 'whelp', 'year', 'yoke',
    # abstract but regularly counted in KJV English
    'abomination', 'calamity', 'charge', 'generation', 'iniquity',
    'kingdom', 'soul', 'vision',
}
_PLURAL_IRREG = {
    'man': 'men', 'child': 'children', 'ox': 'oxen', 'mouse': 'mice',
    'wife': 'wives', 'hoof': 'hoofs',
}
_F_VES = {'calf', 'wolf', 'leaf', 'loaf', 'shelf', 'half', 'sheaf',
          'thief', 'knife', 'life'}


def _plural_word(word):
    low = word.lower()
    if low in _PLURAL_IRREG:
        pl = _PLURAL_IRREG[low]
    elif low.endswith(('s', 'x', 'z', 'ch', 'sh')):
        pl = low + 'es'
    elif low.endswith('y') and low[-2:-1] not in ('a', 'e', 'i', 'o', 'u'):
        pl = low[:-1] + 'ies'
    elif low.endswith('fe') and low in _F_VES:
        pl = low[:-2] + 'ves'
    elif low.endswith('f') and low in _F_VES:
        pl = low[:-1] + 'ves'
    else:
        pl = low + 's'
    return pl.capitalize() if word[:1].isupper() else pl


_POSSESSIVE_HEADS = {'my', 'thy', 'his', 'her', 'our', 'your', 'their'}


def _gloss_for_number(gloss, noun_number):
    """Plural-aware gloss: only for plural nouns, only when the gloss's
    last word is allowlisted. Dual is untouched (body-pair duals carry
    idiomatic glosses). Returns the gloss unchanged otherwise.

    Guards from the 2026-11-03 change census:
    - possessive-headed glosses are skipped ("my soul" is a phrase from
      singular contexts; "my souls" would be wrong);
    - a gloss whose last word also appears earlier is an idiom or a
      junk repeated phrase ("from generation to generation",
      "boards board board") — skipped;
    - an indefinite article governing the head is dropped when
      pluralizing ("a sign" -> "signs", "for a sin offering" ->
      "for sin offerings")."""
    if noun_number != 'plural' or not gloss:
        return gloss
    m = re.search(r"([A-Za-z']+)([^A-Za-z']*)$", gloss)
    if not m or m.group(1).lower() not in _PLURAL_ALLOW:
        return gloss
    words = re.findall(r"[A-Za-z']+", gloss)
    lows = [w.lower() for w in words]
    if words and lows[0] in _POSSESSIVE_HEADS:
        return gloss
    if sum(1 for w in lows if w == m.group(1).lower()) > 1:
        return gloss
    # plural form already present in the gloss ("firebrands firebrand",
    # "the thrones his throne") — junk phrase, leave it alone
    if _plural_word(m.group(1)).lower() in lows:
        return gloss
    # a determiner that forces singular directly before the head
    # ("every corner", "this disease", "the other side", "the same time")
    if len(lows) >= 2 and lows[-2] in ('every', 'this', 'that', 'same',
                                       'other'):
        return gloss
    # predicative singular ("thou art a stranger") — pluralizing the
    # complement breaks subject agreement
    if re.search(r"\b(art|is|was|am)\s+(a|an)\s+[A-Za-z']+$", gloss):
        return gloss
    # an indefinite article must sit within the final three words to be
    # the head's own article ("for a sin offering"); a distant one
    # belongs to another noun ("the tithes a tenth of the tithe") —
    # skip the change entirely in that case
    if any(w in ('a', 'an') for w in lows[:-3]):
        return gloss
    out = gloss[:m.start(1)] + _plural_word(m.group(1)) + m.group(2)
    # drop the indefinite article that governs the final noun phrase:
    # the last ' a '/' an ' before the pluralized word
    head_at = out.rfind(_plural_word(m.group(1)))
    arts = [a for a in re.finditer(r'\b(a|an)\s+', out[:head_at])]
    if arts:
        a = arts[-1]
        out = out[:a.start()] + out[a.end():]
    return out
# --- end of block intended for app_v2.py ----------------------------------


def main(db_path):
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    # lemma gloss map, replicating _build_phrase_map + _api_gloss (KJV leg)
    freq = defaultdict(Counter)
    cur_wid, cur, cur_key = None, [], None
    q = """SELECT w.word_id, w.strongs, r.kjv_word AS txt FROM words w
    JOIN kjv_renderings r ON r.word_id=w.word_id
    ORDER BY w.word_id, r.rendering_id"""
    for row in db.execute(q):
        if row['word_id'] != cur_wid:
            if cur_wid is not None and cur_key:
                freq[cur_key][' '.join(cur)] += 1
            cur_wid, cur, cur_key = row['word_id'], [], row['strongs']
        cur.append(row['txt'])
    if cur_wid is not None and cur_key:
        freq[cur_key][' '.join(cur)] += 1
    gloss = {k: c.most_common(1)[0][0] for k, c in freq.items() if c}

    def verse(book, ch, vs):
        rows = db.execute(
            """SELECT w.word_pos, w.pointed, w.strongs,
                      (SELECT s.number_name FROM morph_segments s
                        WHERE s.pattern_id=w.morph_pattern_id
                          AND s.pos_name='noun' LIMIT 1) AS num
               FROM words w JOIN verses v ON v.verse_id=w.verse_id
               WHERE v.book_id=? AND v.chapter=? AND v.verse=?
               ORDER BY w.word_pos""", (book, ch, vs)).fetchall()
        return [(r['word_pos'], r['pointed'], r['strongs'],
                 gloss.get(r['strongs'], ''),
                 _gloss_for_number(gloss.get(r['strongs'], ''), r['num']))
                for r in rows]

    print('== Eccl 1:2 specimen (expect pos 2,6 vanity -> vanities) ==')
    for pos, heb, s, old, new in verse(21, 1, 2):
        mark = '  <-- CHANGED' if old != new else ''
        print(f'  {pos} {heb} {s}: {old!r} -> {new!r}{mark}')

    print('== regressions: Gen 1:1 (God unchanged), Isa 53:11, Ps 23:1 ==')
    for ref in [(1, 1, 1), (23, 53, 11), (19, 23, 1)]:
        changed = [(p, o, n) for p, h, s, o, n in verse(*ref) if o != n]
        print(f'  {ref}: changes={changed}')

    print('== corpus-wide census of changed glosses ==')
    rows = db.execute(
        """SELECT w.strongs, s.number_name AS num FROM words w
           JOIN morph_segments s ON s.pattern_id=w.morph_pattern_id
           WHERE s.pos_name='noun'""").fetchall()
    changes = Counter()
    total_plural = 0
    for r in rows:
        if r['num'] != 'plural':
            continue
        total_plural += 1
        g = gloss.get(r['strongs'], '')
        ng = _gloss_for_number(g, r['num'])
        if ng != g:
            changes[(g, ng)] += 1
    print(f'  plural noun occurrences: {total_plural}')
    print(f'  changed occurrences: {sum(changes.values())} '
          f'({len(changes)} distinct gloss pairs)')
    for (o, n), c in changes.most_common():
        print(f'   {c:6d}  {o!r} -> {n!r}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bible_v2.db')
