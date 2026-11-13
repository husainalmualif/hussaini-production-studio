#!/usr/bin/env python3
# pylint: disable=too-many-lines,too-many-return-statements,too-many-branches,too-many-locals,too-many-statements,too-many-arguments,too-many-positional-arguments,no-member
"""Hussaini Audio Omni-Architect DSP, 5-Track DAW & Phonetics Compiler (V48.5 OMNI-ARCHITECT).

Standalone empirical production engine implementing Hussaini_Production_Studio_OS_V48_5_OMNI_ARCHITECT:
- Single-Source Version Management via root VERSION file (V48.5 OMNI-ARCHITECT) & JSON constitution
- Module 39 & 51: Two-Channel JSON vs. Compose UI Routing (QC17 inline JSON firewall) and Mandatory
  Collective '(...)' Unison Raddada Estehlal Orthographic Lock (QC18)
- Module 40, 41, 43, 45 & 49: Pure Single-Dialect Vocal Tract Isolation (QC9/QC13), Plain Epenthetic
  Vowels (دُمُوعْ/جُرُوحْ/مِتُونِي) vs. Mandatory Iraqi Prosthetic 'إِCْ' Clusters (إِبْچَفَّكْ/إِعْيُونِي/إِحْسَينْ/إِعْلَه),
  Syncopated Feminine Nouns (العَافْيَه/حَافْيَه/فَاتْحَه), Phonetic Construct 'تْ' (وِسَادَتْ رِيشْ/دِنْيَتْ خَيرْ),
  Unmarked Medial Diphthong Glides (إِحْسَينْ/خَيرْ/زَينَبْ — QC14), and Open Feminine Haa Without Sukun
- Module 44, 47 & 50: Crying & Weeping Isolation to 0 BPM Rubato Minbar Na'i Only (QC15), 36-Term
  Song & Western 12-TET Collapse Blacklist (QC4/QC16), and 4-Genre Religious Vocal Taxonomy
- Module 46, 48 & 52: Dynamic 4-Stage Common Jins Maqam Progression (58-60 BPM Thaqeel sweet spot),
  15 Master Sound Prompts, Abudhiyah Jinas & Zuhayri Mawal Validators, and 5 Golden Pillars Auditor
- Local 16-Mode 5-Track SOS/RMS/LUFS DSP Montage Engine with Stem-Aware AI Percussion Cleaning
  (--replace-ai-percussion: 4th-order SOS HPF @ 120Hz + Fast/Slow RMS De-Clicker ratio > 1.85 +
  LPF @ 4500Hz), Reference Audio Reverse Engineering (--extract-profile), Rosenberg Glottal +
  Formant Ahaat (F1=730, F2=1090, F3=2440Hz, [-4, 0, +4] cents), -28 dBFS Ducking & -14.0 LUFS Master
"""

import argparse
from datetime import datetime, timezone
import json
import os
import re
import sys
import wave

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, iirnotch, lfilter, sosfilt


def get_skill_version():
    """Read the canonical skill version from the root VERSION file."""
    version_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "VERSION"))
    if os.path.isfile(version_file):
        with open(version_file, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    return "V48.5 OMNI-ARCHITECT"


SKILL_VERSION = get_skill_version()

# 24-EDO Maqam Drone Frequencies (Hz) — Section 4 of V48.5 Constitution
MAQAM_FREQS = {
    "bayati": [146.83, 160.00, 174.61, 220.00],
    "saba": [146.83, 160.00, 174.61, 207.65],
    "saba_zamzam": [146.83, 155.56, 174.61, 207.65],
    "hijaz": [146.83, 155.56, 185.00, 220.00],
    "lami": [146.83, 155.56, 174.61, 207.65],
    "kurd": [146.83, 155.56, 174.61, 220.00],
    "rast": [130.81, 146.83, 160.00, 196.00],
    "nahawand": [146.83, 164.81, 174.61, 220.00],
    "sikah": [160.00, 174.61, 196.00, 220.00],
}

COMMON_JINS_GRAPH = {
    "bayati": ["saba", "saba_zamzam", "kurd", "hijaz", "lami", "sikah"],
    "saba": ["saba_zamzam", "bayati", "lami", "hijaz", "rast"],
    "saba_zamzam": ["saba", "lami", "hijaz", "bayati", "kurd"],
    "hijaz": ["saba_zamzam", "bayati", "saba", "kurd", "sikah"],
    "lami": ["saba_zamzam", "saba", "bayati", "kurd"],
    "kurd": ["bayati", "lami", "saba_zamzam", "hijaz"],
    "rast": ["saba", "bayati", "hijaz", "sikah"],
    "nahawand": ["kurd", "bayati", "saba", "hijaz"],
    "sikah": ["bayati", "hijaz", "rast", "saba"],
}

SUPPORTED_DSP_MODES = (
    "latm",
    "heavy_clip",
    "thaqeel_muwazza",
    "studio_arranged",
    "bahrani_fast",
    "bahrani_thulathi",
    "bahrani_rubai",
    "bahrani_haidari",
    "bahrani_waqfa",
    "bahrani_muthakkal",
    "zanjeel_iraqi",
    "zanjeel_bahrani",
    "shoor",
    "bandari",
    "mawal",
    "nai",
)

# 16 Empirically Verified V48.5 (Rev 2) Master Sound Prompts (Modules 36, 44, 46, 48, 50 & 52)
MASTER_SOUND_PROMPTS_V48_5 = {
    "karbalai_muthakkal_58bpm_saba_zamzam_v48_5_deep_root": (
        "Mournful Traditional Iraqi Hussaini Latmiya, heavy Karbalai Muthakkal and Nazla style, "
        "Maqam Saba Zamzam and Bayati, 58 BPM, authentic Iraqi colloquial dialect, commanding deep "
        "resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, "
        "passionate microtonal melisma, heavy 55Hz bare-palm chest thud, 310ms tape echo, 3.5s "
        "Husseiniya reverb, wide unison male Raddada response, Pure Acapella No Instruments"
    ),
    "karbalai_nazla_60bpm_bayati_saba_v48_5_root": (
        "Traditional Iraqi Hussaini Latmiya, heavy Karbalai Nazla style, Maqam Bayati and Saba, "
        "60 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone lead vocal, "
        "powerful high chest-voice climbs, natural vocal rasp, passionate microtonal melisma, "
        "heavy 55Hz bare-palm chest thud, 285ms tape echo, 3.2s Husseiniya hall reverb, wide "
        "unison male Raddada response, Pure Acapella No Instruments"
    ),
    "rukbani_nassari_58bpm_lami_saba_v48_5_stage2": (
        "Mournful Traditional Iraqi Karbalaei Hussaini Rukbani and Nassari Latmiya, Maqam Lami and "
        "Saba, 58 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone lead "
        "vocal, powerful high chest-voice climbs, natural vocal rasp, prolonged mournful vowel "
        "elongations, heavy 55Hz bare-palm chest thud, 320ms tape echo, 3.5s Husseiniya hall "
        "reverb, wide unison male Raddada response, Pure Acapella No Instruments"
    ),
    "karbalai_ashouri_jawab_climax_58bpm_saba_zamzam_hijaz_v48_5_stage3": (
        "Mournful Traditional Iraqi Hussaini Latmiya, dramatic Karbalai Ashouri Nazla climax, "
        "Maqam Saba Zamzam and Hijaz, 58 BPM, authentic Iraqi colloquial dialect, commanding deep "
        "resonant Baritone lead vocal, soaring high chest-voice climbs, natural vocal rasp, "
        "passionate microtonal melisma, heavy 55Hz bare-palm chest thud, 310ms tape echo, 3.5s "
        "Husseiniya hall reverb, wide unison male Raddada response, Pure Acapella No Instruments"
    ),
    "karbalai_wahsha_lami_kasra_56bpm_finale_v48_5_stage4": (
        "Solemn Traditional Iraqi Hussaini Latmiya, mournful Karbalai Lami Kasra style, Maqam Lami "
        "and Saba, 56 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone "
        "lead vocal, soulful microtonal melisma, natural vocal rasp, prolonged vowel elongations, "
        "slow heavy 55Hz bare-palm chest thud, 360ms tape echo, 3.8s Husseiniya dome reverb, wide "
        "unison male Raddada response, Pure Acapella No Instruments"
    ),
    "iraqi_bahrani_58bpm_saba_fusion_master": (
        "Traditional Iraqi and Bahrani Hussaini Latmiya, Thaqeel Faizi and Nazla style, Maqam "
        "Saba, 58 BPM, authentic Iraqi and Bahrani colloquial dialect, commanding deep resonant "
        "Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, passionate "
        "microtonal melisma, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s "
        "Husseiniya hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments"
    ),
    "euphrates_nassari_58bpm_lami": (
        "Traditional Southern Iraqi Euphrates Hussaini Latmiya, Bahr Al-Nassari style, Maqam "
        "Lami, 58 BPM, authentic Southern Iraqi colloquial dialect, commanding deep resonant "
        "Baritone lead vocal, natural vocal rasp, prolonged microtonal vowel elongations, slow "
        "heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, "
        "unison male Raddada response, Pure Acapella No Instruments"
    ),
    "karbalai_mawkib_daraj_74bpm_bayati_hijaz": (
        "Passionate Iraqi Karbalaei Hussaini Mawkib Daraj Latmiya chant, 74 BPM, dignified Maqam "
        "Bayati and Hijaz on D rising to powerful Jawab, commanding resonant Karbalaei Baritone "
        "Radood vocal, natural vocal rasp, booming unison male Mawkib congregation Raddada "
        "responses, deep synchronized 55Hz bare-chest Latm thud in Husseiniya hall, "
        "Pure Acapella No Instruments"
    ),
    "iraqi_keadia_74bpm_kurd": (
        "Traditional Iraqi Hussaini Keadia Latmiya, Maqam Kurd, 74 BPM, authentic Iraqi "
        "colloquial dialect, high-power full-chest belted Baritone lead vocal, natural vocal "
        "rasp, passionate microtonal melisma, rhythmic 55Hz bare-palm chest-slap pulse, 250ms "
        "analog slapback echo, 2.5s Husseiniya hall reverb, energetic unison male Raddada choir "
        "response, Pure Acapella No Instruments"
    ),
    "bahrani_tawshih_faizi_66bpm_hijaz": (
        "Traditional Bahrani Hussaini Tawshih and Faizi Latmiya, Maqam Hijaz, 66 BPM, authentic "
        "Bahrani colloquial dialect, wide majestic Baritone lead vocal, trembling microtonal "
        "vowel elongations, powerful high chest-voice climbs, synchronous 55Hz bare-palm chest "
        "thud, 260ms analog tape delay, 2.8s Matam hall reverb, wide unison male Raddada choir "
        "response, Pure Acapella No Instruments"
    ),
    "bahrani_muthakkal_56bpm_saba": (
        "Mournful Bahrani Qatifi Muthakkal Hussaini Latmiya lament, 56 BPM, solemn Maqam Saba "
        "and Bayati on D, authentic Bahrani colloquial dialect, commanding deep resonant Baritone "
        "Radood vocal, soulful Faizi microtonal melisma, deep slow 55Hz bare-chest Latm thud in "
        "Matam hall, unison male Raddada responses, Pure Acapella No Instruments"
    ),
    "bahrani_waqfa_84bpm_hijaz_bayati": (
        "Mournful Bahrani Hussaini Waqfa Latmiya chant, 84 BPM, solemn Maqam Hijaz and Bayati "
        "with Faizi microtonal vibrato, commanding resonant Baritone Radood, strong synchronized "
        "Bahrani 55Hz bare-chest slaps, unison male Matam congregation responses, "
        "Pure Acapella No Instruments"
    ),
    "bahrani_haidari_96bpm_hijaz": (
        "Epic Bahrani Haidari Mawkib Hussaini Latmiya chant, 96 BPM, commanding Maqam Hijaz on D, "
        "authentic Bahrani colloquial dialect, powerful resonant Baritone Radood vocal, driving "
        "synchronized Bahrani 55Hz bare-chest strikes, antiphonal dual-choir Matam congregation "
        "responses, Pure Acapella No Instruments"
    ),
    "zanjeel_procession_80bpm_hijaz": (
        "Traditional Hussaini Zanjeel procession chant, Maqam Hijaz, 80 BPM, authentic Iraqi "
        "colloquial dialect, thunderous heroic Bass-Baritone lead vocal, commanding epic chest "
        "projection, deep acoustic Dammam drum strikes locked with metallic shoulder Zanjeel "
        "chains and brass Tasa cymbals, 1.2s open-air street slapback echo, massive unison male "
        "Raddada response, No Melodic Instruments"
    ),
    "karbalai_shoor_132bpm_kurd": (
        "Traditional Iraqi Karbalaei Shoor Latmiya, Maqam Kurd, 132 BPM, authentic Iraqi "
        "colloquial dialect, impassioned raspy Baritone lead vocal, powerful high chest-voice "
        "climbs, rapid driving 55Hz bare-palm chest slaps, continuous deep male congregation "
        "rhythmic Hussain chant, 1.5s tight Husseiniya hall reverb, Pure Acapella No Instruments"
    ),
    "minbar_nai_0bpm_rubato_saba_exclusive_weeping": (
        "Traditional Iraqi and Bahrani Minbar Na'i vocal lament, strict Rubato free tempo with "
        "zero rhythmic grid, Maqam Saba, authentic Arabic recitation, deep velvet mournful "
        "Baritone solo voice, raw weeping cracks on phrase endings, prolonged microtonal vowel "
        "cries, 450ms analog tape echo, 3.8s large Husseiniya cathedral reverb, "
        "Pure Solo Acapella No Percussion No Instruments"
    ),
}

# Module 53 (QC19): Mandatory Per-Stage & Per-Section JSON Orchestration Keys
REQUIRED_STAGE_JSON_KEYS = (
    "stage_id",
    "execution_command",
    "title",
    "global_bpm",
    "sound_description",
    "sections",
)

REQUIRED_SECTION_JSON_KEYS = (
    "section_tag",
    "performer",
    "meter_and_syllables",
    "tempo_feel",
    "tor_and_maqam",
    "throat_and_maddat_dynamics",
    "rhythm_chants_and_sfx",
    "audio_engineering_3d",
    "dialect_phonetic_locks",
    "lyrics_arabic",
)

# 36-Term Song, Crying-Clutter & 12-TET Collapse Blacklist for Rhythmic Latmiya Prompts (Module 50)
LATMIYA_SONG_LEAKAGE_BLACKLIST = (
    "piano",
    "guitar",
    "strings",
    "oud",
    "violin",
    "synth",
    "808",
    "trap",
    "studio-arranged",
    "studio-mixed",
    "arranged studio",
    "humming",
    "pads",
    "sub-bass",
    "groove",
    "bandari",
    "harmonic",
    "dammam",
    "syncopated",
    "tenor",
    "reciter",
    "spoken",
    "wailing",
    "screaming",
    "tear-choked",
    "emotional weep cracks",
    "weeping",
    "sobbing",
    "majlis cries",
    "legato phrasing",
    "wordless pharyngeal ahaat vocal drone",
    "calm",
    "serene",
    "bahha",
    "tarjee'",
    "maddat sawtiya",
    "taqatee'",
    "--no piano",
)

# Separation of Poetic Meter (الوزن الشعري) vs. Performance Melody (الطور الأدائي)
POETIC_METERS_CATALOG = {
    "nassari": {
        "arabic_name": "وزن النصّاري",
        "rhyme_scheme": "AAAB",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": [
            "tor_nai_kashi",
            "tor_ashouri",
            "tor_rukbani",
            "tor_janoubi",
            "tor_zaarijawi",
            "tor_muthakkal",
            "tor_darj_karbalai",
        ],
    },
    "faizi": {
        "arabic_name": "وزن الفايزي (البحراني)",
        "rhyme_scheme": "AAAB / AABB",
        "typical_syllables_per_hemistich": (8, 11),
        "compatible_atwar": [
            "tor_faizi_bahrani",
            "tor_muthakkal_bahrani",
            "tor_tawshih_bahrani",
            "tor_waqfa_bahrani",
        ],
    },
    "mujarradat": {
        "arabic_name": "وزن المجرّدات (المهداد / النعي)",
        "rhyme_scheme": "AAAA",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": [
            "tor_nai_mujarrad",
            "tor_ashouri",
            "tor_muthakkal",
            "tor_mullai",
        ],
    },
    "abudhiyah": {
        "arabic_name": "وزن الأبوذية العراقية",
        "rhyme_scheme": "3 homophonous Jinas lines + 4th ending in -يَّه",
        "typical_syllables_per_hemistich": (10, 12),
        "compatible_atwar": [
            "tor_lami_iraqi",
            "tor_huwaizawi",
            "tor_zaarijawi",
            "tor_shushtari",
            "tor_nayli",
        ],
    },
    "zuhayri_mawal": {
        "arabic_name": "وزن الموّال السبعوي (الزهيري)",
        "rhyme_scheme": "7 lines (AAA B AAA or AAA BBB A with 4th-line Arq pivot)",
        "typical_syllables_per_hemistich": (11, 14),
        "compatible_atwar": [
            "tor_mawal_iraqi",
            "tor_rukbani",
            "tor_dashti",
            "tor_kashi",
        ],
    },
    "tajleeb": {
        "arabic_name": "وزن التجليبة",
        "rhyme_scheme": "AABB / ABCB",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": [
            "tor_tajleeb_furati",
            "tor_nai_mujarrad",
            "tor_ashouri",
            "tor_mullai",
        ],
    },
    "rukbani": {
        "arabic_name": "وزن الركباني / الحدي",
        "rhyme_scheme": "AAAB / ABCB",
        "typical_syllables_per_hemistich": (6, 8),
        "compatible_atwar": [
            "tor_rukbani",
            "tor_hadi",
            "tor_darj_karbalai",
            "tor_ashouri",
        ],
    },
    "daksani": {
        "arabic_name": "وزن الدكسني",
        "rhyme_scheme": "AAAB",
        "typical_syllables_per_hemistich": (6, 8),
        "compatible_atwar": ["tor_nai_mujarrad", "tor_mullai", "tor_janoubi"],
    },
    "muwashah": {
        "arabic_name": "وزن الموشّح والتوشيح",
        "rhyme_scheme": "Multi-stanza with unified Lazima",
        "typical_syllables_per_hemistich": (6, 10),
        "compatible_atwar": [
            "tor_tawshih_bahrani",
            "tor_bahrani_thulathi",
            "tor_bahrani_rubai",
            "tor_bahrani_haidari",
            "tor_darj_karbalai",
        ],
    },
    "iraqi_hosa": {
        "arabic_name": "وزن الهوسة العشائرية العراقية",
        "rhyme_scheme": "3+1 Arjooza (AAA fast delivery + B 115-130 BPM crowd Ribat)",
        "typical_syllables_per_hemistich": (7, 10),
        "compatible_atwar": ["tor_hosa_iraqi"],
    },
}

