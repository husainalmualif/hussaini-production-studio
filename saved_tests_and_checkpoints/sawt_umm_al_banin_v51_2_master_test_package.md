# الحزمة الإنتاجية والاختبارية الشاملة المعتمدة (`V51.2 OMNI-ARCHITECT`) — قصيدة «صُوتْ أُمِّ البَنِينْ يِصِيحْ — يَبِنْ حَذْلَمْ»

> [!IMPORTANT]
> **مرجع الاختبار الكامل لجلسة المحادثة الجديدة (`Stages 1 to 6C — 3-Vertical-Line Kasra Locked`):**
> تضم هذه الوثيقة الحزمة الكاملة لقصيدة **«صُوتْ أُمِّ البَنِينْ يِصِيحْ»** بعد تطبيق جميع القواعد السلبية الموثقة سمعياً (`NC1–NC17`)، بما فيها:
> - **`NC1`:** حظر ذكر أي اسم لآلة موسيقية (`Oud, Ney, Flute, Violin, Cello, Guitar, Piano, Drum Kit`) في جميع البرومبتات وكائن التهيئة.
> - **`NC11 & NC12`:** قصر المرحلة الأولى (`Stage 1 Root`) على المقطع الأول فقط، وتمرير النص كاملاً في حقل `lyrics` الموحد لمنع القفز عن المستهل الافتتاحي.
> - **`NC16` (قانون الأسطر العمودية الثلاثة في الكسرة — `23.5s Extend Law`):** صياغة كل كسرة (`2B, 3B, 4B, 5B, 6B`) في **`3 أسطر عمودية حصراً` (`~21.5s`)** تماماً مثل النزلة (`2A, 3A, 4A, 5A, 6A`) لضمان غناء `بيت القفلة` كاملاً بنسبة `100%` داخل نافذة الـ `23.5` ثانية دون أي بتر.
> - **`NC17` (التطهير الإجباري لحقل `Lyrics` قبل كل تمديد):** مسح صندوق `Compose > Lyrics` بالكامل (`Ctrl+A -> Delete`) قبل كل خطوة تمديد في الطريقتين الأولى والثانية لمنع تداخل أو تكرار الأبيات السابقة.

---

## أولاً: الخطوة التأسيسية المشتركة للطريقتين (`Step 1: Pre-Conditioning JSON in Producer Chat`)

افتح جلسة جديدة (`New session`) في `Flow Music`، وأرسل كائن التهيئة التالي في **`Producer Chat`** أولاً (أو إذا كنت ستبدأ التمديد مباشرةً من ملف التأسيس الناجح لديك، انتقل مباشرةً إلى **ثالثاً: مراحل التمديد `2A–6C`**):

```json
{
  "husseini_session_constitution": {
    "version": "V51.2_OMNI_ARCHITECT",
    "poem_title": "صُوتْ أُمِّ البَنِينْ يِصِيحْ — يَبِنْ حَذْلَمْ",
    "artistic_style": "Traditional_Husseini_Vocal_Symphony_100_Percent_Human_Voices_And_Chest_Matam",
    "dialect_lock": "Pure_Iraqi_Karbalai_Dialect_With_Terminal_Sukun",
    "maqam_and_tempo_lock": {
      "primary_maqam": "Maqam Saba & Bayati (24-EDO Sad Lament)",
      "tempo_bpm": 60,
      "vocal_register": "Controlled dignified middle-register baritone delivery, strictly no high-pitched screaming"
    },
    "strict_negative_constraints_nc1_to_nc17": [
      "NC1: 100% Human Vocal and Chest-Beat Matam Percussion ONLY. Zero melodic instruments.",
      "NC3-NC15: Strictly follow all Arabic diacritics (Tashkeel) and pauses (..) in the Lyrics panel.",
      "NC16: Every Extend stage (2A-6B) consists of strictly 3 vertical lines (~21.5s) so the final couplet is sung 100% completely inside the 23.5s Extend window.",
      "NC17: Completely overwrite and clear any previous stage lyrics before registering new stage lyrics."
    ],
    "session_directive": "Lock these rules for the entire session. Do not generate audio until Stage 1 is provided."
  }
}
```

---

## ثانياً: المرحلة الأولى التأسيسية (`Stage 1 Root` — المقطع الأول فقط)

