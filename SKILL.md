---
name: hussaini-production-studio
description: Comprehensive Hussaini audio production, poetic composition, microtonal Maqam and Tor architecture, AI studio prompt engineering (Flow Music, Suno, Udio), Arabic acoustic phonetics compiler, and 5-track DSP vocal montage engine.
allowed-tools: execute_bash view_file write_to_file google
---
# Hussaini Production Studio (V45.0 OMNI-ARCHITECT)

Structured router for authentic Hussaini poetic composition, microtonal Maqam/Tor architecture, **Flow Music `Producer Chat` Two-Step JSON Pre-Conditioning (`Module 39`)**, **Prefix-Aware Morphological Dialect Shaping, Safe Tanween & Anti-Slurring Word Separation (`Modules 40, 41 & 43`)**, **Pre-Generation Poem Linting (`--lint-poem`)**, and **5-Track SOS/RMS/LUFS Audio DSP Montage (`-14.0 LUFS` & `-1.0 dBTP`)**. Version-locked via root `VERSION` (`V45.0 OMNI-ARCHITECT`).

## When to Use

- Producing a Latmiya, Zanjeel, Shoor, Bandari, Mawal, Na'i, Abudhiyah, or Hussaini chant in **Google Flow Music (`Lyria`)**, Suno, or Udio.
- Composing or linting Hussaini poetry in Iraqi, Bahrani, Gulf, or Classical Arabic (Fusha) across traditional meters (`Nassari, Muwashah, Fayzi, Tajleeb, Maymar, Abudhiyah, Mawal, Hosa`).
- Emulating the melodic/rhythmic school or multi-Tor blending of renowned Radoods or Minbar Khutaba ethically via acoustic descriptors.
- Mastering raw vocal recordings (`8-bit, 16-bit, 24-bit, or 32-bit Mono/Stereo WAV` at `8kHz–48kHz`) with 5-Track DAW routing (`Latm, Dammam, Tasa, Zanjeel, Ahaat, Dynacord Echo, Husseiniya Reverb, -28 dBFS RMS Sidechain Ducking`).

## Modular Reference Map (Load Only What You Need)

Do **not** load all reference files at once. Read only the specific module needed for the current task:

1. **`references/modules/module_40_41_43_phonetics_and_dialects.md`**: Prefix-aware morphological word shaping (`ال، و، ب، ك، ل`), safe mid-line Tanween resolution, space-first de-cliticization (`use_tatweel=False`), Dhad/Dhaa (`ض/ظ`) dialect rules, and neutral tie handling (`iraqi_bahrani`).
2. **`references/modules/module_39_json_preconditioning.md`**: Two-Step JSON Session Pre-Conditioning protocol for Flow Music `Producer Chat` with account-agnostic `reference_clip_id=None` default (`<OPTIONAL_USER_CLIP_UUID>`).
3. **`references/modules/module_42_gireez_hosa_and_muharram_calendar.md`**: The Art of Gireez (`الگريز`), Iraqi Hosa (`3+1 Arjooza`), rare heritage Atwar (`Ushshaq, Huwaizawi, Shushtari, Dashti`), and the 10 Nights of Muharram & Safar calendar.
4. **`references/modules/experimental_ab_evaluation_and_human_review.md`**: Empirical A/B evaluation matrix (`Verified` rules vs. `Working Hypotheses`) and the **Mandatory Human, Poetic & Doctrinal Review Gate**.
5. **`references/radoods_and_khutaba_encyclopedia.md`**: Profiles of 20+ Radoods (14 schools), 8 Multi-Tor Blending Masters, 8 Minbar Khutaba, and the **7 Essential Vocal Timbres Matrix** (pure-English descriptors).
6. **`references/atwar_maqamat_and_poetry_guide.md`**: Complete 43-Module encyclopedia, 8-Archetype 40-Word Sound Prompt Library (`Module 36`), 23 Compositional Archetypes (`Sections 10–12`), 5-Track Zanjeel/Bandari DAW Matrix (`Section 13`), Minbar Na'i Phonetics (`Section 14`), Multi-Tor Blending (`Section 15`), and `QC1–QC12` troubleshooting.
7. **`scripts/hussaini_dsp_montage.py` & `tests/test_hussaini_modules.py`**: Executable Phonetics Compiler, Poem Linter, 5-Track DSP Montage Engine (`Pylint 10/10`), and automated `pytest` suite (`--cov-fail-under=70`).

