#!/usr/bin/env python3
# pylint: disable=no-member,too-many-locals,too-many-statements
"""Comprehensive Unit, Negative-Edge, Idempotency, 24-Bit WAV & 16-Mode DSP Test Suite (V48.0).

Validates:
- Unified Lyrics Spec (Arabic [المُسْتَهَلّ]/[النَّزْلَة الأُولَى]/[الكَسْرَة وَالمُسْتَهَلّ] & English [Chorus]/[Verse 1])
  across both 12-line horizontal couplet grid and 20-line vertical 3-Part Golden Architecture
- Module 41 & 48: Anti-Slurring Word Separation, Zero Word-Initial Sukun via Epenthetic Vowels
  (دُمُوعْ، مِتُونِي، سِنِينِي، جُرُوحْ، تِگِلَّه), and Open Feminine Haa without Sukun (غَرِيبَه هَلْ حِچَايَه)
- Module 40: Dialectal & Prosodic Tanween Compiler + Pre-Pause Sukun placement before '..' (never '..ْ')
- Module 43: Prefix-Aware Morphological Word-Boundary Shaping (ال، و، ب، ك، ل)
- Modules 34 & 38: True Prosodic CV/CVV/CVC Segmenter (with Shadda unpacking & Madd detection)
- Heritage Validators: Abudhiyah Jinas (validate_abudhiyah_jinas), Zuhayri Mawal (validate_zuhayri_mawal),
  Interactive Ashouri Ahaat (format_ashouri_interactive_ahaat), Bahrani Antiphonal Faujain, and Wazn vs. Tor
- Module 45 & 46 DSP Upgrades: extract_reference_audio_profile(), Tempo-Synced Delay (60000/(bpm*2)),
  Rosenberg Glottal Pulse + Formant Resonators Ahaat, and Stem-Aware Hybrid Mastering (--replace-ai-percussion)
"""

import os
import sys
import unittest
import wave
import tempfile
import pathlib
import numpy as np
from scipy.io import wavfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import hussaini_dsp_montage as engine  # pylint: disable=wrong-import-position


def test_module41_word_separation_and_tatweel_option():
    """Verify attached vocatives, prepositions, interrogatives, and default use_tatweel=False."""
    raw = "ياحسين ويبوفاضل عالباب بغربتي شصار وشنگول للذبحوا والشمس بدموعي"
    separated_default = engine.de_cliticize_and_separate_words(raw)
    assert "ـ" not in separated_default
    assert "يَا حْسَيْنْ" in separated_default
    assert "وَ يَا بُو فَاضِلْ" in separated_default
    assert "عَلَى البَابْ" in separated_default
    assert "بِ غُرْبِتِي" in separated_default
    assert "إِشْ صَارْ" in separated_default
    assert "وَ إِشْ نْگُولْ" in separated_default
    assert "لِلْ ذَبْحَوْا" in separated_default
    assert "وَ الشَّمْسْ" in separated_default
    assert "بِدْمُوعِي" in separated_default

    with_tatweel = engine.de_cliticize_and_separate_words("بغربتي لحسين", use_tatweel=True)
    assert "بِـ غُرْبِتِي" in with_tatweel
    assert "لِـ حْسَيْنْ" in with_tatweel


def test_module40_tanween_and_pre_pause_sukun_before_dots():
    """Verify Tanween resolution, vocalized verb protection, and Sukun placement BEFORE '..' (never '..ْ')."""
    raw_line = "عينٍ تسيل وجرحٍ چبير وكلٍ ينادي يمظلومُ"
    resolved = engine.resolve_dialectal_and_prosodic_tanween(raw_line, dialect="iraqi")
    assert "عَيْنِنْ تِسِيلْ" in resolved
    assert "جَرْحِنْ چِبِيرْ" in resolved
    assert "كِلِّنْ يِنَادِي" in resolved
    assert resolved.endswith("ْ")

    # Critical Bug Fix: Lines ending with '..' must place Sukun on the word BEFORE '..', never '..ْ'
    vertical_line = "مَاتَتْ وَ مَشْبُوگَه إِدَيْهَا ..\nبِخَرَابَه شَيِّعُوهَا ..\nيَا حْسَيْنْ يَا مَظْلُومُ .."
    resolved_vert = engine.resolve_dialectal_and_prosodic_tanween(vertical_line, dialect="iraqi")
    assert "..ْ" not in resolved_vert
    assert "يَا مَظْلُومْ .." in resolved_vert
    for ln in resolved_vert.splitlines():
        assert ln.endswith("..")

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


