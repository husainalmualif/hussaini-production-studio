# Module 77: V63.0 OMNI-ARCHITECT — Google Flow Music Two-Layer Architecture (`Gemini Producer` + `Lyria 3.5`), Stage-0 `MASTER_STATE` JSON Protocol, 5-Band Spectral Occupancy (`40 Hz–16 kHz`), 5-Minute Staged Word Budget, Maqam Audio Reference Matrix & Hybrid Stem-Split Mastering (`NC38–NC41`)

> **Sources Absorbed & Verified:** `C:\Users\husai\Desktop\Flow Music\google_flow_music_lyria_3_5_json.html` (including 2 quantitative SVG architectural blueprints, 4 JSON master templates, and 30 scholarly/engineering references) + Google DeepMind Official Lyria 3.5 Model Card & Prompt Guide + Google Flow Music Help (`Instructions`, `Flows`, `Memories`, `Remix`, `Stem Split`, `WAV 48 kHz`) + Sunofix / Kompozy / Mubert (`2–4 kHz` neural harshness, `SynthID`, commercial plan licensing).

---

## 1. Two-Layer Internal Architecture of Google Flow Music (`Lyria 3.5`)

Google Flow Music (evolved from Riffusion `2022` -> ProducerAI -> Google Labs Feb `2026` -> Flow Music Apr `2026` -> **`Lyria 3.5`** Jul `2026`) operates as two distinct layers:

1. **Layer 1 — Intelligent Director (`Gemini Producer`):** Stateful conversational LLM director managing project state (`Instructions`, `Flows` slash shortcuts, and `Memories`). Speaking to Layer 1 via **strict structured JSON** eliminates *Attention Leakage* (where prose mixes style directives into sung lyrics, drifts vocalist timbre across `Extend` passes, or muddles Maqam modulations).
2. **Layer 2 — Temporal Latent Diffusion Engine (`Lyria 3.5`):** Trained on Google TPUs via JAX & ML Pathways, operating as Latent Diffusion over temporal audio latents with a **hard `3:00` (`180s`) single-pass Temporal Latent Window ceiling** (upgraded from `30s` in Lyria 3), decoding high-resolution `48 kHz` stereo audio with imperceptible psychoacoustic **SynthID** watermarking. Also supports **Timestamped Timeline Tags** (`[0:00 - 0:50]`, `[0:50 - 1:35]`) and **Multimodal Image-to-Music scoring** (up to `10` still images).

---

## 2. Stage-0 `MASTER_STATE` Session Bootstrap & `inherit_master_state` (`NC38`)

Before generating a single second of audio in a multi-stage `5:00–5:30` production, execute **Stage 0** (`--build-v63-bootstrap track_a|track_b|track_c` / `build_v63_session_bootstrap_json()`):

- **`action`:** `"INITIALIZE_AND_LOCK_STATE_ONLY_DO_NOT_GENERATE"`
- **Confirmation Gate:** Require `Gemini Producer` to confirm locked `MASTER_STATE` rules in 3 bullet points and wait for Stage 1.
- **Persistent Personalization:** Save `master_state` under **Customize Producer -> `Instructions`** or as a reusable **`Flows`** slash shortcut; toggle **`Memories`** cleanly when switching dialects/genres.
- **Zero-Drift Chaining (Stages 2–4):** Every `EXTEND_SEAMLESSLY` and `EXTEND_AND_CONCLUDE` pass MUST include `"inherit_master_state": true`, explicit `time_range`, `transition_rule`, and a brief dialect/constraint anchor.

---

## 3. Five-Band Spectral Occupancy (`40 Hz–16 kHz`) & Anti-Negative-Prompt-Inversion (`NC39`)

`Lyria 3.5` maps instrumentation onto 5 frequency bands. Declaring `exclude_instruments` alone triggers **Negative-Prompt Inversion** (the commercial prior fills empty bands with oud, piano, or pop drums). `validate_spectral_occupancy_v63()` enforces positive acoustic replacement across ALL 5 bands:

