import unittest
import charts


class TestCharts(unittest.TestCase):

    def test_bar_chart(self):
        items = [("Quiz", 59.4), ("Midterm", 59.3), ("Final", 59.5)]
        svg = str(charts.bar_chart(items, y_label="Average Score"))
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("Quiz", svg)

    def test_bell_curve(self):
        svg = str(charts.bell_curve(68.5, mean=59.5, std=18.9, pct=68.0))
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("bell-chart", svg)
        self.assertIn("68.5", svg)

    def test_radar_chart(self):
        axes = [
            ("Quiz", 70.0, 59.4),
            ("Midterm", 65.0, 59.3),
            ("Attendance", 80.0, 76.8),
            ("Assignments", 90.0, 83.5),
            ("Prev GPA", 75.0, 74.8),
            ("Study Time", 50.0, 44.4),
        ]
        svg = str(charts.radar_chart(axes))
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("radar-chart", svg)
        self.assertIn("Cohort Avg", svg)

    def test_score_ring(self):
        svg = str(charts.score_ring(78))
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("78", svg)


if __name__ == "__main__":
    unittest.main()