> [!TIP]
> **ملاحظة:** إذا كنتَ ستستخدم ملف التأسيس الجاهز لديك ([صوت أم البنين (توزيع آخر).mp3](file:///c:/Users/husai/Desktop/%D9%84%D8%B7%D9%85%D9%8A%D8%A7%D8%AA%20%D8%AA%D8%AC%D8%B1%D8%A8%D8%A9/Compose%20%20Lyrics/%D8%B5%D9%88%D8%AA%20%D8%A3%D9%85%20%D8%A7%D9%84%D8%A8%D9%86%D9%8A%D9%86%20(%D8%AA%D9%88%D8%B2%D9%8A%D8%B9%20%D8%A2%D8%AE%D8%B1).mp3) عند `01:40`، أو [صوت أم البنين.mp3](file:///c:/Users/husai/Desktop/%D9%84%D8%B7%D9%85%D9%8A%D8%A7%D8%AA%20%D8%AA%D8%AC%D8%B1%D8%A8%D8%A9/Compose%20%20Lyrics/%D8%B5%D9%88%D8%AA%20%D8%A3%D9%85%20%D8%A7%D9%84%D8%A8%D9%86%D9%8A%D9%86.mp3) عند `01:31`، أو [المرحلة 1 التأسيسية (1).mp3](file:///c:/Users/husai/Desktop/%D9%84%D8%B7%D9%85%D9%8A%D8%A7%D8%AA%20%D8%AA%D8%AC%D8%B1%D8%A8%D8%A9/JSON/%D8%B5%D9%8F%D9%88%D8%AA%D9%92%20%D8%A3%D9%8F%D9%85%D9%90%D9%91%20%D8%A7%D9%84%D8%A8%D9%8E%D9%86%D9%90%D9%8A%D9%86%D9%92%20%D9%8A%D9%90%D8%B5%D9%90%D9%8A%D8%AD%D9%92%20%E2%80%94%20%D8%A7%D9%84%D9%85%D8%B1%D8%AD%D9%84%D8%A9%201%20%D8%A7%D9%84%D8%AA%D8%A3%D8%B3%D9%8A%D8%B3%D9%8A%D8%A9%20(1).mp3) عند `01:41`)، يمكنك تخطي هذا القسم والبدء مباشرةً من **ثالثاً: مراحل التمديد (`2A–6C`)**.

### أ) التأسيس بالطريقة الأولى (`Compose > Lyrics`)
- **حقل `Title`:**
```text
صُوتْ أُمِّ البَنِينْ يِصِيحْ — يَبِنْ حَذْلَمْ
```
- **حقل `Sound`:**
```text
Slow 60 BPM traditional Iraqi Husseini Matam lament in sorrowful Maqam Saba and Bayati. Warm, deep, grief-stricken solo Iraqi Radood baritone vocal with controlled middle-register delivery and natural emotional vibrato, answered by a solemn unison male Husseini choir on the parenthesized refrain lines. Accompanied ONLY by deep muffled rhythmic chest-beat Matam thuds and multi-layered human vocal Ahaat harmonies in a resonant sacred hall reverb. 100% pure human vocal and chest-percussion arrangement, strictly no musical instruments.
```
- **حقل `Lyrics` (`3 أسطر للنزلة 1 + 3 أسطر للكسرة 1`):**
```text
[المُسْتَهَلّ]
صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ ..
(صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ)

[النَّزْلَة الأُولَى]
لَمَّنْ رَدْ إِبِنْ حَذْلَمْ .. يِنْعَى وُيِصْرَخْ بْصُوتَه ..
إِجَتَه .. أُمّ الگَمَرْ وَتْصِيحْ .. يَا هَالنَّاعِي بْسُكُوتَه ..
تِگِلَّه يَبِنْ حَذْلَمْ گُولْ .. عَنْ إِحْسَيْنْ وُإِخُوتَه ..

[الكَسْرَة الأُولَى]
أَرِيدْ أَنْشِدْ رِدَتْ نَشْدَه .. رَدْ لِدْيَارَهْ لَوْ بَعْدَهْ ..
دَلِيلِي انْگِسَمْ نُصَّينْ .. وَرَاهُمْ طَايْحَه بْشِدَّه ..

[المُسْتَهَلّ]
(صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ)
```

### ب) التأسيس بالطريقة الثانية (`JSON` في `Producer Chat`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_1_Root_Foundation",
    "title": "صُوتْ أُمِّ البَنِينْ يِصِيحْ — المرحلة 1 التأسيسية",
    "operation_mode": "CREATE_ROOT_TRACK_STANZA_1_ONLY",
    "lyrics_panel_action": "OVERWRITE_WITH_EXACT_VERBATIM_ARABIC_LYRICS_STARTING_WITH_MUSTAHALL",
    "sound_prompt": "Slow 60 BPM traditional Iraqi Husseini Matam lament in sorrowful Maqam Saba and Bayati. Warm, deep, grief-stricken solo Iraqi Radood baritone vocal with controlled middle-register delivery and natural emotional vibrato, answered by a solemn unison male Husseini choir on the parenthesized refrain lines. Accompanied ONLY by deep muffled rhythmic chest-beat Matam thuds and multi-layered human vocal Ahaat harmonies in a resonant sacred hall reverb. 100% pure human vocal and chest-percussion arrangement, strictly no musical instruments.",
    "lyrics": "[المُسْتَهَلّ]\nصُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ ..\n(صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ)\n\n[النَّزْلَة الأُولَى]\nلَمَّنْ رَدْ إِبِنْ حَذْلَمْ .. يِنْعَى وُيِصْرَخْ بْصُوتَه ..\nإِجَتَه .. أُمّ الگَمَرْ وَتْصِيحْ .. يَا هَالنَّاعِي بْسُكُوتَه ..\nتِگِلَّه يَبِنْ حَذْلَمْ گُولْ .. عَنْ إِحْسَيْنْ وُإِخُوتَه ..\n\n[الكَسْرَة الأُولَى]\nأَرِيدْ أَنْشِدْ رِدَتْ نَشْدَه .. رَدْ لِدْيَارَهْ لَوْ بَعْدَهْ ..\nدَلِيلِي انْگِسَمْ نُصَّينْ .. وَرَاهُمْ طَايْحَه بْشِدَّه ..\n\n[المُسْتَهَلّ]\n(صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ)"
  }
}
```

---

## ثالثاً: مراحل التمديد الكاملة (`Stages 2A to 6C — V51.2 3-Vertical-Line Kasra Fix`)

### المسار الأول: التمديد بطريقة `Compose > Lyrics` (`Remix > Extend`)
> [!WARNING]
> **القاعدة الذهبية (`NC17`):** في كل خطوة اضغط `Remix > Extend`، **امسح كل النص القديم من صندوق `Lyrics` تماماً (`Ctrl+A -> Delete`)**، ثم الصق الأسطر الـ 3 للخطوة الحالية فقط!

#### خطوة التمديد `2A` — النَّزْلَة الثَّانِيَة (`3 أسطر عمودية = 22s`)
```text
[النَّزْلَة الثَّانِيَة]
يِگِلْهَا عَظَّمْ اللّٰه أَجْرِچْ .. عَبْدُاللّٰه وُگَعْ بِالْبَرْ ..
وُمِنْ بَعْدَه تَرَى عُثْمَانْ .. ظَلْ إِعْلَه الثَّرَى مُوذَرْ ..
يَالْحُرَّه وُتَرَى الثَّالِثْ .. أَخَبْرِچْ وُگَعْ جَعْفَرْ ..
```

#### خطوة التمديد `2B` — الكَسْرَة الثَّانِيَة (`3 أسطر عمودية = 21.5s` — حل `NC16`)
```text
[الكَسْرَة الثَّانِيَة]
صَاحَتْ وَالدَّمِعْ بَادِي .. بِشِرْ گَطَّعِتْ إِفَّادِي ..
مَا أَنْشِدَكْ عَلَى أَوْلَادِي ..
عَلَى إِحْسَيْنْ النَّشِدْ كِلَّه .. اشْتَاگَيْتْ أَنْظُرْ لْخَدَّه ..
```

#### خطوة التمديد `3A` — النَّزْلَة الثَّالِثَة (`3 أسطر عمودية = 22s`)
```text
[النَّزْلَة الثَّالِثَة]
يِگِلْهَا الرَّابِعْ الْعَبَّاسْ .. يَمْ الْمَشْرَعَه مَچْتُوفْ ..
عَلَى عَيْنَه سَهَمْ نَابِتْ .. وُظَلْ إِعْلَه النَّهَرْ مَلْهُوفْ ..
وُظَلَّتْ مِنْ وَرَاهْ زَيْنَبْ .. يَمْ عَبَّاسْ مَكْسُورَه ..
```

#### خطوة التمديد `3B` — الكَسْرَة الثَّالِثَة (`3 أسطر عمودية = 21.5s` — حل `NC16`)
```text
[الكَسْرَة الثَّالِثَة]
صَاحَتْ گِلِّي عَاللِّي صَارْ .. لَا تِحْچِيلِي عَالْأَقْمَارْ ..
گَلْبِي مِنِ الصُّبُحْ مِحْتَارْ ..
أَرِيدَنْ خَبَرْ عَنْ إِحْسَيْنْ .. دِگِلِّي الْوَلِي إِحْسَيْنْ إِشْلُونْ ..
```

#### خطوة التمديد `4A` — النَّزْلَة الرَّابِعَة (`3 أسطر عمودية = 22s`)
```text
[النَّزْلَة الرَّابِعَة]
صَاحْ وُدَمْعِتَه تِجْرِي .. أَخَبْرِچْ ذَبْحَوْا الْغَالِي ..
عَلَى التِّرْبَانْ ظَلْ عَارِي .. وُجِسْمَه بِالدِّمَه مَالِي ..
وُالْخَيْلْ إِعْلَه صَدْرَه تْدُوسْ .. مَا مِنَّه كِتِرْ سَالِي ..
```

#### خطوة التمديد `4B` — الكَسْرَة الرَّابِعَة (`3 أسطر عمودية = 21.5s` — حل `NC16`)
```text
[الكَسْرَة الرَّابِعَة]
وُعُگْبَه الْخِيَمْ حَرْگُوهَا .. وُزَيْنَبْ غَصُبْ سَلْبُوهَا ..
وُلِلشَّامَاتْ وَدُّوهَا ..
رَدَّوْا إِلِچْ حَرَمْ وُأَطْفَالْ .. وُالسَّجَّادْ ظَلْ وَحْدَه ..
```

#### خطوة التمديد `5A` — النَّزْلَة الخَامِسَة (`3 أسطر عمودية = 22s`)
```text
[النَّزْلَة الخَامِسَة]
صَاحَتْ يَبْنِي الْمَذْبُوحْ .. يَالْچِنِتْ الْهَوَى لِيَّه ..
مِتَانِيتَكْ تِرِدْ كِلْ يُومْ .. چَا لَيْشْ گَطَعِتْ بِيَّه ..
كِلْهُمْ فِدْوَه يِرْحُولَكْ .. مِنْ نُورَكْ گِطَعْ ضَيَّه ..
```

#### خطوة التمديد `5B` — الكَسْرَة الخَامِسَة (`3 أسطر عمودية = 21.5s` — حل `NC16`)
```text
[الكَسْرَة الخَامِسَة]
كِلْهُمْ مُوتَى مَعْقُولَه .. وِيَّاهُمْ رَيْتْ مَقْتُولَه ..
وُبِالتَّابُوتْ مَشْيُولَه ..
گَبُلْ هَاللَّحْظَه لَوْ مَيْتَه .. وُلَا أَعِيشَنْ بَعَدْ مُدَّه ..
```

#### خطوة التمديد `6A` — النَّزْلَة السَّادِسَة (`3 أسطر عمودية = 22s`)
```text
[النَّزْلَة السَّادِسَة]
رَاحَتْ تِصْرَخْ لْزَيْنَبْ .. يَا يُمَّا الْبِگَا بْرَاسِچْ ..
آنِي سْمَعِتْ وُانْذِهْلَيْتْ .. چَانْ إِشْلُونْ إِحْسَاسِچْ ..
وُشِفْتِيهُمْ بْشُوفْ الْعَيْنْ .. كِلْهَا مْذَبِّحَه نَاسِچْ ..
```

#### خطوة التمديد `6B` — الكَسْرَة السَّادِسَة (`3 أسطر عمودية = 21.5s` — حل `NC16`)
```text
[الكَسْرَة السَّادِسَة]
إِشْلُونْ إِنْتِي تْحَمَّلْتِي .. حْيُودْ إِعْلَه الْأَرُضْ شِفْتِي ..
شْكُبُرْ صَبْرِچْ وُمَا مِتِّي ..
صَبْرِچْ مَا تْحِدَّه حْدُودْ .. رَغُمْ هَمِّچْ عَبَرْ حَدَّه ..
```

#### خطوة التمديد `6C` — الخَاتِمَة والمُسْتَهَلّ الأَخِير (`2 سطرين عموديين = 22s`)
```text
[المُسْتَهَلّ]
صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ ..
(صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ)
```

---

### المسار الثاني: التمديد بطريقة `JSON` في `Producer Chat` (`V51.2 — 3-Vertical-Line Locked`)
> [!WARNING]
> **القاعدة الذهبية (`NC17`):** قبل إرسال كائن `JSON` لأي مرحلة تمديد في `Producer Chat`، افتح تبويب `Compose > Lyrics` وامسح النص القديم منه يدوياً (`Ctrl+A -> Delete`)، ثم أرسل كائن الـ `JSON` التالي في `Producer Chat`.

#### 1. كائن التمديد `Stage 2A` (`النَّزْلَة الثَّانِيَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_2A_Extend_Nazla_2",
    "operation_mode": "EXTEND_FROM_STAGE_1_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in Maqam Bayati descending to Saba. Solo grief-stricken Iraqi Radood vocal ONLY over deep muffled chest-beat Matam thuds and warm low male choral hum (Ahaat). 100% acapella human vocal and chest-percussion only. Sing all 3 lines completely at a solemn measured pace.",
    "lyrics": "[النَّزْلَة الثَّانِيَة]\nيِگِلْهَا عَظَّمْ اللّٰه أَجْرِچْ .. عَبْدُاللّٰه وُگَعْ بِالْبَرْ ..\nوُمِنْ بَعْدَه تَرَى عُثْمَانْ .. ظَلْ إِعْلَه الثَّرَى مُوذَرْ ..\nيَالْحُرَّه وُتَرَى الثَّالِثْ .. أَخَبْرِچْ وُگَعْ جَعْفَرْ .."
  }
}
```

#### 2. كائن التمديد `Stage 2B` (`الكَسْرَة الثَّانِيَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_2B_Extend_Kasra_2",
    "operation_mode": "EXTEND_FROM_STAGE_2A_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in weeping Maqam Saba. Emotional Iraqi Radood vocal crying out the mother's grief over deep chest-beat Matam thuds and solemn male choir Ahaat. 100% acapella human voice and chest percussion only. Sing all 3 vertical lines completely including the final line about Hussein.",
    "lyrics": "[الكَسْرَة الثَّانِيَة]\nصَاحَتْ وَالدَّمِعْ بَادِي .. بِشِرْ گَطَّعِتْ إِفَّادِي ..\nمَا أَنْشِدَكْ عَلَى أَوْلَادِي ..\nعَلَى إِحْسَيْنْ النَّشِدْ كِلَّه .. اشْتَاگَيْتْ أَنْظُرْ لْخَدَّه .."
  }
}
```

#### 3. كائن التمديد `Stage 3A` (`النَّزْلَة الثَّالِثَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_3A_Extend_Nazla_3",
    "operation_mode": "EXTEND_FROM_STAGE_2B_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in solemn Maqam Hijaz and Saba. Deep sorrowful solo Iraqi Radood mourning Al-Abbas over steady muffled chest-beat Matam thuds and low male choir Ahaat. 100% acapella human voice and chest percussion only. Sing all 3 lines completely.",
    "lyrics": "[النَّزْلَة الثَّالِثَة]\nيِگِلْهَا الرَّابِعْ الْعَبَّاسْ .. يَمْ الْمَشْرَعَه مَچْتُوفْ ..\nعَلَى عَيْنَه سَهَمْ نَابِتْ .. وُظَلْ إِعْلَه النَّهَرْ مَلْهُوفْ ..\nوُظَلَّتْ مِنْ وَرَاهْ زَيْنَبْ .. يَمْ عَبَّاسْ مَكْسُورَه .."
  }
}
```

#### 4. كائن التمديد `Stage 3B` (`الكَسْرَة الثَّالِثَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_3B_Extend_Kasra_3",
    "operation_mode": "EXTEND_FROM_STAGE_3A_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in weeping Maqam Saba. Heartbroken Iraqi Radood vocal asking solely about Imam Hussein over deep chest-beat Matam thuds and male choir Ahaat. 100% acapella human voice and chest percussion only. Sing all 3 vertical lines completely.",
    "lyrics": "[الكَسْرَة الثَّالِثَة]\nصَاحَتْ گِلِّي عَاللِّي صَارْ .. لَا تِحْچِيلِي عَالْأَقْمَارْ ..\nگَلْبِي مِنِ الصُّبُحْ مِحْتَارْ ..\nأَرِيدَنْ خَبَرْ عَنْ إِحْسَيْنْ .. دِگِلِّي الْوَلِي إِحْسَيْنْ إِشْلُونْ .."
  }
}
```

#### 5. كائن التمديد `Stage 4A` (`النَّزْلَة الرَّابِعَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_4A_Extend_Nazla_4",
    "operation_mode": "EXTEND_FROM_STAGE_3B_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in intense weeping Maqam Saba (peak grief of Ashura). Trembling tearful Iraqi Radood vocal over heavy resonant chest-beat Matam thuds and sobbing male choir Ahaat. 100% acapella human voice and chest percussion only. Sing all 3 lines completely.",
    "lyrics": "[النَّزْلَة الرَّابِعَة]\nصَاحْ وُدَمْعِتَه تِجْرِي .. أَخَبْرِچْ ذَبْحَوْا الْغَالِي ..\nعَلَى التِّرْبَانْ ظَلْ عَارِي .. وُجِسْمَه بِالدِّمَه مَالِي ..\nوُالْخَيْلْ إِعْلَه صَدْرَه تْدُوسْ .. مَا مِنَّه كِتِرْ سَالِي .."
  }
}
```

#### 6. كائن التمديد `Stage 4B` (`الكَسْرَة الرَّابِعَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_4B_Extend_Kasra_4",
    "operation_mode": "EXTEND_FROM_STAGE_4A_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in weeping Maqam Saba. Sorrowful Iraqi Radood vocal lamenting the burning of the tents over muffled chest-beat Matam thuds and male choir Ahaat. 100% acapella human voice and chest percussion only. Sing all 3 vertical lines completely.",
    "lyrics": "[الكَسْرَة الرَّابِعَة]\nوُعُگْبَه الْخِيَمْ حَرْگُوهَا .. وُزَيْنَبْ غَصُبْ سَلْبُوهَا ..\nوُلِلشَّامَاتْ وَدُّوهَا ..\nرَدَّوْا إِلِچْ حَرَمْ وُأَطْفَالْ .. وُالسَّجَّادْ ظَلْ وَحْدَه .."
  }
}
```

#### 7. كائن التمديد `Stage 5A` (`النَّزْلَة الخَامِسَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_5A_Extend_Nazla_5",
    "operation_mode": "EXTEND_FROM_STAGE_4B_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in intimate weeping Maqam Saba and Bayati. Broken-hearted solo Iraqi Radood vocal addressing the martyred Hussein over soft deep chest-beat Matam thuds and warm male choral hum. 100% acapella human voice and chest percussion only. Sing all 3 lines completely.",
    "lyrics": "[النَّزْلَة الخَامِسَة]\nصَاحَتْ يَبْنِي الْمَذْبُوحْ .. يَالْچِنِتْ الْهَوَى لِيَّه ..\nمِتَانِيتَكْ تِرِدْ كِلْ يُومْ .. چَا لَيْشْ گَطَعِتْ بِيَّه ..\nكِلْهُمْ فِدْوَه يِرْحُولَكْ .. مِنْ نُورَكْ گِطَعْ ضَيَّه .."
  }
}
```

#### 8. كائن التمديد `Stage 5B` (`الكَسْرَة الخَامِسَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_5B_Extend_Kasra_5",
    "operation_mode": "EXTEND_FROM_STAGE_5A_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in weeping Maqam Saba. Grief-stricken Iraqi Radood vocal over deep chest-beat Matam thuds and male choir Ahaat. 100% acapella human voice and chest percussion only. Sing all 3 vertical lines completely.",
    "lyrics": "[الكَسْرَة الخَامِسَة]\nكِلْهُمْ مُوتَى مَعْقُولَه .. وِيَّاهُمْ رَيْتْ مَقْتُولَه ..\nوُبِالتَّابُوتْ مَشْيُولَه ..\nگَبُلْ هَاللَّحْظَه لَوْ مَيْتَه .. وُلَا أَعِيشَنْ بَعَدْ مُدَّه .."
  }
}
```

#### 9. كائن التمديد `Stage 6A` (`النَّزْلَة السَّادِسَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_6A_Extend_Nazla_6",
    "operation_mode": "EXTEND_FROM_STAGE_5B_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in solemn Maqam Bayati and Saba. Noble grieving Iraqi Radood vocal consoling Lady Zainab over steady chest-beat Matam thuds and deep male choir Ahaat. 100% acapella human voice and chest percussion only. Sing all 3 lines completely.",
    "lyrics": "[النَّزْلَة السَّادِسَة]\nرَاحَتْ تِصْرَخْ لْزَيْنَبْ .. يَا يُمَّا الْبِگَا بْرَاسِچْ ..\nآنِي سْمَعِتْ وُانْذِهْلَيْتْ .. چَانْ إِشْلُونْ إِحْسَاسِچْ ..\nوُشِفْتِيهُمْ بْشُوفْ الْعَيْنْ .. كِلْهَا مْذَبِّحَه نَاسِچْ .."
  }
}
```

#### 10. كائن التمديد `Stage 6B` (`الكَسْرَة السَّادِسَة` — `3 أسطر عمودية`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_6B_Extend_Kasra_6",
    "operation_mode": "EXTEND_FROM_STAGE_6A_END",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_3_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam lament in weeping Maqam Saba. Emotional Iraqi Radood vocal praising the patience of Lady Zainab over deep chest-beat Matam thuds and solemn male choir Ahaat. 100% acapella human voice and chest percussion only. Sing all 3 vertical lines completely.",
    "lyrics": "[الكَسْرَة السَّادِسَة]\nإِشْلُونْ إِنْتِي تْحَمَّلْتِي .. حْيُودْ إِعْلَه الْأَرُضْ شِفْتِي ..\nشْكُبُرْ صَبْرِچْ وُمَا مِتِّي ..\nصَبْرِچْ مَا تْحِدَّه حْدُودْ .. رَغُمْ هَمِّچْ عَبَرْ حَدَّه .."
  }
}
```

