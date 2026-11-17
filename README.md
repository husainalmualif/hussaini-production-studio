# استوديو الإنتاج الحسيني الشامل — Hussaini Production Studio (V53.0 OMNI-ARCHITECT)

منظومة هندسية متكاملة ومثبتة تجريبياً للتأليف الشعري الحسيني، وهندسة المقامات الميكروتونالية (`24-EDO`) والأطوار المنبرية والموكبية، وتوليد اللطميات والنواعي بالذكاء الاصطناعي (**Google Flow Music / Lyria 3.5, Suno, Udio**) بدقة نطق وأداء تقارب 100% عبر **الدستور التجريبي الموحّد (`references/hussaini_os_v50_0_constitution.json`)**، و**الفهرس المرجعي الشامل لـ 175 لطمية والمدارس الحسينية التسع (`Module 64 — 9 Master Schools & 25 Master Sound Prompts + V52 Extended Atwar`)**، و**بروتوكول الاستكشاف والتشاور الإلزامي قبل التوليد مقابل وضع التفويض الكامل (`Module 66 — Interactive Consultation vs. Auto-Pilot`)**، و**القواعد السلبية الدائمة (`NC1–NC17`) وقانون الأسطر العمودية الثلاثة في الكسرة ضمن نافذة التمديد `23.5s` (`NC16 & NC17`)**، و**بروتوكول حزم `Stage JSON` مع النسخ الحرفي `lyrics_register_verbatim` (`Modules 53 & 59 — QC19, QC29`)**، ومع **وحدة V52 (`Module 67`): محرك التشكيل وتصريف اللهجات (`99.62%` على 127 مقطعاً)، والمحقق التاريخي (`--verify-history`)، ومخطط مراحل التمديد (`--plan-stages`)، ومحرك المونتاج الصوتي النقي ذو الـ 18 وضعاً (`scripts/hussaini_dsp_montage.py` — `--mode vocal_pure_master`, `--trim-end-sec`, `--fade-out-sec`, `--audit-audio`, `-14.0 LUFS` & `-1.0 dBTP` EBU R128)** (مع حظر ماسترنغ Flow Step 4 السحابي الذي يسبب Clipping).

---

## أبرز ركائز الإصدار `V53.0 OMNI-ARCHITECT` (توحيد `V50.0` + `Module 66` + `NC1–NC17` + تحليل 175 لطمية)

1. **بروتوكول الاستكشاف والتشاور قبل التوليد وبوابة الجودة قبل التمديد (`Module 66`):**
   - يُمنع البدء بتوليد أي مقطع صوتي مباشرة قبل إجراء جلسة استيضاح سريعة مع المستخدم (تحليل البحر العروضي واللهجة والجو الدرامي، ثم عرض الخيارات العملية للمدرسة والأسلوب، الطور والمقام، الإيقاع والـ BPM، المؤثرات الصوتية، وتوزيع الرادود والكورال)، **إلا** إذا فوض المستخدمُ الوكيلَ صراحةً بعبارة مثل *«اختر كل شيء بنفسك»* (`Auto-Pilot Mode`).
   - يُمنع الانتقال إلى مراحل التمديد (`EXTEND`) قبل اجتياز **بوابة الجودة للمرحلة التأسيسية الأولى (`Stage-1 Quality Gate`)**.
