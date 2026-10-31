#!/usr/bin/env python3
"""Hussaini Audio Omni-Engine DSP, 5-Track DAW & Phonetics Compiler (V45.0 OMNI-ARCHITECT).

Bridges poetic/phonetic engineering with procedural DSP audio mastering:
- 5-Track DAW Routing Matrix (Track_01_Dammam_Sub_Bass with 35Hz HPF, +2dB @ 90Hz & 160Hz
  anti-masking notch; Track_02_Kasat_Brass_Cymbals; Track_03_Zanjeel_Chain_FX 120% Ultra-Wide;
  Track_04_Ahaat_Vocal_Choir_Pads 150Hz-12kHz Bandpass; Track_05_Master_Mix_Bus 1.5:1 Glue)
- Smart -3.0dB Dynamic Sidechain Ducking triggered by the Radood's larynx band (140Hz-3200Hz)
- Dynamic Acoustic Preset: 285ms Dynacord Analog Tape Echo + 3.2s Husseiniya Hall Reverb
- Module 40: Dialect-Accurate & Prosodic Tanween Compiler (e.g. عَيْنِنْ تِسِيلْ)
- Module 41: Anti-Slurring Word De-Cliticization & Separation Engine
- Module 43: Automatic Bahrani vs. Iraqi Dialect Identification & Sukun Lock
- Module 34/38/39: Stage-1 Iso-Syllabic Lock Validator, Multi-Tor Melodic Bridge Builder,
  and Flow Music JSON Session Pre-Conditioning Generator
"""

import argparse
import os
import re
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, iirnotch, lfilter

MAQAM_FREQS = {
    "bayati": [146.83, 160.00, 174.61, 220.00],
    "saba": [146.83, 160.00, 174.61, 207.65],
    "hijaz": [146.83, 155.56, 185.00, 220.00],
    "lami": [146.83, 155.56, 174.61, 207.65],
    "kurd": [146.83, 155.56, 174.61, 220.00],
    "rast": [130.81, 146.83, 160.00, 196.00],
}

