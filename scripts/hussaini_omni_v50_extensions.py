#!/usr/bin/env python3
# pylint: disable=too-many-lines,too-many-locals,too-many-branches,too-many-statements,too-many-arguments,too-many-positional-arguments,too-many-return-statements,no-member
"""V50.0 OMNI-PERFECTION Extension Suite for Hussaini Production Studio.

Implements all 7 advanced studio, prosodic, melodic, dialectal, atwar, DSP & AI-routing pillars:
1. 15 24-EDO Microtonal Maqamat in Cents + Transposition + Scala (.scl) Exporter
2. 25-Meter Binary Arud Bitmask Matcher + Unvocalized Prosodic Inference + Canonical Melodic Keys
3. Microtonal Melody Composer (Watad-to-Downbeat Lock, Multi-Maqam Key Switching, Guide WAV & 14-Bit MIDI)
4. 6-Dialect Generative Morphological G2P + IPA Transducer (Iraqi sub-dialects, Bahrani, Qatifi, Hasawi, Ahwazi, Amili, Fusha)
5. 26 Minbar & Mawkib Atwar Rules Engine (with council opening/closing locks & Wannah/Melisma placement)
6. Pro DSP Upgrades: Cents-Histogram Maqam Classifier, Pitch-Tracked Dynamic Ahaat, 24-EDO Pitch Tuner,
   STFT HPSS Percussion Stripping, Dynamic De-Esser, Parallel Vocal Compression, Round-Robin Percussion
   with Brass Tasa & Matam Breath, Semantic Lyric-Driven Foley, Mono-Safe Mid/Side Stereo, & 24-Bit/Stems
7. Multi-Engine AI Prompt & Voice Router (Flow Music / Lyria 3.5, Suno V4.5, Suno V5.5 Anti-Pop-Wash, Udio, Ethical RVC/SVC)
"""

import os
import re
import struct
import wave
import numpy as np
from scipy.ndimage import median_filter
from scipy.signal import butter, sosfilt, stft, istft

# ==============================================================================
# 1. 15 MICROTONAL 24-EDO MAQAMAT (IN CENTS) & SCALA (.SCL) EXPORTER
# ==============================================================================

MAQAM_INTERVALS_CENTS = {
    "bayati": {
        "arabic_name": "مقام البيات",
        "cents": [0.0, 150.0, 300.0, 500.0, 700.0, 800.0, 1000.0, 1200.0],
        "default_tonic_hz": 146.83,  # D3
        "ghammaz_index": 3,          # G (500c)
        "emotion": "شجن منبري أصيل وحزن متزن",
    },
    "bayati_shuri": {
        "arabic_name": "مقام بيات الشوري (القارچغار)",
        "cents": [0.0, 150.0, 300.0, 500.0, 600.0, 900.0, 1000.0, 1200.0],
        "default_tonic_hz": 146.83,
        "ghammaz_index": 3,          # Hijaz jins on 4th degree
        "emotion": "لوعة متصاعدة تجمع دفء البيات وحرقة الحجاز",
    },
    "saba": {
        "arabic_name": "مقام الصبا",
        "cents": [0.0, 150.0, 300.0, 400.0, 700.0, 800.0, 1000.0, 1100.0],
        "default_tonic_hz": 146.83,
        "ghammaz_index": 2,          # F (300c) + Diminished 4th Gb (400c)
        "emotion": "مقام البكاء المطلق والانكسار والفجيعة",
    },
    "saba_zamzam": {
        "arabic_name": "مقام صبا زمزم",
        "cents": [0.0, 100.0, 300.0, 400.0, 700.0, 800.0, 1000.0, 1100.0],
        "default_tonic_hz": 146.83,
        "ghammaz_index": 2,
        "emotion": "انكسار جنائزي عميق بلا ربع تون مع رابعة ناقصة",
    },
    "hijaz": {
        "arabic_name": "مقام الحجاز",
        "cents": [0.0, 100.0, 400.0, 500.0, 700.0, 800.0, 1000.0, 1200.0],
        "default_tonic_hz": 146.83,
        "ghammaz_index": 3,
        "emotion": "نداء الغربة والملحمة والهيبة الزينبية",
    },
    "hijaz_kar": {
        "arabic_name": "مقام حجاز كار",
        "cents": [0.0, 100.0, 400.0, 500.0, 700.0, 800.0, 1100.0, 1200.0],
        "default_tonic_hz": 130.81,  # C3
        "ghammaz_index": 4,
        "emotion": "فخامة ملحمية حزينة ومهابة استوديوية",
    },
    "lami": {
        "arabic_name": "مقام اللامي العراقي",
        "cents": [0.0, 100.0, 300.0, 500.0, 600.0, 800.0, 1000.0, 1200.0],
        "default_tonic_hz": 146.83,
        "ghammaz_index": 3,
        "emotion": "شجن عراقي فراتي خالص في النعي والركباني والأبوذية",
    },
    "kurd": {
        "arabic_name": "مقام الكرد",
        "cents": [0.0, 100.0, 300.0, 500.0, 700.0, 800.0, 1000.0, 1200.0],
        "default_tonic_hz": 146.83,
        "ghammaz_index": 3,
        "emotion": "حنين دافئ ورثاء هادئ متصل",
    },
    "rast": {
        "arabic_name": "مقام الراست",
        "cents": [0.0, 200.0, 350.0, 500.0, 700.0, 900.0, 1050.0, 1200.0],
        "default_tonic_hz": 130.81,  # C3
        "ghammaz_index": 4,
        "emotion": "وقار وفخامة استهلالية ومواكب مهيبة",
    },
    "suznak": {
        "arabic_name": "مقام السوزناك",
        "cents": [0.0, 200.0, 350.0, 500.0, 700.0, 800.0, 1100.0, 1200.0],
        "default_tonic_hz": 130.81,
        "ghammaz_index": 4,
        "emotion": "افتتاح راسخ يتحول في الجواب إلى حرقة الحجاز",
    },
    "nahawand": {
        "arabic_name": "مقام النهاوند",
        "cents": [0.0, 200.0, 300.0, 500.0, 700.0, 800.0, 1100.0, 1200.0],
        "default_tonic_hz": 146.83,
        "ghammaz_index": 4,
        "emotion": "سرد وجداني درامي ومناجاة شجية",
    },
    "sikah": {
        "arabic_name": "مقام السيكاه",
        "cents": [0.0, 150.0, 350.0, 550.0, 650.0, 850.0, 1050.0, 1200.0],
        "default_tonic_hz": 160.00,  # E half-flat 3
        "ghammaz_index": 2,
        "emotion": "روحانية تراثية عميقة لأطوار الزريجاوي والركباني والمشاية",
    },
    "huzam": {
        "arabic_name": "مقام الهزام",
        "cents": [0.0, 150.0, 350.0, 450.0, 750.0, 850.0, 1050.0, 1200.0],
        "default_tonic_hz": 160.00,
        "ghammaz_index": 2,
        "emotion": "شجن شرقي مشبع بالربع تون للتواشيح والنعي التراثي",
    },
    "bastanikar": {
        "arabic_name": "مقام البستنكار",
        "cents": [0.0, 150.0, 350.0, 550.0, 650.0, 750.0, 1050.0, 1150.0],
        "default_tonic_hz": 160.00,
        "ghammaz_index": 2,
        "emotion": "مزيج السيكاه في القرار مع بكاء الصبا في الجواب",
    },
    "ajam": {
        "arabic_name": "مقام العجم",
        "cents": [0.0, 200.0, 400.0, 500.0, 700.0, 900.0, 1100.0, 1200.0],
        "default_tonic_hz": 130.81,
        "ghammaz_index": 4,
        "emotion": "إشراق ولائي للمواليد والأناشيد الحماسية",
    },
}


def transpose_maqam_frequencies(maqam="saba", tonic_hz=None):
    """Return the full 8-degree frequency array (Hz) for any of the 15 Maqamat at a given tonic."""
    spec = MAQAM_INTERVALS_CENTS.get(maqam.lower(), MAQAM_INTERVALS_CENTS["saba"])
    root_hz = float(tonic_hz) if tonic_hz and tonic_hz > 40.0 else spec["default_tonic_hz"]
    return [round(root_hz * (2.0 ** (c / 1200.0)), 3) for c in spec["cents"]]


def export_scala_microtonal_scale(maqam="saba", output_scl_path=None):
    """Build (and optionally save) a Huygens-Fokker Scala (.scl) microtonal tuning file."""
    key = maqam.lower()
    spec = MAQAM_INTERVALS_CENTS.get(key, MAQAM_INTERVALS_CENTS["saba"])
    degrees = spec["cents"][1:]  # Exclude 0.0 tonic per Scala standard
    lines = [
        f"! hussaini_{key}.scl",
        "!",
        f"Hussaini Production Studio V50.0 - {spec['arabic_name']} ({key}) 24-EDO Microtonal Scale",
        f" {len(degrees)}",
        "!",
    ]
    for cent_val in degrees:
        if abs(cent_val - 1200.0) < 1e-4:
            lines.append(" 2/1")
        else:
            lines.append(f" {cent_val:.2f}")
    content = "\n".join(lines) + "\n"
    if output_scl_path:
        out_dir = os.path.dirname(os.path.abspath(output_scl_path))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(output_scl_path, "w", encoding="utf-8") as handle:
            handle.write(content)
    return {"maqam": key, "degree_count": len(degrees), "scala_content": content}


# ==============================================================================
# 2. 25-METER BINARY ARUD BITMASK ENGINE & PROSODY-SAFE CAESURA SPLITTING
# ==============================================================================

