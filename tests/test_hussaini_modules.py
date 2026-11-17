#!/usr/bin/env python3
# pylint: disable=wrong-import-position,too-many-lines,no-member,too-few-public-methods
"""Comprehensive Unit & Integration Test Suite for Hussaini Production Studio (V55.0 OMNI-ARCHITECT)."""

import os
import re
import struct
import sys
import wave

import numpy as np

try:
    from scipy.io import wavfile
except ImportError:  # pragma: no cover - pure-NumPy WAV writer fallback
    class _WavfileFallback:
        """Pure-Python/NumPy RIFF WAV writer matching scipy.io.wavfile.write."""

        @staticmethod
        def write(filename, rate, data):
            """Write uint8, int16, or float32 mono/stereo array to RIFF WAV."""
            arr = np.asarray(data)
            chans = 1 if arr.ndim == 1 else int(arr.shape[1])
            if arr.dtype == np.float32:
                raw = arr.astype("<f4").tobytes()
                fmt_chunk = struct.pack(
                    "<HHIIHH", 3, chans, int(rate), int(rate) * chans * 4, chans * 4, 32
                )
                riff_sz = 36 + len(raw)
                with open(filename, "wb") as fh:
                    fh.write(
                        b"RIFF"
                        + struct.pack("<I", riff_sz)
                        + b"WAVEfmt "
                        + struct.pack("<I", 16)
                        + fmt_chunk
                    )
                    fh.write(b"data" + struct.pack("<I", len(raw)) + raw)
                return
            sampwidth = 1 if arr.dtype == np.uint8 else 2
            payload = arr.tobytes() if sampwidth == 1 else arr.astype("<i2").tobytes()
            with wave.open(str(filename), "wb") as wf:
                wf.setnchannels(chans)
                wf.setsampwidth(sampwidth)
                wf.setframerate(int(rate))
                wf.writeframes(payload)

    wavfile = _WavfileFallback()

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import hussaini_dsp_montage as hds  # noqa: E402


def test_single_source_version_and_v50_architecture():
    """Verify V55.0 OMNI-ARCHITECT version lock, SKILL.md router budget, JSON constitution, and Module 70."""
    assert hds.SKILL_VERSION == "V55.0 OMNI-ARCHITECT"
    skill_md = os.path.join(ROOT_DIR, "SKILL.md")
    assert os.path.isfile(skill_md)
    assert os.path.getsize(skill_md) <= 10500

    cancelled_legacy_files = (
        os.path.join(ROOT_DIR, "references", "hussaini_os_v48_5_constitution.json"),
        os.path.join(ROOT_DIR, "scripts", "hussaini_omni_v50_extensions.py"),
        os.path.join(ROOT_DIR, "references", "modules", "module_49_arud_bitmask_and_25_poetic_meters.md"),
        os.path.join(ROOT_DIR, "references", "modules", "module_50_melody_composition_and_24edo_guide_synth.md"),
        os.path.join(ROOT_DIR, "references", "modules", "module_51_6dialects_g2p_and_25_atwar_encyclopedia.md"),
        os.path.join(ROOT_DIR, "references", "modules", "module_52_pro_dsp_dynamic_ahaat_and_multi_ai_router.md"),
    )
    for obsolete_path in cancelled_legacy_files:
        assert not os.path.exists(obsolete_path)

    v50_module_doc = os.path.join(
        ROOT_DIR,
        "references",
        "modules",
        "module_54_to_65_v50_super_algorithm_and_175_corpus.md",
    )
    v51_module_doc = os.path.join(
        ROOT_DIR,
        "references",
        "modules",
        "module_66_v51_field_evaluation_consultation_and_style_taxonomy.md",
    )
    v52_module_doc = os.path.join(
        ROOT_DIR,
        "references",
        "modules",
        "module_67_v52_pure_vocal_dsp_corpus_phonetics_and_history.md",
    )
    v53_module_doc = os.path.join(
        ROOT_DIR,
        "references",
        "modules",
        "module_68_v53_dual_corpus_flow_bahrani_iraqi_mastery.md",
    )
    v54_module_doc = os.path.join(
        ROOT_DIR,
        "references",
        "modules",
        "module_69_v54_175_mp3_acoustic_lab_24edo_and_studio_dsp.md",
    )
    v55_module_doc = os.path.join(
        ROOT_DIR,
        "references",
        "modules",
        "module_70_v55_tabaa_al_bashar_7exp_lab_5stage_router_and_3poem_benchmark.md",
    )
    assert os.path.isfile(v50_module_doc)
    assert os.path.isfile(v51_module_doc)
    assert os.path.isfile(v52_module_doc)
    assert os.path.isfile(v53_module_doc)
    assert os.path.isfile(v54_module_doc)
    assert os.path.isfile(v55_module_doc)

    constitution = hds.load_v50_0_constitution()
    assert (
        constitution["protocol_metadata"]["protocol_name"]
        == "Hussaini_Production_Studio_OS_V50_0_OMNI_ARCHITECT"
    )
    assert constitution["protocol_metadata"]["skill_version"] == "V55.0 OMNI-ARCHITECT"
    assert len(constitution["5_master_sound_prompts_library_modules_36_44_46_48_52"]) == 25
    assert len(hds.MASTER_SOUND_PROMPTS_V50) == 25
    assert len(constitution["8_v50_empirical_175_corpus_and_9_schools_modules_54_65"]["unified_9_schools_architecture"]) == 9
    assert len(hds.SUPPORTED_DSP_MODES) == 18
    assert "vocal_pure_master" in hds.SUPPORTED_DSP_MODES
    assert "fazzaiya" in hds.SUPPORTED_DSP_MODES
    assert len(hds.EXTENDED_ATWAR_PROMPTS_V52) == 6
    v51_block = constitution["v51_0_protocol_negative_constraints_and_style_taxonomy"]
    assert v51_block["version"] == "V51.2 OMNI-ARCHITECT"
    assert len(v51_block["permanent_negative_constraints_nc1_to_nc17"]) >= 17
    v52_block = constitution["v52_0_module_67_upgrades"]
    assert v52_block["version"] == "V52.0 OMNI-ARCHITECT"
    assert v52_block["supported_dsp_modes_count"] == 18
    v53_block = constitution["v53_0_module_68_upgrades"]
    assert v53_block["version"] == "V53.0 OMNI-ARCHITECT"
    assert v53_block["dual_corpus_benchmark"]["idempotency_failures"] == 0
    v54_block = constitution["v54_0_module_69_upgrades"]
    assert v54_block["version"] == "V54.0 OMNI-ARCHITECT"
    assert v54_block["mp3_175_track_acoustic_lab"]["tracks_analyzed"] == 175
    v55_block = constitution["v55_0_module_70_upgrades"]
    assert v55_block["version"] == "V55.0 OMNI-ARCHITECT"
    assert v55_block["tabaa_al_bashar_7_experiments_lab"]["experiments_executed"] == 7
    assert v55_block["three_benchmark_poems_verification"]["unvocalized_tokens"] == 0


