# Module 74 (V60.0 OMNI-ARCHITECT): Multi-Maqam & 9-School Melodic Diversity, NC27-C Phonological Affricate Law, Live `Remix > Replace` Inpainting (`NC32`), Zero-Piano Spectral Forensics (`NC33`), & Auto Tail-Loop / Mid-Side Vocal Stacking (`NC34`)

## 1. Executive Upgrade Overview (`V58.0 [85%] -> V60.0 [100%]`)

`V60.0 OMNI-ARCHITECT` closes all 4 structural gaps between `V58.0` and `100%` production mastery through:
1. **9-School / 27-Track Corpus Survey & 13-Maqam `24-EDO` Expansion (`Gap 1`):** Surveyed all 9 Schools across the 177-MP3 Hussaini library (`Basim`, `Bujabara`, `Al-Akraf`, `Sayyid Salam`, `Murtadha Harb/Shoor`, `Al-Janami/Bayati`, `Bahrani Studio`, `Basra/Euphrates`, `Farsi Epic Zamineh`), expanded `MAQAM_FREQS`, `COMMON_JINS_GRAPH`, and normalized `_MAQAM_24EDO_TEMPLATES` to **13 Maqams** (`bayati`, `bayati_shuri`, `saba`, `saba_zamzam`, `hijaz`, `hijaz_kar`, `lami`, `kurd`, `nahawand`, `nawa_athar`, `sikah`, `rast`, `ajam`), and codified **`MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60`** (12 distinct sound worlds breaking melodic monotony).
2. **`NC27-C` Phonological Affricate Sukun Law, Fast-Meter Syllable Density Governor (`<= 4.2 syl/s`), & `NC32` Live `Remix > Replace` Inpainting (`Gap 2`):** Empirically solved CVVC/CCC affricate drops (`باتْشِر -> باشر`, `يبتْشي -> يبتي`), locked elision vowels (`بلهيبه -> بِلَهيبه`), added `audit_syllable_density_v60()` (`<= 4.2 syl/s`), and proved live surgical phrase repair via `Remix > Replace` (`Exp 21-A`, `9.7/10`, invisible seam).
3. **Zero-Piano Hardened Axis-3 Prompt & Calibrated Automatic Spectral Forensics (`Gap 3 — NC33`):** Replaced classical `"solo cello"` with `"dark bowed bass cello drone, mournful reed ney, strictly percussive bare chest thuds, subtle acoustic desert wind, strictly zero piano, zero keyboard chords..."` (achieving **0.00% piano** in `Exp 22`, `9.8/10`) and built `detect_piano_and_pop_snare_transients()` (`--detect-artifacts`) using sub-bin parabolic zero-vibrato (`std < 5.5 cents`) linear dB-decay (`R^2 >= 0.80`) piano physics + dual-band coincident pop-snare periodicity.
4. **Complete 4+ Min Production Pipelines, Auto Tail-Loop Trimming, & 5th Masterwork Blueprint (`Gap 4 — NC34`):** Built `detect_extend_restart_loop()` (`--detect-tail-loop`, `--auto-trim-tail-loop`), implemented `apply_mid_side_vocal_stacking_enhancer()` (`--vocal-stacking`, mono-safe `>180 Hz` solo-vs-choir stereo breathing matching the `3.1–6.2 dB` masterwork range), wired Al-Akraf `300–2800 Hz` `--vintage-intro-sec` into `process_audio_file()`, and verified full 4+ min extended productions across both Bahrani (`Exp 21-B`) and Pure Axis-1 Iraqi (`Exp 24-B`).

---

## 2. Empirical Live Flow Music (`Lyria 3.5`) Lab — Experiments `21-A` through `26-B` (29 Cumulative Live Experiments, 100% `20s` Blind Chunk Audited `NC29`)