#### 11. كائن التمديد `Stage 6C` (`الخَاتِمَة والمُسْتَهَلّ الأَخِير` — `2 سطرين عموديين`)
```json
{
  "stage_directive": {
    "stage_id": "Stage_6C_Extend_Grand_Finale_Mustahall",
    "operation_mode": "EXTEND_FROM_STAGE_6B_END_FINAL_OUTRO",
    "lyrics_panel_action": "OVERWRITE_WITH_ONLY_THESE_2_LINES_NO_PREVIOUS_LYRICS",
    "sound_prompt": "Slow 60 BPM Iraqi Husseini Matam grand finale in Maqam Bayati and Saba. Solo Iraqi Radood and full unison Husseini male choir chanting the final refrain together over fading muffled chest-beat Matam thuds and deep vocal Ahaat, ending in a solemn spiritual fade-out. 100% acapella human voice and chest percussion only.",
    "lyrics": "[المُسْتَهَلّ]\nصُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ ..\n(صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ)"
  }
}
```

---

## رابعاً: المعالجة الصوتية اللاحقة والمكساج الاحترافي بأمر الماسترينغ المحلي ذي المسارات الخمسة (`Step 4: Post-Processing & 5-Track Local DSP Mastering`)

بعد اكتمال التمديد النهائي (`Stage 6C`)، تمرّ القصيدة بمرحلتين تكامليتين للمعالجة الصوتية والماسترينغ الاحترافي:

