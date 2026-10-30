#!/usr/bin/env python3
"""Hussaini Audio Omni-Engine DSP & Procedural Montage Script (V37.0 GRAND-MASTER).

Applies authentic Husseiniya acoustic processing to raw vocal recordings:
- High-Pass Filter (85Hz), Boxy Notch (650Hz), and Jawhari Mid-Presence Boost (+4.5dB @ 2.5kHz)
- Classic Dynacord Analog Tape Echo (285ms for Latmiya, 480ms for Mawal/Na'i)
- Husseiniya & Cathedral Convolution Reverb (1.5s to 3.8s decay)
- Procedural Dual-Layer Human Chest-Slap (55Hz sub-thud + 4kHz skin-smack + 110Hz harmonics)
- Iraqi & Bahrani Zanjeel (Dammam + metallic shoulder chains + brass Tasa)
- Karbalaei Shoor (125-145 BPM chest-slap + sub-harmonic Dhikr pulse) & Bandari (6/8)
- Harmonic Male Ahaat Vocal Drone Pads in 6 Maqamat (Bayati, Saba, Hijaz, Lami, Kurd, Rast)
"""

import argparse
import os
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


def tape_saturate(signal, drive=2.2):
    """Apply warm analog tape soft-clipping saturation."""
    return np.tanh(signal * drive) / np.tanh(drive)


def apply_dynacord_echo(signal, sample_rate, delay_ms=285.0, feedback=0.32, mix=0.22):
    """Simulate a classic Dynacord analog tape echo with high-cut damping."""
    delay_samples = max(1, int((delay_ms / 1000.0) * sample_rate))
    num = np.zeros(delay_samples + 1)
    num[0] = 1.0
    den = np.zeros(delay_samples + 1)
    den[0] = 1.0
    den[delay_samples] = -feedback
    echoed = butter_filter(
        lfilter(num, den, signal), min(4500.0, 0.45 * sample_rate), sample_rate, btype="low", order=2
    )
    return (1.0 - mix) * signal + mix * echoed


def apply_husseiniya_reverb(signal, sample_rate, rt60=3.2, wet_mix=0.26):
    """Apply synthetic Husseiniya / Cathedral hall impulse response convolution."""
    rng = np.random.default_rng(seed=42)
    ir_len = max(1, int(rt60 * sample_rate))
    time_axis = np.linspace(0.0, rt60, ir_len, endpoint=False)
    decay = np.exp(-6.91 * time_axis / rt60)
    early_reflections = np.zeros(ir_len)
    for tap_ms, gain in [(18.0, 0.45), (37.0, 0.32), (63.0, 0.24), (95.0, 0.18)]:
        idx = int((tap_ms / 1000.0) * sample_rate)
        if idx < ir_len:
            early_reflections[idx] = gain
    diffuse_tail = rng.standard_normal(ir_len) * decay * 0.18
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
    dammam = np.sin(2.0 * np.pi * 88.0 * t_vec) * np.exp(-t_vec * 12.0)
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
    """Synthesize a warm male Ahaat vocal formant drone in the chosen Maqam."""
    freqs = MAQAM_FREQS.get(maqam_key, MAQAM_FREQS["saba"])
    t_vec = np.arange(num_samples, dtype=np.float64) / sample_rate
    drone = np.zeros(num_samples, dtype=np.float64)
    lfo = 1.0 + 0.003 * np.sin(2.0 * np.pi * 4.8 * t_vec)
    for idx, freq in enumerate(freqs):
        weight = 0.45 if idx == 0 else 0.18
        drone += weight * np.sin(2.0 * np.pi * freq * lfo * t_vec)
        drone += (weight * 0.4) * np.sin(4.0 * np.pi * freq * lfo * t_vec)
    return butter_filter(drone, min(950.0, 0.42 * sample_rate), sample_rate, btype="low", order=2)


def process_audio_file(input_path, output_path, mode="latm", bpm=60.0, maqam_drone="saba"):
    """Load an input WAV file, apply Husseiniya DSP montage, and write stereo WAV."""
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

    echoed_vocal = apply_dynacord_echo(eq_vocal, sample_rate, delay_ms=delay_ms, feedback=0.30, mix=0.22)
    wet_vocal = apply_husseiniya_reverb(echoed_vocal, sample_rate, rt60=rt60, wet_mix=0.26)

    rhythm_bed = build_rhythm_bed(len(mono), sample_rate, mode=mode, bpm=bpm)
    ahaat_pad = synthesize_ahaat_drone(len(mono), sample_rate, maqam_drone)

    vocal_env = np.minimum(1.0, np.abs(eq_vocal) * 2.5)
    ducking = 1.0 - 0.35 * vocal_env

    left_chan = wet_vocal + (0.34 * rhythm_bed + 0.08 * ahaat_pad) * ducking
    right_chan = wet_vocal + (0.32 * np.roll(rhythm_bed, 12) + 0.08 * np.roll(ahaat_pad, 28)) * ducking

    stereo = np.column_stack(( tape_saturate(left_chan, drive=1.4), tape_saturate(right_chan, drive=1.4) ))
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
        description="Hussaini Audio Omni-Engine DSP & Procedural Montage Script"
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
