# استوديو الإنتاج الحسيني الشامل — Hussaini Production Studio (V48.5 OMNI-ARCHITECT (Rev 2))

منظومة هندسية متكاملة ومثبتة تجريبياً للتأليف الشعري الحسيني، وهندسة المقامات الميكروتونالية (`24-EDO`) والأطوار المنبرية والموكبية، وتوليد اللطميات والنواعي بالذكاء الاصطناعي (**Google Flow Music / Lyria 3.5, Suno, Udio**) بدقة نطق وأداء تقارب 100% عبر **الدستور التجريبي الموحّد (`references/hussaini_os_v48_5_constitution.json`)**، و**بروتوكول حزم `JSON` الإلزامية لكل مرحلة ولكل قسم شعري (`Module 53 — QC19`)**، و**مُترجم عزل اللهجة الواحدة والألف الوقائية العراقية وحروف اللين المفتوحة (`Modules 40, 41, 43, 45 & 49`)**، و**جدار عزل البكاء في النعي الحر (`0 BPM`) ومنع انهيار المقام الغربي (`Module 50`)**، و**بروتوكول التوجيه ثنائي القناة والمستهل الجماعي الموحّد `(...)` (`Modules 39 & 51`)**، و**التدرج المقامي الديناميكي ذي الـ 4 مراحل ومكتبة الـ 16 برومبت القياسية (`Module 52`)**، مع **محرك المونتاج الصوتي ذي الـ 16 وضعاً والمسارات الخمسة (`scripts/hussaini_dsp_montage.py` — `--replace-ai-percussion`, `Rosenberg + Formant Ahaat`, `-28 dBFS RMS Ducking`, `-14.0 LUFS` & `-1.0 dBTP`)**.

---

## أبرز ركائز الإصدار `V48.5 OMNI-ARCHITECT (Rev 2)` (خلاصة التجارب العملية الدقيقة)

1. **إلزامية حزم `JSON` لكل مرحلة ولكل قسم شعري (`Module 53 — QC19`):**
   - حظر إخراج مقاطع القصيدة كنص عادي مجرّد (`Bare Plain-Text Stanzas`) بدون تغليفها الكامل داخل حزمة `Stage JSON` (`6` مفاتيح إلزامية) وحزمة `Section JSON` (`10` مفاتيح إلزامية) عبر `--build-stage-json` في `Producer Chat`، مع الحفاظ على نظافة مصفوفة `lyrics_arabic` عربيةً خالصةً 100%.
2. **عزل المجرى الصوتي للهجة الواحدة والألف الوقائية العراقية (`Module 49 — QC9, QC13, QC14`):**
   - منع خلط حركات الفصحى (`عُيُونِي / حُسَيْن / مُطِّينِي / عَلَى`) مع القصيدة الشعبية، وإعلان اللهجة الفعلية فقط في `Sound` (`authentic Iraqi colloquial dialect` أو `authentic Bahrani colloquial dialect`).
   - **العناقيد السهلة** تأخذ حركة دارجة ناعمة بدون همزة قطع (`دُمُوعْ، جُرُوحْ، مِتُونِي، سِنِينِي، سِكِينَه، تِگِلَّه، تِسُولِفْ، هُمُومْ`).
   - **العناقيد العراقية الشفوية والحلقية والطبقية** تُقفل وجوباً بـ **`إِCْ`**: **`إِبْچَفَّكْ`، `إِعْيُونِي`، `إِعْيُونَكْ`، `إِحْسَينْ`، `إِبْمَجْلِسَكْ`، `إِبْگَلْبِي`، `إِبْگَاعْ`، `إِخْيَامْ`، `إِبْهِدَايْ`، `إِبْعِفَّه`، `إِعْلَه`** (مقابل `عَلَه` في البحرانية).
   - **اختزال الأسماء المؤنثة وتاء الإضافة وحروف اللين غير المسكّنة:** `العَافْيَه، حَافْيَه، فَاتْحَه`؛ `وِسَادَتْ رِيشْ، دِنْيَتْ خَيرْ`؛ ترك حروف اللين الوسطية بدون سكون لمنع بتر المدّات (**`إِحْسَينْ، خَيرْ، زَينْ، وَينْ، بَينْ، زَينَبْ`**)، وفتح هاء التأنيث دائماً بدون سكون (**`غَرِيبَه هَلْ حِچَايَه`**).
