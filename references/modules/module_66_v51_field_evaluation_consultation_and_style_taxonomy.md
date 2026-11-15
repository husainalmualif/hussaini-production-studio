# Module 66: V51.0 Field Evaluation, Negative Constraints (NC1–NC10), Pre-Generation Consultation Protocol, Dialect Isolation, and Style Taxonomy

## 1. Empirical Root-Cause Analysis & Permanent Negative Constraints (`NC1–NC10`)

Derived from forensic second-by-second multimodal auditing of the 4 raw Stage-1 outputs (`Compose > Lyrics\Untitled.mp3`, `Compose > Lyrics\Untitled (1).mp3`, `JSON\صُوتْ أُمّ البَنِينْ يِصِيحْ — المرحلة 1 التأسيسية.mp3`, `JSON\صُوتْ أُمّ البَنِينْ يِصِيحْ — المرحلة 1 التأسيسية (1).mp3`):

- **`NC1` (The Instrument-Name Trigger Trap — حظر ذكر أسماء الآلات الموسيقية في Prompts/JSON):**
  - *Failure Observed:* In `Untitled.mp3` (`00:00–00:18`, `02:02–02:41`) and `JSON (1).mp3` (`00:00–00:18`, `01:44–02:27`), mentioning `"Violin, Cello, Ney"` inside the Pre-Conditioning JSON (even under `"allowed_instruments_with_caution: use as pad only"`) and omitting `"Pure Acapella No Instruments"` caused `Lyria 3.5` to generate 18s–44s **tarab solo Ney, Oud, Guitar, Piano, and Western Drum-Kit sections**!
  - *Permanent Constraint:* NEVER include the words `Ney`, `Flute`, `Oud`, `Guitar`, `Violin`, `Cello`, `Piano`, `Clarinet`, or `Drum Kit` anywhere in a `Lyria 3.5` Sound prompt or Pre-Conditioning JSON unless the user explicitly requests an instrumental piece. In **Traditional / Vocal-Symphony Style**, always lock `"Pure Acapella No Instruments, 100% Human Vocal Symphony & Chest Matam Only"`. In **Modern Solemn Style**, lock `"Subtle Dark Low-Frequency Sub-Bass Drone & Warm Vocal Pad Texture Only — Strictly No Solo Melodic Instruments, No Oud, No Ney, No Flute, No Guitar, No Drum Kit"`.

- **`NC2` (Root Stage Duration vs. Lyric Density Mismatch — حظر وضع مقطع قصير واحد في مرحلة التأسيس `150s` دون ضبط الكثافة):**
  - *Failure Observed:* `Lyria 3.5` generates a `135s–170s` (`2:15–2:50`) audio file on initial Root generation (`Stage 1`). Feeding only `11` lines (`~65s` of singing) left `70s–100s` of empty duration, forcing the model either to improvise 40-second instrumental solos (`Untitled.mp3`, `JSON (1).mp3`) or to loop `[المُسْتَهَلّ]` 3 times in a row with vocal collisions and mid-word cutoffs (`Untitled (1).mp3` `01:23–02:31`, `JSON.mp3` `01:32–02:17`).
  - *Permanent Constraint:* In `Stage 1 Root`, either: (a) supply **Stanza 1 + Stanza 2 (`~130–145s` of lyrics)** to fill the natural `2:20` root generation window without looping or solo filler, OR (b) when generating Stanza 1 alone as a `~68s` root test, immediately apply **`Remix > Trim` at the exact end of the first post-stanza `[المُسْتَهَلّ]` (`~01:15–01:25`)** to discard any trailing loop/filler before evaluating or extending.

- **`NC3` (Southern Iraqi `انجسم` vs. Fusha Noun `الجسم` — حظر رسم «انجسم» بالجيم):**
  - *Failure Observed:* Writing `تَرَى گَلْبِي انْجِسَمْ نُصَّيْنْ` with `ج` caused `Lyria 3.5`'s tokenizer to misread `انجسم` as the Fusha noun `الجِسِمْ` (`the body`) in `Untitled (1).mp3` (`01:01`: `گَلْبُ الجِسِمْ الصِّينْ`) and `JSON.mp3` (`00:58`: `گَلْبِي الجِسَمْ نُصَّيْنْ`), or rewrite it to Fusha `انْقَسَمْ نَصِّينْ` (`JSON (1).mp3` `01:24`).
  - *Permanent Constraint:* Write Iraqi reflexes of `ق` (`انقسم`) with Iraqi Gaf `گ` (`انْگِسَمْ نُصَّينْ`), never `انجسم`, so G2P maps it to `/ɪn.gɪ.sam/` and never to `الجِسْم` (`body`).

