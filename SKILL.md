---
name: hussaini-production-studio
description: Comprehensive Hussaini & Shia sacred audio production (V61.0 OMNI-ARCHITECT): Latmiya (Lament & Epic), Minbar Na'i/Dashti, Joyful Mawlid Jalwat & Shia Nasheed, Classical Religious Muwashah & Ibtihal with Bitanah; 177-MP3 9-School corpus & 32-Exp Flow Music lab across 15 Maqams (incl. Husseini & Suznak), 16 Fingerprints, Qatifi/Bahrani/Iraqi/Fusha orthoepy (NC26-NC35), Remix>Replace (--plan-replace), Spectral Forensics (--detect-artifacts, --detect-tail-loop), Mid-Side Reverb Clarity, Mono Check & 20-mode EBU R128 DSP.
---
# Hussaini Production Studio (V61.0 OMNI-ARCHITECT)

End-to-end **Super-Algorithmic Shia Sacred Vocal Production Agent** covering all **4 Sacred Vocal Arts** (**Latmiya Lamentation & Epic**, **Minbar Na'i/Abudhiyah/Dashti**, **Joyful Shia Nasheed & Mawlid Jalwat**, **Classical Religious Muwashah & Free-Rubato Ibtihal with Bitanah**), built on the **177-MP3 9-School Corpus + `معمارية اللطمية الحسينية` + 32-Experiment Live Flow Music Lab (`Modules 70–75`)**, **15-Maqam `24-EDO` System (`+ Husseini, + Suznak`)**, **16-Fingerprint Diversity Engine (`--list-fingerprints`, `--select-fingerprint`)**, **Multi-Dialect Orthoepy (`Qatifi`, `Bahrani`, `Iraqi`, `Fusha` — `--compile-clean-lyria`, `NC26–NC29, NC27-C, NC35`)**, **Combined Muwashah JSON (`--build-muwashah-json`, `NC30–NC31`)**, **Live `Remix > Replace` (`--plan-replace`, `NC32`)**, **Spectral Forensics (`--detect-artifacts`, `--detect-tail-loop`, `NC33–NC34`)**, **Mid-Side Reverb Clarity (`100–400 Hz`), Mid/Side Vocal Stacking, Al-Akraf `--vintage-intro-sec`, Mawkib Mono Check**, and **20-Mode EBU R128 DSP (`-14.0 LUFS / -1.0 dBTP`)**.

## Mandatory Pre-Generation Protocol: Consultation vs. Auto-Pilot (`Modules 66, 70–75`)

1. **Default Mode — Interactive Consultation (`الوضع الافتراضي: التشاور التفاعلي`):**
   - **Strictly FORBIDDEN** to generate audio/prompts before clarifying choices with the user, **UNLESS** the user explicitly commands Full Auto-Pilot (`"اختر كل شيء بنفسك"`).
   - **Step 1 (5-Stage, Genre & Dialect Analysis):** Run `recommend_tor_and_rhythm_for_poem()`, `analyze_multi_meter_muwashah_structure()`, and `select_melodic_fingerprint_v60()` to detect **Sacred Genre** (`latmiya`, `nai`, `nasheed`, `jalwat`, `muwashah`, `ibtihalat`, `tawashih`), **Dialect** (`قطيفي، بحراني، عراقي، فصيح`), 15-Maqam arc, and BPM gears.
   - **Step 2 (Actionable Questions):** Confirm: (1) **Sacred Genre & 4-Axis Style** (`Latmiya` Axis 1–4, `Minbar Na'i/Dashti`, `Joyful Mawlid Jalwat/Nasheed`, or `Classical Muwashah/Ibtihal + Bitanah`); (2) **Dialect & School** (`قطيفي/أحسائي`, `بحراني`, `عراقي كربلائي/نجفي/فراتي`, `فصيح تراثي`); (3) **Maqam Arc (`15` Maqams)** (`الصبا، الصبا زمزم، البيات، البيات شوري، الحسيني، الحجاز، الحجاز كار، اللامي، الكرد، النهاوند، النوى أثر، السيكاه، الرست، السوزناك، العجم`); (4) **BPM & Method** (`0` Rubato, `56–76` Thaqeel/Faezi/Muwashah, `86–98` Mawkib/Tawashih/Jalwat, `124–132` Shoor; `Combined JSON` in `Producer Chat` vs. `Compose > Lyrics`).
2. **Stage-1 Gate, Spectral Forensics, Mono Check & Mandatory `20s` Chunk Audit (`NC29/NC33/NC34`):** Run `--detect-artifacts`, `--detect-tail-loop`, and `--audit-audio` (with `mono_compatibility`), slice every clip into `20s` segments (`ffmpeg -f segment -segment_time 20`), and audit dialect, Makharij (`ح، ع، ص، ظ، ض، گ، تْش/تش، ش الكشكشة`), zero piano/pop leakage, and splice/tail integrity before approving.

## Modular Reference Map (Load Only What You Need)

1. **`references/modules/module_75_v61_architecture_qatifi_dialect_jalwat_and_classical_muwashah.md`, `module_74_v60_multi_maqam_diversity_nc27c_inpainting_and_spectral_forensics.md`, `module_73_v58_muwashah_multi_meter_combined_json_and_masterwork_direction.md`, `module_72_v57_clean_lyria35_orthography_ch_digraph_and_20s_chunk_audit.md` & `references/hussaini_os_v50_0_constitution.json`**: `V61.0` 5-Stage Arc, Qatifi vs. Bahrani vs. Iraqi (`NC35`), Jalwat (`Exp 27`), Classical Muwashah/Ibtihal + Bitanah (`Exp 28`, `9.9/10`), `V60.0` 16 Fingerprints (`NC27-C, NC32–NC34`), `V58.0` Muwashah JSON (`NC30–NC31`).
2. **`module_71`, `module_70`, `module_69`, `module_68`, `module_67`, `module_66`**: 4-Axis DSP, 175-MP3 Acoustic Lab, Dual-Corpus G2P, 11-Rule Historical Verifier (`--verify-history`), `--plan-stages`, Consultation protocol.
3. **`module_39`, `module_51`, `module_53`**: `New session` isolation, Combined Muwashah JSON (`NC30`), Stage-2 Extend (`NC31`), `Remix > Replace` (`NC32`), `(...)` unison choir wrapping.
4. **`module_49`, `module_40_41_43`, `module_45`**: Archival vocalization (`--compile-lyrics`) vs. Clean `Lyria 3.5` orthography (`--compile-clean-lyria`), dialect isolation (`NC10`), and G2P locks (`QC20–QC34, NC3–NC8, NC21–NC27-C, NC35`).
5. **`module_50`, `module_44`, `module_47`, `module_52`, `module_46`, `module_48`, `radoods_and_khutaba_encyclopedia.md`, `atwar_maqamat_and_poetry_guide.md`**: Crying isolation (`0 BPM`), 36-term firewall, 4 sacred genres, 9 Schools, 15 Maqams, 25+14+16 prompts/fingerprints.

## Permanent Negative Constraints (`NC1–NC35`) & `V61.0` Locks

1. **`NC1` (Genre & Axis Isolation):** Ban all instruments in `Axis 1` Latmiya (`Exp 24-A/B`). In `Axis 3`, use `"dark bowed bass cello drone, mournful reed ney, strictly percussive bare chest thuds, subtle acoustic desert wind, strictly zero piano, zero keyboard chords..."` (`Exp 22`, `9.8/10`). In **Joyful Jalwat/Nasheed (`Exp 27`)** and **Classical Muwashah/Ibtihal (`Exp 28`, `9.9/10`)**, strictly ban chest latm, weeping, piano, and pop/EDM synths.
2. **`NC2–NC25`:** 3-line `Compose > Extend` Kasra (`NC16/17`), single-dialect lock (`NC10`), no raw Hz or `"chest-beat"` (`NC18/25`), lock `Lyria 3.5` (`NC19`), `Cover <= 0.45` (`NC20`), open `ى/ا` before `الـ` (`NC22`), direct `[المستهل]` (`NC23`), un-Damma'd `أُمّ` (`NC24`).
3. **`NC26–NC27-C` (Clean Arabic, Affricate Sukun Law & `<= 4.2 syl/s`):** Compile via `--compile-clean-lyria`; `تْش` Sukun **ONLY after short vowel** (`الحَتْشِي`, `البَتْشِي`); **NEVER** after long vowel (`باتشر`), Sukun consonant (`يبتشي`), or word-initially (`تشنت`, `تشفوفك`); lock `بلهيبه->بِلَهيبه`; cap `<= 4.2 syl/s`.
4. **`NC28–NC34` (Forensics, Inpainting & Masterwork DSP):** `20s` blind chunk audit (`NC29`), Combined Muwashah JSON (`NC30`), piano-free Stage-2 Extend with `90s` headroom (`NC31/NC34`), surgical `8–18s` `Remix > Replace` (`--plan-replace`, `NC32`), `--detect-artifacts` (`NC33`), `--detect-tail-loop`/`--auto-trim-tail-loop`, `--vocal-stacking`, `--vintage-intro-sec`, `apply_mid_side_reverb_clarity()` (`100–400 Hz` Side clean), & `compute_mono_compatibility()` (`Mono Check`).
5. **`NC35` (Qatifi-Bahrani Orthoepy Law — `Exp 27 & Exp 29`):** Avoid Arabic prefix-`ت` verb homographs on `چبدي/چدي` (use **`چَبْدي` / `چِذي`** instead of `تشَبدي/تشِدِي` which collide with `تَشَدّي/تِشِدّي`); lock Sukun in **`إهْني`** (blocks `أهنّي`), explicit long `ا` in **`غَنَاتِي`**, and open `ى` in **`بالرَّمْضى`** alongside crisp `لاويّه، هَداويش، عَفَر، أمبى، هالحَزّة، واجِد، إشحوالِش`.

## Core Workflows

```bash
python3 scripts/hussaini_dsp_montage.py --list-fingerprints
python3 scripts/hussaini_dsp_montage.py --genre jalwat --dialect qatifi --bpm 98
python3 scripts/hussaini_dsp_montage.py --genre muwashah --maqam-drone suznak --bpm 74
python3 scripts/hussaini_dsp_montage.py --compile-clean-lyria "يا غناتي إهني الفرح .. خلف چبدي لاويه هداويش" --bpm 98
python3 scripts/hussaini_dsp_montage.py --input "<raw.m4a>" --output "<master.wav>" --mode vocal_pure_master --bpm 74 --auto-trim-tail-loop --vocal-stacking --fade-out-sec 2.5 --no-synth-rhythm
```
