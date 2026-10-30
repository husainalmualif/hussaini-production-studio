# موسوعة مدارس الرواديد والخطباء في الإنتاج الحسيني (Radoods & Khutaba Encyclopedia — V38.0 OMNI-ARCHITECT)

هذا المرجع يوثق الخصائص الفنية، المقامية، اللحنية، والهندسة الصوتية لـ 15+ رادوداً (ضمن 10 مدارس تفصيلية) و8 من كبار خطباء المنبر الحسيني في النعي.
**قاعدة أخلاقية وتشغيلية إلزامية (Module 24 & Rule R5):** عند توليد البرومتات لمنصات الذكاء الاصطناعي، يُمنع استخدام استنساخ البصمة الصوتية الشخصية لرادود حيّ، وبدلاً من ذلك تُترجم مدرسته الفنية إلى **الواصفات الصوتية الإنجليزية النقية والمختصرة (40–45 كلمة)** الموثقة أدناه.
**قاعدة البرومبت القياسي لحقل `Sound` (Module 36):**
1. لا تتجاوز 40 إلى 50 كلمة من الواصفات الإنجليزية الصرفة والواضحة.
2. اذكر اللهجة صراحةً في أول سطر (`authentic Iraqi and Bahrani colloquial dialect` أو `authentic Iraqi colloquial dialect`).
3. ثبّت مقاماً أساسياً واحداً فقط في التوليد التأسيسي (`Maqam Saba` أو `Maqam Bayati` أو `Maqam Hijaz`) لضمان توازن اللحن واستقراره (`Rule B1`).
4. يُمنع وضع الكلمات المعرّبة (`maddat sawtiya`, `taqatee'`, `bahha`, `tarjee'`) أو أرقام المعادل الصوتي (`+4.5dB at 2.5kHz`, `HPF at 85Hz`) أو كلمة `tenor` داخل حقل `Sound`؛ لأن مكان الفلاتر هو أداة `audio__apply_effect` بعد التوليد.

---

## أولاً: التحليل المفصل لمدارس الرواديد الحسينيين (الأسلوب، اللحن والمقامات، البرومبت القياسي ذو الـ 40 كلمة)

### 1. الحاج باسم الكربلائي (عميد المدرسة التجديدية الشاملة)
- **الأسلوب:** يجمع بين الأصالة العراقية والتجديد؛ يمتاز بمرونة حنجرته وقدرته الإبداعية على التنقل بين القصائد المنبرية الكلاسيكية والموشحات الوجدانية والشور.
- **اللحن واستخدام المقامات:** يبدع في مقامات **البيات، السيكا، الكرد، النهاوند، الحجاز، الرست، والصبا** (مع تثبيت مقام أم واحد في المرحلة الأولى والتنقل في المرحلة الثانية `Extend`)، ويمتاز بقفزات قوية في الجواب وجواب الجواب (`powerful high chest-voice climbs`).
- **النماذج المرجعية الأسطورية (إصدار «وجود لوجودي» 1428 هـ، وإصدار «قل ما تشاء» 1432 هـ، وروائع 1447–1448 هـ):**
  1. `أين أنت يا جابر` (`play-fq2ux` — كاظم منظور الكربلائي): المسبّع الكربلائي المركّب (يُنفذ في `Stage 1` بوزن موحد، ثم يُضاف الگريز الداخلي في `Stage 2`).
  2. `أم البنين` (`play-zsnpe` — الملا عطية الجمري): الدمج بين المربوع البحراني الفايزي المنبري واللطم الثقيل (`58 BPM`).
  3. `وجود لوجودي` (`play-da3b9` — جابر الكاظمي): الموشح ذو اللازمة الفلسفية الموحدة (`وهو الماضي والآتي`).
  4. `حلم مذبوح` (`play-bNqR0` — السيد عبد الخالق المحنة): السرد المسرحي المتصاعد على رويّ `-يتي`.
  5. `أقول اسمك` (`play-ZJpsw` — واثق العيساوي): المخمّس الوجداني + بيت القفل (`ملاذ وتنتهي يمك جراحاتي`).
  6. `علامات الحزن` (`play-3vuOX` — السيد عبد الخالق المحنة): التصعيد الطفولي وتضعيف الكلمة الأخيرة (`يا يوم يا يوم`).
  7. `ألم وعتاب` (`play-MOcJn` — السيد عبد الخالق المحنة): ازدواج القافية الداخلية واللازمة السؤالية (`على الچفين اسألك وين دليني`).
  8. `يا حبيبي يا حسين` (`play-Am3rB` — مهدي جناح الكاظمي — `3:32`): التوشيح الفصيح القصير المكثّف.
  9. `يا أكبر جبل` (`play-uG52R` — السيد عبد الخالق المحنة): ثلاثيات وداع الشباب المترابطة القافية (`-رك`).
  10. `لسان الوحي` (`play-JmMVU` — مهدي جناح الكاظمي): الملحمة الفصيحة على بحر الوافر التام.
  11. الروائع الحديثة: `إن شاء الله` (`GDsdpmzeLqw`)، `أوتار التكبير` (`rMVIUkUZ4bU`)، `شاب وطفل` (`RhQdSDt1-mg`)، `بعيونك حزن ينشاف` (`bnuiKoJigFA`).
