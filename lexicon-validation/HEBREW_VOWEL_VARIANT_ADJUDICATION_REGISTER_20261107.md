# Hebrew vowel-only variant adjudication register

**Date:** 2026-11-07  
**Scope:** First source-based adjudication pass over the unresolved or potentially misleading cases surfaced by the 372-group member-level review.  
**Status:** Research register only. No production or shadow database writes; no source lexical, morphology, Strong's, root, or alignment records were changed.

## Governing distinction

The 372-group index is an **orthographic candidate inventory**, not a semantic-equivalence table. The strict signature algorithm remains unchanged. This register adds a second, independent layer: what the evidence currently says about selected lexical, morphological, textual, and source-annotation questions.

The following status labels are deliberately not interchangeable:

- **Resolved** means the specific uncertainty named in the case has been answered from the database morphology, the lexical source, or the cited context. It does not authorize merging.
- **Related Strong's entries** means two IDs are derivationally or lexically related; the original IDs remain intact.
- **Open** means a real source, textual, geographical, or vocalization question remains.
- **Probable source annotation conflict** is a diagnostic, not a correction.

## Findings

### 1. Disputed reading: בְּנִיהֶם in Ezekiel 27:32

The Lampy source row is word_id **238432**, pointed **בְּנִיהֶם**, Strong's **H5204**, morphology **HR/Ncmsc/Sp3mp**. In the database this is preposition ב + a masculine singular noun in construct with a third masculine plural suffix: “in their wailing.”

The BDB entry for H5204 explicitly marks the reading as doubtful. It reports that eleven manuscripts, early editions, and ancient versions have **בְּנֵיהֶם**, “their sons,” rather than the Masoretic **בְּנִיהֶם**. The local `word_variants` rows for word_id 238432 contain spelling variants only; there is no textual qere row attached to this word. Thus the external witness reading must not be silently treated as a stored MT qere.

