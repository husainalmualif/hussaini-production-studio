# بروتوكول التوليد الإلزامي عبر حزم `JSON` لكل مرحلة ولكل قسم شعري (`Module 53: Mandatory Per-Stage & Per-Section JSON Orchestration Schema`) — V48.5 OMNI-ARCHITECT (Rev 2)

توثّق هذه الوحدة القاعدة الحاكمة الجديدة في **`V48.5 OMNI-ARCHITECT (Rev 2)`** (`QC19`): **يُحظر إخراج مقاطع القصيدة كنص عادي مجرّد (`Bare Plain-Text Stanzas`) بدون تغليفها الكامل داخل حزمة `JSON` توجيهية لكل مرحلة (`Stage JSON`) ولكل قسم شعري (`Section JSON`)** عند العمل عبر `Producer Chat` في **Google Flow Music (`Lyria 3.5`)**.

---

## 1. القانون الحاكم (`Core Rule — Module 53 & QC19`)

1. **التهيئة أولاً (`Step 1`):** إرسال دستور الجلسة `references/hussaini_os_v48_5_constitution.json` (`session_mode: "Pre_Conditioning_Lock_Wait_For_Stage_JSON"`) في `Producer Chat` وانتظار تأكيد القفل قبل إرسال المرحلة الأولى.
2. **حظر النص المجرّد (`Zero Bare Stanzas`):** كل مرحلة توليدية — سواء كانت:
   - `Stage 0` (مقدمة النعي المنبري الفصيح الحر `0 BPM Rubato` في جلسة منفصلة)،
   - `Stage 1` (التوليد التأسيسي `58–60 BPM` في `Producer Chat`)،
   - `Stage 2..N` (مراحل التمديد `Remix > Extend` عبر الجنس المشترك `Module 52`)،
   - `Step 4` (أمر المعالجة الصوتية اللاحقة `Master DSP` عبر `audio__apply_effect`) —
   **يجب أن تُصاغ ككائن `JSON` متكامل** يحتوي بداخله على مصفوفة `sections[]` تُعرّف التوجيه الصوتي الدقيق لكل قسم (`[المُسْتَهَلّ]`, `[النَّزْلَة الأُولَى]`, `[الكَسْرَة وَالمُسْتَهَلّ]`).
3. **نظافة مصفوفة `lyrics_arabic` (`Clean Arabic Array Rule`):**
   - تبقى جميع مفاتيح التوجيه الإنجليزية معزولة في الحقول المخصصة لها، بينما تحتوي مصفوفة `"lyrics_arabic"` داخل كل قسم على **الأشطر العربية المشكولة العمودية الصافية فقط** منتهية بـ `..`، مع إحاطة أشطر `[المُسْتَهَلّ]` حصراً بالأقواس الدائرية `(...)` لضمان إنشادها جماعياً 100% من قِبل الردادة (`QC18`)، ودون أي حرف لاتيني أو أقواس `{...}` تسبب انعكاس `RTL` (`QC5 / QC17`).

---

## 2. المفاتيح الإلزامية لحزمة المرحلة وحزمة القسم (`Required JSON Schema Keys`)

### أ. المفاتيح الـ `6` الإلزامية لكل مرحلة (`required_stage_json_keys`):
1. `"stage_id"` — معرف المرحلة (`"stage_0_fusha_intro"`, `"stage_1_root"`, `"stage_2_extend_1"`, `"stage_3_extend_2_climax"`, `"stage_4_extend_3_finale"`).
2. `"execution_command"` — أمر التنفيذ الصريح لوكيل `Producer Chat` (تثبيت `Instrumental: OFF`، تمرير `sound_description`، وتسجيل الأشطر العربية فقط في `lyrics__register`).
3. `"title"` — عنوان القصيدة بالعربية الفصيحة أو الدارجة النظيفة لحقل `Details`.
4. `"global_bpm"` — السرعة الإيقاعية المعتمدة للمرحلة (`58` أو `60` للثقيل الكربلائي، `56` لخاتمة الوحشة، `0` للنعي الحر).
5. `"sound_description"` — البرومبت الإنجليزي القياسي النقي (`45–56` كلمة) المختوم بـ `Pure Acapella No Instruments` والخالي تماماً من مفردات القائمة السوداء (`Module 50`).
6. `"sections"` — مصفوفة الأقسام الشعرية (`Array of Section Directive Objects`).

