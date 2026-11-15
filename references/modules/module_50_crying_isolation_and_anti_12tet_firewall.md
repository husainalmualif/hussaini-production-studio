# عزل البكاء في النعي الحر (`0 BPM`) وجدار الحماية ضد انهيار المقام الغربي (`12-TET`) (`Module 50`) — V48.5 OMNI-ARCHITECT

توثق هذه الوحدة القانون التجريبي الحاسم لمنع فوضى أصوات البكاء الخلفية المتداخلة مع نطق الرادود (`QC15`) ومنع انهيار أرباع التون الشرقية (`24-EDO`) إلى سلالم غربية باردة (`QC16`) داخل **`Google Flow Music (Lyria 3.5)`**.

---

## 1. بروتوكول عزل البكاء والشهقات (`Crying & Weeping Isolation Protocol — QC15`)

أثبتت التجارب المقارنة المكثفة على `Lyria 3.5` أن كتابة واصفات البكاء والنحيب داخل حقل `Sound description` في اللطميات الإيقاعية يولّد ضوضاء بكاء وصراخ عشوائي في الخلفية يطمس مخارج الحروف ويشوّه استقرار الإيقاع:

1. **في جميع اللطميات الإيقاعية (`54 BPM` إلى `132 BPM`):**
   - **حظر مطلق (صفر بكاء أو شهقات في `Sound`):** يُمنع كتابة أيٍّ من المصطلحات: `emotional weep cracks`، `weeping`، `sobbing`، `majlis cries`، `tear-choked`، `wailing`، `screaming`.
   - **البديل الاحترافي الصانع للشجن العميق:** يُولَّد الحزن الفخم حصرياً عبر أبعاد المقام الشرقي (`Maqam Saba / Lami / Bayati / Saba Zamzam`) والواصفات الحنجرية الصافية:
     - `commanding deep resonant Baritone lead vocal`
     - `powerful high chest-voice climbs`
     - `natural vocal rasp`
     - `passionate microtonal melisma` / `prolonged microtonal vowel elongations`
2. **في النعي المنبري الحر فقط (`0 BPM Rubato Minbar Na'i` — جلسة مستقلة):**
   - يُسمح بوضع الكسرات البكائية الحسينية الوقورة **حصرياً** في قالب النعي المنبري الحر المستقل (`minbar_nai_0bpm_rubato_saba_exclusive_weeping`) بشرط تقييدها على نهايات العبارات قبل `..` بعد اكتمال نطق الحروف 100%:
     - `raw weeping cracks on phrase endings, prolonged microtonal vowel cries`.

---

## 2. جدار الحماية ضد الانحراف الغنائي وانهيار المقام الشرقي (`36-Term Song & 12-TET Leakage Blacklist — QC4 & QC16`)

إدراج مصطلحات الغناء الكلاسيكي الغربي مثل `legato phrasing` أو `calm / serene` أو كتابة `wordless pharyngeal Ahaat vocal drone` داخل حقل `Sound` في `Flow Music` يدفع النموذج إلى تسطيح أرباع التون (`24-EDO`) وتحويل اللطمية إلى ترنيمة غربية (`12-TET Ballad / Pad`).

### القائمة السوداء الكاملة المحظورة في حقل `Sound` للطميّة (`LATMIYA_SONG_LEAKAGE_BLACKLIST`):
1. **الآلات والتوزيع الغنائي:** `piano`, `guitar`, `strings`, `oud`, `violin`, `synth`, `808`, `trap`, `studio-arranged`, `studio-mixed`, `arranged studio`, `humming`, `pads`, `sub-bass`, `groove`, `bandari`, `harmonic`, `dammam` *(إلا في الزنجيل الصريح)*, `syncopated`, `--no piano`.
2. **الطبقات الخاطئة والإلقاء النثري:** `tenor`, `reciter`, `spoken`.
3. **الصراخ وفوضى البكاء في الإيقاع:** `wailing`, `screaming`, `tear-choked`, `emotional weep cracks`, `weeping`, `sobbing`, `majlis cries`.
4. **مُسطِّحات المقام الشرقي (`12-TET Collapse Triggers`):** `legato phrasing`, `wordless pharyngeal Ahaat vocal drone`, `calm`, `serene`.
5. **المصطلحات العربية المعرّبة بحروف لاتينية:** `bahha`, `tarjee'`, `maddat sawtiya`, `taqatee'`.

---

## 3. القاعدة الاستوديوية لطبقة الآهات البشرية (`Local Rosenberg + Formant Ahaat Synthesis Only`)

- **في `Flow Music`:** ينتهي وصف كل لطمية إيقاعية بقفل صارم: **`wide unison male Raddada response, Pure Acapella No Instruments`**.
- **في الماسترنغ المحلي (`scripts/hussaini_dsp_montage.py`):** تُولَّد طبقة الآهات البلعومية البشرية (`Ahaat`) محلياً عبر نموذج النبضة الحنجرية الفيزيائي **`Rosenberg Glottal Pulse (Tp=0.40, Tn=0.16) + 3% Breath Noise`** الممرر عبر رنانات الفورمانت البشرية لحرف المدّ `/a:/` (**`F1=730Hz, F2=1090Hz, F3=2440Hz`**) مع تباين كورالي طبيعي **`[-4, 0, +4] cents`** وخفض جانبي ذكي **`-3.0 dB Sidechain Ducking`** تحت صوت الرادود.