PERFORMANCE_ATWAR_CATALOG = {
    "tor_nai_kashi": {
        "arabic_name": "طور النعي الكاشي / المنبري",
        "school": "iraqi_bahrani",
        "primary_maqam": "hijaz",
        "default_bpm": 0,
        "delivery_rule": "مدّ الكلمة الثانية والأخيرة مع ترجيع خفيف وونّة منبرية في القفلة",
    },
    "tor_ashouri": {
        "arabic_name": "الطور العاشوري التفاعلي",
        "school": "iraqi",
        "primary_maqam": "saba",
        "default_bpm": 58,
        "delivery_rule": "مدّ الكلمة الأخيرة وقطع الصوت فجأة (1.5s) لمشاركة المعزين بـ (آه .. آه)",
    },
    "tor_muthakkal_bahrani": {
        "arabic_name": "طور المثكّل البحراني / القطيفي",
        "school": "bahrani",
        "primary_maqam": "saba",
        "default_bpm": 56,
        "delivery_rule": "شجن وقور متدرج مع ونّة بحرانية منكسرة في آخر كل شطر",
    },
    "tor_faizi_bahrani": {
        "arabic_name": "الطور الفايزي البحراني الأصيل",
        "school": "bahrani",
        "primary_maqam": "hijaz",
        "default_bpm": 62,
        "delivery_rule": "اتزان الافتتاح ثم مدّ الكلمة الثالثة بترجيع حلقي وختم الشطر بالونّة",
    },
    "tor_bahrani_thulathi": {
        "arabic_name": "طور العزاء البحراني الثلاثي (الموكبي)",
        "school": "bahrani",
        "primary_maqam": "bayati",
        "default_bpm": 76,
        "delivery_rule": "ضربتان متقاربتان (دم-دم) + ضربة ثالثة ثقيلة مع وقفة تنفسية وتبادل الفوجين",
    },
    "tor_bahrani_rubai": {
        "arabic_name": "طور العزاء البحراني الرباعي",
        "school": "bahrani",
        "primary_maqam": "bayati",
        "default_bpm": 72,
        "delivery_rule": "أربع ضربات صدرية متزنة (3 مسير + 1 ارتكاز) مع نظام الفوجين المتقابلين",
    },
    "tor_bahrani_haidari": {
        "arabic_name": "الطور الحيدري الملحمي البحراني",
        "school": "bahrani",
        "primary_maqam": "hijaz",
        "default_bpm": 96,
        "delivery_rule": "إيقاع موكبي حماسي متصاعد بضربات صدرية حادة في رثاء الأبطال والعباس (ع)",
    },
    "tor_waqfa_bahrani": {
        "arabic_name": "طور الوقفة البحرانية (التجنيزة)",
        "school": "bahrani",
        "primary_maqam": "saba",
        "default_bpm": 104,
        "delivery_rule": "توقف المسير لترديد أبيات قصيرة مكثفة سريعة الإيقاع بتناوب الفوج الأول والثاني",
    },
    "tor_zaarijawi": {
        "arabic_name": "الطور الزريجاوي (طور الكعبي)",
        "school": "iraqi",
        "primary_maqam": "sikah",
        "default_bpm": 0,
        "delivery_rule": "وتيرة متأرجحة مع مدّ وترجيع خفيفين وصعود ونزول بدون ونّة",
    },
    "tor_huwaizawi": {
        "arabic_name": "الطور الحويزاوي",
        "school": "iraqi",
        "primary_maqam": "lami",
        "default_bpm": 0,
        "delivery_rule": "مدّات حنجرية عالية في الجواب في مقام اللامي والصبا مع كسرة فراتية",
    },
}

# Module 41 & 49: Anti-Slurring Word De-Cliticization & Unmarked Diphthongs
WORD_SEPARATION_MAP = {
    "ياحسين": "يَا إِحْسَينْ",
    "يبوفاضل": "يَا بُو فَاضِلْ",
    "يبو فاضل": "يَا بُو فَاضِلْ",
    "يبو السجاد": "يَا بُو السَّجَّادْ",
    "يزينب": "يَا زَينَبْ",
    "يم البنين": "يَا أُمّ البَنِينْ",
    "يحيدر": "يَا حَيدَرْ",
    "يمحمد": "يَا مْحَمَّدْ",
    "يايمه": "يَا يُمَّه",
    "يحبيبه": "يَا حَبِيبَه",
    "يافاطم": "يَا فَاطِمْ",
    "ابأرض": "بِأَرْضِ",
    "عالباب": "إِعْلَه البَابْ",
    "عالرمضا": "إِعْلَه الرَّمْضَه",
    "عالرمضه": "إِعْلَه الرَّمْضَه",
    "عالجمر": "إِعْلَه الجَمُرْ",
    "عالتل": "إِعْلَه التَّلْ",
    "عالنهر": "إِعْلَه النَّهَرْ",
    "عالشاطي": "إِعْلَه الشَّاطِي",
    "بغربتي": "بِـ غُرْبِتِي",
    "بضلوعي": "بِـ ضْلُوعِي",
    "بظلوعي": "بِـ ظْلُوعِي",
    "بدموع": "بِدْمُوعْ",
    "بدموعي": "بِدْمُوعِي",
    "بجروح": "بِجْرُوحْ",
    "بجروحي": "بِجْرُوحِي",
    "لحسين": "لِـ إِحْسَينْ",
    "للشام": "لِلشَّامْ",
    "للذبحوا": "لِلْ ذَبْحَوْا",
    "للناس": "لِلْ نَاسْ",
    "شصار": "إِشْ صَارْ",
    "شجرى": "إِشْ جَرَى",
    "شنگول": "إِشْ نْگُولْ",
    "شنقول": "إِشْ نْگُولْ",
    "شحچي": "إِشْ أَحْچِي",
    "شسوه": "إِشْ سَوَّه",
    "شتريد": "إِشْ تْرِيدْ",
    "شيجيبه": "شِيجِيبَه",
    "شيصير": "شِيصِيرْ",
    "شيفيد": "شِيفِيدْ",
    "اشلون": "إِشْلُونْ",
    "يفگدله": "يِفْگِدْلَه",
    "والشمس": "وَ الشَّمْسْ",
    "والخيل": "وَ الخَيلْ",
    "والمدمع": "وَ المَدْمَعْ",
    "والرأس": "وَ الرَّأْسْ",
}

# Module 49: Colloquial Construct State, Relative Particle & Boundary Sukun Phrases
COLLOQUIAL_PHRASE_MAP = {
    "وسادة ريش": "وِسَادَتْ رِيشْ",
    "وساده ريش": "وِسَادَتْ رِيشْ",
    "دنية خير": "دِنْيَتْ خَيرْ",
    "دنيه خير": "دِنْيَتْ خَيرْ",
    "ال مثل زينب": "إِلْ مِثِلْ زَينَبْ",
    "المثل زينب": "إِلْ مِثِلْ زَينَبْ",
    "بس امسح": "بَسْ إِمْسَحْ",
    "بس إمسح": "بَسْ إِمْسَحْ",
    "استار الكون": "إِسْتَارِ الكُونْ",
    "إستار الكون": "إِسْتَارِ الكُونْ",
    "ابوك حسين": "أَبُوكْ إِحْسَينْ",
    "أبوك حسين": "أَبُوكْ إِحْسَينْ",
}

COLLOQUIAL_TANWEEN_MAP = {
    "عينٍ تسيل": "عَينِنْ تِسِيلْ",
    "كلٍ ينادي": "كِلِّنْ يِنَادِي",
    "جرحٍ چبير": "جَرْحِنْ چِبِيرْ",
    "جرحٍ جبير": "جَرْحِنْ چِبِيرْ",
    "حالٍ يفطر": "حَالِنْ يِفَطِّرْ",
    "يومٍ عظيم": "يَومِنْ عَظِيمْ",
    "ضامرٍ يشكي": "ضَامِرِنْ يِشْكِي",
    "عذراً": "عِذْرَنْ",
}

FUSHA_MIDLINE_TANWEEN_MAP = {
    "جسماً على الثرى": "جِسْمَنْ عَلَى الثَّرَى",
    "جِسْماً عَلَى الثَّرَى": "جِسْمَنْ عَلَى الثَّرَى",
    "أماناً يا": "أَمَانَنْ يَا",
    "مستمسكاً بيدي": "مُسْتَمْسِكَنْ بِيَدِي",
    "دامٍ بلا قبورٍ": "دَامِنْ بِلَا قُبُورْ",
    "دامٍ بلا قبور": "دَامِنْ بِلَا قُبُورْ",
    "دَامٍ بِلَا قُبُورْ": "دَامِنْ بِلَا قُبُورْ",
    "عزٌ لنا": "عِزُّنْ لَنَا",
    "عِزٌّ لَنَا": "عِزُّنْ لَنَا",
    "ظامئاً": "ظَامِئَا",
    "ظَامِئاً": "ظَامِئَا",
}

BAHRANI_MARKERS = (
    "بويي",
    "خويي",
    "ونتي",
    "هالگفره",
    "امساعد",
    "عفارم",
    "إشحالك",
    "اشحالك",
    "لچن",
    "الراعبية",
    "الراعبيه",
    "يا بويي",
    "إشحالش",
    "اشحالش",
    "گلبش",
    "عفتش",
    "هالمسيه",
    "هالمسية",
    "عَلَه",
)

IRAQI_MARKERS = (
    "بويه",
    "خويه",
    "يمه",
    "وليدي",
    "دلالي",
    "شلون",
    "إش صار",
    "شصار",
    "شنگول",
    "شيصير",
    "بلياك",
    "ما ظل",
    "چلبت",
    "وگفت",
    "هسه",
    "هالحچايه",
    "هالحچاية",
    "مشبوگه",
    "يبچي",
    "تشتاگ",
    "تگله",
    "متوني",
    "زرگ",
    "تراچي",
    "ذيچ",
    "البچت",
    "خذتني",
    "أگلكم",
    "الحريگ",
    "الطريگ",
    "هنيالي",
    "أخدمنك",
    "خدمنك",
    "يلحگ",
    "ينخونك",
    "بچفك",
    "بگلبي",
    "بگاع",
    "بهداي",
    "بعفه",
    "إعله",
    "اعله",
    "وسادة ريش",
    "دنية خير",
    "العافية",
    "العافيه",
    "مطيني",
    "يالمطيني",
    "يفگدله",
)

FUSHA_MARKERS = (
    "إنما",
    "إِنَّمَا",
    "ليس",
    "لَيْسَ",
    "كأنما",
    "كَأَنَّمَا",
    "فهو",
    "فَهُوَ",
    "لعل",
    "لَعَلَّ",
    "حيثما",
    "الودجين",
    "القبلتين",
)

# QC13: Classical Fusha vocalizations forbidden inside pure colloquial dialect poems
FUSHA_DIALECT_CLASH_TOKENS = (
    "عُيُونِي",
    "عُيُونَك",
    "عُيُونَكْ",
    "حُسَيْن",
    "حُسَيْنْ",
    "حُسَينْ",
    "مُطِّينِي",
    "يَالمُطِّينِي",
    "بِمَجْلِسِكَ",
    "وِسَادَةِ",
    "دُنْيَةِ",
)

DEMONSTRATIVE_HAL_IRAQI_MAP = {
    "هالحچايه": "هَلْ حِچَايَه",
    "هالحچاية": "هَلْ حِچَايَه",
    "هَالْحِچَايَه": "هَلْ حِچَايَه",
    "هَالْحِچَايَهْ": "هَلْ حِچَايَه",
    "هَلِحْچَايَهْ": "هَلْ حِچَايَه",
    "هالحكايه": "هَلْ حِچَايَه",
    "هالحكاية": "هَلْ حِچَايَه",
    "هالتعب": "هَلْ تَعَبْ",
    "هَالْتَّعَبْ": "هَلْ تَعَبْ",
    "هالليله": "هَلْ لَيلَه",
    "هالليلة": "هَلْ لَيلَه",
    "هَاللَّيْلَه": "هَلْ لَيلَه",
    "هالشام": "هَلْ شَامْ",
    "هَالشَّامْ": "هَلْ شَامْ",
    "هالناس": "هَلْ نَاسْ",
    "هَالنَّاسْ": "هَلْ نَاسْ",
    "هالزمان": "هَلْ زَمَانْ",
    "هَالزَّمَانْ": "هَلْ زَمَانْ",
    "هالدار": "هَلْ دَارْ",
    "هَالدَّارْ": "هَلْ دَارْ",
    "هالدرب": "هَلْ دَرُبْ",
    "هالغرب": "هَلْ غُرَبْ",
    "هَالْغُرَبْ": "هَلْ غُرَبْ",
    "هالگفره": "هَلْ گُفْرَه",
    "هالگفرة": "هَلْ گُفْرَه",
    "هالمسيه": "هَلْ مَسِيَّه",
    "هالمسية": "هَلْ مَسِيَّه",
}

DEMONSTRATIVE_HAL_BAHRANI_MAP = {
    "هالحچايه": "هَلْ حِچَايَه",
    "هالحچاية": "هَلْ حِچَايَه",
    "هَالْحِچَايَه": "هَلْ حِچَايَه",
    "هَالْحِچَايَهْ": "هَلْ حِچَايَه",
    "هالحكايه": "هَلْ حِكَايَه",
    "هالحكاية": "هَلْ حِكَايَه",
    "هالتعب": "هَلْ تَعَبْ",
    "هَالْتَّعَبْ": "هَلْ تَعَبْ",
    "هالليله": "هَلْ لَيلَه",
    "هالليلة": "هَلْ لَيلَه",
    "هَاللَّيْلَه": "هَلْ لَيلَه",
    "هالشام": "هَلْ شَامْ",
    "هالناس": "هَلْ نَاسْ",
    "هالزمان": "هَلْ زَمَانْ",
    "هالدار": "هَلْ دَارْ",
    "هالدرب": "هَلْ دَرِبْ",
    "هالغرب": "هَلْ غُرَبْ",
    "هالگفره": "هَلْ گُفْرَه",
    "هالگفرة": "هَلْ گُفْرَه",
    "هالمسيه": "هَلْ مَسِيَّه",
    "هالمسية": "هَلْ مَسِيَّه",
}

# Module 49: Plain Initial Clusters -> Soft Epenthetic Short Vowel (never word-initial Sukun or artificial إِدْمُوعْ)
WORD_INITIAL_SUKUN_REPAIR_MAP = {
    "إِدْمُوعْ": "دُمُوعْ",
    "دْمُوعْ": "دُمُوعْ",
    "إِجْرُوحْ": "جُرُوحْ",
    "جْرُوحْ": "جُرُوحْ",
    "إِمْتُونِي": "مِتُونِي",
    "مْتُونِي": "مِتُونِي",
    "إِسْنِينِي": "سِنِينِي",
    "سْنِينِي": "سِنِينِي",
    "إِسْكِينَهْ": "سِكِينَه",
    "إِسْكِينَه": "سِكِينَه",
    "سْكِينَه": "سِكِينَه",
    "عْيُونِي": "إِعْيُونِي",
    "عْيُونَكْ": "إِعْيُونَكْ",
    "عْيُونِكْ": "عِيُونِكْ",
    "إِتْگِلَّهْ": "تِگِلَّه",
    "إِتْگِلَّه": "تِگِلَّه",
    "تْگِلَّه": "تِگِلَّه",
    "إِتْسُولِفْ": "تِسُولِفْ",
    "تْسُولِفْ": "تِسُولِفْ",
    "إِهْمُومْ": "هُمُومْ",
    "هْمُومْ": "هُمُومْ",
    "شْفَافَه": "شِفَافَه",
    "مْفَارْگَه": "مِفَارْگَه",
    "شْحَاچِي": "إِشْحَاچِي",
    "جْفُونْهَا": "جُفُونْهَا",
    "بْنَيَّه": "بِنَيَّه",
}

DIALECTAL_DIPHTHONG_AND_VOWEL_MAP = {
    "هَنِيَالِي": "هَنْيَالِي",
    "غَرِيبَهْ": "غَرِيبَه",
    "حِچَايَهْ": "حِچَايَه",
    "حِكَايَهْ": "حِكَايَه",
    "خَرَابَهْ": "خَرَابَه",
    "سَبِيَّهْ": "سَبِيَّه",
    "عَلَوِيَّهْ": "عَلَوِيَّه",
    "صَوَانِيَّهْ": "صَوَانِيَّه",
    "تَرْجِيَّهْ": "تَرْجِيَّه",
    "سَكْتَهْ": "سَكْتَه",
    "عَمْتَهْ": "عَمْتَه",
    "إِلَّهْ": "إِلَّه",
    "عَجِيبَهْ": "عَجِيبَه",
    "حَبِيبَهْ": "حَبِيبَه",
    "أَمِيرَهْ": "أَمِيرَه",
    "أَسِيرَهْ": "أَسِيرَه",
    "عَزِيزَهْ": "عَزِيزَه",
    "سَاعَهْ": "سَاعَه",
    "خِدْمَهْ": "خِدْمَه",
    "زَلْمَهْ": "زَلْمَه",
    "مَسِيَّهْ": "مَسِيَّه",
    "رَزِيَّهْ": "رَزِيَّه",
    "عَطِيَّهْ": "عَطِيَّه",
    "شِفِيَّهْ": "شِفِيَّه",
    "يُمَّهْ": "يُمَّه",
    "بُويَهْ": "بُويَه",
    "خُويَهْ": "خُويَه",
}

