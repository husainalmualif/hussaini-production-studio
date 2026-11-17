# استوديو الإنتاج الحسيني الشامل — Hussaini Production Studio (V55.0 OMNI-ARCHITECT)

منظومة هندسية متكاملة ومثبتة تجريبياً للتأليف الشعري الحسيني، وهندسة المقامات الميكروتونالية (`24-EDO`) والأطوار المنبرية والموكبية، وتوليد اللطميات والنواعي بالذكاء الاصطناعي (**Google Flow Music / Lyria 3.5, Suno, Udio**) بدقة نطق وأداء عالية عبر **الدستور التجريبي الموحّد (`references/hussaini_os_v50_0_constitution.json`)**، و**مختبر تجارب «طبع البشر» السبع على `flowmusic.app` وموجّه المراحل الخمس ومعيار القصائد الثلاث (`Module 70 — V55.0`، القواعد `NC18–NC22`)**، و**مختبر الـ 175 لطمية الصوتي العميق و`Module 69` (`V54.0` — De-Esser `5.5–8.5kHz`، ضاغط Optical RMS، صدى حسينية استيريو حقيقي، ومحلل `24-EDO` النسبي وكاشف النعي الحر `Rubato`)**، و**بروتوكول الاستكشاف والتشاور قبل التوليد (`Module 66`)**، و**القواعد السلبية الدائمة (`NC1–NC22` و`23.5s` 3-Line Kasra Law)**، و**حزم `Stage JSON` (`Modules 53 & 59`)**، ومع **محرك التشكيل وتصريف اللهجات (`100%` في القصائد المرجعية الثلاث و`99.9%+` / `0` أخطاء تكرار عبر `263` مقطعاً)**، و**المحقق التاريخي ذي الـ 11 قاعدة (`--verify-history`)**، و**محرك المونتاج ذي الـ 18 وضعاً (`scripts/hussaini_dsp_montage.py` — `--mode vocal_pure_master`, `--audit-audio`, `-14.0 LUFS / -1.0 dBTP` EBU R128)** (مع حظر ماسترنغ Flow Step 4 السحابي الذي يسبب Clipping).

---

## أبرز ركائز الإصدار `V55.0 OMNI-ARCHITECT` (`Module 70` + `Module 66–69` + `NC1–NC22` + تحليل 175 MP3)

1. **بروتوكول الاستكشاف والتشاور قبل التوليد وبوابة الجودة قبل التمديد (`Module 66 & 70`):**
   - يُمنع البدء بتوليد أي مقطع صوتي مباشرة قبل إجراء جلسة استيضاح سريعة مع المستخدم عبر التحليل الخماسي (`five_stage_analysis`: البحر العروضي، المحور الدرامي، المقام والطور، الإيقاع والـ BPM، والضبط الفونيمي)، **إلا** إذا فوض المستخدمُ الوكيلَ صراحةً بعبارة مثل *«اختر كل شيء بنفسك»* (`Auto-Pilot Mode`).
   - يُمنع الانتقال إلى مراحل التمديد (`EXTEND`) قبل اجتياز **بوابة الجودة للمرحلة التأسيسية الأولى (`Stage-1 Quality Gate`)**.
