# Modules 54–65: The V50.0 Super-Algorithm & 175-Track Empirical Corpus Architecture

## 1. Empirical Foundation: The 175-Track Husseini Corpus (`24.24` Hours)

Across **175 complete Husseini Latmiyat tracks** (`1,454` minutes / `24.24` hours of audio analyzed by the 201-worker swarm), the global physical telemetry establishes the following laws:

- **Global Stanza Cycle Mean (`Module 62 / QC30`):** **`70.81 seconds`** per stanza (`69.19s` in Basim Al-Karbalaei, `69.73s` in Mohammed Bujabara, `75.29s` in Sheikh Hussein Al-Akraf, `78.82s` in Sayyid Salam Al-Hussaini). Because Google Flow Music (`Lyria 3.5`) generates a fixed maximum window of **`80 to 85 seconds`** per `Remix > Extend`, **one single stanza (max 6–7 couplets: 4 couplets `[النَّزْلَة]` + 2 couplets `[الكَسْرَة]` + 1–2 couplets `[المُسْتَهَلّ]`) consumes the entire `Extend` window**. Placing 2+ stanzas in a single `Extend` compresses `11.5s` couplets into `2.5s` (garbling words) and forces the `[المُسْتَهَلّ]` choir to collide over the solo Radood at second `47`.
- **Empirical 6-Band Spectral Curve (`Module 63 / QC35`):**
  - `Sub-Chest (40–90 Hz)`: `-9.26 dB` (Fundamental bare-palm chest thud anchored at **`53–68 Hz`**)
  - `Baritone Body (90–250 Hz)`: `-7.11 dB` (Boost `+1.5 dB @ 110 Hz`)
  - `Low-Mid Mud (250–600 Hz)`: `-4.80 dB` (Cut **`-2.8 dB @ 450 Hz`** to eliminate room boxiness)
  - `Pharyngeal Core (600–1800 Hz)`: `-4.99 dB` (Boost **`+1.8 dB @ 1200 Hz`**)
  - `Jawhari Presence & Slap (1800–4200 Hz)`: `-10.06 dB` (Boost **`+4.5 dB @ 2500 Hz`**)
  - `Air (4200–6000 Hz)`: `-20.57 dB`
- **Forensic Law of `Tasri'` (`التسريع` — `Module 54 / School 07`):**
  - Double-time `Tasri'` in Bahrani/Gulf and Karbalaei studio tracks (e.g., Ali Bouhamad, Basim Al-Karbalaei) is **double syllabic density (`2x` syllables per beat) over an unchanged `57–64 BPM` chest-thump grid**, never a `120 BPM` tempo doubling.

---

## 2. The 9 Master Husseini Schools (`Module 54`)

