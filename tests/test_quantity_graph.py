import unittest
from datetime import date
from pathlib import Path
from fastapi import HTTPException
from backend import quantity_graph
from webui.quantity_graph import build_quantity_graph, load_quantities

ROOT = Path(__file__).resolve().parents[1]


class QuantityGraphTests(unittest.TestCase):
    def test_default_window_is_two_years(self):
        graph = build_quantity_graph(ROOT)
        start = date.fromisoformat(graph["start"])
        end = date.fromisoformat(graph["end"])
        self.assertEqual(start, end.replace(year=end.year - 2))

    def test_dates_and_values_match_source(self):
        history, forecast = load_quantities(ROOT)
        graph = build_quantity_graph(ROOT, date.fromisoformat(history[0]["date"]), date.fromisoformat(forecast[-1]["date"]))
        self.assertEqual(len(graph["points"]), len(history) + len(forecast))
        self.assertEqual(graph["forecast"], forecast)
        self.assertLess(history[-1]["date"], forecast[0]["date"])
        self.assertIn("#fff0da", graph["svg"])
        self.assertIn("#f3f6fa", graph["svg"])
        self.assertTrue(all(0 <= point["x"] <= 864 and 0 <= point["y"] <= 360 for point in graph["points"]))

    def test_forecast_only_range(self):
        _, forecast = load_quantities(ROOT)
        graph = build_quantity_graph(ROOT, date.fromisoformat(forecast[0]["date"]), date.fromisoformat(forecast[3]["date"]))
        self.assertEqual(len(graph["points"]), 4)
        self.assertTrue(all(point["kind"] == "Forecast" for point in graph["points"]))

    def test_reversed_and_empty_ranges(self):
        for start, end in [(date(2027, 1, 1), date(2026, 1, 1)), (date(1900, 1, 1), date(1901, 1, 1))]:
            with self.assertRaises(HTTPException) as error:
                quantity_graph(start, end)
            self.assertEqual(error.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