| Frequency Band | Track A: Pure Acapella Latmiya (`track_a`) | Track B: Dignified Orchestral Nasheed (`track_b`) | Track C: Tawashih / Ibtihal / Mawlid (`track_c`) |
|---|---|---|---|
| **Band 1 (`40–120 Hz`)** | Human vocal bass drone + bare-chest Latm + heavy Bahraini Dammam | Stately timpani + traditional Bendir + warm bassoon & deep cellos | Deep Bitanah bass vocal drone + traditional Daf (Mawlid finale only) |
| **Band 2 (`120–400 Hz`)** | Male vocal humming pads (`Zannah`) + Radood Qarar chest resonance | Legato low strings + noble classical oud / clean acoustic guitar | Classical Munshid Qarar chest register + male Bitanah humming bed |
| **Band 3 (`400 Hz–2 kHz`)** | Layered human Ahaat + unison Al-Raddada choir + quarter-tone harmonies | Expressive solo oboe + reed ney + legato clarinet + balanced choir | Classical Muwashah melody + antiphonal male Bitanah responses |
| **Band 4 (`2–5 kHz`)** | Centered Solo Radood crisp Arabic diction & Shadda (`NC37`) | Centered dignified Baritone Munshid diction + noble brass swells | Crystal-clear Classical Arabic Tajweed diction & controlled melisma |
| **Band 5 (`5–16 kHz`)** | Large Hussaini hall natural reverb + vocal air + subtle Zanjeel | Solemn Tasa shimmer + spacious concert hall stereo reverb | Spacious mosque dome natural echo & delicate vocal breath air |

---

## 4. Five-Minute Staged Word Budget & Pacing (`NC40` — `--plan-v63-workflow`)

Because `Lyria 3.5`'s single-pass latent ceiling is **`3:00` (`180s`)**, a complete **`5:00–5:30`** 5-part Hussaini Dramatic Arc MUST run across **Stage 0 + 4 `Extend` passes** (`00:00–01:15`, `01:15–02:45`, `02:45–03:45`, `03:45–05:15`):

- **Breathing Allowance:** Reserve `~90s` for intro, melodic Kaser/Ahaat breaks, and tail decay -> **`3:30` (`210s`) net sung window**.
- **Net Sung Word Budget (`plan_v63_five_minute_word_budget()`):** **`280–350` net vocalized Arabic words** (`80–100 words/min`, preserving **`12–16s` per bayt** so phonemes and Shadda closures never compress!).
- **Tempo Matrix:** Heavy Slow Latm (`55–75 BPM`), Faezi (`72–102 BPM`), Nassari (`65–95 BPM`), Muwashah/Wahdat (`85–110 BPM`), Fast/Shoor (`115–145 BPM`).

---

## 5. Maqam Text-Adherence Tiers vs. Mandatory `30s` Vocal Reference (`--check-maqam-ref`)

`MAQAM_LYRIA35_ADHERENCE_AND_AUDIO_REF_MATRIX_V63` governs when JSON alone suffices vs. when **`Make tracks for my vocal`** / **`Remix your audio`** (`30s` vocal guide) is required to inject true 24-EDO pitch contours into Lyria 3.5 latents:

- **High Text Adherence (JSON-Only Safe):** `nahawand`, `kurd`, `lami`, `ajam`, `hijaz`, `hijaz_kar`, `nawa_athar`, `saba_zamzam` (`12-TET` safe).
- **Medium Text Adherence (Short Mustahal Reference Recommended):** `bayati`, `bayati_shuri`, `husseini`, `rast`, `suznak`.
- **Low-to-Medium Text Adherence (`30s` Vocal Reference Mandatory for Pure Quarter-Tones):** `saba`, `sikah`.

---

## 6. Dynamic `2.4–3.8 kHz` Lyria Harshness Tamer (`NC41`) & 7-Stage Hybrid DAW Pipeline

Neural vocoder artifacts in `Lyria 3.5` manifest as upper-midrange digital harshness / phase burbling around **`2.0–4.0 kHz`**. `apply_lyria_harshness_tamer_2_4khz()` (`--tame-lyria-harshness`) uses a **100% mono-safe linked mid-channel envelope follower** comparing `2.4–3.8 kHz` against `400–1800 Hz` core vocal warmth, dynamically attenuating harsh spikes up to `-2.8 dB` without dulling Arabic consonants.