def test_module_41_49_57_58_64_iraqi_prosthetic_clusters_and_v50_g2p_locks():
    """Verify selective Iraqi prosthetic clusters (QC33), syncopated nouns, V50/V51.2 G2P locks (NC3-NC16)."""
    raw = (
        "ياحسين يا بويه بچفك بچدم عيوني عيونك بمجلسك بگلبي بگاع خيام بهداي بهيبه بسبي بعفه .. "
        "عالباب للشام العافية حافية فاتحة وسادة ريش دنية خير بس امسح يالمطيني وادم هالحچايه غريبه "
        "مآتمنه في طف كربلا يا جد ثارك بطه والقائم رسم ركضت أشكال "
        "صوت أم البنين يصيح لمن رد ابن حذلم ردت نشده انجسم نصين يبشر گطعت إفادي ما أنشدك علأولادي"
    )
    res = hds.detect_and_shape_dialect(raw)
    assert res["detected_dialect"] == "iraqi"
    assert res["sound_prompt_dialect_declaration"] == "authentic Iraqi colloquial dialect"
    shaped = res["shaped_lyrics"]

    expected_tokens = (
        "يَا إِحْسَينْ",
        "إِبْچَفَّكْ",
        "إِبْچِدَمْ",
        "إِعْيُونِي",
        "إِعْيُونَكْ",
        "إِبْمَجْلِسَكْ",
        "إِبْگَلْبِي",
        "إِبْگَاعْ",
        "خِيَامْ",
        "إِبْهِدَايْ",
        "إِبْهَيبَه",
        "إِبْسَبِي",
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
        "مَآتِمْنَا",
        "فِي طَفِّ كَرْبَلَا",
        "يَا جَدْ ثَارَكْ أَبْطَا",
        "وَالْقَايِمْ رَسَمْ",
        "رِكْضَتْ أَشْكَالْ",
        "صُوتْ أُمِّ البَنِينْ يِصِيحْ",
        "لَمَّنْ رَدْ إِبِنْ حَذْلَمْ",
        "رِدَتْ نَشْدَه",
        "انْگِسَمْ نُصَّينْ",
        "بِشِرْ گَطَّعِتْ إِفَّادِي",
        "مَا أَنْشِدَكْ إِعْلَه أَولَادِي",
    )
    for token in expected_tokens:
        assert token in shaped

    kasra_5_lines = [
        "[الكَسْرَة الثَّانِيَة]",
        "صَاحَتْ وَالدَّمِعْ بَادِي ..",
        "بِشِرْ گَطَّعِتْ إِفَّادِي ..",
        "مَا أَنْشِدَكْ عَلَى أَوْلَادِي ..",
        "عَلَى إِحْسَيْنْ النَّشِدْ كِلَّه .. اشْتَاگَيْتْ أَنْظُرْ لْخَدَّه ..",
        "(عَلَى إِحْسَيْنْ النَّشِدْ كِلَّه .. اشْتَاگَيْتْ أَنْظُرْ لْخَدَّه)",
    ]
    formatted_kasra = hds.format_kasra_three_vertical_lines(kasra_5_lines)
    assert len(formatted_kasra) == 4
    assert formatted_kasra[0] == "[الكَسْرَة الثَّانِيَة]"
    assert formatted_kasra[1] == "صَاحَتْ وَالدَّمِعْ بَادِي .. بِشِرْ گَطَّعِتْ إِفَّادِي .."
    assert formatted_kasra[2] == "مَا أَنْشِدَكْ عَلَى أَوْلَادِي .."
    assert "عَلَى إِحْسَيْنْ النَّشِدْ كِلَّه" in formatted_kasra[3]

    assert "إِحْسَيْنْ" not in shaped
    assert "خَيْرْ" not in shaped
    assert "غَرِيبَهْ" not in shaped
    assert "إِخْيَامْ" not in shaped


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
    assert "مَوْلَايْ" in unwrapped_lint["marked_medial_diphthong_glides_detected"]

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
    assert val_ok["qc29_verbatim_passed"] is True
    assert val_ok["qc30_single_stanza_passed"] is True
    assert len(stage_json["sections"]) == 3
    assert len(stage_json["lyrics_register_verbatim"]) >= 6

    for st_id in ("stage_0_fusha_intro", "stage_2_extend_1", "stage_3_extend_2", "stage_4_extend_3"):
        sub_json = hds.build_stage_orchestration_json("يَا إِحْسَينْ ..", stage_id=st_id, global_bpm=58)
        assert hds.validate_stage_orchestration_json(sub_json)["is_valid_stage_json"] is True

    overcrowded_extend = hds.build_stage_orchestration_json(
        "\n".join(["[النَّزْلَة الثَّانِيَه]"] + ["يَا إِحْسَينْ إِبْگَلْبِي .."] * 20),
        stage_id="stage_2_extend_1",
        global_bpm=58,
    )
    val_over = hds.validate_stage_orchestration_json(overcrowded_extend)
    assert val_over["is_valid_stage_json"] is False
    assert val_over["qc30_single_stanza_passed"] is False

    orphan_lint = hds.lint_poem("[النَّزْلَة الأُولَى]\nمَرَّيتْ إِبْنَهَرْ عَلْقَمِي ..\nوَنَادَيتَه ..")
    assert len(orphan_lint["orphan_single_word_lines_detected"]) == 1
    assert orphan_lint["ready_for_generation"] is False

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


