"""Data gathering and manipulation module for the Health Helper application."""
# Standard library imports
import os
import csv
import ast

# Local imports
from PyQt5.QtWidgets import QDesktopWidget


def get_win_size():
    """Return the appropriate dimensions for a window based on current screen resolution."""
    screen_w = QDesktopWidget().frameGeometry().width()
    screen_h = QDesktopWidget().frameGeometry().height()

    if screen_w == 1024:
        win_w = 1024
    elif screen_w > 1024:
        win_w = 1152
    else:
        win_w = screen_w

    win_h = screen_h - 100
    return win_w, win_h


def get_table_entry_names(table):
    """Get the entry names listed in a table.

    :param table: A QTableWidget object, with each row representing one food dictionary or log entry.

    :returns: A list of three lists: all entry names in the table, the checked entry names only, and the unchecked
        entry names only.
    """
    all_entry_names = []
    checked_entry_names = []
    unchecked_entry_names = []
    for row_num in range(table.rowCount()):
        entry_name = table.item(row_num, 0).text()
        all_entry_names.append(entry_name)
        if table.item(row_num, 0).checkState():
            checked_entry_names.append(entry_name)
        else:
            unchecked_entry_names.append(entry_name)
    return [all_entry_names, checked_entry_names, unchecked_entry_names]


def get_edit_log_amounts(table, checked=False):
    """Get the user-input amounts from the table used to add or edit log entries.

    :param table: A QTableWidget object, with each row representing one food dictionary or log entry.
    :param checked: If True, only the input amounts corresponding to the checked entries are returned. If False, all
        amounts are returned regardless of check state. Default is False.

    :returns: A list of the user-input amounts. Each item is a list containing the number amount and its unit.
    """
    input_amounts = []
    for row_index in range(table.rowCount()):
        if checked:
            if not table.item(row_index, 0).checkState():
                continue

        # The table cells contain a widget with a layout that contains another widget for the input.
        # Get the cell's widget, then use its layout to extract the info from the input widget.
        amount_cell_widget = table.cellWidget(row_index, 1)
        amount_text = amount_cell_widget.layout().itemAt(0).widget().text()
        unit_cell_widget = table.cellWidget(row_index, 2)
        unit = unit_cell_widget.layout().itemAt(0).widget().currentText()
        input_amounts.append([amount_text, unit])
    return input_amounts


def get_entries(path, entry_names=None, match=True, return_all=False):
    """Get a specified set of entries from the food dictionary or a log file.

    :param path: A string of the food dictionary or log file pathname.
    :param entry_names: A list of entry names. Default is None.
    :param match: If True, the entries matching the names in entry_names are returned. If False, the entries that
        do not match the names in entry_names are returned. Default is True.
    :param return_all: If True, all entries in the file at the specified path are returned. Default is False.

    :returns: A list, where each item is a list of information describing one log or FD entry. The order of the
        returned entries corresponds to the order of names in entry_names.
    """
    entries = []
    if not os.path.exists(path):
        return 'file not found'

    with open(path) as f:
        reader = list(csv.reader(f))
        if return_all:
            return reader
        elif not entry_names:
            return []
        else:
            if match:
                for name in entry_names:
                    for row in reader:
                        if row[0] == name:
                            entries.append(row)
            else:
                for row in reader:
                    if row[0] in entry_names:
                        continue
                    else:
                        entries.append(row)
            return entries


def get_file_entry_names(path):
    """Get the names of all entries in the food dictionary or a log file.

    :param path: A string of the food dictionary or log file pathname.

    :returns: A list of the entry names associated with each entry in the food dictionary or a log file.
    """
    entry_names = []
    with open(path) as f:
        reader = list(csv.reader(f))
        for row in reader:
            entry_names.append(row[0])
    return entry_names


