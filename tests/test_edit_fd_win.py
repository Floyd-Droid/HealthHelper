"""Test the EditFoodDictWin widget."""

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


class TestEditFoodDictWin(unittest.TestCase):

    @patch.object(interface, 'FoodDictWin')
    def test_cancel(self, fd_win_mock):
        edit_fd_win = interface.EditFoodDictWin()
        QTest.mouseClick(edit_fd_win.back_to_fd_win_btn, Qt.LeftButton)
        fd_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_edit_entry_name_and_serving_size(self):
        """Check that the entry's name and serving size info is placed into the correct fields by default."""
        edit_fd_win = interface.EditFoodDictWin(edit_entry_name='cereal')
        name = edit_fd_win.info1_layout.itemAt(1).widget().text()
        self.assertEqual(name, 'cereal')

        amount = edit_fd_win.info1_layout.itemAt(3).itemAt(0).widget().text()
        unit = edit_fd_win.info1_layout.itemAt(3).itemAt(1).widget().currentText()
        self.assertEqual(amount, '60')
        self.assertEqual(unit, 'g')

    @patch('healthhelper.interface.FD_PATH', 'nonexistent_path')
    def test_fd_file_creation(self):
        edit_fd_win = interface.EditFoodDictWin()
        # Required info: entry name and at least one serving size.
        edit_fd_win.info1_layout.itemAt(1).widget().setText('new_entry')
        edit_fd_win.info1_layout.itemAt(3).itemAt(0).widget().setText('2')
        edit_fd_win.info1_layout.itemAt(3).itemAt(1).widget().setCurrentText('oz')

        with patch.object(interface, 'FoodDictWin') as fd_win_mock, \
                patch('healthhelper.interface.open', mock_open()) as open_mock, \
                patch('os.makedirs', return_value=None) as makedirs_mock:
            QTest.mouseClick(edit_fd_win.done_btn, Qt.LeftButton)
            open_mock.assert_called()
            fd_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_fd_file_edit(self):
        edit_fd_win = interface.EditFoodDictWin(edit_entry_name='cereal')
        with patch.object(interface, 'FoodDictWin') as fd_win_mock, \
                patch('healthhelper.interface.open', mock_open()) as open_mock:
            QTest.mouseClick(edit_fd_win.done_btn, Qt.LeftButton)
            open_mock.assert_called()
            fd_win_mock.assert_called()


if __name__ == '__main__':
    unittest.main()
