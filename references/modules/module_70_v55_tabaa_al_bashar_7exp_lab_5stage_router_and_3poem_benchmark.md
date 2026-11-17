# Module 70 — V55.0 7-Experiment «Tabaa Al-Bashar» Flow Music Lab (`NC18–NC22`), 4 Pillars of Husseini Dignity, 5-Stage Prosodic Router & 3-Poem Benchmark

> **Parent Module:** `SKILL.md` (`V55.0 OMNI-ARCHITECT`)  
> **Builds Upon:** `module_69_v54_175_mp3_acoustic_lab_24edo_and_studio_dsp.md` (`V54.0`) & `module_66_v51_field_evaluation_consultation_and_style_taxonomy.md` (`NC1–NC17`)  
> **Primary Runtime:** `scripts/hussaini_dsp_montage.py`

---

## 1. The 7 Controlled Live `flowmusic.app` Experiments on «طبع البشر» & Permanent Constraints `NC18–NC22`

Following the initial user critique of the first «طبع البشر» production (`v1`: skipped words `وَدَمْعِتِي / الرُّقَيَّه`, mispronounced `يِنْسَه الوَفَه` as `"ينسى هلوفا"`, and flat pop-nasheed vocal delivery with synthetic hip-hop beats), **7 controlled live experiments (`Exp-1` through `Exp-7`)** were executed on `https://www.flowmusic.app`, downloaded as raw MP3s, audited by ear, and profiled with `extract_reference_audio_profile` against the 175-track Basim Al-Karbalaei target (`sub_45_95_rel_db = -17.12 dB`, `core_600_1800_rel_db = -4.90 dB`, `pres_1800_4500_rel_db = -7.08 dB`):

| Exp ID | Method & Model | Sound / Remix Configuration | Duration | BPM | `f0` / Maqam | `LUFS` | `Sub (45–95Hz)` | `Core (0.6–1.8kHz)` | `Pres (1.8–4.5kHz)` | Empirical Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`Exp-1`** | `Compose` (`Lyria 3.5`, `58 BPM`) | Prompt contained `"55Hz chest thud, no drums, no snares"` | `219.9s` | `111` | `177.6 Hz` (`saba`) | `-11.88` | `-13.00 dB` | `-5.79 dB` | `-6.37 dB` | **Rejected:** Raw `"55Hz"` + negated `"no drums"` triggered cinematic sub-bass & Western snare loop. |
| **`Exp-2`** | `Compose` (`Lyria 3 Pro`, `58 BPM`) | Legacy `Lyria 3 Pro` + `"bare-palm chest slaps"` | `223.9s` | `115` | `188.4 Hz` (`bayati`) | `-13.99` | `-16.95 dB` | `-6.97 dB` | `-5.32 dB` | **Catastrophic Failure:** Collapsed at `0:19` into upbeat celebratory wedding-pop handclapping. |
| **`Exp-3`** | `Compose` (`Lyria 3.5`, `58 BPM`) | Zero percussion words; duplicated Estehlal lines unwrapped + wrapped | `180.0s` | `118` | `204.6 Hz` (`bayati`) | `-13.10` | `-14.37 dB` | `-6.95 dB` | `-6.04 dB` | **Partial:** Zero musical instruments, but duplicated Estehlal lines caused vocal stutter (`0:20–0:45`). |
| **`Exp-4` ★** | `Compose` (`Lyria 3.5`, `58 BPM`) | **`ashura_majlis_noha_58bpm_saba_lami_v55`** + `آااه .. مَولَايْ` opening | `234.8s` | `115` | `188.4 Hz` (`lami = 1.003`) | `-15.48` | **`-16.38 dB`** | `-6.28 dB` | `-6.44 dB` | **Breakthrough #1 (Rhythmic Majlis):** Closest to Basim (`-17.12 dB`), weeping Iraqi Radood + unison Raddada. |
| **`Exp-5` ★** | `Compose` (`Lyria 3.5`, `BPM=Auto`) | **`pure_acapella_weeping_noha_auto_bpm_saba_lami_v55`** | `204.2s` | `97` | `201.9 Hz` (`bayati/saba`) | `-14.37` | **`-45.28 dB`** | **`-4.38 dB`** | `-5.90 dB` | **Breakthrough #2 (100% Pure Vocal Noha):** Zero percussion (`-45.28 dB` sub), raw weeping Karbalaei voice. |
| **`Exp-6` ★** | `Remix > Cover` (`Strength = 0.42`) | `Exp-5` audio reference + `Exp-4` Majlis prompt (`58 BPM`) | `223.4s` | `79` | `172.3 Hz` (`bayati = 0.996`) | `-13.79` | **`-43.60 dB`** | **`-4.08 dB`** | `-6.89 dB` | **Breakthrough #3:** Preserved `Exp-5` weeping throat at lower baritone `172.3 Hz` with zero synthetic beats. |
| **`Exp-7`** | `Remix > Cover` (`Strength = 0.68`) | `Exp-5` audio reference + `Strength = 0.68` (`Less Similar`) | `219.9s` | `115` | `180.3 Hz` (`bayati/lami`) | `-11.90` | `-29.08 dB` | `-4.43 dB` | `-6.66 dB` | **Rejected:** High Cover strength (`>=0.65`) degraded Arabic consonant clarity in Stanza 2 (`~2:20`) and added beats. |

