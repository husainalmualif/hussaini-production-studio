#!/usr/bin/env python3
"""Unit Test Suite for Hussaini Production Studio (V45.0 OMNI-ARCHITECT).

Validates:
- Module 41: Anti-Slurring Word De-Cliticization & Separation
- Module 40: Dialect-Accurate & Prosodic Tanween Compiler (e.g. عَيْنِنْ تِسِيلْ)
- Module 43: Automatic Bahrani vs. Iraqi Dialect Identification & Sukun Lock
- Modules 34 & 38: Stage-1 Iso-Syllabic Lock & 4-Line Stanza Refrain Validator
- Module 39 & Section 15: JSON Pre-Conditioning & Multi-Tor Melodic Bridge Builder
- 5-Track DAW Routing, Track_01_Dammam EQ, and -3.0dB Smart Sidechain Ducking
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import hussaini_dsp_montage as engine  # pylint: disable=wrong-import-position


def test_module41_word_separation_anti_slurring():
    """Verify attached vocatives, prepositions, and interrogatives are separated."""
    raw = "ياحسين ويبوفاضل عالباب بغربتي شصار وشنگول للذبحوا والشمس"
    separated = engine.de_cliticize_and_separate_words(raw)
    assert "يَا حْسَيْنْ" in separated
    assert "يَا بُو فَاضِلْ" in separated
    assert "عَلَى البَابْ" in separated
    assert "بِـ غُرْبِتِي" in separated
    assert "إِشْ صَارْ" in separated
    assert "إِشْ نْگُولْ" in separated
    assert "لِلْ ذَبْحَوْا" in separated
    assert "وَ الشَّمْسْ" in separated


def test_module40_dialectal_and_prosodic_tanween():
    """Verify colloquial mid-line Tanween converts to -ِنْ and lines end with Sukun."""
    raw_line = "عينٍ تسيل وجرحٍ چبير وكلٍ ينادي يمظلومُ"
    resolved = engine.resolve_dialectal_and_prosodic_tanween(raw_line, dialect="iraqi")
    assert "عَيْنِنْ تِسِيلْ" in resolved
    assert "جَرْحِنْ چِبِيرْ" in resolved
    assert "كِلِّنْ يِنَادِي" in resolved
    assert resolved.endswith("ْ")


def test_module43_bahrani_vs_iraqi_dialect_detection_and_sukun():
    """Verify automatic recognition and CVC shaping for Bahrani vs. Iraqi dialects."""
    bahrani_poem = "يا بويي ونتي بهالگفره امساعد الله يا قلبي وصبر"
    bahrani_res = engine.detect_and_shape_dialect(bahrani_poem)
    assert bahrani_res["detected_dialect"] == "bahrani"
    assert "گَلْبِي" in bahrani_res["shaped_lyrics"]
    assert "صَبِرْ" in bahrani_res["shaped_lyrics"]
    assert "3rd-Word Faizi Vibrato" in bahrani_res["maqam_articulation_rule"]

    iraqi_poem = "يا خويه يمه وليدي دلالي شلون شصار بلياك قلب وصبر وجمر"
    iraqi_res = engine.detect_and_shape_dialect(iraqi_poem)
    assert iraqi_res["detected_dialect"] == "iraqi"
    assert "گَلُبْ" in iraqi_res["shaped_lyrics"]
    assert "صَبُرْ" in iraqi_res["shaped_lyrics"]
    assert "جَمُرْ" in iraqi_res["shaped_lyrics"]
    assert "Sudden Drop" in iraqi_res["maqam_articulation_rule"]


def test_module34_and_38_iso_syllabic_stage1_lock():
    """Verify Stage-1 4-line stanza structure, identical 4th-line refrain, and iso-syllabic lock."""
    stanzas = [
        "[المُسْتَهَلّ]",
        "يَا بُو السَّجَّادْ دَلَّالِي تِفَطَّرْ .. عِفْتْنِي بِـ غُرْبِتِي وَ الدَّمِعْ يِسْهَرْ",
        "عَيْنِنْ تِسِيلْ وَ الخِيَمْ تِسْعَرْ .. جَرْحِنْ چِبِيرْ بِـ گَلْبِي مَا يِفْتَرْ",
        "إِشْ صَارْ بِنَه يَا ضَوَه المَحْشَرْ .. كِلِّنْ يِنَادِي يَا غَرِيبْ الطَّفْ",
        "يَا حْسَيْنْ يَا مَظْلُومْ يَا مَنْحُورْ",
        "[المَقْطَع الأَوَّل]",
        "عَلَى الرَّمْضَه وْگَفِتْ وَ العَيْنْ تِرْعَاكْ .. إِشْ نْگُولْ لِلْ ذَبْحَوْا ضَوَه مَلْگَاكْ",
        "بِـ ضْلُوعِي جَمُرْ مَا طِفَه بْـ فَرْگَاكْ .. وَ الشَّمْسْ غَابَتْ يَا حِمَى بْلَيَّاكْ",
        "عَلَى البَابْ أَنْتِظِرْ يَا خُويَه مَمْشَاكْ .. حَالِنْ يِفَطِّرْ صَخَرْ هَالوِدْيَانْ",
        "يَا حْسَيْنْ يَا مَظْلُومْ يَا مَنْحُورْ",
    ]
    report = engine.validate_stage1_iso_syllabic_lock(stanzas)
    assert report["is_valid_stanza_grid"] is True
    assert report["identical_4th_line_refrain"] is True
    assert report["iso_syllabic_balanced"] is True
    assert report["passed"] is True


def test_module39_json_preconditioning_and_multi_tor_bridge():
    """Verify JSON Pre-Conditioning payload and Common-Jins Multi-Tor bridge."""
    payload = engine.build_flowmusic_json_preconditioning(dialect="iraqi_bahrani", maqam="saba", bpm=58)
    assert payload["protocol_name"] == "Hussaini_Production_Studio_OS_V45_OMNI_ARCHITECT"
    assert payload["anti_slurring_word_separation"] is True
    assert payload["dialectal_tanween_compiler"] is True

    bridge = engine.build_multi_tor_melodic_bridge("bayati", "kurd", "thaqeel", "shoor")
    assert bridge["common_jins_compatible"] is True
    assert "Stage-2 Melodic Bridge" in bridge["bridge_instruction"]


def test_dsp_5track_daw_and_minus_3db_sidechain_ducking():
    """Verify Track_01_Dammam EQ, -3.0dB Sidechain Ducking, 285ms Dynacord & 3.2s Reverb."""
    sample_rate = 16000
    t_vec = np.linspace(0.0, 1.0, sample_rate, endpoint=False)
    vocal_sig = 0.8 * np.sin(2.0 * np.pi * 220.0 * t_vec)

    duck_curve = engine.compute_smart_sidechain_ducking(vocal_sig, sample_rate, duck_db=-3.0)
    min_gain = float(np.min(duck_curve))
    expected_minus_3db = float(10.0 ** (-3.0 / 20.0))
    assert abs(min_gain - expected_minus_3db) < 0.05

    dammam_out = engine.apply_track01_dammam_eq(vocal_sig, sample_rate)
    assert len(dammam_out) == len(vocal_sig)

    echo_out = engine.apply_dynacord_echo(vocal_sig, sample_rate, delay_ms=285.0)
    reverb_out = engine.apply_husseiniya_reverb(echo_out, sample_rate, rt60=3.2)
    assert len(reverb_out) == len(vocal_sig)
