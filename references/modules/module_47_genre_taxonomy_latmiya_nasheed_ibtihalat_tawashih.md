# التصنيف الهندسي والفني الصارم بين اللطمية الحسينية، النشيد الإسلامي، الابتهالات الدينية، والتواشيح (`Module 47 & 50`) — V48.5 OMNI-ARCHITECT

تضع هذه الوحدة الحدود الفيزيائية، الإيقاعية، المقامية، والحنجرية الفاصلة بين **الأنواع الصوتية الدينية الأربعة** (`--genre {latmiya,nasheed,ibtihalat,tawashih}`)، وتمنع تسرب أسلوب «الأغنية» أو «النشيد» أو فوضى البكاء الخلفي إلى **اللطمية الحسينية الخالصة**.

---

## أولاً: جدول الفروق الجوهرية بين الفنون الصوتية الدينية الأربعة

| المعيار الفني | 1. اللطمية الحسينية (`latmiya`) | 2. النشيد الإسلامي (`nasheed`) | 3. الابتهالات والمناجاة (`ibtihalat`) | 4. التواشيح والموشحات (`tawashih`) |
| :--- | :--- | :--- | :--- | :--- |
| **الوظيفة الوجدانية** | الرثاء المفجع، العزاء المنبري والموكبي على سيد الشهداء (ع). | الفرح الولائي (المواليد)، الحماسة الإسلامية، التوجيه الروحي. | التضرع الخاشع في جوف الليل، الدعاء النغمي، مناجاة السحر. | المدح النبوي والولائي الموزون بالأدوار والخانات والموشحات. |
| **البنية الإيقاعية** | **لطم صدري بشري خالص (`55Hz Bare-Palm Chest Thud`)** بسرعة `54–132 BPM` (`58–60 BPM` للثقيل؛ `0 BPM` للنعي المنبري). | إيقاع الدف الإنشادي (`Traditional Daf Frame Drum`) بسرعة `78–110 BPM` بدون لطم صدري. | **مرسل حر بلا إيقاع إطلاقاً (`0 BPM Free-Tempo Rubato`)**. | إيقاع موشح كلاسيكي موزون (`68–84 BPM`) بدون لطم صدري. |
| **الأداء الحنجري** | باريتون جوهري رخيم (`Commanding Deep Resonant Baritone`) ببحة طبيعية وعُرَب ربع تون (`24-EDO`) بدون ضوضاء بكاء في الإيقاع. | منشد بصوت دافئ نقي مصقول (`Warm Melodic Munshid Baritone`). | مبتهل منفرد خاشع متضرع (`Reverent Supplicating Solo Mubtahil`) بمدّات نفسية طويلة. | منشد يؤدي «الدور/الخانة» بزخارف مقامية متقنة في حوار مع البطانة. |
| **دور الكورال والجمهور** | **ردّة جمهور الحسينية الموحدة (`Wide Unison Male Raddada Choir`)**؛ صفر هارموني غربي. | كورال إنشادي هارموني متعدد الطبقات (`Harmonic Male Nasheed Choir`). | أداء فردي خالص (`Pure Solo Vocal`) في فضاء مسجدي واسع. | بطانة الموشح (`Unison/Antiphonal Tawashih Bitanah`) تردد المذهب. |
| **المقامات الأساسية** | الصبا، الصبا زمزم، اللامي، البيات، الحجاز، الكرد. | البيات، الراست، النهاوند، العجم، الكرد. | الصبا، الراست، السيكاه، البيات، الحجاز. | الحجاز، البيات، الراست، النهاوند، الصبا. |

---

## ثانياً: القائمة السوداء الكاملة المحظورة في `Sound` للطميّة (`36-Term Blacklist — Module 50`)

يُحظر إدراج أي مصطلح من القائمة التالية في وصف `Sound` للطميّة الحسينية:
- **الآلات والتوزيع الغنائي:** `piano`, `guitar`, `strings`, `oud`, `violin`, `synth`, `808`, `trap`, `studio-arranged`, `studio-mixed`, `arranged studio`, `humming`, `pads`, `sub-bass`, `groove`, `bandari`, `harmonic`, `dammam` *(في غير الزنجيل)*, `syncopated`, `--no piano`.
- **الطبقات الخاطئة والصراخ وفوضى البكاء في الإيقاع:** `tenor`, `reciter`, `spoken`, `wailing`, `screaming`, `tear-choked`, `emotional weep cracks`, `weeping`, `sobbing`, `majlis cries`.
- **مُسطِّحات المقام الغربي والتعريب اللاتيني:** `legato phrasing`, `wordless pharyngeal Ahaat vocal drone`, `calm`, `serene`, `bahha`, `tarjee'`, `maddat sawtiya`, `taqatee'`.

---

## ثالثاً: القوالب القياسية المعتمدة للأنواع الأربعة (`build_vocal_genre_profile — V48.5`)

1. **`--genre latmiya` (`60 BPM` — نقي 100% بدون انحراف غنائي أو فوضى بكاء):**
   `Traditional Iraqi Hussaini Latmiya, heavy Karbalai Nazla style, Maqam Bayati and Saba, 60 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, passionate microtonal melisma, heavy 55Hz bare-palm chest thud, 285ms tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada response, Pure Acapella No Instruments`
2. **`--genre nasheed` (`88 BPM`):**
   `Uplifting Islamic Nasheed vocal arrangement, 88 BPM, warm melodic Munshid baritone lead vocal, Maqam bayati_and_rast, polished multi-layered harmonic male Nasheed choir with gentle vocal humming pads, rhythmic traditional Daf frame drum pulse, clean studio acoustics, Islamic Vocal Nasheed`
3. **`--genre ibtihalat` (`0 BPM Rubato`):**
   `Free-tempo non-metric Islamic Religious Ibtihalat and spiritual Munajat supplication, rubato 0 BPM, reverent weeping supplicating solo Mubtahil Baritone vocal, long breath-sustained melismatic Maqam saba_and_rast improvisation, emotional spiritual Qafla cadences, spacious Mosque hall reverb, Pure Solo Vocal No Instruments`
4. **`--genre tawashih` (`72 BPM`):**
   `Traditional Islamic Religious Tawashih and Muwashahat vocal ensemble, 72 BPM measured classical Arabic poetic cadence, ornate Maqam hijaz_and_bayati microtonal melismas, antiphonal call-and-response between expressive solo Munshid and unison male Tawashih Bitanah choir, traditional spiritual hall acoustics, Pure Vocal Ensemble No Instruments`

---

## رابعاً: قاعدة فصل `هَلْ` بالمسافة وفتح هاء التأنيث بدون سكون (`غَرِيبَه هَلْ حِچَايَه`)

- تُفصل أداة الإشارة **`هَلْ`** بمسافة صريحة، وتُكتب هاء التأنيث **مفتوحة دائماً بدون سكون** لمنع نطق `-HHH`:
  - **`غَرِيبَه هَلْ حِچَايَه`** (عراقي) / **`غَرِيبَه هَلْ حِكَايَه`** (بحراني)
  - **`مِنْ هَلْ تَعَبْ`**، **`هَلْ مَسِيَّه`**، **`هَلْ گُفْرَه`**، **`يَا هَلِ الغُرَبْ`**.