- **`NC4` (Iraqi First/Second Person `رِدِتْ` vs. Fusha `رَدَّتْ` / Stretched `رِدِيتْ`):**
  - *Failure Observed:* `رِدِتْ نَشْدَه` was read as Fusha 3rd-person feminine `رَدَّتْ نِشْدَه` (`/rad.dat/`) in `Untitled (1).mp3` (`00:05`, `00:54`) and stretched into `رِدِيتْ` / `رِيدِتْ` in `Untitled.mp3` (`00:26`) and `JSON.mp3` (`00:06`).
  - *Permanent Constraint:* Write **`رِدَتْ نَشْدَه`** (with Kasra on Raa `رِ`, Fatha on un-geminated Dal `دَ`, and Sukun on Taa `تْ` — `/rɪ.dat naʃ.da/`), which prevented both `رَدَّتْ` and `رِيدِتْ` in `JSON (1).mp3` (`00:25`).

- **`NC5` (Vowel Coalescence Across `ـه + أُمّ` and `صُوتْ + أُمّ`):**
  - *Failure Observed:* `صُوتْ أُمّ` coalesced into `صُوتُومَ` (`JSON.mp3` `00:01`), and `إِجَتَه أُمّ` coalesced into `إِجَتَهُمْ` (`JSON.mp3` `00:39`).
  - *Permanent Constraint:* Place explicit Shadda+Kasra on `أُمِّ` (`صَوْتْ أُمِّ البَنِينْ يِصِيحْ`) and separate `إِجَتَه` from `أُمِّ` with a micro-pause or write **`إِجَتْ أُمُّ الگَمَرْ وَتْصِيحْ`** (with Fatha on Gaf `الگَمَرْ` to prevent `الگِمَارْ` / `الگُمُرْ`, and unvoiced `وَتْصِيحْ` with explicit Sukun on Taa).

- **`NC6` (Masculine Clitic `لِدْيَارَه` Stretched to Feminine `لِدْيَارَهَا`):**
  - *Failure Observed:* `رَدْ لِدْيَارَه لَوْ بَعْدَه` was sung as `رَدْ لِدْيَارَهَا` in `Untitled.mp3` (`00:38`) and `JSON.mp3` (`00:13`).
  - *Permanent Constraint:* Lock terminal Sukun on masculine `ـهْ` when followed by `لَوْ`: **`رَدْ لِدْيَارَهْ لَوْ بَعْدَهْ`**.

- **`NC7` (Prosthetic/Wasl Alif in `إِبِنْ حَذْلَمْ`):**
  - *Failure Observed:* Deleting Alif (`رَدْ بِنْ حَذْلَمْ`) caused assimilation `رَدِّنْ حَذْلَمْ` (`Untitled.mp3` `00:46`), while unvocalized `ابِنْ` caused `أَبِنْ` (`V50.1`).
  - *Permanent Constraint:* Always write explicit Hamzat Qat'/Wasl with Kasra: **`لَمَّنْ رَدْ إِبِنْ حَذْلَمْ`** (with Fatha on `لَمَّنْ` and Fatha on `حَذْلَمْ`).

- **`NC8` (Preventing Verb Misparse on `يَثْرِبْ` and `أَنْشِدَكْ`):**
  - *Failure Observed:* `يَثْرِبْ` was read as `يِثْرُبْ / يِثْرِي / يِثْرُوبْ` (`Untitled 1`, `JSON 1`), and `أَنْشِدَكْ` was read as `إِنْ شَدَّكْ` (`Untitled 1`) or `نِشْدَكْ` (`JSON 1`).
  - *Permanent Constraint:* Write **`يَا أَهْلَ يَثْرِبْ`** (or lock `يَثْرِبْ` with Fatha on Yaa, Sukun on Thaa, Kasra on Raa, Sukun on Baa) and **`أَنْشِدَكْ`** with explicit Fatha-Sukun-Kasra-Fatha-Sukun (`/ʔan.ʃɪ.dak/`, never Shadda on Dal).

