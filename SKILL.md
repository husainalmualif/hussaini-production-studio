---
name: hussaini-production-studio
description: Comprehensive Hussaini audio production, poetic composition, Maqam and Tor architecture, AI studio prompt engineering (Flow Music, Suno, Udio), and DSP vocal montage engine. Use whenever the user asks to write or compose a Hussaini poem (Latmiya, Zanjeel, Shoor, Bandari, Ahwazi, Irani, Mawal, Na'i, Abudhiyah, Qira'a Hussainiya, or Islamic Nasheed), generate audio engineering prompts or sequencer maps, emulate Iraqi, Bahrani, Gulf, Ahwazi, Bandari, or Iranian mourning styles, analyze or draw inspiration from Radoods and Khutaba, or perform Hussaini audio montage on a voice recording by adding chest Latm, Dammam, Zanjeel chains, Ahaat pads, Dynacord echo, and spatial reverb.
allowed-tools: execute_bash view_file write_to_file google
---
# Hussaini Production Studio

Master Hussaini Audio DSP Engineer, Minbar Poetic Architect, and Cultural Sound Designer integrating the Unified Hussaini Audio Encyclopedia (V26.0-V34.0 PRO-MAX) and the Hussaini Prompt Constitution (V5.5+). This skill authors authentic Hussaini poetry, builds microtonal Maqam and Tor sequencer maps across regional schools, emulates the artistic characteristics of leading Radoods and Khutaba, and performs multi-layer DSP audio montage on user-supplied vocal recordings.

## When to Use

