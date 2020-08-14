"""Test the log date widget."""
import os
import unittest
from unittest.mock import patch

import healthhelper.interface as interface
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Directory containing this file
this_dir = os.path.abspath(os.path.dirname(__file__))
# Path of the directory containing some test log files.
TEST_LOG_FILE_DIR = os.path.join(this_dir, 'test_files', 'other_test_log_files')

app = QApplication([])


class TestDate(unittest.TestCase):

    def test_default(self):
        """For default LogWin(), the current date should be placed into the date input fields."""
        log_win = interface.LogWin()
        today = interface.datetime.date.today()
        self.assertEqual(log_win.day_textbox.text(), str(int(today.strftime('%d'))))
        self.assertEqual(log_win.month_combobox.currentText(), today.strftime('%B'))
        self.assertEqual(log_win.year_textbox.text(), str(today.year))

    def test_valid_user_input(self):
        """Check that the 'change log' button calls LogWin, and that the user's
        date input is placed into the date fields by default."""
        log_win = interface.LogWin()
        # Set the input for the date fields.
        log_win.day_textbox.setText("7")
        log_win.month_combobox.setCurrentText("October")
        log_win.year_textbox.setText("2019")

        # Click the 'change log' button and compare the new values to the user's input.
        QTest.mouseClick(log_win.change_log_btn, Qt.LeftButton)
        self.assertEqual(log_win.day_textbox.text(), "7")
        self.assertEqual(log_win.month_combobox.currentText(), "October")
        self.assertEqual(log_win.year_textbox.text(), "2019")

    def test_invalid_year(self):
        """MessageWin should be called if the user provides an invalid year."""
        log_win = interface.LogWin()
        log_win.year_textbox.setText("2")
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(log_win.change_log_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    def test_invalid_day(self):
        """MessageWin should be called if the user provides an invalid day of the month."""
        log_win = interface.LogWin()
        log_win.day_textbox.setText("42")
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(log_win.change_log_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    @patch('healthhelper.interface.LOG_FILES_DIR', TEST_LOG_FILE_DIR)
    def test_next_log_file(self):
        test_date = interface.datetime.date(2020, 6, 30)
        test_log_win = interface.LogWin(date=test_date)
        QTest.mouseClick(test_log_win.next_log_btn, Qt.LeftButton)
        self.assertEqual(test_log_win.next_log_win.date, interface.datetime.date(2020, 7, 1))

    @patch('healthhelper.interface.LOG_FILES_DIR', TEST_LOG_FILE_DIR)
    def test_no_next_log_file(self):
        """MessageWin should be called if there is no next log file."""
        test_date = interface.datetime.date(2020, 7, 1)
        test_log_win = interface.LogWin(date=test_date)
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(test_log_win.next_log_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    @patch('healthhelper.interface.LOG_FILES_DIR', TEST_LOG_FILE_DIR)
    def test_prev_log_file(self):
        test_date = interface.datetime.date(2020, 7, 1)
        test_log_win = interface.LogWin(date=test_date)
        QTest.mouseClick(test_log_win.prev_log_btn, Qt.LeftButton)
        self.assertEqual(test_log_win.prev_log_win.date, interface.datetime.date(2020, 6, 30))

    @patch('healthhelper.interface.LOG_FILES_DIR', TEST_LOG_FILE_DIR)
    def test_no_prev_log_file(self):
        """MessageWin should be called if there is no previous log file."""
        test_date = interface.datetime.date(2020, 6, 30)
        test_log_win = interface.LogWin(date=test_date)
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(test_log_win.prev_log_btn, Qt.LeftButton)
            message_win_mock.assert_called()


if __name__ == '__main__':
    unittest.main()
