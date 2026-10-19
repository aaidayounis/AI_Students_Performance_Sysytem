import unittest
import analysis


class TestAnalysis(unittest.TestCase):

    def test_parse_valid(self):
        form_data = {
            "quiz": "65.5",
            "midterm": "70",
            "gpa": "3.2",
            "study": "4.5",
            "attendance": "85",
            "assign_done": "12",
            "assign_total": "14",
            "sleep": "7.5",
            "internet": "yes",
        }
        vals, errs = analysis.parse(form_data)
        self.assertEqual(errs, {})
        self.assertAlmostEqual(vals["quiz"], 65.5)
        self.assertEqual(vals["internet"], "yes")

    def test_parse_invalid(self):
        form_data = {
            "quiz": "abc",  # Not a number
            "midterm": "150",  # Out of range
            "assign_done": "15",
            "assign_total": "10",  # Done > Total
        }
        vals, errs = analysis.parse(form_data)
        self.assertIn("quiz", errs)
        self.assertIn("midterm", errs)
        self.assertIn("assign_done", errs)

    def test_analyse_sample(self):
        sample = dict(analysis.SAMPLE)
        res = analysis.analyse(sample)
        self.assertIn("est", res)
        self.assertTrue(0 <= res["est"] <= 100)
        self.assertIn("grade", res)
        self.assertIn("ci_low", res)
        self.assertIn("ci_high", res)
        self.assertTrue(res["ci_low"] <= res["est"] <= res["ci_high"])
        self.assertIn("radar_axes", res)
        self.assertEqual(len(res["radar_axes"]), 6)

    def test_all_presets_valid(self):
        for key, pinfo in analysis.PRESETS.items():
            data = pinfo["data"]
            res = analysis.analyse(data)
            self.assertTrue(0 <= res["est"] <= 100, f"Preset {key} produced out of bounds estimate")
            self.assertIn(res["grade"], ["A+", "A", "B", "C", "D", "F"])

    def test_grade_for(self):
        self.assertEqual(analysis.grade_for(95), "A+")
        self.assertEqual(analysis.grade_for(85), "A")
        self.assertEqual(analysis.grade_for(75), "B")
        self.assertEqual(analysis.grade_for(60), "C")
        self.assertEqual(analysis.grade_for(50), "D")
        self.assertEqual(analysis.grade_for(30), "F")


if __name__ == "__main__":
    unittest.main()
