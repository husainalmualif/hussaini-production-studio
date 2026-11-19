#!/usr/bin/env python3
# pylint: disable=too-many-lines,too-many-return-statements,too-many-branches,too-many-locals,too-many-statements,too-many-arguments,too-many-positional-arguments,no-member,chained-comparison
"""Hussaini Audio Omni-Architect DSP, 5-Track DAW & Phonetics Compiler (V57.0 OMNI-ARCHITECT).

Standalone empirical production engine implementing Hussaini_Production_Studio_OS_V50_0_OMNI_ARCHITECT
and V52.0–V57.0 field & 175-track empirical upgrades:
- Single-Source Version Management via root VERSION file & JSON constitution
- Pure-Python WAV I/O (with transparent FFmpeg MP3/M4A/OGG decoding) + ITU-R BS.1770-4 / EBU R128
  K-Weighted Gated Loudness + 4x True-Peak Limiter
- Module 67–72 (V52.0–V57.0): Clean Natural Arabic Lyria 3.5 Orthography Compiler (--compile-clean-lyria,
  NC26 Anti-Token-Shattering, NC27 چ->تش Digraph & Clean گ Lock, NC28 Anti-Pop Regional Vocal Prompts,
  NC29 20s Blind Chunk Phonetic Audit), 4-Axis Modern & Traditional Latmiya Architecture, Singer-Tonic-Locked
  f0 Ahaat & Cello Pad, Vocal-Pulse-Locked (<460Hz) Bare-Chest Latm, Crossover Whip-Snap Suppressor,
  175-Track Calibrated Vocal EQ + Arabic Sibilance De-Esser + Optical Leveler + Stereo Reverb, 24-EDO Maqam &
  Rubato Profiler, 9-School 5-Stage Prosodic Tor Router, NC18–NC29 Flow Music Laws & 3-Poem Benchmark Verifier
"""

import argparse
from datetime import datetime, timezone
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import wave

import numpy as np

try:
    from scipy.signal import butter, fftconvolve, iirnotch, lfilter, sosfilt
except ImportError:  # pragma: no cover - pure-NumPy fallback when scipy DLLs are blocked
    def fftconvolve(in1, in2, mode="full"):
        """Pure-NumPy FFT convolution fallback matching scipy.signal.fftconvolve."""
        a = np.asarray(in1, dtype=np.float64)
        b = np.asarray(in2, dtype=np.float64)
        n = a.size + b.size - 1
        if n <= 0:
            return np.zeros(0, dtype=np.float64)
        nfft = 1 << (n - 1).bit_length()
        out = np.fft.irfft(np.fft.rfft(a, nfft) * np.fft.rfft(b, nfft), nfft)[:n]
        if mode == "same":
            start = (b.size - 1) // 2
            return out[start : start + a.size]
        return out

    def iirnotch(w0, q_factor, fs=2.0):
        """Pure-NumPy 2nd-order IIR notch filter design matching scipy.signal.iirnotch."""
        w0_rad = 2.0 * math.pi * float(w0) / float(fs)
        alpha = math.sin(w0_rad) / (2.0 * max(float(q_factor), 1e-6))
        cos_w0 = math.cos(w0_rad)
        b = np.array([1.0, -2.0 * cos_w0, 1.0], dtype=np.float64) / (1.0 + alpha)
        a = np.array(
            [1.0, -2.0 * cos_w0 / (1.0 + alpha), (1.0 - alpha) / (1.0 + alpha)],
            dtype=np.float64,
        )
        return b, a

    def lfilter(b, a, x):
        """Pure-NumPy frequency-domain IIR/FIR linear filter fallback."""
        arr = np.asarray(x, dtype=np.float64)
        if arr.size == 0:
            return arr.copy()
        b_arr = np.asarray(b, dtype=np.float64) / float(a[0])
        a_arr = np.asarray(a, dtype=np.float64) / float(a[0])
        nfft = 1 << max(4, (arr.size + 64 - 1).bit_length())
        w = 2.0 * np.pi * np.fft.rfftfreq(nfft)
        ejw = np.exp(-1j * w)
        num = np.zeros_like(ejw, dtype=np.complex128)
        den = np.zeros_like(ejw, dtype=np.complex128)
        for idx_b, coef in enumerate(b_arr):
            num += coef * (ejw**idx_b)
        for idx_a, coef in enumerate(a_arr):
            den += coef * (ejw**idx_a)
        den = np.where(np.abs(den) < 1e-12, 1e-12, den)
        return np.fft.irfft(np.fft.rfft(arr, nfft) * (num / den), nfft)[: arr.size]

    def butter(order_n, wn_val, btype="low", output="sos"):
        """Descriptor return for pure-NumPy Butterworth filter fallback."""
        _ = output
        return ("butter_spec", int(order_n), wn_val, str(btype))

    def sosfilt(sos, x):
        """Pure-NumPy zero-clipping Butterworth frequency response filter."""
        arr = np.asarray(x, dtype=np.float64)
        if arr.size == 0:
            return arr.copy()
        _, order, wn, btype = sos
        nfft = 1 << max(4, (arr.size + 64 - 1).bit_length())
        freqs = np.fft.rfftfreq(nfft) * 2.0
        eps = 1e-12
        if btype == "low":
            fc = max(float(wn), eps)
            h_mag = 1.0 / np.sqrt(1.0 + (freqs / fc) ** (2 * order))
        elif btype == "high":
            fc = max(float(wn), eps)
            h_mag = 1.0 / np.sqrt(1.0 + (fc / np.maximum(freqs, eps)) ** (2 * order))
            h_mag[0] = 0.0
        else:
            f_lo = max(float(wn[0]), eps)
            f_hi = max(float(wn[1]), f_lo + eps)
            hp = 1.0 / np.sqrt(1.0 + (f_lo / np.maximum(freqs, eps)) ** (2 * order))
            hp[0] = 0.0
            lp = 1.0 / np.sqrt(1.0 + (freqs / f_hi) ** (2 * order))
            h_mag = hp * lp
        return np.fft.irfft(np.fft.rfft(arr, nfft) * h_mag, nfft)[: arr.size]


def get_skill_version():
    """Read the canonical skill version from the root VERSION file."""
    version_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "VERSION"))
    if os.path.isfile(version_file):
        with open(version_file, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    return "V50.0 OMNI-ARCHITECT"


SKILL_VERSION = get_skill_version()

# 24-EDO Maqam Drone Frequencies (Hz) — Section 4 of V50.0 Constitution
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
    "bayati": ["saba", "saba_zamzam", "kurd", "hijaz", "lami", "sikah", "nahawand"],
    "saba": ["saba_zamzam", "bayati", "lami", "hijaz", "rast", "nahawand"],
    "saba_zamzam": ["saba", "lami", "hijaz", "bayati", "kurd"],
    "hijaz": ["saba_zamzam", "bayati", "saba", "kurd", "sikah", "nahawand"],
    "lami": ["saba_zamzam", "saba", "bayati", "kurd"],
    "kurd": ["bayati", "lami", "saba_zamzam", "hijaz", "nahawand"],
    "rast": ["saba", "bayati", "hijaz", "sikah", "nahawand"],
    "nahawand": ["kurd", "bayati", "saba", "hijaz", "rast"],
    "sikah": ["bayati", "hijaz", "rast", "saba"],
}

SUPPORTED_DSP_MODES = (
    "vocal_pure_master",
    "latm",
    "heavy_clip",
    "thaqeel_muwazza",
    "studio_arranged",
    "modern_studio_ney_strings",
    "cinematic_foley_latmiya",
    "fazzaiya",
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
    "bujabara_qafila_60bpm_saba_hijaz_v50": (
        "Monumental Ahsa and Bahrani Mawkib Hussaini Latmiya, solemn Ashouri Qafila lament style, "
        "Maqam Saba and Hijaz, 60 BPM, authentic Bahrani and Iraqi colloquial dialect, commanding "
        "resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, "
        "passionate microtonal melisma, deep 55Hz bare-palm chest thud, 285ms analog delay, 3.4s "
        "Matam hall reverb, booming unison male Raddada choir response, Pure Acapella No Instruments"
    ),
    "akraf_tawshih_64bpm_hijaz_bayati_v50": (
        "Traditional Bahrani Hussaini Tawshih and Faizi Latmiya, Maqam Hijaz and Bayati, 64 BPM, "
        "authentic Bahrani colloquial dialect, wide majestic Baritone lead vocal, trembling "
        "microtonal vowel elongations, powerful high chest-voice climbs, synchronous 55Hz "
        "bare-palm chest thud, 260ms analog tape delay, 2.8s Matam hall reverb, wide unison male "
        "Raddada choir response, Pure Acapella No Instruments"
    ),
    "sayyid_salam_funeral_muthakkal_56bpm_lami_saba_v50": (
        "Mournful Southern Iraqi Hussaini Latmiya, heavy funeral Muthakkal and Lami style, Maqam "
        "Lami and Saba, 56 BPM, authentic Iraqi colloquial dialect, commanding deep resonant "
        "Baritone lead vocal, soulful microtonal melisma, natural vocal rasp, prolonged vowel "
        "elongations, deep 53Hz bare-palm chest thud, 320ms tape echo, 3.5s Husseiniya hall "
        "reverb, wide unison male Raddada response, Pure Acapella No Instruments"
    ),
    "harb_ayyashi_turaathi_60bpm_lami_bayati_v50": (
        "Traditional Southern Iraqi Euphrates Hussaini Latmiya, Bahr Al-Nassari and Rukbani "
        "style, Maqam Lami and Bayati, 60 BPM, authentic Southern Iraqi colloquial dialect, "
        "commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural "
        "vocal rasp, prolonged microtonal vowel elongations, heavy 55Hz bare-palm chest thud, "
        "285ms analog tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada response, "
        "Pure Acapella No Instruments"
    ),
    "janami_bayati_dialogic_68bpm_bayati_kurd_v50": (
        "Passionate Iraqi Najafi and Karbalaei Hussaini Mawkib Latmiya, melodic dialogic Nazla "
        "style, Maqam Bayati and Kurd, 68 BPM, authentic Iraqi colloquial dialect, commanding "
        "resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, "
        "passionate microtonal melisma, rhythmic 55Hz bare-palm chest thud, 260ms analog delay, "
        "3.0s Husseiniya hall reverb, energetic unison male Raddada choir response, "
        "Pure Acapella No Instruments"
    ),
    "bouhamad_khayyat_studio_58bpm_saba_kurd_v50": (
        "Mournful Bahrani and Gulf Hussaini Studio Latmiya lament, intimate Thaqeel and Faizi "
        "style, Maqam Saba and Kurd, 58 BPM, authentic Bahrani colloquial dialect, commanding "
        "deep close-mic Baritone lead vocal, soulful microtonal melisma, natural vocal rasp, deep "
        "55Hz bare-palm chest thud, 280ms analog tape delay, 3.2s Matam dome reverb, wide unison "
        "male Raddada choir response, Pure Acapella No Instruments"
    ),
    "kaabi_saad_basra_muthakkal_58bpm_hijaz_lami_v50": (
        "Traditional Iraqi Basrawi and Euphrates Hussaini Mawkib Latmiya, heavy Muthakkal and "
        "Nazla style, Maqam Hijaz and Lami, 58 BPM, authentic Southern Iraqi colloquial dialect, "
        "thunderous deep resonant Bass-Baritone lead vocal, powerful high chest-voice climbs, "
        "natural vocal rasp, passionate microtonal melisma, heavy 54Hz bare-palm chest thud, "
        "300ms tape echo, 3.5s Husseiniya hall reverb, massive unison male Raddada response, "
        "Pure Acapella No Instruments"
    ),
    "karimi_rasoli_taheri_zamineh_68bpm_hijaz_bayati_v50": (
        "Epic Hussaini processional Zamineh and Shoor elegy Latmiya, Maqam Hijaz and Bayati, "
        "68 BPM, authentic colloquial mourning articulation, thunderous heroic Bass-Baritone lead "
        "vocal, massive deep chest authority, powerful high chest-voice leaps, driving "
        "synchronous 55Hz bare-palm chest strikes, 250ms analog delay, 2.8s grand Husseiniya hall "
        "reverb, massive unison male congregation response, Pure Acapella No Instruments"
    ),
    "bahrani_haidari_enthusiastic_116bpm_bayati_hijaz_v50": (
        "Energetic Bahrani and Gulf Hussaini Mawkib Haidari chant, passionate antiphonal "
        "call-and-response style, Maqam Bayati and Hijaz, 116 BPM, eloquent Fusha and Gulf "
        "colloquial vocal delivery, commanding resonant Baritone lead vocal, powerful high "
        "chest-voice climbs, natural vocal rasp, driving synchronous 55Hz bare-palm chest "
        "strikes, 240ms tape delay, 2.8s grand Matam hall reverb, massive unison male "
        "congregation response, Pure Acapella No Instruments"
    ),
}

MASTER_SOUND_PROMPTS_V50 = MASTER_SOUND_PROMPTS_V48_5

EXTENDED_ATWAR_PROMPTS_V52 = {
    "karbalai_fazzaiya_84bpm_hijaz_bayati_v52": (
        "Urgent Traditional Iraqi Hussaini Fazzaiya chant, Maqam Hijaz and Bayati, 84 BPM, "
        "authentic Iraqi colloquial dialect, commanding fiery middle-register Baritone lead vocal, "
        "sharp crisp Arabic consonant articulation, synchronized rapid 55Hz bare-palm chest Matam "
        "thuds, 220ms analog delay, 2.5s Husseiniya hall reverb, booming unison male Raddada "
        "congregation response, Pure Acapella No Instruments"
    ),
    "shia_tawshih_nasheed_86bpm_rast_hijaz_v52": (
        "Dignified Spiritual Shia Islamic Choral Tawashih and Nasheed, Maqam Rast and Hijaz, "
        "86 BPM, eloquent Classical Arabic and devotional articulation, resonant Baritone solo "
        "verse answered by rich unison male choir, sacred mosque dome reverb, light respectful "
        "frame percussion only, zero chest Latm, zero Western instruments"
    ),
    "bahrani_thulathi_76bpm_bayati_hijaz_v54": (
        "Passionate Bahrani Hussaini Thulathi triple-pulse Latmiya lament, Maqam Bayati and Hijaz, "
        "76 BPM, authentic Bahrani colloquial dialect, majestic deep resonant Baritone lead vocal, "
        "powerful high chest-voice climbs, natural vocal rasp, triple-cadence 55Hz bare-chest strikes, "
        "260ms tape delay, 2.9s Matam hall reverb, wide unison male Raddada response, "
        "Pure Acapella No Instruments"
    ),
    "hosa_iraqi_mawkib_88bpm_hijaz_v54": (
        "Heroic Traditional Southern Iraqi Hussaini Hosa processional chant, Maqam Hijaz, 88 BPM, "
        "authentic Iraqi colloquial dialect, commanding powerful Bass-Baritone solo lead answered "
        "by booming unified male Mawkib chorus refrain, synchronized 55Hz bare-palm chest thuds, "
        "240ms slapback echo, 2.4s open courtyard reverb, Pure Acapella No Instruments"
    ),
    "ashura_majlis_noha_58bpm_saba_lami_v55": (
        "Authentic Shia Ashura Muharram Majlis Latmiya Noha in sorrowful Iraqi Maqam Saba and Lami, "
        "slow 58 BPM tempo. Heartbroken veteran Iraqi Karbalaei Radood chanting with intense emotional "
        "pain, weeping cracked baritone voice, soaring mournful climbs, and pure Iraqi colloquial "
        "cadence inside a sacred Husseiniya shrine hall. Unison weeping male congregation joins the "
        "chorus refrain with soft muffled bare chest thumping only. Pure human vocal acapella, "
        "strictly no musical instruments."
    ),
    "pure_acapella_weeping_noha_auto_bpm_saba_lami_v55": (
        "Raw unaccompanied acapella Shia Muharram Ashura Noha and Iraqi Minbar lamentation in "
        "heartbreaking Maqam Saba and Lami. Devastated solo Iraqi Karbalaei male voice weeping and "
        "lamenting in authentic Iraqi dialect with aching sustained melodies, raw vocal grief breaks, "
        "and deeply emotional dynamic arcs from quiet sorrowful whispers to passionate high cries, "
        "answered by grieving unison male congregation voices in natural mosque hall acoustics. "
        "Pure vocal acapella only, strictly no musical instruments."
    ),
    "golden_iraqi_studio_latmiya_60bpm_saba_bayati_v56": (
        "Solemn Iraqi Husseini Latmiya lament, Maqam Saba and Bayati, 60 BPM steady slow processional "
        "rhythm, warm deep emotional Arabic male baritone lead vocal, controlled dignified "
        "middle-register mournful delivery, clear crisp Iraqi Arabic pronunciation, smooth microtonal "
        "melisma, deep warm low-frequency muffled bare chest thumping, synchronized male congregation "
        "chorus on refrain only, clean dry studio vocal mix"
    ),
    "golden_bahrani_studio_latmiya_60bpm_saba_bayati_v56": (
        "Solemn Bahrani Husseini Latmiya lament, Maqam Saba and Bayati, 60 BPM steady slow processional "
        "rhythm, warm deep emotional Arabic male baritone lead vocal, controlled dignified "
        "middle-register mournful delivery, clear crisp Bahrani Arabic pronunciation, smooth microtonal "
        "Faizi melisma, deep warm low-frequency muffled bare chest thumping, synchronized male "
        "congregation chorus on refrain only, clean dry studio vocal mix"
    ),
    "mawkib_dammam_cymbals_brass_procession_78bpm_hijaz_v56": (
        "Majestic Traditional Husseini Ashura Mawkib procession chant, Maqam Hijaz and Bayati, "
        "78 BPM steady march, commanding resonant Baritone Radood vocal answered by booming unison "
        "male Mawkib chorus, deep traditional Dammam procession drums, metallic brass Tasa cymbals, "
        "and mournful solemn procession brass horn fanfare, strictly no upbeat pop rhythm"
    ),
    "modern_studio_ney_cello_violin_lament_60bpm_saba_lami_v56": (
        "Modern Studio Husseini Latmiya elegy, Maqam Saba and Lami, 60 BPM slow mournful pulse, "
        "warm deep emotional Arabic male baritone Radood vocal in controlled dignified middle-register "
        "delivery, weeping Arabic Ney flute in intro and interludes, warm low-register dramatic Cello "
        "drone and sorrowful legato Violin counter-melody, multi-layered male choral humming harmonies, "
        "deep muffled studio chest thumping, strictly no upbeat or dance rhythm"
    ),
    "cinematic_electronic_sub_pads_and_foley_latmiya_60bpm_lami_v56": (
        "Cinematic Modern Husseini Studio Latmiya, Maqam Lami and Kurd, 60 BPM solemn dramatic pulse, "
        "warm deep resonant Arabic male baritone Radood vocal, multi-layered male choir harmonies and "
        "background humming pads, deep cinematic Sub-Bass and dark atmospheric Pads, precision "
        "electronic studio chest-thump percussion, and subtle historical Karbala atmospheric wind and "
        "distant battlefield textures, strictly no dance or pop beats"
    ),
    # Module 72 (V57.0): Anti-Pop Regional Dialect Vocal Prompts (NC28 — Zero Piano, Zero Levantine Pop)
    "v57_iraqi_karbalaei_pure_majlis_60bpm_saba_lami": (
        "Traditional Iraqi Karbalaei Ashura Majlis Latmiya elegy, authentic Iraqi Baghdad and Karbala dialect, "
        "Maqam Saba and Lami microtonal chanting, slow 60 BPM dignified mourning cadence, immediate rhythmic "
        "chorus entry from the first second with no solo ad-lib intro, powerful deep resonant Iraqi male Radood "
        "chanting with sharp crisp Arabic pharyngeal pronunciation, responsive unison Iraqi male congregation "
        "Raddada chorus on refrain lines, soft muffled bare chest thumping only, cavernous Karbala shrine hall "
        "acoustics, strictly pure human vocal acapella, zero musical instruments, no piano, no pop singing"
    ),
    "v57_bahrani_matam_pure_58bpm_saba_bayati": (
        "Traditional Bahrani Ashura Matam Latmiya elegy from Bahrain, authentic Gulf Bahrani Arabic dialect, "
        "Maqam Saba and Bayati microtonal mourning chant, slow 58 BPM solemn dignified tempo, deep commanding "
        "Gulf Bahrani male Radood vocal with sharp authentic Arabic throat articulation, powerful unison "
        "Bahrani male Matam choir on refrain lines, soft muffled bare chest thumping only, solemn Bahraini "
        "Matam hall reverb, strictly pure human vocal acapella, zero musical instruments, no piano, no drums, "
        "no pop singing"
    ),
}

# Module 71 & 72 (V56.0–V57.0): The 4 Axes of Modern & Traditional Husseiniya Latmiya Sound Engineering
MODERN_LATMIYA_FOUR_AXES_V56 = {
    "axis_1_human_voice_choral_and_body_latm": {
        "arabic_title": "المحور الأول: الصوت البشري، الكورال، وإيقاع الجسد (الركيزة الأساس)",
        "core_elements": [
            "radood_baritone_maqam_mastery_saba_bayati_hijaz_lami",
            "multi_layer_choral_harmony_and_humming_pads",
            "live_and_sampled_bare_chest_body_latm_percussion",
        ],
        "recommended_dsp_modes": ["thaqeel_muwazza", "bahrani_muthakkal", "vocal_pure_master"],
        "prompt_keys": [
            "v57_iraqi_karbalaei_pure_majlis_60bpm_saba_lami",
            "v57_bahrani_matam_pure_58bpm_saba_bayati",
            "golden_iraqi_studio_latmiya_60bpm_saba_bayati_v56",
            "golden_bahrani_studio_latmiya_60bpm_saba_bayati_v56",
            "ashura_majlis_noha_58bpm_saba_lami_v55",
        ],
    },
    "axis_2_traditional_mawkib_procession_instruments": {
        "arabic_title": "المحور الثاني: الآلات التقليدية في المواكب",
        "core_elements": [
            "dammam_and_procession_drums",
            "brass_cymbals_tasa_sunoog",
            "mournful_heroic_procession_brass_trumpet",
        ],
        "recommended_dsp_modes": ["zanjeel_iraqi", "zanjeel_bahrani", "bandari"],
        "prompt_keys": [
            "mawkib_dammam_cymbals_brass_procession_78bpm_hijaz_v56",
            "zanjeel_procession_80bpm_hijaz",
        ],
    },
    "axis_3_modern_studio_strings_and_wind": {
        "arabic_title": "المحور الثالث: الآلات الوترية والنفخية في التسجيلات الحديثة",
        "core_elements": [
            "weeping_ney_flute_intros_and_interludes",
            "warm_low_register_dramatic_cello",
            "sorrowful_legato_violin_phrases_strictly_non_dance",
        ],
        "recommended_dsp_modes": ["modern_studio_ney_strings", "studio_arranged"],
        "prompt_keys": [
            "modern_studio_ney_cello_violin_lament_60bpm_saba_lami_v56",
            "golden_iraqi_studio_latmiya_60bpm_saba_bayati_v56",
        ],
    },
    "axis_4_electronic_engineering_and_dramatic_foley": {
        "arabic_title": "المحور الرابع: الهندسة الإلكترونية والمؤثرات الصوتية",
        "core_elements": [
            "deep_cinematic_sub_bass_and_ambient_pads",
            "historical_karbala_foley_swords_horses_wind_fire",
            "precision_electronic_studio_chest_latm_percussion",
        ],
        "recommended_dsp_modes": ["cinematic_foley_latmiya", "heavy_clip"],
        "prompt_keys": [
            "cinematic_electronic_sub_pads_and_foley_latmiya_60bpm_lami_v56",
        ],
    },
}

