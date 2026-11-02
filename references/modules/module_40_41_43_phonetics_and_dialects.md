# Modules 40, 41 & 43: Dialectal Tanween, Anti-Slurring Word Separation & Morphological Dialect Engine (V45.0 OMNI-ARCHITECT)

---

## 1. Module 40: Dialectal & Prosodic Tanween (Nunation) Compiler (`مُعَالِجُ التَّنْوِينِ اللَّهْجِيِّ وَالعَرُوضِيّ`)

In Arabic speech-to-singing and neural audio synthesis (`Google Flow Music`), raw orthographic **Tanween** (`ـً / ـٍ / ـٌ`) causes two severe acoustic defects if left uncompiled:
1. **End-of-Line Hard-N Clipping:** Placing `ـً / ـٍ / ـٌ` at the end of a hemistich or rhyme word forces the TTS engine to pronounce a dry, clipped `/n/` consonant instead of a resonant open vowel (`إِشْبَاع`) or clean cutoff (`سُكُون`), destroying the rhyme (`القَافِيَة`).
2. **Colloquial Linker Neglect (`تَنْوِينُ العِوَضِ اللَّهْجِيّ`):** In Iraqi and Bahrani colloquial poetry, an indefinite noun followed by a descriptive verb or adjective (e.g., `عَيْنٍ تِسِيلْ`, `جَرْحٍ چِبِيرْ`, `كِلٍّ يِنَادِي`) relies on an audible **phonetic Nunation linker (`ـِنْ`)** to maintain the prosodic meter (`الوَزْن`). If omitted or left as a bare diacritic, the AI drops a syllable and breaks the rhythm.

### 1.1 The 3 Mandatory Laws of Module 40
| Position & Register | Acoustic Rule | Raw Input (Forbidden / Unstable) | Compiled Phonetic Output (Locked) |
| :--- | :--- | :--- | :--- |
| **Rule 40-A: End-of-Line / Rhyme (`أَوَاخِرُ الأَبْيَاتِ وَالقَوَافِي`)** | **NEVER** leave `ـً / ـٍ / ـٌ` at the end of a line. Convert Accusative (`ـاً`) to open Alif (`ـَا`), and convert `ـٍ / ـٌ` to dead Sukun (`ـْ`). | `سَقَطَ جَسَداً` / `بِلَا قُبُورٍ` | `سَقَطَ جَسَدَا` / `بِلَا قُبُورْ` |
| **Rule 40-B: Mid-Line Colloquial Linker (`التَّنْوِينُ اللَّهْجِيُّ الرَّابِط`)** | Write colloquial mid-line `تنوين الكسر` explicitly as a phonetic Nun + Sukun (`ـِنْ`) when linking a noun to its modifier in Iraqi/Bahrani verse, **without** corrupting already-vocalized following verbs or vocatives (`يَا`). | `عينٍ تسيل` / `جرحٍ چبير` / `كلٍ ينادي` | `عَيْنِنْ تِسِيلْ` / `جَرْحِنْ چِبِيرْ` / `كِلِّنْ يِنَادِي` |
| **Rule 40-C: Mid-Line Fusha Prosodic Tanween (`التَّنْوِينُ الفَصِيحُ الوَصْلِيّ`)** | In Classical Fusha (`الشِّعْرُ الفَصِيح`), mid-line Tanween required by the `تَفْعِيلَة` is written phonetically as `ـَنْ / ـِنْ / ـُنْ` ONLY inside the line, never at the pause. | `جِسْماً عَلَى الثَّرَى` / `دَامٍ بِلَا قُبُورٍ` | `جِسْمَنْ عَلَى الثَّرَى` / `دَامِنْ بِلَا قُبُورْ` |

---

## 2. Module 41: Space-First & Optional-Tatweel Anti-Slurring Engine (`مُحَرِّكُ فَصْلِ الكَلِمَاتِ وَمَنْعِ الإِدْغَامِ العَشْوَائِيّ`)

Neural G2P (Grapheme-to-Phoneme) tokenizers frequently slur attached Arabic vocatives (`يا`), prepositions (`بـ / عـ / لـ`), and interrogative clitics (`شـ`) into a single garbled token when fed as compound strings.

### 2.1 Space-First Default (`use_tatweel=False`) vs. Optional Tatweel (`use_tatweel=True`)
By default (`use_tatweel=False`), the compiler uses **clean space separation** (`بِ غُرْبِتِي`, `لِ حْسَيْنْ`) so zero `ـ` (`Tatweel / U+0640`) characters enter the G2P tokenizer (preventing subword fragmentation in neural TTS). If visual kashida styling is desired for human sheet music, pass `--use-tatweel` (`use_tatweel=True`).

