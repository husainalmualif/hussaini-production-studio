# Module 67 — V52.0 Pure-Vocal Mastering, True EBU R128, 127-Section Corpus Compiler & Historical Verifier

> **Parent Module:** `SKILL.md` (`V52.0 OMNI-ARCHITECT`)  
> **Builds Upon:** `module_66_v51_field_evaluation_consultation_and_style_taxonomy.md` (`NC1–NC17`)  
> **Primary Runtime:** `scripts/hussaini_dsp_montage.py`

---

## 1. Field Findings Behind V52.0 (Flow Music V51.2 Evaluation Synthesis)

Field evaluation of **"صُوتْ أُمِّ البَنِينْ يِصِيحْ يَبِنْ حَذْلَمْ"** across Method 1 (`Compose > Lyrics`, `08:16.94`) and Method 2 (`Producer JSON`, `12:02.05` hard cutoff at `12:02`) revealed four engineering requirements that drove the **V52.0 OMNI-ARCHITECT** upgrade:

| Finding | Field Observation in V51.2 | V52.0 Architectural Solution |
| :--- | :--- | :--- |
| **F1: Cloud Step 4 Overshoot & Clipping** | Flow Music `Step 4` (`audio__apply_effect` EQ/Compression) pushed integrated loudness to `-8.1 / -8.6 LUFS` and clipped peaks to `+0.6 / +0.7 dBFS` (`+300` clipped intervals). | **Banned Step 4 Cloud Mastering.** Export raw Flow audio and master locally with `--mode vocal_pure_master --trim-end-sec <T> --fade-out-sec 3.0` to achieve exact **-14.0 LUFS / -1.0 dBTP**. |
| **F2: Synthetic Matam Clash** | Flow's neural engine already renders realistic bare-palm chest Matam in `Step 1`; overlaying `thaqeel_muwazza` synthetic kick beds risked dual-hit phase clashes. | Added **`vocal_pure_master`** + `--no-synth-rhythm`: preserves Flow's natural `42Hz+` chest Matam (`preserve_chest_thud=True`), skips AI percussion stripping and synthetic beds, and adds gentle Husseiniya dome width. |
| **F3: Method 2 (+60s) Trailing Pads** | Producer JSON `+60s` Extend windows occasionally left up to `9.5–13.5s` low-energy instrumental/Ahaat gaps or hit the `12:02` platform cap abruptly. | Added **`--plan-stages`** (`plan_poem_extend_stages`) with `NC16` 3-line pacing + Method 2 trailing-pad warnings, **`--trim-end-sec` / `--fade-out-sec`**, and **`--audit-audio`** gap & tail verification. |
| **F4: Corpus Phonetics & Historical Integrity** | Unseen Iraqi particles, `كً` / Swash-Kaf variants, trailing punctuation blocking sukun, and unverified folk verses weakened downstream pronunciation and historical fidelity. | Added `COMMON_CORPUS_LEXICON_V52` (`216` forms), `normalize_iraqi_orthographic_gaf`, strict idempotency (`99.62%` across `127` sections), and **`--verify-history`**. |

> **Archival Poem Text Verification Note:** Cross-checking the archival V51.2 checkpoint (`sawt_umm_al_banin_v51_2_master_test_package.md`) and `module_66` benchmark lines (`131–143`) against the canonical poem of **Ja'far Atiyah al-Bazooni** showed altered verses in archival `Stage 1, 3A, 3B, 4A, 4B, 5A, 5B, 6C`. V52 preserves historical V51.2 field reports untouched as benchmark artifacts while requiring source-verified texts via `--verify-history` for all new productions.

---

## 2. Pure-Vocal Mastering & Broadcast EBU R128 DSP Architecture