IRAQI_WORD_SHAPING_MAP = {
    # Module 49 Mandatory Iraqi Prosthetic Clusters
    "بچفك": "إِبْچَفَّكْ",
    "بجفك": "إِبْچَفَّكْ",
    "عيوني": "إِعْيُونِي",
    "عُيُونِي": "إِعْيُونِي",
    "عيونك": "إِعْيُونَكْ",
    "عُيُونَكْ": "إِعْيُونَكْ",
    "حسين": "إِحْسَينْ",
    "حُسَيْن": "إِحْسَينْ",
    "حُسَيْنْ": "إِحْسَينْ",
    "بمجلسك": "إِبْمَجْلِسَكْ",
    "بگلبي": "إِبْگَلْبِي",
    "بگاع": "إِبْگَاعْ",
    "بكاع": "إِبْگَاعْ",
    "خيام": "إِخْيَامْ",
    "بهداي": "إِبْهِدَايْ",
    "بعفه": "إِبْعِفَّه",
    "بعفة": "إِبْعِفَّه",
    "بشده": "إِبْشِدَّه",
    "بشدة": "إِبْشِدَّه",
    "بخرابه": "إِبْخَرَابَه",
    "بخرابة": "إِبْخَرَابَه",
    # Module 49 Syncopated Iraqi Feminine Nouns & Particles/Participles/Homographs
    "العافية": "العَافْيَه",
    "العافيه": "العَافْيَه",
    "عافية": "عَافْيَه",
    "عافيه": "عَافْيَه",
    "حافية": "حَافْيَه",
    "حافيه": "حَافْيَه",
    "فاتحة": "فَاتْحَه",
    "فاتحه": "فَاتْحَه",
    "الفاتحة": "الفَاتْحَه",
    "الفاتحه": "الفَاتْحَه",
    "على": "إِعْلَه",
    "عَلَى": "إِعْلَه",
    "اعله": "إِعْلَه",
    "إعله": "إِعْلَه",
    "يالمطيني": "يَالمِطِّينِي",
    "يَالمُطِّينِي": "يَالمِطِّينِي",
    "مطيني": "مِطِّينِي",
    "مُطِّينِي": "مِطِّينِي",
    "يالمفارگك": "يَالمِفَارِگَكْ",
    "يالمفاركك": "يَالمِفَارِگَكْ",
    "وادم": "وَادِمْ",
    "وآدم": "وَادِمْ",
    "وعرفني": "وِعَرِّفْنِي",
    "ويبان": "وِيْبَانْ",
    "وحط": "وِحُطْ",
    "وراويني": "وِرَاوِينِي",
    "رادو": "رَادَوْ",
    "رادوا": "رَادَوْ",
    "مشو": "مِشَوْ",
    "مشوا": "مِشَوْ",
    "خير": "خَيرْ",
    "زين": "زَينْ",
    "وين": "وَينْ",
    "وينك": "وَينَكْ",
    "بين": "بَينْ",
    "زينب": "زَينَبْ",
    "علوية": "عَلَوِيَّه",
    "علويه": "عَلَوِيَّه",
    "صوانية": "صَوَانِيَّه",
    "صوانيه": "صَوَانِيَّه",
    "ترجية": "تَرْجِيَّه",
    "ترجيه": "تَرْجِيَّه",
    "سكتة": "سَكْتَه",
    "سكته": "سَكْتَه",
    "عمته": "عَمْتَه",
    "إلّه": "إِلَّه",
    # Module 43 Iraqi Karbalai & Euphrates Lexicon
    "قلب": "گَلُبْ",
    "بقلب": "بِـ گَلُبْ",
    "وقلب": "وَ گَلُبْ",
    "قلبي": "گَلْبِي",
    "بقلبي": "بِـ گَلْبِي",
    "وقلبي": "وَ گَلْبِي",
    "قلبك": "گَلْبَكْ",
    "قلبچ": "گَلْبِچْ",
    "قلبه": "گَلْبَه",
    "صبر": "صَبُرْ",
    "وصبر": "وَ صَبُرْ",
    "بصبر": "بِـ صَبُرْ",
    "صبري": "صَبْرِي",
    "صبرك": "صَبْرَكْ",
    "جمر": "جَمُرْ",
    "وجمر": "وَ جَمُرْ",
    "بجمر": "بِـ جَمُرْ",
    "جمرة": "جَمْرَه",
    "جمره": "جَمْرَه",
    "درب": "دَرُبْ",
    "ودرب": "وَ دَرُبْ",
    "گبر": "گَبُرْ",
    "قبر": "گَبُرْ",
    "حرب": "حَرُبْ",
    "چبد": "چَبِدْ",
    "وچبد": "وَ چَبِدْ",
    "جبد": "چَبِدْ",
    "وجبد": "وَ چَبِدْ",
    "چبدي": "چَبْدِي",
    "جبدي": "چَبْدِي",
    "عشگ": "عِشِگْ",
    "حزن": "حِزِنْ",
    "دمع": "دَمِعْ",
    "ودمع": "وَ دَمِعْ",
    "بدمع": "بِـ دَمِعْ",
    "دمعي": "دَمْعِي",
    "دمعة": "دَمْعَه",
    "دمعه": "دَمْعَه",
    "حسرة": "حَسْرَه",
    "ونة": "وِنَّه",
    "ونّة": "وِنَّه",
    "وگفت": "وُگَفِتْ",
    "ووگفت": "وَ وُگَفِتْ",
    "وگفونه": "وُگَفُونَه",
    "عفتني": "عِفْتْنِي",
    "وعفتني": "وَ عِفْتْنِي",
    "ضلوعي": "ضْلُوعِي",
    "فاضل": "فَاضِلْ",
    "وظايع": "وِظَايِعْ",
    "وضايع": "وِظَايِعْ",
    "أنه": "آنَه",
    "انه": "آنَه",
    "وانه": "وَ آنَه",
    "واَنه": "وَ آنَه",
    "اشگد": "إِشْگَدْ",
    "گوه": "گُوَّه",
    "اشهگ": "أَشْهَگْ",
    "گدامي": "گِدَّامِي",
    "صرت": "صِرِتْ",
    "كثر": "كِثِرْ",
    "كلهه": "كِلْهَه",
    "يحرگ": "يِحْرِگْ",
    "يگطع": "يِگْطَعْ",
    "اگبال": "إِگْبَالْ",
    "بايگله": "بَايِگْ لَه",
    "بايگ": "بَايِگْ",
    "بايك": "بَايِگْ",
    "النوگ": "النُّوگْ",
    "النوك": "النُّوگْ",
    "السوگ": "السُّوگْ",
    "السوك": "السُّوگْ",
    "احلوگ": "إِحْلُوگْ",
    "احلوك": "إِحْلُوگْ",
    "فوگ": "فُوگْ",
    "فوك": "فُوگْ",
    "فوگي": "فُوگِي",
    "ينگال": "يِنْگَالْ",
    "ينكال": "يِنْگَالْ",
    "انياك": "إِنْيَاگْ",
    "انياگ": "إِنْيَاگْ",
    "وانياك": "وَ إِنْيَاگْ",
    "الكالي": "الگَالْ لِي",
    "الگالي": "الگَالْ لِي",
    "مدمه": "مُدَمَّه",
    "مدمى": "مُدَمَّه",
    "اتبشري": "إِتْبَشْرِي",
    "اموذر": "إِمْوَذَّرْ",
    "ازماطي": "إِزْمَاطِي",
    "اجفوف": "إِچْفُوفْ",
    "اچفوف": "إِچْفُوفْ",
    "ايرامون": "إِيْرَامُونْ",
    "احجار": "إِحْجَارْ",
    "هوء": "هُوَّه",
    "ترء": "تَرَى",
    "بشدء": "إِبْشِدَّه",
    "گنة": "گِلْنَه",
    "حكنه": "حَگْنَه",
    "يلحك": "يِلْحَگْ",
    "ابجلمة": "بِچِلْمَه",
    "خدمنك": "أَخْدِمَنَّكْ",
    "اخدمنك": "أَخْدِمَنَّكْ",
    "غريبه": "غَرِيبَه",
    "غريبة": "غَرِيبَه",
    "هالحچايه": "هَلْ حِچَايَه",
    "هالحچاية": "هَلْ حِچَايَه",
    "هالحكايه": "هَلْ حِچَايَه",
    "هالحكاية": "هَلْ حِچَايَه",
    "ماتت": "مَاتَتْ",
    "مشبوگه": "مَشْبُوگَه",
    "مشبوگة": "مَشْبُوگَه",
    "مشبوكه": "مَشْبُوگَه",
    "اديها": "إِدَيهَا",
    "إديها": "إِدَيهَا",
    "ايديها": "إِدَيهَا",
    "خرابه": "خَرَابَه",
    "خرابة": "خَرَابَه",
    "ابوها": "أَبُوهَا",
    "أبوها": "أَبُوهَا",
    "مثلي": "مِثْلِي",
    "يبچي": "يِبْچِي",
    "يبكي": "يِبْچِي",
    "عليها": "عَلَيهَا",
    "روت": "رَوَتْ",
    "قصه": "قِصَّه",
    "قصة": "قِصَّه",
    "عجيبه": "عَجِيبَه",
    "عجيبة": "عَجِيبَه",
    "دموع": "دُمُوعْ",
    "زچيه": "زَچِيَّه",
    "زچية": "زَچِيَّه",
    "تسولف": "تِسُولِفْ",
    "هموم": "هُمُومْ",
    "رزيه": "رَزِيَّه",
    "رزية": "رَزِيَّه",
    "طفله": "طِفْلَه",
    "طفلة": "طِفْلَه",
    "شافت": "شَافَتْ",
    "تحن": "تِحِنْ",
    "تشتاگ": "تِشْتَاگْ",
    "تشتاك": "تِشْتَاگْ",
    "ربطوها": "رِبْطُوهَا",
    "حيف": "حَيفْ",
    "تصيح": "تِصِيحْ",
    "عمه": "عَمَّه",
    "عمة": "عَمَّه",
    "ابويه": "أَبُويَه",
    "أبويه": "أَبُويَه",
    "بويه": "بُويَه",
    "خويه": "خُويَه",
    "يمه": "يُمَّه",
    "گعدت": "گَعْدَتْ",
    "تگله": "تِگِلَّه",
    "گوم": "گُومْ",
    "شوف": "شُوفْ",
    "حزينه": "حَزِينَه",
    "حزينة": "حَزِينَه",
    "متوني": "مِتُونِي",
    "زرگ": "زُرُگْ",
    "زُرَگْ": "زُرُگْ",
    "زرك": "زُرُگْ",
    "تراچي": "تَرَاچِي",
    "جروح": "جُرُوحْ",
    "يتيمه": "يَتِيمَه",
    "يتيمة": "يَتِيمَه",
    "حضنت": "حِظْنَتْ",
    "شبگت": "شَبْگَتْ",
    "نحره": "نَحْرَه",
    "سكتت": "سِكْتَتْ",
    "ذيچ": "ذِيچْ",
    "بنية": "بِنَيَّه",
    "بنيه": "بِنَيَّه",
    "كفيلي": "كَفِيلِي",
    "حيلي": "حَيلِي",
    "حيل": "حَيلْ",
    "ليل": "لَيلْ",
    "خذتني": "خِذَتْنِي",
    "احتاجيت": "إِحْتَاجَيتْ",
    "غلاتي": "غَلَاتِي",
    "چم": "چَمْ",
    "ساعه": "سَاعَه",
    "ساعة": "سَاعَه",
    "حياتي": "حَيَاتِي",
    "أگلكم": "أَگِلْكُمْ",
    "اگلكم": "أَگِلْكُمْ",
    "لوعه": "لَوعَه",
    "لوعة": "لَوعَه",
    "تچوي": "تِچْوِي",
    "ناديت": "نَادَيتْ",
    "حريگ": "حَرِيگْ",
    "طريگ": "طَرِيگْ",
    "مدلل": "مُدَلَّلْ",
    "عليك": "عَلَيكْ",
    "سكينه": "سِكِينَه",
    "سكينة": "سِكِينَه",
    "هنيالي": "هَنْيَالِي",
    "خادم": "خَادِمْ",
    "مولاي": "مَولَايْ",
    "سنيني": "سِنِينِي",
    "عيني": "عَينِي",
    "شده": "شِدَّه",
    "شدة": "شِدَّه",
    "ينخونك": "يِنْخُونَكْ",
    "مضيع": "مِظَيِّعْ",
    "ندمان": "نَدْمَانْ",
    "يلحگ": "يِلْحَگْ",
}

BAHRANI_WORD_SHAPING_MAP = {
    "على": "عَلَه",
    "عَلَى": "عَلَه",
    "إِعْلَه": "عَلَه",
    "قلب": "گَلِبْ",
    "بقلب": "بِـ گَلِبْ",
    "وقلب": "وَ گَلِبْ",
    "قلبي": "گَلْبِي",
    "بقلبي": "بِـ گَلْبِي",
    "وقلبي": "وَ گَلْبِي",
    "قلبك": "گَلْبِكْ",
    "قلبچ": "گَلْبِچْ",
    "گلبش": "گَلْبِشْ",
    "قلبه": "گَلْبَه",
    "صبر": "صَبِرْ",
    "وصبر": "وَ صَبِرْ",
    "بصبر": "بِـ صَبِرْ",
    "صبري": "صَبْرِي",
    "صبرك": "صَبْرِكْ",
    "جمر": "جَمِرْ",
    "وجمر": "وَ جَمِرْ",
    "جمرة": "جَمْرَه",
    "جمره": "جَمْرَه",
    "درب": "دَرِبْ",
    "قبر": "گَبِرْ",
    "گبر": "گَبِرْ",
    "حرب": "حَرِبْ",
    "دمع": "دَمِعْ",
    "ودمع": "وَ دَمِعْ",
    "دمعي": "دَمْعِي",
    "دمعة": "دَمْعَه",
    "دمعه": "دَمْعَه",
    "حسرة": "حَسْرَه",
    "ونة": "وِنَّه",
    "ونّة": "وِنَّه",
    "ضلوعي": "ضْلُوعِي",
    "فاضل": "فَاضِلْ",
    "بويي": "بُويِي",
    "خويي": "خُويِي",
    "ونتي": "وِنِّتِي",
    "امساعد": "إِمْسَاعَدْ",
    "اشحالك": "إِشْحَالِكْ",
    "إشحالك": "إِشْحَالِكْ",
    "اشحالش": "إِشْحَالِشْ",
    "إشحالش": "إِشْحَالِشْ",
    "عفتش": "عِفْتِشْ",
    "لچن": "لَچِنْ",
    "الراعبية": "الرَّاعِبِيَّه",
    "الراعبيه": "الرَّاعِبِيَّه",
    "غريبه": "غَرِيبَه",
    "غريبة": "غَرِيبَه",
    "هالحچايه": "هَلْ حِچَايَه",
    "هالحچاية": "هَلْ حِچَايَه",
    "هالحكايه": "هَلْ حِكَايَه",
    "هالحكاية": "هَلْ حِكَايَه",
    "هالگفره": "هَلْ گُفْرَه",
    "هالگفرة": "هَلْ گُفْرَه",
    "هالمسيه": "هَلْ مَسِيَّه",
    "هالمسية": "هَلْ مَسِيَّه",
    "دموع": "دُمُوعْ",
    "جروح": "جُرُوحْ",
    "متوني": "مِتُونِي",
    "سنيني": "سِنِينِي",
    "عيونك": "عِيُونِكْ",
    "وينك": "وَينِكْ",
    "عليها": "عَلَيهَا",
    "اديها": "إِيْدَيهَا",
    "ايديها": "إِيْدَيهَا",
    "حيل": "حَيلْ",
    "ليل": "لَيلْ",
    "خير": "خَيرْ",
    "زين": "زَينْ",
    "وين": "وَينْ",
    "بين": "بَينْ",
    "زينب": "زَينَبْ",
}

HYBRID_WORD_SHAPING_MAP = {
    "قلب": "قَلْبْ",
    "قلبي": "قَلْبِي",
    "قلبك": "قَلْبَكْ",
    "قلبچ": "گَلْبِچْ",
    "قلبه": "قَلْبَه",
    "صبر": "صَبْرْ",
    "صبري": "صَبْرِي",
    "صبرك": "صَبْرَكْ",
    "جمر": "جَمْرْ",
    "جمرة": "جَمْرَه",
    "جمره": "جَمْرَه",
    "درب": "دَرْبْ",
    "قبر": "قَبْرْ",
    "گبر": "گَبِرْ",
    "حرب": "حَرْبْ",
    "دمع": "دَمْعْ",
    "دمعي": "دَمْعِي",
    "دمعة": "دَمْعَه",
    "دمعه": "دَمْعَه",
    "حسرة": "حَسْرَه",
    "ونة": "وِنَّه",
    "ونّة": "وِنَّه",
    "چبد": "چَبِدْ",
    "جبد": "چَبِدْ",
    "وگفت": "وُگَفِتْ",
    "عفتني": "عِفْتْنِي",
    "ضلوعي": "ضْلُوعِي",
    "فاضل": "فَاضِلْ",
    "بچفك": "إِبْچَفَّكْ",
    "عيوني": "إِعْيُونِي",
    "عيونك": "إِعْيُونَكْ",
    "حسين": "إِحْسَينْ",
    "العافية": "العَافْيَه",
    "العافيه": "العَافْيَه",
    "حافية": "حَافْيَه",
    "فاتحة": "فَاتْحَه",
    "خير": "خَيرْ",
    "زين": "زَينْ",
    "وين": "وَينْ",
    "بين": "بَينْ",
    "زينب": "زَينَبْ",
}


def classify_section_tag(tag_str):
    """Normalize any Arabic or English bracketed section header to chorus/verse/intro_outro."""
    clean = re.sub(r"[\[\]\u064B-\u0652]", "", tag_str).strip()
    lower = clean.lower()
    if lower.startswith("chorus") or any(k in clean for k in ("مستهل", "كسر", "لازمة", "لازمه")):
        return "chorus"
    if lower.startswith("verse") or any(k in clean for k in ("مقطع", "نزلة", "نزله", "دور")):
        return "verse"
    if lower.startswith(("intro", "outro")) or any(
        k in clean for k in ("مقدمة", "مقدمه", "خاتمة", "خاتمه", "وقفة", "وقفه", "فوج")
    ):
        return "intro_outro"
    return "other"


def _is_pure_estehlal_tag(tag_str):
    """Return True if tag is [المستهل] (not [الكسرة والمستهل])."""
    clean = re.sub(r"[\[\]\u064B-\u0652]", "", tag_str).strip()
    return ("مستهل" in clean and "كسر" not in clean) or clean.lower() == "chorus"


def _is_kasra_estehlal_tag(tag_str):
    """Return True if tag is [الكسرة والمستهل]."""
    clean = re.sub(r"[\[\]\u064B-\u0652]", "", tag_str).strip()
    return "كسر" in clean and "مستهل" in clean


def enforce_collective_estehlal_parentheses(text):
    """Module 51 (QC18): Wrap all Estehlal choir hemistichs in '(...)' before '..'."""
    blocks = re.split(r"(\[[^\]]+\])", text)
    if len(blocks) == 1:
        return text

    out_chunks = []
    current_tag = ""
    for chunk in blocks:
        if chunk.startswith("[") and chunk.endswith("]"):
            current_tag = chunk
            out_chunks.append(chunk)
            continue

        if _is_pure_estehlal_tag(current_tag):
            lines = chunk.splitlines()
            wrapped_lines = []
            for ln in lines:
                stripped = ln.strip()
                if not stripped:
                    wrapped_lines.append(ln)
                    continue
                has_dots = stripped.endswith("..")
                core = stripped[:-2].strip() if has_dots else stripped
                if not (core.startswith("(") and core.endswith(")")):
                    core = f"({core})"
                wrapped_lines.append(f"{core} .." if has_dots else core)
            out_chunks.append("\n".join(wrapped_lines))
        elif _is_kasra_estehlal_tag(current_tag):
            lines = chunk.splitlines()
            non_empty_indices = [i for i, ln in enumerate(lines) if ln.strip()]
            estehlal_idx_set = set(non_empty_indices[-4:]) if len(non_empty_indices) >= 8 else set()
            wrapped_lines = []
            for i, ln in enumerate(lines):
                if i not in estehlal_idx_set:
                    wrapped_lines.append(ln)
                    continue
                stripped = ln.strip()
                has_dots = stripped.endswith("..")
                core = stripped[:-2].strip() if has_dots else stripped
                if not (core.startswith("(") and core.endswith(")")):
                    core = f"({core})"
                wrapped_lines.append(f"{core} .." if has_dots else core)
            out_chunks.append("\n".join(wrapped_lines))
        else:
            out_chunks.append(chunk)
    return "".join(out_chunks)


def _format_tatweel(text_val, use_tatweel=False):
    """Return text with Tatweel preserved if use_tatweel=True, else clean space-separated."""
    if use_tatweel:
        return text_val
    return re.sub(r"\s+", " ", text_val.replace("ـ", "")).strip()


def normalize_iraqi_orthographic_gaf(text):
    """Normalize Iraqi orthographic 'كَـ' (Kaf + Fatha + Tatweel) into 'گ' (Gaf)."""
    return re.sub(r"ك(?:\u064e\u0640|\u0640\u064e)", "گ", text)


