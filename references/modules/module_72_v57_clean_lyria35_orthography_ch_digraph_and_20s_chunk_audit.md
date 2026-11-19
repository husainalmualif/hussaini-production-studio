# Module 72 — V57.0 Clean Natural Arabic `Lyria 3.5` Orthography (`NC26`), Phonetic `چ -> تش` Digraph & Clean `گ` Lock (`NC27`), Anti-Pop Regional Dialect Prompts (`NC28`) & Mandatory `20s` Blind Chunk Phonetic Audit (`NC29`)

> **Parent Module:** `SKILL.md` (`V57.0 OMNI-ARCHITECT`)  
> **Builds Upon:** `module_71_v56_four_axes_modern_latmiya_pulse_locked_dsp_and_multi_method_lab.md` (`V56.0`, `NC23–NC25`)  
> **Primary Runtime:** `scripts/hussaini_dsp_montage.py` (`format_clean_lyrics_for_lyria35()` / `--compile-clean-lyria`)

---

## 1. The Forensic Discovery: Why Heavy Over-Tashkeel & `"warm deep emotional Arabic male baritone"` Sabotaged Dialect & Makharij (`V56 -> V57`)

Following a strict user critique of the `V56.0` outputs («اللهجة غير صحيحة ولفظ الكلمات ومخارج الحروف غير صحيح»), every generated clip (`Exp-1`, `Exp-2`, `Exp-5`, `Exp-6`) was sliced into **`25-second` isolated chunks** and audited blindly side-by-side against a real human Bahrani Radood reference (`ref_akraf_dam3_alhasan.mp3`). This exposed **4 root failures** that expectation bias had masked when listening to full 3-minute tracks:

1. **Over-Tashkeel BPE Token Shattering (`V56` Fault #1):**
   - Packing 10–14 Unicode diacritics, terminal Sukun (`ْ`) on every closed consonant, and artificial prosthetic spellings (`إِمْنِ`, `إِعْلَه`, `إِتْرَجِمْهَا`, `أُمُّ`, `الصُّوَرْ`, `عَلَه`) fragmented `Lyria 3.5`'s Arabic subword tokens, causing severe lexical hallucinations:
     - `إِمْنِ أُمّ عَبَّاسْ` -> sung as **`إِبْنِي أُمْ عَبَّاسْ`** ("my son Umm Abbas"!)
     - `فَلْسَفَةِ` / `وَفَلْسَفَة` -> sung as **`فَلْسَفَتِي`** ("my philosophy") & **`وَفَلْسَفْأَتِ`**
     - `إِتْرَجِمْهَا أُمُّ البَنِينْ` -> sung as **`إِتْرَاجِمْهَا أُمُورْ أُمُّ البَنِينْ`**
     - `إِعْلَه غَايِبْهَا` -> sung as **`أَعْلَى غَايِبْهَا`**
     - `الصُّوَرْ` -> sung as **`الصُّؤُورْ`** (glottal stop!)
     - `تِهِلْ حَمْرَه` -> sung as **`تِهِي الْحَمْرَا`**
     - `عَلَه التَّرَايِبْ` -> sung as **`عَلَاهِ التَّرَايِبْ`**
     - `مَا يِبْرَه` -> sung as **`مَا يِبْـبَـرَا`**
     - `الشَّمِرْ ... لَوَاهِبْ` -> sung as **`الشَّمِيرْ ... لَوَاهِي`**
2. **Generic Pop-Ballad Sound Descriptor (`V56` Fault #2):**
   - Writing `"warm deep emotional Arabic male baritone"` without banning piano/pop singing pulled `Lyria 3.5` straight into **Syrian/Levantine/Egyptian pop-nasheed training data** (introducing a literal Western piano in `Exp-5` `0:00–0:20`, R&B snare/clap in `Exp-6`, Egyptian `بِيخُوضْ`, weak breathy `ح / ع`, thin `ص`, and Levantine `ز` for `ظ`).
3. **Persian Unicode `چ` (`U+0686`) Collapse (`V56` Fault #3):**
   - Across `Exp-2`, `Exp-5`, and even `V57-A` (`تبچي` -> `تِبْكِي`), raw `چ` consistently collapsed into `ك` or `ج` in `Lyria 3.5`.
4. **Full-Track Expectation Bias (`V56` Fault #4):**
   - Listening to a 3-minute song in one pass allows the listener's brain to mentally fill in intended lyrics behind the melody, hiding subtle makhraj and syllable defects.

---

## 2. The 4 Controlled `V57.0` Phonetic & Makharij Stress-Test Experiments (`V57-A`, `V57-A2`, `V57-B`, `V57-B2` — Cumulative `17` Flow Music Experiments)

Four brand-new `Lyria 3.5` sessions were executed, downloaded, sliced into **`20-second` chunks**, and audited word-by-word:

| Exp ID | Dialect & Poem | Orthography & Prompt Tested | Clip UUID & Length | Chunk-by-Chunk `20s` Forensic Ear Verdict |
| :--- | :--- | :--- | :---: | :--- |
| **`V57-A`** | **Iraqi** («فلسفة الانتظار») | Clean natural Arabic + **internal A/B test (`تبچي` vs `وحتشي` / `ملتشوم`)** + `v57_iraqi_karbalaei_pure_majlis` | `7dd7b0f4` (`03:02`) | **Breakthrough Proof:** Authentic Iraqi Karbalaei Radood + crisp `گ` (`وگَلبه`, `گبلك`, `حگّه`). Proved inside ONE clip: `تبچي` (`چ`) STILL failed -> `تِبْكِي`, while **`وحتشي` & `ملتشوم` (`تش`) SUCCEEDED as `/tʃ/`!** (Had 20s garbled ad-lib intro & `فلسفة -> فسفة` / `اترجمها ام -> ترجمهم`). |
| **`V57-A2` ★** | **Iraqi Champion** («فلسفة الانتظار») | **`--compile-clean-lyria` (`فَلْسَفة`, `تْرَجِّمها .. أُمّ البنين`, `تبتشي`, `حَتشِي`, `مَلتشوم`, `وگَلبه`, `گبلك`, `حگّه`)** + `"immediate rhythmic chorus entry from the first second"` | `d8a6ce81` (`02:44`) | **IRAQI CHAMPION (`v57_iraqi_intidhar_master.mp3`, `-14.0 LUFS / -2.45 dBTP`):** Immediate chorus entry at `0:00` (zero garbled intro), **100% authentic Iraqi Karbalaei voice, crisp pharyngeal `ح/ع`**, effortless **`تِبْچِي`** (`chunk 02`), **`حَچِي`** (`chunk 03/05`), **`مَلْچُوم`** (`chunk 04/06/07`), **`گَلْبَه / گَبْلَك / حَگَّه`**, **`تْرَجِّمها أُمّ البنين`**, **`تِهِلْ حَمْرَه`**, zero piano, zero pop! |
| **`V57-B` ★** | **Bahrani Champion** («صورة جسد عالغبرة») | **`--compile-clean-lyria` (`الصُوَر`, `أوگف`, `على الترايب`, clean `ما يبره`)** + `v57_bahrani_matam_pure_58bpm_saba_bayati` | `54e0c7c7` (`02:42`) | **BAHRANI CHAMPION (`v57_bahrani_sowrat_master.mp3`, `-14.0 LUFS / -1.54 dBTP`):** Pure Bahrani Matam chest latm & unison choir, zero piano/snare/Levantine pop, **crisp emphatic `ص / ظ` & pharyngeal `ح / ع`**, authentic Bahrani **`أُوگَفْ`** (`/g/`), clean **`كل الصُوَر`**, clean **`مرمي على الترايب`**, clean **`ما يبره`**, zero garbled verses across all 8 chunks! |
| **`V57-B2`** | **Bahrani** («صورة جسد عالغبرة») | Variant testing `الوَكْت` + `فيه الحقد لَواهب` | `80b582f3` (`02:44`) | **Rejected by `NC29` Chunk Audit:** `v57b2_chunk_04` garbled `واللحظة نار وغربة .. مات اسم الأمل`; immediately rejected in favor of `V57-B` (`54e0c7c7`). |

---

## 3. Permanent Negative Constraints `NC26–NC29` (`V57.0 OMNI-ARCHITECT`)

1. **`NC26` — Clean Natural Arabic Orthography & Anti-Token-Shattering Law (`--compile-clean-lyria`):**
   - For **`Lyria 3.5` (`Flow Music`)** delivery, **NEVER** feed 100%-over-diacritized text with terminal Sukun spam (`ْ`) or synthetic prosthetic prefixes (`إِمْنِ`, `إِعْلَه`, `إِتْرَجِمْهَا`, `عَلَه الـ`, `أُمُّ`).
   - Use **`format_clean_lyrics_for_lyria35()` (`--compile-clean-lyria`)** which keeps **clean natural Arabic spelling + 1–2 surgical disambiguating diacritics ONLY** on proven homographs (`الصُوَر`, `فَلْسَفة`, `حگّه`, `گَلبه`, `لَواهب`, `الوَكْت`, `أُمّ البنين`, `تْرَجِّمها .. أُمّ البنين`).
   - *(Note: Full morphological vocalization via `--compile-lyrics` remains preserved for archival poetry printing, linguistic verification, and non-`Lyria` TTS/print use.)*
2. **`NC27` — Phonetic Digraph `تش` Law for Gulf/Iraqi `چ` (`/tʃ/`) & Clean `گ` (`/g/`) Law:**
   - Because `Lyria 3.5` systematically collapses raw Persian Unicode `چ` (`U+0686`) into `ك` or `ج`, **`format_clean_lyrics_for_lyria35()` converts `چ -> تش`** (`تبچي -> تبتشي`, `يبچي -> يبتشي`, `حچي -> حَتشِي`, `ملچوم -> مَلتشوم`) which empirically yields authentic `/tʃ/` articulation.
   - Simultaneously, clean un-cluttered **`گ`** (without heavy Tashkeel spam) reliably articulates `/g/` (`وگَلبه`, `گبلك`, `حگّه`, `أوگف`), so colloquial `ق -> گ` is enforced on proven dialectal stems.
3. **`NC28` — Anti-Pop-Ballad & Pure Regional Dialect Vocal Lock:**
   - Never use generic `"warm deep emotional Arabic male baritone"` in pure Iraqi/Bahrani Latmiyas (it pulls Levantine pop-nasheed vocals + piano/snare).
   - Default to **`v57_iraqi_karbalaei_pure_majlis_60bpm_saba_lami`** (with `"immediate rhythmic chorus entry from the first second with no solo ad-lib intro, sharp crisp Arabic pharyngeal pronunciation, zero musical instruments, no piano, no pop singing"`) or **`v57_bahrani_matam_pure_58bpm_saba_bayati`** (`"Traditional Bahrani Ashura Matam Latmiya elegy from Bahrain, authentic Gulf Bahrani Arabic dialect, sharp authentic Arabic throat articulation, zero musical instruments, no piano, no drums, no pop singing"`).
4. **`NC29` — Mandatory `20-Second` Blind Chunk Phonetic & Makharij Audit Gate:**
   - **Strictly FORBIDDEN** to declare any generated Latmiya "clean" after listening only to a full 3-minute pass.
   - Every candidate MUST be sliced via `ffmpeg -f segment -segment_time 20` and audited chunk-by-chunk (`00..0N`) specifically checking: (a) dialect authenticity (zero Levantine/Egyptian pop drift), (b) lexical integrity (zero garbled/hallucinated lines — e.g., rejecting `V57-B2` chunk 04), and (c) Arabic Makharij (`ح، ع، ص، ظ، ض، گ، تش/چ`).