### 2.1 `vocal_pure_master` & `--no-synth-rhythm`
When `mode="vocal_pure_master"` or `no_synth_rhythm=True`:
1. **Optional Clean End Trim & Raised-Cosine Fade:** `--trim-end-sec` slices cleanly before Flow hard-cut boundaries; `--fade-out-sec` applies a smooth `0.5 * (1 + cos(pi * t))` taper to silence (`tail_last_150ms_dbfs < -60 dBFS`).
2. **Organic Thud Preservation:** Bypasses `strip_ai_percussion_from_vocal` and synthetic `build_rhythm_bed` / `ahaat_pad` synthesis; calls `apply_vocal_eq(..., preserve_chest_thud=True)` so Flow's `42 Hz+` bare-palm Matam thuds stay intact.
3. **Subtle Dome Envelopment & Glue:** Applies warm Dynacord analog delay (`wet=0.10`, `feedback=0.20`), asymmetric dual-seed Husseiniya dome reflections (`rt60_sec=2.1`, `pre_delay_ms=20.0 / 26.0`, `wet=0.14`), gentle tape saturation (`drive=1.10`), and light glue compression (`ratio=1.35`, `threshold=0.68`).

### 2.2 ITU-R BS.1770-4 / EBU R128 & 4x True-Peak Limiter
- **`measure_ebu_r128_loudness(stereo, sample_rate)`:** Implements full K-weighting (Stage 1 `+4.0 dB` high-shelf filter at `1681.97 Hz` + Stage 2 RLB `38.135 Hz` high-pass biquad), `400ms` overlapping windows (`100ms` hop), `-70.0 LUFS` absolute gate + `-10.0 LU` relative gate, `10th–95th` percentile LRA, and chunked `4x` oversampled True-Peak detection (`dBTP`).
- **`_apply_lookahead_true_peak_limiter` & `normalize_lufs_and_true_peak`:** Iteratively converges stereo mix to `-14.0 LUFS` while enforcing `-1.0 dBTP` brickwall compliance.
- **`_fast_boxcar_mean(signal, win)`:** `O(N)` chunked `cumsum` moving-average smoothing guarantees exact array-length preservation even on short audio clips (`len(signal) < win`) and accelerates 12-minute `48 kHz` mastering passes by avoiding `O(N * W)` dense convolution.
- **`read_wav_any_depth(input_path, return_stereo=False)`:** Pure-Python RIFF/WAVE parser supporting `8-bit PCM`, `16-bit PCM`, `24-bit PCM`, `32-bit PCM` (including 24-bit packed in 32-bit containers), and `32-bit IEEE Float` (`audio_fmt == 3`), with stereo extraction for `--audit-audio` matching `ffmpeg -af ebur128` to `0.0 dB`.

### 2.3 `--audit-audio` Telemetry Contract
Running `--audit-audio <wav>` emits JSON containing:
- `sample_rate`, `channels`, `bit_depth`, `duration_sec`
- `integrated_lufs`, `lra_lu`, `true_peak_dbtp` (measured natively in stereo when `channels > 1`)
- `max_low_energy_gap_sec`: longest continuous `<-28.0 dBFS` instrumental/Ahaat pad (`0.5s` hops)
- `tail_last_150ms_dbfs` & `abrupt_tail_cutoff_risk` (`True` if final `150ms > -24.0 dBFS`)
- `broadcast_compliant`: `True` iff `true_peak_dbtp <= -0.9` and `-15.5 <= integrated_lufs <= -12.5`

---

## 3. Expanded 18 DSP Modes & V52 Atwar (`EXTENDED_ATWAR_PROMPTS_V52`)

To preserve backward compatibility with V50–V51 constitutional audits (`MASTER_SOUND_PROMPTS_V50 == 25`), V52 adds two new specialized Sound Prompts under `EXTENDED_ATWAR_PROMPTS_V52` and expands `SUPPORTED_DSP_MODES` to **18 modes**:

1. **`vocal_pure_master`** — Pure-Vocal Studio Master (`42Hz+` organic Flow Matam preservation, zero synthetic drums/Ahaat).
2. **`fazzaiya`** (`karbalai_fazzaiya_84bpm_hijaz_bayati_v52`) — Urgent Traditional Iraqi Hussaini Fazzaiya chant (`84 BPM`, Maqam Hijaz & Bayati, fiery commanding baritone + rapid `55Hz` synchronized bare-palm Matam).
3. **`shia_tawshih_nasheed_86bpm_rast_hijaz_v52`** — Dignified Spiritual Shia Islamic Choral Tawashih & Nasheed (`86 BPM`, Maqam Rast & Hijaz, Classical Arabic & devotional articulation, light respectful frame percussion only, zero chest Latm, zero Western instruments).

