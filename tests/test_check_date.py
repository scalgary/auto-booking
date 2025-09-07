from utils import check_date
import unittest
from datetime import datetime, timedelta

class TestCheckDate(unittest.TestCase):
    def test_past_date(self):
        date_str = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%y")
        possible, next_week = check_date(date_str)
        self.assertFalse(possible)
        self.assertFalse(next_week)

    def test_today(self):
        date_str = datetime.now().strftime("%d-%b-%y")
        possible, next_week = check_date(date_str)
        self.assertTrue(possible)
        self.assertFalse(next_week)

    def test_in_3_days(self):
        date_str = (datetime.now() + timedelta(days=3)).strftime("%d-%b-%y")
        possible, next_week = check_date(date_str)
        self.assertTrue(possible)
        self.assertFalse(next_week)

    def test_in_7_days(self):
        date_str = (datetime.now() + timedelta(days=7)).strftime("%d-%b-%y")
        possible, next_week = check_date(date_str)
        self.assertTrue(possible)
        self.assertTrue(next_week)

    def test_in_10_days(self):
        date_str = (datetime.now() + timedelta(days=10)).strftime("%d-%b-%y")
        possible, next_week = check_date(date_str)
        self.assertFalse(possible)
        self.assertFalse(next_week)
    
    def test_manual_1_week(self):
        today = datetime.strptime("07-Sep-25", "%d-%b-%y")
        date_str = "14-Sep-25"
        possible, next_week = check_date(date_str, today)
        self.assertTrue(possible)
        self.assertTrue(next_week)
    
    def test_manual_too_much(self):
        today = datetime.strptime("07-Sep-25", "%d-%b-%y")
        date_str = "15-Sep-25"
        possible, next_week = check_date(date_str, today)
        self.assertFalse(possible)
        self.assertFalse(next_week)
    

    def test_manual_short_week(self):
        today = datetime.strptime("07-Sep-25", "%d-%b-%y")
        date_str = "13-Sep-25"
        possible, next_week = check_date(date_str, today)
        self.assertTrue(possible)
        self.assertFalse(next_week)

    def test_invalid_argument_type(self):
        with self.assertRaises(TypeError):
            check_date(12345)
        with self.assertRaises(TypeError):
            check_date(["07-Sep-25"])
        with self.assertRaises(ValueError):
            check_date("2025-09-07")  # mauvais format

if __name__ == "__main__":
    unittest.main()