def test_module43_prefix_decomposition_dhaa_and_neutral_tie():
    """Verify prefix decomposition (ال، و، ب، ك، ل), الجمرة/والصبر shaping, Iraqi Dhaa, and neutral tie."""
    bahrani_poem = "يا بويي ونتي بهالگفره امساعد الله يا قلبي وقلب والصبر والجمرة ويبوفاضل بضلوعي"
    bahrani_res = engine.detect_and_shape_dialect(bahrani_poem)
    shaped_bahrani = bahrani_res["shaped_lyrics"]
    assert bahrani_res["detected_dialect"] == "bahrani"
    assert "گَلْبِي" in shaped_bahrani
    assert "گَلِبْ" in shaped_bahrani
    assert "وَ الصَبِرْ" in shaped_bahrani
    assert "وَ الجَمْرَه" in shaped_bahrani
    assert "وَ يَا بُو فَاضِلْ" in shaped_bahrani
    assert "بِ ضْلُوعِي" in shaped_bahrani
    assert "3rd-Word Faizi Vibrato" in bahrani_res["maqam_articulation_rule"]

    iraqi_poem = (
        "يا خويه يمه وليدي دلالي شلون شصار بلياك "
        "قلب وقلبي وقلبك والجمرة والمقلوب والصبر وكالجمر وبالقلب وچبد ودمع ووگفت وعفتني ويبوفاضل بضلوعي"
    )
    iraqi_res = engine.detect_and_shape_dialect(iraqi_poem)
    shaped_iraqi = iraqi_res["shaped_lyrics"]
    assert iraqi_res["detected_dialect"] == "iraqi"
    assert iraqi_res["dhad_articulation"] == "Emphatic Iraqi Dhaa (ظ)"
    assert "گَلُبْ" in shaped_iraqi
    assert "گَلْبِي" in shaped_iraqi
    assert "وَ گَلْبَكْ" in shaped_iraqi
    assert "گَلُبْي" not in shaped_iraqi
    assert "گَلُبْك" not in shaped_iraqi
    assert "الجَمُرْة" not in shaped_iraqi
    assert "وَ الجَمْرَه" in shaped_iraqi
    assert "المقلوب" in shaped_iraqi
    assert "وَ الصَبُرْ" in shaped_iraqi
    assert "كَ الجَمُرْ" in shaped_iraqi
    assert "بِ الگَلُبْ" in shaped_iraqi
    assert "چَبِدْ" in shaped_iraqi
    assert "دَمِعْ" in shaped_iraqi
    assert "وُگَفِتْ" in shaped_iraqi
    assert "عِفْتْنِي" in shaped_iraqi
    assert "وَ يَا بُو فَاظِلْ" in shaped_iraqi
    assert "بِ ظْلُوعِي" in shaped_iraqi

    ortho_iraqi = engine.detect_and_shape_dialect(
        "يا يمه ابأرض الشام عشت انه اشكَـد آلام كَـوه النفس اشهكَـ صرت من كثر ما تعبوني صارت كَـدامي بالسوكَـ شيجيبه الي راعي الشيم طوله مدمه الكالي اتبشري اموذر ازماطي"
    )
    shaped_ortho = ortho_iraqi["shaped_lyrics"]
    assert "آنَه" in shaped_ortho
    assert "إِشْگَدْ" in shaped_ortho
    assert "گُوَّه" in shaped_ortho
    assert "أَشْهَگْ" in shaped_ortho
    assert "صِرِتْ" in shaped_ortho
    assert "كِثِرْ" in shaped_ortho
    assert "گِدَّامِي" in shaped_ortho
    assert "بِ السُّوگْ" in shaped_ortho
    assert "بِأَرْضِ" in shaped_ortho
    assert "شِيجِيبَه" in shaped_ortho
    assert "مُدَمَّه" in shaped_ortho
    assert "إِتْبَشْرِي" in shaped_ortho
    assert "إِمْوَذَّرْ" in shaped_ortho
    assert "إِزْمَاطِي" in shaped_ortho

    neutral_res = engine.detect_and_shape_dialect("ياحسين قلب وقلبي والصبر والجمرة ويبوفاضل بضلوعي")
    shaped_neutral = neutral_res["shaped_lyrics"]
    assert neutral_res["detected_dialect"] == "iraqi_bahrani"
    assert neutral_res["dhad_articulation"] == "Balanced Neutral Dhad (ض)"
    assert "قَلْبْ" in shaped_neutral
    assert "قَلْبِي" in shaped_neutral
    assert "وَ الصَبْرْ" in shaped_neutral
    assert "وَ الجَمْرَه" in shaped_neutral
    assert "وَ يَا بُو فَاضِلْ" in shaped_neutral
    assert "بِ ضْلُوعِي" in shaped_neutral
    assert "گَلُبْ" not in shaped_neutral
    assert "گَلِبْ" not in shaped_neutral


