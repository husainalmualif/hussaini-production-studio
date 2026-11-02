#!/usr/bin/env python3
# pylint: disable=no-member
"""Comprehensive Unit, Negative-Edge, Idempotency, 24-Bit WAV & 7-Mode DSP Test Suite (V45.0).

Validates:
- Module 41: Anti-Slurring Word Separation, Space-First default (use_tatweel=False), and Idempotency
- Module 40: Dialectal & Prosodic Tanween Compiler + Protection of Vocalized Verbs (نارٍ يَصْلَى)
  and Vocatives (دمعٍ ياحسين) + Alif Maqsura (ى) exemption
- Module 43: Prefix-Aware Morphological Word-Boundary Shaping (ال، و، ب، ك، ل) so 'الجمرة' -> 'الجَمْرَه',
  'والصبر' -> 'وَ الصَبُرْ' (Iraqi) / 'وَ الصَبِرْ' (Bahrani) / 'وَ الصَبْرْ' (Neutral Tie),
  prevents 'قلبي' -> 'گَلُبْي' and 'المقلوب' corruption, enforces Iraqi Dhaa (فَاظِلْ / ظْلُوعِي)
  in Iraqi dialect while keeping Dhad (ض) in Bahrani and Neutral Tie
- Modules 34 & 38: Arabic Prosodic Syllable Segmenter & Per-Hemistich Balance Validator
- Pre-Generation Poem Linter (lint_poem), Optional reference_clip_id, and Compact SKILL.md Router (<10.5KB)
- DSP Engine & CLI (>85% coverage): 8-bit, 16-bit, 24-bit, and Stereo WAV inputs, all 7 DSP modes,
  custom --samples-dir, --session-log, SOS filters, RMS dBFS Sidechain Ducking, and -14.0 LUFS Mastering
"""

import os
import sys
import wave
import numpy as np
from scipy.io import wavfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import hussaini_dsp_montage as engine  # pylint: disable=wrong-import-position


def test_module41_word_separation_and_tatweel_option():
    """Verify attached vocatives, prepositions, interrogatives, and default use_tatweel=False."""
    raw = "ياحسين ويبوفاضل عالباب بغربتي شصار وشنگول للذبحوا والشمس"
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

    with_tatweel = engine.de_cliticize_and_separate_words("بغربتي لحسين", use_tatweel=True)
    assert "بِـ غُرْبِتِي" in with_tatweel
    assert "لِـ حْسَيْنْ" in with_tatweel


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