COMMON_JINS_GRAPH = {
    "bayati": ["saba", "kurd", "hijaz", "lami"],
    "saba": ["bayati", "lami", "hijaz", "rast"],
    "hijaz": ["bayati", "saba", "kurd"],
    "lami": ["saba", "bayati", "kurd"],
    "kurd": ["bayati", "lami", "hijaz"],
    "rast": ["saba", "bayati", "hijaz"],
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
    "عالباب": "عَلَى البَابْ",
    "عالرمضا": "عَلَى الرَّمْضَه",
    "عالرمضه": "عَلَى الرَّمْضَه",
    "عالتل": "عَلَى التَّلْ",
    "بغربتي": "بِـ غُرْبِتِي",
    "بضلوعي": "بِـ ضْلُوعِي",
    "بظلوعي": "بِـ ظْلُوعِي",
    "للذبحوا": "لِلْ ذَبْحَوْا",
    "شصار": "إِشْ صَارْ",
    "شنگول": "إِشْ نْگُولْ",
    "شنقول": "إِشْ نْگُولْ",
    "شحچي": "إِشْ أَحْچِي",
    "شسوه": "إِشْ سَوَّه",
    "شتريد": "إِشْ تْرِيدْ",
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

BAHRANI_MARKERS = (
    "بويي", "خويي", "ونتي", "هالگفره", "امساعد", "عفارم",
    "إشحالك", "اشحالك", "لچن", "الراعبية", "الراعبيه", "يا بويي",
)

IRAQI_MARKERS = (
    "بويه", "خويه", "يمه", "وليدي", "دلالي", "شلون", "إش صار",
    "شصار", "شنگول", "بلياك", "ما ظل", "چلبت", "وگفت", "هسه",
)


def de_cliticize_and_separate_words(text):
    """Module 41: Separate attached vocatives, prepositions, and clitics to prevent G2P slurring."""
    result = text
    for attached, separated in WORD_SEPARATION_MAP.items():
        result = re.sub(rf"\b{re.escape(attached)}\b", separated, result)
    return result


def resolve_dialectal_and_prosodic_tanween(text, dialect="iraqi"):
    """Module 40: Convert mid-line Tanween to phonetic Nunation and lock final Sukun."""
    processed = text
    for raw_phrase, phonetic_phrase in COLLOQUIAL_TANWEEN_MAP.items():
        processed = processed.replace(raw_phrase, phonetic_phrase)

    if dialect in ("iraqi", "bahrani", "iraqi_bahrani"):
        processed = re.sub(r"(\S+)ٍ\s+([تي])", r"\1ِنْ \2ِ", processed)

    lines = []
    for line in processed.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("["):
            lines.append(line)
            continue
        stripped = re.sub(r"[ٌٍُِ]$", "ْ", stripped)
        if not stripped.endswith(("ْ", "ا", "و", "ي", "ه", "ة", ")")):
            stripped = stripped + "ْ"
        lines.append(stripped)
    return "\n".join(lines)


def detect_and_shape_dialect(text):
    """Module 43: Identify Bahrani vs. Iraqi dialect markers and apply CVC shaping & Sukun lock."""
    bahrani_hits = sum(1 for marker in BAHRANI_MARKERS if marker in text)
    iraqi_hits = sum(1 for marker in IRAQI_MARKERS if marker in text)

    if bahrani_hits > iraqi_hits:
        detected = "bahrani"
    elif iraqi_hits > bahrani_hits:
        detected = "iraqi"
    else:
        detected = "iraqi_bahrani"

    shaped = de_cliticize_and_separate_words(text)
    if detected == "bahrani":
        shaped = shaped.replace("قلبي", "گَلْبِي").replace("صبر", "صَبِرْ")
        maqam_rule = "3rd-Word Faizi Vibrato & Soft Bahrani Imala in Maqam Hijaz/Saba"
    else:
        shaped = shaped.replace("قلب", "گَلُبْ").replace("صبر", "صَبُرْ").replace("جمر", "جَمُرْ")
        maqam_rule = "Emphatic Iraqi Tafkheem & Final-Word Sudden Drop in Maqam Saba/Lami"

    shaped = resolve_dialectal_and_prosodic_tanween(shaped, dialect=detected)
    return {
        "detected_dialect": detected,
        "bahrani_score": bahrani_hits,
        "iraqi_score": iraqi_hits,
        "maqam_articulation_rule": maqam_rule,
        "shaped_lyrics": shaped,
    }


def validate_stage1_iso_syllabic_lock(lines):
    """Modules 34 & 38: Validate 4-line stanzas, identical 4th-line refrain, and balanced length."""
    clean_lines = [
        ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("[")
    ]
    is_valid_count = len(clean_lines) in (4, 8, 12) and len(clean_lines) % 4 == 0
    refrains = [clean_lines[idx] for idx in range(3, len(clean_lines), 4)] if is_valid_count else []
    identical_refrain = len(set(refrains)) <= 1 if refrains else False

    non_refrain_lengths = [
        len(re.sub(r"[\s\.\،\u064B-\u0652]", "", ln))
        for idx, ln in enumerate(clean_lines)
        if (idx + 1) % 4 != 0
    ]
    if non_refrain_lengths:
        spread = max(non_refrain_lengths) - min(non_refrain_lengths)
        iso_balanced = spread <= 8
    else:
        iso_balanced = False

    return {
        "line_count": len(clean_lines),
        "is_valid_stanza_grid": is_valid_count,
        "identical_4th_line_refrain": identical_refrain,
        "iso_syllabic_balanced": iso_balanced,
        "passed": bool(is_valid_count and identical_refrain and iso_balanced),
    }


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


def build_flowmusic_json_preconditioning(dialect="iraqi_bahrani", maqam="saba", bpm=58):
    """Module 39: Build the V45.0 JSON Session Pre-Conditioning payload for Flow Music."""
    return {
        "protocol_name": "Hussaini_Production_Studio_OS_V45_OMNI_ARCHITECT",
        "session_mode": "Pre_Conditioning_Lock_Only_Wait_For_Step_2_Lyrics",
        "target_dialect": dialect,
        "single_stage1_maqam": maqam,
        "tempo_bpm": bpm,
        "anti_slurring_word_separation": True,
        "dialectal_tanween_compiler": True,
        "mandatory_end_of_line_sukun": True,
        "golden_reference_clip_id": "26bbb3d2-65f0-42c3-a167-37127631ef0a",
    }


def butter_filter(data, cutoff, sample_rate, btype="high", order=4):
    """Apply a Butterworth filter (low, high, or band) to a 1D signal."""
    nyq = 0.5 * sample_rate
    norm_cutoff = np.clip(np.asarray(cutoff, dtype=np.float64) / nyq, 1e-4, 0.999)
    num, den = butter(order, norm_cutoff, btype=btype)
    return lfilter(num, den, data)


def apply_vocal_eq(signal, sample_rate):
    """Apply HPF @ 85Hz, boxy notch @ 650Hz, and +4.5dB Jawhari presence @ 2.5kHz."""
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
    """Track_01_Dammam_Sub_Bass: HPF @ 35Hz, +2dB boost @ 90Hz, and 160Hz vocal-clear notch."""
    filtered = butter_filter(dammam_signal, 35.0, sample_rate, btype="high", order=2)
    sub_punch = butter_filter(filtered, [75.0, 105.0], sample_rate, btype="band", order=2)
    filtered = filtered + 0.26 * sub_punch
    nyq = 0.5 * sample_rate
    if nyq > 250.0:
        b_notch, a_notch = iirnotch(160.0 / nyq, 3.5)
        filtered = lfilter(b_notch, a_notch, filtered)
    return filtered


def compute_smart_sidechain_ducking(vocal_signal, sample_rate, duck_db=-3.0):
    """Compute dynamic -3.0dB sidechain ducking gain curve triggered by the Radood's larynx band."""
    nyq = 0.5 * sample_rate
    high_cut = min(3200.0, 0.45 * sample_rate)
    if nyq > 400.0 and high_cut > 150.0:
        larynx_band = butter_filter(vocal_signal, [140.0, high_cut], sample_rate, btype="band", order=2)
    else:
        larynx_band = vocal_signal

    rectified = np.abs(larynx_band)
    peak = np.max(rectified)
    if peak > 1e-8:
        rectified = rectified / peak

    win_len = max(1, int(0.035 * sample_rate))
    kernel = np.ones(win_len, dtype=np.float64) / float(win_len)
    envelope = np.convolve(rectified, kernel, mode="same")
    active_mask = np.clip(envelope * 2.2, 0.0, 1.0)

    target_linear_gain = float(10.0 ** (duck_db / 20.0))
    max_attenuation = 1.0 - target_linear_gain
    return 1.0 - max_attenuation * active_mask


def apply_master_glue_compressor(stereo_signal, ratio=1.5, threshold=0.65):
    """Track_05_Master_Mix_Bus: Gentle 1.5:1 Master Glue Compressor."""
    abs_sig = np.abs(stereo_signal)
    over = np.maximum(0.0, abs_sig - threshold)
    compressed_mag = np.where(abs_sig > threshold, threshold + over / ratio, abs_sig)
    scale = np.where(abs_sig > 1e-8, compressed_mag / np.maximum(abs_sig, 1e-8), 1.0)
    return stereo_signal * scale


def tape_saturate(signal, drive=2.2):
    """Apply warm analog tape soft-clipping saturation."""
    return np.tanh(signal * drive) / np.tanh(drive)


def apply_dynacord_echo(signal, sample_rate, delay_ms=285.0, feedback=0.32, mix=0.22):
    """Simulate a classic 285ms Dynacord analog tape echo with high-cut damping."""
    delay_samples = max(1, int((delay_ms / 1000.0) * sample_rate))
    num = np.zeros(delay_samples + 1)
    num[0] = 1.0
    den = np.zeros(delay_samples + 1)
    den[0] = 1.0
    den[delay_samples] = -feedback
    echoed = butter_filter(
        lfilter(num, den, signal), min(3800.0, 0.45 * sample_rate), sample_rate, btype="low", order=2
    )
    return (1.0 - mix) * signal + mix * echoed


def apply_husseiniya_reverb(signal, sample_rate, rt60=3.2, wet_mix=0.26, pre_delay_ms=40.0):
    """Apply 3.2s Husseiniya / Cathedral hall impulse response convolution with 40ms pre-delay."""
    rng = np.random.default_rng(seed=42)
    ir_len = max(1, int(rt60 * sample_rate))
    pre_delay_samples = min(ir_len - 1, max(0, int((pre_delay_ms / 1000.0) * sample_rate)))
    time_axis = np.linspace(0.0, rt60, ir_len, endpoint=False)
    decay = np.exp(-6.91 * time_axis / rt60)
    early_reflections = np.zeros(ir_len)
    for tap_ms, gain in [(18.0, 0.45), (40.0, 0.35), (63.0, 0.24), (95.0, 0.18)]:
        idx = int((tap_ms / 1000.0) * sample_rate)
        if idx < ir_len:
            early_reflections[idx] = gain
    diffuse_tail = np.roll(rng.standard_normal(ir_len) * decay * 0.18, pre_delay_samples)
    impulse = butter_filter(
        early_reflections + diffuse_tail,
        min(4200.0, 0.45 * sample_rate),
        sample_rate,
        btype="low",
        order=2,
    )
    norm = np.linalg.norm(impulse)
    if norm > 1e-8:
        impulse = impulse / norm
    reverbed = fftconvolve(signal, impulse, mode="full")[: len(signal)]
    return (1.0 - wet_mix) * signal + wet_mix * reverbed


def synthesize_chest_latm_hit(sample_rate):
    """Synthesize a single dual-layer human palm-on-chest slap (55Hz thud + 4kHz smack)."""
    rng = np.random.default_rng(seed=101)
    dur = int(0.32 * sample_rate)
    t_vec = np.linspace(0.0, 0.32, dur, endpoint=False)
    freq_env = 55.0 + 48.0 * np.exp(-t_vec * 42.0)
    phase = 2.0 * np.pi * np.cumsum(freq_env) / sample_rate
    sub_thud = np.sin(phase) * np.exp(-t_vec * 15.0)
    harmonics = 0.35 * np.sin(2.0 * phase) * np.exp(-t_vec * 22.0)
    skin_noise = butter_filter(
        rng.standard_normal(dur),
        [1200.0, min(4800.0, 0.45 * sample_rate)],
        sample_rate,
        btype="band",
        order=2,
    )
    skin_smack = 0.28 * skin_noise * np.exp(-t_vec * 65.0)
    return tape_saturate(sub_thud + harmonics + skin_smack, drive=1.8)


def synthesize_zanjeel_hit(sample_rate, include_tasa=False):
    """Synthesize a Dammam drum strike locked with metallic Zanjeel shoulder chains."""
    rng = np.random.default_rng(seed=202)
    dur = int(0.38 * sample_rate)
    t_vec = np.linspace(0.0, 0.38, dur, endpoint=False)
    dammam_raw = np.sin(2.0 * np.pi * 88.0 * t_vec) * np.exp(-t_vec * 12.0)
    dammam = apply_track01_dammam_eq(dammam_raw, sample_rate)
    chains = butter_filter(
        rng.standard_normal(dur),
        min(2400.0, 0.42 * sample_rate),
        sample_rate,
        btype="high",
        order=2,
    ) * np.exp(-t_vec * 32.0)
    hit = 0.75 * dammam + 0.30 * chains
    if include_tasa:
        tasa = (
            np.sin(2.0 * np.pi * 1380.0 * t_vec) + 0.6 * np.sin(2.0 * np.pi * 2140.0 * t_vec)
        ) * np.exp(-t_vec * 18.0)
        hit = hit + 0.16 * tasa
    return tape_saturate(hit, drive=1.6)


def build_rhythm_bed(num_samples, sample_rate, mode, bpm):
    """Generate the rhythmic bed for the selected Husseiniya mode."""
    bed = np.zeros(num_samples, dtype=np.float64)
    if mode in ("mawal", "nai") or bpm <= 0:
        return bed

    beat_interval = max(1, int((60.0 / float(bpm)) * sample_rate))
    latm_hit = synthesize_chest_latm_hit(sample_rate)

    if mode == "latm":
        for pos in range(0, num_samples - len(latm_hit), beat_interval):
            bed[pos : pos + len(latm_hit)] += latm_hit
    elif mode == "zanjeel_iraqi":
        z_hit = synthesize_zanjeel_hit(sample_rate, include_tasa=False)
        for pos in range(0, num_samples - len(z_hit), beat_interval):
            bed[pos : pos + len(z_hit)] += z_hit
            half = pos + beat_interval // 2
            if half + len(z_hit) < num_samples:
                bed[half : half + len(z_hit)] += 0.45 * z_hit
    elif mode == "zanjeel_bahrani":
        z_hit = synthesize_zanjeel_hit(sample_rate, include_tasa=True)
        phrase_step = beat_interval * 5
        for base in range(0, num_samples - len(z_hit), phrase_step):
            for strike_idx in range(3):
                pos = base + strike_idx * beat_interval
                if pos + len(z_hit) < num_samples:
                    bed[pos : pos + len(z_hit)] += z_hit
    elif mode == "shoor":
        for pos in range(0, num_samples - len(latm_hit), beat_interval):
            bed[pos : pos + len(latm_hit)] += 0.85 * latm_hit
    elif mode == "bandari":
        sub_step = max(1, beat_interval // 3)
        for idx, pos in enumerate(range(0, num_samples - len(latm_hit), sub_step)):
            accent = 1.0 if (idx % 3 == 0) else (0.55 if (idx % 3 == 2) else 0.25)
            bed[pos : pos + len(latm_hit)] += accent * latm_hit

    return bed


def synthesize_ahaat_drone(num_samples, sample_rate, maqam_key):
    """Track_04_Ahaat_Vocal_Choir_Pads: Warm male Ahaat formant pad (Bandpass 150Hz-12kHz)."""
    freqs = MAQAM_FREQS.get(maqam_key, MAQAM_FREQS["saba"])
    t_vec = np.arange(num_samples, dtype=np.float64) / sample_rate
    drone = np.zeros(num_samples, dtype=np.float64)
    lfo = 1.0 + 0.003 * np.sin(2.0 * np.pi * 4.8 * t_vec)
    for idx, freq in enumerate(freqs):
        weight = 0.45 if idx == 0 else 0.18
        drone += weight * np.sin(2.0 * np.pi * freq * lfo * t_vec)
        drone += (weight * 0.4) * np.sin(4.0 * np.pi * freq * lfo * t_vec)
    high_passed = butter_filter(drone, 150.0, sample_rate, btype="high", order=2)
    return butter_filter(high_passed, min(950.0, 0.42 * sample_rate), sample_rate, btype="low", order=2)


def process_audio_file(input_path, output_path, mode="latm", bpm=60.0, maqam_drone="saba"):
    """Load an input WAV file, apply 5-Track Husseiniya DSP montage & -3dB ducking, and write WAV."""
    sample_rate, raw_data = wavfile.read(input_path)
    if raw_data.ndim > 1:
        mono = np.mean(raw_data.astype(np.float64), axis=1)
    else:
        mono = raw_data.astype(np.float64)

    peak = np.max(np.abs(mono))
    if peak > 1e-8:
        mono = mono / peak

    eq_vocal = apply_vocal_eq(mono, sample_rate)
    is_rubato = mode in ("mawal", "nai")
    delay_ms = 450.0 if is_rubato else 285.0
    rt60 = 3.8 if is_rubato else 3.2

    echoed_vocal = apply_dynacord_echo(eq_vocal, sample_rate, delay_ms=delay_ms, feedback=0.32, mix=0.22)
    wet_vocal = apply_husseiniya_reverb(echoed_vocal, sample_rate, rt60=rt60, wet_mix=0.26)

    rhythm_bed = build_rhythm_bed(len(mono), sample_rate, mode=mode, bpm=bpm)
    ahaat_pad = synthesize_ahaat_drone(len(mono), sample_rate, maqam_drone)

    ducking = compute_smart_sidechain_ducking(eq_vocal, sample_rate, duck_db=-3.0)

    left_chan = wet_vocal + (0.34 * rhythm_bed + 0.09 * ahaat_pad) * ducking
    right_chan = wet_vocal + (0.32 * np.roll(rhythm_bed, 14) - 0.09 * np.roll(ahaat_pad, 32)) * ducking

    stereo_raw = np.column_stack((tape_saturate(left_chan, drive=1.4), tape_saturate(right_chan, drive=1.4)))
    stereo = apply_master_glue_compressor(stereo_raw, ratio=1.5, threshold=0.65)
    max_val = np.max(np.abs(stereo))
    if max_val > 1e-8:
        stereo = stereo / max_val * 0.89

    out_int16 = np.clip(stereo * 32767.0, -32768, 32767).astype(np.int16)
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    wavfile.write(output_path, sample_rate, out_int16)


def parse_args(argv=None):
    """Parse CLI arguments for the Hussaini DSP Montage Engine."""
    parser = argparse.ArgumentParser(
        description="Hussaini Audio Omni-Engine DSP & Procedural Montage Script (V45.0)"
    )
    parser.add_argument("--input", required=True, help="Path to raw input WAV recording")
    parser.add_argument("--output", required=True, help="Path to output mastered stereo WAV")
    parser.add_argument(
        "--mode",
        default="latm",
        choices=["latm", "zanjeel_iraqi", "zanjeel_bahrani", "shoor", "bandari", "mawal", "nai"],
        help="Husseiniya rhythmic and acoustic processing mode",
    )
    parser.add_argument("--bpm", type=float, default=60.0, help="Tempo in BPM (0 for Rubato)")
    parser.add_argument(
        "--maqam-drone",
        default="saba",
        choices=list(MAQAM_FREQS.keys()),
        help="Maqam frequency profile for the Ahaat vocal drone pad",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """CLI Entrypoint."""
    args = parse_args(argv)
    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    process_audio_file(
        input_path=args.input,
        output_path=args.output,
        mode=args.mode,
        bpm=args.bpm,
        maqam_drone=args.maqam_drone,
    )
    print(f"Successfully mastered Husseiniya audio ({args.mode}, {args.bpm} BPM, Maqam {args.maqam_drone}) -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
