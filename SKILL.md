---
name: hussaini-production-studio
description: Comprehensive Hussaini audio production, poetic composition, microtonal Maqam and Tor architecture, AI studio prompt engineering (Flow Music, Suno, Udio), Arabic acoustic phonetics compiler, and 5-track DSP vocal montage engine.
allowed-tools: execute_bash view_file write_to_file google
---
# Hussaini Production Studio (V45.0 OMNI-ARCHITECT)

Structured router for authentic Hussaini poetic composition, microtonal Maqam/Tor architecture, **Flow Music `Producer Chat` Two-Step JSON Pre-Conditioning (`Module 39`)**, **Prefix-Aware Morphological Dialect Shaping, Safe Tanween & Anti-Slurring Word Separation (`Modules 40, 41 & 43`)**, **Studio Vocal-Synth, 3D Soundstage, Foley & Heavy Clips (`Module 44`)**, **Pre-Generation Poem Linting (`--lint-poem`)**, and **8-Mode 5-Track SOS/RMS/LUFS Audio DSP Montage (`-14.0 LUFS` & `-1.0 dBTP`)**. Version-locked via root `VERSION` (`V45.0 OMNI-ARCHITECT`).

## When to Use

- Producing a Latmiya, Heavy Studio Clip (`60–75 BPM`), Zanjeel, Shoor, Bandari, Mawal, Na'i, Abudhiyah, or Hussaini chant in **Google Flow Music (`Lyria`)**, Suno, or Udio.
- Composing or linting Hussaini poetry in Iraqi, Bahrani, Gulf, or Classical Arabic (Fusha) across traditional meters (`Ruba'i, Nassari, Muwashah, Fazza'iya, Fayzi, Tajleeb, Maymar, Abudhiyah, Mawal, Hosa`).
- Emulating the melodic/rhythmic school or multi-Tor blending of renowned Radoods or Minbar Khutaba ethically via acoustic descriptors.
- Mastering raw vocal recordings (`8/16/24/32-bit Mono/Stereo WAV` at `8kHz–48kHz`) with 5-Track DAW routing (`Double-Layered Latm + Human Sub-Bass, Dammam, Tasa, Zanjeel, Vocal Synth Strings, 3D Soundstage, Convolution Reverb, Foley, Audio Drop, -28 dBFS RMS Sidechain Ducking`).

## Modular Reference Map (Load Only What You Need)

1. **`references/modules/module_40_41_43_phonetics_and_dialects.md`**: Prefix-aware word shaping (`ال، و، ب، ك، ل`), Iraqi `كَـ ⟵ گ` & `آنَه`, safe Tanween, space-first de-cliticization (`use_tatweel=False`), Dhad/Dhaa (`ض/ظ`), neutral tie (`iraqi_bahrani`), and the **4-Movement Melodic Wave (`التيفال اللحني`)**.
2. **`references/modules/module_44_studio_production_and_heavy_clips.md`**: 3 Studio Tiers (`Pure Acapella`, `Vocal Synth Strings & Ambient Pads`, `Heavy Studio Clips 60–75 BPM`), Double-Layered Beat (`Chest + Palm Snap + Human Sub-Bass`), Sorrowful Woodwind Bridges (`Ney, Duduk, Clarinet`), `3D Soundstage` (`Center Dry Lead` vs. `Extreme L/R Choir & Convolution Reverb`), Foley (`wind, water, horses`), and `Audio Drop`.
3. **`references/modules/module_39_json_preconditioning.md`**: Two-Step JSON Session Pre-Conditioning for Flow Music `Producer Chat` (`reference_clip_id=None` default).
4. **`references/modules/module_42_gireez_hosa_and_muharram_calendar.md`**: The Art of Gireez (`الگريز`), Iraqi Hosa (`3+1 Arjooza`), rare heritage Atwar (`Ushshaq, Huwaizawi, Shushtari, Dashti`), and the 10 Nights of Muharram & Safar calendar.
5. **`references/modules/experimental_ab_evaluation_and_human_review.md`**: Empirical A/B evaluation matrix (`Verified` vs. `Working Hypotheses`) and **Human, Poetic & Doctrinal Review Gate**.
6. **`references/radoods_and_khutaba_encyclopedia.md`**: 20+ Radoods (14 schools), 8 Multi-Tor Masters, 8 Khutaba, and **7 Vocal Timbres Matrix**.
7. **`references/atwar_maqamat_and_poetry_guide.md`**: 43-Module encyclopedia, 8-Archetype 40-Word Sound Prompts (`Module 36`), 23 Archetypes, 5-Track DAW Matrix, and `QC1–QC12`.
8. **`scripts/hussaini_dsp_montage.py` & `tests/test_hussaini_modules.py`**: Phonetics Compiler, Linter, 8-Mode DSP Engine (`Pylint 10/10`), and `pytest` (`--cov-fail-under=70`).