- **البرومبت القياسي المعتمد (40 كلمة — مقفل اللهجة والمقام الواحد):**
  `Traditional Iraqi and Bahrani Hussaini Latmiya, Thaqeel Faizi and Nazla style, Maqam Saba, 58 BPM, authentic Iraqi and Bahrani colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, emotional weep cracks, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments`

### 2. الشيخ حسين الأكرف (مدرسة الوعي واللحن الأكاديمي والتوشيح البحراني)
- **الأسلوب:** أسلوب رسالي وتوعوي يركز على النص الفكري والروحي بالأداء الهادئ والعميق.
- **النموذج المرجعي الأسطوري:** `صلاة الليل` (`Kqrzvm845yQ` — عبد الله القرمزي): التوشيح البحراني الأكاديمي ذو الوقفات التنفسية الوسطية (`..`).
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Bahrani Hussaini Tawshih Latmiya, academic contemplative style, Maqam Nahawand, 64 BPM, authentic Bahrani colloquial dialect, warm resonant Baritone lead vocal, smooth microtonal vowel elongations, gentle emotional chest-voice climbs, calm 55Hz bare-palm chest pulse, 250ms analog delay, 2.8s clean studio reverb, harmonized unison male Raddada choir response, Pure Acapella No Instruments`

### 3. الملا محمد باقر الخاقاني (أيقونة مدرسة الشور العاطفية والشجن المركب)
- **الأسلوب:** يعتمد على أسلوب "الشور" المعاصر والتفاعل العاطفي الباكي والمدات الشجية.
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Iraqi Karbalaei Shoor Latmiya, Maqam Saba, 130 BPM, authentic Iraqi colloquial dialect, impassioned raspy Baritone lead vocal, powerful high chest-voice cries, emotional weep cracks, rapid driving 55Hz bare-palm chest slaps, continuous deep male congregation rhythmic Hussain chant drone, 1.8s Husseiniya hall reverb, Pure Acapella No Instruments`

### 4. الحاج عمار الكناني (صاحب الحنجرة الرخيمة واللطم العراقي الرصين)
- **الأسلوب:** أسلوب عراقي منبري أصيل يركز على "اللطمية الثقيلة" الكلاسيكية وثبات الطبقة الصوتية في مقام البيات والصبا.
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Iraqi Hussaini Latmiya, classic heavy Thaqeel style, Maqam Bayati, 60 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone lead vocal, pitch-stable chest authority, natural vocal rasp, emotional weep cracks, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada response, Pure Acapella No Instruments`

### 5. الرادود سيد سلام الحسيني (مدرسة الشجن العراقي والروحية العالية)
- **الأسلوب:** يمزج بين العزاء العراقي التقليدي (المستهل والجواب) والروحية العالية وتقسيم القصيدة عبر المراحل.
- **النماذج المرجعية الأسطورية:** `الذكريات` (`KS0DidCff70`)، `مو انه يا حزن` (`i9CunjgHGPA`)، `سلام وعن بعد` (`HsKdW96ckM0`)، `بندرية عرس بارض الطفوف` (`VWzjqewppG8`).
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Iraqi Hussaini Majlis Latmiya, spirited Keadia and Thaqeel style, Maqam Bayati, 68 BPM, authentic Iraqi colloquial dialect, high-power full-chest belted Baritone lead vocal, intense gritty upper-register climbs, emotional weep cracks, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s live Husseiniya hall reverb, massive unison male Raddada response, Pure Acapella No Instruments`

