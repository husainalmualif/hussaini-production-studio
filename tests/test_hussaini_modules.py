#!/usr/bin/env python3
# pylint: disable=wrong-import-position,too-many-lines,no-member
"""Comprehensive Unit & Integration Test Suite for Hussaini Production Studio (V48.5 OMNI-ARCHITECT)."""

import os
import sys
import wave

import numpy as np
from scipy.io import wavfile

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import hussaini_dsp_montage as hds  # noqa: E402


def test_single_source_version_and_v50_purge():
    """Verify V48.5 (Rev 2) version lock, SKILL.md router budget, JSON constitution, and zero V50 files."""
    assert hds.SKILL_VERSION == "V48.5 OMNI-ARCHITECT (Rev 2)"
    skill_md = os.path.join(ROOT_DIR, "SKILL.md")
    assert os.path.isfile(skill_md)
    assert os.path.getsize(skill_md) <= 10500

    cancelled_v50_files = (
        os.path.join(ROOT_DIR, "scripts", "hussaini_omni_v50_extensions.py"),
        os.path.join(ROOT_DIR, "references", "modules", "module_49_arud_bitmask_and_25_poetic_meters.md"),
        os.path.join(ROOT_DIR, "references", "modules", "module_50_melody_composition_and_24edo_guide_synth.md"),
        os.path.join(ROOT_DIR, "references", "modules", "module_51_6dialects_g2p_and_25_atwar_encyclopedia.md"),
        os.path.join(ROOT_DIR, "references", "modules", "module_52_pro_dsp_dynamic_ahaat_and_multi_ai_router.md"),
    )
    for obsolete_path in cancelled_v50_files:
        assert not os.path.exists(obsolete_path)

    constitution = hds.load_v48_5_constitution()
    assert (
        constitution["protocol_metadata"]["protocol_name"]
        == "Hussaini_Production_Studio_OS_V48_5_OMNI_ARCHITECT"
    )
    assert constitution["protocol_metadata"]["skill_version"] == "V48.5 OMNI-ARCHITECT (Rev 2)"
    assert len(constitution["5_master_sound_prompts_library_modules_36_44_46_48_52"]) == 16
    assert len(hds.MASTER_SOUND_PROMPTS_V48_5) == 16


def test_module_41_and_49_iraqi_prosthetic_clusters_and_diphthongs():
    """Verify mandatory Iraqi prosthetic clusters, syncopated nouns, constructs, and unmarked diphthongs."""
    raw = (
        "ياحسين يا بويه بچفك عيوني عيونك بمجلسك بگلبي بگاع خيام بهداي بعفه .. "
        "عالباب للشام العافية حافية فاتحة وسادة ريش دنية خير بس امسح يالمطيني وادم هالحچايه غريبه"
    )
    res = hds.detect_and_shape_dialect(raw)
    assert res["detected_dialect"] == "iraqi"
    assert res["sound_prompt_dialect_declaration"] == "authentic Iraqi colloquial dialect"
    shaped = res["shaped_lyrics"]

    expected_tokens = (
        "يَا إِحْسَينْ",
        "إِبْچَفَّكْ",
        "إِعْيُونِي",
        "إِعْيُونَكْ",
        "إِبْمَجْلِسَكْ",
        "إِبْگَلْبِي",
        "إِبْگَاعْ",
        "إِخْيَامْ",
        "إِبْهِدَايْ",
        "إِبْعِفَّه",
        "إِعْلَه البَابْ",
        "لِلشَّامْ",
        "العَافْيَه",
        "حَافْيَه",
        "فَاتْحَه",
        "وِسَادَتْ رِيشْ",
        "دِنْيَتْ خَيرْ",
        "بَسْ إِمْسَحْ",
        "يَالمِطِّينِي",
        "وَادِمْ",
        "هَلْ حِچَايَه",
        "غَرِيبَه",
    )
    for token in expected_tokens:
        assert token in shaped

    assert "إِحْسَيْنْ" not in shaped
    assert "خَيْرْ" not in shaped
    assert "غَرِيبَهْ" not in shaped


