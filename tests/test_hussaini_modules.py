#!/usr/bin/env python3
"""Comprehensive Unit, Negative-Edge, Idempotency & DSP Test Suite (V45.0 OMNI-ARCHITECT).

Validates:
- Module 41: Anti-Slurring Word Separation, Space-vs-Tatweel mode, and Idempotency
- Module 40: Dialectal & Prosodic Tanween Compiler + Protection of Vocalized Verbs (نارٍ يَصْلَى)
  and Vocatives (دمعٍ ياحسين) + Alif Maqsura (ى) exemption
- Module 43: Word-Boundary Morphological Shaping (prevents قلبي -> گَلُبْي and الجمرة -> الجَمُرْة),
  Bahrani bare 'قلب' -> 'گَلِبْ', Iraqi Dhaa option (فَاظِلْ), and Explicit Hybrid Tie Mode
- Modules 34 & 38: Arabic Prosodic Syllable Segmenter & Per-Hemistich Balance Validator
- Pre-Generation Poem Linter (lint_poem) & Optional reference_clip_id in JSON Pre-Conditioning
- DSP Engine: SOS filters, Absolute dBFS RMS Sidechain Ducking (immune to single-clap spikes &
  noise floor), Vectorized Dynacord Echo, and -14.0 LUFS + -1.0 dBTP Mastering
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import hussaini_dsp_montage as engine  # pylint: disable=wrong-import-position


def test_module41_word_separation_and_tatweel_option():
    """Verify attached vocatives, prepositions, interrogatives, and use_tatweel=False."""
    raw = "ياحسين ويبوفاضل عالباب بغربتي شصار وشنگول للذبحوا والشمس"
    separated = engine.de_cliticize_and_separate_words(raw, use_tatweel=True)
    assert "يَا حْسَيْنْ" in separated
    assert "يَا بُو فَاضِلْ" in separated
    assert "عَلَى البَابْ" in separated
    assert "بِـ غُرْبِتِي" in separated
    assert "إِشْ صَارْ" in separated
    assert "إِشْ نْگُولْ" in separated
    assert "لِلْ ذَبْحَوْا" in separated
    assert "وَ الشَّمْسْ" in separated

    no_tatweel = engine.de_cliticize_and_separate_words("بغربتي لحسين", use_tatweel=False)
    assert "ـ" not in no_tatweel
    assert "بِ غُرْبِتِي" in no_tatweel


def test_module40_tanween_and_next_word_protection():
    """Verify Tanween resolution and ensure vocalized verbs (يَصْلَى) & vocatives (ياحسين) are uncorrupted."""
    raw_line = "عينٍ تسيل وجرحٍ چبير وكلٍ ينادي يمظلومُ"
    resolved = engine.resolve_dialectal_and_prosodic_tanween(raw_line, dialect="iraqi")
    assert "عَيْنِنْ تِسِيلْ" in resolved
    assert "جَرْحِنْ چِبِيرْ" in resolved
    assert "كِلِّنْ يِنَادِي" in resolved
    assert resolved.endswith("ْ")

    # Bug 2 edge cases: must NOT produce double diacritics (يَِصْلَى) or Kasra before Alif (يِاحسين)
    edge_vocalized = engine.resolve_dialectal_and_prosodic_tanween("نارٍ يَصْلَى", dialect="iraqi")
    assert "يَِ" not in edge_vocalized
    assert "نارِنْ يَصْلَى" in edge_vocalized
    assert edge_vocalized.endswith("ى")
    assert not edge_vocalized.endswith("ىْ")

    edge_vocative = engine.resolve_dialectal_and_prosodic_tanween("دمعٍ ياحسين", dialect="iraqi")
    assert "يِا" not in edge_vocative
    assert "دمعِنْ يَا حْسَيْنْ" in edge_vocative

    fusha_line1 = "جسماً على الثرى"
    resolved_fusha1 = engine.resolve_dialectal_and_prosodic_tanween(fusha_line1, dialect="fusha")
    assert "جِسْمَنْ عَلَى الثَّرَى" in resolved_fusha1
    assert resolved_fusha1.endswith("ى")

    fusha_line2 = "دامٍ بلا قبورٍ .. يقضي ظامئاً"
    resolved_fusha2 = engine.resolve_dialectal_and_prosodic_tanween(fusha_line2, dialect="fusha")
    assert "دَامِنْ بِلَا قُبُورْ" in resolved_fusha2
    assert resolved_fusha2.endswith("ظَامِئَا")


def test_module43_word_boundary_negative_cases_and_dialects():
    """Verify word-boundary shaping prevents قلبي->گَلُبْي and الجمرة->الجَمُرْة, and handles Bahrani/Iraqi/Hybrid."""
    # Bahrani: both bare 'قلب' and suffixed 'قلبي' are shaped properly
    bahrani_poem = "يا بويي ونتي بهالگفره امساعد الله يا قلبي وقلب وصبر"
    bahrani_res = engine.detect_and_shape_dialect(bahrani_poem)
    assert bahrani_res["detected_dialect"] == "bahrani"
    assert "گَلْبِي" in bahrani_res["shaped_lyrics"]
    assert "گَلِبْ" in bahrani_res["shaped_lyrics"]
    assert "صَبِرْ" in bahrani_res["shaped_lyrics"]
    assert "3rd-Word Faizi Vibrato" in bahrani_res["maqam_articulation_rule"]

    # Iraqi: bare CVC nouns vs. suffixed/derived words (Bug 1 negative cases)
    iraqi_poem = (
        "يا خويه يمه وليدي دلالي شلون شصار بلياك "
        "قلب وقلبي وقلبك والجمرة والمقلوب وصبر وجمر وچبد ودمع ووگفت وعفتني"
    )
    iraqi_res = engine.detect_and_shape_dialect(iraqi_poem)
    shaped_iraqi = iraqi_res["shaped_lyrics"]
    assert iraqi_res["detected_dialect"] == "iraqi"
    assert "گَلُبْ" in shaped_iraqi
    assert "گَلْبِي" in shaped_iraqi
    assert "گَلْبَكْ" in shaped_iraqi
    assert "گَلُبْي" not in shaped_iraqi
    assert "گَلُبْك" not in shaped_iraqi
    assert "الجَمُرْة" not in shaped_iraqi
    assert "الجمرة" in shaped_iraqi
    assert "المقلوب" in shaped_iraqi
    assert "صَبُرْ" in shaped_iraqi
    assert "جَمُرْ" in shaped_iraqi
    assert "چَبِدْ" in shaped_iraqi
    assert "دَمِعْ" in shaped_iraqi
    assert "وْگَفِتْ" in shaped_iraqi
    assert "عِفْتْنِي" in shaped_iraqi

    # Iraqi emphatic Dhaa option (Bug 3)
    dhaa_res = engine.detect_and_shape_dialect("يا خويه يبوفاضل بضلوعي", enforce_iraqi_dhaa=True)
    assert "يَا بُو فَاظِلْ" in dhaa_res["shaped_lyrics"]
    assert "بِـ ظْلُوعِي" in dhaa_res["shaped_lyrics"]

    # Tie / Hybrid case (iraqi_bahrani): does NOT silently force Iraqi گَلُبْ
    hybrid_res = engine.detect_and_shape_dialect("قلب وصبر ودمع")
    assert hybrid_res["detected_dialect"] == "iraqi_bahrani"
    assert "گَلِبْ" in hybrid_res["shaped_lyrics"]
    assert "گَلُبْ" not in hybrid_res["shaped_lyrics"]
    assert "Hybrid Iraqi-Bahrani Fusion" in hybrid_res["maqam_articulation_rule"]


def test_idempotency_across_all_phonetic_compilers():
    """Verify f(f(x)) == f(x) for word separation, Tanween resolution, and dialect shaping."""
    sample = "ياحسين يا خويه شلون قلب وقلبي وعينٍ تسيل ونارٍ يَصْلَى ودمعٍ ياحسين"
    sep1 = engine.de_cliticize_and_separate_words(sample)
    sep2 = engine.de_cliticize_and_separate_words(sep1)
    assert sep1 == sep2

    tan1 = engine.resolve_dialectal_and_prosodic_tanween(sample, dialect="iraqi")
    tan2 = engine.resolve_dialectal_and_prosodic_tanween(tan1, dialect="iraqi")
    assert tan1 == tan2

    sh1 = engine.detect_and_shape_dialect(sample)["shaped_lyrics"]
    sh2 = engine.detect_and_shape_dialect(sh1)["shaped_lyrics"]
    assert sh1 == sh2


def test_module34_and_38_per_hemistich_syllable_validator():
    """Verify per-hemistich syllable segmentation passes balanced stanzas and rejects lopsided hemistichs."""
    balanced_stanzas = [
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
    report = engine.validate_stage1_iso_syllabic_lock(balanced_stanzas)
    assert report["is_valid_stanza_grid"] is True
    assert report["identical_4th_line_refrain"] is True
    assert report["internal_hemistich_balanced"] is True
    assert report["iso_syllabic_balanced"] is True
    assert report["passed"] is True

    # Negative case: line with short 1st hemistich and very long 2nd hemistich must be rejected
    lopsided_stanzas = list(balanced_stanzas)
    lopsided_stanzas[1] = "يَا حْسَيْنْ .. عِفْتْنِي بِـ غُرْبِتِي وَ الدَّمِعْ يِسْهَرْ طُولْ اللَّيَالِي وَ السِّنِينْ"
    bad_report = engine.validate_stage1_iso_syllabic_lock(lopsided_stanzas)
    assert bad_report["internal_hemistich_balanced"] is False
    assert bad_report["passed"] is False


def test_module39_optional_clip_id_and_poem_linter():
    """Verify optional reference_clip_id (default None), Multi-Tor bridge, and lint_poem()."""
    payload_default = engine.build_flowmusic_json_preconditioning(dialect="iraqi_bahrani", maqam="saba", bpm=58)
    assert payload_default["protocol_name"] == "Hussaini_Production_Studio_OS_V45_OMNI_ARCHITECT"
    assert payload_default["reference_clip_id"] is None

    payload_custom = engine.build_flowmusic_json_preconditioning(
        dialect="iraqi", maqam="saba", bpm=58, reference_clip_id="custom-clip-123"
    )
    assert payload_custom["reference_clip_id"] == "custom-clip-123"

    bridge = engine.build_multi_tor_melodic_bridge("bayati", "kurd", "thaqeel", "shoor")
    assert bridge["common_jins_compatible"] is True

    mixed_poem = "إنما ياحسين شلون قلبي"
    lint_res = engine.lint_poem(mixed_poem, stage=1)
    assert lint_res["fusha_colloquial_mixing_in_stage1"] is True
    assert "ياحسين" in lint_res["slurring_risks_detected"]
    assert lint_res["ready_for_generation"] is False


def test_dsp_rms_sidechain_spike_immunity_and_lufs():
    """Verify RMS dBFS ducking ignores noise floor, ducks normal voice even after a clap spike, and normalizes LUFS."""
    sample_rate = 16000
    t_vec = np.linspace(0.0, 2.0, 2 * sample_rate, endpoint=False)

    # 0.0-0.5s: quiet noise floor (-48 dBFS), 0.5-0.52s: 1.0 clap spike, 0.7-1.8s: normal vocal (0.28 amp)
    signal = 0.004 * np.sin(2.0 * np.pi * 200.0 * t_vec)
    signal[int(0.5 * sample_rate) : int(0.52 * sample_rate)] = 1.0
    signal[int(0.7 * sample_rate) : int(1.8 * sample_rate)] = 0.28 * np.sin(
        2.0 * np.pi * 220.0 * t_vec[int(0.7 * sample_rate) : int(1.8 * sample_rate)]
    )

    duck_curve = engine.compute_smart_sidechain_ducking(signal, sample_rate, duck_db=-3.0)
    noise_region_gain = float(np.mean(duck_curve[int(0.1 * sample_rate) : int(0.4 * sample_rate)]))
    vocal_region_gain = float(np.mean(duck_curve[int(1.0 * sample_rate) : int(1.5 * sample_rate)]))
    expected_minus_3db = float(10.0 ** (-3.0 / 20.0))

    assert noise_region_gain > 0.97
    assert abs(vocal_region_gain - expected_minus_3db) < 0.06

    stereo_test = np.column_stack((signal, signal))
    mastered = engine.normalize_lufs_and_true_peak(stereo_test, sample_rate, target_lufs=-14.0, ceiling_dbtp=-1.0)
    assert float(np.max(np.abs(mastered))) <= float(10.0 ** (-1.0 / 20.0)) + 1e-3


def test_cli_flags_and_single_source_version():
    """Verify CLI --compile-lyrics and --lint-poem flags and VERSION single source of truth."""
    assert engine.main(["--compile-lyrics", "ياحسين يا خويه شلون قلب وقلبي وچبد ودمع"]) == 0
    assert engine.main(["--lint-poem", "ياحسين يا خويه شلون قلب وقلبي"]) == 0

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    version_file = os.path.join(repo_root, "VERSION")
    assert os.path.isfile(version_file)
    with open(version_file, "r", encoding="utf-8") as handle:
        canonical_version = handle.read().strip()
    assert engine.SKILL_VERSION == canonical_version

    for rel_path in (
        "SKILL.md",
        "README.md",
        os.path.join("references", "atwar_maqamat_and_poetry_guide.md"),
        os.path.join("references", "radoods_and_khutaba_encyclopedia.md"),
    ):
        full_path = os.path.join(repo_root, rel_path)
        with open(full_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        assert canonical_version in content, f"Missing {canonical_version} in {rel_path}"