2. **القواعد السلبية الدائمة (`NC1–NC17`) وقانون الأسطر العمودية الثلاثة في الكسرة (`23.5s Extend Law — NC16 & NC17`):**
   - **`NC1` (حظر ذكر أسماء الآلات الموسيقية):** منع كتابة (`Ney, Flute, Oud, Guitar, Violin, Cello, Piano, Drum Kit`) في أي برومبت أو كائن JSON لمنع تفعيل عزف منفرد طربي (`Solo`).
   - **`NC16` (قانون الأسطر العمودية الثلاثة في الكسرة):** لما كانت كل نافذة تمديد (`Extend`) مدتها **`23.5` ثانية** ويغني الرادود كل سطر عمودي في `7.5` ثانية على سرعة `60 BPM`، تُصاغ كل **`[الكَسْرَة]` (`2B, 3B, 4B, 5B, 6B`) في `3 أسطر عمودية حصراً` (`~21.5s`)** (السطر 1: الشطر الأول + الشطر الثاني من التثليث بينهما `..` / السطر 2: الشطر الثالث / السطر 3: بيت القفلة كاملاً بدون سطر خامس مكرر للجوقة) لضمان غناء `بيت القفلة` كاملاً بنسبة `100%` دون بتر.
   - **`NC17` (التطهير الإجباري لحقل `Lyrics` قبل كل تمديد):** مسح صندوق `Compose > Lyrics` بالكامل (`Ctrl+A -> Delete`) قبل كل خطوة تمديد في الطريقتين الأولى والثانية لمنع دمج أو تكرار الأبيات السابقة.
   - **`NC3–NC15` (أقفال النطق العراقي الموثقة سمعياً):** كتابة `انْگِسَمْ نُصَّينْ`، `رِدَتْ نَشْدَه`، `صُوتْ أُمِّ البَنِينْ يِصِيحْ`، `لَمَّنْ رَدْ إِبِنْ حَذْلَمْ`، `بِشِرْ گَطَّعِتْ إِفَّادِي`، و`مَا أَنْشِدَكْ عَلَى أَوْلَادِي`.
3. **المدارس الصوتية التسع ومكتبة الـ 25 برومبت القياسية (`Module 64 — 175-Track Corpus`):**
   - تحليل صوتي ومقامي وإيقاعي وهيكلي شامل لـ **`175` لطمية** عبر 9 مدارس كبرى: **مدرسة الملا باسم الكربلائي الكلاسيكية والثقيلة (`School 1`)**، **المدرسة الفراتية الركبانية واللامي (`School 2`)**، **مدرسة الكليبات الاستوديوية السردية (`School 3`)**، **المدرسة البحرانية الموكبية والتراثية (`School 4` — الستراوي، الثلاثي، الرباعي، الحيدري، الوقفة)**، **مدرسة الحماسة والشور السريع (`School 5`)**، **مدرسة النعي المنبري الحر والموال (`School 6 — 0 BPM Rubato`)**، **مدرسة الفصحى الملحمية (`School 7`)**، **المدرسة الخليجية الأحسائية/القطيفية (`School 8`)**، و**مدرسة الليالي العاشورائية الخاصة (`School 9`)**.
2. **قانون الـ 80 ثانية والمقطع الواحد لكل `Extend` (`Module 60 — QC30`):**
   - تقييد كل عملية تمديد (`Remix > Extend`) في `Flow Music` بـ **مقطع شعري واحد فقط (`1 Stanza = [النَّزْلَة] + [الكَسْرَة] + 4 أشطر مستهل`)** بحد أقصى **`7` أبيات (`14` شطراً عمودياً)**، لمنع ضغط الأبيات في `2.5` ثانية وتفادي تداخل صوت الكورال مع الرادود عند الثانية `0:47`.
3. **هندسة المستهل المزدوج ومنع استنساخ الجوقة على النزلة (`Module 61 — QC31`):**
   - تقييد أي بلوك `[المُسْتَهَلّ]` بحد أقصى **`4` أشطر متتالية بين قوسين `(...)`**.
   - عند طلب المستهل مرتين في الافتتاح (`Stage 1 Root`)، يُكتب التكرار الأول باسم **`[المُسْتَهَلّ الأَوَّلْ]`** بدون أقواس على الشطور الثلاثة الأولى (أداء فردي للرادود) مع وضع الشطر الرابع فقط بين قوسين `(...)`، يليه **`[المُسْتَهَلّ]`** بـ `4` أشطر بين قوسين `(...)` (جوقة الردّادة الموحدة)، ثم جسر همهمة `4` ثوانٍ (`مممم...`) قبل `[النَّزْلَة الأُولَى]` لمنع تسرّب الكورال إلى أبيات الرادود.