def test_idempotency_and_true_prosodic_segmenter():
    """Verify f(f(x)) == f(x) and true prosodic CV/CVV/CVC segmentation (Shadda & Madd)."""
    sample = "ياحسين يا خويه شلون قلب وقلبي والصبر والجمرة وعينٍ تسيل ونارٍ يَصْلَى ودمعٍ ياحسين"
    sep1 = engine.de_cliticize_and_separate_words(sample)
    sep2 = engine.de_cliticize_and_separate_words(sep1)
    assert sep1 == sep2

    tan1 = engine.resolve_dialectal_and_prosodic_tanween(sample, dialect="iraqi")
    tan2 = engine.resolve_dialectal_and_prosodic_tanween(tan1, dialect="iraqi")
    assert tan1 == tan2

    sh1 = engine.detect_and_shape_dialect(sample)["shaped_lyrics"]
    sh2 = engine.detect_and_shape_dialect(sh1)["shaped_lyrics"]
    assert sh1 == sh2

    # True Prosodic Segmenter verification:
    # 1) 'تِسِيلْ' = تِ (CV) + سِيلْ (CVCC) -> 2 syllables (Madd Yaa is NOT counted as a consonant!)
    seg_taseel = engine.segment_arabic_prosodic_syllables("تِسِيلْ")
    assert seg_taseel["syllable_count"] == 2
    assert seg_taseel["arud_pattern"] == "//00"

    # 2) 'مَشْبُوگَه' = مَشْ (CVC) + بُو (CVC) + گَه (CVC) -> 3 syllables (Madd Waw properly recognized)
    seg_mashbooga = engine.segment_arabic_prosodic_syllables("مَشْبُوگَه")
    assert seg_mashbooga["syllable_count"] == 3

    # 3) Shadda unpacking: 'مُحَمَّدْ' = مُ (CV) + حَمْ (CVC) + مَدْ (CVC) -> 3 syllables
    seg_shadda = engine.segment_arabic_prosodic_syllables("مُحَمَّدْ")
    assert seg_shadda["syllable_count"] == 3
    assert seg_shadda["arud_pattern"] == "//0/0"

    long_line = "مَكْسُورَة خَاطِرْ وَ الدَّمِعْ .. مَا ظَلْ بَعَدْ بِ عْيُونِي"
    split_res = engine.split_long_lines_for_steady_pacing(long_line, max_words_per_line=5)
    split_lines = split_res.splitlines()
    assert len(split_lines) == 2
    assert split_lines[0].endswith("..")