2. **القواعد السلبية الدائمة (`NC1–NC22`) وقانون الأسطر العمودية الثلاثة في الكسرة (`23.5s Extend Law — NC16 & NC17`):**
   - **`NC1` (حظر ذكر أسماء الآلات الموسيقية):** منع كتابة (`Ney, Flute, Oud, Guitar, Violin, Cello, Piano, Drum Kit`) في أي برومبت أو كائن JSON لمنع تفعيل عزف منفرد طربي (`Solo`).
   - **`NC16` (قانون الأسطر العمودية الثلاثة في الكسرة):** لما كانت كل نافذة تمديد (`Extend`) مدتها **`23.5` ثانية** ويغني الرادود كل سطر عمودي في `7.5` ثانية على سرعة `60 BPM`، تُصاغ كل **`[الكَسْرَة]` (`2B, 3B, 4B, 5B, 6B`) في `3 أسطر عمودية حصراً` (`~21.5s`)** لضمان غناء `بيت القفلة` كاملاً بنسبة `100%` دون بتر.
   - **`NC17` (التطهير الإجباري لحقل `Lyrics` قبل كل تمديد):** مسح صندوق `Compose > Lyrics` بالكامل (`Ctrl+A -> Delete`) قبل كل خطوة تمديد لمنع دمج أو تكرار الأبيات السابقة.
   - **`NC3–NC15` (أقفال النطق العراقي الموثقة سمعياً):** كتابة `انْگِسَمْ نُصَّينْ`، `رِدَتْ نَشْدَه`، `صُوتْ أُمِّ البَنِينْ يِصِيحْ`، `لَمَّنْ رَدْ إِبِنْ حَذْلَمْ`، `بِشِرْ گَطَّعِتْ إِفَّادِي`، و`مَا أَنْشِدَكْ إِعْلَه أَولَادِي`.
   - **`NC18–NC22` (قوانين مختبر التجارب السبع لقصيدة «طبع البشر» على `Lyria 3.5`):**
     - **`NC18`:** حظر كتابة الأرقام الفيزيائية (`53Hz`, `55Hz`, `320ms`) أو مفردات الضرب والإيقاع (`chest slaps`, `percussion`, `drums`, `no drums`) في خانة `Sound`؛ واستخدام البرومبت الموثق `ashura_majlis_noha_58bpm_saba_lami_v55` (`soft muffled bare chest thumping only`) أو `pure_acapella_weeping_noha_auto_bpm_saba_lami_v55` (`BPM = Auto`).
     - **`NC19`:** قفل المحرك دائماً على `Lyria 3.5` (وحظر `Lyria 3 Pro` الذي ينهار إلى تصفيق أفراح)، وحظر الصفات الغنائية الناعمة (`warm, sincere`)، ومنع إرسال JSON التهيئة منفرداً في `Producer Chat` بدون المرحلة الأولى.
     - **`NC20`:** ضبط قوة `Remix > Cover` عند **`Strength <= 0.40–0.45`** (`More Similar`) واستخدام `Split stems` لعزل `Vocals` بنقاء `100%` قبل المونتاج المحلي.
     - **`NC21`:** منع وضع السكتة `..` بين المتلازمين في أشطر الكسرة الثلاثية القصيرة قبل كلمة مفردة (`الخِدْمَه إِنْكِسَارِي وَ دَمْعِتِي` بدلاً من `.. وَدَمْعِتِي`).
     - **`NC22`:** فتح الألف الممدودة/المقصورة قبل `الـ` (`طَبْعِ البَشَرْ يِنْسَى الوَفَا`) وكسر الساكن لالتقاء الساكنين (`مُو مِثِلِ البَشَرْ`).
3. **المدارس الصوتية التسع ومكتبة الـ 31 برومبت القياسية (`25 Master + 6 Extended V52–V55`):**
   - تحليل صوتي ومقامي وإيقاعي وهيكلي شامل لـ **`175` لطمية** عبر 9 مدارس كبرى (`School 01–09`) مع دعم 3 قصائد مرجعية معيارية بنسبة تشكيل وعزل لهجي `100%` (`طبع البشر`، `صورة جسد عالغبرة`، و`فلسفة الانتظار`).
4. **قانون الـ 80 ثانية والمقطع الواحد لكل `Extend` (`Module 60 — QC30`):**
   - تقييد كل عملية تمديد (`Remix > Extend`) بـ **مقطع شعري واحد فقط** بحد أقصى **`7` أبيات (`14` شطراً عمودياً)**.
5. **هندسة المستهل المزدوج ومنع استنساخ الجوقة على النزلة (`Module 61 — QC31`):**
   - تقييد أي بلوك `[المُسْتَهَلّ]` بحد أقصى **`4` أشطر متتالية بين قوسين `(...)`** وعدم تكرار نفس شطر المستهل مكشوفاً ثم بين قوسين في الافتتاح (`NC22`).
