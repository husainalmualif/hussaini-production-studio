---
name: hussaini-production-studio
description: Comprehensive Hussaini audio production, poetic composition, microtonal Maqam and Tor architecture, AI studio prompt engineering (Flow Music, Suno, Udio), Arabic acoustic phonetics compiler, and 5-track DSP vocal montage engine.
allowed-tools: execute_bash view_file write_to_file google
---
# Hussaini Production Studio (V45.0 OMNI-ARCHITECT)

Structured router for authentic Hussaini poetic composition, microtonal Maqam/Tor architecture, **Flow Music `Producer Chat` Two-Step JSON Pre-Conditioning (`Module 39`)**, **Prefix-Aware Morphological Dialect Shaping, Safe Tanween & Anti-Slurring Word Separation (`Modules 40, 41 & 43`)**, **Studio Vocal-Synth, 3D Soundstage, Foley & Heavy Clips (`Module 44`)**, **Pre-Generation Poem Linting (`--lint-poem`)**, and **8-Mode 5-Track SOS/RMS/LUFS Audio DSP Montage (`-14.0 LUFS` & `-1.0 dBTP`)**. Version-locked via root `VERSION` (`V45.0 OMNI-ARCHITECT`).

## When to Use

- Producing a Latmiya, Heavy Studio Clip (`60–75 BPM`), Zanjeel, Shoor, Bandari, Mawal, Na'i, or Abudhiyah in **Flow Music (`Lyria`)**, Suno, or Udio.
- Composing or linting Hussaini poetry in Iraqi, Bahrani, Gulf, or Fusha across traditional meters (`Ruba'i, Nassari, Muwashah, Fazza'iya, Fayzi, Tajleeb, Maymar, Abudhiyah, Mawal, Hosa`).
- Emulating renowned Radoods or Minbar Khutaba ethically via acoustic descriptors.
- Mastering raw vocal WAVs (`8/16/24/32-bit Mono/Stereo, 8k–48kHz`) with 5-Track DAW routing (`Double-Layered Latm + Human Sub-Bass, Dammam, Tasa, Zanjeel, Vocal Synth Strings, 3D Soundstage, Convolution Reverb, Foley, Audio Drop, -28 dBFS RMS Ducking`).

## Modular Reference Map (Load Only What You Need)

1. **`references/modules/module_40_41_43_phonetics_and_dialects.md`**: Prefix-aware shaping (`ال، و، ب، ك، ل`), Iraqi `كَـ ⟵ گ` & `آنَه`, zero initial Sukun, safe Tanween, Dhad/Dhaa (`ض/ظ`), and **4-Movement Melodic Wave (`التيفال اللحني`)**.
2. **`references/modules/module_44_studio_production_and_heavy_clips.md`**: 3 Studio Tiers (`Pure Acapella`, `Vocal Synth Pads`, `Heavy Studio Clips 60–75 BPM`), Double Beat (`Chest + Palm + Sub-Bass`), `3D Soundstage`, Foley, and `Audio Drop`.
3. **`references/modules/module_39_json_preconditioning.md`**: Flow Music Studio UI (`New session`, `Compose` panel, `Remix > Extend / Trim / Replace / Split stems`) & JSON Pre-Conditioning (`reference_clip_id=None`).
4. **`references/modules/module_42_gireez_hosa_and_muharram_calendar.md`**: The Art of Gireez (`الگريز`), Iraqi Hosa (`3+1 Arjooza`), rare heritage Atwar (`Ushshaq, Huwaizawi, Shushtari, Dashti`), and the 10 Nights of Muharram & Safar calendar.
5. **`references/modules/experimental_ab_evaluation_and_human_review.md`**: Empirical A/B evaluation matrix (`Verified` vs. `Working Hypotheses`) and **Human, Poetic & Doctrinal Review Gate**.
6. **`references/radoods_and_khutaba_encyclopedia.md`**: 20+ Radoods (14 schools), 8 Multi-Tor Masters, 8 Khutaba, and **7 Vocal Timbres Matrix**.
7. **`references/atwar_maqamat_and_poetry_guide.md`**: 43-Module encyclopedia, 8-Archetype 40-Word Sound Prompts (`Module 36`), 23 Archetypes, 5-Track DAW Matrix, and `QC1–QC12`.
8. **`scripts/hussaini_dsp_montage.py` & `tests/test_hussaini_modules.py`**: Phonetics Compiler, Linter, 8-Mode DSP Engine (`Pylint 10/10`), and `pytest` (`--cov-fail-under=70`).

## Hard Core Rules & Cultural Firewall

1. **Acoustic Purity, 3-Tier Studio & Anti-Song-Drift Lock (`Module 44`)**:
   - **Tier 1 & 2 (`Pure Acapella & Vocal Humming` — Default)**: Lead vocal (`Baritone`), `Raddada` choir (`Jawab & Qarar`), pharyngeal `Ahaat` humming drone, `Ya Hussain` cries, `55Hz` chest thud + palm snap (`Latm`), `Dammam`, `Tasa`, `Zanjeel`. **Never** write `strings`, `synth`, or `Nahawand` in Flow Music `Sound` prompts (triggers pop-song drift); use `pharyngeal Ahaat vocal humming choir drone` and `strictly non-musical, no instruments` in `Sound`, and generate `Vocal Synth` via local DSP (`--mode heavy_clip`).
   - **Tier 3 (`Heavy Studio Clips 60–66 BPM`)**: Double-layered chest+palm beat + human `Sub-Bass` hum, `3D Soundstage` (`Center Dry` lead + `L/R` choir/pads + `Convolution Reverb`), Foley (`wind, water, horses`), and `Audio Drop`.