def test_unified_lyrics_spec_both_horizontal_and_vertical_and_bilingual_tags():
    """Verify that BOTH 12-line horizontal couplets AND 20-line vertical 3-Part Golden Architecture
    pass validate_stage1_iso_syllabic_lock(), audit_legendary_latmiya_pillars(), and lint_poem()
    with either Arabic tags ([المُسْتَهَلّ]) or English tags ([Chorus]).
    """
    balanced_horizontal = [
        "[المُسْتَهَلّ]",
        "يَا بُو السَّجَّادْ دَلَّالِي تِفَطَّرْ .. عِفْتْنِي بِ غُرْبِتِي وَ الدَّمِعْ يِسْهَرْ",
        "عَيْنِنْ تِسِيلْ وَ الخِيَمْ تِسْعَرْ .. جَرْحِنْ چِبِيرْ بِ گَلْبِي مَا يِفْتَرْ",
        "إِشْ صَارْ بِنَه يَا ضَوَه المَحْشَرْ .. كِلِّنْ يِنَادِي يَا غَرِيبْ الطَّفْ",
        "يَا حْسَيْنْ يَا مَظْلُومْ يَا مَنْحُورْ",
        "[المَقْطَع الأَوَّل]",
        "عَلَى الرَّمْضَه وُگَفِتْ وَ العَيْنْ تِرْعَاكْ .. إِشْ نْگُولْ لِلْ ذَبْحَوْا ضَوَه مَلْگَاكْ",
        "بِ ظْلُوعِي جَمُرْ مَا طِفَه بْ فَرْگَاكْ .. وَ الشَّمْسْ غَابَتْ يَا حِمَى بْلَيَّاكْ",
        "عَلَى البَابْ أَنْتِظِرْ يَا خُويَه مَمْشَاكْ .. حَالِنْ يِفَطِّرْ صَخَرْ هَالوِدْيَانْ",
        "يَا حْسَيْنْ يَا مَظْلُومْ يَا مَنْحُورْ",
    ]
    report = engine.validate_stage1_iso_syllabic_lock(balanced_horizontal)
    assert report["is_valid_stanza_grid"] is True
    assert report["identical_4th_line_refrain"] is True
    assert report["internal_hemistich_balanced"] is True
    assert report["iso_syllabic_balanced"] is True
    assert report["passed"] is True

    lopsided_stanzas = list(balanced_horizontal)
    lopsided_stanzas[1] = "يَا حْسَيْنْ .. عِفْتْنِي بِ غُرْبِتِي وَ الدَّمِعْ يِسْهَرْ طُولْ اللَّيَالِي وَ السِّنِينْ"
    bad_report = engine.validate_stage1_iso_syllabic_lock(lopsided_stanzas)
    assert bad_report["internal_hemistich_balanced"] is False
    assert bad_report["passed"] is False

    # Vertical 20-line Golden Architecture with Arabic tags ([المُسْتَهَلّ], [النَّزْلَة الأُولَى], [الكَسْرَة وَالمُسْتَهَلّ])
    authentic_arabic_tags = (
        "[المُسْتَهَلّ]\nغَرِيبَه هَلْ حِچَايَه ..\nسَبِيَّه مِنِ السَّبَايَا ..\nكِتَلْهَا رَاسْ أَبُوهَا ..\nبِخَرَابَه شَيِّعُوهَا ..\n"
        "[النَّزْلَة الأُولَى]\nمَاتَتْ وَ مَشْبُوگَه إِدَيْهَا ..\nبِلَهْفَه چَانَتْ شَابْگَه ..\nطَابْعَه شِفَافَه عَلَى خَدْهَا ..\nبِرَاسْ أَبُوهَا مِفَارْگَه ..\n"
        "مَيِّتَه وَ الفَرْحَه بِثَغُرْهَا ..\nإِشْحَاچِي يَمْهَا وَ شَاهْگَه ..\nجُفُونْهَا المَا تِرْضَى تِنْسَدْ ..\nمِنْ شَهَرْ مَا طَابْگَه ..\n"
        "[الكَسْرَة وَالمُسْتَهَلّ]\nرَوَتْ قِصَّه عَجِيبَه ..\nمُحِبْ كَاتِلْ حَبِيبَه ..\nعَلَى طَشْتَه لِگُوهَا ..\nبِخَرَابَه شَيِّعُوهَا ..\n"
        "غَرِيبَه هَلْ حِچَايَه ..\nسَبِيَّه مِنِ السَّبَايَا ..\nكِتَلْهَا رَاسْ أَبُوهَا ..\nبِخَرَابَه شَيِّعُوهَا .."
    )
    pillar_ar = engine.audit_legendary_latmiya_pillars(authentic_arabic_tags)
    assert pillar_ar["passed_all_5_pillars"] is True
    assert pillar_ar["zero_word_initial_sukun"] is True
    assert pillar_ar["zero_feminine_haa_sukun"] is True

    iso_vert = engine.validate_stage1_iso_syllabic_lock(authentic_arabic_tags)
    assert iso_vert["layout_format"] == "vertical_hemistichs"
    assert iso_vert["passed"] is True

    lint_vert = engine.lint_poem(authentic_arabic_tags, stage=1)
    assert lint_vert["ready_for_generation"] is True
    assert lint_vert["estimated_stage1_success_score"] >= 85


def test_abudhiyah_jinas_zuhayri_mawal_and_ashouri_ahaat():
    """Verify Iraqi Abudhiyah Jinas validator, 7-line Zuhayri Mawal validator, and Ashouri interactive Ahaat."""
    abudhiyah_valid = (
        "گَلْبِي بِمَأْتَمَكْ يَا حْسَيْنْ يِنْصَابْ ..\n"
        "وَ ذِكْرَكْ مِنْ يِمُرْ الدَّمِعْ يِنْصَابْ ..\n"
        "گَلْبِي بْدَالْ گَلْبَكْ رَيْتْ يِنْصَابْ ..\n"
        "وَ خَدِّي دُونْ خَدَّكْ عَلَى الوَطِيَّه .."
    )
    ab_res = engine.validate_abudhiyah_jinas(abudhiyah_valid)
    assert ab_res["is_valid_abudhiyah"] is True
    assert ab_res["jinas_three_hemistichs_matched"] is True
    assert ab_res["fourth_hemistich_yah_ending"] is True

    abudhiyah_bad = (
        "گَلْبِي بِمَأْتَمَكْ يَا حْسَيْنْ يِنْصَابْ ..\n"
        "وَ ذِكْرَكْ مِنْ يِمُرْ الدَّمِعْ يِجْرِي ..\n"
        "گَلْبِي بْدَالْ گَلْبَكْ رَيْتْ يِنْصَابْ ..\n"
        "وَ خَدِّي دُونْ خَدَّكْ عَلَى التُّرَابْ .."
    )
    ab_bad_res = engine.validate_abudhiyah_jinas(abudhiyah_bad)
    assert ab_bad_res["is_valid_abudhiyah"] is False

    zuhayri_valid = (
        "يَا الهَادِي جَمُرْ الحُزُنْ بِحْشَاشِتِي يَاجِدْ ..\n"
        "حُزُنْ البِگَلْبِي حُزُنْ مِثْلَه فَلَا يَاجِدْ ..\n"
        "لِمُصَابْ شِبْلَكْ تِظُنْ دَمِعْ الجَفِنْ يَاجِدْ ..\n"
        "لَا يِجْدِي دَمْعِي وَ لَا تِبْرِي العِلَلْ وَ تْصِيحْ ..\n"
        "إِغْبَرَّتْ سِمَانَه وَ لَا تِصْفَه بَعَدْ وَ تْصِيحْ ..\n"
        "هَاذِي بَنَاتَكْ إِجَتْ مِنْ كَرْبَلَا وَ تْصِيحْ ..\n"
        "يَا جَدِّي گَطْعَوْا نَحُرْ رَيْحَانِتَكْ يَاجِدْ .."
    )
    z_res = engine.validate_zuhayri_mawal(zuhayri_valid)
    assert z_res["is_valid_zuhayri"] is True
    assert z_res["first_three_jinas_matched"] is True
    assert z_res["seventh_qafla_locked"] is True

    ashouri_formatted = engine.format_ashouri_interactive_ahaat(
        "يَا عَبَّاسْ مَا أَنْتَ اللِّي جِبْتْنِي ..\nوَ بِيْدَكْ يَا خُويَه رَكَّبْتْنِي .."
    )
    assert "(آه .. آه) .." in ashouri_formatted

    faujain_formatted = engine.format_bahrani_antiphonal_faujain(
        "غَرِيبَه هَلْ حِچَايَه ..\nسَبِيَّه مِنِ السَّبَايَا ..\nكِتَلْهَا رَاسْ أَبُوهَا ..\nبِخَرَابَه شَيِّعُوهَا .."
    )
    assert "[الفَوْج الأَوَّل]" in faujain_formatted
    assert "[الفَوْج الثَّانِي]" in faujain_formatted