- **`NC9` (Banning Uncontrolled High-Octave Screaming in Kasras):**
  - *Failure Observed:* In `Untitled.mp3` (`01:21–01:47`) and `Untitled (1).mp3` (`01:17`), the singer jumped into strained high-octave screaming (`آاااه`).
  - *Permanent Constraint:* Always specify `"controlled dignified middle-register baritone delivery, strictly no high-pitched screaming or operatic shouting"`.

- **`NC10` (Strict Dialect Isolation — حظر خلط الإعراب الفصيح بالدارجة):**
  - *Failure Observed:* In `Untitled.mp3` (`00:18`, `01:07`), Fusha case vowels (`صُوتُ أُمَّ البَنِينِ`, `مَقَامَ اليَوْمْ`) were mixed with Iraqi colloquial words.
  - *Permanent Constraint:* Never place Fusha case endings (`ضمة/فتحة/كسرة إعرابية` at word boundaries) on Iraqi or Bahrani colloquial verses; lock `تسكين أواخر الكلمات الدارجة` (`Sukun on colloquial word endings`).

- **`NC11` (Unique Numbered Estehlal Tags in JSON — ترقيم وسوم المستهل في JSON):**
  - *Failure Observed:* In `JSON — المرحلة 1 التأسيسية.mp3`, having two sections with identical `"section_tag": "[المُسْتَهَلّ]"` caused `Producer Chat` to skip the opening `[المُسْتَهَلّ]` at `00:00` and sing it twice at the end (`01:16` and `01:44`).
  - *Permanent Constraint:* Always use distinct numbered tags (`[المُسْتَهَلّ الأَوَّل]` and `[المُسْتَهَلّ الثَّانِي]`) inside JSON `sections[]`.

- **`NC12–NC15` (Micro-Melismatic & Liaison Locks):**
  - Lock `إِجَتْ أُمُّ الگَمَرْ` or pause `إِجَتَه .. أُمُّ الگَمَرْ` to prevent `/h/ + /ʔum/ -> /hum/` coalescence; write `إِبْنْ حَذْلَمْ` with Sukun on Baa to prevent melismatic stretching `إِبِينْ`; write `مْنِ عْلُومْ` to prevent `مِينْ عُلُومْ`; and write `تَرَى آنِي هْوَايْ` without initial Alif on `هْوَايْ`.

- **`NC16` (The 3-Vertical-Line / 23.5-Second `Extend` Law for Kasras — قاعدة الـ 3 أسطر العمودية للكسرة داخل نافذة الـ 23.5 ثانية):**
  - *Failure Observed:* In `صوت أم البنين (Extended).mp3`, every `Extend` step lasted `23.5s`. Because the Radood sings 1 vertical line per `~7.5s` musical phrase at `60 BPM`, all 5 Nazlas (`2A, 3A, 4A, 5A, 6A` — each having **3 vertical lines**) fit `100%` (`3 x 7.5s = 22.5s`), whereas all 5 Kasras (`2B, 3B, 4B, 5B, 6B` — formatted as **5 vertical lines**) spent all `23.5s` singing the first 3 short lines (`7.5s x 3 = 22.5s`) and cut off Line 4 (`بيت القفلة`) at `23.5s`!
  - *Permanent Constraint:* Format every `[الكَسْرَة]` in an `Extend` step (`2B, 3B, 4B, 5B, 6B`) as **EXACTLY 3 VERTICAL LINES (`~21–22s`)** by pairing the first two short triplet hemistichs on Line 1 (`الشطر الأول .. الشطر الثاني ..`), placing the third triplet hemistich on Line 2 (`الشطر الثالث ..`), and placing the closing couplet (`بيت القفلة`) on Line 3 (`الصدر .. العجز ..`). Never exceed **3 vertical lines** in a single `23.5s` `Extend` step.