### Permanent Negative Constraints `NC18–NC22`

1. **`NC18` — Ban Raw DSP Frequencies (`53Hz`, `55Hz`, `320ms`) & Percussion/Slap Nouns in `Compose > Sound`:**
   - Writing raw numbers (`53Hz`, `55Hz`, `310ms`) in `Flow Music` Sound prompts triggers cinematic trailer sub-bass booms (`sub = -10.2 to -13.0 dB`).
   - Writing percussion/strike nouns (`chest slaps`, `percussion`, `drums`, `beats`, `strikes`, or even negated `no drums, no snares`) triggers Western pop/hip-hop snare loops.
   - Use **`ashura_majlis_noha_58bpm_saba_lami_v55`** (`"soft muffled bare chest thumping only. Pure human vocal acapella, strictly no musical instruments"`) for rhythmic `58 BPM` Majlis Latmiyah, or **`pure_acapella_weeping_noha_auto_bpm_saba_lami_v55`** (`BPM = Auto`) for 100% pure vocal Noha.
2. **`NC19` — Lock `Model = Lyria 3.5`, Ban Soft Pop Adjectives, & Ban Standalone Pre-Conditioning JSON:**
   - Always verify `Compose > Advanced > Model = Lyria 3.5`; **never** use `Lyria 3 Pro` (`Exp-2` wedding-clapping collapse).
   - Ban soft pop/nasheed adjectives (`warm, sincere, heartfelt, soft harmonies`) which flatten the Radood into a pop-nasheed singer; use `Heartbroken veteran Iraqi Karbalaei Radood chanting with intense emotional pain, weeping cracked baritone voice, soaring mournful climbs`.
   - Never send a standalone Pre-Conditioning JSON in `Producer Chat` without Stage 1 (`Session 4732f680` generated 2 unsolicited songs with hallucinated lyrics `"يا ضما الفرات"`).
3. **`NC20` — `Remix > Cover` Strength Cap (`<= 0.45`) & `Split Stems` Isolation:**
   - When running `Remix > Cover` on a pure vocal track (`Exp-5 -> Exp-6`), keep **`Strength <= 0.40–0.45`** (`More Similar`). Setting `Strength >= 0.65` (`Exp-7`) degrades Arabic pronunciation in later stanzas and re-introduces synthetic beats.
   - Always use `/library/my-songs -> More options -> Split stems` to isolate `Vocals` 100% cleanly before local 5-track DSP montage (`--mode thaqeel_muwazza` or `--mode vocal_pure_master`).
4. **`NC21` — Syntactic Pause Law (`حظر السكتة .. بين المتلازمين في أشطر الكسرة القصيرة`):**
   - Never place `..` inside a short 3-word clause (`الخِدْمَة إِنْكِسَارِي .. وَدَمْعِتِي` or `حَامِلْ جَمُرْتِي .. بِيدَيَّه`) between coordinate nouns, subject/predicate, verb/subject, or construct state: `Lyria 3.5` treats mid-line `..` before a single stranded word as phrase termination and skipped `وَدَمْعِتِي`. `heal_nc21_short_clause_pauses()` automatically removes mid-clause `..` before a single non-vocative word in 3-word clauses (`الخِدْمَة إِنْكِسَارِي وَ دَمْعِتِي`).
5. **`NC22` — Open-Vowel Liaison (`ى / ا`) & Definite-Article Kasra Lock before `الـ`:**
   - Before `الـ`, write open `-a` endings with `ى / ا` (`طَبْعِ البَشَرْ يِنْسَى الوَفَا`, never `يِنْسَه الوَفَه` which `Lyria 3.5` misreads as `"ينسى هلوفا"`), and place a liaison Kasra on the preceding consonant (`طَبْعِ البَشَرْ`, `مُو مِثِلِ البَشَرْ`, never `مِثِلْ البَشَرْ`).
   - In `[المُسْتَهَلّ]`, never duplicate the same hook line unwrapped + wrapped back-to-back (`Exp-3` stutter); open with a vocal sigh (`آااه .. مَولَايْ .. مَولَايْ`) followed by the parenthesized choir hook `(طَبْعِ البَشَرْ يِنْسَى الوَفَا .. بَسْ إِنْتَ مُو مِثِلِ البَشَرْ)`.

