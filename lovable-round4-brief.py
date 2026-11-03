import json, subprocess
msg = """Round 4 changes from the owner (defaults, Read splash, two nav bars, search):

1) DEFAULT PRECEDENCE. Wire a single effective-rendering rule into the choices store:
- Study page: a word shows (a) the reader's custom/preset choice if set, else (b) its Young's (computed) rendering, else (c) its gloss.
- Read page: (a) the reader's choice if set, else (b) KJV.
Each verse's sentence is its base text with effective renderings substituted at their phrases — Study base text is the YLT verse text, Read base text is the KJV verse text. Replace any invented per-word presets with these REAL per-word values from the corpus (KJV | Young's computed):
1:1 bereshit "In the beginning"|"In the beginning"; bara "created"|"preparing"; Elohim "God"|"God"; et: untranslated in both (empty); hashamayim "the heavens"|"the heavens"; ve'et "and"|"and"; ha'aretz "the earth"|"the earth".
1:2 veha'aretz "And the earth"|"the earth"; hayetah "was"|"hath existed"; tohu "without form"|"waste"; vavohu "and void"|"and void"; vechoshekh "and darkness"|"and darkness"; al-penei "upon the face of"|"on the face of"; tehom "the deep"|"the deep"; veruach "And the Spirit"|"and the Spirit"; Elohim "God"|"God"; merachefet "moved"|"fluttering"; hamayim "the waters"|"the waters".
1:3 vayomer "said"|"saith"; Elohim "God"|"God"; yehi "Let there be"|"Let be"; 'or "light"|"light"; vayehi-'or "and there was light"|"and light is".
Add these YLT verse texts to corpus.ts as the Study base sentences: 1:1 "In the beginning of God's preparing the heavens and the earth —" · 1:2 "the earth hath existed waste and void, and darkness [is] on the face of the deep, and the Spirit of God fluttering on the face of the waters," · 1:3 "and God saith, 'Let light be;' and light is."
Card dropdown options become: Young's (computed) [the default], King James, Custom… (round-3 behavior for Custom).

2) READ SPLASH. /read opens with a splash section: a grid of hyperlinks for all 39 books of the Hebrew Bible (Genesis, Exodus, Leviticus, Numbers, Deuteronomy, Joshua, Judges, Ruth, 1 Samuel, 2 Samuel, 1 Kings, 2 Kings, 1 Chronicles, 2 Chronicles, Ezra, Nehemiah, Esther, Job, Psalms, Proverbs, Ecclesiastes, Song of Songs, Isaiah, Jeremiah, Lamentations, Ezekiel, Daniel, Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi). Genesis is live (scrolls to the chapter text); the rest render muted with a "not in sample" tag, not dead links. Above the grid, anchor dropdowns — Book (Genesis), Chapter (1), Verse (1–31) — with a "Go" button that scrolls to that verse's anchor in the KJV chapter text below (verses 1–5 have text; choosing 6–31 shows a small "beyond the sample verses" note at the text). Verse paragraphs get anchor ids.

3) TWO NAV BARS. (a) A site nav bar fixed at the top of every page: the title "Build Your Own Translation" plus links Home · Study · Read · Search. (b) A text nav bar directly beneath it on the Study and Read pages: Book / Chapter / Verse selects plus Prev and Next buttons, wired to the sample (Study: verse sections 1:1–1:3; Read: verse anchors 1–5; out-of-sample selections disabled).

4) SEARCH AS A SEARCH ENGINE. Redesign /search in the style of a search-engine home/results page: centered title, one large rounded query box with a Search button, results as a ranked list (reference in Deep Gold, verse text, similarity score in slate). Keep the round-3 behavior (empty by default; light/dark → sample results; other queries → the honest no-sample note). In corpus.ts, document the SearchResult interface as the contract for the project's own engine: semantic search over the Bible database's verse embeddings (nomic-embed-text, 768-dim, one vector per verse) served by the project's API — the prototype's bundled sample results implement the same interface so the live endpoint swaps in with no UI change. The landing page's search bar should carry its query text into /search.

Keep all earlier behavior not mentioned here. Re-check the build when done and state plainly whether it compiles cleanly."""
args = {"project_id": "c5cc5312-cdbe-4972-a7d8-11c6067b7e75", "message": msg}
p = subprocess.run(["/opt/hatch/bin/lovable", "call-tool", "--name",
                    "send_message", "--arguments-json", json.dumps(args)],
                   capture_output=True, text=True)
print(p.stdout[:1000]); print(p.stderr[:200])