def normalize_demonstrative_hal(text, dialect="iraqi"):
    """Normalize attached demonstrative 'هالـ / هَالْـ' into authentic Iraqi/Bahrani phonetic forms."""
    dem_map = (
        DEMONSTRATIVE_HAL_BAHRANI_MAP if dialect == "bahrani" else DEMONSTRATIVE_HAL_IRAQI_MAP
    )
    result = text
    for raw_dem, phonetic_dem in dem_map.items():
        result = re.sub(rf"(?<!\S){re.escape(raw_dem)}(?!\S)", phonetic_dem, result)
    result = result.replace("يهل الغرب", "يَا هَلِ الغُرَبْ").replace("يَا هَلْ الغُرَبْ", "يَا هَلِ الغُرَبْ")
    return result


def repair_word_initial_sukun_and_diphthongs(text):
    """Module 49 (QC13 & QC14): Repair plain initial Sukun, strip feminine Haa Sukun, and leave
    medial diphthong glides (ي, و after Fatha) unmarked so Maddat elongate smoothly.
    """
    result = text
    for bad_sukun, repaired in WORD_INITIAL_SUKUN_REPAIR_MAP.items():
        result = re.sub(rf"(?<!\S){re.escape(bad_sukun)}(?!\S)", repaired, result)
    for fusha_diph, coll_mono in DIALECTAL_DIPHTHONG_AND_VOWEL_MAP.items():
        result = re.sub(rf"(?<!\S){re.escape(fusha_diph)}(?!\S)", coll_mono, result)
    # QC14: Leave medial diphthong glides (ي, و after Fatha) unmarked when followed by a letter in-word
    result = re.sub(
        r"\u064E([يو])\u0652(?=[\u0621-\u063A\u0641-\u064A\u067E\u0686\u06AF])",
        r"\u064E\1",
        result,
    )
    # Strip any remaining Sukun directly on word-final feminine Haa/Taa Marbuta before space/pause/paren/EOL
    result = re.sub(r"([هة])\u0652(?=\s|$|\.\.|[،\)])", r"\1", result)
    return result


def de_cliticize_and_separate_words(text, use_tatweel=False):
    """Module 41 & 49: Separate attached vocatives, prepositions, constructs, and clitics."""
    result = normalize_iraqi_orthographic_gaf(text)
    for raw_phrase, shaped_phrase in COLLOQUIAL_PHRASE_MAP.items():
        result = result.replace(raw_phrase, shaped_phrase)
    for attached, separated in WORD_SEPARATION_MAP.items():
        target = _format_tatweel(separated, use_tatweel=use_tatweel)
        result = re.sub(rf"(?<!\S)و{re.escape(attached)}(?!\S)", f"وَ {target}", result)
        result = re.sub(rf"(?<!\S){re.escape(attached)}(?!\S)", target, result)
    return result


def _finalize_hemistich_pause_sukun(segment):
    """Apply pause Tanween conversion and closed-consonant Sukun on a single hemistich."""
    seg = segment.strip()
    if not seg:
        return seg
    close_paren = ""
    if seg.endswith(")"):
        close_paren = ")"
        seg = seg[:-1].rstrip()
    seg = re.sub(r"(?:اً|ً)$", "َا", seg)
    seg = re.sub(r"[ٌٍُِ]$", "ْ", seg)
    seg = re.sub(r"([هة])\u0652$", r"\1", seg)
    if seg and not seg.endswith(("ْ", "ا", "ى", "و", "ي", "ه", "ة")):
        seg = seg + "ْ"
    return f"{seg}{close_paren}"


def resolve_dialectal_and_prosodic_tanween(text, dialect="iraqi", use_tatweel=False):
    """Module 40: Convert mid-line Tanween to phonetic Nunation and apply end-Sukun BEFORE '..'."""
    processed = de_cliticize_and_separate_words(text, use_tatweel=use_tatweel)
    for raw_phrase, phonetic_phrase in COLLOQUIAL_TANWEEN_MAP.items():
        processed = processed.replace(raw_phrase, phonetic_phrase)
    for raw_fusha, phonetic_fusha in FUSHA_MIDLINE_TANWEEN_MAP.items():
        processed = processed.replace(raw_fusha, phonetic_fusha)

    if dialect in ("iraqi", "bahrani", "iraqi_bahrani"):
        processed = re.sub(
            r"(\S+)ٍ\s+([تين])(?![اآى\u064B-\u0652])(\S+)",
            r"\1ِنْ \2ِ\3",
            processed,
        )

    processed = re.sub(r"(\S+)(?:اً|ً)(?=\s+(?!\.\.)\S)", r"\1َنْ", processed)
    processed = re.sub(r"(\S+)ٍ(?=\s+(?!\.\.)\S)", r"\1ِنْ", processed)
    processed = re.sub(r"(\S+)ٌ(?=\s+(?!\.\.)\S)", r"\1ُنْ", processed)

    lines = []
    for line in processed.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("["):
            lines.append(line)
            continue

        trailing_pause = ""
        if stripped.endswith(".."):
            trailing_pause = " .."
            stripped = stripped[:-2].rstrip()

        if ".." in stripped:
            parts = [p.strip() for p in stripped.split("..") if p.strip()]
            resolved_parts = [_finalize_hemistich_pause_sukun(part) for part in parts]
            stripped = " .. ".join(resolved_parts)
        else:
            stripped = _finalize_hemistich_pause_sukun(stripped)

        lines.append(f"{stripped}{trailing_pause}".strip())

    return repair_word_initial_sukun_and_diphthongs("\n".join(lines))


def shape_token_morphologically(token, word_map, use_tatweel=False):
    """Decompose prefixes (ال، و، ب، ك، ل) and shape the stem if present in word_map."""
    if token == "..":
        return token
    match = re.match(r"^([\(\[،]*)(.*?)([\)\]،]*)$", token)
    if not match:
        return token
    lead_punct, core, trail_punct = match.groups()
    if not core:
        return token

    if core in word_map:
        return f"{lead_punct}{_format_tatweel(word_map[core], use_tatweel=use_tatweel)}{trail_punct}"

    b_sep = "بِـ " if use_tatweel else "بِ "
    k_sep = "كَـ " if use_tatweel else "كَ "
    l_sep = "لِـ " if use_tatweel else "لِ "

    prefix_rules = (
        ("وبال", f"وَ {b_sep}ال"),
        ("وكال", f"وَ {k_sep}ال"),
        ("ولل", "وَ لِلْ"),
        ("وال", "وَ ال"),
        ("بال", f"{b_sep}ال"),
        ("كال", f"{k_sep}ال"),
        ("وب", f"وَ {b_sep}"),
        ("وك", f"وَ {k_sep}"),
        ("ول", f"وَ {l_sep}"),
        ("لل", "لِلْ"),
        ("ال", "ال"),
        ("و", "وَ "),
        ("ب", b_sep),
        ("ك", k_sep),
        ("ل", l_sep),
    )
    for raw_pref, vocalized_pref in prefix_rules:
        if core.startswith(raw_pref):
            stem = core[len(raw_pref) :]
            if stem in word_map:
                shaped_stem = _format_tatweel(word_map[stem], use_tatweel=use_tatweel)
                return f"{lead_punct}{vocalized_pref}{shaped_stem}{trail_punct}"
    return token


def shape_words_by_boundary(text, word_map, use_tatweel=False):
    """Apply prefix-aware morphological word shaping strictly on whitespace-delimited tokens."""
    out_lines = []
    for line in text.splitlines():
        tokens = line.split(" ")
        shaped_tokens = [
            shape_token_morphologically(tok, word_map, use_tatweel=use_tatweel) if tok else tok
            for tok in tokens
        ]
        out_lines.append(" ".join(shaped_tokens))
    return "\n".join(out_lines)


def detect_and_shape_dialect(text, enforce_iraqi_dhaa=None, use_tatweel=False):
    """Modules 43 & 49: Identify Pure Bahrani vs. Pure Iraqi vs. Neutral Fusion and shape tokens."""
    bahrani_hits = sum(1 for marker in BAHRANI_MARKERS if marker in text)
    iraqi_hits = sum(1 for marker in IRAQI_MARKERS if marker in text)

    if bahrani_hits > iraqi_hits:
        detected = "bahrani"
    elif iraqi_hits > bahrani_hits:
        detected = "iraqi"
    else:
        detected = "iraqi_bahrani"

    if enforce_iraqi_dhaa is None:
        enforce_iraqi_dhaa = detected == "iraqi"

    shaped = de_cliticize_and_separate_words(text, use_tatweel=use_tatweel)
    shaped = normalize_demonstrative_hal(shaped, dialect=detected)
    shaped = repair_word_initial_sukun_and_diphthongs(shaped)
    if detected == "bahrani":
        shaped = shaped.replace("إِعْلَه الجَمُرْ", "عَلَه الجَمِرْ")
        shaped = shape_words_by_boundary(shaped, BAHRANI_WORD_SHAPING_MAP, use_tatweel=use_tatweel)
        if enforce_iraqi_dhaa:
            shaped = shaped.replace("فَاضِلْ", "فَاظِلْ").replace("ضْلُوعِي", "ظْلُوعِي")
        maqam_rule = "3rd-Word Faizi Vibrato & Soft Bahrani Imala in Maqam Hijaz/Saba"
        dhad_mode = "Emphatic Iraqi Dhaa (ظ)" if enforce_iraqi_dhaa else "Standard/Bahrani Dhad (ض)"
        sound_dialect = "authentic Bahrani colloquial dialect"
    elif detected == "iraqi":
        shaped = shape_words_by_boundary(shaped, IRAQI_WORD_SHAPING_MAP, use_tatweel=use_tatweel)
        if enforce_iraqi_dhaa:
            shaped = (
                shaped.replace("فَاضِلْ", "فَاظِلْ")
                .replace("ضْلُوعِي", "ظْلُوعِي")
                .replace("مَا ضَلْ", "مَا ظَلْ")
            )
        maqam_rule = "Emphatic Iraqi Tafkheem & Final-Word Sudden Drop in Maqam Saba/Lami"
        dhad_mode = "Emphatic Iraqi Dhaa (ظ)" if enforce_iraqi_dhaa else "Dual Dhad/Dhaa Support"
        sound_dialect = "authentic Iraqi colloquial dialect"
    else:
        shaped = shape_words_by_boundary(shaped, HYBRID_WORD_SHAPING_MAP, use_tatweel=use_tatweel)
        if enforce_iraqi_dhaa:
            shaped = shaped.replace("فَاضِلْ", "فَاظِلْ").replace("ضْلُوعِي", "ظْلُوعِي")
        maqam_rule = (
            "Neutral Iraqi-Bahrani Fusion: Faizi 3rd-Word Vibrato + Karbalai Qarar Cadence "
            "in Maqam Saba/Bayati"
        )
        dhad_mode = "Emphatic Iraqi Dhaa (ظ)" if enforce_iraqi_dhaa else "Balanced Neutral Dhad (ض)"
        sound_dialect = "authentic Iraqi and Bahrani colloquial dialect"

    shaped = resolve_dialectal_and_prosodic_tanween(
        shaped, dialect=detected, use_tatweel=use_tatweel
    )
    shaped = repair_word_initial_sukun_and_diphthongs(shaped)
    return {
        "detected_dialect": detected,
        "sound_prompt_dialect_declaration": sound_dialect,
        "bahrani_score": bahrani_hits,
        "iraqi_score": iraqi_hits,
        "dhad_articulation": dhad_mode,
        "maqam_articulation_rule": maqam_rule,
        "shaped_lyrics": shaped,
    }


NON_SPLIT_PARTICLES = {
    "يا",
    "يَا",
    "و",
    "وَ",
    "ب",
    "بِ",
    "بِـ",
    "ل",
    "لِ",
    "لِـ",
    "من",
    "مِنْ",
    "في",
    "فِي",
    "إعله",
    "إِعْلَه",
    "عله",
    "عَلَه",
    "على",
    "عَلَى",
    "هل",
    "هَلْ",
    "إل",
    "إِلْ",
    "ما",
    "مَا",
    "لا",
    "لَا",
    "إش",
    "إِشْ",
}


def _strip_arabic_diacritics(text):
    """Remove Arabic Tashkeel, Tatweel, and punctuation for rhyme/Jinas comparison."""
    cleaned = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", text)
    cleaned = re.sub(r"[\(\)\[\]\u060C.\u061F!:\u00AB\u00BB\x22\x27\-]", "", cleaned)
    return cleaned.strip()


