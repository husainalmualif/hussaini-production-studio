# بروتوكول التهيئة المسبقة بصيغة `JSON` (`Module 39`) مع المعرّف المرجعي الاختياري — V45.0 OMNI-ARCHITECT

يوثق هذا الملف بروتوكول التهيئة المسبقة للجلسة (`JSON Session Pre-Conditioning`) في `Producer Chat` داخل `https://www.flowmusic.app/`.

---

## 1. السياسة الهندسية للمعرّفات الصوتية المرجعية (`Optional Reference Clip ID Policy`)

- **القاعدة الأساسية (عدم الاستنساخ الإجباري والتوافق العام مع جميع الحسابات):**
  - في الدالة البرمجية `build_flowmusic_json_preconditioning(dialect="iraqi_bahrani", maqam="saba", bpm=58, reference_clip_id=None)`، تكون معلمة **`reference_clip_id` اختيارية تماماً وقيمتها الافتراضية `None`**.
  - السبب الهندسي:
    1. التوافق التام مع **القاعدة 5 (منع الاستنساخ الحرفي لبصمة قصيدة سابقة على قصيدة جديدة)**.
    2. لأن معرّفات المقاطع (`clip IDs`) في `Flow Music` قد تكون مرتبطة بمكتبة جلسات المستخدم الخاصة، فلا تُفرض قسراً إلا إذا طلب المستخدم صراحةً تمرير معرّف مرجعي من مكتبته (`--reference-clip-id`).

---

## 2. توليد كائن التهيئة المسبقة برمجياً

```python
from scripts.hussaini_dsp_montage import build_flowmusic_json_preconditioning

# 1) الوضع القياسي المستقل (بدون فرض clip ID مسبق):
payload = build_flowmusic_json_preconditioning(dialect="iraqi_bahrani", maqam="saba", bpm=58)
# payload["golden_reference_clip_id"] -> None

# 2) الوضع المرجعي الاختياري (عند رغبة المستخدم في ربط التوليد بمقطع مرجعي من حسابه):
payload_with_ref = build_flowmusic_json_preconditioning(
    dialect="iraqi",
    maqam="saba",
    bpm=58,
    reference_clip_id="26bbb3d2-65f0-42c3-a167-37127631ef0a",
)
```