4. **حظر السطر اليتيم ذي الكلمة الواحدة والألف الوقائية الانتقائية (`Modules 62 & 63 — QC32, QC33, QC34`):**
   - منع وضع كلمة أو كلمتين في سطر عمودي منفصل (`وَ نَادَيتَه ..` أو `وَ لَاگَيتَه ..` أو `وَ جُرُوحَه ..`) لأن ذلك يكسر وزن الطور في `Lyria 3.5` إلى إلقاء نثري متقطع؛ بل يُدمج الشطر المتوازن كاملاً (`مَرَّيتْ بِـ نَهَرْ عَلْقَمِي .. وَ نَادَيتَه ..` و`گُمِتْ أَنْشِدْ إِعْلَه إِچْفُوفَكْ .. وَ لَاگَيتَه ..`).
   - قصر الألف الوقائية المكسورة `إِ` على العناقيد العراقية الساكنة الحقيقية (`إِحْسَينْ، إِبْچَفَّكْ، إِچْفُوفَكْ، إِعْيُونِي، إِبْگَلْبِي، إِعْلَه`)، ومنع إضافتها على الجموع المكسورة الأول مثل **`خِيَمْ / خِيَامْ`** (تُكتب `مَا ظَلَّتْ خِيَمْ لِينَا` لا `إِخْيَمْ` لمنع تحريفها إلى الفعل `تِخَيَّمْ`)، مع استخدام الصيغ الصرفية الصريحة (`بِالمَذَابِحْ، بِسْيَاطِ الحِقِدْ، بِـ نَهَرْ عَلْقَمِي، رِكْضَتْ أَشْكَالْ`).
5. **حزمة `Stage JSON` ذات الـ 7 مفاتيح وترقيم الكسرات (`Modules 53, 57 & 59 — QC19, QC27, QC29`):**
   - إلزامية المفتاح السابع **`lyrics_register_verbatim`** في كل مرحلة لتمريره حرفياً إلى `lyrics__register`، وترقيم وسوم الكسرة تصاعدياً (`[الكَسْرَة الأُولَى] .. [الكَسْرَة الخَامِسَه]`) لمنع قفز النموذج إلى كسرة سابقة.

---

## أولاً: طريقة التثبيت والتفعيل (`Installation & Setup`)

```bash
npx skills add husainalmualif/hussaini-production-studio
```
أو بنسخ المستودع مباشرة إلى مسار المهارات:
- **Windows:** `C:\Users\<Username>\.gemini\config\skills\hussaini-production-studio`
- **macOS / Linux:** `~/.gemini/config/skills/hussaini-production-studio`

---

## ثانياً: سير العمل التطبيقي في `Flow Music` والمحرك المحلي (`V50.0 OMNI-ARCHITECT`)

### 1. التوليد المتقن في `https://www.flowmusic.app/` عبر الطريقتين المتفق عليهما بعد إرسال كائن التهيئة (`Modules 39, 49–65`)
1. **افتح جلسة جديدة مستقلة (`New session` — `a[href="/session"]`)** لكل قصيدة جديدة.
2. **الخطوة التأسيسية المشتركة في الطريقتين (`Step 1`):** أرسل **كائن التهيئة المسبقة (`Pre-Conditioning JSON`)** في **`Producer Chat`** وانتظر تأكيد القفل.
3. **الطريقة الأولى (`Method 1 — استخدام Compose > Lyrics بعد إرسال كائن التهيئة`):**
   - انتقل إلى لوحة **`Compose > Lyrics`**، والصق وصف `Sound` في خانة `Sound`، والصق النص العربي المشكول الصافي في خانة `Lyrics` (مع فصل `[الكَسْرَة الأُولَى..الخَامِسَه]` و`[المُسْتَهَلّ]` في وسمين مستقلين، وصفر أقواس `{...}` أو حروف إنجليزية).
4. **الطريقة الثانية (`Method 2 — الأوامر بصيغة JSON داخل الأبيات والمقاطع بعد إرسال كائن التهيئة`):**
   - أرسل لكل مرحلة (`Stage 1` إلى `Stage 5`) حزمة الـ `JSON` التوجيهية الكاملة حيث تكون الأوامر بصيغة `JSON` محيطة بالأبيات داخل مصفوفة `sections[]` (`section_tag, performer, meter_and_syllables, tempo_feel, tor_and_maqam, throat_and_maddat_dynamics, rhythm_chants_and_sfx, audio_engineering_3d, dialect_phonetic_locks, lyrics_arabic`) مع `lyrics_register_verbatim`.
