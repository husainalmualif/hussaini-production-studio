# Module 71 — V56.0 Four-Axis Modern Latmiya Sound Engineering, 6-Experiment Multi-Method Bahrani/Iraqi Lab (`NC23–NC25`), Golden Studio `60 BPM` Formula & Vocal-Pulse-Locked DSP

> **Parent Module:** `SKILL.md` (`V56.0 OMNI-ARCHITECT`)  
> **Builds Upon:** `module_70_v55_tabaa_al_bashar_7exp_lab_5stage_router_and_3poem_benchmark.md` (`V55.0`, `NC18–NC22`) & `module_69_v54_175_mp3_acoustic_lab_24edo_and_studio_dsp.md` (`V54.0`)  
> **Primary Runtime:** `scripts/hussaini_dsp_montage.py`

---

## 1. The 4-Axis Sound & Instrument Engineering Specification (`نص البث: هندسة الصوت والآلة في اللطمية الحسينية الحديثة`)

Codified in `MODERN_LATMIYA_FOUR_AXES_V56` inside `scripts/hussaini_dsp_montage.py`, modern and traditional Husseini Latmiya production is organized across **4 Complementary Engineering Axes** (selectable during Pre-Generation Consultation or Auto-Pilot routing):

| Axis ID | Arabic Title (`محور هندسة الصوت`) | Core Acoustic & Instrumental Elements | `Flow Music (Lyria 3.5)` Prompt Key & Local `20-Mode` DSP Route |
| :--- | :--- | :--- | :--- |
| **`Axis 1` (الركيزة الأساس)** | **الصوت البشري، الكورال الهارموني، وإيقاع الجسد** | 1. **صوت الرادود** في المقامات الحزينة (`الصبا، البيات، الحجاز، اللامي`).<br>2. **الكورال البشري (الردادة):** طبقات صوتية متناغمة (`Harmony`) وهمهمات خلفية (`آهات`) تملأ الفراغ الصوتي وتمنح القصيدة عمقاً درامياً.<br>3. **إيقاع اللطم الجسدي:** ضربات الأكف على الصدور كعينات إيقاعية أساسية (`< 460 Hz`). | **Prompt:** `golden_studio_iraqi_60bpm_saba_bayati_v56` / `golden_studio_bahrani_60bpm_saba_bayati_v56` / `pure_acapella_weeping_noha_auto_bpm_saba_lami_v55`<br>**DSP Mode:** `thaqeel_muwazza`, `bahrani_muthakkal`, `vocal_pure_master` + `build_vocal_pulse_locked_chest_latm()` |
| **`Axis 2` (المواكب التقليدية)** | **الآلات التقليدية في المواكب الحسينية** | 1. **الطبول والدمامات** لتنظيم مسير المعزين وتوحيد حركة اللطم أو الزنجيل.<br>2. **الصنوج النحاسية (`Tasa / Cymbals`)** المرافقة للطبول في المواكب.<br>3. **الأبواق النحاسية (`الترامبيت`)** في مواكب العزاء لإصدار نغمات حزينة أو حماسية مهيبة. | **Prompt:** `karbalai_mawkib_dammam_tasa_brass_76bpm_hijaz_v56`<br>**DSP Mode:** `mawkib`, `zanjeel`, `ashura_heavy`, `fazzaiya` |
| **`Axis 3` (التسجيلات الحديثة)** | **الآلات الوترية والنفخية في التسجيلات الحديثة** | 1. **الناي (`Ney`)** في المقدمات والفواصل لمحاكاة صوت النحيب والشجن.<br>2. **التشيلو (`Cello`)** بطبقاته المنخفضة الدافئة لإعطاء ثقل درامي.<br>3. **الكمانات (`Violins`)** لرسم جمل لحنية تزيد التأثير العاطفي، **مع الحرص التام على الابتعاد عن الإيقاعات الراقصة أو الطربية**. | **Prompt:** `modern_studio_ney_cello_strings_60bpm_saba_bayati_v56`<br>**DSP Mode:** `modern_studio_ney_strings`, `studio_arranged` |
| **`Axis 4` (الهندسة الإلكترونية والمؤثرات)** | **الهندسة الإلكترونية والمؤثرات الصوتية السينمائية** | 1. **التوزيع الرقمي (`Sub-Bass & Pads`)** المقفل تلقائياً على طبقة الرادود (`estimate_singer_tonic_root_hz`).<br>2. **المؤثرات الصوتية التاريخية (`Foley`):** صليل السيوف (`swords`)، صهيل الخيول (`horses`)، هبوب الرياح (`wind`)، أصوات النيران (`fire`)، ماء الفرات (`water`)، وأجواء المعركة (`battlefield`).<br>3. **إيقاعات اللطم الإلكترونية النقية** المشتقة من نبض الرادود والكورال (`build_vocal_pulse_locked_chest_latm`). | **Prompt:** `cinematic_karbala_foley_sub_pads_58bpm_saba_lami_v56`<br>**DSP Mode:** `cinematic_foley_latmiya`, `heavy_clip` (`--foley wind\|water\|horses\|swords\|fire\|battlefield`) |