| School ID | Master School & Representative Radoods | Tracks | Thaqeel / Mawkib BPM | Primary 24-EDO Maqamat | Signature Atwar |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **`School 01`** | **Karbalaei Classical & Studio Master** (Al-Haj Basim Al-Karbalaei) | `22` | `55–63` / `71–86` | `saba, saba_zamzam, bayati, hijaz, lami, kurd` | `tor_muthakkal_karbalai, tor_nazla_karbalai, tor_darj_karbalai, tor_rukbani` |
| **`School 02`** | **Monumental Ahsa/Gulf Mawkib & Qafila** (Mohammed & Daniel Bujabara) | `49` | `55–64` / `67–92` | `saba, hijaz, bayati, sikah, lami` | `tor_ashouri_mawkib, tor_qafila_hidaa, tor_bahrani_muthakkal` |
| **`School 03`** | **Classical Bahrani Tawshih & Narrative Ballad** (Sheikh Hussein Al-Akraf) | `19` | `57–67` / `71–100` | `bayati, hijaz, saba, rast, nahawand` | `tor_tawshih_bahrani, tor_faizi_bahrani, tor_bahrani_thulathi, tor_waqfa_bahrani` |
| **`School 04`** | **Southern Iraqi Heavy Funeral March** (Sayyid Salam Al-Hussaini) | `9` | `54.5–60` / `74–109` | `lami, saba, saba_zamzam, kurd, bayati` | `tor_muthakkal_janoubi, tor_lami_iraqi, tor_rukbani` |
| **`School 05`** | **Euphrates Turaathi, Bandariyah, Hosa & Shoor** (Murtada Harb, Madin Al-Ayyashi, Sayyid Faqid) | `10` | `58–67` / `74–86` / `115–133` | `lami, bayati, kurd, saba` | `tor_nassari, tor_rukbani, tor_shoor_karbalai, tor_hosa_iraqi` |
| **`School 06`** | **Modern Najafi/Karbalai Melodic Dialogic** (Al-Janami, Al-Bayati, Qahtan, Sayyid Mohammed) | `11` | `55–67` / `75–133` | `bayati, kurd, saba, lami, hijaz` | `tor_darj_karbalai, tor_nazla_karbalai, tor_keadia` |
| **`School 07`** | **3D Intimate Studio & Bahrani/Gulf/Lebanese Heritage** (Bouhamad, Al-Khayyat, Al-Biladi, Al-Muwail, Khairuddin) | `10` | `55–63` / `71–92` | `kurd, saba, bayati, hijaz, lami` | `tor_faizi_bahrani, tor_muthakkal_bahrani, tor_studio_tasri` |
| **`School 08`** | **Basra, Wasit & Baghdad Heavy Mawkib & Zanjeel** (Al-Kaabi, Al-Saad, Khudur Abbas, Al-Amiri, Al-Bendawi) | `14` | `52–60` / `67–86` | `hijaz, lami, bayati, saba, saba_zamzam` | `tor_muthakkal, tor_zanjeel_iraqi, tor_zaarijawi, tor_janoubi` |
| **`School 09`** | **Persian Zamineh, Sangin, Shoor & Multilingual Noha** (Karimi, Rasoli, Taheri, Mohammadi, Sotoodeh) | `16` | `55–67` / `75–92` / `118–150` | `hijaz, bayati, kurd, saba, nahawand` | `tor_zamineh, tor_sangin, tor_shoor_haidari, tor_mashaya_bilingual` |

---

## 3. Modules 54–65 Architectural Specification

