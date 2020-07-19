"""Test the FoodDictWin widget."""

import os
import unittest
from unittest.mock import patch, mock_open

from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import healthhelper.interface as interface

# Directory containing this file
this_dir = os.path.abspath(os.path.dirname(__file__))
# Path to the test food dictionary file
TEST_FD_PATH = os.path.join(this_dir, 'test_files', 'test_food_dictionary_file.csv')

app = QApplication([])


class TestFoodDictWin(unittest.TestCase):

    def test_fd_to_log_win(self):
        fd_win = interface.FoodDictWin()
        with patch.object(interface, 'LogWin') as log_win_mock:
            QTest.mouseClick(fd_win.goto_log_win_btn, Qt.LeftButton)
            log_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', 'nonexistent_path')
    def test_delete_fd_with_no_fd_file(self):
        """MessageWin should be called if the user clicks 'delete all entries' while no FD file exists."""
        fd_win = interface.FoodDictWin()
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(fd_win.delete_fd_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_delete_fd_with_test_fd_file(self):
        """QDialog should be called if the user clicks 'delete all entries' to ask for confirmation."""
        fd_win = interface.FoodDictWin()
        fd_win.fd_table.item(0, 0).setCheckState(2)
        with patch.object(interface, 'QDialog') as dialog_mock:
            QTest.mouseClick(fd_win.delete_fd_btn, Qt.LeftButton)
            dialog_mock.assert_called()

        # Check that the file is deleted and FoodDictWin is called.
        with patch.object(interface, 'FoodDictWin') as fd_win_mock, \
                patch('os.remove') as remove_mock:
            QTest.mouseClick(fd_win.yes_btn, Qt.LeftButton)
            remove_mock.assert_called()
            fd_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', 'nonexistent_path')
    def test_remove_selected_entries_with_no_fd_file(self):
        """MessageWin should be called if the user clicks 'delete selected entries' while no FD file exists."""
        fd_win = interface.FoodDictWin()
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(fd_win.delete_selected_entries_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_remove_selected_entries_no_entries_selected(self):
        """MessageWin should be called if the user clicks 'remove selected entries' while none are selected."""
        fd_win = interface.FoodDictWin()
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(fd_win.delete_selected_entries_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_remove_selected_entries_with_test_fd_file(self):
        """QDialog should be called if the user clicks 'remove selected entries' to ask for confirmation."""
        fd_win = interface.FoodDictWin()
        fd_win.fd_table.item(0, 0).setCheckState(2)
        with patch.object(interface, 'QDialog') as dialog_mock:
            QTest.mouseClick(fd_win.delete_selected_entries_btn, Qt.LeftButton)
            dialog_mock.assert_called()

        # Check that the file is edited and FoodDictWin is called.
        with patch.object(interface, 'FoodDictWin') as fd_win_mock, \
                patch('healthhelper.interface.open', mock_open()) as open_mock:
            QTest.mouseClick(fd_win.yes_btn, Qt.LeftButton)
            open_mock.assert_called()
            fd_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_fd_to_fd_edit_win(self):
        fd_win = interface.FoodDictWin()
        # Select the first FD entry.
        fd_win.fd_table.item(0, 0).setCheckState(2)
        with patch.object(interface, 'EditFoodDictWin') as edit_win_mock:
            QTest.mouseClick(fd_win.edit_entry_btn, Qt.LeftButton)
            edit_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_fd_to_fd_edit_win_no_selected_entries(self):
        fd_win = interface.FoodDictWin()
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(fd_win.edit_entry_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', 'nonexistent_path')
    def test_fd_to_fd_edit_win_no_fd_file(self):
        fd_win = interface.FoodDictWin()
        with patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(fd_win.edit_entry_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    def test_fd_to_fd_add_win(self):
        fd_win = interface.FoodDictWin()
        with patch.object(interface, 'EditFoodDictWin') as edit_win_mock:
            QTest.mouseClick(fd_win.add_entry_btn, Qt.LeftButton)
            edit_win_mock.assert_called()


if __name__ == '__main__':
    unittest.main()
