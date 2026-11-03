#!/usr/bin/env python3
# pylint: disable=too-many-lines,too-many-return-statements
"""Hussaini Audio Omni-Engine DSP, 5-Track DAW & Phonetics Compiler (V45.0 OMNI-ARCHITECT).

Bridges poetic/phonetic engineering with procedural DSP audio mastering:
- Single-Source Version Management via root VERSION file
- Module 41: Space-First & Optional-Tatweel Anti-Slurring Word De-Cliticization Engine
- Module 40: Safe Dialect-Accurate & Prosodic Tanween Compiler (protects vocalized verbs & vocatives)
- Module 43: Word-Boundary Morphological Dialect Shaper (Bahrani, Iraqi, and Hybrid Iraqi-Bahrani)
- Modules 34 & 38: Arabic Prosodic Syllable Segmenter (CV/CVV/CVC) & Per-Hemistich Iso-Syllabic Validator
- Pre-Generation Poem Linter (lint_poem) & Session Ledger Logger (log_generation_session)
- Module 39: Flow Music JSON Session Pre-Conditioning with Optional reference_clip_id (default None)
- 5-Track DAW Routing with SOS Filters (butter output='sos' + sosfilt), Absolute dBFS RMS Sidechain
  Ducking (-3.0dB with Attack/Release), Fast Vectorized Multi-Tap Dynacord Echo, ITU-R BS.1770-4
  LUFS Loudness Normalization (-14.0 LUFS) + True-Peak Limiter (-1.0 dBTP), Vocal Onset Sync,
  Bandari Swing, and Optional Real Acoustic Samples / IR Directory (--samples-dir)
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
    return "V45.0 OMNI-ARCHITECT"


SKILL_VERSION = get_skill_version()

MAQAM_FREQS = {
    "bayati": [146.83, 160.00, 174.61, 220.00],
    "saba": [146.83, 160.00, 174.61, 207.65],
    "hijaz": [146.83, 155.56, 185.00, 220.00],
    "lami": [146.83, 155.56, 174.61, 207.65],
    "kurd": [146.83, 155.56, 174.61, 220.00],
    "rast": [130.81, 146.83, 160.00, 196.00],
    "nahawand": [146.83, 164.81, 174.61, 220.00],
}

COMMON_JINS_GRAPH = {
    "bayati": ["saba", "kurd", "hijaz", "lami", "nahawand"],
    "saba": ["bayati", "lami", "hijaz", "rast", "nahawand"],
    "hijaz": ["bayati", "saba", "kurd", "nahawand"],
    "lami": ["saba", "bayati", "kurd"],
    "kurd": ["bayati", "lami", "hijaz", "nahawand"],
    "rast": ["saba", "bayati", "hijaz"],
    "nahawand": ["kurd", "bayati", "saba", "hijaz"],
}

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

WORD_INITIAL_SUKUN_REPAIR_MAP = {
    "إِدْمُوعْ": "دْمُوعْ",
    "إِجْرُوحْ": "جْرُوحْ",
    "إِمْتُونِي": "مْتُونِي",
    "إِسْنِينِي": "سْنِينِي",
    "إِسْكِينَهْ": "سْكِينَه",
    "إِسْكِينَه": "سْكِينَه",
    "إِعْيُونَكْ": "عْيُونَكْ",
    "إِعْيُونِكْ": "عْيُونِكْ",
    "إِتْگِلَّهْ": "تْگِلَّه",
    "إِتْگِلَّه": "تْگِلَّه",
    "إِتْسُولِفْ": "تْسُولِفْ",
    "إِهْمُومْ": "هْمُومْ",
}

DIALECTAL_DIPHTHONG_AND_VOWEL_MAP = {
    "هَنِيَالِي": "هَنْيَالِي",
    "غَرِيبَهْ": "غَرِيبَه",
    "حِچَايَهْ": "حِچَايَه",
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
    "وگفت": "وْگَفِتْ",
    "ووگفت": "وَ وْگَفِتْ",
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
    "ابجلمة": "بْچِلْمَه",
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
    "دموع": "دْمُوعْ",
    "زچيه": "زَچِيَّه",
    "زچية": "زَچِيَّه",
    "تسولف": "تْسُولِفْ",
    "هموم": "هْمُومْ",
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
    "تگله": "تْگِلَّه",
    "گوم": "گُومْ",
    "شوف": "شُوفْ",
    "حزينه": "حَزِينَه",
    "حزينة": "حَزِينَه",
    "متوني": "مْتُونِي",
    "زرگ": "زُرُگْ",
    "زُرَگْ": "زُرُگْ",
    "زرك": "زُرُگْ",
    "تراچي": "تَرَاچِي",
    "جروح": "جْرُوحْ",
    "يتيمه": "يَتِيمَه",
    "يتيمة": "يَتِيمَه",
    "حضنت": "حِظْنَتْ",
    "شبگت": "شَبْگَتْ",
    "نحره": "نَحْرَه",
    "سكتت": "سِكْتَتْ",
    "ذيچ": "ذِيچْ",
    "بنية": "بْنَيَّه",
    "بنيه": "بْنَيَّه",
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
    "سكينه": "سْكِينَه",
    "سكينة": "سْكِينَه",
    "هنيالي": "هَنْيَالِي",
    "خادم": "خَادِمْ",
    "مولاي": "مَوْلَايْ",
    "سنيني": "سْنِينِي",
    "عيني": "عَيْنِي",
    "عيونك": "عْيُونَكْ",
    "شده": "شِدَّه",
    "شدة": "شِدَّه",
    "ينخونك": "يِنْخُونَكْ",
    "مضيع": "مْظَيِّعْ",
    "ندمان": "نَدْمَانْ",
    "يلحگ": "يِلْحَگْ",
}

BAHRANI_WORD_SHAPING_MAP = {
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
    "دموع": "دْمُوعْ",
    "جروح": "جْرُوحْ",
    "متوني": "مْتُونِي",
    "سنيني": "سْنِينِي",
    "عيونك": "عْيُونِكْ",
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
    "وگفت": "وْگَفِتْ",
    "عفتني": "عِفْتْنِي",
    "ضلوعي": "ضْلُوعِي",
    "فاضل": "فَاضِلْ",
}


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
    # Also fix 'يهل الغرب' / 'يَا هَلْ الغُرَبْ' liaison Kasra
    result = result.replace("يهل الغرب", "يَا هَلِ الغُرَبْ").replace("يَا هَلْ الغُرَبْ", "يَا هَلِ الغُرَبْ")
    return result


def repair_word_initial_sukun_and_diphthongs(text):
    """Repair word-initial Sukun violations (مْتُونِي -> إِمْتُونِي) and Fusha diphthongs in colloquial text."""
    result = text
    for bad_sukun, repaired in WORD_INITIAL_SUKUN_REPAIR_MAP.items():
        result = re.sub(rf"(?<!\S){re.escape(bad_sukun)}(?!\S)", repaired, result)
    for fusha_diph, coll_mono in DIALECTAL_DIPHTHONG_AND_VOWEL_MAP.items():
        result = re.sub(rf"(?<!\S){re.escape(fusha_diph)}(?!\S)", coll_mono, result)
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
    """Module 40: Convert mid-line Tanween to phonetic Nunation safely without corrupting next word."""
    processed = de_cliticize_and_separate_words(text, use_tatweel=use_tatweel)
    for raw_phrase, phonetic_phrase in COLLOQUIAL_TANWEEN_MAP.items():
        processed = processed.replace(raw_phrase, phonetic_phrase)
    for raw_fusha, phonetic_fusha in FUSHA_MIDLINE_TANWEEN_MAP.items():
        processed = processed.replace(raw_fusha, phonetic_fusha)

    if dialect in ("iraqi", "bahrani", "iraqi_bahrani"):
        # Only add Kasra to following verb prefix (ت/ي/ن) if it has NO existing diacritic and NO following Alif (ا/آ/ى)
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
        stripped = re.sub(r"(?:اً|ً)(\s+\.\.)", r"َا\1", stripped)
        stripped = re.sub(r"(?:اً|ً)$", "َا", stripped)
        stripped = re.sub(r"[ٌٍُِ]$", "ْ", stripped)
        if not stripped.endswith(("ْ", "ا", "ى", "و", "ي", "ه", "ة", ")")):
            stripped = stripped + "ْ"
        lines.append(stripped)
    return "\n".join(lines)


def shape_token_morphologically(token, word_map, use_tatweel=False):
    """Decompose prefixes (ال، و، ب، ك، ل) and shape the stem if present in word_map."""
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
    return {
        "detected_dialect": detected,
        "bahrani_score": bahrani_hits,
        "iraqi_score": iraqi_hits,
        "dhad_articulation": dhad_mode,
        "maqam_articulation_rule": maqam_rule,
        "shaped_lyrics": shaped,
    }


def count_arabic_syllables(hemistich):
    """Estimate prosodic Arabic syllable count (CV / CVV / CVC) for a single hemistich."""
    cleaned = re.sub(r"[\[\]\(\)\.\،\-\_ـ]", " ", hemistich)
    words = [w for w in cleaned.split() if w]
    total_syllables = 0

    for word in words:
        short_vowels = len(re.findall(r"[\u064E\u064F\u0650]", word))
        base_letters = re.findall(r"[\u0621-\u063A\u0641-\u064A\u067E\u0686\u06AF]", word)
        if not base_letters:
            continue
        if short_vowels >= 1:
            long_unmarked = len(re.findall(r"[اآى]", word))
            sukun_count = len(re.findall(r"\u0652", word))
            unmarked_consonants = max(
                0, len(base_letters) - short_vowels - sukun_count - long_unmarked
            )
            word_syllables = short_vowels + max(0, unmarked_consonants // 2)
        else:
            word_syllables = max(1, int(round(len(base_letters) * 0.62)))
        total_syllables += max(1, word_syllables)

    return total_syllables


def validate_stage1_iso_syllabic_lock(lines, max_syllable_spread=3):
    """Modules 34 & 38: Validate 4-line stanzas, identical 4th-line refrain, and per-hemistich syllable balance."""
    clean_lines = [
        ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("[")
    ]
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
            if len(part_syllables) >= 2 and (max(part_syllables) - min(part_syllables)) > max_syllable_spread:
                internal_hemistich_balanced = False
        else:
            hemistich_counts.append(count_arabic_syllables(ln))

    if hemistich_counts:
        spread = max(hemistich_counts) - min(hemistich_counts)
        iso_balanced = internal_hemistich_balanced and (spread <= max_syllable_spread + 1)
    else:
        iso_balanced = False

    return {
        "line_count": len(clean_lines),
        "is_valid_stanza_grid": is_valid_count,
        "identical_4th_line_refrain": identical_refrain,
        "hemistich_syllable_counts": hemistich_counts,
        "internal_hemistich_balanced": internal_hemistich_balanced,
        "iso_syllabic_balanced": iso_balanced,
        "passed": bool(is_valid_count and identical_refrain and iso_balanced),
    }


def lint_poem(text, stage=1):
    """Comprehensive pre-generation poem linter estimating Stage-1 success probability."""
    slurring_risks = [w for w in WORD_SEPARATION_MAP if re.search(rf"(?<!\S)و?{re.escape(w)}(?!\S)", text)]
    has_fusha = any(m in text for m in FUSHA_MARKERS)
    has_colloquial = any(m in text for m in BAHRANI_MARKERS + IRAQI_MARKERS)
    fusha_colloquial_mixed = bool(stage == 1 and has_fusha and has_colloquial)

    dialect_report = detect_and_shape_dialect(text)
    shaped_lines = dialect_report["shaped_lyrics"].splitlines()
    iso_report = validate_stage1_iso_syllabic_lock(shaped_lines)
    tatweel_count = dialect_report["shaped_lyrics"].count("ـ")

    score = 100
    if slurring_risks:
        score -= 15
    if fusha_colloquial_mixed:
        score -= 30
    if not iso_report["is_valid_stanza_grid"]:
        score -= 25
    if not iso_report["identical_4th_line_refrain"]:
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
        "human_review_required": True,
        "estimated_stage1_success_score": score,
        "ready_for_generation": bool(score >= 80 and not fusha_colloquial_mixed),
    }


def split_long_lines_for_steady_pacing(text, max_words_per_line=5):
    """Module 44: Split long narrative lines (>max_words_per_line) vertically into short 3-4 word lines.

    Prevents Flow Music / Lyria from rushing 14-16 syllable lines into a fast, bouncy song-like cadence
    after 1:27 by allocating a full musical bar (3.5-4s) to each short hemistich.
    """
    out_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("["):
            out_lines.append(line)
            continue
        words_only = [w for w in stripped.split() if w != ".." and not w.startswith("(")]
        if len(words_only) > max_words_per_line:
            if ".." in stripped:
                parts = [p.strip() for p in stripped.split("..") if p.strip()]
                for idx, part in enumerate(parts):
                    suffix = " .." if idx < len(parts) - 1 else ""
                    out_lines.append(f"{part}{suffix}")
                continue
            tokens = stripped.split()
            mid = len(tokens) // 2
            out_lines.append(" ".join(tokens[:mid]) + " ..")
            out_lines.append(" ".join(tokens[mid:]))
        else:
            out_lines.append(stripped)
    return "\n".join(out_lines)


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
    """Module 46: Match poetic meter, syllable count, and theme to optimal Tor, Maqam Arc, Rhythm & BPM."""
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
    bahrani_fast_markers = ("يا بويي", "امساعد", "الراعبية", "وقفة", "شيلة")
    shoor_markers = ("شور", "لبيك", "حيدر حيدر", "مجنونك")
    rukbani_markers = ("الغرب خذتني", "گلبی ذاب", "گلبي ذاب", "سياط", "طاح الحيل", "ضعن", "سبايا")

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
        "recommended_tor": tor_name,
        "rhythm_mode": rhythm_mode,
        "recommended_bpm": bpm,
        "avg_hemistich_syllables": round(avg_syllables, 2),
        "detected_dialect": dialect_info["detected_dialect"],
        "maqam_arc": maqam_arc,
        "flowmusic_sound_prompt": sound_prompt,
    }


def audit_legendary_latmiya_pillars(text):
    """Module 48: Audit a Latmiya poem against the 5 Pillars of Legendary Hussaini Latmiya Success."""
    blocks = re.split(r"(\[(?:Chorus|Verse[^\]]*|Outro|Intro)\])", text)
    current_tag = ""
    mid_verse_parentheticals = []
    chorus_line_counts = []
    verse_line_counts = []

    for chunk in blocks:
        if chunk.startswith("[") and chunk.endswith("]"):
            current_tag = chunk
            continue
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            continue
        if "Verse" in current_tag:
            verse_line_counts.append(len(lines))
            for ln in lines:
                if "(" in ln or ")" in ln:
                    mid_verse_parentheticals.append(ln)
        elif "Chorus" in current_tag:
            chorus_line_counts.append(len(lines))

    feminine_haa_sukun_hits = re.findall(r"\S+هْ(?!\S)", text)
    glottal_cluster_hits = re.findall(
        r"(?<!\S)(?:إِدْمُوعْ|إِمْتُونِي|إِسْنِينِي|إِجْرُوحْ|إِتْگِلَّه|إِتْسُولِفْ|إِهْمُومْ)(?!\S)",
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
        "mid_verse_parentheticals_found": mid_verse_parentheticals,
        "feminine_haa_sukun_found": feminine_haa_sukun_hits,
        "passed_all_5_pillars": bool(
            chorus_line_counts
            and clean_8_line_nazlas
            and not mid_verse_parentheticals
            and has_kaser_bridge
            and not feminine_haa_sukun_hits
            and not glottal_cluster_hits
        ),
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
    """Module 39: Build the V45.0 JSON Session Pre-Conditioning payload with optional reference_clip_id."""
    payload = {
        "protocol_name": "Hussaini_Production_Studio_OS_V45_OMNI_ARCHITECT",
        "skill_version": SKILL_VERSION,
        "session_mode": "Pre_Conditioning_Lock_Only_Wait_For_Step_2_Lyrics",
        "target_dialect": dialect,
        "single_stage1_maqam": maqam,
        "tempo_bpm": bpm,
        "anti_slurring_word_separation": True,
        "zero_word_initial_sukun": True,
        "preserve_iraqi_prosthetic_alif": True,
        "vertical_short_line_splitting": True,
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

    # Soft knee 6dB above threshold_dbfs so normal vocal levels reach full -3.0dB ducking
    over_db = np.clip((rms_dbfs - threshold_dbfs) / 12.0, 0.0, 1.0)

    # First-order block smoothing approximating asymmetric attack/release envelope
    atk_samples = max(1, int((attack_ms / 1000.0) * sample_rate))
    rel_samples = max(1, int((release_ms / 1000.0) * sample_rate))
    smooth_win = max(1, (atk_samples + rel_samples) // 2)
    smooth_kernel = np.exp(-np.linspace(0.0, 3.0, smooth_win))
    smooth_kernel /= np.sum(smooth_kernel)
    activity = np.clip(fftconvolve(over_db, smooth_kernel, mode="same")[: len(vocal_signal)], 0.0, 1.0)

    target_linear = float(10.0 ** (duck_db / 20.0))
    ducking_gain = 1.0 - activity * (1.0 - target_linear)
    return ducking_gain


def apply_dynacord_echo(signal, sample_rate, delay_ms=285.0, feedback=0.32, mix=0.22):
    """Fast vectorized multi-tap analog tape slapback echo (replaces slow polynomial lfilter)."""
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


def synthesize_percussion_hit(sample_rate, kind="latm", samples_dir=None):
    """Load real acoustic percussion sample from samples_dir if present, else synthesize procedurally."""
    if samples_dir and os.path.isdir(samples_dir):
        candidate = os.path.join(samples_dir, f"{kind}.wav")
        if os.path.isfile(candidate):
            _, hit_data = wavfile.read(candidate)
            hit_float = hit_data.astype(np.float64)
            if hit_float.ndim > 1:
                hit_float = np.mean(hit_float, axis=1)
            peak = np.max(np.abs(hit_float))
            return hit_float / peak if peak > 1e-8 else hit_float

    rng = np.random.default_rng(seed=101)
    dur = 0.24
    num_samples = max(1, int(dur * sample_rate))
    t_vec = np.linspace(0.0, dur, num_samples, endpoint=False)

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

    if kind in ("heavy_clip", "thaqeel_muwazza"):
        # Double-Layered Beat (Chest Low-End + Crisp Palm Snap) + Beat-Synced Human Sub-Bass Hum
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

    if kind == "bahrani_fast":
        # Studio 44 (Rm0gQkZLQao): Strong fast Bahrani chest+palm slap with high transient energy
        chest_core = np.sin(2.0 * np.pi * 62.0 * t_vec) * np.exp(-18.0 * t_vec)
        sharp_slap = rng.normal(0.0, 1.0, num_samples) * np.exp(-34.0 * t_vec)
        if 0.5 * sample_rate > 3800.0:
            sharp_slap = butter_filter(sharp_slap, [1400.0, 3600.0], sample_rate, btype="band", order=2)
        return 0.70 * chest_core + 0.50 * sharp_slap

    if kind == "studio_arranged":
        # Ammar Al-Hujaimi (AHKVHPS51Sc): 4-Layer Studio Latm (Sub-Kick + Crowd Chest + Palm + Breath)
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
    return 0.80 * sub_thud + 0.25 * skin_slap


def build_rhythm_bed(
    num_samples, sample_rate, mode="latm", bpm=60.0, offset_samples=0, swing=0.0, samples_dir=None
):
    """Generate a synchronized Husseiniya percussion track with onset offset and Bandari swing."""
    bed = np.zeros(num_samples, dtype=np.float64)
    if bpm <= 0.0 or mode in ("mawal", "nai"):
        return bed

    beat_interval = int((60.0 / bpm) * sample_rate)
    if beat_interval <= 0:
        return bed

    primary_hit = synthesize_percussion_hit(sample_rate, "latm", samples_dir=samples_dir)
    heavy_hit = synthesize_percussion_hit(sample_rate, "heavy_clip", samples_dir=samples_dir)
    dammam_hit = synthesize_percussion_hit(sample_rate, "dammam", samples_dir=samples_dir)
    zanjeel_hit = synthesize_percussion_hit(sample_rate, "zanjeel", samples_dir=samples_dir)
    bahrani_hit = synthesize_percussion_hit(sample_rate, "bahrani_fast", samples_dir=samples_dir)
    studio_hit = synthesize_percussion_hit(sample_rate, "studio_arranged", samples_dir=samples_dir)

    cursor = max(0, int(offset_samples))
    beat_idx = 0
    while cursor < num_samples:
        if mode in ("zanjeel_iraqi", "zanjeel_bahrani", "bandari"):
            hit = dammam_hit if (beat_idx % 2 == 0) else (0.65 * dammam_hit + 0.55 * zanjeel_hit)
            if mode == "zanjeel_bahrani" and (beat_idx % 4 == 2):
                sub_pos = cursor + beat_interval // 2
                end_sub = min(num_samples, sub_pos + len(zanjeel_hit))
                if sub_pos < num_samples:
                    bed[sub_pos:end_sub] += 0.6 * zanjeel_hit[: end_sub - sub_pos]
            if mode == "bandari" and swing > 0.0:
                swing_pos = cursor + int(beat_interval * (0.5 + 0.16 * min(swing, 0.35)))
                end_sw = min(num_samples, swing_pos + len(primary_hit))
                if swing_pos < num_samples:
                    bed[swing_pos:end_sw] += 0.45 * primary_hit[: end_sw - swing_pos]
        elif mode == "bahrani_fast":
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
        elif mode in ("heavy_clip", "thaqeel_muwazza"):
            hit = heavy_hit
        else:
            hit = primary_hit

        end_idx = min(num_samples, cursor + len(hit))
        bed[cursor:end_idx] += hit[: end_idx - cursor]
        cursor += beat_interval
        beat_idx += 1

    return bed


def synthesize_ahaat_drone(num_samples, sample_rate, maqam="saba"):
    """Track_04_Ahaat_Vocal_Choir_Pads: Synthesize warm Bandpass (150Hz-12kHz) Ahaat pad."""
    freqs = MAQAM_FREQS.get(maqam, MAQAM_FREQS["saba"])
    t_vec = np.arange(num_samples, dtype=np.float64) / sample_rate
    pad = np.zeros(num_samples, dtype=np.float64)

    for idx, freq in enumerate(freqs):
        lfo = 1.0 + 0.004 * np.sin(2.0 * np.pi * (4.2 + 0.3 * idx) * t_vec)
        pad += (0.35 / (idx + 1)) * np.sin(2.0 * np.pi * freq * lfo * t_vec)

    nyq = 0.5 * sample_rate
    high_cut = min(12000.0, 0.45 * sample_rate)
    if nyq > 300.0 and high_cut > 200.0:
        pad = butter_filter(pad, [150.0, high_cut], sample_rate, btype="band", order=2)
    return pad * 0.14


def synthesize_vocal_synth_strings_pad(num_samples, sample_rate, maqam="saba"):
    """Module 44: Synthesize Vocal-Synth Humming Strings & Cinematic Ambient Pad from vocal formants."""
    freqs = MAQAM_FREQS.get(maqam, MAQAM_FREQS["saba"])
    t_vec = np.arange(num_samples, dtype=np.float64) / sample_rate
    pad = np.zeros(num_samples, dtype=np.float64)
    swell = 0.75 + 0.25 * np.sin(2.0 * np.pi * 0.16 * t_vec)

    for idx, freq in enumerate(freqs):
        vib = 1.0 + 0.0035 * np.sin(2.0 * np.pi * (4.4 + 0.25 * idx) * t_vec)
        fundamental = np.sin(2.0 * np.pi * freq * vib * t_vec)
        octave_harm = 0.45 * np.sin(2.0 * np.pi * (2.0 * freq) * vib * t_vec)
        fifth_harm = 0.22 * np.sin(2.0 * np.pi * (3.0 * freq) * vib * t_vec)
        pad += (0.32 / (idx + 1)) * (fundamental + octave_harm + fifth_harm)

    pad = pad * swell
    nyq = 0.5 * sample_rate
    high_cut = min(2800.0, 0.45 * sample_rate)
    if nyq > 500.0 and high_cut > 320.0:
        pad = butter_filter(pad, [220.0, high_cut], sample_rate, btype="band", order=2)
    return pad * 0.18


def synthesize_contextual_foley(num_samples, sample_rate, foley_type="none"):
    """Module 44: Synthesize subtle dramatic Foley (desert wind, Euphrates water, echoed horses)."""
    if not foley_type or foley_type == "none" or num_samples <= 0:
        return np.zeros(num_samples, dtype=np.float64)

    rng = np.random.default_rng(seed=202)
    t_vec = np.arange(num_samples, dtype=np.float64) / sample_rate
    noise = rng.normal(0.0, 1.0, num_samples)
    nyq = 0.5 * sample_rate

    if foley_type == "wind":
        gust = 0.55 + 0.45 * np.sin(2.0 * np.pi * 0.22 * t_vec)
        high_cut = min(1200.0, 0.42 * sample_rate)
        if nyq > 350.0 and high_cut > 220.0:
            wind = butter_filter(noise, [180.0, high_cut], sample_rate, btype="band", order=2)
        else:
            wind = noise
        return 0.045 * wind * gust

    if foley_type == "water":
        stream = butter_filter(noise, min(900.0, 0.4 * sample_rate), sample_rate, btype="low", order=2)
        droplet_env = np.exp(-35.0 * np.mod(t_vec, 0.45))
        droplet = np.sin(2.0 * np.pi * 1150.0 * t_vec) * droplet_env
        return 0.035 * (0.6 * stream + 0.4 * droplet)

    if foley_type == "horses":
        cadence = np.exp(-28.0 * np.mod(t_vec, 0.38)) + 0.7 * np.exp(-28.0 * np.mod(t_vec + 0.14, 0.38))
        hoof = noise * cadence
        if nyq > 600.0:
            hoof = butter_filter(hoof, [120.0, min(850.0, 0.4 * sample_rate)], sample_rate, btype="band", order=2)
        return 0.04 * hoof

    return np.zeros(num_samples, dtype=np.float64)


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
):
    """Load an input WAV file, apply 5-Track Husseiniya DSP montage & -14 LUFS mastering, and write WAV."""
    sample_rate, mono = read_wav_any_depth(input_path)

    peak = np.max(np.abs(mono))
    if peak > 1e-8:
        mono = mono / peak

    restored_vocal = apply_noise_print_restoration(mono, sample_rate)
    eq_vocal = apply_vocal_eq(restored_vocal, sample_rate)
    is_rubato = mode in ("mawal", "nai")
    delay_ms = 450.0 if is_rubato else 285.0
    rt60 = 3.8 if is_rubato else 3.2

    ir_file = os.path.join(samples_dir, "husseiniya_ir.wav") if samples_dir else None
    echoed_vocal = apply_dynacord_echo(eq_vocal, sample_rate, delay_ms=delay_ms, feedback=0.32, mix=0.22)
    wet_mix_val = 0.14 if mode in ("heavy_clip", "thaqeel_muwazza") else 0.26
    wet_vocal = apply_husseiniya_reverb(
        echoed_vocal, sample_rate, rt60=rt60, wet_mix=wet_mix_val, ir_path=ir_file
    )

    if offset_ms is not None:
        offset_samples = max(0, int((offset_ms / 1000.0) * sample_rate))
    else:
        offset_samples = detect_vocal_onset_offset_samples(eq_vocal, sample_rate)

    rhythm_bed = build_rhythm_bed(
        len(mono),
        sample_rate,
        mode=mode,
        bpm=bpm,
        offset_samples=offset_samples,
        swing=swing,
        samples_dir=samples_dir,
    )
    if mode in ("heavy_clip", "thaqeel_muwazza", "studio_arranged"):
        ahaat_pad = synthesize_vocal_synth_strings_pad(len(mono), sample_rate, maqam_drone)
        rhythm_bed = apply_husseiniya_reverb(
            rhythm_bed, sample_rate, rt60=2.8, wet_mix=0.22, ir_path=ir_file
        )
    else:
        ahaat_pad = synthesize_ahaat_drone(len(mono), sample_rate, maqam_drone)

    foley_bed = synthesize_contextual_foley(len(mono), sample_rate, foley_type=foley)

    if audio_drop_sec is not None:
        rhythm_bed = apply_dramatic_audio_drop(rhythm_bed, sample_rate, drop_start_sec=audio_drop_sec)
        ahaat_pad = apply_dramatic_audio_drop(ahaat_pad, sample_rate, drop_start_sec=audio_drop_sec)

    ducking = compute_smart_sidechain_ducking(eq_vocal, sample_rate, duck_db=-3.0)

    # 3D Soundstage: Lead vocal centered; rhythm, Vocal-Synth Strings, and Foley panned wide L/R
    left_bg = (0.36 * rhythm_bed + 0.12 * ahaat_pad + foley_bed) * ducking
    right_bg = (0.34 * np.roll(rhythm_bed, 18) - 0.12 * np.roll(ahaat_pad, 42) + np.roll(foley_bed, 24)) * ducking
    left_chan = wet_vocal + left_bg
    right_chan = wet_vocal + right_bg

    stereo_raw = np.column_stack(
        (tape_saturate(left_chan, drive=1.4), tape_saturate(right_chan, drive=1.4))
    )
    stereo_glued = apply_master_glue_compressor(stereo_raw, ratio=1.5, threshold=0.65)
    stereo = normalize_lufs_and_true_peak(
        stereo_glued, sample_rate, target_lufs=-14.0, ceiling_dbtp=-1.0
    )

    out_int16 = np.clip(stereo * 32767.0, -32768, 32767).astype(np.int16)
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    wavfile.write(output_path, sample_rate, out_int16)


def parse_args(argv=None):
    """Parse CLI arguments for the Hussaini DSP Montage Engine & Lyrics Compiler/Linter."""
    parser = argparse.ArgumentParser(
        description=f"Hussaini Audio Omni-Engine DSP & Phonetics Compiler Script ({SKILL_VERSION})"
    )
    parser.add_argument("--input", default=None, help="Path to raw input WAV recording")
    parser.add_argument("--output", default=None, help="Path to output mastered stereo WAV")
    parser.add_argument(
        "--compile-lyrics",
        default=None,
        help="Compile and inspect poem lyrics (Modules 40, 41 & 43) directly from the terminal",
    )
    parser.add_argument(
        "--lint-poem",
        default=None,
        help="Run pre-generation poem linter (word boundaries, dialect mix, hemistich syllables)",
    )
    parser.add_argument(
        "--recommend-tor",
        default=None,
        help="Module 46: Recommend optimal Tor, Maqam Arc, Rhythm Mode, BPM, and Sound Prompt for poem",
    )
    parser.add_argument(
        "--genre",
        default=None,
        choices=["latmiya", "nasheed", "ibtihalat", "tawashih"],
        help="Module 47: Build strict vocal genre profile (latmiya, nasheed, ibtihalat, tawashih)",
    )
    parser.add_argument(
        "--enforce-iraqi-dhaa",
        action="store_true",
        default=None,
        help="Explicitly enforce Iraqi emphatic Dhaa (ظ) conversion",
    )
    parser.add_argument(
        "--use-tatweel",
        action="store_true",
        default=False,
        help="Use Arabic Tatweel (ـ) after single-letter prepositions instead of clean space",
    )
    parser.add_argument(
        "--no-tatweel",
        action="store_true",
        default=False,
        help="Force clean space separation without Tatweel (default behavior)",
    )
    parser.add_argument(
        "--mode",
        default="latm",
        choices=[
            "latm",
            "heavy_clip",
            "thaqeel_muwazza",
            "studio_arranged",
            "bahrani_fast",
            "zanjeel_iraqi",
            "zanjeel_bahrani",
            "shoor",
            "bandari",
            "mawal",
            "nai",
        ],
        help="Husseiniya rhythmic and acoustic processing mode (including Module 46 studio modes)",
    )
    parser.add_argument("--bpm", type=float, default=60.0, help="Tempo in BPM (0 for Rubato)")
    parser.add_argument(
        "--maqam-drone",
        default="saba",
        choices=list(MAQAM_FREQS.keys()),
        help="Maqam frequency profile for the Ahaat / Vocal-Synth Strings pad",
    )
    parser.add_argument(
        "--foley",
        default="none",
        choices=["none", "wind", "water", "horses"],
        help="Contextual dramatic Foley bed (wind, water, horses)",
    )
    parser.add_argument(
        "--audio-drop-sec",
        type=float,
        default=None,
        help="Optional timestamp in seconds to trigger a dramatic Audio Drop (solo broken vocal)",
    )
    parser.add_argument(
        "--offset-ms",
        type=float,
        default=None,
        help="Manual rhythm grid offset in ms (defaults to automatic vocal onset detection)",
    )
    parser.add_argument(
        "--swing",
        type=float,
        default=0.0,
        help="Swing factor (0.0 to 0.35) for Bandari 6/8 groove",
    )
    parser.add_argument(
        "--samples-dir",
        default=None,
        help="Optional directory containing real WAV samples (latm.wav, dammam.wav, zanjeel.wav, husseiniya_ir.wav)",
    )
    parser.add_argument(
        "--session-log",
        default=None,
        help="Optional JSON ledger file path to log the session",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """CLI Entrypoint supporting --compile-lyrics, --lint-poem, and WAV DSP mastering."""
    args = parse_args(argv)
    use_tatweel = bool(args.use_tatweel and not args.no_tatweel)
    if args.compile_lyrics is not None:
        report = detect_and_shape_dialect(
            args.compile_lyrics,
            enforce_iraqi_dhaa=args.enforce_iraqi_dhaa,
            use_tatweel=use_tatweel,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.lint_poem is not None:
        report = lint_poem(args.lint_poem)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.recommend_tor is not None:
        report = recommend_tor_and_rhythm_for_poem(args.recommend_tor)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.genre is not None:
        report = build_vocal_genre_profile(
            genre=args.genre,
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
    )
    if args.session_log:
        log_generation_session(
            args.session_log,
            prompt=f"DSP Montage mode={args.mode} bpm={args.bpm} maqam={args.maqam_drone}",
            lyrics=args.input,
            result_url=args.output,
        )
    print(
        f"Successfully mastered Husseiniya audio ({args.mode}, {args.bpm} BPM, "
        f"Maqam {args.maqam_drone}) -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
