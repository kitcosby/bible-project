# Twenty legacy positional divergences — contextual decisions (2026-11-06)

This is a manual review of the 20 remaining YLT token records marked legacy_overlap_review after the initial 37-case reconciliation. It uses the stored YLT verse text, token positions, and profile-specific Greek sequence. Decisions are classifications, not automatic acceptance of a production mapping. Legacy rows remain untouched.

## Summary

- phrase_alignment: 2
- idiomatic_article_subject: 1
- article_noun_phrase: 3
- repeated_article_occurrence: 2
- prepositional_phrase: 2
- conjunction_pair: 1
- article_noun_participle_phrase: 1
- articular_infinitive: 1
- pronoun_direct: 1
- article_adjective_noun_phrase: 1
- pronoun_phrase: 1
- articular_participle: 1
- article_prepositional_phrase: 1
- conjunction_verb_phrase: 1
- preposition_direct: 1

## Case-by-case review

### MT 4:13 — YLT token 14 “the”
- Proposed target: την (profile position 9, G3588, T-ASF).
- Legacy position(s): [10]; matching production positions for target form: [3, 9].
- Classification: **phrase_alignment**.
- Assessment: The YLT phrase “by the sea” represents Greek την παραθαλασσιαν (“the seaside”). The article is part of the translated phrase; the legacy position points to the adjective. Preserve both phrase-level and token-level evidence; not a clean one-token conflict.
- YLT verse: and having left Nazareth having come he dwelt at Capernaum that is by the sea in the borders of Zebulun and Naphtalim
- Greek profile sequence: και καταλιπων την ναζαρετ ελθων κατωκησεν εις καπερναουμ την παραθαλασσιαν εν οριοις ζαβουλων και νεφθαλειμ

### MT 18:30 — YLT token 2 “he”
- Proposed target: ο (profile position 1, G3588, T-NSM).
- Legacy position(s): [4]; matching production positions for target form: [1].
- Classification: **idiomatic_article_subject**.
- Assessment: Greek ο δε ουκ ηθελεν has an article-subject construction rendered idiomatically as “and he would not”. The article can underlie “he”, while the legacy verb position also participates in the predicate. Retain as grammatical/phrase alignment, not a simple lexical equivalent.
- YLT verse: and he would not but having gone away he cast him into prison till he might pay that which was owing
- Greek profile sequence: ο δε ουκ ηθελεν αλλα απελθων εβαλεν αυτον εις φυλακην εως ου αποδω το οφειλομενον

### MT 21:11 — YLT token 2 “the”
- Proposed target: οι (profile position 1, G3588, T-NPM).
- Legacy position(s): [3]; matching production positions for target form: [1].
- Classification: **article_noun_phrase**.
- Assessment: Greek οι οχλοι is “the multitudes”; article position 1 and noun position 3 form the phrase. Direct article proposal is sound; legacy noun association is complementary.
- YLT verse: And the multitudes said This is Jesus the prophet who is from Nazareth of Galilee
- Greek profile sequence: οι δε οχλοι ελεγον ουτος εστιν ιησους ο προφητης ο απο ναζαρετ της γαλιλαιας

### LU 1:26 — YLT token 3 “the”
- Proposed target: τω (profile position 3, G3588, T-DSM).
- Legacy position(s): [6]; matching production positions for target form: [3, 5].
- Classification: **repeated_article_occurrence**.
- Assessment: In εν τω εκτω μηνι, YLT “in the sixth month”, the first τω at position 3 belongs with μηνι; the second τω at position 5 belongs with εκτω. Proposed position 3 is correct.
- YLT verse: And in the sixth month was the messenger Gabriel sent by God to a city of Galilee the name of which is Nazareth
- Greek profile sequence: εν δε τω μηνι τω εκτω απεσταλη ο αγγελος γαβριηλ υπο του θεου εις πολιν της γαλιλαιας η ονομα ναζαρετ

### LU 4:16 — YLT token 21 “the”
- Proposed target: τη (profile position 16, G3588, T-DSF).
- Legacy position(s): [18, 19]; matching production positions for target form: [16].
- Classification: **phrase_alignment**.
- Assessment: Greek εν τη ημερα των σαββατων is rendered “on the sabbath-day”. Article τη belongs to ημερα; legacy span [18,19] covers των σαββατων. YLT compounds the phrase; preserve phrase mapping.
- YLT verse: And he came to Nazareth where he hath been brought up and he went in according to his custom on the sabbath-day to the synagogue and stood up to read
- Greek profile sequence: και ηλθεν εις την ναζαρετ ου ην τεθραμμενος και εισηλθεν κατα το ειωθος αυτω εν τη ημερα των σαββατων εις την συναγωγην και ανεστη αναγνωναι

