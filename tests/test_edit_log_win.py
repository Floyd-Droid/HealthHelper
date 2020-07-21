"""Test the Log Window edit widget."""

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
# Path to the test log file.
TEST_LOG_PATH = os.path.join(this_dir, 'test_files', 'test_log_file.csv')

app = QApplication([])


@patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
class TestEditLogWin(unittest.TestCase):

    def setUp(self):
        """Set up args to be passed to EditLogWin."""
        self.log_win = interface.LogWin()
        self.edit_geo = self.log_win.geometry()
        self.edit_date = interface.datetime.date(2020, 4, 12)

    def test_cancel(self,):
        """Test transition from log add window to log display window after clicking 'cancel'."""
        edit_log_win = interface.EditLogWin(self.edit_date, TEST_LOG_PATH, self.edit_geo, edit=False)
        with patch.object(interface, 'LogWin') as log_win_mock:
            QTest.mouseClick(edit_log_win.back_to_log_win_btn, Qt.LeftButton)
            log_win_mock.assert_called()

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_edit_log_win_table(self):
        """Check that all entries in the table are checked or unchecked after clicking the
        'select all' and 'unselect_all' buttons."""
        log_win = interface.LogWin()
        edit_geo = log_win.geometry()
        edit_date = interface.datetime.date(2020, 4, 12)
        edit_log_win = interface.EditLogWin(edit_date, TEST_LOG_PATH, edit_geo)

        QTest.mouseClick(edit_log_win.select_all_btn, Qt.LeftButton)
        for entry_index in range(edit_log_win.edit_table.rowCount()):
            self.assertEqual(edit_log_win.edit_table.item(entry_index, 0).checkState(), 2)

        QTest.mouseClick(edit_log_win.unselect_all_btn, Qt.LeftButton)
        for entry_index in range(edit_log_win.edit_table.rowCount()):
            self.assertEqual(edit_log_win.edit_table.item(entry_index, 0).checkState(), 0)

    def test_add_entry_to_new_log(self):
        """Test creation of and writing to a log file."""
        edit_log_win = interface.EditLogWin(self.edit_date, 'nonexistent_log_path', self.edit_geo, edit=False)
        # Select the first item in the table, and give an amount of 60 grams.
        edit_log_win.edit_table.item(0, 0).setCheckState(2)
        amount_cell_widget = edit_log_win.edit_table.cellWidget(0, 1)
        amount_cell_widget.layout().itemAt(0).widget().setText('60')
        unit_cell_widget = edit_log_win.edit_table.cellWidget(0, 2)
        unit_cell_widget.layout().itemAt(0).widget().setCurrentText('grams')
        with patch('healthhelper.interface.open', mock_open()), \
                patch('os.makedirs', return_value=None) as makedirs_mock, \
                patch.object(interface, 'LogWin') as log_win_mock:
            QTest.mouseClick(edit_log_win.update_btn, Qt.LeftButton)
            makedirs_mock.assert_called()
            log_win_mock.assert_called()

    def test_add_entry_to_existing_log(self):
        edit_log_win = interface.EditLogWin(self.edit_date, TEST_LOG_PATH, self.edit_geo, edit=False)
        # Select the third item in the table (oats, row index 2), which has not yet been added to the test log.
        # Selecting any other item would result in a duplicate item error message.
        edit_log_win.edit_table.item(2, 0).setCheckState(2)
        amount_cell_widget = edit_log_win.edit_table.cellWidget(2, 1)
        amount_cell_widget.layout().itemAt(0).widget().setText('5')
        with patch('healthhelper.interface.open', mock_open()), \
                patch.object(interface, 'LogWin') as log_win_mock:
            QTest.mouseClick(edit_log_win.update_btn, Qt.LeftButton)
            log_win_mock.assert_called()

    def test_duplicate_entry_selected_to_add(self):
        """MessageWin should be called if the user attempts to add a duplicate item to a log."""
        edit_log_win = interface.EditLogWin(self.edit_date, TEST_LOG_PATH, self.edit_geo, edit=False)
        # Select 'cereal', which is already in the log.
        edit_log_win.edit_table.item(0, 0).setCheckState(2)
        amount_cell_widget = edit_log_win.edit_table.cellWidget(0, 1)
        amount_cell_widget.layout().itemAt(0).widget().setText('5')
        with patch('healthhelper.interface.open', mock_open()), \
                patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(edit_log_win.update_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    def test_adding_nonfloat_amount_to_log(self):
        """MessageWin should be called if the user provides a non-float amount to add."""
        edit_log_win = interface.EditLogWin(self.edit_date, TEST_LOG_PATH, self.edit_geo, edit=False)
        edit_log_win.edit_table.item(0, 0).setCheckState(2)
        amount_cell_widget = edit_log_win.edit_table.cellWidget(0, 1)
        amount_cell_widget.layout().itemAt(0).widget().setText('.')
        with patch('healthhelper.interface.open', mock_open()), \
                patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(edit_log_win.update_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    def test_no_amount_provided_to_add(self):
        """MessageWin should be called if the user doesn't provide an amount to add for a selected entry."""
        edit_log_win = interface.EditLogWin(self.edit_date, TEST_LOG_PATH, self.edit_geo, edit=False)
        edit_log_win.edit_table.item(0, 0).setCheckState(2)
        with patch('healthhelper.interface.open', mock_open()), \
                patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(edit_log_win.update_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    def test_no_selected_entries_to_add(self):
        """MessageWin should be called if the user clicks the update button without selecting any entries to add."""
        edit_log_win = interface.EditLogWin(self.edit_date, TEST_LOG_PATH, self.edit_geo, edit=False)
        with patch('healthhelper.interface.open', mock_open()), \
                patch.object(interface, 'MessageWin') as message_win_mock:
            QTest.mouseClick(edit_log_win.update_btn, Qt.LeftButton)
            message_win_mock.assert_called()

    def test_edit_log_entries(self):
        """Check that an entry in the log file is successfully edited."""
        edit_log_win = interface.EditLogWin(self.edit_date, TEST_LOG_PATH, self.edit_geo,
                                            edit_entry_names=['cereal'], edit=True)
        amount_cell_widget = edit_log_win.edit_table.cellWidget(0, 1)
        amount_cell_widget.layout().itemAt(0).widget().setText('2')
        with patch('healthhelper.interface.open', mock_open()), \
                patch.object(interface, 'LogWin') as log_win_mock:
            QTest.mouseClick(edit_log_win.update_btn, Qt.LeftButton)
            log_win_mock.assert_called()


if __name__ == "__main__":
    unittest.main()
