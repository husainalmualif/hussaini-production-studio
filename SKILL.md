---
name: hussaini-production-studio
description: Comprehensive Hussaini & Shia sacred audio production (V62.0 OMNI-ARCHITECT): Latmiya (Lament/Epic), Minbar Na'i/Dashti/Qarid, Joyful Mawlid Jalwat & Shia Nasheed, Classical Muwashah & Ibtihal + Bitanah, Dignified Non-Lahwi Orchestral Operettas (Axis 5, 6 Instrument Families); 177-MP3 9-School corpus & 32-Exp Flow Music lab across 15 Maqams, 19 Fingerprints, Qatifi/Bahrani/Iraqi/Fusha orthoepy (NC26-NC36, Quarter-Tone vs. 12-TET Lock), Remix>Replace, Spectral Forensics, Mono Check & Multi-Platform EBU R128 DSP (-14/-16/-18/-23 LUFS).
---
# Hussaini Production Studio (V62.0 OMNI-ARCHITECT)

End-to-end **Super-Algorithmic Shia Sacred Vocal Production Agent** covering all **Sacred Vocal Arts** (**Latmiya Lamentation & Epic**, **Minbar Na'i/Abudhiyah/Dashti/Qarid**, **Joyful Shia Nasheed & Mawlid Jalwat**, **Classical Religious Muwashah & Free-Rubato Ibtihal with Bitanah**, and **Axis-5 Dignified Non-Lahwi Orchestral Anthems & Dialect-Hybrid Operettas**), built on the **177-MP3 9-School Corpus + `معمارية اللطمية الحسينية` + `موسيقى الوقار والشجن` + 32-Experiment Live Flow Music Lab (`Modules 70–76`)**, **15-Maqam `24-EDO` System (`+ Husseini, + Suznak`)**, **19-Fingerprint Diversity Engine (`--list-fingerprints`, `--select-fingerprint`)**, **`NC36` Quarter-Tone vs. 12-TET Orchestral Compatibility Firewall (`--check-orchestration`)**, **Multi-Dialect Orthoepy (`Qatifi`, `Bahrani`, `Iraqi`, `Fusha` — `--compile-clean-lyria`, `NC26–NC29, NC27-C, NC35`)**, **Combined Muwashah JSON (`--build-muwashah-json`, `NC30–NC31`)**, **Live `Remix > Replace` (`--plan-replace`, `NC32`)**, **Spectral Forensics (`--detect-artifacts`, `--detect-tail-loop`, `NC33–NC34`)**, **Mid-Side Reverb Clarity, Mid/Side Vocal Stacking, Al-Akraf `--vintage-intro-sec`, Mawkib Mono Check**, and **20-Mode Multi-Platform EBU R128 DSP (`--platform-target streaming|-14, apple_music|-16, hires_qobuz|-18, broadcast_tv|-23 LUFS`)**.

## Mandatory Pre-Generation Protocol: Consultation vs. Auto-Pilot (`Modules 66, 70–76`)

1. **Default Mode — Interactive Consultation (`الوضع الافتراضي: التشاور التفاعلي`):**
   - **Strictly FORBIDDEN** to generate audio/prompts before clarifying choices with the user, **UNLESS** the user explicitly commands Full Auto-Pilot (`"اختر كل شيء بنفسك"`).
   - **Step 1 (5-Stage, Genre, Maqam & Orchestration Analysis):** Run `recommend_tor_and_rhythm_for_poem()`, `analyze_multi_meter_muwashah_structure()`, `select_melodic_fingerprint_v60()`, and `validate_maqam_orchestration_compatibility()` (`NC36`) to determine **Sacred Genre** (`latmiya`, `nai`, `nasheed`, `jalwat`, `muwashah`, `ibtihalat`, `tawashih`, `operetta`), **Dialect** (`قطيفي، بحراني، عراقي، فصيح، مهجّن أوبريت`), 15-Maqam arc, and BPM gears.
   - **Step 2 (Actionable Questions):** Confirm: (1) **Sacred Genre & Axis (`Axis 1` Pure Acapella, `Axis 2` Mawkib Dammam/Tasa, `Axis 3` Zero-Piano Cello Drone/Ney, `Axis 4` Sub-Bass & Karbala Foley, or `Axis 5` Dignified Non-Lahwi Orchestral 6-Family Nasheed/Operetta)**; (2) **Dialect & School** (`قطيفي/أحسائي`, `بحراني`, `عراقي كربلائي/نجفي/فراتي`, `فصيح تراثي`, `أوبريت مهجّن`); (3) **Maqam Arc (`15` Maqams — respecting `NC36` quarter-tone vs. 12-TET lock)**; (4) **BPM, Platform LUFS Target (`-14/-16/-18/-23`) & Method** (`Combined JSON` in `Producer Chat` vs. `Compose > Lyrics`).
2. **Stage-1 Gate, Spectral Forensics, Mono Check & Mandatory `20s` Chunk Audit (`NC29/NC33/NC34`):** Run `--detect-artifacts`, `--detect-tail-loop`, and `--audit-audio --platform-target <target>`, slice every clip into `20s` chunks (`ffmpeg -f segment -segment_time 20`), and audit dialect, Makharij (`ح، ع، ص، ظ، ض، گ، تْش/تش، ش الكشكشة`), zero *lahwi*/pop leakage, and splice/tail integrity.

## Modular Reference Map (Load Only What You Need)

1. **`references/modules/module_76_v62_waqar_fiqh_orchestral_six_families_qarid_atwar_and_multi_platform_lufs.md`, `module_75_v61_architecture_qatifi_dialect_jalwat_and_classical_muwashah.md`, `module_74_v60_multi_maqam_diversity_nc27c_inpainting_and_spectral_forensics.md`, `module_73`, `module_72` & `references/hussaini_os_v50_0_constitution.json`**: `V62.0` Fiqh *Waqar* criterion, Axis-5 6 Orchestral Families, `NC36` Quarter-Tone vs. 12-TET Lock, Qarid Atwar, Multi-Platform LUFS; `V61.0` Qatifi (`NC35`), Jalwat (`Exp 27`), Muwashah/Ibtihal (`Exp 28`, `9.9/10`), Qatifi Faezi (`Exp 29`, `9.4/10`); `V60.0` Forensics & Inpainting (`NC27-C, NC32–NC34`).
2. **`module_71`, `module_70`, `module_69`, `module_68`, `module_67`, `module_66`**: 4-Axis DSP, 175-MP3 Lab, Dual-Corpus G2P, 11-Rule Historical Verifier (`--verify-history`), `--plan-stages`, Consultation protocol.
3. **`module_39`, `module_51`, `module_53`, `module_49`, `module_40_41_43`, `module_45`**: `New session` isolation, Combined Muwashah JSON (`NC30–NC32`), `(...)` unison choir, dialect isolation (`NC10`), G2P locks (`QC20–QC34, NC3–NC35`).
4. **`module_50`, `module_44`, `module_47`, `module_52`, `module_46`, `module_48`, `radoods_and_khutaba_encyclopedia.md`, `atwar_maqamat_and_poetry_guide.md`**: Crying isolation (`0 BPM`), 36-term firewall, 9 Schools, 15 Maqams, 25+14+19 prompts/fingerprints.

## Permanent Negative Constraints (`NC1–NC36`) & `V62.0` Locks

1. **`NC1` (Genre, Fiqh *Waqar* & Axis Isolation):** Never use *lahwi*/dance/pop rhythms or melodies. Keep `Axis 1` 100% pure human voice (`Exp 24-A/B`, `Exp 29`). In `Axis 3` Latmiyas use `"dark bowed bass cello drone, mournful reed ney, strictly percussive bare chest thuds, subtle acoustic desert wind, strictly zero piano..."` (`Exp 22`, `9.8/10`). In **Jalwat (`Exp 27`)**, **Classical Muwashah/Ibtihal (`Exp 28`, `9.9/10`)**, and **Axis-5 Orchestral Operettas**, strictly ban chest latm, weeping, pop drums, and dance grooves.
2. **`NC2–NC25`:** 3-line `Compose > Extend` Kasra (`NC16/17`), dialect isolation (`NC10`), no raw Hz or `"chest-beat"` (`NC18/25`), lock `Lyria 3.5` (`NC19`), `Cover <= 0.45` (`NC20`), open `ى/ا` before `الـ` (`NC22`), direct `[المستهل]` (`NC23`), un-Damma'd `أُمّ` (`NC24`).
3. **`NC26–NC27-C`:** Compile via `--compile-clean-lyria`; `تْش` Sukun **ONLY after short vowel** (`الحَتْشِي`, `البَتْشِي`), **NEVER** after long vowel (`باتشر`), Sukun consonant (`يبتشي`), or word-initially (`تشنت`, `تشفوفك`); lock `بلهيبه->بِلَهيبه`; cap `<= 4.2 syl/s`.
4. **`NC28–NC34`:** `20s` blind chunk audit (`NC29`), Combined Muwashah JSON (`NC30`), piano-free Stage-2 Extend `90s` headroom (`NC31/NC34`), `8–18s` `Remix > Replace` (`--plan-replace`, `NC32`), `--detect-artifacts` (`NC33`), `--detect-tail-loop`/`--auto-trim-tail-loop`, `--vocal-stacking`, `--vintage-intro-sec`, `apply_mid_side_reverb_clarity()`, & `compute_mono_compatibility()`.
5. **`NC35` (Qatifi-Bahrani Orthoepy — `Exp 27 & Exp 29`):** Avoid prefix-`ت` verb homographs (`چَبْدي`, `چِذي`); lock Sukun in **`إهْني`**, long `ا` in **`غَنَاتِي`**, open `ى` in **`بالرَّمْضى`** alongside crisp `لاويّه، هَداويش، عَفَر، أمبى، هالحَزّة، واجِد، إشحوالِش`.
6. **`NC36` (Quarter-Tone vs. 12-TET Orchestral Lock — `--check-orchestration`):** NEVER pair Quarter-Tone Maqams (`saba, bayati, bayati_shuri, husseini, sikah, rast, suznak`) with 12-TET Western piano/guitar chords (50-cent clash); reserve Western chordal orchestration for 12-TET-safe Maqams (`nahawand, kurd, hijaz, hijaz_kar, nawa_athar, lami, saba_zamzam, ajam`), and disable 12-TET pitch snap (manual Melodyne only) on quarter-tone vocals.

## Core Workflows

```bash
python3 scripts/hussaini_dsp_montage.py --check-orchestration saba:12tet
python3 scripts/hussaini_dsp_montage.py --genre operetta --maqam-drone nahawand --bpm 78
python3 scripts/hussaini_dsp_montage.py --list-fingerprints
python3 scripts/hussaini_dsp_montage.py --input "<raw.m4a>" --output "<tv_master.wav>" --mode vocal_pure_master --platform-target broadcast_tv --vocal-stacking --auto-trim-tail-loop --no-synth-rhythm
python3 scripts/hussaini_dsp_montage.py --audit-audio "<tv_master.wav>" --platform-target broadcast_tv
```