2. **Microtonal 24-EDO Maqam & Stage-1 Iso-Syllabic Lock (`Modules 34 & 38`)**:
   - Enforce Arabic 24-EDO quarter-tones (`Maqam Saba, Bayati, Hijaz, Lami, Kurd, Sikah, Rast`) with smooth `Qarar-to-Jawab` legato transitions.
   - Format **Stage 1 (`Root Track`)** as **3–4 words per vertical line ending with `..`** (`split_long_lines_for_steady_pacing`) and resolving to the **identical refrain**. Defer multi-Tor bridges (`Common Jins`) to **Stage 2 (`Remix > Extend`)**.
3. **Morphological Dialect Shaping, Zero Initial Sukun & Anti-Slurring (`Modules 40, 41 & 43`)**:
   - **Zero Word-Initial Sukun & Space-First Separation (`Module 41`)**: Never start a word with Sukun (`ْ`); preserve Iraqi prosthetic Alif (`إِتْبَشْرِي، إِمْوَذَّرْ، إِچْفُوفْ`), write `بِأَرْضِ، شِيجِيبَه، مُدَمَّه`, separate clitics (`ياحسين ⟵ يَا حُسَيْنْ`, `عالباب ⟵ عَلَى البَابْ`), and normalize `كَـ ⟵ گ` (`اشكَـد ⟵ إِشْگَدْ`).
   - **Safe Mid-Line Tanween & End Sukun (`Module 40`)**: Convert mid-line Tanween to `-ِنْ` (`عينٍ تسيل ⟵ عَيْنِنْ تِسِيلْ`, protecting vocalized `نارٍ يَصْلَى` and vocative `دمعٍ ياحسين`). End every hemistich with Sukun (`ْ`) or long vowel (`ظَامِئاً ⟵ ظَامِئَا`, exempting `ى`).
   - **Prefix-Aware Dialect Shaping (`Module 43`)**: Decompose prefixes (`ال، و، ب، ك، ل، وال، بال، كال، لل`) before matching stems (`الجمرة ⟵ الجَمْرَه`, protecting `المقلوب`):
     - **Iraqi (`iraqi`)**: Medial Damma (`قلب ⟵ گَلُبْ`, `والصبر ⟵ وَ الصَبُرْ`), Kasra (`چبد ⟵ چَبِدْ`, `دمع ⟵ دَمِعْ`, `صرت ⟵ صِرِتْ`, `كثر ⟵ كِثِرْ`), open `أنه ⟵ آنَه`, `قلبي ⟵ گَلْبِي`, `قلبك ⟵ گَلْبَكْ`, Iraqi Dhaa `ظ` (`ويبوفاضل ⟵ وَ يَا بُو فَاظِلْ`, `بضلوعي ⟵ بِ ظْلُوعِي`), and **Final-Word Drop (`قاعدة الكسر`)**.
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

### Workflow 2: Flow Music Studio UI (`New session`, `Compose` Panel, & `Remix > Extend / Trim / Replace`)
1. **Step 1 (One New Poem = One Fresh `New session`)**: Always open a brand-new `New session` (`/session/<new-uuid>`) for every new poem (`references/modules/module_39_json_preconditioning.md`); never mix two different poems in the same session.
2. **Step 2 (Direct `Compose` Panel — `Lyrics`, `Sound`, `Details`, `Generate`)**: Put 100% pure vocalized Arabic in `Lyrics` (zero English words, zero word-initial Sukun, 3–4 words per vertical line ending with `..`), put the Title in `Details`, and put the 40–50 word funeral prompt in `Sound`:
   `Slow heavy Iraqi-Bahrani Husseini Latmiya, steady 58 BPM throughout, no tempo acceleration, passionate mourning solo Radood baritone with tearful inner sigh (Wannah), microtonal Maqam Saba with smooth modulation to Bayati and Lami, low-register Qarar human choral Ahaat drone, deep chest thud Latm, extended Husseiniya reverb, strictly non-musical, no instruments`
3. **Step 3 (Extending, Trimming & In-Place Repair via `... -> Remix`)**:
   - **`Remix > Extend`**: Mandatory for adding Stanzas 3, 4, 5 to the same voice/melody (`SETTINGS` time range + `Instruction` + `Edit Lyrics` + `Generate`).
   - **`Remix > Trim` + `Extend`**: Cut at the exact timestamp where a track drifts (e.g. `1:27`), then `Extend` from there.
   - **`Remix > Replace` & `Split stems`**: Fix mispronounced phrases in-place (`Replace`) or isolate vocal stems (`Split stems`).

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
