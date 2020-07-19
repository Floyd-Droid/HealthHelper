"""Test the the LogWin widget."""

import os
import unittest
from unittest.mock import patch

from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import healthhelper.interface as interface

# Directory containing this file
this_dir = os.path.abspath(os.path.dirname(__file__))
# Path to the test log file.
TEST_LOG_PATH = os.path.join(this_dir, 'test_files', 'test_log_file.csv')

app = QApplication([])


class TestLogWin(unittest.TestCase):

    def test_help_win(self):
        """QDialog should be called when the user clicks the help button."""
        log_win = interface.LogWin()
        with patch.object(interface, 'QDialog') as dialog_mock:
            QTest.mouseClick(log_win.help_btn, Qt.LeftButton)
            dialog_mock.assert_called()

    def test_log_to_fd_win(self):
        """Test transition from log display window to food dictionary display window."""
        log_win = interface.LogWin()
        with patch.object(interface, 'FoodDictWin') as fd_win_mock:
            QTest.mouseClick(log_win.goto_fd_btn, Qt.LeftButton)
            fd_win_mock.assert_called()

    @patch('os.path.join', return_value=TEST_LOG_PATH)
    def test_log_win_table(self, os_mock):
        """Check that all entries in the table are checked or unchecked after clicking the
        'select all' and 'unselect_all' buttons."""
        log_win = interface.LogWin()
        QTest.mouseClick(log_win.select_all_btn, Qt.LeftButton)
        for entry_index in range(log_win.log_table.rowCount()):
            # Checked entries have a checkState() equal to 2.
            self.assertEqual(log_win.log_table.item(entry_index, 0).checkState(), 2)

        QTest.mouseClick(log_win.unselect_all_btn, Qt.LeftButton)
        for entry_index in range(log_win.log_table.rowCount()):
            # Unchecked entries have a checkState() equal to 0.
            self.assertEqual(log_win.log_table.item(entry_index, 0).checkState(), 0)

    @patch('os.path.join', return_value='fakepath')
    def test_log_to_delete_log_win_no_log_file(self, join_mock):
        """Test transition from log display window to message window when user clicks 'delete log'
        while no log file exists."""
        log_win = interface.LogWin()
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(log_win.delete_log_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    @patch('os.path.join', return_value=TEST_LOG_PATH)
    def test_delete_log(self, join_mock):
        """Test transition from log display window to message window when user clicks 'delete log'
        using the test log file."""
        log_win = interface.LogWin()
        with patch.object(interface, 'QDialog') as dialog_mock:
            QTest.mouseClick(log_win.delete_log_btn, Qt.LeftButton)
            dialog_mock.assert_called()

        # Test that the log is deleted, and that LogWin is called.
        with patch('os.remove') as remove_mock, \
                patch.object(interface, 'LogWin') as log_win_mock:
            QTest.mouseClick(log_win.yes_btn, Qt.LeftButton)
            remove_mock.assert_called()
            log_win_mock.assert_called()


if __name__ == "__main__":
    unittest.main()