3. **عزل البكاء في النعي الحر `0 BPM` وجدار الـ 36 مصطلحاً ضد الانهيار الغربي (`Module 50 — QC4, QC15, QC16`):**
   - حظر مطلق لكلمات البكاء (`emotional weep cracks, weeping, sobbing, tear-choked, majlis cries`) في جميع اللطميات الإيقاعية (`54–132 BPM`) حتى لا تنشأ ضوضاء خلفية تطمس مخارج حروف الرادود؛ وتقييد الكسرات البكائية **حصرياً** في جلسات النعي المنبري الحر (`0 BPM Rubato Minbar Na'i`) على أواخر العبارات قبل `..`.
   - حظر `legato phrasing` و`calm / serene` و`wordless pharyngeal Ahaat vocal drone` في حقل `Sound` بـ `Flow Music`، وتوليد طبقة الآهات البشرية محلياً عبر `Rosenberg Glottal Pulse + Formants (730/1090/2440Hz)`.
4. **التوجيه ثنائي القناة وإلزامية المستهل الجماعي الموحّد `(...)` (`Module 51 — QC17, QC18`):**
   - إرسال دستور `JSON` وحزم المراحل في `Producer Chat` حصراً، وعند استخدام لوحة `Compose` يدوياً يُلصق النص العربي المشكول النقي فقط في `Lyrics` (صفر أقواس `{...}` وصفر حروف إنجليزية).
   - إحاطة **جميع أشطر `[المُسْتَهَلّ]` الأربعة** بقوسين `(...)` قبل `..` ليؤديها جمهور الردّادة الموحد بنسبة 100%، مع ترك أشطر `[النَّزْلَة]` وأشطر «الكسرة» الفردية الأربعة بدون أقواس.
5. **التدرج المقامي الديناميكي ذو الـ 4 مراحل ومكتبة الـ 16 برومبت القياسية (`Module 52 — QC1`):**
   - النطاق الذهبي للثقيل **`58–60 BPM`** (منع الهبوط تحت `55 BPM`)، والتمديد عبر `Remix > Extend` وفق مسار الأجناس المشتركة:
     - `Stage 0` (`0 BPM` Saba Intro مستقل) ⟵ `Stage 1` (`58–60 BPM` Saba Zamzam / Bayati & Saba) ⟵ `Stage 2` (`58 BPM` Lami & Saba Rukbani) ⟵ `Stage 3` (`58 BPM` Saba Zamzam & Hijaz Ashouri Climax) ⟵ `Stage 4` (`56 BPM` Wahsha Lami & Saba Kasra).
6. **محرك الـ 16 وضعاً للمونتاج الصوتي وفصل إيقاع الذكاء الاصطناعي (`Modules 44 & 46`):**
   - يدعم `16` وضعاً إيقاعياً وموكبياً (`latm, heavy_clip, thaqeel_muwazza, studio_arranged, bahrani_fast, bahrani_thulathi, bahrani_rubai, bahrani_haidari, bahrani_waqfa, bahrani_muthakkal, zanjeel_iraqi, zanjeel_bahrani, shoor, bandari, mawal, nai`) و`9` مقامات (`bayati, saba, saba_zamzam, hijaz, lami, kurd, rast, nahawand, sikah`)، مع `--extract-profile` و`--replace-ai-percussion` (`4th-order SOS HPF @ 120Hz + Fast/Slow RMS De-Clicker ratio > 1.85 + LPF @ 4500Hz`).

---

## أولاً: طريقة التثبيت والتفعيل (`Installation & Setup`)

```bash
npx skills add husainalmualif/hussaini-production-studio
```
أو بنسخ المستودع مباشرة إلى مسار المهارات:
- **Windows:** `C:\Users\<Username>\.gemini\config\skills\hussaini-production-studio`
- **macOS / Linux:** `~/.gemini/config/skills/hussaini-production-studio`