def test_module_49_plain_epenthetic_vowels_and_idempotency():
    """Verify plain initial clusters use soft epenthetic vowels (never word-initial Sukun or إِدْمُوعْ)."""
    raw = "بويه إِدْمُوعْ جْرُوحْ مْتُونِي سْنِينِي تْگِلَّه زَيْنَبْ"
    first_pass = hds.detect_and_shape_dialect(raw)["shaped_lyrics"]
    second_pass = hds.detect_and_shape_dialect(first_pass)["shaped_lyrics"]
    assert first_pass == second_pass
    for clean_tok in ("دُمُوعْ", "جُرُوحْ", "مِتُونِي", "سِنِينِي", "تِگِلَّه", "زَينَبْ"):
        assert clean_tok in first_pass


def test_module_43_and_49_bahrani_vs_neutral_isolation():
    """Verify Pure Bahrani shaping ('عَلَه البَابْ', 'گَلِبْ', 'فَاضِلْ') vs Neutral Tie shaping."""
    bahrani_res = hds.detect_and_shape_dialect("يا بويي ونتي عالباب بقلب وقلبي والصبر ويبوفاضل")
    assert bahrani_res["detected_dialect"] == "bahrani"
    assert bahrani_res["sound_prompt_dialect_declaration"] == "authentic Bahrani colloquial dialect"
    assert "عَلَه البَابْ" in bahrani_res["shaped_lyrics"]
    assert "گَلِبْ" in bahrani_res["shaped_lyrics"]
    assert "گَلْبِي" in bahrani_res["shaped_lyrics"]
    assert "فَاضِلْ" in bahrani_res["shaped_lyrics"]

    neutral_res = hds.detect_and_shape_dialect("ياحسين قلب وقلبي والصبر والجمرة ويبوفاضل")
    assert neutral_res["detected_dialect"] == "iraqi_bahrani"
    assert "قَلْبْ" in neutral_res["shaped_lyrics"]
    assert "قَلْبِي" in neutral_res["shaped_lyrics"]
    assert "فَاضِلْ" in neutral_res["shaped_lyrics"]


def test_module_40_tanween_compiler_colloquial_and_fusha():
    """Verify mid-line phonetic Nunation and pause Tanween resolution before '..'."""
    coll = hds.resolve_dialectal_and_prosodic_tanween("عينٍ تسيل بدمعي .. جرحٍ چبير ..", dialect="iraqi")
    assert "عَينِنْ تِسِيلْ" in coll
    assert "جَرْحِنْ چِبِيرْ .." in coll

    fusha = hds.resolve_dialectal_and_prosodic_tanween(
        "جسماً على الثرى .. قضى ظامئاً ..", dialect="fusha"
    )
    assert "جِسْمَنْ عَلَى الثَّرَى" in fusha
    assert "ظَامِئَا .." in fusha


def test_module_50_crying_isolation_and_anti_12tet_firewall():
    """Verify zero weeping/12-TET leakage in rhythmic prompts and exclusive weeping in 0 BPM Rubato."""
    for key, prompt in hds.MASTER_SOUND_PROMPTS_V48_5.items():
        lower = prompt.lower()
        if key == "minbar_nai_0bpm_rubato_saba_exclusive_weeping":
            assert "weeping" in lower
            assert "rubato" in lower
            continue
        for banned in hds.LATMIYA_SONG_LEAKAGE_BLACKLIST:
            if key == "zanjeel_procession_80bpm_hijaz" and banned == "dammam":
                continue
            assert banned not in lower, f"Leakage '{banned}' found in {key}"

    for genre in ("latmiya", "nasheed", "ibtihalat", "tawashih"):
        prof = hds.build_vocal_genre_profile(genre=genre, dialect="iraqi", maqam="saba", bpm=60)
        assert prof["song_leakage_terms_detected"] == []


