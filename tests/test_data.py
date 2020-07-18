<<<<<<< HEAD
"""Tests for the data module."""
import os
import unittest
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from healthhelper import data
from healthhelper import interface

=======
"""Tests for the 'data' module."""
import os
import unittest
from healthhelper import data

# Set up globals
#
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
# Directory containing this file
this_dir = os.path.abspath(os.path.dirname(__file__))
# Path to the test food dictionary file
TEST_FD_PATH = os.path.join(this_dir, 'test_files', 'test_food_dictionary_file.csv')
# Path to the test log file.
TEST_LOG_PATH = os.path.join(this_dir, 'test_files', 'test_log_file.csv')

<<<<<<< HEAD
app = QApplication([])


class TestGetTableEntryNames(unittest.TestCase):
    """get_table_entry_names() should return a list of lists: A list of all table entries, a list of the
    selected entries, and a list of the unselected entries.
    """

    @patch('os.path.join', return_value=TEST_LOG_PATH)
    def test_log_table(self, join_mock):
        log_win = interface.LogWin()
        # Select the first two entries
        log_win.log_table.item(0, 0).setCheckState(2)
        log_win.log_table.item(1, 0).setCheckState(2)

        result = data.get_table_entry_names(log_win.log_table)
        self.assertEqual(result[0], ['cereal', 'chocolate', 'peanut butter'])
        self.assertEqual(result[1], ['cereal', 'chocolate'])
        self.assertEqual(result[2], ['peanut butter'])

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_fd_table(self):
        fd_win = interface.FoodDictWin()
        fd_win.fd_table.item(0, 0).setCheckState(2)
        fd_win.fd_table.item(1, 0).setCheckState(2)

        result = data.get_table_entry_names(fd_win.fd_table)
        self.assertEqual(result[0], ['cereal', 'chocolate', 'oats', 'peanut butter'])
        self.assertEqual(result[1], ['cereal', 'chocolate'])
        self.assertEqual(result[2], ['oats', 'peanut butter'])

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def test_log_edit_table(self):
        log_win = interface.LogWin()
        edit_geo = log_win.geometry()
        edit_date = interface.datetime.date(2020, 4, 12)
        edit_log_win = interface.EditLogWin(edit_date,
                                            TEST_LOG_PATH,
                                            edit_geo,
                                            edit_entry_names=None,
                                            edit=False)
        edit_log_win.edit_table.item(0, 0).setCheckState(2)
        edit_log_win.edit_table.item(1, 0).setCheckState(2)

        result = data.get_table_entry_names(edit_log_win.edit_table)
        self.assertEqual(result[0], ['cereal', 'chocolate', 'oats', 'peanut butter'])
        self.assertEqual(result[1], ['cereal', 'chocolate'])
        self.assertEqual(result[2], ['oats', 'peanut butter'])


class TestGetEditLogAmounts(unittest.TestCase):

    @patch('healthhelper.interface.FD_PATH', TEST_FD_PATH)
    def setUp(self):
        """Set up a table with four entries, two of which are checked. Provide amount information for each entry."""
        log_win = interface.LogWin()
        edit_geo = log_win.geometry()
        edit_date = interface.datetime.date(2020, 4, 12)
        self.edit_log_win = interface.EditLogWin(edit_date,
                                                 TEST_LOG_PATH,
                                                 edit_geo,
                                                 edit_entry_names=None,
                                                 edit=False)
        # Select two entries, but provide amount info for all entries.
        self.edit_log_win.edit_table.item(0, 0).setCheckState(2)
        self.edit_log_win.edit_table.item(1, 0).setCheckState(2)

        self.edit_log_win.edit_table.cellWidget(0, 1).layout().itemAt(0).widget().setText('60')
        self.edit_log_win.edit_table.cellWidget(0, 2).layout().itemAt(0).widget().setCurrentText('g')

        self.edit_log_win.edit_table.cellWidget(1, 1).layout().itemAt(0).widget().setText('2')
        self.edit_log_win.edit_table.cellWidget(1, 2).layout().itemAt(0).widget().setCurrentText('item(s)')

        self.edit_log_win.edit_table.cellWidget(2, 1).layout().itemAt(0).widget().setText('0.5')
        self.edit_log_win.edit_table.cellWidget(2, 2).layout().itemAt(0).widget().setCurrentText('cup')

        self.edit_log_win.edit_table.cellWidget(3, 1).layout().itemAt(0).widget().setText('4')
        self.edit_log_win.edit_table.cellWidget(3, 2).layout().itemAt(0).widget().setCurrentText('tbsp')

    def test_checked(self):
        """Test with checked=True. Only selected entry amounts are returned."""
        result = data.get_edit_log_amounts(self.edit_log_win.edit_table, checked=True)
        self.assertEqual(result, [['60', 'g'], ['2', 'item(s)']])

    def test_unchecked(self):
        """Test with checked=False. All entry amounts are returned."""
        result = data.get_edit_log_amounts(self.edit_log_win.edit_table, checked=False)
        self.assertEqual(result, [['60', 'g'], ['2', 'item(s)'], ['0.5', 'cup'], ['4', 'tbsp']])