### ب. المفاتيح الـ `10` الإلزامية لكل قسم شعري (`required_section_json_keys`):
1. `"section_tag"` — الوسم العربي الصرف (`"[المُسْتَهَلّ]"`، `"[النَّزْلَة الأُولَى]"`، `"[الكَسْرَة وَالمُسْتَهَلّ]"` — ويُحظر `[Chorus]` و`[Verse]` و`[Bridge]`).
2. `"performer"` — المؤدي الفعلي (`"100% Wide Unison Male Raddada Congregation Choir"` للمستهل، و`"Solo Commanding Jawhari Baritone Radood"` للنزلة وأشطر الكسرة الأربعة الأولى).
3. `"meter_and_syllables"` — البحر/الوزن وعدد المقاطع العروضية المقفلة (`Iso-Syllabic Lock`).
4. `"tempo_feel"` — الإحساس الإيقاعي والنبض الموكبي (`Steady heavy 58 BPM chest pulse`).
5. `"tor_and_maqam"` — الطور الأدائي والمقام الميكروتونالي (`24-EDO`) وطبقة القرار/الجواب.
6. `"throat_and_maddat_dynamics"` — ديناميكيات الحنجرة والمدّات بدون بكاء خلفي متداخل (`Natural laryngeal rasp & open diphthong Maddat`).
7. `"rhythm_chants_and_sfx"` — اللطم الصدري البشري (`55Hz thud + 2.4kHz palm slap`) ونَفَس المعزين.
8. `"audio_engineering_3d"` — التموضع المكاني ثلاثي الأبعاد (`100% Center Dry Lead` مقابل `+-85% Wide Raddada Choir`).
9. `"dialect_phonetic_locks"` — أقفال اللهجة النقية والألف الوقائية العراقية (`إِبْچَفَّكْ / إِعْيُونِي / إِحْسَينْ / إِعْلَه / غَرِيبَه`).
10. `"lyrics_arabic"` — مصفوفة الأشطر العربية المشكولة العمودية الجاهزة للتسجيل الصوتي المباشر.

---

## 3. نموذج تطبيقي قياسي لحزمة `Stage 1 Root JSON` (`58 BPM Saba Zamzam`)

```json
{
  "stage_id": "stage_1_root",
  "execution_command": "Execute Stage 1 Root generation with Instrumental mode strictly OFF. Register ONLY Arabic section_tag headers and lyrics_arabic lines into lyrics__register, and set sound_description in Sound.",
  "title": "يَا إِحْسَينْ إِبْگَلْبِي",
  "global_bpm": 58,
  "sound_description": "Mournful Traditional Iraqi Hussaini Latmiya, heavy Karbalai Muthakkal and Nazla style, Maqam Saba Zamzam and Bayati, 58 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, passionate microtonal melisma, heavy 55Hz bare-palm chest thud, 310ms tape echo, 3.5s Husseiniya reverb, wide unison male Raddada response, Pure Acapella No Instruments",
  "sections": [
    {
      "section_tag": "[المُسْتَهَلّ]",
      "performer": "100% Wide Unison Male Raddada Congregation Choir (Zero Solo Lead)",
      "meter_and_syllables": "Nassari / 7-8 uniform prosodic syllables per vertical line",
      "tempo_feel": "58 BPM solemn heavy Karbalai Muthakkal chest-strike lock",
      "tor_and_maqam": "Tor Muthakkal Karbalai — Maqam Saba Zamzam & Bayati (Qarar & Jawab octave unison)",
      "throat_and_maddat_dynamics": "Unified congregation chest resonance with prolonged open vowel Maddat before '..'",
      "rhythm_chants_and_sfx": "Synchronized 55Hz bare-palm chest thud + Matam congregation breath",
      "audio_engineering_3d": "85% wide L/R Husseiniya hall stereo field, 3.5s dome reverb",
      "dialect_phonetic_locks": "Pure Iraqi colloquial isolation: إِحْسَينْ، إِبْگَلْبِي، إِخْيَامَكْ (unmarked diphthong glides)",
      "lyrics_arabic": [
        "(يَا إِحْسَينْ إِبْگَلْبِي) ..",
        "(صَوْتَكْ يِسْرِي إِبْدَمِّي) ..",
        "(مَا أَنْسَى إِخْيَامَكْ) ..",
        "(يَا سُلْطَانْ هُمُومِي) .."
      ]
    }
  ]
}
```

---

## 4. التوليد والتحقق الآلي عبر أداة السطر البرمجي (`CLI`)

```bash
python3 scripts/hussaini_dsp_montage.py --build-stage-json "[المُسْتَهَلّ]\nيَا إِحْسَينْ إِبْگَلْبِي ..\n[النَّزْلَة الأُولَى]\nوُگَفِتْ إِعْلَه البَابْ .."
```
