# هندسة الإنتاج الاستوديوي الحديث، المحاكاة الصوتية البشرية (`Rosenberg Formant Ahaat`)، والكليبات الثقيلة (`Module 44 & 50`) — V48.5 OMNI-ARCHITECT

يوثق هذا المرجع المعماري المستويات الثلاثة لإنتاج اللطمية الحسينية من الأداء المنبري الأصيل إلى **الكليبات الاستوديوية الثقيلة (`Heavy Studio Clips 60–75 BPM`)**، والعمق ثلاثي الأبعاد (`3D Soundstage`)، والمؤثرات البيئية (`Foley`)، والانقطاع الدرامي (`Audio Drop`)، مع تطبيق جدار الحماية الصارم في `Module 50` بين ما يُكتب في `Flow Music` وما يُولَّد محلياً في محرك `scripts/hussaini_dsp_montage.py`.

---

## أولاً: مستويات التوزيع الصوتي والبدائل البشرية (`The 3 Studio Production Tiers`)

### 1. المستوى الأول: العزاء التراثي المحافظ (`Tier 1 — Pure Heritage Acapella`)
- **في المنتصف (`Center 0%`):** صوت رادود باريتون جوهري رخيم (`Commanding Deep Resonant Jawhari Baritone`) جاف وقريب مع صدى شريطي مضبوط الإيقاع (`285ms Tape Echo`).
- **في الأطراف (`Wide Stereo L/R`):** لطم صدري بشري متراكب (`55Hz Bare-Palm Chest Thud`) + جمهور الردّادة الموحد (`Wide Unison Male Raddada Choir`) داخل قبة حسينية (`3.2s Hall Reverb`).

### 2. المستوى الثاني: الآهات البلعومية الفورمانتية المحافظة (`Tier 2 — Local Rosenberg + Formant Vocal Synth`)
- **تحذير تجريبي صارم (`Module 50 — QC4 & QC16`):** يُحظر قطعيّاً كتابة `strings`، `synth`، `humming`، `pads`، أو `wordless pharyngeal Ahaat vocal drone` داخل حقل `Sound` في `Flow Music` لأنها تحول العمل إلى ترنيمة غربية (`12-TET`).
- **التوليد المحلي النقي:** تُولَّد طبقة الآهات البشرية محلياً داخل `scripts/hussaini_dsp_montage.py` عبر دالة `synthesize_ahaat_drone` و`synthesize_vocal_synth_strings_pad` باستخدام النبضة الحنجرية **`Rosenberg Pulse (Tp=0.40, Tn=0.16) + 3% Breath Noise`** ورنانات الفورمانت **`F1=730Hz, F2=1090Hz, F3=2440Hz`** مع تباين كورالي **`[-4, 0, +4] cents`** وخفض جانبي **`-3.0 dB Sidechain Ducking`**.

### 3. المستوى الثالث: الكليبات الاستوديوية الثقيلة (`Tier 3 — Heavy Studio Clips 60–75 BPM`)
تُنفَّذ في مونتاج المسارات الخمسة (`--mode heavy_clip` ومع `--replace-ai-percussion` عند الحاجة):
1. **الضربة المزدوجة + همهمة القرار البشرية:** دمج ضربة الصدر العميقة (`54Hz`) + صفعة الكف (`1.8–3.2kHz`) + نبضة همهمة قرار بشرية متزامنة (`44Hz Human Sub-Bass Hum`).
2. **تنظيف مسار الرادود واستبدال إيقاع الذكاء الاصطناعي (`--replace-ai-percussion`):**
   - تطبيق فلتر `4th-order SOS HPF @ 120Hz` + كاشف العابرات السريع/البطيء (`Fast/Slow RMS Transient De-Clicker, ratio > 1.85`) + `LPF @ 4500Hz` لتجريد صوت الرادود من أي إيقاع آلي مشوّه قبل بناء اللطم البشري المتعدد الطبقات تحته.
3. **المؤثرات البيئية (`--foley <none|wind|water|horses>`) والانقطاع الدرامي (`--audio-drop-sec <sec>`):**
   - رياح الصحراء (`wind`)، جريان الماء (`water`)، وصهيل/عدو الخيل البعيد (`horses`)، مع خفض الخلفية لمدة `3.0s` لإبراز صوت الرادود منفرداً في بيت الذروة.

---

## ثانياً: قاعدة الكسر العمودي للأسطر الطويلة (`Vertical Short-Line Splitting`) وقالب `Sound` القياسي

- يخصص نموذج `Lyria` لكل سطر (`\n`) دورةً إيقاعية واحدة؛ لذا تُقسم الأبيات الطويلة عمودياً عبر `split_long_lines_for_steady_pacing` إلى أشطر قصيرة (`3–4 كلمات / 6–8 مقاطع`) منتهية بـ `..`.
- **قالب `Sound` المعتمد في `Flow Music` قبل الماسترنغ المحلي للكليبات الثقيلة (`60 BPM — Zero 12-TET Drift`):**
```text
Traditional Iraqi Hussaini Latmiya, heavy Karbalai Nazla style, Maqam Bayati and Saba, 60 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, passionate microtonal melisma, heavy 55Hz bare-palm chest thud, 285ms tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada response, Pure Acapella No Instruments
```