## Hard Core Rules & Cultural Firewall

1. **Acoustic Purity & 3-Tier Studio Architecture (`Module 44`)**:
   - **Tier 1 & 2 (`Pure Acapella & Vocal Synth` — Default)**: Lead vocal (`Baritone`), `Raddada` choir (`Jawab & Qarar`), pharyngeal `Ahaat` pads, `Vocal Synth` humming strings, spontaneous `Ya Hussain` cries, `55Hz` chest thud + palm snap (`Latm`), `Dammam`, `Tasa`, `Zanjeel`. Forbid pop/dance instruments (`piano, guitar, 808, trap`), `tenor`, transliterated Arabic, or raw EQ numbers in `Sound`.
   - **Tier 3 (`Heavy Studio Clips 60–75 BPM`, when requested)**: Double-layered chest+palm beat with beat-synced human `Sub-Bass` hum, `3D Soundstage` (`100% Center Dry` lead + extreme `L/R` choir/pads with `Convolution Reverb`), Foley (`wind, water, horses`), `Audio Drop`, and optional solo woodwind bridges (`Ney, Duduk, Clarinet`).
2. **Microtonal 24-EDO Maqam & Stage-1 Iso-Syllabic Lock (`Modules 34 & 38`)**:
   - Enforce Arabic 24-EDO quarter-tones (`Maqam Saba, Bayati, Hijaz, Lami, Kurd, Nahawand, Sikah, Rast`) with smooth `Qarar-to-Jawab` legato transitions.
   - Format **Stage 1 (`Root Track`)** as **12 lines max (3 stanzas × 4 hemistichs)** sharing the **exact same prosodic meter and syllable count** (`validate_stage1_iso_syllabic_lock`) and resolving to the **identical 4th-line anchor refrain**.
   - Lock **ONE primary Maqam** in Stage 1 (`Rule B1`). Defer multi-Tor bridges (`Common Jins`) to **Stage 2 (`Extend`)**. Never mix Fusha and Colloquial in Stage 1.
3. **Morphological Dialect Shaping, Safe Tanween & Anti-Slurring (`Modules 40, 41 & 43`)**:
   - **Space-First Separation (`Module 41`, `use_tatweel=False` default)**: Separate attached vocatives, prepositions, and interrogatives (`ياحسين ⟵ يَا حْسَيْنْ`, `عالباب ⟵ عَلَى البَابْ`, `بغربتي ⟵ بِ غُرْبِتِي`, `شصار ⟵ إِشْ صَارْ`) and normalize Iraqi `كَـ ⟵ گ` (`اشكَـد ⟵ إِشْگَدْ`).
   - **Safe Mid-Line Tanween & End Sukun (`Module 40`)**: Convert mid-line Tanween to `-ِنْ` (`عينٍ تسيل ⟵ عَيْنِنْ تِسِيلْ`, protecting vocalized `نارٍ يَصْلَى` and vocative `دمعٍ ياحسين`). End every hemistich with Sukun (`ْ`) or long open vowel (`ظامِئاً ⟵ ظَامِئَا`, exempting `ى`).
   - **Prefix-Aware Dialect Shaping (`Module 43`)**: Decompose prefixes (`ال، و، ب، ك، ل، وال، بال، كال، لل`) before matching stems (`الجمرة ⟵ الجَمْرَه`, protecting `المقلوب`):
     - **Iraqi (`iraqi`)**: Medial Damma (`قلب ⟵ گَلُبْ`, `والصبر ⟵ وَ الصَبُرْ`), Euphrates Kasra (`چبد ⟵ چَبِدْ`, `دمع ⟵ دَمِعْ`, `صرت ⟵ صِرِتْ`, `كثر ⟵ كِثِرْ`), open `أنه ⟵ آنَه`, `قلبي ⟵ گَلْبِي`, `قلبك ⟵ گَلْبَكْ`, Iraqi Dhaa `ظ` (`ويبوفاضل ⟵ وَ يَا بُو فَاظِلْ`, `بضلوعي ⟵ بِ ظْلُوعِي`), and **Final-Word Drop (`قاعدة الكسر`)**.
     - **Bahrani (`bahrani`)**: Light Kasra (`قلب ⟵ گَلِبْ`, `والصبر ⟵ وَ الصَبِرْ`, `قلبي ⟵ گَلْبِي`, `قلبك ⟵ گَلْبِكْ`), Dhad `ض` (`فَاضِلْ`, `ضْلُوعِي`), and **3rd-Word Faizi Vibrato (`الترجيع الفايزي`)**.
     - **Neutral Tie (`iraqi_bahrani`)**: **100% neutral shaping** (`قلب ⟵ قَلْبْ`, `قلبي ⟵ قَلْبِي`, `والصبر ⟵ وَ الصَبْرْ`, `الجمرة ⟵ الجَمْرَه`, `فَاضِلْ`).