def test_module_51_collective_estehlal_and_qc1_to_qc18_linter():
    """Verify collective '(...)' Estehlal wrapper, 5 Golden Pillars auditor, and QC13/14/17/18 linter."""
    raw_poem = "\n".join(
        [
            "[المُسْتَهَلّ]",
            "يَا إِحْسَينْ إِبْگَلْبِي ..",
            "صَوْتَكْ يِسْرِي إِبْدَمِّي ..",
            "مَا أَنْسَى إِخْيَامَكْ ..",
            "يَا سُلْطَانْ إِهْمُومِي ..",
            "[النَّزْلَة الأُولَى]",
            "وُگَفِتْ إِعْلَه البَابْ ..",
            "أَنْظُرْ دَرُبْ الشَّامْ ..",
            "دُمُوعْ إِعْيُونِي تْسِيلْ ..",
            "تِسُولِفْ بِالأَيْتَامْ ..",
            "إِبْچَفَّكْ يَا مَوْلَايْ ..",
            "إِمْسَحْ دَمْعَاتِي ..",
            "إِبْمَجْلِسَكْ أَرْتَاحْ ..",
            "تِشْفَى جُرُوحَاتِي ..",
            "[الكَسْرَة وَالمُسْتَهَلّ]",
            "غَرِيبَه هَلْ حِچَايَه ..",
            "ظَلَّتْ بِالخَرَابَه ..",
            "تِنَادِي يَا بُويَه ..",
            "شُوفْ إِشْ صَارْ إِبْحَالِي ..",
            "يَا إِحْسَينْ إِبْگَلْبِي ..",
            "صَوْتَكْ يِسْرِي إِبْدَمِّي ..",
            "مَا أَنْسَى إِخْيَامَكْ ..",
            "يَا سُلْطَانْ إِهْمُومِي ..",
        ]
    )
    unwrapped_lint = hds.lint_poem(raw_poem)
    assert unwrapped_lint["solo_estehlal_violation"] is True
    assert unwrapped_lint["marked_medial_diphthong_glides_detected"] == ["مَوْلَايْ"]

    repaired = unwrapped_lint["auto_repaired_lyrics"]
    clean_lint = hds.lint_poem(repaired)
    assert clean_lint["solo_estehlal_violation"] is False
    assert clean_lint["inline_json_in_lyrics"] is False
    assert clean_lint["fusha_dialect_clash_detected"] == []
    assert clean_lint["ready_for_generation"] is True

    pillars = hds.audit_legendary_latmiya_pillars(repaired)
    assert pillars["all_five_pillars_passed"] is True
    assert pillars["total_vertical_lines"] == 20

    bad_poem = "[المُسْتَهَلّ]\n{\"bpm\": 60}\nبويه عُيُونِي يا حُسَيْن عَلَى الباب خَيْرْ"
    bad_lint = hds.lint_poem(bad_poem)
    assert bad_lint["inline_json_in_lyrics"] is True
    assert "عُيُونِي" in bad_lint["fusha_dialect_clash_detected"]
    assert "عَلَى" in bad_lint["fusha_dialect_clash_detected"]
    assert "خَيْرْ" in bad_lint["marked_medial_diphthong_glides_detected"]
    assert bad_lint["ready_for_generation"] is False