### أ) الخطوة الرابعة داخل الاستوديو (`Step 4: In-Studio Post-Processing via Producer Chat`)
أرسل كائن المعالجة اللاحقة التالي في **`Producer Chat`** لتطبيق سلسلة الفلاتر الهندسية (`audio__apply_effect`) على المقطع النهائي المكتمل قبل تحميله (أو استخدم خيار `Remix > Split stems` لتحميل مسار `Vocals` الصافي للماسترينغ المحلي):

```json
{
  "stage_directive": {
    "stage_id": "Step_4_Post_Generation_Master_DSP",
    "operation_mode": "APPLY_MASTER_AUDIO_EFFECT_CHAIN",
    "tool": "audio__apply_effect",
    "execution_command": "Apply audio__apply_effect on the final extended clip: HighPass filter at 85Hz, AdvancedEqualizer (cut 450Hz by -2.5dB to remove low-mid boxiness, boost mid 1200Hz by +1.5dB for warm Jawhari Baritone chest body, boost high-mid presence 2500Hz by +4.5dB for crisp Arabic consonant clarity), Compressor (ratio 3:1, threshold -12.0dB), Reverb (room_size 0.55, wet_mix 0.18, Husseiniya hall RT60 3.2s), and True-Peak Limiter at -1.0dB."
  }
}
```