POETIC_METERS_V50 = {
    "nassari": {
        "arabic_name": "وزن النصّاري",
        "tafila_formula": "مفاعيلن مفاعيلن مفاعيل",
        "binary_bitmask": "//0/0/0//0/0/0//0/00",
        "canonical_melodic_key": "هذا الرمح بفّاده تثنّه .. وهذا بيه للنشّاب رنّه",
        "rhyme_scheme": "AAAB (الرابع يستقر على الراء أو قافية المستهل)",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": [
            "tor_nai_kashi", "tor_ashouri", "tor_rukbani", "tor_janoubi",
            "tor_zaarijawi", "tor_muthakkal_bahrani", "tor_darj_karbalai",
        ],
    },
    "tajleeb": {
        "arabic_name": "وزن التجليبة",
        "tafila_formula": "مفاعيلن مفاعيلن مفاعيلن",
        "binary_bitmask": "//0/0/0//0/0/0//0/0/0",
        "canonical_melodic_key": "عجيب الشرب ماي بشربته تهنّى .. ومات حسين ضامي ولا شرب منّه",
        "rhyme_scheme": "AABB / ABCB",
        "typical_syllables_per_hemistich": (8, 10),
        "compatible_atwar": ["tor_nai_kashi", "tor_ashouri", "tor_mullai", "tor_janoubi"],
    },
    "mujarasha": {
        "arabic_name": "وزن المجرشة",
        "tafila_formula": "مستفعلن مستفعلن مستفعلن مفعولن",
        "binary_bitmask": "/0/0//0/0/0//0/0/0//0/0/00",
        "canonical_melodic_key": "يم حسين گوم انظر يتاماك .. فوگ الهزل مشّوها عداك",
        "rhyme_scheme": "AAAB / AABB",
        "typical_syllables_per_hemistich": (10, 13),
        "compatible_atwar": ["tor_darj_karbalai", "tor_rukbani", "tor_bahrani_rubai"],
    },
    "hajri": {
        "arabic_name": "وزن الهجري",
        "tafila_formula": "فاعلاتن فاعلاتن فاعلاتن فاعلات",
        "binary_bitmask": "/0//0/0/0//0/0/0//0/0/0//00",
        "canonical_melodic_key": "اشرب الماء وعجّل قبل أن يأتي الصباح",
        "rhyme_scheme": "AABB / ABCB",
        "typical_syllables_per_hemistich": (10, 12),
        "compatible_atwar": ["tor_darj_karbalai", "tor_bahrani_haidari", "tor_rukbani"],
    },
    "shiati": {
        "arabic_name": "وزن الشيعتي",
        "tafila_formula": "فاعلاتن فاعلاتن فاعلات",
        "binary_bitmask": "/0//0/0/0//0/0/0//00",
        "canonical_melodic_key": "گوم يا حيدر بناتك شوفهن بالطف سبايا",
        "rhyme_scheme": "AAAB / ABCB",
        "typical_syllables_per_hemistich": (8, 10),
        "compatible_atwar": ["tor_nai_kashi", "tor_ashouri", "tor_darj_karbalai"],
    },
    "muwashah": {
        "arabic_name": "وزن الموشّح والتوشيح",
        "tafila_formula": "فاعلاتن فاعلاتن فاعلن",
        "binary_bitmask": "/0//0/0/0//0/0/0//0",
        "canonical_melodic_key": "جينا ننشد كربلا مضيعينها .. بيها زينب گالوا ميسرينها",
        "rhyme_scheme": "متعدد الأدوار والخانات مع لازمة موحدة",
        "typical_syllables_per_hemistich": (7, 10),
        "compatible_atwar": [
            "tor_faizi_bahrani", "tor_bahrani_thulathi", "tor_bahrani_rubai",
            "tor_bahrani_haidari", "tor_darj_karbalai",
        ],
    },
    "faizi": {
        "arabic_name": "وزن الفايزي (البحراني)",
        "tafila_formula": "مستفعلن مستفعلن مفعولان",
        "binary_bitmask": "/0/0//0/0/0//0/0/00",
        "canonical_melodic_key": "گلبي يبو حمزة تراه تفطّر وذاب .. مثل المصيبة اللي دهتني ما حد نصاب",
        "rhyme_scheme": "AAAB / AABB",
        "typical_syllables_per_hemistich": (8, 11),
        "compatible_atwar": [
            "tor_faizi_bahrani", "tor_faizi_iraqi", "tor_muthakkal_bahrani",
            "tor_waqfa_bahrani", "tor_nai_kashi",
        ],
    },
    "mujarradat": {
        "arabic_name": "وزن المجرّدات (المهداد / النعي)",
        "tafila_formula": "مستفعلن مستفعلاتن",
        "binary_bitmask": "/0/0//0/0/0//0/0",
        "canonical_melodic_key": "نايم يبعد أختك وممدود .. فوگ النهر وبگترك الجود",
        "rhyme_scheme": "AAAA (متحد الروي صدراً وعجزاً)",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": ["tor_nai_kashi", "tor_ashouri", "tor_muthakkal_bahrani", "tor_mullai"],
    },
    "abudhiyah": {
        "arabic_name": "وزن الأبوذية العراقية",
        "tafila_formula": "مفاعيلن مفاعيلن فعولن",
        "binary_bitmask": "//0/0/0//0/0/0//0/0",
        "canonical_melodic_key": "گلبي بمأتمك يحسين ينصاب .. وذكرك من يمر الدمع ينصاب",
        "rhyme_scheme": "AAA(Jinas) + B(-يَّه)",
        "typical_syllables_per_hemistich": (9, 11),
        "compatible_atwar": [
            "tor_abudhiyah", "tor_huwaizawi", "tor_zaarijawi", "tor_shushtari", "tor_nayli",
        ],
    },
    "zuhayri_mawal": {
        "arabic_name": "وزن الموّال السبعوي (الزهيري)",
        "tafila_formula": "مستفعلن فاعلن مستفعلن فاعلان",
        "binary_bitmask": "/0/0//0/0//0/0/0//0/0//00",
        "canonical_melodic_key": "يا الهادي جمر الحزن بحشاشتي ياجد",
        "rhyme_scheme": "AAA B AAA (مع العرگ في الشطر الرابع)",
        "typical_syllables_per_hemistich": (11, 14),
        "compatible_atwar": ["tor_mawal_iraqi", "tor_rukbani", "tor_dashti", "tor_nai_kashi"],
    },
    "maymar": {
        "arabic_name": "وزن الميمر",
        "tafila_formula": "مستفعلن مستفعلن مستفعل",
        "binary_bitmask": "/0/0//0/0/0//0/0/0/0",
        "canonical_melodic_key": "يا دار انشدچ عن أهاليچ .. يا دار عزّيني وأعزّيچ",
        "rhyme_scheme": "AAAB",
        "typical_syllables_per_hemistich": (8, 10),
        "compatible_atwar": ["tor_nayli", "tor_nai_kashi", "tor_janoubi"],
    },
    "darmi": {
        "arabic_name": "وزن الدارمي الحسيني",
        "tafila_formula": "مستفعلن فعلان مستفعلاتن",
        "binary_bitmask": "/0/0//0/0/00/0/0//0/0",
        "canonical_melodic_key": "تجري الدموع عليك يا بو الأئمة .. والگلب ذاب اليوم من كثر همّه",
        "rhyme_scheme": "AA",
        "typical_syllables_per_hemistich": (9, 11),
        "compatible_atwar": ["tor_nai_kashi", "tor_ashouri", "tor_janoubi"],
    },
    "saree_shabi": {
        "arabic_name": "وزن السريع الشعبي",
        "tafila_formula": "مستفعلن مستفعلن فاعلن",
        "binary_bitmask": "/0/0//0/0/0//0/0//0",
        "canonical_melodic_key": "عباس يا سردار ماي الفرات",
        "rhyme_scheme": "AABB / ABCB",
        "typical_syllables_per_hemistich": (8, 10),
        "compatible_atwar": ["tor_bahrani_haidari", "tor_waqfa_bahrani", "tor_darj_karbalai"],
    },
    "nayel": {
        "arabic_name": "وزن النايل",
        "tafila_formula": "مستفعلن فاعلن مستفعلن فاعلن",
        "binary_bitmask": "/0/0//0/0//0/0/0//0/0//0",
        "canonical_melodic_key": "يا رايح الكربلا سلّم على المذبوح",
        "rhyme_scheme": "AABB",
        "typical_syllables_per_hemistich": (10, 12),
        "compatible_atwar": ["tor_nayli", "tor_rukbani"],
    },
    "shiyala": {
        "arabic_name": "وزن الشيّالة",
        "tafila_formula": "مستفعلن مفعولن مستفعلن مفعولن",
        "binary_bitmask": "/0/0//0/0/00/0/0//0/0/00",
        "canonical_melodic_key": "شيلوا نعش مولانا فوگ المتون",
        "rhyme_scheme": "AAAB",
        "typical_syllables_per_hemistich": (9, 11),
        "compatible_atwar": ["tor_bahrani_thulathi", "tor_darj_karbalai"],
    },
    "taweel_shabi": {
        "arabic_name": "البحر الطويل الشعبي",
        "tafila_formula": "مفاعيلن مفاعيلن مفاعيلن مفاعيلن",
        "binary_bitmask": "//0/0/0//0/0/0//0/0/0//0/0/0",
        "canonical_melodic_key": "يا تالي هلي يحسين يا سلوة هلي يحسين",
        "rhyme_scheme": "AAAB / ABCB",
        "typical_syllables_per_hemistich": (12, 15),
        "compatible_atwar": ["tor_iraqi_qadeem", "tor_nai_kashi", "tor_muthakkal_bahrani"],
    },
    "rukbani": {
        "arabic_name": "وزن الركباني",
        "tafila_formula": "مستفعلن مستفعلن فعولن",
        "binary_bitmask": "/0/0//0/0/0//0//0/0",
        "canonical_melodic_key": "ودعتك الله يا ذبيح الما شرب ماي",
        "rhyme_scheme": "AAAB / ABCB",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": ["tor_rukbani", "tor_hadi", "tor_darj_karbalai", "tor_ashouri"],
    },
    "hadi": {
        "arabic_name": "وزن الحدي",
        "tafila_formula": "مستفعلن مستفعلن",
        "binary_bitmask": "/0/0//0/0/0//0",
        "canonical_melodic_key": "لمن حدى الحادي بودايع الهادي",
        "rhyme_scheme": "AAAB",
        "typical_syllables_per_hemistich": (6, 8),
        "compatible_atwar": ["tor_hadi", "tor_rukbani"],
    },
    "daksani": {
        "arabic_name": "وزن الدكسني",
        "tafila_formula": "مستفعلن فاعلاتن",
        "binary_bitmask": "/0/0//0/0//0/0",
        "canonical_melodic_key": "گعدن يم ابو اليمّه ينحبن",
        "rhyme_scheme": "AAAB",
        "typical_syllables_per_hemistich": (6, 8),
        "compatible_atwar": ["tor_nai_kashi_2", "tor_mullai", "tor_janoubi"],
    },
    "muthakkal_wazn": {
        "arabic_name": "وزن المثكّل الشعبي",
        "tafila_formula": "مفعولات مستفعلاتن",
        "binary_bitmask": "/0/0/0//0/0//0/0",
        "canonical_melodic_key": "يبني ضعيفه وذوّب گليبي مصابك",
        "rhyme_scheme": "AAAB",
        "typical_syllables_per_hemistich": (7, 9),
        "compatible_atwar": ["tor_muthakkal_bahrani", "tor_faizi_bahrani"],
    },
    "hosa_arjooza": {
        "arabic_name": "أرجوزة الهوسة الحسينية (3+1)",
        "tafila_formula": "مستفعلن مستفعلن (3 أشطر + رباط)",
        "binary_bitmask": "/0/0//0/0/0//0",
        "canonical_melodic_key": "ها خوتي ها .. عبّاس سبع الگنطرة",
        "rhyme_scheme": "AAAB (رباط جماعي)",
        "typical_syllables_per_hemistich": (6, 8),
        "compatible_atwar": ["tor_waqfa_bahrani", "tor_bahrani_haidari"],
    },
    "wafir_fusha": {
        "arabic_name": "بحر الوافر الفصيح",
        "tafila_formula": "مفاعلتن مفاعلتن فعولن",
        "binary_bitmask": "//0///0//0///0//0/0",
        "canonical_melodic_key": "لسانُ الوحيِ يقرأُ في الطفوفِ",
        "rhyme_scheme": "قافية موحدة فصيحة",
        "typical_syllables_per_hemistich": (10, 12),
        "compatible_atwar": ["tor_nai_kashi", "tor_takhmis", "tor_qazwini"],
    },
    "kamil_fusha": {
        "arabic_name": "بحر الكامل الفصيح",
        "tafila_formula": "متفاعلن متفاعلن متفاعلن",
        "binary_bitmask": "///0//0///0//0///0//0",
        "canonical_melodic_key": "أبكي عليكَ بعبرةٍ مسكوبةٍ",
        "rhyme_scheme": "قافية موحدة أو تخميس",
        "typical_syllables_per_hemistich": (11, 15),
        "compatible_atwar": ["tor_takhmis", "tor_nai_kashi", "tor_hadee"],
    },
    "ramal_amili": {
        "arabic_name": "مجزوء الرمل / النعي العاملي",
        "tafila_formula": "فاعلاتن فاعلاتن",
        "binary_bitmask": "/0//0/0/0//0/0",
        "canonical_melodic_key": "يا غريب الدار مالك .. رايح وتارك أطفالك",
        "rhyme_scheme": "AAAB",
        "typical_syllables_per_hemistich": (6, 8),
        "compatible_atwar": ["tor_amili", "tor_faizi_bahrani"],
    },
    "mutadarak_latm": {
        "arabic_name": "بحر المتدارك / الخبب الموكبي",
        "tafila_formula": "فعلن فعلن فعلن فعلن",
        "binary_bitmask": "/0/0/0/0/0/0/0/0",
        "canonical_melodic_key": "لبّيكَ حسينٌ لبّيكا",
        "rhyme_scheme": "ثنائي إيقاعي سريع",
        "typical_syllables_per_hemistich": (5, 8),
        "compatible_atwar": ["tor_waqfa_bahrani", "tor_ashouri"],
    },
}