---

## 2. The 4 Pillars of Husseini Dignity & 5-Stage Prosodic/Dramatic/Phonetic Router

Integrating the architectural guidelines from the shared research dialogues (`celxHIkSDBIlC175M`, `oo3CACjm8BBqt0x9t`, and `1kbC1fkJ0Pyt`):

### 2.1 Four Pillars of Husseini Dignity (`الأركان الأربعة للوقار الحسيني`)
1. **Spiritual & Doctrinal Authenticity (`الأصالة الروحية والعقائدية`):** Every poem is audited by `verify_historical_narratives()` against *Al-Irshad*, *Al-Luhuf*, and *Nafas al-Mahmum* (`9` verified authentic motifs + `11` distortion/Ghuluw firewalls).
2. **Vocal & Melodic Sobriety (`الوقار الصوتي والمقامي`):** 24-EDO microtonal Maqam lock (`Saba`, `Saba Zamzam`, `Lami`, `Bayati`, `Hijaz`) with weeping Karbalaei/Bahrani chest delivery, strictly banning Western pop/tarab melody or celebratory clapping (`NC18–NC19`).
3. **Prosodic & Syntactic Integrity (`سلامة التقطيع العروضي والتلازم النحوي`):** Iso-syllabic hemistich balance (`validate_stage1_iso_syllabic_lock`), 3-line `NC16` Kasra formatting (`format_kasra_three_vertical_lines`), and `NC21` syntactic pause healing (`heal_nc21_short_clause_pauses`).
4. **Dialectal & Acoustic Precision (`الضبط اللهجي الدقيق والعزل الصوتي`):** Strict separation of Pure Iraqi (`إِعْلَه`, `گَلُبْ`, `إِبْچَفَّكْ`) vs. Pure Bahrani (`عَلَه / إِعْلَى`, `گَلِبْ`, `عِيُونِشْ`, `وِشْ نَاوِي`, `عَالْغَبْرَه`) and local EBU R128 mastering (`-14.0 LUFS / <= -1.0 dBTP`).

### 2.2 The 5-Stage Analysis (`five_stage_analysis` in `recommend_tor_and_rhythm_for_poem`)
Every call to `recommend_tor_and_rhythm_for_poem(text)` now returns a structured `five_stage_analysis` dictionary:
- **`stage_1_structural_and_prosodic`:** Poetic meter (`nassari`, `faizi`, `rukbani`, `thulathi`, `muwashah`, `fazzaiya`, `hosa`, `abudhiyah`, `zuhayri`), Arabic Wazn name, average syllables per hemistich, and iso-syllabic spread.
- **`stage_2_dramatic_and_thematic`:** Matched School (`School 01–09`) and emotional axis (`munajat_and_loyalty`, `ashura_tragedy_and_masaaib`, or `husseini_devotion`).
- **`stage_3_maqam_and_vocal_contour`:** Primary Maqam, 4-stage Common Jins Maqam progression arc, and performance Tor.
- **`stage_4_rhythmic_and_matam_architecture`:** Target BPM, recommended 18-mode DSP mode, and tempo-synced Dynacord echo delay (`ms`).
- **`stage_5_phonetic_g2p_and_flowmusic_lock`:** Detected dialect, Sound prompt dialect declaration, `Lyria 3.5` model lock, and `NC18–NC22` enforcement status.

---

## 3. Compiler & G2P Morphological Engine Upgrades (`V55.0`)