6. **حظر السطر اليتيم ذي الكلمة الواحدة والألف الوقائية الانتقائية (`Modules 62 & 63 — QC32, QC33, QC34`):**
   - منع وضع كلمة مفردة في سطر عمودي منفصل، وقصر الألف الوقائية المكسورة `إِ` على العناقيد العراقية الساكنة الحقيقية مع منع `إِبْأ` قبل الهمزة (`QC34`: `بِأَرْضِ`).
7. **حزمة `Stage JSON` ذات الـ 7 مفاتيح وترقيم الكسرات (`Modules 53, 57 & 59 — QC19, QC27, QC29`):**
   - إلزامية المفتاح السابع **`lyrics_register_verbatim`** في كل مرحلة لتمريره حرفياً إلى `lyrics__register`، وترقيم وسوم الكسرة تصاعدياً.

---

## أولاً: طريقة التثبيت والتفعيل (`Installation & Setup`)

```bash
npx skills add husainalmualif/hussaini-production-studio
```
أو بنسخ المستودع مباشرة إلى مسار المهارات:
- **Windows:** `C:\Users\<Username>\.gemini\config\skills\hussaini-production-studio`
- **macOS / Linux:** `~/.gemini/config/skills/hussaini-production-studio`

---

## ثانياً: سير العمل التطبيقي في `Flow Music` والمحرك المحلي (`V55.0 OMNI-ARCHITECT`)

### 1. التوليد المتقن في `https://www.flowmusic.app/` عبر `Lyria 3.5` (`Modules 39, 49–70`)
1. **افتح جلسة جديدة مستقلة (`New session` — `a[href="/session"]`)** لكل قصيدة جديدة وتأكد في `Compose > Advanced` أن الموديل هو **`Lyria 3.5`** (`NC19`).
2. **الطريقة الأولى الموصى بها (`Method 1 — Compose > Lyrics` مباشرة):**
   - انتقل إلى لوحة **`Compose > Lyrics`**، والصق وصف `Sound` الموثق (`ashura_majlis_noha_58bpm_saba_lami_v55` أو `pure_acapella_weeping_noha_auto_bpm_saba_lami_v55`) في خانة `Sound`، والصق النص العربي المشكول الصافي في خانة `Lyrics`.
3. **الطريقة الثانية (`Method 2 — Stage & Section JSON` في `Producer Chat`):**
   - أرسل كائن التهيئة المسبقة متبوعاً مباشرة بحزمة `Stage 1 JSON` (يُحظر إرسال كائن التهيئة منفرداً دون القصيدة منعاً لتوليد أغنية عشوائية — `NC19`).
4. **التمديد أو التغطية وفصل المسارات (`Remix > Extend / Cover <= 0.45` + `Split stems`):**
   - عند استخدام `Remix > Cover` اضبط `Strength <= 0.45` (`NC20`)، واستخدم `Split stems` لعزل `Vocals` قبل المونتاج المحلي ذي الـ 5 مسارات.

### 2. الأوامر البرمجية والطرفية (`CLI & Python API — V55.0 OMNI-ARCHITECT`)

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# 1) ترجمة وتشكيل النص الشعري وبناء حزمة Stage JSON ذات الـ 7 مفاتيح (Modules 53, 59–70 — QC19, QC29–QC35, NC18–NC22)
python3 scripts/hussaini_dsp_montage.py --compile-lyrics "طبع البشر ينسه الوفه بس انته مو مثل البشر"
python3 scripts/hussaini_dsp_montage.py --build-stage-json "[المُسْتَهَلّ]\n(طَبْعِ البَشَرْ يِنْسَى الوَفَا .. بَسْ إِنْتَ مُو مِثِلِ البَشَرْ) .."

# 2) فحص القصيدة الشامل عبر بوابات الجودة الـ 35 (QC1–QC35)
python3 scripts/hussaini_dsp_montage.py --lint-poem "[المُسْتَهَلّ]\n(طَبْعِ البَشَرْ يِنْسَى الوَفَا .. بَسْ إِنْتَ مُو مِثِلِ البَشَرْ) .."

