# بروتوكول التهيئة المسبقة بصيغة `JSON` والاحتراف الكامل لواجهة `Flow Music Studio` (`Module 39`) — V45.0 OMNI-ARCHITECT

يوثق هذا الملف بروتوكول التهيئة المسبقة للجلسة (`JSON Session Pre-Conditioning`) والقواعد الهندسية الصارمة للتعامل الاحترافي مع واجهة وأدوات `https://www.flowmusic.app/` (`New session`، لوحة `Compose` المباشرة، وقائمة `Remix > Extend / Trim / Replace / Cover / Variation / Use prompt / Split stems`).

---

## 1. السياسة الهندسية للمعرّفات الصوتية المرجعية (`Optional Reference Clip ID Policy`)

- **القاعدة الأساسية (عدم الاستنساخ الإجباري والتوافق العام مع جميع الحسابات):**
  - في الدالة البرمجية `build_flowmusic_json_preconditioning(dialect="iraqi_bahrani", maqam="saba", bpm=58, reference_clip_id=None)`، تكون معلمة **`reference_clip_id` اختيارية تماماً وقيمتها الافتراضية `None` (`null`)**.
  - **السبب الهندسي والمعماري:**
    1. **التوافق التام مع القاعدة 5 (`Strict Anti-Cloning`):** منع استنساخ بصمة أو لحن قصيدة سابقة على قصيدة جديدة مختلفة الوزن والموضوع.
    2. **خصوصية الحساب (`Account-Scoped Clip UUIDs`):** معرّفات المقاطع (`UUIDs`) في `Flow Music` مرتبطة حصرياً بمكتبة الحساب الذي أنشأها، ولن تعمل لدى أي مستخدم آخر؛ لذا يُستخدم `<OPTIONAL_USER_CLIP_UUID>` كمثال توضيحي فقط، وتبقى القيمة الافتراضية `None`.

---

## 2. توليد كائن التهيئة المسبقة برمجياً

```python
from scripts.hussaini_dsp_montage import build_flowmusic_json_preconditioning

# 1) الوضع القياسي المستقل (بدون فرض clip ID مسبق — يعمل على جميع الحسابات):
payload = build_flowmusic_json_preconditioning(dialect="iraqi_bahrani", maqam="saba", bpm=58)
# payload["reference_clip_id"] -> None

# 2) الوضع المرجعي الاختياري (عند رغبة المستخدم في ربط التوليد بمقطع من حسابه الشخصي فقط):
payload_with_ref = build_flowmusic_json_preconditioning(
    dialect="iraqi",
    maqam="saba",
    bpm=58,
    reference_clip_id="<OPTIONAL_USER_CLIP_UUID>",
)
```

---

## 3. القواعد الهندسية الصارمة لاحتراف واجهة وأدوات `Flow Music Studio`

### أ) القاعدة الذهبية الأولى: عزل المشاريع (`One New Poem = One New Session`)
- **عندما يعطيك المستخدم كلمات قصيدة شعرية حسينية جديدة، يجب فوراً فتح مشروع جديد مستقل (`New session`) والبدء من الصفر!**
- **يُمنع منعاً باتاً** توليد قصيدة جديدة داخل جلسة (`Session`) قديمة تحتوي على قصائد سابقة؛ لأن بقاءك في نفس الجلسة يجعل وكيل `Producer` يخلط بين كلمات القصيدة القديمة والقصيدة الجديدة أو يستدعي معرّفات مقاطع سابقة غير متوافقة عروضياً.
- **محددات الواجهة (`DOM Selectors`):**
  - لفتح مشروع جديد: انقر على `a[href="/session"]` (`New session`).
  - **تنبيه هام حول عرض الشاشة (`Viewport Rule`):** إذا كان الشريط الجانبي الأيسر مفتوحاً، فإنه قد يدفع لوحة `Compose` اليمنى خارج الشاشة؛ لذلك يجب دائماً طيّ الشريط الجانبي الأيسر عبر `button[aria-label="Close sidebar"]` والتأكد من فتح لوحة الاستوديو عبر `button[aria-label="Toggle compose panel"]` (`data-state="open"`).

### ب) القاعدة الذهبية الثانية: استخدام لوحة `Compose` المباشرة (`Direct Compose Studio Panel`)
بدلاً من حشو التعليمات الإنجليزية مع الكلمات العربية في صندوق المحادثة (`textarea[aria-label="Chat message"]`)، استخدم حقول لوحة **`Compose`** المخصصة مباشرةً:
1. **قسم الكلمات (`Lyrics` — `textarea[aria-label="Lyrics"]`):**
   - ضع فيه **النص الشعري العربي المُشكّل فقط** (مع الفواصل `..` وعناوين المقاطع `[Intro]`، `[Chorus]`، `[Verse 1]`) دون أي كلمة إنجليزية أو شرح تقني.
   - تأكد من بقاء مفتاح `button[role="switch"][aria-label="Toggle instrumental mode"]` مغلقاً (`OFF`).