### 2.2 Mandatory De-Cliticization & Orthographic Gaf Normalization Table
| Attached / Raw Input | Default Space-First Output (`use_tatweel=False`) | Optional Tatweel Output (`use_tatweel=True`) | Acoustic Justification |
| :--- | :--- | :--- | :--- |
| `ياحسين` / `وياحسين` | `يَا حْسَيْنْ` / `وَ يَا حْسَيْنْ` | `يَا حْسَيْنْ` / `وَ يَا حْسَيْنْ` | Prevents swallowing the long `ا` of the vocative `يَا`. |
| `يبوفاضل` / `يبو فاضل` | `يَا بُو فَاظِلْ` (Iraqi) / `يَا بُو فَاضِلْ` | `يَا بُو فَاظِلْ` / `يَا بُو فَاضِلْ` | Restores the open vocative vowel and separates `بُو` from `فَاضِلْ`. |
| `يايمه` / `يافاطم` / `يحبيبه` | `يَا يُمَّه` / `يَا فَاطِمْ` / `يَا حَبِيبَه` | `يَا يُمَّه` / `يَا فَاطِمْ` / `يَا حَبِيبَه` | Separates attached colloquial vocatives cleanly. |
| `عالباب` / `عالرمضا` / `عالشاطي` | `عَلَى البَابْ` / `عَلَى الرَّمْضَه` / `عَلَى الشَّاطِي` | `عَلَى البَابْ` / `عَلَى الرَّمْضَه` / `عَلَى الشَّاطِي` | Expands contracted `عَالـ` so the AI articulates both syllables smoothly. |
| `للذبحوا` / `للناس` | `لِلْ ذَبْحَوْا` / `لِلْ نَاسْ` | `لِلْ ذَبْحَوْا` / `لِلْ نَاسْ` | Prevents attached `للـ` relative/prepositional slurring. |
| `شصار` / `شنگول` / `شيجيبه` | `إِشْ صَارْ` / `إِشْ نْگُولْ` / `إِشْ يْجِيبَه` | `إِشْ صَارْ` / `إِشْ نْگُولْ` / `إِشْ يْجِيبَه` | Separates the Iraqi/Gulf interrogative `شـ` into a distinct phonetic syllable `إِشْ`. |
| `بغربتي` / `بضلوعي` / `ابأرض` | `بِ غُرْبِتِي` / `بِ ظْلُوعِي` / `بِ أَرْضْ` | `بِـ غُرْبِتِي` / `بِـ ظْلُوعِي` / `بِـ أَرْضْ` | Detaches single-letter prepositions with clean space by default. |
| `اشكَد` / `كَوه` / `اشهكَ` / `كَدامي` | `إِشْگَدْ` / `گُوَّه` / `أَشْهَگْ` / `گِدَّامِي` | `إِشْگَدْ` / `گُوَّه` / `أَشْهَگْ` / `گِدَّامِي` | **Iraqi Orthographic Gaf Normalization (`كَـ -> گ`):** Converts Iraqi keyboard shorthand (`Kaf + Fatha + Tatweel`) directly into phonetic `گ` (`U+06AF`) so the AI never pronounces a classical `/k/` or fragments on `ـ`. |

---

## 3. Module 43: Word-Boundary Morphological Dialect Shaper (`مُحَرِّكُ التَّشْكِيلِ الصَّرْفِيِّ اللَّهْجِيّ`)

Beyond simple consonant swaps (`گ / چ`), **Bahrani**, **Iraqi**, and **Neutral Iraqi-Bahrani Hybrid** dialects differ fundamentally in **internal vowel epenthesis (`كَسْرُ أَوْ ضَمُّ الوسط`)**, **suffix vowels**, and **melodic ornamentation**:

### 3.1 Prefix-Aware Token Boundary Shaping
To guarantee zero substring corruption (e.g., never turning `مُقَاتِلْ` into `مُگَاتِلْ` or corrupting `أَقْبَلَ`), the morphological shaper operates strictly on **whitespace-delimited word tokens**, decomposing prefixes (`الـ / وَ / بِـ / كَـ / لِـ`) before matching the stem.