**Disposition:** keep the MT reading and the alternative witness reading distinct. This is a textual-critical question, not an ordinary semantic variant.  
Sources: [BDB/Strong's H5204](https://biblehub.com/strongs/hebrew/5204.htm); [Ezekiel 27:32 Hebrew analysis](https://www.openbible.com/text/ezekiel/27-32.htm).

### 2. לְבֹא חֲמָת: infinitive or toponym?

The database assigns **HNp** (proper name) to לְבֹא in Numbers 13:21 and 34:8. Other occurrences of the same form family are parsed as **HR/Vqc** (preposition + Qal infinitive construct), H935. Independent grammatical analyses parse the phrase as “to/unto the entrance of Hamath.” The UBS translator handbook notes that some translations treat “Lebo” as part of the place-name, while other renderings translate “entrance of Hamath”; it recommends the place-name rendering for Numbers 13:21 on geographical/contextual grounds.

**Disposition:** genuinely ambiguous boundary between a verbal infinitive/nominalized “entrance” and a toponymic reading. The database's proper-name parse is not disproved by grammar alone. This remains open pending OSHB source annotation and geographical review.  
Sources: [Numbers 34:8, Mechon-Mamre](https://www.mechon-mamre.org/p/pt/pt0434.htm); [Numbers 13:21, UBS translator handbook](https://tips.translation.bible/tip_verse/num-1321/); [Numbers 34:8, Hebrew analysis](https://biblehub.com/text/numbers/34-8.htm).

### 3. לָעִיר in 2 Kings 19:13 / Isaiah 37:13

The project database assigns **HNp** to the forms in the parallel 2 Kings/Isaiah passages, despite Strong's H5892 (“city”). The parallel phrase is conventionally read “the king of the city of Sepharvaim”; an independent Hebrew text analysis explicitly parses לָעִיר as “of the city.” Micah 6:9 has the same common noun with morphology **HRd/Ncfsa** (preposition + definite article + common feminine singular noun).

**Disposition:** probable source morphology inconsistency. Do not change the source parse until the exact OSHB XML and parallel token records have been checked.  
Sources: [2 Kings 19:13 Hebrew analysis](https://mail.cnbible.com/text/2_kings/19-13.htm); [Isaiah/2 Kings parallel text analysis](https://bibliaparalela.com/text/2_kings/19-13.htm).

### 4. Resolved lexical collisions and rare forms

- **בְּכַר, Genesis 31:34 (H3733):** BDB/Strong's includes “basket-saddle” or camel saddle; the context is Rachel placing the teraphim in the camel's gear. This is not H1060 “firstborn.” [H3733 lexical entry](https://biblehub.com/strongs/hebrew/H3733.htm).
- **הָדָה, Isaiah 11:8 (H1911):** the verb means “stretch out the hand”; the clause says the weaned child stretches out his hand toward/on the viper's den. **הֹדֹה**, Jeremiah 22:18 (H1935), is the noun “majesty/splendour” with a suffix. Distinct lexemes. [H1911](https://biblehub.com/bdb/1911.htm); [H1935](https://biblehub.com/bdb/1935.htm).
- **וַיִּגְלֹם, 2 Kings 2:8 (H1563):** BDB defines the verb “wrap up, fold, fold together,” matching Elijah's wrapping/folding of his mantle. The other member, וַיַּגְלֵם in 1 Chronicles 5:26, is H1540 with a 3mp object suffix and means “carry them into exile.” Distinct verbal lexemes. [H1563 BDB](https://biblehub.com/bdb/1563.htm).
- **רָדָה, Judges 14:9 (H7287):** BDB has a distinct second entry for רָדָה, “scrape out,” and explicitly cites the scraping of honey from the lion's carcass. The other member רְדָה in Genesis 45:9 and Ezekiel 32:19 is the imperative of ירד, “go down.” Distinct lexemes and forms. [H7287 BDB](https://www.studylight.org/lexicons/eng/hebrew/7287.html).
- **עַלְוָה, 1 Chronicles 1:51 (H5933):** BDB identifies this as an Edomite male proper name, Alvah. The other member is עַל + a pronominal suffix, H5921 (“upon her/it”). Distinct lexemes.

### 5. Related Strong's entries, not proven data errors

- **רֹעַי:** the source assigns H7473 in Genesis 13:8 and H7462 in Ezekiel 34:8 to the same pointed/member key and morphology. H7473 is explicitly derived from the active participle of H7462 and means “shepherd” as a substantive. This is a related-lemma/Strong's distinction; it is not, by itself, evidence of corrupt data. [H7473](https://primebible.com/strongs/hebrew/H7473).
- **מהר family:** H4118 is derived from H4116; H4120 is the feminine noun/adverb from H4118 (“haste, quickly”). These are related derivational forms, not interchangeable lexical records. [H4120](https://studybible.info/strongs/H4120).

### 6. Morphology questions resolved against the OSHB code legend

The official OSHB code table defines the verb stem and conjugation positions separately: `q` in the stem position is Qal; `p` in the conjugation position is perfect; `v` is imperative; `h` is Hiphil; `N` is Niphal; `r` is active participle; `a` is infinitive absolute; `Sh` is paragogic he; `Ti` is an interrogative particle; `Td` is the definite article. [Official OSHB Hebrew Morphology Codes](https://hb.openscriptures.org/parsing/HebrewMorphologyCodes.html).

- **הֲרֹאֶה, Ezekiel 8:6:** database pattern **HTi/Vqrmsa** = interrogative particle + Qal active participle masculine singular absolute. The following explicit pronoun **אַתָּה** is second masculine singular. The clause addresses Ezekiel: “Are you seeing…?” This resolves the earlier uncertainty about whether the participle's subject was “he” or “you.”
- **הֵאִירָה / הָאִירָה:** pattern IDs 2866/2908 are **HVhp3fs** versus **HVhv2ms/Sh**: Hiphil perfect 3fs versus Hiphil imperative 2ms + paragogic he.
- **הֵאָכֹל / הָאֹכֵל:** pattern IDs 2640/2381 are **HVNa** versus **HTd/Vqrmsa**: Niphal infinitive absolute versus definite article + Qal active participle masculine singular absolute.
- **שִׁלְחָה / שָׁלְחָה** and **שִׁמְעָה / שָׁמְעָה:** pattern IDs 3360/3283 are **HVqv2ms/Sh** versus **HVqp3fs**: Qal imperative 2ms + paragogic he versus Qal perfect 3fs.

These code checks resolve morphology labels, not every translation nuance. The source codes are preserved.

### 7. Vocalization/source-text review still open: עֳלֶיהָ / עָלֶיהָ

The final batch found one Isaiah 37:33 occurrence with **עֳלֶיהָ** and 32 other occurrences with **עָלֶיהָ**. Both are assigned H5921 and the same morphology **HR/Sp3fs** (preposition עַל + 3fs suffix). No grammatical or semantic difference is supplied by the current database.

**Disposition:** preserve both raw pointed forms; compare the exact WLC/OSHB source tokens and Masoretic vocalization before deciding whether this is a source-text difference, normalization issue, or legitimate vocalization variant. Do not create a second lexical identity on the current evidence.

## Recommended next sequence

1. Resolve the two source-annotation candidates by checking the exact OSHB XML: לָעִיר (2 Kings 19:13 / Isaiah 37:13) and לְבֹא (Numbers 13:21 / 34:8).
2. Review the textual apparatus for Ezekiel 27:32 and decide whether the alternative בְּנֵיהֶם reading belongs in a separate textual-witness record; do not insert it into the MT word row.
3. Compare the WLC/OSHB source for עֳלֶיהָ / עָלֶיהָ.
4. Only after those checks, propose any source corrections or app presentation changes. The orthographic candidate layer remains separate from lexical identity and textual apparatus.

## Preservation statement

This register was built from read-only queries of the Lampy `bible` database and the existing review reports, plus cited lexical/morphological sources. No production or shadow database rows, source annotations, root assignments, Strong's values, morphology, alignments, embeddings, or vectorizers were changed.

## 8. Further source-text checks (2026-11-07 continuation)

### לְבֹא חֲמָת — both grammatical and geographical analyses remain viable

The WLC transcription gives the same pointed token, **לְבֹא**, in Numbers 13:21 and 34:8. Independent WLC text analyses classify it as a verb with Strong's H935; one renders the token “entering,” and the other “to the Lebo-Hamath.” This supports the infinitive analysis at the grammatical level but does not settle whether the phrase functions as a place-name.

The UBS *Handbook on Numbers* explicitly reports both renderings. For Numbers 13:21 it recommends “Lebo-hamath” on the basis that “Lebo” was part of the name in 1 Kings 8:65, while also noting “Hamath Pass” as plausible. Its Numbers 34:8 discussion renders the phrase “to the entrance of Hamath” and refers readers back to 13:21. A separate UBS note says the exact meaning is unclear and presents the city-name and entrance/pass options.

**Updated assessment:** retain the case as genuinely open. Do not mark the database's HNp annotation as disproved solely because independent interlinear tools parse the form as H935. Morphological analysis of the token and interpretation of the phrase boundary are related but distinct questions.

Sources: [WLC analysis, Numbers 13:21](https://cnbible.com/text/numbers/13-21.htm); [WLC analysis, Numbers 34:8](https://cnbible.com/text/numbers/34-8.htm); [UBS Handbook, Numbers 13:21](https://tips.translation.bible/tip_verse/num-1321/); [UBS Handbook, Numbers 34:8](https://tips.translation.bible/tip_verse/num-34-8/); [UBS discussion of the phrase](https://tips.translation.bible/tip_source/omanson-ellington-2008/page/162/).

### לָעִיר — common-noun reading is strongly supported

The WLC text in both 2 Kings 19:13 and Isaiah 37:13 has **לָעִיר** in the phrase naming “the king of the city of Sepharvaim.” Independent WLC analyses assign Strong's H5892 and identify the token as the common noun “city,” not a proper name. This supports the register's existing diagnosis of a probable source morphology inconsistency where the project database assigns HNp.

**Updated assessment:** retain **OPEN_SOURCE_MORPHOLOGY_QA**, with high priority. The common-noun reading is strongly supported by the parallel syntax and independent analysis, but the exact OSHB XML/word annotation and the project's source-to-database mapping still need to be checked before proposing a correction.

Sources: [WLC analysis, 2 Kings 19:13](https://cnbible.com/text/2_kings/19-13.htm); [WLC analysis, Isaiah 37:13](https://cnbible.com/text/isaiah/37-13.htm).

### עֳלֶיהָ / עָלֶיהָ — WLC form is corroborated; another text display differs

The pointed WLC text of Isaiah 37:33 is independently displayed as **עֳלֶיהָ** by CNBible, BibleHub, BibleGateway's WLC, and Israel.com. CNBible's WLC analysis identifies it as the preposition “against/upon” (H5921). Sefaria's Isaiah 37:33 display instead has **עָלֶיהָ**. These are different vowel-point sequences on the same consonantal form, and the project's two member records share H5921 and morphology HR/Sp3fs.

**Disposition: RESOLVED_SOURCE_FORM.** The WLC vocalization **עֳלֶיהָ** is externally corroborated and is supported for this project’s WLC source snapshot. It shares H5921 and HR/Sp3fs with the ordinary **עָלֶיהָ** form, so the candidate is a valid vowel-only orthographic variant, not a separate lexical identity or obvious database typo. Sefaria displays **עָלֶיהָ**, but its precise textual base/normalization policy remains unidentified; retain that as an edition-comparison note only. Preserve raw forms and source provenance; do not merge the source member assignments.

Sources: [CNBible WLC, Isaiah 37:33](https://www.cnbible.com/text/isaiah/37-33.htm); [BibleHub WLC, Isaiah 37:33](https://biblehub.com/texts/isaiah/37-33.htm); [BibleGateway WLC, Isaiah 37:33](https://www.biblegateway.com/passage/?search=Isaiah+37&version=WLC); [Sefaria, Isaiah 37:33](https://www.sefaria.org/Isaiah.37.1-38.22).

### Methodological note: key-only NFC validation

The OSHB repository README warns against NFC normalization of Hebrew source text. A new read-only live-corpus test found that 138,497 word rows change code-point order under NFC, while the raw source strings remain preserved. The current NFC comparison inventory is nevertheless reproducible: NFC-then-vowel-removal and vowel-removal-then-NFC produce identical 3,349 candidate groups and identical normalized member sets (zero mismatches). See [HEBREW_VOWEL_VARIANT_NFC_NORMALIZATION_CHECK_20261107.md](HEBREW_VOWEL_VARIANT_NFC_NORMALIZATION_CHECK_20261107.md).

**Disposition:** retain NFC for comparison keys only under the current tested convention; never rewrite raw source strings. Keep this test as a regression requirement when the corpus or normalization implementation changes.


## 9. Live database row-level confirmation

A fresh read-only query against Lampy's live `bible` database confirms the exact records underlying the open cases:

| Reference | `word_id` | Stored pointed form | Strong's | Stored morphology |
|---|---:|---|---|---|
| Numbers 13:21 | 47351 | `לְבֹ֥א` | H935 | HNp |
| Numbers 34:8 | 55394 | `לְבֹ֣א` | H935 | HNp |
| 2 Kings 19:13 | 126492 | `לָעִ֣יר` | H5892 | HNp |
| Isaiah 37:13 | 202764 | `לָעִ֣יר` | H5892 | HNp |
| Isaiah 37:33 | 203026 | `עֳלֶ֖יהָ` | H5921 | HR/Sp3fs |
| Ezekiel 27:32 | 238432 | `בְּנִיהֶם֙` | H5204 | HR/Ncmsc/Sp3mp |

This confirms the live database's current assignments, including the combination of H935 with HNp for both לְבֹא tokens and H5892 with HNp for both לָעִיר tokens. It does **not** establish whether those morphology values originate in the pinned OSHB XML or were introduced by a later parser/crosswalk step.

The project's OSHB provenance file pins the upstream source to commit `3d15126fb1ef74867fc1434be1942e837932691f` (2024-08-27), with the per-book files under `wlc/*.xml`. Direct retrieval of the large upstream XML files was not successful in this session, so the exact source-XML comparison remains outstanding. No correction has been applied.


### בְּנִיהֶם / בְּנֵיהֶם — Septuagint evidence checked

The Hebrew Masoretic text is displayed as **בְּנִיהֶם** in Ezekiel 27:32 and parsed by the project as preposition ב + the rare singular noun נִי (“wailing”) + 3mp suffix. The Greek Septuagint text displayed for the verse reads **καὶ λήμψονται οἱ υἱοὶ αὐτῶν ἐπὶ σὲ θρῆνον** (“and their sons will take up a lament for you”), which corresponds to the alternative Hebrew vocalization **בְּנֵיהֶם** (“their sons”), not the MT's “in their wailing” analysis. BDB records the same alternative in eleven manuscripts, early editions, and ancient versions, while explicitly calling the MT lexical reading doubtful.

**Updated assessment:** this is a substantive textual/lexical ambiguity within the same consonantal spelling, not merely two meanings of one securely established MT lemma. The LXX supports the “their sons” reading; the MT preserves “in their wailing.” Keep the MT word row and any external-witness reading separate. The project has no local qere row for word_id 238432, so do not manufacture a Masoretic qere entry. A future apparatus proposal should record the witness, reading, and provenance explicitly.

Sources: [WLC and Hebrew analysis, Ezekiel 27:32](https://www.cnbible.com/text/ezekiel/27-32.htm); [Greek Septuagint and MT interlinear, Ezekiel 27:32](https://thecorebible.org/interlinear/?book=26&chapter=27&verse=32); [BDB/Strong's H5204 textual note](https://www.studylight.org/lexicons/eng/hebrew/5204.html).


### Morphology provenance narrowed

Inspection of the project's pinned-source parser, `worker-out/oshb/parse_oshb.py`, shows that it reads `morph = el.get('morph') or ''` and writes that value directly to the TSV. The accompanying `worker-out/oshb/README.txt` explicitly defines the `morph` column as OSHB `@morph` “verbatim.” No morphology-code transformation is present in this parser.

**Implication:** the live HNp values for the two לְבֹא tokens and the two לָעִיר tokens are likely inherited from the pinned OSHB XML annotation, not introduced by this parser. This narrows the question from “did the local parser corrupt the code?” to “is the upstream OSHB annotation defensible, and does the independent interlinear analysis parse the same text/word segmentation?” The exact XML attributes are still not directly retrieved, so this is a provenance-supported inference, not a direct XML inspection. No parser or database correction is proposed.


### YLT alignment check for word_id 238432

A separate read-only query of the live YLT alignment tables found a likely alignment anomaly in Ezekiel 27:32:

- The YLT verse text is: “And lifted up for thee have their sons a lamentation, And they have lamented over thee, who [is] as Tyre? As the cut-off one in the midst of the sea?”
- The verse has 30 whitespace-delimited YLT tokens but only 14 distinct token positions in `ylt_renderings`.
- MT word_id **238432** (`בְּנִיהֶם֙`, H5204, morphology `HR/Ncmsc/Sp3mp`) is linked by rows labeled `bridged` to YLT positions **1 “And”** and **2 “lifted”**.
- The preceding Hebrew verb word_id **238430** (`וְנָשְׂאוּ`, H5375) has no YLT alignment rows.
- YLT positions **7 “their”** and **8 “sons”** have no alignment rows; the YLT translation appears to follow the “their sons” interpretation rather than the MT “in their wailing” lexical analysis.

**Assessment:** this is a strong candidate for a U-1 YLT alignment defect or an unresolved alternative-reading alignment, not proof that the MT word row should be changed. The existing YLT text and all `ylt_renderings` rows are preserved. Do not recompute or rewrite the alignment as part of this Hebrew variant task. Create a separate alignment review item if the YLT alignment project is resumed.