# 3) استعراض خطة المراحل والتحليل الخماسي وتصدير دستور V55.0 OMNI-ARCHITECT
python3 scripts/hussaini_dsp_montage.py --recommend-tor "طبع البشر ينسه الوفه بس انته مو مثل البشر"
python3 scripts/hussaini_dsp_montage.py --stage-plan iraqi
python3 scripts/hussaini_dsp_montage.py --verify-history "صوت أم البنين يصيح يبن حذلم"
python3 scripts/hussaini_dsp_montage.py --plan-stages "[المُسْتَهَلّ]\nصوت أم البنين يصيح يبن حذلم\n[الكوبليه الأول]\nيا ناشد على الطف وعندك علم"
python3 scripts/hussaini_dsp_montage.py --export-constitution

# 4) المونتاج الصوتي ذو الـ 18 وضعاً وماسترنغ EBU R128 (-14.0 LUFS / -1.0 dBTP) + فحص --audit-audio
python3 scripts/hussaini_dsp_montage.py \
  --input "split_vocals.wav" \
  --output "mastered_heavy_clip.wav" \
  --mode "thaqeel_muwazza" \
  --bpm 58 \
  --maqam-drone "saba_zamzam" \
  --replace-ai-percussion \
  --fade-out-sec 3.0

# 5) فحص جودة الكود (Pylint 10/10) وتشغيل اختبارات الوحدات الشاملة (Pytest >= 75% Coverage)
pylint --disable=C0301,R0912,R0913,R0914,R0915,R0917 scripts/hussaini_dsp_montage.py tests/test_hussaini_modules.py
pytest -v --cov=scripts --cov-fail-under=75 tests/test_hussaini_modules.py
```

---

## ثالثاً: هيكل ملفات المهارة وبيئة الفحص الآلي (`Repository Structure — 30 Canonical Files`)

```text
hussaini-production-studio/
├── VERSION                                                                  # مصدر الحقيقة الموحد للإصدار (V55.0 OMNI-ARCHITECT)
├── SKILL.md                                                                 # الموجّه المهيكل الرشيق (<= 10.5KB Router)
├── README.md                                                                # الدليل الشامل للاستخدام والمرجع السريع
├── requirements.txt                                                         # المتطلبات البرمجية الخفيفة (numpy, scipy, pylint, pytest, pytest-cov)
├── references/
│   ├── hussaini_os_v50_0_constitution.json                                  # الدستور التجريبي الموحّد لـ V55.0 OMNI-ARCHITECT (9 Schools, 31 Prompts, QC1–QC35, NC1–NC22)
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
│       ├── module_68_v53_dual_corpus_flow_bahrani_iraqi_mastery.md           # بروتوكول V53.0: تدقيق الكوربوسين، تجارب Flow البحرانية والعراقية، QC34، و 11 قاعدة مقاتل
│       ├── module_69_v54_175_mp3_acoustic_lab_24edo_and_studio_dsp.md        # بروتوكول V54.0: مختبر 175 MP3، De-Esser، Optical RMS، Stereo Dome، و 24-EDO النسبي/Rubato
│       └── module_70_v55_tabaa_al_bashar_7exp_lab_5stage_router_and_3poem_benchmark.md # بروتوكول V55.0: تجارب طبع البشر الـ 7 (NC18–NC22)، الموجه الخماسي، ومعيار القصائد الثلاث
├── scripts/
│   └── hussaini_dsp_montage.py                                              # المحرك المستقل للنطق الصوتي والـ 18-Mode Pure-Vocal / 5-Track DSP (EBU R128)
├── tests/
│   └── test_hussaini_modules.py                                             # اختبارات الوحدات الشاملة لـ Modules 34–70 وQC1–QC35 وNC1–NC22 والـ DSP
└── .github/
    └── workflows/
        └── ci.yml                                                           # فحص GitHub Actions CI عبر Python 3.10, 3.11, 3.12
```