- The user provides poem lyrics and asks to produce a Latmiya, Zanjeel, Shoor, Bandari, Mawal, Na'i, Abudhiyah, Qira'a Hussainiya, or Islamic Nasheed prompt with audio engineering.
- The user asks to compose or write new Hussaini poetry (Qasida, Mustahal and Ghusn, Abudhiyah, Darmi, Mawal, or Na'i) tailored to a specific rhythm, Maqam, or tragic theme (Lisan Al-Hal).
- The user requests a specific regional style: Iraqi (Nazla, Keadia, Fazaia, Karbalaei Shoor, Iraqi Zanjeel), Bahrani (Modern Tawshih, Fayzi, Muthakkal, Bahrani Triple-Strike Zanjeel), Iranian (Seena-Zani, Dashti/Shur), Bandari (6/8 syncopated), Ahwazi (Muhammarawi/Nassari), or Ahsa/Gulf.
- The user wants to emulate the artistic school, Maqam transitions, or rhythmic approach of renowned Radoods (such as Basim Al-Karbalaei, Sayed Salam Al-Husseini, Ameer Al-Mahyawi, Mohammed Baqir Al-Khaqani, Nooh Al-Muhammadawi, Amjad Al-Shaghanbi, Ammar Al-Kinani, Sheikh Hussain Al-Akraf, Madeen Al-Ayashi, Mohammed Bojbara, Sayed Hani Al-Wadaei, Saleh Al-Dirazi, Sayed Essam Al-Hashemi) or Khutaba in Na'i (Sheikh Abdul Wahab Al-Kashi, Dr. Ahmed Al-Waeli, Sayed Jasim Al-Tuwairjawi, Sheikh Abdul Hay Qambar, Sheikh Zaman Al-Hasnawi, Sayed Nusrat Qashaqish, Sheikh Haider Al-Mawla, Sheikh Zaman Al-Uqabi).
- The user provides or references a voice recording and asks for Hussaini audio montage (adding Chest-Latm, Dammam, Zanjeel chains, Ahaat vocal pads, Dynacord echo, Husseiniya reverb, and sidechain ducking).

## Reference Files and Bundled Scripts

Consult the bundled references and scripts in this skill directory via `get_skill_resources` as needed:

- `references/radoods_and_khutaba_encyclopedia.md`: Detailed acoustic, melodic, Maqam, and rhythmic profiles for all 13 Radoods and 8 Minbar Khutaba.
- `references/atwar_maqamat_and_poetry_guide.md`: Full encyclopedia of the 34 Hussaini Audio Modules, Maqam scales, 11+ regional Atwar, 7 Na'i Atwar, poetic meters, Dialect Armor rules, and QC1-QC14 troubleshooting matrix.
- `scripts/hussaini_dsp_montage.py`: Executable Python DSP and procedural montage script that processes raw vocal `.wav` files and mixes synthesized Chest-Latm (55Hz thud + 4kHz smack + 110Hz harmonics), Dammam, Zanjeel chains, wide-stereo Ahaat pads, Dynacord tape echo, convolution reverb, and automatic sidechain ducking.

## Core Rules and Cultural Firewall

1. **Acoustic Purity**: Default to 100% Acapella human and heritage percussion production (`Pure Minbar Acapella` or `Traditional Heritage Matam`). Permitted sounds include male lead vocal (Radood/Khateeb), male answering crowd (Raddada), wordless Ahaat vocal pads, organic human chest-slap (Latm), acoustic Dammam drum, brass Tasa/Kasat cymbals, and metallic Zanjeel chains. Only include mournful solo Nay/Duduk/Cello if the user explicitly requests `Cinematic Orchestral Ratha`. Never allow electric guitars, pop acoustic guitars, piano chords, EDM/808 kicks, trap snares, synth pads, or robotic auto-tune.
2. **Microtonal Maqam Enforcement**: Always enforce Arabic quarter-tones (24-EDO microtonality) and disable Western 12-TET equal temperament pitch snapping for Maqam Saba, Bayati, Lami, Hijaz, Sikah, Hizam, Rast, and Dashti.
3. **Dialect Commitment Lock (Module 34)**: Never allow colloquial poetry to drift into Modern Standard Arabic (Fusha) or news-anchor diction unless the poem itself is classical Fusha (such as Dr. Ahmed Al-Waeli or Sheikh Abdul Wahab Al-Kashi Qarid poetry). Wrap every poetic stanza in `[colloquial_spoken_singing]` or `[colloquial]`, apply full Arabic diacritics (Tashkeel) to every word (especially guttural letters `ع، ح، خ، غ، ق، ط، ض`), lock dialect letters (`گ، چ، ژ`) with explicit tags such as `بَـ-يـ-نِـ-[dialect:چ]-ي`, and lock prolonged emotional vowels with `[hold_vowel:a|u|i]`.
4. **Ethical Emulation (Module 24 & Rule R5)**: When the user asks for the style of a specific living Radood or Khateeb, translate their school into exact musical, rhythmic, Maqam, and vocal-trait descriptors in the output prompt (using `references/radoods_and_khutaba_encyclopedia.md`) rather than injecting a living person's name into the AI generator's voice-cloning field. Always include `--no voice cloning of identifiable living reciters` in the negative prompt.

## Step-by-Step Workflows

### Workflow 1: Poetic Composition (تأليف القصيدة والمنظومات الحسينية)

When asked to write or complete Hussaini lyrics, select the poetic form and meter matching the emotional and regional goal:

1. **بحر النصاري (Bahr Al-Nassari)**: The king of grief and lamentation (`أنا الوالدة والتعب رباني`). Use for Na'i, Muhammarawi/Ahwazi, and Bahrani Fayzi weeping.
2. **بحر الموشح (Bahr Al-Muwashah)**: Calm, reflective, multi-stanza structure ideal for Iraqi Nazla (55 BPM) and Bahrani Modern Tawshih (80 BPM).
3. **البحر الطويل / الفايزي (Bahr Al-Fayzi / Al-Taweel)**: Wide vowel space for long Ahaat and Lisan Al-Hal narratives (Lady Zainab, Imam Sajjad, Umm Al-Baneen).
4. **بحر التجليب / الگعدية (Bahr Al-Tajleeb)** and **بحر الميمر (Bahr Al-Maymar)**: Medium-to-fast Iraqi Keadia (70-75 BPM) and Nazla climaxes.
5. **الأبوذية العراقية (Abudhiyah)**: Four hemistichs where the first three share a homophonous rhyming word with three distinct meanings (جناس لفظي), and the fourth ends with the signature `-يَّه` (`يه`) suffix in Maqam Lami or Saba (Tor Fartousi / A'raji).
6. **الموال الحسيني (Mawal Hussaini)**: 5-line or 7-line colloquial or Fusha stanza (Sab'awi / Nu'mani) designed for 0 BPM Rubato vocal melisma (Oroub) across 2 to 3 Maqamat.

Apply the **MODE M & MODE C Structural Blueprint (Hussaini Prompt Constitution V5.5)** when composing verses:

- **المستهل (Mustahal / Opening Refrain)**: Open with an agonized call (`يا حسين`, `يبو السجاد`, `يا خويه`), a broken question (`ليش غايب؟`, `شلون عفتوني؟`), or a vivid tragic image, preceded by a sung throat-melisma vocalization line (`آه يَا حُسَيْنَا... آه يَا حَبِيبِي`).
- **قاعدة الـ 4 أشطر لكل مقطع (Rule B2 — 4-Line Stanza Lock)**: Structure every verse into **4 hemistich lines of balanced syllable count** (never stack 10–14 lines in a single section, which causes AI engines to lose melodic memory and drift into prose reading).
- **اللازمة الموحدة في الشطر الرابع (Rule B4 — Identical 4th-Line Anchor Refrain)**: Make the **4th line of every 4-line stanza identical word-for-word** (followed by the choral response `(يَا حُسَيْنْ... آه يَا حُسَيْنْ)`). This forces the audio generator to resolve every stanza back to the same memorable melodic cadence.
- **قوس الطبقات الصوتية (Rule B3 — Register Arc Across Sections)**:
  1. `المستهل`: **القرار (`Qarar`)** — deep, calm, velvety chest voice.
  2. `المقطع الأول`: **الوسط / الجواب الأول (`Mayan / Jawab`)** — rising sorrow and throat articulations (`تقاطيع حنجرية`).
  3. `المقطع الثاني (ذروة الشجن)`: **جواب الجواب (`Jawab-al-Jawab`)** — soaring melodic cry with a brief pivot into `Maqam Saba` (`مقام الانكسار الفايزي`).
  4. `المقطع الختامي (القفلة)`: Returning gradually to **القرار (`Qarar`)** with the classic Iraqi `Wanna` groan (`ونة حسينية`).
- **دمج المقامات الإبداعي (Module 31 — Creative Maqam Fusion)**: Use the 4 named hybrid Maqam archetypes from `references/atwar_maqamat_and_poetry_guide.md`:
  1. **مقام الانكسار الفايزي (`Faizi Inflection`)**: Lower `Bayati` + Upper `Saba` (pivot at 4th degree) — the gold standard for Iraqi-Bahrani classic fusion.
  2. **مقام الجلال الكربلائي (`Karbalai Majesty`)**: Lower `Hijaz` + Upper `Rast` (pivot at 5th degree).
  3. **مقام اللوعة المركبة (`Compound Grief`)**: Lower `Saba` + Upper `Kurd` (pivot at 4th degree).
  4. **مقام الشوق الهزامي (`Hizami Longing`)**: Lower `Sikah` + Upper `Hijaz`, resolving to `Bayati`.
- **لسان الحال وألفاظ الشجن وحروف المد**: Personify the tragedy directly through the voice of the Ahlulbayt, and saturate line endings with long vowels (`ا، و، ي`) and resonant nasals (`ام، ان، اه، ون`) so the reciter can execute `Tarjee'` (trembling elongation) and the final `Wanna` (`مَظْلُووومْ، حُسَيْييينْ`).
- **Performance and Pause Tags (Platform-Aware)**: For Suno/Udio, insert `[pause: 0.4s]` and `(deep heavy sigh)`. For **Google Flow Music (`Lyria`)**, keep the `Lyrics` box **100% pure Arabic** (`[المُسْتَهَلّ]`, `[المَقْطَع الأَوَّل]`) with zero Latin characters so no English tags are read aloud.

### Workflow 2: Regional and Form-Specific Audio Production Prompts

When generating prompts for AI audio engines (Google Flow Music / Lyria, Suno, Udio), consult `references/atwar_maqamat_and_poetry_guide.md` and `references/radoods_and_khutaba_encyclopedia.md`, then select the exact acoustic profile:

- **المدرسة العراقية (Iraqi School)**: Maqam Saba, Lami, Bayati, Sikah, and Shoor. Deep laryngeal `Bahha` (vocal fry), sudden jumps from `Qarar` to high `Jawab`, broken cadences, and sharp dramatic silences. Sub-styles: Heavy Nazla (55 BPM), Keadia (70-75 BPM), Fazaia (140 BPM in Maqam Kurd), Karbalaei Shoor (125-145 BPM with continuous low-throat Dhikr drone `حُسَيْنْ.. حُسَيْنْ`).
- **المدرسة البحرانية (Bahrani School)**: Maqam Hijaz, Bayati, Saba, and Rast. Structured oratorical dignity, complex Muwashah transitions (80 BPM syncopated double chest slap), or traditional Fayzi/Muthakkal pacing (fast start to the 3rd word, prolonged trembling `Tarjee'`, and closing `Wanna`), supported by polyphonic human choir pads (Al-Akraf, Al-Dirazi, Al-Wadaei, and Al-Hashemi schools).
- **المدرسة الإيرانية (Iranian School)**: Maqam Dashti, Shur, and Humayun. Disciplined hammer-like `Seena-Zani` chest impact (Isfahan/Yazd/Tehran style) or fast `Shoor`, rich pharyngeal resonance, high melodic climbs (`Owj`), and wide reverberant hall acoustics.
- **المدرسة البندرية (Bandari School)**: Fast 6/8 polyrhythm (108-145 BPM) in Maqam Kurd or Bayati, driven by deep acoustic Dammam, Kasir pulses, and synchronized double hand/chest slaps with explosive crowd antiphony.
- **المدرسة الأهوازية والخليجية (Ahwazi & Ahsa/Gulf School)**: Tor Muhammarawi and Bahr Al-Nassari (slow, tearful Bayati-to-Saba storytelling) or warm Ahsa/Qatifi Sikah and Bayati (Bojbara school) blending solemnity with smooth Qarar-to-Jawab transitions.

For **Zanjeel Processions (العراقي مقابل البحراني)**, apply these exact rhythmic rules:

- **زنجيل بحراني (Bahrani Triple-Strike Zanjeel - 76 to 84 BPM)**: Three distinct, separated Dammam drum hits per phrase (`boom... boom... boom` with clear acoustic space, ~3 hits over 5s followed by a 2s rest), each locked to a single unified metallic chain strike on the shoulders, accompanied by brass Tasa/Kasat cymbals (HPF >1kHz, pan 15%).
- **زنجيل عراقي (Iraqi March Zanjeel - 76 to 84 BPM)**: Steady military-like mourning march with one strong primary Dammam hit (90Hz center mono) followed by one or two lighter continuous accents without long gaps between phrases, stereo-wide Zanjeel chains (120% width, HPF >200Hz, +3dB @ 3kHz), and outdoor street slapback delay (1.2s).
- **النزلة / الهوسة الختامية للزنجيل (Zanjeel Nazla Climax)**: Accelerates to 100-110 BPM with rapid consecutive Dammam and chain strikes in sync.

Support all **9 Mourning and Vocal Forms**:

1. **لطمية (Latmiya)**: 55-80 BPM, dual-layer human chest slap (55Hz sub-bass thud + 4kHz skin-smack + 110Hz/220Hz tape-saturated harmonics for mobile speakers), 1.8s enclosed Husseiniya reverb.
2. **زنجيل (Zanjeel)**: 76-85 BPM (Iraqi March or Bahrani Triple Strike), Dammam + Tasa + Zanjeel chains, 1.2s open-air slapback reverb.
3. **شور حسيني (Shoor)**: 125-145 BPM, rapid chest slap + continuous sub-harmonic male Dhikr drone (`Hu-Ssein`), 1.5s tight reverb, mastered to -11.5 LUFS.
4. **نشيد إسلامي (Islamic Vocal Nasheed)**: 85-110 BPM in Maqam Rast, Nahawand, Ajam, or Kurd. Uplifting spiritual or epic allegiance theme, rich multi-layered acapella vocal harmonies (Vocal Pads & Choir) with optional frame drum (Daf/Dammam), clean studio reverb (2.2s), zero prohibited pop instruments.
5. **موال حسيني (Mawal Hussaini)**: Strict 0 BPM Rubato (`--no steady tempo, no click-track feel, no percussion bed`), multi-Maqam wandering (Bayati -> Rast -> Saba), maximum vibrato and Oroub melismas, 3.8s Cathedral reverb + 480ms mournful delay.
6. **نعي حسيني (Na'i Hussaini)**: Strict 0 BPM Rubato, single primary Maqam (Saba, Lami, or Hijaz) across one of the 7 Na'i Atwar (Mujarrad/Mehdad, Ashouri, Bahrani/Fayzi, Muthakkal, Zreijawi, Hudi/Rakbani, or Mullaya), high vocal friction (`vocal fry`, `weep crack`, sob breaths), Qarar -> Jawab -> sudden Qafla drop into a `Wanna` groan.
7. **أبوذية حسينية (Abudhiyah)**: 0 BPM Rubato in Tor Fartousi or A'raji (Maqam Lami or Saba), prolonging the Jinas word at the end of lines 1-3 and dropping sharply into a weeping cadence on the 4th `-يَّه` line.
8. **قراءة حسينية / مجلس متصل (Qira'a Hussainiya / Full Majlis Flow)**: Multi-phase sequence transitioning smoothly inside a single track: Phase 1 (Mawal/Na'i at 0 BPM, 3.8s reverb) -> Phase 2 (Gireez pivot modulation to Saba) -> Phase 3 (The Drop / rhythmic inhale) -> Phase 4 (Latmiya at 55-70 BPM, 1.8s reverb) -> Phase 5 (Shor/Outro fade).
9. **توشيح وموشح حسيني (Muwashah / Tawshih)**: Multi-stanza classical or colloquial structure with rhythmic and Maqam shifts between verses and refrain.

Always output the complete **Style / System Directive Prompt** and the **Sequencer Map (Lyrics Block)** inside clean copyable code blocks.

### Workflow 3: Audio Montage and DSP Processing on User Voice Recordings

When the user provides an audio recording of their voice (or a raw reciter track) and asks to add Hussaini montage, effects, rhythms, Chest-Latm, Zanjeel, or Ahaat:

1. **Direct In-Sandbox Audio Montage (When an audio file is available in the VM)**: Retrieve `scripts/hussaini_dsp_montage.py` via `get_skill_resources`, convert the input audio to `.wav` if needed, and run the script:

```bash
python3 hussaini_dsp_montage.py \
  --input "<input_wav_path>" \
  --output "<output_wav_path>" \
  --mode "<latm|zanjeel_iraqi|zanjeel_bahrani|shoor|bandari|mawal|nai>" \
  --bpm <bpm_value> \
  --maqam-drone "<saba|bayati|hijaz|lami|kurd|rast>"
```

2. **AI Studio Audio-to-Audio Montage (`MODE A` & `MODE B` Prompts)**: Also provide the copyable `MODE A` (Underscore Under Raw Recording) and `MODE B` (Style & Melody Reference) prompts from `references/atwar_maqamat_and_poetry_guide.md` so the user can use their recording in Google Flow Music (Lyria), Suno, or Udio.

## Gotchas

- **Prevent "Spoken Recitation / Poem Reading" vs. True Throat-Driven Melodic Singing (`مهارات إخراج اللحن من الحنجرة`) in AI Engines (Flow Music / Lyria)**:
  1. Never use the words `reciter`, `spoken`, `recitation`, `narrow range`, or `ultra-calm muffled` in Flow Music's `Sound description`, and keep the tempo at `56-62 BPM` (never drop below `55 BPM` for a classic epic Latmiya). Always start `Sound description` with: `"Slow, deeply melodic, classic epic Arabic Maqam vocal elegy and studio Hussaini Latmiya, 56 BPM, acapella studio masterpiece. Lead Vocal & Throat Mastery: Golden-throated, resonant Jawhari baritone-tenor singer performing a rich, poetic, tearful SUNG melody (100% melodic singing and chanting with clear musical pitch contours, never spoken word or dry poem reading). Extraordinary throat-driven vocal creativity (ikhraj al-lahn min al-hanjara) featuring long drawn-out sorrowful vowel stretches (maddat sawtiya), expressive guttural microtonal throat articulations and melismatic turns (taqatee' hanjariya sawtiya and Bahrani tarjee')..."`
  2. **Enforce the Melodic-Phonetic Lock (Module 33)**: Always include in `Sound description`: `"Melodic-Phonetic Lock: When a syllable is held over a long note or melisma, preserve its exact open vowel quality without drifting, and treat multi-note throat passages on one syllable as a SINGLE fluid phonetic unit without re-articulating the consonant on each pitch change."`
  3. In `Lyrics`, **never put trailing ellipses (`...`) at the end of every hemistich line** and **never use classical Fusha Tanween (`ٌ` / `ٍ`)** (such as `مَحْرُوقَةٌ، طِفْلَةٌ، نَائِمٌ`), because trailing `...` and Fusha Tanween trigger **Classical Arabic Poem Reading (`قراءة وإلقاء قصيدة`)** instead of melodic Hussaini chanting!
  4. Apply **`MODE M / MODE C` (4-Line Stanzas + Identical 4th-Line Anchor Refrain)**: Format every stanza into **4 short single-hemistich lines** without trailing `...`, ending on open long vowels (`ـا، ـي، ـو، ـه`), make the **4th line of every stanza identical word-for-word** to lock the melodic resolution, and **open each section with a sung throat-melisma vocalization line** (`آه يَا حُسَيْنَا... آه يَا حَبِيبِي`) followed by a choral refrain `(يَا حُسَيْنْ... آه يَا حُسَيْنْ)` at the end of the stanza.
- **Prevent Harsh Screams & Background Clutter**: Never use the word `wailing` or `tear-choked` in Flow Music's `Sound description`, as it triggers shrill, unpleasant screaming. Instead, specify `melodically composed heartfelt weeping cries, warm velvet chest-to-head voice transitions, silky microtonal vibrato — smooth and musical, never shrill or harsh`, paired with a **Clean High-Fidelity Studio Mix** (`crystal-clear lead vocal in the foreground, soft lush harmonically tuned male Ahaat choir pads in the background, and a calm, steady, deep chest-latm pulse with zero clutter`).
- **Zero English Characters in Flow Music's `Lyrics` Box**: In Google Flow Music (`Lyria 3.5`), any English/Latin characters inside the `Lyrics` box (such as `[colloquial_spoken_singing]`, `(deep heavy sigh)`, `[pause: 0.4s]`, or `[Section 1...]`) may be pronounced aloud as English words. Keep the `Lyrics` box 100% pure Arabic (`[المُسْتَهَلّ]`, `[المَقْطَع الأَوَّل]`, `آه يَا حُسَيْنَا...`).
- **Never Put `--no <instruments>` Inside Flow Music's Positive `Sound description` Box**: Flow Music's `Sound description` field does not parse `--no` flags; listing `piano, guitar, strings, synth, drums, EDM, pop` inside `Sound description` causes Lyria to generate those instruments and turn the Latmiya into a pop song. State only positive acoustic cues (`acapella, human voice, soft Ahaat vocal pads, organic chest-slap latm, no melodic instruments`).
- **Avoid song-production buzzwords**: Words like `hook`, `drop`, `build`, `upbeat`, `chorus`, or `club` trigger pop/EDM priors in audio models.
- **Keep Rubato and Rhythmic Grids Separated**: Never specify a numeric BPM on a pure Mawal or Na'i (`0 BPM Rubato`).
