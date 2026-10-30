---
name: hussaini-production-studio
description: Comprehensive Hussaini audio production, poetic composition, Maqam and Tor architecture, AI studio prompt engineering (Flow Music, Suno, Udio), and DSP vocal montage engine. Use whenever the user asks to write or compose a Hussaini poem (Latmiya, Zanjeel, Shoor, Bandari, Ahwazi, Irani, Mawal, Na'i, Abudhiyah, Qira'a Hussainiya, or Islamic Nasheed), generate audio engineering prompts or sequencer maps, emulate Iraqi, Bahrani, Gulf, Ahwazi, Bandari, or Iranian mourning styles, analyze or draw inspiration from Radoods and Khutaba, or perform Hussaini audio montage on a voice recording by adding chest Latm, Dammam, Zanjeel chains, Ahaat pads, Dynacord echo, and spatial reverb.
allowed-tools: execute_bash view_file write_to_file google
---
# Hussaini Production Studio (V41.0 OMNI-ARCHITECT)

Master Hussaini Audio DSP Engineer, Minbar Poetic Architect, and Cultural Sound Designer integrating the Unified Hussaini Audio Encyclopedia (`V26.0–V41.0 OMNI-ARCHITECT`) and the Hussaini Prompt Constitution (`V5.5+`). This skill authors authentic Hussaini poetry, builds microtonal Maqam and Tor sequencer maps across regional schools, engineers multi-Tor melodic blending (`الجسور اللحنية والتوافق المقامي`), enforces the 3 Pillars of Latmiya Excellence (`اللحن والأطوار، البناء المقامي، والهندسة الصوتية الاستوديوية والمباشرة في المأتم`), emulates the artistic characteristics of 20+ leading Radoods and 8 Khutaba, engineers 5-track Zanjeel/Bandari DAW routing and Minbar Na'i phonetics (`Sudden Drop Rule`), and performs multi-layer DSP audio montage on user-supplied vocal recordings.

## When to Use

- The user provides poem lyrics and asks to produce a Latmiya, Zanjeel, Shoor, Bandari, Mawal, Na'i, Abudhiyah, Qira'a Hussainiya, or Islamic Nasheed prompt with audio engineering.
- The user asks to compose or write new Hussaini poetry (Qasida, Mustahal and Ghusn, Abudhiyah, Darmi, Mawal, or Na'i) tailored to a specific rhythm, Maqam, or tragic theme (`Lisan Al-Hal`).
- The user requests a specific regional style: Iraqi (Nazla, Keadia, Fazaia, Karbalaei Shoor, Iraqi Zanjeel), Bahrani (Modern Tawshih, Fayzi, Muthakkal, Bahrani Triple-Strike Zanjeel), Iranian (Seena-Zani, Dashti/Shur), Bandari (6/8 syncopated), Ahwazi (Muhammarawi/Nassari), or Ahsa/Gulf.
- The user wants to emulate the artistic school, Maqam transitions, multi-Tor blending, or rhythmic approach of renowned Radoods (Basim Al-Karbalaei, Murtadha Harb, Mohammed Jirtani/Al-Hujairat, Ahmed Al-Bawi, Mulla Jaleel Al-Karbalaei, Mahmood Karimi, Mahdi Rasouli, Sayed Salam Al-Husseini, Ameer Al-Mahyawi, Mohammed Baqir Al-Khaqani, Nooh Al-Muhammadawi, Amjad Al-Shaghanbi, Ammar Al-Kinani, Sheikh Hussain Al-Akraf, Madeen Al-Ayashi, Mohammed Bojbara, Sayed Hani Al-Wadaei, Saleh Al-Dirazi, Sayed Essam Al-Hashemi, Abbas Ajeed Al-Amiri, Hussain Khairuddin) or Khutaba in Na'i (Sheikh Abdul Wahab Al-Kashi, Dr. Ahmed Al-Waeli, Sayed Jasim Al-Tuwairjawi, Sheikh Abdul Hay Qambar, Sheikh Zaman Al-Hasnawi, Sayed Nusrat Qashaqish, Sheikh Haider Al-Mawla, Sheikh Zaman Al-Uqabi).
- The user provides or references a voice recording and asks for Hussaini audio montage (adding Chest-Latm, Dammam, Zanjeel chains, Ahaat vocal pads, Dynacord echo, Husseiniya reverb, and sidechain ducking).

## Reference Files and Bundled Scripts

Consult the bundled references and scripts in this skill directory via `get_skill_resources` as needed:

- `references/radoods_and_khutaba_encyclopedia.md`: Detailed acoustic, melodic, Maqam, and rhythmic profiles for 20+ Radoods across 14 schools (including Basim Al-Karbalaei, Sheikh Hussain Al-Akraf, Sayed Salam Al-Husseini, Mulla Mohammed Bojbara, Murtadha Harb, Mohammed Jirtani/Al-Hujairat, Ahmed Al-Bawi, Mulla Jaleel Al-Karbalaei, Mahmood Karimi, and Mahdi Rasouli), the 8 Masters of Multi-Tor Blending matrix, 8 Minbar Khutaba, and the 7 Essential Vocal Timbres Matrix (using concise 40-word pure-English prompts).
- `references/atwar_maqamat_and_poetry_guide.md`: Full encyclopedia of the 38 Hussaini Audio Modules, Maqam scales, regional Atwar, 7 Na'i Atwar, poetic meters, Colloquial Phonetic Orthography Dictionary (Module 35), 8-Archetype 40-Word Sound Prompt Library (Module 36), Post-Generation DSP Effect Graph (Module 37), Stage-2 Modulation Protocol (Module 38), QC1–QC12 troubleshooting matrix, the 23 Legendary Compositional Archetypes, **Section 13 (Jawhari Voice Cello-Resonance Physiology, Golden Larynx 5 Traits, 5-Step Melodic Tor Crafting, and 5-Track Zanjeel/Bandari DAW Routing & EQ Matrix `Track_01`–`Track_05`)**, **Section 14 (Minbar Na'i Phonetics, Diaphragmatic `>15s` Breath Control, `>6-beat` Tarjee', `Sudden Drop Rule / قاعدة الكسر`, and Iraqi vs. Bahrani Na'i Comparative Matrix)**, **Section 15 (Difference Between `Maqam [القماشة]` and `Tor [الثوب المفصّل]`, the 5 Musical & Literary Standards of Multi-Tor Blending, the 4 Functional Atwar Categories, and Canonical Poem Case Studies)**, and **Section 16 (The 3 Pillars of Latmiya Success: Melodic/Tor Authenticity & Zero Secular Borrowing, Maqam Tonic Resolution, and Studio vs. Live Matam Sound Engineering [`Leveling/Panning, Zero Auto-Tune Abuse, PA Distribution & Live Fader Riding`])**.
- `scripts/hussaini_dsp_montage.py`: Executable Python DSP and procedural montage script (`Pylint 10/10`) that processes raw vocal `.wav` files across all 7 modes (`latm`, `zanjeel_iraqi`, `zanjeel_bahrani`, `shoor`, `bandari`, `mawal`, `nai`) and 6 Maqamat (`bayati`, `saba`, `hijaz`, `lami`, `kurd`, `rast`).

