# Works Cited — Bible Project

The authorities this project cites: the corpus source texts and lexica the
database is built from, and the academic references designated for the
lexicon and grammar work. Data sources are public-domain per the project
rule (see README.md: "Public-domain sources only. No NIV, no HALOT.").

## Grammar references — academic resources

Designated by Kit Cosby, 2026-11-12, as the project's academic grammar
resources (from his own bookshelf; the reference standard for grammar
questions in the lexicon-and-grammar prong, alongside the corpus's own
morphology data):

- Mounce, William D. *Basics of Biblical Greek Grammar*. Grand Rapids, MI:
  Zondervan. (Copy held in Kit's library; edition not recorded.)
- Pratico, Gary D., and Miles V. Van Pelt. *Basics of Biblical Hebrew
  Grammar*. Grand Rapids, MI: Zondervan. (Copy held in Kit's library;
  edition not recorded.)

## Corpus source authorities

- Open Scriptures Hebrew Bible (OSHB) — Hebrew text and morphology codes;
  the Strong's crosswalk for the `words` table.
- Brown–Driver–Briggs (BDB) — Hebrew lexicon glosses (`glosses` table).
- Strong, James. *The Exhaustive Concordance of the Bible* — Strong's
  numbering, kept as a foreign key into the dictionary forms.
- King James Version (KJV) — English rendering corpus (`kjv_words`,
  `kjv_renderings`).
- Young, Robert. *Young's Literal Translation* (YLT) — the literal English
  rendering the computed-YLT work is measured against.
- Brenton, Lancelot C. L. *The Septuagint with Apocrypha* (1844) — English
  bridge for the Septuagint (LXX) witness layer.
- Robinson, Maurice A. — parsed Textus Receptus Greek New Testament
  (Robinson–Pierpont tradition), the NT Greek basis.
- SBL Greek New Testament (SBLGNT) and the Byzantine textform — NT variant
  witnesses carried in the corpus.