### 6. أمير المحياوي ونوح المحمداوي وأمجد الشغانبي وعباس عجيد العامري (مدرسة السلو الحزين والشوق الرضوي-الحسيني)
- **النموذج المرجعي الأسطوري (عباس عجيد العامري):** `مشهد حلم` (`NUZMRXW5xgU` — هادي شبيب الخيكاني).
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Southern Iraqi slow Hussaini elegy, Maqam Kurd, 58 BPM, authentic Iraqi colloquial dialect, grieving warm Baritone lead vocal, prolonged mournful vowel elongations, emotional high chest-voice cries, natural weep cracks, slow 55Hz bare-palm chest pulse, 285ms analog tape echo, 3.2s spacious hall reverb, unison male Raddada response, Pure Acapella No Instruments`

### 7. الرادود مدين العياشي (مدرسة الإرث الفراتي الجنوبي والأداء الدافئ)
- **النموذج المرجعي الأسطوري:** `يمه اكعديلي` (`8iqVTvsqWb0` — علي هادي الخزعلي).
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Southern Iraqi Euphrates Hussaini Latmiya, Bahr Al-Nassari style, Maqam Lami, 56 BPM, authentic Southern Iraqi colloquial dialect, raw grieving Baritone lead vocal, exhausted tear-choked chest timbre, natural weep cracks, slow heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, unison male Raddada response, Pure Acapella No Instruments`

### 8. الملا محمد بوجبارة (المدرسة الإحسائية الخليجية المتطورة)
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Ahsa Gulf Hussaini Latmiya, Maqam Sikah, 64 BPM, authentic Gulf and Iraqi colloquial dialect, articulate resonant Baritone lead vocal, smooth microtonal transitions, powerful high chest-voice climbs, steady 55Hz bare-palm chest thud, 260ms analog delay, 3.0s spatial hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments`

### 9. الرادود صالح الدرازي (عملاق المدرسة البحرانية الملحمية الأصيلة)
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Bahrani Mawkib Hussaini Latmiya, heavy Haidari and Faizi style, Maqam Hijaz, 62 BPM, authentic Bahrani colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, heavy synchronous 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Matam hall reverb, massive unison male Raddada response, Pure Acapella No Instruments`

### 10. السيد هاني الوداعي والسيد عصام الهاشمي وحسين خير الدين (المدرسة البحرانية التراثية ومدرسة النشيد اللطمي المقاوم)
- **النماذج المرجعية الأسطورية:** `نوح الراعبية` (`c-7qBrZjIkc` — السيد عصام الهاشمي)، `في درب فاطمة` (`x6SAJcKf4gE` — حسين خير الدين).
- **البرومبت القياسي المعتمد (40 كلمة):**
  `Traditional Bahrani heritage Hussaini Latmiya, Faizi and Nazla style, Maqam Saba, 60 BPM, authentic Bahrani colloquial dialect, wide majestic Baritone lead vocal, trembling microtonal vowel elongations, emotional weep cracks, heavy 55Hz bare-palm chest thud, 280ms analog tape delay, 3.0s Matam hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments`

---

## ثانياً: مدارس كبار الخطباء في النعي الحسيني (The 8 Minbar Na'i Masters — 0 BPM Rubato Standard)

1. **الشيخ عبد الوهاب الكاشي (الطور الكاشي والجهارة المنبرية):**
   `Traditional Minbar Na'i vocal lament, strict Rubato free tempo with zero rhythmic grid, Maqam Hijaz, authentic Bahrani and Iraqi colloquial dialect, commanding wide-range resonant Baritone solo voice, prolonged soaring vowel cries, descending mournful cadences, 450ms analog echo, 3.8s cathedral reverb, Pure Solo Acapella No Percussion`
2. **الشيخ الدكتور أحمد الوائلي (الوقار الأكاديمي والنعي الفصيح والدارمي):**
   `Traditional Minbar Na'i vocal lament, strict Rubato free tempo with zero rhythmic grid, Maqam Bayati, dignified classical Arabic and Iraqi colloquial articulation, calm paternal Baritone solo voice, gentle tearful tremolo, 420ms analog delay, 3.5s hall reverb, Pure Solo Acapella No Percussion`
3. **السيد جاسم الطويرجاوي (الفجيعة الفراتية والدمعة الفورية):**
   `Traditional Southern Iraqi Euphrates Minbar Na'i lament, strict Rubato free tempo with zero rhythmic grid, Maqam Saba, authentic Iraqi colloquial dialect, deep velvet mournful Baritone solo voice, raw weeping cracks, breathless grieving sighs, 450ms analog tape echo, 3.8s Husseiniya cathedral reverb, Pure Solo Acapella No Percussion`
4. **الشيخ عبد الحي قمبر (الشجن البحراني والفايزي الأصيل):**
   `Traditional Bahrani Faizi Minbar Na'i vocal lament, strict Rubato free tempo with zero rhythmic grid, Maqam Saba, authentic Bahrani colloquial dialect, resonant mournful Baritone solo voice, trembling microtonal vowel elongations, deep descending weeping groan, 450ms analog echo, 3.8s Matam hall reverb, Pure Solo Acapella No Percussion`