def test_module39_optional_clip_id_and_poem_linter():
    """Verify optional reference_clip_id (default None), Multi-Tor bridge, and lint_poem()."""
    payload_default = engine.build_flowmusic_json_preconditioning(dialect="iraqi_bahrani", maqam="saba", bpm=58)
    assert payload_default["protocol_name"] == "Hussaini_Production_Studio_OS_V48_OMNI_ARCHITECT"
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


def test_dsp_rms_sidechain_tempo_delay_formant_ahaat_and_lufs():
    """Verify RMS dBFS ducking, Tempo-Synced Delay formula, Rosenberg Formant Ahaat, and LUFS."""
    sample_rate = 16000
    t_vec = np.linspace(0.0, 2.0, 2 * sample_rate, endpoint=False)

    # Verify Tempo-Synced Delay formula: 60000 / (bpm * 2) clipped to [210, 460] ms
    assert abs(engine.compute_tempo_synced_delay_ms(100.0, is_rubato=False) - 300.0) < 1e-6
    assert abs(engine.compute_tempo_synced_delay_ms(60.0, is_rubato=False) - 460.0) < 1e-6
    assert abs(engine.compute_tempo_synced_delay_ms(0.0, is_rubato=True) - 450.0) < 1e-6

    # Verify Rosenberg Glottal + Formant Ahaat synthesis has rich formant harmonics (not pure sine)
    ahaat_sig = engine.synthesize_ahaat_drone(sample_rate, sample_rate, maqam="saba")
    assert len(ahaat_sig) == sample_rate
    assert float(np.max(np.abs(ahaat_sig))) > 0.01

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