---

## 2. Reverse-Engineering the User's Saved Favorite Track (`لحن وطور مميز.mp3`, `04:48`)

Auditing the user's saved reference file `Desktop\لطميات تجربة\لحن وطور مميز.mp3` (`288.62s`, `f0 = 207.93 Hz`, `Maqam Lami = 0.861`, `sub = -15.32 dB`, `core = -5.77 dB`) and tracing its exact provenance to the `V50.1` production of «صوت أم البنين يصيح» revealed **why** it achieved the deepest Husseini melody and solemn Tor:

1. **Autoregressive Maqam Conditioning in the First 15 Seconds (`Axis 3 & Axis 4` Intro):**
   - In `Lyria 3.5`, the first 15–20 seconds of audio establish the harmonic scale and microtonal `24-EDO` pitch center for the entire 3-to-5-minute generation.
   - When `V51–V55` enforced a global `"Pure Acapella No Instruments, zero pads, zero strings"` ban across all prompts, `Lyria 3.5` lost its harmonic Maqam floor and frequently defaulted to either dry Western church/nasheed chanting or 78 seconds of unpitched theatrical solo gasping (`Exp-2` `0:00–1:18`).
   - By contrast, the **`V50.1 / V56.0` Golden Studio `60 BPM` Formula** (`60 BPM`, `Maqam Saba and Bayati`, `"warm deep emotional Arabic male baritone lead vocal, controlled dignified middle-register mournful delivery, no high-pitch screaming, responsive male chorus chanting in unison on refrain lines, deep slow resonant bare chest thumping rhythm at 60 BPM, solemn cavernous Husseiniya reverberation"`) allows `Lyria 3.5` to lay down a solemn minor/Maqam atmospheric foundation (`Sub-Bass + Cello/Ney Pad`) that locks the singer and unison choir into authentic **Maqam Lami / Saba / Bayati** (`f0 = 180.5–208.6 Hz`).
2. **Replacing `"chest-beat"` with `"bare chest thumping"` + Local Whip-Snap Suppression:**
   - The only flaw in the original `V50.1` prompt was the hyphenated word `"chest-beat"`, which caused `Lyria 3.5` to layer a sharp `1.85–9.8 kHz` studio rimshot/whip-snap over the low chest thud. Replacing `"chest-beat"` with `"bare chest thumping"` in `golden_studio_iraqi_60bpm_saba_bayati_v56` & `golden_studio_bahrani_60bpm_saba_bayati_v56` and running `suppress_whip_snap_transients()` in local DSP preserves the rich `50–150 Hz` chest thump while softening sharp upper-mid snaps.

---

## 3. The 6 Multi-Method Live `Flow Music (Lyria 3.5)` Experiments (`Exp-1` to `Exp-6`) & Laws `NC23–NC25`

Across **Bahrani** («صورة جسد عالغبرة» — نادر التتان) and **Iraqi** («فلسفة الانتظار — اترجمها أم البنين» — حيدر تركي الكربلائي), 6 live experiments tested 4 distinct production methodologies:

