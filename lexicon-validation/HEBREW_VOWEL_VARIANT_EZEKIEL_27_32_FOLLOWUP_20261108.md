# Ezekiel 27:32 — follow-up source audit (2026-11-08)

## Purpose and status

This note supplements, but does not overwrite, the 2026-11-07 adjudication register. It records a second-pass audit of the published research summary and accessible primary/secondary references. The case remains **OPEN_TEXT_CRITICAL_REVIEW**. No production data, OSHB source annotation, lexicon entry, YLT text, or alignment row is changed.

## 1. The two readings are morphologically and syntactically distinct

The consonantal sequence is בניהם in both readings, but the vocalization yields different lexical segmentation:

| Reading | Analysis | Sense | Syntactic role in the clause |
|---|---|---|---|
| MT בְּנִיהֶם | בְּ (preposition) + נִי (rare noun, “wailing”) + 3mp suffix | “in their wailing” | Adverbial/prepositional phrase modifying the raising of a lament |
| Alternative בְּנֵיהֶם | בֵּן, plural construct בְּנֵי + 3mp suffix | “their sons” | Noun phrase; naturally read as the subject of “will raise a lament” |

The OSHB source annotation for the MT is exactly lemma `b/5204`, morphology `HR/Ncmsc/Sp3mp`, segmented `בְּ/נִי/הֶם֙` (word id `26F8P`, pinned source commit `3d15126fb1ef74867fc1434be1942e837932691f`). This verifies what the upstream source encodes; it does not adjudicate whether the MT reading is original.

The alternative is not an MT qere in the project's local data. It is a distinct vocalization/lexical analysis supported by ancient versional evidence and reported Hebrew manuscripts. It must remain an external textual witness/reading, not be inserted as a qere or used to rewrite the MT token.

## 2. Lexical status of נִי (H5204)

BDB explicitly labels נִי “si vera lectio” (“if this is indeed the correct reading”) and calls the MT reading improbable. The entry treats נִי as a masculine noun meaning wailing, equates it with נְהִי, and reports the alternative בְּנֵיהֶם in the Greek and Syriac evidence. It also reports Cornill's treatment of “their sons” as a gloss, with Buhl and Bertholet for comparison.

H5204 is a hapax in the MT corpus: it occurs only at Ezekiel 27:32. Its etymological association with H5091 נהה (“to wail”) is explicitly uncertain. The lemma should therefore be described as a **source-encoded, doubtful hapax**, not as an independently well-attested Hebrew lexeme.

Gesenius-Kautzsch-Cowley, *Hebrew Grammar* §23, lists the form as “perhaps also” an example of syncope: בְּנִיהֶם for בְּנְהִיהֶם. The qualification “perhaps” matters. GKC offers a possible phonological explanation for the MT pointing, not a demonstration that the hypothetical expanded form existed in the Vorlage, nor proof that the MT is original. The form is compatible with the proposal; the proposal remains conjectural.

## 3. Witness audit