- **`Module 54` (Prosodic, Thematic & 9-School Router):** Routes any poem by meter (`Nassari, Faizi, Mujarradat, Abudhiyah, Zuhayri Mawal, Rukbani, Muwashah, Iraqi Hosa`), syllable spread (`<= 3`), dialect, and Muharram/Safar theme to one of the 9 Schools.
- **`Module 55` (24-EDO 6-Stage Common Jins Maqam Graph):** `Stage 0` (`0 BPM` Rubato Saba) -> `Stage 1 Root` (`58 BPM` Saba Zamzam & Bayati) -> `Stage 2 Extend 1` (`58 BPM` Lami & Saba Rukbani) -> `Stage 3 Extend 2 Climax` (`58 BPM` Saba Zamzam & High Hijaz Jawab) -> `Stage 4 Extend 3 Martyrs` (`60 BPM` Bayati & Saba) -> `Stage 5 Extend 4 Finale` (`56 BPM` Lami Kasra + `3.0s` Audio Drop).
- **`Module 56` (Doubled Opening Estehlal, 4-Line `(...)` Cap & Humming Bridge — `QC31`):** Cap every `[المُسْتَهَلّ]` choir block at **4 parenthesized `(...)` lines**. In Stage 1 Root, structure doubled opening Estehlals as `[المُسْتَهَلّ الأَوَّلْ]` (solo Radood lines with final `(...)` refrain line) + `[المُسْتَهَلّ]` (4 `(...)` unison choir lines) + a 4s closed-lip humming bridge (`مممم...`) before `[النَّزْلَة الأُولَى]`.
- **`Modules 57 & 58` (Acoustically Verified `Lyria 3.5` G2P Locks — `QC20–QC28, QC33, QC34`):**
  1. `QC20`: Write 1st-person plural clitic `-نه` after Meem/Noon with open upright Alif **`ـنَا`** (`مَآتِمْنَا، يِلِمْنَا، أُمْنَا، قَايِمْنَا`) to prevent splitting into `مِنَه`.
  2. `QC21`: Write open Alif Maqsura with upright Alif **`ا`** (`المُعَزَّا، أَنْعَا، بِالدِّمَا، أَبْطَا`) and active participles with Yaa (`وَالْقَايِمْ رَسَمْ، قَايِمْ، لِلثَّايْرِينْ`).
  3. `QC22`: Lock geminated/closed monosyllables (`فِي طَفِّ كَرْبَلَا، هَلْ شَهَرْ الأَلَمْ`).
  4. `QC23`: Ban Fusha Damma on the 2nd consonant of CVC nouns (`حزن، گلب، جرح، المهر`) -> enforce Kasra/Sukun (`وْ حِزِنْ عَاشُورْ قَايِمْ، حِزْنَكْ خَفْ، يَا گَلْبِ اليِهِيدْ، وَ يَا جَرْحِ يِلْتَمْ، مِنْ ظَهْرِ المُهْرْ`).
  5. `QC24 & QC28`: Prevent tokenizer lexical substitution and construct garbling (`يِبْكِي بِلَا شُعُورْ، مَقْطُوعَةِ النُّحُورْ، بِدَمْعَه مَا تِنْكَفْ، وَ فَرَّتْ أَيْتَامَكْ، وَ حَرْگَتْ خِيَامَكْ، السَّلَّابْ گِدَّامَكْ، تِنْزِفْ أَلَامَكْ، وَ دَلِيلَكْ طَرْ`).
  6. `QC33`: **Selective Prosthetic Alif Whitelist** — restrict `إِCْ` to verified stems (`إِحْسَينْ، إِعْلَه، إِبْچَفَّكْ، إِبْچِدَمْ، إِعْيُونِي، إِچْفُوفَكْ، إِبْگَلْبِي، إِبْگَاعْ، إِبْهَيبَه، إِبْسَبِي`). Keep `خِيَمْ / خِيَامَكْ` without prosthetic Alif (preventing verb mutation `تِخَيَّمْ`) and use pure Kasra `بِـ` before `ن/س/م/ك/ال` (`بِالمَذَابِحْ، بِسْيَاطِ الحِقِدْ`).
  7. `QC34`: **Kaf vs. Gaf & Feminine Haa Boundary Lock** — lock `رِكْضَتْ أَشْكَالْ`, `وَدَّعْتَكْ`, and geminated feminine rhymes without final Damma inflation (`إِبْهَيبَه وَ عِزَّه / غُزَّه / مَعَزَّه / مِعْتَزَّه`).
- **`Modules 59–62` (11–12s Couplet Calibration, Numbered Kaser, `lyrics_register_verbatim` & 80s Single-Stanza Law — `QC26, QC27, QC29, QC30, QC32`):**
  - Number every Kaser header uniquely (`[الكَسْرَة الأُولَى]` .. `[الكَسْرَة الخَامِسَه]`) separate from `[المُسْتَهَلّ]`.
  - Include top-level `lyrics_register_verbatim` in every Stage JSON.
  - Ban orphan 1-word vertical lines (`QC32`).
- **`Modules 63–65` (Spectral Mastering, Cross-Dialect Bridge & Canonical V50.0 CLI/GitHub Gate — `QC35`):**
  - Trim trailing drift (`Remix > Trim`) before `Remix > Extend`, apply Step 4 `audio__apply_effect` EQ, and master locally via `scripts/hussaini_dsp_montage.py`.