### AC 10:38 — YLT token 28 “the”
- Proposed target: του (profile position 23, G3588, T-GSM).
- Legacy position(s): [24]; matching production positions for target form: [23].
- Classification: **prepositional_phrase**.
- Assessment: Greek υπο του διαβολου is “by the devil”. Proposed του is the article; legacy διαβολου is the noun. Both belong to the same prepositional phrase.
- YLT verse: Jesus who is from Nazareth how God did anoint him with the Holy Spirit and power who went through doing good and healing all those oppressed by the devil because God was with him
- Greek profile sequence: ιησουν τον απο ναζαρετ ως εχρισεν αυτον ο θεος πνευματι αγιω και δυναμει ος διηλθεν ευεργετων και ιωμενος παντας τους καταδυναστευομενους υπο του διαβολου οτι ο θεος ην μετ αυτου

### AC 19:27 — YLT token 31 “and”
- Proposed target: δε (profile position 24, G1161, CONJ).
- Legacy position(s): [25]; matching production positions for target form: [3, 24].
- Classification: **conjunction_pair**.
- Assessment: Greek δε και is rendered “and also”. Proposed δε is compatible with “and”; the following και supports “also”. Legacy position 25 is the second conjunction. Preserve the two-part mapping.
- YLT verse: and not only is this department in danger for us of coming into disregard but also that of the great goddess Artemis the temple is to be reckoned for nothing and also her greatness is about to be brought down whom all Asia and the world doth worship
- Greek profile sequence: ου μονον δε τουτο κινδυνευει ημιν το μερος εις απελεγμον ελθειν αλλα και το της μεγαλης θεας αρτεμιδος ιερον εις ουδεν λογισθηναι μελλειν δε και καθαιρεισθαι την μεγαλειοτητα αυτης ην ολη η ασια και η οικουμενη σεβεται

### AC 21:8 — YLT token 19 “into”
- Proposed target: εις (profile position 14, G1519, PREP).
- Legacy position(s): [14]; matching production positions for target form: [11, 15].
- Classification: **prepositional_phrase**.
- Assessment: Greek εις τον οικον is “into the house”. Proposed εις is the preposition and is the direct equivalent of “into”; legacy position set points elsewhere in the variant-inclusive production sequence.
- YLT verse: and on the morrow Paul and his company having gone forth we came to Caesarea and having entered into the house of Philip the evangelist who is of the seven we remained with him
- Greek profile sequence: τη δε επαυριον εξελθοντες οι περι τον παυλον ηλθον εις καισαρειαν και εισελθοντες εις τον οικον φιλιππου του ευαγγελιστου του οντος εκ των επτα εμειναμεν παρ αυτω

### AC 22:25 — YLT token 13 “the”
- Proposed target: τον (profile position 9, G3588, T-ASM).
- Legacy position(s): [11]; matching production positions for target form: [10].
- Classification: **article_noun_participle_phrase**.
- Assessment: Greek τον εστωτα εκατονταρχον describes “the centurion who was standing”. Proposed article τον introduces the phrase; legacy noun position identifies εκατονταρχον. Retain both phrase components.
- YLT verse: And as he was stretching him with the thongs Paul said unto the centurion who was standing by A man a Roman uncondemned is it lawful to you to scourge
- Greek profile sequence: ως δε προετεινεν αυτον τοις ιμασιν ειπεν προς τον εστωτα εκατονταρχον ο παυλος ει ανθρωπον ρωμαιον και ακατακριτον εξεστιν υμιν μαστιζειν

### AC 26:18 — YLT token 5 “to”
- Proposed target: του (profile position 4, G3588, T-GSN).
- Legacy position(s): [5]; matching production positions for target form: [4, 19].
- Classification: **articular_infinitive**.
- Assessment: Greek του επιστρεψαι is an articular infinitive rendered “to turn”. The proposed article του is part of the infinitival construction and can underlie the English infinitive marker; do not treat this as a literal article gloss.
- YLT verse: to open their eyes to turn them from darkness to light and from the authority of the Adversary unto God for their receiving forgiveness of sins and a lot among those having been sanctified by faith that is toward me
- Greek profile sequence: ανοιξαι οφθαλμους αυτων του επιστρεψαι απο σκοτους εις φως και της εξουσιας του σατανα επι τον θεον του λαβειν αυτους αφεσιν αμαρτιων και κληρον εν τοις ηγιασμενοις πιστει τη εις εμε

