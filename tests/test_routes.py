import unittest
from app import app


class TestRoutes(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"AI Students", resp.data)
        self.assertIn(b"Quick Presets", resp.data)

    def test_get_index_preset(self):
        resp = self.client.get("/?preset=high_potential")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Estimated final exam", resp.data)
        self.assertIn(b"95% Confidence Interval", resp.data)

    def test_get_about(self):
        resp = self.client.get("/about")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Collaborators", resp.data)
        self.assertIn(b"Problem Statement", resp.data)
        self.assertIn(b"Aaida Younis", resp.data)

    def test_post_analyzer(self):
        form_data = {
            "quiz": "75",
            "midterm": "72",
            "gpa": "3.3",
            "study": "5.0",
            "attendance": "88",
            "assign_done": "13",
            "assign_total": "14",
            "sleep": "7.5",
            "internet": "yes",
        }
        resp = self.client.post("/", data=form_data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Estimated final exam", resp.data)
        self.assertIn(b"Cohort Percentile Distribution", resp.data)

    def test_export_csv(self):
        resp = self.client.get("/export?quiz=80&midterm=75&attendance=90")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "text/csv")
        self.assertIn("attachment; filename=student_performance_report.csv", resp.headers.get("Content-Disposition", ""))
        self.assertIn(b"Student Academic & Performance Report", resp.data)

    def test_404_page(self):
        resp = self.client.get("/non-existent-endpoint")
        self.assertEqual(resp.status_code, 404)
        self.assertIn(b"404", resp.data)
        self.assertIn(b"Page Not Found", resp.data)


if __name__ == "__main__":
    unittest.main()