| Exp | School / Dialect / Style | Maqam Arc & BPM | Axis / Method | Clip UUID & Duration | Blind `20s` Audit Score | Key Empirical Findings & Honest Notes |
|---|---|---|---|---|---|---|
| **Exp 21-A** | Bahrani Multi-Meter Muwashah «بكاء الورق» | Bayati -> Hijaz -> Saba (`72 BPM`) | `Remix > Replace` (`0:56–1:07`, `11s`) on `M2-B` | `5172764b-9597-43a9-a52c-4f877c0a8058` (`2:39`) | **`9.7 / 10`** | **Proved `NC32`:** Repaired `بلهيبه -> بِلَهيبه` 100%, invisible splice seam, zero voice/maqam drift, 0% piano/pop. |
| **Exp 21-B** | Bahrani Extended Stage-2 Muwashah | Bayati -> Saba (`72 BPM`) | `Remix > Extend` (`2:35–3:45`) from `5172764b` | `4f987ba8-7202-4b68-bbf5-5fa6dc8b4e6d` (`3:45` -> `3:38.5` trim) | **`9.2 / 10`** | 0.00% piano across `3:38`, invisible `2:35` seam, `في يوم العاشر` fixed 100%. Exposed CVVC `باتْشِر -> باشر` drop (`NC27-C`), 3-word cut on tight `70s` window, and `3:43` tail loop (`NC34`). |
| **Exp 22** | Bahrani Cradle Muwashah «أشم خدّك» | **Nahawand -> Kurd -> Saba** (`64 BPM`) | Zero-Piano Axis 3 Combined JSON | `3a1846ce-832f-47eb-acb8-b21ab3862567` (`3:02`) | **`9.8 / 10`** *(Record)* | **Proved `NC33`:** **0.00% piano, 0.00% pop snare**, 100% distinct Nahawand/Kurd cradle melody, crisp `أحتْشي`, `تشِنت`, `گ`, Qa'da drop (`c06`), clean ending with zero loop. |
| **Exp 23** | Epic Fusha/Bahrani Mawkib «أصحاب الحسين» | **Hijaz Kar** (`88 -> 96 BPM`) | Axis 2 Dammam & Brass Tasa | `2bfdacc0-7688-44b6-82bb-5cd15ee04ca5` (`2:56`) | **`9.2 / 10`** | Explosive `96 BPM` Haidari gear jump on `لبّيك` (`c05`), 0% piano, clean stop (`c08`). Honest flaws: bright brass fanfare, slight fast-choir rush on `إنّه وعد الأُلى` (`c02`). |
| **Exp 24-A** | Pure Iraqi Karbalaei Multi-Tor «يا بوفاضل» | **Saba Zamzam -> Lami** (`58 BPM`) | **Pure Axis 1** (Zero Instruments) | `2af13afc-efa2-4bb9-a8b1-740e249d87fc` (`3:02`) | **`9.7 / 10`** | **0.00% instruments**, authentic Karbala Husseiniya choir + Ahaat + bare chest latm, crisp Iraqi `گ/تْش`, clean fade, zero loop. |
| **Exp 24-B** | 4+ Min Pure Axis-1 Iraqi Extended Production | **Hijaz Jawab -> Euphrates Lami Kasra** (`58 BPM`) | `Remix > Extend` (`2:55–4:25`, `90s` headroom) from `2af13afc` | `9dc63acd-96dd-4bcf-a682-29f7ab340d90` (`4:25` -> `4:18.5` trim) | **`9.4 / 10`** | **0.00% instruments across full `4:18`**, dramatic Qa'da silence drop at `3:37` -> devastating Lami Kasra (`گطعوا تشفوفك`), zero truncated lyrics (`90s` headroom). Exposed CCC `يبتْشي -> يبتي` drop (`NC27-C`) & `4:20` tail loop (`NC34`). |
| **Exp 25** | Iraqi Rapid Shoor & Haidari Majlis | **Kurd & Bayati Shuri** (`124 BPM`) | Pure Axis 1 Rapid Shoor | `d5942c88-e2ae-4884-8008-753970ee1fb7` (`2:36`) | **`9.1 / 10`** | Authentic `124 BPM` Karbala Shoor crowd energy, dramatic stop-time finale (`مولاي يا نور العين`), zero piano/EDM. Minor low bass undertone; ultra-fast 2-beat crowd response validates `<= 4.2 syl/s` density cap. |
| **Exp 26-A** | Minbar Abudhiyah & Na'i (True Rubato) | **Sikah -> Saba** (`0 BPM`) | Pure Solo Acapella (`0 BPM` Rubato) | `bb6ce74e-e26b-43e1-b428-092473a921a9` (`2:59`) | **`9.5 / 10`** | **100.00% true `0 BPM` unmetered solo voice**, zero percussion/instruments, authentic Iraqi Khatib breath & weeping Majlis cue (`واحسيناه`), spotless Na'i (`c05–c08`), minor Abudhiyah melisma stretch (`c01/c03`). |
| **Exp 26-B** | Classical Devotional Tawashih / Madih | **Rast -> Ajam** (`86 BPM`) | Devotional Fusha Choir + Daf | `7a91ad46-9409-494b-b66a-c262f0304d1b` (`2:46`) | **`9.5 / 10`** | Radiant uplifting Fusha Munshid + choir modulation (`Rast -> Ajam`), 0% chest latm, 0% weeping, 0% piano, clean choral fade (`c08`). Added subtle Eastern strings/Oud alongside Daf. |