5. **التمديد عبر المراحل (`Remix > Extend — 1 Stanza per Extend Law QC30`):**
   - خصص لكل مقطع شعري مرحلة `Extend` مستقلة (`Stage 2 = المقطع 2 فقط`، `Stage 3 = المقطع 3 فقط`، `Stage 4 = المقطع 4 فقط`، `Stage 5 = المقطع 5 فقط`).

### 2. الأوامر البرمجية والطرفية (`CLI & Python API — V50.0 OMNI-ARCHITECT`)

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# 1) ترجمة وتشكيل النص الشعري وبناء حزمة Stage JSON ذات الـ 7 مفاتيح (Modules 53, 59–63 — QC19, QC29–QC35)
python3 scripts/hussaini_dsp_montage.py --compile-lyrics "ياحسين بچفك عيوني عالباب وسادة ريش والعافية"
python3 scripts/hussaini_dsp_montage.py --build-stage-json "[المُسْتَهَلّ]\n(گَعْدَتْ إِعْلَه التَّلْ تِنَاشِدْ) ..\n[النَّزْلَة الأُولَى]\nمِشَتْ زَينَبْ إِعْلَه الرَّمْضَه .."

# 2) فحص القصيدة الشامل عبر بوابات الجودة الـ 35 (QC1–QC35)
python3 scripts/hussaini_dsp_montage.py --lint-poem "[المُسْتَهَلّ]\n(گَعْدَتْ إِعْلَه التَّلْ تِنَاشِدْ) ..\n(وَينَكْ يَا خُويَه إِحْسَينْ) ..\n(مَا ظَلَّتْ خِيَمْ لِينَا) ..\n(تِحْمِي بَنَاتِ الدِّينْ) .."

# 3) استعراض خطة المراحل وتصدير دستور V50.0 OMNI-ARCHITECT (25 Master Sound Prompts & 9 Schools)
python3 scripts/hussaini_dsp_montage.py --stage-plan iraqi
python3 scripts/hussaini_dsp_montage.py --verify-history "صوت أم البنين يصيح يبن حذلم"
python3 scripts/hussaini_dsp_montage.py --plan-stages "[المُسْتَهَلّ]\nصوت أم البنين يصيح يبن حذلم\n[الكوبليه الأول]\nيا ناشد على الطف وعندك علم"
python3 scripts/hussaini_dsp_montage.py --export-constitution

# 4) المونتاج الصوتي ذو الـ 18 وضعاً: الوضع النقي (--mode vocal_pure_master لحفظ لطمة Flow الطبيعية) أو الـ 5 مسارات مع تنظيف الإيقاع الآلي وماسترنغ EBU R128 (-14.0 LUFS / -1.0 dBTP) + فحص --audit-audio
python3 scripts/hussaini_dsp_montage.py \
  --input "split_vocals.wav" \
  --output "mastered_heavy_clip.wav" \
  --mode "heavy_clip" \
  --bpm 58 \
  --maqam-drone "saba_zamzam" \
  --replace-ai-percussion \
  --foley "wind" \
  --audio-drop-sec 12.0