def test_v52_float32_wav_ebu_r128_pure_master_and_audit(tmp_path):
    """Verify 32-bit Float WAV I/O, EBU R128 loudness, vocal_pure_master trim/fade, and --audit-audio."""
    sr = 16000
    t_vec = np.linspace(0.0, 2.2, int(sr * 2.2), endpoint=False)
    mono_sig = 0.28 * np.sin(2.0 * np.pi * 190.0 * t_vec) + 0.14 * np.sin(2.0 * np.pi * 55.0 * t_vec)
    stereo_f32 = np.column_stack((mono_sig, 0.92 * mono_sig)).astype(np.float32)

    in_f32 = tmp_path / "in_f32.wav"
    wavfile.write(str(in_f32), sr, stereo_f32)

    read_sr, read_st, chans, depth = hds.read_wav_any_depth(str(in_f32), return_stereo=True)
    assert read_sr == sr
    assert chans == 2
    assert depth == "32-bit Float"
    assert read_st.shape == stereo_f32.shape

    raw_stats = hds.measure_ebu_r128_loudness(read_st, sr)
    assert -30.0 < raw_stats["integrated_lufs"] < -5.0

    # Verify short-clip O(N) boxcar smoothing never mismatches array lengths
    short_clip = mono_sig[:600]
    assert len(hds.strip_ai_percussion_from_vocal(short_clip, sr)) == 600
    assert len(hds.compute_smart_sidechain_ducking(short_clip, sr)) == 600

    out_pure = tmp_path / "out_pure_v52.wav"
    res = hds.process_audio_file(
        str(in_f32),
        str(out_pure),
        mode="vocal_pure_master",
        bpm=60,
        trim_end_sec=1.6,
        fade_out_sec=0.35,
        no_synth_rhythm=True,
    )
    assert res["pure_vocal_master"] is True
    audit = hds.audit_rendered_audio(str(out_pure))
    assert audit["duration_sec"] == 1.6
    assert abs(audit["integrated_lufs"] - res["integrated_lufs"]) <= 0.1
    assert abs(audit["true_peak_dbtp"] - res["true_peak_dbtp"]) <= 0.1
    assert audit["true_peak_dbtp"] <= -0.9
    assert audit["tail_last_150ms_dbfs"] < -24.0
    assert audit["abrupt_tail_cutoff_risk"] is False
    assert audit["broadcast_compliant"] is True
    assert hds.main(["--audit-audio", str(out_pure)]) == 0