---

## ثانياً: سير العمل التطبيقي في `Flow Music` والمحرك المحلي

### 1. التوليد المتقن في `https://www.flowmusic.app/` عبر القناتين وحزم `Stage JSON` (`Modules 39, 49–53`)
1. **افتح جلسة جديدة مستقلة (`New session` — `a[href="/session"]`)** لكل قصيدة جديدة.
2. **القناة الأولى (`Producer Chat`):** أرسل محتوى الدستور المرجعي `references/hussaini_os_v48_5_constitution.json` وانتظر تأكيد القفل، ثم أرسل حزمة `Stage 1 JSON` الكاملة (`--build-stage-json` — `Module 53`).
3. **القناة الثانية (`Compose Panel` — عند الاستخدام اليدوي البديل):**
   - **`Lyrics`:** نص عربي مشكول نقي بـ 20 سطراً عمودياً (`[المُسْتَهَلّ]` 4 أشطر بين `(...)` + `[النَّزْلَة الأُولَى]` 8 أشطر بدون أقواس + `[الكَسْرَة وَالمُسْتَهَلّ]` 4 أشطر فردية + 4 أشطر مستهل بين `(...)`).
   - **`Sound` (`Stage 1 — 58 BPM Saba Zamzam`):**
     ```text
     Mournful Traditional Iraqi Hussaini Latmiya, heavy Karbalai Muthakkal and Nazla style, Maqam Saba Zamzam and Bayati, 58 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, passionate microtonal melisma, heavy 55Hz bare-palm chest thud, 310ms tape echo, 3.5s Husseiniya reverb, wide unison male Raddada response, Pure Acapella No Instruments
     ```
4. **التمديد عبر المراحل (`Remix > Extend`):** انتقل في `Stage 2` إلى `rukbani_nassari_58bpm_lami_saba_v48_5_stage2`، وفي `Stage 3` إلى `karbalai_ashouri_jawab_climax_58bpm_saba_zamzam_hijaz_v48_5_stage3`، وفي `Stage 4` إلى `karbalai_wahsha_lami_kasra_56bpm_finale_v48_5_stage4`.
5. **المعالجة اللاحقة (`audio__apply_effect`):**
   ```text
   Apply audio__apply_effect on the generated clip: HighPass filter at 85Hz, AdvancedEqualizer (cut 450Hz by -2.5dB, boost mid 1200Hz by +1.5dB, boost high-mid presence 2500Hz by +4.5dB), Compressor (ratio 3:1, threshold -12dB), Reverb (room_size 0.55, wet mix 0.18), and Limiter at -1.0dB.
   ```

### 2. الأوامر البرمجية والطرفية (`CLI & Python API — V48.5 OMNI-ARCHITECT (Rev 2)`)

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# 1) ترجمة وتشكيل النص الشعري وبناء حزمة Stage JSON الإلزامية (Module 53 — QC19)
python3 scripts/hussaini_dsp_montage.py --compile-lyrics "ياحسين بچفك عيوني عالباب وسادة ريش والعافية"
python3 scripts/hussaini_dsp_montage.py --build-stage-json "[المُسْتَهَلّ]\n(غَرِيبَه هَلْ حِچَايَه) ..\n[النَّزْلَة الأُولَى]\nوُگَفِتْ إِعْلَه البَابْ .."

# 2) فحص القصيدة الشامل عبر بوابات الجودة (QC1–QC19) وتطبيق قفل المستهل الجماعي (...)
python3 scripts/hussaini_dsp_montage.py --lint-poem "[المُسْتَهَلّ]\n(غَرِيبَه هَلْ حِچَايَه) ..\n(سَبِيَّه مِنِ السَّبَايَا) ..\n(كِتَلْهَا رَاسْ أَبُوهَا) ..\n(إِبْخَرَابَه شَيِّعُوهَا) .."