# 5) فحص جودة الكود (Pylint) وتشغيل اختبارات الوحدات الشاملة (Pytest >= 75% Coverage)
pylint --disable=C0301,R0912,R0913,R0914,R0915,R0917 scripts/hussaini_dsp_montage.py tests/test_hussaini_modules.py
pytest -v --cov=scripts --cov-fail-under=75 tests/test_hussaini_modules.py
```

---

## ثالثاً: هيكل ملفات المهارة وبيئة الفحص الآلي (`Repository Structure — 28 Canonical Files`)

```text
hussaini-production-studio/
├── VERSION                                                                  # مصدر الحقيقة الموحد للإصدار (V53.0 OMNI-ARCHITECT)
├── SKILL.md                                                                 # الموجّه المهيكل الرشيق (<= 10.5KB Router)
├── README.md                                                                # الدليل الشامل للاستخدام والمرجع السريع
├── requirements.txt                                                         # المتطلبات البرمجية الخفيفة (numpy, scipy, pylint, pytest, pytest-cov)
├── references/
│   ├── hussaini_os_v50_0_constitution.json                                  # الدستور التجريبي الموحّد لـ V53.0 OMNI-ARCHITECT (9 Schools, 25 Prompts, QC1–QC35, NC1–NC17)
│   ├── atwar_maqamat_and_poetry_guide.md                                    # الموسوعة المرجعية الشاملة للأطوار والمقامات والعروض (Sections 1–19)
│   ├── radoods_and_khutaba_encyclopedia.md                                  # موسوعة 20+ رادوداً (14 مدرسة) و8 من خطباء المنبر
│   └── modules/
│       ├── experimental_ab_evaluation_and_human_review.md                   # مصفوفة التقييم التجريبي وبوابة المراجعة الشرعية والأدبية
│       ├── module_39_json_preconditioning.md                                # التهيئة المسبقة للجلسة وأدوات واجهة Flow Music
│       ├── module_40_41_43_phonetics_and_dialects.md                        # التنوين اللهجي/العروضي، فكّ الالتصاق، وتفكيك البادئات
│       ├── module_42_gireez_hosa_and_muharram_calendar.md                   # فن الگريز، الهوسة العراقية (3+1)، وتقويم محرم وصفر
│       ├── module_44_studio_production_and_heavy_clips.md                   # المستويات الاستوديوية الثلاثة، Rosenberg Ahaat، والكليبات الثقيلة
│       ├── module_45_dialect_orthoepy_and_tashkeel_mastery.md               # الحنجرة الذهبية، الهندسة العكسية، والضبط الفونيمي
│       ├── module_46_rhythm_choir_and_tor_diversity.md                      # 6 عائلات إيقاعية، أطوار البحرين الستة، وفصل الوزن عن الطور
│       ├── module_47_genre_taxonomy_latmiya_nasheed_ibtihalat_tawashih.md   # التفريق الصارم بين الفنون الدينية الأربعة والقائمة السوداء
│       ├── module_48_secrets_of_legendary_latmiyat.md                       # الأركان الذهبية الخمسة والمعمارية الموحدة ذات الـ 20 سطراً
│       ├── module_49_pure_dialect_isolation_and_iraqi_prosthetic_clusters.md # عزل اللهجة الواحدة، الألف الوقائية العراقية، وحروف اللين المفتوحة
│       ├── module_50_crying_isolation_and_anti_12tet_firewall.md            # عزل البكاء في 0 BPM وجدار الـ 36 مصطلحاً ضد انهيار 24-EDO
│       ├── module_51_two_channel_routing_and_collective_estehlal.md         # التوجيه ثنائي القناة وإلزامية المستهل الجماعي (...)
│       ├── module_52_dynamic_4stage_maqam_progression_and_master_prompts.md # التدرج المقامي الرباعي ومصفوفة البرومبتات القياسية
│       ├── module_53_per_stage_and_section_json_orchestration.md            # إلزامية حزم Stage/Section JSON ومنع النص المجرّد (QC19)
│       ├── module_54_to_65_v50_super_algorithm_and_175_corpus.md            # خوارزمية V50.0 الفائقة، المدارس التسع، قانون الـ 80 ثانية، ومصفوفة QC20–QC35
│       ├── module_66_v51_field_evaluation_consultation_and_style_taxonomy.md # بروتوكول V51.2، الاستشارة مقابل التفويض، القواعد السلبية NC1–NC17، وقانون الأسطر الـ 3
│       ├── module_67_v52_pure_vocal_dsp_corpus_phonetics_and_history.md      # بروتوكول V52.0: vocal_pure_master، EBU R128، --verify-history، --plan-stages، ومصرف الـ 127 مقطعاً
│       └── module_68_v53_dual_corpus_flow_bahrani_iraqi_mastery.md           # بروتوكول V53.0: تدقيق الكوربوسين (99.9%+)، تجارب Flow البحرانية والعراقية، QC34، و 11 قاعدة مقاتل
├── scripts/
│   └── hussaini_dsp_montage.py                                              # المحرك المستقل للنطق الصوتي والـ 18-Mode Pure-Vocal / 5-Track DSP (EBU R128)
├── tests/
│   └── test_hussaini_modules.py                                             # اختبارات الوحدات الشاملة لـ Modules 34–68 وQC1–QC35 وNC1–NC17 والـ DSP
└── .github/
    └── workflows/
        └── ci.yml                                                           # فحص GitHub Actions CI عبر Python 3.10, 3.11, 3.12
```