def test_v52_corpus_phonetics_kaf_daad_sanitization_and_idempotency():
    """Verify V52 decorator sanitization, Swash-Kaf/kaf-tanween Gaf normalization, Daad/Dhaa & idempotency."""
    sanitized = hds.sanitize_poem_decorations("۞ [المستهل] 💔 صَوتْ أم البنين — ..\nالشاعر: فلان")
    assert "[المستهل]" in sanitized
    assert "💔" not in sanitized
    assert "فلان" not in sanitized

    gaf_norm = hds.normalize_iraqi_orthographic_gaf("كًلبي کلب گعدت \u06AA\u064E\u0640ال")
    assert gaf_norm.startswith("گلبي")
    assert "\u06AA" not in gaf_norm

    daad_norm = hds.normalize_daad_dhaa_homographs("ضل يبچي على الضلع")
    assert "ظَلْ" in daad_norm
    assert "الضلع" in daad_norm

    fusha_res = hds.detect_and_shape_dialect("إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ وَجِسْمًا طَاهِرًا")
    assert fusha_res["detected_dialect"] in ("fusha", "iraqi_bahrani", "iraqi")

    colloquial_poem = "[النزلة]\nوي اهلي ويه وياي وياهم واليه ..\nوعلى الحرام اخت القمر .."
    first = hds.detect_and_shape_dialect(colloquial_poem)["shaped_lyrics"]
    second = hds.detect_and_shape_dialect(first)["shaped_lyrics"]
    assert first == second


def test_v52_historical_verifier_stage_planner_and_atwar_routing():
    """Verify --verify-history, --plan-stages NC16 partitioner, and Fazzaiya/Tawashih routing."""
    clean_poem = (
        "[المستهل]\nصوت أم البنين يصيح يبن حذلم\n"
        "[الكوبليه الأول]\nيا ناشد على الطف وعندك علم\nأربع إخوة راحوا وما ظل سهم\n"
        "يا عباس عالعلگمي والمشرعة"
    )
    hist_ok = hds.verify_historical_narratives(clean_poem)
    assert hist_ok["is_historically_clean"] is True
    assert hist_ok["historical_accuracy_score"] == 100
    assert any(m["motif_id"] == "umm_al_banin_madina" for m in hist_ok["verified_authentic_motifs"])
    assert "الإرشاد للشيخ المفيد" in hist_ok["canonical_sources"]

    hist_bad = hds.verify_historical_narratives("أم البنين بالخيم بكربلا وشفت عرس القاسم")
    assert hist_bad["is_historically_clean"] is False
    assert len(hist_bad["distortions_and_warnings"]) >= 2

    plan = hds.plan_poem_extend_stages(clean_poem, target_method="both", bpm=60)
    assert plan["extend_stages"]
    assert all(blk["nc16_three_line_compliant"] for blk in plan["extend_stages"])
    assert all("method_2_pad_warning" in blk for blk in plan["extend_stages"])
    assert "vocal_pure_master" in plan["mastering_recommendation"]

    faz = hds.recommend_tor_and_rhythm_for_poem("فزاعية حماس گوم وياي")
    assert faz["recommended_dsp_mode"] == "fazzaiya"
    assert faz["recommended_bpm"] == 84
    assert "Fazzaiya" in faz["master_sound_prompt"]

    taw = hds.recommend_tor_and_rhythm_for_poem("تواشيح أهل الكساء صل على محمد")
    assert taw["recommended_dsp_mode"] == "vocal_pure_master"
    assert taw["recommended_bpm"] == 86
    assert "Tawashih" in taw["master_sound_prompt"]

    assert hds.main(["--verify-history", clean_poem]) == 0
    assert hds.main(["--plan-stages", clean_poem]) == 0