| Exp ID | Poem & Dialect | Production Methodology | Clip ID & Duration | `f0` / Maqam | `Sub (45–95Hz)` | Honest Ear-Audit Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **`Exp-1`** | «صورة جسد عالغبرة» (**Bahrani**) | **Method A:** Pure Vocal (`BPM=Auto`, `pure_acapella`) + Local Pulse-Locked `< 460 Hz` Chest Latm (`199` hits) | `d903464c` (`180.0s`) | `191.5 Hz` (`saba/bayati`) | `-34.85 dB` raw -> **`-16.8 dB`** mastered | Authentic weeping Bahrani vocal + organic chest latm (`bahrani_sowrat_jasad_v56_latm.mp3`), but `آهْ هَذَا...` in Kasra caused trailing `-i` release (`التَّرَايِبِي`). |
| **`Exp-2`** | «فلسفة الانتظار» (**Iraqi**) | **Method A:** Pure Vocal (`BPM=Auto`) + `آااه .. يَا أُمَّ البَنِينْ` line + `"weeping vocal grief breaks"` | `f057b7dc` (`180.0s`, cut `1:18–2:44` = `86.0s`) | `189.2 Hz` (`bayati/lami`) | `-41.10 dB` raw -> **`-17.2 dB`** mastered | First `78s` collapsed into theatrical solo gasping; **however, `1:18–2:44` (`iraqi_intidhar_v56_latm.mp3`, `88` hits) achieved extraordinary unison Raddada + `آه.. هُو..` choir ostinato pad!** |
| **`Exp-3`** | «صورة جسد عالغبرة» (**Bahrani**) | **Method B:** `Remix > Cover` (`Strength=0.45`) on `Exp-2` choir seed with full explicit martyrdom lyrics (`مَذْبُوحْ`) | Blocked at `43%` | — | — | **Discovery (`NC25`):** `Remix > Cover` (`Edit Lyrics`) runs a strict LLM text filter on `Instruction` that rejects explicit gore/martyrdom words (`مَذْبُوحْ / ذَبَحْ`) which pass in `Compose > Lyrics`. |
| **`Exp-4`** | «صورة جسد عالغبرة» (**Bahrani**) | **Method C:** Uploaded Local Audio Reference (`+ -> Upload > Audio` `melody_ref.mp3` `55s`) + `Cover` (`Strength=0.42`) | `7ab9a2ac` (`54.7s`) | `186.4 Hz` (`bayati`) | `-38.90 dB` | Confirmed custom external audio upload works (`melody_ref.mp3` chip attached) and locks output length to reference length (`55s`), though choir texture was thinner than `Exp-2`. |
| **`Exp-5` ★** | «فلسفة الانتظار» (**Iraqi**) | **Method D (Golden Studio `60 BPM`):** `golden_studio_iraqi_60bpm_saba_bayati_v56` + Direct Mustahall (`NC23`) + Local `V56.0` Master (`104.32 Hz` tonic pad) | `1b5ec43b` (`180.0s`) | **`208.64 Hz`** (`lami = 1.046`) | `-14.96 dB` | **Matches `لحن وطور مميز.mp3` (`207.93 Hz`) within `0.7 Hz`!** Deep mournful studio intro, zero theatrical gasping, strong unison choir & solo baritone (`v56_iraqi_intidhar_master.mp3`). Taught `NC24` (`أُمّ البَنِينْ` without Damma). |
| **`Exp-6` ★** | «صورة جسد عالغبرة» (**Bahrani**) | **Method D (Golden Studio `60 BPM`):** `golden_studio_bahrani_60bpm_saba_bayati_v56` + Direct Mustahall (`NC23`) + Local `V56.0` Master (`90.25 Hz` tonic pad) | `5b20fd78` (`174.6s`) | **`180.49 Hz`** (`lami = 0.855`) | `-8.21 dB` | **Best Overall Full-Length Studio Bahrani Latmiya (`v56_bahrani_sowrat_master.mp3`)!** Deep `180.5 Hz` baritone, powerful unison choir, `100%` clean `التَّرَايِبْ / لَوَاهِبْ` (cured trailing `-i`), and moving final `2:02–2:55` chorus. |

### Permanent Negative Constraints `NC23–NC25`

1. **`NC23` — Direct Rhythmic Mustahall Entry & Anti-Theatrical-Gasping Law:**
   - Never start `[المُسْتَهَلّ]` with a standalone `آااه .. يَا أُمَّ البَنِينْ` or `آااه .. مَولَايْ` line when using grief descriptors (`"Devastated ... weeping ... vocal grief breaks"`): `Lyria 3.5` interprets an opening `آااه ..` line as an un-timed solo theatrical crying improvisation (`78s` in `Exp-2`).
   - Always start `[المُسْتَهَلّ]` **directly with the parenthesized poetic refrain couplet** `(صُورَة جَسَدْ عَالْغَبْرَه...)` and use `"warm deep emotional Arabic male baritone lead vocal, controlled dignified middle-register mournful delivery, no high-pitch screaming"`.
