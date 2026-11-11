#!/usr/bin/env python3
# pylint: disable=too-many-lines,too-many-return-statements,too-many-branches,too-many-locals,too-many-statements,too-many-arguments,too-many-positional-arguments
"""Hussaini Audio Omni-Engine DSP, 5-Track DAW & Phonetics Compiler (V50.0 OMNI-PERFECTION).

Bridges poetic/phonetic engineering with procedural DSP audio mastering:
- Single-Source Version Management via root VERSION file (V50.0 OMNI-PERFECTION)
- Unified Lyrics Spec (Arabic [المُسْتَهَلّ]/[النَّزْلَة الأُولَى]/[الكَسْرَة وَالمُسْتَهَلّ] & English [Chorus]/[Verse 1])
  supporting both 12-line horizontal couplet grid and 20-line vertical 3-Part Golden Architecture
- Module 41 & 48: Zero Word-Initial Sukun (epenthetic short vowel مِتُونِي/دُمُوعْ/جُرُوحْ or clitic liaison بِدْمُوعْ)
  and Open Feminine Haa (-َه without Sukun) to eliminate G2P heavy 'HHH' & glottal stops
- Module 40: Safe Dialect-Accurate & Prosodic Tanween Compiler (preserving trailing '..' hemistich pause)
- Module 43: Word-Boundary Morphological Dialect Shaper (Bahrani, Iraqi, and Hybrid Iraqi-Bahrani)
- Modules 34 & 38: True Prosodic CV/CVV/CVC Segmenter (with Shadda gemination & Madd detection)
- Heritage Poetics & Atwar Separation: Poetic Meter (Wazn) vs. Performance Melody (Tor),
  Iraqi Abudhiyah Jinas Validator (validate_abudhiyah_jinas), Seven-Line Zuhayri Mawal Validator
  (validate_zuhayri_mawal), Interactive Ashouri Ahaat Injector (format_ashouri_interactive_ahaat),
  and Bahrani Heritage Modes (bahrani_thulathi, bahrani_rubai, bahrani_haidari, bahrani_waqfa,
  bahrani_muthakkal, and Antiphonal Dual-Choir Faujain routing)
- Reference Audio Reverse Engineering (extract_reference_audio_profile via Low-Band Autocorrelation,
  Cepstral Tonic Pitch & Maqam Estimator, Crest Factor & LUFS)
- 5-Track DAW Routing with Tempo-Synced Delay (60000 / (bpm * 2)), Rosenberg Glottal Pulse + Formant
  Resonator Ahaat Synthesis (F1=730Hz, F2=1090Hz, F3=2440Hz, +-4 cents choir detune), Stem-Aware
  Hybrid Mastering (--replace-ai-percussion), SOS Filters, -28 dBFS RMS Ducking, and -14.0 LUFS Mastering
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

from hussaini_omni_v50_extensions import (  # pylint: disable=unused-import
    MAQAM_INTERVALS_CENTS,
    POETIC_METERS_V50,
    PERFORMANCE_ATWAR_V50,
    apply_generative_morphological_rules,
    apply_microtonal_maqam_tuning,
    apply_minbar_tor_delivery_rules,
    apply_mono_safe_stereo_stage,
    apply_parallel_vocal_compression,
    apply_vocal_deesser,
    build_multi_engine_ai_prompt,
    classify_maqam_by_cents_histogram,
    compile_generative_g2p_and_ipa,
    compose_microtonal_melody_for_poem as _compose_melody_ext,
    export_guide_melody_wav,
    export_microtonal_midi,
    export_scala_microtonal_scale,
    generate_multi_maqam_readings as _multi_maqam_ext,
    infer_unvocalized_arud_pattern,
    match_poetic_meter_bitmask as _match_meter_ext,
    prosody_safe_caesura_split,
    strip_ai_percussion_stft_hpss,
    synthesize_dynamic_pitch_tracked_ahaat,
    synthesize_semantic_lyric_foley,
    synthesize_tasa_and_matam_breath,
    transcribe_vocalized_arabic_to_ipa,
    transpose_maqam_frequencies,
    write_wav_bit_depth,
)


def get_skill_version():
    """Read the canonical skill version from the root VERSION file."""
    version_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "VERSION"))
    if os.path.isfile(version_file):
        with open(version_file, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    return "V50.0 OMNI-PERFECTION"


SKILL_VERSION = get_skill_version()

MAQAM_FREQS = {
    m_key: transpose_maqam_frequencies(m_key)[:6]
    for m_key in MAQAM_INTERVALS_CENTS
}

COMMON_JINS_GRAPH = {
    "bayati": ["saba", "bayati_shuri", "kurd", "hijaz", "lami", "nahawand", "sikah", "rast"],
    "bayati_shuri": ["bayati", "hijaz", "saba", "kurd"],
    "saba": ["saba_zamzam", "bayati", "lami", "hijaz", "rast", "nahawand", "bastanikar"],
    "saba_zamzam": ["saba", "kurd", "lami", "hijaz", "bayati"],
    "hijaz": ["hijaz_kar", "bayati", "bayati_shuri", "saba", "kurd", "nahawand", "sikah", "suznak"],
    "hijaz_kar": ["hijaz", "nahawand", "suznak", "rast"],
    "lami": ["saba", "saba_zamzam", "bayati", "kurd"],
    "kurd": ["bayati", "lami", "saba_zamzam", "hijaz", "nahawand"],
    "rast": ["suznak", "saba", "bayati", "hijaz", "sikah", "ajam"],
    "suznak": ["rast", "hijaz", "nahawand", "bayati"],
    "nahawand": ["hijaz_kar", "kurd", "bayati", "saba", "hijaz", "suznak", "ajam"],
    "sikah": ["huzam", "bastanikar", "bayati", "hijaz", "rast", "saba"],
    "huzam": ["sikah", "bastanikar", "hijaz", "bayati"],
    "bastanikar": ["sikah", "huzam", "saba", "bayati"],
    "ajam": ["rast", "nahawand", "kurd"],
}

# Separation of Poetic Meter (الوزن الشعري) vs. Performance Melody (الطور الأدائي)
POETIC_METERS_CATALOG = {
    "nassari": {
        "arabic_name": "وزن النصّاري",
        "rhyme_scheme": "AAAB (الرابع يستقر على الراء أو قافية المستهل)",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": [
            "tor_nai_kashi", "tor_ashouri", "tor_rukbani", "tor_janoubi",
            "tor_zaarijawi", "tor_muthakkal", "tor_darj_karbalai",
        ],
    },
    "faizi": {
        "arabic_name": "وزن الفايزي (البحراني)",
        "rhyme_scheme": "AAAB / AABB",
        "typical_syllables_per_hemistich": (8, 11),
        "compatible_atwar": [
            "tor_faizi_bahrani", "tor_muthakkal_bahrani", "tor_tawshih_bahrani",
            "tor_waqfa_bahrani", "tor_nai_kashi",
        ],
    },
    "mujarradat": {
        "arabic_name": "وزن المجرّدات (المهداد / النعي)",
        "rhyme_scheme": "AAAA (متحد الروي صدراً وعجزاً)",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": [
            "tor_nai_mujarrad", "tor_ashouri", "tor_muthakkal", "tor_mullai",
        ],
    },
    "abudhiyah": {
        "arabic_name": "وزن الأبوذية العراقية",
        "rhyme_scheme": "AAA(Jinas) + B(-يَّه)",
        "typical_syllables_per_hemistich": (10, 12),
        "compatible_atwar": [
            "tor_lami_iraqi", "tor_huwaizawi", "tor_zaarijawi", "tor_shushtari", "tor_nayli",
        ],
    },
    "zuhayri_mawal": {
        "arabic_name": "وزن الموّال السبعوي (الزهيري)",
        "rhyme_scheme": "AAA B AAA (مع العرگ في الشطر الرابع)",
        "typical_syllables_per_hemistich": (11, 14),
        "compatible_atwar": [
            "tor_mawal_iraqi", "tor_rukbani", "tor_dashti", "tor_kashi",
        ],
    },
    "tajleeb": {
        "arabic_name": "وزن التجليبة",
        "rhyme_scheme": "AABB / ABCB",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": [
            "tor_tajleeb_furati", "tor_nai_mujarrad", "tor_ashouri", "tor_mullai",
        ],
    },
    "rukbani": {
        "arabic_name": "وزن الركباني / الحدي",
        "rhyme_scheme": "AAAB / ABCB",
        "typical_syllables_per_hemistich": (6, 8),
        "compatible_atwar": [
            "tor_rukbani", "tor_hadi", "tor_darj_karbalai", "tor_ashouri",
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
        "rhyme_scheme": "متعدد الأدوار والخانات مع لازمة موحدة",
        "typical_syllables_per_hemistich": (6, 10),
        "compatible_atwar": [
            "tor_tawshih_bahrani", "tor_bahrani_thulathi", "tor_bahrani_rubai",
            "tor_bahrani_haidari", "tor_darj_karbalai",
        ],
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
        "default_bpm": 56,
        "delivery_rule": "مدّ الكلمة الأخيرة وقطع الصوت فجأة (1.5s) لمشاركة المعزين بـ (آه .. آه)",
    },
    "tor_muthakkal_bahrani": {
        "arabic_name": "طور المثكّل البحراني / القطيفي",
        "school": "bahrani",
        "primary_maqam": "saba",
        "default_bpm": 54,
        "delivery_rule": "يبدأ وينتهي بهدوء تام مع ونّة منكسرة في آخر كل شطر لاستدرار الدمعة",
    },
    "tor_faizi_bahrani": {
        "arabic_name": "الطور الفايزي البحراني الأصيل",
        "school": "bahrani",
        "primary_maqam": "hijaz",
        "default_bpm": 62,
        "delivery_rule": "الإسراع حتى الكلمة الثالثة ثم مدّها وترجيعها وختم الشطر بالونّة قبل الحرف الأخير",
    },
    "tor_bahrani_thulathi": {
        "arabic_name": "طور العزاء البحراني الثلاثي (الموكبي)",
        "school": "bahrani",
        "primary_maqam": "bayati",
        "default_bpm": 76,
        "delivery_rule": "ضربتان متقاربتان (دم-دم) + ضربة ثالثة ثقيلة مع وقفة تنفسية وتبادل الفوجين",
    },
    "tor_bahrani_rubai": {
        "arabic_name": "طور العزاء البحراني الرباعي (الداخلية والموكب)",
        "school": "bahrani",
        "primary_maqam": "nahawand",
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
        "delivery_rule": "وتيرة متأرجحة مع مدّ وترجيع خفيفين وصعود ونزول بنبرة منهدّ الركن بدون ونّة",
    },
    "tor_huwaizawi": {
        "arabic_name": "الطور الحويزاوي",
        "school": "iraqi",
        "primary_maqam": "lami",
        "default_bpm": 0,
        "delivery_rule": "مدّات حنجرية عالية في الجواب في مقام اللامي والصبا مع كسرة فراتية",
    },
}
POETIC_METERS_CATALOG.update(POETIC_METERS_V50)
PERFORMANCE_ATWAR_CATALOG.update(PERFORMANCE_ATWAR_V50)


WORD_SEPARATION_MAP = {
    "ياحسين": "يَا حْسَيْنْ",
    "يبوفاضل": "يَا بُو فَاضِلْ",
    "يبو فاضل": "يَا بُو فَاضِلْ",
    "يبو السجاد": "يَا بُو السَّجَّادْ",
    "يزينب": "يَا زَيْنَبْ",
    "يم البنين": "يَا أُمّ البَنِينْ",
    "يحيدر": "يَا حَيْدَرْ",
    "يمحمد": "يَا مْحَمَّدْ",
    "يايمه": "يَا يُمَّه",
    "يحبيبه": "يَا حَبِيبَه",
    "يافاطم": "يَا فَاطِمْ",
    "ابأرض": "بِأَرْضِ",
    "عالباب": "عَلَى البَابْ",
    "عالرمضا": "عَلَى الرَّمْضَه",
    "عالرمضه": "عَلَى الرَّمْضَه",
    "عالتل": "عَلَى التَّلْ",
    "عالنهر": "عَلَى النَّهَرْ",
    "عالشاطي": "عَلَى الشَّاطِي",
    "بغربتي": "بِـ غُرْبِتِي",
    "بضلوعي": "بِـ ضْلُوعِي",
    "بظلوعي": "بِـ ظْلُوعِي",
    "بدموع": "بِدْمُوعْ",
    "بدموعي": "بِدْمُوعِي",
    "بجروح": "بِجْرُوحْ",
    "بجروحي": "بِجْرُوحِي",
    "لحسين": "لِـ حْسَيْنْ",
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
    "شيفيد": "شِيفِيدْ",
    "اشلون": "إِشْلُونْ",
    "والشمس": "وَ الشَّمْسْ",
    "والخيل": "وَ الخَيْلْ",
    "والمدمع": "وَ المَدْمَعْ",
    "والرأس": "وَ الرَّأْسْ",
}

COLLOQUIAL_TANWEEN_MAP = {
    "عينٍ تسيل": "عَيْنِنْ تِسِيلْ",
    "كلٍ ينادي": "كِلِّنْ يِنَادِي",
    "جرحٍ چبير": "جَرْحِنْ چِبِيرْ",
    "جرحٍ جبير": "جَرْحِنْ چِبِيرْ",
    "حالٍ يفطر": "حَالِنْ يِفَطِّرْ",
    "يومٍ عظيم": "يَوْمِنْ عَظِيمْ",
    "ضامرٍ يشكي": "ضَامِرِنْ يِشْكِي",
}

FUSHA_MIDLINE_TANWEEN_MAP = {
    "جسماً على الثرى": "جِسْمَنْ عَلَى الثَّرَى",
    "جِسْماً عَلَى الثَّرَى": "جِسْمَنْ عَلَى الثَّرَى",
    "دامٍ بلا قبورٍ": "دَامِنْ بِلَا قُبُورْ",
    "دامٍ بلا قبور": "دَامِنْ بِلَا قُبُورْ",
    "دَامٍ بِلَا قُبُورْ": "دَامِنْ بِلَا قُبُورْ",
    "عزٌ لنا": "عِزُّنْ لَنَا",
    "عِزٌّ لَنَا": "عِزُّنْ لَنَا",
    "ظامئاً": "ظَامِئَا",
    "ظَامِئاً": "ظَامِئَا",
}

BAHRANI_MARKERS = (
    "بويي", "خويي", "ونتي", "هالگفره", "امساعد", "عفارم",
    "إشحالك", "اشحالك", "لچن", "الراعبية", "الراعبيه", "يا بويي",
    "إشحالش", "اشحالش", "گلبش", "عفتش", "هالمسيه", "هالمسية",
)

IRAQI_MARKERS = (
    "بويه", "خويه", "يمه", "وليدي", "دلالي", "شلون", "إش صار",
    "شصار", "شنگول", "بلياك", "ما ظل", "چلبت", "وگفت", "هسه",
    "هالحچايه", "هالحچاية", "مشبوگه", "يبچي", "تشتاگ", "تگله",
    "متوني", "زرگ", "تراچي", "ذيچ", "البچت", "خذتني", "أگلكم",
    "الحريگ", "الطريگ", "هنيالي", "أخدمنك", "خدمنك", "يلحگ", "ينخونك",
)

FUSHA_MARKERS = (
    "إنما", "إِنَّمَا", "ليس", "لَيْسَ", "كأنما", "كَأَنَّمَا", "فهو", "فَهُوَ",
    "لعل", "لَعَلَّ", "حيثما", "الودجين", "القبلتين",
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
    "هالليله": "هَلْ لَيْلَه",
    "هالليلة": "هَلْ لَيْلَه",
    "هَاللَّيْلَه": "هَلْ لَيْلَه",
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
    "هالليله": "هَلْ لَيْلَه",
    "هالليلة": "هَلْ لَيْلَه",
    "هَاللَّيْلَه": "هَلْ لَيْلَه",
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

# Zero Word-Initial Sukun & Zero Artificial Glottal Hamza:
# Replace both artificial prosthetic 'إِCْ' and bare initial Sukun 'Cْ' with soft epenthetic short vowel
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
    "إِعْيُونَكْ": "عِيُونَكْ",
    "عْيُونَكْ": "عِيُونَكْ",
    "إِعْيُونِكْ": "عِيُونِكْ",
    "عْيُونِكْ": "عِيُونِكْ",
    "إِعْيُونِي": "عِيُونِي",
    "عْيُونِي": "عِيُونِي",
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
    "ينگال": "يِنْگَالْ",
    "ينكال": "يِنْگَالْ",
    "انياك": "إِنْيَاگْ",
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
    "اديها": "إِدَيْهَا",
    "إديها": "إِدَيْهَا",
    "ايديها": "إِدَيْهَا",
    "خرابه": "خَرَابَه",
    "خرابة": "خَرَابَه",
    "ابوها": "أَبُوهَا",
    "أبوها": "أَبُوهَا",
    "مثلي": "مِثْلِي",
    "يبچي": "يِبْچِي",
    "يبكي": "يِبْچِي",
    "عليها": "عَلَيْهَا",
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
    "حيف": "حَيْفْ",
    "تصيح": "تِصِيحْ",
    "عمه": "عَمَّه",
    "عمة": "عَمَّه",
    "وين": "وَيْنْ",
    "وينك": "وَيْنَكْ",
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
    "حيلي": "حَيْلِي",
    "حيل": "حَيْلْ",
    "ليل": "لَيْلْ",
    "خذتني": "خِذَتْنِي",
    "احتاجيت": "إِحْتَاجَيْتْ",
    "غلاتي": "غَلَاتِي",
    "چم": "چَمْ",
    "ساعه": "سَاعَه",
    "ساعة": "سَاعَه",
    "حياتي": "حَيَاتِي",
    "أگلكم": "أَگِلْكُمْ",
    "اگلكم": "أَگِلْكُمْ",
    "لوعه": "لَوْعَه",
    "لوعة": "لَوْعَه",
    "تچوي": "تِچْوِي",
    "ناديت": "نَادَيْتْ",
    "حريگ": "حَرِيگْ",
    "طريگ": "طَرِيگْ",
    "مدلل": "مُدَلَّلْ",
    "عليك": "عَلَيْكْ",
    "سكينه": "سِكِينَه",
    "سكينة": "سِكِينَه",
    "هنيالي": "هَنْيَالِي",
    "خادم": "خَادِمْ",
    "مولاي": "مَوْلَايْ",
    "سنيني": "سِنِينِي",
    "عيني": "عَيْنِي",
    "عيونك": "عِيُونَكْ",
    "شده": "شِدَّه",
    "شدة": "شِدَّه",
    "ينخونك": "يِنْخُونَكْ",
    "مضيع": "مِظَيِّعْ",
    "ندمان": "نَدْمَانْ",
    "يلحگ": "يِلْحَگْ",
}

BAHRANI_WORD_SHAPING_MAP = {
    "قلب": "گَلِبْ",
    "بقلب": "بِـ گَلِبْ",
    "وقلب": "وَ گَلِبْ",
    "قلبي": "گَلْبِي",
    "بقلبي": "بِـ گَلِبْ",
    "وقلبي": "وَ گَلِبْ",
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
    "ونتي": "وَنِّتِي",
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
    "وينك": "وَيْنِكْ",
    "عليها": "عَلَيْهَا",
    "اديها": "إِيْدَيْهَا",
    "ايديها": "إِيْدَيْهَا",
    "حيل": "حَيْلْ",
    "ليل": "لَيْلْ",
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
}

# Unified Bilingual Lyrics Section Tag Mapping (Arabic <-> English)
UNIFIED_CHORUS_TAGS = (
    "Chorus", "المستهل", "المُسْتَهَلّ", "الكسر والمستهل", "الكَسْرَة وَالمُسْتَهَلّ",
    "اللازمة", "اللَّازِمَة",
)
UNIFIED_VERSE_TAGS = (
    "Verse", "المقطع", "المَقْطَع", "النزلة", "النَّزْلَة", "الدور", "الدَّوْر",
)
UNIFIED_INTRO_OUTRO_TAGS = (
    "Intro", "Outro", "مقدمة", "المقدمة", "المُقَدِّمَة", "خاتمة", "الخاتمة", "الخَاتِمَة",
    "الوقفة", "الوَقْفَة", "الفوج الأول", "الفوج الثاني",
)


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
    """Eliminate word-initial Sukun (مْتُونِي -> مِتُونِي) & feminine Haa Sukun (غَرِيبَهْ -> غَرِيبَه)."""
    result = text
    for bad_sukun, repaired in WORD_INITIAL_SUKUN_REPAIR_MAP.items():
        result = re.sub(rf"(?<!\S){re.escape(bad_sukun)}(?!\S)", repaired, result)
    for fusha_diph, coll_mono in DIALECTAL_DIPHTHONG_AND_VOWEL_MAP.items():
        result = re.sub(rf"(?<!\S){re.escape(fusha_diph)}(?!\S)", coll_mono, result)
    # Strip any remaining Sukun directly on word-final feminine Haa/Taa Marbuta before space/pause/EOL
    result = re.sub(r"([هة])\u0652(?=\s|$|\.\.|[،\)])", r"\1", result)
    # Generic guard: if any Arabic word starts with Consonant + Sukun (e.g. بْكَرْبَلَا), convert initial Sukun to light Kasra
    # Word-initial Sukun is repaired deterministically via WORD_INITIAL_SUKUN_REPAIR_MAP while preserving clitic liaison (بِ ضْلُوعِي)
    return result


def de_cliticize_and_separate_words(text, use_tatweel=False):
    """Module 41: Separate attached vocatives, prepositions, and clitics to prevent G2P slurring."""
    result = normalize_iraqi_orthographic_gaf(text)
    for attached, separated in WORD_SEPARATION_MAP.items():
        target = _format_tatweel(separated, use_tatweel=use_tatweel)
        result = re.sub(rf"(?<!\S)و{re.escape(attached)}(?!\S)", f"وَ {target}", result)
        result = re.sub(rf"(?<!\S){re.escape(attached)}(?!\S)", target, result)
    return result


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

        # Preserve trailing pause marker '..' so Sukun is placed on the word BEFORE '..', never '..ْ'
        trailing_pause = ""
        if stripped.endswith(".."):
            trailing_pause = " .."
            stripped = stripped[:-2].rstrip()

        # Also handle mid-line hemistich pause '..'
        if ".." in stripped:
            parts = [p.strip() for p in stripped.split("..")]
            resolved_parts = []
            for part in parts:
                if not part:
                    continue
                part = re.sub(r"(?:اً|ً)$", "َا", part)
                part = re.sub(r"[ٌٍُِ]$", "ْ", part)
                part = re.sub(r"([هة])\u0652$", r"\1", part)
                if not part.endswith(("ْ", "ا", "ى", "و", "ي", "ه", "ة", ")")):
                    part = part + "ْ"
                resolved_parts.append(part)
            stripped = " .. ".join(resolved_parts)
        else:
            stripped = re.sub(r"(?:اً|ً)$", "َا", stripped)
            stripped = re.sub(r"[ٌٍُِ]$", "ْ", stripped)
            stripped = re.sub(r"([هة])\u0652$", r"\1", stripped)
            if stripped and not stripped.endswith(("ْ", "ا", "ى", "و", "ي", "ه", "ة", ")")):
                stripped = stripped + "ْ"

        lines.append(f"{stripped}{trailing_pause}".strip())
    return "\n".join(lines)


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
    """Module 43: Identify Bahrani vs. Iraqi vs. Neutral Hybrid and apply morphological shaping."""
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
        shaped = shape_words_by_boundary(shaped, BAHRANI_WORD_SHAPING_MAP, use_tatweel=use_tatweel)
        if enforce_iraqi_dhaa:
            shaped = shaped.replace("فَاضِلْ", "فَاظِلْ").replace("ضْلُوعِي", "ظْلُوعِي")
        maqam_rule = "3rd-Word Faizi Vibrato & Soft Bahrani Imala in Maqam Hijaz/Saba"
        dhad_mode = "Emphatic Iraqi Dhaa (ظ)" if enforce_iraqi_dhaa else "Standard/Bahrani Dhad (ض)"
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
    else:
        shaped = shape_words_by_boundary(shaped, HYBRID_WORD_SHAPING_MAP, use_tatweel=use_tatweel)
        if enforce_iraqi_dhaa:
            shaped = shaped.replace("فَاضِلْ", "فَاظِلْ").replace("ضْلُوعِي", "ظْلُوعِي")
        maqam_rule = (
            "Neutral Iraqi-Bahrani Fusion: Faizi 3rd-Word Vibrato + Karbalai Qarar Cadence "
            "in Maqam Saba/Bayati"
        )
        dhad_mode = "Emphatic Iraqi Dhaa (ظ)" if enforce_iraqi_dhaa else "Balanced Neutral Dhad (ض)"

    shaped = resolve_dialectal_and_prosodic_tanween(
        shaped, dialect=detected, use_tatweel=use_tatweel
    )
    shaped = repair_word_initial_sukun_and_diphthongs(shaped)
    return {
        "detected_dialect": detected,
        "bahrani_score": bahrani_hits,
        "iraqi_score": iraqi_hits,
        "dhad_articulation": dhad_mode,
        "maqam_articulation_rule": maqam_rule,
        "shaped_lyrics": shaped,
    }


def segment_arabic_prosodic_syllables(hemistich):
    """True Prosodic CV/CVV/CVC Segmenter (المُقطِّع العروضي الصوتي الحقيقي).

    Unpacks Shadda (ّ) into (Sukun 0 + Moved /), distinguishes long Madd vowels (ا، آ، ى، و، ي)
    from consonant glides, and returns the exact syllable list, count, and Haraka/Sukun pattern (/0).
    """
    cleaned = re.sub(r"[\[\]\(\)\.\،\-\_ـ]", " ", hemistich)
    words = [w for w in cleaned.split() if w]
    syllables = []
    arud_pattern = []

    short_vowels_set = {"\u064E", "\u064F", "\u0650"}  # Fatha, Damma, Kasra
    tanween_set = {"\u064B", "\u064C", "\u064D"}      # Fathatan, Dammatan, Kasratan
    sukun_char = "\u0652"
    shadda_char = "\u0651"
    madda_char = "آ"
    long_alifs = {"ا", "ى"}

    for word in words:
        # Tokenize word into (base_letter, diacritics_list)
        units = []
        for ch in word:
            if re.match(r"[\u0621-\u063A\u0641-\u064A\u067E\u0686\u06AF]", ch):
                units.append([ch, []])
            elif ch in short_vowels_set or ch in tanween_set or ch in (sukun_char, shadda_char, "\u0670"):
                if units:
                    units[-1][1].append(ch)

        if not units:
            continue

        has_any_diacritic = any(u[1] for u in units)
        if not has_any_diacritic:
            inferred_syls, inferred_pat = infer_unvocalized_arud_pattern(word)
            syllables.extend(inferred_syls)
            arud_pattern.extend(inferred_pat)
            continue

        # Expand units into elementary prosodic phonemes: 'C' (moved consonant), 'S' (sakin/madd)
        events = []
        num_u = len(units)
        for idx, (letter, diags) in enumerate(units):
            # Definite article 'ال' at word start: Alif Wasl is elided in connected prosody (همزة الوصل تسقط في الدرج)
            if idx == 0 and letter == "ا" and not diags and num_u >= 2 and units[1][0] == "ل":
                continue
            if idx == 1 and letter == "ل" and units[0][0] == "ا" and not units[0][1]:
                events.append("S")
                continue

            if letter == madda_char:
                events.append("C")
                events.append("S")
                continue

            has_shadda = shadda_char in diags
            has_sukun = sukun_char in diags
            has_short_v = any(d in short_vowels_set or d == "\u0670" for d in diags)
            has_tanween = any(d in tanween_set for d in diags)

            if has_shadda:
                # Shadda unpacks into Sakin (0) closing preceding vowel + Moved (/) if vocalized
                events.append("S")
                if has_short_v or has_tanween or (idx + 1 < num_u and units[idx + 1][0] in ("ا", "ى", "و", "ي")):
                    events.append("C")
                if has_tanween:
                    events.append("S")
                continue

            if has_tanween:
                events.append("C")
                events.append("S")
                continue

            if has_sukun:
                events.append("S")
                continue

            if has_short_v:
                events.append("C")
                continue

            # Unmarked letter inside a vocalized word:
            # Check if it is a Madd vowel (ا، ى، و، ي) preceded by a moved letter
            if letter in long_alifs:
                events.append("S")
            elif letter in ("و", "ي") and events and events[-1] == "C":
                # Madd Waw or Yaa (e.g. تِسِيلْ, مَشْبُوگَه, دُمُوعْ)
                events.append("S")
            elif idx == num_u - 1 and letter in ("ه", "ة"):
                # Open colloquial feminine Haa at word end closes or softens syllable without adding extra beat
                if events and events[-1] == "C":
                    events.append("S")
            elif idx == num_u - 1:
                # Word-final unmarked consonant in pause position is Sakin
                events.append("S")
            else:
                # Unmarked consonant in partially vocalized word: infer moved 'C' unless preceded by 'C' and followed by 'C'
                events.append("C")

        # Group elementary events into CV (/), CVV/CVC (/0), CVVC/CVCC (/00) syllables
        i = 0
        while i < len(events):
            if events[i] == "S":
                # Attach stray leading Sakin to previous syllable if available, else promote to light CV
                if syllables:
                    syllables[-1] += "C"
                    arud_pattern[-1] += "0"
                else:
                    syllables.append("CV")
                    arud_pattern.append("/")
                i += 1
                continue

            # events[i] == 'C'
            s_count = 0
            j = i + 1
            while j < len(events) and events[j] == "S":
                s_count += 1
                j += 1

            if s_count == 0:
                syllables.append("CV")
                arud_pattern.append("/")
            elif s_count == 1:
                syllables.append("CVC")
                arud_pattern.append("/0")
            else:
                syllables.append("CVCC")
                arud_pattern.append("/00")
            i = j

    return {
        "syllable_count": len(syllables),
        "syllables": syllables,
        "arud_pattern": "".join(arud_pattern),
    }


def count_arabic_syllables(hemistich):
    """Calculate prosodic Arabic syllable count (CV / CVV / CVC) using the true prosodic segmenter."""
    return segment_arabic_prosodic_syllables(hemistich)["syllable_count"]


def validate_stage1_iso_syllabic_lock(lines, max_syllable_spread=3):
    """Modules 34, 38 & 48: Unified Validator supporting BOTH 12-line horizontal couplet grid
    AND 20-line vertical 3-Part Golden Architecture (Estehlal 4 + Nazla 8 + Kaser+Estehlal 8)
    with full bilingual tag recognition ([Chorus]/[المُسْتَهَلّ], [Verse 1]/[النَّزْلَة الأُولَى]).
    """
    if isinstance(lines, str):
        raw_lines = lines.splitlines()
    else:
        raw_lines = list(lines)

    clean_lines = [
        ln.strip() for ln in raw_lines if ln.strip() and not ln.strip().startswith("[")
    ]

    # Detect whether input uses horizontal couplets ('..' in middle of line) or vertical hemistichs ('..' at end)
    has_mid_line_dots = any(
        ".." in ln and not ln.endswith("..") for ln in clean_lines
    )

    if has_mid_line_dots:
        # Mode A: Classic 4 / 8 / 12 horizontal couplet lines with identical 4th-line refrain
        is_valid_count = len(clean_lines) in (4, 8, 12) and len(clean_lines) % 4 == 0
        refrains = [clean_lines[idx] for idx in range(3, len(clean_lines), 4)] if is_valid_count else []
        identical_refrain = len(set(refrains)) <= 1 if refrains else False

        hemistich_counts = []
        internal_hemistich_balanced = True

        for idx, ln in enumerate(clean_lines):
            if (idx + 1) % 4 == 0:
                continue
            if ".." in ln:
                parts = [p.strip() for p in ln.split("..") if p.strip()]
                part_syllables = [count_arabic_syllables(p) for p in parts]
                hemistich_counts.extend(part_syllables)
                if (
                    len(part_syllables) >= 2
                    and (max(part_syllables) - min(part_syllables)) > max_syllable_spread
                ):
                    internal_hemistich_balanced = False
            else:
                hemistich_counts.append(count_arabic_syllables(ln))

        if hemistich_counts:
            spread = max(hemistich_counts) - min(hemistich_counts)
            iso_balanced = internal_hemistich_balanced and (spread <= max_syllable_spread + 1)
        else:
            iso_balanced = False

        return {
            "layout_format": "horizontal_couplets",
            "line_count": len(clean_lines),
            "is_valid_stanza_grid": is_valid_count,
            "identical_4th_line_refrain": identical_refrain,
            "hemistich_syllable_counts": hemistich_counts,
            "internal_hemistich_balanced": internal_hemistich_balanced,
            "iso_syllabic_balanced": iso_balanced,
            "passed": bool(is_valid_count and identical_refrain and iso_balanced),
        }

    # Mode B: Vertical hemistich architecture (e.g. Module 48 3-Part Golden Architecture: 4 + 8 + 8 = 20 lines, or 4/8/12/16/20)
    is_valid_count = len(clean_lines) >= 4 and len(clean_lines) % 4 == 0
    # Check refrain anchor: either every 4th line matches OR the final 4 lines repeat the opening 4-line Estehlal
    every_4th = [clean_lines[idx] for idx in range(3, len(clean_lines), 4)] if is_valid_count else []
    estehlal_repeats_at_end = (
        len(clean_lines) >= 8 and clean_lines[:4] == clean_lines[-4:]
    )
    last_line_matches = len(clean_lines) >= 8 and clean_lines[3] == clean_lines[-1]
    identical_refrain = bool(
        (every_4th and len(set(every_4th)) <= 1) or estehlal_repeats_at_end or last_line_matches
    )

    hemistich_counts = [
        count_arabic_syllables(ln.replace("..", "").strip()) for ln in clean_lines
    ]
    internal_hemistich_balanced = True
    for idx in range(0, len(hemistich_counts) - 1, 2):
        if abs(hemistich_counts[idx] - hemistich_counts[idx + 1]) > max_syllable_spread:
            internal_hemistich_balanced = False

    if hemistich_counts:
        spread = max(hemistich_counts) - min(hemistich_counts)
        iso_balanced = internal_hemistich_balanced and (spread <= max_syllable_spread + 1)
    else:
        iso_balanced = False

    return {
        "layout_format": "vertical_hemistichs",
        "line_count": len(clean_lines),
        "is_valid_stanza_grid": is_valid_count,
        "identical_4th_line_refrain": identical_refrain,
        "hemistich_syllable_counts": hemistich_counts,
        "internal_hemistich_balanced": internal_hemistich_balanced,
        "iso_syllabic_balanced": iso_balanced,
        "passed": bool(is_valid_count and identical_refrain and iso_balanced),
    }


def audit_legendary_latmiya_pillars(text):
    """Module 48: Audit a Latmiya poem against the 5 Pillars of Legendary Hussaini Latmiya Success.

    Accepts BOTH Arabic section tags ([المُسْتَهَلّ], [النَّزْلَة الأُولَى], [المَقْطَع الأَوَّل], [الكَسْرَة وَالمُسْتَهَلّ])
    AND English section tags ([Chorus], [Verse 1], [Intro], [Outro]).
    """
    blocks = re.split(r"(\[[^\]]+\])", text)
    current_role = ""
    mid_verse_parentheticals = []
    chorus_line_counts = []
    verse_line_counts = []

    for chunk in blocks:
        if chunk.startswith("[") and chunk.endswith("]"):
            current_role = classify_section_tag(chunk)
            continue
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            continue
        if current_role == "verse":
            verse_line_counts.append(len(lines))
            for ln in lines:
                if "(" in ln or ")" in ln:
                    mid_verse_parentheticals.append(ln)
        elif current_role == "chorus":
            chorus_line_counts.append(len(lines))

    feminine_haa_sukun_hits = re.findall(r"\S+[هة]\u0652(?!\S)", text)
    glottal_cluster_hits = re.findall(
        r"(?<!\S)(?:إِدْمُوعْ|إِمْتُونِي|إِسْنِينِي|إِجْرُوحْ|إِتْگِلَّه|إِتْسُولِفْ|إِهْمُومْ)(?!\S)",
        text,
    )
    word_initial_sukun_hits = re.findall(
        r"(?<!\S)[\u0627-\u063A\u0641-\u064A\u067E\u0686\u06AF]\u0652\S+",
        text,
    )
    has_kaser_bridge = any(c >= 8 for c in chorus_line_counts[1:]) if len(chorus_line_counts) > 1 else False
    clean_8_line_nazlas = bool(verse_line_counts) and all(v == 8 for v in verse_line_counts)

    return {
        "module": "Module_48_Legendary_Latmiya_Success_Pillars",
        "has_opening_estehlal_chorus": bool(chorus_line_counts and chorus_line_counts[0] >= 4),
        "clean_8_hemistich_nazlas": clean_8_line_nazlas,
        "zero_mid_verse_parenthetical_interruptions": len(mid_verse_parentheticals) == 0,
        "has_kaser_bridge_in_subsequent_choruses": has_kaser_bridge,
        "zero_feminine_haa_sukun": len(feminine_haa_sukun_hits) == 0,
        "zero_artificial_glottal_cluster_hamza": len(glottal_cluster_hits) == 0,
        "zero_word_initial_sukun": len(word_initial_sukun_hits) == 0,
        "mid_verse_parentheticals_found": mid_verse_parentheticals,
        "feminine_haa_sukun_found": feminine_haa_sukun_hits,
        "word_initial_sukun_found": word_initial_sukun_hits,
        "passed_all_5_pillars": bool(
            chorus_line_counts
            and clean_8_line_nazlas
            and not mid_verse_parentheticals
            and has_kaser_bridge
            and not feminine_haa_sukun_hits
            and not glottal_cluster_hits
        ),
    }


def lint_poem(text, stage=1):
    """Comprehensive pre-generation poem linter supporting both 12-line horizontal & 20-line vertical specs."""
    slurring_risks = [w for w in WORD_SEPARATION_MAP if re.search(rf"(?<!\S)و?{re.escape(w)}(?!\S)", text)]
    has_fusha = any(m in text for m in FUSHA_MARKERS)
    has_colloquial = any(m in text for m in BAHRANI_MARKERS + IRAQI_MARKERS)
    fusha_colloquial_mixed = bool(stage == 1 and has_fusha and has_colloquial)

    dialect_report = detect_and_shape_dialect(text)
    shaped_lines = dialect_report["shaped_lyrics"].splitlines()
    iso_report = validate_stage1_iso_syllabic_lock(shaped_lines)
    pillar_report = audit_legendary_latmiya_pillars(dialect_report["shaped_lyrics"])
    tatweel_count = dialect_report["shaped_lyrics"].count("ـ")

    score = 100
    if slurring_risks:
        score -= 15
    if fusha_colloquial_mixed:
        score -= 30
    if not (iso_report["is_valid_stanza_grid"] or pillar_report["passed_all_5_pillars"]):
        score -= 25
    if not (iso_report["identical_4th_line_refrain"] or pillar_report["has_kaser_bridge_in_subsequent_choruses"]):
        score -= 15
    if not iso_report["iso_syllabic_balanced"]:
        score -= 25
    score = max(0, score)

    return {
        "skill_version": SKILL_VERSION,
        "stage": stage,
        "slurring_risks_detected": slurring_risks,
        "fusha_colloquial_mixing_in_stage1": fusha_colloquial_mixed,
        "tatweel_character_count": tatweel_count,
        "dialect_report": dialect_report,
        "iso_syllabic_report": iso_report,
        "pillar_audit": pillar_report,
        "human_review_required": True,
        "estimated_stage1_success_score": score,
        "ready_for_generation": bool(score >= 80 and not fusha_colloquial_mixed),
    }


def _strip_arabic_diacritics(word):
    """Strip diacritics, punctuation, and Tatweel to compare homographic Jinas roots."""
    cleaned = re.sub(r"[\u064B-\u0652\u0670ـ\.\،\(\)\[\]]", "", word).strip()
    return cleaned.replace("ة", "ه").replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")


def validate_abudhiyah_jinas(lines):
    """Validate Iraqi Abudhiyah (الأبوذية العراقية):
    - 4 hemistichs total
    - First 3 hemistichs end with exact homophonous Jinas word (الجناس اللفظي التام)
    - 4th hemistich ends with '-يَّه / -يه / -ية' (الياء والهاء/التاء المربوطة: الغاضريه / الوطيه / المنيه)
    - Returns melodic contour rules for Maqam Lami / Saba / Huwaizawi.
    """
    if isinstance(lines, str):
        raw = [ln.strip() for ln in lines.splitlines() if ln.strip() and not ln.strip().startswith("[")]
    else:
        raw = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("[")]

    hemistichs = []
    for ln in raw:
        if ".." in ln and not ln.endswith(".."):
            hemistichs.extend([p.strip() for p in ln.split("..") if p.strip()])
        else:
            hemistichs.append(ln.replace("..", "").strip())

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
            "hemistich_1": "التأسيس في القرار والوسط مع تكرار ومدّ كلمة الجناس الأولى (تثبيت المقام)",
            "hemistich_2": "التموج النغمي والترجيع على كلمة الجناس الثانية في مقام اللامي أو الصبا",
            "hemistich_3": "التصعيد الدرامي إلى ذروة الجواب (الحويزاوي / العلواني) عند كلمة الجناس الثالثة",
            "hemistich_4_qafla": "الكسرة الفراتية الهابطة إلى القرار والختم بمدّة (-يَّه) والونّة الحزينة",
        },
    }


def validate_zuhayri_mawal(lines):
    """Validate Seven-Line Iraqi Zuhayri Mawal (الموّال السبعوي الزهيري AAA B AAA / AAA BBB A):
    - 7 hemistichs total
    - Hemistichs 1, 2, 3 share Jinas rhyme A
    - Hemistichs 4, 5, 6 share pivot rhyme B ('العرگ') OR Hemistich 4 is pivot B and 5, 6, 7 return to A
    - Hemistich 7 locks back onto Jinas rhyme A with a final Wannah cadence.
    """
    if isinstance(lines, str):
        raw = [ln.strip() for ln in lines.splitlines() if ln.strip() and not ln.strip().startswith("[")]
    else:
        raw = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("[")]

    hemistichs = [ln.replace("..", "").strip() for ln in raw if ln.strip()]
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
        "primary_jinas_word": hemistichs[0].split()[-1],
        "arq_pivot_word": hemistichs[3].split()[-1],
        "first_three_jinas_matched": first_three_match,
        "seventh_qafla_locked": seventh_matches_first,
    }


def format_ashouri_interactive_ahaat(text, ahaat_phrase="(آه .. آه)"):
    """Inject Interactive Ashouri Congregation Ahaat ('.. (آه .. آه) ..') after couplet endings.

    In Tor Al-Ashouri, the reciter elongates the final word of the couplet, drops volume, and
    cuts abruptly to leave a 1.5s gap where the congregation responds with 'آه .. آه'.
    """
    raw_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    out_lines = []
    verse_counter = 0
    for ln in raw_lines:
        if ln.startswith("["):
            out_lines.append(ln)
            verse_counter = 0
            continue
        verse_counter += 1
        base = ln if ln.endswith("..") else f"{ln} .."
        if verse_counter % 2 == 0 and ahaat_phrase not in base:
            out_lines.append(f"{base} {ahaat_phrase} ..")
        else:
            out_lines.append(base)
    return "\n".join(out_lines)


def format_bahrani_antiphonal_faujain(estehlal_lines):
    """Format Bahrani/Karbalai Antiphonal Dual-Choir (نظام الفوجين / الحلقتين المتقابلتين) routing."""
    if isinstance(estehlal_lines, str):
        clean = [ln.strip() for ln in estehlal_lines.splitlines() if ln.strip() and not ln.strip().startswith("[")]
    else:
        clean = [ln.strip() for ln in estehlal_lines if ln.strip() and not ln.strip().startswith("[")]

    out = ["[المُسْتَهَلّ]"]
    for ln in clean:
        out.append(ln if ln.endswith("..") else f"{ln} ..")
    out.append("[الفَوْج الأَوَّل]")
    for ln in clean[: max(2, len(clean) // 2)]:
        out.append(f"({ln.replace('..', '').strip()}) ..")
    out.append("[الفَوْج الثَّانِي]")
    for ln in clean[max(2, len(clean) // 2) :]:
        out.append(f"({ln.replace('..', '').strip()}) ..")
    return "\n".join(out)


def split_long_lines_for_steady_pacing(text, max_words_per_line=5):
    """Modules 44 & 49: Prosody- & syntax-safe vertical short-line caesura splitter."""
    out_lines = []
    for line in text.splitlines():
        out_lines.extend(
            prosody_safe_caesura_split(
                line, segment_arabic_prosodic_syllables, max_words_per_line=max_words_per_line
            )
        )
    return "\n".join(out_lines)


def match_poetic_meter_bitmask(text):
    """Module 49: Match poem lines against all 25 Hussaini poetic meters via binary Arud bitmasks."""
    shaped = detect_and_shape_dialect(text)["shaped_lyrics"]
    return _match_meter_ext(shaped, segment_arabic_prosodic_syllables)

def compose_microtonal_melody_for_poem(poem_text, maqam="saba", bpm=60.0, tonic_hz=None):
    """Module 50: Compose a 24-EDO microtonal melody locking prosodic Watad onto chest downbeats."""
    shaped = detect_and_shape_dialect(poem_text)["shaped_lyrics"]
    return _compose_melody_ext(
        shaped, segment_arabic_prosodic_syllables, maqam=maqam, bpm=bpm, tonic_hz=tonic_hz
    )


def generate_multi_maqam_readings(
    poem_text, maqamat=("bayati", "saba", "hijaz", "nahawand", "lami"), bpm=60.0
):
    """Module 50: Generate comparative Maqam key readings for the exact same poem."""
    shaped = detect_and_shape_dialect(poem_text)["shaped_lyrics"]
    return _multi_maqam_ext(shaped, segment_arabic_prosodic_syllables, maqamat=maqamat, bpm=bpm)


def compile_dialect_g2p_and_ipa(text, dialect=None, use_tatweel=False):
    """Module 51: Compile lyrics across 6 Hussaini dialect ecosystems with generative G2P & IPA."""
    return compile_generative_g2p_and_ipa(
        text, detect_and_shape_dialect, dialect=dialect, use_tatweel=use_tatweel
    )


def build_multi_tor_melodic_bridge(from_maqam, to_maqam, from_tor="thaqeel", to_tor="shoor"):
    """Section 15 & Module 38: Validate Common Jins and build Stage-2 Extend bridge prompt."""
    f_key = from_maqam.lower()
    t_key = to_maqam.lower()
    compatible = t_key in COMMON_JINS_GRAPH.get(f_key, []) or f_key == t_key
    return {
        "common_jins_compatible": compatible,
        "from_maqam": f_key,
        "to_maqam": t_key,
        "bridge_instruction": (
            f"Stage-2 Melodic Bridge: Transition smoothly via common tetrachord from "
            f"Maqam {f_key.capitalize()} ({from_tor}) to Maqam {t_key.capitalize()} ({to_tor}) "
            f"before resolving back to the tonic Qarar."
        ),
    }


def recommend_tor_and_rhythm_for_poem(text):
    """Module 46: Match poetic meter (Wazn), syllable count, and theme to optimal Tor, Maqam Arc, Rhythm & BPM."""
    dialect_info = detect_and_shape_dialect(text)
    clean_lines = [
        ln.strip() for ln in dialect_info["shaped_lyrics"].splitlines()
        if ln.strip() and not ln.strip().startswith("[") and not ln.strip().startswith("(")
    ]
    syllables = []
    for ln in clean_lines:
        parts = [p.strip() for p in ln.split("..") if p.strip()]
        for part in parts:
            syllables.append(count_arabic_syllables(part))
    avg_syllables = float(np.mean(syllables)) if syllables else 7.5

    bandari_markers = ("خدمنك", "أخدمنك", "خادم", "وافتخر", "تجاره الخدمه", "مشاية", "مشايه", "زوار")
    bahrani_fast_markers = ("يا بويي", "امساعد", "الراعبية", "وقفة", "شيلة", "تجنيزة")
    bahrani_muthakkal_markers = ("يبني ضعيفه", "قليبي", "مثكل", "ونتي بهالمسيه")
    bahrani_haidari_markers = ("حيدري", "بيرق", "شمر اردانك", "يا داحي الباب")
    shoor_markers = ("شور", "لبيك", "حيدر حيدر", "مجنونك")
    rukbani_markers = ("الغرب خذتني", "گلبی ذاب", "گلبي ذاب", "سياط", "طاح الحيل", "ضعن", "سبايا")

    # Identify poetic meter (الوزن الشعري) distinct from performance Tor (الطور الأدائي)
    abudhiyah_check = validate_abudhiyah_jinas(clean_lines[:4]) if len(clean_lines) >= 4 else {"is_valid_abudhiyah": False}
    zuhayri_check = validate_zuhayri_mawal(clean_lines[:7]) if len(clean_lines) >= 7 else {"is_valid_zuhayri": False}
    if abudhiyah_check.get("is_valid_abudhiyah"):
        poetic_meter = "abudhiyah"
    elif zuhayri_check.get("is_valid_zuhayri"):
        poetic_meter = "zuhayri_mawal"
    elif dialect_info["detected_dialect"] == "bahrani":
        poetic_meter = "faizi" if avg_syllables >= 8.0 else "muwashah"
    elif 6.0 <= avg_syllables <= 7.5:
        poetic_meter = "rukbani"
    else:
        poetic_meter = "nassari"

    if any(m in text for m in shoor_markers) or avg_syllables <= 5.2:
        tor_name = "Karbalai_Shoor_Climactic"
        rhythm_mode = "shoor"
        bpm = 128
        maqam_arc = "Saba_Qarar -> Hijaz_Jawab -> Saba_Chorus"
        sound_prompt = (
            "Mournful Iraqi Karbalaei Shoor Latmiya chant, 128 BPM, impassioned Maqam Saba and "
            "Bayati melodic arc, raspy grieving Baritone Radood vocal, rapid driving 55Hz bare-chest "
            "Latm thuds with rhythmic congregation Matam breath, unison male Raddada responses, "
            "Husseiniya hall acoustics, Pure Acapella No Instruments"
        )
    elif any(m in text for m in bandari_markers):
        tor_name = "Karbalai_Mawkib_Daraj_and_Mashaya"
        rhythm_mode = "bandari"
        bpm = 74
        maqam_arc = "Bayati_Wasat -> Hijaz_Jawab -> Bayati_Refrain"
        sound_prompt = (
            "Passionate Iraqi Karbalaei Hussaini Mawkib Daraj Latmiya chant, 74 BPM, dignified "
            "Maqam Bayati and Hijaz on D rising to powerful Jawab, strong resonant Karbalaei "
            "Baritone Radood vocal with proud Husseini service devotion, booming unison male "
            "Mawkib congregation Raddada responses, deep synchronized 55Hz bare-chest Latm thud "
            "and Matam breath in Husseiniya hall, Pure Acapella No Instruments"
        )
    elif any(m in text for m in bahrani_muthakkal_markers):
        tor_name = "Bahrani_Qatifi_Muthakkal_Lament"
        rhythm_mode = "bahrani_muthakkal"
        bpm = 54
        maqam_arc = "Saba_Qarar_Calm -> Bayati_Faizi_Wannah -> Saba_Whispered_Qafla"
        sound_prompt = (
            "Mournful Bahrani Qatifi Muthakkal Hussaini Latmiya lament, 54 BPM, solemn Maqam Saba "
            "and Bayati on D, authentic Bahrani dialect articulation, grieving calm Baritone Radood "
            "vocal ending each hemistich with a broken weeping Wannah sigh, deep slow 55Hz bare-chest "
            "Latm thud in Matam hall, unison male Raddada responses, Pure Acapella No Instruments"
        )
    elif any(m in text for m in bahrani_haidari_markers):
        tor_name = "Bahrani_Haidari_Mawkib_Epic"
        rhythm_mode = "bahrani_haidari"
        bpm = 96
        maqam_arc = "Hijaz_Qarar -> Rast_and_Hijaz_Jawab -> Hijaz_Waqfa"
        sound_prompt = (
            "Epic Bahrani Haidari Mawkib Hussaini Latmiya chant, 96 BPM, commanding Maqam Hijaz "
            "on D, authentic Bahrani dialect articulation, powerful resonant Baritone Radood vocal, "
            "driving synchronized Bahrani 55Hz bare-chest strikes, antiphonal dual-choir Matam "
            "congregation responses, Pure Acapella No Instruments"
        )
    elif dialect_info["detected_dialect"] == "bahrani" or any(m in text for m in bahrani_fast_markers):
        tor_name = "Bahrani_Waqfa_and_Faizi_Tawshih"
        rhythm_mode = "bahrani_fast"
        bpm = 84
        maqam_arc = "Hijaz_and_Bayati_Tawshih -> Saba_Faizi_Jawab -> Hijaz_Waqfa"
        sound_prompt = (
            "Mournful Bahrani Hussaini Waqfa Latmiya chant, 84 BPM, solemn Maqam Hijaz and Bayati "
            "with Faizi microtonal vibrato, grieving resonant Baritone Radood, strong synchronized "
            "Bahrani 55Hz bare-chest slaps, unison male Matam congregation responses, "
            "Pure Acapella No Instruments"
        )
    elif any(m in text for m in rukbani_markers) or (6.0 <= avg_syllables <= 7.3):
        tor_name = "Rukbani_Nassari_Karbalai_Lament"
        rhythm_mode = "studio_arranged"
        bpm = 64
        maqam_arc = "Lami_and_Bayati_Wasat -> Hijaz_and_Saba_Jawab -> Lami_Kasra"
        sound_prompt = (
            "Mournful Iraqi Karbalaei Hussaini Rukbani Latmiya chant, 64 BPM, solemn weeping Maqam "
            "Lami and Saba on D, authentic Karbalaei Iraqi dialect articulation, grieving solo "
            "Baritone Radood vocal with tearful Wannah and weeping voice cracks, unison male "
            "congregation Raddada responses, deep 55Hz bare-chest Latm thud in Husseiniya hall, "
            "Pure Acapella No Instruments"
        )
    else:
        tor_name = "Thaqeel_Muwazza_and_Faizi_Nai"
        rhythm_mode = "thaqeel_muwazza"
        bpm = 55
        maqam_arc = "Bayati_Qarar -> Saba_Zamzam_Jawab -> Lami_Faizi_Kasra"
        sound_prompt = (
            "Mournful Iraqi Karbalaei Hussaini Latmiya chant, 55 BPM, solemn weeping Maqam Saba "
            "Zamzam and Lami on D, authentic Karbalaei Iraqi dialect articulation, grieving solo "
            "Baritone Radood vocal with tearful Wannah and weeping voice cracks, unison male "
            "congregation Raddada responses, deep 55Hz bare-chest Latm thud in Husseiniya hall, "
            "Pure Acapella No Instruments"
        )

    return {
        "poetic_meter": poetic_meter,
        "poetic_meter_info": POETIC_METERS_CATALOG.get(poetic_meter, {}),
        "recommended_tor": tor_name,
        "rhythm_mode": rhythm_mode,
        "recommended_bpm": bpm,
        "avg_hemistich_syllables": round(avg_syllables, 2),
        "detected_dialect": dialect_info["detected_dialect"],
        "maqam_arc": maqam_arc,
        "flowmusic_sound_prompt": sound_prompt,
    }


LATMIYA_SONG_LEAKAGE_BLACKLIST = (
    "studio-arranged",
    "studio-mixed",
    "humming",
    "pads",
    "sub-bass",
    "groove",
    "bandari",
    "harmonic",
    "dammam",
    "syncopated",
    "arranged studio",
    "tenor",
)


def build_vocal_genre_profile(genre="latmiya", dialect="iraqi", maqam=None, bpm=None):
    """Module 47: Strictly separate Latmiya, Islamic Nasheed, Ibtihalat, and Tawashih profiles."""
    g_key = genre.strip().lower()
    if g_key == "nasheed":
        target_maqam = maqam or "bayati_and_rast"
        target_bpm = 88 if bpm is None else int(bpm)
        prompt = (
            f"Uplifting Islamic Nasheed vocal arrangement, {target_bpm} BPM, warm melodic Munshid "
            f"baritone lead vocal, Maqam {target_maqam}, polished multi-layered harmonic male "
            "Nasheed choir with gentle vocal humming pads, rhythmic traditional Daf frame drum "
            "pulse, clean studio acoustics, Islamic Vocal Nasheed"
        )
        rhythm_type = "daf_and_harmonic_choir_arrangement"
        chest_latm = False
    elif g_key == "ibtihalat":
        target_maqam = maqam or "saba_and_rast"
        target_bpm = 0
        prompt = (
            "Free-tempo non-metric Islamic Religious Ibtihalat and spiritual Munajat supplication, "
            f"rubato 0 BPM, reverent weeping supplicating solo Mubtahil Baritone vocal, long "
            f"breath-sustained melismatic Maqam {target_maqam} improvisation, emotional spiritual "
            "Qafla cadences, spacious Mosque hall reverb, Pure Solo Vocal No Instruments"
        )
        rhythm_type = "free_tempo_rubato_non_metric"
        chest_latm = False
    elif g_key == "tawashih":
        target_maqam = maqam or "hijaz_and_bayati"
        target_bpm = 72 if bpm is None else int(bpm)
        prompt = (
            f"Traditional Islamic Religious Tawashih and Muwashahat vocal ensemble, {target_bpm} BPM "
            f"measured classical Arabic poetic cadence, ornate Maqam {target_maqam} microtonal "
            "melismas, antiphonal call-and-response between expressive solo Munshid and unison "
            "male Tawashih Bitanah choir, traditional spiritual hall acoustics, "
            "Pure Vocal Ensemble No Instruments"
        )
        rhythm_type = "measured_classical_muwashah_antiphonal"
        chest_latm = False
    else:
        g_key = "latmiya"
        target_maqam = maqam or "saba_and_bayati"
        target_bpm = 60 if bpm is None else int(bpm)
        dialect_label = "Bahrani" if dialect == "bahrani" else "Iraqi Karbalaei"
        prompt = (
            f"Mournful {dialect_label} Hussaini Latmiya chant, {target_bpm} BPM, solemn weeping "
            f"Maqam {target_maqam} on D, authentic {dialect_label} dialect articulation, grieving "
            "solo Baritone Radood vocal with tearful Wannah and weeping voice cracks, unison male "
            "congregation Raddada responses, deep 55Hz bare-chest Latm thud in Husseiniya hall, "
            "Pure Acapella No Instruments"
        )
        rhythm_type = "55hz_bare_chest_latm_and_matam_breath"
        chest_latm = True

    leakage_found = [
        bad for bad in LATMIYA_SONG_LEAKAGE_BLACKLIST if g_key == "latmiya" and bad in prompt.lower()
    ]
    return {
        "genre": g_key,
        "dialect": dialect,
        "maqam": target_maqam,
        "bpm": target_bpm,
        "rhythm_type": rhythm_type,
        "uses_chest_latm": chest_latm,
        "song_leakage_terms_detected": leakage_found,
        "flowmusic_sound_prompt": prompt,
    }


def build_flowmusic_json_preconditioning(
    dialect="iraqi_bahrani", maqam="saba", bpm=58, reference_clip_id=None
):
    """Module 39: Build the JSON Session Pre-Conditioning payload with optional reference_clip_id."""
    payload = {
        "protocol_name": "Hussaini_Production_Studio_OS_V50_OMNI_PERFECTION",
        "skill_version": SKILL_VERSION,
        "session_mode": "Pre_Conditioning_Lock_Only_Wait_For_Step_2_Lyrics",
        "target_dialect": dialect,
        "single_stage1_maqam": maqam,
        "tempo_bpm": bpm,
        "anti_slurring_word_separation": True,
        "zero_word_initial_sukun": True,
        "open_feminine_haa_without_sukun": True,
        "preserve_iraqi_prosthetic_alif": True,
        "vertical_short_line_splitting": True,
        "bilingual_section_tags_supported": True,
        "dialectal_tanween_compiler": True,
        "mandatory_end_of_line_sukun": True,
        "strictly_non_musical_no_instruments": True,
        "extend_via_native_remix_extend": True,
        "reference_clip_id": reference_clip_id,
    }
    return payload


def log_generation_session(ledger_path, prompt, lyrics, seed=None, reference_clip_id=None, result_url=None):
    """Append a structured generation record to a JSON ledger file for empirical tracking."""
    entries = []
    if os.path.isfile(ledger_path):
        try:
            with open(ledger_path, "r", encoding="utf-8") as handle:
                entries = json.load(handle)
        except ValueError:
            entries = []
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "skill_version": SKILL_VERSION,
        "sound_prompt": prompt,
        "lyrics_line_count": len([ln for ln in lyrics.splitlines() if ln.strip()]),
        "seed": seed,
        "reference_clip_id": reference_clip_id,
        "result_url": result_url,
    }
    entries.append(entry)
    with open(ledger_path, "w", encoding="utf-8") as handle:
        json.dump(entries, handle, ensure_ascii=False, indent=2)
    return entry


def butter_filter(data, cutoff, sample_rate, btype="high", order=4):
    """Apply a numerically stable Second-Order Sections (SOS) Butterworth filter to a 1D signal."""
    nyq = 0.5 * sample_rate
    norm_cutoff = np.clip(np.asarray(cutoff, dtype=np.float64) / nyq, 1e-4, 0.999)
    sos = butter(order, norm_cutoff, btype=btype, output="sos")
    return sosfilt(sos, data)


def extract_reference_audio_profile(input_path):
    """Module 45: Reverse-engineer an audio reference WAV to extract BPM, Tonic Pitch, Maqam, Crest Factor & LUFS.

    1. Exact BPM via autocorrelation of the Low-Band Onset Envelope (40-120Hz chest Latm band).
    2. Tonic Pitch (Hz) & approximate Maqam via Autocorrelation / Cepstral Pitch Histogram.
    3. Dynamic Crest Factor (dB) and Integrated Loudness (LUFS).
    """
    sample_rate, mono = read_wav_any_depth(input_path)
    if len(mono) == 0:
        return {
            "estimated_bpm": 0.0,
            "tonic_freq_hz": 146.83,
            "estimated_maqam": "saba",
            "crest_factor_db": 0.0,
            "integrated_lufs": -70.0,
            "is_rubato": True,
        }

    # 1. Low-Band Onset Envelope (40-120Hz) for BPM Autocorrelation
    nyq = 0.5 * sample_rate
    if nyq > 140.0:
        low_band = butter_filter(mono, [40.0, 120.0], sample_rate, btype="band", order=2)
    else:
        low_band = mono

    hop = max(1, int(0.01 * sample_rate))  # 100 Hz envelope rate
    env_rate = sample_rate / float(hop)
    rectified = np.abs(low_band)
    n_frames = max(1, len(rectified) // hop)
    env = np.array([
        float(np.mean(rectified[i * hop : (i + 1) * hop])) for i in range(n_frames)
    ], dtype=np.float64)
    onset_env = np.maximum(0.0, np.diff(env, prepend=env[0]))

    min_bpm, max_bpm = 45.0, 150.0
    min_lag = max(1, int(env_rate * 60.0 / max_bpm))
    max_lag = min(len(onset_env) - 1, int(env_rate * 60.0 / min_bpm))

    if max_lag > min_lag and np.std(onset_env) > 1e-6:
        centered = onset_env - np.mean(onset_env)
        acf = np.correlate(centered, centered, mode="full")[len(centered) - 1 :]
        search_window = acf[min_lag : max_lag + 1]
        best_lag = min_lag + int(np.argmax(search_window))
        peak_strength = float(search_window[best_lag - min_lag] / (acf[0] + 1e-9))
        estimated_bpm = round(float(60.0 * env_rate / best_lag), 1) if peak_strength > 0.08 else 0.0
    else:
        estimated_bpm = 0.0

    # 2. Tonic Pitch & Maqam Approximation via Vocal Band (110-350Hz) Autocorrelation
    if nyq > 400.0:
        vocal_band = butter_filter(mono, [110.0, 350.0], sample_rate, btype="band", order=2)
    else:
        vocal_band = mono

    frame_len = min(len(vocal_band), max(256, int(0.06 * sample_rate)))
    pitches = []
    min_p_lag = max(1, int(sample_rate / 330.0))
    max_p_lag = min(frame_len - 1, int(sample_rate / 115.0))
    if max_p_lag > min_p_lag:
        for start in range(0, len(vocal_band) - frame_len + 1, frame_len):
            seg = vocal_band[start : start + frame_len]
            if np.sqrt(np.mean(seg ** 2)) < 0.02:
                continue
            seg_acf = np.correlate(seg, seg, mode="full")[len(seg) - 1 :]
            p_lag = min_p_lag + int(np.argmax(seg_acf[min_p_lag : max_p_lag + 1]))
            pitches.append(float(sample_rate / p_lag))

    tonic_hz, best_maqam, maqam_scores = classify_maqam_by_cents_histogram(
        pitches, fallback_maqam="saba"
    )

    # 3. Crest Factor & Integrated LUFS
    rms = float(np.sqrt(np.mean(mono ** 2)) + 1e-12)
    peak = float(np.max(np.abs(mono)) + 1e-12)
    crest_db = round(float(20.0 * np.log10(peak / rms)), 2)
    integrated_lufs = round(float(-0.691 + 10.0 * np.log10(max(float(np.mean(mono ** 2)), 1e-12))), 2)

    return {
        "sample_rate": sample_rate,
        "duration_sec": round(len(mono) / float(sample_rate), 2),
        "estimated_bpm": estimated_bpm,
        "is_rubato": estimated_bpm == 0.0,
        "tonic_freq_hz": tonic_hz,
        "estimated_maqam": best_maqam,
        "maqam_histogram_scores": maqam_scores,
        "crest_factor_db": crest_db,
        "integrated_lufs": integrated_lufs,
    }


def strip_ai_percussion_from_vocal(signal, sample_rate):
    """Module 52 Stem-Aware Hybrid Mastering: STFT Median HPSS preserving 4.5-12kHz vocal air."""
    if len(signal) == 0:
        return signal
    return strip_ai_percussion_stft_hpss(signal, sample_rate)


def apply_noise_print_restoration(signal, sample_rate, gate_threshold_dbfs=-42.0, reduction_db=-10.0):
    """Module 46 (Adobe Audition Step 1 — k-7KPSudf28): Smooth noise-print floor attenuation."""
    if len(signal) == 0:
        return signal
    win_len = max(1, int(0.02 * sample_rate))
    kernel = np.ones(win_len, dtype=np.float64) / win_len
    rms = np.sqrt(np.maximum(np.convolve(signal ** 2, kernel, mode="same"), 1e-16))
    rms_db = 20.0 * np.log10(rms + 1e-12)
    open_ratio = np.clip((rms_db - gate_threshold_dbfs) / 8.0, 0.0, 1.0)
    floor_gain = float(10.0 ** (reduction_db / 20.0))
    gain_env = floor_gain + open_ratio * (1.0 - floor_gain)
    return signal * gain_env


def apply_vocal_eq(signal, sample_rate):
    """Apply SOS HPF @ 85Hz, boxy notch @ 650Hz, and +4.5dB Jawhari presence @ 2.5kHz."""
    cleaned = butter_filter(signal, 85.0, sample_rate, btype="high", order=4)
    nyq = 0.5 * sample_rate
    if nyq > 700.0:
        b_notch, a_notch = iirnotch(650.0 / nyq, 4.0)
        cleaned = lfilter(b_notch, a_notch, cleaned)
    if nyq > 3800.0:
        presence_band = butter_filter(
            cleaned, [1800.0, 3400.0], sample_rate, btype="band", order=2
        )
        cleaned = cleaned + 0.68 * presence_band
    return cleaned


def apply_track01_dammam_eq(dammam_signal, sample_rate):
    """Track_01_Dammam_Sub_Bass: SOS HPF @ 35Hz, +2dB boost @ 90Hz, and 160Hz vocal-clear notch."""
    filtered = butter_filter(dammam_signal, 35.0, sample_rate, btype="high", order=2)
    nyq = 0.5 * sample_rate
    if nyq > 120.0:
        sub_punch = butter_filter(filtered, [75.0, 105.0], sample_rate, btype="band", order=2)
        filtered = filtered + 0.26 * sub_punch
    if nyq > 250.0:
        b_notch, a_notch = iirnotch(160.0 / nyq, 3.5)
        filtered = lfilter(b_notch, a_notch, filtered)
    return filtered


def compute_smart_sidechain_ducking(
    vocal_signal, sample_rate, duck_db=-3.0, threshold_dbfs=-28.0, attack_ms=15.0, release_ms=120.0
):
    """Compute absolute dBFS RMS sidechain ducking with attack/release smoothing (immune to single-clap spikes)."""
    nyq = 0.5 * sample_rate
    high_cut = min(3200.0, 0.45 * sample_rate)
    if nyq > 400.0 and high_cut > 150.0:
        larynx_band = butter_filter(vocal_signal, [140.0, high_cut], sample_rate, btype="band", order=2)
    else:
        larynx_band = vocal_signal

    win_len = max(1, int(0.025 * sample_rate))
    power_kernel = np.ones(win_len, dtype=np.float64) / win_len
    rms = np.sqrt(np.maximum(np.convolve(larynx_band ** 2, power_kernel, mode="same"), 1e-16))
    rms_dbfs = 20.0 * np.log10(rms + 1e-12)

    over_db = np.clip((rms_dbfs - threshold_dbfs) / 12.0, 0.0, 1.0)

    atk_samples = max(1, int((attack_ms / 1000.0) * sample_rate))
    rel_samples = max(1, int((release_ms / 1000.0) * sample_rate))
    smooth_win = max(1, (atk_samples + rel_samples) // 2)
    smooth_kernel = np.exp(-np.linspace(0.0, 3.0, smooth_win))
    smooth_kernel /= np.sum(smooth_kernel)
    activity = np.clip(fftconvolve(over_db, smooth_kernel, mode="same")[: len(vocal_signal)], 0.0, 1.0)

    target_linear = float(10.0 ** (duck_db / 20.0))
    ducking_gain = 1.0 - activity * (1.0 - target_linear)
    return ducking_gain


def compute_tempo_synced_delay_ms(bpm, is_rubato=False):
    """Module 46: Compute mathematically tempo-synced delay time: 60000 / (bpm * 2) clipped to [210, 460] ms."""
    if is_rubato or bpm <= 0.0:
        return 450.0
    return float(np.clip(60000.0 / (float(bpm) * 2.0), 210.0, 460.0))


def apply_dynacord_echo(signal, sample_rate, delay_ms=285.0, feedback=0.32, mix=0.22):
    """Fast vectorized multi-tap analog tape slapback echo."""
    delay_samples = max(1, int((delay_ms / 1000.0) * sample_rate))
    echo_bus = np.zeros_like(signal, dtype=np.float64)
    n_samples = len(signal)

    for tap in range(1, 8):
        shift = tap * delay_samples
        if shift >= n_samples:
            break
        gain = (feedback ** (tap - 1)) * (1.0 - 0.15 * (tap - 1))
        if gain <= 1e-4:
            break
        echo_bus[shift:] += gain * signal[: n_samples - shift]

    if 0.5 * sample_rate > 4000.0:
        echo_bus = butter_filter(echo_bus, 3800.0, sample_rate, btype="low", order=2)
    return signal + mix * echo_bus


def apply_husseiniya_reverb(signal, sample_rate, rt60=3.2, wet_mix=0.26, pre_delay_ms=40.0, ir_path=None):
    """Convolve signal with a real Husseiniya IR (if provided) or procedural hall IR with 40ms pre-delay."""
    if ir_path and os.path.isfile(ir_path):
        _, ir_raw = wavfile.read(ir_path)
        ir = ir_raw.astype(np.float64)
        if ir.ndim > 1:
            ir = np.mean(ir, axis=1)
        ir_norm = np.linalg.norm(ir)
        if ir_norm > 1e-8:
            ir = ir / ir_norm
    else:
        rng = np.random.default_rng(seed=42)
        ir_len = max(1, int(rt60 * sample_rate))
        pre_delay = max(1, int((pre_delay_ms / 1000.0) * sample_rate))
        t_vec = np.linspace(0.0, rt60, ir_len, endpoint=False)
        decay = np.exp(-6.91 * t_vec / rt60)
        ir = rng.normal(0.0, 1.0, ir_len) * decay
        if pre_delay < ir_len:
            ir[:pre_delay] *= 0.05
        if 0.5 * sample_rate > 3500.0:
            ir = butter_filter(ir, 3200.0, sample_rate, btype="low", order=2)
        ir = ir / (np.linalg.norm(ir) + 1e-9)

    wet = fftconvolve(signal, ir, mode="full")[: len(signal)]
    return (1.0 - wet_mix) * signal + wet_mix * wet


def detect_vocal_onset_offset_samples(vocal_signal, sample_rate, threshold_dbfs=-32.0):
    """Detect the first vocal onset sample index to align the percussion grid with the Radood."""
    frame_len = max(1, int(0.02 * sample_rate))
    thresh_lin = 10.0 ** (threshold_dbfs / 20.0)
    for start in range(0, len(vocal_signal) - frame_len, frame_len):
        frame_rms = float(np.sqrt(np.mean(vocal_signal[start : start + frame_len] ** 2)))
        if frame_rms >= thresh_lin:
            return start
    return 0


def synthesize_percussion_hit(sample_rate, kind="latm", samples_dir=None, variant_idx=0):
    """Load real acoustic percussion sample or synthesize round-robin humanized Husseiniya percussion."""
    if samples_dir and os.path.isdir(samples_dir):
        for cand_name in (f"{kind}_{variant_idx + 1}.wav", f"{kind}.wav"):
            candidate = os.path.join(samples_dir, cand_name)
            if os.path.isfile(candidate):
                _, hit_data = wavfile.read(candidate)
                hit_float = hit_data.astype(np.float64)
                if hit_float.ndim > 1:
                    hit_float = np.mean(hit_float, axis=1)
                peak = np.max(np.abs(hit_float))
                return hit_float / peak if peak > 1e-8 else hit_float

    if kind in ("tasa", "matam_breath"):
        return synthesize_tasa_and_matam_breath(sample_rate, kind=kind, seed=300 + variant_idx)

    rng = np.random.default_rng(seed=101 + int(variant_idx) * 17)
    pitch_jit = 1.0 + 0.018 * np.sin(float(variant_idx) * 1.7)
    vel_jit = 0.94 + 0.06 * np.cos(float(variant_idx) * 1.3)
    dur = 0.24
    num_samples = max(1, int(dur * sample_rate))
    t_vec = np.linspace(0.0, dur, num_samples, endpoint=False) * pitch_jit

    if kind == "dammam":
        freq_env = 90.0 * np.exp(-14.0 * t_vec) + 48.0
        body = np.sin(2.0 * np.pi * freq_env * t_vec) * np.exp(-11.0 * t_vec)
        raw_dammam = 0.9 * body
        return apply_track01_dammam_eq(raw_dammam, sample_rate)

    if kind == "zanjeel":
        noise = rng.normal(0.0, 1.0, num_samples)
        if 0.5 * sample_rate > 2500.0:
            metallic = butter_filter(noise, 2200.0, sample_rate, btype="high", order=2)
        else:
            metallic = noise
        return 0.45 * metallic * np.exp(-22.0 * t_vec)

    if kind in ("heavy_clip", "thaqeel_muwazza", "bahrani_muthakkal"):
        chest_low = np.sin(2.0 * np.pi * 54.0 * t_vec) * np.exp(-12.0 * t_vec)
        human_sub_hum = (
            np.sin(2.0 * np.pi * 44.0 * t_vec)
            * (1.0 - np.exp(-38.0 * t_vec))
            * np.exp(-7.5 * t_vec)
        )
        palm_snap = rng.normal(0.0, 1.0, num_samples) * np.exp(-48.0 * t_vec)
        if 0.5 * sample_rate > 3400.0:
            palm_snap = butter_filter(palm_snap, [1600.0, 3200.0], sample_rate, btype="band", order=2)
        elif 0.5 * sample_rate > 1200.0:
            palm_snap = butter_filter(palm_snap, [300.0, 1100.0], sample_rate, btype="band", order=2)
        return 0.68 * chest_low + 0.45 * human_sub_hum + 0.35 * palm_snap

    if kind in ("bahrani_fast", "bahrani_haidari", "bahrani_waqfa"):
        chest_core = np.sin(2.0 * np.pi * 62.0 * t_vec) * np.exp(-18.0 * t_vec)
        sharp_slap = rng.normal(0.0, 1.0, num_samples) * np.exp(-34.0 * t_vec)
        if 0.5 * sample_rate > 3800.0:
            sharp_slap = butter_filter(sharp_slap, [1400.0, 3600.0], sample_rate, btype="band", order=2)
        return 0.70 * chest_core + 0.50 * sharp_slap

    if kind in ("studio_arranged", "bahrani_thulathi", "bahrani_rubai"):
        sub_kick = np.sin(2.0 * np.pi * 56.0 * t_vec) * np.exp(-15.0 * t_vec)
        crowd_mid = rng.normal(0.0, 1.0, num_samples) * np.exp(-26.0 * t_vec)
        if 0.5 * sample_rate > 1000.0:
            crowd_mid = butter_filter(crowd_mid, [180.0, 650.0], sample_rate, btype="band", order=2)
        palm_click = rng.normal(0.0, 1.0, num_samples) * np.exp(-52.0 * t_vec)
        if 0.5 * sample_rate > 3200.0:
            palm_click = butter_filter(palm_click, [1800.0, 3100.0], sample_rate, btype="band", order=2)
        return 0.65 * sub_kick + 0.32 * crowd_mid + 0.30 * palm_click

    sub_thud = np.sin(2.0 * np.pi * 55.0 * t_vec) * np.exp(-16.0 * t_vec)
    skin_slap = rng.normal(0.0, 1.0, num_samples) * np.exp(-42.0 * t_vec)
    if 0.5 * sample_rate > 1200.0:
        skin_slap = butter_filter(skin_slap, [200.0, 1100.0], sample_rate, btype="band", order=2)
    return vel_jit * (0.80 * sub_thud + 0.25 * skin_slap)


def build_rhythm_bed(
    num_samples, sample_rate, mode="latm", bpm=60.0, offset_samples=0, swing=0.0, samples_dir=None
):
    """Module 52: Round-Robin Humanized Husseiniya Percussion (Latm, Dammam, Brass Tasa, Zanjeel, Hosa & Breath)."""
    bed = np.zeros(num_samples, dtype=np.float64)
    if bpm <= 0.0 or mode in ("mawal", "nai"):
        return bed

    beat_interval = int((60.0 / bpm) * sample_rate)
    if beat_interval <= 0:
        return bed

    rr_count = 6
    banks = {
        k: [synthesize_percussion_hit(sample_rate, k, samples_dir=samples_dir, variant_idx=v) for v in range(rr_count)]
        for k in ("latm", "heavy_clip", "dammam", "zanjeel", "bahrani_fast", "studio_arranged", "tasa", "matam_breath")
    }
    rng = np.random.default_rng(seed=505)
    max_jitter = min(beat_interval // 10, max(1, int(0.008 * sample_rate)))

    cursor = max(0, int(offset_samples))
    beat_idx = 0
    while cursor < num_samples:
        rr = beat_idx % rr_count
        primary_hit = banks["latm"][rr]
        heavy_hit = banks["heavy_clip"][rr]
        dammam_hit = banks["dammam"][rr]
        zanjeel_hit = banks["zanjeel"][rr]
        bahrani_hit = banks["bahrani_fast"][rr]
        studio_hit = banks["studio_arranged"][rr]
        tasa_hit = banks["tasa"][rr]
        breath_hit = banks["matam_breath"][rr]

        if mode in ("zanjeel_iraqi", "zanjeel_bahrani", "bandari", "dammam_tasa"):
            if beat_idx % 2 == 0:
                hit = dammam_hit
            else:
                max_h = max(len(dammam_hit), len(zanjeel_hit), len(tasa_hit))
                hit = np.zeros(max_h, dtype=np.float64)
                hit[: len(dammam_hit)] += 0.65 * dammam_hit
                hit[: len(zanjeel_hit)] += 0.50 * zanjeel_hit
                hit[: len(tasa_hit)] += 0.28 * tasa_hit
            if mode in ("zanjeel_bahrani", "dammam_tasa") and (beat_idx % 4 == 2):
                sub_pos = cursor + beat_interval // 2
                end_sub = min(num_samples, sub_pos + len(tasa_hit))
                if sub_pos < num_samples:
                    bed[sub_pos:end_sub] += 0.52 * tasa_hit[: end_sub - sub_pos]
            if mode == "bandari" and swing > 0.0:
                swing_pos = cursor + int(beat_interval * (0.5 + 0.16 * min(swing, 0.35)))
                end_sw = min(num_samples, swing_pos + len(primary_hit))
                if swing_pos < num_samples:
                    bed[swing_pos:end_sw] += 0.45 * primary_hit[: end_sw - swing_pos]
        elif mode in ("iraqi_hosa", "bahrani_hosa"):
            # Hosa 3+1 celebratory-epic tribal/mawkib stomp & double chest clap
            if beat_idx % 4 == 3:
                max_h = max(len(bahrani_hit), len(dammam_hit))
                hit = np.zeros(max_h, dtype=np.float64)
                hit[: len(bahrani_hit)] += 1.15 * bahrani_hit
                hit[: len(dammam_hit)] += 0.35 * dammam_hit
            else:
                hit = bahrani_hit
            sub_pos = cursor + (beat_interval * 2) // 3
            end_sub = min(num_samples, sub_pos + len(bahrani_hit))
            if sub_pos < num_samples:
                bed[sub_pos:end_sub] += 0.58 * bahrani_hit[: end_sub - sub_pos]
        elif mode == "bahrani_thulathi":
            step_in_cycle = beat_idx % 4
            if step_in_cycle in (0, 1):
                hit = 0.85 * studio_hit
            elif step_in_cycle == 2:
                hit = 1.15 * heavy_hit
            else:
                hit = np.zeros_like(primary_hit)
        elif mode == "bahrani_rubai":
            step_in_cycle = beat_idx % 4
            hit = (1.15 * heavy_hit) if step_in_cycle == 3 else (0.85 * studio_hit)
        elif mode in ("bahrani_fast", "bahrani_haidari", "bahrani_waqfa"):
            hit = bahrani_hit
            if beat_idx % 2 == 1:
                sub_pos = cursor + beat_interval // 2
                end_sub = min(num_samples, sub_pos + len(bahrani_hit))
                if sub_pos < num_samples:
                    bed[sub_pos:end_sub] += 0.52 * bahrani_hit[: end_sub - sub_pos]
        elif mode == "studio_arranged":
            hit = studio_hit
            if beat_idx % 4 == 3:
                sub_pos = cursor + beat_interval // 2
                end_sub = min(num_samples, sub_pos + len(primary_hit))
                if sub_pos < num_samples:
                    bed[sub_pos:end_sub] += 0.38 * primary_hit[: end_sub - sub_pos]
        elif mode in ("heavy_clip", "thaqeel_muwazza", "bahrani_muthakkal"):
            hit = heavy_hit
        else:
            hit = primary_hit

        # Add congregation Matam exhale breath on off-beats in Shoor, Latm, and Heavy Clips
        if mode in ("shoor", "latm", "heavy_clip") and beat_interval > len(breath_hit):
            br_pos = cursor + beat_interval // 2
            end_br = min(num_samples, br_pos + len(breath_hit))
            if br_pos < num_samples:
                bed[br_pos:end_br] += (0.55 if mode == "shoor" else 0.26) * breath_hit[: end_br - br_pos]

        # Subtle crowd micro-timing humanization (except beat 0 anchor)
        jitter = 0 if beat_idx == 0 else int(rng.integers(-max_jitter, max_jitter + 1))
        hit_pos = max(0, cursor + jitter)
        end_idx = min(num_samples, hit_pos + len(hit))
        if hit_pos < num_samples:
            bed[hit_pos:end_idx] += hit[: end_idx - hit_pos]
        cursor += beat_interval
        beat_idx += 1

    return bed


def _generate_rosenberg_glottal_source(t_vec, f0_hz, vibrato_hz=4.5, breath_noise_ratio=0.03, seed=77):
    """Synthesize a realistic human Rosenberg Glottal Pulse train + 3% aspiration breath noise."""
    rng = np.random.default_rng(seed=seed)
    vib = 1.0 + 0.0035 * np.sin(2.0 * np.pi * vibrato_hz * t_vec)
    phase = np.mod(np.cumsum((f0_hz * vib) / max(1.0, float(len(t_vec)) / (t_vec[-1] + 1e-9))), 1.0)
    if len(t_vec) > 1:
        dt = float(t_vec[1] - t_vec[0])
        phase = np.mod(np.cumsum(f0_hz * vib * dt), 1.0)

    # Rosenberg glottal model: opening phase Tp=0.40, closing phase Tn=0.16
    tp = 0.40
    tn = 0.16
    pulse = np.zeros_like(phase)
    open_mask = phase < tp
    close_mask = (phase >= tp) & (phase < (tp + tn))
    pulse[open_mask] = 0.5 * (1.0 - np.cos(np.pi * phase[open_mask] / tp))
    pulse[close_mask] = np.cos(0.5 * np.pi * (phase[close_mask] - tp) / tn)
    # Differentiate glottal flow to model lip radiation
    glottal_deriv = np.diff(pulse, prepend=pulse[0])
    peak = np.max(np.abs(glottal_deriv))
    if peak > 1e-8:
        glottal_deriv = glottal_deriv / peak

    breath = rng.normal(0.0, 1.0, len(t_vec))
    return (1.0 - breath_noise_ratio) * glottal_deriv + breath_noise_ratio * breath


def _apply_ahaat_formant_resonators(source_sig, sample_rate):
    """Pass glottal source through human pharyngeal vowel /a:/ ('آه') formant resonators:
    F1 ~= 730 Hz, F2 ~= 1090 Hz, F3 ~= 2440 Hz.
    """
    nyq = 0.5 * sample_rate
    out = np.zeros_like(source_sig)
    formants = (
        (730.0, 90.0, 1.00),
        (1090.0, 110.0, 0.55),
        (2440.0, 160.0, 0.25),
    )
    for center_hz, bw_hz, gain in formants:
        low_f = max(60.0, center_hz - 0.5 * bw_hz)
        high_f = min(0.45 * sample_rate, center_hz + 0.5 * bw_hz)
        if nyq > center_hz + 80.0 and high_f > low_f + 20.0:
            band = butter_filter(source_sig, [low_f, high_f], sample_rate, btype="band", order=2)
            out += gain * band
    if np.max(np.abs(out)) < 1e-8:
        return source_sig
    return out / (np.max(np.abs(out)) + 1e-9)


def synthesize_ahaat_drone(num_samples, sample_rate, maqam="saba"):
    """Track_04_Ahaat_Vocal_Choir_Pads: Synthesize human pharyngeal Ahaat ('آه') choir via
    Rosenberg Glottal Pulse + 3% Breath Noise + Formant Resonators (F1=730, F2=1090, F3=2440Hz)
    with natural choir detuning (+-4 cents) across unison/octave voices.
    """
    if num_samples <= 0:
        return np.zeros(0, dtype=np.float64)
    freqs = MAQAM_FREQS.get(maqam, MAQAM_FREQS["saba"])
    t_vec = np.arange(num_samples, dtype=np.float64) / sample_rate
    pad = np.zeros(num_samples, dtype=np.float64)
    detune_cents = (-4.0, 0.0, +4.0)

    for idx, base_freq in enumerate(freqs[:3]):
        voice_mix = np.zeros(num_samples, dtype=np.float64)
        for c_idx, cents in enumerate(detune_cents):
            detuned_freq = base_freq * (2.0 ** (cents / 1200.0))
            glottal = _generate_rosenberg_glottal_source(
                t_vec,
                detuned_freq,
                vibrato_hz=4.1 + 0.25 * idx + 0.1 * c_idx,
                breath_noise_ratio=0.03,
                seed=70 + idx * 10 + c_idx,
            )
            voice_mix += glottal / len(detune_cents)
        resonated = _apply_ahaat_formant_resonators(voice_mix, sample_rate)
        pad += (0.42 / (idx + 1)) * resonated

    nyq = 0.5 * sample_rate
    high_cut = min(12000.0, 0.45 * sample_rate)
    if nyq > 300.0 and high_cut > 200.0:
        pad = butter_filter(pad, [150.0, high_cut], sample_rate, btype="band", order=2)
    return pad * 0.14


def synthesize_vocal_synth_strings_pad(num_samples, sample_rate, maqam="saba"):
    """Module 44: Synthesize Vocal-Synth Humming Strings & Cinematic Ambient Pad using Rosenberg
    glottal pulses filtered through pharyngeal 'آه/ممم' vocal formants with +-4 cents ensemble detune.
    """
    if num_samples <= 0:
        return np.zeros(0, dtype=np.float64)
    freqs = MAQAM_FREQS.get(maqam, MAQAM_FREQS["saba"])
    t_vec = np.arange(num_samples, dtype=np.float64) / sample_rate
    pad = np.zeros(num_samples, dtype=np.float64)
    swell = 0.75 + 0.25 * np.sin(2.0 * np.pi * 0.16 * t_vec)

    for idx, freq in enumerate(freqs):
        for c_idx, cents in enumerate((-4.0, +4.0)):
            detuned = freq * (2.0 ** (cents / 1200.0))
            glottal = _generate_rosenberg_glottal_source(
                t_vec,
                detuned,
                vibrato_hz=4.3 + 0.2 * idx,
                breath_noise_ratio=0.03,
                seed=90 + idx * 5 + c_idx,
            )
            resonated = _apply_ahaat_formant_resonators(glottal, sample_rate)
            pad += (0.24 / (idx + 1)) * resonated

    pad = pad * swell
    nyq = 0.5 * sample_rate
    high_cut = min(2800.0, 0.45 * sample_rate)
    if nyq > 500.0 and high_cut > 320.0:
        pad = butter_filter(pad, [220.0, high_cut], sample_rate, btype="band", order=2)
    return pad * 0.18


def synthesize_contextual_foley(num_samples, sample_rate, foley_type="none", lyrics_text=None):
    """Modules 44 & 52: Synthesize static or semantic lyric-timed ritual Foley cues."""
    return synthesize_semantic_lyric_foley(
        num_samples, sample_rate, foley_type=foley_type, lyrics_text=lyrics_text
    )


def apply_dramatic_audio_drop(signal, sample_rate, drop_start_sec=None, drop_duration_sec=3.0):
    """Module 44: Apply a dramatic Audio Drop to background tracks so the Radood stands solo."""
    if drop_start_sec is None or drop_start_sec < 0.0 or len(signal) == 0:
        return signal

    out = signal.copy()
    start_idx = min(len(out), int(drop_start_sec * sample_rate))
    end_idx = min(len(out), int((drop_start_sec + drop_duration_sec) * sample_rate))
    if start_idx >= end_idx:
        return out

    env = np.ones(len(out), dtype=np.float64)
    env[start_idx:end_idx] = 0.05
    fade_len = min(int(0.05 * sample_rate), (end_idx - start_idx) // 2)
    if fade_len > 1:
        env[start_idx : start_idx + fade_len] = np.linspace(1.0, 0.05, fade_len)
        env[end_idx - fade_len : end_idx] = np.linspace(0.05, 1.0, fade_len)
    return out * env


def tape_saturate(signal, drive=1.35):
    """Apply smooth analog harmonic saturation."""
    return np.tanh(drive * signal) / np.tanh(drive)


def apply_master_glue_compressor(stereo_signal, ratio=1.5, threshold=0.65):
    """Track_05_Master_Mix_Bus: Apply gentle 1.5:1 glue compression across stereo bus."""
    mag = np.abs(stereo_signal)
    over = np.maximum(0.0, mag - threshold)
    compressed_mag = np.where(mag > threshold, threshold + over / ratio, mag)
    gain = np.where(mag > 1e-8, compressed_mag / (mag + 1e-12), 1.0)
    return stereo_signal * gain


def normalize_lufs_and_true_peak(stereo_signal, sample_rate, target_lufs=-14.0, ceiling_dbtp=-1.0):
    """Normalize integrated loudness to -14.0 LUFS (ITU-R BS.1770-4 K-weighted) with -1.0 dBTP limiter."""
    nyq = 0.5 * sample_rate
    weighted = stereo_signal.copy()
    if nyq > 80.0:
        for ch in range(weighted.shape[1]):
            weighted[:, ch] = butter_filter(weighted[:, ch], 38.0, sample_rate, btype="high", order=2)
    if nyq > 2000.0:
        for ch in range(weighted.shape[1]):
            shelf = butter_filter(weighted[:, ch], 1681.0, sample_rate, btype="high", order=2)
            weighted[:, ch] = weighted[:, ch] + 0.58 * shelf

    mean_square = float(np.mean(np.sum(weighted ** 2, axis=1)))
    current_lufs = -0.691 + 10.0 * np.log10(max(mean_square, 1e-12))
    gain_db = np.clip(target_lufs - current_lufs, -18.0, 18.0)
    scaled = stereo_signal * (10.0 ** (gain_db / 20.0))

    ceiling_lin = float(10.0 ** (ceiling_dbtp / 20.0))
    peak = float(np.max(np.abs(scaled)))
    if peak > ceiling_lin:
        scaled = ceiling_lin * np.tanh(scaled / ceiling_lin)
    return scaled


def read_wav_any_depth(input_path):
    """Read 8-bit, 16-bit, 24-bit, or 32-bit Mono/Stereo WAV files into a 1D float64 mono array."""
    try:
        with wave.open(input_path, "rb") as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            raw_bytes = wf.readframes(wf.getnframes())

        if sampwidth == 1:
            data = (np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
        elif sampwidth == 2:
            data = np.frombuffer(raw_bytes, dtype="<i2").astype(np.float64) / 32768.0
        elif sampwidth == 3:
            raw_u8 = np.frombuffer(raw_bytes, dtype=np.uint8).reshape(-1, 3)
            signed_24 = (
                raw_u8[:, 0].astype(np.int32)
                | (raw_u8[:, 1].astype(np.int32) << 8)
                | (raw_u8[:, 2].astype(np.int32) << 16)
            )
            neg_mask = (signed_24 & 0x800000) != 0
            signed_24[neg_mask] -= 1 << 24
            data = signed_24.astype(np.float64) / float(1 << 23)
        elif sampwidth == 4:
            data = np.frombuffer(raw_bytes, dtype="<i4").astype(np.float64) / float(1 << 31)
        else:
            raise wave.Error(f"Unsupported sample width: {sampwidth}")

        if n_channels > 1:
            data = data.reshape(-1, n_channels).mean(axis=1)
        return sample_rate, data
    except wave.Error:
        sample_rate, raw_data = wavfile.read(input_path)
        if raw_data.ndim > 1:
            mono = np.mean(raw_data.astype(np.float64), axis=1)
        else:
            mono = raw_data.astype(np.float64)
        return sample_rate, mono


def process_audio_file(
    input_path,
    output_path,
    mode="latm",
    bpm=60.0,
    maqam_drone="saba",
    offset_ms=None,
    swing=0.0,
    samples_dir=None,
    foley="none",
    audio_drop_sec=None,
    replace_ai_percussion=False,
    microtonal_tune=0.0,
    bit_depth=16,
    lyrics_text=None,
    export_stems_dir=None,
):
    """Load WAV, apply V50.0 Pitch-Tracked 5-Track Husseiniya DSP & Mono-Safe -14 LUFS Master."""
    sample_rate, mono = read_wav_any_depth(input_path)

    peak = np.max(np.abs(mono))
    if peak > 1e-8:
        mono = mono / peak

    if replace_ai_percussion:
        if bpm <= 0.0 and mode not in ("mawal", "nai"):
            ref_prof = extract_reference_audio_profile(input_path)
            bpm = ref_prof["estimated_bpm"] if ref_prof["estimated_bpm"] > 0.0 else 60.0
        mono = strip_ai_percussion_from_vocal(mono, sample_rate)

    restored_vocal = apply_noise_print_restoration(mono, sample_rate)
    tuned_vocal = apply_microtonal_maqam_tuning(
        restored_vocal, sample_rate, maqam=maqam_drone, strength=microtonal_tune
    )
    eq_vocal = apply_vocal_eq(tuned_vocal, sample_rate)
    deessed_vocal = apply_vocal_deesser(eq_vocal, sample_rate)
    steady_vocal = apply_parallel_vocal_compression(deessed_vocal, blend=0.24)

    is_rubato = mode in ("mawal", "nai")
    delay_ms = compute_tempo_synced_delay_ms(bpm, is_rubato=is_rubato)
    rt60 = 3.8 if is_rubato else 3.2

    ir_file = os.path.join(samples_dir, "husseiniya_ir.wav") if samples_dir else None
    echoed_vocal = apply_dynacord_echo(steady_vocal, sample_rate, delay_ms=delay_ms, feedback=0.32, mix=0.22)
    wet_mix_val = 0.14 if mode in ("heavy_clip", "thaqeel_muwazza", "bahrani_muthakkal") else 0.26
    wet_vocal = apply_husseiniya_reverb(
        echoed_vocal, sample_rate, rt60=rt60, wet_mix=wet_mix_val, ir_path=ir_file
    )

    if offset_ms is not None:
        offset_samples = max(0, int((offset_ms / 1000.0) * sample_rate))
    else:
        offset_samples = detect_vocal_onset_offset_samples(steady_vocal, sample_rate)

    rhythm_bed = build_rhythm_bed(
        len(mono),
        sample_rate,
        mode=mode,
        bpm=bpm,
        offset_samples=offset_samples,
        swing=swing,
        samples_dir=samples_dir,
    )
    use_strings_pad = mode in ("heavy_clip", "thaqeel_muwazza", "studio_arranged", "bahrani_muthakkal")
    ahaat_pad = synthesize_dynamic_pitch_tracked_ahaat(
        steady_vocal, sample_rate, maqam=maqam_drone, is_strings_pad=use_strings_pad
    )
    if use_strings_pad:
        rhythm_bed = apply_husseiniya_reverb(
            rhythm_bed, sample_rate, rt60=2.8, wet_mix=0.22, ir_path=ir_file
        )

    foley_bed = synthesize_contextual_foley(
        len(mono), sample_rate, foley_type=foley, lyrics_text=lyrics_text
    )

    if audio_drop_sec is not None:
        rhythm_bed = apply_dramatic_audio_drop(rhythm_bed, sample_rate, drop_start_sec=audio_drop_sec)
        ahaat_pad = apply_dramatic_audio_drop(ahaat_pad, sample_rate, drop_start_sec=audio_drop_sec)

    ducking = compute_smart_sidechain_ducking(steady_vocal, sample_rate, duck_db=-3.0)
    left_chan, right_chan = apply_mono_safe_stereo_stage(
        wet_vocal, rhythm_bed, ahaat_pad, foley_bed, ducking, sample_rate, replace_ai=replace_ai_percussion
    )

    stereo_raw = np.column_stack(
        (tape_saturate(left_chan, drive=1.35), tape_saturate(right_chan, drive=1.35))
    )
    stereo_glued = apply_master_glue_compressor(stereo_raw, ratio=1.5, threshold=0.65)
    stereo = normalize_lufs_and_true_peak(
        stereo_glued, sample_rate, target_lufs=-14.0, ceiling_dbtp=-1.0
    )

    write_wav_bit_depth(output_path, sample_rate, stereo, bit_depth=bit_depth)

    if export_stems_dir:
        os.makedirs(export_stems_dir, exist_ok=True)
        write_wav_bit_depth(os.path.join(export_stems_dir, "01_Lead_Radood.wav"), sample_rate, wet_vocal, bit_depth=bit_depth)
        write_wav_bit_depth(os.path.join(export_stems_dir, "02_Percussion_Latm.wav"), sample_rate, rhythm_bed * ducking, bit_depth=bit_depth)
        write_wav_bit_depth(os.path.join(export_stems_dir, "03_Dynamic_Ahaat_Pad.wav"), sample_rate, ahaat_pad * ducking, bit_depth=bit_depth)
        write_wav_bit_depth(os.path.join(export_stems_dir, "04_Semantic_Foley.wav"), sample_rate, foley_bed * ducking, bit_depth=bit_depth)
        write_wav_bit_depth(os.path.join(export_stems_dir, "05_Master_Mix.wav"), sample_rate, stereo, bit_depth=bit_depth)


def parse_args(argv=None):
    """Parse CLI arguments for the V50.0 Hussaini DSP Montage, Melody & Prosody Compiler."""
    parser = argparse.ArgumentParser(
        description=f"Hussaini Audio Omni-Engine DSP, Melody & Prosody Compiler ({SKILL_VERSION})"
    )
    parser.add_argument("--input", default=None, help="Path to raw input WAV recording")
    parser.add_argument("--output", default=None, help="Path to output mastered stereo WAV")
    parser.add_argument("--extract-profile", default=None, help="Reverse-engineer BPM, Tonic, 15-Maqam Cents Histogram & LUFS")
    parser.add_argument("--compile-lyrics", default=None, help="Compile poem lyrics (Modules 40, 41 & 43)")
    parser.add_argument("--compile-g2p", default=None, help="Module 51: 6-Dialect Generative G2P + IPA transcription")
    parser.add_argument("--dialect", default=None, help="Optional explicit dialect (iraqi, iraqi_janoubi, bahrani, qatifi, hasawi, ahwazi, amili, fusha)")
    parser.add_argument("--match-meter", default=None, help="Module 49: Binary Arud bitmask match across 25 poetic meters")
    parser.add_argument("--compose-melody", default=None, help="Module 50: Compose 24-EDO syllable-locked microtonal melody")
    parser.add_argument("--melody-wav", default=None, help="Optional output path for 24-EDO Guide Vocal WAV")
    parser.add_argument("--melody-midi", default=None, help="Optional output path for 14-bit Pitch-Bend Microtonal MIDI")
    parser.add_argument("--multi-maqam", action="store_true", default=False, help="Include comparative multi-Maqam key readings")
    parser.add_argument("--export-scala", default=None, help="Export Huygens-Fokker Scala (.scl) microtonal tuning file")
    parser.add_argument("--tor-rules", default=None, choices=list(PERFORMANCE_ATWAR_CATALOG.keys()), help="Module 51: Apply specific Tor delivery & council placement rules")
    parser.add_argument("--council-pos", default="middle", choices=["opening", "middle", "closing"], help="Position in Husseini council (opening, middle, closing)")
    parser.add_argument("--ai-router", default=None, choices=["flow_music", "suno_v4_5", "suno_v5_5", "udio", "rvc_svc"], help="Module 52: Multi-engine AI prompt & voice router")
    parser.add_argument("--verified-voice-id", default=None, help="Optional verified custom voice ID for ethical SVC/Voice Cloning")
    parser.add_argument("--lint-poem", default=None, help="Run pre-generation poem linter")
    parser.add_argument("--validate-abudhiyah", default=None, help="Validate Iraqi Abudhiyah Jinas")
    parser.add_argument("--validate-zuhayri", default=None, help="Validate 7-line Zuhayri Mawal")
    parser.add_argument("--recommend-tor", default=None, help="Recommend Poetic Meter, Tor, Maqam Arc, Rhythm & BPM")
    parser.add_argument("--genre", default=None, choices=["latmiya", "nasheed", "ibtihalat", "tawashih"], help="Build strict vocal genre profile")
    parser.add_argument("--enforce-iraqi-dhaa", action="store_true", default=None, help="Explicitly enforce Iraqi emphatic Dhaa (ظ)")
    parser.add_argument("--use-tatweel", action="store_true", default=False, help="Use Tatweel after single-letter prepositions")
    parser.add_argument("--no-tatweel", action="store_true", default=False, help="Force clean space separation (default)")
    parser.add_argument("--replace-ai-percussion", action="store_true", default=False, help="STFT HPSS AI percussion removal + human Latm rebuild")
    parser.add_argument(
        "--mode",
        default="latm",
        choices=[
            "latm", "heavy_clip", "thaqeel_muwazza", "studio_arranged",
            "bahrani_fast", "bahrani_thulathi", "bahrani_rubai", "bahrani_haidari",
            "bahrani_waqfa", "bahrani_muthakkal", "zanjeel_iraqi", "zanjeel_bahrani",
            "dammam_tasa", "iraqi_hosa", "bahrani_hosa", "shoor", "bandari", "mawal", "nai",
        ],
        help="Husseiniya rhythmic and acoustic processing mode (19 heritage & studio modes)",
    )
    parser.add_argument("--bpm", type=float, default=60.0, help="Tempo in BPM (0 for Rubato)")
    parser.add_argument("--maqam-drone", default="saba", choices=list(MAQAM_FREQS.keys()), help="15-Maqam 24-EDO profile")
    parser.add_argument(
        "--foley",
        default="none",
        choices=["none", "wind", "water", "horses", "chains", "swords", "majlis_weeping", "auto"],
        help="Static or semantic lyric-driven ('auto') ritual Foley sound design",
    )
    parser.add_argument("--lyrics-text", default=None, help="Poem text used for semantic Foley timing or Tor rules")
    parser.add_argument("--microtonal-tune", type=float, default=0.0, help="24-EDO Maqam vocal pitch-correction strength (0.0 to 1.0)")
    parser.add_argument("--bit-depth", type=int, default=16, choices=[16, 24], help="Output PCM WAV bit depth (16 or studio 24-bit)")
    parser.add_argument("--export-stems", default=None, help="Optional directory to export 5 separated mixing stems")
    parser.add_argument("--audio-drop-sec", type=float, default=None, help="Timestamp (sec) for dramatic Audio Drop")
    parser.add_argument("--offset-ms", type=float, default=None, help="Manual rhythm grid offset in ms")
    parser.add_argument("--swing", type=float, default=0.0, help="Swing factor (0.0 to 0.35)")
    parser.add_argument("--samples-dir", default=None, help="Optional directory containing real WAV percussion/IR samples")
    parser.add_argument("--session-log", default=None, help="Optional JSON ledger file path")
    return parser.parse_args(argv)


def main(argv=None):
    """CLI Entrypoint supporting V50.0 Prosody, Melody, 6-Dialect G2P, Multi-AI Router & 24-Bit DSP."""
    args = parse_args(argv)
    use_tatweel = bool(args.use_tatweel and not args.no_tatweel)

    if args.export_scala is not None:
        rep = export_scala_microtonal_scale(maqam=args.maqam_drone, output_scl_path=args.export_scala)
        if args.compose_melody is None and args.input is None:
            print(json.dumps(rep, ensure_ascii=False, indent=2))
            return 0

    if args.extract_profile is not None:
        if not os.path.isfile(args.extract_profile):
            print(f"Error: Profile input file not found: {args.extract_profile}", file=sys.stderr)
            return 1
        print(json.dumps(extract_reference_audio_profile(args.extract_profile), ensure_ascii=False, indent=2))
        return 0

    if args.match_meter is not None:
        print(json.dumps(match_poetic_meter_bitmask(args.match_meter), ensure_ascii=False, indent=2))
        return 0

    if args.compile_g2p is not None:
        rep = compile_dialect_g2p_and_ipa(args.compile_g2p, dialect=args.dialect, use_tatweel=use_tatweel)
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0

    if args.tor_rules is not None:
        sample_txt = args.lyrics_text or "يَا حْسَيْنْ يَا مَظْلُومْ .."
        rep = apply_minbar_tor_delivery_rules(sample_txt, tor_id=args.tor_rules, position=args.council_pos)
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0

    if args.compose_melody is not None:
        plan = compose_microtonal_melody_for_poem(
            args.compose_melody, maqam=args.maqam_drone, bpm=args.bpm
        )
        if args.melody_wav:
            export_guide_melody_wav(plan, args.melody_wav, bit_depth=args.bit_depth)
            plan["exported_guide_wav"] = args.melody_wav
        if args.melody_midi:
            export_microtonal_midi(plan, args.melody_midi)
            plan["exported_microtonal_midi"] = args.melody_midi
        if args.multi_maqam:
            plan["multi_maqam_readings"] = generate_multi_maqam_readings(args.compose_melody, bpm=args.bpm)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    if args.ai_router is not None:
        rep = build_multi_engine_ai_prompt(
            engine_name=args.ai_router,
            dialect=args.dialect or "iraqi",
            maqam=args.maqam_drone,
            bpm=int(args.bpm),
            verified_voice_id=args.verified_voice_id,
        )
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0

    if args.compile_lyrics is not None:
        report = detect_and_shape_dialect(
            args.compile_lyrics,
            enforce_iraqi_dhaa=args.enforce_iraqi_dhaa,
            use_tatweel=use_tatweel,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.lint_poem is not None:
        print(json.dumps(lint_poem(args.lint_poem), ensure_ascii=False, indent=2))
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
        report = build_vocal_genre_profile(
            genre=args.genre,
            dialect=args.dialect or "iraqi",
            maqam=args.maqam_drone,
            bpm=args.bpm if args.bpm else None,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if not args.input or not args.output:
        print("Error: --input and --output are required for audio processing.", file=sys.stderr)
        return 1

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    process_audio_file(
        input_path=args.input,
        output_path=args.output,
        mode=args.mode,
        bpm=args.bpm,
        maqam_drone=args.maqam_drone,
        offset_ms=args.offset_ms,
        swing=args.swing,
        samples_dir=args.samples_dir,
        foley=args.foley,
        audio_drop_sec=args.audio_drop_sec,
        replace_ai_percussion=args.replace_ai_percussion,
        microtonal_tune=args.microtonal_tune,
        bit_depth=args.bit_depth,
        lyrics_text=args.lyrics_text,
        export_stems_dir=args.export_stems,
    )
    if args.session_log:
        log_generation_session(
            args.session_log,
            prompt=f"DSP Montage V50 mode={args.mode} bpm={args.bpm} maqam={args.maqam_drone} {args.bit_depth}bit",
            lyrics=args.lyrics_text or args.input,
            result_url=args.output,
        )
    print(
        f"Successfully mastered Husseiniya audio ({args.mode}, {args.bpm} BPM, "
        f"Maqam {args.maqam_drone}, {args.bit_depth}-bit Mono-Safe) -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