def test_v53_dual_corpus_bahrani_iraqi_ear_locks_and_audio_profiler(tmp_path):
    """Verify V53 Kashida healing, Tawshih guard, QC34 pre-Hamza lock, Bahrani isolation, 11 Muqatila rules & profiler."""
    raw_social = (
        "المجموعة الرابعة\n"
        "اللهم صل على محمد وال محمد وعجل فرجهم\n"
        "●●●●●●●●●●●●\n"
        "لــو مــا وجـهـته كــربلة •.•.• إبأرض الشام ما بگت خوان\n"
        "✍ مـوسـى الخـادم\n"
        "#قصائد_السبي_محرم_الحرام_١٤٤٤_هـ"
    )
    sanitized = hds.sanitize_poem_decorations(raw_social)
    assert "لــو" not in sanitized and "ل و" not in sanitized
    assert "لو ما وجهته كربلة" in sanitized
    assert "اللهم صل" not in sanitized and "●●●●" not in sanitized

    shaped_res = hds.detect_and_shape_dialect(sanitized)
    shaped = shaped_res["shaped_lyrics"]
    assert "بِأَرْضِ" in shaped and "إِبْأَرْضِ" not in shaped
    assert "بِگَتْ" in shaped and "إِخْوَانْ" in shaped

    # Ensure banner 'صل على' or vocalized Fazzaiya header routes accurately
    rec_latm = hds.recommend_tor_and_rhythm_for_poem("اللهم صل على محمد وال محمد\n[فَزَّاعِيَّة]\nوسفه كربلا سبي")
    assert rec_latm["recommended_dsp_mode"] == "fazzaiya"
    assert rec_latm["recommended_bpm"] == 84
    assert len(rec_latm["recommended_maqam_progression"]) == 4
    assert "الفزاعية" in rec_latm["detected_poetic_wazn_ar"]

    # Bahrani 2nd-fem '-ish' isolation and standard Dhad preservation
    bahr = hds.detect_and_shape_dialect("عَلَه التَّلْ عيونش وگلبش يا خويي فاضل")
    assert bahr["detected_dialect"] == "bahrani"
    assert "عِيُونِشْ" in bahr["shaped_lyrics"] and "گَلْبِشْ" in bahr["shaped_lyrics"]
    assert "فَاضِلْ" in bahr["shaped_lyrics"]

    # Idempotency with ماضل + بكلبي + Kaf-Fatha inflections
    p_idem = "ماضل بكلبي وكال الكمر .. بلحضه هالضلام واضلوعنه"
    pass1 = hds.detect_and_shape_dialect(p_idem)["shaped_lyrics"]
    pass2 = hds.detect_and_shape_dialect(pass1)["shaped_lyrics"]
    assert pass1 == pass2
    assert "بِگَلْبِي" in pass1 or "إِبْگَلْبِي" in pass1
    assert "گَالْ" in pass1 and "الگَمَرْ" in pass1
    assert "لَحْظَه" in pass1 and "هَلظَّلَامْ" in pass1 and "أَضْلُوعْنَه" in pass1

    # Expanded Muqatila & Aqida rules
    hv = hds.verify_historical_narratives(
        "ألف جرح وتسعميه .. تقل كن فيكون .. شرب الماي العباس .. رقية ماتت بكربلا"
    )
    rule_ids = {w["rule_id"] for w in hv["distortions_and_warnings"]}
    assert {
        "legendary_wound_count_1900",
        "ghuluw_divine_attribution",
        "abbas_drinking_water_claim",
        "ruqayyah_died_in_karbala_error",
    }.issubset(rule_ids)
    assert hds.verify_historical_narratives("العباس ما شرب الماي على العلقمي")["is_historically_clean"] is True

    # Windowed Baritone f0 median & BPM profiler accuracy check
    sr = 16000
    dur = 4.0
    t_arr = np.linspace(0.0, dur, int(sr * dur), endpoint=False)
    beat_hz = 85.0 / 60.0
    env = 0.35 + 0.65 * (0.5 * (1.0 + np.cos(2.0 * np.pi * beat_hz * t_arr))) ** 6
    sig = 0.25 * env * np.sin(2.0 * np.pi * 147.0 * t_arr)
    wav_test = tmp_path / "prof_85bpm.wav"
    wavfile.write(str(wav_test), sr, (sig * 32767).astype(np.int16))
    prof = hds.extract_reference_audio_profile(str(wav_test))
    assert 80 <= prof["estimated_bpm"] <= 90
    assert 140.0 <= prof["estimated_fundamental_hz"] <= 155.0
    assert prof["recommended_dsp_mode"] == "fazzaiya"
    assert prof["integrated_lufs"] == prof["integrated_lufs_approx"]