1. **Imperfect-Prefix Kasra Guard before `ا / آ / ى` (`_vocalize_unseen_arabic_word`):** Prevents `idx == 0` imperfect prefix Kasra (`يِـ / تِـ / نِـ`) when `nxt in ("ا", "آ", "ى")`, fixing `نَامُوسَكْ`, `يَابِسْ`, `تَالِيهَا`, `نَاطِرْ`, `نَاحَتْ`.
2. **Diphthong vs. Long `/iː/` Disambiguation before `ي`:** Word-initial `C + ي + C` defaults to diphthong Fatha (`عَينَكْ`, `سَيفَكْ`, `شَيبَه`, `هَيبَه`) except `_INITIAL_LONG_I_STEMS` (`فِي`, `بِيهْ`, `بِيهَا`, `بِيشْ`, `حِيرَه`, `عِيشَه`), while medial `idx > 0` `C + ي + C` defaults to long `/iː/` Kasra (`البَنِينْ`, `جَمِيلَكْ`, `دَخِيلَكْ`, `تِرِيدْ`, `يِعِيشْ`, `شَنِيعَه`, `الشَّرِيعَه`, `نَعِيمْ`, `الظَّهِيرَه`, `كَسِيرَه`, `وَحِيدَه`, `نَصِيبَه`) except before 1st/2nd-person past suffixes (`صَدَّيتْ`, `خَلَّيتْ`, `حَزَّيتْ`, `فِدَيتَه`, `نِطَيتَه`).
3. **Consonantal Glide `و / ي` & Broken Plural `مَفَاعِلْ / فَوَاعِلْ` Vocalization:** Recognizes `و / ي` as consonants when preceded or followed by `ا / آ` (`غَايِبْ`, `رَايِدْ`, `عَايِشْ`, `ذَايِبْ`, `زَايِرْ`, `طَايِحْ`, `التَّرَايِبْ`, `الشَّعَايِرْ`, `بَوَاتِرْ`, `لَوَاهِبْ`, `ثِيَابَكْ`, `هِيَامَه`, `لِلْقِيَامَه`) and assigns Kasra to the penultimate consonant of `مَفَاعِلْ / فَوَاعِلْ` (`المَشَاعِرْ`, `المَنَاحِرْ`, `بِالمَخَالِبْ`, `الخَنَاجِرْ`).
4. **Attached `بِالـ / كَالـ` + Sun-Letter Shadda + 2-Letter Stem Guard (`shape_token_morphologically`):** Formats `بال -> بِال` without an internal space, injects `\u0651` on sun-letter stems (`بِالدَّمِعْ`, `بِالتُّرُبْ`, `بِالصِّدِگْ`, `الرُّقَيَّه`, `الرَّزِيَّه`), and guards 2-letter stems (`بِلَا`, `لَمَّنْ`, `بِيهْ`, `بِيشْ`, `وَ لَوْ`) from false prefix splitting.
5. **Partial Poet Diacritic Normalization (`_is_partially_vocalized_poet_word`):** Words carrying only a poet Shadda (`إلاّ`, `حرّك`, `اتوسّد`, `يتحوّل`, `طوّل`, `إتخيّل`, `يهبّره`, `حزّيت`) or a single disambiguating vowel without Sukun (`أستعجِل`, `الحُسين`, `الوكِت`, `غُربه`, `المُستقر`, `والمجِد`, `مُخلد`, `واجزِم`, `لَمن`) are normalized into full, idempotent vocalization (`pass1 == pass2`).
6. **Pure-NumPy Signal Processing Fallback:** Provides a built-in pure-NumPy implementation of `butter`, `sosfilt`, `iirnotch`, `lfilter`, and `fftconvolve` whenever `scipy.signal` DLLs are unavailable or blocked by Windows Application Control policies.

---

## 4. The 3-Poem Benchmark Verification (`100%` G2P, `0` Unvocalized Tokens, `100%` Idempotency)

| Benchmark Poem | Poet | Detected Dialect | Routed Mode / BPM / Maqam | Extend Blocks | Historical Motifs Verified | Unvocalized Tokens | Idempotency (`pass1 == pass2`) |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| **1. «طبع البشر»** | محمد الإبراهيمي | `iraqi` (`iraq=2, bahr=0`) | `thaqeel_muwazza` / `58 BPM` / `saba_zamzam` (`tor_ashouri`) | `23` (`estehlal=5`) | `infant_harmala_arrow`, `ten_horsemen_trampling` | **`0`** (`100%`) | **`True`** |
| **2. «صورة جسد عالغبرة»** | نادر التتان | `bahrani` (`bahr=9, iraq=1`) | `bahrani_muthakkal` / `56 BPM` / `saba` (`tor_muthakkal_bahrani`) | `17` (`estehlal=3`) | `shimr_chest_and_nahr_martyrdom` | **`0`** (`100%`) | **`True`** |
| **3. «فلسفة الانتظار — اترجمها أم البنين»** | حيدر تركي الكربلائي | `iraqi` (`iraq=2, bahr=0`) | `thaqeel_muwazza` / `58 BPM` / `saba_zamzam` (`tor_ashouri`) | `16` (`estehlal=4`) | `imam_mahdi_intidhar_and_loyalty`, `umm_al_banin_madina` | **`0`** (`100%`) | **`True`** |