## Hard Core Rules & Cultural Firewall

1. **Acoustic Purity (`100% Acapella & Heritage Matam Percussion`)**:
   - Permitted: Male lead vocal (`Baritone / Bass-Baritone`), unison `Raddada` choir, wordless `Ahaat` pads, `55Hz` bare-palm chest thud (`Latm`), acoustic `Dammam`, brass `Tasa/Kasat`, and metallic `Zanjeel` chains.
   - Strictly forbidden in `Sound`: Musical instruments (`piano, guitar, strings, synth, 808, trap`), the word `tenor`, transliterated Arabic terms (`bahha, tarjee', maddat, taqatee'`), or raw EQ numbers (`+4.5dB at 2.5kHz`). Apply EQ/filters post-generation via `audio__apply_effect`.
2. **Microtonal 24-EDO Maqam & Stage-1 Iso-Syllabic Lock (`Modules 34 & 38`)**:
   - Enforce Arabic 24-EDO quarter-tones (`Maqam Saba, Bayati, Hijaz, Lami, Kurd, Sikah, Rast`).
   - Format **Stage 1 (`Root Track`)** as **12 lines max (3 stanzas × 4 hemistichs)** sharing the **exact same prosodic meter and syllable count** (`validate_stage1_iso_syllabic_lock`), resolving to the **identical 4th-line anchor refrain**.
   - Lock **ONE single primary Maqam** in Stage 1 (`Rule B1`). Defer multi-Tor transitions (`Common Jins` melodic bridges) and Gireez shifts to **Stage 2 (`Extend`)**. Never mix Fusha and Colloquial in Stage 1.
3. **Morphological Dialect Shaping, Safe Tanween & Anti-Slurring Separation (`Modules 40, 41 & 43`)**:
   - **Space-First Anti-Slurring Separation (`Module 41`, `use_tatweel=False`)**: Separate attached vocatives, prepositions, interrogatives, and conjunctions with spaces (`ياحسين ⟵ يَا حْسَيْنْ`, `عالباب ⟵ عَلَى البَابْ`, `شصار ⟵ إِشْ صَارْ`).
   - **Safe Mid-Line Tanween & Sukun (`Module 40`)**: Convert colloquial mid-line Tanween to `-ِنْ` with a Kasra verb prefix only when unvocalized and not followed by Alif (`عينٍ تسيل ⟵ عَيْنِنْ تِسِيلْ`). End every hemistich with Sukun (`ْ`) or open vowel (`ظَامِئاً ⟵ ظَامِئَا`, exempting `ى`).
   - **Prefix-Aware Morphological Dialect Shaping (`Module 43`)**: Decompose prefixes (`ال، و، ب، ك، ل، وال، بال، كال، لل`) before matching stems (`الجمرة ⟵ الجَمْرَه`) while protecting derived passive participles (`المقلوب`):
     - **Iraqi (`iraqi`)**: Medial Damma (`گَلُبْ`, `وَ الصَبُرْ`, `كَ الجَمُرْ`), Euphrates Kasra (`چَبِدْ`, `دَمِعْ`), suffixed `گَلْبِي / گَلْبَكْ`, automatic Iraqi Dhaa `ظ` (`وَ يَا بُو فَاظِلْ`, `بِ ظْلُوعِي`), and **Final-Word Sudden Drop (`قاعدة الكسر`)**.
     - **Bahrani (`bahrani`)**: Light Kasra/Sukun (`گَلِبْ`, `وَ الصَبِرْ`, `گَلْبِي`, `گَلْبِكْ`), standard Dhad `ض` (`فَاضِلْ`), soft `-َه` Imala, and **3rd-Word Faizi Vibrato (`الترجيع الفايزي`)**.
     - **Neutral Tie (`iraqi_bahrani`)**: When dialect markers tie, apply **100% neutral shaping** (`قَلْبْ`, `قَلْبِي`, `وَ الصَبْرْ`, `الجَمْرَه`, `فَاضِلْ`) without biasing toward Iraqi `-ُ` or Bahrani `-ِ`.