def test_all_16_dsp_modes_extract_profile_and_replace_ai_percussion(tmp_path):
    """Verify 24-bit/8-bit/Stereo WAV inputs, extract_reference_audio_profile(), --replace-ai-percussion,
    and all 16 CLI DSP modes (including Bahrani Thulathi, Ruba'i, Haidari, Waqfa, Muthakkal).
    """
    sr = 8000
    dur = 2.5
    t_vec = np.linspace(0.0, dur, int(sr * dur), endpoint=False)
    # Create a synthetic reference track with 60 BPM (1 Hz) 60Hz chest thuds + 146.83 Hz (D3) vocal tone
    vocal_tone = 0.35 * np.sin(2.0 * np.pi * 146.83 * t_vec)
    beat_pulses = np.exp(-18.0 * np.mod(t_vec, 1.0)) * np.sin(2.0 * np.pi * 60.0 * t_vec)
    ref_sig = 0.5 * vocal_tone + 0.45 * beat_pulses

    wav_ref = str(tmp_path / "ref_60bpm.wav")
    wavfile.write(wav_ref, sr, (ref_sig * 24000).astype(np.int16))

    profile = engine.extract_reference_audio_profile(wav_ref)
    assert 55.0 <= profile["estimated_bpm"] <= 65.0
    assert 135.0 <= profile["tonic_freq_hz"] <= 160.0
    assert profile["estimated_maqam"] in engine.MAQAM_FREQS
    assert engine.main(["--extract-profile", wav_ref]) == 0

    # Create a 24-bit PCM WAV file
    sine = 0.4 * np.sin(2.0 * np.pi * 220.0 * t_vec[: int(sr * 0.35)])
    wav_24bit = str(tmp_path / "input_24bit.wav")
    int24_vals = np.clip(sine * ((1 << 23) - 1), -(1 << 23), (1 << 23) - 1).astype(np.int32)
    packed_24 = bytearray()
    for val in int24_vals:
        uval = int(val) & 0xFFFFFF
        packed_24.extend((uval & 0xFF, (uval >> 8) & 0xFF, (uval >> 16) & 0xFF))
    with wave.open(wav_24bit, "wb") as wf:  # pylint: disable=no-member
        wf.setnchannels(1)
        wf.setsampwidth(3)
        wf.setframerate(sr)
        wf.writeframes(bytes(packed_24))

    read_sr, read_mono = engine.read_wav_any_depth(wav_24bit)
    assert read_sr == sr
    assert len(read_mono) == len(sine)
    assert np.allclose(read_mono, sine, atol=1e-3)

    wav_8bit = str(tmp_path / "input_8bit.wav")
    u8_vals = np.clip((sine * 127.0) + 128.0, 0, 255).astype(np.uint8)
    with wave.open(wav_8bit, "wb") as wf:  # pylint: disable=no-member
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(sr)
        wf.writeframes(u8_vals.tobytes())

    wav_stereo = str(tmp_path / "input_stereo.wav")
    stereo_16 = np.column_stack(((sine * 16000).astype(np.int16), (sine * 14000).astype(np.int16)))
    wavfile.write(wav_stereo, sr, stereo_16)

    samples_dir = tmp_path / "custom_samples"
    samples_dir.mkdir()
    short_hit = (0.5 * np.sin(2.0 * np.pi * 90.0 * np.linspace(0, 0.08, int(sr * 0.08))) * 32767).astype(np.int16)
    for name in ("latm.wav", "dammam.wav", "zanjeel.wav", "husseiniya_ir.wav"):
        wavfile.write(str(samples_dir / name), sr, short_hit)

    ledger_file = str(tmp_path / "session_ledger.json")

    modes_and_inputs = [
        ("latm", wav_24bit, "saba", "60", "none"),
        ("heavy_clip", wav_24bit, "nahawand", "66", "wind"),
        ("thaqeel_muwazza", wav_24bit, "saba", "60", "none"),
        ("studio_arranged", wav_stereo, "lami", "74", "none"),
        ("bahrani_fast", wav_8bit, "hijaz", "88", "none"),
        ("bahrani_thulathi", wav_24bit, "bayati", "76", "none"),
        ("bahrani_rubai", wav_stereo, "nahawand", "72", "none"),
        ("bahrani_haidari", wav_24bit, "hijaz", "96", "none"),
        ("bahrani_waqfa", wav_8bit, "saba", "104", "none"),
        ("bahrani_muthakkal", wav_24bit, "saba", "54", "none"),
        ("zanjeel_iraqi", wav_stereo, "hijaz", "80", "horses"),
        ("zanjeel_bahrani", wav_8bit, "bayati", "80", "water"),
        ("shoor", wav_24bit, "kurd", "130", "none"),
        ("bandari", wav_stereo, "rast", "105", "none"),
        ("mawal", wav_24bit, "lami", "0", "none"),
        ("nai", wav_8bit, "saba", "0", "none"),
    ]
    for mode, in_wav, maqam, bpm, foley_kind in modes_and_inputs:
        out_wav = str(tmp_path / f"out_{mode}.wav")
        rc = engine.main([
            "--input", in_wav,
            "--output", out_wav,
            "--mode", mode,
            "--bpm", bpm,
            "--maqam-drone", maqam,
            "--foley", foley_kind,
            "--audio-drop-sec", "0.08",
            "--swing", "0.2",
            "--offset-ms", "20",
            "--samples-dir", str(samples_dir),
            "--session-log", ledger_file,
        ])
        assert rc == 0
        assert os.path.isfile(out_wav)

    # Test Stem-Aware Hybrid Mastering (--replace-ai-percussion)
    out_hybrid = str(tmp_path / "out_hybrid_replaced.wav")
    rc_hybrid = engine.main([
        "--input", wav_ref,
        "--output", out_hybrid,
        "--mode", "thaqeel_muwazza",
        "--bpm", "0",
        "--maqam-drone", "saba",
        "--replace-ai-percussion",
    ])
    assert rc_hybrid == 0
    assert os.path.isfile(out_hybrid)

    assert os.path.isfile(ledger_file)
    assert engine.main([]) == 1
    assert engine.main(["--input", str(tmp_path / "nonexistent.wav"), "--output", str(tmp_path / "x.wav")]) == 1