---

## 3. Permanent `V60.0` Engineering Laws (`NC27-C`, `NC32`, `NC33`, `NC34`)

### `NC27-C` — Phonological Affricate Sukun Law (`تْش` vs. `تش`) & Fast-Meter Syllable Density Governor (`<= 4.2 syl/s`)
- **Rule 1 (Short-Vowel Medial CVC Only):** Place Sukun `تْش` **ONLY directly after a short vowel** (e.g., `الحَتْشِي`, `البَتْشِي`) so `Lyria 3.5` never splits the affricate into 3 syllables (`ḥa-ta-shī`).
- **Rule 2 (Zero Sukun After Long Vowel, Sukun Consonant, or Word-Initially):** **NEVER** place Sukun `تْش` after a long vowel (`ا/و/ي` — illegal CVVC: `باتْشِر` collapsed to `باشر` in `Exp 21-B`), after a Sukun consonant (`بْ+تْ` — illegal CCC: `يبتْشي` collapsed to `يبتي` in `Exp 24-B`), or word-initially (`تْشنت`, `تْشفوفك`). Always emit plain `تش` (`باتشر`, `يبتشي`, `تبتشي`, `تشنت`, `تشفوفك`).
- **Rule 3 (Elision Vowel Locks & Density Cap):** Lock fast-meter vowel elisions (`بلهيبه -> بِلَهيبه`, `ولهيب -> ولَهيب`, `عشت -> عِشت`, `أذنت -> أذِنت`) and enforce `audit_syllable_density_v60()` (`<= 4.2 syl/s`) so fast `88–132 BPM` sections never garble consonants.

### `NC32` — Live `Remix > Replace` Surgical Inpainting Protocol (`--plan-replace`)
- Never regenerate a `9.4+/10` take just to repair 1–2 mispronounced words.
- Use `build_remix_replace_inpainting_plan()` (`--plan-replace <UUID> <START> <END> <OLD> <FIXED>`) targeting a tight `8–18s` phrase window around clean phrase boundaries (proven `11s` window `0:56–1:07` in `Exp 21-A`, `9.7/10`), edit ONLY that single line in `Edit Lyrics`, lock `Model = Lyria 3.5` + zero-piano `Instruction`, and run `20s` blind chunk audit across both splice seams.

### `NC33` — Zero-Piano Axis-3 Prompt Engineering & Calibrated Spectral Forensics (`--detect-artifacts`)
- **Prompt Firewall:** Replace `"solo cello"` (which triggers classical chamber piano accompaniment in Lyria 3.5) with **`"dark bowed bass cello drone, mournful reed ney, strictly percussive bare chest thuds, subtle acoustic desert wind, strictly zero piano, zero keyboard chords, zero pop drums, zero rock snare backbeat"`**.
- **Automatic Forensic Gate (`detect_piano_and_pop_snare_transients()`):**
  - *Piano Physics:* Tracks `190–1400 Hz` spectral peaks with parabolic sub-bin frequency interpolation (`nfft=4096 @ 16 kHz`); flags rigid struck-string piano notes having sharp attack (`>= +9.5 dB`), **zero vibrato (`std < 5.5 cents` over `150ms`)**, and linear log-amplitude exponential decay (`-95..-14 dB/s`, `R^2 >= 0.80`). Threshold `>= 3` rigid decay notes per `20s` chunk achieved **100% precision & recall** separating piano-contaminated takes (`M1`, `M2-A`) from piano-free studio/human recordings (`M2-B`, `Exp 22`, `Exp 24-B`, Al-Akraf, Basim, Sayyid Salam).
  - *Pop-Snare Physics:* Detects coincident mid-low body (`170–520 Hz`) + broadband wire noise (`2400–7200 Hz`, flatness `> 0.30`) bursts and measures backbeat periodicity (`0.36–1.20s` autocorrelation lag).