| Witness/source | Reading or report | Type and approximate date | What it establishes / caveat |
|---|---|---|---|
| Masoretic/WLC tradition | בְּנִיהֶם, “in their wailing” | Hebrew vocalized tradition; represented by the Leningrad-based WLC | Establishes the source reading adopted by OSHB. It does not establish that the vocalization is the earliest recoverable reading. |
| Old Greek (OG) | καὶ λήμψονται οἱ υἱοὶ αὐτῶν ἐπὶ σὲ θρῆνον καὶ θρήνημά σοι — “and their sons will take up a lament over you and a lamentation for you” | Greek translation; extant witnesses include P967 (late 2nd/early 3rd century CE) and later codices | Explicitly supports “their sons.” The OG also lacks MT v.31. This is significant versional evidence, but the translator's Vorlage must be distinguished from the extant Greek manuscript date. |
| Papyrus 967 (P967) | Includes “their sons” at v.32; omits v.31 | Greek papyrus, late 2nd/early 3rd century CE | Confirms that the sons reading and the shorter local literary sequence existed in an early Greek witness. It does not prove that this form of the book or this reading is chronologically prior to the MT tradition. |
| Theodotion | בְּנֵיהֶם (“their sons”) is reported | Greek revision/versional evidence | Reported by Gesenius; direct manuscript/edition collation at this locus has not yet been inspected. Do not count it automatically as independent of OG without a witness-level study. |
| Syriac Peshitta | בְּנֵיהֶם (“their sons”) is reported | Syriac version | Reported by BDB/Gesenius. Its exact Syriac wording and dependence on Hebrew/Greek at this locus have not yet been independently collated. |
| Arabic | “their sons” is reported | Arabic versional evidence; specific version/manuscript not identified in the consulted lexicon entry | Gesenius reports this alongside LXX; exact witness and dependence remain unverified. |
| Eleven Hebrew manuscripts | בְּנֵיהֶם is reported | Direct Hebrew manuscript evidence, identities/dates not supplied in the consulted lexicon entry | Potentially important direct evidence, but currently second-hand. The individual codices, their dates, and whether the reading is consonantal or vocalic must be verified before weighting them. |
| Several early printed editions | בְּנֵיהֶם is reported | Printed Hebrew editions; exact editions not identified | Supports an alternate vocalization in the printed tradition, but is not equivalent to eleven independent ancient manuscripts. |
| Targum / Vulgate | No secure verse-specific reading established in this audit | Ancient versions | The prior automated summary's generalized descriptions were not substantiated at this verse. Do not cite them as witnesses for either reading until directly checked. |

The online Greek transcription of Ezekiel 27 gives v.32 as `καὶ λήμψονται οἱ υἱοὶ αὐτῶν ...` and proceeds from v.30 directly to v.32. Werner's commentary explicitly notes that P967 retains “their sons” and that v.31 is absent from the Septuagint. These are useful checks, but a critical edition and manuscript images remain preferable to derivative online transcriptions.

## 4. Context and edition-level caution

The MT has an extended sequence of mourning rites in vv.30–31 and then continues in v.32. The OG omits v.31 but has the sons-reading in v.32. This pairing makes it reasonable to investigate whether the local reading participates in a broader literary/textual form of Ezekiel rather than being only a vowel-pointing difference.

It is not legitimate to infer from P967's age that its reading is automatically earlier. Patmore argues that the Qumran/Masada evidence complicates a simple “shorter OG = earlier / longer MT = later expansion” model and that two forms of Ezekiel may have circulated concurrently. That is a book-level methodological caution, not a direct verdict on Ezekiel 27:32. The verse-specific evidence still has to be weighed independently.

## 5. Commentaries and the NET note: verified bibliographic pointers, limits

- The NET note for Ezekiel 27:32 explicitly directs readers to Leslie C. Allen, *Ezekiel 20–48* (WBC), vol. 2, p. 83, and Daniel I. Block, *The Book of Ezekiel, Chapters 25–48* (NICOT), vol. 2, pp. 85–86, for a list of explanations and emendations. This verifies the page references as bibliographic pointers, but the commentary pages themselves were not available for direct inspection in this audit.
- The NET note's specific adoption of M. Dahood's proposal (“Accadian-Ugaritic dmt in Ezekiel 27:32,” *Biblica* 45 [1964], 83–84) concerns the later expression כְּדֻמָה, not the earlier word בְּנִיהֶם. These are separate lexical/textual problems in the same verse.
- Zimmerli's *Ezekiel 2* (Hermeneia; 1983) covers Ezekiel 25:1–32:32 on pp. 3–178. JSTOR confirms the book and section range, but its full commentary text was not accessible here; no exact page or position on this variant is claimed.
- Werner Bible Commentary defends a descendant-based reading of “their sons,” arguing that later generations could mourn Tyre's later conquest. This is a contextual interpretation, not independent manuscript evidence. Keil and Delitzsch's contrary contextual objection remains an interpretive argument, not a textual witness.

## 6. Corrections to the previous automated research summary