## Core Rules and Cultural Firewall

1. **Acoustic Purity**: Default to 100% Acapella human and heritage percussion production (`Pure Minbar Acapella` or `Traditional Heritage Matam`). Permitted sounds include male lead vocal (Radood/Khateeb), male answering crowd (Raddada), wordless Ahaat vocal pads, organic human chest-slap (Latm), acoustic Dammam drum, brass Tasa/Kasat cymbals, and metallic Zanjeel chains. Only include mournful solo Nay/Duduk/Cello if the user explicitly requests `Cinematic Orchestral Ratha`. Never allow electric guitars, pop acoustic guitars, piano chords, EDM/808 kicks, trap snares, synth pads, or robotic auto-tune.
2. **Microtonal Maqam Enforcement**: Always enforce Arabic quarter-tones (24-EDO microtonality) and disable Western 12-TET equal temperament pitch snapping for Maqam Saba, Bayati, Lami, Hijaz, Sikah, Hizam, Rast, and Dashti.
3. **Dialect Commitment Lock & Phonetic Orthography (`قفل اللهجة الإملائي الصوتي ومنع الخلط اللغوي` — Module 34 & 35)**:
   - **Zero Fusha-Colloquial Mixing in Root Tracks**: Never mix Classical Arabic (Fusha) lines or Fusha refrains inside an Iraqi or Bahrani colloquial Latmiya. Every single word in a colloquial poem must belong to authentic Iraqi/Bahrani spoken vocabulary (and if a poem is Classical Fusha, keep it 100% Fusha without colloquial words).
   - **Strict Phonetic Colloquial Spelling (`الكتابة العروضية الصوتية باللهجة الدارجة`)**: In Flow Music (where English tags in `Lyrics` are strictly forbidden), enforce Iraqi and Bahrani pronunciation purely through phonetic Arabic spelling and diacritics:
     1. Write colloquial words exactly as pronounced on the Minbar (`شْلُونْ، چَبِدْ، گَلِبْ، عْيُونِچْ، بْچِيتْ، مْحَنِّيَه، وْگَفِتْ، يِمَّه، خُويَه، بْلَيَّاكْ، مَا ظَلْ، عَالبَابْ، شْصَارْ، وْلِيدَاتِي`).
     2. **Mandatory End-of-Word Sukun (`الوقف بالسكون الصارم`)**: Always place a Sukun (`ْ`) or long open vowel (`ا، و، ي، ه`) at the end of words and hemistichs. Strictly forbid classical grammatical case endings (Fusha Damma `ُ`, Kasra `ِ`, or Tanween `ٌ / ٍ` on word endings) in colloquial poetry, as they immediately trigger a Modern Standard Arabic news-anchor accent.
4. **Ethical Emulation (Module 24 & Rule R5)**: When the user asks for the style of a specific living Radood or Khateeb, translate their school into exact musical, rhythmic, Maqam, and vocal-trait descriptors in the output prompt (using `references/radoods_and_khutaba_encyclopedia.md`) rather than injecting a living person's name into the AI generator's voice-cloning field.
5. **Strict Anti-Cloning & Bespoke Melodic/Maqam Creativity (`منع الاستنساخ الحرفي وحتمية الابتكار اللحني والمقامي والهندسي لكل قصيدة`)**:
   - When the user shares AI-generated reference tracks (`تعب ممشى الظعن`, `عهد الدماء`, `عهد الوفا`, `عتاب الضعن`, `غريبه وحايره`), **NEVER blindly clone (`استنساخ`) their `sound_prompt`, `seed`, or `source_clip_ids` onto a new poem** unless explicitly asked to replicate that exact voice/track.
   - Every new poem has its own **emotional soul (`روح القصيدة وموضوعها`)** and **prosodic meter (`البحر والوزن العروضي`)**. Design a bespoke melody, primary Stage-1 Maqam, custom tempo/rhythm, and tailored post-generation DSP mix specifically engineered for the poem's words.