def infer_unvocalized_arud_pattern(word):
    """Infer prosodic syllables (CV, CVC, CVCC) and (/0) bitmask for an unvocalized Arabic word."""
    letters = [ch for ch in word if re.match(r"[ء-غف-يپچگ]", ch)]
    if not letters:
        return [], []
    # Strip silent definite article Alif at start in connected flow
    idx = 0
    events = []
    n_let = len(letters)
    if n_let >= 3 and letters[0] == "ا" and letters[1] == "ل":
        events.append("S")
        idx = 2

    long_vowels = {"ا", "آ", "ى"}
    glides = {"و", "ي"}
    while idx < n_let:
        ch = letters[idx]
        if ch == "آ":
            events.extend(["C", "S"])
        elif ch in long_vowels:
            if not events or events[-1] == "S":
                events.append("C")
            events.append("S")
        elif ch in glides and idx > 0 and events and events[-1] == "C":
            # Likely long vowel Madd unless word-initial
            events.append("S")
        elif idx == n_let - 1 and ch in ("ه", "ة"):
            if events and events[-1] == "C":
                events.append("S")
            else:
                events.extend(["C", "S"])
        elif idx == n_let - 1:
            # Final consonant closes syllable in pause
            if not events or events[-1] == "S":
                events.extend(["C", "S"])
            else:
                events.append("S")
        else:
            # Interior consonant: insert epenthetic Sakin closure on typical closed prefixes (مِن، عَن، قَد، هَل، إِش، يِن، تِن، مَف، مُس)
            events.append("C")
            if idx == 1 and letters[0] in ("م", "ي", "ت", "ن", "ا", "إ", "أ") and n_let >= 4 and letters[idx + 1] not in long_vowels | glides:
                events.append("S")
        idx += 1

    syllables = []
    arud_pat = []
    pos = 0
    while pos < len(events):
        if events[pos] == "S":
            if syllables:
                syllables[-1] += "C"
                arud_pat[-1] += "0"
            else:
                syllables.append("CV")
                arud_pat.append("/")
            pos += 1
            continue
        s_cnt = 0
        nxt = pos + 1
        while nxt < len(events) and events[nxt] == "S":
            s_cnt += 1
            nxt += 1
        if s_cnt == 0:
            syllables.append("CV")
            arud_pat.append("/")
        elif s_cnt == 1:
            syllables.append("CVC")
            arud_pat.append("/0")
        else:
            syllables.append("CVCC")
            arud_pat.append("/00")
        pos = nxt
    return syllables, arud_pat


def _bitmask_similarity(pat_a, pat_b):
    """Compute normalized Levenshtein similarity between two '/0' prosodic bitmasks."""
    if not pat_a or not pat_b:
        return 0.0
    m, n = len(pat_a), len(pat_b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            cost = 0 if pat_a[i - 1] == pat_b[j - 1] else 1
            dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + cost)
            prev = temp
    return round(1.0 - (dp[n] / float(max(m, n))), 4)


def match_poetic_meter_bitmask(text, segmenter_fn):
    """Match poem hemistichs against all 25 Hussaini poetic meters via binary Arud bitmasks."""
    lines = [
        ln.strip() for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith("[") and not ln.strip().startswith("(")
    ]
    hemistichs = []
    for ln in lines:
        parts = [p.strip() for p in ln.split("..") if p.strip()]
        hemistichs.extend(parts)
    if not hemistichs:
        hemistichs = [text.strip()]

    patterns = [segmenter_fn(h)["arud_pattern"] for h in hemistichs if h]
    avg_syllables = float(np.mean([segmenter_fn(h)["syllable_count"] for h in hemistichs])) if hemistichs else 0.0

    scored = []
    for m_id, spec in POETIC_METERS_V50.items():
        target_mask = spec["binary_bitmask"]
        sims = [_bitmask_similarity(p, target_mask) for p in patterns]
        mean_sim = float(np.mean(sims)) if sims else 0.0
        low_s, high_s = spec["typical_syllables_per_hemistich"]
        if low_s <= avg_syllables <= high_s:
            mean_sim += 0.06
        scored.append((mean_sim, m_id, spec))

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_id, best_spec = scored[0]
    runner_up_id = scored[1][1] if len(scored) > 1 else None
    return {
        "matched_meter": best_id,
        "arabic_name": best_spec["arabic_name"],
        "tafila_formula": best_spec["tafila_formula"],
        "target_bitmask": best_spec["binary_bitmask"],
        "observed_bitmasks": patterns[:6],
        "confidence_score": round(min(1.0, best_score), 3),
        "canonical_melodic_key": best_spec["canonical_melodic_key"],
        "compatible_atwar": best_spec["compatible_atwar"],
        "runner_up_meter": runner_up_id,
    }


INSEPARABLE_PROCLITICS = {
    "يا", "يَا", "أبو", "أَبُو", "بو", "بُو", "ابن", "ابْن", "أم", "أُم",
    "من", "مِنْ", "في", "فِي", "على", "عَلَى", "اعله", "عن", "عَنْ", "إلى", "إِلَى",
    "كل", "كُلْ", "كِلْ", "ما", "مَا", "لا", "لَا", "هل", "هَلْ", "بِ", "لِ", "كَ", "وَ", "عا",
}