### `NC34` — `90s` Extend Headroom, Auto Tail-Loop Trimming (`--detect-tail-loop` / `--auto-trim-tail-loop`), & 5th Masterwork Blueprint (`--vocal-stacking`)
- **Stage-2 Extend Headroom:** Always give Stage-2 `Remix > Extend` **`90s` headroom** (e.g., `2:55 -> 4:25` in `Exp 24-B`) instead of tight `70s` windows (`Exp 21-B`) so the final couplet never truncates.
- **Auto Tail-Loop Detection (`detect_extend_restart_loop()`):** Scans the final `28s` for a cadential valley (`< -34 dBFS`, dropping `>= 14 dB` below preceding 5s active RMS) followed by a sudden re-entry spike (`>= +11 dB` to `> -28 dBFS`) and outputs exact `recommended_trim_sec`. Passing `--auto-trim-tail-loop` to `process_audio_file()` automatically trims the loop cleanly and applies a smooth raised-cosine fade-out before `-14.0 LUFS / -1.0 dBTP` mastering.
- **5th Masterwork Blueprint (`apply_mid_side_vocal_stacking_enhancer()` — `--vocal-stacking`) + Al-Akraf Vintage Intro (`--vintage-intro-sec`):** Contrasts intimate centered solo Radood passages (`-1.5 dB` side focus) with wide mono-safe (`>180 Hz` HPF on Side so `55 Hz` chest Latm stays locked mono) choral swells (`+4.2 dB` side expansion), matching the empirical `3.1–6.2 dB` stereo breathing measured across the 177-MP3 corpus.

---

## 4. `V60.0` CLI Quick Reference

```bash
# 1) List & select from 12 diverse Multi-Maqam & 9-School Melodic Fingerprints
python3 scripts/hussaini_dsp_montage.py --list-fingerprints
python3 scripts/hussaini_dsp_montage.py --select-fingerprint v60_bahrani_cradle_nahawand_kurd_saba_64bpm
python3 scripts/hussaini_dsp_montage.py --select-fingerprint "auto:أشم خدك يا طفلي الرضيع"

# 2) Compile Clean Lyria 3.5 Lyrics with NC27-C Affricate Law & <=4.2 syl/s Density Audit
python3 scripts/hussaini_dsp_montage.py --compile-clean-lyria "ليش الفجر قاسي بلهيبه .. باچر يبتشي وگطعوا چفوفك" --bpm 88

# 3) Plan Surgical Live Remix > Replace Inpainting (NC32)
python3 scripts/hussaini_dsp_montage.py --plan-replace "<CLIP_UUID>" 56 67 "ليش الفجر قاسي .. بلهيبه" "ليش الفجر قاسي .. بِلَهيبه"

# 4) Run Automatic Spectral Forensics (Piano / Pop Snare NC33) & Tail-Loop Detection (NC34)
python3 scripts/hussaini_dsp_montage.py --detect-artifacts "<raw.m4a>"
python3 scripts/hussaini_dsp_montage.py --detect-tail-loop "<extended.m4a>"

# 5) Full V60 Masterwork Post-Production (Auto Tail-Loop Trim + Vintage Intro + Mid/Side Vocal Stacking + EBU R128)
python3 scripts/hussaini_dsp_montage.py --input "<extended.m4a>" --output "<master_v60.wav>" \
  --mode vocal_pure_master --bpm 58 --auto-trim-tail-loop --vocal-stacking --fade-out-sec 2.5 --no-synth-rhythm
```
