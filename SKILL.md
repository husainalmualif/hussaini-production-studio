---
name: hussaini-production-studio
description: Comprehensive Hussaini audio production, poetic composition, microtonal Maqam and Tor architecture, AI studio prompt engineering (Flow Music, Suno, Udio), Arabic acoustic phonetics compiler, and 5-track DSP vocal montage engine.
---
# Hussaini Production Studio (V48.0 OMNI-ARCHITECT)

Structured router for authentic Hussaini composition, **Poetic Meter vs. Performance Tor Architecture**, microtonal 24-EDO Maqam engineering, **Flow Music JSON Pre-Conditioning (`Module 39`)**, **Morphological Dialect Shaping, Epenthetic Initial-Vowel Repair & Open Feminine Haa (`Modules 40, 41, 43 & 45`)**, **Studio Vocal-Synth, Formant Ahaat & Heavy Clips (`Module 44`)**, **Golden Larynx & Audio Reverse Engineering (`Module 45`)**, **Bahrani & Karbalaei Heritage Atwar, Abudhiyah Jinas & Zuhayri Mawal Validators (`Module 46 & 48`)**, **Strict Genre Taxonomy (`Module 47`)**, **Unified Bilingual Poem Linter (`--lint-poem`)**, and **16-Mode 5-Track Audio DSP Montage with Stem-Aware Percussion Replacement (`--replace-ai-percussion`, `-14.0 LUFS` & `-1.0 dBTP`)**. Version-locked via root `VERSION` (`V48.0 OMNI-ARCHITECT`).

## When to Use

- Producing a Latmiya, Heavy Studio Clip (`60–75 BPM`), Bahrani Mawkib (`Thulathi, Ruba'i, Haidari, Waqfa/Tajneeza, Muthakkal`), Zanjeel, Shoor, Bandari, Mawal Zuhayri, Na'i, Abudhiyah, Nasheed, Ibtihalat, or Tawashih in **Flow Music (`Lyria`)**, Suno, or Udio.
- Composing or linting Hussaini poetry in Iraqi, Bahrani, Gulf, or Fusha across traditional meters (`Nassari, Faizi, Mujarradat/Mahdad, Abudhiyah, Zuhayri Mawal, Tajleeb, Rukbani, Daksani, Muwashah, Hosa`).
- Reverse-engineering reference WAV tracks (`--extract-profile`) or mastering raw/split-stem vocal WAVs (`--replace-ai-percussion`) with 5-Track DAW routing (`Tempo-Synced Delay, Rosenberg Glottal + Formant Ahaat, Convolution Reverb, -28 dBFS RMS Ducking`).

## Modular Reference Map (Load Only What You Need)