def test_module_46_48_52_validators_formatters_and_stage_plan(tmp_path):
    """Verify Abudhiyah, Zuhayri, Ashouri, Faujain, Caesura splitter, 4-Stage Plan & Session Logger."""
    abudhiyah = [
        "گلبي بمأتمك يحسين ينصاب ..",
        "وذكرك من يمر الدمع ينصاب ..",
        "گلبي بدال گلبك ريت ينصاب ..",
        "وخدي دون خدك على الوطيه ..",
    ]
    assert hds.validate_abudhiyah_jinas(abudhiyah)["is_valid_abudhiyah"] is True

    zuhayri = [
        "يا صاح دمع الجفن عالخد جرى وسال ..",
        "والگلب من فرگتك ذاب بحزن وسال ..",
        "ما ظل صبر بالصدر عن غربتك وسال ..",
        "بالطف وگفنا بدمع نندب أبو السجاد ..",
        "والشام شافت سبي وآل النبي تنقاد ..",
        "ما تنطفي جمرته لو مرت الأعياد ..",
        "كل ما يمر عاشور دمعي تحدر وسال ..",
    ]
    assert hds.validate_zuhayri_mawal(zuhayri)["is_valid_zuhayri"] is True

    ashouri = hds.format_ashouri_interactive_ahaat("يَا إِحْسَينْ يَا مَظْلُومْ ..")
    assert "(آه .. آه)" in ashouri

    faujain = hds.format_bahrani_antiphonal_faujain(["مَاجُورَه يَا زَهْرَه ..", "بِمُصَابْ أَبُو السَّجَّادْ .."])
    assert "[الفَوْج الأَوَّل]" in faujain and "[الفَوْج الثَّانِي]" in faujain

    split_text = hds.split_long_lines_for_steady_pacing(
        "وُگَفِتْ إِبْمَجْلِسَكْ يَا سَيِّدِي إِعْلَه البَابْ أَنْتَظِرْ", max_words_per_line=4
    )
    for line in split_text.splitlines():
        core = line.replace("..", "").strip()
        assert not core.endswith("إِعْلَه") and not core.endswith("يَا")

    bridge = hds.build_multi_tor_melodic_bridge("tor_ashouri", "tor_lami_iraqi", "saba", "lami", 58)
    assert bridge["common_jins_compatible"] is True

    plan = hds.build_four_stage_latmiya_plan("iraqi")
    assert plan["stage_1_root_track"]["bpm"] == 58
    assert plan["stage_4_extend_3_kasra_finale"]["bpm"] == 56
    assert plan["stage_4_extend_3_kasra_finale"]["audio_drop_sec"] == 3.0

    for sample in (
        "هنيالي من خدمنك خادم مولاي",
        "يا عباس يا كفيل زينب",
        "شور حسين حسين لبيك",
        "يا بويي ونتي بالگلب",
        "بويه شلون دلالي",
    ):
        rec = hds.recommend_tor_and_rhythm_for_poem(sample)
        assert rec["recommended_bpm"] >= 56

    precond = hds.build_flowmusic_json_preconditioning()
    assert precond["reference_clip_id"] is None
    assert precond["session_mode"] == "Pre_Conditioning_Lock_Wait_For_Stage_JSON"

    stage_json = hds.build_stage_orchestration_json(
        "[المُسْتَهَلّ]\nياحسين بگلبي ..\n[النَّزْلَة الأُولَى]\nوگفت عالباب ..\n[الكَسْرَة وَالمُسْتَهَلّ]\nغريبه هالحچايه ..",
        stage_id="stage_1_root",
        title="يَا إِحْسَينْ إِبْگَلْبِي",
        global_bpm=58,
    )
    val_ok = hds.validate_stage_orchestration_json(stage_json)
    assert val_ok["is_valid_stage_json"] is True
    assert val_ok["qc19_passed"] is True
    assert len(stage_json["sections"]) == 3

    for st_id in ("stage_0_fusha_intro", "stage_2_extend_1", "stage_3_extend_2", "stage_4_extend_3"):
        sub_json = hds.build_stage_orchestration_json("يَا إِحْسَينْ ..", stage_id=st_id, global_bpm=58)
        assert hds.validate_stage_orchestration_json(sub_json)["is_valid_stage_json"] is True

    bad_stage = {
        "stage_id": "stage_1_root",
        "sections": [{"section_tag": "[Chorus]", "lyrics_arabic": ["Hello {bad}"]}],
    }
    val_bad = hds.validate_stage_orchestration_json(bad_stage)
    assert val_bad["is_valid_stage_json"] is False
    assert len(val_bad["missing_stage_keys"]) > 0
    assert len(val_bad["section_errors"]) > 0
    assert hds.validate_stage_orchestration_json("bare plain text")["is_valid_stage_json"] is False

    log_file = tmp_path / "session_audit.jsonl"
    rec_log = hds.log_generation_session(str(log_file), "قصيدة الطف", poet_name="شاعر المنبر")
    assert rec_log["living_artist_impersonation"] is False
    assert log_file.is_file()


