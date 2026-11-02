# بروتوكول التهيئة المسبقة بصيغة `JSON` (`Module 39`) مع المعرّف المرجعي الاختياري — V45.0 OMNI-ARCHITECT

يوثق هذا الملف بروتوكول التهيئة المسبقة للجلسة (`JSON Session Pre-Conditioning`) في `Producer Chat` داخل `https://www.flowmusic.app/`.

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