def select_all_entries(table):
    """Select all entries in a table widget.

    :param table: A QTableWidget object, with each row representing one food dictionary or log entry.
    """
    for row_index in range(table.rowCount()):
        table.item(row_index, 0).setCheckState(2)  # State 2 is a checkmark.


def unselect_all_entries(table):
    """Unselect all entries in a table widget.

    :param table: A QTableWidget object, with each row representing one food dictionary or log entry.
    """
    for row_index in range(table.rowCount()):
        table.item(row_index, 0).setCheckState(0)


def sum_shared_values(values_list):
    """Sum the values in the entry info list by index. The first item of every list in values_list is summed, and
    so on. If a float representing a sum can be converted into a whole number integer, do so.

    :param values_list: A list of lists. Each list consists of strings representing the info of one log entry.

    :returns: A list of the summed totals as strings.
    """
    totals = []
    for values in zip(*values_list):  # values is a list of info corresponding to one entry.
        sum_ = 0
        for val in values:
            if not val:
                val = 0
            sum_ += float(val)
        if int(sum_) == float(sum_):
            sum_ = int(sum_)
        totals.append(str(round(sum_, 2)))
    return totals


def calculate_entry_info(entries_to_modify, user_input_amounts, tally=False, edit=False):
    """Calculate finalized entry information based on the unaltered entry list and the user-input amounts.
    Specifically, multiply each number value associated with an entry by the number of servings calculated from
    the amount provided by the user.

    :param entries_to_modify: A list of lists. Each list consists of info describing one log entry.
    :param user_input_amounts:  A list of lists. Each list consists of an amount and its associated unit
        corresponding to one entry.
    :param tally: If True, any blank user input amounts are ignored. If False, a string is returned that will
        determine an error message to be displayed. Default is False.
    :param edit: If True, this function returns a string that determines a particular error message if the user
        provided insufficient or invalid amount input. Default is False.

    :returns: A list of lists. Each list is a set of string info describing one finalized log entry.

    As an example, if a serving size option from a food dictionary entry is 50 grams, and the user provides an amount
    of 100 grams for that food item, then every entry value is multiplied by the number of servings, 100 / 50 = 2.
    """
    calculated_entries = []
    for entry_num in range(len(entries_to_modify)):
        input_amount = user_input_amounts[entry_num][0]
        input_unit = user_input_amounts[entry_num][1]

        if tally:
            try:
                float(input_amount)
            except ValueError:
                # Non-float values have no weight in the tally.
                input_amount = 0
        else:
            # The user is adding entries to a log file.
            # Return a string that will determine which error message is presented to the user.
            if not input_amount:
                if edit:
                    return 'no amount given (log edit)'
                else:
                    return 'no amount given (log add)'
            else:
                try:
                    float(input_amount)
                except ValueError:
                    return 'invalid amount'

        if input_unit == 'Serving(s)':
            num_of_servings = float(input_amount)
        else:
            # Dictionary of serving sizes, units.
            serv_size_options = ast.literal_eval(entries_to_modify[entry_num][1])
            serv_size = serv_size_options[input_unit]
            num_of_servings = float(input_amount) / float(serv_size)

        edited_entry = []
        edited_entry.append(entries_to_modify[entry_num][0])
        edited_entry.append([input_amount, input_unit])

        # Delete [total_cost, total_servings] from each entry. The rest of the values will be
        # multiplied by the number of servings.
        del entries_to_modify[entry_num][17]

        for val in entries_to_modify[entry_num][2:]:
            # Ranges from calories to cost per serving.
            if not val:
                edited_entry.append(val)
                continue
            total_val = round(float(val) * num_of_servings, 2)
            # Drop the decimal if possible.
            if total_val == int(total_val):
                total_val = int(total_val)
            edited_entry.append(total_val)

        if num_of_servings == int(num_of_servings):
            num_of_servings = int(num_of_servings)
        edited_entry.insert(2, round(num_of_servings, 2))
        calculated_entries.append(edited_entry)
    return calculated_entries
