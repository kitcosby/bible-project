#!/usr/bin/env python3
"""Regression reproductions for pipe-delimited Robinson TR source tokens.

These tests are marked expectedFailure because the current master parser
skips the first reading in these pipe-delimited variant groups. The canonical
librobinson reader selects either first or second variant explicitly; this
fixture specifies the first-variant behavior expected for the primary TR
alignment. When the parser fix is implemented, remove expectedFailure and
keep the assertions as passing regression tests.

Run from the repository root:
    python3 -m unittest eval.test_nt_parser_variants -v
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_nt_under_test", ROOT / "build_nt.py")
BUILD_NT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(BUILD_NT)


class PipeDelimitedTRVariantTests(unittest.TestCase):
    def parse_fixture(self, files):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for code, text in files.items():
                (root / f"{code}.UTR").write_text(text, encoding="utf-8")
            old_dir, old_ids = BUILD_NT.TR_DIR, BUILD_NT.TR2ID
            try:
                BUILD_NT.TR_DIR = str(root)
                BUILD_NT.TR2ID = {"JOH": 43, "COL": 51}
                return BUILD_NT.parse_tr()
            finally:
                BUILD_NT.TR_DIR, BUILD_NT.TR2ID = old_dir, old_ids

    @unittest.expectedFailure
    def test_john_9_21_keeps_autou_variant_as_one_token(self):
        source = (
            "9:21 pws 4459 {ADV-I} de 1161 {CONJ} nun 3568 {ADV} "
            "blepei 991 5719 {V-PAI-3S} ouk 3756 {PRT-N} "
            "oidamen 1492 5758 {V-RAI-1P} h 2228 {PRT} tiv 5101 {I-NSM} "
            "hnoixen 455 5656 {V-AAI-3S} autou 846 {P-GSM} "
            "tous 3588 {T-APM} ofqalmous 3788 {N-APM} hmeis 1473 {P-1NP} "
            "ouk 3756 {PRT-N} oidamen 1492 5758 {V-RAI-1P} "
            "autos 846 {P-NSM} hlikian 2244 {N-ASF} ecei 2192 5719 {V-PAI-3S} "
            "auton 846 {P-ASM} erwthsate 2065 5657 {V-AAM-2P} "
            "autos 846 {P-NSM} peri 4012 {PREP} "
            "| autou 848 | autou 846 | {P-GSM} "
            "lalhsei 2980 5692 {V-FAI-3S}\n"
        )
        parsed = self.parse_fixture({"JOH": source})
        words = parsed[(43, 9, 21)]
        self.assertEqual(len(words), 24)
        self.assertEqual(words[22][1:], ("autou", "G848", None, "P-GSM"))
        self.assertEqual(words[23][1], "lalhsei")

    @unittest.expectedFailure
    def test_colossians_4_10_keeps_barnaba_and_both_morphologies(self):
        source = (
            "4:10 aspazetai 782 5736 {V-PNI-3S} umav 4771 {P-2AP} "
            "aristarcov 708 {N-NSM} o 3588 {T-NSM} "
            "sunaicmalwtov 4869 {A-NSM} mou 1473 {P-1GS} "
            "kai 2532 {CONJ} markov 3138 {N-NSM} o 3588 {T-NSM} "
            "aneyiov 431 {N-NSM} barnaba 921 | {N-GSM} | {N-DSM} | "
            "peri 4012 {PREP} ou 3739 {R-GSM} elabete 2983 5627 {V-2AAI-2P} "
            "entolav 1785 {N-APF} ean 1437 {COND} elqh 2064 5632 {V-2AAS-3S} "
            "prov 4314 {PREP} umav 4771 {P-2AP} dexasqe 1209 5663 {V-ADM-2P} "
            "auton 846 {P-ASM}\n"
        )
        parsed = self.parse_fixture({"COL": source})
        words = parsed[(51, 4, 10)]
        self.assertEqual(len(words), 21)
        self.assertEqual(words[10][1], "barnaba")
        self.assertEqual(words[10][2], "G921")
        self.assertEqual(words[10][4], "N-GSM")


if __name__ == "__main__":
    unittest.main()
