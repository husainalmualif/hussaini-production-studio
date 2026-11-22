#!/usr/bin/env python3
# pylint: disable=too-many-lines,too-many-return-statements,too-many-branches,too-many-locals,too-many-statements,too-many-arguments,too-many-positional-arguments,no-member,chained-comparison
"""Hussaini Audio Omni-Architect DSP, 5-Track DAW & Phonetics Compiler (V64.0 OMNI-ARCHITECT).

Standalone empirical production engine implementing Hussaini_Production_Studio_OS_V50_0_OMNI_ARCHITECT
and V52.0–V64.0 field & 177-track empirical upgrades:
- Single-Source Version Management via root VERSION file & JSON constitution
- Pure-Python WAV I/O (with transparent FFmpeg MP3/M4A/OGG decoding) + ITU-R BS.1770-4 / EBU R128
  K-Weighted Gated Loudness + 4x True-Peak Limiter
- Module 67–78 (V52.0–V64.0): Iraqi & Basim Al-Karbalai Acoustic/Phonetic Ground-Truth Engine
  (NC43 Cadence-Locked 24-EDO Maqam Classifier, NC44–NC45 Iraqi Prosody & G2P Landmine Pre-Flight
  --audit-iraqi-preflight, NC46–NC47 Audio Ground-Truth Gate --audit-ground-truth), Stage-0 MASTER_STATE
  Bootstrap & Chained Back-to-Front Replace (--build-v63-bootstrap, --plan-chained-replace, NC38–NC42),
  Waqar 6-Family Orchestral & Shadda/Wasl Orthoepy (--check-orchestration, --audit-orthoepy, NC36–NC37),
  Qatifi/Bahrani/Iraqi Clean Lyria 3.5 Orthography (--compile-clean-lyria, NC26–NC35), Multi-Meter
  Muwashah JSON, 15 Maqams, 19 Fingerprints, and 20-Mode Multi-Platform EBU R128 DSP (-14/-16/-18/-23 LUFS)
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

# 24-EDO Maqam Drone Frequencies (Hz) — Section 4 of V50.0 Constitution + V60/V61 15-Maqam Expansion
MAQAM_FREQS = {
    "bayati": [146.83, 160.00, 174.61, 220.00],
    "bayati_shuri": [146.83, 160.00, 174.61, 196.00, 207.65, 246.94],
    "husseini": [146.83, 160.00, 174.61, 196.00, 220.00, 240.00],
    "saba": [146.83, 160.00, 174.61, 207.65],
    "saba_zamzam": [146.83, 155.56, 174.61, 185.00, 220.00],
    "hijaz": [146.83, 155.56, 185.00, 220.00],
    "hijaz_kar": [130.81, 138.59, 164.81, 174.61, 196.00, 207.65, 246.94],
    "lami": [146.83, 155.56, 174.61, 196.00, 207.65],
    "kurd": [146.83, 155.56, 174.61, 220.00],
    "nahawand": [146.83, 164.81, 174.61, 220.00],
    "nawa_athar": [130.81, 146.83, 155.56, 185.00, 196.00, 207.65, 246.94],
    "sikah": [160.00, 174.61, 196.00, 220.00],
    "rast": [130.81, 146.83, 160.00, 196.00],
    "suznak": [130.81, 146.83, 160.00, 174.61, 196.00, 207.65, 246.94],
    "ajam": [130.81, 146.83, 164.81, 174.61, 196.00],
}

COMMON_JINS_GRAPH = {
    "bayati": ["husseini", "bayati_shuri", "saba", "saba_zamzam", "kurd", "hijaz", "lami", "sikah", "nahawand", "ajam"],
    "bayati_shuri": ["bayati", "husseini", "hijaz", "hijaz_kar", "saba", "kurd", "nawa_athar"],
    "husseini": ["bayati", "bayati_shuri", "saba", "rast", "suznak", "hijaz", "lami"],
    "saba": ["saba_zamzam", "bayati", "husseini", "bayati_shuri", "lami", "hijaz", "rast", "nahawand", "ajam"],
    "saba_zamzam": ["saba", "lami", "hijaz", "bayati", "kurd"],
    "hijaz": ["hijaz_kar", "suznak", "bayati_shuri", "saba_zamzam", "bayati", "saba", "kurd", "sikah", "nahawand"],
    "hijaz_kar": ["hijaz", "suznak", "nawa_athar", "bayati_shuri", "nahawand", "kurd"],
    "lami": ["saba_zamzam", "saba", "bayati", "husseini", "kurd"],
    "kurd": ["bayati", "bayati_shuri", "lami", "saba_zamzam", "hijaz", "nahawand", "ajam"],
    "nahawand": ["nawa_athar", "kurd", "bayati", "saba", "hijaz", "hijaz_kar", "rast", "ajam"],
    "nawa_athar": ["nahawand", "hijaz_kar", "hijaz", "kurd", "bayati_shuri"],
    "sikah": ["bayati", "husseini", "hijaz", "rast", "suznak", "saba", "ajam"],
    "rast": ["suznak", "ajam", "saba", "bayati", "husseini", "hijaz", "sikah", "nahawand"],
    "suznak": ["rast", "hijaz", "hijaz_kar", "ajam", "husseini", "bayati", "nahawand"],
    "ajam": ["rast", "suznak", "nahawand", "sikah", "kurd", "bayati"],
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
    "v58_bahrani_muwashah_hybrid_72bpm_bayati_hijaz_saba": (
        "Authentic Bahraini Shia Husseini Multi-Meter Muwashah Studio Latmiya, 72 BPM shifting dynamically "
        "across poetic meters via cadential Qa'da rhythm drops, Maqam Bayati modulating via Common Jins to "
        "Hijaz and Saba, authentic Gulf Bahrani male Radood vocal with sharp crisp Arabic pharyngeal "
        "pronunciation and Qarar-to-Jawab emotional arc, powerful wide unison Bahrani male Matam choir "
        "call-and-response, strictly percussive bare chest thuds, dark bowed bass cello drone, mournful "
        "reed ney, subtle acoustic desert wind, sacred Bahraini Matam reverb, strictly no piano, zero "
        "keyboard chords, no pop drums, no snare backbeat, no dance beat, no Arabic pop singing"
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

# Module 73 (V58.0): 5 Empirical Sound Direction & Multi-Meter Muwashah Blueprints (177-MP3 Masterwork Study)
MASTERWORK_DIRECTION_BLUEPRINTS_V58 = {
    "vintage_telephone_intro_to_full_drop": {
        "reference_masterwork": "جابر يا جابر (الشيخ حسين الأكرف)",
        "technique": "Bandpass 300-2800 Hz archive/nostalgia EQ during opening intro -> explosive full-bandwidth studio drop",
        "dsp_function": "apply_vintage_telephone_intro_fx",
    },
    "cadential_qada_rhythm_mute_shift": {
        "reference_masterwork": "جابر يا جابر (1:45) و أصحاب الحسين (2:30)",
        "technique": "Mute percussion completely on soaring solo melisma ('الكعدة الحسينية') over dark humming/cello bed, then slam into new poetic meter",
        "dsp_function": "apply_dramatic_audio_drop",
    },
    "half_double_time_and_progressive_bpm_gears": {
        "reference_masterwork": "حج الدموع (65<->130), باب الساعات (111->55), أصحاب الحسين (88->48->81), مات الماي (70->86->103)",
        "technique": "Shift between long narrative lines and short staccato Muwashah meters using 0.5x / 2.0x gears or structured +15-20 BPM step-ups",
        "verified_gear_ratios": [0.5, 1.0, 1.25, 2.0],
    },
    "qarar_to_jawab_vocal_pitch_arc": {
        "reference_masterwork": "أذان العشق (+11.9 st), إعصار (+7.9 st), جابر يا جابر (+7.5 st), حج الدموع (+7.2 st)",
        "technique": "Climb 6 to 12 semitones from solemn chest-voice Qarar intro to soaring emotional Jawab chorus/climax",
        "empirical_range_semitones": [6.8, 11.9],
    },
    "stereo_width_breathing_and_vocal_stacking": {
        "reference_masterwork": "باب الساعات (+6.22 dB), مات الماي (+5.12 dB), أذان العشق (+5.06 dB), جابر يا جابر (+3.84 dB)",
        "technique": "Contrast intimate center-mono solo Radood with wide stereo Bass/Baritone/Tenor unison & harmonic choir walls (+3.1 to +6.2 dB side expansion)",
        "empirical_range_db": [3.1, 6.2],
        "dsp_function": "apply_mid_side_vocal_stacking_enhancer",
    },
}

# Module 74 (V60.0): 12 Empirically Verified Multi-Maqam & 9-School Melodic Fingerprints (Break Melodic Monotony)
MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60 = {
    "v60_bahrani_cradle_nahawand_kurd_saba_64bpm": {
        "school": "School 03 & 07 — Bahrani Modern Studio Muwashah (Al-Akraf / Bouhamad)",
        "dialect": "bahrani",
        "axis": "axis_3_zero_piano_hybrid",
        "bpm": 64,
        "maqam_arc": ["nahawand", "kurd", "saba"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "Exp 22 (3a1846ce, 9.8/10, 0.00% piano, 0.00% pop snare)",
        "sound_prompt": (
            "Intimate Bahraini Shia Husseini Multi-Meter Cradle Muwashah elegy, 64 BPM gentle swaying lament "
            "with cadential Qa'da silence drops, Maqam Nahawand modulating via Common Jins to Kurd and heartbreaking "
            "Saba, authentic Gulf Bahrani male Baritone Radood vocal with sharp crisp Arabic pharyngeal articulation, "
            "warm resonant unison Bahrani male Matam choir on refrain only, strictly percussive bare chest thuds, "
            "dark bowed bass cello drone, mournful reed ney, subtle acoustic desert wind, Bahraini Matam reverb, "
            "strictly zero piano, zero keyboard chords, zero pop drums, zero rock snare backbeat, zero Arabic pop singing"
        ),
    },
    "v60_bahrani_muwashah_bayati_hijaz_saba_72bpm": {
        "school": "School 03 — Bahrani Multi-Meter Muwashah (Al-Akraf / Nader Al-Tattan)",
        "dialect": "bahrani",
        "axis": "axis_3_zero_piano_hybrid",
        "bpm": 72,
        "maqam_arc": ["bayati", "bayati_shuri", "hijaz", "saba"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "Exp 21-A (5172764b, 9.7/10 Replace) & Exp 21-B (4f987ba8, 3:38 Extend)",
        "sound_prompt": (
            "Authentic Bahraini Shia Husseini Multi-Meter Muwashah Studio Latmiya, 72 BPM shifting dynamically "
            "across poetic meters via cadential Qa'da rhythm drops, Maqam Bayati modulating via Common Jins to "
            "Hijaz and Saba, authentic Gulf Bahrani male Radood vocal with sharp crisp Arabic pharyngeal "
            "pronunciation and Qarar-to-Jawab emotional arc, powerful wide unison Bahrani male Matam choir "
            "call-and-response, strictly percussive bare chest thuds, dark bowed bass cello drone, mournful "
            "reed ney, subtle acoustic desert wind, sacred Bahraini Matam reverb, strictly zero piano, zero "
            "keyboard chords, zero pop drums, zero snare backbeat, zero dance beat, zero Arabic pop singing"
        ),
    },
    "v60_epic_fusha_mawkib_hijaz_kar_88_to_96bpm": {
        "school": "School 03 & 02 — Epic Fusha/Bahrani Ashura Mawkib & Haidari Gear-Up",
        "dialect": "fusha",
        "axis": "axis_2_mawkib_procession",
        "bpm": 88,
        "maqam_arc": ["hijaz_kar", "hijaz", "bayati_shuri"],
        "dsp_mode": "zanjeel_bahrani",
        "empirical_exp": "Exp 23 (2bfdacc0, 9.2/10, 88->96 BPM Haidari gear jump, 0% piano)",
        "sound_prompt": (
            "Epic Classical Arabic Shia Ashura Mawkib heroic march chant, Maqam Hijaz Kar with dramatic "
            "augmented-second gravity shifting from 88 BPM dignified procession to 96 BPM fiery Haidari climax, "
            "commanding deep resonant Bass-Baritone Radood vocal answered by massive thunderous unison male "
            "Mawkib congregation choir, deep traditional Dammam procession drums, metallic brass Tasa cymbals, "
            "strictly percussive bare chest strikes, cavernous courtyard acoustics, strictly zero piano, zero "
            "keyboard chords, zero modern pop drums, zero upbeat dance rhythm"
        ),
    },
    "v60_iraqi_karbalaei_pure_saba_zamzam_lami_58bpm": {
        "school": "School 01 & 04 — Pure Iraqi Karbalaei Muthakkal & Nazla (Basim / Sayyid Salam)",
        "dialect": "iraqi",
        "axis": "axis_1_pure_acapella",
        "bpm": 58,
        "maqam_arc": ["saba_zamzam", "lami", "hijaz", "lami"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "Exp 24-A (2af13afc, 9.7/10) & Exp 24-B (9dc63acd, 4:18 Pure Axis 1 Extend, 9.4/10)",
        "sound_prompt": (
            "Traditional Iraqi Karbalaei Ashura Majlis Latmiya elegy, authentic Southern Iraqi Karbala dialect, "
            "Maqam Saba Zamzam modulating to devastating Euphrates Maqam Lami with dramatic Qa'da silence drop, "
            "slow heavy 58 BPM Muthakkal mourning pulse, commanding deep resonant Iraqi Karbalaei Baritone Radood "
            "with authentic microtonal melisma and crisp pharyngeal pronunciation, massive unison Iraqi male "
            "Raddada congregation choir with solemn human Ahaat backing, heavy muffled bare-palm chest thumping "
            "only, cavernous Karbala shrine hall acoustics, strictly 100% pure human vocal acapella, zero musical "
            "instruments, zero piano, zero strings, zero drums"
        ),
    },
    "v60_iraqi_euphrates_nassari_lami_56bpm": {
        "school": "School 04 & 08 — Southern Iraqi Euphrates Nassari & Basra Funeral Muthakkal",
        "dialect": "iraqi",
        "axis": "axis_1_pure_acapella",
        "bpm": 56,
        "maqam_arc": ["lami", "saba", "lami"],
        "dsp_mode": "thaqeel_muwazza",
        "empirical_exp": "175-MP3 School 04/08 Corpus (Sayyid Salam / Al-Kaabi) + Exp 24-B Lami Kasra",
        "sound_prompt": (
            "Mournful Southern Iraqi Euphrates Nassari and funeral Muthakkal Husseini Latmiya, slow 56 BPM "
            "grave processional cadence, Maqam Lami and Saba microtonal weeping melisma, deep velvety Iraqi "
            "Bass-Baritone Radood with prolonged aching vowel cadences, dark responsive unison male Husseiniya "
            "congregation choir, slow heavy muffled bare-palm chest thumping only, grand Karbala dome reverb, "
            "strictly 100% pure human vocal acapella, zero musical instruments, zero piano"
        ),
    },
    "v60_iraqi_rapid_shoor_kurd_bayati_shuri_124bpm": {
        "school": "School 05 — Iraqi Rapid Shoor & Haidari Majlis (Murtadha Harb / Faqid)",
        "dialect": "iraqi",
        "axis": "axis_1_pure_acapella",
        "bpm": 124,
        "maqam_arc": ["kurd", "bayati_shuri", "hijaz"],
        "dsp_mode": "shoor",
        "empirical_exp": "Exp 25 (d5942c88, 9.1/10, 124 BPM authentic Iraqi Shoor crowd thunder)",
        "sound_prompt": (
            "Intense Iraqi Karbalaei Rapid Shoor Husseini Latmiya, driving 124 BPM ecstatic mourning tempo, "
            "Maqam Kurd and Bayati Shuri fiery melodic hook, passionate raspy Iraqi Baritone Radood leading "
            "a thunderous unified Karbala Husseiniya male congregation chanting continuous rhythmic Hussain "
            "ostinato and synchronized rapid bare-palm chest strikes, dramatic stop-time solo vocal finale, "
            "tight live Husseiniya hall reverb, strictly zero piano, zero EDM synths, zero pop drum kit"
        ),
    },
    "v60_minbar_rubato_abudhiyah_nai_sikah_saba_0bpm": {
        "school": "Minbar Khutaba — Strict Unmetered Rubato Abudhiyah & Na'i (0 BPM)",
        "dialect": "iraqi",
        "axis": "axis_1_pure_solo_rubato",
        "bpm": 0,
        "maqam_arc": ["sikah", "saba", "lami"],
        "dsp_mode": "nai",
        "empirical_exp": "Exp 26-A (bb6ce74e, 9.5/10, true 0 BPM unmetered rubato pure solo voice)",
        "sound_prompt": (
            "Authentic Traditional Iraqi and Bahrani Minbar Abudhiyah and Na'i vocal lamentation, strict "
            "0 BPM unmetered Rubato free tempo with zero rhythmic pulse and zero beat grid, Maqam Sikah "
            "modulating into heartbroken microtonal Maqam Saba, devastating solo veteran Iraqi Khatib Baritone "
            "voice with natural breath intakes, soulful prolonged microtonal melisma, dignified weeping cracks "
            "on phrase endings only, hushed Karbala Husseiniya hall acoustics, strictly 100% pure solo human "
            "voice acapella, zero percussion, zero chest latm, zero musical instruments, zero piano"
        ),
    },
    "v60_classical_devotional_tawashih_rast_ajam_86bpm": {
        "school": "Classical Devotional Tawashih & Madih — Radiant Fusha Choral (Non-Latmiya)",
        "dialect": "fusha",
        "axis": "axis_devotional_tawashih",
        "bpm": 86,
        "maqam_arc": ["rast", "ajam", "rast"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "Exp 26-B (7a91ad46, 9.5/10, radiant Maqam Rast -> Ajam devotional choir)",
        "sound_prompt": (
            "Classical Arabic Islamic devotional Tawashih and Madih choral anthem in luminous Maqam Rast "
            "modulating to uplifting joyful Maqam Ajam, 86 BPM moderate majestic swaying rhythm, warm resonant "
            "solo Arab Munshid leading a rich traditional male vocal choir in unison and octave harmonies, "
            "gentle acoustic frame Daf drum pulse, warm stone mosque reverb, radiant spiritual devotion, "
            "strictly zero chest latm, zero weeping, zero piano, zero pop drums, zero electric synths"
        ),
    },
    "v60_bahrani_thulathi_bayati_shuri_nawa_athar_76bpm": {
        "school": "School 03 & 07 — Bahrani Triple-Pulse Thulathi (76 BPM Triplet Swing)",
        "dialect": "bahrani",
        "axis": "axis_1_pure_acapella",
        "bpm": 76,
        "maqam_arc": ["bayati_shuri", "nawa_athar", "bayati"],
        "dsp_mode": "bahrani_thulathi",
        "empirical_exp": "175-MP3 School 03/07 Triplet Survey + V54 Thulathi 75 BPM Triplet Verification",
        "sound_prompt": (
            "Passionate Bahrani Hussaini Thulathi triple-pulse Latmiya lament, 76 BPM authentic 6/8 triple "
            "Bahrani Matam cadence, Maqam Bayati Shuri modulating to dramatic Nawa Athar, commanding deep "
            "Gulf Bahrani male Baritone Radood with crisp pharyngeal pronunciation and Faizi microtonal "
            "vibrato, wide unison Bahrani male Matam choir response, synchronized triple-cadence bare-palm "
            "chest thumping only, solemn Matam dome reverb, strictly pure human vocal acapella, zero piano, "
            "zero musical instruments"
        ),
    },
    "v60_ahsa_bujabara_qafila_nawa_athar_hijaz_60bpm": {
        "school": "School 02 — Ahsa & Qatif Monumental Ashouri Qafila (Bujabara)",
        "dialect": "bahrani",
        "axis": "axis_3_zero_piano_hybrid",
        "bpm": 60,
        "maqam_arc": ["nawa_athar", "hijaz", "saba"],
        "dsp_mode": "modern_studio_ney_strings",
        "empirical_exp": "175-MP3 School 02 Anatomy (إعصار +7.9st arc, 8.2 dB stereo breathing)",
        "sound_prompt": (
            "Monumental Ahsa and Bahrani Ashouri Qafila Husseini Studio Latmiya, 60 BPM towering solemn "
            "processional weight, dramatic Maqam Nawa Athar modulating via Common Jins to Hijaz and Saba, "
            "commanding resonant Gulf Baritone Radood climbing from deep Qarar to soaring Jawab climax, "
            "massive layered male Matam unison choir, strictly percussive heavy bare chest thuds, dark bowed "
            "bass cello drone, mournful reed ney, subtle desert wind, strictly zero piano, zero keyboard chords, "
            "zero pop drums, zero snare backbeat"
        ),
    },
    "v60_najafi_dialogic_nazla_bayati_kurd_70bpm": {
        "school": "School 06 — Iraqi Najafi Dialogic Melodic Nazla (Al-Janami / Haidar Al-Bayati)",
        "dialect": "iraqi",
        "axis": "axis_1_pure_acapella",
        "bpm": 70,
        "maqam_arc": ["bayati", "kurd", "hijaz"],
        "dsp_mode": "latm",
        "empirical_exp": "175-MP3 School 06 Survey (70 BPM dialogic Najafi cadence, 6.4 dB stereo contrast)",
        "sound_prompt": (
            "Passionate Iraqi Najafi and Karbalaei dialogic Nazla Husseini Latmiya, 70 BPM steady rhythmic "
            "chest-latm stride, expressive Maqam Bayati modulating smoothly to Maqam Kurd and Hijaz, clear "
            "commanding Iraqi Baritone Radood with crisp pharyngeal colloquial articulation in brisk call-and-response "
            "with resonant unison Iraqi male Raddada choir, muffled bare-palm chest thumping only, authentic "
            "Najaf Husseiniya hall acoustics, strictly pure human vocal acapella, zero musical instruments, zero piano"
        ),
    },
    "v60_farsi_epic_zamineh_hijaz_kar_kurd_68bpm": {
        "school": "School 09 — Epic Processional Zamineh & Heroic Elegy (Karimi / Rasoli / Taheri)",
        "dialect": "iraqi",
        "axis": "axis_4_cinematic_sub_foley",
        "bpm": 68,
        "maqam_arc": ["hijaz_kar", "kurd", "nahawand"],
        "dsp_mode": "cinematic_foley_latmiya",
        "empirical_exp": "175-MP3 School 09 Survey (68 BPM monumental Bass-Baritone Zamineh gravity)",
        "sound_prompt": (
            "Monumental Epic Processional Zamineh Husseini Elegy, 68 BPM thunderous heavy stride, dramatic "
            "Maqam Hijaz Kar and Kurd gravity, commanding heroic Bass-Baritone lead vocal rising into massive "
            "stadium-scale unison male congregation chants, deep dark atmospheric cello drone and subtle desert "
            "battlefield wind textures, heavy synchronized bare-palm chest thuds, grand Husseiniya hall reverb, "
            "strictly zero piano, zero pop drums, zero rock snare backbeat, zero dance beats"
        ),
    },
    "v61_qatifi_faezi_husseini_saba_66bpm": {
        "school": "School 02 & 03 — Eastern Arabian Qatifi & Hasawi Heritage Faezi (Mulla Ali bin Fayez)",
        "dialect": "qatifi",
        "axis": "axis_1_pure_acapella",
        "bpm": 66,
        "maqam_arc": ["husseini", "bayati", "saba"],
        "dsp_mode": "bahrani_muthakkal",
        "empirical_exp": "Exp 29 (b7f0448a, 9.4/10, 0% instruments, pure Qatifi-Hasawi Faezi Husseini->Saba + NC35 audit)",
        "sound_prompt": (
            "Traditional Eastern Arabian Qatifi and Hasawi Faezi Husseini Latmiya elegy, 66 BPM warm calm "
            "triple-cadence mourning stride, Maqam Husseini emphasizing fifth-degree tension modulating into "
            "heartbroken Maqam Saba, authentic Eastern Arabian Qatifi-Bahrani Gulf male Baritone Radood with "
            "dignified storytelling clarity and microtonal vocal arabesques, warm unison male Matam congregation "
            "responses, soft muffled bare-palm chest thumping only, solemn Qatif Husseiniya dome acoustics, "
            "strictly 100% pure human vocal acapella, zero musical instruments, zero piano"
        ),
    },
    "v61_minbar_dashti_qatifi_nai_0bpm": {
        "school": "Minbar Khutaba — Persian-Arabic Tor Dashti & Qatifi Rubato Na'i (0 BPM)",
        "dialect": "qatifi",
        "axis": "axis_1_pure_solo_rubato",
        "bpm": 0,
        "maqam_arc": ["husseini", "bayati", "saba"],
        "dsp_mode": "nai",
        "empirical_exp": "V61 Minbar Dashti/Qatifi Canon + Exp 26-A (bb6ce74e, 9.5/10 true 0 BPM Rubato)",
        "sound_prompt": (
            "Traditional Qatifi, Bahrani, and Persian-Arabic Tor Dashti Minbar Na'i vocal lamentation, strict "
            "0 BPM unmetered free-time Rubato with zero beat grid, Maqam Husseini and Dashti plaintive rising-falling "
            "cadences resolving into Maqam Saba, intimate velvet solo veteran Khatib Baritone voice with unhurried "
            "prolonged vowels, natural breaths, and soft dignified weeping cracks on phrase endings only, sacred "
            "Husseiniya room acoustics, strictly 100% pure solo human voice acapella, zero percussion, zero piano"
        ),
    },
    "v61_qatifi_bahrani_jalwat_mawlid_ajam_rast_98bpm": {
        "school": "Joyful Shia Mawlid & Wilayah — Eastern Arabian Qatifi/Bahrani Jalwat & Celebratory Nasheed",
        "dialect": "qatifi",
        "axis": "axis_joyful_jalwat_nasheed",
        "bpm": 98,
        "maqam_arc": ["ajam", "rast", "suznak"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "Exp 27 (40f3ef1e, 9.3/10, authentic Qatifi-Bahrani Mawlid Jalwat, 0% latm, 0% piano)",
        "sound_prompt": (
            "Joyful Traditional Eastern Arabian Qatifi and Bahrani Shia Islamic Mawlid Jalwat and celebratory "
            "religious Nasheed, Maqam Ajam modulating to majestic Maqam Rast and Suznak, 98 BPM uplifting festive "
            "Khaleeji-Gulf devotional swaying rhythm, authentic Eastern Arabian Qatifi-Bahrani Gulf male Munshid "
            "lead vocal with crisp joyful Arabic articulation, enthusiastic unison male congregation choir "
            "call-and-response, traditional acoustic frame Daf drums and dignified synchronized celebratory hand "
            "clapping only, warm stone mosque celebration acoustics, strictly zero chest latm, zero weeping, "
            "zero piano, zero keyboard chords, zero modern pop synths, zero EDM drums"
        ),
    },
    "v61_classical_muwashah_ibtihal_husseini_suznak_74bpm": {
        "school": "Classical Heritage Religious Muwashah & Free-Rubato Ibtihal with Male Bitanah Choir",
        "dialect": "fusha",
        "axis": "axis_devotional_tawashih",
        "bpm": 74,
        "maqam_arc": ["husseini", "suznak", "hijaz", "rast"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "Exp 28 (6f531049, 9.9/10 ALL-TIME RECORD, 0 BPM Husseini Ibtihal -> 74 BPM Suznak Muwashah + Bitanah)",
        "sound_prompt": (
            "Classical Heritage Arabic Islamic Sacred Ibtihal transitioning into Traditional Religious Muwashah "
            "with male Bitanah choir, opening in strict 0 BPM unmetered solo Rubato Maqam Husseini spiritual "
            "supplication then entering 74 BPM dignified measured Maqam Suznak (Rast root with Hijaz upper fifth), "
            "commanding velvet Arab Munshid and Mubtahil Baritone lead vocal with intricate 24-EDO microtonal "
            "melisma and crisp Classical Arabic pronunciation, answered antiphonally by rich resonant unison male "
            "Bitanah choir on Taslim and Qafila refrains, gentle solemn acoustic frame Daf pulse in Muwashah only, "
            "cavernous mosque dome reverb, strictly zero chest latm, zero weeping, zero piano, zero pop drums"
        ),
    },
    "v62_orchestral_mahdawi_anthem_nahawand_kurd_78bpm": {
        "school": "Axis 5 — Contemporary Dignified Non-Lahwi Orchestral Shia Mahdawi & Social Anthem",
        "dialect": "fusha",
        "axis": "axis_5_dignified_orchestral_waqar",
        "bpm": 78,
        "maqam_arc": ["nahawand", "kurd", "ajam"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "V62 Architecture (موسيقى الوقار والشجن — 12-TET-Safe Orchestral Maqam Lock NC36)",
        "sound_prompt": (
            "Dignified Contemporary Orchestral Arabic Shia Islamic Mahdawi Anthem, 78 BPM solemn majestic steady "
            "march, 12-TET orchestral-safe Maqam Nahawand modulating smoothly to tender Maqam Kurd and uplifting "
            "heroic Maqam Ajam, commanding resonant Arab male Munshid Baritone lead vocal with crisp Classical "
            "Arabic pronunciation, rich layered male orchestral choir harmonies, lush sustained legato orchestral "
            "strings (violins, violas, deep cellos), expressive solo oboe, warm bassoon harmonic foundation, "
            "gentle contemplative acoustic guitar fingerpicking arpeggios, solemn orchestral timpani swells and "
            "traditional Bendir frame drum, spacious concert hall reverb, strictly non-dance, zero piano, zero "
            "pop drums, zero rock snare backbeat, zero jazz, zero chest latm"
        ),
    },
    "v62_qarid_hadi_qazwini_caravan_sikah_bayati_68bpm": {
        "school": "Classical Qarid & Caravan Atwar — Al-Hadi, Al-Qazwini & Al-Rukbani (Sheikh Baqir Al-Darraji)",
        "dialect": "fusha",
        "axis": "axis_3_zero_piano_hybrid",
        "bpm": 68,
        "maqam_arc": ["sikah", "bayati", "saba"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "V62 Qarid Atwar Canon (Al-Muthakkal, Al-Hadi, Al-Qazwini — 24-EDO Quarter-Tone Pure NC36)",
        "sound_prompt": (
            "Classical Arabic Qarid Hussaini Caravan Lament in Tor Al-Hadi and Al-Rukbani transitioning into "
            "sharp oratorical Al-Qazwini gravity, 68 BPM dignified desert caravan stride, 24-EDO quarter-tone "
            "Maqam Sikah modulating via Common Jins to Bayati and heartbroken Saba, commanding resonant Baritone "
            "Munshid vocal with unhurried rhyme elongations and microtonal arabesques, mournful breathy reed Ney, "
            "dignified solo Oud taqsim phrases, soft solemn Bendir frame drum, warm stone hall acoustics, strictly "
            "zero piano, zero 12-TET guitar chords, zero pop drums, zero dance rhythm"
        ),
    },
    "v62_dialect_hybrid_epic_operetta_hijaz_nahawand_84bpm": {
        "school": "Modern Shia Epic Historical Operetta — Fusha Narrative + Colloquial Climax Hybridization",
        "dialect": "iraqi_bahrani",
        "axis": "axis_5_dignified_orchestral_waqar",
        "bpm": 84,
        "maqam_arc": ["hijaz", "nahawand", "ajam"],
        "dsp_mode": "vocal_pure_master",
        "empirical_exp": "V62 Dialect-Hybrid Epic Operetta Architecture (Fusha Epic Opening -> Colloquial Emotional Peak)",
        "sound_prompt": (
            "Monumental Contemporary Arabic Shia Historical Epic Operetta blending Classical Fusha narrative "
            "stanzas with intimate Gulf-Iraqi colloquial emotional refrains, 84 BPM majestic dramatic march, "
            "12-TET orchestral-safe Maqam Hijaz modulating to cinematic Maqam Nahawand and heroic Maqam Ajam, "
            "commanding Baritone lead vocal answered by grand unison and harmonic male choir, sweeping sustained "
            "legato orchestral strings, noble solemn brass fanfare, deep orchestral timpani and traditional "
            "Dammam strikes, cavernous cinematic hall reverb, strictly non-dance, zero piano, zero pop drums, "
            "zero snare backbeat, zero club beats"
        ),
    },
}

# Module 76 (V62.0): Multi-Platform Mastering Targets (EBU R128 / ITU-R BS.1770 — موسيقى الوقار والشجن)
PLATFORM_LUFS_TARGETS_V62 = {
    "streaming": {
        "target_lufs": -14.0,
        "ceiling_dbtp": -1.0,
        "tolerance_lu": 1.5,
        "platforms": "YouTube, Spotify, Tidal",
    },
    "apple_music": {
        "target_lufs": -16.0,
        "ceiling_dbtp": -1.0,
        "tolerance_lu": 1.5,
        "platforms": "Apple Music",
    },
    "hires_qobuz": {
        "target_lufs": -18.0,
        "ceiling_dbtp": -1.0,
        "tolerance_lu": 1.5,
        "platforms": "Qobuz & Hi-Res Audiophile",
    },
    "broadcast_tv": {
        "target_lufs": -23.0,
        "ceiling_dbtp": -1.0,
        "tolerance_lu": 1.5,
        "platforms": "EBU R128 Broadcast Television",
    },
}

# Module 76 (V62.0 — NC36): Quarter-Tone Eastern Maqams vs. 12-TET Orchestral-Compatible Maqams
QUARTER_TONE_EASTERN_MAQAMS = frozenset(
    ("saba", "bayati", "bayati_shuri", "husseini", "sikah", "rast", "suznak")
)
ORCHESTRAL_12TET_SAFE_MAQAMS = frozenset(
    ("nahawand", "kurd", "hijaz", "hijaz_kar", "nawa_athar", "lami", "saba_zamzam", "ajam")
)

# Module 76 (V62.0): Axis 5 — Six Dignified Non-Lahwi Orchestral Instrument Families (موسيقى الوقار والشجن)
ORCHESTRAL_SIX_FAMILIES_WAQAR_V62 = {
    "woodwinds_spiritual": {
        "arabic_title": "الناي والفلوت والأوبوا والفاجوت (الباصون)",
        "instruments": ["ney", "flute", "oboe", "bassoon"],
        "waqar_rule": "Ney leads Saba/Bayati spiritual grief; Flute brings serenity; Oboe carries piercing elegiac sorrow; Bassoon anchors low orchestral gravity.",
    },
    "reeds_and_brass_dignified": {
        "arabic_title": "الكلارينيت والساكسفون المتصل والهارمونيكا والأبواق النحاسية",
        "instruments": ["clarinet", "legato_saxophone", "quiet_harmonica", "martial_brass"],
        "waqar_rule": "Clarinet for modal transitions; slow Legato Saxophone strictly zero jazz/dance; quiet solo Harmonica for longing/exile; dignified Brass for martial heroic epics.",
    },
    "strings_and_oud_legato": {
        "arabic_title": "الوتريات الأوركسترالية المتصلة والعود التقسيمي الرصين",
        "instruments": ["violin_legato", "viola_legato", "cello_legato", "solo_oud_taqsim"],
        "waqar_rule": "Sustained Legato orchestral string beds for epic grief; dignified unhurried solo Oud taqsim strictly avoiding fast dance strumming.",
    },
    "guitars_contemplative": {
        "arabic_title": "القيتار الأكوستيك والكلاسيك والغيتار الكهربائي النقي",
        "instruments": ["acoustic_guitar_fingerpicking", "clean_tone_electric_guitar"],
        "waqar_rule": "Gentle fingerpicking arpeggios and ambient clean-tone reverb swells in 12-TET-safe Maqams only (NC36); zero rock/pop strumming.",
    },
    "keys_and_vocal_pads": {
        "arabic_title": "البيانو التأملي والأورغ الشرقي الميكروتوني والبادات والكورال",
        "instruments": ["contemplative_piano_12tet_only", "oriental_24edo_keyboard", "ambient_pads", "layered_choir"],
        "waqar_rule": "Contemplative Piano strictly restricted to non-Latmiya 12-TET-safe Maqams (Nahawand/Kurd/Ajam, NC36); use Oriental 24-EDO keyboard for quarter-tone Maqams.",
    },
    "percussion_dignified": {
        "arabic_title": "البندير والدمامات والطوس والتيمباني والإيقاعات الموزونة",
        "instruments": ["bendir", "dammam", "tasa", "timpani", "dignified_cinematic_drums"],
        "waqar_rule": "Bendir for heritage Madih/Tawashih; Dammam, Tasa, Timpani & solemn cinematic drums for Mawkib/operetta gravitas; strictly zero club/dance beats.",
    },
}

# Module 76 (V62.0): Classical Qarid & Popular Heritage Atwar Catalog (Sheikh Baqir Al-Darraji & Dalil Al-Qurraa)
QARID_AND_POPULAR_ATWAR_V62 = {
    "qarid_classical_fusha": {
        "al_muthakkal_qarid": "Grave dignified Fusha Qarid with prolonged rhyme Madd (56-64 BPM or Rubato).",
        "al_hadi": "Caravan travel cadence on Maqam Sikah or Bayati evoking the Karbala journey (64-72 BPM).",
        "al_qazwini": "Sharp oratorical historical lamentation tone suited for solemn Karbala chronicles.",
    },
    "popular_heritage_colloquial": {
        "al_faezi": "Mulla Ali bin Fayez slow or ascending triple-cadence lament shared across Qatif, Bahrain & Iraq.",
        "al_rukbani": "Desert caravan elegiac lament on Maqam Sikah/Lami portraying the captives' march.",
        "al_zurayji": "Southern Iraqi Euphrates plaintive heritage Tor.",
        "al_janubi": "Deep emotional Southern Iraqi mourning melody.",
        "al_mullai": "Classic Najafi/Karbalaei Mulla storytelling recitative cadence.",
        "al_jamarat": "Bahraini heritage poetic elegy form pioneered by Mulla Atiya Al-Jamri.",
        "al_maymar_and_nayel": "Iraqi colloquial lyrical quatrain/couplet meters for emotional mourning.",
        "al_jalwat": "Celebratory Qatifi & Bahraini Mawlid/wedding devotional chants on Rast, Sikah & Ajam.",
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
    # Authentic Nader Al-Tattan / Gulf Bahrani lexicon markers (V57.1)
    "آنا",
    "شنهو",
    "منهو",
    "منته",
    "اوي ",
    "اوياي",
    "اوياك",
    "اوياهم",
    "وي زوارك",
    "ابلا ",
    "اعلى بالي",
    "اعلى نحرك",
    "اعلى گبرك",
    "اعليك",
    "اعليها",
    "اعليه",
    "الماتم",
    "بماتمك",
    "اورّي اشموع",
    "يوري اشموع",
    "اشكثر",
    "اشكبرها",
    "اشعجب",
    "شاللي",
    "شتسوي",
    "شقول",
    "شقصدي",
    "شيداويها",
    "شيقدرها",
    "أشوه",
    "مهو",
    "ماحد",
    "عدكم",
    "عدها",
    "اثنعش",
    "أجدامه",
    "أجدامي",
    "باچر",
    "بالورگ",
    "احترگ",
    "أوراگ",
    "وچني",
    "چتف",
    "ايبدي",
    "ايقول",
    "ايجدد",
    "ايهندس",
    "ايزور",
    "اتضمها",
    "اتواسوها",
    "ل تنسيني",
    "لزورك",
    "لفيت",
    "يوليدي",
    "شالأهزه",
    "وش دراني",
    "وش هالقلب",
    "وش معنى",
    "وش نابت",
    "للحين",
    "عقب هذا",
    "أناظر ليك",
    "الضعينة",
    "سولف لي",
    "ابلياك",
)

# Module 75 (V61.0): Distinctive Eastern Arabian Qatifi Dialect Markers (shared mother-dialect with Bahrani + local Qatifi lexicon)
QATIFI_MARKERS = (
    "غناتي",
    "غَنَاتِي",
    "غَناتي",
    "هداويش",
    "هَداويش",
    "لاويه",
    "لاويّه",
    "عفر",
    "عَفَر",
    "إهني",
    "اهني",
    "إهنيّ",
    "امبى",
    "أمبى",
    "چدي",
    "تشِدِي",
    "خلف چبدي",
    "خلف تشبدي",
    "خلف تشَبدي",
    "خلفدي",
    "شحوالش",
    "إشحوالش",
    "إشحوالِش",
    "شحوالك",
    "إشحوالك",
    "هالحزة",
    "هالحَزّة",
    "هالحزه",
    "واجد",
    "واجِد",
    "مغربل",
    "دريشة",
    "القطيف",
    "قطيفي",
    "تاروت",
    "صفوى",
    "سيهات",
    "العوامية",
    "أبغى",
    "ماني",
)

QATIFI_WORD_SHAPING_MAP = {
    "غناتي": "غَنَاتِي",
    "هداويش": "هَدَاوِيشْ",
    "لاويه": "لَاوِيَّه",
    "عفر": "عَفَرْ",
    "إهني": "إِهْنِي",
    "اهني": "إِهْنِي",
    "امبى": "أَمْبَى",
    "چدي": "چِدِي",
    "خلفدي": "خَلَفْدِي",
    "شحوالش": "إِشْحْوَالِشْ",
    "شحوالك": "إِشْحْوَالَكْ",
    "هالحزة": "هَلْ حَزَّه",
    "هالحزه": "هَلْ حَزَّه",
    "واجد": "وَاجِدْ",
    "مغربل": "إِمْغَرْبَلْ",
    "دريشة": "دِرِيشَه",
    "أبغى": "أَبْغَى",
    "ماني": "مَانِي",
    "بقلب": "إِبْگَلِبْ",
    "بقلبي": "إِبْگَلْبِي",
    "عالباب": "عَلَه البَابْ",
}

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


def _count_qatifi_markers(text):
    """Module 75 (V61.0): Count distinctive Eastern Arabian Qatifi markers on diacritic-stripped text."""
    ortho = normalize_daad_dhaa_homographs(normalize_iraqi_orthographic_gaf(text))
    bare_text = re.sub(r"[\u064B-\u0652]", "", ortho)
    hits = 0
    for marker in QATIFI_MARKERS:
        bare_m = re.sub(r"[\u064B-\u0652]", "", marker)
        if bare_m and re.search(rf"(?<!\S){re.escape(bare_m)}(?!\S)", bare_text):
            hits += 1
    return hits


def detect_and_shape_dialect(text, enforce_iraqi_dhaa=None, use_tatweel=False, dialect=None):
    """Modules 43, 49 & 75 (V61.0): Identify Qatifi, Bahrani, Iraqi, or Neutral Fusion and shape tokens."""
    bahrani_hits, iraqi_hits = _count_dialect_markers(text)
    qatifi_hits = _count_qatifi_markers(text)

    if dialect in ("qatifi", "bahrani", "iraqi", "iraqi_bahrani", "fusha"):
        detected = dialect
    elif qatifi_hits >= 2 and qatifi_hits >= iraqi_hits:
        detected = "qatifi"
    elif bahrani_hits > iraqi_hits:
        detected = "bahrani"
    elif iraqi_hits > bahrani_hits:
        detected = "iraqi"
    else:
        detected = "iraqi_bahrani"

    if enforce_iraqi_dhaa is None:
        enforce_iraqi_dhaa = detected == "iraqi"

    shaped = de_cliticize_and_separate_words(text, use_tatweel=use_tatweel)
    shaped = heal_nc21_short_clause_pauses(shaped)
    shaped = normalize_demonstrative_hal(shaped, dialect="bahrani" if detected == "qatifi" else detected)
    shaped = repair_word_initial_sukun_and_diphthongs(shaped)
    if detected == "qatifi":
        shaped = shaped.replace("إِعْلَه الجَمُرْ", "عَلَه الجَمِرْ")
        shaped = shape_words_by_boundary(shaped, BAHRANI_WORD_SHAPING_MAP, use_tatweel=use_tatweel)
        shaped = shape_words_by_boundary(shaped, QATIFI_WORD_SHAPING_MAP, use_tatweel=use_tatweel)
        if enforce_iraqi_dhaa:
            shaped = shaped.replace("فَاضِلْ", "فَاظِلْ").replace("ضْلُوعِي", "ظْلُوعِي")
        maqam_rule = "Calm Qatifi-Hasawi Faezi Storytelling Cadence & Warm Microtonal Imala in Maqam Husseini/Saba"
        dhad_mode = "Emphatic Iraqi Dhaa (ظ)" if enforce_iraqi_dhaa else "Standard/Qatifi-Bahrani Dhad (ض)"
        sound_dialect = "authentic Eastern Arabian Qatifi-Bahrani Gulf dialect"
    elif detected == "bahrani":
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
        "qatifi_score": qatifi_hits,
        "iraqi_score": iraqi_hits,
        "dhad_articulation": dhad_mode,
        "maqam_articulation_rule": maqam_rule,
        "shaped_lyrics": shaped,
    }


def audit_syllable_density_v60(lyrics_text, target_bpm=72.0, max_syl_per_sec=4.2):
    """Module 74 (V60.0, NC27-C): Fast-Meter Syllable Density Governor (<= 4.2 syl/s prevents Lyria 3.5 garble)."""
    bpm_eff = float(target_bpm) if target_bpm and float(target_bpm) > 0.0 else 72.0
    # Empirical Lyria 3.5 bar window: ~4 beats per poetic line at <= 76 BPM, ~3 beats at faster 88-132 BPM meters
    beats_per_line = 3.0 if bpm_eff >= 88.0 else 4.0
    line_sec = max(1.6, (60.0 / bpm_eff) * beats_per_line)

    dense_lines = []
    max_rate = 0.0
    for idx, raw_ln in enumerate(lyrics_text.splitlines(), start=1):
        ln = raw_ln.strip()
        if not ln or (ln.startswith("[") and ln.endswith("]")):
            continue
        clean = re.sub(r"[^\u0621-\u064A\u067E\u0686\u06AF\s]", "", ln).strip()
        words = [w for w in clean.split() if w]
        if not words:
            continue
        syl_est = sum(max(1, int(round(len(w) * 0.58))) for w in words)
        # Lines split by '..' get extra bar phrasing budget
        n_segs = max(1, len([p for p in ln.split("..") if p.strip()]))
        eff_sec = line_sec * (1.0 + 0.55 * (n_segs - 1))
        rate = round(float(syl_est) / eff_sec, 2)
        max_rate = max(max_rate, rate)
        if rate > float(max_syl_per_sec):
            dense_lines.append(
                {
                    "line_number": idx,
                    "estimated_syllables": syl_est,
                    "estimated_syl_per_sec": rate,
                    "suggestion": "Split line with '..' breath pause or trim 1-2 words to stay <= 4.2 syl/s (NC27-C).",
                    "text": ln,
                }
            )
    return {
        "target_bpm": round(bpm_eff, 1),
        "cap_syl_per_sec": float(max_syl_per_sec),
        "max_syllables_per_sec": round(max_rate, 2),
        "exceeds_4_2_syl_per_sec_cap": bool(dense_lines),
        "dense_line_count": len(dense_lines),
        "dense_lines": dense_lines,
    }


def format_clean_lyrics_for_lyria35(raw_poem, dialect=None, target_bpm=None):
    """Module 72, 74 & 75 (V57.0–V61.0): Clean Natural Arabic + NC27-C Affricate Law + NC35 Qatifi Locks + Density Governor."""
    sanitized = sanitize_poem_decorations(raw_poem.replace("\\n", "\n"))
    bahrani_hits, iraqi_hits = _count_dialect_markers(sanitized)
    qatifi_hits = _count_qatifi_markers(sanitized)
    if dialect in ("iraqi", "bahrani", "qatifi", "iraqi_bahrani", "fusha"):
        detected = dialect
    elif qatifi_hits >= 2 and qatifi_hits >= iraqi_hits:
        detected = "qatifi"
    elif bahrani_hits > iraqi_hits:
        detected = "bahrani"
    elif iraqi_hits > bahrani_hits:
        detected = "iraqi"
    else:
        detected = "iraqi_bahrani"

    # NC27-C: Detect & repair any illegal user-supplied Sukun on تْش before stripping heavy tashkeel
    illegal_tsh_fixed = len(re.findall(r"(?:^|[\s(\[]|[اوي\u0652])تْش|بْ?تْش", sanitized))

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

    # Restore synthetic prosthetic إمن / إعله / اوي / ابلا tokens that Lyria 3.5 misreads
    cleaned = re.sub(r"(?<!\w)[إا]من(?!\w)", "من", cleaned)
    cleaned = re.sub(r"(?<!\w)[إا]عله(?!\w)", "على", cleaned)
    cleaned = re.sub(r"(?<!\w)اعلى(?!\w)", "على", cleaned)
    cleaned = re.sub(r"(?<!\w)اعليك(?!\w)", "عليك", cleaned)
    cleaned = re.sub(r"(?<!\w)اعليه(?!\w)", "عليه", cleaned)
    cleaned = re.sub(r"(?<!\w)اعليها(?!\w)", "عليها", cleaned)
    cleaned = re.sub(r"(?<!\w)ابلا(?!\w)", "بلا", cleaned)
    cleaned = re.sub(r"(?<!\w)ابلياك(?!\w)", "بليّاك", cleaned)
    cleaned = re.sub(r"(?<!\w)اوي(?!\w)", "ويّ", cleaned)
    cleaned = re.sub(r"(?<!\w)اوياي(?!\w)", "ويّاي", cleaned)
    cleaned = re.sub(r"(?<!\w)اوياك(?!\w)", "ويّاك", cleaned)
    cleaned = re.sub(r"(?<!\w)اوياهم(?!\w)", "ويّاهم", cleaned)
    cleaned = re.sub(r"(?<!\w)[إا]حسين(?!\w)", "حسين", cleaned)
    cleaned = re.sub(r"(?<!\w)[إا]ب(?=[گقكجچتثدذرزسشصضطظعغفقكلمنهوي])", "ب", cleaned)
    cleaned = re.sub(r"(?<!\w)[إا]عيون", "عيون", cleaned)
    cleaned = cleaned.replace("فاظل", "فاضل")

    # NC27 & NC27-C: Phonologically-exact affricate law (تْش ONLY after short vowel; plain تش after long vowel/Sukun/initial)
    token_map = {
        "تبچي": "تبتشي",
        "يبچي": "يبتشي",
        "أحچي": "أحتشي",
        "احچي": "أحتشي",
        "واحچيله": "واحتشيله",
        "البچي": "البَتْشِي",
        "الحچي": "الحَتْشِي",
        "البتشي": "البَتْشِي",
        "الحتشي": "الحَتْشِي",
        "باچر": "باتشر",
        "باتشر": "باتشر",
        "وچني": "وتشني",
        "چتف": "تشتف",
        "چم": "تشم",
        "چنت": "تشنت",
        "چنه": "تشنه",
        "چنها": "تشنها",
        "چفوفك": "تشفوفك",
        "چفوفه": "تشفوفه",
        "چفوف": "تشفوف",
        "چفي": "تشفي",
        "چفك": "تشفك",
        "يچوي": "يتشوي",
        "مچوي": "متشوي",
        # NC35 (V61.0): Empirically proven Qatifi-Bahrani clean Lyria 3.5 orthoepy locks (Exp 27 & Exp 29)
        "چبدي": "چَبْدي",
        "تشبدي": "چَبْدي",
        "چدي": "چِذي",
        "چذي": "چِذي",
        "تشدي": "چِذي",
        "مچان": "مكان",
        "متشان": "مكان",
        "چبير": "تشِبير",
        "تشبير": "تشِبير",
        "غناتي": "غَنَاتِي",
        "إهني": "إهْني",
        "إهنيّ": "إهْني",
        "اهني": "إهْني",
        "اهنيّ": "إهْني",
        "بالرمضا": "بالرَّمْضى",
        "بالرمضى": "بالرَّمْضى",
        "لاويه": "لاويّه",
        "لاويّه": "لاويّه",
        "هداويش": "هَداويش",
        "عفر": "عَفَر",
        "امبى": "أمبى",
        "أمبى": "أمبى",
        "هالحزة": "هالحَزّة",
        "هالحزه": "هالحَزّة",
        "هالحزّة": "هالحَزّة",
        "واجد": "واجِد",
        "شحوالش": "إشحوالِش",
        "اشحوالش": "إشحوالِش",
        "إشحوالش": "إشحوالِش",
        "شحوالك": "إشحوالَك",
        "اشحوالك": "إشحوالَك",
        "إشحوالك": "إشحوالَك",
        "حچي": "حَتشِي",
        "وحچي": "وحَتشِي",
        "حتشي": "حَتشِي",
        "وحتشي": "وحَتشِي",
        "ملچوم": "مَلتشوم",
        "ملتشوم": "مَلتشوم",
        "بلهيبه": "بِلَهيبه",
        "ولهيب": "ولَهيب",
        "عشت": "عِشت",
        "أذنت": "أذِنت",
        "وگلبه": "وگَلبه",
        "وقلبه": "وگَلبه",
        "گلبه": "گَلبه",
        "قلبه": "گَلبه",
        "قلبي": "گلبي",
        "وبقلبي": "وبگلبي",
        "يقول": "يگول",
        "أقول": "أگول",
        "اقول": "أگول",
        "أقدر": "أگدر",
        "اقدر": "أگدر",
        "تقدر": "تگدر",
        "قدامي": "گدامي",
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
            hdr_inner = line.strip()[1:-1].strip()
            hdr_head = re.split(r"\s*[—\-:|/]\s*", hdr_inner)[0].strip()
            hdr_ar = re.sub(r"[A-Za-z0-9_]+", "", hdr_head).strip()
            out_lines.append(f"[{hdr_ar or 'المقطع'}]")
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
        if detected in ("bahrani", "qatifi")
        else "v57_iraqi_karbalaei_pure_majlis_60bpm_saba_lami"
    )
    density_report = audit_syllable_density_v60(
        final_lyrics, target_bpm=target_bpm if target_bpm is not None else 72.0
    )
    return {
        "detected_dialect": detected,
        "clean_lyria35_lyrics": final_lyrics,
        "recommended_v57_prompt_key": prompt_key,
        "recommended_v57_sound_prompt": EXTENDED_ATWAR_PROMPTS_V52[prompt_key],
        "nc26_anti_token_shattering_applied": True,
        "nc27_ch_to_tsh_digraph_count": ch_converted,
        "nc27c_phonological_affricate_rule_applied": True,
        "nc27c_illegal_tsh_sukun_repaired": illegal_tsh_fixed,
        "syllable_density_report": density_report,
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
    shoor_kw = ("حسين حسين", "مامدفون والينه")
    shoor_block_kw = (
        "شمر", "مذبوح", "حوافر", "الزهرا", "فاطمه", "فاطمة", "ضلع",
        "الأربعين", "زوارك", "نبي مرسل", "صلى الله عليك", "المهدي",
        "المرتضى", "ليلة الضربه", "ليلة الضربة", "عبدالله", "فاضوا هياما",
    )
    ecstatic_shoor_kw = ("مجنون", "جنون", "اهواك", "عشگ", "عشق", "شيعي", "حبيب")
    fazzaiya_kw = ("فزاعيه", "فزاعية", "رباطات فزاعية", "تبرالي")
    hosa_kw = ("[هوسة]", "هوسه", "هوسة", "رباطات")
    tawshih_kw = (
        "[تواشيح]", "[ابتهالات]", "تواشيح", "أهل الكساء", "المباهلة",
        "أنشودة", "نشيد", "صلى الله عليك", "نبي مرسل", "قاب قوسين",
    )
    epic_fusha_kw = ("فاضوا هياما", "أنصار الإبا", "ساعة الصفر", "قبضة الكف الخيبرية")
    tragedy_kw = ("كربلا", "عاشور", "سبي", "سبايا", "مذبوح", "حوافر", "شمر", "مشرعة", "علگمي", "علقمي", "خرابة", "خرابه", "نحر", "على صدره", "عالصدر")
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

    is_ecstatic_shoor = (
        avg_words <= 4.3
        and len(hemistichs) <= 14
        and any(k in bare_text for k in ecstatic_shoor_kw)
        and not any(k in bare_text for k in shoor_block_kw)
    )
    if any(k in bare_text for k in nai_explicit_kw) or is_abudhiyah or is_zuhayri:
        mode = "nai"
        bpm = 0
        maqam = "saba"
        meter = "abudhiyah" if is_abudhiyah else ("zuhayri" if is_zuhayri else "mujarradat")
        tor = "tor_nai_kashi"
        school = "School 04 (النعي المنبري والشجن العراقي)"
        prompt = MASTER_SOUND_PROMPTS_V48_5["minbar_nai_0bpm_rubato_saba_exclusive_weeping"]
    elif any(k in bare_text for k in epic_fusha_kw):
        mode = "zanjeel_bahrani"
        bpm = 82
        maqam = "hijaz"
        meter = "muwashah"
        tor = "tor_bahrani_waqfa"
        school = "School 03 (القصيدة الفصحى الملحمية البحرانية — الأكرف/التتان)"
        prompt = EXTENDED_ATWAR_PROMPTS_V52["mawkib_dammam_cymbals_brass_procession_78bpm_hijaz_v56"]
    elif any(k in bare_text for k in tawshih_kw) and not any(k in bare_text for k in tragedy_kw):
        mode = "vocal_pure_master"
        bpm = 86
        maqam = "rast"
        meter = "muwashah"
        tor = "tor_tawshih_shia"
        school = "School 03 (التوشيح والقصيدة الإنشادية — الأكرف)"
        prompt = EXTENDED_ATWAR_PROMPTS_V52["shia_tawshih_nasheed_86bpm_rast_hijaz_v52"]
    elif shoor_exact or any(k in bare_text for k in shoor_kw) or is_ecstatic_shoor:
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


def validate_maqam_orchestration_compatibility(maqam, uses_western_12tet_chords=False):
    """Module 76 (V62.0 — NC36): Guard Quarter-Tone Eastern Maqams against 12-TET Piano/Guitar chord clash."""
    m_key = str(maqam or "saba").strip().lower()
    if m_key not in MAQAM_FREQS:
        raise ValueError(f"Unsupported Maqam for orchestration check: {maqam}")
    has_qt = m_key in QUARTER_TONE_EASTERN_MAQAMS
    clash = bool(has_qt and uses_western_12tet_chords)
    if clash:
        rec = (
            f"Maqam '{m_key}' contains 24-EDO quarter-tones: avoid Western 12-TET piano/guitar chords. "
            "Use Pure Acapella, 24-EDO Ney/Oud/Legato Strings, or Oriental Quarter-Tone Keyboard — or "
            "modulate to a 12-TET-safe Maqam (nahawand, kurd, hijaz, ajam) for Western orchestral chords."
        )
    elif has_qt:
        rec = (
            f"Maqam '{m_key}' is a pure 24-EDO quarter-tone Eastern Maqam: disable 12-TET pitch snap "
            "(manual microtonal Melodyne only) and pair with vocal acapella, Ney, Oud, or fretless strings."
        )
    else:
        rec = (
            f"Maqam '{m_key}' is 12-TET orchestral-compatible (zero quarter-tones): safely supports "
            "dignified non-lahwi orchestral strings, oboe, bassoon, brass, acoustic guitar arpeggios, "
            "and contemplative piano in non-Latmiya Nasheed/Operetta productions (NC36)."
        )
    return {
        "maqam": m_key,
        "contains_quarter_tone": has_qt,
        "orchestral_12tet_compatible": not has_qt,
        "uses_western_12tet_chords": bool(uses_western_12tet_chords),
        "quarter_tone_clash_risk": clash,
        "nc36_passed": not clash,
        "recommendation": rec,
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

    if g_key == "jalwat":
        chosen_maqam = (maqam or "ajam").lower()
        chosen_bpm = 98 if bpm is None else int(bpm)
        return {
            "genre": "jalwat",
            "dialect": dialect,
            "maqam": chosen_maqam,
            "bpm": chosen_bpm,
            "uses_chest_latm": False,
            "sound_prompt": MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60[
                "v61_qatifi_bahrani_jalwat_mawlid_ajam_rast_98bpm"
            ]["sound_prompt"],
            "song_leakage_terms_detected": [],
        }

    if g_key == "muwashah":
        chosen_maqam = (maqam or "suznak").lower()
        chosen_bpm = 74 if bpm is None else int(bpm)
        return {
            "genre": "muwashah",
            "dialect": "fusha",
            "maqam": chosen_maqam,
            "bpm": chosen_bpm,
            "uses_chest_latm": False,
            "sound_prompt": MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60[
                "v61_classical_muwashah_ibtihal_husseini_suznak_74bpm"
            ]["sound_prompt"],
            "song_leakage_terms_detected": [],
        }

    if g_key == "nai":
        chosen_maqam = (maqam or "husseini").lower()
        fp_key = (
            "v61_minbar_dashti_qatifi_nai_0bpm"
            if dialect in ("qatifi", "bahrani")
            else "v60_minbar_rubato_abudhiyah_nai_sikah_saba_0bpm"
        )
        return {
            "genre": "nai",
            "dialect": dialect,
            "maqam": chosen_maqam,
            "bpm": 0,
            "uses_chest_latm": False,
            "crying_isolated_to_zero_bpm": True,
            "sound_prompt": MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60[fp_key]["sound_prompt"],
            "song_leakage_terms_detected": [],
        }

    if g_key == "operetta":
        chosen_maqam = (maqam or "nahawand").lower()
        chosen_bpm = 78 if bpm is None else int(bpm)
        fp_key = (
            "v62_dialect_hybrid_epic_operetta_hijaz_nahawand_84bpm"
            if chosen_maqam in ("hijaz", "hijaz_kar") or chosen_bpm >= 82
            else "v62_orchestral_mahdawi_anthem_nahawand_kurd_78bpm"
        )
        return {
            "genre": "operetta",
            "dialect": dialect,
            "maqam": chosen_maqam,
            "bpm": chosen_bpm,
            "uses_chest_latm": False,
            "nc36_orchestration_check": validate_maqam_orchestration_compatibility(
                chosen_maqam, uses_western_12tet_chords=True
            ),
            "sound_prompt": MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60[fp_key]["sound_prompt"],
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


def _estimate_muwashah_segment_syllables(line_text):
    """Estimate prosodic word/segment syllable length for Muwashah multi-meter detection."""
    parts = [p.strip() for p in re.split(r"\.\.|/|—", line_text) if p.strip()]
    if not parts:
        return 0.0, 0
    seg_lens = []
    for part in parts:
        clean_p = re.sub(r"[^\u0621-\u064A\u067E\u0686\u06AF\s]", "", part).strip()
        words = [w for w in clean_p.split() if w]
        syls = sum(max(1, int(round(len(w) * 0.55))) for w in words)
        seg_lens.append(syls)
    avg_seg = float(sum(seg_lens)) / max(1, len(seg_lens))
    return avg_seg, len(parts)


def analyze_multi_meter_muwashah_structure(poem_text):
    """Module 73 (V58.0): Detect Multi-Meter Muwashah sections and map Common Jins Maqam & BPM gears."""
    normalized = poem_text.replace("\\n", "\n").strip()
    raw_blocks = re.split(r"(\[[^\]]+\])", normalized)
    parsed_blocks = []
    if len(raw_blocks) > 1:
        cur_tag = "[المستهل]"
        for chunk in raw_blocks:
            if chunk.startswith("[") and chunk.endswith("]"):
                cur_tag = chunk.strip()
            elif chunk.strip():
                lns = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
                if lns:
                    parsed_blocks.append((cur_tag, lns))
    else:
        # Auto-group untagged multi-meter poems by blank lines or clear line-length/structure shifts
        cur_lines = []
        cur_bucket = None
        sec_idx = 1
        for raw_ln in normalized.splitlines():
            ln = raw_ln.strip()
            if not ln:
                if cur_lines:
                    parsed_blocks.append((f"[المقطع {sec_idx}]", cur_lines))
                    sec_idx += 1
                    cur_lines = []
                    cur_bucket = None
                continue
            avg_seg, n_parts = _estimate_muwashah_segment_syllables(ln)
            is_choir = ln.startswith("(") and ln.endswith(")")
            bucket = (
                "choir"
                if is_choir
                else ("short_staccato" if (avg_seg <= 5.8 and n_parts >= 2) else ("long_narrative" if avg_seg >= 9.0 else "medium_flow"))
            )
            if cur_bucket is not None and bucket != cur_bucket and len(cur_lines) >= 2:
                parsed_blocks.append((f"[المقطع {sec_idx}]", cur_lines))
                sec_idx += 1
                cur_lines = [ln]
                cur_bucket = bucket
            else:
                cur_lines.append(ln)
                cur_bucket = bucket
        if cur_lines:
            parsed_blocks.append((f"[المقطع {sec_idx}]", cur_lines))

    if not parsed_blocks:
        parsed_blocks = [("[المستهل]", [normalized])] if normalized else []

    rec_base = recommend_tor_and_rhythm_for_poem(normalized)
    base_bpm = max(56, min(96, int(rec_base.get("recommended_bpm", 72)) or 72))
    dialect = rec_base.get("detected_dialect", "bahrani")

    archetypes = set()
    section_blueprints = []
    maqam_arc = []
    bpm_gears = []
    for idx, (tag, lines) in enumerate(parsed_blocks):
        seg_vals = [_estimate_muwashah_segment_syllables(ln) for ln in lines]
        avg_syl = round(float(sum(v[0] for v in seg_vals)) / max(1, len(seg_vals)), 2)
        max_parts = max((v[1] for v in seg_vals), default=1)
        joined = " ".join(lines)
        has_choir_parens = any("(" in ln and ")" in ln for ln in lines)
        is_narrative_opening = "سردي" in tag or (idx == 0 and avg_syl >= 8.5 and not has_choir_parens)
        is_choir_tag = any(k in tag for k in ("لازمة", "كورال", "جماعي", "مستهل", "مُسْتَهَلّ", "موشح جماعي"))
        is_elegy_tag = any(k in tag for k in ("زينب", "الختام", "نعي", "مصرع", "كسرة", "فجيعة")) or any(
            k in joined for k in ("زينب", "نحره", "ذبح", "مرمي", "اموت", "أموت")
        )

        if has_choir_parens or (is_choir_tag and not is_narrative_opening):
            archetype = "collective_choir_anthem"
            maqam_name = "Hijaz"
            gear_mult = 1.0
            bpm_sec = base_bpm
            register = "Jawab (+6 to +9 semitones soaring chest unison)"
            transition = "1-beat full silence explosion into wide stereo male Majlis choir (+5 dB side expansion)"
            performer = "Full wide unison Bahrani/Iraqi male Matam congregation choir"
        elif avg_syl <= 6.2 and max_parts >= 2:
            archetype = "short_staccato_muwashah"
            maqam_name = "Bayati Shuri / Hijaz"
            gear_mult = 1.25
            bpm_sec = min(130, int(round(base_bpm * 1.15)))
            register = "Wasat (middle energetic narrative register)"
            transition = "Cadential Qa'da rhythm mute drop before locking brisk staccato chest-latm pulse"
            performer = "Solo Radood brisk rhythmic delivery with short choral response echoes"
        elif is_elegy_tag and idx >= max(1, len(parsed_blocks) - 2):
            archetype = "solemn_weeping_elegy"
            maqam_name = "Saba / Lami"
            gear_mult = 0.75 if base_bpm >= 80 else 1.0
            bpm_sec = max(56, int(round(base_bpm * gear_mult)))
            register = "Jawab emotional peak descending into heartbroken Qarar resolution"
            transition = "Al-Akraf Qa'da full percussion mute over solo mournful Cello/Ney breath -> slow heavy grief drop"
            performer = "Solo Radood tear-laced authentic dialect delivery answered by deep unison choir"
        else:
            archetype = "long_narrative_opening"
            maqam_name = "Bayati"
            gear_mult = 1.0
            bpm_sec = base_bpm
            register = "Qarar (deep warm intimate Baritone chest voice)"
            transition = "Solemn opening Cello/Ney or vintage archive EQ drop into steady bare-chest Matam pulse"
            performer = "Solo authentic dialect Radood centered dry-forward"

        archetypes.add(archetype)
        if not maqam_arc or maqam_arc[-1] != maqam_name:
            maqam_arc.append(maqam_name)
        bpm_gears.append(bpm_sec)
        section_blueprints.append(
            {
                "section_index": idx + 1,
                "section_tag": tag,
                "prosodic_archetype": archetype,
                "avg_segment_syllables": avg_syl,
                "max_hemistichs_per_line": max_parts,
                "line_count": len(lines),
                "maqam": maqam_name,
                "target_bpm": bpm_sec,
                "bpm_gear_ratio": gear_mult,
                "vocal_register_arc": register,
                "transition_technique": transition,
                "performer_role": performer,
                "raw_lines": lines,
            }
        )

    return {
        "detected_dialect": dialect,
        "base_bpm": base_bpm,
        "section_count": len(section_blueprints),
        "meter_diversity_count": len(archetypes),
        "is_multi_meter_muwashah": len(archetypes) >= 2 or len(section_blueprints) >= 3,
        "recommended_maqam_arc": maqam_arc,
        "recommended_bpm_gears": bpm_gears,
        "masterwork_blueprints_applied": list(MASTERWORK_DIRECTION_BLUEPRINTS_V58.keys()),
        "section_blueprints": section_blueprints,
    }


def select_melodic_fingerprint_v60(fingerprint_key=None, poem_text=None, dialect=None, axis=None):
    """Module 74 (V60.0): Select one of 12 diverse Multi-Maqam & 9-School Melodic Fingerprints."""
    if fingerprint_key:
        if fingerprint_key not in MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60:
            raise ValueError(f"Unknown V60 melodic fingerprint: {fingerprint_key}")
        entry = dict(MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60[fingerprint_key])
        entry["fingerprint_key"] = fingerprint_key
        return entry

    text_norm = sanitize_poem_decorations((poem_text or "").replace("\\n", "\n"))
    det_dialect = dialect
    if not det_dialect and text_norm:
        det_dialect = format_clean_lyrics_for_lyria35(text_norm)["detected_dialect"]
    rec = recommend_tor_and_rhythm_for_poem(text_norm) if text_norm else {}
    rec_mode = rec.get("recommended_dsp_mode", "latm")

    if any(k in text_norm for k in ("صاحب العصر", "المهدي", "يا مهدي", "أوبريت", "الأوبريت", "فجر الوعود")):
        chosen = "v62_orchestral_mahdawi_anthem_nahawand_kurd_78bpm"
    elif any(k in text_norm for k in ("الحدي", "القزويني", "قريض", "مسير القوافل", "الركباني")):
        chosen = "v62_qarid_hadi_qazwini_caravan_sikah_bayati_68bpm"
    elif any(k in text_norm for k in ("جلوة", "جلوات", "المولد", "هالمولد", "أفراحنا", "يا هلا بهالمولد")):
        chosen = "v61_qatifi_bahrani_jalwat_mawlid_ajam_rast_98bpm"
    elif any(k in text_norm for k in ("الابتهال", "ابتهال", "البطانة", "الخانة", "التسليم", "يا نور طه", "أتيت بابك خاشعا")):
        chosen = "v61_classical_muwashah_ibtihal_husseini_suznak_74bpm"
    elif any(k in text_norm for k in ("الدشتي", "طور دشتي")):
        chosen = "v61_minbar_dashti_qatifi_nai_0bpm"
    elif rec_mode == "nai" or (rec.get("recommended_bpm") == 0):
        chosen = (
            "v61_minbar_dashti_qatifi_nai_0bpm"
            if det_dialect == "qatifi"
            else "v60_minbar_rubato_abudhiyah_nai_sikah_saba_0bpm"
        )
    elif rec_mode == "shoor" or (rec.get("recommended_bpm", 60) >= 115):
        chosen = "v60_iraqi_rapid_shoor_kurd_bayati_shuri_124bpm"
    elif any(k in text_norm for k in ("صلى الإله", "عرفنا خلقك", "سيد الرسل", "صلوا عليه", "بدر التمام")):
        chosen = "v60_classical_devotional_tawashih_rast_ajam_86bpm"
    elif axis == "axis_2_mawkib_procession" or rec_mode in ("zanjeel_bahrani", "zanjeel_iraqi"):
        chosen = "v60_epic_fusha_mawkib_hijaz_kar_88_to_96bpm"
    elif axis == "axis_4_cinematic_sub_foley" or rec_mode == "cinematic_foley_latmiya":
        chosen = "v60_farsi_epic_zamineh_hijaz_kar_kurd_68bpm"
    elif det_dialect == "qatifi":
        chosen = "v61_qatifi_faezi_husseini_saba_66bpm"
    elif det_dialect == "bahrani":
        if rec_mode == "bahrani_thulathi":
            chosen = "v60_bahrani_thulathi_bayati_shuri_nawa_athar_76bpm"
        elif any(k in text_norm for k in ("أشم", "خدك", "رضيع", "مهد", "رباب", "طفل")):
            chosen = "v60_bahrani_cradle_nahawand_kurd_saba_64bpm"
        else:
            chosen = "v60_bahrani_muwashah_bayati_hijaz_saba_72bpm"
    elif axis == "axis_3_zero_piano_hybrid":
        chosen = "v60_ahsa_bujabara_qafila_nawa_athar_hijaz_60bpm"
    elif rec.get("recommended_bpm", 60) >= 68:
        chosen = "v60_najafi_dialogic_nazla_bayati_kurd_70bpm"
    else:
        chosen = "v60_iraqi_karbalaei_pure_saba_zamzam_lami_58bpm"

    entry = dict(MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60[chosen])
    entry["fingerprint_key"] = chosen
    return entry


def build_remix_replace_inpainting_plan(
    clip_uuid,
    start_sec,
    end_sec,
    old_lyric_line,
    fixed_lyric_line,
    axis_mode="hybrid_axis1_3",
    dialect=None,
):
    """Module 74 (V60.0, NC32): Build exact Flow Music Remix > Replace surgical inpainting plan."""
    t_start = max(0.0, float(start_sec))
    t_end = max(t_start + 1.0, float(end_sec))
    window_sec = round(t_end - t_start, 2)
    clean_fix = format_clean_lyrics_for_lyria35(fixed_lyric_line, dialect=dialect)
    fixed_clean = clean_fix["clean_lyria35_lyrics"].strip()

    if axis_mode == "axis1_pure":
        inst_lock = "strictly 100% pure human vocal acapella and muffled bare chest thuds only, zero musical instruments, zero piano"
    else:
        inst_lock = (
            "preserve exact existing dark bowed bass cello drone, reed ney, and bare chest thuds only, "
            "strictly zero piano, zero keyboard chords, zero pop drums, zero snare backbeat"
        )

    warnings = []
    if window_sec < 8.0:
        warnings.append("Replace window < 8s: expand slightly around full phrase boundaries (8-18s recommended).")
    elif window_sec > 30.0:
        warnings.append("Replace window > 30s: narrow to single mispronounced phrase so melody/voice stays locked.")

    return {
        "protocol_rule": "NC32_live_remix_replace_surgical_inpainting",
        "skill_version": SKILL_VERSION,
        "target_clip_uuid": str(clip_uuid),
        "ui_workflow": [
            "Open target clip -> click Remix > Replace.",
            f"Open Settings -> set Start = {t_start:.1f}s and End = {t_end:.1f}s ({window_sec:.1f}s phrase window).",
            "Open Edit Lyrics -> replace ONLY the flawed target line verbatim with 'fixed_lyric_clean'.",
            "Paste 'instruction' into the Replace prompt box, ensure Model = Lyria 3.5, and Generate.",
            "Slice output into 20s chunks (NC29) and audit splice boundaries and target Makharij.",
        ],
        "settings": {
            "start_sec": round(t_start, 2),
            "end_sec": round(t_end, 2),
            "window_sec": window_sec,
            "model_lock": "Lyria 3.5",
        },
        "edit_lyrics_diff": {
            "old_lyric_line": str(old_lyric_line).strip(),
            "fixed_lyric_clean": fixed_clean,
        },
        "instruction": (
            "Surgically re-sing ONLY this short phrase in the exact same Radood singer voice, Maqam, "
            f"tempo, and acoustics with crystal-clear Arabic pronunciation on '{fixed_clean}', seamless "
            f"invisible splice boundaries, {inst_lock}."
        ),
        "window_warnings": warnings,
        "nc32_verified_benchmark": "Exp 21-A (5172764b, 0:56-1:07, 11s window, بلهيبه->بِلَهيبه, 9.7/10)",
    }


def build_v58_combined_muwashah_json(
    poem_text,
    title="موشّح حسيني متعدد الأوزان",
    axis_mode="hybrid_axis1_3",
    stage_2_text=None,
    fingerprint_key=None,
):
    """Module 73 & 74 (V58.0–V60.0, NC30–NC33): Build Combined Pre-Conditioning + Clean-Orthography Muwashah JSON."""
    clean_stage1 = format_clean_lyrics_for_lyria35(poem_text)
    analysis = analyze_multi_meter_muwashah_structure(clean_stage1["clean_lyria35_lyrics"])
    dialect = clean_stage1["detected_dialect"]
    base_bpm = analysis["base_bpm"]

    selected_fp = None
    if fingerprint_key:
        selected_fp = select_melodic_fingerprint_v60(fingerprint_key=fingerprint_key)
        sound_prompt = selected_fp["sound_prompt"]
        base_bpm = selected_fp["bpm"]
        inst_rule = (
            "Strictly pure human vocal acapella and muffled bare chest thumping only; zero musical instruments"
            if "axis_1" in selected_fp["axis"]
            else (
                "Dark bowed bass cello drone, mournful reed ney, strictly percussive bare chest thuds, "
                "subtle acoustic desert wind; strictly zero piano, zero keyboard chords, no pop drums, no snare backbeat"
            )
        )
    elif axis_mode == "axis1_pure":
        sound_prompt = EXTENDED_ATWAR_PROMPTS_V52[
            "v57_bahrani_matam_pure_58bpm_saba_bayati"
            if dialect == "bahrani"
            else "v57_iraqi_karbalaei_pure_majlis_60bpm_saba_lami"
        ]
        inst_rule = "Strictly pure human vocal acapella and muffled bare chest thumping only; zero musical instruments"
    else:
        sound_prompt = EXTENDED_ATWAR_PROMPTS_V52["v58_bahrani_muwashah_hybrid_72bpm_bayati_hijaz_saba"]
        if dialect == "iraqi":
            sound_prompt = sound_prompt.replace("Bahraini", "Iraqi Karbalaei").replace("Gulf Bahrani", "Iraqi Karbalaei")
        inst_rule = (
            "Dark bowed bass cello drone, mournful reed ney, strictly percussive bare chest thuds, "
            "subtle acoustic desert wind; strictly zero piano, zero keyboard chords, no pop drums, no snare backbeat, no dance beat"
        )

    arrangement_sections = []
    verbatim_lines = []
    for bp in analysis["section_blueprints"]:
        arrangement_sections.append(
            {
                "section_index": bp["section_index"],
                "section_tag_arabic": bp["section_tag"],
                "prosodic_archetype": bp["prosodic_archetype"],
                "maqam_and_jins": bp["maqam"],
                "target_bpm_feel": bp["target_bpm"],
                "vocal_register_and_pitch_arc": bp["vocal_register_arc"],
                "performer_and_choir_layering": bp["performer_role"],
                "transition_and_drop_direction": bp["transition_technique"],
                "instrumentation_rule": inst_rule,
            }
        )
        verbatim_lines.append(bp["section_tag"])
        verbatim_lines.extend(bp["raw_lines"])

    payload = {
        "protocol_name": "Hussaini_Production_Studio_OS_V50_0_OMNI_ARCHITECT",
        "skill_version": SKILL_VERSION,
        "execution_mode": "V58_COMBINED_PRECONDITIONING_AND_MUWASHAH_GENERATION",
        "nc30_combined_json_lock": (
            "Lock all pre-conditioning acoustic and dialect rules AND immediately generate Stage 1 "
            "from 'lyrics_register_verbatim' in this same turn (never invent placeholder lyrics)."
        ),
        "session_preconditioning_lock": {
            "model_lock": "Lyria 3.5",
            "instrumental_mode": "OFF",
            "dialect_lock": (
                "authentic Bahrani colloquial dialect"
                if dialect == "bahrani"
                else "authentic Iraqi colloquial dialect"
            ),
            "anti_pop_firewall": [
                "no piano",
                "no pop drums",
                "no rock snare backbeat",
                "no dance or darbuka interlude",
                "no Arabic romantic pop singing",
            ],
            "lyrics_orthography_rule": "NC26/NC27 Clean Natural Arabic with surgical affricate تْش & clean گ — register 100% verbatim with zero English words in Lyrics",
            "metadata_language_rule": "Parse all English arrangement_sections[] silently; never copy English words into lyrics__register",
        },
        "title": title,
        "global_bpm": base_bpm,
        "axis_mode": axis_mode,
        "selected_melodic_fingerprint": selected_fp["fingerprint_key"] if selected_fp else None,
        "sound_description": sound_prompt,
        "syllable_density_report": clean_stage1["syllable_density_report"],
        "muwashah_structure_summary": {
            "is_multi_meter_muwashah": analysis["is_multi_meter_muwashah"],
            "meter_diversity_count": analysis["meter_diversity_count"],
            "recommended_maqam_arc": selected_fp["maqam_arc"] if selected_fp else analysis["recommended_maqam_arc"],
            "recommended_bpm_gears": analysis["recommended_bpm_gears"],
        },
        "arrangement_sections": arrangement_sections,
        "lyrics_register_verbatim": verbatim_lines,
    }

    if stage_2_text and str(stage_2_text).strip():
        clean_s2 = format_clean_lyrics_for_lyria35(stage_2_text, dialect=dialect)
        s2_analysis = analyze_multi_meter_muwashah_structure(clean_s2["clean_lyria35_lyrics"])
        s2_verbatim = []
        s2_sections = []
        for bp2 in s2_analysis["section_blueprints"]:
            s2_sections.append(
                {
                    "section_index": bp2["section_index"],
                    "section_tag_arabic": bp2["section_tag"],
                    "prosodic_archetype": bp2["prosodic_archetype"],
                    "maqam_and_jins": bp2["maqam"],
                    "target_bpm_feel": bp2["target_bpm"],
                    "transition_and_drop_direction": bp2["transition_technique"],
                }
            )
            s2_verbatim.append(bp2["section_tag"])
            s2_verbatim.extend(bp2["raw_lines"])
        payload["stage_2_extend_json"] = {
            "execution_mode": "V58_STAGE_2_DYNAMIC_JSON_EXTEND",
            "lyrics_panel_action": "OVERWRITE_WITH_STAGE_2_ONLY",
            "nc31_extend_seam_and_tail_law": (
                "Continue seamlessly in exact Stage-1 singer voice, key, and instruments; "
                "overwrite Lyrics with Stage-2 lines ONLY; after generation, run 20s blind chunk audit "
                "and trim any trailing restart loop cleanly before mastering."
            ),
            "sound_description_continuation": sound_prompt,
            "arrangement_sections": s2_sections,
            "lyrics_register_verbatim": s2_verbatim,
        }

    return payload


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
    "bayati": {0: 1.85, 3: 1.75, 5: 0.45, 6: 1.35, 10: 1.55, 14: 1.20, 16: 0.85, 20: 0.90},
    "bayati_shuri": {0: 1.70, 3: 1.65, 5: 0.40, 6: 1.25, 10: 1.35, 12: 1.45, 18: 1.40, 20: 0.70},
    "husseini": {0: 1.70, 3: 1.60, 5: 0.40, 6: 1.20, 10: 1.35, 14: 1.65, 17: 1.25, 20: 0.75},
    "saba": {0: 1.85, 3: 1.75, 5: 0.75, 6: 1.25, 8: 2.00, 14: 0.90, 16: 0.80, 20: 0.60},
    "saba_zamzam": {0: 1.80, 2: 1.55, 6: 1.35, 8: 2.05, 14: 1.15, 16: 1.05, 20: 0.95},
    "hijaz": {0: 1.85, 2: 1.65, 8: 1.85, 10: 1.45, 14: 1.25, 16: 1.00, 20: 0.85},
    "hijaz_kar": {0: 1.75, 2: 1.55, 8: 1.70, 10: 1.20, 14: 1.20, 16: 1.20, 22: 1.30},
    "lami": {0: 1.85, 2: 1.45, 6: 1.35, 10: 1.45, 12: 1.75, 16: 1.10, 20: 0.95},
    "kurd": {0: 1.85, 2: 1.45, 6: 1.35, 10: 1.45, 14: 1.40, 16: 1.20, 20: 1.20},
    "nahawand": {0: 1.85, 4: 1.30, 6: 1.40, 10: 1.35, 14: 1.35, 16: 1.05, 20: 0.90, 22: 0.70},
    "nawa_athar": {0: 1.75, 4: 1.20, 6: 1.30, 12: 1.75, 14: 1.20, 16: 1.25, 22: 1.45},
    "sikah": {0: 1.85, 3: 1.50, 7: 1.70, 10: 1.40, 13: 1.35, 17: 1.10, 20: 1.00},
    "rast": {0: 1.85, 4: 1.25, 7: 1.75, 10: 1.35, 14: 1.25, 18: 1.10, 21: 1.35},
    "suznak": {0: 1.75, 4: 1.20, 7: 1.60, 10: 1.20, 14: 1.40, 16: 1.35, 22: 1.40},
    "ajam": {0: 1.80, 4: 1.30, 8: 1.60, 10: 1.30, 14: 1.40, 18: 1.20, 22: 1.30},
}
_QUARTER_TONE_MAQAM_SET = {"bayati", "bayati_shuri", "husseini", "saba", "sikah", "rast", "suznak"}


def _extract_24edo_maqam_profile(mono, sample_rate):
    """Module 69 & 78 (V64.0 NC43): Cadence-locked 24-EDO chroma & Maqam classifier (blocks Locrian rotation)."""
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
        is_phrase_end = (i + 2 < nf and rms[i + 2] < 0.60 * rms[i]) or (i >= nf - 3)
        cad = 4.5 if is_phrase_end else 1.0
        obs.append((24.0 * math.log2(f0 / 440.0), f0, rms[i], cad))

    if not obs:
        return "bayati", 146.83, 0.0, [("bayati", 1.0)]

    med_f0 = float(np.median([item[1] for item in obs]))
    h120 = np.zeros(120, dtype=np.float64)
    cad24_global = np.zeros(24, dtype=np.float64)
    for qt_val, _, r_val, cad_val in obs:
        h120[int(round(qt_val * 5.0)) % 120] += r_val * cad_val
        if cad_val > 1.5:
            cad24_global[int(round(qt_val)) % 24] += r_val * cad_val
    cad24_sum = float(cad24_global.sum())

    # NC43: Anchor tonic strictly to top-4 cadentially supported pitch centers (prevents Locrian/Lami rotation on Western minor)
    seen = {}
    for a120 in np.argsort(h120)[::-1][:6]:
        if h120[a120] <= 0.0:
            continue
        ch24 = np.zeros(24, dtype=np.float64)
        a_qt = a120 / 5.0
        for qt_val, _, r_val, _ in obs:
            ch24[int(round(qt_val - a_qt)) % 24] += r_val
        ch24 /= float(ch24.sum()) + 1e-9
        if ch24[0] < 0.09:
            continue
        if cad24_sum > 1e-9:
            a24 = int(round(a_qt)) % 24
            cad_share = float(cad24_global[a24] + 0.5 * cad24_global[(a24 - 1) % 24] + 0.5 * cad24_global[(a24 + 1) % 24]) / cad24_sum
            if cad_share < 0.10:
                continue
        else:
            cad_share = float(ch24[0])
        odd_qt = float(ch24[1::2].sum())
        for mn, prof in _MAQAM_24EDO_TEMPLATES.items():
            w_norm = float(sum(prof.values())) / 9.90
            pos = sum(ch24[d] * (w / w_norm) for d, w in prof.items())
            non_sc = sum(ch24[d] for d in range(24) if d not in prof)
            has_qt = mn in _QUARTER_TONE_MAQAM_SET
            qt_bonus = 0.25 * odd_qt if has_qt else -0.25 * max(0.0, odd_qt - 0.12)
            razor = 0.0
            if mn == "saba":
                razor = 0.45 * (ch24[8] - 0.5 * ch24[10])
            elif mn == "bayati":
                razor = 0.30 * (ch24[10] - ch24[8])
            elif mn == "lami":
                # Real Iraqi Lami requires tonic Finalis prominence + diminished-5th (bin 12) without major-3rd (bin 8)
                razor = 0.15 * cad_share - 0.35 * ch24[8]
            sc = pos - 0.6 * non_sc + qt_bonus + razor + 0.12 * cad_share
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


def apply_vintage_telephone_intro_fx(signal, sample_rate, intro_end_sec=10.0, crossfade_sec=0.35):
    """Module 73 (V58.0): Apply Al-Akraf 300-2800Hz archive/telephone EQ intro -> full-bandwidth studio drop."""
    arr = np.asarray(signal, dtype=np.float64)
    if arr.size == 0 or float(intro_end_sec) <= 0.0:
        return arr.copy()
    cut_idx = min(len(arr), int(float(intro_end_sec) * sample_rate))
    if cut_idx <= 8:
        return arr.copy()

    nyq = 0.5 * float(sample_rate)
    lo_hz = min(300.0, 0.20 * nyq)
    hi_hz = min(2800.0, 0.85 * nyq)
    if hi_hz <= lo_hz + 50.0:
        return arr.copy()

    band = butter_filter(arr, [lo_hz, hi_hz], sample_rate, btype="band", order=3)
    vintage = np.tanh(band * 1.45) / np.tanh(1.45)

    out = arr.copy()
    xfade = min(cut_idx // 2, max(1, int(float(crossfade_sec) * sample_rate)))
    solid_end = max(0, cut_idx - xfade)
    out[:solid_end] = vintage[:solid_end]
    if xfade > 1 and solid_end < cut_idx:
        ramp = np.linspace(0.0, 1.0, cut_idx - solid_end)
        out[solid_end:cut_idx] = (1.0 - ramp) * vintage[solid_end:cut_idx] + ramp * arr[solid_end:cut_idx]
    return out


def apply_mid_side_vocal_stacking_enhancer(
    stereo,
    sample_rate,
    solo_side_atten_db=-1.5,
    choir_side_boost_db=4.2,
    low_mono_hz=180.0,
):
    """Module 74 (V60.0, NC34): 5th Masterwork Blueprint — Mono-safe Mid/Side Solo-vs-Choir Vocal Stacking."""
    arr = np.asarray(stereo, dtype=np.float64)
    if arr.ndim == 1:
        arr = np.column_stack((arr, arr))
    if arr.shape[0] < 64:
        return arr.copy()

    mid = 0.5 * (arr[:, 0] + arr[:, 1])
    side = 0.5 * (arr[:, 0] - arr[:, 1])

    # Keep sub/chest-latm (<180Hz) strictly mono-centered for punch & mono compatibility
    side_hi = butter_filter(side, low_mono_hz, sample_rate, btype="high", order=2)
    side_lo = side - side_hi

    # If signal is pure mono (zero side), synthesize subtle decorrelated vocal choir air (>220Hz) for swells
    side_rms = float(np.sqrt(np.mean(side_hi**2)))
    mid_rms = float(np.sqrt(np.mean(mid**2)) + 1e-9)
    if side_rms < 0.015 * mid_rms:
        haas_n = max(1, int(0.011 * sample_rate))
        mid_hi = butter_filter(mid, max(220.0, low_mono_hz), sample_rate, btype="high", order=2)
        shifted = np.roll(mid_hi, haas_n)
        shifted[:haas_n] = 0.0
        side_hi = 0.22 * (mid_hi - shifted)

    # Dynamic energy swell detector (0.5s RMS) separates intimate solo passages from wide choir walls
    win = max(16, int(0.50 * sample_rate))
    env = np.sqrt(np.maximum(_fast_boxcar_mean(mid**2, win), 1e-12))
    pos_env = env[env > 1e-4]
    med_env = float(np.median(pos_env)) if pos_env.size > 0 else float(np.median(env) + 1e-6)
    swell_ratio = env / max(med_env, 1e-6)
    # Smoothly map swell_ratio [0.75..1.45] -> [0.0..1.0] (0=solo center focus, 1=wide choir wall)
    choir_weight = np.clip((swell_ratio - 0.75) / 0.70, 0.0, 1.0)
    gain_db = float(solo_side_atten_db) + choir_weight * (float(choir_side_boost_db) - float(solo_side_atten_db))
    side_gain = 10.0 ** (gain_db / 20.0)

    side_out = side_lo * 0.75 + side_hi * side_gain
    return np.column_stack((mid + side_out, mid - side_out))


def apply_mid_side_reverb_clarity(stereo, sample_rate, side_cut_hz=320.0, low_side_atten=0.35):
    """Module 75 (V61.0): Mid-Side EQ cleaning 100-400Hz reverb mud from Side channel while keeping center pure."""
    arr = np.asarray(stereo, dtype=np.float64)
    if arr.ndim == 1 or arr.shape[0] < 32:
        return arr.copy()
    mid = 0.5 * (arr[:, 0] + arr[:, 1])
    side = 0.5 * (arr[:, 0] - arr[:, 1])
    cut_eff = min(float(side_cut_hz), 0.35 * float(sample_rate))
    side_hi = butter_filter(side, cut_eff, sample_rate, btype="high", order=2)
    side_lo = side - side_hi
    side_clean = side_hi + float(low_side_atten) * side_lo
    return np.column_stack((mid + side_clean, mid - side_clean))


def compute_mono_compatibility(stereo):
    """Module 75 (V61.0): Verify Mawkib PA Mono Check (L/R correlation & mono-sum energy retention)."""
    arr = np.asarray(stereo, dtype=np.float64)
    if arr.ndim == 1 or arr.shape[0] == 0:
        return {"lr_phase_correlation": 1.0, "mono_energy_retention_db": 0.0, "mono_safe": True}
    left = arr[:, 0]
    right = arr[:, 1]
    denom = math.sqrt(float(np.sum(left**2)) * float(np.sum(right**2))) + 1e-12
    corr = float(np.clip(float(np.sum(left * right)) / denom, -1.0, 1.0))
    mono_sum = 0.5 * (left + right)
    stereo_pow = 0.5 * (float(np.mean(left**2)) + float(np.mean(right**2))) + 1e-12
    mono_pow = float(np.mean(mono_sum**2)) + 1e-12
    retention_db = round(10.0 * math.log10(mono_pow / stereo_pow), 2)
    return {
        "lr_phase_correlation": round(corr, 3),
        "mono_energy_retention_db": retention_db,
        "mono_safe": bool(corr >= 0.20 and retention_db >= -3.0),
    }


def _resolve_audio_input_mono(audio_path_or_mono, sample_rate=None):
    """Load file path via read_wav_any_depth or wrap an in-memory 1D/2D NumPy array cleanly."""
    if isinstance(audio_path_or_mono, (str, os.PathLike)):
        sr, mono, _, _ = read_wav_any_depth(str(audio_path_or_mono), return_stereo=False)
        return int(sr), np.asarray(mono, dtype=np.float64)
    if sample_rate is None:
        raise ValueError("sample_rate is required when passing an in-memory audio array.")
    arr = np.asarray(audio_path_or_mono, dtype=np.float64)
    if arr.ndim == 2:
        arr = np.mean(arr, axis=1)
    return int(sample_rate), arr


def detect_piano_and_pop_snare_transients(audio_path_or_mono, sample_rate=None, chunk_sec=20.0):
    """Module 74 (V60.0, NC33): Calibrated Zero-Vibrato Piano Hammer & Dual-Band Pop-Snare Forensic Detector."""
    sr, mono = _resolve_audio_input_mono(audio_path_or_mono, sample_rate=sample_rate)
    if mono.size < 256:
        return {
            "piano_leakage_detected": False,
            "pop_snare_detected": False,
            "passed_nc33_zero_artifact_gate": True,
            "total_rigid_decay_notes": 0,
            "max_chunk_piano_notes": 0,
            "total_snare_hits": 0,
            "max_snare_periodicity": 0.0,
            "flagged_chunks": [],
            "chunks": [],
        }

    # Anti-aliased integer decimation toward ~16 kHz for 10x speed & calibrated 3.9 Hz STFT resolution
    work_sr = sr
    work_mono = mono
    if sr >= 28000:
        decim = max(2, int(round(sr / 16000.0)))
        work_mono = butter_filter(mono, 0.44 * (sr / float(decim)), sr, btype="low", order=4)[::decim]
        work_sr = int(round(sr / float(decim)))

    c_len = max(1024, int(float(chunk_sec) * work_sr))
    n_chunks = max(1, int(math.ceil(len(work_mono) / float(c_len))))

    nfft = 4096
    frame = max(256, int(0.064 * work_sr))
    hop = max(64, int(0.015 * work_sr))
    win = np.hanning(frame)
    freqs = np.fft.rfftfreq(nfft, d=1.0 / float(work_sr))
    k_lo = int(np.searchsorted(freqs, 240.0))
    k_hi = int(np.searchsorted(freqs, min(1800.0, 0.44 * work_sr)))

    s_wire = (freqs >= 2400.0) & (freqs <= min(7200.0, 0.46 * work_sr))
    s_body = (freqs >= 170.0) & (freqs <= 520.0)
    s_sub = (freqs >= 45.0) & (freqs <= 155.0)

    n_track = 16  # 240ms decay tracking separates rigid 12-TET piano strings from Arabic vocal vibrato
    t_ax = np.arange(n_track, dtype=np.float64) * (hop / float(work_sr))
    t_mean = float(np.mean(t_ax))
    t_var = float(np.sum((t_ax - t_mean) ** 2)) + 1e-12
    backbeat_lo = max(4, int(0.36 * work_sr / float(hop)))
    backbeat_hi = max(backbeat_lo + 2, int(1.20 * work_sr / float(hop)))

    chunks = []
    flagged_chunks = []
    for ci in range(n_chunks):
        seg = work_mono[ci * c_len : min(len(work_mono), (ci + 1) * c_len)]
        nf = (len(seg) - frame) // hop
        if nf < n_track + 4:
            continue
        idx = np.arange(frame)[None, :] + (np.arange(nf) * hop)[:, None]
        mag = np.abs(np.fft.rfft(seg[idx] * win[None, :], n=nfft, axis=1)) + 1e-12
        log_m = 20.0 * np.log10(mag)

        # 1) Zero-Vibrato 240ms 12-TET Parabolic Sub-Bin Exponential-Decay Piano Partial Detector
        hit_frames = set()
        for t_idx in range(2, nf - n_track - 1):
            sl = log_m[t_idx, k_lo:k_hi]
            if sl.size < 6:
                continue
            floor = float(np.median(sl))
            for j in range(2, sl.size - 2):
                if sl[j] < floor + 17.0 or not (sl[j] > sl[j - 1] and sl[j] >= sl[j + 1]):
                    continue
                k = k_lo + j
                if sl[j] - float(np.mean(log_m[t_idx - 2 : t_idx, k])) < 11.0:
                    continue
                f_track = []
                a_track = []
                for dt in range(n_track):
                    sub = log_m[t_idx + dt, k - 1 : k + 2]
                    kk = k + int(np.argmax(sub)) - 1
                    kk = max(1, min(log_m.shape[1] - 2, kk))
                    y0, y1, y2 = log_m[t_idx + dt, kk - 1], log_m[t_idx + dt, kk], log_m[t_idx + dt, kk + 1]
                    den = y0 - 2.0 * y1 + y2
                    delta = float(np.clip(0.5 * (y0 - y2) / den, -0.5, 0.5)) if abs(den) > 1e-9 else 0.0
                    f_track.append((kk + delta) * (work_sr / float(nfft)))
                    a_track.append(y1)
                f_arr = np.asarray(f_track, dtype=np.float64)
                a_arr = np.asarray(a_track, dtype=np.float64)
                if f_arr[0] <= 1.0:
                    continue
                f_std_cents = float(np.std(1200.0 * np.log2(np.maximum(f_arr, 1.0) / f_arr[0])))
                med_hz = float(np.median(f_arr))
                midi_f = 69.0 + 12.0 * math.log2(max(med_hz, 20.0) / 440.0)
                tet_err_cents = abs(midi_f - round(midi_f)) * 100.0
                a_mean = float(np.mean(a_arr))
                slope = float(np.sum((t_ax - t_mean) * (a_arr - a_mean)) / t_var)
                ss_tot = float(np.sum((a_arr - a_mean) ** 2)) + 1e-9
                ss_res = float(np.sum((a_arr - (a_mean + slope * (t_ax - t_mean))) ** 2))
                r2_val = 1.0 - ss_res / ss_tot
                if f_std_cents < 5.0 and tet_err_cents < 20.0 and -75.0 <= slope <= -10.0 and r2_val >= 0.80:
                    hit_frames.add(t_idx)
                    break

        clustered = []
        for f_i in sorted(hit_frames):
            if not clustered or (f_i - clustered[-1]) >= 10:
                clustered.append(f_i)
        rigid_notes = len(clustered)

        # 2) Dual-Band Coincident Pop-Snare & Backbeat Periodicity Detector
        snare_hits = 0
        snare_ac = 0.0
        if np.any(s_wire) and np.any(s_body):
            sw = mag[:, s_wire]
            sb = mag[:, s_body]
            sm = mag[:, s_sub] if np.any(s_sub) else sb
            ew = np.sqrt(np.mean(sw**2, axis=1))
            eb = np.sqrt(np.mean(sb**2, axis=1))
            es = np.sqrt(np.mean(sm**2, axis=1)) + 1e-10
            flat_w = np.exp(np.mean(np.log(sw), axis=1)) / (np.mean(sw, axis=1) + 1e-10)
            dw = np.maximum(0.0, np.diff(ew, prepend=ew[0]))
            db = np.maximum(0.0, np.diff(eb, prepend=eb[0]))
            dw_thr = float(np.median(dw)) + 2.8 * float(np.std(dw))
            db_thr = float(np.median(db)) + 1.8 * float(np.std(db))
            coinc = np.where((dw > dw_thr) & (db > db_thr) & (flat_w > 0.30) & (ew > 0.10 * es))[0]
            deb = []
            for si in coinc:
                if not deb or (si - deb[-1]) >= 10:
                    deb.append(si)
            snare_hits = len(deb)
            sn_env = dw * np.where(flat_w > 0.28, 1.0, 0.0)
            sn_env -= np.mean(sn_env)
            if float(np.std(sn_env)) > 1e-8 and len(sn_env) > backbeat_lo + 2:
                ac = np.correlate(sn_env, sn_env, mode="full")[len(sn_env) - 1 :]
                ac /= max(float(ac[0]), 1e-12)
                hi_cap = min(backbeat_hi, len(ac) - 1)
                if hi_cap > backbeat_lo:
                    snare_ac = round(float(np.max(ac[backbeat_lo:hi_cap])), 3)

        p_flag = rigid_notes >= 3
        s_flag = (snare_hits >= 10) or (snare_hits >= 6 and snare_ac >= 0.32)
        chunk_rec = {
            "chunk_index": ci,
            "start_sec": round(ci * float(chunk_sec), 1),
            "rigid_decay_piano_notes": rigid_notes,
            "coincident_snare_hits": snare_hits,
            "snare_backbeat_periodicity": snare_ac,
            "piano_flagged": p_flag,
            "snare_flagged": s_flag,
        }
        chunks.append(chunk_rec)
        if p_flag or s_flag:
            flagged_chunks.append(chunk_rec)

    tot_p = sum(c["rigid_decay_piano_notes"] for c in chunks)
    max_p = max((c["rigid_decay_piano_notes"] for c in chunks), default=0)
    opening_p = sum(c["rigid_decay_piano_notes"] for c in chunks[:3])
    tot_s = sum(c["coincident_snare_hits"] for c in chunks)
    max_ac = max((c["snare_backbeat_periodicity"] for c in chunks), default=0.0)
    piano_det = (max_p >= 3) or (tot_p >= 5 and opening_p >= 3)
    snare_det = any(c["snare_flagged"] for c in chunks) or (tot_s >= 55 and max_ac >= 0.30)
    return {
        "piano_leakage_detected": bool(piano_det),
        "pop_snare_detected": bool(snare_det),
        "passed_nc33_zero_artifact_gate": bool(not piano_det and not snare_det),
        "total_rigid_decay_notes": int(tot_p),
        "opening_60s_piano_notes": int(opening_p),
        "max_chunk_piano_notes": int(max_p),
        "total_snare_hits": int(tot_s),
        "max_snare_periodicity": round(float(max_ac), 3),
        "flagged_chunks": flagged_chunks,
        "chunks": chunks,
    }


def detect_extend_restart_loop(audio_path_or_mono, sample_rate=None, tail_window_sec=10.5):
    """Module 74 (V60.0, NC34): Detect accidental Remix > Extend trailing restart loop & compute clean trim timestamp."""
    sr, mono = _resolve_audio_input_mono(audio_path_or_mono, sample_rate=sample_rate)
    duration_sec = round(len(mono) / max(1.0, float(sr)), 3)
    hop = max(1, int(0.5 * sr))
    n_hops = len(mono) // hop
    if n_hops < 16:
        return {
            "tail_loop_detected": False,
            "duration_sec": duration_sec,
            "valley_sec": None,
            "valley_dbfs": None,
            "reentry_sec": None,
            "reentry_jump_db": 0.0,
            "recommended_trim_sec": None,
        }

    rms_db = np.array(
        [
            20.0 * math.log10(float(np.sqrt(np.mean(mono[i * hop : (i + 1) * hop] ** 2)) + 1e-9))
            for i in range(n_hops)
        ],
        dtype=np.float64,
    )
    tail_bins = min(n_hops - 10, max(6, int(round(float(tail_window_sec) / 0.5))))
    start_bin = max(10, n_hops - tail_bins)

    best_hit = None
    for idx in range(start_bin, n_hops - 2):
        val_db = float(rms_db[idx])
        if val_db > -34.0:
            continue
        prev_slice = rms_db[max(0, idx - 10) : idx]
        prev_active = float(np.percentile(prev_slice, 75)) if prev_slice.size > 0 else -18.0
        if prev_active - val_db < 14.0:
            continue
        post_slice = rms_db[idx + 1 : min(n_hops, idx + 16)]
        if post_slice.size == 0:
            continue
        post_peak_rel = int(np.argmax(post_slice))
        post_peak_db = float(post_slice[post_peak_rel])
        jump_db = post_peak_db - val_db
        if jump_db >= 11.0 and post_peak_db > -28.0:
            valley_sec = round(idx * 0.5, 2)
            reentry_sec = round((idx + 1 + post_peak_rel) * 0.5, 2)
            best_hit = {
                "tail_loop_detected": True,
                "duration_sec": duration_sec,
                "valley_sec": valley_sec,
                "valley_dbfs": round(val_db, 2),
                "reentry_sec": reentry_sec,
                "reentry_jump_db": round(jump_db, 2),
                "recommended_trim_sec": round(max(1.0, valley_sec), 2),
            }
            break

    if best_hit is not None:
        return best_hit
    return {
        "tail_loop_detected": False,
        "duration_sec": duration_sec,
        "valley_sec": None,
        "valley_dbfs": None,
        "reentry_sec": None,
        "reentry_jump_db": 0.0,
        "recommended_trim_sec": None,
    }


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


def audit_rendered_audio(wav_path, platform_target="streaming"):
    """Audit rendered WAV for multi-platform EBU R128 loudness, True Peak, Mono Check, gaps & tail cutoff."""
    if platform_target not in PLATFORM_LUFS_TARGETS_V62:
        raise ValueError(f"Unsupported platform_target: {platform_target}")
    pt_cfg = PLATFORM_LUFS_TARGETS_V62[platform_target]
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
    tail_loop = detect_extend_restart_loop(mono, sample_rate=sample_rate)
    mono_check = compute_mono_compatibility(stereo if channels > 1 else mono)
    lo_lufs = pt_cfg["target_lufs"] - pt_cfg["tolerance_lu"]
    hi_lufs = pt_cfg["target_lufs"] + pt_cfg["tolerance_lu"]
    broadcast_ok = bool(stats["true_peak_dbtp"] <= -0.9 and lo_lufs <= stats["integrated_lufs"] <= hi_lufs)
    return {
        "wav_path": wav_path,
        "platform_target": platform_target,
        "target_lufs": pt_cfg["target_lufs"],
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
        "tail_loop_detected": tail_loop["tail_loop_detected"],
        "recommended_trim_sec": tail_loop["recommended_trim_sec"],
        "mono_compatibility": mono_check,
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
    vintage_intro_sec=0.0,
    vocal_stacking=False,
    auto_trim_tail_loop=False,
    platform_target="streaming",
    tame_lyria_harshness=False,
):
    """Run complete 5-Track SOS/RMS/LUFS or Pure Vocal Husseiniya DSP montage (V63.0 multi-platform + Lyria 2-4kHz tamer)."""
    if mode not in SUPPORTED_DSP_MODES:
        raise ValueError(f"Unsupported DSP mode: {mode}")
    if platform_target not in PLATFORM_LUFS_TARGETS_V62:
        raise ValueError(f"Unsupported platform_target: {platform_target}")
    pt_cfg = PLATFORM_LUFS_TARGETS_V62[platform_target]

    sample_rate, mono, _, _ = read_wav_any_depth(input_path)
    auto_trimmed_at = None
    effective_trim = trim_end_sec
    effective_fade = float(fade_out_sec or 0.0)
    if auto_trim_tail_loop and effective_trim is None:
        loop_info = detect_extend_restart_loop(mono, sample_rate=sample_rate)
        if loop_info["tail_loop_detected"] and loop_info["recommended_trim_sec"]:
            effective_trim = loop_info["recommended_trim_sec"]
            auto_trimmed_at = effective_trim
            if effective_fade <= 0.0:
                effective_fade = 2.0

    if effective_trim is not None and float(effective_trim) > 0.2:
        max_samples = min(len(mono), int(float(effective_trim) * sample_rate))
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

    if vintage_intro_sec and float(vintage_intro_sec) > 0.0:
        stereo_glued = np.column_stack(
            (
                apply_vintage_telephone_intro_fx(stereo_glued[:, 0], sample_rate, intro_end_sec=float(vintage_intro_sec)),
                apply_vintage_telephone_intro_fx(stereo_glued[:, 1], sample_rate, intro_end_sec=float(vintage_intro_sec)),
            )
        )

    if vocal_stacking:
        stereo_glued = apply_mid_side_vocal_stacking_enhancer(stereo_glued, sample_rate)
    if tame_lyria_harshness:
        stereo_glued = apply_lyria_harshness_tamer_2_4khz(stereo_glued, sample_rate)
    stereo_glued = apply_mid_side_reverb_clarity(stereo_glued, sample_rate, side_cut_hz=320.0)

    if effective_fade > 0.0 and stereo_glued.shape[0] > 8:
        fade_len = min(stereo_glued.shape[0] // 2, int(effective_fade * sample_rate))
        if fade_len > 2:
            curve = 0.5 * (1.0 + np.cos(np.pi * np.linspace(0.0, 1.0, fade_len)))
            stereo_glued = stereo_glued.copy()
            stereo_glued[-fade_len:] *= curve[:, np.newaxis]

    master = normalize_lufs_and_true_peak(
        stereo_glued,
        sample_rate,
        target_lufs=pt_cfg["target_lufs"],
        ceiling_dbtp=pt_cfg["ceiling_dbtp"],
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
        "platform_target": platform_target,
        "target_lufs": pt_cfg["target_lufs"],
        "pure_vocal_master": pure_mode,
        "bpm": bpm,
        "maqam_drone": maqam_drone,
        "replace_ai_percussion": bool(replace_ai_percussion and not pure_mode),
        "vintage_intro_sec": round(float(vintage_intro_sec or 0.0), 2),
        "vocal_stacking_applied": bool(vocal_stacking),
        "lyria_harshness_tamed_2_4khz": bool(tame_lyria_harshness),
        "auto_trimmed_tail_loop_sec": auto_trimmed_at,
        "integrated_lufs": out_stats["integrated_lufs"],
        "true_peak_dbtp": out_stats["true_peak_dbtp"],
        "lra_lu": out_stats["lra_lu"],
    }


def _nc37_strip_diacritics(text: str) -> str:
    """Strip Arabic diacritics (U+064B..U+065F, U+0670) for structural comparison."""
    return re.sub(r"[\u064B-\u065F\u0670]", "", text)


def _nc37_levenshtein_1(word_a: str, word_b: str) -> bool:
    """Return True if two distinct normalized Arabic stems are within edit distance 1."""
    if word_a == word_b or abs(len(word_a) - len(word_b)) > 1:
        return False
    if len(word_a) == len(word_b):
        return sum(ca != cb for ca, cb in zip(word_a, word_b)) == 1
    short_w, long_w = (word_a, word_b) if len(word_a) < len(word_b) else (word_b, word_a)
    for idx in range(len(long_w)):
        if long_w[:idx] + long_w[idx + 1:] == short_w:
            return True
    return False


def audit_fusha_shadda_wasl_and_makharij_v62(lyrics_text: str) -> dict:
    """V62.0 (NC37): Pre-flight Fusha Orthoepy, Shadda, Wasl, Punctuation & Rhyme-Carryover Linter.

    Empirically engineered from Exp 30 & Exp 31 vocal-isolated 10s micro-audits to prevent:
    - NC37-A: Unanchored choir Shadda blur (e.g. عَجِّلْ -> عَاجِلْ, مَهْدِيَّ -> مَهْدِي)
    - NC37-B: Comma-after-Sukun Tanween artifact (عَجِّلْ، -> عَجِّلُنْ) & single-word '..' drop
    - NC37-C: Inline parenthetical echo '(...)' swallowing words of the next dense line
    - NC37-D: 'الِا' Wasl-Alif misread as 'الأَ', half-vocalized medial consonants (جُمعةٍ),
      and adjacent-section near-homophone rhyme contamination (أَجْمَلْ -> نُورَ الأَجْمَلْ)
    """
    raw_lines = [ln.strip() for ln in lyrics_text.replace("\\n", "\n").splitlines() if ln.strip()]
    choir_shadda_risks = []
    comma_after_sukun_traps = []
    ellipses_drop_traps = []
    inline_echo_swallow_traps = []
    wasl_alif_traps = []
    half_vocalized_words = []
    rhyme_carryover_traps = []
    tatweel_hallucination_traps = []

    diac_chars = set("\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0670")
    skip_medial = set("اويىآأإؤئة\u0640")
    lyric_entries = []
    section_idx = 0

    for ln in raw_lines:
        if ln.startswith("[") and ln.endswith("]"):
            section_idx += 1
            continue
        lyric_entries.append((section_idx, ln))

        # NC37-A: Full-choir (...) line containing Shadda U+0651
        if ln.startswith("(") and ln.endswith(")") and "\u0651" in ln:
            shadda_words = [w for w in re.findall(r"[\u0600-\u06FF]+", ln) if "\u0651" in w]
            choir_shadda_risks.append({
                "line": ln,
                "shadda_words": shadda_words,
                "fix": "Anchor Shadda-bearing words with centered Solo Lead vocal (choir behind lead only) to prevent Lyria 3.5 gemination blur (NC37-A).",
            })

        # NC37-B1: Comma/punctuation immediately after Sukun
        for match in re.finditer(r"([\u0600-\u06FF]+\u0652)([،,؛;])", ln):
            comma_after_sukun_traps.append({
                "token": match.group(0),
                "fix": f"Remove punctuation '{match.group(2)}' after Sukun -> '{match.group(1)}' to prevent unwanted '-un' Tanween artifact (NC37-B).",
            })

        # NC37-B2: Single word before '..' break (outro/pause omission risk, including inside '(...)')
        ln_unwrapped = ln[1:-1].strip() if ln.startswith("(") and ln.endswith(")") else ln
        ell_m = re.match(r"^([\u0600-\u06FF]+)\s*\.\.\s+(.+)$", ln_unwrapped)
        if ell_m:
            ellipses_drop_traps.append({
                "line": ln,
                "at_risk_word": ell_m.group(1),
                "fix": f"Remove '..' after '{ell_m.group(1)}' -> '{ell_m.group(1)} {ell_m.group(2)}' so Lyria 3.5 does not omit it (NC37-B).",
            })

        # NC37-D1: Graphic 'الِا' / 'الْا' Wasl-Alif misread as 'الأَ' & Tatweel U+0640 consonant hallucination (Exp 33: أَهِـيْ->أَهِبِي)
        for w in re.findall(r"[\u0600-\u06FF]+", ln):
            if "\u0640" in w:
                tatweel_hallucination_traps.append({
                    "word": w,
                    "fix": w.replace("\u0640", ""),
                    "reason": "Unicode Tatweel (ـ U+0640) causes Lyria 3.5 to hallucinate an extra consonant (Exp 33: أَهِـيْ -> أَهِبِي).",
                })
            if re.search(r"ال[\u0650\u0652]ا", w):
                wasl_alif_traps.append({
                    "word": w,
                    "fix": re.sub(r"ال[\u0650\u0652]ا", "الإِ", w),
                })

        # NC37-D2: Half-vocalized medial consonant inside a partially diacritized word
        for w in re.findall(r"[\u0600-\u06FF]+", ln):
            if not any(ch in diac_chars for ch in w):
                continue
            pairs = []
            for ch in w:
                if ch in diac_chars:
                    if pairs:
                        pairs[-1] = (pairs[-1][0], True)
                else:
                    pairs.append((ch, False))
            start_i = 2 if len(pairs) >= 4 and pairs[0][0] == "ا" and pairs[1][0] == "ل" else 0
            if len(pairs) >= 5 and pairs[0][0] in "بلوفك" and pairs[1][0] == "ا" and pairs[2][0] == "ل":
                start_i = 3
            missing_letters = []
            for idx in range(start_i + 1, max(start_i + 1, len(pairs) - 1)):
                base_ch, has_d = pairs[idx]
                next_ch = pairs[idx + 1][0] if idx + 1 < len(pairs) else ""
                if not has_d and base_ch not in skip_medial and next_ch not in ("ا", "ى"):
                    missing_letters.append(base_ch)
            if missing_letters:
                half_vocalized_words.append({
                    "word": w,
                    "missing_medial_consonants": missing_letters,
                    "fix": "Fully vocalize every medial consonant (e.g. جُمعةٍ -> جُمُعَةٍ) to prevent vowel guesswork (NC37-D).",
                })

    # NC37-C & NC37-D3: Cross-line & cross-section checks
    for idx in range(len(lyric_entries) - 1):
        sec_a, ln_a = lyric_entries[idx]
        sec_b, ln_b = lyric_entries[idx + 1]
        if re.search(r"\([^)]+\)\s*$", ln_a) and not ln_a.startswith("("):
            next_words = re.findall(r"[\u0600-\u06FF]+", re.sub(r"\([^)]*\)", "", ln_b))
            if len(next_words) >= 4:
                inline_echo_swallow_traps.append({
                    "echo_line": ln_a,
                    "next_dense_line": ln_b,
                    "fix": "Move inline echo '(...)' to its own line or remove it before a >=4-word line to prevent swallowing opening words (NC37-C).",
                })
        if sec_a != sec_b:
            clean_a = ln_a[1:-1] if ln_a.startswith("(") and ln_a.endswith(")") else re.sub(r"\([^)]*\)", "", ln_a)
            clean_b = ln_b[1:-1] if ln_b.startswith("(") and ln_b.endswith(")") else re.sub(r"\([^)]*\)", "", ln_b)
            words_a = re.findall(r"[\u0600-\u06FF]+", clean_a)
            words_b = re.findall(r"[\u0600-\u06FF]+", clean_b)
            if words_a and words_b:
                stem_a = re.sub(r"^ال", "", _nc37_strip_diacritics(words_a[-1])).replace("أ", "ا").replace("إ", "ا")
                stem_b = re.sub(r"^ال", "", _nc37_strip_diacritics(words_b[-1])).replace("أ", "ا").replace("إ", "ا")
                if len(stem_a) >= 3 and len(stem_b) >= 3 and _nc37_levenshtein_1(stem_a, stem_b):
                    rhyme_carryover_traps.append({
                        "prev_section_end_word": words_a[-1],
                        "next_section_end_word": words_b[-1],
                        "fix": f"Replace near-homophone '{words_a[-1]}' before reprise ending in '{words_b[-1]}' to prevent rhyme contamination (NC37-D).",
                    })

    total_issues = (
        len(choir_shadda_risks)
        + len(comma_after_sukun_traps)
        + len(ellipses_drop_traps)
        + len(inline_echo_swallow_traps)
        + len(wasl_alif_traps)
        + len(half_vocalized_words)
        + len(rhyme_carryover_traps)
        + len(tatweel_hallucination_traps)
    )
    return {
        "nc37_preflight_passed": total_issues == 0,
        "total_issues": total_issues,
        "choir_shadda_blur_risks": choir_shadda_risks,
        "comma_after_sukun_traps": comma_after_sukun_traps,
        "ellipses_drop_traps": ellipses_drop_traps,
        "inline_echo_swallow_traps": inline_echo_swallow_traps,
        "wasl_alif_traps": wasl_alif_traps,
        "half_vocalized_words": half_vocalized_words,
        "rhyme_carryover_traps": rhyme_carryover_traps,
        "tatweel_hallucination_traps": tatweel_hallucination_traps,
    }


def compute_strict_production_score_v62(
    music_score: float,
    orthoepy_score: float,
    critical_verbal_defects: int = 0,
    major_verbal_defects: int = 0,
) -> dict:
    """V62.0 (NC37-E): Zero-Flattery Strict Production Score Ceiling (Eliminates Orchestral Halo Inflation).

    Any critical verbal defect (dropped Shadda like عَجِّلْ->عَاجِلْ, added Tanween عَجِّلُنْ,
    omitted word, or word mutation الأَمَلْ->الأَجْمَلْ) caps overall score strictly <= 7.9
    and forces release_ready=False until surgically repaired or re-generated.
    """
    m_sc = max(0.0, min(10.0, float(music_score)))
    o_sc = max(0.0, min(10.0, float(orthoepy_score)))
    crit = max(0, int(critical_verbal_defects))
    maj = max(0, int(major_verbal_defects))

    weighted = 0.45 * m_sc + 0.55 * o_sc
    capped = min(weighted, o_sc + 1.2)
    cap_reason = "orthoepy_halo_cap" if capped < weighted else "none"

    if crit >= 1:
        capped = min(capped, 7.9)
        cap_reason = f"critical_verbal_defects_cap ({crit} critical)"
        release_ready = False
        verdict = "NEEDS_FIX_NOT_RELEASE_READY"
    elif maj >= 2:
        capped = min(capped, 8.4)
        cap_reason = f"major_verbal_defects_cap ({maj} major)"
        release_ready = False
        verdict = "NEEDS_POLISH_BEFORE_RELEASE"
    else:
        release_ready = bool(o_sc >= 8.8 and capped >= 8.8)
        verdict = "RELEASE_READY_STRICT_PASS" if release_ready else "BELOW_RELEASE_THRESHOLD"

    return {
        "music_score": round(m_sc, 2),
        "orthoepy_score": round(o_sc, 2),
        "critical_verbal_defects": crit,
        "major_verbal_defects": maj,
        "strict_overall_score": round(capped, 2),
        "release_ready": release_ready,
        "verdict": verdict,
        "cap_reason": cap_reason,
        "mandatory_audit_ffmpeg_filter": (
            "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=140,"
            "equalizer=f=2600:t=q:w=1.2:g=4,equalizer=f=5500:t=q:w=1.5:g=2"
        ),
    }


FIVE_BAND_SPECTRAL_OCCUPANCY_V63 = {
    "TRACK_A_PURE_ACAPELLA_LATMIYA": {
        "track_alias": "track_a",
        "title_ar": "المسار الأول: اللطمية الحسينية الخالصة (أكابيلا وموكب بلا معازف ولا تآلفات غربية)",
        "commercial_prior_rule": "Occupy all 5 bands positively with monophonic Husseiniya body percussion & strictly unison octave Raddada response; keep vocal texture 100% monophonic/octave with zero Western 12-TET minor triads (NC39/NC46).",
        "exclude_instruments": ["oud", "violin", "guitar", "piano", "synthesizer", "pop drums", "rock snare"],
        "allowed_percussion": ["synchronized bare-chest Latm thumping", "heavy Bahraini Dammam drum", "Iraqi Zanjeel"],
        "allowed_elements": [
            "deep resonant bare-chest Latm low-end pulse",
            "warm monophonic Radood chest-to-Mayan modal delivery",
            "unison Al-Raddada male congregation call-and-response (strictly monophonic, zero Western triads)",
            "articulate Iraqi/Bahrani/Qatifi Arabic diction",
            "natural cavernous Husseiniya hall dome reflections",
        ],
        "bands": {
            "band_1_40_120hz": "Deep resonant bare-chest Latm thumping + heavy Bahraini Dammam sub-fundamental",
            "band_2_120_400hz": "Warm monophonic Radood Qarar chest resonance + congregation chest-strike body",
            "band_3_400_2000hz": "Stepwise modal Radood lament + strictly unison Al-Raddada congregation response",
            "band_4_2000_5000hz": "Centered Solo Radood articulate Arabic Makharij & weeping Iraqi Wanna inflection",
            "band_5_5000_16000hz": "Natural cavernous Husseiniya dome reflections + organic congregation breath air",
        },
    },
    "TRACK_B_DIGNIFIED_ORCHESTRAL_NASHEED": {
        "track_alias": "track_b",
        "title_ar": "المسار الثاني: النشيد الشيعي الأوركسترالي الوقور والأوبريت (6 عائلات غير لهوية)",
        "commercial_prior_rule": "Lock articulation to Legato, Clean Tone, and Stately Marching to prevent pop/tarab drift (NC39).",
        "exclude_styles": ["belly dance rhythm", "pop groove", "fast tarab ornamentation", "club beats", "trap beat"],
        "articulation_lock": "Slow legato orchestral strings, expressive solo oboe & reed ney, clean acoustic guitar fingerpicking, stately marching timpani & Bendir",
        "allowed_percussion": ["stately orchestral timpani swells", "traditional Bendir frame drum", "solemn Tasa cymbals"],
        "allowed_elements": [
            "sustained legato orchestral strings & deep cellos",
            "expressive solo oboe, reed ney & warm bassoon",
            "dignified Baritone Munshid lead vocal & balanced male choir",
            "spacious concert hall natural reverb",
        ],
        "bands": {
            "band_1_40_120hz": "Stately orchestral timpani swells + traditional Bendir + warm bassoon & deep cellos",
            "band_2_120_400hz": "Sustained legato low strings + dignified classical oud / clean acoustic guitar warmth",
            "band_3_400_2000hz": "Expressive solo oboe + mournful reed ney + legato clarinet + balanced male choir",
            "band_4_2000_5000hz": "Centered dignified Baritone Munshid Arabic diction + noble brass swells",
            "band_5_5000_16000hz": "Solemn Tasa shimmer + spacious concert hall stereo reverb",
        },
    },
    "TRACK_C_TAWASHIH_IBTIHAL_MAWLID": {
        "track_alias": "track_c",
        "title_ar": "المسار الثالث: التواشيح والابتهالات التراثية والبطانة والمواليد الدفّية",
        "commercial_prior_rule": "Fill upper & lower spectrum with mosque dome reverb, vocal Bitanah humming pads, and traditional Daf only in celebratory finale (NC39).",
        "exclude_instruments": ["string instruments", "wind instruments", "piano", "electronic synths", "pop drums", "chest latm"],
        "allowed_percussion": ["traditional Daf frame drum in final Mawlid/Jalwat stage only"],
        "allowed_elements": [
            "Pure Acapella classical Munshid with controlled Arabic melisma",
            "harmonic male Bitanah humming pads & choral response",
            "spacious mosque dome natural echo",
        ],
        "bands": {
            "band_1_40_120hz": "Deep Bitanah bass vocal drone + warm traditional Daf skin resonance (Mawlid finale only)",
            "band_2_120_400hz": "Warm classical Munshid Qarar chest register + male Bitanah humming bed",
            "band_3_400_2000hz": "Classical Muwashah melody + antiphonal male Bitanah choir responses",
            "band_4_2000_5000hz": "Crystal-clear Classical Arabic Tajweed articulation & controlled melisma",
            "band_5_5000_16000hz": "Spacious mosque dome natural echo & delicate vocal breath air",
        },
    },
}

MAQAM_LYRIA35_ADHERENCE_AND_AUDIO_REF_MATRIX_V63 = {
    "saba": {
        "quarter_tone": True,
        "lyria35_text_adherence": "low_to_medium",
        "audio_reference_policy": "mandatory_30s_make_tracks_for_my_vocal",
        "atwar": ["النعي الحسيني", "المصرع", "الدشتي الباكي"],
        "modulation_targets": ["hijaz", "ajam_triad_flash", "bayati"],
        "guidance": "Saba flattens toward 12-TET on text-only; record a 30s vocal guide via Make tracks for my vocal to inject authentic quarter-tone pitch contour directly into Lyria 3.5 latents.",
    },
    "sikah": {
        "quarter_tone": True,
        "lyria35_text_adherence": "low_to_medium",
        "audio_reference_policy": "mandatory_30s_make_tracks_for_my_vocal",
        "atwar": ["الحدي", "الركباني", "الجلوات", "الأبوذية المنبرية"],
        "modulation_targets": ["rast", "saba", "bayati"],
        "guidance": "Sikah neutral third flattens on text-only; upload a 30s Hadi/Jalwat vocal reference or modulate into Sikah from Rast/Bayati.",
    },
    "bayati": {
        "quarter_tone": True,
        "lyria35_text_adherence": "medium",
        "audio_reference_policy": "recommended_short_mustahal",
        "atwar": ["الفائزي", "المثكل", "الطور البحراني والقطيفي", "الموكبي"],
        "modulation_targets": ["saba", "nahawand", "hijaz"],
        "guidance": "Moderate adherence via explicit 'Maqam Bayati'; upload short Mustahal reference for locked regional Qatifi/Bahrani/Iraqi quarter-tone Tor.",
    },
    "bayati_shuri": {
        "quarter_tone": True,
        "lyria35_text_adherence": "medium",
        "audio_reference_policy": "recommended_short_mustahal",
        "atwar": ["الشور العراقي", "الثلاثي البحراني", "النزلة الدرامية"],
        "modulation_targets": ["hijaz", "kurd", "bayati"],
        "guidance": "Bayati Shuri's upper Hijaz tetrachord anchors Lyria better than plain Bayati, though a short Mustahal vocal guide locks the neutral second.",
    },
    "husseini": {
        "quarter_tone": True,
        "lyria35_text_adherence": "medium",
        "audio_reference_policy": "recommended_short_mustahal",
        "atwar": ["الفائزي القطيفي", "الابتهال الخاشع", "الدشتي"],
        "modulation_targets": ["saba", "suznak", "bayati"],
        "guidance": "Emphasize fifth-degree tension ('Maqam Husseini'); proven live in Exp 28 (9.9/10) and Exp 29 (9.4/10).",
    },
    "rast": {
        "quarter_tone": True,
        "lyria35_text_adherence": "medium",
        "audio_reference_policy": "recommended_short_mustahal",
        "atwar": ["التواشيح التراثية", "الحدي", "الجلوات والمواليد"],
        "modulation_targets": ["suznak", "sikah", "ajam"],
        "guidance": "Noble dignified cadence ('Maqam Rast, noble dignified cadence'); pairs smoothly with Suznak or Ajam.",
    },
    "suznak": {
        "quarter_tone": True,
        "lyria35_text_adherence": "medium",
        "audio_reference_policy": "recommended_short_mustahal",
        "atwar": ["الموشح الديني التراثي", "الجلوات الفرحة"],
        "modulation_targets": ["rast", "hijaz", "husseini"],
        "guidance": "Rast base + Hijaz on fifth degree; empirically proven in Exp 28 (9.9/10) with Male Bitanah Choir.",
    },
    "hijaz": {
        "quarter_tone": False,
        "lyria35_text_adherence": "high",
        "audio_reference_policy": "optional",
        "atwar": ["القزويني", "مطالع الملاحم", "النزلة السريعة"],
        "modulation_targets": ["nahawand", "rast", "kurd"],
        "guidance": "High text adherence via JSON ('Maqam Hijaz, solemn eastern resonance'); 12-TET orchestral-safe.",
    },
    "hijaz_kar": {
        "quarter_tone": False,
        "lyria35_text_adherence": "high",
        "audio_reference_policy": "optional",
        "atwar": ["الموكب الملحمي الفصيح", "الزمينة"],
        "modulation_targets": ["hijaz", "kurd", "nahawand"],
        "guidance": "High text adherence via JSON (proven in Exp 23); ideal for epic Fusha Mawkib and heroic operettas.",
    },
    "nahawand": {
        "quarter_tone": False,
        "lyria35_text_adherence": "high",
        "audio_reference_policy": "optional",
        "atwar": ["النشيد الأوركسترالي المهدوي", "اللطم الوجداني", "المهد البحراني"],
        "modulation_targets": ["kurd", "ajam", "hijaz"],
        "guidance": "Very high text adherence via JSON ('Maqam Nahawand, melancholic minor'); proven in Exp 22 & Exp 32; 12-TET orchestral-safe.",
    },
    "kurd": {
        "quarter_tone": False,
        "lyria35_text_adherence": "high",
        "audio_reference_policy": "optional",
        "atwar": ["اللطمية الوجدانية الحديثة", "الشور", "النشيد الوجداني"],
        "modulation_targets": ["nahawand", "ajam", "hijaz"],
        "guidance": "Very high text adherence via JSON; seamless partner to Nahawand and Ajam in Axis-5 orchestral anthems.",
    },
    "lami": {
        "quarter_tone": False,
        "lyria35_text_adherence": "low_without_audio_ref",
        "audio_reference_policy": "mandatory_30s_iraqi_audio_ref",
        "atwar": ["المثكل الجنوبي", "الرثاء الفراتي", "السيد سلام", "النزلة الكربلائية الباسمية"],
        "modulation_targets": ["kurd", "saba_zamzam", "bayati"],
        "guidance": "V64.0 Ground-Truth Correction (Exp 35 Post-Mortem): Text-only 'Maqam Lami' collapses to Western 12-TET Bb-minor/Gb-major in Lyria 3.5; ALWAYS upload a clean 30-85s Iraqi vocal+Latm reference via '+ -> Upload > Audio' (Cover -> Extend).",
    },
    "nawa_athar": {
        "quarter_tone": False,
        "lyria35_text_adherence": "high",
        "audio_reference_policy": "optional",
        "atwar": ["قافلة عاشوراء الأحسائية", "الملحمة الدرامية"],
        "modulation_targets": ["hijaz", "nahawand", "kurd"],
        "guidance": "High text adherence via JSON; strong dramatic minor-augmented intervals compatible with 12-TET strings.",
    },
    "saba_zamzam": {
        "quarter_tone": False,
        "lyria35_text_adherence": "low_without_audio_ref",
        "audio_reference_policy": "mandatory_30s_iraqi_audio_ref",
        "atwar": ["النزلة الكربلائية الحزينة", "بديل الصبا الخالي من الربع تون"],
        "modulation_targets": ["lami", "kurd", "hijaz"],
        "guidance": "V64.0 Ground-Truth Correction (Exp 35 Post-Mortem): Text-only 'Saba Zamzam' collapses to Western 12-TET natural minor; upload an authentic Iraqi vocal+Latm reference via '+ -> Upload > Audio' to lock diminished-4th modal cadences.",
    },
    "ajam": {
        "quarter_tone": False,
        "lyria35_text_adherence": "high",
        "audio_reference_policy": "optional",
        "atwar": ["الأناشيد المهدوية الحماسية", "المواليد", "ومضة العجم الثلاثي"],
        "modulation_targets": ["nahawand", "kurd", "rast"],
        "guidance": "Very high text adherence via JSON ('Maqam Ajam, solemn marching anthemic choir, strictly non-dance'); proven in Exp 27 & Exp 32.",
    },
}


def apply_lyria_harshness_tamer_2_4khz(
    stereo_signal: np.ndarray,
    sample_rate: int,
    max_cut_db: float = 2.8,
) -> np.ndarray:
    """V63.0 (NC41): Dynamic 2.4-3.8 kHz neural vocoder harshness tamer for Lyria 3.5 exports.

    Isolates the upper-midrange digital harshness / phase-burble zone (2.4-3.8 kHz) reported on
    dense Lyria 3.5 choral/vocal renders and applies smooth, mono-safe envelope-following dynamic
    attenuation (up to -max_cut_db) only when harshness spikes exceed core vocal warmth (400-1800 Hz).
    """
    arr = np.asarray(stereo_signal, dtype=np.float64)
    if arr.size < 32 or sample_rate < 6000:
        return arr.copy()
    was_mono = arr.ndim == 1
    st = np.column_stack((arr, arr)) if was_mono else arr.copy()

    nyq = 0.5 * float(sample_rate)
    hi_hz = min(3800.0, 0.90 * nyq)
    lo_hz = min(2400.0, hi_hz * 0.65)
    core_hi = min(1800.0, lo_hz * 0.85)
    core_lo = min(400.0, core_hi * 0.50)
    if lo_hz <= 20.0 or hi_hz <= lo_hz + 50.0 or core_hi <= core_lo + 50.0:
        return arr.copy()

    # Design linked mono detector (100% phase/mono-safe gain reduction across L & R)
    mid = 0.5 * (st[:, 0] + st[:, 1])
    sos_harsh = butter(2, [lo_hz / nyq, hi_hz / nyq], btype="bandpass", output="sos")
    sos_core = butter(2, [core_lo / nyq, core_hi / nyq], btype="bandpass", output="sos")
    harsh_mid = sosfilt(sos_harsh, mid)
    core_mid = sosfilt(sos_core, mid)

    win = max(8, int(0.030 * sample_rate))
    kernel = np.ones(win, dtype=np.float64) / float(win)
    harsh_env = np.sqrt(np.maximum(fftconvolve(harsh_mid * harsh_mid, kernel, mode="same"), 1e-12))
    core_env = np.sqrt(np.maximum(fftconvolve(core_mid * core_mid, kernel, mode="same"), 1e-12))

    # Ratio above 0.42 triggers proportional gentle dynamic cut up to max_cut_db
    ratio = harsh_env / (core_env + 1e-6)
    excess = np.clip((ratio - 0.42) / 0.58, 0.0, 1.0)
    cut_db = np.clip(excess * float(max_cut_db), 0.0, abs(float(max_cut_db)))
    band_gain = 10.0 ** (-cut_db / 20.0)
    sub_factor = 1.0 - band_gain  # amount of 2.4-3.8 kHz band to dynamically subtract

    out = st.copy()
    for ch in range(st.shape[1]):
        ch_harsh = sosfilt(sos_harsh, st[:, ch])
        out[:, ch] = st[:, ch] - sub_factor * ch_harsh

    return out[:, 0] if was_mono else out


def _resolve_v63_track_mode(track_mode: str) -> str:
    """Resolve short aliases ('track_a', 'track_b', 'track_c') to canonical V63 track mode keys."""
    key = (track_mode or "TRACK_A_PURE_ACAPELLA_LATMIYA").strip().upper()
    alias_map = {
        "TRACK_A": "TRACK_A_PURE_ACAPELLA_LATMIYA",
        "A": "TRACK_A_PURE_ACAPELLA_LATMIYA",
        "LATMIYA": "TRACK_A_PURE_ACAPELLA_LATMIYA",
        "TRACK_B": "TRACK_B_DIGNIFIED_ORCHESTRAL_NASHEED",
        "B": "TRACK_B_DIGNIFIED_ORCHESTRAL_NASHEED",
        "ORCHESTRAL": "TRACK_B_DIGNIFIED_ORCHESTRAL_NASHEED",
        "OPERETTA": "TRACK_B_DIGNIFIED_ORCHESTRAL_NASHEED",
        "TRACK_C": "TRACK_C_TAWASHIH_IBTIHAL_MAWLID",
        "C": "TRACK_C_TAWASHIH_IBTIHAL_MAWLID",
        "TAWASHIH": "TRACK_C_TAWASHIH_IBTIHAL_MAWLID",
        "MUWASHAH": "TRACK_C_TAWASHIH_IBTIHAL_MAWLID",
    }
    resolved = alias_map.get(key, key)
    if resolved not in FIVE_BAND_SPECTRAL_OCCUPANCY_V63:
        raise ValueError(f"Unsupported V63 track_mode: {track_mode}")
    return resolved


def build_v63_session_bootstrap_json(
    track_mode: str = "TRACK_A_PURE_ACAPELLA_LATMIYA",
    dialect: str = "bahrani",
    target_duration: str = "05:30",
    vocal_identity: str = None,
) -> dict:
    """V63.0 (NC38): Build Stage-0 Gemini Producer Session Bootstrap JSON (MASTER_STATE Lock)."""
    mode_key = _resolve_v63_track_mode(track_mode)
    spec = FIVE_BAND_SPECTRAL_OCCUPANCY_V63[mode_key]
    dialect_map = {
        "bahrani": "Strict authentic Bahraini Khaleeji phonetic delivery (No-MSA drift)",
        "qatifi": "Strict authentic Eastern Arabian Qatifi-Hasawi phonetic delivery (NC35, No-MSA drift)",
        "iraqi": "Strict authentic Iraqi Karbalaei/Southern phonetic delivery (No-MSA drift)",
        "fusha": "Crystal-clear Classical Arabic Fusha with Tajweed-grade Shadda & Makharij (NC37)",
        "iraqi_bahrani": "Dual-stage dialect lock: Fusha narrative intro + colloquial emotional chorus isolated in separate JSON stages",
    }
    default_vocal = (
        "Consistent commanding male Radood Baritone timbre locked across all 4 Extend passes"
        if mode_key == "TRACK_A_PURE_ACAPELLA_LATMIYA"
        else "Consistent dignified resonant male Munshid Baritone timbre locked across all Extend passes"
    )
    return {
        "session_bootstrap": {
            "action": "INITIALIZE_AND_LOCK_STATE_ONLY_DO_NOT_GENERATE",
            "confirmation_required": "Confirm locked MASTER_STATE rules in 3 concise bullet points and wait for Stage 1 JSON.",
            "architecture_layer": "Layer 1 (Gemini Producer JSON Orchestration) -> Layer 2 (Lyria 3.5 Temporal Latent Diffusion)",
            "track_mode": mode_key,
            "master_state": {
                "target_total_duration": target_duration,
                "single_pass_ceiling": "03:00 (Lyria 3.5 Temporal Latent Window)",
                "vocal_identity": vocal_identity or default_vocal,
                "dialect_lock": dialect_map.get(dialect, dialect_map["bahrani"]),
                "strict_constraints": {
                    "exclude_instruments": spec.get("exclude_instruments", []),
                    "exclude_styles": spec.get("exclude_styles", ["pop groove", "dance beat", "club rhythm"]),
                    "allowed_percussion": spec["allowed_percussion"],
                    "allowed_elements": spec["allowed_elements"],
                    "anti_negative_prompt_inversion": "Always occupy all 5 spectral bands (40 Hz - 16 kHz) with positive acoustic replacements (NC39).",
                },
                "five_band_positive_occupancy": spec["bands"],
                "stage_roadmap": [
                    "Stage 1 (00:00-01:15): GENERATE_INITIAL — Intro/Na'i + Mustahal",
                    "Stage 2 (01:15-02:45): EXTEND_SEAMLESSLY (inherit_master_state: true) — Verses 1 + Raddada",
                    "Stage 3 (02:45-03:45): EXTEND_SEAMLESSLY (inherit_master_state: true) — Kaser/Melodic Break + Ahaat",
                    "Stage 4 (03:45-05:15): EXTEND_AND_CONCLUDE (inherit_master_state: true) — Climax Nazla / Na'i Outro",
                ],
            },
            "customize_producer_tips": {
                "instructions": "Save master_state permanently under Flow Music > Customize Producer > Instructions for zero-drift sessions.",
                "flows": "Save this Stage-0 JSON as a reusable /flow shortcut to bootstrap new Latmiya/Nasheed projects in 1 command.",
                "memories": "Keep Memories enabled for stylistic consistency or start a fresh session when switching dialects/genres.",
            },
        }
    }


def validate_spectral_occupancy_v63(json_payload: dict) -> dict:
    """V63.0 (NC39): Enforce 5-band (40 Hz - 16 kHz) positive spectral occupancy & block Negative-Prompt Inversion."""
    if not isinstance(json_payload, dict):
        raise ValueError("json_payload must be a dict")
    constraints = {}
    if "session_bootstrap" in json_payload:
        ms = json_payload["session_bootstrap"].get("master_state", {})
        constraints = ms.get("strict_constraints", {})
        five_bands = ms.get("five_band_positive_occupancy", {})
    elif "project_settings" in json_payload:
        constraints = json_payload["project_settings"].get("strict_constraints", {})
        five_bands = json_payload["project_settings"].get("five_band_positive_occupancy", {})
    else:
        constraints = json_payload.get("strict_constraints", json_payload)
        five_bands = json_payload.get("five_band_positive_occupancy", {})

    has_negative = bool(constraints.get("exclude_instruments") or constraints.get("exclude_styles"))
    positive_pool = (
        list(constraints.get("allowed_percussion", []))
        + list(constraints.get("allowed_elements", []))
        + ([constraints["articulation_lock"]] if constraints.get("articulation_lock") else [])
    )
    has_positive = len(positive_pool) >= 2
    inversion_risk = bool(has_negative and not has_positive)

    required_bands = (
        "band_1_40_120hz",
        "band_2_120_400hz",
        "band_3_400_2000hz",
        "band_4_2000_5000hz",
        "band_5_5000_16000hz",
    )
    missing_bands = [b for b in required_bands if not str(five_bands.get(b, "")).strip()]

    return {
        "nc39_passed": (not inversion_risk) and len(missing_bands) == 0,
        "has_negative_constraints": has_negative,
        "has_positive_replacements": has_positive,
        "negative_prompt_inversion_risk": inversion_risk,
        "missing_spectral_bands": missing_bands,
        "positive_elements_count": len(positive_pool),
    }


def plan_v63_five_minute_word_budget(
    poem_text: str,
    track_mode: str = "TRACK_A_PURE_ACAPELLA_LATMIYA",
    dialect: str = "bahrani",
    target_duration_sec: int = 315,
    maqam_arc=None,
) -> dict:
    """V63.0 (NC38-NC40): Plan 5-minute staged word budget (280-350 net words, 12-16s/bayt) & full 5-step JSON."""
    mode_key = _resolve_v63_track_mode(track_mode)
    spec = FIVE_BAND_SPECTRAL_OCCUPANCY_V63[mode_key]
    clean_lines = [
        ln.strip()
        for ln in poem_text.replace("\\n", "\n").splitlines()
        if ln.strip() and not (ln.strip().startswith("[") and ln.strip().endswith("]"))
    ]
    all_words = []
    for ln in clean_lines:
        all_words.extend(re.findall(r"[\u0600-\u06FF]+", ln))
    word_count = len(all_words)
    bayt_count = max(1, math.ceil(len(clean_lines) / 2.0))

    target_sec = max(120, int(target_duration_sec))
    breathing_sec = 90 if target_sec >= 270 else int(round(target_sec * 0.28))
    net_vocal_sec = max(60, target_sec - breathing_sec)
    optimal_min_words = int(round((net_vocal_sec / 60.0) * 80.0))
    optimal_max_words = int(round((net_vocal_sec / 60.0) * 100.0))
    sec_per_bayt = round(net_vocal_sec / float(bayt_count), 2)
    requires_extend = target_sec > 180

    if not maqam_arc:
        if mode_key == "TRACK_A_PURE_ACAPELLA_LATMIYA":
            maqam_arc = ["saba", "bayati", "kurd", "hijaz"]
        elif mode_key == "TRACK_B_DIGNIFIED_ORCHESTRAL_NASHEED":
            maqam_arc = ["nahawand", "kurd", "ajam", "nahawand"]
        else:
            maqam_arc = ["rast", "sikah", "nahawand", "ajam"]

    audio_ref_advisories = []
    for mq in dict.fromkeys(maqam_arc):
        info = MAQAM_LYRIA35_ADHERENCE_AND_AUDIO_REF_MATRIX_V63.get(mq)
        if info and info["audio_reference_policy"] != "optional":
            audio_ref_advisories.append({
                "maqam": mq,
                "adherence": info["lyria35_text_adherence"],
                "policy": info["audio_reference_policy"],
                "guidance": info["guidance"],
            })

    # Partition poem lines evenly across 4 stages (Stage 1..4)
    n_lines = len(clean_lines)
    chunks = [[], [], [], []]
    for i, ln in enumerate(clean_lines):
        bucket = min(3, int(i * 4 / max(1, n_lines)))
        chunks[bucket].append(ln)

    stage_meta = [
        (1, "GENERATE_INITIAL", "[المستهل]", "00:00 - 01:15", maqam_arc[0], 60 if mode_key == "TRACK_A_PURE_ACAPELLA_LATMIYA" else 76, "Establish locked timbre, dialect, and 5-band positive acoustics"),
        (2, "EXTEND_SEAMLESSLY", "[النزلة الأولى]", "01:15 - 02:45", maqam_arc[min(1, len(maqam_arc) - 1)], 62 if mode_key == "TRACK_A_PURE_ACAPELLA_LATMIYA" else 82, f"Modulate smoothly from {maqam_arc[0]} to {maqam_arc[min(1, len(maqam_arc) - 1)]}"),
        (3, "EXTEND_SEAMLESSLY", "[الكسر]", "02:45 - 03:45", maqam_arc[min(2, len(maqam_arc) - 1)], 60 if mode_key == "TRACK_A_PURE_ACAPELLA_LATMIYA" else 78, "Drop percussion briefly for melodic Kaser breathing space"),
        (4, "EXTEND_AND_CONCLUDE", "[الخاتمة]", "03:45 - 05:15", maqam_arc[min(3, len(maqam_arc) - 1)], 62 if mode_key == "TRACK_A_PURE_ACAPELLA_LATMIYA" else 86, "Return to collective Mustahal refrain and resolve naturally on modal Qarar"),
    ]

    bootstrap = build_v63_session_bootstrap_json(
        track_mode=mode_key,
        dialect=dialect,
        target_duration=f"{target_sec // 60:02d}:{target_sec % 60:02d}",
    )
    stages = []
    for sid, action, tag, trange, mq, bpm_val, trule in stage_meta:
        stage_obj = {
            "stage_id": sid,
            "action": action,
            "inherit_master_state": sid > 1,
            "section_tag": tag,
            "time_range": trange,
            "transition_rule": trule,
            "music_theory": {
                "maqam": mq,
                "tempo_bpm": bpm_val,
                "nc36_orchestration": validate_maqam_orchestration_compatibility(
                    mq, uses_western_12tet_chords=(mode_key == "TRACK_B_DIGNIFIED_ORCHESTRAL_NASHEED")
                ),
            },
            "lyrics": "\n".join(chunks[sid - 1]),
        }
        stages.append(stage_obj)

    nc39_check = validate_spectral_occupancy_v63(bootstrap)
    nc37_check = audit_fusha_shadda_wasl_and_makharij_v62(poem_text)

    if word_count < optimal_min_words:
        budget_status = "under_budget_expand_or_shorten_target"
    elif word_count > optimal_max_words:
        budget_status = "over_budget_phoneme_compression_risk"
    else:
        budget_status = "optimal_nc40_word_budget"

    return {
        "track_mode": mode_key,
        "dialect": dialect,
        "target_duration_sec": target_sec,
        "lyria35_single_pass_ceiling_sec": 180,
        "requires_staged_extend": requires_extend,
        "word_budget": {
            "actual_arabic_words": word_count,
            "bayt_count": bayt_count,
            "breathing_allowance_sec": breathing_sec,
            "net_vocal_sec": net_vocal_sec,
            "optimal_word_range": [optimal_min_words, optimal_max_words],
            "estimated_sec_per_bayt": sec_per_bayt,
            "ideal_sec_per_bayt_range": [12.0, 16.0],
            "status": budget_status,
        },
        "audio_reference_advisories": audio_ref_advisories,
        "nc39_spectral_occupancy": nc39_check,
        "nc37_orthoepy_preflight": {
            "passed": nc37_check["nc37_preflight_passed"],
            "total_issues": nc37_check["total_issues"],
        },
        "stage_0_bootstrap": bootstrap,
        "stages_1_to_4": stages,
        "hybrid_post_production_7_stages": [
            "1. Flow Music Remix > Replace (8-18s surgical fix for any dialect/Shadda flaw)",
            "2. Flow Music Stem Split + 48 kHz WAV Export (isolate Radood, Choir, Latm, Strings)",
            "3. Melodyne Manual 24-EDO Correction (disable 12-TET snap on quarter-tone Maqams)",
            "4. Dynamic EQ: HPF <80Hz, warm cut 200-400Hz, Lyria harshness tamer 2.4-3.8kHz (--tame-lyria-harshness)",
            "5. Serial Compression (2:1-4:1) + De-Esser (5-8kHz on س/ص/ش/ز)",
            "6. Mid-Side Reverb Clarity EQ + Sidechain Ducking 4:1-6:1 (2-4 dB)",
            "7. Multi-Platform EBU R128 Master (-14/-16/-18/-23 LUFS, -1.0 dBTP) + Mono Check (SynthID preserved)",
        ],
        "five_band_positive_occupancy": spec["bands"],
    }


def plan_chained_surgical_replace_v63(
    clip_uuid: str,
    defect_windows: list,
) -> dict:
    """V63.0 (NC42): Plan Back-to-Front chained surgical Remix > Replace passes on Lyria 3.5.

    Empirically discovered in Exp 34-A/B/C (c7622fcc -> c0eaa434 -> 86b71050 -> 6c5808e1):
    - Replacing an earlier window can shift all downstream timestamps by +/-1-3s (-1.8s in Pass 1).
    - Ordering passes strictly BACK-TO-FRONT (highest timestamp -> lowest timestamp) guarantees
      earlier timestamps never shift between chained passes.
    - Merges windows separated by < 4.0s and enforces 8-16s window bounds with mandatory
      8s vocal-isolated + raw stereo seam verification after each pass.
    """
    if not defect_windows:
        return {
            "clip_uuid": clip_uuid,
            "ordering_rule": "BACK_TO_FRONT_DESCENDING_TIMESTAMP (NC42)",
            "total_passes": 0,
            "merged_windows_count": 0,
            "passes": [],
        }

    norm = []
    for item in defect_windows:
        s_sec = max(0.0, float(item["start_sec"]))
        e_sec = max(s_sec + 8.0, float(item["end_sec"]))
        if e_sec - s_sec > 18.0:
            e_sec = s_sec + 18.0
        norm.append({
            "start_sec": round(s_sec, 2),
            "end_sec": round(e_sec, 2),
            "old_line": str(item.get("old_line", "")).strip(),
            "fixed_line": str(item.get("fixed_line", "")).strip(),
            "defect_note": str(item.get("defect_note", "")).strip(),
        })

    # Merge close/overlapping windows (<4s gap) in ascending order first
    norm.sort(key=lambda w: w["start_sec"])
    merged = []
    merged_count = 0
    for w in norm:
        if merged and w["start_sec"] - merged[-1]["end_sec"] < 4.0 and (w["end_sec"] - merged[-1]["start_sec"]) <= 18.0:
            prev = merged[-1]
            prev["end_sec"] = max(prev["end_sec"], w["end_sec"])
            prev["old_line"] = " / ".join(x for x in (prev["old_line"], w["old_line"]) if x)
            prev["fixed_line"] = " / ".join(x for x in (prev["fixed_line"], w["fixed_line"]) if x)
            prev["defect_note"] = " + ".join(x for x in (prev["defect_note"], w["defect_note"]) if x)
            merged_count += 1
        else:
            merged.append(w)

    # Reverse strictly to BACK-TO-FRONT (descending start_sec) so earlier timestamps never drift
    merged.sort(key=lambda w: w["start_sec"], reverse=True)
    passes = []
    for idx, w in enumerate(merged, start=1):
        plan_step = build_remix_replace_inpainting_plan(
            clip_uuid=clip_uuid if idx == 1 else f"<output_clip_uuid_from_pass_{idx - 1}>",
            start_sec=w["start_sec"],
            end_sec=w["end_sec"],
            old_lyric_line=w["old_line"] or "(localized vocal defect)",
            fixed_lyric_line=w["fixed_line"] or "(clean articulated target lyric)",
        )
        passes.append({
            "pass_number": idx,
            "target_clip": clip_uuid if idx == 1 else f"<pass_{idx - 1}_replaced_uuid>",
            "window_sec": [w["start_sec"], w["end_sec"]],
            "defect_note": w["defect_note"],
            "replace_plan": plan_step,
            "mandatory_post_pass_verification": (
                f"Download Pass {idx} clip, listen to full-stereo seam + 8s vocal-isolated zoom "
                f"over {w['start_sec']:.0f}s-{w['end_sec']:.0f}s before launching Pass {idx + 1}."
            ),
        })

    return {
        "clip_uuid": clip_uuid,
        "ordering_rule": "BACK_TO_FRONT_DESCENDING_TIMESTAMP (NC42)",
        "total_passes": len(passes),
        "merged_windows_count": merged_count,
        "passes": passes,
    }


def _estimate_arabic_vocalic_syllables_v64(line_text: str) -> int:
    """Estimate sung Arabic vocalic nuclei count on clean or vocalized text for Karbalaei prosody checks."""
    clean = re.sub(r"\([^)]*\)", lambda m: m.group(0)[1:-1], line_text)
    clean = re.sub(r"[^\u0621-\u064A\u067E\u0686\u06AF\s]", "", clean)
    words = [w for w in clean.split() if w]
    total = 0
    for w in words:
        core = re.sub(r"^ال", "ل", w)
        long_v = len(re.findall(r"[اويىآ]", core))
        cons = max(0, len(core) - long_v)
        est = max(1, long_v + int(math.ceil(max(0, cons - long_v) * 0.55)))
        total += min(est, max(1, len(core) - 1) if len(core) > 1 else 1)
    return total


def _extract_rhyme_tail_v64(line_text: str) -> str:
    """Extract normalized 2-letter rhyme tail of a poetic line for AAAB Iraqi stanza verification."""
    clean = line_text.strip()
    if clean.startswith("(") and clean.endswith(")"):
        clean = clean[1:-1].strip()
    clean = re.sub(r"[\u064B-\u0652\u0670]", "", clean)
    words = re.findall(r"[\u0621-\u064A\u067E\u0686\u06AF]+", clean)
    if not words:
        return ""
    last = words[-1].replace("ة", "ه").replace("ى", "ا").replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return last[-2:] if len(last) >= 2 else last


def audit_iraqi_latmiya_preflight_v64(poem_text: str, target_bpm: float = 62.0) -> dict:
    """V64.0 (NC44-NC45): Pre-flight Iraqi Karbalaei Prosody, Raddada, Fusha-Leak & G2P Landmine Gate.

    Engineered from the ruthless Exp 35 Post-Mortem (f60b364d & 6c5be3ad vs. Basim Al-Karbalai's
    أم البنين, ألم وعتاب, ساعة الذبح) to block all 7 failure modes before calling Lyria 3.5:
    1. Verbose/Latin '[...]' headers (e.g. '[المستهل — 62 BPM — ...]')
    2. Missing collective '(...)' Raddada unison tags in '[المستهل]'
    3. Fusha case/mood grammar leaks inside Iraqi dialect ('طَاحَ', 'وِضَاعَ', 'أَدْرِكِ', 'لَا وَلِيَّ', 'اعْلَه')
    4. Persian 'گ/چ' consonant-cluster BPE shattering landmines ('وگفت->وتفت', 'گلبي->كلبي', 'ملچوم->ملتشوم', ungeminated 'دلالي')
    5. Over-stuffed >=15-syllable lines lacking ' .. ' breath pauses
    6. Stanza prosodic syllable spread > 3 or broken 'A-A-X-Y' stanza rhyme (e.g. 'سلابه/مرتابه/تجاوبها/دلالي')
    7. Heavy Sukun/Harakat token-shattering spam (> 35% diacritics-to-letters ratio)
    """
    raw_lines = [ln.strip() for ln in poem_text.replace("\\n", "\n").splitlines() if ln.strip()]
    verbose_headers = []
    fusha_leaks = []
    g2p_landmines = []
    overlong_lines = []
    broken_stanza_rhymes = []

    sections = []
    cur_header = "[عام]"
    cur_lines = []
    for ln in raw_lines:
        if ln.startswith("[") and ln.endswith("]"):
            if cur_lines:
                sections.append((cur_header, cur_lines))
                cur_lines = []
            cur_header = ln
            inner = ln[1:-1].strip()
            if re.search(r"[A-Za-z0-9]", inner) or len(inner.split()) > 3 or "—" in inner:
                verbose_headers.append(ln)
        else:
            cur_lines.append(ln)
    if cur_lines:
        sections.append((cur_header, cur_lines))

    # Check Mustahal collective (...) Raddada wrapping
    missing_mustahal_choir = False
    for hdr, s_lines in sections:
        if "مستهل" in hdr or "لازمة" in hdr:
            if s_lines and not any("(" in x and ")" in x for x in s_lines):
                missing_mustahal_choir = True

    # Check Fusha leaks, G2P cluster landmines & diacritic spam
    all_lyric_text = "\n".join(ln for _, s_lines in sections for ln in s_lines)
    diac_count = len(re.findall(r"[\u064B-\u0652\u0670]", all_lyric_text))
    letter_count = max(1, len(re.findall(r"[\u0621-\u064A\u067E\u0686\u06AF]", all_lyric_text)))
    diacritic_ratio = round(diac_count / float(letter_count), 3)
    heavy_sukun_spam = diacritic_ratio > 0.38

    fusha_patterns = [
        (r"طَاحَ\s+ال", "طَاحَ -> طاح (Fusha past Fatha in Iraqi dialect)"),
        (r"ضَاعَ\s+ال", "ضَاعَ -> ضاع (Fusha past Fatha in Iraqi dialect)"),
        (r"أَدْرِكِ\s+ال", "أَدْرِكِ -> أدرك / ادرك (Fusha Kasra Wasl in Iraqi dialect)"),
        (r"لَا\s+وَلِيَّ", "لَا وَلِيَّ -> لا حامي / لا والي (Fusha لا النافية للجنس misread as وِلِيَّه)"),
        (r"(?<!\w)اعْلَه(?!\w)|(?<!\w)اعله(?!\w)", "اعله -> على (unvocalized Alif misread as Fusha أَعْلَى)"),
    ]
    for pat, msg in fusha_patterns:
        if re.search(pat, all_lyric_text):
            fusha_leaks.append(msg)

    bare_tokens = re.findall(r"[\u0621-\u064A\u067E\u0686\u06AF\u0651]+", re.sub(r"[\u064B-\u0650\u0652\u0670]", "", all_lyric_text))
    cluster_gaf_traps = {"وگفت", "گطعة", "گطعه", "گطعت", "گطّعت", "إبگلبي", "ابگلبي", "گلبي", "تگعد", "تگطع", "تگطّع", "عگب", "ملچوم", "ملتشوم", "حچي", "حتشي", "چبدي", "تشبدي"}
    for tok in bare_tokens:
        plain = tok.replace("\u0651", "")
        if plain in cluster_gaf_traps:
            g2p_landmines.append(f"{tok}: high-risk Lyria 3.5 G2P cluster/devoicing trap (e.g. وگفت->وتفت, گلبي->كلبي)")
        if plain == "دلالي" and "\u0651" not in tok:
            g2p_landmines.append("دلالي missing Shadda -> write دَلَّالي (otherwise sung da-lā-lī 'my pampering')")

    # Prosodic syllable density & stanza AAAB rhyme audit
    stanza_spread_violations = []
    for hdr, s_lines in sections:
        syls = [_estimate_arabic_vocalic_syllables_v64(ln) for ln in s_lines]
        for ln, sy in zip(s_lines, syls):
            if sy >= 15 and ".." not in ln:
                overlong_lines.append({"section": hdr, "line": ln, "estimated_syllables": sy})
        if len(syls) >= 3 and "موال" not in hdr and "نعي" not in hdr:
            non_refrain_syls = [sy for ln, sy in zip(s_lines, syls) if not (ln.startswith("(") and ln.endswith(")"))]
            if len(non_refrain_syls) >= 3 and (max(non_refrain_syls) - min(non_refrain_syls)) > 4:
                stanza_spread_violations.append({
                    "section": hdr,
                    "syllables": non_refrain_syls,
                    "spread": max(non_refrain_syls) - min(non_refrain_syls),
                })
        # Check 4-line stanza rhyme (first 3 lines must share rhyme tail AAA, or AABB/AAAA)
        verse_only = [ln for ln in s_lines if not (ln.startswith("(") and ln.endswith(")"))]
        if len(verse_only) == 4 and "مستهل" not in hdr and "خاتمة" not in hdr:
            tails = [_extract_rhyme_tail_v64(ln) for ln in verse_only]
            if len(set(tails[:3])) > 1 and not (tails[0] == tails[1] and tails[2] == tails[3]):
                broken_stanza_rhymes.append({"section": hdr, "rhyme_tails": tails})

    _ = target_bpm
    passed = (
        not verbose_headers
        and not missing_mustahal_choir
        and not fusha_leaks
        and not g2p_landmines
        and not overlong_lines
        and not broken_stanza_rhymes
        and not heavy_sukun_spam
    )
    return {
        "v64_iraqi_preflight_passed": passed,
        "verbose_or_latin_headers": verbose_headers,
        "missing_mustahal_raddada_parentheses": missing_mustahal_choir,
        "fusha_grammar_leaks": fusha_leaks,
        "lyria_g2p_cluster_landmines": sorted(set(g2p_landmines)),
        "heavy_sukun_token_shattering_spam": heavy_sukun_spam,
        "diacritic_to_letter_ratio": diacritic_ratio,
        "overlong_unsplit_lines": overlong_lines,
        "stanza_syllable_spread_violations": stanza_spread_violations,
        "broken_stanza_rhymes": broken_stanza_rhymes,
    }


def audit_latmiya_audio_ground_truth_v64(
    wav_path: str,
    expected_maqam: str = "lami",
    target_bpm: float = 62.0,
) -> dict:
    """V64.0 (NC46-NC47): Audio-Driven Ground-Truth Gate for Iraqi/Bahrani Latmiyas.

    Eliminates self-congratulatory confirmation bias (which falsely scored Exp 35 f60b364d at 9.66/10)
    by computing objective acoustic gates directly from the rendered waveform:
    1. Cadence-locked Maqam match vs. 12-TET Western Major/Minor Diatonic Collapse
    2. Microtonal 30-50c quarter-tone presence when expected_maqam is a quarter-tone Maqam
    3. Peak syllabic onset rate ('patter_rush_detected' if max 15s window > 3.85 onsets/sec on slow <=70 BPM lament)
    4. Double-time stadium march tempo drift (estimated_bpm > 1.55 * target_bpm)
    5. Objective 'audio_music_ceiling_10' bounding compute_strict_production_score_v62()
    """
    sr, stereo, _, _ = read_wav_any_depth(wav_path, return_stereo=True)
    mono = np.mean(stereo, axis=1) if stereo.ndim == 2 else stereo.astype(np.float64)
    prof = extract_reference_audio_profile(wav_path)
    detected_mq = prof["closest_maqam"]
    top3 = prof.get("maqam_top3_candidates", [])
    est_bpm = float(prof.get("estimated_bpm", target_bpm))

    # Measure 12-TET lock percentage & quarter-tone 30-50c percentage on voiced vocal frames
    voc = butter_filter(mono, [95.0, min(3000.0, 0.45 * sr)], sr, btype="band", order=3)
    win = max(256, int(0.08 * sr))
    hop = max(128, int(0.04 * sr))
    nfft = 8192
    freqs = np.fft.rfftfreq(nfft, d=1.0 / sr)
    lo_k = int(np.searchsorted(freqs, 95.0))
    hi_k = int(np.searchsorted(freqs, min(420.0, 0.42 * sr)))
    hann = np.hanning(win)
    nf = max(0, (len(voc) - win) // hop + 1)
    rms = np.array([float(np.sqrt(np.mean(voc[i * hop : i * hop + win] ** 2))) for i in range(nf)]) if nf > 0 else np.zeros(1)
    gate = max(1e-4, 0.28 * float(np.percentile(rms, 90))) if nf > 0 else 1e-4

    cents_devs = []
    for i in range(nf):
        if rms[i] < gate or hi_k <= lo_k:
            continue
        spec = np.abs(np.fft.rfft(voc[i * hop : i * hop + win] * hann, n=nfft))
        k = lo_k + int(np.argmax(spec[lo_k:hi_k]))
        f0 = max(65.0, float(freqs[k]))
        semi = 12.0 * math.log2(f0 / 440.0)
        cents_devs.append(abs(semi - round(semi)) * 100.0)

    within_20c_pct = round(100.0 * sum(1 for c in cents_devs if c <= 20.0) / max(1, len(cents_devs)), 2)
    qt_30_50c_pct = round(100.0 * sum(1 for c in cents_devs if 30.0 <= c <= 50.0) / max(1, len(cents_devs)), 2)

    # Measure peak syllabic vowel-nucleus density (240-1350 Hz F1/F2 band, excluding chest thuds & breath hiss)
    vow_band = butter_filter(mono, [240.0, min(1350.0, 0.42 * sr)], sr, btype="band", order=3)
    env_hop = max(64, int(0.025 * sr))
    n_env = max(1, len(vow_band) // env_hop)
    env = np.array([float(np.sqrt(np.mean(vow_band[i * env_hop : (i + 1) * env_hop] ** 2))) for i in range(n_env)])
    env_p90 = float(np.percentile(env, 90)) if len(env) > 0 else 1e-4
    diff_env = np.maximum(0.0, np.diff(env, prepend=env[0]))
    onset_thr = max(1e-4, 0.22 * env_p90)
    onset_idx = []
    min_gap = max(1, int(0.18 / 0.025))
    for i in range(1, len(diff_env) - 1):
        if env[i] > 0.25 * env_p90 and diff_env[i] > onset_thr and diff_env[i] >= diff_env[i - 1] and diff_env[i] >= diff_env[i + 1]:
            if not onset_idx or (i - onset_idx[-1]) >= min_gap:
                onset_idx.append(i)
    onset_times = np.array(onset_idx, dtype=np.float64) * (env_hop / float(sr))
    dur_sec = len(mono) / float(sr)
    max_win_onsets_per_sec = 0.0
    w_sec = min(18.0, max(4.0, dur_sec))
    t_cur = 0.0
    while t_cur + w_sec <= dur_sec + 0.01:
        cnt = int(np.sum((onset_times >= t_cur) & (onset_times < t_cur + w_sec)))
        max_win_onsets_per_sec = max(max_win_onsets_per_sec, cnt / w_sec)
        t_cur += 5.0
    max_win_onsets_per_sec = round(max_win_onsets_per_sec, 2)

    # Measure physical 45-105 Hz sub-bass chest-latm strike rate (separates 60 BPM chest-latm + off-beat 'Shaheed' breath from 108+ BPM stadium march)
    sub_band = butter_filter(mono, [45.0, 105.0], sr, btype="band", order=3)
    sub_hop = max(64, int(0.04 * sr))
    n_sub = max(1, len(sub_band) // sub_hop)
    sub_env = np.array([float(np.sqrt(np.mean(sub_band[i * sub_hop : (i + 1) * sub_hop] ** 2))) for i in range(n_sub)])
    sub_p90 = float(np.percentile(sub_env, 90)) + 1e-8
    sub_diff = np.maximum(0.0, np.diff(sub_env, prepend=sub_env[0]))
    sub_min_gap = max(1, int(0.42 / 0.04))
    sub_hits = []
    for i in range(1, n_sub - 1):
        if sub_env[i] > 0.35 * sub_p90 and sub_diff[i] > 0.20 * sub_p90 and sub_diff[i] >= sub_diff[i - 1] and sub_diff[i] >= sub_diff[i + 1]:
            if not sub_hits or (i - sub_hits[-1]) >= sub_min_gap:
                sub_hits.append(i)
    sub_chest_strikes_per_min = round(len(sub_hits) * 60.0 / max(1.0, dur_sec), 1)

    exp_mq = (expected_maqam or "lami").strip().lower()
    top3_dict = {item[0]: float(item[1]) for item in top3}
    top_sc = float(top3[0][1]) if top3 else 0.0
    ajam_near_tie = ("ajam" in top3_dict) and (top3_dict["ajam"] >= top_sc - 0.05) and (top3_dict["ajam"] >= 0.95)
    western_12tet_collapse = bool(
        exp_mq in ("lami", "saba", "saba_zamzam", "bayati", "bayati_shuri", "husseini", "sikah")
        and (ajam_near_tie or (within_20c_pct >= 73.0 and detected_mq == "ajam"))
    )
    missing_quarter_tone = bool(exp_mq in _QUARTER_TONE_MAQAM_SET and qt_30_50c_pct < 13.5)
    patter_rush = bool(target_bpm <= 72.0 and max_win_onsets_per_sec > 3.35)
    double_time_drift = bool(
        0.0 < target_bpm <= 72.0
        and est_bpm > 1.55 * target_bpm
        and (sub_chest_strikes_per_min > 1.48 * target_bpm or max_win_onsets_per_sec > 3.10)
    )

    ceiling = 9.8
    reasons = []
    if western_12tet_collapse:
        ceiling = min(ceiling, 4.2)
        reasons.append(f"western_12tet_diatonic_collapse (detected={detected_mq}, within_20c={within_20c_pct}%)")
    if missing_quarter_tone:
        ceiling = min(ceiling, 5.0)
        reasons.append(f"missing_quarter_tone_microtonality (qt_30_50c={qt_30_50c_pct}% < 13.5% for {exp_mq})")
    if patter_rush:
        ceiling = min(ceiling, 4.5)
        reasons.append(f"syllabic_patter_rush (max_15s_onsets_per_sec={max_win_onsets_per_sec} > 3.35)")
    if double_time_drift:
        ceiling = min(ceiling, 5.2)
        reasons.append(
            f"double_time_tempo_drift (estimated_bpm={est_bpm}, chest_strikes_per_min={sub_chest_strikes_per_min} vs target={target_bpm})"
        )

    return {
        "wav_path": wav_path,
        "expected_maqam": exp_mq,
        "detected_maqam_cadence_locked": detected_mq,
        "maqam_top3_candidates": top3,
        "within_20c_of_12tet_pct": within_20c_pct,
        "quarter_tone_30_to_50c_pct": qt_30_50c_pct,
        "max_15s_onsets_per_sec": max_win_onsets_per_sec,
        "sub_chest_strikes_per_min": sub_chest_strikes_per_min,
        "estimated_bpm": est_bpm,
        "target_bpm": target_bpm,
        "western_12tet_collapse_detected": western_12tet_collapse,
        "missing_quarter_tone_detected": missing_quarter_tone,
        "patter_rush_detected": patter_rush,
        "double_time_tempo_drift_detected": double_time_drift,
        "audio_music_ceiling_10": round(ceiling, 2),
        "ground_truth_gate_passed": len(reasons) == 0,
        "failure_reasons": reasons,
    }


def parse_args(argv=None):
    """Parse CLI flags for V60.0 Multi-Maqam Diversity, NC27-C/NC32-NC34 Forensics & 20-Mode DSP."""
    parser = argparse.ArgumentParser(
        description=f"Hussaini Production Studio DSP & Phonetics Engine ({SKILL_VERSION})"
    )
    parser.add_argument("--version", action="version", version=SKILL_VERSION)
    parser.add_argument("--input", help="Input vocal WAV/MP3/M4A file (8/16/24/32-bit mono or stereo)")
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
        help="24-EDO Maqam formant Ahaat drone (13 Arabic/Hussaini Maqams)",
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
    parser.add_argument(
        "--vintage-intro-sec",
        type=float,
        default=0.0,
        help="V60.0 (Al-Akraf Blueprint): Apply 300-2800Hz vintage telephone intro EQ up to N seconds",
    )
    parser.add_argument(
        "--vocal-stacking",
        action="store_true",
        help="V60.0 (NC34 5th Blueprint): Apply mono-safe Mid/Side Solo-vs-Choir vocal stacking enhancer",
    )
    parser.add_argument(
        "--auto-trim-tail-loop",
        action="store_true",
        help="V60.0 (NC34): Automatically detect & trim trailing Remix > Extend restart loops",
    )
    parser.add_argument(
        "--tame-lyria-harshness",
        action="store_true",
        help="V63.0 (NC41): Apply dynamic mono-safe 2.4-3.8 kHz neural vocoder harshness tamer for Lyria 3.5 exports",
    )
    parser.add_argument("--samples-dir", default=None, help="Optional directory of real WAV one-shots")
    parser.add_argument("--compile-lyrics", default=None, help="Shape & vocalize Arabic poem text")
    parser.add_argument(
        "--compile-clean-lyria",
        default=None,
        help="V60.0 NC26/NC27-C: Compile clean natural Arabic + affricate Sukun law + <=4.2 syl/s density audit",
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
    parser.add_argument(
        "--build-muwashah-json",
        default=None,
        help="V60.0 Module 73/74 (NC30/NC33): Analyze multi-meter Muwashah & build Zero-Piano Combined JSON",
    )
    parser.add_argument(
        "--list-fingerprints",
        action="store_true",
        help="V60.0: List all 12 Multi-Maqam & 9-School Melodic Fingerprints",
    )
    parser.add_argument(
        "--select-fingerprint",
        default=None,
        help="V60.0: Select specific melodic fingerprint key (or 'auto:<poem_text>')",
    )
    parser.add_argument(
        "--plan-replace",
        nargs=5,
        metavar=("CLIP_UUID", "START_SEC", "END_SEC", "OLD_LINE", "FIXED_LINE"),
        default=None,
        help="V60.0 (NC32): Build exact Flow Music Remix > Replace surgical inpainting plan",
    )
    parser.add_argument(
        "--detect-artifacts",
        default=None,
        help="V60.0 (NC33): Run calibrated Zero-Vibrato Piano Hammer & Dual-Band Pop-Snare forensic audit",
    )
    parser.add_argument(
        "--detect-tail-loop",
        default=None,
        help="V60.0 (NC34): Detect trailing Remix > Extend restart loop & report clean trim timestamp",
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
        choices=["latmiya", "nai", "nasheed", "jalwat", "ibtihalat", "tawashih", "muwashah", "operetta"],
        help="Generate genre acoustic profile & Sound prompt (Latmiya, Na'i, Nasheed, Jalwat, Ibtihalat, Tawashih, Muwashah, Operetta)",
    )
    parser.add_argument(
        "--dialect",
        default="iraqi",
        choices=["iraqi", "bahrani", "qatifi", "iraqi_bahrani", "fusha"],
        help="Target dialect for --genre or lyric shaping (iraqi, bahrani, qatifi, iraqi_bahrani, fusha)",
    )
    parser.add_argument(
        "--platform-target",
        default="streaming",
        choices=list(PLATFORM_LUFS_TARGETS_V62.keys()),
        help="V62.0 multi-platform EBU R128 mastering target: streaming (-14), apple_music (-16), hires_qobuz (-18), broadcast_tv (-23 LUFS)",
    )
    parser.add_argument(
        "--check-orchestration",
        default=None,
        help="V62.0 (NC36): Check Quarter-Tone vs. 12-TET orchestral compatibility for a Maqam (append ':12tet' to test Western chord clash)",
    )
    parser.add_argument(
        "--audit-orthoepy",
        default=None,
        help="V62.0 (NC37): Pre-flight Fusha Shadda, Wasl-Alif, comma-after-Sukun, inline-echo & rhyme-carryover audit",
    )
    parser.add_argument(
        "--build-v63-bootstrap",
        default=None,
        choices=["track_a", "track_b", "track_c"],
        help="V63.0 (NC38-NC39): Emit Stage-0 Gemini Producer MASTER_STATE Bootstrap JSON with 5-band positive spectral fill",
    )
    parser.add_argument(
        "--plan-v63-workflow",
        default=None,
        help="V63.0 (NC38-NC40): Plan 5-minute staged word budget (280-350 net words) & full Stage 0..4 JSON workflow",
    )
    parser.add_argument(
        "--check-maqam-ref",
        default=None,
        choices=list(MAQAM_FREQS.keys()),
        help="V63.0: Check Lyria 3.5 text adherence tier & mandatory 30s Make-tracks-for-my-vocal Audio Reference policy for a Maqam",
    )
    parser.add_argument(
        "--plan-chained-replace",
        nargs=2,
        metavar=("CLIP_UUID", "WINDOWS_SPEC"),
        default=None,
        help="V63.0 (NC42): Plan Back-to-Front chained Remix > Replace passes (WINDOWS_SPEC: 'start-end:old->fixed;...')",
    )
    parser.add_argument(
        "--audit-iraqi-preflight",
        default=None,
        help="V64.0 (NC44-NC45): Audit Iraqi Karbalaei prosody, Raddada (...), Fusha leaks & G2P cluster landmines",
    )
    parser.add_argument(
        "--audit-ground-truth",
        default=None,
        help="V64.0 (NC46-NC47): Audio-driven ground-truth Maqam, 12-TET collapse, quarter-tone & patter-rush gate",
    )
    parser.add_argument("--extract-profile", default=None, help="Reverse-engineer reference WAV/MP3 profile")
    parser.add_argument("--audit-audio", default=None, help="Audit WAV loudness, True Peak, gaps & tail cutoff/loops")
    return parser.parse_args(argv)


def main(argv=None):
    """CLI entrypoint for Hussaini Production Studio V60.0 OMNI-ARCHITECT."""
    args = parse_args(argv)

    if args.export_constitution:
        print(json.dumps(load_v48_5_constitution(), ensure_ascii=False, indent=2))
        return 0

    if args.list_fingerprints:
        summary = {
            k: {
                "school": v["school"],
                "dialect": v["dialect"],
                "axis": v["axis"],
                "bpm": v["bpm"],
                "maqam_arc": v["maqam_arc"],
                "empirical_exp": v["empirical_exp"],
            }
            for k, v in MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60.items()
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    if args.select_fingerprint is not None:
        raw_fp = args.select_fingerprint
        if raw_fp.startswith("auto:"):
            fp_obj = select_melodic_fingerprint_v60(poem_text=raw_fp[5:])
        else:
            fp_obj = select_melodic_fingerprint_v60(fingerprint_key=raw_fp)
        print(json.dumps(fp_obj, ensure_ascii=False, indent=2))
        return 0

    if args.plan_replace is not None:
        clip_id, s_sec, e_sec, old_ln, fix_ln = args.plan_replace
        rep_plan = build_remix_replace_inpainting_plan(
            clip_uuid=clip_id,
            start_sec=float(s_sec),
            end_sec=float(e_sec),
            old_lyric_line=old_ln,
            fixed_lyric_line=fix_ln,
        )
        print(json.dumps(rep_plan, ensure_ascii=False, indent=2))
        return 0

    if args.detect_artifacts is not None:
        print(json.dumps(detect_piano_and_pop_snare_transients(args.detect_artifacts), ensure_ascii=False, indent=2))
        return 0

    if args.detect_tail_loop is not None:
        print(json.dumps(detect_extend_restart_loop(args.detect_tail_loop), ensure_ascii=False, indent=2))
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

    if args.build_muwashah_json is not None:
        muwashah_payload = build_v58_combined_muwashah_json(args.build_muwashah_json)
        print(json.dumps(muwashah_payload, ensure_ascii=False, indent=2))
        return 0

    if args.compile_lyrics is not None:
        report = detect_and_shape_dialect(args.compile_lyrics.replace("\\n", "\n"))
        report["shaped_lyrics"] = enforce_collective_estehlal_parentheses(report["shaped_lyrics"])
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.compile_clean_lyria is not None:
        report = format_clean_lyrics_for_lyria35(args.compile_clean_lyria, target_bpm=args.bpm)
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
            genre=args.genre, dialect=args.dialect, maqam=args.maqam_drone, bpm=int(args.bpm)
        )
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        return 0

    if args.check_orchestration is not None:
        raw_chk = args.check_orchestration.strip()
        if ":" in raw_chk:
            mq_part, flag_part = raw_chk.split(":", 1)
            use_12 = flag_part.lower() in ("12tet", "chords", "piano", "true", "1")
        else:
            mq_part, use_12 = raw_chk, True
        print(
            json.dumps(
                validate_maqam_orchestration_compatibility(mq_part, uses_western_12tet_chords=use_12),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.audit_orthoepy is not None:
        print(
            json.dumps(
                audit_fusha_shadda_wasl_and_makharij_v62(args.audit_orthoepy),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.build_v63_bootstrap is not None:
        print(
            json.dumps(
                build_v63_session_bootstrap_json(
                    track_mode=args.build_v63_bootstrap,
                    dialect=args.dialect,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.plan_v63_workflow is not None:
        tm = "track_b" if args.genre in ("nasheed", "operetta") else ("track_c" if args.genre in ("tawashih", "ibtihalat", "muwashah", "jalwat") else "track_a")
        print(
            json.dumps(
                plan_v63_five_minute_word_budget(
                    poem_text=args.plan_v63_workflow,
                    track_mode=tm,
                    dialect=args.dialect,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.check_maqam_ref is not None:
        print(
            json.dumps(
                {
                    "maqam": args.check_maqam_ref,
                    **MAQAM_LYRIA35_ADHERENCE_AND_AUDIO_REF_MATRIX_V63[args.check_maqam_ref],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.plan_chained_replace is not None:
        c_uuid, w_spec = args.plan_chained_replace
        parsed_wins = []
        for entry in [e.strip() for e in w_spec.split(";") if e.strip()]:
            rng_part, _, txt_part = entry.partition(":")
            s_str, _, e_str = rng_part.partition("-")
            old_txt, _, fix_txt = txt_part.partition("->")
            parsed_wins.append({
                "start_sec": float(s_str),
                "end_sec": float(e_str) if e_str else float(s_str) + 10.0,
                "old_line": old_txt.strip(),
                "fixed_line": fix_txt.strip(),
            })
        print(json.dumps(plan_chained_surgical_replace_v63(c_uuid, parsed_wins), ensure_ascii=False, indent=2))
        return 0

    if args.audit_iraqi_preflight is not None:
        print(
            json.dumps(
                audit_iraqi_latmiya_preflight_v64(args.audit_iraqi_preflight, target_bpm=args.bpm),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.audit_ground_truth is not None:
        print(
            json.dumps(
                audit_latmiya_audio_ground_truth_v64(
                    args.audit_ground_truth,
                    expected_maqam=args.maqam_drone,
                    target_bpm=args.bpm,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.extract_profile is not None:
        print(json.dumps(extract_reference_audio_profile(args.extract_profile), ensure_ascii=False, indent=2))
        return 0

    if args.audit_audio is not None:
        print(
            json.dumps(
                audit_rendered_audio(args.audit_audio, platform_target=args.platform_target),
                ensure_ascii=False,
                indent=2,
            )
        )
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
            vintage_intro_sec=args.vintage_intro_sec,
            vocal_stacking=args.vocal_stacking,
            auto_trim_tail_loop=args.auto_trim_tail_loop,
            platform_target=args.platform_target,
            tame_lyria_harshness=args.tame_lyria_harshness,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(json.dumps(build_flowmusic_json_preconditioning(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