def test_16_dsp_modes_24bit_wav_profile_and_percussion_cleaning(tmp_path):
    """Verify 8/16/24-bit WAV reading, --extract-profile, --replace-ai-percussion, and all 16 DSP modes."""
    sr = 16000
    t_vec = np.linspace(0.0, 0.8, int(0.8 * sr), endpoint=False)
    vocal = 0.35 * np.sin(2.0 * np.pi * 160.0 * t_vec)

    in_16 = tmp_path / "in_16.wav"
    wavfile.write(str(in_16), sr, (vocal * 32767).astype(np.int16))

    in_8 = tmp_path / "in_8.wav"
    wavfile.write(str(in_8), sr, np.clip((vocal * 127 + 128), 0, 255).astype(np.uint8))
    assert hds.read_wav_any_depth(str(in_8))[3] == "8-bit PCM"

    in_24 = tmp_path / "in_24.wav"
    scaled_24 = np.clip(np.round(vocal * 8388607.0), -8388608, 8388607).astype(np.int32)
    b0 = (scaled_24 & 0xFF).astype(np.uint8)
    b1 = ((scaled_24 >> 8) & 0xFF).astype(np.uint8)
    b2 = ((scaled_24 >> 16) & 0xFF).astype(np.uint8)
    packed_24 = np.column_stack((b0, b1, b2)).tobytes()
    with wave.open(str(in_24), "wb") as wav_out:
        wav_out.setnchannels(1)
        wav_out.setsampwidth(3)
        wav_out.setframerate(sr)
        wav_out.writeframes(packed_24)
    sr_24, mono_24, ch_24, depth_24 = hds.read_wav_any_depth(str(in_24))
    assert sr_24 == sr and ch_24 == 1 and depth_24 == "24-bit PCM"
    assert len(mono_24) == len(vocal)

    prof = hds.extract_reference_audio_profile(str(in_16))
    assert prof["closest_maqam"] in hds.MAQAM_FREQS

    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()
    wavfile.write(str(samples_dir / "latm.wav"), sr, (vocal[:800] * 32767).astype(np.int16))

    for idx, mode in enumerate(hds.SUPPORTED_DSP_MODES):
        out_wav = tmp_path / f"out_{mode}.wav"
        foley_choice = ("none", "wind", "water", "horses")[idx % 4]
        res = hds.process_audio_file(
            str(in_24 if idx == 0 else in_16),
            str(out_wav),
            mode=mode,
            bpm=62.0,
            maqam_drone="saba_zamzam" if idx == 1 else "saba",
            swing=0.18,
            foley=foley_choice,
            audio_drop_sec=0.1 if idx % 3 == 0 else None,
            replace_ai_percussion=(idx % 2 == 0),
            samples_dir=str(samples_dir) if idx == 0 else None,
        )
        assert out_wav.is_file() and out_wav.stat().st_size > 200
        assert res["mode"] == mode

    in_8k = tmp_path / "in_8k.wav"
    t_8k = np.linspace(0.0, 0.5, 4000, endpoint=False)
    wavfile.write(str(in_8k), 8000, (0.3 * np.sin(2.0 * np.pi * 150.0 * t_8k) * 32767).astype(np.int16))
    out_8k = tmp_path / "out_8k.wav"
    assert hds.main(["--input", str(in_8k), "--output", str(out_8k), "--mode", "latm", "--replace-ai-percussion"]) == 0
    assert hds.main(["--compile-lyrics", "ياحسين بچفك عيوني"]) == 0
    assert hds.main(["--lint-poem", "ياحسين يا بويه"]) == 0
    assert hds.main(["--enforce-estehlal", "[المُسْتَهَلّ]\nيَا إِحْسَينْ .."]) == 0
    assert hds.main(["--build-stage-json", "[المُسْتَهَلّ]\nيَا إِحْسَينْ .."]) == 0
    assert hds.main(["--stage-plan", "iraqi"]) == 0
    assert hds.main(["--export-constitution"]) == 0
    assert hds.main(["--extract-profile", str(in_16)]) == 0