def _infer_unvocalized_word_syllables(word):
    """Estimate prosodic syllables for an unvocalized Arabic token."""
    letters = re.sub(r"[^\u0621-\u063A\u0641-\u064A\u067E\u0686\u06AF]", "", word)
    if not letters:
        return ["CV"]
    if letters.startswith("ال") and len(letters) > 2:
        letters = letters[1:]
    n_chars = len(letters)
    if n_chars <= 2:
        return ["CVC"]
    long_vowels = sum(1 for ch in letters[1:] if ch in "اويىآ")
    est = max(1, min(n_chars - 1, long_vowels + max(1, (n_chars - long_vowels) // 2)))
    return ["CV"] * est


def segment_arabic_prosodic_syllables(hemistich):
    """Segment an Arabic hemistich into prosodic CV/CVV/CVC syllables."""
    clean = re.sub(r"\[[^\]]*\]", " ", hemistich)
    clean = clean.replace("..", " ")
    clean = re.sub(r"[\(\)\u060C.\u061F!:\u00AB\u00BB\x22\x27]", " ", clean)
    tokens = [tok.strip() for tok in clean.split() if tok.strip()]
    if not tokens:
        return []

    syllables = []
    short_vowels = {"\u064E", "\u064F", "\u0650"}
    tanween_marks = {"\u064B", "\u064C", "\u064D"}

    for token in tokens:
        has_tashkeel = bool(re.search(r"[\u064B-\u0652]", token))
        if not has_tashkeel:
            syllables.extend(_infer_unvocalized_word_syllables(token))
            continue

        word_syls = []
        idx = 0
        length = len(token)
        while idx < length:
            ch = token[idx]
            if not ("\u0621" <= ch <= "\u064A" or ch in "پچگ"):
                idx += 1
                continue
            if ch == "آ":
                word_syls.append("CVV")
                idx += 1
                continue

            marks = []
            next_idx = idx + 1
            while next_idx < length and ("\u064B" <= token[next_idx] <= "\u0652" or token[next_idx] == "\u0670"):
                marks.append(token[next_idx])
                next_idx += 1

            if "\u0651" in marks and word_syls and not word_syls[-1].endswith("C"):
                word_syls[-1] = word_syls[-1] + "C"

            if any(m in tanween_marks for m in marks):
                word_syls.append("CVC")
            elif any(m in short_vowels or m == "\u0670" for m in marks):
                if next_idx < length and token[next_idx] in "اويى":
                    glide_idx = next_idx + 1
                    glide_marks = []
                    while glide_idx < length and "\u064B" <= token[glide_idx] <= "\u0652":
                        glide_marks.append(token[glide_idx])
                        glide_idx += 1
                    if not any(m in short_vowels or m == "\u0651" for m in glide_marks):
                        word_syls.append("CVV")
                        idx = glide_idx
                        continue
                word_syls.append("CV")
            elif "\u0652" in marks:
                if word_syls:
                    word_syls[-1] = word_syls[-1] + "C"
            elif ch in "اويى" and word_syls and word_syls[-1] == "CV":
                word_syls[-1] = "CVV"

            idx = next_idx

        if not word_syls:
            word_syls = _infer_unvocalized_word_syllables(token)
        syllables.extend(word_syls)

    return syllables


def count_arabic_syllables(hemistich):
    """Count prosodic syllables (CV/CVV/CVC) in an Arabic hemistich."""
    return len(segment_arabic_prosodic_syllables(hemistich))


def _extract_poem_hemistichs(lines):
    """Normalize string, flat line list, or nested stanza list into clean hemistich strings."""
    if isinstance(lines, str):
        raw_lines = lines.splitlines()
    elif lines and isinstance(lines[0], (list, tuple)):
        raw_lines = [ln for stanza in lines for ln in stanza]
    else:
        raw_lines = list(lines)

    hemistichs = []
    for raw in raw_lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("["):
            continue
        if stripped.endswith(".."):
            stripped = stripped[:-2].strip()
        if stripped.startswith("(") and stripped.endswith(")"):
            stripped = stripped[1:-1].strip()
        if ".." in stripped:
            parts = [p.strip().strip("()").strip() for p in stripped.split("..") if p.strip()]
            hemistichs.extend([p for p in parts if p])
        elif stripped:
            hemistichs.append(stripped)
    return hemistichs


def validate_stage1_iso_syllabic_lock(lines, max_syllable_spread=3):
    """Module 38 & 48 (Pillar 5 / QC3): Verify uniform prosodic syllable spread in Stage 1."""
    hemistichs = _extract_poem_hemistichs(lines)
    if not hemistichs:
        return {
            "is_stage1_locked": False,
            "hemistich_count": 0,
            "min_syllables": 0,
            "max_syllables": 0,
            "syllable_spread": 0,
            "refrain_consistent": False,
            "syllable_counts": [],
        }

    counts = [count_arabic_syllables(h) for h in hemistichs]
    min_syl = min(counts)
    max_syl = max(counts)
    spread = max_syl - min_syl

    refrain_consistent = True
    if isinstance(lines, (list, tuple)) and lines and isinstance(lines[0], (list, tuple)):
        first_stanza_norm = [_strip_arabic_diacritics(ln) for ln in lines[0] if ln.strip()]
        if len(lines) >= 3:
            last_stanza_norm = [_strip_arabic_diacritics(ln) for ln in lines[-1] if ln.strip()]
            if len(first_stanza_norm) == len(last_stanza_norm):
                refrain_consistent = first_stanza_norm == last_stanza_norm

    return {
        "is_stage1_locked": spread <= max_syllable_spread,
        "hemistich_count": len(hemistichs),
        "min_syllables": min_syl,
        "max_syllables": max_syl,
        "syllable_spread": spread,
        "refrain_consistent": refrain_consistent,
        "syllable_counts": counts,
    }


def _check_collective_estehlal_lock(text):
    """Return True if all [المستهل] lines and final 4 [الكسرة والمستهل] lines are wrapped in (...)."""
    blocks = re.split(r"(\[[^\]]+\])", text)
    if len(blocks) == 1:
        return True

    current_tag = ""
    for chunk in blocks:
        if chunk.startswith("[") and chunk.endswith("]"):
            current_tag = chunk
            continue
        non_empty = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if not non_empty:
            continue

        clean_tag = re.sub(r"[\[\]\u064B-\u0652]", "", current_tag).strip()
        if "مستهل" in clean_tag and "كسر" not in clean_tag:
            for ln in non_empty:
                core = ln[:-2].strip() if ln.endswith("..") else ln
                if not (core.startswith("(") and core.endswith(")")):
                    return False
        elif "كسر" in clean_tag and "مستهل" in clean_tag and len(non_empty) >= 8:
            for ln in non_empty[-4:]:
                core = ln[:-2].strip() if ln.endswith("..") else ln
                if not (core.startswith("(") and core.endswith(")")):
                    return False
    return True


def audit_legendary_latmiya_pillars(text):
    """Module 48 & 51: Audit poem against the 5 Golden Pillars & Collective Estehlal Lock."""
    tags = re.findall(r"\[[^\]]+\]", text)
    forbidden_tags = [
        t
        for t in tags
        if re.sub(r"[\[\]\s]", "", t).lower() in ("bridge", "pre-chorus", "prechorus", "chorus", "verse")
    ]
    classified = [classify_section_tag(t) for t in tags]
    has_chorus = "chorus" in classified
    has_verse = "verse" in classified

    blocks = re.split(r"(\[[^\]]+\])", text)
    first_estehlal_lines = []
    current_tag = ""
    for chunk in blocks:
        if chunk.startswith("[") and chunk.endswith("]"):
            current_tag = chunk
            continue
        if _is_pure_estehlal_tag(current_tag) and not first_estehlal_lines:
            first_estehlal_lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]

    hook_short = bool(first_estehlal_lines) and (2 <= len(first_estehlal_lines) <= 6) and all(
        len(ln.replace("..", "").strip("() ").split()) <= 6 for ln in first_estehlal_lines
    )
    collective_locked = _check_collective_estehlal_lock(text)
    three_part_ok = has_chorus and has_verse and not forbidden_tags
    no_inline_json = "{" not in text and "}" not in text
    iso_report = validate_stage1_iso_syllabic_lock(text)
    vertical_lines = [
        ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("[")
    ]

    pillars = {
        "pillar_1_estehlal_hook": hook_short,
        "pillar_2_collective_estehlal_parentheses": collective_locked,
        "pillar_3_three_part_architecture": three_part_ok,
        "pillar_4_clean_lyrics_channel_no_json": no_inline_json and not forbidden_tags,
        "pillar_5_iso_syllabic_lock": iso_report["is_stage1_locked"],
    }
    return {
        "all_five_pillars_passed": all(pillars.values()),
        "pillars": pillars,
        "collective_estehlal_locked": collective_locked,
        "forbidden_tags_found": forbidden_tags,
        "total_vertical_lines": len(vertical_lines),
        "iso_syllabic_report": iso_report,
    }


def lint_poem(text, stage=1):
    """Unified QC1-QC18 Poem Linter for V48.5 OMNI-ARCHITECT."""
    dialect_report = detect_and_shape_dialect(text)
    tokens_raw = re.findall(r"[^\s\(\)\[\]،.]+", text)

    slurring_risks = sorted(
        {
            tok
            for tok in tokens_raw
            if tok in WORD_SEPARATION_MAP or tok in DEMONSTRATIVE_HAL_IRAQI_MAP
        }
    )
    raw_tanween_tokens = sorted({tok for tok in tokens_raw if re.search(r"[\u064B\u064C\u064D]", tok)})

    has_fusha = any(marker in text for marker in FUSHA_MARKERS)
    has_colloquial = any(marker in text for marker in IRAQI_MARKERS) or any(
        marker in text for marker in BAHRANI_MARKERS
    )
    fusha_colloquial_mix = bool(stage == 1 and has_fusha and has_colloquial)

    is_colloquial_context = has_colloquial or dialect_report["detected_dialect"] in ("iraqi", "bahrani")
    fusha_clash_tokens = []
    if is_colloquial_context and not (has_fusha and not has_colloquial):
        fusha_clash_tokens = sorted(
            {
                tok
                for tok in tokens_raw
                if tok in FUSHA_DIALECT_CLASH_TOKENS or tok == "عَلَى"
            }
        )

    marked_diphthongs = sorted(
        set(
            re.findall(
                r"\S*\u064E[يو]\u0652[\u0621-\u063A\u0641-\u064A\u067E\u0686\u06AF]\S*",
                text,
            )
        )
    )
    initial_sukun_tokens = sorted(
        {
            tok
            for tok in tokens_raw
            if re.match(r"^[\u0621-\u064A\u067E\u0686\u06AF]\u0652", tok)
        }
    )
    closed_haa_sukun = sorted(
        set(re.findall(r"\S*[هة]\u0652(?=\s|$|\.\.|[،\)])", text))
    )

    tags = re.findall(r"\[[^\]]+\]", text)
    forbidden_tags = [
        t
        for t in tags
        if re.sub(r"[\[\]\s]", "", t).lower() in ("bridge", "pre-chorus", "prechorus", "chorus", "verse")
    ]
    english_tags = [t for t in tags if re.search(r"[A-Za-z]", t)]
    text_without_tags = re.sub(r"\[[^\]]+\]", " ", text)
    latin_outside_tags = sorted(set(re.findall(r"[A-Za-z]+", text_without_tags)))

    inline_json = "{" in text or "}" in text
    solo_estehlal_violation = not _check_collective_estehlal_lock(text)
    iso_report = validate_stage1_iso_syllabic_lock(text)
    repaired_lyrics = enforce_collective_estehlal_parentheses(dialect_report["shaped_lyrics"])

    ready = (
        not slurring_risks
        and not raw_tanween_tokens
        and not fusha_colloquial_mix
        and not fusha_clash_tokens
        and not marked_diphthongs
        and not initial_sukun_tokens
        and not closed_haa_sukun
        and not forbidden_tags
        and not english_tags
        and not latin_outside_tags
        and not inline_json
        and not solo_estehlal_violation
        and iso_report["is_stage1_locked"]
    )

    return {
        "skill_version": SKILL_VERSION,
        "stage": stage,
        "ready_for_generation": ready,
        "detected_dialect": dialect_report["detected_dialect"],
        "sound_prompt_dialect_declaration": dialect_report["sound_prompt_dialect_declaration"],
        "slurring_risks_detected": slurring_risks,
        "raw_tanween_detected": raw_tanween_tokens,
        "fusha_colloquial_mixing_in_stage1": fusha_colloquial_mix,
        "fusha_dialect_clash_detected": fusha_clash_tokens,
        "marked_medial_diphthong_glides_detected": marked_diphthongs,
        "word_initial_sukun_detected": initial_sukun_tokens,
        "closed_feminine_haa_sukun_detected": closed_haa_sukun,
        "forbidden_section_tags_detected": forbidden_tags,
        "english_section_tags_detected": english_tags,
        "latin_chars_outside_tags_detected": latin_outside_tags,
        "inline_json_in_lyrics": inline_json,
        "solo_estehlal_violation": solo_estehlal_violation,
        "iso_syllabic_report": iso_report,
        "auto_repaired_lyrics": repaired_lyrics,
    }


def validate_abudhiyah_jinas(lines):
    """Module 46: Validate 4-line Iraqi Abudhiyah (3 homophonous Jinas lines + 4th ending in -يَّه)."""
    hemistichs = _extract_poem_hemistichs(lines)
    if len(hemistichs) != 4:
        return {
            "is_valid_abudhiyah": False,
            "hemistich_count": len(hemistichs),
            "error": "الأبوذية يجب أن تتكون من 4 أشطر بالضبط.",
        }

    end_words_raw = [h.split()[-1] if h.split() else "" for h in hemistichs]
    end_words_norm = [_strip_arabic_diacritics(w) for w in end_words_raw]
    jinas_match = len(set(end_words_norm[:3])) == 1 and bool(end_words_norm[0])
    fourth_word = end_words_norm[3]
    ends_with_yah = fourth_word.endswith(("يه", "ية"))

    return {
        "is_valid_abudhiyah": bool(jinas_match and ends_with_yah),
        "hemistich_count": 4,
        "jinas_word": end_words_raw[0] if jinas_match else None,
        "end_words": end_words_raw,
        "jinas_three_hemistichs_matched": jinas_match,
        "fourth_hemistich_yah_ending": ends_with_yah,
        "melodic_contour_blueprint": {
            "hemistich_1": "التأسيس في القرار والوسط مع تثبيت كلمة الجناس الأولى",
            "hemistich_2": "التموج النغمي والترجيع في مقام اللامي أو الصبا",
            "hemistich_3": "التصعيد الدرامي إلى ذروة الجواب (الحويزاوي / العلواني)",
            "hemistich_4_qafla": "الكسرة الفراتية الهابطة إلى القرار والختم بمدّة (-يَّه)",
        },
    }


def validate_zuhayri_mawal(lines):
    """Module 46: Validate 7-line Iraqi Zuhayri Mawal (AAA_B_AAA or AAA_BBB_A with 4th-line Arq)."""
    hemistichs = _extract_poem_hemistichs(lines)
    if len(hemistichs) != 7:
        return {
            "is_valid_zuhayri": False,
            "hemistich_count": len(hemistichs),
            "error": "الموّال السبعوي (الزهيري) يجب أن يتكون من 7 أشطر.",
        }

    end_words = [_strip_arabic_diacritics(h.split()[-1]) if h.split() else "" for h in hemistichs]
    first_three_match = len(set(end_words[:3])) == 1 and bool(end_words[0])
    seventh_matches_first = end_words[6] == end_words[0]
    arq_distinct = end_words[3] != end_words[0] and bool(end_words[3])
    middle_pattern = "AAA_BBB_A" if len(set(end_words[3:6])) == 1 else "AAA_B_AAA"

    return {
        "is_valid_zuhayri": bool(first_three_match and seventh_matches_first and arq_distinct),
        "hemistich_count": 7,
        "scheme_detected": middle_pattern,
        "rhyme_a_word": end_words[0],
        "rhyme_b_arq_word": end_words[3],
        "end_words": end_words,
    }


def format_ashouri_interactive_ahaat(text):
    """Module 46: Append '.. (آه .. آه) ..' after couplets for 1.5s congregation interaction."""
    out_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("["):
            out_lines.append(line)
            continue
        if "(آه .. آه)" in stripped:
            out_lines.append(stripped)
            continue
        base = stripped[:-2].strip() if stripped.endswith("..") else stripped
        out_lines.append(f"{base} .. (آه .. آه) ..")
    return "\n".join(out_lines)


def format_bahrani_antiphonal_faujain(estehlal_lines):
    """Module 46: Format Bahrani Mawkib lines into Antiphonal Dual-Choir ([الفَوْج الأَوَّل] / [الفَوْج الثَّانِي])."""
    if isinstance(estehlal_lines, str):
        clean_lines = [
            ln.strip() for ln in estehlal_lines.splitlines() if ln.strip() and not ln.strip().startswith("[")
        ]
    else:
        clean_lines = [ln.strip() for ln in estehlal_lines if ln.strip()]

    midpoint = max(1, len(clean_lines) // 2)
    fauj_1 = clean_lines[:midpoint]
    fauj_2 = clean_lines[midpoint:] if clean_lines[midpoint:] else clean_lines[:midpoint]

    def _wrap_choir_line(item):
        core = item[:-2].strip() if item.endswith("..") else item
        if not (core.startswith("(") and core.endswith(")")):
            core = f"({core})"
        return f"{core} .."

    block_1 = "\n".join(_wrap_choir_line(ln) for ln in fauj_1)
    block_2 = "\n".join(_wrap_choir_line(ln) for ln in fauj_2)
    return f"[الفَوْج الأَوَّل]\n{block_1}\n\n[الفَوْج الثَّانِي]\n{block_2}"


def split_long_lines_for_steady_pacing(text, max_words_per_line=5):
    """Module 48 (QC6): Split overly long lines into balanced vertical lines without stranding proclitics."""
    out_lines = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("["):
            out_lines.append(raw_line)
            continue

        is_wrapped = False
        base = stripped[:-2].strip() if stripped.endswith("..") else stripped
        if base.startswith("(") and base.endswith(")"):
            is_wrapped = True
            base = base[1:-1].strip()

        if ".." in base:
            segments = [seg.strip() for seg in base.split("..") if seg.strip()]
            for seg in segments:
                out_lines.append(f"({seg}) .." if is_wrapped else f"{seg} ..")
            continue

        words = base.split()
        if len(words) <= max_words_per_line:
            out_lines.append(f"({base}) .." if is_wrapped else f"{base} ..")
            continue

        split_idx = len(words) // 2
        while split_idx > 1 and words[split_idx - 1] in NON_SPLIT_PARTICLES:
            split_idx -= 1
        if words[split_idx - 1] in NON_SPLIT_PARTICLES and split_idx < len(words) - 1:
            split_idx += 1

        part1 = " ".join(words[:split_idx])
        part2 = " ".join(words[split_idx:])
        if is_wrapped:
            out_lines.append(f"({part1}) ..")
            out_lines.append(f"({part2}) ..")
        else:
            out_lines.append(f"{part1} ..")
            out_lines.append(f"{part2} ..")

    return "\n".join(out_lines)


def build_multi_tor_melodic_bridge(
    primary_tor, secondary_tor, primary_maqam="saba", secondary_maqam="lami", base_bpm=58
):
    """Module 46 & 52: Build a Common Jins Multi-Tor transition blueprint for Remix > Extend."""
    p_key = primary_maqam.lower()
    s_key = secondary_maqam.lower()
    compatible_targets = COMMON_JINS_GRAPH.get(p_key, [])
    jins_compatible = s_key == p_key or s_key in compatible_targets
    pivot_maqam = s_key if jins_compatible else (compatible_targets[0] if compatible_targets else "bayati")

    return {
        "primary_tor": primary_tor,
        "secondary_tor": secondary_tor,
        "primary_maqam": p_key,
        "secondary_maqam": s_key,
        "common_jins_compatible": jins_compatible,
        "recommended_pivot_maqam": pivot_maqam,
        "stage_1_bpm": base_bpm,
        "stage_2_extend_bpm": base_bpm,
        "execution_method": "Stage 1 Root Track -> Remix > Extend (Common Jins Modulation)",
    }


def load_v48_5_constitution():
    """Load the canonical V48.5 OMNI-ARCHITECT JSON constitution from references/."""
    constitution_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "references",
            "hussaini_os_v48_5_constitution.json",
        )
    )
    with open(constitution_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_four_stage_latmiya_plan(dialect="iraqi"):
    """Module 52: Return the empirically verified 4-Stage Common Jins Maqam & Atwar progression."""
    is_bahrani = dialect == "bahrani"
    stage_1_prompt = (
        MASTER_SOUND_PROMPTS_V48_5["bahrani_muthakkal_56bpm_saba"]
        if is_bahrani
        else MASTER_SOUND_PROMPTS_V48_5["karbalai_muthakkal_58bpm_saba_zamzam_v48_5_deep_root"]
    )
    return {
        "protocol_version": SKILL_VERSION,
        "dialect": dialect,
        "stage_0_optional_fusha_intro": {
            "session_rule": "Separate New Session (0 BPM Free-Tempo Rubato — Exclusive Weeping Zone)",
            "bpm": 0,
            "maqam": "saba",
            "sound_prompt": MASTER_SOUND_PROMPTS_V48_5["minbar_nai_0bpm_rubato_saba_exclusive_weeping"],
        },
        "stage_1_root_track": {
            "execution": "New Session -> Step 1 Pre-Conditioning JSON -> Step 2 Stage 1 JSON",
            "bpm": 56 if is_bahrani else 58,
            "maqam": "saba" if is_bahrani else "saba_zamzam",
            "secondary_maqam": "bayati",
            "sound_prompt": stage_1_prompt,
        },
        "stage_2_extend_1_narrative": {
            "execution": "Remix > Extend (Stage 2 JSON — Common Jins Modulation)",
            "bpm": 66 if is_bahrani else 58,
            "maqam": "hijaz" if is_bahrani else "lami",
            "common_jins_from_stage_1": True,
            "sound_prompt": (
                MASTER_SOUND_PROMPTS_V48_5["bahrani_tawshih_faizi_66bpm_hijaz"]
                if is_bahrani
                else MASTER_SOUND_PROMPTS_V48_5["rukbani_nassari_58bpm_lami_saba_v48_5_stage2"]
            ),
        },
        "stage_3_extend_2_jawab_climax": {
            "execution": "Remix > Extend (Stage 3 JSON — Ashouri Jawab Peak)",
            "bpm": 84 if is_bahrani else 58,
            "maqam": "saba_zamzam" if not is_bahrani else "hijaz",
            "secondary_maqam": "hijaz",
            "common_jins_from_stage_2": True,
            "sound_prompt": (
                MASTER_SOUND_PROMPTS_V48_5["bahrani_waqfa_84bpm_hijaz_bayati"]
                if is_bahrani
                else MASTER_SOUND_PROMPTS_V48_5[
                    "karbalai_ashouri_jawab_climax_58bpm_saba_zamzam_hijaz_v48_5_stage3"
                ]
            ),
        },
        "stage_4_extend_3_kasra_finale": {
            "execution": "Remix > Extend (Stage 4 JSON) -> Local 5-Track DSP (3.0s Audio Drop + -14.0 LUFS)",
            "bpm": 56,
            "maqam": "saba" if is_bahrani else "lami",
            "audio_drop_sec": 3.0,
            "common_jins_from_stage_3": True,
            "sound_prompt": (
                MASTER_SOUND_PROMPTS_V48_5["bahrani_muthakkal_56bpm_saba"]
                if is_bahrani
                else MASTER_SOUND_PROMPTS_V48_5["karbalai_wahsha_lami_kasra_56bpm_finale_v48_5_stage4"]
            ),
        },
    }


def recommend_tor_and_rhythm_for_poem(text):
    """Module 46, 48 & 52: Recommend Poetic Meter, Performance Tor, DSP Mode, BPM & V48.5 Prompt."""
    dialect_info = detect_and_shape_dialect(text)
    dialect = dialect_info["detected_dialect"]
    iso = validate_stage1_iso_syllabic_lock(text)
    avg_syl = (
        int(round(sum(iso["syllable_counts"]) / len(iso["syllable_counts"])))
        if iso["syllable_counts"]
        else 8
    )

    service_kw = ("خادم", "خدمنك", "أخدمنك", "هنيالي", "موكب", "مشايه", "مشاية", "راية")
    heroic_kw = ("عباس", "كفيل", "حيدر", "كرار", "صوله", "سيف", "زنجيل")
    shoor_kw = ("شور", "حسين حسين", "لبيك")

    if any(k in text for k in shoor_kw):
        mode = "shoor"
        bpm = 132
        maqam = "kurd"
        meter = "rukbani"
        tor = "tor_darj_karbalai"
        prompt = MASTER_SOUND_PROMPTS_V48_5["karbalai_shoor_132bpm_kurd"]
    elif any(k in text for k in heroic_kw):
        if dialect == "bahrani":
            mode = "bahrani_haidari"
            bpm = 96
            maqam = "hijaz"
            meter = "muwashah"
            tor = "tor_bahrani_haidari"
            prompt = MASTER_SOUND_PROMPTS_V48_5["bahrani_haidari_96bpm_hijaz"]
        else:
            mode = "zanjeel_iraqi"
            bpm = 80
            maqam = "hijaz"
            meter = "muwashah"
            tor = "tor_darj_karbalai"
            prompt = MASTER_SOUND_PROMPTS_V48_5["zanjeel_procession_80bpm_hijaz"]
    elif any(k in text for k in service_kw):
        mode = "bandari"
        bpm = 74
        maqam = "bayati"
        meter = "rukbani"
        tor = "tor_darj_karbalai"
        prompt = MASTER_SOUND_PROMPTS_V48_5["karbalai_mawkib_daraj_74bpm_bayati_hijaz"]
    elif dialect == "bahrani":
        mode = "bahrani_muthakkal"
        bpm = 56
        maqam = "saba"
        meter = "faizi"
        tor = "tor_muthakkal_bahrani"
        prompt = MASTER_SOUND_PROMPTS_V48_5["bahrani_muthakkal_56bpm_saba"]
    elif dialect == "iraqi_bahrani":
        mode = "thaqeel_muwazza"
        bpm = 58
        maqam = "saba"
        meter = "nassari"
        tor = "tor_ashouri"
        prompt = MASTER_SOUND_PROMPTS_V48_5["iraqi_bahrani_58bpm_saba_fusion_master"]
    else:
        mode = "thaqeel_muwazza"
        bpm = 60
        maqam = "bayati"
        meter = "nassari" if avg_syl >= 7 else "rukbani"
        tor = "tor_ashouri"
        prompt = MASTER_SOUND_PROMPTS_V48_5["karbalai_nazla_60bpm_bayati_saba_v48_5_root"]

    return {
        "detected_dialect": dialect,
        "average_syllables_per_hemistich": avg_syl,
        "recommended_poetic_meter": meter,
        "recommended_performance_tor": tor,
        "recommended_dsp_mode": mode,
        "recommended_bpm": bpm,
        "recommended_maqam": maqam,
        "master_sound_prompt": prompt,
    }


def build_vocal_genre_profile(genre="latmiya", dialect="iraqi", maqam=None, bpm=None):
    """Module 47 & 50: Build strict acoustic firewall & Sound prompt for 4 religious vocal genres."""
    g_key = genre.strip().lower()
    if g_key == "latmiya":
        chosen_maqam = (maqam or "saba").lower()
        chosen_bpm = 60 if bpm is None else int(bpm)
        if chosen_bpm == 0:
            prompt = MASTER_SOUND_PROMPTS_V48_5["minbar_nai_0bpm_rubato_saba_exclusive_weeping"]
        elif dialect == "bahrani":
            prompt = MASTER_SOUND_PROMPTS_V48_5["bahrani_muthakkal_56bpm_saba"]
            chosen_bpm = 56 if bpm is None else chosen_bpm
        elif dialect == "iraqi_bahrani":
            prompt = MASTER_SOUND_PROMPTS_V48_5["iraqi_bahrani_58bpm_saba_fusion_master"]
            chosen_bpm = 58 if bpm is None else chosen_bpm
        else:
            prompt = MASTER_SOUND_PROMPTS_V48_5["karbalai_nazla_60bpm_bayati_saba_v48_5_root"]

        prompt_lower = prompt.lower()
        leakage = [
            term
            for term in LATMIYA_SONG_LEAKAGE_BLACKLIST
            if term in prompt_lower and not (chosen_bpm == 0 and term == "weeping")
        ]
        return {
            "genre": "latmiya",
            "dialect": dialect,
            "maqam": chosen_maqam,
            "bpm": chosen_bpm,
            "uses_chest_latm": chosen_bpm > 0,
            "crying_isolated_to_zero_bpm": True,
            "sound_prompt": prompt,
            "song_leakage_terms_detected": leakage,
        }

    if g_key == "nasheed":
        chosen_maqam = (maqam or "bayati").lower()
        chosen_bpm = 90 if bpm is None else int(bpm)
        return {
            "genre": "nasheed",
            "dialect": dialect,
            "maqam": chosen_maqam,
            "bpm": chosen_bpm,
            "uses_chest_latm": False,
            "sound_prompt": (
                f"Spiritual Islamic Vocal Nasheed, Maqam {chosen_maqam.capitalize()}, {chosen_bpm} BPM, "
                "warm resonant Baritone lead vocal, uplifting male choir harmony, gentle acoustic frame "
                "drum Daf pulse, spacious hall reverb, No Western Pop Synths"
            ),
            "song_leakage_terms_detected": [],
        }

    if g_key == "ibtihalat":
        chosen_maqam = (maqam or "saba").lower()
        return {
            "genre": "ibtihalat",
            "dialect": "fusha",
            "maqam": chosen_maqam,
            "bpm": 0,
            "uses_chest_latm": False,
            "sound_prompt": (
                f"Classical Spiritual Arabic Ibtihalat supplication, strict free-tempo Rubato, Maqam "
                f"{chosen_maqam.capitalize()}, authentic Classical Arabic articulation, resonant solo "
                "Mubtahil Baritone voice, intricate 24-EDO microtonal melisma, 3.8s grand Mosque dome "
                "reverb, Pure Solo Acapella No Percussion No Instruments"
            ),
            "song_leakage_terms_detected": [],
        }

    if g_key == "tawashih":
        chosen_maqam = (maqam or "hijaz").lower()
        chosen_bpm = 74 if bpm is None else int(bpm)
        return {
            "genre": "tawashih",
            "dialect": dialect,
            "maqam": chosen_maqam,
            "bpm": chosen_bpm,
            "uses_chest_latm": False,
            "sound_prompt": (
                f"Traditional Islamic Vocal Tawashih Muwashah, Maqam {chosen_maqam.capitalize()}, "
                f"{chosen_bpm} BPM, commanding solo Munshid Baritone vocal with antiphonal unison male "
                "Bitanah choir responses, microtonal Eastern ornamentation, warm courtyard reverb, "
                "Pure Vocal Ensemble No Melodic Instruments"
            ),
            "song_leakage_terms_detected": [],
        }

    raise ValueError(f"Unsupported religious vocal genre: {genre}")


def build_flowmusic_json_preconditioning(
    maqam="saba_zamzam",
    bpm=58,
    dialect="iraqi",
    tor_style="heavy Karbalai Muthakkal and Nazla style",
    reference_clip_id=None,
):
    """Module 39, 51 & 53: Build Step-1 Producer Chat Session Pre-Conditioning JSON (V48.5 Rev 2)."""
    profile = build_vocal_genre_profile(genre="latmiya", dialect=dialect, maqam=maqam, bpm=bpm)
    dialect_decl = (
        "authentic Bahrani colloquial dialect"
        if dialect == "bahrani"
        else (
            "authentic Iraqi and Bahrani colloquial dialect"
            if dialect == "iraqi_bahrani"
            else "authentic Iraqi colloquial dialect"
        )
    )
    return {
        "protocol_name": "Hussaini_Production_Studio_OS_V48_5_OMNI_ARCHITECT",
        "skill_version": SKILL_VERSION,
        "session_mode": "Pre_Conditioning_Lock_Wait_For_Stage_JSON",
        "channel_routing": {
            "producer_chat": "JSON Pre-Conditioning & Per-Stage/Per-Section Orchestration ONLY",
            "compose_lyrics_panel": "Pure Vocalized Arabic Poems & Arabic Section Headers ONLY (Zero JSON / Zero English)",
        },
        "reference_clip_id": reference_clip_id,
        "acoustic_lock": {
            "genre": "Pure Acapella Hussaini Latmiya",
            "tuning_system": "24-EDO Arabic Microtonal Maqam",
            "primary_maqam": maqam,
            "bpm": bpm,
            "tor_style": tor_style,
            "dialect_isolation": dialect_decl,
            "lead_vocal": "Commanding deep resonant Jawhari Baritone",
            "collective_estehlal_choir": "100% Unison Male Raddada Choir on all (...) Estehlal lines",
            "crying_isolation": "Zero background weeping in rhythmic 54-132 BPM Latmiyas (0 BPM Rubato only)",
            "sound_prompt": profile["sound_prompt"],
        },
    }


def build_stage_orchestration_json(
    poem_text, stage_id="stage_1_root", title="قصيدة حسينية", global_bpm=58
):
    """Module 53 (QC19): Build complete Per-Stage & Per-Section JSON orchestration payload."""
    normalized_input = poem_text.replace("\\n", "\n")
    dialect_info = detect_and_shape_dialect(normalized_input)
    dialect = dialect_info["detected_dialect"]
    shaped_text = enforce_collective_estehlal_parentheses(dialect_info["shaped_lyrics"])

    bpm_val = int(global_bpm)
    if bpm_val == 0 or "stage_0" in stage_id:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["minbar_nai_0bpm_rubato_saba_exclusive_weeping"]
        bpm_val = 0
    elif dialect == "bahrani":
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["bahrani_muthakkal_56bpm_saba"]
    elif dialect == "iraqi_bahrani":
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["iraqi_bahrani_58bpm_saba_fusion_master"]
    elif "stage_2" in stage_id:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["rukbani_nassari_58bpm_lami_saba_v48_5_stage2"]
    elif "stage_3" in stage_id:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5[
            "karbalai_ashouri_jawab_climax_58bpm_saba_zamzam_hijaz_v48_5_stage3"
        ]
    elif "stage_4" in stage_id:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["karbalai_wahsha_lami_kasra_56bpm_finale_v48_5_stage4"]
    elif bpm_val <= 58:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["karbalai_muthakkal_58bpm_saba_zamzam_v48_5_deep_root"]
    else:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["karbalai_nazla_60bpm_bayati_saba_v48_5_root"]

    raw_blocks = re.split(r"(\[[^\]]+\])", shaped_text)
    parsed_sections = []
    if len(raw_blocks) == 1:
        wrapped_block = enforce_collective_estehlal_parentheses(f"[المُسْتَهَلّ]\n{shaped_text}")
        parsed_sections.append(("[المُسْتَهَلّ]", wrapped_block.split("\n", 1)[-1]))
    else:
        cur_tag = "[المُسْتَهَلّ]"
        for chunk in raw_blocks:
            if chunk.startswith("[") and chunk.endswith("]"):
                cur_tag = chunk
            elif chunk.strip():
                parsed_sections.append((cur_tag, chunk))

    sections_out = []
    for sec_tag, body in parsed_sections:
        lines = []
        for raw_ln in body.splitlines():
            clean_ln = raw_ln.strip()
            if not clean_ln:
                continue
            if not clean_ln.endswith(".."):
                clean_ln = f"{clean_ln} .."
            lines.append(clean_ln)
        if not lines:
            continue

        iso_sec = validate_stage1_iso_syllabic_lock(lines)
        is_estehlal = _is_pure_estehlal_tag(sec_tag)
        is_kasra = _is_kasra_estehlal_tag(sec_tag)
        if is_estehlal:
            performer = "100% Wide Unison Male Raddada Congregation Choir (Zero Solo Lead)"
            tor_maqam = "Tor Muthakkal Karbalai — 24-EDO Maqam Saba Zamzam & Bayati (Qarar & Jawab octave unison)"
            spatial = "85% wide L/R Husseiniya hall stereo field, 3.5s dome reverb"
        elif is_kasra:
            performer = "4 Solo Maqam Lami Kasra Lines -> 4 Unison Raddada Congregation Estehlal Lines"
            tor_maqam = "Tor Lami Kasra — 24-EDO Maqam Lami descending to Qarar tonic"
            spatial = "Center dry Radood on Kasra (3.0s Latm drop) -> 85% wide Raddada return"
        else:
            performer = "Solo Commanding Jawhari Baritone Radood (Unwrapped Lines)"
            tor_maqam = "Tor Karbalai Nazla — 24-EDO Maqam Saba Zamzam & Bayati rising to Jawab climb"
            spatial = "100% center dry-forward vocal presence with 310ms analog tape echo"

        sections_out.append(
            {
                "section_tag": sec_tag,
                "performer": performer,
                "meter_and_syllables": (
                    f"Iso-syllabic lock ({iso_sec['min_syllables']}-{iso_sec['max_syllables']} "
                    "prosodic syllables per vertical line)"
                ),
                "tempo_feel": (
                    "Strict free-tempo Rubato (0 BPM)"
                    if bpm_val == 0
                    else f"{bpm_val} BPM steady heavy Husseiniya chest-strike pulse"
                ),
                "tor_and_maqam": tor_maqam,
                "throat_and_maddat_dynamics": (
                    "Natural laryngeal rasp, passionate 24-EDO microtonal melisma, unmarked open "
                    "diphthong Maddat before '..' (zero background crying clutter)"
                ),
                "rhythm_chants_and_sfx": (
                    "Pure solo Rubato acapella (zero percussion)"
                    if bpm_val == 0
                    else "Organic 55Hz bare-palm chest thud + 2.4kHz palm slap + Matam breath"
                ),
                "audio_engineering_3d": spatial,
                "dialect_phonetic_locks": (
                    f"{dialect_info['sound_prompt_dialect_declaration']} — pure single-dialect lock, "
                    "prosthetic 'إِCْ' clusters, open feminine 'ه' without Sukun"
                ),
                "lyrics_arabic": lines,
            }
        )

    return {
        "stage_id": stage_id,
        "execution_command": (
            f"Execute {stage_id} in Producer Chat with Instrumental mode strictly OFF. "
            "Register ONLY Arabic section_tag headers and pure vocalized lyrics_arabic lines "
            "into lyrics__register, and lock sound_description in Sound."
        ),
        "title": title,
        "global_bpm": bpm_val,
        "sound_description": sound_desc,
        "sections": sections_out,
    }


def validate_stage_orchestration_json(payload):
    """Module 53 (QC19): Validate a Per-Stage & Per-Section JSON orchestration payload."""
    if not isinstance(payload, dict):
        return {
            "is_valid_stage_json": False,
            "qc19_passed": False,
            "missing_stage_keys": list(REQUIRED_STAGE_JSON_KEYS),
            "section_errors": ["Stage payload must be a JSON object (dict)."],
        }

    missing_stage = [k for k in REQUIRED_STAGE_JSON_KEYS if k not in payload]
    section_errors = []
    sections = payload.get("sections")
    if not isinstance(sections, list) or not sections:
        section_errors.append("'sections' must be a non-empty list of section JSON objects.")
    else:
        for idx, sec in enumerate(sections):
            if not isinstance(sec, dict):
                section_errors.append(f"Section {idx} is not a JSON object.")
                continue
            missing_sec = [k for k in REQUIRED_SECTION_JSON_KEYS if k not in sec]
            if missing_sec:
                section_errors.append(f"Section {idx} missing keys: {missing_sec}")
            sec_tag = str(sec.get("section_tag", ""))
            if re.search(r"[A-Za-z]", sec_tag):
                section_errors.append(f"Section {idx} uses forbidden Latin section_tag: {sec_tag}")
            lyrics_list = sec.get("lyrics_arabic")
            if not isinstance(lyrics_list, list) or not lyrics_list:
                section_errors.append(f"Section {idx} 'lyrics_arabic' must be a non-empty list.")
                continue
            is_estehlal = _is_pure_estehlal_tag(sec_tag)
            for ln in lyrics_list:
                ln_str = str(ln).strip()
                if re.search(r"[A-Za-z]", ln_str) or "{" in ln_str or "}" in ln_str:
                    section_errors.append(
                        f"Section {idx} 'lyrics_arabic' contains forbidden Latin or JSON braces: {ln_str}"
                    )
                if is_estehlal:
                    core = ln_str[:-2].strip() if ln_str.endswith("..") else ln_str
                    if not (core.startswith("(") and core.endswith(")")):
                        section_errors.append(
                            f"Section {idx} Estehlal line missing collective '(...)' lock: {ln_str}"
                        )

    is_valid = not missing_stage and not section_errors
    return {
        "is_valid_stage_json": is_valid,
        "qc19_passed": is_valid,
        "missing_stage_keys": missing_stage,
        "section_errors": section_errors,
    }


def log_generation_session(
    log_path,
    poem_title,
    poet_name="غير محدد",
    permission_verified=False,
    dialect="iraqi",
    maqam="saba",
    bpm=60,
    candidate_chosen="A",
    notes="",
):
    """Module 24 & Empirical Ledger: Append structured JSONL generation audit record."""
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "skill_version": SKILL_VERSION,
        "poem_title": poem_title,
        "poet_name": poet_name,
        "permission_verified": bool(permission_verified),
        "living_artist_impersonation": False,
        "dialect": dialect,
        "maqam": maqam,
        "bpm": int(bpm),
        "candidate_chosen": candidate_chosen,
        "notes": notes,
    }
    parent = os.path.dirname(os.path.abspath(log_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def butter_filter(data, cutoff, sample_rate, btype="low", order=4):
    """Apply Nyquist-safe 2nd-order-section (SOS) Butterworth filter across all sample rates."""
    arr = np.asarray(data, dtype=np.float64)
    nyq = 0.5 * float(sample_rate)
    if nyq <= 25.0 or arr.size < 8:
        return arr.copy()

    if isinstance(cutoff, (list, tuple, np.ndarray)):
        low = max(12.0, min(float(cutoff[0]), nyq * 0.82))
        high = max(low + 20.0, min(float(cutoff[1]), nyq * 0.94))
        if low >= high or high >= nyq:
            return arr.copy()
        wn = [low / nyq, high / nyq]
    else:
        freq = max(12.0, min(float(cutoff), nyq * 0.92))
        if freq >= nyq:
            return arr.copy()
        wn = freq / nyq

    sos = butter(order, wn, btype=btype, output="sos")
    return sosfilt(sos, arr)


def read_wav_any_depth(input_path):
    """Read 8-bit, 16-bit, 24-bit (3-byte PCM), or 32-bit mono/stereo WAV into float64 [-1, 1]."""
    try:
        sample_rate, raw = wavfile.read(input_path)
        if raw.ndim > 1:
            channels = int(raw.shape[1])
            mono_raw = np.mean(raw.astype(np.float64), axis=1)
        else:
            channels = 1
            mono_raw = raw.astype(np.float64)

        if raw.dtype == np.uint8:
            mono = (mono_raw - 128.0) / 128.0
            bit_depth = "8-bit PCM"
        elif raw.dtype == np.int16:
            mono = mono_raw / 32768.0
            bit_depth = "16-bit PCM"
        elif raw.dtype == np.int32:
            max_abs = float(np.max(np.abs(mono_raw))) if mono_raw.size else 0.0
            if 0.0 < max_abs <= 8388608.0:
                mono = mono_raw / 8388608.0
                bit_depth = "24-bit PCM (32-bit container)"
            else:
                mono = mono_raw / 2147483648.0
                bit_depth = "32-bit PCM"
        else:
            mono = np.clip(mono_raw, -1.0, 1.0)
            bit_depth = "32-bit Float"
        return int(sample_rate), np.clip(mono, -1.0, 1.0), channels, bit_depth
    except ValueError as exc:
        with wave.open(input_path, "rb") as wav_in:
            channels = wav_in.getnchannels()
            sampwidth = wav_in.getsampwidth()
            sample_rate = wav_in.getframerate()
            n_frames = wav_in.getnframes()
            raw_bytes = wav_in.readframes(n_frames)

        if sampwidth == 3:
            byte_arr = np.frombuffer(raw_bytes, dtype=np.uint8).reshape(-1, 3)
            signed = (
                byte_arr[:, 0].astype(np.int32)
                | (byte_arr[:, 1].astype(np.int32) << 8)
                | (byte_arr[:, 2].astype(np.int32) << 16)
            )
            neg_mask = (signed & 0x800000) != 0
            signed[neg_mask] -= 1 << 24
            if channels > 1:
                signed = signed.reshape(-1, channels)
                mono = np.mean(signed.astype(np.float64), axis=1) / 8388608.0
            else:
                mono = signed.astype(np.float64) / 8388608.0
            return int(sample_rate), np.clip(mono, -1.0, 1.0), int(channels), "24-bit PCM"

        raise ValueError(f"Unsupported WAV sample width: {sampwidth} bytes") from exc


def _classify_maqam_from_pitches(detected_hz):
    """Find the closest 24-EDO Maqam in MAQAM_FREQS using minimum cents distance."""
    if detected_hz <= 0.0:
        return "saba"
    best_maqam = "saba"
    best_cents = 1e9
    for maqam_name, freqs in MAQAM_FREQS.items():
        for target_hz in freqs:
            folded = detected_hz
            while folded > target_hz * 1.45:
                folded *= 0.5
            while folded < target_hz * 0.70:
                folded *= 2.0
            cents = abs(1200.0 * np.log2(max(folded, 1e-6) / target_hz))
            if cents < best_cents:
                best_cents = cents
                best_maqam = maqam_name
    return best_maqam


def extract_reference_audio_profile(input_path):
    """Module 45: Reverse-engineer BPM, fundamental Hz, closest 24-EDO Maqam, and LUFS from WAV."""
    sample_rate, mono, channels, bit_depth = read_wav_any_depth(input_path)
    duration_sec = round(len(mono) / max(1.0, float(sample_rate)), 3)

    rms = float(np.sqrt(np.mean(mono**2)) + 1e-9)
    lufs_approx = round(float(-0.691 + 20.0 * np.log10(rms)), 2)

    spec = np.abs(np.fft.rfft(mono * np.hanning(max(1, len(mono)))))
    freqs = np.fft.rfftfreq(max(1, len(mono)), d=1.0 / sample_rate)
    vocal_mask = (freqs >= 85.0) & (freqs <= min(450.0, 0.45 * sample_rate))
    if np.any(vocal_mask):
        sub_spec = spec[vocal_mask]
        sub_freqs = freqs[vocal_mask]
        dom_hz = float(sub_freqs[int(np.argmax(sub_spec))])
    else:
        dom_hz = 146.83

    closest_maqam = _classify_maqam_from_pitches(dom_hz)

    hop = max(1, int(0.02 * sample_rate))
    n_frames = len(mono) // hop
    estimated_bpm = 60
    if n_frames >= 20:
        env = np.array(
            [np.sqrt(np.mean(mono[i * hop : (i + 1) * hop] ** 2)) for i in range(n_frames)],
            dtype=np.float64,
        )
        onset = np.maximum(0.0, np.diff(env, prepend=env[0]))
        onset -= np.mean(onset)
        if float(np.std(onset)) > 1e-6:
            acorr = np.correlate(onset, onset, mode="full")[len(onset) - 1 :]
            min_lag = max(1, int((60.0 / 145.0) / 0.02))
            max_lag = min(len(acorr) - 1, int((60.0 / 48.0) / 0.02))
            if max_lag > min_lag:
                best_lag = min_lag + int(np.argmax(acorr[min_lag : max_lag + 1]))
                estimated_bpm = int(round(60.0 / (best_lag * 0.02)))

    rec_mode = "shoor" if estimated_bpm >= 115 else ("bandari" if estimated_bpm >= 72 else "thaqeel_muwazza")
    profile_prompt = build_vocal_genre_profile(
        genre="latmiya", dialect="iraqi", maqam=closest_maqam, bpm=estimated_bpm
    )["sound_prompt"]

    return {
        "skill_version": SKILL_VERSION,
        "input_path": input_path,
        "sample_rate": sample_rate,
        "channels": channels,
        "bit_depth": bit_depth,
        "duration_sec": duration_sec,
        "estimated_bpm": estimated_bpm,
        "estimated_fundamental_hz": round(dom_hz, 2),
        "closest_maqam": closest_maqam,
        "integrated_lufs_approx": lufs_approx,
        "recommended_dsp_mode": rec_mode,
        "recommended_sound_prompt": profile_prompt,
    }


def strip_ai_percussion_from_vocal(signal, sample_rate):
    """Module 44 (--replace-ai-percussion): Remove AI sub-thumps (<120Hz) & palm-click spikes."""
    cleaned = butter_filter(signal, 120.0, sample_rate, btype="high", order=4)
    fast_win = max(1, int(0.005 * sample_rate))
    slow_win = max(fast_win + 2, int(0.060 * sample_rate))

    sq = cleaned**2
    fast_rms = np.sqrt(np.convolve(sq, np.ones(fast_win) / fast_win, mode="same") + 1e-12)
    slow_rms = np.sqrt(np.convolve(sq, np.ones(slow_win) / slow_win, mode="same") + 1e-12)

    ratio = fast_rms / (slow_rms + 1e-6)
    transient_gain = np.where(ratio > 1.85, np.clip(1.85 / np.maximum(ratio, 1e-6), 0.28, 1.0), 1.0)
    smooth_win = max(1, int(0.004 * sample_rate))
    smooth_gain = np.convolve(transient_gain, np.ones(smooth_win) / smooth_win, mode="same")
    declicked = cleaned * smooth_gain
    return butter_filter(declicked, 4500.0, sample_rate, btype="low", order=2)


def apply_noise_print_restoration(signal, sample_rate):
    """Suppress background floor in quiet frames while preserving natural consonant breath."""
    win = max(1, int(0.025 * sample_rate))
    sq = signal**2
    rms_env = np.sqrt(np.convolve(sq, np.ones(win) / win, mode="same") + 1e-12)
    noise_floor = float(np.percentile(rms_env, 10))
    threshold = max(noise_floor * 1.6, 1e-5)
    gate_gain = np.clip(rms_env / threshold, 0.35, 1.0)
    smooth = max(1, int(0.015 * sample_rate))
    gate_smooth = np.convolve(gate_gain, np.ones(smooth) / smooth, mode="same")
    return signal * gate_smooth


def apply_vocal_eq(signal, sample_rate):
    """Apply Jawhari Baritone Vocal Chain: 85Hz HPF, 320Hz mud notch, 2.5kHz harshness tame & presence."""
    out = butter_filter(signal, 85.0, sample_rate, btype="high", order=4)
    if 320.0 < 0.46 * sample_rate:
        b_mud, a_mud = iirnotch(320.0, 2.8, sample_rate)
        out = 0.72 * out + 0.28 * lfilter(b_mud, a_mud, out)
    if 2500.0 < 0.46 * sample_rate:
        b_harsh, a_harsh = iirnotch(2500.0, 3.5, sample_rate)
        out = 0.80 * out + 0.20 * lfilter(b_harsh, a_harsh, out)
    presence = butter_filter(out, [1600.0, 3800.0], sample_rate, btype="band", order=2)
    return out + 0.18 * presence


def apply_track01_dammam_eq(signal, sample_rate):
    """Shape Track 01 Dammam sub-punch (55-90Hz) and remove boxy mid mud."""
    low_body = butter_filter(signal, 160.0, sample_rate, btype="low", order=2)
    if 260.0 < 0.46 * sample_rate:
        b_box, a_box = iirnotch(260.0, 2.2, sample_rate)
        cleaned = lfilter(b_box, a_box, signal)
    else:
        cleaned = signal
    return 0.75 * cleaned + 0.35 * low_body


def compute_smart_sidechain_ducking(vocal_signal, sample_rate, duck_db=-3.0, threshold_dbfs=-28.0):
    """Compute smooth -3.0dB RMS sidechain ducking envelope when Radood exceeds -28 dBFS."""
    win = max(1, int(0.050 * sample_rate))
    rms = np.sqrt(np.convolve(vocal_signal**2, np.ones(win) / win, mode="same") + 1e-12)
    thresh_lin = 10.0 ** (threshold_dbfs / 20.0)
    min_gain = 10.0 ** (duck_db / 20.0)
    active = np.clip((rms - thresh_lin) / max(thresh_lin * 2.0, 1e-6), 0.0, 1.0)
    raw_gain = 1.0 - active * (1.0 - min_gain)
    rel_win = max(1, int(0.080 * sample_rate))
    return np.convolve(raw_gain, np.ones(rel_win) / rel_win, mode="same")


def compute_tempo_synced_delay_ms(bpm, mode="latm"):
    """Compute BPM-locked analog tape delay time in milliseconds (180-450ms)."""
    if bpm <= 0 or mode in ("mawal", "nai"):
        return 420.0
    beat_ms = 60000.0 / float(bpm)
    delay_ms = beat_ms * 0.25 if beat_ms > 700.0 else beat_ms * 0.5
    return float(np.clip(delay_ms, 180.0, 440.0))


def apply_dynacord_echo(signal, sample_rate, delay_ms=285.0, feedback=0.26, wet=0.20):
    """Apply warm band-limited Husseiniya Dynacord analog tape echo."""
    delay_samples = max(1, int((delay_ms / 1000.0) * sample_rate))
    echo_buf = np.zeros(len(signal) + delay_samples * 3, dtype=np.float64)
    echo_buf[: len(signal)] = signal
    for tap in range(1, 4):
        gain = (feedback**tap) * wet
        start = tap * delay_samples
        echo_buf[start : start + len(signal)] += gain * signal
    trimmed = echo_buf[: len(signal)]
    warm_echo = butter_filter(trimmed - signal, [180.0, 2800.0], sample_rate, btype="band", order=2)
    return signal + warm_echo


def apply_husseiniya_reverb(signal, sample_rate, rt60_sec=2.8, pre_delay_ms=24.0, wet=0.22):
    """Apply synthetic Husseiniya hall impulse response via FFT convolution."""
    ir_len = max(16, int(min(rt60_sec, 3.8) * sample_rate))
    rng = np.random.default_rng(4850)
    t_ir = np.linspace(0.0, rt60_sec, ir_len, endpoint=False)
    decay = np.exp(-6.91 * t_ir / max(rt60_sec, 0.2))
    ir = rng.normal(0.0, 1.0, ir_len) * decay
    ir = butter_filter(ir, [160.0, 4200.0], sample_rate, btype="band", order=2)
    norm = float(np.sqrt(np.sum(ir**2)) + 1e-9)
    ir /= norm

    pre_samples = max(0, int((pre_delay_ms / 1000.0) * sample_rate))
    convolved = fftconvolve(signal, ir)[: len(signal)]
    if pre_samples > 0 and pre_samples < len(convolved):
        convolved = np.concatenate((np.zeros(pre_samples, dtype=np.float64), convolved[:-pre_samples]))
    return (1.0 - wet) * signal + wet * convolved


def detect_vocal_onset_offset_samples(vocal_signal, sample_rate):
    """Detect first active Radood vocal onset so percussion locks onto phrase entry."""
    threshold = max(0.04 * float(np.max(np.abs(vocal_signal)) + 1e-9), 1e-4)
    idx = np.where(np.abs(vocal_signal) >= threshold)[0]
    if idx.size == 0:
        return 0
    return min(int(idx[0]), int(0.5 * sample_rate))


def _load_optional_sample_hit(samples_dir, name, sample_rate):
    """Load an optional external one-shot WAV from samples_dir if present."""
    if not samples_dir:
        return None
    candidate = os.path.join(samples_dir, f"{name}.wav")
    if not os.path.isfile(candidate):
        return None
    sr_hit, mono_hit, _, _ = read_wav_any_depth(candidate)
    if sr_hit == sample_rate or mono_hit.size < 4:
        return mono_hit
    new_len = max(4, int(len(mono_hit) * (float(sample_rate) / float(sr_hit))))
    x_old = np.linspace(0.0, 1.0, len(mono_hit))
    x_new = np.linspace(0.0, 1.0, new_len)
    return np.interp(x_new, x_old, mono_hit)


def synthesize_percussion_hit(sample_rate, kind="latm", variant_idx=0, samples_dir=None):
    """Synthesize organic round-robin Husseini percussion hits (Latm, Dammam, Zanjeel, Tasa, Breath)."""
    ext = _load_optional_sample_hit(samples_dir, kind, sample_rate)
    if ext is not None:
        vel = 0.94 + 0.06 * np.cos(float(variant_idx) * 1.3)
        return ext * vel

    rng = np.random.default_rng(4850 + int(variant_idx) * 19)
    pitch_jit = 1.0 + 0.015 * np.sin(float(variant_idx) * 1.7)
    vel_jit = 0.94 + 0.06 * np.cos(float(variant_idx) * 1.3)
    dur = 0.24
    num_samples = max(4, int(dur * sample_rate))
    t_vec = np.linspace(0.0, dur, num_samples, endpoint=False) * pitch_jit

    if kind == "dammam":
        freq_env = 88.0 * np.exp(-14.0 * t_vec) + 48.0
        body = np.sin(2.0 * np.pi * freq_env * t_vec) * np.exp(-10.5 * t_vec)
        return vel_jit * apply_track01_dammam_eq(0.90 * body, sample_rate)

    if kind == "zanjeel":
        noise = rng.normal(0.0, 1.0, num_samples)
        metallic = butter_filter(noise, 2100.0, sample_rate, btype="high", order=2)
        return vel_jit * 0.44 * metallic * np.exp(-22.0 * t_vec)

    if kind == "tasa":
        cym = (
            0.5 * np.sin(2.0 * np.pi * 880.0 * t_vec)
            + 0.35 * np.sin(2.0 * np.pi * 1345.0 * t_vec)
            + 0.30 * rng.normal(0.0, 1.0, num_samples)
        )
        ring = butter_filter(cym, 1600.0, sample_rate, btype="high", order=2)
        return vel_jit * 0.36 * ring * np.exp(-14.0 * t_vec)

    if kind == "breath":
        air = rng.normal(0.0, 1.0, num_samples)
        shaped_air = butter_filter(air, [240.0, 1400.0], sample_rate, btype="band", order=2)
        env = np.sin(np.pi * np.linspace(0.0, 1.0, num_samples)) ** 1.5
        return vel_jit * 0.16 * shaped_air * env

    if kind in ("heavy_clip", "thaqeel_muwazza", "bahrani_muthakkal"):
        chest_low = np.sin(2.0 * np.pi * 54.0 * t_vec) * np.exp(-12.0 * t_vec)
        sub_hum = (
            np.sin(2.0 * np.pi * 44.0 * t_vec)
            * (1.0 - np.exp(-36.0 * t_vec))
            * np.exp(-7.5 * t_vec)
        )
        palm_snap = butter_filter(
            rng.normal(0.0, 1.0, num_samples) * np.exp(-46.0 * t_vec),
            [1500.0, 3200.0],
            sample_rate,
            btype="band",
            order=2,
        )
        return vel_jit * (0.68 * chest_low + 0.42 * sub_hum + 0.34 * palm_snap)

    if kind in ("bahrani_fast", "bahrani_haidari", "bahrani_waqfa"):
        chest_core = np.sin(2.0 * np.pi * 60.0 * t_vec) * np.exp(-17.0 * t_vec)
        sharp_slap = butter_filter(
            rng.normal(0.0, 1.0, num_samples) * np.exp(-34.0 * t_vec),
            [1400.0, 3500.0],
            sample_rate,
            btype="band",
            order=2,
        )
        return vel_jit * (0.70 * chest_core + 0.48 * sharp_slap)

    if kind in ("studio_arranged", "bahrani_thulathi", "bahrani_rubai"):
        sub_kick = np.sin(2.0 * np.pi * 55.0 * t_vec) * np.exp(-15.0 * t_vec)
        palm_click = butter_filter(
            rng.normal(0.0, 1.0, num_samples) * np.exp(-48.0 * t_vec),
            [1600.0, 3100.0],
            sample_rate,
            btype="band",
            order=2,
        )
        return vel_jit * (0.68 * sub_kick + 0.32 * palm_click)

    sub_thud = np.sin(2.0 * np.pi * 55.0 * t_vec) * np.exp(-16.0 * t_vec)
    skin_slap = butter_filter(
        rng.normal(0.0, 1.0, num_samples) * np.exp(-40.0 * t_vec),
        [220.0, 1800.0],
        sample_rate,
        btype="band",
        order=2,
    )
    return vel_jit * (0.78 * sub_thud + 0.26 * skin_slap)


def _add_hit_at(bed, hit, pos, gain=1.0):
    """Mix a one-shot percussion array safely into bed at sample index pos."""
    if pos < 0 or pos >= len(bed):
        return
    end = min(len(bed), pos + len(hit))
    bed[pos:end] += gain * hit[: end - pos]


def build_rhythm_bed(
    num_samples, sample_rate, mode="latm", bpm=60.0, offset_samples=0, swing=0.0, samples_dir=None
):
    """Build 16-mode round-robin Husseiniya percussion bed (Latm, Bahrani Atwar, Zanjeel, Shoor, Bandari)."""
    bed = np.zeros(num_samples, dtype=np.float64)
    if bpm <= 0.0 or mode in ("mawal", "nai") or num_samples <= 0:
        return bed

    beat_samples = max(1, int((60.0 / float(bpm)) * sample_rate))
    rr_count = 4
    hit_kind = mode if mode not in ("zanjeel_iraqi", "zanjeel_bahrani", "bandari", "shoor") else "latm"
    main_bank = [
        synthesize_percussion_hit(sample_rate, kind=hit_kind, variant_idx=i, samples_dir=samples_dir)
        for i in range(rr_count)
    ]
    dammam_bank = [
        synthesize_percussion_hit(sample_rate, kind="dammam", variant_idx=i, samples_dir=samples_dir)
        for i in range(rr_count)
    ]
    zanjeel_bank = [
        synthesize_percussion_hit(sample_rate, kind="zanjeel", variant_idx=i, samples_dir=samples_dir)
        for i in range(rr_count)
    ]
    tasa_bank = [
        synthesize_percussion_hit(sample_rate, kind="tasa", variant_idx=i, samples_dir=samples_dir)
        for i in range(rr_count)
    ]
    breath_bank = [
        synthesize_percussion_hit(sample_rate, kind="breath", variant_idx=i, samples_dir=samples_dir)
        for i in range(rr_count)
    ]

    swing_clamped = float(np.clip(swing, 0.0, 0.45))
    beat_idx = 0
    cursor = int(max(0, offset_samples))

    while cursor < num_samples:
        rr = beat_idx % rr_count
        if mode == "bahrani_thulathi":
            step_in_bar = beat_idx % 4
            if step_in_bar == 0:
                _add_hit_at(bed, main_bank[rr], cursor, gain=0.95)
                _add_hit_at(bed, main_bank[(rr + 1) % rr_count], cursor + int(0.42 * beat_samples), gain=0.88)
            elif step_in_bar == 1:
                _add_hit_at(bed, main_bank[rr], cursor, gain=1.12)
            elif step_in_bar == 3:
                _add_hit_at(bed, breath_bank[rr], cursor, gain=0.80)
        elif mode == "bahrani_rubai":
            accent = 1.18 if (beat_idx % 4 == 3) else 0.92
            _add_hit_at(bed, main_bank[rr], cursor, gain=accent)
        elif mode == "zanjeel_iraqi":
            _add_hit_at(bed, dammam_bank[rr], cursor, gain=0.95)
            off = cursor + int((0.5 + 0.25 * swing_clamped) * beat_samples)
            _add_hit_at(bed, zanjeel_bank[rr], off, gain=0.85)
            if beat_idx % 2 == 1:
                _add_hit_at(bed, tasa_bank[rr], cursor, gain=0.55)
        elif mode == "zanjeel_bahrani":
            _add_hit_at(bed, dammam_bank[rr], cursor, gain=0.92)
            _add_hit_at(bed, dammam_bank[(rr + 1) % rr_count], cursor + int(0.33 * beat_samples), gain=0.65)
            _add_hit_at(bed, zanjeel_bank[rr], cursor + int(0.66 * beat_samples), gain=0.82)
            if beat_idx % 4 == 3:
                _add_hit_at(bed, tasa_bank[rr], cursor, gain=0.55)
        elif mode == "bandari":
            _add_hit_at(bed, dammam_bank[rr], cursor, gain=0.88)
            sub_pos = cursor + int((0.66 + 0.12 * swing_clamped) * beat_samples)
            _add_hit_at(bed, main_bank[rr], sub_pos, gain=0.72)
        elif mode == "shoor":
            _add_hit_at(bed, main_bank[rr], cursor, gain=0.95)
            _add_hit_at(bed, main_bank[(rr + 1) % rr_count], cursor + beat_samples // 2, gain=0.78)
            _add_hit_at(bed, breath_bank[rr], cursor + beat_samples // 2, gain=0.90)
        elif mode == "studio_arranged":
            _add_hit_at(bed, main_bank[rr], cursor, gain=0.95)
            _add_hit_at(bed, main_bank[(rr + 1) % rr_count], cursor + beat_samples // 2, gain=0.35)
        else:
            _add_hit_at(bed, main_bank[rr], cursor, gain=0.96)
            _add_hit_at(bed, breath_bank[rr], cursor + beat_samples // 2, gain=0.55)

        cursor += beat_samples
        beat_idx += 1

    return bed


def _generate_rosenberg_glottal_source(num_samples, sample_rate, freq_hz):
    """Synthesize organic human vocal-fold Rosenberg glottal pulse train (zero robotic sawtooth)."""
    t_vec = np.arange(num_samples, dtype=np.float64) / float(sample_rate)
    vibrato = 1.0 + 0.003 * np.sin(2.0 * np.pi * 5.2 * t_vec)
    phase = np.mod(t_vec * freq_hz * vibrato, 1.0)
    open_q = 0.45
    close_q = 0.16
    glottal = np.zeros_like(phase)
    open_mask = phase < open_q
    close_mask = (phase >= open_q) & (phase < open_q + close_q)
    glottal[open_mask] = 0.5 * (1.0 - np.cos(np.pi * phase[open_mask] / open_q))
    glottal[close_mask] = np.cos(0.5 * np.pi * (phase[close_mask] - open_q) / close_q)
    glottal -= np.mean(glottal)
    return glottal


def _apply_ahaat_formant_resonators(source, sample_rate):
    """Shape glottal source through pharyngeal Arabic /aː/ vowel formants (F1=730, F2=1090, F3=2440Hz)."""
    f1 = butter_filter(source, [580.0, 880.0], sample_rate, btype="band", order=2)
    f2 = butter_filter(source, [940.0, 1280.0], sample_rate, btype="band", order=2)
    f3 = butter_filter(source, [2150.0, 2750.0], sample_rate, btype="band", order=2)
    return 0.58 * f1 + 0.30 * f2 + 0.12 * f3


def synthesize_ahaat_drone(num_samples, sample_rate, maqam="saba"):
    """Module 44: Synthesize 24-EDO human pharyngeal Ahaat pad ([-4, 0, +4] cents ensemble)."""
    if num_samples <= 0:
        return np.zeros(0, dtype=np.float64)
    freqs = MAQAM_FREQS.get(maqam.lower(), MAQAM_FREQS["saba"])
    tonic_hz = freqs[0]
    fourth_hz = freqs[2]
    detune_cents = (-4.0, 0.0, 4.0)

    ensemble = np.zeros(num_samples, dtype=np.float64)
    for cents in detune_cents:
        ratio = 2.0 ** (cents / 1200.0)
        v_tonic = _generate_rosenberg_glottal_source(num_samples, sample_rate, tonic_hz * ratio)
        v_fourth = _generate_rosenberg_glottal_source(num_samples, sample_rate, fourth_hz * ratio)
        ensemble += 0.68 * v_tonic + 0.32 * v_fourth

    shaped = _apply_ahaat_formant_resonators(ensemble / float(len(detune_cents)), sample_rate)
    t_vec = np.arange(num_samples, dtype=np.float64) / float(sample_rate)
    breath_lfo = 0.78 + 0.22 * np.sin(2.0 * np.pi * 0.22 * t_vec)
    peak = float(np.max(np.abs(shaped)) + 1e-9)
    return 0.18 * (shaped / peak) * breath_lfo


def synthesize_vocal_synth_strings_pad(num_samples, sample_rate, maqam="saba"):
    """Module 44 (Tier 2): Synthesize conservative human vocal-synth pad (zero musical strings)."""
    base = synthesize_ahaat_drone(num_samples, sample_rate, maqam=maqam)
    freqs = MAQAM_FREQS.get(maqam.lower(), MAQAM_FREQS["saba"])
    upper = _generate_rosenberg_glottal_source(num_samples, sample_rate, freqs[3])
    upper_shaped = _apply_ahaat_formant_resonators(upper, sample_rate)
    peak = float(np.max(np.abs(upper_shaped)) + 1e-9)
    return base + 0.06 * (upper_shaped / peak)


def synthesize_contextual_foley(num_samples, sample_rate, foley_type="none"):
    """Synthesize subtle Karbala atmospheric Foley (desert wind, Euphrates water, distant horses)."""
    if not foley_type or foley_type == "none" or num_samples <= 0:
        return np.zeros(num_samples, dtype=np.float64)

    rng = np.random.default_rng(4851)
    t_vec = np.arange(num_samples, dtype=np.float64) / float(sample_rate)
    noise = rng.normal(0.0, 1.0, num_samples)

    if foley_type == "wind":
        band = butter_filter(noise, [180.0, 750.0], sample_rate, btype="band", order=2)
        swell = 0.55 + 0.45 * np.sin(2.0 * np.pi * 0.18 * t_vec)
        return 0.05 * band * swell

    if foley_type == "water":
        ripple = butter_filter(noise, [500.0, 2200.0], sample_rate, btype="band", order=2)
        mod = 0.65 + 0.35 * np.sin(2.0 * np.pi * 1.4 * t_vec)
        return 0.04 * ripple * mod

    if foley_type == "horses":
        bed = np.zeros(num_samples, dtype=np.float64)
        step = max(1, int(0.42 * sample_rate))
        hoof = butter_filter(
            rng.normal(0.0, 1.0, max(4, int(0.08 * sample_rate))),
            [220.0, 1100.0],
            sample_rate,
            btype="band",
            order=2,
        )
        pos = 0
        while pos < num_samples:
            _add_hit_at(bed, hoof, pos, gain=0.05)
            _add_hit_at(bed, hoof, pos + int(0.14 * sample_rate), gain=0.04)
            pos += step
        return bed

    return np.zeros(num_samples, dtype=np.float64)


def apply_dramatic_audio_drop(bed_signal, sample_rate, drop_start_sec=0.0, drop_duration_sec=3.0):
    """Module 44: Mute Latm & Ahaat for 3.0s at Kasra climax so solo Radood cry stands exposed."""
    out = bed_signal.copy()
    start = max(0, int(float(drop_start_sec) * sample_rate))
    end = min(len(out), start + int(float(drop_duration_sec) * sample_rate))
    if start >= len(out) or end <= start:
        return out

    fade = min(max(1, int(0.04 * sample_rate)), (end - start) // 2)
    out[start:end] *= 0.03
    if fade > 1:
        out[start : start + fade] = bed_signal[start : start + fade] * np.linspace(1.0, 0.03, fade)
        out[end - fade : end] = bed_signal[end - fade : end] * np.linspace(0.03, 1.0, fade)
    return out


def tape_saturate(signal, drive=1.25):
    """Apply gentle analog harmonic warmth via normalized hyperbolic tangent."""
    return np.tanh(signal * drive) / np.tanh(drive)


def apply_master_glue_compressor(stereo, ratio=1.6, threshold=0.62):
    """Apply gentle bus glue compression preserving mono compatibility."""
    mag = np.max(np.abs(stereo), axis=1)
    over = np.maximum(0.0, mag - threshold)
    compressed_mag = np.where(mag > threshold, threshold + over / ratio, mag)
    gain = np.where(mag > 1e-8, compressed_mag / np.maximum(mag, 1e-8), 1.0)
    return stereo * gain[:, np.newaxis]


def normalize_lufs_and_true_peak(stereo, sample_rate, target_lufs=-14.0, ceiling_dbtp=-1.0):
    """Normalize stereo mix to -14.0 LUFS with 4x oversampled -1.0 dBTP True Peak brickwall ceiling."""
    if stereo.size == 0:
        return stereo
    mid = np.mean(stereo, axis=1)
    k_weighted = butter_filter(mid, 100.0, sample_rate, btype="high", order=2)
    mean_sq = float(np.mean(k_weighted**2) + 1e-12)
    current_lufs = -0.691 + 10.0 * np.log10(mean_sq)
    gain_db = float(np.clip(target_lufs - current_lufs, -18.0, 24.0))
    scaled = stereo * (10.0 ** (gain_db / 20.0))

    ceiling = 10.0 ** (ceiling_dbtp / 20.0)
    n_frames = scaled.shape[0]
    if n_frames >= 4:
        x_base = np.arange(n_frames, dtype=np.float64)
        x_over = np.linspace(0.0, float(n_frames - 1), n_frames * 4)
        peak_l = float(np.max(np.abs(np.interp(x_over, x_base, scaled[:, 0]))))
        peak_r = float(np.max(np.abs(np.interp(x_over, x_base, scaled[:, 1]))))
        true_peak = max(peak_l, peak_r, float(np.max(np.abs(scaled))))
    else:
        true_peak = float(np.max(np.abs(scaled)))

    if true_peak > ceiling and true_peak > 0.0:
        scaled *= ceiling / true_peak
    return np.clip(scaled, -ceiling, ceiling)


def process_audio_file(
    input_path,
    output_path,
    mode="latm",
    bpm=60.0,
    maqam_drone="saba",
    swing=0.0,
    foley="none",
    audio_drop_sec=None,
    replace_ai_percussion=False,
    samples_dir=None,
):
    """Run complete 5-Track SOS/RMS/LUFS Husseiniya DSP vocal & percussion montage."""
    if mode not in SUPPORTED_DSP_MODES:
        raise ValueError(f"Unsupported DSP mode: {mode}")

    sample_rate, mono, _, _ = read_wav_any_depth(input_path)
    vocal_in = strip_ai_percussion_from_vocal(mono, sample_rate) if replace_ai_percussion else mono
    restored = apply_noise_print_restoration(vocal_in, sample_rate)
    eq_vocal = apply_vocal_eq(restored, sample_rate)

    delay_ms = compute_tempo_synced_delay_ms(bpm, mode=mode)
    echo_vocal = apply_dynacord_echo(eq_vocal, sample_rate, delay_ms=delay_ms)
    rt60 = 3.4 if mode in ("mawal", "nai", "thaqeel_muwazza", "bahrani_muthakkal") else 2.4
    wet_vocal = apply_husseiniya_reverb(echo_vocal, sample_rate, rt60_sec=rt60)

    onset_offset = detect_vocal_onset_offset_samples(eq_vocal, sample_rate)
    rhythm_bed = build_rhythm_bed(
        len(mono),
        sample_rate,
        mode=mode,
        bpm=bpm,
        offset_samples=onset_offset,
        swing=swing,
        samples_dir=samples_dir,
    )
    ahaat_pad = (
        synthesize_vocal_synth_strings_pad(len(mono), sample_rate, maqam=maqam_drone)
        if mode in ("studio_arranged", "heavy_clip")
        else synthesize_ahaat_drone(len(mono), sample_rate, maqam=maqam_drone)
    )
    foley_bed = synthesize_contextual_foley(len(mono), sample_rate, foley_type=foley)

    if audio_drop_sec is not None:
        rhythm_bed = apply_dramatic_audio_drop(rhythm_bed, sample_rate, drop_start_sec=audio_drop_sec)
        ahaat_pad = apply_dramatic_audio_drop(ahaat_pad, sample_rate, drop_start_sec=audio_drop_sec)

    ducking = compute_smart_sidechain_ducking(eq_vocal, sample_rate, duck_db=-3.0, threshold_dbfs=-28.0)

    haas_shift = max(1, int(0.009 * sample_rate))
    ahaat_right = np.roll(ahaat_pad, haas_shift)
    ahaat_right[:haas_shift] = ahaat_pad[:haas_shift]

    left_chan = wet_vocal + 0.82 * (rhythm_bed * ducking) + 0.72 * (ahaat_pad * ducking) + foley_bed
    right_chan = wet_vocal + 0.82 * (rhythm_bed * ducking) + 0.72 * (ahaat_right * ducking) + foley_bed

    stereo_sat = np.column_stack((tape_saturate(left_chan), tape_saturate(right_chan)))
    stereo_glued = apply_master_glue_compressor(stereo_sat)
    master = normalize_lufs_and_true_peak(
        stereo_glued, sample_rate, target_lufs=-14.0, ceiling_dbtp=-1.0
    )

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    pcm16 = np.clip(np.round(master * 32767.0), -32768, 32767).astype(np.int16)
    wavfile.write(output_path, sample_rate, pcm16)
    return {
        "output_path": output_path,
        "sample_rate": sample_rate,
        "mode": mode,
        "bpm": bpm,
        "maqam_drone": maqam_drone,
        "replace_ai_percussion": bool(replace_ai_percussion),
    }


def parse_args(argv=None):
    """Parse CLI flags for V48.5 Phonetics, Linter, Validators, Genre Firewall & 16-Mode DSP."""
    parser = argparse.ArgumentParser(
        description=f"Hussaini Production Studio DSP & Phonetics Engine ({SKILL_VERSION})"
    )
    parser.add_argument("--version", action="version", version=SKILL_VERSION)
    parser.add_argument("--input", help="Input vocal WAV file (8/16/24/32-bit mono or stereo)")
    parser.add_argument("--output", help="Output mastered 16-bit stereo WAV file (-14 LUFS)")
    parser.add_argument(
        "--mode",
        default="latm",
        choices=list(SUPPORTED_DSP_MODES),
        help="Husseiniya rhythm & production mode (16 modes)",
    )
    parser.add_argument("--bpm", type=float, default=60.0, help="Target tempo in BPM (default: 60)")
    parser.add_argument(
        "--maqam-drone",
        default="saba",
        choices=list(MAQAM_FREQS.keys()),
        help="24-EDO Maqam formant Ahaat drone",
    )
    parser.add_argument("--swing", type=float, default=0.0, help="Mawkib/Bandari swing (0.0-0.45)")
    parser.add_argument(
        "--foley",
        default="none",
        choices=["none", "wind", "water", "horses"],
        help="Contextual atmospheric Foley",
    )
    parser.add_argument(
        "--audio-drop-sec",
        type=float,
        default=None,
        help="Timestamp (sec) to trigger 3.0s solo Kasra audio drop",
    )
    parser.add_argument(
        "--replace-ai-percussion",
        action="store_true",
        help="Strip residual AI percussion (<120Hz thumps & click spikes) before adding organic Latm",
    )
    parser.add_argument("--samples-dir", default=None, help="Optional directory of real WAV one-shots")
    parser.add_argument("--compile-lyrics", default=None, help="Shape & vocalize Arabic poem text")
    parser.add_argument("--lint-poem", default=None, help="Run QC1-QC19 linter on poem text")
    parser.add_argument(
        "--enforce-estehlal",
        default=None,
        help="Wrap [المستهل] lines in '(...)' for 100% unison Raddada choir delivery",
    )
    parser.add_argument(
        "--build-stage-json",
        default=None,
        help="Build Module 53 Per-Stage & Per-Section JSON orchestration payload (QC19)",
    )
    parser.add_argument("--validate-abudhiyah", default=None, help="Validate 4-line Abudhiyah Jinas")
    parser.add_argument("--validate-zuhayri", default=None, help="Validate 7-line Zuhayri Mawal")
    parser.add_argument("--recommend-tor", default=None, help="Recommend Tor, BPM & V48.5 Sound prompt")
    parser.add_argument(
        "--stage-plan",
        default=None,
        choices=["iraqi", "bahrani", "iraqi_bahrani"],
        help="Output 4-Stage Common Jins Maqam & Atwar progression JSON",
    )
    parser.add_argument(
        "--export-constitution",
        action="store_true",
        help="Print canonical V48.5 OMNI-ARCHITECT JSON constitution",
    )
    parser.add_argument(
        "--genre",
        default=None,
        choices=["latmiya", "nasheed", "ibtihalat", "tawashih"],
        help="Generate genre acoustic profile & Sound prompt",
    )
    parser.add_argument("--extract-profile", default=None, help="Reverse-engineer reference WAV profile")
    return parser.parse_args(argv)


def main(argv=None):
    """CLI entrypoint for Hussaini Production Studio V48.5 OMNI-ARCHITECT."""
    args = parse_args(argv)

    if args.export_constitution:
        print(json.dumps(load_v48_5_constitution(), ensure_ascii=False, indent=2))
        return 0

    if args.stage_plan:
        print(json.dumps(build_four_stage_latmiya_plan(args.stage_plan), ensure_ascii=False, indent=2))
        return 0

    if args.enforce_estehlal is not None:
        print(enforce_collective_estehlal_parentheses(args.enforce_estehlal.replace("\\n", "\n")))
        return 0

    if args.build_stage_json is not None:
        stage_payload = build_stage_orchestration_json(
            args.build_stage_json, global_bpm=int(round(args.bpm))
        )
        print(json.dumps(stage_payload, ensure_ascii=False, indent=2))
        return 0

    if args.compile_lyrics is not None:
        report = detect_and_shape_dialect(args.compile_lyrics.replace("\\n", "\n"))
        report["shaped_lyrics"] = enforce_collective_estehlal_parentheses(report["shaped_lyrics"])
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.lint_poem is not None:
        print(json.dumps(lint_poem(args.lint_poem.replace("\\n", "\n")), ensure_ascii=False, indent=2))
        return 0

    if args.validate_abudhiyah is not None:
        print(json.dumps(validate_abudhiyah_jinas(args.validate_abudhiyah), ensure_ascii=False, indent=2))
        return 0

    if args.validate_zuhayri is not None:
        print(json.dumps(validate_zuhayri_mawal(args.validate_zuhayri), ensure_ascii=False, indent=2))
        return 0

    if args.recommend_tor is not None:
        print(json.dumps(recommend_tor_and_rhythm_for_poem(args.recommend_tor), ensure_ascii=False, indent=2))
        return 0

    if args.genre is not None:
        profile = build_vocal_genre_profile(
            genre=args.genre, dialect="iraqi", maqam=args.maqam_drone, bpm=int(args.bpm)
        )
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        return 0

    if args.extract_profile is not None:
        print(json.dumps(extract_reference_audio_profile(args.extract_profile), ensure_ascii=False, indent=2))
        return 0

    if args.input and args.output:
        result = process_audio_file(
            args.input,
            args.output,
            mode=args.mode,
            bpm=args.bpm,
            maqam_drone=args.maqam_drone,
            swing=args.swing,
            foley=args.foley,
            audio_drop_sec=args.audio_drop_sec,
            replace_ai_percussion=args.replace_ai_percussion,
            samples_dir=args.samples_dir,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(json.dumps(build_flowmusic_json_preconditioning(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