4. **Ethical Emulation & Anti-Cloning (`Modules 24 & 39`)**: Translate living Radood/Khateeb styles into acoustic descriptors; never reuse unrelated `seed`/`reference_clip_id` (`reference_clip_id=None` default).
5. **Mandatory Human, Poetic & Doctrinal Review Gate**: Verify historical accuracy (`مقتل معتبر`) and preserve poet attribution.

## Core Workflows

### Workflow 1: Pre-Generation Poem Linting & Phonetic Compilation
```bash
python3 scripts/hussaini_dsp_montage.py --lint-poem "ياحسين يا خويه شلون قلب وقلبي .. عينٍ تسيل بدمعي"
python3 scripts/hussaini_dsp_montage.py --compile-lyrics "ياحسين يا خويه شلون قلب وقلبي وقلبك والصبر والجمرة ويبوفاضل بضلوعي"
```

### Workflow 2: Two-Step JSON Pre-Conditioning & 40-Word Sound Prompt in Flow Music
1. **Step 1 (`New session` -> `Producer Chat`)**: Generate JSON constitution via `build_flowmusic_json_preconditioning(dialect, maqam, bpm, reference_clip_id=None)` (`references/modules/module_39_json_preconditioning.md`) and lock in session memory before registering lyrics.
2. **Step 2 (Register Pure-Arabic Lyrics & Generate with 40–50 Word English `Sound` Prompt)**:
   `Cinematic Heavy Studio Hussaini Latmiya, Maqam Saba and Kurd on D, 66 BPM, dry intimate center Baritone lead vocal, smooth legato Qarar to Jawab melody, double-layered chest thud and palm snap with deep human vocal sub-bass hum, wide 3D stereo pharyngeal Ahaat vocal-synth strings pad, Husseiniya convolution reverb, Pure Vocal Synth No Instruments`
3. **Step 3 (Post-Generation DSP via `audio__apply_effect`)**:
   `Apply audio__apply_effect on the generated clip: HighPass filter at 85Hz, AdvancedEqualizer (cut 450Hz by -2.5dB, boost mid 1200Hz by +1.5dB, boost high-mid presence 2500Hz by +4.5dB), Compressor (ratio 3:1, threshold -12dB), Reverb (room_size 0.55, wet mix 0.18), and Limiter at -1.0dB.`

### Workflow 3: 5-Track SOS/RMS/LUFS Audio Montage & Heavy Studio Clips (`Module 44`)
```bash
python3 scripts/hussaini_dsp_montage.py \
  --input "<input_wav_path>" \
  --output "<output_wav_path>" \
  --mode "<latm|heavy_clip|zanjeel_iraqi|zanjeel_bahrani|shoor|bandari|mawal|nai>" \
  --bpm <bpm_value> \
  --maqam-drone "<saba|bayati|hijaz|lami|kurd|rast|nahawand>" \
  [--foley "<none|wind|water|horses>"] \
  [--audio-drop-sec <climax_drop_start_sec>] \
  [--samples-dir "<optional_real_samples_folder>"] \
  [--offset-ms <optional_onset_ms>] \
  [--swing <0.0_to_0.35>] \
  [--session-log "<optional_ledger_json>"]

pytest -v --cov=scripts --cov-fail-under=70 tests/test_hussaini_modules.py
pylint scripts/hussaini_dsp_montage.py tests/test_hussaini_modules.py
```

## Critical Gotchas

- **`New session` vs. `Spaces` in Flow Music**: Always use **`New session`** for generating, extending, or remixing audio tracks.
- **100% Pure Arabic in `Lyrics`**: Use `[المُسْتَهَلّ]`, `[المَقْطَع الأَوَّل]` for section headers, ` .. ` for mid-verse breath pause, and reserve `(...)` **exclusively** for sung choir responses like `(مَوْلَايَ يَا حُسَيْنْ)`.
