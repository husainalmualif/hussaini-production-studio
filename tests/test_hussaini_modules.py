#!/usr/bin/env python3
# pylint: disable=line-too-long,too-many-locals,too-many-statements,no-member
"""Unit tests for Hussaini Production Studio V45.0 OMNI-ARCHITECT modules."""

import json
import os
import sys
import tempfile
import unittest
import wave
import numpy as np
from scipy.io import wavfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import hussaini_dsp_montage as hdm  # noqa: E402  # pylint: disable=wrong-import-position


class TestHussainiOmniArchitectV45(unittest.TestCase):
    """Comprehensive test suite for V45.0 OMNI-ARCHITECT phonetics, prosody, and 5-Track DAW DSP."""

    def test_version_single_source_of_truth(self):
        """Verify SKILL_VERSION is loaded from the root VERSION file."""
        self.assertEqual(hdm.get_skill_version(), "V45.0 OMNI-ARCHITECT")
        self.assertEqual(hdm.SKILL_VERSION, "V45.0 OMNI-ARCHITECT")

    def test_module41_space_first_default_and_optional_tatweel(self):
        """Module 41: Verify space-first separation by default (0 Tatweel) and optional Tatweel mode."""
        raw = "ياحسين وياحسين يبوفاضل عالباب بغربتي بضلوعي لحسين شصار شنگول"
        separated_default = hdm.de_cliticize_and_separate_words(raw, use_tatweel=False)
        self.assertNotIn("ـ", separated_default)
        self.assertIn("يَا حْسَيْنْ", separated_default)
        self.assertIn("وَ يَا حْسَيْنْ", separated_default)
        self.assertIn("بِ غُرْبِتِي", separated_default)
        self.assertIn("لِ حْسَيْنْ", separated_default)

        separated_tatweel = hdm.de_cliticize_and_separate_words(raw, use_tatweel=True)
        self.assertIn("بِـ غُرْبِتِي", separated_tatweel)
        self.assertIn("لِـ حْسَيْنْ", separated_tatweel)

    def test_module40_safe_tanween_protects_vocalized_verbs_and_vocatives(self):
        """Module 40: Ensure Tanween regex never corrupts already-vocalized verbs or vocatives."""
        raw_poem = (
            "[المستهل]\n"
            "عينٍ تسيل على الثرى .. يومٍ تنادي زينب\n"
            "قلبٍ يُنادي يا حسين .. جرحٍ تَراهُ داميا\n"
            "جسماً على الثرى .. دامٍ بلا قبورٍ"
        )
        compiled = hdm.resolve_dialectal_and_prosodic_tanween(raw_poem, dialect="iraqi")
        self.assertIn("عَيْنِنْ تِسِيلْ", compiled)
        # "تنادي" has Alif after ن, must NOT become "تِنادي" if next char is ا, wait: ت + ن -> تِنادي is valid colloquial,
        # but "تَراهُ" and "يُنادي" already have diacritics and must NOT receive a second Kasra!
        self.assertIn("قَلْبِنْ يُنَادِي", hdm.resolve_dialectal_and_prosodic_tanween("قلبٍ يُنَادِي", dialect="iraqi"))
        self.assertIn("جَرْحِنْ تَرَاهُ", hdm.resolve_dialectal_and_prosodic_tanween("جرحٍ تَرَاهُ", dialect="iraqi"))
        self.assertIn("جِسْمَنْ عَلَى الثَّرَى", compiled)
        self.assertIn("دَامِنْ بِلَا قُبُورْ", compiled)

    def test_module43_word_boundary_prevents_substring_corruption(self):
        """Module 43: Ensure word-boundary shaping never corrupts substrings like مقاتل or أقبل."""
        iraqi_text = "بويه شلون مقاتل أقبل بقلب صبر وجمر"
        res = hdm.detect_and_shape_dialect(iraqi_text, use_tatweel=False)
        self.assertEqual(res["detected_dialect"], "iraqi")
        # "مقاتل" and "أقبل" must remain untouched while "بقلب", "صبر", "وجمر" are shaped
        self.assertIn("مقاتل", res["shaped_lyrics"])
        self.assertIn("أقبل", res["shaped_lyrics"])
        self.assertIn("بِ گَلُبْ", res["shaped_lyrics"])
        self.assertIn("صَبُرْ", res["shaped_lyrics"])
        self.assertIn("وَ جَمُرْ", res["shaped_lyrics"])

    def test_module43_prefix_decomposition_dhaa_and_neutral_tie(self):
        """Module 43: Verify prefix decomposition, Iraqi Dhaa, Bahrani Kasra, and neutral hybrid."""
        bahrani_text = "يا بويي ونتي هالگفره بالقلب ودمع وفاضل"
        bahrani_res = hdm.detect_and_shape_dialect(bahrani_text, use_tatweel=False)
        self.assertEqual(bahrani_res["detected_dialect"], "bahrani")
        self.assertIn("بِ الگَلِبْ", bahrani_res["shaped_lyrics"])
        self.assertIn("فَاضِلْ", bahrani_res["shaped_lyrics"])

        bahrani_dhaa = hdm.detect_and_shape_dialect(
            bahrani_text, enforce_iraqi_dhaa=True, use_tatweel=False
        )
        self.assertIn("فَاظِلْ", bahrani_dhaa["shaped_lyrics"])

        iraqi_text = "يمه بويه شلون چلبت وگفت وبالقلب وكالجمر وللدمع"
        iraqi_res = hdm.detect_and_shape_dialect(iraqi_text, use_tatweel=False)
        self.assertEqual(iraqi_res["detected_dialect"], "iraqi")
        self.assertIn("بِ الگَلُبْ", iraqi_res["shaped_lyrics"])
        self.assertIn("كَ الجَمُرْ", iraqi_res["shaped_lyrics"])
        self.assertIn("لِلْ دَمِعْ", iraqi_res["shaped_lyrics"])

        neutral_text = "في كربلاءوقف الغريب بدمع وصبر وفاضل"
        neutral_res = hdm.detect_and_shape_dialect(neutral_text, use_tatweel=False)
        self.assertEqual(neutral_res["detected_dialect"], "iraqi_bahrani")
        self.assertIn("صَبْرْ", neutral_res["shaped_lyrics"])
        self.assertIn("فَاضِلْ", neutral_res["shaped_lyrics"])

        neutral_dhaa = hdm.detect_and_shape_dialect(
            neutral_text, enforce_iraqi_dhaa=True, use_tatweel=False
        )
        self.assertIn("فَاظِلْ", neutral_dhaa["shaped_lyrics"])
        self.assertEqual(
            hdm.shape_token_morphologically("...", hdm.IRAQI_WORD_SHAPING_MAP),
            "...",
        )

    def test_module41_and_43_iraqi_orthographic_gaf_and_sham_lament_lexicon(self):
        """Verify Iraqi orthographic 'كَـ' -> 'گ' normalization and Sham lament vocabulary."""
        raw_sham = (
            "يايمه ابأرض الشام عشت انه اشكَد آلام "
            "كلهه فرحانه وانه تعبانه للذبحوا حسين "
            "كَوه النفس اشهكَ صرت من كثر ما تعبوني صارت كَدامي "
            "يحركَ خيام يكَطع بنحره اكَبَال الأيتام "
            "السهم بايكَله النظر عالشاطي فوكَ الأتراب "
            "دخلونه بذيچ النوك وافتروا بينه السوك وطلعت للناس احلوك وصار ينكال"
        )
        res = hdm.detect_and_shape_dialect(raw_sham, use_tatweel=False)
        self.assertEqual(res["detected_dialect"], "iraqi")
        shaped = res["shaped_lyrics"]
        self.assertIn("يَا يُمَّه", shaped)
        self.assertIn("بِ أَرْضْ", shaped)
        self.assertIn("آنَه", shaped)
        self.assertIn("إِشْگَدْ", shaped)
        self.assertIn("كِلْهَه", shaped)
        self.assertIn("وَ آنَه", shaped)
        self.assertIn("لِلْ ذَبْحَوْا", shaped)
        self.assertIn("گُوَّه", shaped)
        self.assertIn("أَشْهَگْ", shaped)
        self.assertIn("صِرِتْ", shaped)
        self.assertIn("كِثِرْ", shaped)
        self.assertIn("گِدَّامِي", shaped)
        self.assertIn("يِحْرِگْ", shaped)
        self.assertIn("يِگْطَعْ", shaped)
        self.assertIn("گْبَالْ", shaped)
        self.assertIn("بَايِگْ لَه", shaped)
        self.assertIn("عَلَى الشَّاطِي", shaped)
        self.assertIn("فُوگْ", shaped)
        self.assertIn("النُّوگْ", shaped)
        self.assertIn("السُّوگْ", shaped)
        self.assertIn("لِلْ نَاسْ", shaped)
        self.assertIn("حْلُوگْ", shaped)
        self.assertIn("يِنْگَالْ", shaped)

    def test_module34_38_per_hemistich_syllable_and_poem_linter(self):
        """Modules 34 & 38: Verify Arabic syllable counter, hemistich balance, and lint_poem."""
        balanced_lines = [
            "يَا كَرْبَلَا طَالَ البَلَا .. وَ القَلْبُ فِيكِ مُبْتَلَى",
            "جِئْنَا إِلَيْكِ بِ الدِّمَا .. نَبْكِي إِمَامَ الأَوْلِيَا",
            "صَبْرُ العَقِيلَةِ انْقَضَى .. وَ الدَّمْعُ فَوْقَ الخَدِّ سَالْ",
            "يَا حُسَيْنُ يَا مَظْلُومْ",
            "فِي الطَّفِّ خَرَّ المُجْتَبَى .. ظَامِي الحَشَا فَوْقَ الثَّرَى",
            "وَ السَّهْمُ فِي القَلْبِ اسْتَوَى .. وَ الشَّمْرُ بِ السَّيْفِ اعْتَلَى",
            "نَادَتْهُ زَيْنَبُ الهدى .. أَخِي أَخِي مَنْ لِلْعِيَالْ",
            "يَا حُسَيْنُ يَا مَظْلُومْ",
        ]
        iso_res = hdm.validate_stage1_iso_syllabic_lock(balanced_lines)
        self.assertTrue(iso_res["is_valid_stanza_grid"])
        self.assertTrue(iso_res["identical_4th_line_refrain"])
        self.assertTrue(iso_res["internal_hemistich_balanced"])
        self.assertTrue(iso_res["passed"])

        unbalanced_lines = [
            "يَا حُسَيْنْ .. يَا سَيِّدَ الشُّهَدَاءِ الكِرَامِ الأَبْرَارِ الأَطْهَارِ فِي كَرْبَلَاءْ",
            "جِئْنَا .. نَبْكِي",
            "صَبْرُنا .. طَالْ",
            "يَا حُسَيْنْ",
        ]
        unbalanced_res = hdm.validate_stage1_iso_syllabic_lock(unbalanced_lines, max_syllable_spread=2)
        self.assertFalse(unbalanced_res["internal_hemistich_balanced"])
        self.assertFalse(unbalanced_res["passed"])
        self.assertFalse(hdm.validate_stage1_iso_syllabic_lock([])["iso_syllabic_balanced"])

        # Unvocalized syllable estimation fallback + non-hemistich single line
        single_lines = [
            "سلام الله على الحسين الشهيد",
            "سلام الله على العباس الكفيل",
            "سلام الله على زينب الحوراء",
            "يا مظلوم",
        ]
        self.assertTrue(hdm.validate_stage1_iso_syllabic_lock(single_lines)["is_valid_stanza_grid"])

        # Lint poem with Fusha + Colloquial mixing and slurring risks
        mixed_poem = "ياحسين إنما بويه شلون ليس في الدار غيرنا"
        lint_res = hdm.lint_poem(mixed_poem, stage=1)
        self.assertTrue(lint_res["fusha_colloquial_mixing_in_stage1"])
        self.assertIn("ياحسين", lint_res["slurring_risks_detected"])
        self.assertFalse(lint_res["ready_for_generation"])

    def test_module39_json_preconditioning_and_session_ledger(self):
        """Module 39: Verify optional reference_clip_id (default None) and JSON session ledger."""
        default_payload = hdm.build_flowmusic_json_preconditioning()
        self.assertIsNone(default_payload["reference_clip_id"])
        self.assertEqual(default_payload["skill_version"], "V45.0 OMNI-ARCHITECT")

        custom_payload = hdm.build_flowmusic_json_preconditioning(
            dialect="bahrani", maqam="hijaz", bpm=62, reference_clip_id="ref-uuid-999"
        )
        self.assertEqual(custom_payload["reference_clip_id"], "ref-uuid-999")

        bridge = hdm.build_multi_tor_melodic_bridge("saba", "lami")
        self.assertTrue(bridge["common_jins_compatible"])

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = os.path.join(tmpdir, "session_ledger.json")
            with open(ledger_file, "w", encoding="utf-8") as bad_f:
                bad_f.write("{invalid-json")
            entry1 = hdm.log_generation_session(
                ledger_file, "Saba Latm", "سطر أول\nسطر ثاني", seed=42
            )
            self.assertEqual(entry1["lyrics_line_count"], 2)
            entry2 = hdm.log_generation_session(
                ledger_file, "Hijaz Shoor", "سطر واحد", reference_clip_id="clip-1"
            )
            self.assertEqual(entry2["reference_clip_id"], "clip-1")
            with open(ledger_file, "r", encoding="utf-8") as f_in:
                saved = json.load(f_in)
            self.assertEqual(len(saved), 2)

    def test_dsp_absolute_dbfs_sidechain_and_lufs_mastering(self):
        """Verify absolute dBFS sidechain immunity to single spikes, LUFS normalization, and multi-depth WAV."""
        sr = 16000
        t_vec = np.linspace(0.0, 1.5, int(1.5 * sr), endpoint=False)
        # Quiet signal with a single 1-sample spike at index 100, then sustained vocal from 0.5s to 1.2s
        signal = np.zeros_like(t_vec)
        signal[100] = 1.0  # Single-sample spike
        vocal_mask = (t_vec >= 0.5) & (t_vec <= 1.2)
        signal[vocal_mask] = 0.5 * np.sin(2.0 * np.pi * 240.0 * t_vec[vocal_mask])

        ducking = hdm.compute_smart_sidechain_ducking(signal, sr, duck_db=-3.0)
        # During the sustained vocal (around 0.85s), ducking must reach ~0.708 (-3dB)
        mid_vocal_idx = int(0.85 * sr)
        self.assertAlmostEqual(float(ducking[mid_vocal_idx]), 10.0 ** (-3.0 / 20.0), delta=0.06)
        # During silence (around 0.3s), ducking must be ~1.0 (no attenuation)
        silence_idx = int(0.30 * sr)
        self.assertGreater(float(ducking[silence_idx]), 0.98)

        # Test onset detection
        onset = hdm.detect_vocal_onset_offset_samples(signal, sr)
        self.assertGreater(onset, 0)
        self.assertEqual(hdm.detect_vocal_onset_offset_samples(np.zeros(500), sr), 0)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test 24-bit stereo WAV reading
            wav24_path = os.path.join(tmpdir, "input24.wav")
            with wave.open(wav24_path, "wb") as wf:  # pylint: disable=no-member
                wf.setnchannels(2)
                wf.setsampwidth(3)
                wf.setframerate(sr)
                # 500 frames of 24-bit stereo (3 bytes * 2 channels = 6 bytes per frame)
                wf.writeframes(b"\x00\x10\x00\x00\xf0\xff" * 500)
            sr_read, data_24 = hdm.read_wav_any_depth(wav24_path)
            self.assertEqual(sr_read, sr)
            self.assertEqual(len(data_24), 500)

            # Test 8-bit and 32-bit WAV reading
            for width, frame_bytes in ((1, b"\x80\x90"), (4, b"\x00\x00\x10\x00")):
                w_path = os.path.join(tmpdir, f"in_{width}.wav")
                with wave.open(w_path, "wb") as wf:  # pylint: disable=no-member
                    wf.setnchannels(1)
                    wf.setsampwidth(width)
                    wf.setframerate(sr)
                    wf.writeframes(frame_bytes * 100)
                _, d_out = hdm.read_wav_any_depth(w_path)
                self.assertGreater(len(d_out), 0)

            # Test custom samples_dir with real IR and percussion WAVs
            samples_dir = os.path.join(tmpdir, "samples")
            os.makedirs(samples_dir, exist_ok=True)
            dummy_hit = (np.sin(2.0 * np.pi * 80.0 * t_vec[:800]) * 16000).astype(np.int16)
            wavfile.write(os.path.join(samples_dir, "latm.wav"), sr, np.column_stack((dummy_hit, dummy_hit)))
            wavfile.write(os.path.join(samples_dir, "husseiniya_ir.wav"), sr, np.column_stack((dummy_hit, dummy_hit)))

            raw_16 = os.path.join(tmpdir, "raw16.wav")
            wavfile.write(raw_16, sr, (signal * 20000).astype(np.int16))

            out_bandari = os.path.join(tmpdir, "sub", "out_bandari.wav")
            hdm.process_audio_file(
                raw_16,
                out_bandari,
                mode="bandari",
                bpm=120.0,
                maqam_drone="hijaz",
                swing=0.25,
                samples_dir=samples_dir,
            )
            self.assertTrue(os.path.isfile(out_bandari))

            out_bahrani = os.path.join(tmpdir, "out_bahrani.wav")
            hdm.process_audio_file(
                raw_16,
                out_bahrani,
                mode="zanjeel_bahrani",
                bpm=90.0,
                maqam_drone="saba",
                offset_ms=20.0,
            )
            self.assertTrue(os.path.isfile(out_bahrani))

            out_mawal = os.path.join(tmpdir, "out_mawal.wav")
            hdm.process_audio_file(raw_16, out_mawal, mode="mawal", bpm=0.0, maqam_drone="lami")
            self.assertTrue(os.path.isfile(out_mawal))

    def test_cli_entrypoints_compile_lint_and_audio(self):
        """Verify CLI entrypoints (--compile-lyrics, --lint-poem, --session-log, and error paths)."""
        self.assertEqual(
            hdm.main(["--compile-lyrics", "ياحسين بويه شلون بقلب صبر", "--no-tatweel"]),
            0,
        )
        self.assertEqual(
            hdm.main(["--compile-lyrics", "يبوفاضل بغربتي", "--use-tatweel", "--enforce-iraqi-dhaa"]),
            0,
        )
        self.assertEqual(
            hdm.main(["--lint-poem", "يَا كَرْبَلَا طَالَ البَلَا .. وَ القَلْبُ فِيكِ مُبْتَلَى"]),
            0,
        )
        self.assertEqual(hdm.main([]), 1)
        self.assertEqual(hdm.main(["--input", "nonexistent.wav", "--output", "out.wav"]), 1)

        with tempfile.TemporaryDirectory() as tmpdir:
            sr = 8000
            in_wav = os.path.join(tmpdir, "cli_in.wav")
            out_wav = os.path.join(tmpdir, "cli_out.wav")
            ledger = os.path.join(tmpdir, "cli_ledger.json")
            sig = (np.sin(np.linspace(0, 50, 4000)) * 12000).astype(np.int16)
            wavfile.write(in_wav, sr, sig)
            rc = hdm.main(
                [
                    "--input",
                    in_wav,
                    "--output",
                    out_wav,
                    "--mode",
                    "latm",
                    "--bpm",
                    "60",
                    "--session-log",
                    ledger,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(out_wav))
            self.assertTrue(os.path.isfile(ledger))


if __name__ == "__main__":
    unittest.main()