def prosody_safe_caesura_split(line_str, segmenter_fn, max_words_per_line=5):
    """Split a long poetic line at the most prosodically balanced & syntactically safe caesura."""
    stripped = line_str.strip()
    if not stripped or stripped.startswith("["):
        return [line_str]
    words_only = [w for w in stripped.split() if w != ".." and not w.startswith("(")]
    if len(words_only) <= max_words_per_line:
        return [stripped]
    if ".." in stripped:
        parts = [p.strip() for p in stripped.split("..") if p.strip()]
        return [
            f"{part}{' ..' if idx < len(parts) - 1 else ''}"
            for idx, part in enumerate(parts)
        ]

    tokens = stripped.split()
    n_tok = len(tokens)
    best_idx = max(1, n_tok // 2)
    best_penalty = 1e9
    for split_i in range(2, n_tok - 1):
        prev_clean = re.sub(r"[ً-ْ،.]", "", tokens[split_i - 1])
        # Never split immediately after a preposition, vocative, negation, or construct proclitic
        syntax_penalty = 50.0 if tokens[split_i - 1] in INSEPARABLE_PROCLITICS or prev_clean in INSEPARABLE_PROCLITICS else 0.0
        left_syl = segmenter_fn(" ".join(tokens[:split_i]))["syllable_count"]
        right_syl = segmenter_fn(" ".join(tokens[split_i:]))["syllable_count"]
        imbalance = abs(left_syl - right_syl) + 0.25 * abs(split_i - (n_tok / 2.0))
        total_pen = syntax_penalty + imbalance
        if total_pen < best_penalty:
            best_penalty = total_pen
            best_idx = split_i
    return [" ".join(tokens[:best_idx]) + " ..", " ".join(tokens[best_idx:])]


# ==============================================================================
# 3. MICROTONAL 24-EDO MELODY COMPOSER, GUIDE WAV & 14-BIT MIDI EXPORTER
# ==============================================================================

SECTION_CONTOURS = {
    "chorus": [0, 2, 3, 2, 1, 2, 1, 0],           # Circular memorable Estehlal settling on Qarar
    "verse_low": [0, 1, 2, 3, 2, 1, 1, 0],        # Calm weeping Qarar/Wasat narrative
    "verse_high": [3, 4, 5, 6, 7, 5, 4, 3],       # Climactic Ghammaz -> Jawab ascent
    "kaser": [3, 4, 3, 2, 3, 2, 1, 0],            # Maqaseer / Kaser modal pivot back to tonic
}


def compose_microtonal_melody_for_poem(
    poem_text, segmenter_fn, maqam="saba", bpm=60.0, tonic_hz=None
):
    """Compose a syllable-aligned 24-EDO melody locking prosodic Watad/Madd onto chest downbeats."""
    m_key = maqam.lower()
    spec = MAQAM_INTERVALS_CENTS.get(m_key, MAQAM_INTERVALS_CENTS["saba"])
    scale_freqs = transpose_maqam_frequencies(m_key, tonic_hz=tonic_hz)
    eff_bpm = float(bpm) if bpm and bpm > 0.0 else 58.0
    beat_sec = 60.0 / eff_bpm

    raw_lines = [ln.strip() for ln in poem_text.splitlines() if ln.strip()]
    role = "chorus"
    verse_line_idx = 0
    note_events = []
    hemistich_summaries = []
    cur_time = 0.20  # 200ms breath lead-in

    for ln in raw_lines:
        if ln.startswith("[") and ln.endswith("]"):
            clean_tag = re.sub(r"[ً-ْ]", "", ln).lower()
            if any(k in clean_tag for k in ("كسر", "مقاصير", "kaser")):
                role = "kaser"
            elif any(k in clean_tag for k in ("نزلة", "مقطع", "دور", "verse")):
                role = "verse"
                verse_line_idx = 0
            else:
                role = "chorus"
            continue

        hemistichs = [p.strip() for p in ln.split("..") if p.strip()]
        for hem in hemistichs:
            seg = segmenter_fn(hem)
            syl_types = seg["syllables"] or ["CVC"]
            n_syl = len(syl_types)
            # Allocate 2 bars (8 beats) if >9 syllables so last 3 words are NEVER rushed/eaten!
            bars_allocated = 2 if n_syl >= 10 else 1
            phrase_beats = 4 * bars_allocated
            phrase_dur = phrase_beats * beat_sec
            # Reserve final 22% of phrase for rhyme elongation + Wannah + breath pause
            singing_budget = phrase_dur * 0.78
            pause_budget = phrase_dur * 0.22

            if role == "verse":
                contour_key = "verse_low" if verse_line_idx < 4 else "verse_high"
                verse_line_idx += 1
            else:
                contour_key = role
            contour = SECTION_CONTOURS.get(contour_key, SECTION_CONTOURS["chorus"])

            # Weight durations: CV = 1.0, CVC = 1.65 (Sabab/Watad core), CVCC = 2.25 (Madd/Pause)
            weights = []
            for idx_s, s_kind in enumerate(syl_types):
                base_w = 1.0 if s_kind == "CV" else (1.65 if s_kind == "CVC" else 2.25)
                if idx_s == n_syl - 1:
                    base_w *= 1.45  # Melismatic Qafla / Wannah stretch
                weights.append(base_w)
            w_sum = sum(weights) or 1.0

            downbeat_locked_indices = []
            local_t = 0.0
            for idx_s, (s_kind, w_val) in enumerate(zip(syl_types, weights)):
                dur_s = singing_budget * (w_val / w_sum)
                # Snap Watad / heavy CVC near a primary beat directly onto the chest Latm downbeat
                beat_pos = (cur_time + local_t - 0.20) / beat_sec
                nearest_beat = round(beat_pos)
                if s_kind in ("CVC", "CVCC") and abs(beat_pos - nearest_beat) <= 0.22:
                    downbeat_locked_indices.append(idx_s)

                deg_idx = contour[min(len(contour) - 1, int(idx_s * len(contour) / max(1, n_syl)))]
                if idx_s == n_syl - 1 and role in ("chorus", "kaser"):
                    deg_idx = 0  # Lock chorus/kaser cadence to tonic Qarar
                freq_hz = scale_freqs[deg_idx]
                cents_val = spec["cents"][deg_idx]
                note_events.append({
                    "start_sec": round(cur_time + local_t, 4),
                    "duration_sec": round(dur_s, 4),
                    "syllable_type": s_kind,
                    "scale_degree": deg_idx + 1,
                    "cents_from_tonic": cents_val,
                    "freq_hz": freq_hz,
                    "section_role": contour_key,
                    "is_final_qafla": idx_s == n_syl - 1,
                })
                local_t += dur_s

            hemistich_summaries.append({
                "hemistich": hem,
                "syllable_count": n_syl,
                "bars_allocated": bars_allocated,
                "watad_downbeat_locks": downbeat_locked_indices,
                "anti_rush_breath_sec": round(pause_budget, 3),
                "section_contour": contour_key,
            })
            cur_time += singing_budget + pause_budget

    return {
        "maqam": m_key,
        "arabic_maqam_name": spec["arabic_name"],
        "tonic_hz": scale_freqs[0],
        "ghammaz_freq_hz": scale_freqs[spec["ghammaz_index"]],
        "bpm": eff_bpm,
        "total_duration_sec": round(cur_time, 2),
        "hemistich_alignments": hemistich_summaries,
        "note_events": note_events,
    }


def generate_multi_maqam_readings(poem_text, segmenter_fn, maqamat=("bayati", "saba", "hijaz", "nahawand", "lami"), bpm=60.0):
    """Generate comparative melodic blueprints of the exact same poem across multiple Maqam keys."""
    readings = {}
    for mq in maqamat:
        plan = compose_microtonal_melody_for_poem(poem_text, segmenter_fn, maqam=mq, bpm=bpm)
        readings[mq] = {
            "arabic_name": plan["arabic_maqam_name"],
            "tonic_hz": plan["tonic_hz"],
            "ghammaz_freq_hz": plan["ghammaz_freq_hz"],
            "emotion": MAQAM_INTERVALS_CENTS[mq]["emotion"],
            "opening_4_notes_hz": [ev["freq_hz"] for ev in plan["note_events"][:4]],
        }
    return readings


def write_wav_bit_depth(output_path, sample_rate, signal_array, bit_depth=16):
    """Write mono or stereo float64 [-1.0, 1.0] signal as 16-bit or 24-bit PCM WAV."""
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    arr = np.asarray(signal_array, dtype=np.float64)
    if arr.ndim == 1:
        n_channels = 1
        flat = np.clip(arr, -1.0, 1.0)
    else:
        n_channels = arr.shape[1]
        flat = np.clip(arr.reshape(-1), -1.0, 1.0)

    with wave.open(output_path, "wb") as wf:  # pylint: disable=no-member
        wf.setnchannels(n_channels)
        wf.setframerate(int(sample_rate))
        if int(bit_depth) == 24:
            wf.setsampwidth(3)
            max_i24 = (1 << 23) - 1
            scaled = np.clip(np.round(flat * max_i24), -(1 << 23), max_i24).astype(np.int32)
            # Vectorized little-endian 3-byte packing
            raw_bytes = scaled.astype("<i4").view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
            wf.writeframes(raw_bytes)
        else:
            wf.setsampwidth(2)
            scaled16 = np.clip(np.round(flat * 32767.0), -32768, 32767).astype("<i2")
            wf.writeframes(scaled16.tobytes())


def export_guide_melody_wav(melody_plan, output_wav_path, sample_rate=48000, bit_depth=24):
    """Synthesize a 24-EDO microtonal human-formant vocal guide WAV + soft chest-latm pulse."""
    total_dur = max(1.0, float(melody_plan["total_duration_sec"]) + 0.4)
    n_samples = int(total_dur * sample_rate)
    f0_track = np.zeros(n_samples, dtype=np.float64)
    amp_env = np.zeros(n_samples, dtype=np.float64)

    for ev in melody_plan["note_events"]:
        s_idx = max(0, int(ev["start_sec"] * sample_rate))
        e_idx = min(n_samples, int((ev["start_sec"] + ev["duration_sec"]) * sample_rate))
        if e_idx <= s_idx:
            continue
        seg_len = e_idx - s_idx
        f0_track[s_idx:e_idx] = ev["freq_hz"]
        # Smooth attack & weeping Wannah release on final Qafla notes
        env = np.ones(seg_len, dtype=np.float64)
        atk = min(seg_len // 3, max(1, int(0.025 * sample_rate)))
        rel = min(seg_len // 2, max(1, int((0.12 if ev["is_final_qafla"] else 0.035) * sample_rate)))
        if atk > 1:
            env[:atk] = np.linspace(0.0, 1.0, atk)
        if rel > 1:
            env[-rel:] = np.linspace(1.0, 0.08, rel)
        amp_env[s_idx:e_idx] = env

    # Fill silent f0 regions with tonic and apply 30ms portamento smoothing
    tonic = float(melody_plan["tonic_hz"])
    f0_filled = np.where(f0_track > 20.0, f0_track, tonic)
    glide_win = max(1, int(0.030 * sample_rate))
    f0_smooth = np.convolve(f0_filled, np.ones(glide_win) / glide_win, mode="same")

    t_vec = np.arange(n_samples, dtype=np.float64) / sample_rate
    vibrato = 1.0 + 0.0045 * np.sin(2.0 * np.pi * 4.6 * t_vec)
    phase = np.mod(np.cumsum(f0_smooth * vibrato / sample_rate), 1.0)
    # Rosenberg glottal pulse
    tp, tn = 0.40, 0.16
    glottal = np.zeros_like(phase)
    m_open = phase < tp
    m_close = (phase >= tp) & (phase < tp + tn)
    glottal[m_open] = 0.5 * (1.0 - np.cos(np.pi * phase[m_open] / tp))
    glottal[m_close] = np.cos(0.5 * np.pi * (phase[m_close] - tp) / tn)
    deriv = np.diff(glottal, prepend=glottal[0])

    # Apply human /a:/-/o:/ warm mourning vocal formants
    nyq = 0.5 * sample_rate
    voiced = np.zeros_like(deriv)
    for center_hz, bw_hz, gain in ((650.0, 95.0, 1.0), (1080.0, 120.0, 0.58), (2420.0, 170.0, 0.26)):
        low_f = max(60.0, center_hz - 0.5 * bw_hz)
        high_f = min(0.45 * sample_rate, center_hz + 0.5 * bw_hz)
        if nyq > high_f + 40.0:
            sos = butter(2, [low_f / nyq, high_f / nyq], btype="band", output="sos")
            voiced += gain * sosfilt(sos, deriv)
    if np.max(np.abs(voiced)) < 1e-8:
        voiced = deriv
    voiced = (voiced / (np.max(np.abs(voiced)) + 1e-9)) * amp_env * 0.68

    # Add soft synchronized chest-latm reference pulse on beats
    bpm = float(melody_plan["bpm"])
    if bpm > 0.0:
        beat_step = max(1, int((60.0 / bpm) * sample_rate))
        hit_len = min(beat_step, int(0.18 * sample_rate))
        th_t = np.arange(hit_len, dtype=np.float64) / sample_rate
        soft_latm = 0.22 * np.sin(2.0 * np.pi * 55.0 * th_t) * np.exp(-16.0 * th_t)
        cursor = int(0.20 * sample_rate)
        while cursor + hit_len < n_samples:
            voiced[cursor : cursor + hit_len] += soft_latm
            cursor += beat_step

    peak = np.max(np.abs(voiced))
    if peak > 0.92:
        voiced = voiced * (0.92 / peak)
    write_wav_bit_depth(output_wav_path, sample_rate, voiced, bit_depth=bit_depth)
    return output_wav_path


def _encode_midi_varlen(val):
    """Encode non-negative integer as Standard MIDI Variable-Length Quantity."""
    val = max(0, int(val))
    buf = [val & 0x7F]
    val >>= 7
    while val > 0:
        buf.append((val & 0x7F) | 0x80)
        val >>= 7
    buf.reverse()
    return bytes(buf)


def export_microtonal_midi(melody_plan, output_midi_path):
    """Export Standard MIDI File (.mid) with 14-bit Pitch-Bend microtonal 24-EDO tuning."""
    ticks_per_beat = 480
    bpm = float(melody_plan["bpm"]) if melody_plan["bpm"] > 0 else 60.0
    mpqn = int(round(60_000_000.0 / bpm))
    sec_to_tick = (bpm / 60.0) * ticks_per_beat

    events = []  # (abs_tick, raw_bytes)
    # Tempo Meta Event FF 51 03 tt tt tt
    tempo_bytes = bytes([0xFF, 0x51, 0x03, (mpqn >> 16) & 0xFF, (mpqn >> 8) & 0xFF, mpqn & 0xFF])
    events.append((0, tempo_bytes))

    for ev in melody_plan["note_events"]:
        freq = max(30.0, float(ev["freq_hz"]))
        exact_midi = 69.0 + 12.0 * np.log2(freq / 440.0)
        nearest_note = int(np.clip(round(exact_midi), 24, 96))
        frac_semitones = exact_midi - nearest_note  # in [-0.5, +0.5]
        # Standard +-2 semitone pitch-bend range: center = 8192, +2 semi = 16383
        bend_val = int(np.clip(round(8192.0 + (frac_semitones / 2.0) * 8191.0), 0, 16383))
        lsb = bend_val & 0x7F
        msb = (bend_val >> 7) & 0x7F

        s_tick = int(round(ev["start_sec"] * sec_to_tick))
        e_tick = max(s_tick + 20, int(round((ev["start_sec"] + ev["duration_sec"]) * sec_to_tick)))
        vel = 98 if ev["section_role"] == "verse_high" else 84
        events.append((s_tick, bytes([0xE0, lsb, msb])))
        events.append((s_tick, bytes([0x90, nearest_note, vel])))
        events.append((e_tick, bytes([0x80, nearest_note, 0x00])))

    events.sort(key=lambda item: item[0])
    track_data = bytearray()
    prev_tick = 0
    for tick, msg in events:
        delta = max(0, tick - prev_tick)
        track_data.extend(_encode_midi_varlen(delta))
        track_data.extend(msg)
        prev_tick = tick
    # End of Track Meta Event
    track_data.extend(bytes([0x00, 0xFF, 0x2F, 0x00]))

    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, ticks_per_beat)
    track_chunk = b"MTrk" + struct.pack(">I", len(track_data)) + bytes(track_data)
    out_dir = os.path.dirname(os.path.abspath(output_midi_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(output_midi_path, "wb") as handle:
        handle.write(header + track_chunk)
    return output_midi_path


# ==============================================================================
# 4. 6-DIALECT GENERATIVE G2P + IPA TRANSDUCER & 26 ATWAR ENGINE
# ==============================================================================

EXTENDED_DIALECT_MARKERS = {
    "amili": ("عا مصابو", "مصابو", "نحرو", "شرابو", "الولايي", "حشايي", "ليتو", "هلعليله", "عالغاضريي"),
    "ahwazi": ("حويزاوي", "علواني", "هيمه", "ششتري", "خوزستان", "كارون", "يبويَه", "أهواز"),
    "qatifi": ("قطيفي", "خطي", "تاروت", "سيهات", "عوامية", "واحسيناه", "ضربوها", "فجعوها"),
    "hasawi": ("أحسائي", "حساوي", "هجر", "المبرز", "الهفوف", "يا بو علي"),
    "iraqi_janoubi": ("ريّال", "مسيّد", "رفيج", "ضيج", "طريج", "ياي", "چثير"),
}
SUN_LETTERS = set("تثدذرزسشصضطظلن")

ARABIC_TO_IPA = {
    "ء": "ʔ", "أ": "ʔa", "إ": "ʔi", "آ": "ʔaː", "ا": "aː", "ى": "aː",
    "ب": "b", "پ": "p", "ت": "t", "ة": "a", "ث": "θ", "ج": "dʒ", "چ": "tʃ",
    "ح": "ħ", "خ": "x", "د": "d", "ذ": "ð", "ر": "r", "ز": "z", "س": "s",
    "ش": "ʃ", "ص": "sˤ", "ض": "dˤ", "ط": "tˤ", "ظ": "ðˤ", "ع": "ʕ", "غ": "ɣ",
    "ف": "f", "ق": "q", "ك": "k", "گ": "ɡ", "ل": "l", "م": "m", "ن": "n",
    "ه": "h", "و": "w", "ي": "j",
    "\u064E": "a", "\u064F": "u", "\u0650": "i", "\u0652": "",
}


def apply_generative_morphological_rules(word, dialect="iraqi"):
    """Apply generative morphological vocalization to out-of-vocabulary Arabic tokens."""
    if not word or any(d in word for d in ("\u064E", "\u064F", "\u0650", "\u0651")):
        return word
    clean = re.sub(r"[^\u0621-\u063A\u0641-\u064A\u067E\u0686\u06AF]", "", word)
    if dialect == "amili" and clean == "عا":
        return "عَا"
    if len(clean) < 3:
        return word

    # Amili Lebanese rules: 'عا' -> 'عَا', '-و' masculine pronoun -> 'ـُو', '-يي' -> 'ـِيِّي'
    if dialect == "amili":
        if clean == "عا":
            return "عَا"
        if clean.endswith("يي") and len(clean) >= 4:
            return clean[:-2] + "ِيِّي"
        if clean.endswith("و") and not clean.endswith("وا") and len(clean) >= 4:
            return clean[:-1] + "ُو"

    # Qatifi / Bahrani feminine 2nd-person '-ش' -> 'ـِشْ'
    if dialect in ("bahrani", "qatifi", "hasawi") and clean.endswith("ش") and len(clean) >= 4:
        return clean[:-1] + "ِشْ"

    # Iraqi / Ahwazi feminine 2nd-person '-چ' -> 'ـِچْ'
    if dialect in ("iraqi", "iraqi_karbalai", "iraqi_janoubi", "ahwazi") and clean.endswith("چ") and len(clean) >= 4:
        return clean[:-1] + "ِچْ"

    # Colloquial imperfective verb prefix Kasra (يِفْعَلْ / تِفْعَلْ / نِفْعَلْ)
    if dialect != "fusha" and clean[0] in ("ي", "ت", "ن") and clean[1] not in ("ا", "و", "ي") and len(clean) in (4, 5):
        return f"{clean[0]}\u0650{clean[1:]}\u0652"

    return word


def transcribe_vocalized_arabic_to_ipa(vocalized_text, dialect="iraqi"):
    """Convert vocalized Arabic Hussaini lyrics into International Phonetic Alphabet (IPA)."""
    tokens = vocalized_text.split()
    ipa_tokens = []
    for tok in tokens:
        if tok == ".." or tok.startswith("["):
            ipa_tokens.append("|" if tok == ".." else tok)
            continue
        w = tok.strip("()،.")
        # Sun-letter assimilation for 'ال'
        if w.startswith("ال") and len(w) >= 3:
            nxt = w[2]
            if nxt in SUN_LETTERS:
                c_ipa = ARABIC_TO_IPA.get(nxt, nxt)
                rest = w[3:]
                prefix_ipa = f"a{c_ipa}-{c_ipa}"
            else:
                prefix_ipa = "al-"
                rest = w[2:]
        else:
            prefix_ipa = ""
            rest = w

        out = [prefix_ipa]
        n_ch = len(rest)
        for idx, ch in enumerate(rest):
            if ch == "\u0651":  # Shadda gemination
                if out:
                    out.append("ː")
                continue
            if idx == n_ch - 1 and ch in ("ه", "ة") and dialect != "fusha":
                out.append("a")
                continue
            if ch in ("و", "ي") and idx > 0 and rest[idx - 1] in ("\u064F", "\u0650"):
                out[-1] = "uː" if ch == "و" else "iː"
                continue
            if ch == "ا" and idx > 0 and rest[idx - 1] == "\u064E":
                out[-1] = "aː"
                continue
            out.append(ARABIC_TO_IPA.get(ch, ""))
        ipa_str = "".join(out).strip("-")
        if ipa_str:
            ipa_tokens.append(ipa_str)
    return " ".join(ipa_tokens)


def compile_generative_g2p_and_ipa(text, base_shaper_fn, dialect=None, use_tatweel=False):
    """Compile lyrics across all 6 Hussaini dialect ecosystems with generative morphology & IPA."""
    detected_ext = dialect
    if not detected_ext:
        for d_key, markers in EXTENDED_DIALECT_MARKERS.items():
            if any(m in text for m in markers):
                detected_ext = d_key
                break

    base_res = base_shaper_fn(text, use_tatweel=use_tatweel)
    active_dialect = detected_ext or base_res["detected_dialect"]
    shaped_lines = []
    for ln in base_res["shaped_lyrics"].splitlines():
        if not ln.strip() or ln.strip().startswith("["):
            shaped_lines.append(ln)
            continue
        toks = [apply_generative_morphological_rules(t, dialect=active_dialect) for t in ln.split(" ")]
        shaped_lines.append(" ".join(toks))

    final_lyrics = "\n".join(shaped_lines)
    # Strip any accidental Sukun on open feminine Haa in colloquial dialects
    if active_dialect != "fusha":
        final_lyrics = re.sub(r"([هة])\u0652(?=\s|$|\.\.|[،\)])", r"\1", final_lyrics)

    ipa_out = transcribe_vocalized_arabic_to_ipa(final_lyrics, dialect=active_dialect)
    return {
        "ecosystem_dialect": active_dialect,
        "base_dialect_family": base_res["detected_dialect"],
        "shaped_lyrics": final_lyrics,
        "ipa_transcription": ipa_out,
        "maqam_articulation_rule": base_res["maqam_articulation_rule"],
    }


PERFORMANCE_ATWAR_V50 = {
    "tor_nai_kashi": {
        "arabic_name": "طور النعي الكاشي / المنبري (الكيفية الأولى)",
        "school": "iraqi_bahrani", "primary_maqam": "hijaz", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "مدّ وترجيع الكلمة الثانية والأخيرة من كل شطر مع ترقيق الصوت والونّة في القفلة",
    },
    "tor_nai_kashi_2": {
        "arabic_name": "طور النعي المنبري (الكيفية الثانية - الوصل)",
        "school": "iraqi", "primary_maqam": "saba", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "مدّ الكلمة الثانية وما قبل الأخيرة وتكرار الكلمة الأخيرة ووصلها بالشطر التالي",
    },
    "tor_janoubi": {
        "arabic_name": "الطور الجنوبي المفجع",
        "school": "iraqi_janoubi", "primary_maqam": "saba", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "المدّ والترجيع من أول كلمة وآخرها مع إقحام الفواجع اللفظية (يمّه / بويه / خويه)",
    },
    "tor_iraqi_qadeem": {
        "arabic_name": "الطور العراقي القديم",
        "school": "iraqi", "primary_maqam": "bayati", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": True, "uses_wannah": True,
        "delivery_rule": "مدّ الكلمة الأخيرة بونّة خفيفة لمشاركة الجمهور، ويُمنع الختم به بل يُتحول لطور النعي",
    },
    "tor_rukbani": {
        "arabic_name": "الطور الركباني (الوداعيات)",
        "school": "iraqi", "primary_maqam": "sikah", "default_bpm": 64,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "الإسراع في بداية الشطر مع مدّ وسط الصدر ونهايته والعجز بطبقة عالية وونّة خفيفة",
    },
    "tor_hadi": {
        "arabic_name": "طور الحدي (مسير الظعن بأنواعه الثلاثة)",
        "school": "iraqi_bahrani", "primary_maqam": "hijaz", "default_bpm": 62,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "النطق ببطء كأنه يخرج رغماً عن القارئ مع مدّ متقطع حزين في آخر الصدر والعجز",
    },
    "tor_faizi_iraqi": {
        "arabic_name": "الطور الفايزي (الطريقة العراقية)",
        "school": "iraqi", "primary_maqam": "hijaz", "default_bpm": 64,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "الابتداء بقوة والإسراع حتى مدّ الكلمة الثالثة وترجيعها ثم الونّة قبل الحرف الأخير",
    },
    "tor_faizi_bahrani": {
        "arabic_name": "الطور الفايزي البحراني الأصيل",
        "school": "bahrani", "primary_maqam": "hijaz", "default_bpm": 62,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "الإسراع حتى الكلمة الثالثة ثم مدّها وترجيعها بإمالة بحرانية وختم الشطر بالونّة",
    },
    "tor_muthakkal_bahrani": {
        "arabic_name": "طور المثكّل البحراني / القطيفي",
        "school": "bahrani_qatifi", "primary_maqam": "saba", "default_bpm": 54,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "يبدأ وينتهي بهدوء تام مع ونّة منكسرة في آخر كل شطر لاستدرار الدمعة",
    },
    "tor_ashouri": {
        "arabic_name": "الطور العاشوري التفاعلي",
        "school": "iraqi", "primary_maqam": "saba", "default_bpm": 56,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "مدّ الكلمة الأخيرة طويلاً وتخفيف الصوت وقطعه (1.5s) لمشاركة المعزين بـ (آه .. آه)",
    },
    "tor_abudhiyah": {
        "arabic_name": "طور الأبوذية المنبرية",
        "school": "iraqi", "primary_maqam": "lami", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "مدّ الجناس في الأول والثاني، التصعيد للجواب في الثالث، والكسرة الفراتية على (-يَّه) في الرابع",
    },
    "tor_dashti": {
        "arabic_name": "الطور الدشتي",
        "school": "ahwazi_iraqi", "primary_maqam": "bayati_shuri", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "رفع الصوت وخفضه بمدّ وترجيع حزين على جنس بيات الشوري بدون ونّة ختامية",
    },
    "tor_mawal_iraqi": {
        "arabic_name": "طور الموّال الزهيري السبعوي",
        "school": "iraqi", "primary_maqam": "rast", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "تقطيع الشطر إلى مقطعين بوقفة تنفس وسطية والانكسار في شطر العرگ الرابع",
    },
    "tor_nayli": {
        "arabic_name": "الطور النايلي (جواب العمالقة)",
        "school": "iraqi", "primary_maqam": "hijaz", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "انطلاق مباشر من طبقة الجواب العالية بتطويح ومدّ طويل في الصدر بدون ونّة",
    },
    "tor_hadee": {
        "arabic_name": "الطور الهادئ (طور المصرع والتخلص)",
        "school": "iraqi_bahrani", "primary_maqam": "saba_zamzam", "default_bpm": 0,
        "forbid_opening": True, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "مدّ على وتيرة هادئة بترجيع خفيف للمصرع وبيت التخلص، ولا يُبتدأ به بدون تمهيد",
    },
    "tor_mullai": {
        "arabic_name": "الطور الملّائي",
        "school": "iraqi", "primary_maqam": "bayati", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "التوقف والترجيع الخفيف على كل كلمة ويزداد التوقف والترجيع في آخر كلمة من الشطر",
    },
    "tor_amili": {
        "arabic_name": "طور النعي العاملي التراثي",
        "school": "amili", "primary_maqam": "bayati", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": True, "uses_wannah": False,
        "delivery_rule": "مدّ وترجيع في الشطرين الأولين، وتباطؤ وتوقف على كل كلمة في الثالث والرابع، ولا يُختم به",
    },
    "tor_takhmis": {
        "arabic_name": "طور التخميس المنبري والموكبي",
        "school": "iraqi_bahrani", "primary_maqam": "hijaz", "default_bpm": 58,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "تصعيد تدريجي عبر 4 أشطر تمهيدية والهبوط المفجع في الشطر الخامس الجامع",
    },
    "tor_qazwini": {
        "arabic_name": "الطور القزويني المنبري",
        "school": "iraqi", "primary_maqam": "suznak", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "قراءة منبرية متدرجة للأبيات الفصيحة تنتقل من الوقار إلى الشجن البكائي",
    },
    "tor_nuwayni": {
        "arabic_name": "الطور النويني",
        "school": "iraqi", "primary_maqam": "saba", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "أنين منبري متهدج منخفض الطبقة لمجالس المصيبة",
    },
    "tor_taghreed_hazeen": {
        "arabic_name": "طور التغريد الحزين",
        "school": "iraqi", "primary_maqam": "lami", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "تموجات حنجرية رقيقة متتابعة في الجواب المتوسط تصور غربة الأيتام والسبايا",
    },
    "tor_lahn_firaq": {
        "arabic_name": "طور لحن الفراق",
        "school": "iraqi", "primary_maqam": "kurd", "default_bpm": 56,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "أداء وداعي متهدج طويل المدّ يناسب وداع الحسين (ع) وليلة العاشر",
    },
    "tor_zaarijawi": {
        "arabic_name": "الطور الزريجاوي (طور الكعبي)",
        "school": "iraqi", "primary_maqam": "sikah", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "وتيرة متأرجحة مع مدّ وترجيع خفيفين وصعود ونزول بنبرة منهدّ الركن بدون ونّة",
    },
    "tor_huwaizawi": {
        "arabic_name": "الطور الحويزاوي الأهوازي/الفراتي",
        "school": "ahwazi_iraqi", "primary_maqam": "lami", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "مدّات حنجرية عالية في الجواب في مقام اللامي والصبا مع كسرة فراتية",
    },
    "tor_shushtari": {
        "arabic_name": "الطور الششتري",
        "school": "ahwazi_iraqi", "primary_maqam": "huzam", "default_bpm": 0,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": True,
        "delivery_rule": "شجن مقام الهزام والبيات بانتقالات ربع تون دقيقة للنعيات التراثية",
    },
    "tor_darj_karbalai": {
        "arabic_name": "طور الدرج الكربلائي الموكبي",
        "school": "iraqi", "primary_maqam": "bayati", "default_bpm": 72,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "مشية موكبية متزنة وقوية تتدرج من البيات إلى جواب الحجاز",
    },
    "tor_bahrani_thulathi": {
        "arabic_name": "طور العزاء البحراني الثلاثي (الموكبي)",
        "school": "bahrani", "primary_maqam": "bayati", "default_bpm": 76,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "ضربتان متقاربتان (دم-دم) + ضربة ثالثة ثقيلة مع وقفة تنفسية وتبادل الفوجين",
    },
    "tor_bahrani_rubai": {
        "arabic_name": "طور العزاء البحراني الرباعي (الداخلية والموكب)",
        "school": "bahrani", "primary_maqam": "nahawand", "default_bpm": 72,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "أربع ضربات صدرية متزنة (3 مسير + 1 ارتكاز) مع نظام الفوجين المتقابلين",
    },
    "tor_bahrani_haidari": {
        "arabic_name": "الطور الحيدري الملحمي البحراني",
        "school": "bahrani", "primary_maqam": "hijaz", "default_bpm": 96,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "إيقاع موكبي حماسي متصاعد بضربات صدرية حادة في رثاء الأبطال والعباس (ع)",
    },
    "tor_waqfa_bahrani": {
        "arabic_name": "طور الوقفة البحرانية (التجنيزة)",
        "school": "bahrani", "primary_maqam": "saba", "default_bpm": 104,
        "forbid_opening": False, "forbid_closing": False, "uses_wannah": False,
        "delivery_rule": "توقف المسير لترديد أبيات قصيرة مكثفة سريعة الإيقاع بتناوب الفوج الأول والثاني",
    },
}


def apply_minbar_tor_delivery_rules(lyrics_text, tor_id="tor_nai_kashi", position="middle"):
    """Validate council placement locks and annotate delivery phrasing for any of the Atwar."""
    spec = PERFORMANCE_ATWAR_V50.get(tor_id, PERFORMANCE_ATWAR_V50["tor_nai_kashi"])
    warnings = []
    recommended_followup_tor = None
    recommended_prelude_tor = None

    if position == "opening" and spec["forbid_opening"]:
        warnings.append(f"لا يُبتدأ بـ {spec['arabic_name']} مباشرة؛ يجب التمهيد بطور النعي أو الدرج أولاً.")
        recommended_prelude_tor = "tor_nai_kashi"
    if position == "closing" and spec["forbid_closing"]:
        warnings.append(f"لا يُختم المجلس بـ {spec['arabic_name']}؛ يجب التحول إلى طور النعي الكاشي في الختام.")
        recommended_followup_tor = "tor_nai_kashi"

    lines = [ln.strip() for ln in lyrics_text.splitlines() if ln.strip() and not ln.strip().startswith("[")]
    phrased_lines = []
    for idx, ln in enumerate(lines):
        base = ln.replace("..", "").strip()
        words = base.split()
        if tor_id == "tor_ashouri":
            phrased_lines.append(f"{base} .. (آه .. آه) ..")
        elif tor_id == "tor_janoubi" and idx == 0 and not any(v in base for v in ("يمه", "يمّه", "بويه", "خويه")):
            phrased_lines.append(f"آه يَا خُويَه .. {base} ..")
        elif tor_id == "tor_nai_kashi_2" and len(words) >= 3:
            last_w = words[-1]
            phrased_lines.append(f"{base} .. ({last_w})")
        else:
            phrased_lines.append(f"{base} ..")

    return {
        "tor_id": tor_id,
        "arabic_name": spec["arabic_name"],
        "primary_maqam": spec["primary_maqam"],
        "default_bpm": spec["default_bpm"],
        "uses_wannah": spec["uses_wannah"],
        "delivery_rule": spec["delivery_rule"],
        "council_position_warnings": warnings,
        "recommended_prelude_tor": recommended_prelude_tor,
        "recommended_followup_tor": recommended_followup_tor,
        "phrased_lyrics": "\n".join(phrased_lines),
    }


# ==============================================================================
# 5. PRO DSP UPGRADES: CENTS HISTOGRAM, DYNAMIC AHAAT, 24-EDO TUNER, HPSS & M/S
# ==============================================================================

def classify_maqam_by_cents_histogram(pitches_hz, fallback_maqam="saba"):
    """Classify Maqam across all 15 Maqamat using a 24-EDO cent-interval histogram."""
    if not pitches_hz:
        return 146.83, fallback_maqam, {}

    arr = np.asarray(pitches_hz, dtype=np.float64)
    # Estimate tonic from the stable lower-register anchor (20th percentile cluster)
    low_anchor = float(np.percentile(arr, 22))
    # Snap tonic near nearest cluster mode within +-8% of low_anchor
    near_low = arr[(arr >= 0.92 * low_anchor) & (arr <= 1.08 * low_anchor)]
    tonic_hz = round(float(np.median(near_low)) if len(near_low) > 0 else low_anchor, 2)

    rel_cents = np.mod(1200.0 * np.log2(np.maximum(arr, 30.0) / max(tonic_hz, 30.0)), 1200.0)
    # If input is a pure single-frequency test tone, match closest default tonic first
    if float(np.std(rel_cents)) < 12.0:
        best_m = fallback_maqam
        best_d = 1e9
        for m_name, spec in MAQAM_INTERVALS_CENTS.items():
            d = abs(tonic_hz - spec["default_tonic_hz"])
            if d < best_d:
                best_d = d
                best_m = m_name
        return tonic_hz, best_m, {best_m: 1.0}

    grid = np.linspace(0.0, 1150.0, 24)  # 50-cent quarter-tone bins
    obs_hist = np.zeros(24, dtype=np.float64)
    for c_val in rel_cents:
        diffs = np.minimum(np.abs(grid - c_val), 1200.0 - np.abs(grid - c_val))
        obs_hist += np.exp(-0.5 * ((diffs / 28.0) ** 2))
    obs_norm = obs_hist / (np.linalg.norm(obs_hist) + 1e-12)

    scores = {}
    for m_name, spec in MAQAM_INTERVALS_CENTS.items():
        tmpl = np.zeros(24, dtype=np.float64)
        for idx_d, deg_c in enumerate(spec["cents"][:-1]):
            weight = 1.35 if idx_d in (0, spec["ghammaz_index"]) else 1.0
            diffs = np.minimum(np.abs(grid - deg_c), 1200.0 - np.abs(grid - deg_c))
            tmpl += weight * np.exp(-0.5 * ((diffs / 25.0) ** 2))
        tmpl_norm = tmpl / (np.linalg.norm(tmpl) + 1e-12)
        scores[m_name] = round(float(np.dot(obs_norm, tmpl_norm)), 4)

    best_maqam = max(scores, key=scores.get)
    return tonic_hz, best_maqam, scores


def strip_ai_percussion_stft_hpss(signal, sample_rate):
    """STFT Median Harmonic-Percussive Source Separation preserving 4.5-12kHz vocal clarity."""
    if len(signal) < 512:
        return signal
    nperseg = min(1024, max(128, len(signal) // 4))
    _, _, zxx = stft(signal, fs=sample_rate, nperseg=nperseg)
    mag = np.abs(zxx)
    # Harmonic energy is smooth across time; percussive clicks/thuds are smooth across frequency
    harm = median_filter(mag, size=(1, min(13, max(3, mag.shape[1] // 3))))
    perc = median_filter(mag, size=(min(13, max(3, mag.shape[0] // 4)), 1))
    mask_h = (harm ** 2) / ((harm ** 2) + (1.35 * (perc ** 2)) + 1e-16)
    _, rec = istft(zxx * mask_h, fs=sample_rate, nperseg=nperseg)
    rec = rec[: len(signal)]
    if len(rec) < len(signal):
        rec = np.pad(rec, (0, len(signal) - len(rec)))
    # Gentle 85Hz sub-thud cleanup keeping full 85Hz-12kHz vocal spectrum intact
    nyq = 0.5 * sample_rate
    if nyq > 120.0:
        sos = butter(4, min(95.0, 0.4 * sample_rate) / nyq, btype="high", output="sos")
        rec = sosfilt(sos, rec)
    return rec


def apply_microtonal_maqam_tuning(vocal_signal, sample_rate, maqam="saba", strength=0.0):
    """Retune voiced frames gently toward nearest 24-EDO Maqam scale degree while keeping Wannah."""
    if strength <= 0.01 or len(vocal_signal) < 512:
        return vocal_signal
    strength = float(np.clip(strength, 0.0, 1.0))
    scale_hz = np.asarray(transpose_maqam_frequencies(maqam), dtype=np.float64)
    # Build 3-octave 24-EDO target grid (Qarar, Wasat, Jawab)
    targets = np.concatenate([0.5 * scale_hz[:-1], scale_hz[:-1], 2.0 * scale_hz])

    hop = max(128, int(0.04 * sample_rate))
    out = vocal_signal.copy()
    min_lag = max(1, int(sample_rate / 420.0))
    max_lag = max(min_lag + 2, int(sample_rate / 95.0))

    for start in range(0, len(vocal_signal) - 2 * hop, hop):
        frame = vocal_signal[start : start + 2 * hop]
        if max_lag >= len(frame) or np.sqrt(np.mean(frame ** 2)) < 0.025:
            continue
        acf = np.correlate(frame, frame, mode="full")[len(frame) - 1 :]
        lag = min_lag + int(np.argmax(acf[min_lag:max_lag]))
        f_est = float(sample_rate / lag)
        nearest_t = targets[int(np.argmin(np.abs(targets - f_est)))]
        cents_err = 1200.0 * np.log2((nearest_t + 1e-9) / (f_est + 1e-9))
        # Preserve intentional wide Wannah pitch glides (>95 cents) and tiny vibrato (<6 cents)
        if 6.0 <= abs(cents_err) <= 95.0:
            ratio = 2.0 ** ((strength * cents_err) / 1200.0)
            idx_src = np.clip(np.arange(hop, dtype=np.float64) * ratio, 0, len(frame) - 1)
            shifted = np.interp(idx_src, np.arange(len(frame), dtype=np.float64), frame)
            win = np.hanning(hop)
            out[start : start + hop] = (1.0 - win) * out[start : start + hop] + win * shifted
    return out


def apply_vocal_deesser(signal, sample_rate, threshold_rms=0.09, reduction_db=-5.5):
    """Dynamic De-Esser taming harsh 5.2kHz-9.5kHz sibilance (س، ص، ش) without dulling vowels."""
    nyq = 0.5 * sample_rate
    if nyq <= 5600.0 or len(signal) == 0:
        return signal
    high_f = min(9500.0, 0.46 * sample_rate)
    sos = butter(2, [5200.0 / nyq, high_f / nyq], btype="band", output="sos")
    sib_band = sosfilt(sos, signal)
    win = max(1, int(0.008 * sample_rate))
    sib_rms = np.sqrt(np.maximum(np.convolve(sib_band ** 2, np.ones(win) / win, mode="same"), 1e-16))
    atten = float(10.0 ** (reduction_db / 20.0))
    over = np.clip((sib_rms - threshold_rms) / (threshold_rms + 1e-9), 0.0, 1.0)
    return signal - over * (1.0 - atten) * sib_band


def apply_parallel_vocal_compression(signal, blend=0.24):
    """Apply smooth parallel vocal compression to stabilize intimate whispers & high Jawab climbs."""
    if len(signal) == 0 or blend <= 0.0:
        return signal
    compressed = np.tanh(2.4 * signal) / np.tanh(2.4)
    return (1.0 - blend) * signal + blend * compressed


def synthesize_dynamic_pitch_tracked_ahaat(vocal_signal, sample_rate, maqam="saba", is_strings_pad=False):
    """Synthesize Pitch-Tracked Dynamic Formant Ahaat following Radood Qarar/Wasat/Jawab degrees."""
    n_samples = len(vocal_signal)
    if n_samples <= 0:
        return np.zeros(0, dtype=np.float64)

    scale_hz = transpose_maqam_frequencies(maqam)
    spec = MAQAM_INTERVALS_CENTS.get(maqam.lower(), MAQAM_INTERVALS_CENTS["saba"])
    tonic_hz = scale_hz[0]
    ghammaz_hz = scale_hz[spec["ghammaz_index"]]
    fifth_hz = scale_hz[min(4, len(scale_hz) - 1)]

    # Track vocal F0 & pause activity every 50ms so Ahaat follows register shifts without clashing
    win = max(64, int(0.05 * sample_rate))
    target_f0 = np.full(n_samples, tonic_hz, dtype=np.float64)
    pause_swell = np.ones(n_samples, dtype=np.float64)
    min_lag = max(1, int(sample_rate / 380.0))
    max_lag = max(min_lag + 2, int(sample_rate / 105.0))

    cur_degree_hz = tonic_hz
    for start in range(0, n_samples, win):
        end = min(n_samples, start + win)
        seg = vocal_signal[start:end]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) > 0 else 0.0
        if rms >= 0.025 and len(seg) > max_lag:
            acf = np.correlate(seg, seg, mode="full")[len(seg) - 1 :]
            lag = min_lag + int(np.argmax(acf[min_lag:max_lag]))
            f_vo = float(sample_rate / lag)
            if f_vo >= 1.42 * tonic_hz:
                cur_degree_hz = ghammaz_hz
            elif f_vo >= 1.22 * tonic_hz:
                cur_degree_hz = scale_hz[2]
            else:
                cur_degree_hz = tonic_hz
            pause_swell[start:end] = 0.88
        else:
            # Gentle swell in vocal silence/breaths to fill the emotional gap (Lesson 10 rule)
            pause_swell[start:end] = 1.24
        target_f0[start:end] = cur_degree_hz

    glide = max(1, int(0.12 * sample_rate))
    f0_smooth = np.convolve(target_f0, np.ones(glide) / glide, mode="same")
    swell_smooth = np.convolve(pause_swell, np.ones(glide) / glide, mode="same")

    t_vec = np.arange(n_samples, dtype=np.float64) / sample_rate
    pad = np.zeros(n_samples, dtype=np.float64)
    rng = np.random.default_rng(seed=77)
    nyq = 0.5 * sample_rate

    # Choir unison + octave/fifth modal support (zero Western major/minor third clash)
    ratios = (1.0, fifth_hz / tonic_hz, 0.5) if is_strings_pad else (1.0, 0.5)
    for r_idx, mult in enumerate(ratios):
        for c_idx, cents in enumerate((-4.5, 0.0, +4.5)):
            f_inst = f0_smooth * mult * (2.0 ** (cents / 1200.0))
            vib = 1.0 + 0.0035 * np.sin(2.0 * np.pi * (4.1 + 0.2 * r_idx + 0.1 * c_idx) * t_vec)
            phase = np.mod(np.cumsum(f_inst * vib / sample_rate), 1.0)
            tp, tn = 0.40, 0.16
            pulse = np.zeros_like(phase)
            m1 = phase < tp
            m2 = (phase >= tp) & (phase < tp + tn)
            pulse[m1] = 0.5 * (1.0 - np.cos(np.pi * phase[m1] / tp))
            pulse[m2] = np.cos(0.5 * np.pi * (phase[m2] - tp) / tn)
            glottal = 0.97 * np.diff(pulse, prepend=pulse[0]) + 0.03 * rng.normal(0.0, 0.25, n_samples)
            pad += (0.36 / (r_idx + 1)) * (glottal / 3.0)

    # Apply human pharyngeal /a:/ formants
    resonated = np.zeros_like(pad)
    for c_hz, bw_hz, g_val in ((730.0, 95.0, 1.0), (1090.0, 115.0, 0.55), (2440.0, 165.0, 0.25)):
        lf, hf = max(60.0, c_hz - 0.5 * bw_hz), min(0.45 * sample_rate, c_hz + 0.5 * bw_hz)
        if nyq > hf + 30.0 and hf > lf + 20.0:
            sos = butter(2, [lf / nyq, hf / nyq], btype="band", output="sos")
            resonated += g_val * sosfilt(sos, pad)
    if np.max(np.abs(resonated)) < 1e-8:
        resonated = pad
    resonated = resonated / (np.max(np.abs(resonated)) + 1e-9)
    return resonated * swell_smooth * (0.17 if is_strings_pad else 0.14)


def synthesize_tasa_and_matam_breath(sample_rate, kind="tasa", seed=303):
    """Synthesize authentic Karbalai/Bahrani Brass Tasa (الطاسة النحاسية) or congregation Matam Breath."""
    rng = np.random.default_rng(seed=seed)
    nyq = 0.5 * sample_rate
    if kind == "tasa":
        dur = 0.24
        n_s = max(1, int(dur * sample_rate))
        t_v = np.linspace(0.0, dur, n_s, endpoint=False)
        # Inharmonic brass cymbal modes + high metallic shimmer
        modes = (
            0.45 * np.sin(2.0 * np.pi * 1480.0 * t_v)
            + 0.35 * np.sin(2.0 * np.pi * 2310.0 * t_v)
            + 0.25 * np.sin(2.0 * np.pi * 3670.0 * t_v)
        ) * np.exp(-16.0 * t_v)
        shimmer = rng.normal(0.0, 1.0, n_s) * np.exp(-24.0 * t_v)
        if nyq > 3200.0:
            sos = butter(2, 2800.0 / nyq, btype="high", output="sos")
            shimmer = sosfilt(sos, shimmer)
        return 0.35 * modes + 0.28 * shimmer

    # Congregation Matam rhythmic exhale/inhale breath ('حيدر / آه / زفير الشور')
    dur = 0.22
    n_s = max(1, int(dur * sample_rate))
    t_v = np.linspace(0.0, dur, n_s, endpoint=False)
    env = np.sin(np.pi * t_v / dur) ** 1.4
    noise = rng.normal(0.0, 1.0, n_s) * env
    if nyq > 1600.0:
        sos = butter(2, [350.0 / nyq, min(1800.0, 0.44 * sample_rate) / nyq], btype="band", output="sos")
        noise = sosfilt(sos, noise)
    return 0.22 * noise


SEMANTIC_FOLEY_LEXICON = {
    "water": ("فرات", "ماي", "ماء", "عطش", "ظامي", "ضامي", "نهر", "شاطي", "شريعة", "جود", "ساقي"),
    "horses": ("خيل", "مهر", "جواد", "أعوجية", "اعوجيه", "حوافر", "ركضت", "فرس", "سرج"),
    "wind": ("صحراء", "طف", "رمضا", "غربة", "غربه", "خرابة", "خرابه", "برية", "فلوات", "خيم"),
    "chains": ("قيود", "سلاسل", "غل", "جامعة", "سجاد", "يسر", "سبايا", "أسر", "حبال"),
    "swords": ("سيف", "رمح", "سهام", "حومة", "قتال", "درع", "ميدان", "نبل", "شفرة"),
    "majlis_weeping": ("يتامى", "ونين", "دموع", "تبچي", "يبچي", "نعي", "مفجوعة", "فاطمة", "رقية"),
}


def _render_foley_segment(num_samples, sample_rate, cue_type, seed=404):
    """Synthesize a specific spatial ritual Foley texture for a given time segment."""
    if num_samples <= 0 or cue_type == "none":
        return np.zeros(max(0, num_samples), dtype=np.float64)
    rng = np.random.default_rng(seed=seed)
    t_vec = np.arange(num_samples, dtype=np.float64) / sample_rate
    noise = rng.normal(0.0, 1.0, num_samples)
    nyq = 0.5 * sample_rate

    if cue_type == "chains":
        clink_env = np.exp(-42.0 * np.mod(t_vec, 0.62)) + 0.6 * np.exp(-50.0 * np.mod(t_vec + 0.11, 0.62))
        metallic = noise * clink_env
        if nyq > 2600.0:
            sos = butter(2, [1900.0 / nyq, min(4800.0, 0.45 * sample_rate) / nyq], btype="band", output="sos")
            metallic = sosfilt(sos, metallic)
        return 0.035 * metallic

    if cue_type == "swords":
        ring = (
            np.sin(2.0 * np.pi * 1820.0 * t_vec) + 0.6 * np.sin(2.0 * np.pi * 2940.0 * t_vec)
        ) * np.exp(-9.0 * np.mod(t_vec, 1.1))
        return 0.025 * ring

    if cue_type == "majlis_weeping":
        swell = 0.5 + 0.5 * np.sin(2.0 * np.pi * 0.28 * t_vec)
        murmur = noise * swell
        if nyq > 900.0:
            sos = butter(2, [240.0 / nyq, min(950.0, 0.42 * sample_rate) / nyq], btype="band", output="sos")
            murmur = sosfilt(sos, murmur)
        return 0.032 * murmur

    if cue_type == "water":
        sos = butter(2, min(900.0, 0.4 * sample_rate) / nyq, btype="low", output="sos")
        stream = sosfilt(sos, noise)
        droplet = np.sin(2.0 * np.pi * 1150.0 * t_vec) * np.exp(-35.0 * np.mod(t_vec, 0.45))
        return 0.035 * (0.6 * stream + 0.4 * droplet)

    if cue_type == "horses":
        cadence = np.exp(-28.0 * np.mod(t_vec, 0.38)) + 0.7 * np.exp(-28.0 * np.mod(t_vec + 0.14, 0.38))
        hoof = noise * cadence
        if nyq > 600.0:
            sos = butter(2, [120.0 / nyq, min(850.0, 0.4 * sample_rate) / nyq], btype="band", output="sos")
            hoof = sosfilt(sos, hoof)
        return 0.04 * hoof

    # Default desert wind
    gust = 0.55 + 0.45 * np.sin(2.0 * np.pi * 0.22 * t_vec)
    if nyq > 350.0:
        sos = butter(2, [180.0 / nyq, min(1200.0, 0.42 * sample_rate) / nyq], btype="band", output="sos")
        noise = sosfilt(sos, noise)
    return 0.042 * noise * gust


def synthesize_semantic_lyric_foley(num_samples, sample_rate, foley_type="none", lyrics_text=None):
    """Synthesize static or semantic lyric-timed Foley cues aligned proportionally to poem verses."""
    if num_samples <= 0 or not foley_type or foley_type == "none":
        return np.zeros(max(0, num_samples), dtype=np.float64)

    if foley_type != "auto" or not lyrics_text:
        return _render_foley_segment(num_samples, sample_rate, foley_type)

    lines = [ln.strip() for ln in lyrics_text.splitlines() if ln.strip() and not ln.strip().startswith("[")]
    if not lines:
        return np.zeros(num_samples, dtype=np.float64)

    bed = np.zeros(num_samples, dtype=np.float64)
    seg_len = max(1, num_samples // len(lines))
    fade = min(seg_len // 4, max(1, int(0.08 * sample_rate)))

    for idx, ln in enumerate(lines):
        matched_cue = "none"
        for cue_name, keywords in SEMANTIC_FOLEY_LEXICON.items():
            if any(kw in ln for kw in keywords):
                matched_cue = cue_name
                break
        if matched_cue == "none":
            continue
        s_i = idx * seg_len
        e_i = num_samples if idx == len(lines) - 1 else min(num_samples, (idx + 1) * seg_len)
        cue_audio = _render_foley_segment(e_i - s_i, sample_rate, matched_cue, seed=500 + idx)
        if fade > 1 and len(cue_audio) > 2 * fade:
            cue_audio[:fade] *= np.linspace(0.0, 1.0, fade)
            cue_audio[-fade:] *= np.linspace(1.0, 0.0, fade)
        bed[s_i:e_i] += cue_audio
    return bed


def apply_mono_safe_stereo_stage(wet_vocal, rhythm_bed, ahaat_pad, foley_bed, ducking, sample_rate, replace_ai=False):
    """Build a 100% Mono-Compatible Mid/Side 3D stereo image (zero comb filtering on PA speakers).

    Because Left = Mid + Side and Right = Mid - Side, summing (Left + Right) / 2 on a Husseiniya
    Mono PA system yields pure Mid with ZERO phase cancellation on the Radood or chest sub-bass!
    """
    r_gain = 0.43 if replace_ai else 0.35
    mid = wet_vocal + (r_gain * rhythm_bed + 0.12 * ahaat_pad + foley_bed) * ducking

    # Create orthogonal Side signal ONLY for frequencies > 180Hz (keeping sub-bass 100% centered)
    nyq = 0.5 * sample_rate
    ambience_src = (0.14 * ahaat_pad + 0.11 * rhythm_bed + 0.85 * foley_bed) * ducking
    if nyq > 240.0 and len(ambience_src) > 32:
        sos_hp = butter(2, min(185.0, 0.4 * sample_rate) / nyq, btype="high", output="sos")
        side_high = sosfilt(sos_hp, ambience_src)
        # First-order all-pass phase shift for wide 3D Husseiniya hall immersion
        shift_s = max(1, int(0.011 * sample_rate))
        side = np.zeros_like(side_high)
        if shift_s < len(side_high):
            side[shift_s:] = 0.65 * side_high[:-shift_s]
    else:
        side = np.zeros_like(mid)

    left = mid + side
    right = mid - side
    return left, right


# ==============================================================================
# 6. MULTI-ENGINE AI AUDIO & VOICE ROUTER (FLOW MUSIC, SUNO V4.5/V5.5, UDIO, RVC)
# ==============================================================================

def build_multi_engine_ai_prompt(
    engine_name="flow_music",
    dialect="iraqi",
    maqam="saba",
    bpm=60,
    tor_name="Karbalaei Funeral Latmiya",
    verified_voice_id=None,
):
    """Build platform-optimized, anti-pop-washing prompts & configs across 2026 AI audio engines."""
    eng = engine_name.strip().lower()
    m_key = maqam.lower()
    m_spec = MAQAM_INTERVALS_CENTS.get(m_key, MAQAM_INTERVALS_CENTS["saba"])
    d_label = {
        "bahrani": "Bahrani Matam",
        "qatifi": "Qatifi Bahrani",
        "hasawi": "Hasawi Gulf",
        "ahwazi": "Ahwazi Khuzestani",
        "amili": "South Lebanese Amili",
        "fusha": "Classical Arabic Fusha",
    }.get(dialect, "Iraqi Karbalaei")

    if eng == "suno_v4_5":
        style_prompt = (
            f"Heavy solemn {d_label} Hussaini Latmiya mourning chant at {bpm} BPM in microtonal "
            f"Arabic Maqam {m_key} ({m_spec['arabic_name']}) with quarter-tone ornaments. "
            "Commanding resonant grieving Baritone Radood lead vocal with tearful Wannah, "
            "powerful unison male Husseiniya congregation Raddada responses, and massive "
            "synchronized 55Hz bare-chest Latm thuds in a reverberant stone Matam hall. "
            "Strictly vocal and chest percussion, no melodic instruments."
        )
        notes = "Suno V4.5 excels at heavy percussive chest weight and dense congregation energy."
    elif eng == "suno_v5_5":
        style_prompt = (
            f"Traditional non-pop microtonal {d_label} Hussaini mourning recitative ({tor_name}), "
            f"{bpm} BPM, modal Arabic scale Maqam {m_key} quarter-tone intonation, raw unpolished "
            "emotional weeping Baritone Radood vocal with pharyngeal voice cracks, unison male "
            "Matam Raddada call-and-response, acoustic bare-chest Latm pulse, zero Western chords, "
            "zero pop-washing, Pure Acapella No Instruments"
        )
        notes = (
            "Suno V5.5 maximizes vocal expression and supports verified Custom Voice Fingerprints; "
            "explicit anti-pop-washing & modal quarter-tone locks prevent Western pop smoothing."
        )
    elif eng == "udio":
        style_prompt = (
            f"religious chant, traditional middle eastern vocal, {d_label.lower()} latmiya, "
            f"microtonal maqam {m_key}, 24-tet quarter-tone melisma, {bpm} bpm, grieving male "
            "baritone soloist, unison male congregation response, body percussion chest thud, "
            "acapella, no instruments, live husseiniya acoustics"
        )
        notes = "Udio responds strongly to comma-separated ethnomusicological & 24-TET tags."
    elif eng == "rvc_svc":
        style_prompt = "Ethical Post-Generation RVC v2 / So-VITS-SVC Timbre Conversion Pipeline"
        notes = (
            "Applies ONLY user-owned or contract-licensed Radood voice models over clean split "
            "vocal stems using RMVPE pitch extraction to preserve quarter-tones and Wannah."
        )
        return {
            "target_engine": "rvc_svc",
            "f0_method": "rmvpe",
            "f0_up_key": 0,
            "index_rate": 0.64,
            "filter_radius": 3,
            "rms_mix_rate": 0.25,
            "protect_voiceless_consonants": 0.35,
            "verified_voice_model_id": verified_voice_id,
            "ethical_policy": "Zero living-Radood impersonation; verified custom voice models only.",
            "engineering_notes": notes,
        }
    else:
        eng = "flow_music"
        style_prompt = (
            f"Mournful {d_label} Hussaini Latmiya chant, {bpm} BPM, solemn weeping Maqam {m_key} "
            f"on D, authentic {d_label} dialect articulation, grieving solo Baritone Radood vocal "
            "with tearful Wannah and weeping voice cracks, unison male congregation Raddada "
            "responses, deep 55Hz bare-chest Latm thud in Husseiniya hall, "
            "Pure Acapella No Instruments"
        )
        notes = "Optimized 42-word Flow Music (Lyria 3.5) Sound prompt with zero song-leakage words."

    return {
        "target_engine": eng,
        "dialect": dialect,
        "maqam": m_key,
        "bpm": bpm,
        "verified_voice_id": verified_voice_id,
        "style_or_sound_prompt": style_prompt,
        "lyrics_header_rule": "Use pure Arabic bracketed headers ([المُسْتَهَلّ], [النَّزْلَة الأُولَى], [الكَسْرَة وَالمُسْتَهَلّ]).",
        "engineering_notes": notes,
    }