- **`NC17` (Manual/Atomic Lyrics Buffer Verification Before `Extend` — منع بقاء الأبيات السابقة في حقل Lyrics):**
  - *Failure Observed:* In `صوت أم البنين (توزيع آخر) (Extended).mp3` and `JSON (Extended).mp3`, old lyrics remained in the `Lyrics` box during `Extend`, causing the model to fuse words from different stanzas (`عالقسم الله أجرچ`, `بشر يبرچ وگع جعفر`, `ما منه كتر سلبوها`) and repeat Stanza 1 at the end.
  - *Permanent Constraint:* Before clicking `Extend` (or sending a stage JSON in `Producer Chat`), verify visually in the `Compose > Lyrics` panel that **all previous stage lyrics are deleted** and only the **3 vertical lines** of the current step are present.

---

## 2. Mandatory Pre-Generation Discovery & Consultation Protocol (`بروتوكول الاستكشاف والتشاور قبل التوليد`)

1. **Default Mode — Interactive Consultation (`الوضع الافتراضي: التشاور التفاعلي`):**
   - Strictly FORBIDDEN to generate or output final production prompts/audio immediately upon receiving a poem unless the user explicitly commands Full Auto-Pilot.
   - **Step A (Comprehensive Poem Analysis via the 175-Track Corpus):** Analyze the poem's prosodic meter (`البحر العروضي والوزن المقطعي`), dialect (`عراقي، بحراني، فصيح`), dramatic arc (`الجو الدرامي`), and stanza structure (`المستهل، النزلات، الكسرات`).
   - **Step B (Structured Consultation Questions & Practical Options):** Present concise, actionable choices covering:
     1. **School & Artistic Style (`المدرسة والأسلوب الفني`):** Traditional Vocal-Symphony (`تقليدي سيمفونية بشرية كمدرسة باسم الكربلائي والسيد سلام`), Modern Solemn Studio (`حديث وقور`), Minbar Na'i (`نعي منبري`), Shoor (`شور`), Tawashih/Nasheed (`تواشيح/إنشاد`), or Hybrid (`هجين`).
     2. **Melody, Maqam & Husseini Tor (`اللحن والطور والمقام`):** Best-fit Maqam (`الصبا، البيات، الحجاز، اللامي، الكرد، النهاوند`) and Tor (`مثكل كربلائي، ركباني، نصاري، فائزي، بحراني ثلاثي/رباعي/حيدري`).
     3. **Rhythm, BPM & Strike Pattern (`الإيقاع والسرعة ونمط الضربات`):** Exact BPM (`56–60 BPM` Thaqeel, `72–84 BPM` Wast/Mawkib, `115–133 BPM` Shoor, `0 BPM` Rubato Na'i) and chest-strike pattern.
     4. **SFX & Spatial Atmosphere (`المؤثرات الصوتية والجو العام`):** Sacred Hall/Dome reverb, layered human Ahaat pads, Mawkib ambiance, or dramatic low sub-bass drone.
     5. **Vocal & Choral Arrangement (`توزيع الأداء الصوتي`):** Exact mapping of Solo Radood (`الملا/الرادود منفرداً`) vs. Unison Sheyala/Choir (`الكورال/الردّة`).

2. **Exception — Full Delegation Mode (`وضع التفويض الكامل — Auto-Pilot Mode`):**
   - Triggered ONLY when the user explicitly commands: `"اختر كل شيء بنفسك"` or `"نفّذ بالوضع التلقائي الكامل"`.
   - Skip questions and execute immediately by selecting the optimal, 100% technically feasible parameters from the 175-track corpus, and attach a concise summary table of the chosen engineering decisions alongside Stage 1.

3. **Technical Feasibility & Anti-Distortion Advisory (`قاعدة الواقعية وقابلية التنفيذ`):**
   - Every option offered or executed MUST be 100% achievable on the target engine (`Lyria 3.5` / Flow Music) without distortion. If the user requests an incompatible or quality-destroying setting, immediately alert the user and provide the engineered alternative.

4. **Quality Gate Before EXTEND (`بوابة الجودة قبل التمديد`):**
   - In BOTH modes (Interactive and Auto-Pilot), **NEVER proceed to `EXTEND` stages (`Stages 2..6`) until `Stage 1 Root` has been acoustically and linguistically verified and approved**.

---

## 3. Strict Dialect Phonetics & G2P Isolation (`الفصل الصارم بين اللهجات ومخارج الحروف`)

| Feature (`الخصيصة الصوتية`) | Iraqi Husseini Dialect (`اللهجة العراقية الدارجة`) | Bahrani / Ahsa Dialect (`اللهجة البحرانية والأحسائية`) | Classical Arabic (`اللغة العربية الفصحى`) |
| :--- | :--- | :--- | :--- |
| **Target Consonants (`مخارج الحروف`)** | `گ` = `/g/` (`گَلِبْ، انْگِسَمْ`), `چ` = `/tʃ/` (`أَجْرِچْ، مَچْوِيَّه`), emphatic `ر` and `ص` | `ق` = `/g/` or `/dʒ/`, soft `چ` = `/tʃ/`, Bahrani `وَنَّة` nasalized cadence | Pure MSA `ق` = `/q/`, `ك` = `/k/`, `ج` = `/dʒ/`, strict `ض` vs. `ظ` distinction |
| **Word-Final Endings (`أواخر الكلمات`)** | **Strict Sukun (`تسكين الأواخر`)**; feminine `ـه` = soft `/a/` (`نَشْدَه، مَكْسُورَه`); masculine `ـهْ` = `/ah/` | **Strict Sukun (`تسكين الأواخر`)** with elongated final vowel glide (`مَدَّة بحرانية`) | Grammatical case endings (`حركات الإعراب: ضمة، فتحة، كسرة`) inside connected phrases, Sukun only at pause (`الوقف`) |
| **Stress & Epenthesis (`النبر وكسر التقاء الساكنين`)** | Selective prosthetic `إِCْ` (`إِحْسَينْ، إِبِنْ حَذْلَمْ، إِعْلَه`) and CVC Kasra (`گَلِبْ، دَمِعْ، صَبِرْ`) | Smooth CV syllable linking (`عَلَى حْسَينْ، يَا بُو السَّجَّادْ`) | Strict MSA syllabification without colloquial prosthetic vowels |

---

## 4. Precise Taxonomy of Husseini Performance Styles (`التصنيف الدقيق للأساليب الفنية`)

1. **Traditional / Vocal-Symphony Style (`الأسلوب التقليدي / سيمفونية الصوت البشري` — مدرسة باسم الكربلائي والسيد سلام الحسيني):**
   - **Core Rule:** 100% Human Vocal & Chest-Percussion Symphony (`Pure Acapella No Instruments`). Multi-layered human Ahaat/harmonies (`Bass Vocal Drone + Baritone Pad + High Mournful Ahaat`) + synchronized chest Matam + Sacred Dome Reverb (`2.8s–3.5s`) make pure human voices sound like a full orchestral symphony.
2. **Modern Solemn Style (`الأسلوب الحديث الوقور` — كليبات الاستوديو المعاصرة):**
   - **Core Rule:** Dignified contemporary studio arrangement using deep dark atmospheric sub-bass pads and subtle harmonic beds (`-18dB`) that preserve Husseini majesty (`الوقار والقدسية العاشورائية`), strictly banning solo tarab playing (`No Solo Ney/Oud/Guitar`) or upbeat pop drums.
3. **Mournful Minbar Na'i (`النعي المنبري الحزين` — `0 BPM` Rubato):**
   - **Core Rule:** Rhythm-free (`0 BPM Rubato`), solo Khateeb/Radood on Maqam Saba, Hijaz, or Bayati (`أطوار الفائزي، التميمي، الحلي، الأبوذية`) with soft room reverb and zero rhythmic percussion.
4. **Husseini Shoor (`أسلوب الشور الحسيني` — `115–133 BPM`):**
   - **Core Rule:** Fast driving collective chest-latm pulse (`115–133 BPM`) on Maqam Bayati or Kurd, built on short repetitive passionate refrains (`ذكر ومواساة سريعة`).
5. **Shia Islamic Tawashih & Nasheed (`الأناشيد والتواشيح الدينية الشيعية`):**
   - **Core Rule:** Melodic/harmonic choral arrangement (`Rast, Nahawand, Sikah, Hijaz, Ajam`) with rich multi-part male choir harmonies (`بدون لطم صدري؛ إما أكابيلا روحانية للتواشيح أو إيقاع دف/إيقاع إنشادي وقور للأناشيد`).
6. **Hybrid Style (`الأسلوب الهجين`):**
   - **Core Rule:** Combines a Traditional Vocal-Symphony Nazla/Mawkib pulse with a Modern Solemn atmospheric pad in the Kasra (`الكَسْرَة`), governed by strict seam transitions.


---

## سابعاً: السجل المرجعي للاختبارات الميدانية (`N = 8 Tracks`) وحزمة الاختبار القياسية لقصيدة «صُوتْ أُمِّ البَنِينْ يِصِيحْ — يَبِنْ حَذْلَمْ» (`V51.2 Benchmark`)

### 1. ملخص نتائج التجارب الميدانية الثماني بدون معالجة لاحقة (`Raw Output Telemetry`)
1. **تجارب التأسيس (`Stage 1 Root — 4 Tracks`):**
   - `Compose > Lyrics\صوت أم البنين (توزيع آخر).mp3` (`02:49`): **`96.8%`** (المركز الأول تأسيسياً — اكتمل عند `01:40`؛ خلو تام من المعازف `100%`).
   - `Compose > Lyrics\صوت أم البنين.mp3` (`02:27`): **`94.5%`** (اكتمل عند `01:31`؛ خلو تام من المعازف `100%`).
   - `JSON\صُوتْ أُمِّ البَنِينْ يِصِيحْ — المرحلة 1 التأسيسية (1).mp3` (`01:41`): **`92.5%`** (المقطع الأول كامل مع المستهل الافتتاحي والختامي).
   - `JSON\صُوتْ أُمِّ البَنِينْ يِصِيحْ — المرحلة 1 التأسيسية.mp3` (`01:39`): **`86.5%`** (قفز عن المستهل الافتتاحي عند `00:00` مما أوجب القاعدة `NC12`).
2. **تجارب التمديد الكامل (`Full Extended — 4 Tracks / ~23.7 Minutes`):**
   - `Compose > Lyrics\صوت أم البنين (Extended).mp3` (`05:56`): **`89.5%`** (المركز الأول في التمديد — خلو تام من المعازف `100%`، نطق سليم `96%`، اكتمال النزلات الخمس `2A–6A` بنسبة `100%`، واكتمال المستهل الختامي `6C` بنسبة `100%`؛ وكشف لنا قانون الأسطر العمودية الثلاثة في الكسرة `NC16`).
   - `JSON\صُوتْ أُمِّ البَنِينْ يِصِيحْ — المرحلة 1 التأسيسية (Extended) (1).mp3` (`05:50`): **`83.5%`** (أثبت عملياً نجاح أداء الكسرتين `2B` و`6B` كاملتين مع `بيت القفلة` وترديد الجوقة بنسبة `100%`!).
   - `JSON\صُوتْ أُمِّ البَنِينْ يِصِيحْ — المرحلة 1 التأسيسية (Extended).mp3` (`05:58`): **`68.5%`** (كشف ضرورة عدم ترك سطر الجوقة يتكرر عبر الكسرات `NC16/NC17`).
   - `Compose > Lyrics\صوت أم البنين (توزيع آخر) (Extended).mp3` (`05:56`): **`64.0%`** (كشف حتمية تفريغ صندوق `Lyrics` قبل كل تمديد `NC17`).

### 2. جدول المراحل القياسي الكامل للاختبار (`Stages 1 to 6C — V51.2 3-Vertical-Line Locked`)
- **المرحلة 1 (`Stage 1 Root`):** `[المُسْتَهَلّ]` + `[النَّزْلَة الأُولَى]` (`3 أسطر`) + `[الكَسْرَة الأُولَى]` (`3 أسطر`) + `[المُسْتَهَلّ]`.
- **مراحل التمديد (`Stages 2A–6B` — كل مرحلة `3 أسطر عمودية حصراً = 21.5s` داخل نافذة `23.5s`):**
  - `2A`: `يِگِلْهَا عَظَّمْ اللّٰه أَجْرِچْ .. عَبْدُاللّٰه وُگَعْ بِالْبَرْ ..` / `وُمِنْ بَعْدَه تَرَى عُثْمَانْ .. ظَلْ إِعْلَه الثَّرَى مُوذَرْ ..` / `يَالْحُرَّه وُتَرَى الثَّالِثْ .. أَخَبْرِچْ وُگَعْ جَعْفَرْ ..`
  - `2B`: `صَاحَتْ وَالدَّمِعْ بَادِي .. بِشِرْ گَطَّعِتْ إِفَّادِي ..` / `مَا أَنْشِدَكْ عَلَى أَوْلَادِي ..` / `عَلَى إِحْسَيْنْ النَّشِدْ كِلَّه .. اشْتَاگَيْتْ أَنْظُرْ لْخَدَّه ..`
  - `3A`: `يِگِلْهَا الرَّابِعْ الْعَبَّاسْ .. يَمْ الْمَشْرَعَه مَچْتُوفْ ..` / `عَلَى عَيْنَه سَهَمْ نَابِتْ .. وُظَلْ إِعْلَه النَّهَرْ مَلْهُوفْ ..` / `وُظَلَّتْ مِنْ وَرَاهْ زَيْنَبْ .. يَمْ عَبَّاسْ مَكْسُورَه ..`
  - `3B`: `صَاحَتْ گِلِّي عَاللِّي صَارْ .. لَا تِحْچِيلِي عَالْأَقْمَارْ ..` / `گَلْبِي مِنِ الصُّبُحْ مِحْتَارْ ..` / `أَرِيدَنْ خَبَرْ عَنْ إِحْسَيْنْ .. دِگِلِّي الْوَلِي إِحْسَيْنْ إِشْلُونْ ..`
  - `4A`: `صَاحْ وُدَمْعِتَه تِجْرِي .. أَخَبْرِچْ ذَبْحَوْا الْغَالِي ..` / `عَلَى التِّرْبَانْ ظَلْ عَارِي .. وُجِسْمَه بِالدِّمَه مَالِي ..` / `وُالْخَيْلْ إِعْلَه صَدْرَه تْدُوسْ .. مَا مِنَّه كِتِرْ سَالِي ..`
  - `4B`: `وُعُگْبَه الْخِيَمْ حَرْگُوهَا .. وُزَيْنَبْ غَصُبْ سَلْبُوهَا ..` / `وُلِلشَّامَاتْ وَدُّوهَا ..` / `رَدَّوْا إِلِچْ حَرَمْ وُأَطْفَالْ .. وُالسَّجَّادْ ظَلْ وَحْدَه ..`
  - `5A`: `صَاحَتْ يَبْنِي الْمَذْبُوحْ .. يَالْچِنِتْ الْهَوَى لِيَّه ..` / `مِتَانِيتَكْ تِرِدْ كِلْ يُومْ .. چَا لَيْشْ گَطَعِتْ بِيَّه ..` / `كِلْهُمْ فِدْوَه يِرْحُولَكْ .. مِنْ نُورَكْ گِطَعْ ضَيَّه ..`
  - `5B`: `كِلْهُمْ مُوتَى مَعْقُولَه .. وِيَّاهُمْ رَيْتْ مَقْتُولَه ..` / `وُبِالتَّابُوتْ مَشْيُولَه ..` / `گَبُلْ هَاللَّحْظَه لَوْ مَيْتَه .. وُلَا أَعِيشَنْ بَعَدْ مُدَّه ..`
  - `6A`: `رَاحَتْ تِصْرَخْ لْزَيْنَبْ .. يَا يُمَّا الْبِگَا بْرَاسِچْ ..` / `آنِي سْمَعِتْ وُانْذِهْلَيْتْ .. چَانْ إِشْلُونْ إِحْسَاسِچْ ..` / `وُشِفْتِيهُمْ بْشُوفْ الْعَيْنْ .. كِلْهَا مْذَبِّحَه نَاسِچْ ..`
  - `6B`: `إِشْلُونْ إِنْتِي تْحَمَّلْتِي .. حْيُودْ إِعْلَه الْأَرُضْ شِفْتِي ..` / `شْكُبُرْ صَبْرِچْ وُمَا مِتِّي ..` / `صَبْرِچْ مَا تْحِدَّه حْدُودْ .. رَغُمْ هَمِّچْ عَبَرْ حَدَّه ..`
  - `6C` (`الخاتمة`): `[المُسْتَهَلّ]` (`صُوتْ أُمِّ البَنِينْ يِصِيحْ .. يَبِنْ حَذْلَمْ .. عَلَى أَوْلَادِي دَلِيلِي يِطِيحْ .. يَبِنْ حَذْلَمْ ..` + تكرار الجوقة بين قوسين).