1. The statement that P967 demonstrates an earlier Vorlage for this particular reading was too strong. P967 is an early Greek manuscript and the OG is a distinct textual witness; neither fact alone establishes priority at v.32.
2. The claim that the NET/Dahood note concerns בְּנִיהֶם was incorrect. The note concerns כְּדֻמָה (“like a tower” / related proposals), later in the verse.
3. A generic claim that the Targum and Vulgate support a particular interpretation was not verified at this locus and is withdrawn pending direct collation.
4. The previous report's characterization of the case as only a vowel variation was incomplete. It is a vowel-only orthographic match under the project's rule, but the readings differ in lexical identity, morphological segmentation, and syntax.

## 7. Current disposition and next evidence required

**Established**
- The WLC/OSHB MT source form is בְּנִיהֶם, annotated as H5204 and parsed as preposition + noun + suffix.
- The alternative בְּנֵיהֶם (“their sons”) is reported by BDB/Gesenius from versional evidence and eleven Hebrew manuscripts; the OG wording is explicit, and P967 retains it while omitting v.31.
- The two forms share the same consonantal sequence and differ only in vowel points, so group 504 is a valid candidate under the strict project rule.
- The two readings are lexically, morphologically, and syntactically different.

**Plausible**
- The MT form may reflect a contracted form related to נְהִי, as GKC §23 cautiously suggests.
- The “sons” reading may reflect a Hebrew Vorlage distinct from the vocalized MT form; it may also represent an ancient interpretive/translation choice. The extant evidence does not yet discriminate decisively.

**Unresolved**
- Which reading is earlier, and whether “their sons” is original, a gloss, or a contextual reinterpretation.
- The identity, date, and precise reading (consonantal/vocalic) of the eleven Hebrew manuscripts and early editions.
- The exact relationship of Theodotion, Syriac, and Arabic witnesses to one another and to OG/Hebrew exemplars.
- The direct positions of Allen, Block, and Zimmerli; direct collation in BHS/BHQ/Göttingen apparatuses; and any relevant Hebrew witness not represented in the consulted lexicons.

**Disposition:** retain the source MT annotation and all existing lexicon data unchanged. Retain shadow candidate group 504 as an orthographic cross-reference with a prominent note that it is a lexical/morphological ambiguity and an unresolved textual-critical case. Do not convert the alternative into a qere, do not merge H5204 with H1121, and do not alter YLT text or alignment.

The most useful next checks are: (1) inspect Allen 2:83 and Block 2:85–86 directly; (2) inspect BHS and Göttingen/Ziegler apparatus at Ezek 27:32 and record exact sigla; (3) identify and collate the eleven Hebrew codices/early editions cited by Gesenius; (4) collate P967, Vaticanus, Alexandrinus, Theodotion, Peshitta, Targum, and Vulgate separately at vv.31–32; and (5) compare OG translator habits for בֵּן/בְּנֵי and for rendering Hebrew lament terminology.

## Sources consulted