def test_v54_175track_dsp_deesser_optical_stereo_24edo_and_multi_tor(tmp_path):
    """Verify V54 De-Esser, Optical Compressor, Stereo Reverb, 24-EDO Saba/Bayati, active participles & 9-School Router."""
    # 1. Active participle فَاعِلْ Kasra, 'آهْ' Sukun preservation, 'وَلَوْ' prefix guard & idempotency
    poem = "إحسين آه .. يَا سِرّ عَطَاء خالق وصادق .. ولو هل دمع"
    p1 = hds.detect_and_shape_dialect(poem)["shaped_lyrics"]
    p2 = hds.detect_and_shape_dialect(p1)["shaped_lyrics"]
    assert p1 == p2
    assert "آهْ" in p1
    assert "خَالِقْ" in p1 and "صَادِقْ" in p1
    assert "وَ لَوْ" in p1 and "وَ لِ وَ" not in p1

    # 2. Substring 'شور' inside 'عاشور' never triggers Shoor; Bahrani service retains Bahrani dialect
    bahr_thul = hds.recommend_tor_and_rhythm_for_poem(
        "عاشور ظل جمرة بألم\nوالراية ترفرف بالعزم\nعيونش يزينب تنادي\nگلبش صبر"
    )
    assert bahr_thul["detected_dialect"] == "bahrani"
    assert bahr_thul["recommended_dsp_mode"] == "bahrani_thulathi"
    assert bahr_thul["recommended_bpm"] == 76
    assert "Bahrani" in bahr_thul["master_sound_prompt"]

    # Abudhiyah Jinas & Hosa & Short ecstatic Shoor routing
    abud = hds.recommend_tor_and_rhythm_for_poem(
        "دمع عيني على الخدين جاري\nوطيفك بالليل ما فارگ جاري\nأنا المذبوح والمگطوع جاري\nعلى التربان مرمي بالغاضريه"
    )
    assert abud["recommended_dsp_mode"] == "nai" and abud["recommended_bpm"] == 0
    shoor_ec = hds.recommend_tor_and_rhythm_for_poem("عشگ مجنون\nحبيب حسين\nلأجلك ذوب\nياسر النور")
    assert shoor_ec["recommended_dsp_mode"] == "shoor" and shoor_ec["recommended_bpm"] == 132
    hosa = hds.recommend_tor_and_rhythm_for_poem("[هوسة]\nنضل للماي المشرعة نردها")
    assert hosa["recommended_bpm"] == 88 and "Hosa" in hosa["master_sound_prompt"]

    # 3. Arabic De-Esser (5.5-8.5kHz attenuation) & Optical Vocal Compressor
    sr = 44100
    t_s = np.linspace(0.0, 1.0, sr, endpoint=False)
    sib_test = 0.15 * np.sin(2.0 * np.pi * 180.0 * t_s) + 0.35 * np.sin(2.0 * np.pi * 6800.0 * t_s)
    deessed = hds.apply_arabic_deesser(sib_test, sr)
    hi_before = float(np.sqrt(np.mean(hds.butter_filter(sib_test, [5500.0, 8500.0], sr, btype="band") ** 2)))
    hi_after = float(np.sqrt(np.mean(hds.butter_filter(deessed, [5500.0, 8500.0], sr, btype="band") ** 2)))
    assert hi_after < 0.72 * hi_before

    dyn_sig = np.concatenate([0.08 * np.sin(2.0 * np.pi * 180.0 * t_s[: sr // 2]), 0.65 * np.sin(2.0 * np.pi * 180.0 * t_s[: sr // 2])])
    leveled = hds.apply_optical_vocal_compressor(dyn_sig, sr)
    ratio_before = float(np.max(np.abs(dyn_sig[sr // 2 :]))) / max(float(np.max(np.abs(dyn_sig[: sr // 2]))), 1e-6)
    ratio_after = float(np.max(np.abs(leveled[sr // 2 :]))) / max(float(np.max(np.abs(leveled[: sr // 2]))), 1e-6)
    assert ratio_after < ratio_before

    # 4. 24-EDO Maqam Saba (bin 8) vs Bayati (bin 10) harmonic discrimination & Stereo Decorrelated Tail Fade
    dur_m = 2.4
    tm = np.linspace(0.0, dur_m, int(sr * dur_m), endpoint=False)
    tonic = 146.83
    notes = [
        tonic,
        tonic * (2.0 ** (3.0 / 24.0)),   # E-half-flat (neutral 2nd)
        tonic * (2.0 ** (5.0 / 24.0)),   # F
        tonic * (2.0 ** (8.0 / 24.0)),   # G-flat (Saba diminished 4th!)
        tonic * (2.0 ** (8.0 / 24.0)),
        tonic,
    ]
    seg_len = len(tm) // len(notes)
    saba_sig = np.zeros_like(tm)
    for idx_n, f_note in enumerate(notes):
        sl = slice(idx_n * seg_len, (idx_n + 1) * seg_len)
        tv = tm[sl]
        saba_sig[sl] = 0.28 * (np.sin(2 * np.pi * f_note * tv) + 0.5 * np.sin(2 * np.pi * 2 * f_note * tv) + 0.25 * np.sin(2 * np.pi * 3 * f_note * tv))
    saba_wav = tmp_path / "saba_24edo.wav"
    wavfile.write(str(saba_wav), sr, (saba_sig * 32767).astype(np.int16))
    prof_saba = hds.extract_reference_audio_profile(str(saba_wav))
    assert prof_saba["closest_maqam"] == "saba"
    assert "maqam_top3_candidates" in prof_saba and "crest_factor_db" in prof_saba

    out_stereo = tmp_path / "saba_v54_master.wav"
    hds.process_audio_file(str(saba_wav), str(out_stereo), mode="thaqeel_muwazza", bpm=58, maqam_drone="saba", fade_out_sec=0.5)
    _, st_arr, _, _ = hds.read_wav_any_depth(str(out_stereo), return_stereo=True)
    assert not np.allclose(st_arr[:, 0], st_arr[:, 1])  # True stereo decorrelation!
    au_saba = hds.audit_rendered_audio(str(out_stereo))
    assert au_saba["broadcast_compliant"] is True
    assert au_saba["abrupt_tail_cutoff_risk"] is False and au_saba["tail_last_150ms_dbfs"] < -35.0


def test_v55_three_benchmark_poems_g2p_5stage_router_and_nc18_nc22():
    """Verify V55 Module 70: NC18-NC22 locks, 5-Stage Prosodic Router, and 3-Poem Benchmark (100% G2P & Idempotency)."""
    # 1. Verify NC18 & NC19 on V55 prompts and preconditioning JSON
    for p_key in ("ashura_majlis_noha_58bpm_saba_lami_v55", "pure_acapella_weeping_noha_auto_bpm_saba_lami_v55"):
        prompt_str = hds.EXTENDED_ATWAR_PROMPTS_V52[p_key]
        assert "55Hz" not in prompt_str and "53Hz" not in prompt_str and "320ms" not in prompt_str
        assert "chest slaps" not in prompt_str.lower() and "no drums" not in prompt_str.lower()
        assert "strictly no musical instruments" in prompt_str.lower()

    pre = hds.build_flowmusic_json_preconditioning()
    assert "Lyria 3.5" in pre["acoustic_lock"]["lyria_model_lock"]
    assert pre["acoustic_lock"]["remix_cover_strength_cap"] <= 0.45

    # 2. Verify NC21 (short-clause pause healing) & NC22 (liaison Kasra & open -a before الـ) + morphological fixes
    tabaa_sample = (
        "طبع البشر ينسه الوفه\n"
        "بس انته مو مثل البشر\n"
        "ناموسك بظل العرش\n"
        "وتنزل هوى للمختنگ\n"
        "والخدمه بالصدگ وجذب\n"
        "الخدمه انكساري .. ودمعتي\n"
        "الخدمه قراري .. بصفنتي .. مولاي\n"
        "حامل جمرتي .. بديه\n"
        "وتطلع حسرتي .. الرقيه .. مولاي\n"
        "سهرانه عينك بالدمع\n"
        "وسهرانه عيني بلا دمع\n"
        "تاليها مطرت .. حوافر\n"
        "وروحك تعلت .. بواتر .. مولاي\n"
        "صار الطفل رزقه السهم .. والنار مرزوقه بمهد .. خيل عشره"
    )
    res_tabaa = hds.detect_and_shape_dialect(tabaa_sample)
    assert res_tabaa["detected_dialect"] == "iraqi"
    s_tabaa = res_tabaa["shaped_lyrics"]
    assert hds.detect_and_shape_dialect(s_tabaa)["shaped_lyrics"] == s_tabaa
    assert "طَبْعِ البَشَرْ يِنْسَى الوَفَا" in s_tabaa
    assert "بَسْ إِنْتَ مُو مِثِلِ البَشَرْ" in s_tabaa
    assert "نَامُوسَكْ" in s_tabaa and "نِامُوسَكْ" not in s_tabaa
    assert "بِالصِّدِگْ" in s_tabaa and "بِالدَّمِعْ" in s_tabaa and "بِلَا دَمِعْ" in s_tabaa
    assert "عَينَكْ" in s_tabaa and "عِينَكْ" not in s_tabaa
    assert "الخِدْمَه إِنْكِسَارِي وَ دَمْعِتِي" in s_tabaa
    assert "الخِدْمَه قَرَارِي بِصَفْنِتِي .. مَولَايْ" in s_tabaa
    assert "الرُّقَيَّه .. مَولَايْ" in s_tabaa
    assert "تَالِيهَا مِطْرَتْ حَوَافِرْ" in s_tabaa
    assert "بَوَاتِرْ" in s_tabaa and "بُواتَرْ" not in s_tabaa

    rec_tabaa = hds.recommend_tor_and_rhythm_for_poem(tabaa_sample)
    assert rec_tabaa["recommended_bpm"] == 58
    assert rec_tabaa["recommended_maqam"] == "saba_zamzam"
    assert "five_stage_analysis" in rec_tabaa
    assert rec_tabaa["five_stage_analysis"]["stage_5_phonetic_g2p_and_flowmusic_lock"]["lyria_model_lock"] == "Lyria 3.5"
    hist_tabaa = hds.verify_historical_narratives(tabaa_sample)
    assert hist_tabaa["is_historically_clean"] is True
    motifs_tabaa = {m["motif_id"] for m in hist_tabaa["verified_authentic_motifs"]}
    assert {"infant_harmala_arrow", "ten_horsemen_trampling"}.issubset(motifs_tabaa)

    # 3. Verify Bahrani Benchmark Poem 2 («صورة جسد عالغبرة» — Nader Al-Tattan)
    bahrani_sample = (
        "أختصر كل الحدث و أستعجِل الظهيره\n"
        "واندفن وجه النهر والكل جَمَد في حِيره\n"
        "مات كل شي و رحل إلاّ الحُسين و حُبّه\n"
        "صورة جسد عالغبره .. صورة جرح ما يبره\n"
        "آه هذا الشمر .. بيه الحقد لواهب\n"
        "الحُسين اعلى الثرى .. صاعد على صدره الشمر\n"
        "ما صعد حافي بعد .. بنعاله جالس عالصدر\n"
        "طوّل جلوسه اعلى الصدر .. واحسين يناظر للخدر\n"
        "وش ناوي تفعل يا شمر .. صوب النحر\n"
        "قبض الشيبه و بقى يحز بمنحره\n"
        "مشى سيفه اعلى النحر أْو ظل يهبّره\n"
        "والمُستقر جهنم .. والمجِد نصيبه .. يظل اسمه مُخلد للقيامه"
    )
    res_bahr = hds.detect_and_shape_dialect(bahrani_sample)
    assert res_bahr["detected_dialect"] == "bahrani"
    assert res_bahr["bahrani_score"] >= 6
    s_bahr = res_bahr["shaped_lyrics"]
    assert hds.detect_and_shape_dialect(s_bahr)["shaped_lyrics"] == s_bahr
    assert "أَسْتَعْجِلْ الظَّهِيرَه" in s_bahr
    assert "عَالْغَبْرَه" in s_bahr and "عَالصَّدِرْ" in s_bahr
    assert "بِيه الحِقِدْ لَوَاهِبْ" in s_bahr
    assert "المُسْتَقَرْ" in s_bahr and "مُخَلَّدْ لِلْقِيَامَه" in s_bahr
    rec_bahr = hds.recommend_tor_and_rhythm_for_poem(bahrani_sample)
    assert rec_bahr["detected_dialect"] == "bahrani"
    assert rec_bahr["recommended_dsp_mode"] == "bahrani_muthakkal"
    assert rec_bahr["recommended_bpm"] == 56
    hist_bahr = hds.verify_historical_narratives(bahrani_sample)
    assert any(m["motif_id"] == "shimr_chest_and_nahr_martyrdom" for m in hist_bahr["verified_authentic_motifs"])

    # 4. Verify Iraqi Benchmark Poem 3 («فلسفة الانتظار» — Haidar Turki Al-Karbalaei)
    intidhar_sample = (
        "فلسفة الانتظار .. للغايب باختصار\n"
        "اترجمها ام البنين\n"
        "——-\n"
        "يامن ناطر الغايب .. وحچي اسمعونك بكل يوم\n"
        "المامذبوحله ابن ادم .. ايسولف حقه ماملچوم\n"
        "——-\n"
        "ابلايه انفاس ابو صالح .. كلشي الدنيا ماتسوه\n"
        "هوه الفارگ احبابه .. روحه اتضل تواليها"
    )
    res_int = hds.detect_and_shape_dialect(hds.sanitize_poem_decorations(intidhar_sample))
    assert res_int["detected_dialect"] == "iraqi"
    s_int = res_int["shaped_lyrics"]
    assert hds.detect_and_shape_dialect(s_int)["shaped_lyrics"] == s_int
    assert "أُمّ البَنِينْ" in s_int and "البَنَينْ" not in s_int
    assert "نَاطِرْ الغَايِبْ" in s_int and "وَ حَچِي يِسَمْعُونَكْ" in s_int
    assert "تِوَالِيهَا" in s_int
    plan_int = hds.plan_poem_extend_stages(intidhar_sample, bpm=58)
    assert plan_int["total_extend_blocks"] >= 2
    hist_int = hds.verify_historical_narratives(intidhar_sample)
    motifs_int = {m["motif_id"] for m in hist_int["verified_authentic_motifs"]}
    assert {"imam_mahdi_intidhar_and_loyalty", "umm_al_banin_madina"}.issubset(motifs_int)

    # Check zero unvocalized >=2-letter tokens across all 3 samples
    for shaped_poem in (s_tabaa, s_bahr, s_int):
        for tok in shaped_poem.split():
            core = re.sub(r"[^\u0621-\u064A\u067E\u0686\u06AF\u064B-\u0652\u0670]", "", tok)
            letters = re.findall(r"[\u0621-\u064A\u067E\u0686\u06AF]", core)
            if len(letters) >= 2:
                assert re.search(r"[\u064B-\u0652\u0670]", core), f"Unvocalized token: {tok}"