### RO 1:27 — YLT token 19 “their”
- Proposed target: αυτων (profile position 16, G846, P-GPM).
- Legacy position(s): [14, 15]; matching production positions for target form: [16, 32].
- Classification: **pronoun_direct**.
- Assessment: Greek αυτων is the possessive/genitive pronoun “their”. Proposed target is direct; legacy positions [14,15] belong to the preceding article+noun phrase τη ορεξει. This is a genuine legacy positional divergence.
- YLT verse: and in like manner also the males having left the natural use of the female did burn in their longing toward one another males with males working shame and the recompense of their error that was fit in themselves receiving
- Greek profile sequence: ομοιως τε και οι αρρενες αφεντες την φυσικην χρησιν της θηλειας εξεκαυθησαν εν τη ορεξει αυτων εις αλληλους αρσενες εν αρσεσιν την ασχημοσυνην κατεργαζομενοι και την αντιμισθιαν ην εδει της πλανης αυτων εν εαυτοις απολαμβανοντες

### 1CO 5:7 — YLT token 4 “the”
- Proposed target: την (profile position 3, G3588, T-ASF).
- Legacy position(s): [4]; matching production positions for target form: [3].
- Classification: **article_adjective_noun_phrase**.
- Assessment: Greek την παλαιαν ζυμην is “the old leaven”. Proposed article την corresponds to “the”; legacy position 4 is the adjective παλαιαν. These are different components of the same phrase.
- YLT verse: cleanse out therefore the old leaven that ye may be a new lump according as ye are unleavened for also our passover for us was sacrificed Christ
- Greek profile sequence: εκκαθαρατε ουν την παλαιαν ζυμην ινα ητε νεον φυραμα καθως εστε αζυμοι και γαρ το πασχα ημων υπερ ημων ετυθη χριστος

### PHP 4:2 — YLT token 12 “same”
- Proposed target: αυτο (profile position 7, G846, P-ASN).
- Legacy position(s): [8]; matching production positions for target form: [7].
- Classification: **pronoun_phrase**.
- Assessment: Greek το αυτο φρονειν expresses “to be of the same mind”. Proposed αυτο contributes “same”; legacy position 8 is the infinitive φρονειν. Phrase-level relationship, not lexical conflict.
- YLT verse: Euodia I exhort and Syntyche I exhort to be of the same mind in the Lord
- Greek profile sequence: ευοδιαν παρακαλω και συντυχην παρακαλω το αυτο φρονειν εν κυριω

### COL 4:11 — YLT token 7 “who”
- Proposed target: οι (profile position 6, G3588, T-NPM).
- Legacy position(s): [7]; matching production positions for target form: [6].
- Classification: **articular_participle**.
- Assessment: Greek οι οντες εκ περιτομης is “who are of the circumcision”. The article οι introduces a substantival participle; proposed “who” is defensible, while legacy participle position is also relevant to the clause.
- YLT verse: and Jesus who is called Justus who are of the circumcision these only are fellow-workers for the reign of God who did become a comfort to me
- Greek profile sequence: και ιησους ο λεγομενος ιουστος οι οντες εκ περιτομης ουτοι μονοι συνεργοι εις την βασιλειαν του θεου οιτινες εγενηθησαν μοι παρηγορια

### COL 4:14 — YLT token 5 “the”
- Proposed target: ο (profile position 6, G3588, T-NSM).
- Legacy position(s): [7]; matching production positions for target form: [4, 6].
- Classification: **repeated_article_occurrence**.
- Assessment: Greek ο ιατρος ο αγαπητος has two articles. YLT “the beloved physician” is most closely associated with the second article at position 6 before αγαπητος; proposed position 6 is correct. Legacy position 7 is adjective αγαπητος.
- YLT verse: Salute you doth Lukas the beloved physician and Demas
- Greek profile sequence: ασπαζεται υμας λουκας ο ιατρος ο αγαπητος και δημας