2. **قسم الوصف الصوتي (`Sound` — `textarea[aria-label="Sound description"]`):**
   - ضع فيه وصف الهوية الصوتية والطور والمقام والنبض (`BPM`) فقط.
3. **قسم التفاصيل والعنوان (`Details` — `textarea[maxlength="100"]`):**
   - افتح القسم عبر `button[aria-label="Expand Details section"]`، واكتب عنوان اللطمية باللغة العربية بشكل نظيف.
4. **زر التوليد (`Generate` $\rightarrow$ `CHOOSE` $\rightarrow$ `Keep Both`):**
   - اضغط زر `Generate` أسفل يمين لوحة `Compose`، وعند ظهور المرشَّحَين (`A/B Candidates`) اختر الأفضل عبر `CHOOSE` ثم اضغط `Keep Both` لحفظ النسختين في المكتبة (`Library`).

### ج) القاعدة الذهبية الثالثة: إتقان أدوات `Remix` الاحترافية (`...` $\rightarrow$ `Remix >`)
عند النقر على زر النقاط الثلاث `button[aria-label^="More options for "]` بجانب أي مقطع، تفتح قائمة **`Remix >`** سبع أدوات احترافية:

1. **`Extend` (`|-> Extend` — التمديد السلس للقصيدة الطويلة بنفس الصوت واللحن):**
   - **الاستخدام الإلزامي:** عند الرغبة في تمديد اللطمية وإضافة مقاطع شعرية جديدة (المقطع الثالث، الرابع، الخامس، الخاتمة)، **استخدم `Remix > Extend` حصراً** بدلاً من توليد مقطع منفصل يفقد هوية الصوت أو اللحن!
   - **خطوات `Extend` ومحدداتها (`Edit Mode Drawer DOM`):**
     - افتح `button[aria-label^="More options for "]` $\rightarrow$ `Remix` $\rightarrow$ `Extend`.
     - اضبط نقطة التمديد الزمنية (`SETTINGS: Extend <start>-<end>`).
     - في حقل **`Instruction`** (`textarea[aria-label="Instruction"]`): اكتب توجيه الحفاظ على نفس الأداء (`Continue in the exact same slow weeping Radood voice, steady BPM, Maqam Saba, and low Qarar Ahaat`).
     - انقر على زر **`Edit Lyrics`** لفتح نافذة تعديل الكلمات التفاعلية (`Modal textarea` مع `Show Diff`)، وأضف الأبيات الجديدة في نهايتها (مقسّمة عمودياً وبدون أي سكون ابتدائي)، ثم اضغط **`Done`**.
     - اضغط **`Generate`** أسفل يمين لوحة `EXTEND` للحصول على اللطمية الممدّدة كملف صوتي واحد متصل (`<Title> (Extended)`).
2. **`Trim` (`✂ Trim` — قصّ الجزء المنحرف ثم التمديد منه):**
   - إذا كانت اللطمية رائعة من البداية حتى ثانية معينة (مثلاً `0:00–1:27`) ثم انحرفت بعدها إلى سرعة أو لحن غنائي، استخدم **`Remix > Trim`** لقصّ المقطع عند `1:27`، ثم استخدم **`Remix > Extend`** انطلاقاً من `1:27` لإكمال القصيدة بنفس الشجن.
3. **`Replace` (`Replace` — الإصلاح الموضعي لأخطاء اللفظ `Inpainting`):**
   - إذا وُجد خطأ في لفظ كلمة أو شطر واحد داخل مقطع متكامل، استخدم **`Remix > Replace`** لتحديد الثواني الخاصة بذلك الشطر فقط، وعدّل تشكيله الصوتي في `Edit Lyrics` لإصلاحه موضعياً دون المساس ببقية اللطمية.
4. **`Use prompt` (`Use prompt` — استنساخ الإعدادات إلى لوحة `Compose`):**
   - ينسخ حقول `Lyrics` و`Sound` و`Details` الخاصة بالمقطع مباشرة إلى لوحة `Compose` للتعديل النظيف عليها.
5. **`Cover` & `Variation`:**
   - **`Cover`**: إعادة أداء نفس المسار اللحني بصوت أو طابع كورالي مختلف.
   - **`Variation`**: توليد تنويعة لحنية قريبة تحافظ على روح المقطع الأصلي.
6. **`Start session`:**
   - فتح جلسة عمل جديدة تنطلق من هذا المقطع المحدّد فقط.
7. **`Split stems` (في القائمة الرئيسية `...`):**
   - فصل اللطمية إلى مسارات مستقلة (`Vocals`, `Drums`, `Bass`, `Other`) لاستخراج صوت الرادود الصافي ومعالجته عبر محرك المونتاج ذي الـ 5 مسارات (`scripts/hussaini_dsp_montage.py`).