Complete `18` `SUPPORTED_DSP_MODES`:
`vocal_pure_master`, `latm`, `heavy_clip`, `thaqeel_muwazza`, `studio_arranged`, `fazzaiya`, `bahrani_fast`, `bahrani_thulathi`, `bahrani_rubai`, `bahrani_haidari`, `bahrani_waqfa`, `bahrani_muthakkal`, `zanjeel_iraqi`, `zanjeel_bahrani`, `shoor`, `bandari`, `mawal`, `nai`.

---

## 4. Historical Verifier (`--verify-history`) & Extend Stage Planner (`--plan-stages`)

### 4.1 `--verify-history` (`verify_historical_narratives`)
Scans poem lyrics against verified Karbala, Madina, and Ahl al-Bayt historical motifs and cross-checks known folk fabrications or chronological anachronisms. Returns:
- `historical_accuracy_score` (`0–100`), `is_historically_clean`
- `verified_authentic_motifs` (e.g., `umm_al_banin_madina` — Umm al-Banin receiving Bashir ibn Hadhlam's elegy in Medina)
- `distortions_and_warnings`
- `canonical_sources`: **الإرشاد للشيخ المفيد**, **اللهوف في قتلى الطفوف لابن طاووس**, **نفس المهموم للشيخ عباس القمي**

### 4.2 `--plan-stages` (`plan_poem_extend_stages`)
Automates `NC16` (max 3 vertical lines / `~23.5s` Extend window) before touching Flow Music:
- Extracts `[المُسْتَهَلّ]` for **Stage 1 (`stage_1_estehlal`)** and closes **Stage 6C (`grand_finale_stage_6c`)** with identical unison parentheses.
- Chunks poem body into `<= 3` vertical-line Extend blocks (`Stage_1_Body`, `3A`, ...) and computes `estimated_singing_sec`.
- Evaluates fit against **Method 1 (`+30s` Compose Extend)** vs. **Method 2 (`+60s` Producer Extend)** and emits explicit trailing-pad alerts (`method_2_pad_warning`) plus the local `vocal_pure_master` mastering command.

---

## 5. V52.0 Corpus Compiler & Iraqi/Bahrani/Fusha G2P Pipeline

Measured against the **127-section (`14,924`-token)** empirical Hussaini poetry corpus:
- **Vocalization Coverage:** `14,867 / 14,924` tokens vocalized (**`99.62%`**).
- **Strict Idempotency:** Re-running `detect_and_shape_dialect` on compiled output yields **0 idempotency failures** across all `127` sections.
- **Pipeline Ordering & Normalizations:**
  1. `sanitize_poem_decorations`: Strips extraneous ornamental symbols while preserving verse markers and section tags.
  2. `normalize_iraqi_orthographic_gaf`: Standardizes Swash-Kaf (`\u06AA -> ك`), Heh Doachashmee (`\u06BE -> ه`), and Farsi Yeh (`\u06CC -> ي`), while converting `كً` (`ك` + Fathatan), `كَـ`/`كـَ`, and curated `KAF_FATHA_TO_GAF_LEXICON` forms into **`گ`**.
  3. `de_cliticize_and_separate_words`: Spaces `..` pauses and separates agglutinated particles cleanly.
  4. `COMMON_CORPUS_LEXICON_V52` (`216` entries): High-frequency colloquial Iraqi/Bahrani forms (`وي`, `ويه`, `وياي`, `وياه`, `وياهم`, `وياها`, `اويه`, `اوياي`, `اوياه`, `اليه`, `وعلى`, `الحرام`, `اخت`, `يه`, `اي`, etc.) plus liturgical terms.
  5. `_vocalize_unseen_arabic_word`: Handles word-initial consonant `و`/`ي` without raw regex `\u` escape failures (`"\u064E\\g<1>"`).
  6. `enforce_iraqi_dhaa` runs **after** `shape_unseen_corpus_tokens` (protecting Quranic/Fusha homographs via `normalize_daad_dhaa_homographs` when Classical/Fusha dialect is active).
  7. `resolve_dialectal_and_prosodic_tanween` & `_finalize_hemistich_pause_sukun`: Uses non-greedy token matching (`\S+?`) + proper trailing punctuation handling (`…`, `.`, `]`).
