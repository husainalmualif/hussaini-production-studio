# بروتوكول التهيئة المسبقة بصيغة `JSON` والاحتراف الكامل لواجهة `Flow Music Studio` (`Modules 39, 51 & 53`) — V48.5 OMNI-ARCHITECT (Rev 2)

يوثق هذا الملف بروتوكول التهيئة المسبقة للجلسة (`JSON Session Pre-Conditioning` عبر الدستور المرجعي `references/hussaini_os_v48_5_constitution.json` بوضع `"Pre_Conditioning_Lock_Wait_For_Stage_JSON"`)، وحزم المراحل الإلزامية (`Module 53` — `--build-stage-json`)، والقواعد الهندسية الصارمة للتعامل الاحترافي ثنائي القناة مع واجهة وأدوات `https://www.flowmusic.app/` (`New session`، لوحة `Compose` المباشرة، وقائمة `Remix > Extend / Trim / Replace / Cover / Variation / Use prompt / Split stems`).

---

## 1. السياسة الهندسية للمعرّفات الصوتية المرجعية (`Optional Reference Clip ID Policy — QC7`)

- في الدالة البرمجية `build_flowmusic_json_preconditioning(dialect="iraqi", maqam="saba", bpm=60, reference_clip_id=None)`، تكون معلمة **`reference_clip_id` اختيارية تماماً وقيمتها الافتراضية `None` (`null`)**:
  1. **منع الاستنساخ الأعمى (`Strict Anti-Cloning`):** منع لصق لحن قصيدة سابقة على قصيدة جديدة مختلفة الوزن والموضوع.
  2. **خصوصية الحساب (`Account-Scoped Clip UUIDs`):** معرّفات المقاطع في `Flow Music` خاصة بالحساب الذي أنشأها فقط؛ لذا تبقى `None` افتراضياً للتوافق مع جميع الحسابات.

---

## 2. توليد كائن التهيئة المسبقة برمجياً (`V48.5 OMNI-ARCHITECT`)

```python
from scripts.hussaini_dsp_montage import (
    build_flowmusic_json_preconditioning,
    build_stage_orchestration_json,
    load_v48_5_constitution,
)

# 1) تحميل الدستور التجريبي الكامل V48.5 (Rev 2) لإرساله في Producer Chat (القناة 1):
constitution = load_v48_5_constitution()

# 2) توليد كائن التهيئة المخصص للجلسة وحزمة المرحلة الأولى (Module 53):
payload = build_flowmusic_json_preconditioning(dialect="iraqi", maqam="saba_zamzam", bpm=58)
# payload["session_mode"] -> "Pre_Conditioning_Lock_Wait_For_Stage_JSON"
# payload["reference_clip_id"] -> None
stage_1 = build_stage_orchestration_json("[المُسْتَهَلّ]\nيَا إِحْسَينْ إِبْگَلْبِي ..")
```

---

## 3. القواعد الهندسية الصارمة لاحتراف واجهة وأدوات `Flow Music Studio`

### أ) القاعدة الذهبية الأولى: عزل المشاريع (`One New Poem = One New Session`)
- **قصيدة جديدة = مشروع جديد مستقل (`a[href="/session"]` — `New session`)**؛ وكذلك تُعزل مقدمات النعي المنبري الفصيح (`0 BPM Rubato`) في جلسة مستقلة خاصة بها.
- **قاعدة عرض الشاشة (`Viewport Rule`):** أغلق الشريط الجانبي الأيسر (`button[aria-label="Close sidebar"]`) وافتح لوحة التلحين (`button[aria-label="Toggle compose panel"]`).

### ب) القاعدة الذهبية الثانية: التوجيه ثنائي القناة (`Two-Channel Routing — Module 51 & QC17`)
1. **القناة الأولى (`Producer Chat` — `textarea[aria-label="Chat message"]`):**
   - أرسل دستور `Hussaini_Production_Studio_OS_V48_5_OMNI_ARCHITECT` في بداية الجلسة لقفل الذاكرة، واستخدمها لاحقاً لتطبيق `audio__apply_effect`.
2. **القناة الثانية (`Compose Panel`):**
   - **`Lyrics` (`textarea[aria-label="Lyrics"]`):** نص شعري عربي مشكول نقي 100% فقط، بعناوين عربية صريحة (`[المُسْتَهَلّ]`، `[النَّزْلَة الأُولَى]`، `[الكَسْرَة وَالمُسْتَهَلّ]`)، مع إحاطة جميع أشطر `[المُسْتَهَلّ]` بقوسين `(...)` قبل `..` (`QC18`)، و**صفر حروف لاتينية (`QC5`) وصفر أقواس `JSON` `{...}` (`QC17`)**. تأكد أن مفتاح `Toggle instrumental mode` مغلق (`OFF`).
   - **`Sound` (`textarea[aria-label="Sound description"]`):** وصف إنجليزي نقي (`45–56 كلمة`) من مكتبة `Module 52` مختوم بـ `Pure Acapella No Instruments` وبدون أي كلمات بكاء في الإيقاع (`QC15`).
   - **`Details` (`textarea[maxlength="100"]`):** عنوان القصيدة بالعربية، ثم اضغط `Generate` $\rightarrow$ قارن المرشَّحَين `A/B` $\rightarrow$ `CHOOSE / Keep Both`.

### ج) القاعدة الذهبية الثالثة: إتقان أدوات `Remix` الاحترافية (`...` $\rightarrow$ `Remix >`)
1. **`Extend` (`|-> Extend` — التمديد عبر المراحل الأربع `Module 52`):**
   - أضف التوجيه الإنجليزي للاستمرار وتحديث المقام في `textarea[aria-label="Instruction"]` **أولاً** (`Continue in the exact same commanding Baritone Radood voice and steady 60 BPM pulse, modulating smoothly to Maqam Lami and Bayati`)، ثم افتح **`Edit Lyrics`** وأضف النزلة الجديدة مع المستهل الجماعي `(...)` واضغط **`Done`** ثم **`Generate`**.
2. **`Trim` (`✂ Trim`):** قصّ المقطع قبل أي انحراف متأخر (مثلاً `1:27`) ثم مدّد منه عبر `Remix > Extend`.
3. **`Replace` (`Inpainting`):** إصلاح نطق كلمة واحدة موضعياً بتعديل تشكيلها في `Edit Lyrics` دون إعادة توليد القصيدة.
4. **`Split stems`:** فصل المسارات (`Vocals`, `Drums`, `Bass`, `Other`) لإدخال الصوت الصافي إلى `scripts/hussaini_dsp_montage.py`.