### COL 4:15 — YLT token 10 “the”
- Proposed target: την (profile position 9, G3588, T-ASF).
- Legacy position(s): [13]; matching production positions for target form: [9].
- Classification: **article_prepositional_phrase**.
- Assessment: Greek την κατ οικον εκκλησιαν is “the assembly in the house”. Proposed article την begins the noun phrase; legacy position 13 is εκκλησιαν, the head noun. Both are valid phrase components.
- YLT verse: salute ye those in Laodicea brethren and Nymphas and the assembly in his house
- Greek profile sequence: ασπασασθε τους εν λαοδικεια αδελφους και νυμφαν και την κατ οικον αυτου εκκλησιαν

### COL 4:16 — YLT token 14 “the”
- Proposed target: τη (profile position 12, G3588, T-DSF).
- Legacy position(s): [14]; matching production positions for target form: [12].
- Classification: **article_noun_phrase**.
- Assessment: Greek εν τη λαοδικεων εκκλησια is “in the assembly of the Laodiceans”. Proposed τη is the article; legacy position 14 is the noun εκκλησια. Preserve both phrase components.
- YLT verse: and when the epistle may be read with you cause that also in the assembly of the Laodiceans it may be read and the epistle from Laodicea that ye also may read
- Greek profile sequence: και οταν αναγνωσθη παρ υμιν η επιστολη ποιησατε ινα και εν τη λαοδικεων εκκλησια αναγνωσθη και την εκ λαοδικειας ινα και υμεις αναγνωτε

### 1TI 3:2 — YLT token 4 “the”
- Proposed target: τον (profile position 3, G3588, T-ASM).
- Legacy position(s): [2]; matching production positions for target form: [3].
- Classification: **article_noun_phrase**.
- Assessment: Greek τον επισκοπον is “the overseer”. Proposed article τον is direct; legacy position 2 is ου(ν), not the article, so this is a likely legacy positional error, pending check against exact production sequence provenance.
- YLT verse: it behoveth therefore the overseer to be blameless of one wife a husband vigilant sober decent a friend of strangers apt to teach
- Greek profile sequence: δει ουν τον επισκοπον ανεπιληπτον ειναι μιας γυναικος ανδρα νηφαλιον σωφρονα κοσμιον φιλοξενον διδακτικον

### JAS 4:13 — YLT token 24 “and”
- Proposed target: και (profile position 18, G2532, CONJ).
- Legacy position(s): [19]; matching production positions for target form: [6, 15, 21, 23, 26].
- Classification: **conjunction_verb_phrase**.
- Assessment: Greek και εμπορευσωμεθα is “and traffic”. Proposed και before the verb corresponds to YLT “and”; legacy position 19 is the verb. Both components of the coordinated predicate are relevant.
- YLT verse: Go now ye who are saying To-day and to-morrow we will go on to such a city and will pass there one year and traffic and make gain
- Greek profile sequence: αγε νυν οι λεγοντες σημερον και αυριον πορευσωμεθα εις τηνδε την πολιν και ποιησωμεν εκει ενιαυτον ενα και εμπορευσωμεθα και κερδησωμεν

### 2PE 2:9 — YLT token 15 “to”
- Proposed target: εις (profile position 9, G1519, PREP).
- Legacy position(s): [13]; matching production positions for target form: [10].
- Classification: **preposition_direct**.
- Assessment: Greek εις ημεραν is “to a day”. Proposed εις is direct; legacy position 13 τηρειν corresponds to “to keep” later in the verse. This is a strong legacy misassignment; preserve legacy row and flag for future repair proposal.
- YLT verse: The Lord hath known to rescue pious ones out of temptation and unrighteous ones to a day of judgment being punished to keep
- Greek profile sequence: οιδεν κυριος ευσεβεις εκ πειρασμου ρυεσθαι αδικους δε εις ημεραν κρισεως κολαζομενους τηρειν

## Disposition

The review supports the proposed Greek target in all 20 cases as a contextually plausible component of the translation, but not always as a one-to-one lexical gloss. Several are article+noun, article+participle, prepositional, or conjunction+verb phrase relationships. The most important likely legacy positional errors are Romans 1:27 (possessive pronoun) and 2 Peter 2:9 (the second “to”, not the later “to keep”); 1 Timothy 3:2 also merits checking because the legacy position points to ου(ν).

No rows were modified during this contextual audit. Preserve phrase-level and token-level distinctions rather than overwriting legacy positions. Before production migration, occurrence-specific position disagreements must be resolved against the exact production source sequence and variant provenance.