### 3.2 Comparative Dialectal Morphology Matrix
| Linguistic Feature | Iraqi Dialect (`اللهجة العراقية`) | Bahrani Dialect (`اللهجة البحرانية`) | Neutral Iraqi-Bahrani Hybrid (`فصحى الوسط الحسيني الميسرة`) |
| :--- | :--- | :--- | :--- |
| **Epenthetic Vowel in `فَعْل` Nouns (`قلب / صبر / جمر / درب / قبر`)** | **Damma (`ضَمُّ الحَرْفِ الثَّانِي`)** before labials/liquids: `گَلُبْ`, `صَبُرْ`, `جَمُرْ`, `دَرُبْ`, `گَبُرْ` | **Kasra (`كَسْرُ الحَرْفِ الثَّانِي`)** with front-vowel harmony: `گَلِبْ`, `صَبِرْ`, `جَمِرْ`, `دَرِبْ`, `گَبِرْ` | **Clean Sukun or Standard Vowel:** `قَلْبْ`, `صَبْرْ`, `جَمْرْ`, `دَرْبْ`, `قَبْرْ` |
| **Euphrates Iraqi Kasra Epenthesis (`صرت / كثر / دمع / كلهه`)** | **Soft Kasra Epenthesis:** `صِرِتْ`, `مِنْ كِثِرْ`, `وَ الدَّمِعْ`, `كِلْهَه` | **Fronted Kasra:** `صِرِتْ`, `دَمِعْ` | **Standard:** `صِرْتْ`, `دَمْعْ` |
| **1st-Person Singular Pronoun (`أنه / وانه`)** | **Open Long Alif (`آنَه / وَ آنَه`):** Prevents TTS from reading `أنه` as Fusha `أَنَّهُ` (`annahu`). | `آنَا` / `أَنَا` | `أَنَا` / `آنَه` |
| **Iraqi Long-U & Gaf Stems (`السوك / النوك / احلوك / فوك / بايك / ينكال`)** | `السُّوگْ`, `النُّوگْ`, `حْلُوگْ`, `فُوگْ`, `بَايِگْ`, `يِنْگَالْ` | `السُّوقْ` / `السُّوگْ`, `فَوْقْ` | `السُّوقْ`, `فَوْقْ` |
| **2nd-Person Masc. Suffix (`ـك`)** | **Fatha (`ـَكْ`):** `گَلْبَكْ`, `صَبْرَكْ` | **Kasra (`ـِكْ`):** `گَلْبِكْ`, `صَبْرِكْ` | **Fatha (`ـَكْ`):** `قَلْبَكْ`, `صَبْرَكْ` |
| **Articulation of `ض` (`Dhad`)** | **Emphatic Merged `ظ` (`Dhaa`):** `فَاظِلْ`, `ظْلُوعِي`, `مَا ظَلْ` | **Retained `ض` (or soft Gulf `ظ`):** `فَاضِلْ`, `ضْلُوعِي` | **Retained `ض` (unless `--enforce-iraqi-dhaa`):** `فَاضِلْ`, `ضْلُوعِي` |

---

## 4. Reference Melodic Legato Wave Architecture (`هَنْدَسَةُ المَوْجَةِ اللَّحْنِيَّةِ الهَادِئَةِ — طَوْرُ يَا يُمَّه بْأَرْضِ الشَّامْ`)

When replicating calm, weeping Iraqi legato laments (such as *«يَا يُمَّه بْأَرْضِ الشَّامْ»* at **66 BPM** in **Maqam Kurd / Bayati on D**), each stanza follows a **4-Movement Circular Melodic Wave** (`مَوْجَةٌ لَحْنِيَّةٌ دَائِرِيَّةٌ مِنْ أَرْبَعِ حَرَكَات`):

| Movement | Stanza Lines | Prosodic & Melodic Contour | Acoustic Execution Rule |
| :--- | :--- | :--- | :--- |
| **Movement A (`المُسْتَهَلّ الهَادِئ`)** | 4 short lines (`3 + 1`) | `ـَامْ / ـَامْ / ـَامْ` -> `ذِبْحَوْا أَحْلَامِي (×2)` | Soft, weeping mid-Baritone entry; the 4th line drops to the tonic Qarar and is echoed softly by a unison chorus. |
| **Movement B (`المَثْنَى المَمْدُود`)** | 2 paired couplets (4 short hemistichs) | `مِنْ وُصَلْنَاهَا .. الشَّامْ شِفْنَاهَا / نَاسْهَه مْعَيِّدَه .. لِلْ ذَبْحَوْا حْسِينْ` | Each internal rhyme (`ـَاهَا / ـَانَه` or `بَابِچْ / عِينِچْ`) is held on a **2-second open legato vowel (`مَدّ صَوْتِيّ مَفْتُوح`)** with zero rushing. |
| **Movement C (`السَّرْدُ التَّفْصِيلِيّ`)** | 3 long 16-syllable narrative lines | `مَكْسُورَة خَاطِرْ وَ الدَّمِعْ .. مَا ظَلْ بَعَدْ بِ عْيُونِي` | Smooth, stepwise descending narrative wave (`سَرْدٌ مُتَدَرِّجٌ هَابِط`) unifying all 3 line endings on a shared long vowel (`ـُونِي / ـْمَه / ـَعْبَه`). |
| **Movement D (`التَّسْلِيمُ وَ القَفْلَة`)** | 3 short lines returning to Mustahall melody | `بَسْ رُوسْ إِخْوَانِي وْيَايْ ... صَارَتْ گِدَّامِي (ذِبْحَوْا أَحْلَامِي)` | Circular melodic return (`التَّسْلِيمُ الدَّائِرِيّ`) to the exact melody of Movement A, resolving on `ـَامِي` (`گِدَّامِي / أَيَّامِي / أَيْتَامِي / الحَامِي / الدَّامِي`) + refrain `(ذِبْحَوْا أَحْلَامِي)`. |