5. **الشيخ زمان الحسناوي (النعي العراقي المعاصر والانتقال النغمي السلس):**
   `Traditional Iraqi Minbar Na'i and Abudhiyah vocal lament, strict Rubato free tempo with zero rhythmic grid, Maqam Lami, authentic Iraqi colloquial dialect, rich resonant Baritone solo voice, smooth microtonal slides, tearful broken cadences, 450ms analog tape echo, 3.8s cathedral reverb, Pure Solo Acapella No Percussion`
6. **السيد نصرات قشاقش (رثاء جبل عامل والتصعيد الدرامي الفاجع):**
   `Traditional Minbar Na'i dramatic vocal lament, strict Rubato free tempo with zero rhythmic grid, Maqam Saba, authentic colloquial mourning dialect, powerful emotive Baritone solo voice, audible weeping inhales, soaring high chest-voice cries, 450ms analog echo, 3.8s hall reverb, Pure Solo Acapella No Percussion`
7. **الشيخ حيدر المولى (النعي الإنشادي الشجي والحزن الرخيم):**
   `Traditional Iraqi Minbar Na'i vocal lament, strict Rubato free tempo with zero rhythmic grid, Maqam Bayati, authentic Iraqi colloquial dialect, lyrical velvet Baritone solo voice, smooth mournful vowel elongations, emotional weep cracks, 420ms analog delay, 3.6s hall reverb, Pure Solo Acapella No Percussion`
8. **الشيخ زمان العقابي (الشجن الجنوبي الريفي والأبوذية المفجوعة):**
   `Traditional Southern Iraqi rural Minbar Na'i and Abudhiyah lament, strict Rubato free tempo with zero rhythmic grid, Maqam Lami, authentic Southern Iraqi colloquial dialect, husky raspy Baritone solo voice, raw emotional weep cracks, 450ms analog tape echo, 3.8s Husseiniya reverb, Pure Solo Acapella No Percussion`

---

## ثالثاً: مصفوفة الطبقات والخامات الصوتية الجوهرية السبعة (بواصفات إنجليزية نقية ومختصرة بدون `tenor`)

- **القاعدة الحاسمة لمنع نعومة الصوت وضياع اللهجة:** يُمنع استخدام كلمة **`tenor`** (أو `baritone-tenor`) أو المصطلحات المعرّبة (`bahha`, `tarjee'`, `maddat`) أو أرقام الـ `EQ` داخل حقل `Sound`. استخدم أحد الواصفات الإنجليزية الصرفة التالية داخل البرومبت القياسي ذي الـ 40 كلمة:
  1. **الباريتون الجوهري الفخم ذو الجوابات الصاعدة (دمج باسم الكربلائي + عمار الكناني + صالح الدرازي):**
     `commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, emotional weep cracks`
  2. **الباريتون المنبري الرخيم ذو البحة الشجية (الطويرجاوي، حمزة الزغير، العلوي، مرتضى حرب):**
     `deep velvet mournful Baritone lead vocal, heavy chest resonance, raw vocal rasp, tearful weeping cracks, descending mournful cadences`
  3. **الباص-باريتون الملحمي الحماسي المجلجل (قحطان البديري، حيدر البياتي، مهدي رسولي):**
     `thunderous heroic Bass-Baritone lead vocal, massive deep chest authority, commanding epic projection, powerful high chest-voice leaps`
  4. **الحنجرة البحرانية التوشيحية العريضة (الشيخ حسين الأكرف، السيد عصام الهاشمي، الدرازي):**
     `wide majestic Bahrani Baritone lead vocal, warm velvety chest resonance, trembling microtonal vowel elongations, soaring high chest-voice climaxes`
  5. **الحنجرة الفراتية الشجية المخنوقة بالعَبرة (مدين العياشي، عباس عجيد العامري، داخل حسن):**
     `raw grieving southern Iraqi Baritone lead vocal, exhausted tear-choked chest timbre, natural weep cracks, prolonged high mournful vowel cries`
  6. **الصوت الصدري الجبلي الصاعد (سيد سلام الحسيني، مسلم الوائلي، جليل الكربلائي):**
     `high-power full-chest belted Baritone lead vocal, intense gritty upper-register projection, emotional weep cracks, commanding congregation delivery`
  7. **الكورال الحسيني المهيب (`Unison Raddada Choir`):**
     `wide unison male Raddada choir response, deep masculine congregation chanting`
