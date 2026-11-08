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