# 3) استعراض خطة المراحل الأربع (Stage 0–4) وتصدير دستور V48.5 (Rev 2)
python3 scripts/hussaini_dsp_montage.py --stage-plan iraqi
python3 scripts/hussaini_dsp_montage.py --export-constitution

# 4) التحقق من الأبوذية العراقية والموال الزهيري واقتراح الطور والهندسة العكسية للملفات الصوتية
python3 scripts/hussaini_dsp_montage.py --validate-abudhiyah "گلبي بمأتمك يحسين ينصاب ..\nوذكرك من يمر الدمع ينصاب ..\nگلبي بدال گلبك ريت ينصاب ..\nوخدي دون خدك على الوطيه .."
python3 scripts/hussaini_dsp_montage.py --recommend-tor "هنيالي من خدمنك .. خادم وافتخر مولاي"
python3 scripts/hussaini_dsp_montage.py --extract-profile "reference_latmiya.wav"

# 5) المونتاج الصوتي ذو الـ 5 مسارات والـ 16 وضعاً مع تنظيف الإيقاع الآلي (--replace-ai-percussion) وماسترنغ -14 LUFS
python3 scripts/hussaini_dsp_montage.py \
  --input "split_vocals.wav" \
  --output "mastered_heavy_clip.wav" \
  --mode "heavy_clip" \
  --bpm 58 \
  --maqam-drone "saba_zamzam" \
  --replace-ai-percussion \
  --foley "wind" \
  --audio-drop-sec 12.0

# 6) فحص جودة الكود (Pylint) وتشغيل اختبارات الوحدات الشاملة (Pytest >= 75% Coverage)
pylint --disable=C0301,R0912,R0913,R0914,R0915,R0917 scripts/hussaini_dsp_montage.py tests/test_hussaini_modules.py
pytest -v --cov=scripts --cov-fail-under=75 tests/test_hussaini_modules.py
```

---

## ثالثاً: هيكل ملفات المهارة وبيئة الفحص الآلي (`Repository Structure — 24 Canonical Files`)

```text
hussaini-production-studio/
├── VERSION                                                                  # مصدر الحقيقة الموحد للإصدار (V48.5 OMNI-ARCHITECT (Rev 2))
├── SKILL.md                                                                 # الموجّه المهيكل الرشيق (<= 10.5KB Router)
├── README.md                                                                # الدليل الشامل للاستخدام والمرجع السريع
├── requirements.txt                                                         # المتطلبات البرمجية الخفيفة (numpy, scipy, pylint, pytest, pytest-cov)
├── references/
│   ├── hussaini_os_v48_5_constitution.json                                  # الدستور التجريبي الكامل لـ V48.5 Rev 2 (JSON Constitution)
│   ├── atwar_maqamat_and_poetry_guide.md                                    # الموسوعة المرجعية الشاملة للأطوار والمقامات والعروض (Sections 1–19)
│   ├── radoods_and_khutaba_encyclopedia.md                                  # موسوعة 20+ رادوداً (14 مدرسة) و8 من خطباء المنبر
│   └── modules/
│       ├── experimental_ab_evaluation_and_human_review.md                   # مصفوفة التقييم التجريبي (E1–E13) وبوابة المراجعة الشرعية والأدبية
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
│       ├── module_52_dynamic_4stage_maqam_progression_and_master_prompts.md # التدرج المقامي الرباعي، 16 برومبت قياسي، ومصفوفة QC1–QC19
│       └── module_53_per_stage_and_section_json_orchestration.md            # إلزامية حزم Stage/Section JSON ومنع النص المجرّد (QC19)
├── scripts/
│   └── hussaini_dsp_montage.py                                              # المحرك المستقل للنطق الصوتي والـ 16-Mode 5-Track DSP (Pylint 10/10)
├── tests/
│   └── test_hussaini_modules.py                                             # اختبارات الوحدات الشاملة لـ Modules 34–53 وQC1–QC19 والـ DSP
└── .github/
    └── workflows/
        └── ci.yml                                                           # فحص GitHub Actions CI عبر Python 3.10, 3.11, 3.12
```