**7-Stage Hybrid Post-Production Chain:**
1. **`Remix > Replace`** (`8–18s`) surgical fix for localized dialect/Shadda glitches (`NC32`).
2. **`Flow Music Stem Split` + `48 kHz WAV Export`** (isolate Radood, Choir, Latm, Strings; note faint algorithmic reverb bleed).
3. **`Melodyne` Manual 24-EDO** with `12-TET` Snap strictly OFF on quarter-tone Maqams (`NC36`).
4. **Dynamic EQ:** HPF `<80 Hz`, warmth cut `200–400 Hz`, Lyria harshness tamer `2.4–3.8 kHz` (`--tame-lyria-harshness`).
5. **Serial Compression (`2:1–4:1`) + De-Esser (`5–8 kHz`)** on `س، ص، ش، ز`.
6. **Mid-Side Reverb Clarity EQ + Sidechain Ducking (`4:1–6:1`, `2–4 dB`)**.
7. **Multi-Platform EBU R128 (`-14 / -16 / -18 / -23 LUFS`, `-1.0 dBTP`) + Mono Check** (SynthID persists transparently across processing; commercial release rights apply to paid `Starter / Plus / Member` plans).

---

## 7. Live Empirical Proof: `Exp 33` (36th Cumulative Flow Music Lab Experiment — Strict Zero-Flattery Audit)

- **Protocol Tested:** Two-turn **`V63.0` Stage-0 `MASTER_STATE` Bootstrap (`DO_NOT_GENERATE`) -> Stage-1 `Track A` Pure Acapella Qatifi-Bahrani Latmiya JSON (`5-Band Positive Spectral Occupancy`)** on **`Lyria 3.5`**.
- **Session URL:** `https://www.flowmusic.app/session/84261b1f-b31a-4094-8c2c-83d2cd00b613?t=true`
- **Track & Clip UUID:** `لطمية بحرانية — 01` (`2:53`, `173.323s`) — `1e09a84e-29b6-4b35-9d85-1ff8e5bac5ad`
- **Verified `V63.0` Breakthroughs:**
  1. **`NC38` Stage-0 Compliance (`100%`):** `Gemini Producer` obeyed `INITIALIZE_AND_LOCK_STATE_ONLY_DO_NOT_GENERATE` with zero premature generation, confirmed all 3 locked rule groups, and inherited `MASTER_STATE` into Stage 1.
  2. **`NC39` 5-Band Anti-Inversion (`100%`):** `passed_nc33_zero_artifact_gate: true` (`0` opening piano notes, `0` pop snare flags, `0` flagged chunks) — pure human vocal symphony (`Zannah`, `Ahaat`, bare-chest Latm, subtle Dammam, Matam hall reverb) with genuine `0 BPM` Rubato Na'i (`0:00–0:26`) -> `74 BPM` Mustahal (`0:27`) and `Mono Safe` (`0.741`).
  3. **Maqam Reference Matrix Confirmed:** Without a `30s` audio guide for quarter-tone Saba/Bayati, Lyria drifted toward 12-TET (`closest_maqam: ajam 0.944`), empirically validating why `saba` requires `mandatory_30s_make_tracks_for_my_vocal`.
- **Ruthless Vocal-Isolated `10s` Forensic Findings (`22` micro-slices — Zero Flattery):**
  - **New Permanent Discovery (`Tatweel U+0640` Ban in `--audit-orthoepy`):** At `0:01`, `أَهِـيْ` (containing Unicode Tatweel `ـ`) caused `Lyria 3.5` to hallucinate a fake `ب` (`أَهِبِي`)! Now automatically blocked by `tatweel_hallucination_traps` in `audit_fusha_shadda_wasl_and_makharij_v62()`.
  - **Other Critical Findings (`0:34–1:06`):** `هَالْبِيتْ مُظْلِمْ وَينْكُمْ` garbled to `مِتْوَيْنْكُمْ` on Chorus 1 & 2 (before singing 100% cleanly on Chorus 3 at `2:15`); on Chorus 2, `غَنَاتِي` became `عَنَاتِي` (`0:53`) and `هَدَاوِيشْ` dropped `ش` (`1:05`). Meanwhile `1:15–2:53` (`وَگَفْتِ إِهْنِي`, `عَفَرْ طَاحْ العَلَمْ`, and full Chorus 3/Outro `غَنَاتِي / مُظْلِمْ / لَاوِيَّه / هَدَاوِيشْ`) were crystal-clear Qatifi-Bahrani.
  - **Strict Zero-Flattery Score:** Architecture/Mix `9.3/10`, Orthoepy `6.8/10` (`3` critical defects) -> **`7.90 / 10` (`NEEDS_FIX_NOT_RELEASE_READY` — fixable via Tatweel removal + `Remix > Replace` on `0:30–1:08`)**.
