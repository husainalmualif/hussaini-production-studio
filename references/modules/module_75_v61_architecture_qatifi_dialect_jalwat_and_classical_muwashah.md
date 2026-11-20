# Module 75 (V61.0 OMNI-ARCHITECT): Complete Hussaini Architecture (`code_artifact.html`), Qatifi vs. Bahrani vs. Iraqi Multi-Dialect Orthoepy (`NC35`), Joyful Mawlid Jalwat & Nasheeds, Classical Muwashahat/Ibtihalat with Bitanah, & Mid-Side Reverb / Mono Check DSP

## 1. Architectural Knowledge Absorbed from `معمارية اللطمية الحسينية` (`code_artifact.html`)

1. **The 5-Stage Dramatic Arc (`القوس الدرامي الخماسي`):**
   - `1) التمهيد / الموّال الاستهلالي` (Atmospheric entry) -> `2) المستهل` ("أب القصيدة" — Abdul-Shaheed Al-Thawr: warrants half the poet's effort as the collective anchor) -> `3) الأبيات السردية والوجدانية` (Sensory/symbolic imagery & dramatic persona/Qinaa) -> `4) الكسر / الرباط اللحني` (Rhythmic/modal break preventing monotony) -> `5) النعي / الخاتمة الفجائعية` (Devastating emotional peak).
2. **4 Regional Schools Matrix:**
   - **المدرسة العراقية:** Deep mournful Maqams (`Saba`, `Lami`, `Husseini`), rich Karbalaei/Najafi tearful vocabulary, fluid Qarid-to-colloquial transitions.
   - **المدرسة البحرينية:** Tight Mawkib Mustahall construction (1990s renewal), ideological/awareness depth, disciplined collective choral/Faujain arrangements.
   - **المدرسة القطيفية والأحسائية:** Preservation of heritage Atwar (`الطور الفائزي` — Mulla Ali bin Fayez, `الطور القطيفي` — Sheikh Fawzi Al-Saif canon), warm calm storytelling grief cadence intimate to Majlis listeners.
   - **الأثر الإيراني والآذري:** Fast `Shoor` (`115–145 BPM`) and epic choral layering (strictly governed by Majlis dignity).
3. **Vocal Physiology & Eastern Maqam Expansion (`13 -> 15 Maqams`):**
   - **Diaphragmatic breathing (`التنفس الحجابي`)** + gradual `Qarar -> Wasat (Mixed) -> Jawab (Head)` pitch ascent (`البدء بصوت منخفض متزن ثم العلو تدريجياً`).
   - **2 New Maqams Added to `MAQAM_FREQS`, `COMMON_JINS_GRAPH`, & `_MAQAM_24EDO_TEMPLATES`:**
     - **`husseini` (`مقام الحسيني`):** Branch of Bayati emphasizing the 5th scale degree (`14 QT` tension resolving to `10 QT`) with neutral 2nd (`3 QT`) & neutral 6th (`17 QT`) — foundational to Iraqi/Qatifi elegies and sacred Ibtihalat.
     - **`suznak` (`مقام السوزناك`):** Root *Jins Rast* (`0, 4, 7, 10 QT`) + upper *Jins Hijaz* on the 5th degree (`14, 16, 22 QT`) — premier Maqam for classical religious Muwashahat, Tawashih, Mawlid & dignified epic discourse.
   - **Ajam Trichord Flash Modulation (`ومضة العجم الثلاثي`):** Touching the Ajam trichord on degree 3 or 6 of Bayati/Saba/Kurd to create a brief flash of pride/hope before returning to grief.
4. **4-Layer Human Acapella Soundstage & 2 New DSP Gates:**
   - **4 Human Layers (`40 Hz–16 kHz`):** `1) Human Bass (40–140 Hz)`, `2) Sustained Zannah Drone`, `3) 24-EDO Quarter-Tone-Aware Choral Harmonies`, `4) Emotional Ahaat` + Chest Latm (`Sidechain 4:1–6:1, 2–4 dB ducking`).
   - **`apply_mid_side_reverb_clarity()` (`Mid-Side EQ 100–400 Hz`):** Attenuates low-mid mud (`< 320 Hz`) in the stereo Side channel (`L - R`) so dome reverb feels cavernous without clouding the center Radood vocal.
   - **`compute_mono_compatibility()` (`Mono Check`):** Computes L/R phase correlation & mono-sum energy retention (`dB`) inside `--audit-audio` so Mawkib PA mono speakers never lose choir or chest Latm punch.

---

## 2. Multi-Dialect Orthoepy Matrix: Qatifi (`قطيفي`) vs. Bahrani (`بحراني`) vs. Iraqi (`عراقي`) (`NC35`)

| Feature | **Qatifi (`اللهجة القطيفية`)** | **Bahrani (`اللهجة البحرانية`)** | **Iraqi (`اللهجة العراقية`)** |
|---|---|---|---|
| **Historical Kinship** | Core mainland branch of the mother Bahrani dialect (`إقليم البحرين التاريخي`: Qatif, Awamiyah, Tarout, Safwa, Saihat) | Island branch of the mother Bahrani dialect (`قرى ومدن البحرين`) | Mesopotamian `Gelet` Karbalaei / Najafi / Euphrates dialect |
| **Feminine 2nd-Person (`كِ`)** | **Kashkasha (`ش`)**: `شحوالش`, `بيتش`, `عليش`, `فيش`, `عيونش` | **Kashkasha (`ش`)**: `اشحالش`, `بيتش`, `عيونش`, `گلبش` | **`چ / تْش`** (`گلبچ`, `عيونچ`, `أبوچ`) |
| **Interdental `ث`** | Modern poetic Qatifi largely preserves `ث` or softens gently to `ت` (`ثلاثة/تلاثة`) | Traditional village Bahrani often shifts `ث -> ف` (`فلافة`, `كفير`) | Preserves `ث` cleanly (`ثلاثة`, `مثل`) |
| **Distinctive Markers** | `غناتي`, `هداويش`, `لاويه`, `عفر`, `إهني`, `امبى`, `چدي`, `خلف چبدي`, `شحوالش`, `هالحزة`, `واجد`, `مغربل`, `أبغى`, `ماني` | `بويي`, `خويي`, `ونتي`, `شنهو`, `منهو`, `ويش`, `أحين`, `إلين`, `امساعد`, `هالگفرة`, `اورّي اشموع`, `أجدامي` | `بويه`, `خويه`, `هسه`, `شگد`, `شلون`, `بلياك`, `ما ظل`, `تراچي`, `ذيچ`, `إبچفك`, `إعله`, `وگفت` |
| **Prosodic Intonation** | Calm, warm, intimate storytelling Faezi/Qatifi cadence | Crisp rhythmic Mawkib & Faujain dual-choir cadence | Deep heroic Qarar-to-Jawab Karbalaei vocal projection |
| **Flow Music Declaration** | `authentic Eastern Arabian Qatifi-Bahrani Gulf dialect` | `authentic Bahrani colloquial dialect` | `authentic Iraqi colloquial dialect` |

### `NC35` — Qatifi-Bahrani Clean `Lyria 3.5` Orthoepy Locks (Empirically Discovered in `Exp 27`)
1. **Explicit Vowel on `ش` Before Closed Consonant Clusters (`چبدي -> تشَبدي`, `چدي -> تشِدِي`, `مچان -> متشَان`, `چبير -> تشِبير`):** In `Exp 27 c03`, writing bare `تشبدي` before closed `بْد` split into 3 syllables (`تَشَبْدي`). Putting an explicit short vowel on `ش` (`تشَبدي`) locks `/tʃab.diː/` cleanly!
2. **No Final Shadda on `إهني` & Explicit Long Alif on `غَنَاتِي`:** In `Exp 27 c01`, `إهنيّ` shifted to `هَنِّيَّ` and `غَناتي` compressed to `غَنِّتي`. Always compile as **`إهني`** (no trailing Shadda) and **`غَنَاتِي`**, plus **`لاويّه`**, **`هَداويش`**, **`عَفَر`**, **`أمبى`**, **`هالحَزّة`**, **`واجِد`**, **`إشحوالِش`**.

---

## 3. Complete 4-Family Sacred Vocal Taxonomy & 2 New Live Flow Music Proofs (`Exp 27 & Exp 28` — 31 Cumulative Live Experiments)

| Exp | Genre & Sacred Family | Maqam Arc & BPM | Clip UUID & Duration | Blind `20s` Audit Score | Empirical Verdict & Honest Notes |
|---|---|---|---|---|---|
| **Exp 27** | **Joyful Shia Mawlid Jalwat & Nasheed** (Qatifi-Bahrani dialect — «جلوة المولد الشريف») | **Ajam -> Rast -> Suznak** (`98 BPM`) | `40f3ef1e-bdb9-4d38-9103-e2358e848113` (`2:34`) | **`9.3 / 10`** | 100% joyous Khaleeji/Qatifi Mawlid Jalwat with Daf + clapping + choral `الله`, **0% chest latm, 0% weeping, 0% piano**, clean finale stop. Exposed `إهنيّ`/`تشبدي` -> codified permanently as **`NC35`**. |
| **Exp 28** | **Classical Heritage Ibtihal + Religious Muwashah with Male Bitanah Choir** («ابتهال وموشح - يا نور طه») | **`0 BPM` Husseini Rubato -> `74 BPM` Suznak** (`المطلع/الدور/الخانة/التسليم`) | `6f531049-2ff0-4db2-9bbc-80a83eacda19` (`3:00`) | **`9.9 / 10`** *(ALL-TIME RECORD)* | **Spotless 0 BPM Rubato Maqam Husseini Ibtihal (`c00–c01`)** transitioning seamlessly into **74 BPM Maqam Suznak Muwashah with traditional male Bitanah choir & gentle Daf (`c02–c08`)**, authentic upper-5th Hijaz Khana modulation (`c05–c06`), 100% Classical Makharij, 0% latm, 0% piano, zero tail loop! |

### 4 New Fingerprints Added (`12 -> 16` in `MULTI_MAQAM_MELODIC_FINGERPRINT_LIBRARY_V60`)
1. `v61_qatifi_faezi_husseini_saba_66bpm` (Qatifi/Hasawi Faezi lamentation, `66 BPM`, `Husseini -> Bayati -> Saba`, Pure Axis 1)
2. `v61_minbar_dashti_qatifi_nai_0bpm` (Persian-Arabic `Tor Dashti` & Qatifi Rubato Minbar Na'i, `0 BPM`, Pure Solo)
3. `v61_qatifi_bahrani_jalwat_mawlid_ajam_rast_98bpm` (Joyful Qatifi-Bahrani Mawlid Jalwat & Shia Nasheed, `98 BPM`, `Ajam -> Rast -> Suznak` — `Exp 27`)
4. `v61_classical_muwashah_ibtihal_husseini_suznak_74bpm` (Classical Sacred `0 BPM` Husseini Ibtihal -> `74 BPM` Suznak Muwashah + Male Bitanah — `Exp 28`, **`9.9/10`**)