---

### ب) المكساج الاحترافي بأمر الماسترينغ المحلي ذي المسارات الخمسة (`5-Track SOS/RMS/LUFS Local DAW Engine`)

يعمل المحرك الصوتي المحلي [hussaini_dsp_montage.py](file:///C:/Users/husai/.gemini/config/skills/hussaini-production-studio/scripts/hussaini_dsp_montage.py) كبنك مكساج وماسترينغ رقمي من **5 مسارات صوتية مستقلة (`5-Track Husseiniya DAW`)** تُدمج وتُعاير قياسياً إلى **`-14.0 LUFS`** وسقف قمة حقيقية **`-1.0 dBTP True Peak`**:

| رقم المسار | اسم المسار الهندسي (`Track Role`) | المعالجة الفيزيائية والطيفيّة المطبّقة (`SOS / RMS / Formant DSP`) |
| :--- | :--- | :--- |
| **المسار 1 (`Track 01`)** | **مسار الرادود والردّادة (`Lead Baritone & Unison Choir Chain`)** | تنقية الضجيج الخلفي (`Noise-Print Gate`) + معادل الباريتون الجوهري (`4th-order SOS HPF @ 85Hz` + مصيدة الصندوقية `320Hz Notch` + تنعيم الحدة `2500Hz Notch` + تعزيز الحضور `1.6–3.8kHz`) + صدى ديناكورد الشريطي المتزامن مع السرعة (`250ms Dynacord Tape Echo @ 60 BPM`) + صدى القبة الحسينية (`3.4s FFT Convolution Reverb`). |
| **المسار 2 (`Track 02`)** | **لطم الصدر الثقيل وهمهمة القرار (`54–55Hz Sub-Chest Thud & 44Hz Sub-Hum`)** | بناء ضربة الصدر البشرية العميقة (`54–55Hz Bare-Palm Chest Thud`) مدعومة بنبضة قرار بشرية (`44Hz Sub-Bass Hum`) بنظام التناوب العضوي (`4x Round-Robin`) ومزامنة تلقائية مع أول نبرة لصوت الرادود (`Vocal Onset Lock`). |
| **المسار 3 (`Track 03`)** | **صفعة الكف ونَفَس المعزّين (`Palm Snap 1.5–3.2kHz & Congregation Breath`)** | طبقة صفعة الكف الحية (`1.5–3.2kHz Bandpass Snap`) مع نَفَس جمهور المعزّين (`240–1400Hz Shaped Air Envelope`) على أنصاف الضربات لإعطاء روح المجلس الحسيني الحي. |
| **المسار 4 (`Track 04`)** | **الآهات البلعومية الفورمانتية (`24-EDO Rosenberg Glottal + Formant Ahaat Pad`)** | توليد بشري فيزيائي نقي (`Rosenberg Glottal Pulse Tp=0.45, Tn=0.16`) عبر رنانات الفورمانت العربية (`F1=730Hz, F2=1090Hz, F3=2440Hz`) على ترددات **مقام الصبا الميكروتونالية (`24-EDO Saba: 146.83Hz / 174.61Hz`)** بتباين كورالي (`[-4, 0, +4] cents`) وتوسيع ستيريو (`9ms Haas Shift`) وخفض جانبي ذكي (`-3.0 dB Sidechain Ducking @ -28 dBFS`) ينخفض تلقائياً لحظة نطق الرادود. |
| **المسار 5 (`Track 05`)** | **المؤثرات البيئية، الانقطاع الدرامي، وباص الماستر (`Foley, 3s Audio Drop & -14 LUFS Master Bus`)** | مؤثرات كربلاء البيئية الاختيارية (`--foley wind|water|horses`) + كتم درامي للخلفية لمدة `3.0s` في ذروة الكسرة (`--audio-drop-sec`) + تشبع شريطي دافئ (`Hyperbolic Tangent Tape Saturation`) + ضاغط تماسك (`1.6:1 Master Bus Glue Compressor`) + معايرة نهائية إلى **`-14.0 LUFS`** و**`-1.0 dBTP`** (`4x Oversampled Brickwall Limiter`). |

#### 1. أوامر التشغيل المباشرة في `PowerShell` (قصيدة «صُوتْ أُمِّ البَنِينْ يِصِيحْ» — `60 BPM / Maqam Saba`)

- **الخيار الأول (الماسترينغ الثقيل الموزّع مع الحفاظ على لطم التوليد الأصلي — `Recommended when Stage 1–6C has clean chest thuds`):**
```powershell
# 1) تحويل ملف الـ MP3 الممتد الناتج من Flow Music إلى WAV قياسي (48kHz / 24-bit):
ffmpeg -y -i "C:\Users\husai\Desktop\لطميات تجربة\Compose  Lyrics\صوت أم البنين (Extended).mp3" -ar 48000 -ac 2 "C:\Users\husai\Desktop\لطميات تجربة\sawt_umm_al_banin_raw.wav"

# 2) تشغيل محرك الماسترينغ المحلي ذي المسارات الخمسة (طور الثقيل الكربلائي الموزّع 60 BPM على مقام الصبا):
python "C:\Users\husai\.gemini\config\skills\hussaini-production-studio\scripts\hussaini_dsp_montage.py" `
  --input "C:\Users\husai\Desktop\لطميات تجربة\sawt_umm_al_banin_raw.wav" `
  --output "C:\Users\husai\Desktop\لطميات تجربة\صوت أم البنين — ماستر 5 مسارات (-14 LUFS).wav" `
  --mode "thaqeel_muwazza" `
  --bpm 60 `
  --maqam-drone "saba"
```

- **الخيار الثاني (استبدال إيقاع الذكاء الاصطناعي بالكامل وبناء اللطم البشري الخماسي من الصفر — `--replace-ai-percussion` + `--mode heavy_clip`):**
```powershell
python "C:\Users\husai\.gemini\config\skills\hussaini-production-studio\scripts\hussaini_dsp_montage.py" `
  --input "C:\Users\husai\Desktop\لطميات تجربة\sawt_umm_al_banin_raw.wav" `
  --output "C:\Users\husai\Desktop\لطميات تجربة\صوت أم البنين — كليب استوديو ثقيل 5 مسارات (-14 LUFS).wav" `
  --mode "heavy_clip" `
  --bpm 60 `
  --maqam-drone "saba" `
  --replace-ai-percussion
```

- **الخيار الثالث (إضافة انقطاع درامي `3.0s Audio Drop` في ذروة الكسرة الرابعة `ذَبْحَوْا الْغَالِي` + أجواء رياح الطف الخفيفة `--foley wind`):**
```powershell
python "C:\Users\husai\.gemini\config\skills\hussaini-production-studio\scripts\hussaini_dsp_montage.py" `
  --input "C:\Users\husai\Desktop\لطميات تجربة\sawt_umm_al_banin_raw.wav" `
  --output "C:\Users\husai\Desktop\لطميات تجربة\صوت أم البنين — ماستر درامي كامل (-14 LUFS).wav" `
  --mode "thaqeel_muwazza" `
  --bpm 60 `
  --maqam-drone "saba" `
  --foley "wind" `
  --audio-drop-sec 215.0
```