1. **`references/modules/module_40_41_43_phonetics_and_dialects.md` & `references/modules/module_45_dialect_orthoepy_and_tashkeel_mastery.md`**: Prefix-aware shaping (`ال، و، ب، ك، ل`), Iraqi `كَـ ⟵ گ` & `آنَه`, demonstrative separation (`غَرِيبَه هَلْ حِچَايَه` with open feminine `ه` without Sukun), zero initial Sukun via soft epenthetic vowels (`دُمُوعْ، مِتُونِي، سِنِينِي، جُرُوحْ، تِگِلَّه`) or clitic liaison (`بِدْمُوعْ`), safe Tanween preserving trailing `..`, and **Audio Reverse Engineering (`extract_reference_audio_profile`)**.
2. **`references/modules/module_44_studio_production_and_heavy_clips.md` & `references/modules/module_46_rhythm_choir_and_tor_diversity.md`**: Studio Tiers (`Pure Acapella`, `Heavy Clips`), 20 Reference Tracks (`6 Rhythm/FX Families`), **Separation of Poetic Meter (`الوزن الشعري`) vs. Performance Tor (`الطور الأدائي`)**, Bahrani Heritage Modes (`bahrani_thulathi, bahrani_rubai, bahrani_haidari, bahrani_waqfa, bahrani_muthakkal` & Antiphonal `Faujain`), and Tempo-Synced Delay (`60000 / (bpm * 2)`).
3. **`references/modules/module_47_genre_taxonomy_latmiya_nasheed_ibtihalat_tawashih.md` & `references/modules/module_48_secrets_of_legendary_latmiyat.md`**: 4-Genre Taxonomy (`Latmiya/Nasheed/Ibtihalat/Tawashih`), Song-Leakage Blacklist, **5 Pillars of Legendary Latmiyat** (`audit_legendary_latmiya_pillars`), **Abudhiyah Jinas (`validate_abudhiyah_jinas`)**, **Zuhayri Mawal (`validate_zuhayri_mawal`)**, and **Interactive Ashouri Ahaat (`format_ashouri_interactive_ahaat`)**.
4. **`references/modules/module_39_json_preconditioning.md`**: Flow Music UI (`New session`, `Compose`, `Remix > Extend / Trim / Replace / Split stems`) & JSON Pre-Conditioning (`reference_clip_id=None`).
5. **`references/modules/module_42_gireez_hosa_and_muharram_calendar.md`**: Gireez (`الگريز`), Iraqi Hosa (`3+1 Arjooza`), heritage Atwar (`Ushshaq, Huwaizawi, Shushtari, Dashti`), and 10 Nights of Muharram & Safar.
6. **`references/modules/experimental_ab_evaluation_and_human_review.md`**: Empirical A/B evaluation matrix (`E1–E8`) and **Human, Poetic & Doctrinal Review Gate**.
7. **`references/radoods_and_khutaba_encyclopedia.md` & `references/atwar_maqamat_and_poetry_guide.md`**: 20+ Radoods (14 Schools), 8 Khutaba, 7 Vocal Timbres Matrix, 23 Legendary Archetypes, Sections 1–19, and `QC1–QC12`.

## Hard Core Rules & Cultural Firewall

1. **Acoustic Purity, 3-Tier Studio & Anti-Song-Drift Lock (`Module 44 & 47`)**:
   - **Tier 1 & 2 (`Pure Acapella & Vocal Humming` — Default)**: Lead vocal (`Baritone`), `Raddada` choir (`Jawab & Qarar`), pharyngeal `Ahaat` drone, `55Hz` chest thud + palm snap (`Latm`). **Never** write song-leakage words (`strings`, `synth`, `Nahawand`, `Studio-arranged`, `humming`, `pads`, `groove`, `Bandari`, `sub-bass`, `tenor`) or transliterated Arabic (`bahha`, `tarjee'`, `maddat`) in Flow Music `Sound` prompts for a pure Latmiya; end with `Pure Acapella No Instruments`.
   - **Tier 3 (`Heavy Studio Clips 60–75 BPM` & `--replace-ai-percussion`)**: Double-layered chest+palm beat + human `Sub-Bass` hum, Rosenberg Glottal + Formant `Ahaat` (`F1=730, F2=1090, F3=2440Hz`, `±4 cents` detune), `3D Soundstage`, Foley (`wind, water, horses`), and `Audio Drop`.
2. **Unified Bilingual Lyrics Spec & Stage-1 Iso-Syllabic Lock (`Modules 34, 38 & 48`)**:
   - Write pure Arabic section headers in Flow Music `Lyrics` (`[المُسْتَهَلّ]`, `[النَّزْلَة الأُولَى]`, `[الكَسْرَة وَالمُسْتَهَلّ]`) to prevent English vocal readouts (`Rule E1/QC5`), while all code validators (`validate_stage1_iso_syllabic_lock`, `audit_legendary_latmiya_pillars`, `lint_poem`) seamlessly accept both Arabic tags and English tags (`[Chorus]`, `[Verse 1]`) and both 12-line horizontal couplets and 20-line vertical 3-Part Golden Architecture (`4 Estehlal + 8 Nazla + 4 Kaser + 4 Estehlal`).