2. **`NC24` — Colloquial Un-Damma'd `أُمّ` Lock, Pre-`الـ` Bahrani `عَلَى` Liaison Lock & Kasra `آهْ` Removal:**
   - Never place a Fusha case Damma on `أُمُّ البَنِينْ` or `أُمُّ الأَرْبَعَه` inside Iraqi/Bahrani colloquial lyrics: in `Exp-5`, `Lyria 3.5` stretched the Damma on `أُمُّ` into an extra syllable (`"أُمُورْ أُمُّ البَنِينْ"`), whereas `أُمّ البَنِينْ` (with Shadda only, no Damma) in `Exp-2` was sung `100%` cleanly (`إِتْرَجِمْهَا أُمّ البَنِينْ`). `detect_and_shape_dialect()` now normalizes `أُمُّ البَنِينْ -> أُمّ البَنِينْ` and `أُمُّ الأَرْبَعَه -> أُمّ الأَرْبَعَه` automatically.
   - Before `الـ`, always normalize Bahrani `عَلَه التَّرَايِبْ` to `عَلَى التَّرَايِبْ` so `Lyria 3.5` never pronounces the `ـه` as `/h/` (`"عَلَاهِ التَّرَايِبْ"` at `1:53` in `Exp-6`).
   - In 3-line Kasra (`[الكَسْرَة]`), never insert an extra exclamatory `آهْ` before `هَذَا الحُسَينْ / هَذَا الشَّمِرْ`: removing `آهْ` in `Exp-6` completely cured the trailing `-i` release vowel (`التَّرَايِبِي / لَوَاهِبِي`) heard in `Exp-1`.
3. **`NC25` — `"chest-beat"` Token Firewall, `Remix > Cover` Moderation Firewall & Uploaded Audio Reference Law:**
   - Replace hyphenated `"chest-beat"` with `"bare chest thumping"` in all `Compose > Sound` prompts so `Lyria 3.5` does not trigger a high-frequency studio rimshot/clap on beat 1.
   - Because `Remix > Cover` (`Edit Lyrics`) applies a stricter text moderation filter on the `Instruction` payload than `Compose > Lyrics` (`Exp-3` blocked at `43%` on `مَذْبُوحْ`), always generate explicit Karbala martyrdom poems directly via **`Compose > Lyrics`** (`Method D` or `Method A`), or soften explicit gore tokens during `Cover`.
   - When uploading a local reference MP3 via `+ -> Upload > Audio`, remember that `Flow Music` locks the generated Cover track's duration to the uploaded reference clip's duration (`55s` in `Exp-4`).

---

## 4. Local Studio DSP Engine Upgrades (`V56.0 OMNI-ARCHITECT` — `20` Modes)

1. **`estimate_singer_tonic_root_hz(mono, sample_rate, fallback_hz=110.0)`:**
   - Extracts the singer's actual median fundamental frequency `med_f0` via `_extract_24edo_maqam_profile()` and octave-folds it into the `[73.0, 146.0] Hz` bass register (`90.25 Hz` for Bahrani `180.49 Hz`; `104.32 Hz` for Iraqi `208.64 Hz`).
   - Both `synthesize_ahaat_drone(..., tonic_hz=singer_tonic_hz)` and `synthesize_vocal_synth_strings_pad(..., tonic_hz=singer_tonic_hz)` automatically scale their `24-EDO` Maqam intervals to the singer's exact tonic, eliminating key clashes (`نشاز الطبقة`) between the vocal and the local Ahaat/Cello pad.
2. **`build_vocal_pulse_locked_chest_latm(mono, sample_rate, mode="thaqeel_muwazza", target_bpm=60.0)`:**
   - Instead of slapping a rigid mathematical metronome grid across rubato or breathing vocal phrases, detects the actual `105–420 Hz` vocal/Raddada phrase energy peaks and aligns `< 460 Hz` low-passed bare-palm chest impacts (`synthesize_chest_latm_hit` + `460 Hz` 2nd-order Butterworth LPF) directly to the singer's natural cadence (`199` hits on Bahrani `Exp-1`, `88` hits on Iraqi `Exp-2`).
3. **`suppress_whip_snap_transients(signal, sample_rate)`:**
   - Dual-band fast-attack (`2.5 ms`) envelope suppressor across `1850–9800 Hz` that tames sharp AI rimshots, claps, and whip-like transients while leaving `50–150 Hz` deep chest thuds and `250–1750 Hz` Arabic vocal formants completely untouched.
4. **Expanded 6-Type Historical Karbala Foley (`synthesize_contextual_foley`) & 2 New DSP Modes (`20` Modes Total):**
   - Added `"swords"` (metallic Karbala sword clashes `1.4–5.2 kHz`), `"fire"` (tent-fire rumble `120–580 Hz` + crackle spikes `1.8–5.8 kHz`), and `"battlefield"` (combined desert wind + distant fire + subtle sword clashes) alongside `"wind"`, `"water"`, and `"horses"`.
   - Added `--mode modern_studio_ney_strings` (`Axis 3`) and `--mode cinematic_foley_latmiya` (`Axis 4`) to `SUPPORTED_DSP_MODES` (`20` modes total).