# Module 53 & 61 (QC19 & QC29): Mandatory 7-Key Per-Stage & 10-Key Per-Section JSON Orchestration Keys
REQUIRED_STAGE_JSON_KEYS = (
    "stage_id",
    "execution_command",
    "title",
    "global_bpm",
    "sound_description",
    "lyrics_register_verbatim",
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
    "zero vocal overlap",
    "with zero vocal overlap",
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
    "fazzaiya": {
        "arabic_name": "وزن الفزاعية والرباطات الموكبية",
        "rhyme_scheme": "AAAB / AAAA rapid heroic refrain (Ribatat)",
        "typical_syllables_per_hemistich": (6, 9),
        "compatible_atwar": ["tor_fazzaiya_karbalai", "tor_bahrani_haidari", "tor_darj_karbalai"],
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
    "tor_fazzaiya_karbalai": {
        "arabic_name": "طور الفزاعية والرباط الكربلائي",
        "school": "iraqi",
        "primary_maqam": "hijaz",
        "default_bpm": 84,
        "delivery_rule": "دخول متسارع حاسم بنداء النخوة ثم ردّة جماعية قاطعة بضربات صدر حادة ومنتظمة",
    },
    "tor_tawshih_shia": {
        "arabic_name": "طور التوشيح والنشيد الولائي",
        "school": "iraqi_bahrani",
        "primary_maqam": "rast",
        "default_bpm": 86,
        "delivery_rule": "أداء إنشادي وقور متوازن المقام بالدف الهادئ أو الأكابيلا الجماعية دون لطم صدري",
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
    "إبأرض": "بِأَرْضِ",
    "مابگت": "مَا بِگَتْ",
    "مابقت": "مَا بِگَتْ",
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

# Module 49, 57, 58 & 64: Colloquial Construct State, Relative Particle & Verified Lyria 3.5 G2P Locks
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
    "في طف كربلا": "فِي طَفِّ كَرْبَلَا",
    "في طف كربلاء": "فِي طَفِّ كَرْبَلَا",
    "هل شهر الألم": "هَلْ شَهَرْ الأَلَمْ",
    "هالشهر الألم": "هَلْ شَهَرْ الأَلَمْ",
    "والقائم رسم": "وَالْقَايِمْ رَسَمْ",
    "والقايم رسم": "وَالْقَايِمْ رَسَمْ",
    "يا جد ثارك بطه": "يَا جَدْ ثَارَكْ أَبْطَا",
    "ثارك بطه": "ثَارَكْ أَبْطَا",
    "من ظهر المهر": "مِنْ ظَهْرِ المُهْرْ",
    "وحزن عاشور قايم": "وْ حِزِنْ عَاشُورْ قَايِمْ",
    "وحزن عاشور قائم": "وْ حِزِنْ عَاشُورْ قَايِمْ",
    "حزنك خف": "حِزْنَكْ خَفْ",
    "يا گلب اليهيد": "يَا گَلْبِ اليِهِيدْ",
    "ويا جرح يلتم": "وَ يَا جَرْحِ يِلْتَمْ",
    "يبكي بلا شعور": "يِبْكِي بِلَا شُعُورْ",
    "يبچي بلا شعور": "يِبْكِي بِلَا شُعُورْ",
    "مقطوعة النحور": "مَقْطُوعَةِ النُّحُورْ",
    "بدمعه ما تنكف": "بِدَمْعَه مَا تِنْكَفْ",
    "وفرت أيتامك": "وَ فَرَّتْ أَيْتَامَكْ",
    "وحرگت خيامك": "وَ حَرْگَتْ خِيَامَكْ",
    "السلاب گدامك": "السَّلَّابْ گِدَّامَكْ",
    "تنزف آلامك": "تِنْزِفْ أَلَامَكْ",
    "ودليلك طر": "وَ دَلِيلَكْ طَرْ",
    "ركضت أشكال": "رِكْضَتْ أَشْكَالْ",
    "ركضت اشكال": "رِكْضَتْ أَشْكَالْ",
    "بسياط الحقد": "بِسْيَاطِ الحِقِدْ",
    # Module 66 (V51.2 NC3-NC15): Sawt Umm Al-Banin Empirically Verified Iraqi G2P Locks
    "صوت أم البنين يصيح": "صُوتْ أُمِّ البَنِينْ يِصِيحْ",
    "يبن حذلم": "يَبِنْ حَذْلَمْ",
    "لمن رد ابن حذلم": "لَمَّنْ رَدْ إِبِنْ حَذْلَمْ",
    "ردت نشده": "رِدَتْ نَشْدَه",
    "ردت نشدة": "رِدَتْ نَشْدَه",
    "رد لدياره لو بعده": "رَدْ لِدْيَارَهْ لَوْ بَعْدَهْ",
    "انگسم نصين": "انْگِسَمْ نُصَّينْ",
    "انجسم نصين": "انْگِسَمْ نُصَّينْ",
    "يبشر گطعت إفادي": "بِشِرْ گَطَّعِتْ إِفَّادِي",
    "بشر گطعت إفادي": "بِشِرْ گَطَّعِتْ إِفَّادِي",
    "ما أنشدك علأولادي": "مَا أَنْشِدَكْ إِعْلَه أَولَادِي",
    "ما أنشدك على أولادي": "مَا أَنْشِدَكْ إِعْلَه أَولَادِي",
    "يا أهل يثرب": "يَا أَهْلَ يَثْرِبْ",
    # Module 70 (V55.0 NC21-NC22 & 3-Poem Benchmark Locks):
    "طبع البشر ينسه الوفه": "طَبْعِ البَشَرْ يِنْسَى الوَفَا",
    "طبع البشر ينسى الوفا": "طَبْعِ البَشَرْ يِنْسَى الوَفَا",
    "طبع البشر": "طَبْعِ البَشَرْ",
    "بس انته مو مثل البشر": "بَسْ إِنْتَ مُو مِثِلِ البَشَرْ",
    "بس إنت مو مثل البشر": "بَسْ إِنْتَ مُو مِثِلِ البَشَرْ",
    "مو مثل البشر": "مُو مِثِلِ البَشَرْ",
    "ناموسك بظل العرش": "نَامُوسَكْ إِبْظِلِّ العَرِشْ",
    "وتنزل هوى للمختنگ": "وِتْنَزِّلْ هَوَى لِلْمِخْتِنِگْ",
    "والخدمه بالصدگ وجذب": "وَ الخِدْمَه بِالصِّدِگْ وْچِذِبْ",
    "حنين وماگلت مره شعليه": "حِنَيِّنْ وَ مَا گِلِتْ مَرَّه إِشْعَلَيَّه",
    "بس ياويل أجلك خيل عشره": "بَسْ يَا وَيلْ إِجَوْ لَكْ خَيلْ عَشْرَه",
    "طايح يغربيل الزلم": "طَايِحْ يَغِرْبِيلْ الزِّلِمْ",
    "يمغربل الدنيا بنحر": "يِمْغَرْبِلْ الدِّنْيَا إِبْنَحَرْ",
    "فلسفة الانتظار": "فَلْسَفَةُ الِانْتِظَارْ",
    "وفلسفة الوفه يقره": "وَ فَلْسَفَة الوَفَا يِقْرَه",
    "ودموع الانكسار": "وَ دُمُوعْ الِانْكِسَارْ",
    "وحچي اسمعونك": "وَ حَچِي يِسَمْعُونَكْ",
    "حچي اسمعونك": "حَچِي يِسَمْعُونَكْ",
    "المامذبوحله إبن ادم": "المَا مَذْبُوحْ لَه إِبِنْ آدَمْ",
    "والرايحله أبو اليمه": "وَ الرَّايِحْ لَه أَبُو اليِمَّه",
    "الامامك شوگك امن ايقل": "لإِمَامَكْ شُوگَكْ إِمْنِ يْقِلْ",
    "راح الكربلا وراحت": "رَاحْ لْكَرْبَلَا وَ رَاحَتْ",
    "راح الكربله وراحت": "رَاحْ لْكَرْبَلَا وَ رَاحَتْ",
    "تعلمنه اله فدوه": "تِعَلَّمْنَه إِلَه فِدْوَه",
    "ومن انگول البذار": "وَ مِنْ نْگُولْ البِذَارْ",
    "والاحزانه جهار": "وَ لأَحْزَانَه جِهَارْ",
    "وجهه في وجهه اشيريد": "وَجْهَه فِي وَجْهَه إِشْيِرِيدْ",
    "مشى سيفه اعلى النحر أو ظل يهبّره": "مِشَى سَيفَه إِعْلَى النَّحَرْ وَ ظَلْ يِهَبْرَه",
    "مشى سيفه اعلى النحر أْو ظل يهبّره": "مِشَى سَيفَه إِعْلَى النَّحَرْ وَ ظَلْ يِهَبْرَه",
    "تمشي علي جراحه": "تِمْشِي عَلَه جِرَاحَه",
    "وانته الـ داستك أقدام الليالي": "وَ إِنْتَه إِلْ دَاسِتَكْ أَقْدَامْ اللَّيَالِي",
    "وانته ال داستك أقدام الليالي": "وَ إِنْتَه إِلْ دَاسِتَكْ أَقْدَامْ اللَّيَالِي",
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
    "شلونش",
    "گلبش",
    "عيونش",
    "دمعش",
    "خدرش",
    "بيتش",
    "روحش",
    "حالش",
    "عفتش",
    "شفتش",
    "هالمسيه",
    "هالمسية",
    "ويش",
    "بهالشكل",
    "هالشكل",
    "أحين",
    "الحين",
    "إلين",
    "عَلَه",
    "وش ناوي",
    "اعلى الصدر",
    "اعلى الثرى",
    "اعلى النحر",
    "عالصدر",
    "عالغبره",
    "عالغبرة",
    "في حيره",
    "في حيرة",
    "في وجهه",
    "صوب النحر",
)

IRAQI_MARKERS = (
    "بويه",
    "خويه",
    "يخويه",
    "يمه",
    "وليدي",
    "دلالي",
    "شلون",
    "اشلون",
    "إش صار",
    "شصار",
    "شنگول",
    "شيصير",
    "شگد",
    "شكد",
    "بلياك",
    "ما ظل",
    "ماظل",
    "چلبت",
    "وگفت",
    "هسه",
    "هالحچايه",
    "هالحچاية",
    "مشبوگه",
    "يبچي",
    "ابچي",
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
    "اچفوف",
    "چفين",
    "بگلبي",
    "بكلبي",
    "بگاع",
    "بهداي",
    "بعفه",
    "بگت",
    "وسفه",
    "تظل",
    "يحاچيني",
    "إعله",
    "اعله",
    "وسادة ريش",
    "دنية خير",
    "العافية",
    "العافيه",
    "مطيني",
    "يالمطيني",
    "يفگدله",
    "آنه",
    "چنت",
    "چان",
    "چانت",
    "چا",
    "موش",
    "اويلاه",
    "أويلاه",
    "گوه",
    "گمت",
    "گعد",
    "گال",
    "هيج",
    "موذر",
    "مچتوف",
    "مگطع",
    "العلگمي",
    "فاگد",
    "تبرالي",
    "يبرالي",
    "صدگ",
    "منطيني",
    "مختنگ",
    "شعليه",
    "تگلي",
    "ملچوم",
    "الفارگ",
    "ابلايه",
    "ماتسوه",
    "المشتاگ",
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
    "إِتْسِيلْ": "تِسِيلْ",
    "تْسِيلْ": "تِسِيلْ",
    "إِهْمُومْ": "هُمُومْ",
    "هْمُومْ": "هُمُومْ",
    "إِهْمُومِي": "هُمُومِي",
    "هْمُومِي": "هُمُومِي",
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
    # Module 49 & 64 (QC13 & QC33): Selective Iraqi Prosthetic Clusters & Verified G2P Locks
    "بچفك": "إِبْچَفَّكْ",
    "بجفك": "إِبْچَفَّكْ",
    "بچدم": "إِبْچِدَمْ",
    "بجدم": "إِبْچِدَمْ",
    "چفوفك": "إِچْفُوفَكْ",
    "جفوفك": "إِچْفُوفَكْ",
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
    "خيام": "خِيَامْ",
    "خيم": "خِيَمْ",
    "بهداي": "إِبْهِدَايْ",
    "بهيبه": "إِبْهَيبَه",
    "بهيبة": "إِبْهَيبَه",
    "بسبي": "إِبْسَبِي",
    "بعفه": "إِبْعِفَّه",
    "بعفة": "إِبْعِفَّه",
    "بشده": "إِبْشِدَّه",
    "بشدة": "إِبْشِدَّه",
    "بخرابه": "إِبْخَرَابَه",
    "بخرابة": "إِبْخَرَابَه",
    "بالمذابح": "بِالمَذَابِحْ",
    "مآتمنه": "مَآتِمْنَا",
    "مآتمنا": "مَآتِمْنَا",
    "يلمنه": "يِلِمْنَا",
    "يلمنا": "يِلِمْنَا",
    "أمنه": "أُمْنَا",
    "أمنا": "أُمْنَا",
    "قايمنه": "قَايِمْنَا",
    "قايمنا": "قَايِمْنَا",
    "المعزى": "المُعَزَّا",
    "أنعى": "أَنْعَا",
    "بالدما": "بِالدِّمَا",
    "بطه": "أَبْطَا",
    "أبطى": "أَبْطَا",
    "قائم": "قَايِمْ",
    "قايم": "قَايِمْ",
    "للثائرين": "لِلثَّايْرِينْ",
    "للثايرين": "لِلثَّايْرِينْ",
    "أشكال": "أَشْكَالْ",
    "اشكال": "أَشْكَالْ",
    "ودعتك": "وَدَّعْتَكْ",
    "عزه": "عِزَّه",
    "عزة": "عِزَّه",
    "غزه": "غُزَّه",
    "غزة": "غُزَّه",
    "معزه": "مَعَزَّه",
    "معزة": "مَعَزَّه",
    "معتزه": "مِعْتَزَّه",
    "معتزة": "مِعْتَزَّه",
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
    "انجسم": "انْگِسَمْ",
    "انگسم": "انْگِسَمْ",
    "أنشدك": "أَنْشِدَكْ",
    "انشدك": "أَنْشِدَكْ",
    "إفادي": "إِفَّادِي",
    "افادي": "إِفَّادِي",
    "حذلم": "حَذْلَمْ",
    "مچتوف": "مَچْتُوفْ",
    "موذر": "مُوذَرْ",
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
    "شلونش": "إِشْلُونِشْ",
    "عيونش": "عِيُونِشْ",
    "دمعش": "دَمْعِشْ",
    "خدرش": "خِدْرِشْ",
    "بيتش": "بَيتِشْ",
    "روحش": "رُوحِشْ",
    "حالش": "حَالِشْ",
    "شفتش": "شِفْتِشْ",
    "ويش": "وِيشْ",
    "شنهو": "شِنْهُو",
    "أحين": "أَحِينْ",
    "احين": "أَحِينْ",
    "إلين": "إِلَينْ",
    "فجر": "فَجِرْ",
    "بحر": "بَحِرْ",
    "نصر": "نَصِرْ",
    "متن": "مَتِنْ",
    "بدر": "بَدِرْ",
    "ذكر": "ذِكِرْ",
    "صدر": "صَدِرْ",
    "گعد": "گِعَدْ",
    "گاعد": "گَاعِدْ",
    "مشينه": "مِشِينَه",
    "بچينه": "بِچِينَه",
    "ضلوع": "ضْلُوعْ",
    "ضل": "ضَلْ",
    "ضلت": "ضَلَّتْ",
    "ضليت": "ضَلَّيتْ",
    "ظليت": "ضَلَّيتْ",
    "يوبه": "يُوبَه",
    "اعلى": "إِعْلَى",
    "عالصدر": "عَالصَّدِرْ",
    "عالغبره": "عَالْغَبْرَه",
    "عالغبرة": "عَالْغَبْرَه",
    "گلبه": "گَلْبَه",
    "بيه": "بِيهْ",
    "نحره": "نَحْرَه",
    "جسمه": "جِسْمَه",
    "جَمَد": "جِمَدْ",
    "بقى": "بِقَى",
    "جَزِم": "جَزِمْ",
    "مَر": "مَرْ",
    "أْو": "وَ",
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
    "شلونش": "إِشْلُونِشْ",
    "عيونش": "عِيُونِشْ",
    "دمعش": "دَمْعِشْ",
    "خدرش": "خِدْرِشْ",
    "بيتش": "بَيتِشْ",
    "روحش": "رُوحِشْ",
    "حالش": "حَالِشْ",
    "شفتش": "شِفْتِشْ",
    "ويش": "وِيشْ",
    "شنهو": "شِنْهُو",
    "أحين": "أَحِينْ",
    "احين": "أَحِينْ",
    "إلين": "إِلَينْ",
    "فجر": "فَجِرْ",
    "بحر": "بَحِرْ",
    "نصر": "نَصِرْ",
    "متن": "مَتِنْ",
    "بدر": "بَدِرْ",
    "ذكر": "ذِكِرْ",
    "صدر": "صَدِرْ",
    "گعد": "گِعَدْ",
    "گاعد": "گَاعِدْ",
    "مشينه": "مِشِينَه",
    "بچينه": "بِچِينَه",
    "ضلوع": "ضْلُوعْ",
    "ضل": "ضَلْ",
    "ضلت": "ضَلَّتْ",
    "ضليت": "ضَلَّيتْ",
    "ظليت": "ضَلَّيتْ",
    "يوبه": "يُوبَه",
    "اعلى": "إِعْلَى",
    "عالصدر": "عَالصَّدِرْ",
    "عالغبره": "عَالْغَبْرَه",
    "عالغبرة": "عَالْغَبْرَه",
    "گلبه": "گَلْبَه",
    "بيه": "بِيهْ",
    "نحره": "نَحْرَه",
    "جسمه": "جِسْمَه",
    "جَمَد": "جِمَدْ",
    "بقى": "بِقَى",
    "جَزِم": "جَزِمْ",
    "مَر": "مَرْ",
    "أْو": "وَ",
}

# V52.0 Corpus-Validated High-Frequency Iraqi/Husseini Lexicon, Kaf-Fatha & Daad/Dhaa Locks
KAF_FATHA_TO_GAF_LEXICON = {
    "كَلب": "گَلُبْ",
    "كَلبي": "گَلْبِي",
    "كَلبك": "گَلْبَكْ",
    "كَلبه": "گَلْبَه",
    "كَلبها": "گَلْبْهَا",
    "وكَلبه": "وَ گَلْبَه",
    "لكَبر": "لِـ گَبِرْ",
    "كَبر": "گَبِرْ",
    "كَبره": "گَبْرَه",
    "تخنكَني": "تِخْنِگْنِي",
    "ينكَل": "يِنْگِلْ",
    "خانكَته": "خَانِگْتَه",
    "خانكَني": "خَانِگْنِي",
    "الفركَه": "الفِرْگَه",
    "فركَه": "فِرْگَه",
    "فركَتك": "فِرْگِتَكْ",
    "فركَتهم": "فِرْگَتْهُمْ",
    "ابفركَتك": "إِبْفِرْگِتَكْ",
    "فاكَد": "فَاگِدْ",
    "فاكَدين": "فَاگْدِينْ",
    "ملكَاك": "مَلْگَاكْ",
    "الكَفه": "الگِفَه",
    "كَفاه": "گِفَاهْ",
    "كَعد": "گِعَدْ",
    "كَعدت": "گَعْدَتْ",
    "وكَع": "وُگَعْ",
    "وكَف": "وُگَفْ",
    "تندكَ": "تِنْدَگْ",
    "مكَطوع": "مَگْطُوعْ",
    "مكَطوعه": "مَگْطُوعَه",
    "المكَطع": "المْگَطَّعْ",
    "تكًول": "تْگُولْ",
    "تكول": "تْگُولْ",
    "تكَول": "تْگُولْ",
    "دكَول": "دْگُولْ",
    "ادكَول": "تِدْگُولْ",
    "يالتكَول": "يَالْتِگُولْ",
    "كَالو": "گَالَوْ",
    "وكَالت": "وَ گَالَتْ",
    "لكَيت": "لِگَيتْ",
    "لكَيته": "لِگَيتَه",
    "يلكَه": "يِلْگَه",
    "وتلكَه": "وَ تِلْگَه",
    "عكَب": "عُگُبْ",
    "عكَبه": "عُگْبَه",
    "بكَاع": "إِبْگَاعْ",
    "الكَاع": "الگَاعْ",
    "كَاع": "گَاعْ",
    "كَمر": "گَمَرْ",
    "شكَد": "إِشْگَدْ",
    "كَدامك": "گِدَّامَكْ",
    "كَبلك": "گَبْلَكْ",
    "كَبله": "گَبْلَه",
    "كَامت": "گَامَتْ",
    "كَمت": "گِمِتْ",
    "كَوه": "گُوَّه",
    "اكَدر": "أَگْدَرْ",
    "فوكَاهه": "فُوگَاهَا",
    "ابكَربه": "إِبْگُرْبَه",
    "شبكَته": "شِبْگَتَه",
    "اتشاكَف": "إِتْشَاگَفْ",
    "وباكَك": "وَ بَاگَكْ",
    "وتنكَضي": "وَ تِنْگِضِي",
    "تكَطر": "تْگَطِّرْ",
    "وتكَنطر": "وَ تْگَنْطَرْ",
    "كَظيان": "گِضْيَانْ",
    "اكَظيهم": "أَگْضِيهُمْ",
    "تشكَ": "تِشِگْ",
    "حلكَ": "حَلِگْ",
}

DAAD_DHAA_SPELLING_FIX_MAP = {
    "الغاظريه": "الغَاضْرِيَّه",
    "الغاظرية": "الغَاضْرِيَّه",
    "للغاظريه": "لِلْغَاضْرِيَّه",
    "أظلوع": "أَضْلُوعْ",
    "اظلوع": "أَضْلُوعْ",
    "اضلوعنه": "أَضْلُوعْنَه",
    "الظلوع": "الضُّلُوعْ",
    "أظلاع": "أَضْلَاعْ",
    "اظلاع": "أَضْلَاعْ",
    "فظه": "فِضَّه",
    "بفظه": "بِفِضَّه",
    "مظيف": "مَضِيفْ",
    "لمظيفه": "لِمَضِيفَه",
    "ومظيفه": "وَ مَضِيفَه",
    "ارظ": "أَرْضْ",
    "أرظ": "أَرْضْ",
    "ظرب": "ضَرَبْ",
    "ظربو": "ضَرَبُو",
    "ظربوه": "ضَرَبُوه",
    "تنظرب": "تِنْضَرِبْ",
    "انضر": "أَنْظُرْ",
    "أنضر": "أَنْظُرْ",
    "انضرلك": "أَنْظُرْلَكْ",
    "تنضر": "تِنْظُرْ",
    "هالتنضر": "هَلْتِنْظُرْ",
    "ينضر": "يِنْظُرْ",
    "نضر": "نَظَرْ",
    "نضره": "نَظْرَه",
    "نضرة": "نَظْرَه",
    "نضرات": "نَظْرَاتْ",
    "نضراته": "نَظْرَاتَه",
    "ناضر": "نَاظِرْ",
    "الناضرين": "النَّاظْرِينْ",
    "لحضه": "لَحْظَه",
    "لحضة": "لَحْظَه",
    "بلحضه": "بْلَحْظَه",
    "لحضرته": "لْحَضْرْتَه",
    "لحضات": "لَحْظَاتْ",
    "حظرت": "حَضْرَتْ",
    "اليحظر": "اليِحْضَرْ",
    "ضالم": "ظَالِمْ",
    "الضالم": "الظَّالِمْ",
    "ضلمه": "ظُلْمَه",
    "ضلمة": "ظُلْمَه",
    "الضلمه": "الظُّلْمَه",
    "ضلام": "ظَلَامْ",
    "الضلام": "الظَّلَامْ",
    "هالضلام": "هَلظَّلَامْ",
    "ضهر": "ظَهَرْ",
    "بضهر": "بِظَهَرْ",
    "ضهره": "ظَهْرَه",
    "بضهره": "بِظَهْرَه",
    "وبضهره": "وَ بْظَهْرَه",
    "مضلوم": "مَظْلُومْ",
    "مضلومه": "مَظْلُومَه",
    "يضل": "يِظَلْ",
    "تضل": "تِظَلْ",
    "ماضل": "مَا ظَلْ",
    "ضلت": "ظَلَّتْ",
    "ضليت": "ظَلَّيتْ",
    "ضلينه": "ظَلَّينَه",
    "فاصل": "فَاضِلْ",
}

COMMON_CORPUS_LEXICON_V52 = {
    "من": "مِنْ",
    "يا": "يَا",
    "ما": "مَا",
    "لا": "لَا",
    "بس": "بَسْ",
    "لو": "لَوْ",
    "مو": "مُو",
    "او": "أَوْ",
    "أو": "أَوْ",
    "الله": "اللّٰه",
    "والله": "وَ اللّٰه",
    "کل": "كِلْ",
    "كل": "كِلْ",
    "كله": "كِلَّه",
    "كلها": "كِلْهَا",
    "كلهم": "كِلْهُمْ",
    "كلشي": "كِلْشِي",
    "علي": "عَلِي",
    "حيدر": "حَيدَرْ",
    "عباس": "عَبَّاسْ",
    "العباس": "العَبَّاسْ",
    "ابوفاضل": "أَبُو فَاضِلْ",
    "أبوفاضل": "أَبُو فَاضِلْ",
    "يبوفاضل": "يَبُو فَاضِلْ",
    "ابو": "أَبُو",
    "أبو": "أَبُو",
    "يبن": "يَبِنْ",
    "ابن": "إِبِنْ",
    "ام": "أُمّ",
    "أم": "أُمّ",
    "امي": "أُمِّي",
    "أمي": "أُمِّي",
    "امها": "أُمَّهَا",
    "ابوها": "أَبُوهَا",
    "اخوها": "أَخُوهَا",
    "اخوي": "أَخُويْ",
    "أخوي": "أَخُويْ",
    "كلبي": "گَلْبِي",
    "وكلبي": "وَ گَلْبِي",
    "بكلبي": "إِبْگَلْبِي",
    "كلبه": "گَلْبَه",
    "وكلبه": "وَ گَلْبَه",
    "كلبها": "گَلْبْهَا",
    "كلبك": "گَلْبَكْ",
    "كال": "گَالْ",
    "وكال": "وَ گَالْ",
    "كالو": "گَالَوْ",
    "كالوا": "گَالَوْ",
    "كالت": "گَالَتْ",
    "كمر": "گَمَرْ",
    "الكمر": "الگَمَرْ",
    "ملكاك": "مَلْگَاكْ",
    "وكت": "وَكِتْ",
    "الوكت": "الوَكِتْ",
    "كلش": "كِلِّشْ",
    "اكدر": "أَگْدَرْ",
    "تكدر": "تِگْدَرْ",
    "كدام": "گِدَّامْ",
    "كدامك": "گِدَّامَكْ",
    "اوكف": "أَوْگَفْ",
    "أوكف": "أَوْگَفْ",
    "اه": "آهْ",
    "آه": "آهْ",
    "الآه": "الآهْ",
    "آيه": "آيَه",
    "الايه": "الآيَه",
    "ايه": "إِيَه",
    "أوف": "أُوفْ",
    "و": "وَ",
    "آ": "آ",
    "وي": "وِيْ",
    "ويه": "وِيَّه",
    "وياي": "وِيَّايْ",
    "وياه": "وِيَّاهْ",
    "وياهم": "وِيَّاهُمْ",
    "وياها": "وِيَّاهَا",
    "اويه": "وِيَّه",
    "اوياي": "وِيَّايْ",
    "اوياه": "وِيَّاهْ",
    "اليه": "إِلِيَّه",
    "واليه": "وَ إِلِيَّه",
    "ولو": "وَ لَوْ",
    "إحسين": "إِحْسَينْ",
    "سر": "سِرّ",
    "حب": "حُبّ",
    "الحب": "الحُبّ",
    "حبه": "حُبَّه",
    "هو": "هُوَ",
    "نور": "نُورْ",
    "نوره": "نُورَه",
    "بگلب": "إِبْگَلْبِ",
    "المحب": "المُحِبّ",
    "الصدگ": "الصِّدِگْ",
    "صدق": "صِدِگْ",
    "شنهو": "شِنْهُو",
    "تجلى": "تِجَلَّى",
    "صلى": "صَلَّى",
    "الجفن": "الجِفِنْ",
    "الاصل": "الأَصِلْ",
    "الأصل": "الأَصِلْ",
    "نصرش": "نَصْرِشْ",
    "اخوش": "أَخُوشْ",
    "أخوش": "أَخُوشْ",
    "وعلى": "وَ عَلَى",
    "الحرام": "الحَرَامْ",
    "اخت": "أُخِتْ",
    "يه": "يَه",
    "اي": "إِي",
    "أجه": "أَجَه",
    "اجه": "أَجَه",
    "راح": "رَاحْ",
    "راحت": "رَاحَتْ",
    "رد": "رَدْ",
    "ردت": "رِدَتْ",
    "عندي": "عِنْدِي",
    "فاطمه": "فَاطْمَه",
    "فاطمة": "فَاطْمَه",
    "الزهرا": "الزَّهْرَا",
    "الزهره": "الزَّهْرَه",
    "الزهرة": "الزَّهْرَه",
    "العقيله": "العَقِيلَه",
    "العقيلة": "العَقِيلَه",
    "السجاد": "السَّجَّادْ",
    "رقيه": "رُقَيَّه",
    "رقية": "رُقَيَّه",
    "القاسم": "القَاسِمْ",
    "الاكبر": "الأَكْبَرْ",
    "الأكبر": "الأَكْبَرْ",
    "مسلم": "مُسْلِمْ",
    "الحسن": "الحَسَنْ",
    "هذا": "هَذَا",
    "هذي": "هَذِي",
    "هاي": "هَايْ",
    "هسه": "هَسَّه",
    "مثل": "مِثِلْ",
    "ولا": "وَ لَا",
    "اهواي": "إِهْوَايْ",
    "هواي": "إِهْوَايْ",
    "احنه": "إِحْنَه",
    "احنا": "إِحْنَه",
    "واحنه": "وَ إِحْنَه",
    "يتامه": "يَتَامَى",
    "يتامى": "يَتَامَى",
    "ايتام": "أَيتَامْ",
    "أيتام": "أَيتَامْ",
    "عمتك": "عَمْتَكْ",
    "صرنه": "صِرْنَه",
    "صرنا": "صِرْنَه",
    "الي": "إِلِي",
    "إلي": "إِلِي",
    "النه": "إِلْنَه",
    "الشام": "الشَّامْ",
    "الكوفه": "الكُوفَه",
    "الكوفة": "الكُوفَه",
    "كربلا": "كَرْبَلَا",
    "كربله": "كَرْبَلَا",
    "كربلاء": "كَرْبَلَا",
    "الطف": "الطَّفْ",
    "الطفوف": "الطُّفُوفْ",
    "المشرعه": "المَشْرَعَه",
    "المشرعة": "المَشْرَعَه",
    "العلگمي": "العَلْگَمِي",
    "العلقمي": "العَلْگَمِي",
    "الفرات": "الفُرَاتْ",
    "النهر": "النَّهَرْ",
    "نهر": "نَهَرْ",
    "الماي": "المَايْ",
    "ماي": "مَايْ",
    "عطشان": "عَطْشَانْ",
    "سهم": "سَهَمْ",
    "السهم": "السَّهَمْ",
    "اسهام": "إِسْهَامْ",
    "رمح": "رُمُحْ",
    "الرمح": "الرُّمُحْ",
    "سيف": "سَيفْ",
    "السيف": "السَّيفْ",
    "خيمه": "خَيمَه",
    "خيمة": "خَيمَه",
    "الخيم": "الخِيَمْ",
    "العبايه": "العَبَايَه",
    "العباءه": "العَبَاءَه",
    "الراس": "الرَّاسْ",
    "راس": "رَاسْ",
    "النحر": "النَّحَرْ",
    "نحر": "نَحَرْ",
    "منحر": "مَنْحَرْ",
    "صدر": "صَدِرْ",
    "صدره": "صَدْرَه",
    "ضلع": "ضِلِعْ",
    "ضلعي": "ضِلْعِي",
    "البسمار": "البُسْمَارْ",
    "بسمار": "بُسْمَارْ",
    "حبل": "حَبِلْ",
    "احبال": "إِحْبَالْ",
    "السوط": "السُّوطْ",
    "سوط": "سُوطْ",
    "صوت": "صُوتْ",
    "الصوت": "الصُّوتْ",
    "النار": "النَّارْ",
    "نار": "نَارْ",
    "الخيل": "الخَيلْ",
    "خيل": "خَيلْ",
    "حوافر": "حَوَافِرْ",
    "التل": "التَّلْ",
    "الترب": "التُّرُبْ",
    "التراب": "التُّرَابْ",
    "تراب": "تُرَابْ",
    "الطريق": "الطَّرِيقْ",
    "درب": "دَرُبْ",
    "سبي": "سَبِي",
    "السبي": "السَّبِي",
    "مسبيه": "مَسْبِيَّه",
    "الهزل": "الهَزِلْ",
    "هزيله": "هَزِيلَه",
    "باچر": "بَاچِرْ",
    "گال": "گَالْ",
    "گالت": "گَالَتْ",
    "گلت": "گِلْتْ",
    "شوف": "شُوفْ",
    "شفت": "شِفِتْ",
    "شفته": "شِفْتَه",
    "گوم": "گُومْ",
    "ليش": "لَيشْ",
    "شلون": "إِشْلُونْ",
    "وحدي": "وَحْدِي",
    "وحده": "وَحْدَه",
    "الگمر": "الگَمَرْ",
    "گمر": "گَمَرْ",
    "الناس": "النَّاسْ",
    "العدا": "العِدَا",
    "العده": "العِدَه",
    "الشمر": "الشَّمِرْ",
    "الحسين": "الحُسَينْ",
    "ابو اليمه": "أَبُو اليِمَّه",
    "ماتت": "مَاتَتْ",
    "ذبحو": "ذِبْحَوْ",
    "ذبحوه": "ذَبْحُوهْ",
    "سبوها": "سَبُوهَا",
    "حركوها": "حَرْگُوهَا",
    "حرگوها": "حَرْگُوهَا",
    "ودوها": "وَدُّوهَا",
    "جتفوها": "چَتَّفُوهَا",
    "چتفوها": "چَتَّفُوهَا",
    "گعدت": "گَعْدَتْ",
    "نامت": "نَامَتْ",
    "فزت": "فَزَّتْ",
    "ابلا": "بِلَا",
    "ابلايه": "بِلَايَه",
    "والخيام": "وَ الخِيَامْ",
    "بالميدان": "بِالمَيدَانْ",
    "دورك": "دَورَكْ",
    "موسى": "مُوسَى",
    "سلام": "سَلَامْ",
    "نوح": "نُوحْ",
    "ينوح": "يِنُوحْ",
    "تبچي": "تِبْچِي",
    "ابچي": "إِبْچِي",
    "واحچي": "وَ أَحْچِي",
    "احچي": "أَحْچِي",
    "اسمع": "إِسْمَعْ",
    "انظر": "أَنْظُرْ",
    "وانظر": "وَ أَنْظُرْ",
    "اوگف": "أَوْگَفْ",
    "اودعها": "أَوَدِّعْهَا",
    "اودعهم": "أَوَدِّعْهُمْ",
    "امسح": "إِمْسَحْ",
    "اتنادي": "تِنَادِي",
    "اتشوف": "تِشُوفْ",
    "انذبح": "انْذِبَحْ",
    "انكسر": "انْكِسَرْ",
    "انگطع": "انْگِطَعْ",
    "بگت": "بِگَتْ",
    "بقت": "بِگَتْ",
    "بگيت": "بِگَيتْ",
    "بقيت": "بِگَيتْ",
    "بقه": "بِگَه",
    "خوان": "إِخْوَانْ",
    "خوّان": "إِخْوَانْ",
    "اخوان": "إِخْوَانْ",
    "إخوان": "إِخْوَانْ",
    "خواتي": "خَوَاتِي",
    # Module 70 (V55.0): 3-Benchmark-Poem Lexicon Locks (Tabaa Al-Bashar, Sowrat Jasad, Falsafat Al-Intidhar)
    "ينسه": "يِنْسَى",
    "ينسى": "يِنْسَى",
    "ماتنسه": "مَا تِنْسَى",
    "الوفه": "الوَفَا",
    "الوفا": "الوَفَا",
    "الوفاء": "الوَفَاءْ",
    "انته": "إِنْتَه",
    "أنته": "إِنْتَه",
    "وانته": "وَ إِنْتَه",
    "إنت": "إِنْتَ",
    "انت": "إِنْتَ",
    "اليزعلك": "اليِزَعْلَكْ",
    "بالفعل": "بِالفِعِلْ",
    "تفزعله": "تِفْزَعْلَه",
    "عثر": "عِثَرْ",
    "ناموسك": "نَامُوسَكْ",
    "بظل": "إِبْظِلِّ",
    "العرش": "العَرِشْ",
    "وتنزل": "وِتْنَزِّلْ",
    "هوى": "هَوَى",
    "للمختنگ": "لِلْمِخْتِنِگْ",
    "المختنگ": "المِخْتِنِگْ",
    "الخدمه": "الخِدْمَه",
    "الخدمة": "الخِدْمَه",
    "والخدمه": "وَ الخِدْمَه",
    "بالصدگ": "بِالصِّدِگْ",
    "وجذب": "وْچِذِبْ",
    "حاسبها": "حَاسِبْهَا",
    "حتى": "حَتَّى",
    "وحتى": "وَ حَتَّى",
    "المو": "المُو",
    "صدگ": "صِدِگْ",
    "أليه": "إِلِيَّه",
    "يساترني": "يْسَاتِرْنِي",
    "وتحط": "وِتْحُطْ",
    "أيدك": "إِيدَكْ",
    "ايدك": "إِيدَكْ",
    "إيدي": "إِيدِي",
    "ايدي": "إِيدِي",
    "عليه": "عَلَيَّه",
    "حنين": "حِنَيِّنْ",
    "وماگلت": "وَ مَا گِلِتْ",
    "ماگلت": "مَا گِلِتْ",
    "مره": "مَرَّه",
    "شعليه": "إِشْعَلَيَّه",
    "انكساري": "إِنْكِسَارِي",
    "الانكسار": "الِانْكِسَارْ",
    "الانتظار": "الِانْتِظَارْ",
    "ودمعتي": "وَ دَمْعِتِي",
    "دمعتي": "دَمْعِتِي",
    "قراري": "قَرَارِي",
    "بصفنتي": "بِصَفْنِتِي",
    "صفنتي": "صَفْنِتِي",
    "حامل": "حَامِلْ",
    "جمرتي": "جَمُرْتِي",
    "بديه": "بِيدَيَّه",
    "بديها": "بِيدَيهَا",
    "بديهن": "بِيدَيهِنْ",
    "وتطلع": "وِتْطَلِّعْ",
    "حسرتي": "حَسْرِتِي",
    "الحسره": "الحَسْرَه",
    "الرقيه": "الرُّقَيَّه",
    "ورقيه": "وَ رُقَيَّه",
    "سهرانه": "سَهْرَانَه",
    "وسهرانه": "وَ سَهْرَانَه",
    "عينك": "عَينَكْ",
    "بالدمع": "بِالدَّمِعْ",
    "بلا": "بِلَا",
    "يالتنسمع": "يَالْتِنْسِمِعْ",
    "لَمن": "لَمَّنْ",
    "لمن": "لَمَّنْ",
    "تون": "تِوِنْ",
    "ضحكي": "ضِحْكِي",
    "ينسمع": "يِنْسِمِعْ",
    "صديت": "صَدَّيتْ",
    "ماصديت": "مَا صَدَّيتْ",
    "ألي": "إِلِي",
    "ألك": "إِلَكْ",
    "بعين": "إِبْعَينِ",
    "العطف": "العَطُفْ",
    "عطفك": "عَطْفَكْ",
    "رازقني": "رَازِقْنِي",
    "غير": "غَيرْ",
    "أسئلك": "أَسْأَلَكْ",
    "وأسئلك": "وَ أَسْأَلَكْ",
    "ماتنتضرني": "مَا تِنْتِظِرْنِي",
    "تنتضرني": "تِنْتِظِرْنِي",
    "ترست": "تِرَسِتْ",
    "بعطائك": "إِبْعَطَائَكْ",
    "عطائك": "عَطَائَكْ",
    "جميلك": "جَمِيلَكْ",
    "يالمبللني": "يَالِمْبَلِّلْنِي",
    "دخيلك": "دَخِيلَكْ",
    "اتگلي": "تِگِلِّي",
    "هاك": "هَاكْ",
    "اجيلك": "أَجِيلَكْ",
    "منطيني": "مِنْطِينِي",
    "هيبه": "هَيبَه",
    "بردائك": "بِرِدَائَكْ",
    "ردائك": "رِدَائَكْ",
    "شيبه": "شَيبَه",
    "الشيبه": "الشَّيبَه",
    "بخدمتك": "إِبْخِدْمِتَكْ",
    "خدمتك": "خِدْمِتَكْ",
    "ملتني": "مِلَتْنِي",
    "زاير": "زَايِرْ",
    "حضرتك": "حَضْرِتَكْ",
    "جبتني": "جِبْتِنِي",
    "أتنومس": "أَتْنَومَسْ",
    "بفي": "إِبْفَيّ",
    "رحمتك": "رَحْمِتَكْ",
    "وماحسبت": "وَ مَا حِسَبِتْ",
    "ماحسبت": "مَا حِسَبِتْ",
    "بشمس": "إِبْشَمِسْ",
    "معقوله": "مَعْقُولَه",
    "خدك": "خَدَّكْ",
    "بالترب": "بِالتُّرُبْ",
    "ماعندي": "مَا عِنْدِي",
    "احساس": "إِحْسَاسْ",
    "وأحس": "وَ أَحِسْ",
    "يابس": "يَابِسْ",
    "رموشك": "رُمُوشَكْ",
    "دمه": "دِمَا",
    "تنفتح": "تِنْفِتِحْ",
    "نظره": "نَظْرَه",
    "النظره": "النَّظْرَه",
    "لخيامك": "لِخْيَامَكْ",
    "تصد": "تِصِدْ",
    "اليذبحونك": "اليِذِبْحُونَكْ",
    "أجو": "إِجَوْ",
    "گبل": "گَبُلْ",
    "لاتنذبح": "لَا تِنْذِبِحْ",
    "وتريد": "وِتْرِيدْ",
    "تريد": "تِرِيدْ",
    "ياويل": "يَا وَيلْ",
    "أجلك": "إِجَوْ لَكْ",
    "عشره": "عَشْرَه",
    "تشوفهن": "تِشُوفْهِنْ",
    "غبره": "غَبْرَه",
    "ياهو": "يَاهُو",
    "التحشمه": "التِحَشْمَه",
    "رميه": "رَمِيَّه",
    "رمية": "رَمْيَةِ",
    "التكلمه": "التِكَلْمَه",
    "دميه": "دَمِيَّه",
    "تاليها": "تَالِيهَا",
    "مطرت": "مِطْرَتْ",
    "وروحك": "وَ رُوحَكْ",
    "تعلت": "تِعَلَّتْ",
    "بواتر": "بَوَاتِرْ",
    "طايح": "طَايِحْ",
    "يغربيل": "يَغِرْبِيلْ",
    "الزلم": "الزِّلِمْ",
    "يمغربل": "يِمْغَرْبِلْ",
    "الدنيا": "الدِّنْيَا",
    "بنحر": "إِبْنَحَرْ",
    "عايش": "عَايِشْ",
    "بريبه": "إِبْرَيبَه",
    "ثيابك": "ثِيَابَكْ",
    "ماعبر": "مَا عِبَرْ",
    "ساوموك": "سَاوِمُوكْ",
    "أعله": "إِعْلَه",
    "الطفل": "الطِّفِلْ",
    "رجعت": "رَجَّعِتْ",
    "واحد": "وَاحِدْ",
    "أبد": "أَبَدْ",
    "رزقه": "رِزْقَه",
    "مرزوقه": "مَرْزُوقَه",
    "بمهد": "إِبْمَهَدْ",
    "ماخليت": "مَا خَلَّيتْ",
    "خليت": "خَلَّيتْ",
    "يوم": "يُومْ",
    "عاشر": "عَاشِرْ",
    "بضناك": "إِبْضَنَاكْ",
    "معزب": "مْعَزِّبْ",
    "حلوگ": "إِحْلُوگْ",
    "الخناجر": "الخَنَاجِرْ",
    "وصدرك": "وَ صَدْرَكْ",
    "صدرك": "صَدْرَكْ",
    "معبر": "مَعْبَرْ",
    "للحوافر": "لِلْحَوَافِرْ",
    "جاسم": "جَاسِمْ",
    "فديته": "فِدَيتَه",
    "بشهامه": "بِشَهَامَه",
    "نطيته": "نِطَيتَه",
    "بهيامه": "إِبْهِيَامَه",
    "هيامه": "هِيَامَه",
    "الرزيه": "الرَّزِيَّه",
    "خوله": "خَولَه",
    "سبيهن": "سَبِيهِنْ",
    "أختصر": "أَخْتَصِرْ",
    "الحدث": "الحَدَثْ",
    "أستعجِل": "أَسْتَعْجِلْ",
    "استعجل": "أَسْتَعْجِلْ",
    "الظهيره": "الظَّهِيرَه",
    "شي": "شِي",
    "ومن": "وَ مِنَ",
    "وامن": "وَ إِمْنِ",
    "الصبح": "الصُّبُحْ",
    "كسيره": "كَسِيرَه",
    "واندفن": "وَ انْدِفَنْ",
    "وجه": "وَجْهِ",
    "وجهه": "وَجْهَه",
    "والكل": "وَ الكِلْ",
    "جمد": "جِمَدْ",
    "في": "فِي",
    "حيره": "حِيرَه",
    "مات": "مَاتْ",
    "رحل": "رَحَلْ",
    "إلاّ": "إِلَّا",
    "إلا": "إِلَّا",
    "الحُسين": "الحُسَينْ",
    "والحُسين": "وَ الحُسَينْ",
    "وحُبّه": "وَ حُبَّه",
    "الوكِت": "الوَكِتْ",
    "اللحظه": "اللَّحْظَه",
    "غُربه": "غُرْبَه",
    "غربه": "غُرْبَه",
    "إسم": "إِسْمِ",
    "اسمه": "إِسْمَه",
    "الأمل": "الأَمَلْ",
    "والعيشه": "وَ العِيشَه",
    "العيشه": "العِيشَه",
    "صارت": "صَارَتْ",
    "صعبه": "صَعْبَه",
    "نبض": "نَبْضِ",
    "الشمس": "الشَّمِسْ",
    "واحسين": "وَ احْسَينْ",
    "يوزع": "يِوَزِّعْ",
    "گلبه": "گَلْبَه",
    "وگلبه": "وَ گَلْبَه",
    "أحچي": "أَحْچِي",
    "عن": "عَنْ",
    "حجر": "حَجَرْ",
    "دم": "دَمْ",
    "السما": "السَّمَا",
    "منها": "مِنْهَا",
    "انفجر": "انْفِجَرْ",
    "مر": "مَرْ",
    "وخلص": "وَ خِلَصْ",
    "هالمشهد": "هَلْمَشْهَدْ",
    "ذاك": "ذَاكْ",
    "صورته": "صُورْتَه",
    "الصوره": "الصُّورَه",
    "الصور": "الصُّوَرْ",
    "صوره": "صُورَه",
    "صورة": "صُورَةْ",
    "الأهم": "الأَهَمْ",
    "طاح": "طَاحْ",
    "وتعب": "وَ تِعَبْ",
    "اتوسّد": "اتْوَسَّدْ",
    "اتوسد": "اتْوَسَّدْ",
    "واتوسّد": "وَ اتْوَسَّدْ",
    "أطويها": "أَطْوِيهَا",
    "خل": "خَلْ",
    "الزمن": "الزَّمَنْ",
    "يرويها": "يِرْوِيهَا",
    "وحيده": "وَحِيدَه",
    "اللي": "اللِّي",
    "تظل": "تِظَلْ",
    "يظل": "يِظَلْ",
    "أوگف": "أَوْگَفْ",
    "بحسره": "إِبْحَسْرَه",
    "جسد": "جَسَدْ",
    "عالغبره": "عَالْغَبْرَه",
    "جرح": "جَرِحْ",
    "يبره": "يِبْرَه",
    "ومحد": "وَ مَحَّدْ",
    "حرّك": "حَرَّكْ",
    "حرك": "حَرَّكْ",
    "رمش": "رِمِشْ",
    "يشد": "يِشِدْ",
    "مرمي": "مَرْمِي",
    "الترايب": "التَّرَايِبْ",
    "بالناب": "بِالنَّابْ",
    "وبالمخالب": "وَ بِالمَخَالِبْ",
    "بالمخالب": "بِالمَخَالِبْ",
    "وجسمه": "وَ جِسْمَه",
    "ذايب": "ذَايِبْ",
    "بيه": "بِيهْ",
    "بيها": "بِيهَا",
    "الحقد": "الحِقِدْ",
    "لواهب": "لَوَاهِبْ",
    "حين": "حِينْ",
    "التمر": "التِمُرْ",
    "تمر": "تِمُرْ",
    "يتحوّل": "يِتْحَوَّلْ",
    "يتحول": "يِتْحَوَّلْ",
    "العالم": "العَالَمْ",
    "اعلى": "إِعْلَى",
    "الثرى": "الثَّرَى",
    "صاعد": "صَاعِدْ",
    "صعد": "صِعَدْ",
    "حافي": "حَافِي",
    "بعد": "بَعَدْ",
    "بنعاله": "بِانْعَالَه",
    "انعاله": "إِنْعَالَه",
    "جالس": "جَالِسْ",
    "عالصدر": "عَالصَّدِرْ",
    "الصدر": "الصَّدِرْ",
    "اشيريد": "إِشْيِرِيدْ",
    "ياربي": "يَا رَبِّي",
    "الصبر": "الصَّبِرْ",
    "طوّل": "طَوَّلْ",
    "طول": "طَوَّلْ",
    "جلوسه": "جُلُوسَه",
    "يناظر": "يِنَاظِرْ",
    "للخدر": "لِلْخِدِرْ",
    "وش": "وِشْ",
    "ناوي": "نَاوِي",
    "تفعل": "تِفْعَلْ",
    "شمر": "شِمِرْ",
    "تستحي": "تِسْتَحِي",
    "إتخيّل": "إِتْخَيَّلْ",
    "اتخيل": "إِتْخَيَّلْ",
    "استقر": "اسْتِقَرْ",
    "يم": "يَمْ",
    "رقبته": "رَقْبِتَه",
    "صوب": "صُوبْ",
    "يتخطى": "يِتْخَطَّى",
    "ويخلي": "وَ يْخَلِّي",
    "أثر": "أَثَرْ",
    "يالواطي": "يَالْوَاطِي",
    "راقب": "رَاقِبْ",
    "قبض": "قَبَضْ",
    "وبقى": "وَ بِقَى",
    "يحز": "يِحِزْ",
    "بمنحره": "إِبْمَنْحَرَه",
    "مشى": "مِشَى",
    "سيفه": "سَيفَه",
    "سيفك": "سَيفَكْ",
    "يهبّره": "يِهَبْرَه",
    "يهبره": "يِهَبْرَه",
    "ناحت": "نَاحَتْ",
    "الأكوان": "الأَكْوَانْ",
    "الدهر": "الدَّهَرْ",
    "خجلان": "خَجْلَانْ",
    "الأرض": "الأَرِضْ",
    "ماجت": "مَاجَتْ",
    "حمره": "حَمْرَه",
    "حزّيت": "حَزَّيتْ",
    "حزيت": "حَزَّيتْ",
    "منحره": "مَنْحَرَه",
    "نبي": "نَبِي",
    "مرسول": "مَرْسُولْ",
    "منقطع": "مُنْقَطِعْ",
    "كافر": "كَافِرْ",
    "مجرم": "مُجْرِمْ",
    "فاجر": "فَاجِرْ",
    "فعلتك": "فَعْلِتَكْ",
    "شنيعه": "شَنِيعَه",
    "ظالم": "ظَالِمْ",
    "واهم": "وَاهِمْ",
    "النادم": "النَّادِمْ",
    "يذبح": "يِذْبَحْ",
    "الشريعه": "الشَّرِيعَه",
    "تطلب": "تِطْلُبْ",
    "نعيم": "نَعِيمْ",
    "راحه": "رَاحَه",
    "فوز": "فَوزْ",
    "مغنم": "مَغْنَمْ",
    "تمشي": "تِمْشِي",
    "يمشي": "يِمْشِي",
    "جراحه": "جِرَاحَه",
    "المُستقر": "المُسْتَقَرْ",
    "المستقر": "المُسْتَقَرْ",
    "جهنم": "جَهَنَّمْ",
    "يتملك": "يِتْمَلَّكْ",
    "المشاعر": "المَشَاعِرْ",
    "ينكتب": "يِنْكِتِبْ",
    "خلوده": "خُلُودَه",
    "ويصبح": "وَ يِصْبِحْ",
    "الشعاير": "الشَّعَايِرْ",
    "والمجِد": "وَ المَجِدْ",
    "المجد": "المَجِدْ",
    "نصيبه": "نَصِيبَه",
    "وايامه": "وَ أَيَّامَه",
    "ايامها": "أَيَّامْهَا",
    "ايام": "أَيَّامْ",
    "تتبعه": "تِتْبَعَه",
    "بدماها": "إِبْدِمَاهَا",
    "للمحشر": "لِلْمَحْشَرْ",
    "المناحر": "المَنَاحِرْ",
    "مظلوم": "مَظْلُومْ",
    "محروم": "مَحْرُومْ",
    "يعيش": "يِعِيشْ",
    "ايعيش": "يْعِيشْ",
    "بكل": "إِبْكِلْ",
    "ثابت": "ثَابِتْ",
    "مُخلد": "مُخَلَّدْ",
    "مخلد": "مُخَلَّدْ",
    "للقيامه": "لِلْقِيَامَه",
    "إخسأ": "إِخْسَأْ",
    "دست": "دِسِتْ",
    "داستك": "دَاسِتَكْ",
    "أقدام": "أَقْدَامْ",
    "الليالي": "اللَّيَالِي",
    "واجزِم": "وَ أَجْزِمْ",
    "واجزم": "وَ أَجْزِمْ",
    "لك": "لَكْ",
    "جزم": "جَزِمْ",
    "منهزم": "مُنْهَزِمْ",
    "انتصر": "انْتَصَرْ",
    "يبالي": "يِبَالِي",
    "فلسفة": "فَلْسَفَة",
    "وفلسفة": "وَ فَلْسَفَة",
    "للغايب": "لِلْغَايِبْ",
    "الغايب": "الغَايِبْ",
    "غايب": "غَايِبْ",
    "غايبها": "غَايِبْهَا",
    "غايبه": "غَايْبَه",
    "باختصار": "بِاخْتِصَارْ",
    "اترجمها": "إِتْرَجْمَهَا",
    "البنين": "البَنِينْ",
    "كلمن": "كِلْمَنْ",
    "منتظر": "مُنْتَظِرْ",
    "منتظره": "مُنْتَظْرَه",
    "امن": "إِمْنِ",
    "الوله": "الوَلَه",
    "بغمار": "إِبْغِمَارْ",
    "وجوب": "وُجُوبْ",
    "ايخوض": "يْخُوضْ",
    "يقره": "يِقْرَه",
    "اتعلم": "إِتْعَلَّمْ",
    "يمن": "يَمَنْ",
    "يامن": "يَا مَنْ",
    "للمهدي": "لِلْمَهْدِي",
    "دمعتها": "دَمْعَتْهَا",
    "تهل": "تِهِلْ",
    "ودموع": "وَ دُمُوعْ",
    "ناطر": "نَاطِرْ",
    "وحچي": "وَ حَچِي",
    "اسمعونك": "يْسَمْعُونَكْ",
    "تره": "تَرَى",
    "الاربعه": "الأَرْبَعَه",
    "قبلك": "گَبْلَكْ",
    "شبعت": "شِبْعَتْ",
    "لوم": "لُومْ",
    "المامذبوحله": "المَا مَذْبُوحْ لَه",
    "ادم": "آدَمْ",
    "ايسولف": "يْسُولِفْ",
    "حقه": "حَقَّه",
    "ماملچوم": "مَا مَلْچُومْ",
    "والرايحله": "وَ الرَّايِحْ لَه",
    "اليمه": "اليِمَّه",
    "عاديه": "عَادِيَّه",
    "يطلگ": "يِطَلِّگْ",
    "النوم": "النُّومْ",
    "والحدر": "وَ الحَدِرْ",
    "اعيونه": "إِعْيُونَه",
    "اعيونك": "إِعْيُونَكْ",
    "اعيونچ": "إِعْيُونِچْ",
    "عالم": "عَالَمْ",
    "حبها": "حُبْهَا",
    "رايد": "رَايِدْ",
    "اتدرسه": "إِتْدَرْسَه",
    "ابحب": "إِبْحُبّ",
    "ابحث": "إِبْحَثْ",
    "اخذه": "إِخْذَه",
    "وطبقه": "وَ طَبْقَه",
    "بنفسه": "إِبْنَفْسَه",
    "اساس": "أَسَاسْ",
    "المعرفه": "المَعْرِفَه",
    "القصوى": "القُصْوَى",
    "وكون": "وَ كُونْ",
    "الامامك": "لإِمَامَكْ",
    "شوگك": "شُوگَكْ",
    "شوگه": "شُوگَه",
    "ايقل": "يْقِلْ",
    "اترسه": "إِتْرِسَه",
    "اشواگك": "أَشْوَاگَكْ",
    "مهما": "مَهْمَا",
    "صار": "صَارْ",
    "الكربلا": "لْكَرْبَلَا",
    "الحلوه": "الحِلْوَه",
    "مانسمه": "مَا نَسْمَه",
    "بالطاهره": "بِالطَّاهِرَه",
    "تهوه": "تِهْوَه",
    "اعز": "أَعَزْ",
    "مانمتلك": "مَا نِمْتِلِكْ",
    "تعلمنه": "تِعَلَّمْنَه",
    "اله": "إِلَه",
    "فدوه": "فِدْوَه",
    "بلايه": "بِلَايَه",
    "انفاس": "أَنْفَاسْ",
    "صالح": "صَالِحْ",
    "ماتسوه": "مَا تِسْوَه",
    "انگول": "نْگُولْ",
    "البذار": "البِذَارْ",
    "اتسولف": "تِسُولِفْ",
    "والدمعات": "وَ الدَّمْعَاتْ",
    "هوه": "هُوَّه",
    "الفارگ": "الفَارَگْ",
    "احبابه": "أَحْبَابَه",
    "روحه": "رُوحَه",
    "اتضل": "تِظَلْ",
    "تواليها": "تِوَالِيهَا",
    "تشتاگه": "تِشْتَاگَه",
    "حاچيها": "حَاچِيهَا",
    "گلها": "گِلْهَا",
    "ابداعة": "إِبْدَاعَة",
    "بيش": "بِيشْ",
    "اطفيها": "أَطَفِّيهَا",
    "الدمعه": "الدَّمْعَه",
    "ونهار": "وَ نَهَارْ",
    "المثل": "المِثِلْ",
    "ينطر": "يِنْطُرْ",
    "اعوام": "أَعْوَامْ",
    "شما": "شْمَا",
    "يحاچونه": "يِحَاچُونَه",
    "المشتاگ": "المِشْتَاگْ",
    "ماينلام": "مَا يِنْلَامْ",
    "المنذبح": "المِنْذِبِحْ",
    "متفزز": "مِتْفَزِّزْ",
    "اجروحه": "جُرُوحَه",
    "إسهام": "إِسْهَامْ",
    "اليدور": "اليِدَوِّرْ",
    "مستعد": "مِسْتَعِدْ",
    "والاحزانه": "وَ لأَحْزَانَه",
    "جهار": "جِهَارْ",
    "جَمَد": "جِمَدْ",
    "بقى": "بِقَى",
    "جَزِم": "جَزِمْ",
    "مَر": "مَرْ",
    "أْو": "وَ",
    "نحره": "نَحْرَه",
    "جسمه": "جِسْمَه",
    "الكربله": "لْكَرْبَلَا",
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


def format_kasra_three_vertical_lines(kasra_lines):
    """Module 66 (NC16 — 23.5s Extend Window Law): Format a Kasra into strictly 3 vertical lines.

    Combines Hemistich 1 and Hemistich 2 on Line 1, keeps Hemistich 3 on Line 2, places the
    closing Qafla couplet on Line 3, and removes any redundant 5th parenthetical choral echo line
    during Extend stages so the 23.5s window sings 100% of the Qafla without cutoff.
    """
    if isinstance(kasra_lines, str):
        raw_list = [ln.strip() for ln in kasra_lines.splitlines() if ln.strip()]
    else:
        raw_list = [str(ln).strip() for ln in kasra_lines if str(ln).strip()]

    header = None
    content = []
    for item in raw_list:
        if item.startswith("[") and item.endswith("]"):
            header = item
        elif not (item.startswith("(") and (item.endswith(")") or item.endswith(") .."))):
            norm_item = item if item.endswith("..") else f"{item} .."
            content.append(norm_item)

    if len(content) == 4:
        h1 = content[0][:-2].strip()
        h2 = content[1][:-2].strip()
        three_lines = [
            f"{h1} .. {h2} ..",
            content[2],
            content[3],
        ]
    else:
        three_lines = content[:3]

    if header:
        return [header] + three_lines
    return three_lines


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
            out_chunks.append("\n".join(wrapped_lines) + ("\n" if chunk.endswith("\n") else ""))
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
            out_chunks.append("\n".join(wrapped_lines) + ("\n" if chunk.endswith("\n") else ""))
        else:
            out_chunks.append(chunk)
    return "".join(out_chunks)


def _format_tatweel(text_val, use_tatweel=False):
    """Return text with Tatweel preserved if use_tatweel=True, else clean space-separated."""
    if use_tatweel:
        return text_val
    return re.sub(r"\s+", " ", text_val.replace("ـ", "")).strip()


def sanitize_poem_decorations(text):
    """Module 68 (V53.0): Strip emojis, channel dividers, inline kashida, and poet banners safely."""
    out_lines = []
    boilerplate_prefixes = (
        "تمت",
        "الشاعر",
        "كلمات",
        "الرادود",
        "اداء",
        "أداء",
        "اللهم صل على محمد",
        "اللهم عجل لوليك",
        "السلام على الحسين",
        "قصائد حسينية مكتوبة",
        "قثائد حسينية مكتوبة",
        "قصائد محرم",
        "قصائد السبي",
        "المجموعة الا",
        "المجموعة الث",
        "المجموعة الر",
        "المجموعة الخ",
        "المجموعة الس",
        "المجموعة الت",
        "لايسمح",
        "لا يسمح",
        "نسألكم الدعاء",
        "نسالكم الدعاء",
        "الفاتحه لروح",
        "الفاتحة لروح",
        "رابط ",
    )
    arabic_letter_re = re.compile(r"[\u0621-\u064A\u067E\u0686\u06AF]")
    for raw_ln in text.splitlines():
        stripped_ln = raw_ln.strip()
        if not stripped_ln:
            continue
        if stripped_ln.startswith(("#", "✍")):
            continue
        if re.fullmatch(r"[\s💔❤😭✏★☆۞◆◇▪✦🙨🙜❀✿↻↺✍•●○■□►◄▲▼#@+*~=_ـ./\\|\-،:؛؟!⊰⊱─═\d\u0660-\u0669⁰¹²³⁴⁵⁶⁷⁸⁹()]+", stripped_ln):
            continue

        cleaned = raw_ln.replace("\u06C6", "و ").replace("\u06A9", "ك").replace("\u06AA", "ك").replace("\u06CC", "ي").replace("\u06BE", "ه")
        cleaned = re.sub(r"[💔❤😭✏★☆۞◆◇▪✦🙨🙜❀✿↻↺✍•●○■□►◄▲▼#@+*~=_/\\|\-«»\"“”⊰⊱─═⁰¹²³⁴⁵⁶⁷⁸⁹]+", " ", cleaned)
        cleaned = re.sub(r"\(\s*[عس]\s*\)", " ", cleaned)
        cleaned = re.sub(r"ك(?:\u064e\u0640|\u0640\u064e|\u064b)", "گ", cleaned)
        # Heal mid-word expressive poet kashida (ـ) without breaking spacing
        cleaned = re.sub(
            r"(?<=[\u0621-\u064A\u064B-\u0652\u067E\u0686\u06AF])\u0640+(?=[\u0621-\u064A\u064B-\u0652\u067E\u0686\u06AF])",
            "",
            cleaned,
        )
        cleaned = re.sub(r"\s+\u0640+\s+|\s+\u0640+$|^\u0640+\s+", " ", cleaned)
        cleaned = re.sub(r"(?<!\.)\.\.(?!\.)", " .. ", cleaned)
        cleaned = re.sub(r"\.{3,}|…", " .. ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not cleaned or not arabic_letter_re.search(cleaned):
            continue

        bare = re.sub(r"[\u064B-\u0652\s:.،؛/\\0-9\u0660-\u0669]", "", cleaned)
        if not bare:
            continue
        if any(bare.startswith(p.replace(" ", "")) for p in boilerplate_prefixes):
            continue
        if len(cleaned.split()) <= 4 and re.search(r"(?:^|\s)(?:خادم|الخادم|الكربلائي|الدراجي|الخفاجي|البديري|الشويلي|الطائي|الشاعر|الركابي|الغنامي|الابراهيمي|البزوني|المياحي|الخيكاني|العكيلي|المبارك|السعيدي|الربيعي|اللامي|العارضي|الذبحاوي|الجحيشي)(?:\s|$)", cleaned):
            continue
        out_lines.append(cleaned)
    return "\n".join(out_lines)


def normalize_iraqi_orthographic_gaf(text):
    """Normalize Swash Kaf, Kaf+Fatha/Tanween+Tatweel, and attested Iraqi Kaf+Fatha Gaf stems into 'گ'."""
    norm = text.replace("\u06AA", "ك").replace("\u06A9", "ك").replace("\u06BE", "ه").replace("\u06CC", "ي").replace("\u06C6", "و")
    norm = re.sub(r"ك(?:\u064e\u0640|\u0640\u064e|\u064b)", "گ", norm)
    for raw_kaf_gaf, shaped_gaf in KAF_FATHA_TO_GAF_LEXICON.items():
        norm = re.sub(rf"(?<!\S){re.escape(raw_kaf_gaf)}(?!\S)", shaped_gaf, norm)
    # Catch prefixed/suffixed inflections of high-frequency Iraqi Gaf roots written with Kaf+Fatha (كَ)
    norm = re.sub(
        r"ك\u064E(?=(?:لب|عد|اع|مر|بل|در|طع|ض[يى]|ظي|طر|دام|وه|ام|ف[اه]|نطر|الو|الت))",
        "گ",
        norm,
    )
    norm = re.sub(
        r"(?<=[افملن])ك\u064E(?=(?:د|اك|اع|اه|ع|ف|ط))",
        "گ",
        norm,
    )
    return norm


def normalize_daad_dhaa_homographs(text):
    """Correct common Iraqi poet Daad/Dhaa spelling swaps (including 'و' clitic prefix) before G2P shaping."""
    result = text
    for wrong_tok, fixed_tok in DAAD_DHAA_SPELLING_FIX_MAP.items():
        result = re.sub(rf"(?<!\S)و{re.escape(wrong_tok)}(?!\S)", f"وَ {fixed_tok}", result)
        result = re.sub(rf"(?<!\S){re.escape(wrong_tok)}(?!\S)", fixed_tok, result)
    # Disambiguate standalone 'ضل' (remained -> ظَلْ) except when meaning straying 'ضل الطريق/السبيل'
    result = re.sub(r"(?<!\S)ضل(?!\S)(?!\s+(?:الطريق|السبيل|عن|من))", "ظَلْ", result)
    return result


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
    """Module 49 & 68 (QC13, QC14 & QC34): Repair plain initial Sukun, block prosthetic pre-Hamza 'إِبْأ', strip feminine Haa Sukun, and leave medial diphthongs unmarked."""
    result = re.sub(r"(?<!\S)إِبْ([أإآ])", r"بِ\1", text)
    for bad_sukun, repaired in WORD_INITIAL_SUKUN_REPAIR_MAP.items():
        result = re.sub(rf"(?<!\S){re.escape(bad_sukun)}(?!\S)", repaired, result)
    for fusha_diph, coll_mono in DIALECTAL_DIPHTHONG_AND_VOWEL_MAP.items():
        result = re.sub(rf"(?<!\S){re.escape(fusha_diph)}(?!\S)", coll_mono, result)
    # Fallback repair for any remaining unmapped word-initial consonant+Sukun (QC13 guard)
    result = re.sub(r"(?<![\u0621-\u064A\u067E\u0686\u06AF\u064B-\u0652])([حعخغ])\u0652", r"\1ِ", result)
    result = re.sub(r"(?<![\u0621-\u064A\u067E\u0686\u06AF\u064B-\u0652])([\u0628-\u064A\u067E\u0686\u06AF])\u0652", r"\1ِ", result)
    # QC14: Leave medial diphthong glides (ي, و after Fatha) unmarked when followed by a letter in-word
    result = re.sub(
        r"\u064E([يو])\u0652(?=[\u0621-\u063A\u0641-\u064A\u067E\u0686\u06AF])",
        "\u064E\\g<1>",
        result,
    )
    # Strip any remaining Sukun directly on word-final feminine Haa/Taa Marbuta (preserving 'آهْ')
    result = re.sub(r"(?<!آ)([هة])\u0652(?=\s|$|\.\.|[،\)])", r"\1", result)
    return result


def de_cliticize_and_separate_words(text, use_tatweel=False):
    """Module 41 & 49: Separate attached vocatives, prepositions, constructs, and clitics."""
    result = re.sub(r"[ \t]*(?<!\.)\.\.(?!\.)[ \t]*", " .. ", text)
    result = re.sub(r" +", " ", result)
    result = normalize_iraqi_orthographic_gaf(result)
    # Remove mid-word kashida safely while keeping trailing prefix tatweel if requested
    result = re.sub(
        r"(?<=[\u0621-\u064A\u064B-\u0652\u067E\u0686\u06AF])\u0640+(?=[\u0621-\u064A\u064B-\u0652\u067E\u0686\u06AF])",
        "",
        result,
    )
    result = normalize_daad_dhaa_homographs(result)
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
    trail_match = re.search(r"([\s\)\]\.\u2026،؛:!؟\"']+)$", seg)
    trail_punct = ""
    if trail_match:
        trail_punct = trail_match.group(1)
        seg = seg[: trail_match.start()].rstrip()
    seg = re.sub(r"(?:\u0627\u064B|\u064B\u0627|\u064B)$", "َا", seg)
    seg = re.sub(r"[ٌٍُِ]$", "ْ", seg)
    seg = re.sub(r"(?<!آ)([هة])\u0652$", r"\1", seg)
    if (
        seg
        and re.search(r"[\u0621-\u063A\u0641-\u064A\u067E\u0686\u06AF]$", seg)
        and not seg.endswith(("ْ", "ا", "آ", "ى", "و", "ي", "ه", "ة"))
    ):
        seg = seg + "ْ"
    return f"{seg}{trail_punct}"


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

    processed = re.sub(r"(\S+?)(?:\u0627\u064B|\u064B\u0627|\u064B)(?=\s+(?!\.\.)\S)", r"\1َنْ", processed)
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
    if re.search(r"[\u064B-\u0652]", core):
        return token

    b_sep = "بِـ " if use_tatweel else "بِ "
    k_sep = "كَـ " if use_tatweel else "كَ "
    l_sep = "لِـ " if use_tatweel else "لِ "
    bal_pref = "بِـ ال" if use_tatweel else "بِال"
    kal_pref = "كَـ ال" if use_tatweel else "كَال"

    prefix_rules = (
        ("وبال", f"وَ {bal_pref}"),
        ("وكال", f"وَ {kal_pref}"),
        ("ولل", "وَ لِلْ"),
        ("وال", "وَ ال"),
        ("بال", bal_pref),
        ("كال", kal_pref),
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
            min_stem = 3 if raw_pref in ("ب", "ك", "ل", "وب", "وك", "ول") else 2
            if stem in ("يه", "اي", "وي", "اه", "آه"):
                continue
            if raw_pref == "و" and stem in ("لو", "لا", "ما", "من", "هو", "هي", "هم", "لك", "لي", "له", "يه", "بي", "في", "اي"):
                continue
            if len(stem) >= min_stem and stem in word_map:
                shaped_stem = _format_tatweel(word_map[stem], use_tatweel=use_tatweel)
                if vocalized_pref.endswith("ال") and stem[0] in _SUN_LETTERS and "\u0651" not in shaped_stem[:3]:
                    if len(shaped_stem) >= 2 and "\u064B" <= shaped_stem[1] <= "\u0650":
                        shaped_stem = shaped_stem[:2] + "\u0651" + shaped_stem[2:]
                    else:
                        shaped_stem = shaped_stem[0] + "\u0651" + shaped_stem[1:]
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


_SUN_LETTERS = frozenset("تثدذرزسشصضطظلن")
_INITIAL_LONG_I_STEMS = frozenset(
    ("في", "بيه", "بيها", "بيهم", "بيهن", "بيش", "ريش", "عيش", "عيشه", "حيره", "سيره", "ديره", "طينه", "قيمه", "شيمه", "شيعه", "شيعتك", "جين", "حين", "دين")
)


def _vocalize_unseen_arabic_word(core, dialect="iraqi"):
    """Apply conservative Iraqi/Fusha rule-based Tashkeel to bare unseen Arabic words (idempotent)."""
    if not core or re.search(r"[\u064B-\u0652]", core):
        return core
    if not re.fullmatch(r"[\u0621-\u064A\u067E\u0686\u06AF]+", core):
        return core
    if core in COMMON_CORPUS_LEXICON_V52:
        return COMMON_CORPUS_LEXICON_V52[core]

    prefix_out = ""
    stem = core
    if stem.startswith("وال") and len(stem) > 4:
        prefix_out, stem = "وَ ال", stem[3:]
    elif stem.startswith("بال") and len(stem) > 4:
        prefix_out, stem = "بِال", stem[3:]
    elif stem.startswith("لال") or (stem.startswith("لل") and len(stem) > 3):
        prefix_out, stem = "لِل", stem[2:]
    elif stem.startswith("ال") and len(stem) > 3:
        prefix_out, stem = "ال", stem[2:]
    elif stem.startswith("و") and len(stem) > 3 and stem[1:] in COMMON_CORPUS_LEXICON_V52:
        return f"وَ {COMMON_CORPUS_LEXICON_V52[stem[1:]]}"
    elif stem.startswith("و") and len(stem) == 5 and stem[2] == "ا":
        prefix_out, stem = "وَ ", stem[1:]

    if prefix_out == "لِل" and len(stem) >= 1 and stem[0] not in _SUN_LETTERS:
        prefix_out = "لِلْ"

    if prefix_out.endswith(("ال", "ل", "لِلْ")):
        if stem in COMMON_CORPUS_LEXICON_V52:
            sun_mark = "\u0651" if stem[0] in _SUN_LETTERS else ""
            shaped_s = COMMON_CORPUS_LEXICON_V52[stem]
            if sun_mark and len(shaped_s) >= 1 and "\u0651" not in shaped_s[:3]:
                shaped_s = shaped_s[0] + sun_mark + shaped_s[1:]
            return f"{prefix_out}{shaped_s}"

    if len(stem) <= 1:
        return f"{prefix_out}{stem}"

    long_v = set("اويىآ")
    out_chars = []
    n_len = len(stem)
    for idx, ch in enumerate(stem):
        nxt = stem[idx + 1] if idx + 1 < n_len else ""
        prv = stem[idx - 1] if idx > 0 else ""
        is_last = idx == n_len - 1
        out_chars.append(ch)
        if idx == 0 and prefix_out.endswith("ال") and ch in _SUN_LETTERS:
            out_chars.append("\u0651")
        is_consonantal_glide = ch in ("و", "ي") and (
            idx == 0 or nxt in ("ا", "آ") or (prv in ("ا", "آ") and not is_last)
        )
        if ch in long_v and not is_consonantal_glide:
            continue
        if is_last:
            if dialect != "fusha" and ch not in "هة":
                out_chars.append("\u0652")
            continue
        if prv in ("ا", "آ") and ch in ("و", "ي") and nxt not in ("ا", "آ"):
            out_chars.append("\u0650")
        elif idx == 0 and ch in ("ي", "ت", "ن") and n_len >= 4 and nxt not in ("ا", "آ", "ى"):
            out_chars.append("\u0650")  # colloquial imperfect prefix يِـ تِـ نِـ
        elif idx == 0 and ch == "و":
            out_chars.append("\u0650" if nxt == "ي" and n_len <= 3 else "\u064E")
        elif idx == 0 and ch == "ا":
            continue
        elif nxt in ("ا", "آ"):
            out_chars.append("\u064E")
        elif nxt == "و":
            if idx + 2 < n_len and stem[idx + 2] in ("ا", "آ"):
                out_chars.append("\u0650" if idx == 0 and ch in ("ت", "ي", "ن") else "\u064E")
            else:
                out_chars.append("\u064F" if idx > 0 or ch not in "لمنس" else "\u064E")
        elif nxt == "ي" and idx + 2 == n_len:
            out_chars.append("\u0650")
        elif nxt == "ي":
            if idx == 0:
                out_chars.append("\u0650" if stem in _INITIAL_LONG_I_STEMS else "\u064E")
            else:
                rem_after_y = stem[idx + 2 :]
                is_past_or_pron_diph = rem_after_y in ("ت", "تك", "ته", "تها", "تهم", "توا", "تو", "نا", "نه")
                out_chars.append("\u064E" if is_past_or_pron_diph else "\u0650")
        elif prv == "ا" and idx == 1:
            out_chars.append("\u0652" if ch not in long_v and n_len >= 4 else "\u064E")
        elif prv == "ا" and idx == n_len - 2 and n_len in (4, 5) and ch not in long_v:
            out_chars.append("\u0650")  # Active participle فَاعِلْ & broken plural مَفَاعِلْ / فَوَاعِلْ
        elif idx % 2 == 0 or (idx + 2 == n_len):
            out_chars.append("\u064E")
        else:
            out_chars.append("\u0652" if idx > 0 and nxt not in long_v else "\u064E")

    vocalized = "".join(out_chars)
    # Guard QC14 & closed feminine haa & initial sukun
    vocalized = re.sub(r"\u064E([يو])\u0652(?=[\u0621-\u064A\u067E\u0686\u06AF])", "\u064E\\g<1>", vocalized)
    vocalized = re.sub(r"([هة])\u0652$", r"\1", vocalized)
    if len(vocalized) >= 2 and vocalized[1] == "\u0652":
        vocalized = vocalized[0] + "\u064E" + vocalized[2:]
    return f"{prefix_out}{vocalized}"


def _is_partially_vocalized_poet_word(core):
    """Return True if core has only a poet Shadda or a single disambiguating vowel without Sukun."""
    if not core or core in ("اللّٰه", "أُمّ", "حُبّ", "سِرّ", "وَ", "بِ", "لِ", "كَ", "فَ"):
        return False
    if core.endswith("\u0652") or "\u0652" in core:
        return False
    arabic_letters = re.findall(r"[\u0621-\u064A\u067E\u0686\u06AF]", core)
    if len(arabic_letters) < 3:
        return False
    vowel_marks = re.findall(r"[\u064B-\u0650\u0670]", core)
    return len(vowel_marks) <= 1


def shape_unseen_corpus_tokens(text, dialect="iraqi", use_tatweel=False):
    """Apply V52 corpus lexicon and morphological vocalizer on unvocalized or partially vocalized words."""
    out_lines = []
    for line in text.splitlines():
        if line.strip().startswith("["):
            out_lines.append(line)
            continue
        tokens = line.split(" ")
        new_tokens = []
        for tok in tokens:
            if not tok or tok == "..":
                new_tokens.append(tok)
                continue
            m = re.match(r"^([\(\[\{\"“«'،\.\u2026•✦★✍]*)(.*?)([\)\]\}\"»'،\.\u2026؛:!؟•✦★]*)$", tok)
            if not m:
                new_tokens.append(tok)
                continue
            lead_p, core, trail_p = m.groups()
            if not core:
                new_tokens.append(tok)
                continue
            if core in COMMON_CORPUS_LEXICON_V52:
                shaped_core = _format_tatweel(COMMON_CORPUS_LEXICON_V52[core], use_tatweel=use_tatweel)
                new_tokens.append(f"{lead_p}{shaped_core}{trail_p}")
                continue
            if re.search(r"[\u064B-\u0652]", core):
                if _is_partially_vocalized_poet_word(core):
                    bare_core = re.sub(r"[\u064B-\u0652\u0670]", "", core)
                    shaped_core = shape_token_morphologically(
                        bare_core, COMMON_CORPUS_LEXICON_V52, use_tatweel=use_tatweel
                    )
                    if shaped_core == bare_core:
                        shaped_core = _vocalize_unseen_arabic_word(bare_core, dialect=dialect)
                    new_tokens.append(f"{lead_p}{shaped_core}{trail_p}")
                else:
                    new_tokens.append(tok)
                continue
            shaped_core = shape_token_morphologically(core, COMMON_CORPUS_LEXICON_V52, use_tatweel=use_tatweel)
            if shaped_core == core:
                shaped_core = _vocalize_unseen_arabic_word(core, dialect=dialect)
            new_tokens.append(f"{lead_p}{shaped_core}{trail_p}")
        out_lines.append(" ".join(new_tokens))
    return "\n".join(out_lines)


def heal_nc21_short_clause_pauses(text):
    """Module 70 (NC21): Remove mid-clause '..' before a single stranded word in 3-word Kasra lines."""
    vocative_refrains = frozenset(("مولاي", "يحسين", "بويه", "يمه", "اه", "آه", "لا", "والله"))
    healed_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("[") or ".." not in stripped:
            healed_lines.append(line)
            continue
        trailing_pause = " .." if stripped.endswith("..") else ""
        body = stripped[:-2].rstrip() if stripped.endswith("..") else stripped
        if ".." not in body:
            healed_lines.append(line)
            continue
        parts = [p.strip() for p in body.split("..") if p.strip()]
        if len(parts) in (2, 3):
            w1 = [w for w in parts[0].split() if _strip_arabic_diacritics(w) not in ("و", "ف", "ب", "ل")]
            w2 = [w for w in parts[1].split() if _strip_arabic_diacritics(w) not in ("و", "ف", "ب", "ل")]
            w2_bare = _strip_arabic_diacritics(w2[0]) if len(w2) == 1 else ""
            if len(w1) == 2 and len(w2) == 1 and w2_bare not in vocative_refrains and not parts[1].startswith("("):
                merged = f"{parts[0]} {parts[1]}"
                parts = [merged] + parts[2:]
        healed_lines.append(f"{' .. '.join(parts)}{trailing_pause}".strip())
    return "\n".join(healed_lines)


def _count_dialect_markers(text):
    """Count Iraqi vs. Bahrani markers stably on diacritic-stripped & ortho-normalized text."""
    ortho = normalize_daad_dhaa_homographs(normalize_iraqi_orthographic_gaf(text))
    bare_text = re.sub(r"[\u064B-\u0652]", "", ortho)
    bahrani_hits = 0
    for marker in BAHRANI_MARKERS:
        if marker == "عَلَه":
            if re.search(r"(?<!\S)عَل?َه(?!\S)", text) and "إِعْلَه" not in text and "اعله" not in bare_text and "إعله" not in bare_text:
                bahrani_hits += 1
        else:
            bare_m = re.sub(r"[\u064B-\u0652]", "", marker)
            if bare_m and re.search(rf"(?<!\S){re.escape(bare_m)}(?!\S)", bare_text):
                bahrani_hits += 1
    iraqi_hits = 0
    for marker in IRAQI_MARKERS:
        bare_m = re.sub(r"[\u064B-\u0652]", "", marker)
        if bare_m and bare_m in bare_text:
            iraqi_hits += 1
    return bahrani_hits, iraqi_hits


def detect_and_shape_dialect(text, enforce_iraqi_dhaa=None, use_tatweel=False):
    """Modules 43 & 49: Identify Pure Bahrani vs. Pure Iraqi vs. Neutral Fusion and shape tokens."""
    bahrani_hits, iraqi_hits = _count_dialect_markers(text)

    if bahrani_hits > iraqi_hits:
        detected = "bahrani"
    elif iraqi_hits > bahrani_hits:
        detected = "iraqi"
    else:
        detected = "iraqi_bahrani"

    if enforce_iraqi_dhaa is None:
        enforce_iraqi_dhaa = detected == "iraqi"

    shaped = de_cliticize_and_separate_words(text, use_tatweel=use_tatweel)
    shaped = heal_nc21_short_clause_pauses(shaped)
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

    shaped = shape_unseen_corpus_tokens(shaped, dialect=detected, use_tatweel=use_tatweel)
    if enforce_iraqi_dhaa:
        shaped = (
            shaped.replace("فَاضِلْ", "فَاظِلْ")
            .replace("ضْلُوعِي", "ظْلُوعِي")
            .replace("مَا ضَلْ", "مَا ظَلْ")
        )
    shaped = resolve_dialectal_and_prosodic_tanween(
        shaped, dialect=detected, use_tatweel=use_tatweel
    )
    shaped = repair_word_initial_sukun_and_diphthongs(shaped)
    if detected != "fusha":
        shaped = (
            shaped.replace("أُمُّ البَنِينْ", "أُمّ البَنِينْ")
            .replace("أُمُّ الأَرْبَعَه", "أُمّ الأَرْبَعَه")
            .replace("عَلَه التَّرَايِبْ", "عَلَى التَّرَايِبْ")
        )
    return {
        "detected_dialect": detected,
        "sound_prompt_dialect_declaration": sound_dialect,
        "bahrani_score": bahrani_hits,
        "iraqi_score": iraqi_hits,
        "dhad_articulation": dhad_mode,
        "maqam_articulation_rule": maqam_rule,
        "shaped_lyrics": shaped,
    }


def format_clean_lyrics_for_lyria35(raw_poem, dialect=None):
    """Module 72 (V57.0): Compile Clean Natural Arabic + Surgical Vowels + NC27 (چ->تش & گ) for Lyria 3.5."""
    sanitized = sanitize_poem_decorations(raw_poem.replace("\\n", "\n"))
    bahrani_hits, iraqi_hits = _count_dialect_markers(sanitized)
    if dialect in ("iraqi", "bahrani", "iraqi_bahrani", "fusha"):
        detected = dialect
    elif bahrani_hits > iraqi_hits:
        detected = "bahrani"
    elif iraqi_hits > bahrani_hits:
        detected = "iraqi"
    else:
        detected = "iraqi_bahrani"

    # NC26: Strip heavy diacritic clutter & terminal Sukun spam to prevent BPE token shattering in Lyria 3.5
    stripped = re.sub(r"[\u064B-\u0652\u0670]", "", sanitized)
    ch_converted = stripped.count("چ")

    phrase_fixes = (
        ("اترجمها ام البنين", "تْرَجِّمها .. أُمّ البنين"),
        ("إترجمها ام البنين", "تْرَجِّمها .. أُمّ البنين"),
        ("اترجمها أم البنين", "تْرَجِّمها .. أُمّ البنين"),
        ("إترجمها أم البنين", "تْرَجِّمها .. أُمّ البنين"),
        ("ترجمها .. ام البنين", "تْرَجِّمها .. أُمّ البنين"),
        ("ترجمها .. أم البنين", "تْرَجِّمها .. أُمّ البنين"),
        ("عله الترايب", "على الترايب"),
        ("اعله غايبها", "على غايبها"),
        ("إعله غايبها", "على غايبها"),
        ("ام البنين", "أُمّ البنين"),
        ("أم البنين", "أُمّ البنين"),
    )
    cleaned = stripped
    for src_p, dst_p in phrase_fixes:
        cleaned = cleaned.replace(src_p, dst_p)

    # Restore synthetic prosthetic إمن / إعله tokens that Lyria 3.5 misread as إبني / أعلى
    cleaned = re.sub(r"(?<!\w)[إا]من(?!\w)", "من", cleaned)
    cleaned = re.sub(r"(?<!\w)[إا]عله(?!\w)", "على", cleaned)

    # NC27: Convert Iraqi/Bahrani چ -> تش digraph & colloquial ق -> گ on proven stems
    token_map = {
        "تبچي": "تبتشي",
        "يبچي": "يبتشي",
        "حچي": "حَتشِي",
        "وحچي": "وحَتشِي",
        "حتشي": "حَتشِي",
        "وحتشي": "وحَتشِي",
        "ملچوم": "مَلتشوم",
        "ملتشوم": "مَلتشوم",
        "وگلبه": "وگَلبه",
        "وقلبه": "وگَلبه",
        "گلبه": "گَلبه",
        "قلبه": "گَلبه",
        "قبلك": "گبلك",
        "گبلك": "گبلك",
        "حقه": "حگّه",
        "حگه": "حگّه",
        "أوقف": "أوگف",
        "اوقف": "أوگف",
        "اوگف": "أوگف",
        "أوگف": "أوگف",
        "الصور": "الصُوَر",
        "فلسفة": "فَلْسَفة",
        "وفلسفة": "وفَلْسَفة",
        "الوكت": "الوَكْت",
        "لواهب": "لَواهب",
        "الحب": "الحُب",
        "يتعلم": "يتعلّم",
        "خلي": "خلّي",
        "حبه": "حبّه",
        "وحبه": "وحبّه",
        "اترجمها": "تْرَجِّمها",
        "ترجمها": "تْرَجِّمها",
    }

    out_lines = []
    for line in cleaned.splitlines():
        if line.strip().startswith("[") and line.strip().endswith("]"):
            out_lines.append(line.strip())
            continue
        words = line.split(" ")
        new_words = []
        for w in words:
            prefix = ""
            suffix = ""
            core = w
            while core and core[0] in "([\"'":
                prefix += core[0]
                core = core[1:]
            while core and core[-1] in ")]\"'.،؟!":
                suffix = core[-1] + suffix
                core = core[:-1]
            bare_core = re.sub(r"[\u064B-\u0652\u0670]", "", core)
            if bare_core in token_map:
                core = token_map[bare_core]
            elif "چ" in core:
                core = core.replace("چ", "تش")
            new_words.append(f"{prefix}{core}{suffix}")
        out_lines.append(" ".join(new_words))

    final_lyrics = "\n".join(out_lines)
    prompt_key = (
        "v57_bahrani_matam_pure_58bpm_saba_bayati"
        if detected == "bahrani"
        else "v57_iraqi_karbalaei_pure_majlis_60bpm_saba_lami"
    )
    return {
        "detected_dialect": detected,
        "clean_lyria35_lyrics": final_lyrics,
        "recommended_v57_prompt_key": prompt_key,
        "recommended_v57_sound_prompt": EXTENDED_ATWAR_PROMPTS_V52[prompt_key],
        "nc26_anti_token_shattering_applied": True,
        "nc27_ch_to_tsh_digraph_count": ch_converted,
        "nc29_mandatory_chunk_audit_sec": 20,
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
    cleaned = re.sub(r"[\(\)\[\]،.؟!:«»\"'\\-]", "", cleaned)
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
    if n_chars == 3 and long_vowels == 0:
        return ["CV", "CVC"]
    est = max(1, min(n_chars - 1, long_vowels + max(1, (n_chars - long_vowels) // 2)))
    return ["CV"] * est


def segment_arabic_prosodic_syllables(hemistich):
    """Segment an Arabic hemistich into prosodic CV/CVV/CVC syllables."""
    clean = re.sub(r"\[[^\]]*\]", " ", hemistich)
    clean = clean.replace("..", " ")
    clean = re.sub(r"[\(\)،.؟!:«»\"']", " ", clean)
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

    # QC31, QC32 & QC30 checks
    orphan_single_word_lines = []
    estehlal_over_4_lines = False
    non_header_lines = []
    blocks_lint = re.split(r"(\[[^\]]+\])", text)
    cur_tag_lint = ""
    for chunk_l in blocks_lint:
        if chunk_l.startswith("[") and chunk_l.endswith("]"):
            cur_tag_lint = chunk_l
            continue
        lines_in_block = [ln.strip() for ln in chunk_l.splitlines() if ln.strip()]
        if _is_pure_estehlal_tag(cur_tag_lint) and len(lines_in_block) > 4:
            estehlal_over_4_lines = True
        for ln_item in lines_in_block:
            if not ln_item.startswith("["):
                non_header_lines.append(ln_item)
                core_words = [
                    w
                    for w in ln_item.replace("..", "").strip("() ").split()
                    if w and not w.startswith("ممم")
                ]
                if len(core_words) == 1:
                    orphan_single_word_lines.append(ln_item)

    extend_couplet_budget_violation = bool(stage >= 2 and len(non_header_lines) > 18)

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
        and not orphan_single_word_lines
        and not estehlal_over_4_lines
        and not extend_couplet_budget_violation
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
        "orphan_single_word_lines_detected": orphan_single_word_lines,
        "estehlal_over_4_lines_violation": estehlal_over_4_lines,
        "extend_couplet_budget_violation": extend_couplet_budget_violation,
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


def load_v50_0_constitution():
    """Load the canonical V50.0 OMNI-ARCHITECT JSON constitution from references/."""
    v50_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "references",
            "hussaini_os_v50_0_constitution.json",
        )
    )
    if os.path.isfile(v50_path):
        with open(v50_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    v48_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "references",
            "hussaini_os_v48_5_constitution.json",
        )
    )
    with open(v48_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_v48_5_constitution():
    """Backward-compatible loader returning the canonical constitution."""
    return load_v50_0_constitution()


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


def verify_historical_narratives(text):
    """Module 67 (V52.0): Verify Husseini poetry against authentic Ahl al-Bayt historical sources.

    Flags known weak/distorted popular motifs (Mufid/Luhuf/Muqarrim/Mutahhari standards),
    doctrinal exaggerations (Ghuluw), or Zainabi dignity phrasings, while recognizing verified motifs.
    """
    clean = re.sub(r"[\u064B-\u0652]", "", text)
    warnings = []
    verified_motifs = []

    authentic_checks = (
        ("abbas_martyrdom", ("المشرعة", "المشرعه", "العلقمي", "العلگمي", "چفين", "جفين", "بسهم", "العمد"), "مقتل أبي الفضل العباس (ع) على العلقمي وقطع الكفين والسهم في العين"),
        ("infant_harmala_arrow", ("الرضيع", "عبد الله", "عبدالله", "حرملة", "مثلث", "بمهد", "رزقه السهم", "الطفل رزقه السهم"), "شهادة الطفل الرضيع عبد الله بالسهم المثلث في نحره"),
        ("ten_horsemen_trampling", ("عشرة", "عشر خيول", "عشر اخيول", "خيل عشره", "خيل عشرة", "الحوافر", "للحوافر", "حوافر", "صدر الحسين"), "إجالة الخيول العشرة على الصدر الشريف بعد الشهادة"),
        ("shimr_chest_and_nahr_martyrdom", ("صاعد إعله صدره", "صاعد اعله صدره", "جلوسه اعلى الصدر", "عالصدر", "قبض الشيبه", "يحز بمنحره"), "جثوم الشمر على الصدر الشريف وقبض الشيبة المقدسة وحزّ المنحر"),
        ("imam_mahdi_intidhar_and_loyalty", ("فلسفة الانتظار", "للمهدي", "أبو صالح", "ابو صالح", "ناطر الغايب"), "عقيدة انتظار الإمام المهدي (عج) والوفاء الحسيني على نهج أم البنين (ع)"),
        ("zainab_sajjad_protection", ("السجاد", "العليل", "زينب", "ما رأيت إلا جميلا"), "صمود العقيلة زينب (ع) وحفظها الإمام السجاد (ع)"),
        ("zahra_door_compression", ("الضلع", "البسمار", "الزهراء", "الزهره", "الباب"), "مظلومية السيدة فاطمة الزهراء (ع) وإخفاء قبرها"),
        ("umm_al_banin_madina", ("حذلم", "يثرب", "لدياره", "ام البنين", "أم البنين"), "استقبال أم البنين (ع) نعي بشير بن جذلم في المدينة المنورة"),
    )
    for motif_id, keys, desc in authentic_checks:
        if any(k in clean for k in keys):
            verified_motifs.append({"motif_id": motif_id, "description_ar": desc})

    distortion_rules = [
        (
            "wedding_of_qasim_anachronism",
            r"(?:عرس\s+القاسم|زفاف\s+القاسم|ليلة\s+عرس|چف\s+الحنه|كف\s+الحنة|عريس\s+كربلا|عريس)",
            "التنبيه التاريخي (زفاف القاسم ع): رواية عرس القاسم يوم عاشوراء غير ثابتة في المقاتل المعتبرة كالإرشاد واللهوف ونفس المهموم؛ يُرجّح الاقتصار على بطولته وشبابه.",
        ),
        (
            "umm_al_banin_in_karbala",
            r"(?:أم\s+البنين|ام\s+البنين).{0,45}(?:بالخيم|بكربلا|بالطف|عالنهر|بالمشرعة)",
            "تحريف مكاني: السيدة أم البنين (ع) بقيت في المدينة المنورة ولم تحضر كربلاء.",
        ),
        (
            "layla_in_karbala",
            r"ليلى.{0,45}(?:بالخيم|بكربلا|بالطف|ودعت|شافت\s+الاكبر)",
            "تحقيق تاريخي: حضور السيدة ليلى أم علي الأكبر (ع) في كربلاء غير ثابت بالأسانيد الأقدمية عند المحققين.",
        ),
        (
            "infant_killed_by_sword",
            r"(?:الرضيع|عبد\s*الله|المهد).{0,35}(?:ذبح\s+بسيف|بسيف\s+الشمر|حز\s+وريده\s+الشمر)",
            "خطأ روائي: عبد الله الرضيع (ع) استشهد بسهم مثلث رماه حرملة في نحره، لا بالسيف على يد الشمر.",
        ),
        (
            "hijab_indignity_wording",
            r"(?:بلا\s+حجاب|ما\s*ضل\s+حجاب|ماضل\s+عدنه\s+حجاب|بلا\s+ستر)",
            "تنبيه وقار عقائدي: يُنصح بتجنب عبارة 'بلا حجاب'؛ فقد حرصت العقيلة زينب والحرائر على التستر بأيديهن وبقايا الأردية وحفظ العفة التامة.",
        ),
        (
            "excessive_mythic_body_count",
            r"(?:ثلاثمية\s+ألف|مئات\s+الألوف|مليون\s+قتيل).{0,30}(?:بسيف|طبر|ذبح)",
            "مبالغة روائية غير منضبطة: استعمل أوصاف البسالة الموثقة دون أرقام خرافية تصادم المقاتل الرصينة.",
        ),
        (
            "legendary_wound_count_1900",
            r"(?:ألف|الف)\s+جرح\s+وتسعمي[هة]|تسعمي[هة]\s+(?:جرح|طعنة)",
            "تدقيق مقاتلي: رقم (1900) جرح ورد في روايات متأخرة؛ والأثبت في المصادر الأولى عشرات الطعنات والضربات والسهام.",
        ),
        (
            "ghuluw_divine_attribution",
            r"(?:تقل|تقول)\s+كن\s+فيكون|انت\s+الخالق|انت\s+الرب",
            "تحذير عقائدي (الغلو): يجب تنزيه المقامات عن نسبة الخلق والتكوين المستقل عن الله سبحانه؛ التزم بتفويضهم وعبوديتهم لله.",
        ),
        (
            "abbas_drinking_water_claim",
            r"(?:(?:العباس|ابو\s*فاضل|ابوالفضل).{0,25}(?<!ما\s)(?<!لم\s)(?<!لا\s)(?:شرب\s+الماي|ارتوى\s+من\s+الماي)|(?<!ما\s)(?<!لم\s)(?<!لا\s)(?:شرب\s+الماي|ارتوى\s+من\s+الماي).{0,20}(?:العباس|ابو\s*فاضل|ابوالفضل))",
            "خطأ روائي: أبو الفضل العباس (ع) غرف الماء من الفرات ثم رماه وفاءً لعطش الحسين (ع) ولم يشرب منه.",
        ),
        (
            "ruqayyah_died_in_karbala_error",
            r"رقية.{0,30}(?:ماتت\s+بكربلا|انذبحت\s+بالطف|اندفنت\s+بالطف)",
            "خطأ مكاني: السيدة رقية (ع) توفيت في خربة الشام لا في أرض كربلاء.",
        ),
        (
            "sajjad_combat_error",
            r"(?:السجاد|العليل|زين\s*العابدين).{0,30}(?:شهر\s+سيفه\s+وقاتل|قتل\s+الاف|بارز\s+الفرسان)",
            "تحقيق تاريخي: الإمام السجاد (ع) كان مثقلاً بالمرض يوم العاشر حفظاً للإمامة، وجهاده الأعظم كان بالخطابة في الكوفة والشام.",
        ),
    ]
    for rule_id, pattern, msg in distortion_rules:
        if re.search(pattern, clean):
            warnings.append({"rule_id": rule_id, "severity": "warning", "message_ar": msg})

    score = max(0, 100 - 20 * len(warnings))
    return {
        "skill_version": SKILL_VERSION,
        "historical_accuracy_score": score,
        "is_historically_clean": len(warnings) == 0,
        "verified_authentic_motifs": verified_motifs,
        "distortions_and_warnings": warnings,
        "canonical_sources": ["الإرشاد للشيخ المفيد", "اللهوف في قتلى الطفوف لابن طاووس", "نفس المهموم للشيخ عباس القمي"],
    }


def _split_clean_poem_lines(poem_text):
    """Split raw poem into clean stanzas using tags or decorative dividers."""
    norm_text = poem_text.replace("\\n", "\n")
    divider_re = re.compile(
        r"^[\s💔❤😭✏★☆۞◆◇▪✦🙨🙜❀✿↻↺✍•●○■□►◄▲▼#@+*~=_ـ./\\|\-،:؛؟!⊰⊱─═—–“”\"']+$"
    )
    raw_chunks = []
    cur_chunk = []
    for raw_ln in norm_text.splitlines():
        s_ln = raw_ln.strip()
        if s_ln and divider_re.fullmatch(s_ln):
            if cur_chunk:
                raw_chunks.append("\n".join(cur_chunk))
                cur_chunk = []
        else:
            cur_chunk.append(raw_ln)
    if cur_chunk:
        raw_chunks.append("\n".join(cur_chunk))

    stanzas = []
    current_tag = "[المُسْتَهَلّ]"
    current_lines = []
    for idx_c, chunk_str in enumerate(raw_chunks):
        sanitized = sanitize_poem_decorations(chunk_str)
        if not sanitized.strip():
            continue
        if idx_c > 0 and current_lines:
            stanzas.append((current_tag, current_lines))
            current_lines = []
            current_tag = f"[المَقْطَع {len(stanzas)}]"
        for raw_ln in sanitized.splitlines():
            ln = raw_ln.strip()
            if not ln:
                continue
            if ln.startswith("[") and ln.endswith("]"):
                if current_lines:
                    stanzas.append((current_tag, current_lines))
                    current_lines = []
                current_tag = ln
            else:
                current_lines.append(ln)
    if current_lines:
        stanzas.append((current_tag, current_lines))
    return stanzas


def plan_poem_extend_stages(poem_text, target_method="both", bpm=60):
    """Module 67 & 70 (V52.0–V55.0): Partition any Hussaini poem into V52 3-Line NC16 Extend Stages.

    Accounts empirically for Method 1 (+30s Compose Extend) and Method 2 (+60s Producer Chat
    Extend tail-pad & Step 4 limiter findings from V51.2 evaluation).
    """
    raw_stanzas = _split_clean_poem_lines(poem_text)
    stanzas = []
    for tag, lines in raw_stanzas:
        shaped_lines = [
            ln.strip()
            for ln in detect_and_shape_dialect("\n".join(lines))["shaped_lyrics"].splitlines()
            if ln.strip()
        ]
        if shaped_lines:
            stanzas.append((tag, shaped_lines))

    estehlal_lines = []
    body_stanzas = []

    for tag, lines in stanzas:
        if _is_pure_estehlal_tag(tag) and not estehlal_lines:
            if len(lines) > 4 and len(stanzas) == 1:
                estehlal_lines = lines[:2]
                body_stanzas.append(("[النَّزْلَة 1]", lines[2:]))
            elif len(lines) > 4:
                estehlal_lines = lines[:4]
                body_stanzas.append(("[النَّزْلَة 1]", lines[4:]))
            else:
                estehlal_lines = lines[:4]
        else:
            body_stanzas.append((tag, lines))

    if not estehlal_lines and body_stanzas:
        first_tag, first_lines = body_stanzas[0]
        estehlal_lines = first_lines[:2]
        if len(first_lines) > 2:
            body_stanzas[0] = (first_tag, first_lines[2:])
        else:
            body_stanzas = body_stanzas[1:]

    estehlal_block = enforce_collective_estehlal_parentheses(
        "\n".join(["[المُسْتَهَلّ]"] + [ln if ln.endswith("..") else f"{ln} .." for ln in estehlal_lines])
    )
    extend_stages = []
    sec_per_line = 7.4 * (60.0 / max(40.0, float(bpm or 60)))

    for idx, (tag, lines) in enumerate(body_stanzas, start=1):
        sub_chunks = [lines[i : i + 3] for i in range(0, len(lines), 3)]
        for sub_idx, chunk in enumerate(sub_chunks):
            if len(chunk) == 4:
                formatted = format_kasra_three_vertical_lines(chunk)
            else:
                formatted = [ln if ln.endswith("..") else f"{ln} .." for ln in chunk]
            is_kasra = (sub_idx % 2 == 1) or ("كسر" in tag)
            stage_code = f"{idx + 1}{'B' if is_kasra else 'A'}" if idx >= 2 or sub_idx > 0 else "Stage_1_Body"
            header = f"[الكَسْرَة {idx}]" if is_kasra else f"[النَّزْلَة {idx}]"
            est_sec = round(len(formatted) * sec_per_line, 1)
            extend_stages.append(
                {
                    "stage_code": stage_code,
                    "section_header": header,
                    "vertical_lines": formatted,
                    "vertical_line_count": len(formatted),
                    "nc16_three_line_compliant": len(formatted) <= 3,
                    "estimated_singing_sec": est_sec,
                    "method_1_window_fit": "OK (+30s Compose Extend)" if est_sec <= 28.0 else "Trim-tight (+30s)",
                    "method_2_pad_warning": (
                        f"Producer +60s window leaves ~{max(0.0, round(60.0 - est_sec, 1))}s trailing Ahaat/repeat risk; "
                        "audit singing end timestamp before next extend."
                    ),
                }
            )

    return {
        "skill_version": SKILL_VERSION,
        "target_method": target_method,
        "bpm": int(bpm),
        "stage_1_estehlal": estehlal_block.splitlines(),
        "total_extend_blocks": len(extend_stages),
        "extend_stages": extend_stages,
        "grand_finale_stage_6c": estehlal_block.splitlines(),
        "mastering_recommendation": (
            "Prefer local '--mode vocal_pure_master --trim-end-sec <end> --fade-out-sec 3.0' (-14.0 LUFS / "
            "-1.0 dBTP) over cloud Step 4 audio__apply_effect which clips above 0 dBFS."
        ),
    }


def recommend_tor_and_rhythm_for_poem(text):
    """Module 46, 48, 52, 67, 68 & 69: Recommend Meter, Tor, School, DSP Mode, BPM, Maqam & Prompt."""
    clean_text = sanitize_poem_decorations(text) or text
    bare_text = re.sub(r"[\u064B-\u0652]", "", clean_text)
    dialect_info = detect_and_shape_dialect(clean_text)
    dialect = dialect_info["detected_dialect"]
    iso = validate_stage1_iso_syllabic_lock(clean_text)
    hemistichs = _extract_poem_hemistichs(clean_text.splitlines())
    avg_syl = (
        int(round(sum(iso["syllable_counts"]) / len(iso["syllable_counts"])))
        if iso["syllable_counts"]
        else 8
    )
    avg_words = (
        sum(len(h.split()) for h in hemistichs) / float(len(hemistichs))
        if hemistichs
        else 5.0
    )

    is_abudhiyah = (
        len(hemistichs) == 4 and validate_abudhiyah_jinas(clean_text.splitlines()).get("is_valid_abudhiyah", False)
    )
    is_zuhayri = (
        len(hemistichs) == 7 and validate_zuhayri_mawal(clean_text.splitlines()).get("is_valid_zuhayri", False)
    )

    service_kw = ("خادم", "خدمنك", "أخدمنك", "هنيالي", "موكب", "مشايه", "مشاية", "راية")
    heroic_kw = ("عباس", "كفيل", "حيدر", "كرار", "صوله", "سيف", "زنجيل")
    shoor_exact = bool(re.search(r"(?<!\S)(?:ال)?ش[و]+ر(?!\S)|\[(?:ال)?شور\]", bare_text))
    shoor_kw = ("حسين حسين", "لبيك", "مامدفون والينه")
    ecstatic_shoor_kw = ("مجنون", "جنون", "اهواك", "عشگ", "عشق", "شيعي", "حبيب")
    fazzaiya_kw = ("فزاعيه", "فزاعية", "رباطات فزاعية", "تبرالي")
    hosa_kw = ("[هوسة]", "هوسه", "هوسة", "رباطات")
    tawshih_kw = ("[تواشيح]", "[ابتهالات]", "تواشيح", "أهل الكساء", "المباهلة", "أنشودة", "نشيد")
    tragedy_kw = ("كربلا", "عاشور", "سبي", "سبايا", "مذبوح", "حوافر", "شمر", "مشرعة", "علگمي", "علقمي", "خرابة", "خرابه", "نحر", "صدر")
    lami_grief_kw = ("سبي", "خرابة", "خرابه", "غربة", "غربه", "عليل", "سياط", "يمه", "تراب", "عطشان")
    munajat_khidma_kw = (
        "طبع البشر",
        "الخدمه انكساري",
        "الخدمة انكساري",
        "سهرانه عينك",
        "بخدمتك",
        "بعطائك",
        "فلسفة الانتظار",
        "ناطر الغايب",
        "اترجمها أم البنين",
    )
    journey_kw = ("ناقة", "ناگه", "ظعن", "ضعن", "مسير", "سفر", "صحرا", "طويل", "ليل")
    thulathi_kw = ("[ثلاثي]", "ثلاثي", "وقفة", "وقفه", "زحف", "صمود")
    nai_explicit_kw = ("[نعي]", "[موال]", "[أبوذية]")

    if any(k in bare_text for k in nai_explicit_kw) or is_abudhiyah or is_zuhayri:
        mode = "nai"
        bpm = 0
        maqam = "saba"
        meter = "abudhiyah" if is_abudhiyah else ("zuhayri" if is_zuhayri else "mujarradat")
        tor = "tor_nai_kashi"
        school = "School 04 (النعي المنبري والشجن العراقي)"
        prompt = MASTER_SOUND_PROMPTS_V48_5["minbar_nai_0bpm_rubato_saba_exclusive_weeping"]
    elif shoor_exact or any(k in bare_text for k in shoor_kw) or (
        avg_words <= 4.3 and any(k in bare_text for k in ecstatic_shoor_kw) and not any(k in bare_text for k in ("شمر", "مذبوح", "حوافر"))
    ):
        mode = "shoor"
        bpm = 132
        maqam = "kurd"
        meter = "rukbani"
        tor = "tor_darj_karbalai"
        school = "School 05 (الشور الكربلائي والإيقاع الحماسي)"
        prompt = MASTER_SOUND_PROMPTS_V48_5["karbalai_shoor_132bpm_kurd"]
    elif any(k in bare_text for k in hosa_kw):
        if dialect == "bahrani":
            mode = "bahrani_haidari"
            bpm = 96
            maqam = "hijaz"
            meter = "hosa"
            tor = "tor_bahrani_haidari"
            school = "School 02/03 (الحيدري والأهزوجة البحرانية)"
            prompt = MASTER_SOUND_PROMPTS_V48_5["bahrani_haidari_96bpm_hijaz"]
        else:
            mode = "zanjeel_iraqi"
            bpm = 88
            maqam = "hijaz"
            meter = "hosa"
            tor = "tor_hosa_iraqi"
            school = "School 05 (الأهزوجة والهوسة الموكبية)"
            prompt = EXTENDED_ATWAR_PROMPTS_V52["hosa_iraqi_mawkib_88bpm_hijaz_v54"]
    elif any(k in bare_text for k in tawshih_kw) and not any(k in bare_text for k in tragedy_kw):
        mode = "vocal_pure_master"
        bpm = 86
        maqam = "rast"
        meter = "muwashah"
        tor = "tor_tawshih_shia"
        school = "School 03 (التوشيح والقصيدة الإنشادية — الأكرف)"
        prompt = EXTENDED_ATWAR_PROMPTS_V52["shia_tawshih_nasheed_86bpm_rast_hijaz_v52"]
    elif any(k in bare_text for k in fazzaiya_kw) or ("گوم" in bare_text and not any(k in bare_text for k in heroic_kw)):
        if dialect == "bahrani":
            mode = "bahrani_waqfa"
            bpm = 84
            maqam = "hijaz"
            meter = "thulathi"
            tor = "tor_bahrani_waqfa"
            school = "School 03/07 (الوقفة البحرانية الفائزية)"
            prompt = MASTER_SOUND_PROMPTS_V48_5["bahrani_waqfa_84bpm_hijaz_bayati"]
        else:
            mode = "fazzaiya"
            bpm = 84
            maqam = "hijaz"
            meter = "fazzaiya"
            tor = "tor_fazzaiya_karbalai"
            school = "School 05/08 (الفزاعية والرباطات الفراتية)"
            prompt = EXTENDED_ATWAR_PROMPTS_V52["karbalai_fazzaiya_84bpm_hijaz_bayati_v52"]
    elif any(k in bare_text for k in munajat_khidma_kw):
        mode = "thaqeel_muwazza"
        bpm = 58
        maqam = "saba_zamzam"
        meter = "nassari"
        tor = "tor_ashouri"
        school = "School 01/06 (المناجاة الكربلائية الثقيلة وطور الخدمة — باسم الكربلائي)"
        prompt = EXTENDED_ATWAR_PROMPTS_V52["ashura_majlis_noha_58bpm_saba_lami_v55"]
    elif any(k in bare_text for k in heroic_kw) and not any(
        k in bare_text for k in ("ام عباس", "أم عباس", "يا شمر", "سيفك النادم", "سيفه اعلى النحر", "صورة جسد")
    ):
        if dialect == "bahrani":
            mode = "bahrani_haidari"
            bpm = 96
            maqam = "hijaz"
            meter = "muwashah"
            tor = "tor_bahrani_haidari"
            school = "School 02/03 (الحيدري البحراني والإحسائي الموكبي)"
            prompt = MASTER_SOUND_PROMPTS_V48_5["bahrani_haidari_96bpm_hijaz"]
        else:
            mode = "zanjeel_iraqi"
            bpm = 80
            maqam = "hijaz"
            meter = "muwashah"
            tor = "tor_darj_karbalai"
            school = "School 08 (مواكب البصرة والزنجيل الملحمي)"
            prompt = MASTER_SOUND_PROMPTS_V48_5["zanjeel_procession_80bpm_hijaz"]
    elif any(k in bare_text for k in service_kw):
        if dialect == "bahrani":
            mode = "bahrani_thulathi"
            bpm = 76
            maqam = "bayati"
            meter = "thulathi"
            tor = "tor_bahrani_thulathi"
            school = "School 03/07 (اللطم الثلاثي والموكبي البحراني — الأكرف)"
            prompt = EXTENDED_ATWAR_PROMPTS_V52["bahrani_thulathi_76bpm_bayati_hijaz_v54"]
        else:
            mode = "bandari"
            bpm = 74
            maqam = "bayati"
            meter = "rukbani"
            tor = "tor_darj_karbalai"
            school = "School 05 (طور الدرج الموكبي والمشاية)"
            prompt = MASTER_SOUND_PROMPTS_V48_5["karbalai_mawkib_daraj_74bpm_bayati_hijaz"]
    elif dialect == "bahrani":
        if any(k in bare_text for k in thulathi_kw) or (avg_syl <= 7 and len(hemistichs) >= 4):
            mode = "bahrani_thulathi"
            bpm = 76
            maqam = "bayati"
            meter = "thulathi"
            tor = "tor_bahrani_thulathi"
            school = "School 03/07 (اللطم الثلاثي والوقفة البحرانية — الأكرف)"
            prompt = EXTENDED_ATWAR_PROMPTS_V52["bahrani_thulathi_76bpm_bayati_hijaz_v54"]
        else:
            mode = "bahrani_muthakkal"
            bpm = 56
            maqam = "saba"
            meter = "faizi"
            tor = "tor_muthakkal_bahrani"
            school = "School 02/07 (المثكّل والفايزي البحراني/الإحسائي — بوجبارة وبوحمد)"
            prompt = MASTER_SOUND_PROMPTS_V48_5["bahrani_muthakkal_56bpm_saba"]
    elif dialect == "iraqi_bahrani":
        mode = "thaqeel_muwazza"
        bpm = 58
        maqam = "saba"
        meter = "nassari"
        tor = "tor_ashouri"
        school = "School 02/01 (الهجين العراقي-البحراني الفاخر — قافلة عاشوراء)"
        prompt = MASTER_SOUND_PROMPTS_V48_5["iraqi_bahrani_58bpm_saba_fusion_master"]
    elif any(k in bare_text for k in lami_grief_kw) and not any(k in bare_text for k in heroic_kw):
        if any(k in bare_text for k in journey_kw) and avg_syl >= 8:
            mode = "studio_arranged"
            bpm = 64
            maqam = "lami"
            meter = "tajleeba"
            tor = "tor_rukbani_nassari"
            school = "School 05/04 (الركباني والتجليبة الفراتية — حرب والعياشي)"
            prompt = MASTER_SOUND_PROMPTS_V48_5["harb_ayyashi_turaathi_60bpm_lami_bayati_v50"]
        else:
            mode = "thaqeel_muwazza"
            bpm = 56
            maqam = "lami"
            meter = "nassari"
            tor = "tor_lami_iraqi"
            school = "School 04 (الشجن العراقي الثقيل واللامي — السيد سلام)"
            prompt = MASTER_SOUND_PROMPTS_V48_5["sayyid_salam_funeral_muthakkal_56bpm_lami_saba_v50"]
    elif avg_words <= 4.6 and avg_syl <= 7 and len(hemistichs) >= 4:
        mode = "studio_arranged"
        bpm = 68
        maqam = "bayati"
        meter = "rukbani"
        tor = "tor_darj_karbalai"
        school = "School 06 (اللحن الحواري النجفي/الكربلائي — الجنامي والسيد محمد)"
        prompt = MASTER_SOUND_PROMPTS_V48_5["janami_bayati_dialogic_68bpm_bayati_kurd_v50"]
    else:
        mode = "thaqeel_muwazza"
        bpm = 60
        maqam = "bayati"
        meter = "nassari" if avg_syl >= 7 else "rukbani"
        tor = "tor_ashouri"
        school = "School 01 (المدرسة الكربلائية التأسيسية — باسم الكربلائي)"
        prompt = MASTER_SOUND_PROMPTS_V48_5["karbalai_nazla_60bpm_bayati_saba_v48_5_root"]

    wazn_map = {
        "abudhiyah": "بحر الأبوذية المربوعة (جناس + قفلة -يَّه)",
        "zuhayri": "الموال السبعوي (الزهيري AAABAAA)",
        "mujarradat": "مجردات / نعي منبري حر",
        "rukbani": "بحر الركباني",
        "tajleeba": "بحر التجليبة والهزج الفراتي",
        "muwashah": "الموشح الملحمي / التوشيح",
        "fazzaiya": "طور الفزاعية والرباطات",
        "hosa": "الأهزوجة والهوسة الحماسية",
        "thulathi": "اللطم الثلاثي والوقفة البحرانية",
        "faizi": "البحر الفائزي البحراني",
        "nassari": "بحر النصاري الفراتي/الكربلائي",
    }
    stage_key = "bahrani" if dialect == "bahrani" else ("iraqi_bahrani" if dialect == "iraqi_bahrani" else "iraqi")
    progression = build_four_stage_latmiya_plan(dialect=stage_key)
    maqam_arc = [
        progression["stage_1_root_track"]["maqam"],
        progression["stage_2_extend_1_narrative"]["maqam"],
        progression["stage_3_extend_2_jawab_climax"]["maqam"],
        progression["stage_4_extend_3_kasra_finale"]["maqam"],
    ]
    return {
        "detected_dialect": dialect,
        "average_syllables_per_hemistich": avg_syl,
        "recommended_poetic_meter": meter,
        "detected_poetic_wazn_ar": wazn_map.get(meter, "بحر النصاري"),
        "recommended_performance_tor": tor,
        "recommended_school": school,
        "recommended_dsp_mode": mode,
        "recommended_bpm": bpm,
        "recommended_maqam": maqam,
        "recommended_maqam_progression": maqam_arc,
        "five_stage_analysis": {
            "stage_1_structural_and_prosodic": {
                "detected_meter": meter,
                "wazn_ar": wazn_map.get(meter, "بحر النصاري"),
                "avg_syllables": avg_syl,
                "syllable_spread": iso["syllable_spread"],
            },
            "stage_2_dramatic_and_thematic": {
                "school": school,
                "emotional_axis": (
                    "munajat_and_loyalty"
                    if any(k in bare_text for k in munajat_khidma_kw)
                    else ("ashura_tragedy_and_masaaib" if any(k in bare_text for k in tragedy_kw) else "husseini_devotion")
                ),
            },
            "stage_3_maqam_and_vocal_contour": {
                "primary_maqam": maqam,
                "four_stage_maqam_arc": maqam_arc,
                "performance_tor": tor,
            },
            "stage_4_rhythmic_and_matam_architecture": {
                "recommended_bpm": bpm,
                "recommended_dsp_mode": mode,
                "echo_delay_ms": compute_tempo_synced_delay_ms(bpm, mode=mode),
            },
            "stage_5_phonetic_g2p_and_flowmusic_lock": {
                "detected_dialect": dialect,
                "sound_prompt_dialect": dialect_info["sound_prompt_dialect_declaration"],
                "lyria_model_lock": "Lyria 3.5",
                "nc18_nc22_enforced": True,
            },
        },
        "recommended_dsp_params": {
            "echo_delay_ms": compute_tempo_synced_delay_ms(bpm, mode=mode),
            "reverb_rt60_sec": 3.4 if mode in ("mawal", "nai", "thaqeel_muwazza", "bahrani_muthakkal") else 2.4,
            "pre_delay_ms": 22.0 if bpm <= 64 else 32.0,
            "target_lra_lu": "6.5-8.5",
            "deess_band_hz": "5500-8500",
        },
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
        elif chosen_bpm >= 115:
            prompt = MASTER_SOUND_PROMPTS_V48_5["karbalai_shoor_132bpm_kurd"]
        elif chosen_bpm >= 92:
            prompt = (
                MASTER_SOUND_PROMPTS_V48_5["bahrani_haidari_96bpm_hijaz"]
                if dialect == "bahrani"
                else MASTER_SOUND_PROMPTS_V48_5["zanjeel_procession_80bpm_hijaz"]
            )
        elif chosen_bpm >= 82:
            prompt = (
                MASTER_SOUND_PROMPTS_V48_5["bahrani_waqfa_84bpm_hijaz_bayati"]
                if dialect == "bahrani"
                else EXTENDED_ATWAR_PROMPTS_V52["karbalai_fazzaiya_84bpm_hijaz_bayati_v52"]
            )
        elif chosen_bpm >= 70:
            prompt = (
                EXTENDED_ATWAR_PROMPTS_V52["bahrani_thulathi_76bpm_bayati_hijaz_v54"]
                if dialect == "bahrani"
                else MASTER_SOUND_PROMPTS_V48_5["karbalai_mawkib_daraj_74bpm_bayati_hijaz"]
            )
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
        "protocol_name": "Hussaini_Production_Studio_OS_V50_0_OMNI_ARCHITECT",
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
            "single_stanza_extend_law": "Max 6-7 couplets (ONE SINGLE STANZA) per Remix > Extend stage (~80s window — QC30)",
            "lyria_model_lock": "Lyria 3.5 (Strictly ban legacy Lyria 3 Pro — NC19)",
            "remix_cover_strength_cap": 0.45,
            "standalone_preconditioning_warning": "Never send Pre-Conditioning JSON in Producer Chat without Stage 1 poem (NC19)",
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
    elif "stage_2" in stage_id:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["rukbani_nassari_58bpm_lami_saba_v48_5_stage2"]
    elif "stage_3" in stage_id:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5[
            "karbalai_ashouri_jawab_climax_58bpm_saba_zamzam_hijaz_v48_5_stage3"
        ]
    elif "stage_4" in stage_id:
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["karbalai_wahsha_lami_kasra_56bpm_finale_v48_5_stage4"]
    elif dialect == "iraqi_bahrani":
        sound_desc = MASTER_SOUND_PROMPTS_V48_5["iraqi_bahrani_58bpm_saba_fusion_master"]
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

    verbatim_lines = []
    for sec_obj in sections_out:
        verbatim_lines.append(sec_obj["section_tag"])
        verbatim_lines.extend(sec_obj["lyrics_arabic"])

    return {
        "stage_id": stage_id,
        "execution_command": (
            f"Execute {stage_id} in Producer Chat with Instrumental mode strictly OFF "
            "(Single Stanza ONLY — Max 7 Couplets / ~80s Time Budget, QC30). "
            "Register the exact contiguous lines in 'lyrics_register_verbatim' verbatim into "
            "lyrics__register without skipping or summarizing (QC29), and lock sound_description in Sound."
        ),
        "title": title,
        "global_bpm": bpm_val,
        "sound_description": sound_desc,
        "lyrics_register_verbatim": verbatim_lines,
        "sections": sections_out,
    }


def validate_stage_orchestration_json(payload):
    """Module 53, 61 & 62 (QC19, QC29, QC30): Validate a 7-Key Per-Stage & 10-Key Per-Section JSON payload."""
    if not isinstance(payload, dict):
        return {
            "is_valid_stage_json": False,
            "qc19_passed": False,
            "qc29_verbatim_passed": False,
            "qc30_single_stanza_passed": False,
            "missing_stage_keys": list(REQUIRED_STAGE_JSON_KEYS),
            "section_errors": ["Stage payload must be a JSON object (dict)."],
        }

    missing_stage = [k for k in REQUIRED_STAGE_JSON_KEYS if k not in payload]
    section_errors = []
    verbatim = payload.get("lyrics_register_verbatim")
    qc29_ok = isinstance(verbatim, list) and len(verbatim) > 0
    if not qc29_ok:
        section_errors.append("'lyrics_register_verbatim' must be a non-empty list of strings (QC29).")

    sections = payload.get("sections")
    total_arabic_lines = 0
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
            total_arabic_lines += len(lyrics_list)
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

    stage_id_str = str(payload.get("stage_id", ""))
    is_extend_stage = "extend" in stage_id_str.lower() or any(
        k in stage_id_str for k in ("stage_2", "stage_3", "stage_4", "stage_5")
    )
    qc30_ok = not (is_extend_stage and total_arabic_lines > 18)
    if not qc30_ok:
        section_errors.append(
            f"Extend stage exceeds 80s Single-Stanza Law (QC30): {total_arabic_lines} lines (>18 max)."
        )

    is_valid = not missing_stage and not section_errors and qc29_ok and qc30_ok
    return {
        "is_valid_stage_json": is_valid,
        "qc19_passed": is_valid,
        "qc29_verbatim_passed": qc29_ok,
        "qc30_single_stanza_passed": qc30_ok,
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


def _write_wav_pcm16(output_path, sample_rate, stereo_float):
    """Write a float64 [-1, 1] stereo/mono array cleanly to 16-bit PCM WAV using stdlib wave."""
    clipped = np.clip(np.asarray(stereo_float, dtype=np.float64), -1.0, 1.0)
    if clipped.ndim == 1:
        clipped = np.column_stack((clipped, clipped))
    pcm16 = np.clip(np.round(clipped * 32767.0), -32768, 32767).astype("<i2")
    with wave.open(output_path, "wb") as wav_out:
        wav_out.setnchannels(int(pcm16.shape[1]))
        wav_out.setsampwidth(2)
        wav_out.setframerate(int(sample_rate))
        wav_out.writeframes(pcm16.tobytes())


def _decode_audio_with_ffmpeg(input_path, return_stereo=False):
    """Decode compressed audio (.mp3/.m4a/.ogg/.flac) seamlessly via FFmpeg when available."""
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise ValueError(f"FFmpeg required to decode non-WAV audio directly: {input_path}")
    target_sr = 44100
    raw = subprocess.check_output(
        [
            ffmpeg_bin, "-v", "error", "-i", input_path,
            "-ac", "2", "-ar", str(target_sr), "-f", "s16le", "-",
        ],
        stderr=subprocess.DEVNULL,
    )
    arr = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    usable = (len(arr) // 2) * 2
    stereo = np.clip(arr[:usable].reshape(-1, 2), -1.0, 1.0)
    if return_stereo:
        return target_sr, stereo, 2, "FFmpeg Decoded 16-bit PCM"
    mono = np.mean(stereo, axis=1) if stereo.shape[0] else np.zeros(0, dtype=np.float64)
    return target_sr, np.clip(mono, -1.0, 1.0), 2, "FFmpeg Decoded 16-bit PCM"


def read_wav_any_depth(input_path, return_stereo=False):
    """Read 8/16/24/32-bit PCM/Float WAV or compressed MP3/M4A/OGG/FLAC into float64 [-1, 1]."""
    ext = os.path.splitext(str(input_path))[1].lower()
    if ext in (".mp3", ".m4a", ".aac", ".ogg", ".opus", ".flac", ".wma", ".webm"):
        return _decode_audio_with_ffmpeg(input_path, return_stereo=return_stereo)

    with open(input_path, "rb") as handle:
        header = handle.read(12)
        if len(header) < 12 or header[:4] != b"RIFF" or header[8:12] != b"WAVE":
            raise ValueError(f"Not a valid RIFF/WAVE file: {input_path}")
        audio_fmt = 1
        channels = 1
        sample_rate = 44100
        bits_per_sample = 16
        data_bytes = b""
        while True:
            chunk_hdr = handle.read(8)
            if len(chunk_hdr) < 8:
                break
            chunk_id, chunk_size = struct.unpack("<4sI", chunk_hdr)
            chunk_payload = handle.read(chunk_size)
            if chunk_size % 2 == 1:
                handle.read(1)
            if chunk_id == b"fmt " and len(chunk_payload) >= 16:
                audio_fmt, channels, sample_rate, _, _, bits_per_sample = struct.unpack(
                    "<HHIIHH", chunk_payload[:16]
                )
            elif chunk_id == b"data":
                data_bytes = chunk_payload
                break

    if not data_bytes:
        empty_shape = (0, 2) if return_stereo else 0
        return int(sample_rate), np.zeros(empty_shape, dtype=np.float64), int(channels), f"{bits_per_sample}-bit PCM"

    if audio_fmt == 3 and bits_per_sample == 32:
        raw = np.frombuffer(data_bytes, dtype="<f4").astype(np.float64)
        bit_depth = "32-bit Float"
    elif bits_per_sample == 8:
        raw = (np.frombuffer(data_bytes, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
        bit_depth = "8-bit PCM"
    elif bits_per_sample == 16:
        raw = np.frombuffer(data_bytes, dtype="<i2").astype(np.float64) / 32768.0
        bit_depth = "16-bit PCM"
    elif bits_per_sample == 24:
        usable = (len(data_bytes) // 3) * 3
        byte_arr = np.frombuffer(data_bytes[:usable], dtype=np.uint8).reshape(-1, 3)
        signed = (
            byte_arr[:, 0].astype(np.int32)
            | (byte_arr[:, 1].astype(np.int32) << 8)
            | (byte_arr[:, 2].astype(np.int32) << 16)
        )
        neg_mask = (signed & 0x800000) != 0
        signed[neg_mask] -= 1 << 24
        raw = signed.astype(np.float64) / 8388608.0
        bit_depth = "24-bit PCM"
    else:
        signed32 = np.frombuffer(data_bytes, dtype="<i4").astype(np.float64)
        max_abs = float(np.max(np.abs(signed32))) if signed32.size else 0.0
        if 0.0 < max_abs <= 8388608.0:
            raw = signed32 / 8388608.0
            bit_depth = "24-bit PCM (32-bit container)"
        else:
            raw = signed32 / 2147483648.0
            bit_depth = "32-bit PCM"

    if channels > 1:
        usable_frames = (len(raw) // channels) * channels
        multichan = raw[:usable_frames].reshape(-1, channels)
        if return_stereo:
            return (
                int(sample_rate),
                np.clip(multichan[:, :2], -1.0, 1.0),
                int(channels),
                bit_depth,
            )
        mono = np.mean(multichan, axis=1)
    else:
        mono = raw
        if return_stereo:
            clipped = np.clip(mono, -1.0, 1.0)
            return (
                int(sample_rate),
                np.column_stack((clipped, clipped)),
                int(channels),
                bit_depth,
            )
    return int(sample_rate), np.clip(mono, -1.0, 1.0), int(channels), bit_depth


_MAQAM_24EDO_TEMPLATES = {
    "bayati": {0: 1.8, 3: 1.7, 5: 1.2, 10: 1.6, 14: 1.2, 16: 0.9, 20: 0.9},
    "saba": {0: 1.8, 3: 1.7, 5: 1.3, 8: 2.0, 14: 1.0, 16: 0.9, 20: 0.8},
    "saba_zamzam": {0: 1.7, 2: 1.5, 5: 1.3, 8: 2.0, 14: 1.0, 16: 0.9, 20: 0.8},
    "hijaz": {0: 1.8, 2: 1.6, 8: 1.8, 10: 1.4, 14: 1.2, 16: 0.9, 20: 0.8},
    "lami": {0: 1.8, 2: 1.4, 6: 1.3, 10: 1.4, 12: 1.7, 16: 0.9, 20: 0.8},
    "kurd": {0: 1.8, 2: 1.3, 6: 1.2, 10: 1.3, 14: 1.2, 16: 0.9, 20: 0.8},
    "rast": {0: 1.8, 4: 1.2, 7: 1.7, 10: 1.3, 14: 1.2, 18: 1.0, 21: 1.3},
    "nahawand": {0: 1.8, 4: 1.2, 6: 1.3, 10: 1.3, 14: 1.2, 16: 0.9, 22: 1.0},
    "sikah": {0: 1.8, 3: 1.4, 7: 1.6, 10: 1.3, 13: 1.3, 17: 1.0, 20: 0.9},
}


def _extract_24edo_maqam_profile(mono, sample_rate):
    """Module 69 (V54.0): Singer-relative 12-cent anchor 24-EDO chroma & Saba/Bayati Maqam classifier."""
    if len(mono) < 512:
        return "bayati", 146.83, 0.0, [("bayati", 1.0)]
    voc = butter_filter(mono, [90.0, min(3200.0, 0.45 * sample_rate)], sample_rate, btype="band", order=3)
    win = max(256, int(0.12 * sample_rate))
    hop = max(128, int(0.06 * sample_rate))
    nfft = 16384
    if len(voc) < win:
        return "bayati", 146.83, 0.0, [("bayati", 1.0)]

    freqs = np.fft.rfftfreq(nfft, d=1.0 / sample_rate)
    lo = int(np.searchsorted(freqs, 90.0))
    hi = int(np.searchsorted(freqs, min(420.0, 0.42 * sample_rate)))
    hann = np.hanning(win)
    nf = (len(voc) - win) // hop + 1
    rms = np.array([float(np.sqrt(np.mean(voc[i * hop : i * hop + win] ** 2))) for i in range(nf)])
    gate = max(1e-4, 0.25 * float(np.percentile(rms, 90))) if nf > 0 else 1e-4

    obs = []
    for i in range(nf):
        if rms[i] < gate:
            continue
        spec = np.abs(np.fft.rfft(voc[i * hop : i * hop + win] * hann, n=nfft))
        lim = max(1, len(spec) // 3)
        s1 = spec[:lim]
        mx = float(np.max(s1)) + 1e-12
        s2 = spec[::2][:lim] / mx
        s3 = spec[::3][:lim] / mx
        hscore = s1 * (0.35 + 0.45 * s2) * (0.45 + 0.35 * s3)
        hi_lim = min(hi, len(hscore) - 1)
        if hi_lim <= lo:
            continue
        k = lo + int(np.argmax(hscore[lo:hi_lim]))
        if 0 < k < len(hscore) - 1:
            den = hscore[k - 1] - 2.0 * hscore[k] + hscore[k + 1]
            dk = 0.5 * (hscore[k - 1] - hscore[k + 1]) / den if abs(den) > 1e-12 else 0.0
            dk = float(np.clip(dk, -0.5, 0.5))
            f0 = max(60.0, (k + dk) * (sample_rate / float(nfft)))
        else:
            f0 = max(60.0, float(freqs[k]))
        cad = 2.0 if (i + 2 < nf and rms[i + 2] < 0.65 * rms[i]) else 1.0
        obs.append((24.0 * math.log2(f0 / 440.0), f0, rms[i], cad))

    if not obs:
        return "bayati", 146.83, 0.0, [("bayati", 1.0)]

    med_f0 = float(np.median([item[1] for item in obs]))
    h120 = np.zeros(120, dtype=np.float64)
    for qt_val, _, r_val, cad_val in obs:
        h120[int(round(qt_val * 5.0)) % 120] += r_val * cad_val

    seen = {}
    for a120 in np.argsort(h120)[::-1][:10]:
        if h120[a120] <= 0.0:
            continue
        ch24 = np.zeros(24, dtype=np.float64)
        a_qt = a120 / 5.0
        for qt_val, _, r_val, _ in obs:
            ch24[int(round(qt_val - a_qt)) % 24] += r_val
        ch24 /= float(ch24.sum()) + 1e-9
        if ch24[0] < 0.07:
            continue
        odd_qt = float(ch24[1::2].sum())
        for mn, prof in _MAQAM_24EDO_TEMPLATES.items():
            pos = sum(ch24[d] * w for d, w in prof.items())
            non_sc = sum(ch24[d] for d in range(24) if d not in prof)
            has_qt = any(d % 2 == 1 for d in prof)
            qt_bonus = 0.25 * odd_qt if has_qt else -0.25 * max(0.0, odd_qt - 0.12)
            razor = 0.0
            if mn == "saba":
                razor = 0.45 * (ch24[8] - 0.5 * ch24[10])
            elif mn == "bayati":
                razor = 0.30 * (ch24[10] - ch24[8])
            sc = pos - 0.6 * non_sc + qt_bonus + razor
            if mn not in seen or sc > seen[mn][0]:
                seen[mn] = (sc, odd_qt)

    if not seen:
        return _classify_maqam_from_pitches(med_f0), round(med_f0, 2), 0.0, [("bayati", 1.0)]
    ranked = sorted([(val[0], name, val[1]) for name, val in seen.items()], reverse=True)
    best_sc, best_name, best_qt = ranked[0]
    _ = best_sc
    top3 = [(name, round(float(sc), 3)) for sc, name, _ in ranked[:3]]
    return best_name, round(med_f0, 2), round(float(best_qt), 3), top3


def _classify_maqam_from_pitches(detected_hz):
    """Find the closest 24-EDO Maqam in MAQAM_FREQS using minimum cents distance."""
    if isinstance(detected_hz, (list, tuple, np.ndarray)):
        vals = [float(v) for v in detected_hz if float(v) > 0.0]
        if not vals:
            return "saba"
        detected_hz = float(np.median(vals))
    if detected_hz <= 0.0:
        return "saba"
    best_maqam = "saba"
    best_cents = 1e9
    for maqam_name, freqs in MAQAM_FREQS.items():
        for target_hz in freqs:
            folded = float(detected_hz)
            while folded > target_hz * 1.45:
                folded *= 0.5
            while folded < target_hz * 0.70:
                folded *= 2.0
            cents = abs(1200.0 * np.log2(max(folded, 1e-6) / target_hz))
            if cents < best_cents:
                best_cents = cents
                best_maqam = maqam_name
    return best_maqam


def _compute_dual_band_bpm(mono, sample_rate):
    """Detect BPM via adaptive local-peak Sub-Chest (45-135Hz) + Fullband autocorrelation & Rubato detection."""
    hop = max(1, int(0.02 * sample_rate))
    n_frames = len(mono) // hop
    if n_frames < 50:
        return 60, "short_default", False, 0.0

    def _band_acorr(sig):
        frames = sig[: n_frames * hop].reshape(n_frames, hop)
        env = np.sqrt(np.mean(frames**2, axis=1) + 1e-12)
        on_raw = np.maximum(0.0, np.diff(env, prepend=env[0]))
        loc = _fast_boxcar_mean(on_raw, max(5, int(0.45 / 0.02)))
        onset = np.maximum(0.0, on_raw - loc)
        onset -= np.mean(onset)
        if float(np.std(onset)) <= 1e-7:
            return 60, 0.0, 0.0, 0.0
        ac = np.correlate(onset, onset, mode="full")[len(onset) - 1 :]
        ac = ac / np.maximum(1, len(onset) - np.arange(len(ac)))
        ac0 = max(float(ac[0]), 1e-12)
        min_l = max(2, int((60.0 / 145.0) / 0.02))
        max_l = min(len(ac) - 2, int((60.0 / 48.0) / 0.02))
        if max_l <= min_l:
            return 60, 0.0, 0.0, 0.0
        pks = [k for k in range(min_l, max_l + 1) if ac[k] >= ac[k - 1] and ac[k] >= ac[k + 1] and ac[k] > 0.0]
        if not pks:
            return 0, 0.0, 0.0, 0.0
        best_l = max(pks, key=lambda k: ac[k])
        if best_l * 2 <= max_l and ac[best_l * 2] >= 0.72 * ac[best_l]:
            best_l *= 2
        strength = float(ac[best_l]) / ac0
        seg_ac = ac[min_l : max_l + 1]
        prom = float(ac[best_l]) / max(float(np.median(np.abs(seg_ac))), 1e-9)
        lag3 = int(round(best_l / 3.0))
        lag2 = int(round(best_l / 2.0))
        e3 = max(0.0, float(ac[lag3])) if 0 < lag3 < len(ac) else 0.0
        e2 = max(0.0, float(ac[lag2])) if 0 < lag2 < len(ac) else 0.0
        trip = e3 / max(e2 + e3, 1e-9)
        return int(round(60.0 / (best_l * 0.02))), strength, prom, trip

    low_sig = butter_filter(mono, [45.0, min(135.0, 0.45 * sample_rate)], sample_rate, btype="band", order=3)
    b_low, st_low, pr_low, tr_low = _band_acorr(low_sig)
    b_full, st_full, pr_full, tr_full = _band_acorr(mono)

    if st_low >= 0.16 and b_low > 0:
        return b_low, "sub_chest_45_135hz", False, round(tr_low, 3)
    if len(mono) >= 12.0 * sample_rate and (
        max(st_low, st_full) < 0.032 or (max(st_low, st_full) < 0.045 and max(pr_low, pr_full) < 4.5)
    ):
        return 0, "rubato_free_tempo", True, 0.0
    if b_full > 0:
        return b_full, "fullband_onset", False, round(tr_full, 3)
    return 0 if len(mono) >= 12.0 * sample_rate else 60, "fallback", False, 0.0


def extract_reference_audio_profile(input_path):
    """Module 45, 68 & 69: Reverse-engineer Dual-Band BPM, 24-EDO Maqam, EQ/Stereo & School."""
    sample_rate, stereo, channels, bit_depth = read_wav_any_depth(input_path, return_stereo=True)
    mono = np.mean(stereo, axis=1) if stereo.shape[0] > 0 else np.zeros(0, dtype=np.float64)
    duration_sec = round(len(mono) / max(1.0, float(sample_rate)), 3)

    loud_stats = measure_ebu_r128_loudness(stereo if channels > 1 else mono, sample_rate)
    lufs_approx = loud_stats["integrated_lufs"]

    # Stereo width & dynamic crest factor
    mid = 0.5 * (stereo[:, 0] + stereo[:, 1]) if stereo.shape[0] > 0 else mono
    side = 0.5 * (stereo[:, 0] - stereo[:, 1]) if stereo.shape[0] > 0 else np.zeros(0, dtype=np.float64)
    mid_rms = float(np.sqrt(np.mean(mid * mid) + 1e-12)) if len(mid) else 1e-9
    side_rms = float(np.sqrt(np.mean(side * side) + 1e-12)) if len(side) else 1e-9
    side_mid_db = round(20.0 * math.log10(max(side_rms, 1e-9) / max(mid_rms, 1e-9)), 2)

    full_rms = float(np.sqrt(np.mean(mono * mono) + 1e-12)) if len(mono) else 1e-9
    peak_lin = float(np.max(np.abs(mono)) + 1e-12) if len(mono) else 1e-9
    crest_db = round(20.0 * math.log10(peak_lin / full_rms), 2)
    full_db = 20.0 * math.log10(max(full_rms, 1e-9))

    def _rel_band_db(lo_hz, hi_hz):
        if hi_hz >= 0.46 * sample_rate or lo_hz >= hi_hz or len(mono) < 256:
            return None
        filt = butter_filter(mono, [lo_hz, hi_hz], sample_rate, btype="band", order=3)
        b_rms = float(np.sqrt(np.mean(filt * filt) + 1e-12))
        return round(20.0 * math.log10(max(b_rms, 1e-9)) - full_db, 2)

    spectral_bands = {
        "sub_45_95_rel_db": _rel_band_db(45.0, 95.0),
        "bass_95_220_rel_db": _rel_band_db(95.0, 220.0),
        "mud_250_550_rel_db": _rel_band_db(250.0, 550.0),
        "core_600_1800_rel_db": _rel_band_db(600.0, 1800.0),
        "pres_1800_4500_rel_db": _rel_band_db(1800.0, 4500.0),
        "sib_5500_8500_rel_db": _rel_band_db(5500.0, 8500.0),
    }

    closest_maqam, dom_hz, qt_ratio, maqam_top3 = _extract_24edo_maqam_profile(mono, sample_rate)
    estimated_bpm, bpm_src, is_rubato, triplet_ratio = _compute_dual_band_bpm(mono, sample_rate)

    if is_rubato or estimated_bpm == 0:
        rec_mode = "nai"
        school_guess = "School 04/01 (نعي منبري وموال حر — 0 BPM)"
    elif estimated_bpm >= 115:
        rec_mode = "shoor"
        school_guess = "School 05/09 (شور كربلائي أو إيراني متسارع)"
    elif estimated_bpm >= 92:
        rec_mode = "bahrani_haidari"
        school_guess = "School 02/03 (الحيدري الموكبي المتسارع)"
    elif estimated_bpm >= 80:
        rec_mode = "fazzaiya"
        school_guess = "School 05/08 (فزاعية ووقفة عاشورائية)"
    elif estimated_bpm >= 70 and triplet_ratio >= 0.26:
        rec_mode = "bahrani_thulathi"
        school_guess = "School 03/07 (اللطم الثلاثي البحراني — الأكرف)"
    elif estimated_bpm >= 70:
        rec_mode = "bandari"
        school_guess = "School 05/01 (درج موكبي ومشاية)"
    elif estimated_bpm >= 63:
        rec_mode = "studio_arranged"
        school_guess = "School 06/01 (نزلة كربلائية أو حوارية استوديوية)"
    else:
        rec_mode = "thaqeel_muwazza"
        school_guess = (
            "School 04 (شجن ثقيل جنائزي — السيد سلام)"
            if estimated_bpm <= 57
            else "School 01/02 (ثقيل موزع — باسم وبوجبارة)"
        )

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
        "bpm_source": bpm_src,
        "is_rubato_free_tempo": is_rubato,
        "triplet_swing_ratio": triplet_ratio,
        "estimated_fundamental_hz": round(dom_hz, 2),
        "closest_maqam": closest_maqam,
        "maqam_top3_candidates": maqam_top3,
        "quarter_tone_energy_ratio": qt_ratio,
        "integrated_lufs": loud_stats["integrated_lufs"],
        "integrated_lufs_approx": lufs_approx,
        "lra_lu": loud_stats["lra_lu"],
        "crest_factor_db": crest_db,
        "side_mid_stereo_db": side_mid_db,
        "spectral_bands_rel_db": spectral_bands,
        "closest_master_school": school_guess,
        "recommended_dsp_mode": rec_mode,
        "recommended_sound_prompt": profile_prompt,
    }


def _fast_boxcar_mean(signal, win):
    """Fast O(N) chunked cumsum boxcar moving average matching centered mode='same' length."""
    arr = np.asarray(signal, dtype=np.float64)
    n = arr.shape[0]
    w = max(1, int(win))
    if n == 0 or w <= 1:
        return arr.copy()
    left_pad = w // 2
    right_pad = (w - 1) // 2
    padded = np.pad(arr, (left_pad, right_pad), mode="constant", constant_values=0.0)
    out = np.empty(n, dtype=np.float64)
    chunk_sz = 65536
    inv_w = 1.0 / float(w)
    for start in range(0, n, chunk_sz):
        end = min(n, start + chunk_sz)
        seg = padded[start : end + w - 1]
        csum = np.empty(seg.shape[0] + 1, dtype=np.float64)
        csum[0] = 0.0
        np.cumsum(seg, out=csum[1:])
        out[start:end] = (csum[w:] - csum[:-w]) * inv_w
    return out


def suppress_whip_snap_transients(signal, sample_rate):
    """Module 71 (V56.0): Crossover (>1.85 kHz) fast/slow transient ratio suppressor for AI rim/whip-snaps."""
    if len(signal) < 64 or sample_rate <= 8000:
        return signal
    low_mid = butter_filter(signal, 1850.0, sample_rate, btype="low", order=2)
    snap_band = butter_filter(signal, 1850.0, sample_rate, btype="high", order=2)
    env = np.abs(snap_band)
    fast_win = max(1, int(0.003 * sample_rate))
    slow_win = max(fast_win + 2, int(0.240 * sample_rate))
    fast_env = _fast_boxcar_mean(env, fast_win)
    slow_env = _fast_boxcar_mean(env, slow_win) + 1e-7
    med_hi = float(np.median(env) + 1e-7)
    ratio = np.maximum(fast_env / slow_env, fast_env / (2.2 * med_hi))
    thresh = 1.45
    gain = np.where(ratio > thresh, np.clip((thresh / (ratio + 1e-9)) ** 1.85, 0.10, 1.0), 1.0)
    smooth_gain = _fast_boxcar_mean(gain, max(1, int(0.004 * sample_rate)))
    return low_mid + snap_band * smooth_gain


def strip_ai_percussion_from_vocal(signal, sample_rate):
    """Module 44, 67 & 71: Attenuate AI sub-thumps (<105Hz) & high-band whip-snap transients while preserving air."""
    de_snapped = suppress_whip_snap_transients(signal, sample_rate)
    cleaned = butter_filter(de_snapped, 105.0, sample_rate, btype="high", order=4)
    fast_win = max(1, int(0.005 * sample_rate))
    slow_win = max(fast_win + 2, int(0.060 * sample_rate))

    sq = cleaned**2
    fast_rms = np.sqrt(np.maximum(_fast_boxcar_mean(sq, fast_win), 1e-12))
    slow_rms = np.sqrt(np.maximum(_fast_boxcar_mean(sq, slow_win), 1e-12))

    ratio = fast_rms / (slow_rms + 1e-6)
    transient_gain = np.where(ratio > 1.95, np.clip(1.95 / np.maximum(ratio, 1e-6), 0.35, 1.0), 1.0)
    smooth_win = max(1, int(0.004 * sample_rate))
    smooth_gain = _fast_boxcar_mean(transient_gain, smooth_win)
    declicked = cleaned * smooth_gain
    return butter_filter(declicked, min(11500.0, 0.46 * sample_rate), sample_rate, btype="low", order=2)


def apply_noise_print_restoration(signal, sample_rate):
    """Suppress background floor in quiet frames while preserving natural consonant breath."""
    win = max(1, int(0.025 * sample_rate))
    sq = signal**2
    rms_env = np.sqrt(np.maximum(_fast_boxcar_mean(sq, win), 1e-12))
    noise_floor = float(np.percentile(rms_env, 10))
    threshold = max(noise_floor * 1.5, 1e-5)
    gate_gain = np.clip(rms_env / threshold, 0.45, 1.0)
    smooth = max(1, int(0.015 * sample_rate))
    gate_smooth = _fast_boxcar_mean(gate_gain, smooth)
    return signal * gate_smooth


def apply_vocal_eq(signal, sample_rate, preserve_chest_thud=False):
    """Module 63 & 69 (V54.0): Apply 175-track calibrated EQ (mud notch @ 450Hz, pharyngeal 1.2kHz, presence)."""
    hpf_hz = 42.0 if preserve_chest_thud else 84.0
    out = butter_filter(signal, hpf_hz, sample_rate, btype="high", order=2 if preserve_chest_thud else 4)
    if 450.0 < 0.45 * sample_rate:
        b_mud, a_mud = iirnotch(450.0, 2.2, sample_rate)
        out = 0.72 * out + 0.28 * lfilter(b_mud, a_mud, out)
    if 2500.0 < 0.45 * sample_rate:
        b_harsh, a_harsh = iirnotch(2500.0, 3.8, sample_rate)
        out = 0.88 * out + 0.12 * lfilter(b_harsh, a_harsh, out)
    core = butter_filter(out, [900.0, min(1750.0, 0.43 * sample_rate)], sample_rate, btype="band", order=2)
    presence = butter_filter(out, [1850.0, min(4300.0, 0.44 * sample_rate)], sample_rate, btype="band", order=2)
    warm = (
        butter_filter(out, [95.0, min(190.0, 0.42 * sample_rate)], sample_rate, btype="band", order=2)
        if preserve_chest_thud
        else 0.0
    )
    return out + 0.14 * core + (0.14 if preserve_chest_thud else 0.18) * presence + (0.08 * warm if preserve_chest_thud else 0.0)


def apply_arabic_deesser(signal, sample_rate, threshold_ratio=0.35, max_atten_db=4.5):
    """Module 69 (V54.0): Dynamically tame 5.5-8.5kHz Arabic sibilance (ص/س/ش) per Basim/Akraf curves."""
    if len(signal) < 64 or sample_rate <= 18500:
        return signal
    hi_cut = min(8500.0, 0.45 * sample_rate)
    if hi_cut <= 5600.0:
        return signal
    sib_band = butter_filter(signal, [5500.0, hi_cut], sample_rate, btype="band", order=3)
    fast_win = max(1, int(0.008 * sample_rate))
    slow_win = max(fast_win + 2, int(0.080 * sample_rate))
    sib_rms = np.sqrt(np.maximum(_fast_boxcar_mean(sib_band**2, fast_win), 1e-12))
    full_rms = np.sqrt(np.maximum(_fast_boxcar_mean(signal**2, slow_win), 1e-12))
    thresh = np.maximum(1e-4, threshold_ratio * full_rms)
    excess = np.maximum(0.0, sib_rms / np.maximum(thresh, 1e-6) - 1.0)
    min_gain = 10.0 ** (-abs(max_atten_db) / 20.0)
    gain = np.clip(1.0 / (1.0 + 0.85 * excess), min_gain, 1.0)
    return (signal - sib_band) + sib_band * gain


def apply_optical_vocal_compressor(signal, sample_rate, threshold_db=-20.0, ratio=2.2):
    """Module 69 (V54.0): Gentle RMS optical vocal leveler tightening LRA toward 6-9 LU studio sweet spot."""
    if len(signal) < 64:
        return signal
    win = max(1, int(0.080 * sample_rate))
    rms = np.sqrt(np.maximum(_fast_boxcar_mean(signal**2, win), 1e-12))
    rms_db = 20.0 * np.log10(np.maximum(rms, 1e-6))
    over_db = np.maximum(0.0, rms_db - threshold_db)
    reduced_db = over_db * (1.0 - 1.0 / max(ratio, 1.0))
    gain = 10.0 ** (-reduced_db / 20.0)
    smooth_win = max(1, int(0.040 * sample_rate))
    gain_smooth = _fast_boxcar_mean(gain, smooth_win)
    return signal * gain_smooth


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
    rms = np.sqrt(np.maximum(_fast_boxcar_mean(vocal_signal**2, win), 1e-12))
    thresh_lin = 10.0 ** (threshold_dbfs / 20.0)
    min_gain = 10.0 ** (duck_db / 20.0)
    active = np.clip((rms - thresh_lin) / max(thresh_lin * 2.0, 1e-6), 0.0, 1.0)
    raw_gain = 1.0 - active * (1.0 - min_gain)
    rel_win = max(1, int(0.080 * sample_rate))
    return _fast_boxcar_mean(raw_gain, rel_win)


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


def apply_husseiniya_reverb(signal, sample_rate, rt60_sec=2.8, pre_delay_ms=24.0, wet=0.22, seed=4850):
    """Apply sacred Husseiniya dome impulse response with discrete early reflections + smooth tail."""
    ir_len = max(16, int(min(rt60_sec, 3.8) * sample_rate))
    rng = np.random.default_rng(int(seed))
    t_ir = np.linspace(0.0, rt60_sec, ir_len, endpoint=False)
    attack = 1.0 - np.exp(-35.0 * t_ir)
    decay = np.exp(-6.91 * t_ir / max(rt60_sec, 0.2))
    ir = rng.normal(0.0, 1.0, ir_len) * attack * decay
    for tap_ms, tap_amp in ((11.0, 0.28), (19.0, 0.21), (29.0, 0.16), (43.0, 0.11)):
        idx = int((tap_ms / 1000.0) * sample_rate)
        if idx < ir_len:
            ir[idx] += tap_amp
    ir = butter_filter(ir, [140.0, min(5200.0, 0.44 * sample_rate)], sample_rate, btype="band", order=2)
    norm = float(np.sqrt(np.sum(ir**2)) + 1e-9)
    ir /= norm

    pre_samples = max(0, int((pre_delay_ms / 1000.0) * sample_rate))
    convolved = fftconvolve(signal, ir)[: len(signal)]
    if 0 < pre_samples < len(convolved):
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
        chest_low = np.sin(2.0 * np.pi * (52.0 + 18.0 * np.exp(-24.0 * t_vec)) * t_vec) * np.exp(-11.0 * t_vec)
        sub_hum = (
            np.sin(2.0 * np.pi * 46.0 * t_vec)
            * (1.0 - np.exp(-28.0 * t_vec))
            * np.exp(-8.0 * t_vec)
        )
        # V52: Warm fleshy chest/palm body (140-520 Hz) replacing harsh synthetic woodblock click
        palm_meat = butter_filter(
            rng.normal(0.0, 1.0, num_samples) * np.exp(-32.0 * t_vec),
            [140.0, 520.0],
            sample_rate,
            btype="band",
            order=2,
        )
        return vel_jit * (0.72 * chest_low + 0.36 * sub_hum + 0.28 * palm_meat)

    if kind in ("bahrani_fast", "bahrani_haidari", "bahrani_waqfa", "fazzaiya"):
        chest_core = np.sin(2.0 * np.pi * (60.0 + 14.0 * np.exp(-28.0 * t_vec)) * t_vec) * np.exp(-15.0 * t_vec)
        palm_thump = butter_filter(
            rng.normal(0.0, 1.0, num_samples) * np.exp(-30.0 * t_vec),
            [180.0, 780.0],
            sample_rate,
            btype="band",
            order=2,
        )
        return vel_jit * (0.74 * chest_core + 0.34 * palm_thump)

    if kind in ("studio_arranged", "bahrani_thulathi", "bahrani_rubai"):
        sub_kick = np.sin(2.0 * np.pi * 55.0 * t_vec) * np.exp(-14.0 * t_vec)
        palm_body = butter_filter(
            rng.normal(0.0, 1.0, num_samples) * np.exp(-36.0 * t_vec),
            [160.0, 620.0],
            sample_rate,
            btype="band",
            order=2,
        )
        return vel_jit * (0.72 * sub_kick + 0.26 * palm_body)

    sub_thud = np.sin(2.0 * np.pi * 55.0 * t_vec) * np.exp(-15.0 * t_vec)
    skin_slap = butter_filter(
        rng.normal(0.0, 1.0, num_samples) * np.exp(-34.0 * t_vec),
        [180.0, 750.0],
        sample_rate,
        btype="band",
        order=2,
    )
    return vel_jit * (0.80 * sub_thud + 0.24 * skin_slap)


def _add_hit_at(bed, hit, pos, gain=1.0):
    """Mix a one-shot percussion array safely into bed at sample index pos."""
    if pos < 0 or pos >= len(bed):
        return
    end = min(len(bed), pos + len(hit))
    bed[pos:end] += gain * hit[: end - pos]


def build_rhythm_bed(
    num_samples,
    sample_rate,
    mode="latm",
    bpm=60.0,
    offset_samples=0,
    swing=0.0,
    samples_dir=None,
    vocal_signal=None,
):
    """Build 18-mode round-robin Husseiniya percussion bed with optional vocal-envelope gating."""
    bed = np.zeros(num_samples, dtype=np.float64)
    if bpm <= 0.0 or mode in ("vocal_pure_master", "mawal", "nai") or num_samples <= 0:
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
            step_in_bar = beat_idx % 3
            if step_in_bar == 0:
                _add_hit_at(bed, main_bank[rr], cursor, gain=1.08)
                _add_hit_at(bed, main_bank[(rr + 1) % rr_count], cursor + int(0.36 * beat_samples), gain=0.82)
            elif step_in_bar == 1:
                _add_hit_at(bed, main_bank[rr], cursor, gain=0.92)
                _add_hit_at(bed, main_bank[(rr + 2) % rr_count], cursor + int(0.66 * beat_samples), gain=0.68)
            else:
                _add_hit_at(bed, breath_bank[rr], cursor, gain=0.84)
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
            jitter = int(((rr - 1.5) * 0.0025) * sample_rate)
            _add_hit_at(bed, main_bank[rr], max(0, cursor + jitter), gain=0.96)
            _add_hit_at(bed, main_bank[(rr + 1) % rr_count], cursor + beat_samples // 2, gain=0.80)
            _add_hit_at(bed, breath_bank[rr], cursor + beat_samples // 2, gain=0.92)
        elif mode == "fazzaiya":
            _add_hit_at(bed, main_bank[rr], cursor, gain=0.98)
            _add_hit_at(bed, main_bank[(rr + 1) % rr_count], cursor + int(0.5 * beat_samples), gain=0.62)
        elif mode == "studio_arranged":
            _add_hit_at(bed, main_bank[rr], cursor, gain=0.95)
            _add_hit_at(bed, main_bank[(rr + 1) % rr_count], cursor + beat_samples // 2, gain=0.35)
        else:
            _add_hit_at(bed, main_bank[rr], cursor, gain=0.92)
            _add_hit_at(bed, breath_bank[rr], cursor + beat_samples // 2, gain=0.34)

        cursor += beat_samples
        beat_idx += 1

    if vocal_signal is not None and len(vocal_signal) == num_samples and num_samples > 0:
        win = min(num_samples, max(1, int(0.85 * sample_rate)))
        v_rms = np.sqrt(np.maximum(_fast_boxcar_mean(vocal_signal**2, win)[:num_samples], 1e-12))
        v_gate = np.clip((v_rms - 0.008) / 0.015, 0.15, 1.0)
        bed *= v_gate

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


def estimate_singer_tonic_root_hz(mono, sample_rate, fallback_hz=110.0):
    """Module 71 (V56.0): Detect singer's actual fundamental tonic and fold into bass register [73, 146] Hz."""
    if len(mono) < 256:
        return float(fallback_hz)
    _, med_f0, _, _ = _extract_24edo_maqam_profile(mono, sample_rate)
    root_hz = float(med_f0) if med_f0 and med_f0 > 40.0 else float(fallback_hz)
    while root_hz > 146.0:
        root_hz *= 0.5
    while root_hz < 73.0:
        root_hz *= 2.0
    return round(root_hz, 2)


def build_vocal_pulse_locked_chest_latm(mono, sample_rate, mode="thaqeel_muwazza", target_bpm=60.0):
    """Module 71 (V56.0): Derive < 460 Hz bare-palm chest impacts directly from vocal/Raddada pulse peaks."""
    num_samples = len(mono)
    if num_samples == 0:
        return np.zeros(0, dtype=np.float64), 0
    low_vocal = butter_filter(mono, [105.0, 420.0], sample_rate, btype="band", order=2)
    win = max(1, int(0.065 * sample_rate))
    env = np.sqrt(np.maximum(0.0, _fast_boxcar_mean(low_vocal**2, win)))
    beat_sec = 60.0 / max(30.0, min(145.0, float(target_bpm)))
    min_gap = max(1, int(0.76 * beat_sec * sample_rate))
    max_gap = max(min_gap + 1, int(1.42 * beat_sec * sample_rate))
    step_samples = max(1, int(beat_sec * sample_rate))
    med_env = float(np.median(env) + 1e-8)
    start_idx = detect_vocal_onset_offset_samples(mono, sample_rate)
    hit_positions = []
    pos = start_idx
    while pos < num_samples - int(0.45 * sample_rate):
        win_s = max(start_idx, pos - int(0.28 * step_samples))
        win_e = min(num_samples - 1, pos + int(0.32 * step_samples))
        if win_e <= win_s:
            break
        local_peak = win_s + int(np.argmax(env[win_s:win_e]))
        if env[local_peak] >= 0.45 * med_env:
            if not hit_positions or (local_peak - hit_positions[-1]) >= min_gap:
                hit_positions.append(local_peak)
                pos = local_peak + step_samples
            else:
                pos += step_samples
        else:
            if hit_positions and (pos - hit_positions[-1]) <= max_gap:
                hit_positions.append(pos)
            pos += step_samples

    hit_kind = "latm" if mode == "wahda" else "thaqeel_muwazza"
    chest_hit = synthesize_percussion_hit(sample_rate, kind=hit_kind)
    chest_hit = butter_filter(chest_hit, 460.0, sample_rate, btype="low", order=2)
    bed = np.zeros(num_samples, dtype=np.float64)
    for idx, hit_pos in enumerate(hit_positions):
        vel = 0.88 if (idx % 2 == 0) else 0.72
        _add_hit_at(bed, chest_hit, hit_pos, gain=vel)
        if mode in ("shoor", "fazzaiya") and idx % 2 == 1:
            _add_hit_at(bed, chest_hit, hit_pos + int(0.26 * step_samples), gain=0.45)
    return bed, len(hit_positions)


def synthesize_ahaat_drone(num_samples, sample_rate, maqam="saba", tonic_hz=None):
    """Module 44, 69 & 71: Synthesize 24-EDO human pharyngeal Ahaat pad locked to singer tonic f0."""
    if num_samples <= 0:
        return np.zeros(0, dtype=np.float64)
    freqs = list(MAQAM_FREQS.get(maqam.lower(), MAQAM_FREQS["saba"]))
    if tonic_hz is not None and float(tonic_hz) > 40.0:
        scale_ratio = float(tonic_hz) / float(freqs[0])
        freqs = [f * scale_ratio for f in freqs]
    root_tonic_hz = freqs[0]
    modal_2nd_hz = freqs[1]
    fourth_hz = freqs[2]
    detune_cents = (-4.0, 0.0, 4.0)
    t_vec = np.arange(num_samples, dtype=np.float64) / float(sample_rate)
    modal_sway = 0.5 * (1.0 - np.cos(2.0 * np.pi * 0.11 * t_vec))

    ensemble = np.zeros(num_samples, dtype=np.float64)
    for cents in detune_cents:
        ratio = 2.0 ** (cents / 1200.0)
        v_tonic = _generate_rosenberg_glottal_source(num_samples, sample_rate, root_tonic_hz * ratio)
        v_second = _generate_rosenberg_glottal_source(num_samples, sample_rate, modal_2nd_hz * ratio)
        v_fourth = _generate_rosenberg_glottal_source(num_samples, sample_rate, fourth_hz * ratio)
        ensemble += 0.62 * v_tonic + 0.24 * (1.0 - 0.35 * modal_sway) * v_fourth + 0.14 * modal_sway * v_second

    shaped = _apply_ahaat_formant_resonators(ensemble / float(len(detune_cents)), sample_rate)
    breath_lfo = 0.78 + 0.22 * np.sin(2.0 * np.pi * 0.22 * t_vec)
    peak = float(np.max(np.abs(shaped)) + 1e-9)
    return 0.18 * (shaped / peak) * breath_lfo


def synthesize_vocal_synth_strings_pad(num_samples, sample_rate, maqam="saba", tonic_hz=None):
    """Module 44 & 71 (Axis 3/4): Synthesize warm low cello/human vocal-synth pad locked to singer tonic f0."""
    base = synthesize_ahaat_drone(num_samples, sample_rate, maqam=maqam, tonic_hz=tonic_hz)
    freqs = list(MAQAM_FREQS.get(maqam.lower(), MAQAM_FREQS["saba"]))
    if tonic_hz is not None and float(tonic_hz) > 40.0:
        scale_ratio = float(tonic_hz) / float(freqs[0])
        freqs = [f * scale_ratio for f in freqs]
    upper = _generate_rosenberg_glottal_source(num_samples, sample_rate, freqs[3])
    upper_shaped = _apply_ahaat_formant_resonators(upper, sample_rate)
    peak = float(np.max(np.abs(upper_shaped)) + 1e-9)
    return base + 0.06 * (upper_shaped / peak)


def synthesize_contextual_foley(num_samples, sample_rate, foley_type="none"):
    """Module 71 (Axis 4): Synthesize subtle Karbala atmospheric Foley (wind, water, horses, swords, fire, battlefield)."""
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

    if foley_type == "swords":
        bed = np.zeros(num_samples, dtype=np.float64)
        step = max(1, int(1.85 * sample_rate))
        clash_len = max(8, int(0.22 * sample_rate))
        t_c = np.arange(clash_len, dtype=np.float64) / float(sample_rate)
        ring = (
            0.55 * np.sin(2.0 * np.pi * 1940.0 * t_c)
            + 0.30 * np.sin(2.0 * np.pi * 2870.0 * t_c)
            + 0.15 * butter_filter(rng.normal(0.0, 1.0, clash_len), [1400.0, 5200.0], sample_rate, btype="band", order=2)
        ) * np.exp(-16.0 * t_c)
        pos = min(int(0.10 * sample_rate), max(0, num_samples // 4))
        while pos < num_samples:
            _add_hit_at(bed, ring, pos, gain=0.035)
            pos += step
        return bed

    if foley_type == "fire":
        rumble = butter_filter(noise, [120.0, 580.0], sample_rate, btype="band", order=2)
        crackle_src = np.where(np.abs(noise) > 2.35, noise, 0.0)
        crackle = butter_filter(crackle_src, [1800.0, 5800.0], sample_rate, btype="band", order=2)
        flicker = 0.65 + 0.35 * np.sin(2.0 * np.pi * 0.45 * t_vec)
        return 0.035 * rumble * flicker + 0.025 * crackle

    if foley_type == "battlefield":
        wind_layer = synthesize_contextual_foley(num_samples, sample_rate, foley_type="wind")
        fire_layer = synthesize_contextual_foley(num_samples, sample_rate, foley_type="fire")
        swords_layer = synthesize_contextual_foley(num_samples, sample_rate, foley_type="swords")
        return 0.55 * wind_layer + 0.45 * fire_layer + 0.40 * swords_layer

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


def _k_weight_signal(chan, sample_rate):
    """Apply ITU-R BS.1770-4 Stage-1 (+4dB High Shelf) and Stage-2 (38.1Hz RLB HPF)."""
    fs = float(max(8000, sample_rate))
    # Stage 1: +3.99984385 dB high shelf around 1681.97 Hz
    db_gain = 3.999843853973347
    vh = 10.0 ** (db_gain / 20.0)
    vb = vh**0.4996667741545416
    k0 = np.tan(np.pi * min(1681.974450955533, 0.44 * fs) / fs)
    q_hs = 0.7071752369554196
    a0_hs = 1.0 + k0 / q_hs + k0 * k0
    b_hs = np.array(
        [(vh + vb * k0 / q_hs + k0 * k0) / a0_hs, 2.0 * (k0 * k0 - vh) / a0_hs, (vh - vb * k0 / q_hs + k0 * k0) / a0_hs]
    )
    a_hs = np.array([1.0, 2.0 * (k0 * k0 - 1.0) / a0_hs, (1.0 - k0 / q_hs + k0 * k0) / a0_hs])
    stage1 = lfilter(b_hs, a_hs, chan)

    # Stage 2: RLB 38.135 Hz high-pass biquad
    k1 = np.tan(np.pi * 38.13547087602444 / fs)
    q_hp = 0.5003270373238773
    a0_hp = 1.0 + k1 / q_hp + k1 * k1
    b_hp = np.array([1.0 / a0_hp, -2.0 / a0_hp, 1.0 / a0_hp])
    a_hp = np.array([1.0, 2.0 * (k1 * k1 - 1.0) / a0_hp, (1.0 - k1 / q_hp + k1 * k1) / a0_hp])
    return lfilter(b_hp, a_hp, stage1)


def measure_ebu_r128_loudness(stereo, sample_rate):
    """Measure ITU-R BS.1770-4 / EBU R128 Gated Integrated Loudness (LUFS), LRA & 4x True Peak."""
    arr = np.asarray(stereo, dtype=np.float64)
    if arr.ndim == 1:
        arr = np.column_stack((arr, arr))
    if arr.shape[0] == 0:
        return {"integrated_lufs": -70.0, "lra_lu": 0.0, "true_peak_dbtp": -120.0}

    kw_l = _k_weight_signal(arr[:, 0], sample_rate)
    kw_r = _k_weight_signal(arr[:, 1], sample_rate)
    power_sum = kw_l**2 + kw_r**2

    block_len = max(1, int(0.400 * sample_rate))
    hop_len = max(1, int(0.100 * sample_rate))
    if len(power_sum) <= block_len:
        mean_pow = float(np.mean(power_sum) + 1e-12)
        lufs = -0.691 + 10.0 * np.log10(mean_pow)
        lra = 0.0
    else:
        csum = np.concatenate(([0.0], np.cumsum(power_sum)))
        starts = np.arange(0, len(power_sum) - block_len + 1, hop_len)
        block_pow = np.maximum((csum[starts + block_len] - csum[starts]) / float(block_len), 1e-12)
        block_lufs = -0.691 + 10.0 * np.log10(block_pow)

        abs_mask = block_lufs > -70.0
        if not np.any(abs_mask):
            lufs = float(np.mean(block_lufs))
        else:
            ungated_pow = float(np.mean(block_pow[abs_mask]))
            rel_thresh = -0.691 + 10.0 * np.log10(ungated_pow) - 10.0
            rel_mask = abs_mask & (block_lufs > rel_thresh)
            gated_pow = float(np.mean(block_pow[rel_mask])) if np.any(rel_mask) else ungated_pow
            lufs = -0.691 + 10.0 * np.log10(max(gated_pow, 1e-12))

        st_mask = block_lufs > -70.0
        if np.sum(st_mask) >= 4:
            vals = block_lufs[st_mask]
            lra = float(max(0.0, np.percentile(vals, 95) - np.percentile(vals, 10)))
        else:
            lra = 0.0

    n_frames = arr.shape[0]
    if n_frames >= 4:
        # Fast vectorized peak check without blowing RAM on very long streams (chunked 4x interpolation)
        peak_val = float(np.max(np.abs(arr)))
        chunk_sz = max(4096, int(sample_rate * 10))
        for start in range(0, n_frames, chunk_sz):
            seg = arr[start : min(n_frames, start + chunk_sz)]
            if seg.shape[0] < 4:
                continue
            xb = np.arange(seg.shape[0], dtype=np.float64)
            xo = np.linspace(0.0, float(seg.shape[0] - 1), seg.shape[0] * 4)
            peak_val = max(
                peak_val,
                float(np.max(np.abs(np.interp(xo, xb, seg[:, 0])))),
                float(np.max(np.abs(np.interp(xo, xb, seg[:, 1])))),
            )
    else:
        peak_val = float(np.max(np.abs(arr)))
    dbtp = float(20.0 * np.log10(max(peak_val, 1e-9)))
    return {
        "integrated_lufs": round(lufs, 2),
        "lra_lu": round(lra, 2),
        "true_peak_dbtp": round(dbtp, 2),
    }


def _apply_lookahead_true_peak_limiter(stereo, sample_rate, ceiling_lin):
    """Smooth lookahead soft-knee True-Peak brickwall limiter preventing hard sample clipping."""
    if stereo.shape[0] == 0:
        return stereo
    mag = np.max(np.abs(stereo), axis=1)
    needed_gain = np.where(mag > ceiling_lin, ceiling_lin / np.maximum(mag, 1e-9), 1.0)
    win = min(len(needed_gain), max(1, int(0.012 * sample_rate)))
    # Local minimum gain envelope via O(N) rolling window on deficit
    deficit = 1.0 - needed_gain
    smooth_def = (
        _fast_boxcar_mean(deficit, win) * (float(win) / float(max(1, win // 2)))
    )[: len(deficit)]
    env_gain = np.clip(1.0 - smooth_def, 0.05, 1.0)
    env_gain = np.minimum(env_gain, needed_gain)
    limited = stereo * env_gain[:, np.newaxis]

    # Exact 4x oversampled ceiling verification chunk-by-chunk
    n_frames = limited.shape[0]
    chunk_sz = max(4096, int(sample_rate * 10))
    peak_4x = float(np.max(np.abs(limited)))
    if n_frames >= 4:
        for start in range(0, n_frames, chunk_sz):
            seg = limited[start : min(n_frames, start + chunk_sz)]
            if seg.shape[0] < 4:
                continue
            xb = np.arange(seg.shape[0], dtype=np.float64)
            xo = np.linspace(0.0, float(seg.shape[0] - 1), seg.shape[0] * 4)
            peak_4x = max(
                peak_4x,
                float(np.max(np.abs(np.interp(xo, xb, seg[:, 0])))),
                float(np.max(np.abs(np.interp(xo, xb, seg[:, 1])))),
            )
    if peak_4x > ceiling_lin and peak_4x > 0.0:
        limited *= (ceiling_lin * 0.996) / peak_4x
    return np.clip(limited, -ceiling_lin, ceiling_lin)


def normalize_lufs_and_true_peak(stereo, sample_rate, target_lufs=-14.0, ceiling_dbtp=-1.0):
    """Normalize stereo mix to exact ITU-R BS.1770-4 -14.0 LUFS & -1.0 dBTP True-Peak ceiling."""
    if stereo.size == 0:
        return stereo
    ceiling = 10.0 ** (ceiling_dbtp / 20.0)
    scaled = stereo.copy()
    for _ in range(2):
        stats = measure_ebu_r128_loudness(scaled, sample_rate)
        gain_db = float(np.clip(target_lufs - stats["integrated_lufs"], -18.0, 24.0))
        scaled = scaled * (10.0 ** (gain_db / 20.0))
        scaled = _apply_lookahead_true_peak_limiter(scaled, sample_rate, ceiling)
        if abs(target_lufs - measure_ebu_r128_loudness(scaled, sample_rate)["integrated_lufs"]) <= 0.25:
            break
    return scaled


def audit_rendered_audio(wav_path):
    """Audit rendered WAV for EBU R128 broadcast compliance, low-vocal Ahaat pads & tail cutoff."""
    sample_rate, stereo, channels, bit_depth = read_wav_any_depth(wav_path, return_stereo=True)
    mono = np.mean(stereo, axis=1) if stereo.shape[0] > 0 else np.zeros(0, dtype=np.float64)
    stats = measure_ebu_r128_loudness(stereo if channels > 1 else mono, sample_rate)
    duration_sec = round(len(mono) / max(1.0, float(sample_rate)), 3)

    hop = max(1, int(0.5 * sample_rate))
    n_hops = len(mono) // hop
    low_streak = 0.0
    max_low_pad = 0.0
    for i in range(n_hops):
        seg = mono[i * hop : (i + 1) * hop]
        rms_db = 20.0 * np.log10(float(np.sqrt(np.mean(seg**2)) + 1e-9))
        if rms_db < -28.0:
            low_streak += 0.5
            max_low_pad = max(max_low_pad, low_streak)
        else:
            low_streak = 0.0

    tail_samples = max(1, int(0.15 * sample_rate))
    tail_rms_db = 20.0 * np.log10(float(np.sqrt(np.mean(mono[-tail_samples:] ** 2)) + 1e-9)) if len(mono) else -90.0
    abrupt_tail_cutoff = bool(tail_rms_db > -24.0)
    broadcast_ok = bool(stats["true_peak_dbtp"] <= -0.9 and -15.5 <= stats["integrated_lufs"] <= -12.5)
    return {
        "wav_path": wav_path,
        "sample_rate": sample_rate,
        "channels": channels,
        "bit_depth": bit_depth,
        "duration_sec": duration_sec,
        "integrated_lufs": stats["integrated_lufs"],
        "lra_lu": stats["lra_lu"],
        "true_peak_dbtp": stats["true_peak_dbtp"],
        "max_low_energy_gap_sec": round(max_low_pad, 2),
        "tail_last_150ms_dbfs": round(tail_rms_db, 2),
        "abrupt_tail_cutoff_risk": abrupt_tail_cutoff,
        "broadcast_compliant": broadcast_ok,
    }


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
    trim_end_sec=None,
    fade_out_sec=0.0,
    no_synth_rhythm=False,
):
    """Run complete 5-Track SOS/RMS/LUFS or Pure Vocal Husseiniya DSP montage."""
    if mode not in SUPPORTED_DSP_MODES:
        raise ValueError(f"Unsupported DSP mode: {mode}")

    sample_rate, mono, _, _ = read_wav_any_depth(input_path)
    if trim_end_sec is not None and float(trim_end_sec) > 0.2:
        max_samples = min(len(mono), int(float(trim_end_sec) * sample_rate))
        mono = mono[:max_samples]

    pure_mode = mode == "vocal_pure_master" or bool(no_synth_rhythm)
    vocal_in = (
        strip_ai_percussion_from_vocal(mono, sample_rate)
        if (replace_ai_percussion and not pure_mode)
        else mono
    )
    restored = apply_noise_print_restoration(vocal_in, sample_rate)
    eq_vocal = apply_vocal_eq(restored, sample_rate, preserve_chest_thud=pure_mode)
    deessed_vocal = apply_arabic_deesser(eq_vocal, sample_rate)
    leveled_vocal = apply_optical_vocal_compressor(deessed_vocal, sample_rate)

    delay_ms = compute_tempo_synced_delay_ms(bpm, mode=mode)
    if pure_mode:
        echo_l = apply_dynacord_echo(leveled_vocal, sample_rate, delay_ms=delay_ms, feedback=0.20, wet=0.10)
        echo_r = apply_dynacord_echo(leveled_vocal, sample_rate, delay_ms=delay_ms * 1.07, feedback=0.18, wet=0.10)
        wet_l = apply_husseiniya_reverb(echo_l, sample_rate, rt60_sec=2.2, pre_delay_ms=19.0, wet=0.15, seed=4850)
        wet_r = apply_husseiniya_reverb(echo_r, sample_rate, rt60_sec=2.2, pre_delay_ms=27.0, wet=0.15, seed=4899)
        foley_bed = synthesize_contextual_foley(len(mono), sample_rate, foley_type=foley)
        left_chan = wet_l + 0.5 * foley_bed
        right_chan = wet_r + 0.5 * foley_bed
        stereo_sat = np.column_stack((tape_saturate(left_chan, drive=1.10), tape_saturate(right_chan, drive=1.10)))
        stereo_glued = apply_master_glue_compressor(stereo_sat, ratio=1.35, threshold=0.68)
    else:
        echo_l = apply_dynacord_echo(leveled_vocal, sample_rate, delay_ms=delay_ms)
        echo_r = apply_dynacord_echo(leveled_vocal, sample_rate, delay_ms=delay_ms * 1.07)
        rt60 = 3.4 if mode in ("mawal", "nai", "thaqeel_muwazza", "bahrani_muthakkal") else 2.4
        wet_l = apply_husseiniya_reverb(echo_l, sample_rate, rt60_sec=rt60, pre_delay_ms=18.0, wet=0.22, seed=4850)
        wet_r = apply_husseiniya_reverb(echo_r, sample_rate, rt60_sec=rt60, pre_delay_ms=27.0, wet=0.22, seed=4899)

        onset_offset = detect_vocal_onset_offset_samples(leveled_vocal, sample_rate)
        singer_tonic_hz = estimate_singer_tonic_root_hz(leveled_vocal, sample_rate)
        if mode in ("modern_studio_ney_strings", "cinematic_foley_latmiya"):
            rhythm_bed, _ = build_vocal_pulse_locked_chest_latm(
                leveled_vocal, sample_rate, mode="thaqeel_muwazza", target_bpm=bpm
            )
        else:
            rhythm_bed = build_rhythm_bed(
                len(mono),
                sample_rate,
                mode=mode,
                bpm=bpm,
                offset_samples=onset_offset,
                swing=swing,
                samples_dir=samples_dir,
                vocal_signal=leveled_vocal,
            )
        ahaat_pad = (
            synthesize_vocal_synth_strings_pad(
                len(mono), sample_rate, maqam=maqam_drone, tonic_hz=singer_tonic_hz
            )
            if mode in ("studio_arranged", "heavy_clip", "modern_studio_ney_strings", "cinematic_foley_latmiya")
            else synthesize_ahaat_drone(len(mono), sample_rate, maqam=maqam_drone, tonic_hz=singer_tonic_hz)
        )
        effective_foley = "battlefield" if (mode == "cinematic_foley_latmiya" and foley == "none") else foley
        foley_bed = synthesize_contextual_foley(len(mono), sample_rate, foley_type=effective_foley)

        if audio_drop_sec is not None:
            rhythm_bed = apply_dramatic_audio_drop(rhythm_bed, sample_rate, drop_start_sec=audio_drop_sec)
            ahaat_pad = apply_dramatic_audio_drop(ahaat_pad, sample_rate, drop_start_sec=audio_drop_sec)

        ducking = compute_smart_sidechain_ducking(leveled_vocal, sample_rate, duck_db=-3.0, threshold_dbfs=-28.0)

        haas_shift = max(1, int(0.009 * sample_rate))
        ahaat_right = np.roll(ahaat_pad, haas_shift)
        ahaat_right[:haas_shift] = ahaat_pad[:haas_shift]

        left_chan = wet_l + 0.78 * (rhythm_bed * ducking) + 0.65 * (ahaat_pad * ducking) + foley_bed
        right_chan = wet_r + 0.78 * (rhythm_bed * ducking) + 0.65 * (ahaat_right * ducking) + foley_bed

        stereo_sat = np.column_stack((tape_saturate(left_chan), tape_saturate(right_chan)))
        stereo_glued = apply_master_glue_compressor(stereo_sat)

    if fade_out_sec and float(fade_out_sec) > 0.0 and stereo_glued.shape[0] > 8:
        fade_len = min(stereo_glued.shape[0] // 2, int(float(fade_out_sec) * sample_rate))
        if fade_len > 2:
            curve = 0.5 * (1.0 + np.cos(np.pi * np.linspace(0.0, 1.0, fade_len)))
            stereo_glued = stereo_glued.copy()
            stereo_glued[-fade_len:] *= curve[:, np.newaxis]

    master = normalize_lufs_and_true_peak(
        stereo_glued, sample_rate, target_lufs=-14.0, ceiling_dbtp=-1.0
    )

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    _write_wav_pcm16(output_path, sample_rate, master)
    out_stats = measure_ebu_r128_loudness(master, sample_rate)
    return {
        "output_path": output_path,
        "sample_rate": sample_rate,
        "mode": mode,
        "pure_vocal_master": pure_mode,
        "bpm": bpm,
        "maqam_drone": maqam_drone,
        "replace_ai_percussion": bool(replace_ai_percussion and not pure_mode),
        "integrated_lufs": out_stats["integrated_lufs"],
        "true_peak_dbtp": out_stats["true_peak_dbtp"],
        "lra_lu": out_stats["lra_lu"],
    }


def parse_args(argv=None):
    """Parse CLI flags for V52.0 Phonetics, History Firewall, Stage Planner & 18-Mode DSP."""
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
        help="Husseiniya rhythm & production mode (20 modes incl. modern_studio_ney_strings & cinematic_foley_latmiya)",
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
        choices=["none", "wind", "water", "horses", "swords", "fire", "battlefield"],
        help="Contextual atmospheric Foley (Axis 4: wind, water, horses, swords, fire, battlefield)",
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
        help="Strip residual AI percussion (<105Hz thumps & click spikes) before adding organic Latm",
    )
    parser.add_argument("--no-synth-rhythm", action="store_true", help="Disable synthetic rhythm & Ahaat beds")
    parser.add_argument("--trim-end-sec", type=float, default=None, help="Trim input audio cleanly at timestamp (sec)")
    parser.add_argument("--fade-out-sec", type=float, default=0.0, help="Apply raised-cosine fade-out duration (sec)")
    parser.add_argument("--samples-dir", default=None, help="Optional directory of real WAV one-shots")
    parser.add_argument("--compile-lyrics", default=None, help="Shape & vocalize Arabic poem text")
    parser.add_argument(
        "--compile-clean-lyria",
        default=None,
        help="V57.0 NC26/NC27: Compile clean natural Arabic + surgical vowels & چ->تش digraph for Lyria 3.5",
    )
    parser.add_argument("--lint-poem", default=None, help="Run QC1-QC35 linter on poem text")
    parser.add_argument("--verify-history", default=None, help="Verify poem against Ahl al-Bayt historical narratives")
    parser.add_argument("--plan-stages", default=None, help="Partition full poem into V52 NC16 3-line Extend stages")
    parser.add_argument(
        "--enforce-estehlal",
        default=None,
        help="Wrap [المستهل] lines in '(...)' for 100%% unison Raddada choir delivery",
    )
    parser.add_argument(
        "--build-stage-json",
        default=None,
        help="Build Module 53 Per-Stage & Per-Section JSON orchestration payload (QC19)",
    )
    parser.add_argument("--validate-abudhiyah", default=None, help="Validate 4-line Abudhiyah Jinas")
    parser.add_argument("--validate-zuhayri", default=None, help="Validate 7-line Zuhayri Mawal")
    parser.add_argument("--recommend-tor", default=None, help="Recommend Tor, BPM & Sound prompt")
    parser.add_argument(
        "--stage-plan",
        default=None,
        choices=["iraqi", "bahrani", "iraqi_bahrani"],
        help="Output 4-Stage Common Jins Maqam & Atwar progression JSON",
    )
    parser.add_argument(
        "--export-constitution",
        action="store_true",
        help="Print canonical OMNI-ARCHITECT JSON constitution",
    )
    parser.add_argument(
        "--genre",
        default=None,
        choices=["latmiya", "nasheed", "ibtihalat", "tawashih"],
        help="Generate genre acoustic profile & Sound prompt",
    )
    parser.add_argument("--extract-profile", default=None, help="Reverse-engineer reference WAV profile")
    parser.add_argument("--audit-audio", default=None, help="Audit WAV loudness, True Peak, gaps & tail cutoff")
    return parser.parse_args(argv)


def main(argv=None):
    """CLI entrypoint for Hussaini Production Studio V52.0 OMNI-ARCHITECT."""
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

    if args.compile_clean_lyria is not None:
        report = format_clean_lyrics_for_lyria35(args.compile_clean_lyria)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.lint_poem is not None:
        print(json.dumps(lint_poem(args.lint_poem.replace("\\n", "\n")), ensure_ascii=False, indent=2))
        return 0

    if args.verify_history is not None:
        print(json.dumps(verify_historical_narratives(args.verify_history.replace("\\n", "\n")), ensure_ascii=False, indent=2))
        return 0

    if args.plan_stages is not None:
        print(json.dumps(plan_poem_extend_stages(args.plan_stages.replace("\\n", "\n"), bpm=args.bpm), ensure_ascii=False, indent=2))
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

    if args.audit_audio is not None:
        print(json.dumps(audit_rendered_audio(args.audit_audio), ensure_ascii=False, indent=2))
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
            trim_end_sec=args.trim_end_sec,
            fade_out_sec=args.fade_out_sec,
            no_synth_rhythm=args.no_synth_rhythm,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(json.dumps(build_flowmusic_json_preconditioning(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