- BDB, entry נִי (H5204), reproduced with its textual note at [StudyLight, Hebrew Lexicon 5204](https://www.studylight.org/lexicons/eng/hebrew/5204.html).
- Gesenius-Kautzsch-Cowley, *Hebrew Grammar* §23, especially the cautious example “perhaps also” בְּנִיהֶם for בְּנְהִיהֶם: [online text](https://www.studylight.org/lexicons/eng/gesenius/23.html).
- [Old Greek text of Ezekiel 27](https://dapytains.biblindex.org/en/bible/septuaginta/ez-27), especially vv.30 and 32.
- [Werner Bible Commentary, Ezekiel 27:1–36](https://wernerbiblecommentary.org/?q=node/919), especially notes on vv.31–32.
- [NET Bible, Ezekiel 27:32](https://classic.net.bible.org/passage.php?passage=Eze+27%3A32), including its pointer to Allen and Block and its Dahood note.
- [Zimmerli, *Ezekiel 2* (Hermeneia), JSTOR book record and contents](https://doi.org/10.2307/j.ctvb6v7xg).
- Hector M. Patmore, “The Shorter and Longer Texts of Ezekiel,” *Journal for the Study of the Old Testament* 32/2 (2007), 231–242, [DOI](https://doi.org/10.1177/0309089207085885).
- Timothy P. Mackie, “Text-Critical Issues in Ezekiel,” *The Oxford Handbook of the Book of Ezekiel* (2020), [DOI](https://doi.org/10.1093/oxfordhb/9780190634513.013.16).
- John Screnock, “A New Approach to Using the Old Greek in Hebrew Bible Textual Criticism,” *Textus* (2018), [DOI](https://doi.org/10.1163/2589255x-02701008).

This note is an evidence audit, not a final textual-critical verdict.


## 8. Additional witness and reception audit (2026-11-08)

A further check located a directly displayed Targum Jonathan text at Ezekiel 27:31–32, together with Rashi's comment on the Hebrew phrase. This adds evidence for the history of interpretation, but it does **not** establish that the Targum or Rashi preserves the alternative “their sons.”

### Targum Jonathan

The displayed Aramaic at v.32 is:

`וְיִטְלוּן עֲלָךְ בְּעִינוּיֵהוֹן אִילְיָא וְיֵלִילוּן עֲלָךְ`

The accompanying English translation is: “And in their affliction they shall raise a lamentation over you and wail over you.” The Aramaic has `בְּעִינוּיֵהוֹן` (“in their affliction/distress”) rather than a transparent equivalent of “their sons.” The Targum therefore **does not attest the sons reading in its extant wording**. Its rendering is compatible with a mourning/wailing interpretation of the clause, but it is a targumic paraphrase and cannot be treated as a literal retroversion of the Hebrew vocalization. Its v.31 is also present, unlike the Old Greek sequence.

This is a correction to the earlier source-audit table's overly broad “Targum not verified” statement: the Targum has now been directly inspected in an online text presentation. It should be recorded as a checked versional rendering that supports the mourning sense, not as direct evidence for the MT's precise lexeme נִי or for the alternative בְּנֵיהֶם.

### Rashi

Rashi explicitly glosses the MT phrase `בְּנִיהֶם` as “with their wailing” (בְּעִינוּיֵהוֹן / with their wailing in the displayed commentary translation). This confirms a medieval Jewish interpretation of the received Hebrew pointing as a mourning expression. Rashi is an exegetical witness to the interpretation of the MT form, not an independent manuscript witness to the consonantal or vocalic text.

### The Hebrew manuscript report remains unidentifiable

The additional check of Bullinger's *Companion Bible* note confirms a secondary report that “some codices,” together with two early printed editions, the Septuagint, and Syriac, read “their sons.” Bullinger does not identify those codices or editions in the verse note. This independently confirms the existence of a circulated report of Hebrew manuscript support, but it does not identify or date the manuscripts.

The eleven-manuscript count remains attributable to the Gesenius lexicon report as previously recorded. No primary catalogue, manuscript shelfmark list, or edition-by-edition collation has yet been located to map that count onto named codices. Therefore:
- Do not turn “eleven manuscripts” into eleven independent witnesses.
- Do not assume all eleven are ancient; date and provenance are unknown.
- Do not assume the two early printed editions are independent of the manuscript copies or of each other.
- Keep the report second-hand until its cited apparatus or source can be identified.

### Revised witness matrix

| Witness | Directly inspected here? | Reading / evidence | Evidential status |
|---|---:|---|---|
| WLC / OSHB MT | Yes, through the displayed Hebrew text and pinned OSHB source annotation | בְּנִיהֶם; H5204; “in their wailing” | Directly establishes the project source reading, not priority |
| Old Greek | Greek wording checked in an online transcription | οἱ υἱοὶ αὐτῶν, “their sons”; v.31 absent in this sequence | Direct versional evidence |
| P967 | No manuscript image or critical transcription independently collated in this pass | “Their sons” and omission of v.31 reported by Werner | Secondary report pending papyrus collation |
| Syriac Peshitta | No Syriac manuscript/critical edition directly collated | “Their sons” reported by BDB/Gesenius and Bullinger | Secondary report pending direct check |
| Theodotion | No | “Their sons” reported by Gesenius | Secondary report pending direct check |
| Targum Jonathan | Yes, online Aramaic text at vv.31–32 | “In their affliction … lament … wail”; no explicit “sons” | Directly checked versional wording; compatible with mourning sense, not a literal Vorlage claim |
| Rashi | Yes, displayed commentary | Interprets בְּנִיהֶם as “with their wailing” | Directly checked medieval exegesis; not a textual witness |
| Eleven Hebrew manuscripts | No; report only | בְּנֵיהֶם reported by Gesenius | Second-hand; identities and dates unresolved |
| Two early printed editions | No; report only | “Their sons” reported by Bullinger | Second-hand; editions not identified |
| Arabic | No | Reported by Gesenius alongside LXX | Witness/version not identified |
| Vulgate | No | No verified reading for this word obtained | Still unverified; do not cite |

### Updated conclusion

The evidence now shows at least three distinguishable interpretive/textual trajectories:
1. The MT vocalization, understood by BDB, Rashi, and the Targum's rendering as a mourning/wailing expression (although the Targum paraphrases it as “affliction”).
2. The Old Greek's explicit “their sons,” also reported for Syriac and a set of Hebrew manuscripts/early editions.
3. Cornill's proposal, reported by BDB, that “their sons” is a gloss and should be removed.

This makes the textual problem more substantive than a simple choice between two equally transparent Hebrew words. The MT's rare noun is lexically doubtful, while the alternative has clearer Hebrew morphology and explicit ancient versional support. Conversely, the “sons” reading is not unanimous across the ancient versions, and its Hebrew manuscript support remains insufficiently documented. The source MT must remain unchanged, and the adjudication case remains open.

**New direct source:** [Sefaria, Targum Jonathan on Ezekiel 27:31–32](https://www.sefaria.org/Targum_Jonathan_on_Ezekiel.27.31?with=all).  
**Additional interpretive source:** [Ezekiel 27:32 with Rashi and Targum Jonathan](https://fa.israel.fm/texts/ezekiel/27/32/).  
**Secondary manuscript-report source:** [Bullinger, *Companion Bible*, Ezekiel 27](https://www.truthaccordingtoscripture.com/commentaries/bul/ezekiel-27.php).


## 9. Primary-edition pathway for P967 and Göttingen apparatus (2026-11-08)

### P967: the relevant papyrus passage is covered by the Princeton edition

A bibliographic audit has now identified the exact primary edition needed to collate Papyrus 967 at Ezekiel 27:32:

- Allan Chester Johnson, Henry Snyder Gehman, and Edmund Harris Kase, Jr., eds., *The John H. Scheide Biblical Papyri: Ezekiel* (Princeton: Princeton University Press, 1938), Princeton University Studies in Papyrology 3.
- The Princeton leaves preserve Ezekiel 19:12–37:4, with gaps. Ezekiel 27:32 falls within that coverage.
- The edition includes a transcription of the relevant chapters with a critical apparatus and photographic plates.
- Open Library identifies the volume as a 1938, 181-page Princeton University Press publication and records the collection as 21 leaves / 42 pages from the ancient codex. Its catalog links to the Internet Archive item, but the scan could not be opened in this research session.
- A Brill bibliographic appendix independently specifies that the Princeton edition transcribes Ezekiel 19:12–37:4 with critical apparatus. This is the decisive lead for a verse-level collation.

**Important limitation:** the papyrus transcription and apparatus at Ezekiel 27:32 have not yet been read directly. Therefore the present record does not upgrade “P967 reads their sons” from secondary report to independently verified papyrus transcription. The Greek Old Greek wording is independently visible in online transcriptions, but that is not a substitute for the Princeton edition's apparatus.

### Göttingen edition identified

The relevant critical edition is Joseph Ziegler, ed., *Ezechiel*, *Septuaginta: Vetus Testamentum Graecum* XVI/1 (Göttingen: Vandenhoeck & Ruprecht, 1978). The currently marketed Göttingen module explicitly includes Ziegler's critical text and apparatus, with two apparatus modules: one for Greek Old Greek textual evidence and another for Hexaplaric/revision evidence (including material associated with Theodotion).

This confirms the correct edition and its apparatus structure. It does **not** supply the apparatus entry at 27:32; that entry has not been directly inspected. The online Greek transcription's `οἱ υἱοὶ αὐτῶν` should therefore not be conflated with a completed Ziegler apparatus collation.

### P967 dating and provenance: tightened description

The current institutional CSNTM catalogue dates Rahlfs 967 to the third century and describes it as an early-third-century papyrus. The University of Cologne's P967 project describes the codex as produced around 200 CE. Scholarly descriptions vary between late second/early third century and first half of the third century. Use **“around the turn of the third century / early third century”** as a cautious working description; avoid an over-precise single date.

The Princeton edition's publication is especially important because its leaves cover the target passage, whereas the Chester Beatty fragments published by Kenyon cover Ezekiel 11:25–17:21 and do not themselves include chapter 27.

### What this does and does not establish

**Established bibliographically**
- A primary edition exists for the relevant P967 passage.
- Its published coverage includes Ezekiel 27:32.
- It includes a critical apparatus, so the exact papyrus reading and editorial treatment should be recoverable from the volume.
- Ziegler's Göttingen *Ezechiel* (1978) is the correct critical Septuagint edition and contains separate apparatuses for OG and Hexaplaric evidence.

**Not yet established by direct collation**
- The exact P967 line/column and papyrus spelling at Ezekiel 27:32.
- Whether the 1938 editors record any lacuna, correction, supralinear mark, or variant at this word.
- The exact Ziegler apparatus sigla and whether Theodotion is separately attested at this locus.
- The manuscript identities behind Gesenius's eleven Hebrew manuscripts.

### Next exact operations

1. Obtain and inspect Johnson–Gehman–Kase 1938, transcription and apparatus for Ezekiel 27:32; record page, line/column, papyrus reading, editorial supplements, and apparatus sigla.
2. Inspect Ziegler 1978, Ezekiel 27:31–32, both apparatuses; transcribe only the relevant sigla and distinguish OG witnesses from Hexaplaric witnesses.
3. Trace the Gesenius “eleven manuscripts” statement back to its cited source/apparatus, then identify each codex and its date where possible.
4. Only after those checks, revise the witness weighting. Do not close the case solely because the primary editions have been located.

### Sources added in this pass

- [Open Library catalogue: Johnson, Gehman, and Kase, *The John H. Scheide Biblical Papyri: Ezekiel* (1938)](https://openlibrary.org/books/OL6367418M/The_John_H._Scheide_Biblical_papyri_Ezekiel).
- [Brill bibliographic appendix: contents of P967 publications](https://brill.com/previewpdf/book/9789004222458/B9789004222458_009.xml).
- [Princeton University Library Digital PUL: Scheide M 97, Greek Ezekiel papyrus](https://dpul.princeton.edu/global-book-forms/feature/from-papyrus-scroll-to-codex).
- [CSNTM catalogue: Rahlfs 967](https://manuscripts.csntm.org/manuscript/view/Rahlfs_967).
- [University of Cologne: P967 codex description and surviving portions](https://papyri.uni-koeln.de/features/rahlfs).
- [IOSCS overview of critical Septuagint editions and the Göttingen apparatus model](https://septuaginta.uni-goettingen.de/ioscs/editions/).
- [Accordance catalogue entry for Ziegler, *Ezechiel* (Göttingen Septuagint XVI/1, 1978), including its two apparatus modules](https://www.accordancebible.com/product/lxx-gottingen-with-apparatus-ezekiel/).

The adjudication remains **OPEN_TEXT_CRITICAL_REVIEW**. No source text, lexicon entry, YLT wording, alignment, or production database has been modified.