=======
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1

class TestGetEntries(unittest.TestCase):

    def setUp(self):
<<<<<<< HEAD
        """Set up test entries from the log and food dictionary files."""
=======
        # Set up test entries from the log and food dictionary files.
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        self.fd_entries = [['cereal', "{'g': '60'}", '200', '1.5', '0', '0', '0', '0',
                            '0', '10', '48', '8', '2', '6', '0', '0', '7', "['2.00', '8']", '0.25'],
                           ['chocolate', "{'item(s)': '1', 'g': '25'}", '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '', '', "['2.23', '5']", '0.446'],
                           ['oats', "{'g': '40', 'cup': '0.25'}", '150', '2.5', '0', '0', '1', '1',
                            '0', '0', '27', '4', '2', '2', '1', '0', '5', '', ''],
                           ['peanut butter', "{'g': '32', 'tbsp': '2'}", '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '', '', '', '']]
        self.log_entries = [['cereal', "['1.5', 'Serving(s)']", '1.5', '300', '2.25', '0', '0', '0', '0',
                             '0', '15', '72', '12', '3', '9', '0', '0', '10.5', '0.38'],
                            ['chocolate', "['3', 'item(s)']", '3', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '', '', '1.34'],
                            ['peanut butter', "['4', 'tbsp']", '2', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '', '', '']]

    def test_nonexistent_path(self):
<<<<<<< HEAD
        """If the path doesn't exist, a string should be returned."""
        fake_path = "fakepath"
        result1 = data.get_entries(fake_path,
                                   entry_names=None,
                                   match=True,
                                   return_all=False)
        self.assertEqual(result1, "file not found")

    def test_return_match_only(self):
        """If match is True, only entries whose name matches one in entry_names should be returned."""
        fd_names = ['cereal', 'chocolate', 'peanut butter']
        log_names = ['cereal', 'peanut butter']
        result1 = data.get_entries(TEST_FD_PATH,
                                   entry_names=fd_names,
                                   match=True,
                                   return_all=False)
        result2 = data.get_entries(TEST_LOG_PATH,
                                   entry_names=log_names,
                                   match=True,
                                   return_all=False)
=======
        # If the path doesn't exist, a string should be returned.
        fake_path = "fakepath"
        result1 = data.get_entries(fake_path, entry_names=None, match=True, return_all=False)
        self.assertEqual(result1, "file not found")

    def test_return_match_only(self):
        # If match is True, only entries whose name matches one in entry_names should be returned.
        fd_names = ['cereal', 'chocolate', 'peanut butter']
        log_names = ['cereal', 'peanut butter']
        result1 = data.get_entries(TEST_FD_PATH, entry_names=fd_names, match=True, return_all=False)
        result2 = data.get_entries(TEST_LOG_PATH, entry_names=log_names, match=True, return_all=False)
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1

        self.assertEqual(result1, [self.fd_entries[0], self.fd_entries[1], self.fd_entries[3]])
        self.assertEqual(result2, [self.log_entries[0], self.log_entries[2]])

    def test_return_nonmatch_only(self):
<<<<<<< HEAD
        """If match is False, only entries whose name does not match any in entry_names should be returned."""
        fd_names = ['chocolate', 'peanut butter']
        log_names = ['cereal', 'peanut butter']
        result1 = data.get_entries(TEST_FD_PATH,
                                   entry_names=fd_names,
                                   match=False,
                                   return_all=False)
        result2 = data.get_entries(TEST_LOG_PATH,
                                   entry_names=log_names,
                                   match=False,
                                   return_all=False)
=======
        # If match is False, only entries whose name does not match any in entry_names should be returned.
        fd_names = ['chocolate', 'peanut butter']
        log_names = ['cereal', 'peanut butter']
        result1 = data.get_entries(TEST_FD_PATH, entry_names=fd_names, match=False, return_all=False)
        result2 = data.get_entries(TEST_LOG_PATH, entry_names=log_names, match=False, return_all=False)

>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        self.assertEqual(result1, [self.fd_entries[0], self.fd_entries[2]])
        self.assertEqual(result2, [self.log_entries[1]])

    def test_return_all(self):
<<<<<<< HEAD
        """Check that all entries are returned if return_all is True."""
        result1 = data.get_entries(TEST_FD_PATH,
                                   entry_names=None,
                                   match=False,
                                   return_all=True)
        result2 = data.get_entries(TEST_LOG_PATH,
                                   entry_names=None,
                                   match=False,
                                   return_all=True)
=======
        # Ensure that all entries are returned if return_all is True.
        result1 = data.get_entries(TEST_FD_PATH, entry_names=None, match=False, return_all=True)
        result2 = data.get_entries(TEST_LOG_PATH, entry_names=None, match=False, return_all=True)
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        self.assertEqual(result1, self.fd_entries)
        self.assertEqual(result2, self.log_entries)


class TestGetFileEntryNames(unittest.TestCase):

    def test_name_list(self):
<<<<<<< HEAD
        """Check that all entry names are pulled from the test log and food dictionary files."""
=======
        # Ensure that all entry names are pulled from the test log and food dictionary files.
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        result1 = data.get_file_entry_names(TEST_FD_PATH)
        result2 = data.get_file_entry_names(TEST_LOG_PATH)
        self.assertEqual(result1, ['cereal', 'chocolate', 'oats', 'peanut butter'])
        self.assertEqual(result2, ['cereal', 'chocolate', 'peanut butter'])


class TestSumSharedValues(unittest.TestCase):

    def test_sum(self):
<<<<<<< HEAD
        """The first number of each list should be summed, and so on."""
=======
        # The first number of each list should be summed, and so on.
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        val_list = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        result = data.sum_shared_values(val_list)
        self.assertEqual(result, ['12', '15', '18'])


class TestCalculateEntryInfo(unittest.TestCase):

<<<<<<< HEAD
    def setUp(self):
        """Set up test food dictionary entries and test amount inputs."""
=======
    def setUp(self):  # fixture method
        # Set up test food dictionary entries and test amount inputs.
        #
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        # Entry with all values
        self.entry1 = ['cereal', "{'g': '60'}", '200', '1.5', '0', '0', '0', '0',
                       '0', '10', '48', '8', '2', '6', '0', '0', '7', "['2.00', '8']", '0.25']
        # Entry with minimum number of values
        self.entry2 = ['peanut butter', "{'g': '32', 'tbsp': '2'}", '', '', '', '', '', '',
                       '', '', '', '', '', '', '', '', '', '', '']
        self.fd_entries = [self.entry1, self.entry2]
        self.amounts = [['1.5', 'Serving(s)'], ['4', 'tbsp']]
        self.missing_amounts = [['', 'Serving(s)'], ['', 'tbsp']]
        self.invalid_amounts = [['+', 'Serving(s)'], ['.', 'tbsp']]

    def test_length(self):
<<<<<<< HEAD
        """Each entry list must have 19 items."""
=======
        # Each entry list must have 19 items.
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        for entry in self.fd_entries:
            self.assertEqual(len(entry), 19)

    def test_with_invalid_amount(self):
<<<<<<< HEAD
        """When the user attempts to write entries to a log file without providing valid amounts,
        a particular string should be returned."""
        # Missing amount, user is adding entries.
        result = data.calculate_entry_info(self.fd_entries,
                                           self.missing_amounts,
                                           tally=False,
                                           edit=False)
        self.assertEqual(result, 'no amount given (log add)')

        # Missing amount, user is editing entries.
        result = data.calculate_entry_info(self.fd_entries,
                                           self.missing_amounts,
                                           tally=False,
                                           edit=True)
        self.assertEqual(result, 'no amount given (log edit)')

        # Non-number amount provided.
        result = data.calculate_entry_info(self.fd_entries,
                                           self.invalid_amounts,
                                           tally=False,
                                           edit=True)
        self.assertEqual(result, 'invalid amount')

    def test_multiply_by_num_servings(self):
        """Check that each value in an entry is multiplied by the number of servings, and that
        any missing values are ignored."""
=======
        # When the user attempts to write entries to a log file without providing valid amounts,
        # a particular string should be returned.
        #
        # Missing amount, user is adding entries.
        result = data.calculate_entry_info(self.fd_entries, self.missing_amounts, tally=False, edit=False)
        self.assertEqual(result, 'no amount given (log add)')

        # Missing amount, user is editing entries.
        result = data.calculate_entry_info(self.fd_entries, self.missing_amounts, tally=False, edit=True)
        self.assertEqual(result, 'no amount given (log edit)')

        # Non-number amount provided
        result = data.calculate_entry_info(self.fd_entries, self.invalid_amounts, tally=False, edit=True)
        self.assertEqual(result, 'invalid amount')

    def test_multiply_by_num_servings(self):
        # Ensure each value in an entry is multiplied by the number of servings, and that
        # any missing values are ignored.
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        expected_result1 = ['cereal', ['1.5', 'Serving(s)'], 1.5, 300, 2.25, 0, 0, 0, 0,
                            0, 15, 72, 12, 3, 9, 0, 0, 10.5, 0.38]
        expected_result2 = ['peanut butter', ['4', 'tbsp'], 2, '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '', '', '']
<<<<<<< HEAD
        result = data.calculate_entry_info(self.fd_entries,
                                           self.amounts,
                                           tally=False,
                                           edit=False)
=======
        result = data.calculate_entry_info(self.fd_entries, self.amounts, tally=False, edit=False)
>>>>>>> 98ff17273899349b8309b1c08ddfa42e81c8a8e1
        self.assertEqual(result, [expected_result1, expected_result2])


if __name__ == "__main__":
    unittest.main()