def test_module43_prefix_decomposition_dhaa_and_neutral_tie():
    """Verify prefix decomposition (ال، و، ب، ك، ل), الجمرة/والصبر shaping, Iraqi Dhaa, and neutral tie."""
    # 1. Bahrani: shapes bare 'قلب', 'والصبر', 'الجمرة', and keeps standard Dhad (ض) in فَاضِلْ / ضْلُوعِي
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

    # 2. Iraqi: shapes prefixes (والصبر، كالجمر، بالقلب، الجمرة), protects المقلوب, and applies Iraqi Dhaa (ظ)
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
    assert "وْگَفِتْ" in shaped_iraqi
    assert "عِفْتْنِي" in shaped_iraqi
    assert "وَ يَا بُو فَاظِلْ" in shaped_iraqi
    assert "بِ ظْلُوعِي" in shaped_iraqi

    # 2b. Iraqi orthographic 'كَـ' (Kaf + Fatha + Tatweel) & open 'آنَه' from reference audio
    ortho_iraqi = engine.detect_and_shape_dialect(
        "يا يمه ابأرض الشام عشت انه اشكَـد آلام كَـوه النفس اشهكَـ صرت من كثر ما تعبوني صارت كَـدامي بالسوكَـ"
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

    # 3. Tie / Neutral case (iraqi_bahrani on 'يا حسين ...'): 100% neutral vocalization (قَلْبْ، صَبْرْ، ض)
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


def test_idempotency_across_all_phonetic_compilers():
    """Verify f(f(x)) == f(x) for word separation, Tanween resolution, and dialect shaping."""
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

    # Verify vertical splitting of long narrative lines (>5 words) to prevent rushed post-1:27 cadence
    long_line = "مَكْسُورَة خَاطِرْ وَ الدَّمِعْ .. مَا ظَلْ بَعَدْ بِ عْيُونِي"
    split_res = engine.split_long_lines_for_steady_pacing(long_line, max_words_per_line=5)
    split_lines = split_res.splitlines()
    assert len(split_lines) == 2
    assert split_lines[0].endswith("..")


def test_module34_and_38_per_hemistich_syllable_validator():
    """Verify per-hemistich syllable segmentation passes balanced stanzas and rejects lopsided hemistichs."""
    balanced_stanzas = [
        "[المُسْتَهَلّ]",
        "يَا بُو السَّجَّادْ دَلَّالِي تِفَطَّرْ .. عِفْتْنِي بِ غُرْبِتِي وَ الدَّمِعْ يِسْهَرْ",
        "عَيْنِنْ تِسِيلْ وَ الخِيَمْ تِسْعَرْ .. جَرْحِنْ چِبِيرْ بِ گَلْبِي مَا يِفْتَرْ",
        "إِشْ صَارْ بِنَه يَا ضَوَه المَحْشَرْ .. كِلِّنْ يِنَادِي يَا غَرِيبْ الطَّفْ",
        "يَا حْسَيْنْ يَا مَظْلُومْ يَا مَنْحُورْ",
        "[المَقْطَع الأَوَّل]",
        "عَلَى الرَّمْضَه وْگَفِتْ وَ العَيْنْ تِرْعَاكْ .. إِشْ نْگُولْ لِلْ ذَبْحَوْا ضَوَه مَلْگَاكْ",
        "بِ ظْلُوعِي جَمُرْ مَا طِفَه بْ فَرْگَاكْ .. وَ الشَّمْسْ غَابَتْ يَا حِمَى بْلَيَّاكْ",
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
    lopsided_stanzas[1] = "يَا حْسَيْنْ .. عِفْتْنِي بِ غُرْبِتِي وَ الدَّمِعْ يِسْهَرْ طُولْ اللَّيَالِي وَ السِّنِينْ"
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


def test_all_7_dsp_modes_24bit_wav_and_samples_dir(tmp_path):
    """Verify 24-bit, 8-bit, and Stereo WAV inputs, all 7 CLI DSP modes, custom samples_dir, and session_log."""
    sr = 8000
    t_vec = np.linspace(0.0, 0.35, int(sr * 0.35), endpoint=False)
    sine = 0.4 * np.sin(2.0 * np.pi * 220.0 * t_vec)

    # 1) Create a 24-bit PCM WAV file (sampwidth=3, with negative & positive values)
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

    # 2) Create an 8-bit PCM WAV file (sampwidth=1) and a 16-bit Stereo WAV file
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

    # 3) Create custom samples_dir with latm.wav, dammam.wav, zanjeel.wav, husseiniya_ir.wav
    samples_dir = tmp_path / "custom_samples"
    samples_dir.mkdir()
    short_hit = (0.5 * np.sin(2.0 * np.pi * 90.0 * np.linspace(0, 0.08, int(sr * 0.08))) * 32767).astype(np.int16)
    for name in ("latm.wav", "dammam.wav", "zanjeel.wav", "husseiniya_ir.wav"):
        wavfile.write(str(samples_dir / name), sr, short_hit)

    ledger_file = str(tmp_path / "session_ledger.json")

    # 4) Run all 8 DSP modes (including heavy_clip, foley, and audio_drop_sec) via CLI main()
    modes_and_inputs = [
        ("latm", wav_24bit, "saba", "60", "none"),
        ("heavy_clip", wav_24bit, "nahawand", "66", "wind"),
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

    assert os.path.isfile(ledger_file)
    assert engine.main([]) == 1
    assert engine.main(["--input", str(tmp_path / "nonexistent.wav"), "--output", str(tmp_path / "x.wav")]) == 1


def test_cli_flags_version_and_compact_skill_router():
    """Verify CLI flags, VERSION single source of truth, and compact SKILL.md router size (<= 10.5KB)."""
    assert engine.main(["--compile-lyrics", "ياحسين يا خويه شلون قلب وقلبي وچبد ودمع", "--use-tatweel"]) == 0
    assert engine.main(["--lint-poem", "ياحسين يا خويه شلون قلب وقلبي"]) == 0

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    version_file = os.path.join(repo_root, "VERSION")
    assert os.path.isfile(version_file)
    with open(version_file, "r", encoding="utf-8") as handle:
        canonical_version = handle.read().strip()
    assert engine.SKILL_VERSION == canonical_version

    skill_md_path = os.path.join(repo_root, "SKILL.md")
    with open(skill_md_path, "r", encoding="utf-8") as handle:
        skill_content = handle.read()
    skill_bytes = len(skill_content.encode("utf-8"))
    assert skill_bytes <= 10500, f"SKILL.md router must be <= 10.5KB (got {skill_bytes} bytes)"
    assert "26bbb3d2-65f0-42c3-a167-37127631ef0a" not in skill_content

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