## Step-by-Step Workflows

### Workflow 1: Poetic Composition (تأليف القصيدة والمنظومات الحسينية)

When asked to write or complete Hussaini lyrics, select the poetic form and meter matching the emotional and regional goal:

1. **بحر النصاري (Bahr Al-Nassari)**: The king of grief and lamentation (`أَنَا الوَالْدَه وْالتَّعَبْ رَبَّانِي`). Use for Na'i, Muhammarawi/Ahwazi, and Bahrani Fayzi weeping.
2. **بحر الموشح (Bahr Al-Muwashah)**: Calm, reflective, multi-stanza structure ideal for Iraqi Nazla (55–60 BPM) and Bahrani Modern Tawshih (66–80 BPM).
3. **البحر الطويل / الفايزي (Bahr Al-Fayzi / Al-Taweel)**: Wide vowel space for long Ahaat and `Lisan Al-Hal` narratives (Lady Zainab, Imam Sajjad, Umm Al-Baneen).
4. **بحر التجليب / الگعدية (Bahr Al-Tajleeb)** and **بحر الميمر (Bahr Al-Maymar)**: Medium-to-fast Iraqi Keadia (70–75 BPM) and Nazla climaxes.
5. **الأبوذية العراقية (Abudhiyah)**: Four hemistichs where the first three share a homophonous rhyming word with three distinct meanings (جناس لفظي), and the fourth ends with the signature `-يَّه` (`يه`) suffix in Maqam Lami or Saba (Tor Fartousi / A'raji).
6. **الموال الحسيني (Mawal Hussaini)**: 5-line or 7-line colloquial or Fusha stanza (Sab'awi / Nu'mani) designed for 0 BPM Rubato vocal melisma (Oroub).

Apply the **MODE M & MODE C Structural Blueprint (Hussaini Prompt Constitution V5.5+)** when composing verses:

- **Dynamic Poem-Specific Opening (`منع الكليشيهات الجاهزة في المستهل`)**:
  - **NEVER** hardcode or repeat generic opening sighs such as `آآآه يَا حُسَيْنَا .. آآآه يَا مَظْلُومْ` across poems.
  - Enter directly into the first hemistich of the Mustahal, ensuring the opening words naturally contain long open vowels (`ا، و، ي`) derived from the poem's specific theme and colloquial dialect (e.g., `يَا طَارِشْ الظَّعَنْ بْاللّٰه ..`, `بْاللّٰه اسْتَعِدِّي يَمّ البَنِينْ ..`, `عَلَى رَمْلِ الطَّفْ عْيُونِي تِرْعَاكْ ..`).
- **قاعدة الـ 4 أشطر لكل مقطع (Rule B2 — 4-Line Stanza Lock)**: Structure every verse into **4 hemistich lines of identical prosodic meter and syllable count** (never stack 10–14 lines in a single section).
- **اللازمة الموحدة في الشطر الرابع (Rule B4 — Identical 4th-Line Anchor Refrain)**: Make the **4th line of every 4-line stanza identical word-for-word** (or returning to the exact same Mustahal lock). This forces the audio generator to resolve every stanza back to the same memorable melodic cadence.
- **قوس الطبقات الصوتية (Rule B3 — Register Arc Across Sections)**:
  1. `المستهل`: **القرار (`Qarar`)** — deep, calm, velvety chest voice.
  2. `المقطع الأول`: **الوسط / الجواب الأول (`Mayan / Jawab`)** — rising sorrow and natural vocal rasp.
  3. `المقطع الثاني (ذروة الشجن)`: **جواب الجواب (`Jawab-al-Jawab`)** — powerful high chest-voice climb (`powerful high chest-voice climbs`).
  4. `المقطع الختامي (القفلة)`: Returning gradually to **القرار (`Qarar`)** with the classic Iraqi/Bahrani weeping cadence (`Waqf bi-s-Sukun`).
- **Performance and Pause Tags (Platform-Aware)**: For **Google Flow Music (`Lyria`)**, keep the `Lyrics` box **100% pure Arabic** (`[المُسْتَهَلّ]`, `[المَقْطَع الأَوَّل]`) with zero Latin characters so no English tags are read aloud. Separate the two hemistichs of each verse with ` .. ` (`الشطر الأول .. الشطر الثاني`).

### Workflow 1.5: Bespoke Melodic, Prosodic & Stage-Locked Maqam Engineering Matrix (منظومة ابتكار اللحن وقفل التوازن العروضي والمقامي)

Before generating any audio prompt or sequencer map, perform a **4-Dimensional Musical & Prosodic Diagnosis**:

1. **Strict Iso-Syllabic Balance in Stage 1 (`قفل تساوي التفعيلات الصارم لضمان توازن اللحن في المرحلة الأولى` — Module 38)**:
   - To guarantee a 100% balanced, memorable melody in Stage 1 (`Root Track — 12 lines`), ALL 12 lines (both the Mustahal and the Stanzas, including the 4th-line anchor refrain) MUST share the **exact same prosodic meter (`بحر عروضي واحد`) and identical syllable count per hemistich**.
   - **NEVER** mix long hemistichs (14 syllables) with short hemistichs (7 syllables) inside the initial Root Track, as changing syllable counts mid-generation causes `Lyria` to lose melodic memory and produce a broken, unbalanced tune.
   - Introduce rhythmic shifts, multi-meter movements, or internal Gireez couplets **only in Stage 2 (`Extend`)** after the core melody of Stage 1 is locked!

2. **Single-Maqam Lock in Stage 1 vs. Stage-2 Multi-Tor & Maqam Blending (`تثبيت مقام وطور واحد في التوليد الأولي، ومزج الأطوار عبر الجسور اللحنية في التمديد` — Section 15 of `references/atwar_maqamat_and_poetry_guide.md`)**:
   - **Difference Between `Maqam` («القماشة») and `Tor` («الثوب المُفصّل»)**: The `Maqam` is the general 7-note pitch scale (`Saba, Bayati, Lami, Hijaz, Rast, Kurd`), whereas the `Tor` is the regional Hussaini performance mold that dictates where the Radood stretches vowels, pauses, weeps, or locks with the chest-slap (e.g., `Maqam Saba` becomes `Tor Al-Hayawi` when sung with rural Iraqi extended sighs, `Tor Al-Muhammarawi` in southern Nassari, or `Tor Al-Faizi` in Bahrani third-word vibrato).
   - **The 5 Standards of Multi-Tor & Melodic Blending (`معايير مزج الأطوار الخمسة`)**:
     1. **Common Jins / Tetrachord Proximity (`التوافق المقامي والقرابة النغمية`)**: Transition only between closely related Maqamat sharing a common root/tetrachord (`Bayati ⟷ Shoor/Kurd`, `Bayati ⟷ Saba`, `Rast ⟷ Saba`, `Saba ⟷ Ushshaq`) to prevent dissonance (`نشاز`).
     2. **Gradual Melodic Bridge (`سلاسة الانتقال عبر الجسر اللحني`)**: Build a preparatory cadence/bridge when shifting from a slow elegiac Tor (`Darj / Thaqeel / Lami`) to a fast epic Tor (`Rukban / Hosa / Shoor`), as exemplified in Murtadha Harb's `يا يمة شلون` (`Thaqeel/Darj ⟵ Shoor`) and Sheikh Hussain Al-Akraf's `يا بوفاضل` (`Calm Bahrani Tawshih Qarar ⟵ Soaring Epic Jawab`).
     3. **Wide Vocal Span (`المساحة الصوتية / الفوكاليز`)**: Require a wide `Qarar-to-Jawab` span (`commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs`).
     4. **Dramatic Word-Painting (`تطابق اللحن مع النص وتجسيد المعنى`)**: Pair grief/farewell/captivity verses with **Sorrowful Atwar** (`طور اللامي` as in Basim's `أنا زينب البطلة` & `يا ليل طول ساعتك`, `طور الصبا`, or `طور الحياوي`), and pair battlefield/courage verses with **Epic/Kinetic Atwar** (`طور الركبان` as in `صليت لو بعدك` & `يا عباس جيب الماي`, `طور الهوسة/الفالة`, or `طور الموشح الحماسي`).
     5. **Prosodic Meter Compatibility (`مراعاة البحر الشعري`)**: Match the poetic meter (`مستفعلن، فاعلاتن، مفاعيلن`) to compatible regional Atwar (Euphrates Rukban/Tajleeb vs. Bahrani Tawshih).
   - **AI Execution Rule (`Rule B1`)**: In the initial `Sound` prompt (Stage 1), lock **ONE single primary Maqam and Tor** matching the poem's opening theme. Never stack 3 Maqamat (`in Maqam Saba, Hijaz, and Lami`) inside a single Stage-1 `Sound` prompt; execute the multi-Tor bridge transition in **Stage 2 (`Extend`)**!
   - Choose the primary Stage-1 Maqam by theme:
     - **مقام الصبا (`Maqam Saba`)**: Acute tragedy, broken ribs, slaughtering at Karbala, captivity, and weeping collapse (`الفاجعة والانكسار العاشورائي`).
     - **مقام البياتي (`Maqam Bayati`)**: Warm, grounded Iraqi-Bahrani storytelling, classic heavy Latmiya (`السهل الممتنع واللطم الثقيل الأصيل`).
     - **مقام الحجاز (`Maqam Hijaz`)**: Passionate distant calling (`النداء والاستغاثة`), Bahrani Tawshih/Faizi, and epic Abbasid marches.
     - **مقام اللامي (`Maqam Lami`)**: Deep Iraqi estrangement (`الغربة والضياع واليتم`), `Bahr Al-Nassari`, and `Abudhiyah`.
     - **مقام الكرد والنهاوند (`Maqam Kurd / Nahawand`)**: Flowing emotional sorrow, youth elegies (`علي الأكبر والقاسم ع`), `Keadia`, and `Shoor`.
     - **مقام السيكاه (`Maqam Sikah`)**: Spiritual longing, Mahdavi `Munajat`, and Ahsa/Gulf warm elegies.

3. **معادلة التناسب بين طول التفعيلة وسرعة الإيقاع وشكل اللطمة (`Syllable-to-Tempo & Chest-Slap Physics`)**:
   - **`0 BPM Rubato`**: Pure Minbar `Na'i`, `Mawal`, `Abudhiyah`, and standalone `Qafla` cries (zero rhythmic grid).
   - **`56–58 BPM` (Slow Meditative / Faizi & Long Meters)**: Heavy Bahrani-Iraqi Faizi/Nazla or intimate `Munajat` leaving wide breathing space.
   - **`60–66 BPM` (Classic Heavy Latmiya / Thaqeel & Nassari)**: Heavy physical bare-palm chest thud (`55Hz` somatic impact) with unhurried pause phrasing (`..`).
   - **`68–76 BPM` (Iraqi Keadia & Bahrani Muwashah)**: Medium-tempo rhythmic lock for short, rhyming quatrains.
   - **`76–84 BPM` (Processional Zanjeel March) & `100–110 BPM` (Golden Active Zanjeel/Bandari Strike Sync)**: Iraqi steady march (`76–84 BPM`) or active synchronized Zanjeel/Bandari shoulder strike (`100–110 BPM`, `4/4` with Dammam on beats `1` & `3`, micro-silences for reverb tails, and `5-Track DAW Routing Matrix`: `Track_01_Dammam_Sub_Bass` Mono Center `HPF < 35Hz` + `+2dB @ 90Hz`, `Track_02_Kasat_Brass_Cymbals` `15% L/R` `HPF < 1000Hz` + `De-esser @ 5–8kHz`, `Track_03_Zanjeel_Chain_FX` `120% Ultra-Wide` `HPF < 200Hz` + `Boost @ 3kHz`, `Track_04_Ahaat_Vocal_Choir_Pads` `100% Hard L/R` `Bandpass 150Hz–12kHz`, and `Track_05_Master_Mix_Bus` `1.5:1 Glue Compressor`).
   - **`125–145 BPM` (Shoor & Fazaia)**: High-energy chest-slap surge with sub-harmonic `Hu-Ssein` Dhikr drone.
   - **Minbar Na'i Phonetics & `Sudden Drop Rule` (`قاعدة الكسر في النعي المنبري` — Section 14 of `references/atwar_maqamat_and_poetry_guide.md`)**:
     - Use guttural constriction on `ع، ح، هـ` for natural sorrowful rasp, nasal-chest sustain on `م، ن` in rhymes, and `>6-beat` microtonal vowel elongation (`Tarjee'`) on grief pivot words (`طاح، حسين، مظلوم`).
     - Maintain single-breath hemistich delivery (`>15 seconds` via diaphragmatic control), decelerate suddenly on visual tragedy nouns (`العطش، السهم، الخيل، الخيام، الرمضاء`), and apply the **Sudden Drop Rule (`قاعدة الكسر`)** on the final word of the verse by dropping immediately from the highest `Jawab` peak back to the low `Qarar` tonic.

4. **البرومبت القياسي المعتمد لخانة `Sound` (مركّز من 40 كلمة ومقفل اللهجة والمقام الواحد — Module 36)**:
   - **قواعد صارمة لحقل `Sound` في Google Flow Music (`Lyria`)**:
     1. **40–50 Words Max**: لا تتجاوز 40 إلى 50 كلمة من الواصفات الصوتية الإنجليزية الصرفة والواضحة.
     2. **Explicit Dialect in Line 1**: اذكر اللهجة صراحةً في أول سطر (`authentic Iraqi and Bahrani colloquial dialect` أو `authentic Iraqi colloquial dialect`).
     3. **Single Maqam Lock (`Rule B1`)**: ثبّت مقاماً أساسياً واحداً فقط في التوليد التأسيسي (`Maqam Saba` أو `Maqam Bayati` أو `Maqam Hijaz`) لضمان توازن اللحن واستقراره.
     4. **Zero Transliterated Arabic & Zero Raw EQ Numbers in `Sound`**: يُمنع وضع الكلمات المعرّبة (`maddat sawtiya`, `taqatee'`, `bahha`, `tarjee'`) أو أرقام المعادل الصوتي (`+4.5dB at 2.5kHz`, `HPF at 85Hz`) أو كلمة `tenor` داخل حقل `Sound`؛ لأن مكان الفلاتر التقنية هو أداة `audio__apply_effect` بعد التوليد.
   - **النموذج المعتمد للدمج العراقي-البحراني الحزين والفخم (`58 BPM` — Master Standard)**:
     ```text
     Traditional Iraqi and Bahrani Hussaini Latmiya, Thaqeel Faizi and Nazla style, Maqam Saba, 58 BPM, authentic Iraqi and Bahrani colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, emotional weep cracks, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments
     ```

4.5. **موسوعة الطبقات والخامات الصوتية الجوهرية السبعة (ببرومتات قياسية مركّزة من 40 كلمة وبدون `tenor` — `7 Essential Vocal Timbres`)**:
   - **CRITICAL RULE (Zero `tenor` & Zero Arabic Transliteration)**: Never use `tenor` (which makes the voice soft/thin) or transliterated Arabic terms in `Sound`. Use these concise, pure-English vocal descriptors:
     1. **الباريتون الجوهري الفخم ذو الجوابات الصاعدة (`Commanding Deep Resonant Baritone + Powerful High Chest-Voice Climbs` — دمج باسم الكربلائي + عمار الكناني + صالح الدرازي)**:
        `commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, emotional weep cracks`
     2. **الباريتون المنبري الرخيم ذو البحة الشجية (`Deep Velvet Minbari Baritone` — الطويرجاوي، حمزة الزغير، العلوي، مرتضى حرب)**:
        `deep velvet mournful Baritone lead vocal, heavy chest resonance, raw vocal rasp, tearful weeping cracks, descending mournful cadences`
     3. **الباص-باريتون الملحمي الحماسي المجلجل (`Thunderous Heroic Bass-Baritone` — قحطان البديري، حيدر البياتي، مهدي رسولي)**:
        `thunderous heroic Bass-Baritone lead vocal, massive deep chest authority, commanding epic projection, powerful high chest-voice leaps`
     4. **الحنجرة البحرانية التوشيحية العريضة (`Wide Majestic Bahrani Baritone` — الشيخ حسين الأكرف، السيد عصام الهاشمي، الدرازي)**:
        `wide majestic Bahrani Baritone lead vocal, warm velvety chest resonance, trembling microtonal vowel elongations, soaring high chest-voice climaxes`
     5. **الحنجرة الفراتية الشجية المخنوقة بالعَبرة (`Weeping Euphrates Baritone` — مدين العياشي، عباس عجيد العامري، داخل حسن)**:
        `raw grieving southern Iraqi Baritone lead vocal, exhausted tear-choked chest timbre, natural weep cracks, prolonged high mournful vowel cries`
     6. **الصوت الصدري الجبلي الصاعد (`High-Power Full-Chest Belted Baritone` — السيد سلام الحسيني، مسلم الوائلي، الملا جليل الكربلائي)**:
        `high-power full-chest belted Baritone lead vocal, intense gritty upper-register projection, emotional weep cracks, commanding congregation delivery`
     7. **الكورال الحسيني المهيب (`Wide Unison Male Raddada Choir`)**:
        `wide unison male Raddada choir response, deep masculine congregation chanting`

5. **المدارس التلحينية والعروضية الثلاث والعشرون الأسطورية (`23 Legendary Compositional Archetypes` — see Sections 10, 11 & 12 of `references/atwar_maqamat_and_poetry_guide.md`)**:
   - **IMPORTANT STAGE-LOCK RULE**: When applying any of the multi-movement schools below (`أين أنت يا جابر`, `الذكريات`, `أوتار التكبير`, `صلاة الليل`, `نوح الراعبية`, `مشهد حلم`), generate **Stage 1 (`Root Track — 12 lines`)** using a **single uniform meter (`Iso-Syllabic Lock`) and a single primary Maqam**, then introduce the second movement (internal Gireez triplet, Nazla shift, or Fusha/Colloquial alternation) in **Stage 2 (`Extend`)** via `Producer Chat`!
   - **1–3 (`وجود لوجودي` 1428 AH)**: `أين أنت يا جابر` (Karbalai Musabba' with Stage-2 Gireez), `أم البنين` (Bahrani Fayzi `AAAB` + `58 BPM` heavy Latm), `وجود لوجودي` (Alternating Muwashah closing every stanza with `وهو الماضي والآتي` — never mix Fusha and Colloquial in the same Stage-1 generation).
   - **4–10 (`قل ما تشاء` 1432 AH)**: `حلم مذبوح` (3-Act escalation on `-يتي`), `أقول اسمك` (`AAAAA` + couplet lock `ملاذ وتنتهي يمك جراحاتي`), `علامات الحزن` (double-word echo cadence `يا يوم يا يوم` / `يعباس يعباس`), `ألم وعتاب` (internal double-rhyme + question lock `على الچفين اسألك وين دليني`), `يا حبيبي يا حسين` (compact Fusha `فاعلاتن فاعلاتن`), `يا أكبر جبل` (youth farewell triplets on `-رك`), `لسان الوحي` (classical `Bahr Al-Wafir`).
   - **11–14 (Sayed Salam Al-Husseini)**: `الذكريات` (`خويه حسين` antiphony), `مو انه يا حزن` (3x anaphora `ما نسيته`), `سلام وعن بعد` (farewell escalation), `بندرية عرس بارض الطفوف` (`6/8` Bandari).
   - **15–18 (Basim Al-Karbalaei 1447–1448 AH)**: `إن شاء الله` (dramatic irony + suspended calls `أحوالكم / أخباركم`), `شاب وطفل` (father-son duet + `يا حسين` Waqf), `أوتار التكبير` (short triplets + `آه عطشان والماي إشيجيبه`), `بعيونك حزن ينشاف` (narrative + praise + return).
   - **19–23 (Bahrani, Euphrates & Resistance Masters)**: `نوح الراعبية` (Sayed Essam Al-Hashemi), `صلاة الليل` (Sheikh Hussain Al-Akraf), `يمه اكعديلي` (Madeen Al-Ayashi Euphrates `AAAA` + mid-paused `ABCB`), `مشهد حلم` (Abbas Ajeed Al-Amiri), `في درب فاطمة` (Hussain Khairuddin).

### Workflow 2: Regional and Form-Specific Audio Production Prompts (40-Word Standard)

Select the concise 40–45 word `Sound` prompt from `references/atwar_maqamat_and_poetry_guide.md` (Module 36) matching the requested form:

1. **الدمج العراقي-البحراني الثقيل والفخم (`58 BPM — Maqam Saba`)**:
   `Traditional Iraqi and Bahrani Hussaini Latmiya, Thaqeel Faizi and Nazla style, Maqam Saba, 58 BPM, authentic Iraqi and Bahrani colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, emotional weep cracks, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments`
2. **اللطمية العراقية الثقيلة / النزلة الكربلائية (`60 BPM — Maqam Bayati`)**:
   `Traditional Iraqi Hussaini Latmiya, heavy Karbalai Nazla style, Maqam Bayati, 60 BPM, authentic Iraqi colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, emotional weep cracks, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments`
3. **الموشح البحراني الرزين والطور الفائزي (`66 BPM — Maqam Hijaz`)**:
   `Traditional Bahrani Hussaini Tawshih and Faizi Latmiya, Maqam Hijaz, 66 BPM, authentic Bahrani colloquial dialect, wide majestic Baritone lead vocal, trembling microtonal vowel elongations, powerful high chest-voice climbs, synchronous 55Hz bare-palm chest thud, 260ms analog tape delay, 2.8s Matam hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments`
4. **بحر النصاري والنعي اللطمي الفراتي (`56 BPM — Maqam Lami`)**:
   `Traditional Southern Iraqi Euphrates Hussaini Latmiya, Bahr Al-Nassari style, Maqam Lami, 56 BPM, authentic Southern Iraqi colloquial dialect, raw grieving Baritone lead vocal, natural weep cracks, prolonged mournful vowel cries, slow heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, unison male Raddada response, Pure Acapella No Instruments`
5. **الگعدية العراقية والمتوسط السريع (`74 BPM — Maqam Kurd`)**:
   `Traditional Iraqi Hussaini Keadia Latmiya, Maqam Kurd, 74 BPM, authentic Iraqi colloquial dialect, high-power full-chest belted Baritone lead vocal, natural vocal rasp, emotional weep cracks, rhythmic 55Hz bare-palm chest-slap pulse, 250ms analog slapback echo, 2.5s Husseiniya hall reverb, energetic unison male Raddada choir response, Pure Acapella No Instruments`
6. **الزنجيل الموكبي العراقي/البحراني (`80 BPM — Maqam Hijaz`)**:
   `Traditional Hussaini Zanjeel procession chant, Maqam Hijaz, 80 BPM, authentic Iraqi and Bahrani colloquial dialect, thunderous heroic Bass-Baritone lead vocal, commanding epic chest projection, deep acoustic Dammam drum strikes locked with metallic shoulder Zanjeel chains and brass Tasa cymbals, 1.2s open-air street slapback echo, massive unison male Raddada response, No Melodic Instruments`
7. **الشور الحسيني الحماسي (`132 BPM — Maqam Kurd`)**:
   `Traditional Iraqi Karbalaei Shoor Latmiya, Maqam Kurd, 132 BPM, authentic Iraqi colloquial dialect, impassioned raspy Baritone lead vocal, powerful high chest-voice cries, rapid driving 55Hz bare-palm chest slaps, continuous deep male congregation rhythmic Hussain chant drone, 1.5s tight Husseiniya hall reverb, Pure Acapella No Instruments`
8. **النعي المنبري والموال الحر بلا إيقاع (`0 BPM Rubato — Maqam Saba`)**:
   `Traditional Iraqi and Bahrani Minbar Na'i vocal lament, strict Rubato free tempo with zero rhythmic grid, Maqam Saba, authentic Iraqi and Bahrani colloquial dialect, deep velvet mournful Baritone solo voice, raw weeping cracks, prolonged microtonal vowel cries, 450ms analog tape echo, 3.8s large Husseiniya cathedral reverb, Pure Solo Acapella No Percussion No Instruments`

### Workflow 3: Audio Montage and DSP Processing on User Voice Recordings

1. **Direct In-Sandbox Audio Montage**: Run `scripts/hussaini_dsp_montage.py`:
```bash
python3 hussaini_dsp_montage.py \
  --input "<input_wav_path>" \
  --output "<output_wav_path>" \
  --mode "<latm|zanjeel_iraqi|zanjeel_bahrani|shoor|bandari|mawal|nai>" \
  --bpm <bpm_value> \
  --maqam-drone "<saba|bayati|hijaz|lami|kurd|rast>"
```
2. **Post-Generation DSP Mastering in Google Flow Music (`audio__apply_effect` — Module 37)**:
   - Never put raw EQ/filter numbers (`+4.5dB at 2.5kHz`, `HPF at 85Hz`) inside the initial `Sound` box. Instead, apply them **after generation** via `Producer Chat`:
     `Apply audio__apply_effect on the generated clip: HighPass filter at 85Hz, AdvancedEqualizer (cut 450Hz by -2.5dB, boost mid 1200Hz by +1.5dB, boost high-mid presence 2500Hz by +4.5dB), Compressor (ratio 3:1, threshold -12dB), Reverb (room_size 0.55, wet mix 0.18), and Limiter at -1.0dB.`

## Gotchas

- **Google Flow Music Architecture (`New session` vs. `Spaces`)**:
  - **`New session` (`+ New session` / جلسة جديدة — The Direct Generative Audio Studio)**: Always use **`New session`** for generating, editing, remixing, or extending poems, Latmiyat, Mawals, and audio clips (`Lyrics` box + `Sound` prompt + `AI Producer` chat + `Remix/Extend` + `MP3/WAV/Stems` export).
  - **`Spaces` (`/library/spaces` — المساحات البرمجية والتفاعلية)**: Never use `Spaces` for direct song/Latmiya audio generation. Use `Spaces` **only** when the user explicitly wants to build a custom interactive web tool or mini-application (`App/Tool` via Vibe-coding inside the browser).
- **The 5 Golden Engineering Locks for Dialect, Melodic Balance, and Vocal Majesty in Flow Music**:
  1. **Concise 40-Word `Sound` Prompt with Explicit Dialect & Single Maqam Lock**:
     - Keep `Sound` between **40 and 50 pure English words**.
     - Always state `authentic Iraqi and Bahrani colloquial dialect` (or `authentic Iraqi colloquial dialect`) in the first line.
     - Lock **ONE single Maqam** (`Maqam Saba` or `Maqam Bayati`) in Stage 1 (`Rule B1`) — never list 3 Maqamat at once.
     - Never include transliterated Arabic terms (`maddat sawtiya`, `taqatee'`, `bahha`, `tarjee'`), raw EQ numbers (`+4.5dB at 2.5kHz`, `HPF at 85Hz`), or the word `tenor` inside `Sound`.
  2. **Strict Iso-Syllabic Balance in Stage 1 (`قفل تساوي التفعيلات الصارم في المرحلة الأولى`)**:
     - Format Stage 1 (`Root Track`) as **12 lines max (3 stanzas of 4 lines each)**.
     - All 12 lines (Mustahal + Stanzas + 4th-line anchor refrain) MUST share the **exact same prosodic meter and syllable count per hemistich**. Never mix long (14-syllable) and short (7-syllable) lines in Stage 1; introduce rhythmic/Gireez shifts only in Stage 2 (`Extend`).
  3. **Dialect Commitment Lock & Phonetic Colloquial Orthography (`قفل اللهجة الإملائي والوقف بالسكون`)**:
     - Never mix Fusha and Colloquial lines in Stage 1.
     - Write colloquial words phonetically (`شْلُونْ، چَبِدْ، گَلِبْ، عْيُونِچْ، بْچِيتْ، مْحَنِّيَه، وْگَفِتْ، يِمَّه، خُويَه، بْلَيَّاكْ، مَا ظَلْ`) and place a mandatory **Sukun (`ْ`)** or long open vowel (`ا، و، ي، ه`) at the end of words and hemistichs (zero Fusha case endings `ُ / ِ` or Tanween `ٌ / ٍ`).
  4. **Dynamic Poem-Specific Opening (`منع كليشيه آآآه يَا حُسَيْنَا .. آآآه يَا مَظْلُومْ`)**:
     - Never prepend generic repeated clichés like `آآآه يَا حُسَيْنَا .. آآآه يَا مَظْلُومْ` to poems. Start directly with the poem's own first hemistich containing natural long vowels (`يَا طَارِشْ الظَّعَنْ بْاللّٰه ..`, `بْاللّٰه اسْتَعِدِّي يَمّ البَنِينْ ..`).
  5. **100% Vocal Timbre Lock via `Producer Chat` + Golden Reference Clip `26bbb3d2-65f0-42c3-a167-37127631ef0a`**:
     - To lock the vocal timbre 100% onto the deep Iraqi-Bahrani Baritone reference in `Producer Chat`, use:
       `Register the lyrics using lyrics__register and create the track using audio__create_song referencing clip ID "26bbb3d2-65f0-42c3-a167-37127631ef0a" at 58 BPM with this sound prompt: "Traditional Iraqi and Bahrani Hussaini Latmiya, Thaqeel Faizi and Nazla style, Maqam Saba, 58 BPM, authentic Iraqi and Bahrani colloquial dialect, commanding deep resonant Baritone lead vocal, powerful high chest-voice climbs, natural vocal rasp, emotional weep cracks, heavy 55Hz bare-palm chest thud, 285ms analog tape echo, 3.2s Husseiniya hall reverb, wide unison male Raddada choir response, Pure Acapella No Instruments"`
- **Master Reference Clips in Flow Music (Acoustic Building Blocks)**:
  - `["34d27fb5-9fdc-4923-a260-9d14edba6313"]` (`عهد الدماء - نسخة ثانية`, parent of stem `785f8230-757e-49b1-a093-4883888cd1ef`)
  - `["26bbb3d2-65f0-42c3-a167-37127631ef0a"]` (`عهد الوفا V33.0 Grand Master`)
  - `["c5c2291b-5261-4358-a826-62df0f06a972"]` (`عهد الصدور`)
  - `["38e14d1c-f452-41b5-af3d-589a526961e8"]` (`يا حسين - الدمعة ماتروح`)
  - `["94098363-76cc-4bea-87c2-4bd0b1b4e649"]` (`عتاب الضعن`)
  - `["2ed9b98c-dac9-427d-809f-d1b202f82bb5"]` (`غريبه وحايره - بحر النصاري V36.0` — `seed: 562968419`, zero bracket tags in lyrics, 4-line alternating Mustahal `ABABABA`)
- **Zero English Characters & Zero Stage Directions in Parentheses inside `Lyrics`**: Keep `Lyrics` 100% pure Arabic (`[المُسْتَهَلّ]`, `[المَقْطَع الأَوَّل]`). Never put structural labels like `(الرابط والقفلة)` inside parentheses `(...)` because `Lyria` sings anything inside `(...)` as a choir response; use square brackets `[...]` or blank lines for structure, and reserve `(...)` strictly for actual choral words like `(مَوْلَايَ يَا حُسَيْنْ)`.
- **Never Put `--no <instruments>` Inside Flow Music's Positive `Sound` Box**: State only positive acoustic cues (`Pure Acapella No Instruments`).