4. **Ethical Emulation (`Module 24`)**: Translate living Radood/Khateeb styles into acoustic/Maqam descriptors (`references/radoods_and_khutaba_encyclopedia.md`); never inject a living person's name into voice-cloning fields.
5. **Strict Anti-Cloning & Account-Scoped Reference Clip Policy (`Rule 5 & Module 39`)**:
   - Never clone a previous track's `seed` or `reference_clip_id` onto an unrelated poem.
   - Flow Music clip UUIDs (`<OPTIONAL_USER_CLIP_UUID>`) are private to the account that created them; `reference_clip_id` defaults to `None` in `build_flowmusic_json_preconditioning`.
6. **Mandatory Human, Poetic & Doctrinal Review Gate**: Verify historical accuracy (`مقتل معتبر`), preserve poet attribution, and avoid repetitive opening clichés.

## Core Workflows

### Workflow 1: Pre-Generation Poem Linting & Phonetic Compilation
```bash
python3 scripts/hussaini_dsp_montage.py --lint-poem "ياحسين يا خويه شلون قلب وقلبي .. عينٍ تسيل بدمعي"
python3 scripts/hussaini_dsp_montage.py --compile-lyrics "ياحسين يا خويه شلون قلب وقلبي وقلبك والصبر والجمرة ويبوفاضل بضلوعي"
```

### Workflow 2: Two-Step JSON Pre-Conditioning & 40-Word Sound Prompt in Flow Music
1. **Step 1 (Pre-Conditioning in `New session` -> `Producer Chat`)**: Generate the JSON constitution via `build_flowmusic_json_preconditioning(dialect, maqam, bpm, reference_clip_id=None)` (`references/modules/module_39_json_preconditioning.md`) and lock it in session memory before calling `lyrics__register`.
2. **Step 2 (Register Pure-Arabic Lyrics & Generate with 40–50 Word English `Sound` Prompt)**:
   - Master 40-Word `Sound` Prompt (`58 BPM Maqam Saba` — see `Module 36` in `references/atwar_maqamat_and_poetry_guide.md`):
     `Traditional Iraqi and Bahrani Hussaini Latmiya, Thaqeel Faizi and Nazla style, Maqam Saba, 58 BPM, authentic Iraqi and Bahrani colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, emotional weep cracks, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments`
   - Pass `reference_clip_id="<OPTIONAL_USER_CLIP_UUID>"` only when anchoring to a personal workspace clip.
3. **Step 3 (Post-Generation DSP via `audio__apply_effect`)**:
   `Apply audio__apply_effect on the generated clip: HighPass filter at 85Hz, AdvancedEqualizer (cut 450Hz by -2.5dB, boost mid 1200Hz by +1.5dB, boost high-mid presence 2500Hz by +4.5dB), Compressor (ratio 3:1, threshold -12dB), Reverb (room_size 0.55, wet mix 0.18), and Limiter at -1.0dB.`

### Workflow 3: 5-Track SOS/RMS/LUFS Audio Montage & Automated CI Testing
```bash
python3 scripts/hussaini_dsp_montage.py \
  --input "<input_wav_path>" --output "<output_wav_path>" \
  --mode "<latm|zanjeel_iraqi|zanjeel_bahrani|shoor|bandari|mawal|nai>" \
  --bpm <bpm_value> --maqam-drone "<saba|bayati|hijaz|lami|kurd|rast>" \
  [--samples-dir "<folder>"] [--offset-ms <ms>] [--swing <0.0_to_0.35>] [--session-log "<json>"]

pytest -v --cov=scripts --cov-fail-under=70 tests/test_hussaini_modules.py
pylint scripts/hussaini_dsp_montage.py tests/test_hussaini_modules.py
```

## Critical Gotchas

- **`New session` vs. `Spaces` in Flow Music**: Always use **`New session`** for generating, extending, or remixing audio tracks. Use **`Spaces`** only for interactive web mini-apps (`Vibe-coding`).
- **100% Pure Arabic in `Lyrics`**: Use `[المُسْتَهَلّ]`, `[المَقْطَع الأَوَّل]` for headers, ` .. ` for breath pause, and reserve `(...)` **exclusively** for sung choir responses like `(مَوْلَايَ يَا حُسَيْنْ)`.