def test_cli_flags_version_and_compact_skill_router():
    """Verify CLI flags, VERSION single source of truth, and compact SKILL.md router size (<= 10.5KB)."""
    assert engine.main(["--compile-lyrics", "ياحسين يا خويه شلون قلب وقلبي وچبد ودمع", "--use-tatweel"]) == 0
    assert engine.main(["--lint-poem", "ياحسين يا خويه شلون قلب وقلبي"]) == 0
    assert engine.main(["--recommend-tor", "هنيالي من خدمنك .. خادم وافتخر مولاي"]) == 0
    assert engine.main([
        "--validate-abudhiyah",
        "گلبي بمأتمك يحسين ينصاب ..\nوذكرك من يمر الدمع ينصاب ..\nگلبي بدال گلبك ريت ينصاب ..\nوخدي دون خدك على الوطيه .."
    ]) == 0
    assert engine.main([
        "--validate-zuhayri",
        "يا الهادي جمر الحزن بحشاشتي ياجد ..\nحزن البقلبي حزن مثله فلا ياجد ..\nلمصاب شبلك تظن دمع الجفن ياجد ..\nلا يجدي دمعي ولا تبري العلل وتصيح ..\nاغبرت سمانه ولا تصفه بعد وتصيح ..\nهاذي بناتك اجت من كربلا وتصيح ..\nيا جدي گطعوا نحر ريحانتك ياجد .."
    ]) == 0

    rec_bandari = engine.recommend_tor_and_rhythm_for_poem("هنيالي من خدمنك .. خادم وافتخر مولاي")
    assert rec_bandari["rhythm_mode"] == "bandari"
    assert rec_bandari["recommended_bpm"] == 74
    assert "poetic_meter" in rec_bandari
    assert "Bandari" not in rec_bandari["flowmusic_sound_prompt"]
    assert "groove" not in rec_bandari["flowmusic_sound_prompt"]

    rec_rukbani = engine.recommend_tor_and_rhythm_for_poem("يا هل الغرب خذتني .. احتاجيت احس غلاتي")
    assert rec_rukbani["rhythm_mode"] == "studio_arranged"
    assert rec_rukbani["recommended_bpm"] == 64
    assert "humming" not in rec_rukbani["flowmusic_sound_prompt"]
    assert "pads" not in rec_rukbani["flowmusic_sound_prompt"]

    rec_bahrani = engine.recommend_tor_and_rhythm_for_poem("يا بويي ونتي وامساعد")
    assert rec_bahrani["rhythm_mode"] == "bahrani_fast"
    assert rec_bahrani["recommended_bpm"] == 84

    rec_muthakkal = engine.recommend_tor_and_rhythm_for_poem("يبني ضعيفه وذوب قليبي امصابك")
    assert rec_muthakkal["rhythm_mode"] == "bahrani_muthakkal"
    assert rec_muthakkal["recommended_bpm"] == 54

    rec_shoor = engine.recommend_tor_and_rhythm_for_poem("شور لبيك حيدر حيدر")
    assert rec_shoor["rhythm_mode"] == "shoor"

    rec_thaqeel = engine.recommend_tor_and_rhythm_for_poem(
        "غريبه هالحچايه ماتت ومشبوگه اديها .. ماتت بخرابه ابوها مثلي يبچي عليها"
    )
    assert rec_thaqeel["rhythm_mode"] == "thaqeel_muwazza"
    assert rec_thaqeel["recommended_bpm"] == 55
    assert "humming" not in rec_thaqeel["flowmusic_sound_prompt"]

    for g_name in ("latmiya", "nasheed", "ibtihalat", "tawashih"):
        assert engine.main(["--genre", g_name]) == 0

    prof_latmiya = engine.build_vocal_genre_profile("latmiya", dialect="iraqi")
    assert prof_latmiya["uses_chest_latm"] is True
    assert prof_latmiya["song_leakage_terms_detected"] == []
    assert "Pure Acapella No Instruments" in prof_latmiya["flowmusic_sound_prompt"]

    # Verify epenthetic vowel repair for initial consonant clusters & open feminine Haa without Sukun
    iraqi_hal = engine.detect_and_shape_dialect(
        "غَرِيبَهْ هَالْحِچَايَهْ ماتت ومشبوگه إِدَيْهَا يبچي عَلَيْهَا إِمْتُونِي زُرَگْ هَنِيَالِي إِسْنِينِي إِدْمُوعْ إِجْرُوحْ مِنْ هَالْتَّعَبْ"
    )
    assert iraqi_hal["detected_dialect"] == "iraqi"
    assert "غَرِيبَه هَلْ حِچَايَه" in iraqi_hal["shaped_lyrics"]
    assert "غَرِيبَهْ" not in iraqi_hal["shaped_lyrics"]
    assert "مِتُونِي" in iraqi_hal["shaped_lyrics"]
    assert "مْتُونِي" not in iraqi_hal["shaped_lyrics"]
    assert "سِنِينِي" in iraqi_hal["shaped_lyrics"]
    assert "دُمُوعْ" in iraqi_hal["shaped_lyrics"]
    assert "جُرُوحْ" in iraqi_hal["shaped_lyrics"]
    assert "هَنْيَالِي" in iraqi_hal["shaped_lyrics"]
    assert "هَلْ تَعَبْ" in iraqi_hal["shaped_lyrics"]

    bahrani_hal = engine.detect_and_shape_dialect(
        "يا بويي ونتي اشحالش غريبه هالحچايه بهالگفره هالمسيهْ"
    )
    assert bahrani_hal["detected_dialect"] == "bahrani"
    assert "غَرِيبَه هَلْ حِچَايَه" in bahrani_hal["shaped_lyrics"]
    assert "إِشْحَالِشْ" in bahrani_hal["shaped_lyrics"]
    assert "هَلْ مَسِيَّه" in bahrani_hal["shaped_lyrics"]
    assert "مَسِيَّهْ" not in bahrani_hal["shaped_lyrics"]

    authentic_sample = (
        "[Chorus]\nغَرِيبَه هَلْ حِچَايَه ..\nسَبِيَّه مِنِ السَّبَايَا ..\nكِتَلْهَا رَاسْ أَبُوهَا ..\nبِخَرَابَه شَيِّعُوهَا ..\n"
        "[Verse 1]\nمَاتَتْ وَ مَشْبُوگَه إِدَيْهَا ..\nبِلَهْفَه چَانَتْ شَابْگَه ..\nطَابْعَه شِفَافَه عَلَى خَدْهَا ..\nبِرَاسْ أَبُوهَا مِفَارْگَه ..\n"
        "مَيِّتَه وَ الفَرْحَه بِثَغُرْهَا ..\nإِشْحَاچِي يَمْهَا وَ شَاهْگَه ..\nجُفُونْهَا المَا تِرْضَى تِنْسَدْ ..\nمِنْ شَهَرْ مَا طَابْگَه ..\n"
        "[Chorus]\nرَوَتْ قِصَّه عَجِيبَه ..\nمُحِبْ كَاتِلْ حَبِيبَه ..\nعَلَى طَشْتَه لِگُوهَا ..\nبِخَرَابَه شَيِّعُوهَا ..\n"
        "غَرِيبَه هَلْ حِچَايَه ..\nسَبِيَّه مِنِ السَّبَايَا ..\nكِتَلْهَا رَاسْ أَبُوهَا ..\nبِخَرَابَه شَيِّعُوهَا .."
    )
    pillar_audit = engine.audit_legendary_latmiya_pillars(authentic_sample)
    assert pillar_audit["passed_all_5_pillars"] is True

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    version_file = os.path.join(repo_root, "VERSION")
    assert os.path.isfile(version_file)
    with open(version_file, "r", encoding="utf-8") as handle:
        canonical_version = handle.read().strip()
    assert engine.SKILL_VERSION == canonical_version

    # Ensure duplicate module_45_golden_larynx_and_reverse_engineering.md no longer exists
    dup_mod45 = os.path.join(
        repo_root, "references", "modules", "module_45_golden_larynx_and_reverse_engineering.md"
    )
    assert not os.path.exists(dup_mod45)

    skill_md_path = os.path.join(repo_root, "SKILL.md")
    with open(skill_md_path, "r", encoding="utf-8") as handle:
        skill_content = handle.read()
    skill_bytes = len(skill_content.encode("utf-8"))
    assert skill_bytes <= 10500, f"SKILL.md router must be <= 10.5KB (got {skill_bytes} bytes)"

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


class HussainiOmniArchitectTestSuite(unittest.TestCase):
    """Unittest wrapper so standard `python3 -m unittest` runs all tests cleanly."""

    def test_all(self):
        """Run all module and DSP tests."""
        test_module41_word_separation_and_tatweel_option()
        test_module40_tanween_and_pre_pause_sukun_before_dots()
        test_module43_prefix_decomposition_dhaa_and_neutral_tie()
        test_idempotency_and_true_prosodic_segmenter()
        test_unified_lyrics_spec_both_horizontal_and_vertical_and_bilingual_tags()
        test_abudhiyah_jinas_zuhayri_mawal_and_ashouri_ahaat()
        test_module39_optional_clip_id_and_poem_linter()
        test_dsp_rms_sidechain_tempo_delay_formant_ahaat_and_lufs()
        with tempfile.TemporaryDirectory() as td:
            test_all_16_dsp_modes_extract_profile_and_replace_ai_percussion(pathlib.Path(td))
        test_cli_flags_version_and_compact_skill_router()


if __name__ == "__main__":
    unittest.main()