3. **Morphological Dialect Shaping, Zero Initial Sukun & Open Feminine Haa (`Modules 40, 41, 43, 45 & 48`)**:
   - **Zero Word-Initial Sukun & Zero Glottal Cluster Hamza**: Never start a word with Sukun (`ْ`) or artificial `إِCْ`; use soft epenthetic short vowels at line/word start (`دُمُوعْ، مِتُونِي، سِنِينِي، جُرُوحْ، تِگِلَّه، سِكِينَه`) or clitic liaison (`بِدْمُوعْ، وَ جُرُوحْ`), while preserving true Iraqi prosthetic Alif (`إِتْبَشْرِي، إِمْوَذَّرْ، إِچْفُوفْ`).
   - **Open Feminine Haa Without Sukun**: Always leave word-final feminine `ه/ة` open without Sukun (`غَرِيبَه هَلْ حِچَايَه، سَبِيَّه، خَرَابَه، مَسِيَّه`) to prevent heavy `-HHH` endings.
   - **Safe Mid-Line Tanween & Pre-Pause Sukun (`Module 40`)**: Convert mid-line Tanween to `-ِنْ` (`عينٍ تسيل ⟵ عَيْنِنْ تِسِيلْ`) and place end-of-hemistich Sukun (`ْ`) on the word **before** `..` (never `..ْ`).
4. **Ethical Emulation & Doctrinal Review Gate (`Modules 24 & 39`)**: Translate living Radood/Khateeb styles into acoustic descriptors (`reference_clip_id=None` default) and verify historical accuracy (`مقتل معتبر`) and poet attribution.

## Core Workflows

### Workflow 1: Poem Linting, Prosodic/Jinas Validation, Tor Recommendation & Audio Profiling
```bash
python3 scripts/hussaini_dsp_montage.py --lint-poem "ياحسين يا خويه شلون قلب وقلبي .. عينٍ تسيل بدمعي"
python3 scripts/hussaini_dsp_montage.py --compile-lyrics "ياحسين يا خويه شلون قلب وقلبي وقلبك والصبر والجمرة ويبوفاضل بضلوعي"
python3 scripts/hussaini_dsp_montage.py --validate-abudhiyah "گلبي بمأتمك يحسين ينصاب ..\nوذكرك من يمر الدمع ينصاب ..\nگلبي بدال گلبك ريت ينصاب ..\nوخدي دون خدك على الوطيه .."
python3 scripts/hussaini_dsp_montage.py --recommend-tor "هنيالي من خدمنك .. خادم وافتخر مولاي"
python3 scripts/hussaini_dsp_montage.py --extract-profile "reference_latmiya.wav"
```

### Workflow 2: 5-Track SOS/RMS/LUFS Audio Montage & Stem-Aware Percussion Replacement (`Module 44 & 46`)
```bash
python3 scripts/hussaini_dsp_montage.py \
  --input "<input_or_split_vocals_wav>" \
  --output "<output_mastered_wav>" \
  --mode "<latm|heavy_clip|thaqeel_muwazza|studio_arranged|bahrani_fast|bahrani_thulathi|bahrani_rubai|bahrani_haidari|bahrani_waqfa|bahrani_muthakkal|zanjeel_iraqi|zanjeel_bahrani|shoor|bandari|mawal|nai>" \
  --bpm <bpm_value> \
  --maqam-drone "<saba|bayati|hijaz|lami|kurd|rast|nahawand|sikah>" \
  [--replace-ai-percussion] \
  [--foley "<none|wind|water|horses>"] \
  [--audio-drop-sec <climax_drop_start_sec>]
```

## Critical Gotchas

- **One Poem = `New session` + JSON Pre-Conditioning**: Open `New session`, lock `Module 39` JSON in `Producer Chat` first, then generate via `Compose` and extend via `Remix > Extend`.
- **Forbidden Tags & Words**: Never use `[Bridge]` or `[Pre-Chorus]` in `Lyrics`, and never use song-leakage words (`Studio-arranged`, `humming`, `pads`, `groove`, `Bandari`, `sub-bass`, `tenor`) in `Sound` for a pure Latmiya.
