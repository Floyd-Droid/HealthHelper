"""
UI for the Health Helper application.

Keep track of daily nutrition and track spending on groceries with the Health Helper application.
The user provides nutrition and cost information for a custom set of food items stored in a
csv file called the "food dictionary" (FD). This information is used to create other csv files
called log files, which store information about how many calories, sugar, etc. the user has had, and how
much the amount of food costs. The application allows the user to take control over their health and
grocery spending.
"""
# Standard library imports
import os
import csv
import datetime
import ast
import bisect
import copy

# Third party imports
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import (QMainWindow, QDialog, QWidget, QLineEdit, QPushButton, QLabel, QComboBox,
                             QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout, QSpacerItem,
                             QDesktopWidget, QHBoxLayout, QVBoxLayout, QFormLayout)

# Local imports
from healthhelper import data

# Initialise globals
# Directory containing this file.
FILE_DIR = os.path.abspath(os.path.dirname(__file__))

# Path to the food dictionary csv file.
FD_PATH = os.path.join(FILE_DIR, '..', 'files', 'food_dictionary.csv')

# Path to the log files directory.
LOG_FILES_DIR = os.path.join(FILE_DIR, '..', 'files', 'log files')


class LogsWin(QMainWindow):
    """Allow the user to view or edit the contents of a log file, which uses the food dictionary as a source of
    entry information. The log is a csv file that contains info about the user's food consumption for the day.
    For example, one row in a log file may look like:

    spaghetti,"['112', 'g']",2,360,3,0,0,0,0,0,0,80,12,,,4,0,14,0.12

    The above entry represents 112 grams of spaghetti. The third position is the number of servings (2), followed by
    the calories, total fat, saturated fat, trans fat, polyunsaturated fat, monounsaturated fat, cholesterol,
    sodium, total carbohydrate, total dietary fiber, soluble fiber, insoluble fiber, total sugars, added sugars, and
    protein. The last value is the total cost of the entry (12 cents). The 'missing' values are those
    that were ignored by the user when adding the food item to the food dictionary, since the user is not required to
    give all info.

    For each log entry, the user provides a weight or volume amount corresponding to one of the serving size options
    stored in the food dictionary. In this example, the user ate 112 grams of spaghetti. The food dictionary would
    list the corresponding serving size to be 56 grams, so the user ate two servings. Each value in the food
    dictionary entry for spaghetti is then multiplied by 2 and added to a log file for the specified date.
    """

    def __init__(self, date=datetime.date.today(), geo=None):
        """Constructor.

        :param date: datetime object that determines the log file to be viewed or edited. Default is the current date.
        :param geo: A QRect() object containing the dimensions and position of the previous window. The current
            window's geometry is set equal to this value. Default is None.
        """
        super().__init__()
        self.date = date
        self.geo = geo

        # Day in 01 - 31 format.
        self.day = self.date.strftime('%d')
        # Month in 01 - 12 format.
        self.month = self.date.strftime('%m')
        # Month name (January, February, etc.)
        self.month_str = self.date.strftime('%B')
        self.year = str(self.date.year)

        # Example log file path for June 12, 2020: /files/log files/2020/06 - June/12.csv
        self.log_file_path = os.path.join(LOG_FILES_DIR, self.year, self.month + ' - '
                                          + self.month_str, self.day + '.csv')
        self.init_ui()

    def init_ui(self):
        """Set up UI. Include a widget that allows the user to change the log file by providing a valid date.
        Include a table that displays info about the entries in the log file. Include a table that displays the
        tallied information of all entries as well as the selected entries only. Include buttons that allow
        the user to add or edit log entries, navigate log files, select or unselect all entries, and go to the
        food dictionary window.
        """
        self.setWindowTitle("View or Edit Logs")
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # Center the window unless a previous window's geometry was passed to the instance.
        if not self.geo:
            self.w, self.h = data.get_win_size()
            self.resize(self.w, self.h)
            self.center()
        else:
            self.setGeometry(self.geo)

        # Help button informs the user how to use the application.
        self.help_btn = QPushButton('Help', self)
        self.help_btn.setFixedSize(75, 27)

        # Widget that displays a date and allows user input to change the date.
        self.log_date_w = QWidget()
        self.log_date_w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.log_date_layout = QHBoxLayout()

        log_date_label = QLabel('Log date:', self)
        month_combobox = QComboBox(self)
        month_combobox.setFixedSize(100, 27)
        month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                      'November', 'December']
        month_combobox.addItems(month_list)

        # Only allow positive integers for the date input fields.
        validator = QIntValidator()
        validator.setBottom(0)
        day_textbox = QLineEdit(self)
        day_textbox.setFixedSize(50, 27)
        day_textbox.setValidator(validator)
        year_textbox = QLineEdit(self)
        year_textbox.setFixedSize(50, 27)
        year_textbox.setValidator(validator)

        self.log_date_layout.addWidget(log_date_label)
        self.log_date_layout.addWidget(month_combobox)
        self.log_date_layout.addWidget(day_textbox)
        self.log_date_layout.addWidget(year_textbox)
        self.log_date_w.setLayout(self.log_date_layout)

        # Set the default log date widget values to the selected or default date.
        month_combobox.setCurrentIndex(int(self.month) - 1)
        # Convert day to int, then string. For example, 01 becomes 1.
        day_textbox.setText(str(int(self.day)))
        year_textbox.setText(self.year)

        # Add buttons for choosing the log to view or edit.
        # The current date's log is selected by default.
        self.change_log_btn = QPushButton('Change log', self)
        self.change_log_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.prev_log_btn = QPushButton('Previous log', self)
        self.prev_log_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.next_log_btn = QPushButton('Next log', self)
        self.next_log_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Table widget that displays the details of the selected log.
        self.log_table = QTableWidget()
        self.log_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.col_labels = ['Name', 'Amount', 'Calories', 'Total\nFat\n(g)', 'Sat.\nFat\n(g)', 'Trans\nFat\n(g)',
                           'Poly.\nFat\n(g)', 'Mono.\nFat\n(g)', 'Chol.\n(mg)', 'Sodium\n(mg)', 'Total\nCarbs\n(g)',
                           'Total\nFiber\n(g)', 'Sol.\nFiber\n(g)', 'Insol.\nFiber\n(g)',
                           'Total\nSugars\n(g)', 'Added\nSugars\n(g)', 'Protein\n(g)', 'Cost\n($)']

        # Place the grand totals and subtotals in a separate table widget for easier viewing.
        # The subtotals are the totals only for the entries that are selected.
        self.totals_table = QTableWidget()
        self.totals_table.setFixedHeight(124)
        self.totals_table.setRowCount(2)
        # -1 to exclude the 'amount' column for the totals table.
        self.totals_table.setColumnCount(len(self.col_labels) - 1)
        self.totals_table.setRowHeight(0, 50)
        self.totals_table.setRowHeight(1, 50)
        totals_item = QTableWidgetItem('All entries')
        totals_item.setTextAlignment(Qt.AlignCenter)
        totals_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.totals_table.setItem(0, 0, totals_item)

        # To disallow interacting with the rest of the cells, place empty
        # items into the cells and set their flags.
        for i in range(1, self.totals_table.columnCount()):
            blank_item = QTableWidgetItem('')
            blank_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.totals_table.setItem(0, i, blank_item)

        totals_h_header = self.totals_table.horizontalHeader()
        self.totals_table.setHorizontalHeaderLabels(['Totals', *self.col_labels[2:]])
        totals_h_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # Allow first column to stretch as table expands.
        totals_h_header.setSectionResizeMode(0, QHeaderView.Stretch)

        totals_v_header = self.totals_table.verticalHeader()
        # Remove default numbered header.
        totals_v_header.setVisible(False)
        totals_v_header.setDefaultSectionSize(30)

        subtotals_item = QTableWidgetItem('Selected entries')
        subtotals_item.setTextAlignment(Qt.AlignCenter)
        subtotals_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.totals_table.setItem(1, 0, subtotals_item)

        # For subtotals, leave the other cells blank until the user selects entries.
        for i in range(1, self.totals_table.columnCount()):
            blank_item = QTableWidgetItem('')
            blank_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.totals_table.setItem(1, i, blank_item)

        # Alert the user if the log file doesn't exist.
        if not os.path.exists(self.log_file_path):
            self.log_table.setRowCount(1)
            self.log_table.setColumnCount(1)
            no_log_item = QTableWidgetItem(f"There is no log file for {self.month_str} {int(self.day)}, {self.year}.")
            self.log_table.setItem(0, 0, no_log_item)
            no_log_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            log_h_header = self.log_table.horizontalHeader()
            log_h_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.log_table.horizontalHeader().setVisible(False)
            self.log_table.verticalHeader().setVisible(False)
        else:
            # Place one set of entry information into each row of the table.
            self.log_entries = data.get_entries(self.log_file_path, return_all=True)  # [[entry1], [entry2], ...]]
            self.log_table.setRowCount(len(self.log_entries))
            self.log_table.setColumnCount(len(self.col_labels))

            for entry_num in range(len(self.log_entries)):
                self.log_table.setRowHeight(entry_num, 50)
                entry = self.log_entries[entry_num]  # [name, amount, num_servings, calories, ...]
                name_checkbox = QTableWidgetItem(entry[0])
                name_checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                name_checkbox.setCheckState(Qt.Unchecked)
                self.log_table.setItem(entry_num, 0, name_checkbox)
                amount_list = ast.literal_eval(entry[1])  # [amount, unit]
                num_of_servings = ast.literal_eval(entry[2])

                # For each amount table cell, display the amount in terms of
                # weight/volume (if available) and serving size.
                if amount_list[1] == 'Serving(s)':
                    serv_item = QTableWidgetItem(f"{num_of_servings} serving(s)")
                else:
                    serv_item = QTableWidgetItem(f"{amount_list[0]}  {amount_list[1]}\n{num_of_servings} serving(s)")
                serv_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                serv_item.setTextAlignment(Qt.AlignCenter)
                self.log_table.setItem(entry_num, 1, serv_item)

                for i in range(3, len(entry)):
                    # Ranges from number of servings had to the entry cost.
                    if i == 18:
                        if entry[18]:
                            # If there is cost info, show 2 decimal places.
                            cost = float(entry[i])
                            val = QTableWidgetItem(f'{cost:.2f}')
                        else:
                            val = QTableWidgetItem("")
                    else:
                        val = QTableWidgetItem(entry[i])
                    val.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    val.setTextAlignment(Qt.AlignCenter)
                    # Use i - 1 since the amount and number of servings were both placed into column 2.
                    self.log_table.setItem(entry_num, i - 1, val)

            # For the totals table, create a deep copy of the log entries to delete values irrelevant to the tally.
            # The original must remain intact for when the user selects an entry, resetting the subtotals.
            self.log_entries_copy = copy.deepcopy(self.log_entries)
            for entry in self.log_entries_copy:
                # Delete the entry name, serving size options, and number of servings had for each entry.
                del entry[:3]
            grand_totals = data.sum_shared_values(self.log_entries_copy)

            for i in range(len(grand_totals)):
                if i == 15:
                    cost = float(grand_totals[i])
                    val = QTableWidgetItem(f'{cost:.2f}')
                else:
                    val = QTableWidgetItem(grand_totals[i])
                val.setTextAlignment(Qt.AlignCenter)
                val.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.totals_table.setItem(0, i + 1, val)  # i + 1 to skip over the row title cell.

            # If an entry is checked or unchecked, re-tally the subtotals.
            self.log_table.itemChanged.connect(self.selection_changed)
            log_h_header = self.log_table.horizontalHeader()
            self.log_table.setHorizontalHeaderLabels(self.col_labels)
            log_h_header.setSectionResizeMode(QHeaderView.ResizeToContents)
            log_h_header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Add a button that takes the user to the food dictionary view screen.
        self.goto_fd_btn = QPushButton('Go to food dictionary', self)
        self.goto_fd_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add buttons that add or remove entries from the log.
        self.add_entries_btn = QPushButton('Add entries to log', self)
        self.add_entries_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.remove_entries_btn = QPushButton('Remove selected entries', self)
        self.remove_entries_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add buttons that check or uncheck all entries.
        self.select_all_btn = QPushButton('Select all entries', self)
        self.select_all_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.unselect_all_btn = QPushButton('Unselect all entries', self)
        self.unselect_all_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add a button that deletes the currently selected log.
        self.delete_log_btn = QPushButton('Delete log', self)
        self.delete_log_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add a button that allows the user to edit the selected entries.
        self.edit_entries_btn = QPushButton('Edit selected entries', self)
        self.edit_entries_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.help_btn.clicked.connect(self.help_info)
        self.change_log_btn.clicked.connect(self.change_date)
        self.prev_log_btn.clicked.connect(self.goto_prev_log)
        self.next_log_btn.clicked.connect(self.goto_next_log)
        self.add_entries_btn.clicked.connect(self.add_entries)
        self.select_all_btn.clicked.connect(self.select_all)
        self.unselect_all_btn.clicked.connect(self.unselect_all)
        self.delete_log_btn.clicked.connect(self.confirm_delete_log)
        self.remove_entries_btn.clicked.connect(self.remove_entries)
        self.edit_entries_btn.clicked.connect(self.edit_entries)
        self.goto_fd_btn.clicked.connect(self.goto_fd_win)

        layout = QGridLayout()
        spacer = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.help_btn, 0, 0)
        layout.addWidget(self.goto_fd_btn, 0, 1)
        layout.addWidget(self.log_date_w, 0, 3, 1, 2, alignment=Qt.AlignCenter)
        layout.addWidget(self.change_log_btn, 0, 5, alignment=Qt.AlignLeft)
        layout.addWidget(self.prev_log_btn, 0, 7, alignment=Qt.AlignRight)
        layout.addWidget(self.next_log_btn, 0, 8)

        layout.addWidget(self.log_table, 1, 0, 1, 9)
        layout.addItem(spacer, 2, 0, 1, 9)
        layout.addWidget(self.totals_table, 3, 0, 1, 9)
        layout.addItem(spacer, 4, 0, 1, 9)

        layout.addWidget(self.select_all_btn, 5, 0)
        layout.addWidget(self.unselect_all_btn, 5, 1)
        layout.addWidget(self.delete_log_btn, 5, 3, alignment=Qt.AlignRight)
        layout.addWidget(self.remove_entries_btn, 5, 4, alignment=Qt.AlignRight)
        layout.addWidget(self.edit_entries_btn, 5, 7)
        layout.addWidget(self.add_entries_btn, 5, 8)
        layout.addItem(spacer, 6, 0, 1, 9)

        # QMainWindow requires the layout to be applied to a widget,
        # which is then set as the central widget of the window.
        main_w = QWidget()
        main_w.setLayout(layout)
        self.setCentralWidget(main_w)
        self.setStyleSheet('''
            QMainWindow {
                background-color: rgb(0, 0, 30);
            }
            QWidget {
                font: 14px;
            }
            QLabel {
                color: white;
                font-weight: 500;
            }
            QHeaderView {
                background-color: rgb(90, 90, 180);
            }
            QHeaderView::section {
                font: 14px;
                font-weight: 500;
                color: white;
                background-color: rgb(90, 90, 180);
                border-top: 0px solid black;
                border-bottom: 1px solid black;
                border-left: 0px solid black;
                border-right: 1px solid black;   
            }
            QHeaderView::section::checked {
                background-color: rgb(60, 180, 60);
            }
            QTableView {
                background-color: rgb(200, 200, 255);
                selection-background-color: rgb(60, 180, 60);
                selection-color: black;
                gridline-color: black;
                font: 14px;
                font-weight: 500;
            }
            QTableCornerButton::section {
                background-color: rgb(90, 90, 180);
                border: 1px solid rgb(90, 90, 180);
            }
            QPushButton {
                font: 14px;
                color: rgb(255, 255, 255);
                background-color: rgb(70, 70, 70);
                border-width: 2px;
                border-style: outset;
                border-radius: 5px;
                border-color: gray;
                padding: 3px;
            }
            QLineEdit {
                border: 1px solid gray;
                border-radius: 5px;
            }
            QComboBox {
                border: 1px solid gray;
                border-radius: 5px;
            }
            ''')

    def center(self):
        """Move the window to the center of the screen by moving the window geometry's center point to the center
        of the desktop screen.
        """
        geo = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center_point)
        self.move(geo.topLeft())

    def help_info(self):
        """Show the user a dialog box with instructions to navigate or use the application from the log view
        screen.
        """
        info = QLabel("- Enter the date of the log you would like to view or edit, then click 'Change log'. The "
                      "current date is selected by default.\n\n"
                      "- The food dictionary is used to add entries to a log. To view or edit the food "
                      "dictionary, click the 'Go to food dictionary' button in the top left of the screen.\n\n"
                      "- Once you have added entries to the food dictionary, you can click the 'Add entries' button "
                      "on the log view screen to choose which entries from the food dictionary are added to the log, "
                      "along with the amount to add. You can also experiment with different food combinations "
                      "without adding them to a log, allowing you to plan a meal.\n\n"
                      "- The table below the log table displays the total nutritional information (and cost) of all "
                      "log entries, as well as the totals for the selected entries only.\n\n"
                      "- To edit existing log entries, select the entries to be edited, then click the 'Edit "
                      "selected entries' button.\n\n"
                      "- You can quickly remove entries from the log by selecting them and clicking the 'Remove "
                      "selected entries' button. You can also delete the log altogether with the 'Delete log' "
                      "button.", self)
        info.setWordWrap(True)
        info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        ok_btn = QPushButton('Ok', self)
        ok_btn.setFixedSize(75, 27)
        ok_btn.clicked.connect(self.close_win)

        self.dlg = QDialog(self)
        self.dlg.setWindowTitle('Help')
        self.dlg.setFixedWidth(600)
        help_layout = QVBoxLayout()
        help_layout.addWidget(info)
        help_layout.addWidget(ok_btn, alignment=Qt.AlignRight)
        help_layout.setSpacing(20)
        self.dlg.setLayout(help_layout)
        self.dlg.setStyleSheet('''
            QDialog {
                background-color: rgb(255, 250, 230);
                border: 2px solid red;
            }
            QWidget {
                font: 14px;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                color: black;
                background-color: rgb(210, 210, 210);
                border-width: 2px;
                border-style: outset;
                border-radius: 5px;
                border-color: rgb(70, 70, 70);
                padding: 3px;
            }
            ''')
        self.dlg.show()

    def change_date(self):
        """Use the date information provided by the user to change the log file that is to be viewed or edited.
        Give an error message if insufficient or invalid date information is provided.
        """
        # Go through the layout and get the user-input data. January is the 0th index of the combobox, but is
        # represented by the integer 1 for a datetime object, so add 1 to the month combobox index.
        month = self.log_date_layout.itemAt(1).widget().currentIndex() + 1
        day = self.log_date_layout.itemAt(2).widget().text()
        year = self.log_date_layout.itemAt(3).widget().text()

        if not day or not year:
            self.mess_win = MessageWin('blank date')
            self.mess_win.show()
            return

        # Only allow for days 1 - 31
        if int(day) not in range(1, 32):
            self.mess_win = MessageWin('invalid day')
            self.mess_win.show()
            return

        if len(year) != 4:
            self.mess_win = MessageWin('invalid year')
            self.mess_win.show()
            return

        # If the input date doesn't exist, prompt the user to try again.
        try:
            new_date = datetime.date(int(year), int(month), int(day))
        except ValueError:
            self.mess_win = MessageWin('date does not exist')
            self.mess_win.show()
            return

        current_geo = self.geometry()
        self.edit_logs_win = LogsWin(new_date, current_geo)
        self.edit_logs_win.show()
        self.close()

    def goto_prev_log(self):
        """Use the currently selected date to find the previous available log file path in the 'log files' directory,
        create a datetime object from the pathname, then display the contents of that date's log file. If there are
        no previous files, alert the user.
        """
        all_pathnames = []
        for dirpath, dirnames, filenames in os.walk(LOG_FILES_DIR):
            for filename in filenames:
                current_file_path = os.path.join(dirpath, filename)
                all_pathnames.append(current_file_path)

        # If the file corresponding to the currently selected date doesn't exist, use the position that the file
        # would have in the directory to find the previous available file that exists.
        if not os.path.exists(self.log_file_path):
            bisect.insort(all_pathnames, self.log_file_path)
        prev_file_index = all_pathnames.index(self.log_file_path) - 1
        if prev_file_index == -1:
            self.mess_win = MessageWin('no previous file')
            self.mess_win.show()
            return

        # Extract date information from the log file's path name to create a date object.
        prev_file_path = all_pathnames[prev_file_index]
        prev_file_info = prev_file_path.split('\\')
        year = int(prev_file_info[-3])
        # Convert month into an integer, ex: 01 becomes 1.
        month = int(prev_file_info[-2][0:2])
        day = int(prev_file_info[-1][0:2])
        prev_date = datetime.date(year, month, day)

        current_geo = self.geometry()
        self.next_log_win = LogsWin(prev_date, current_geo)
        self.next_log_win.show()
        self.close()

    def goto_next_log(self):
        """Use the currently selected date to find the next available log file path in the 'log files' directory,
        create a datetime object from the pathname, then display the contents of that date's log file. If there are
        no more files, alert the user.
        """
        all_pathnames = []
        for dirpath, dirnames, filenames in os.walk(LOG_FILES_DIR):
            for filename in filenames:
                current_file_path = os.path.join(dirpath, filename)
                all_pathnames.append(current_file_path)

        # If the file corresponding to the currently selected date doesn't exist, use the position that the file
        # would have in the directory to find the next available file that exists.
        if not os.path.exists(self.log_file_path):
            bisect.insort(all_pathnames, self.log_file_path)
        next_file_index = all_pathnames.index(self.log_file_path) + 1
        try:
            next_file_path = all_pathnames[next_file_index]
        except IndexError:
            self.mess_win = MessageWin('no next file')
            self.mess_win.show()
            return

        # Extract date information from the log file's path name to create a date object.
        next_file_info = next_file_path.split('\\')
        year = int(next_file_info[-3])
        # Convert month into an integer, ex: 01 becomes 1.
        month = int(next_file_info[-2][0:2])
        day = int(next_file_info[-1][0:2])
        next_date = datetime.date(year, month, day)

        current_geo = self.geometry()
        self.next_log_win = LogsWin(next_date, current_geo)
        self.next_log_win.show()
        self.close()

    def remove_entries(self):
        """Get a list of the unchecked entries in the log view table, overwrite the log file with those entries,
        removing the checked entries, then display the updated log to the user. If all entries are selected, ask the
        user for confirmation before deleting the log. Once complete, take the user to the log window to view the
        updated log.
        """
        if not os.path.exists(self.log_file_path):
            self.mess_win = MessageWin('log file not found')
            self.mess_win.show()
            return
        else:
            checked_entry_names = data.get_table_entry_names(self.log_table)[1]
            unchecked_entry_names = data.get_table_entry_names(self.log_table)[2]
            if not checked_entry_names:
                self.mess_win = MessageWin('no selected entries to remove')
                self.mess_win.show()
                return
            elif not unchecked_entry_names:
                # All entries are selected for removal.
                self.confirm_delete_log()
            else:
                entries_to_keep = data.get_entries(self.log_file_path, unchecked_entry_names, match=True)
                with open(self.log_file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(entries_to_keep)

                current_geo = self.geometry()
                self.logs_win = LogsWin(self.date, current_geo)
                self.logs_win.show()
                self.close()

    def select_all(self):
        """Select all entries in the log display widget."""
        if not os.path.exists(self.log_file_path):
            return
        data.select_all_entries(self.log_table)

    def unselect_all(self):
        """Unselect all entries in the log display widget."""
        if not os.path.exists(self.log_file_path):
            return
        data.unselect_all_entries(self.log_table)

    def selection_changed(self):
        """Gather the names of the selected log entries, calculate the entry totals, and display the subtotals as the
        second row of the totals table widget. Update the subtotals each time the user selects or deselects an entry.
        """
        checked_entry_names = data.get_table_entry_names(self.log_table)[1]

        # Leave the table widget row blank if there are no selected entries to tally. There isn't a way to clear the
        # contents of only one row, so an empty string will be placed into each cell instead.
        if not checked_entry_names:
            for i in range(1, self.totals_table.columnCount()):  # Start at index 1 to skip over row title cell.
                blank_item = QTableWidgetItem('')
                self.totals_table.setItem(1, i, blank_item)
            return
        selected_log_entries = data.get_entries(self.log_file_path, checked_entry_names)

        # Remove entry name, serving size options, and number of servings since they are irrelevant to the tally.
        for entry in selected_log_entries:
            del entry[:3]
        totals = data.sum_shared_values(selected_log_entries)

        for i in range(len(totals)):
            if i == 15:
                cost = float(totals[i])
                val = QTableWidgetItem(f'{cost:.2f}')
            else:
                val = QTableWidgetItem(totals[i])
            val.setTextAlignment(Qt.AlignCenter)
            val.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.totals_table.setItem(1, i + 1, val)  # i + 1 to skip over row title cell.

    def confirm_delete_log(self):
        """Display a dialog box that asks user for confirmation to delete the currently selected log."""
        if not os.path.exists(self.log_file_path):
            self.mess_win = MessageWin('log file not found')
            self.mess_win.show()
        else:
            self.dlg = QDialog(self)
            self.dlg.setFixedWidth(350)
            message = QLabel(f"Are you sure you want to delete the log for {self.month_str} {self.day}, {self.year}?"
                             f" This can't be undone.", self)
            message.setWordWrap(True)
            yes_btn = QPushButton("Yes", self)
            yes_btn.setFixedSize(85, 27)
            yes_btn.clicked.connect(self.delete_log)
            no_btn = QPushButton("Nevermind", self)
            no_btn.setFixedSize(85, 27)
            no_btn.clicked.connect(self.close_win)
            main_layout = QVBoxLayout()
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(yes_btn)
            btn_layout.addWidget(no_btn)
            main_layout.addWidget(message)
            main_layout.addLayout(btn_layout)
            main_layout.setSpacing(20)
            self.dlg.setLayout(main_layout)
            self.dlg.setStyleSheet('''
                QDialog {
                background-color: rgb(255, 250, 230);
                border: 2px solid red;
                }
                QWidget {
                    font: 14px;
                }
                QLabel {
                    color: black;
                }
                QPushButton {
                    color: black;
                    background-color: rgb(210, 210, 210);
                    border-width: 2px;
                    border-style: outset;
                    border-radius: 5px;
                    border-color: rgb(70, 70, 70);
                    padding: 3px;
                }
                ''')
            self.dlg.show()

    def delete_log(self):
        """Delete the currently selected log file."""
        os.remove(self.log_file_path)
        # Close the dialog box.
        self.close_win()
        current_geo = self.geometry()
        self.log_win = LogsWin(self.date, current_geo)
        self.log_win.show()
        self.close()

    def edit_entries(self):
        """Pass a list of selected log entry names to EditLogWin instance for editing. If no entries are
        selected, prompt the user to select at least one. It is possible that the user has deleted a food dictionary
        entry from which a log entry is based on. Check the selected entry names against current food dictionary
        entry names, and inform the user if a particular entry no longer exists, and therefore can't be edited.
        """
        checked_entry_names = data.get_table_entry_names(self.log_table)[1]
        if not checked_entry_names:
            self.mess_win = MessageWin('no log entries selected to edit')
            self.mess_win.show()
            return

        if not os.path.exists(FD_PATH):
            self.mess_win = MessageWin('fd file not found (log window edit)')
            self.mess_win.show()
            return

        fd_entry_names = data.get_file_entry_names(FD_PATH)
        for name in checked_entry_names:
            if name not in fd_entry_names:
                self.mess_win = MessageWin('fd entry no longer exists', entry_name=name)
                self.mess_win.show()
                return

        current_geo = self.geometry()
        self.edit_win = EditLogWin(self.date, self.log_file_path, current_geo, checked_entry_names, edit=True)
        self.edit_win.show()
        self.close()

    def add_entries(self):
        """Display the contents of the food dictionary and allow the user to select entries to add to a log. If the
        food dictionary file doesn't exist, tell the user to add entries first.
        """
        if not os.path.exists(FD_PATH):
            self.mess_win = MessageWin('fd file not found (log window)')
            self.mess_win.show()
            return

        current_geo = self.geometry()
        self.edit_win = EditLogWin(self.date, self.log_file_path, current_geo, edit=False)
        self.edit_win.show()
        self.close()

    def close_win(self):
        """Close the 'help' dialog or the 'delete confirmation' dialog."""
        self.dlg.close()

    def goto_fd_win(self):
        """Take the user to the food dictionary window."""
        current_geo = self.geometry()
        self.fd_win = FoodDictWin(current_geo)
        self.fd_win.show()
        self.close()


class EditLogWin(QDialog):
    """Allow the user to add entries or to edit existing entries in a log file."""

    def __init__(self, date, log_file_path, geo, edit_entry_names=None, edit=False):
        """Constructor.

        :param date: A datetime object that determines the log file to be edited.
        :param log_file_path: A string of the log file's pathname.
        :param geo: A QRect() object containing the dimensions and position of the previous window. The current
            window's dimensions and position are set equal to this value.
        :param edit_entry_names: A list of strings. Each item is the name of a log entry to be edited. Default is
            None.
        :param edit: If True, this class allows the user to edit the existing log entries corresponding to the
            names in edit_entry_names. If False, the user selects new entries to add to the log from the food
            dictionary. Default is False.
        """
        super().__init__()
        self.date = date
        self.log_file_path = log_file_path
        self.geo = geo
        self.edit_entry_names = edit_entry_names
        self.edit = edit
        self.init_ui()

    def init_ui(self):
        """Set up UI. Include a description that depends on whether the user is adding or editing log entries.
        Include a table that displays a list of entry options along with input fields for the amount to be added
        or edited. Include a table that displays the tallied information of the selected entries given the
        user-input amounts.
        """
        if self.edit:
            self.setWindowTitle('Edit Log Entries')
        else:
            self.setWindowTitle('Add Entries to Log')
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setGeometry(self.geo)

        # Set up different descriptions depending on whether or not the user is editing existing entries.
        if self.edit:
            description = QLabel("Modify the log entries below, then click 'Update log' to save the changes. The "
                                 "'Totals' table shows the totals for the selected entries only. All entries in the "
                                 "table are saved to the log regardless of whether or not they are checked, so "
                                 "be sure to provide an amount for each entry.", self)
        else:
            description = QLabel("Select which entries to add to the log, providing the decimal amount to add along "
                                 "with its unit of measurement, then click 'Update log'. The 'Totals' table shows "
                                 "the totals for the selected entries only.", self)
        description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        description.setWordWrap(True)

        # Table for the FD entries and the amount input fields.
        self.edit_table = QTableWidget()
        self.edit_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Provide a separate 'totals' table that tallies the info of all entries being edited given the user input.
        # This allows the user to see the magnitude of certain entry contributions without requiring the user to
        # modify the log file just yet. The user can more easily plan a meal this way.
        self.totals_table = QTableWidget()
        self.totals_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.totals_table.setFixedHeight(93)

        self.select_all_btn = QPushButton('Select all entries', self)
        self.select_all_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.select_all_btn.clicked.connect(self.select_all)
        self.unselect_all_btn = QPushButton('Unselect all entries', self)
        self.unselect_all_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.unselect_all_btn.clicked.connect(self.unselect_all)
        self.update_btn = QPushButton('Update log', self)
        self.update_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.update_btn.setDefault(True)

        # Connect the update button to the appropriate slot depending on whether
        # the user is editing or adding entries.
        if self.edit:
            self.update_btn.clicked.connect(self.update_log)
        else:
            self.update_btn.clicked.connect(self.add_to_log)
        self.back_to_log_win_btn = QPushButton('Cancel', self)
        self.back_to_log_win_btn.setFixedSize(85, 27)
        self.back_to_log_win_btn.clicked.connect(self.back_to_log_win)

        spacer1 = QSpacerItem(300, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
        spacer2 = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.main_layout = QVBoxLayout()
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.back_to_log_win_btn)
        self.btn_layout.addWidget(self.select_all_btn)
        self.btn_layout.addWidget(self.unselect_all_btn)
        self.btn_layout.addWidget(self.update_btn)

        edit_layout = QHBoxLayout()
        edit_layout.addItem(spacer1)
        edit_layout.addWidget(self.edit_table)
        edit_layout.addItem(spacer1)

        self.main_layout.addWidget(description)
        self.main_layout.addLayout(edit_layout)
        self.main_layout.addItem(spacer2)
        self.main_layout.addWidget(self.totals_table)
        self.main_layout.addItem(spacer2)
        self.main_layout.addLayout(self.btn_layout)
        self.setLayout(self.main_layout)

        self.edit_table.setColumnCount(3)
        self.edit_table.setHorizontalHeaderLabels(['Name', 'Amount', 'Weight/Volume'])
        h_header = self.edit_table.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        h_header.setSectionResizeMode(0, QHeaderView.Stretch)

        # If the user is editing entries, the table entries will correspond to
        # self.edit_entry_names. Otherwise, they will be all entries in the FD.
        if self.edit:
            table_entry_names = self.edit_entry_names
            old_entries = data.get_entries(self.log_file_path, self.edit_entry_names, match=True)
            old_amounts = []  # [[amount1, unit1], [amount2, unit2], ...]
            for entry in old_entries:
                amount = ast.literal_eval(entry[1])  # [amount, unit]
                old_amounts.append(amount)

            # Get the serving size options of the entries to be edited from the FD.
            # The order of the entries matches the order of appearance of the edit entry names.
            old_entry_fd_matches = data.get_entries(FD_PATH, self.edit_entry_names, match=True)

            # List of dictionaries containing the serving size options for each entry to edit.
            self.serv_options = []
            for entry in old_entry_fd_matches:
                serv_dict = ast.literal_eval(entry[1])
                self.serv_options.append(serv_dict)
        else:
            table_entry_names = data.get_file_entry_names(FD_PATH)
            fd_entries = data.get_entries(FD_PATH, return_all=True)

            # List of dictionaries containing serving size options for each FD entry.
            self.serv_options = []
            for entry in fd_entries:
                serv_dict = ast.literal_eval(entry[1])
                self.serv_options.append(serv_dict)
        self.edit_table.setRowCount(len(table_entry_names))

        # Set up the log edit table.
        for i in range(self.edit_table.rowCount()):
            self.edit_table.setRowHeight(i, 40)

            # Add the entry name with a checkbox.
            # Checked entries will be tallied in the totals table.
            name_checkbox = QTableWidgetItem(table_entry_names[i])
            name_checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            name_checkbox.setCheckState(Qt.Unchecked)
            self.edit_table.setItem(i, 0, name_checkbox)

            # Each amount input widget will need to be added to a layout, which will be
            # set on a QWidget(). This is done to vertically center the widget within the cell.
            amount_textbox = QLineEdit(self)

            # Each amount field only accepts positive floats.
            validator = QDoubleValidator()
            validator.setNotation(QDoubleValidator.StandardNotation)
            validator.setBottom(0)
            amount_textbox.setValidator(validator)
            amount_textbox.setFixedSize(50, 27)
            # Center-align cursor within the amount field.
            amount_textbox.setAlignment(Qt.AlignCenter)

            amount_w = QWidget()
            amount_layout = QHBoxLayout()
            amount_layout.addWidget(amount_textbox)
            amount_w.setLayout(amount_layout)
            self.edit_table.setCellWidget(i, 1, amount_w)

            # QComboBox for the possible units of measurement.
            combobox = QComboBox()
            combobox.setFixedSize(90, 27)

            unit_options = []
            for key in self.serv_options[i].keys():
                unit_options.append(key)
            combobox.addItems(['Serving(s)', *unit_options])

            unit_w = QWidget()
            unit_layout = QHBoxLayout()
            unit_layout.addWidget(combobox)
            unit_w.setLayout(unit_layout)
            self.edit_table.setCellWidget(i, 2, unit_w)

            # If the user is editing entries, place the original input into the fields by default.
            if self.edit:
                amount_textbox.setText(old_amounts[i][0])
                combobox.setCurrentText(old_amounts[i][1])

            # If the inputs are modified, re-tally the info
            amount_textbox.textEdited.connect(self.input_changed)
            combobox.currentIndexChanged.connect(self.input_changed)
        self.col_labels = ['Calories', 'Total\nFat\n(g)', 'Sat.\nFat\n(g)', 'Trans\nFat\n(g)',
                           'Poly.\nFat\n(g)', 'Mono.\nFat\n(g)', 'Chol.\n(mg)', 'Sodium\n(mg)', 'Total\nCarbs\n(g)',
                           'Total\nFiber\n(g)', 'Sol.\nFiber\n(g)', 'Insol.\nFiber\n(g)',
                           'Total\nSugars\n(g)', 'Added\nSugars\n(g)', 'Protein\n(g)', 'Cost\n($)']
        self.totals_table.setRowCount(1)
        # +1 accounts for the 'Totals' label in first column.
        self.totals_table.setColumnCount(len(self.col_labels) + 1)
        self.totals_table.setRowHeight(0, 50)
        self.totals_table.setRowHeight(1, 50)
        totals_item = QTableWidgetItem('Selected entries')
        totals_item.setTextAlignment(Qt.AlignCenter)
        totals_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.totals_table.setItem(0, 0, totals_item)

        # Leave the totals table blank and non-interactive until the user selects any entries.
        for i in range(1, self.totals_table.columnCount()):
            blank_item = QTableWidgetItem('')
            blank_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.totals_table.setItem(0, i, blank_item)

        totals_h_header = self.totals_table.horizontalHeader()
        self.totals_table.setHorizontalHeaderLabels(['Totals', *self.col_labels])
        totals_h_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        totals_h_header.setSectionResizeMode(0, QHeaderView.Stretch)

        totals_v_header = self.totals_table.verticalHeader()
        # The default numbered headers are unnecessary.
        totals_v_header.setVisible(False)
        totals_v_header.setDefaultSectionSize(30)
        self.setStyleSheet('''
            QDialog {
                background-color: rgb(0, 0, 30);
            }
            QWidget {
                font: 14px;
            }
            QLabel {
                color: white;
            }
            QHeaderView {
                background-color: rgb(255, 90, 10);
            }
            QHeaderView::section {
                font: 14px;
                font-weight: 500;
                color: black;
                background-color: rgb(255, 90, 10);
                border-top: 0px solid black;
                border-bottom: 1px solid black;
                border-left: 0px solid black;
                border-right: 1px solid black;
            }
            QHeaderView::section::checked {
                background-color: rgb(60, 180, 60);
            }
            QTableView {
                background-color: rgb(255, 230, 200);
                selection-background-color: rgb(60, 180, 60);
                selection-color: black;
                gridline-color: black;
                font: 14px;
                font-weight: 500;
            }
            QTableCornerButton::section {
                background-color: rgb(255, 90, 10);
                border: 1px solid rgb(255, 90, 10);
            }
            QPushButton {
                font: 14px;
                color: rgb(255, 255, 255);
                background-color: rgb(70, 70, 70);
                border-width: 2px;
                border-style: outset;
                border-radius: 5px;
                border-color: gray;
                padding: 3px;
            }
            QLineEdit {
                border: 1px solid gray;
                border-radius: 5px;
            }
            QComboBox {
                border: 1px solid gray;
                border-radius: 5px;
            }
            ''')
        # Re-tally the totals any time the user selects or unselects an entry.
        self.edit_table.itemChanged.connect(self.input_changed)

    def select_all(self):
        """Select all entries in the table of entries to be edited."""
        data.select_all_entries(self.edit_table)

    def unselect_all(self):
        """Unselect all entries in the table of entries to be edited."""
        data.unselect_all_entries(self.edit_table)

    def input_changed(self):
        """Get the entry information of the checked entries and use their corresponding amount inputs to tally the
        entry information and display the totals in the totals table. If no entries are selected, leave the totals
        table blank.
        """
        checked_entry_names = data.get_table_entry_names(self.edit_table)[1]
        checked_entry_amounts = data.get_edit_log_amounts(self.edit_table, checked=True)  # [[amount1, unit1], ...]
        if not checked_entry_names:
            for i in range(1, self.totals_table.columnCount()):
                blank_item = QTableWidgetItem('')
                self.totals_table.setItem(0, i, blank_item)
            return

        unmodified_entries = data.get_entries(FD_PATH, checked_entry_names, match=True)
        calculated_entries = data.calculate_entry_info(unmodified_entries, checked_entry_amounts, tally=True)

        # Remove entry name, serving size options, and number of servings since they are irrelevant to the tally.
        for entry in calculated_entries:
            del entry[:3]
        summed_values = data.sum_shared_values(calculated_entries)
        for i in range(len(summed_values)):
            if i == 15:
                cost = float(summed_values[i])
                val = QTableWidgetItem(f'{cost:.2f}')
            else:
                val = QTableWidgetItem(summed_values[i])
            val.setTextAlignment(Qt.AlignCenter)
            val.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.totals_table.setItem(0, i + 1, val)  # i + 1 to skip over row title cell.

    def add_to_log(self):
        """Calculate finalized entry info from the user's input in the entry table and add each entry to a log file.
        If one of the new entry names matches an existing one in the log, tell the user to edit the existing entry
        instead. If the user has provided invalid or insufficient amount input, prompt them to try again. Once
        completed, take the user to the log window to view the updated log.
        """
        new_entry_names = data.get_table_entry_names(self.edit_table)[1]
        if not new_entry_names:
            self.mess_win = MessageWin('no log entries selected to add')
            self.mess_win.show()
            return

        if os.path.exists(self.log_file_path):
            current_log_entry_names = data.get_file_entry_names(self.log_file_path)
            for name in new_entry_names:
                if name in current_log_entry_names:
                    self.mess_win = MessageWin('duplicate log entry', entry_name=name)
                    self.mess_win.show()
                    return

        new_entries = data.get_entries(FD_PATH, new_entry_names, match=True)
        new_entry_amounts = data.get_edit_log_amounts(self.edit_table, checked=True)  # [[amount1, unit1], ...]
        calculated_entries = data.calculate_entry_info(new_entries, new_entry_amounts, tally=False)
        if calculated_entries == 'no amount given (log add)':
            self.mess_win = MessageWin('no amount given (log add)')
            self.mess_win.show()
            return

        if calculated_entries == 'invalid amount':
            self.mess_win = MessageWin('invalid amount')
            self.mess_win.show()
            return

        if not os.path.exists(os.path.dirname(self.log_file_path)):
            os.makedirs(os.path.dirname(self.log_file_path))

        with open(self.log_file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            for entry in calculated_entries:
                writer.writerow(entry)

        current_geo = self.geometry()
        self.log_win = LogsWin(self.date, current_geo)
        self.log_win.show()
        self.close()

    def update_log(self):
        """Calculate finalized entry info from the user's input in the entry edit table and replaces each matching
        old entry in a log file with the updated entry. If the user has provided insufficient or invalid amount
        input, prompt them to try again. Once completed, take the user to the log window to view the updated log.
        """
        edit_entry_names = data.get_table_entry_names(self.edit_table)[0]
        entries_to_write = data.get_entries(self.log_file_path, edit_entry_names, match=False)

        unmodified_entries = data.get_entries(FD_PATH, edit_entry_names, match=True)
        edit_entry_amounts = data.get_edit_log_amounts(self.edit_table, checked=False)  # [[amount1, unit1], ...]

        calculated_entries = data.calculate_entry_info(unmodified_entries, edit_entry_amounts, edit=True)
        if calculated_entries == 'no amount given (log edit)':
            self.mess_win = MessageWin('no amount given (log edit)')
            self.mess_win.show()
            return

        if calculated_entries == 'invalid amount':
            self.mess_win = MessageWin('invalid amount')
            self.mess_win.show()
            return

        for entry in calculated_entries:
            entries_to_write.append(entry)

        with open(self.log_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(entries_to_write)

        current_geo = self.geometry()
        self.log_win = LogsWin(self.date, current_geo)
        self.log_win.show()
        self.close()

    def back_to_log_win(self):
        """Take the user back to the log window."""
        current_geo = self.geometry()
        self.log_win = LogsWin(self.date, current_geo)
        self.log_win.show()
        self.close()


class FoodDictWin(QDialog):
    """Allow the user to view or edit the food dictionary (FD), which is a csv file that stores information about
    user-input food items. The user pulls information from the food dictionary when adding an entry to a log file.

    For example, one row in the food dictionary file may look like:

    spaghetti,"{'g': '56', 'oz': '2'}",180,1.5,0,0,0,0,0,0,40,6,,,2,0,7,"[1.15, 8]",0.14

    The above entry represents spaghetti. The second value is a dictionary of the serving sizes, 56 grams or 2
    ounces. The third position is the number of  calories (180), followed by total fat, saturated fat,
    trans fat, polyunsaturated fat, monounsaturated fat, cholesterol, sodium, total carbohydrate,
    total dietary fiber, soluble fiber, insoluble fiber, total sugars, added sugars, and protein. The
    second to last value is a list, in which the first item is the total cost of the container, followed by the
    total number of servings per container. In this example, one box of spaghetti costs $1.15, and there are 8
    servings per box. The information in this list is used to calculate the last value, which is the cost per
    serving of the entry (1.15 / 8 = 14 cents). The 'missing' values are those that were ignored by the
    user when adding the entry to the food dictionary, since the user is not required to give all info.
    """

    def __init__(self, geo=None):
        """Constructor.

        :param geo: A QRect() object containing the dimensions and position of the previous window. The current
            window's dimensions and position are set equal to this value. Default is None.
        """
        super().__init__()
        self.geo = geo
        self.init_ui()

    def init_ui(self):
        """Setup UI. Include a table that displays the contents of the food dictionary. Include buttons to allow the
        user to add, edit, or remove entries from the food dictionary.
        """
        self.setWindowTitle('View or Edit the Food Dictionary')
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # Center the window unless a previous window's geometry was passed to the instance.
        if not self.geo:
            self.w, self.h = data.get_win_size()
            self.resize(self.w, self.h)
            self.center()
        else:
            self.setGeometry(self.geo)
        description = QLabel("Below is the food dictionary, where information about different food items is kept and "
                             "used when managing daily logs. Click the 'Add an entry' button to add a food "
                             "item by providing its name, nutritional content, and (optionally) cost. You can select "
                             "any of the entries and click 'Delete selected entries' to delete them from the food "
                             "dictionary. You can also select an entry and click 'Edit selected entry' to change any "
                             "information.", self)
        description.setObjectName('description')
        description.setWordWrap(True)
        description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Table widget that displays the details of the FD.
        self.fd_table = QTableWidget(self)
        self.fd_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add buttons to edit the FD or allow navigation.
        self.select_all_btn = QPushButton('Select all entries', self)
        self.select_all_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.select_all_btn.clicked.connect(self.select_all)
        self.unselect_all_btn = QPushButton('Unselect all entries', self)
        self.unselect_all_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.unselect_all_btn.clicked.connect(self.unselect_all)
        self.delete_fd_btn = QPushButton('Delete all entries', self)
        self.delete_fd_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.delete_fd_btn.clicked.connect(self.confirm_delete_fd)
        self.add_entry_btn = QPushButton('Add an entry', self)
        self.add_entry_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # Press Enter to press the 'Add an entry' button
        self.add_entry_btn.setDefault(True)
        self.add_entry_btn.clicked.connect(self.add_entries_to_fd)
        self.delete_selected_entries_btn = QPushButton('Delete selected entries', self)
        self.delete_selected_entries_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.delete_selected_entries_btn.clicked.connect(self.remove_entries_confirmation)
        self.edit_entry_btn = QPushButton('Edit selected entry', self)
        self.edit_entry_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit_entry_btn.clicked.connect(self.edit_entry)
        self.goto_log_win_btn = QPushButton('Go to logs', self)
        self.goto_log_win_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.goto_log_win_btn.clicked.connect(self.goto_log_win)

        self.main_layout = QVBoxLayout()
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.select_all_btn)
        self.btn_layout.addWidget(self.unselect_all_btn)
        self.btn_layout.addWidget(self.delete_fd_btn)
        self.btn_layout.addWidget(self.delete_selected_entries_btn)
        self.btn_layout.addWidget(self.edit_entry_btn)
        self.btn_layout.addWidget(self.add_entry_btn)

        self.main_layout.addWidget(self.goto_log_win_btn)
        self.main_layout.addWidget(description)
        self.main_layout.addWidget(self.fd_table)
        self.main_layout.addLayout(self.btn_layout)
        self.setLayout(self.main_layout)
        self.main_layout.setSpacing(15)

        if not os.path.exists(FD_PATH):
            # The FD doesn't exist, alert the user.
            self.fd_table.setRowCount(1)
            self.fd_table.setColumnCount(1)
            no_fd_item = QTableWidgetItem("There are currently no entries in the food dictionary. Please click the "
                                          "'Add an entry' button to get started.")
            self.fd_table.setItem(0, 0, no_fd_item)
            no_fd_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            fd_h_header = self.fd_table.horizontalHeader()
            fd_h_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            fd_h_header.setVisible(False)

            fd_v_header = self.fd_table.verticalHeader()
            fd_v_header.setVisible(False)
        else:
            # Display the FD's contents.
            fd_entries = data.get_entries(FD_PATH, return_all=True)

            col_labels = ['Name', 'Serving\nSize', 'Calories', 'Total\nFat\n(g)', 'Sat.\nFat\n(g)', 'Trans\nFat\n(g)',
                          'Poly.\nFat\n(g)', 'Mono.\nFat\n(g)', 'Chol.\n(mg)', 'Sodium\n(mg)', 'Total\nCarbs\n(g)',
                          'Total\nFiber\n(g)', 'Sol.\nFiber\n(g)', 'Insol.\nFiber\n(g)',
                          'Total\nSugars\n(g)', 'Added\nSugars\n(g)', 'Protein\n(g)', 'Cost\n($)']
            self.fd_table.setRowCount(len(fd_entries))
            self.fd_table.setColumnCount(len(col_labels))

            for entry_num in range(len(fd_entries)):
                self.fd_table.setRowHeight(entry_num, 50)
                entry = fd_entries[entry_num]
                name_checkbox = QTableWidgetItem(entry[0])
                name_checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                name_checkbox.setCheckState(Qt.Unchecked)
                self.fd_table.setItem(entry_num, 0, name_checkbox)

                serv_options_dict = ast.literal_eval(entry[1])  # {amount1: unit1, amount2: unit2, ...}
                serv_options_list = []  # [[amount1, unit1], [amount2, unit2], ...]
                for unit in serv_options_dict.keys():
                    amount = serv_options_dict[unit]
                    serv_options_list.append([amount, unit])
                serv_label = QTableWidgetItem(f'{serv_options_list[0][0]} {serv_options_list[0][1]}')
                # Disallow editing of the values.
                serv_label.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                # Go through the rest of the serving sizes, if any, and append their values to serv_label.
                for i in range(1, len(serv_options_list)):
                    serv_label.setText(serv_label.text() + f'\n{serv_options_list[i][0]} {serv_options_list[i][1]}')
                serv_label.setTextAlignment(Qt.AlignCenter)
                self.fd_table.setItem(entry_num, 1, serv_label)

                for i in range(2, len(entry[:-2])):  # Up to index -2 since cost will be handled separately.
                    val = QTableWidgetItem(entry[i])
                    val.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    val.setTextAlignment(Qt.AlignCenter)
                    self.fd_table.setItem(entry_num, i, val)

                cost_info = entry[17]
                if not cost_info:
                    cost_item = QTableWidgetItem("")
                else:
                    total_cost = ast.literal_eval(cost_info)[0]
                    serv_per_container = ast.literal_eval(cost_info)[1]
                    unit_cost = round(float(entry[18]), 2)
                    cost_item = QTableWidgetItem(f"{serv_per_container} serving(s): ${total_cost}\n"
                                                 f"1 serving: ${unit_cost:.2f} ")
                cost_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.fd_table.setItem(entry_num, 17, cost_item)

            fd_h_header = self.fd_table.horizontalHeader()
            self.fd_table.setHorizontalHeaderLabels(col_labels)
            fd_h_header.setSectionResizeMode(QHeaderView.ResizeToContents)
            fd_h_header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.setStyleSheet('''
            QDialog {
                background-color: rgb(0, 0, 30);
            }
            QWidget {
                font: 14px;
            }
            QLabel {
                color: white;
            }
            QHeaderView {
                background-color: rgb(60, 170, 60);

            }
            QHeaderView::section {
                font: 14px;
                font-weight: 500;
                color: black;
                background-color: rgb(60, 170, 60);
                border-top: 0px solid black;
                border-bottom: 1px solid black;
                border-left: 0px solid black;
                border-right: 1px solid black;
            }
            QHeaderView::section::checked {
                background-color: rgb(60, 60, 180);
            }
            QTableView {
                background-color: rgb(200, 200, 255);
                selection-background-color: rgb(60, 60, 180);
                selection-color: white;
                gridline-color: black;
                font: 14px;
                font-weight: 500;
            }
            QTableCornerButton::section {
                background-color: rgb(60, 170, 60);
                border: 1px solid rgb(60, 170, 60);
            }
            QPushButton {
                color: rgb(255, 255, 255);
                background-color: rgb(70, 70, 70);
                border-width: 2px;
                border-style: outset;
                border-radius: 5px;
                border-color: gray;
                padding: 3px;
            }
            ''')

    def center(self):
        """Move the window to the center of the screen by moving the window geometry's center point to the center
        of the desktop screen.
        """
        geo = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center_point)
        self.move(geo.topLeft())

    def goto_log_win(self):
        """Take the user to the log window."""
        current_geo = self.geometry()
        self.log_win = LogsWin(datetime.date.today(), current_geo)
        self.log_win.show()
        self.close()

    def add_entries_to_fd(self):
        """Allow the user to add an entry to the food dictionary file."""
        self.add_to_fd_win = EditFoodDictWin()
        self.add_to_fd_win.show()
        self.close()

    def remove_entries_confirmation(self):
        """Display a dialog box that asks the user for confirmation to delete the selected food dictionary entries."""
        if not os.path.exists(FD_PATH):
            self.mess_win = MessageWin('fd file not found (fd window)')
            self.mess_win.show()
            return
        else:
            checked_entry_names = data.get_table_entry_names(self.fd_table)[1]
            unchecked_entry_names = data.get_table_entry_names(self.fd_table)[2]
            if not checked_entry_names:
                self.mess_win = MessageWin('no selected entries to remove')
                self.mess_win.show()
                return
            elif not unchecked_entry_names:
                # All entries are selected for removal.
                self.confirm_delete_fd()
            else:
                self.dlg = QDialog(self)
                self.dlg.setFixedWidth(350)
                message = QLabel("Are you sure you want to delete the selected entries from the food dictionary? "
                                 "This can't be undone.", self)
                message.setWordWrap(True)
                yes_btn = QPushButton("Yes", self)
                yes_btn.setFixedSize(85, 27)
                yes_btn.clicked.connect(self.remove_entries_from_fd)
                no_btn = QPushButton("Nevermind", self)
                no_btn.setFixedSize(85, 27)
                no_btn.clicked.connect(self.close_win)
                main_layout = QVBoxLayout()
                btn_layout = QHBoxLayout()
                btn_layout.addWidget(yes_btn)
                btn_layout.addWidget(no_btn)
                main_layout.addWidget(message)
                main_layout.addLayout(btn_layout)
                main_layout.setSpacing(20)
                self.dlg.setLayout(main_layout)
                self.dlg.setStyleSheet('''
                QDialog {
                    background-color: rgb(255, 250, 230);
                    border: 2px solid red;
                }
                QWidget {
                    font: 14px;
                }
                QLabel {
                    color: black;
                }
                QPushButton {
                    color: black;
                    background-color: rgb(210, 210, 210);
                    border-width: 2px;
                    border-style: outset;
                    border-radius: 5px;
                    border-color: rgb(70, 70, 70);
                    padding: 3px;
                }
                    ''')
                self.dlg.show()

    def remove_entries_from_fd(self):
        """Get a list of the unchecked entries in the food dictionary table, then overwrite the food dictionary file
        with those entries, removing the checked entries. If there are no selected entries, prompt the user to select
        at least one.
        """
        if not os.path.exists(FD_PATH):
            self.mess_win = MessageWin('fd file not found (fd window)')
            self.mess_win.show()
            return

        unchecked_entry_names = data.get_table_entry_names(self.fd_table)[2]
        entries_to_keep = data.get_entries(FD_PATH, unchecked_entry_names, match=True)
        with open(FD_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(entries_to_keep)

        self.close_win()
        current_geo = self.geometry()
        self.logs_win = FoodDictWin(current_geo)
        self.logs_win.show()
        self.close()

    def select_all(self):
        """Select all entries in the food dictionary table widget."""
        if not os.path.exists(FD_PATH):
            return
        data.select_all_entries(self.fd_table)

    def unselect_all(self):
        """Unselect all entries in the food dictionary table widget."""
        if not os.path.exists(FD_PATH):
            return
        data.unselect_all_entries(self.fd_table)

    def edit_entry(self):
        """Get the name of the selected entry in the food dictionary table, then pass it to EditFoodDictWin to be
        edited. If multiple entries or none are selected, prompt the user to select only one and try again.
        """
        if not os.path.exists(FD_PATH):
            self.mess_win = MessageWin('fd file not found (fd window)')
            self.mess_win.show()
            return

        checked_entry_names = data.get_table_entry_names(self.fd_table)[1]
        if not checked_entry_names or len(checked_entry_names) > 1:
            self.mess_win = MessageWin('no single fd entry selected')
            self.mess_win.show()
            return

        self.add_to_fd_win = EditFoodDictWin(checked_entry_names[0])
        self.add_to_fd_win.show()
        self.close()

    def confirm_delete_fd(self):
        """Display a dialog box that asks user for confirmation to delete the food dictionary file."""
        if not os.path.exists(FD_PATH):
            self.mess_win = MessageWin('fd file not found (fd window)')
            self.mess_win.show()
        else:
            self.dlg = QDialog(self)
            self.dlg.setFixedWidth(350)
            message = QLabel("Are you sure you want to delete all entries from the food dictionary? This can't be "
                             "undone.", self)
            message.setWordWrap(True)
            yes_btn = QPushButton("Yes", self)
            yes_btn.setFixedSize(85, 27)
            yes_btn.clicked.connect(self.delete_fd)
            no_btn = QPushButton("Nevermind", self)
            no_btn.setFixedSize(85, 27)
            no_btn.clicked.connect(self.close_win)
            main_layout = QVBoxLayout()
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(yes_btn)
            btn_layout.addWidget(no_btn)
            main_layout.addWidget(message)
            main_layout.addLayout(btn_layout)
            main_layout.setSpacing(20)
            self.dlg.setLayout(main_layout)
            self.dlg.setStyleSheet('''
                QDialog {
                background-color: rgb(255, 250, 230);
                border: 2px solid red;
                }
                QWidget {
                    font: 14px;
                }
                QLabel {
                    color: black;
                }
                QPushButton {
                    color: black;
                    background-color: rgb(210, 210, 210);
                    border-width: 2px;
                    border-style: outset;
                    border-radius: 5px;
                    border-color: rgb(70, 70, 70);
                    padding: 3px;
                }
                ''')
            self.dlg.show()

    def delete_fd(self):
        """Delete the food dictionary file and take the user to the food dictionary view screen."""
        os.remove(FD_PATH)
        self.close_win()
        current_geo = self.geometry()
        self.fd_win = FoodDictWin(current_geo)
        self.fd_win.show()
        self.close()

    def close_win(self):
        """Close the dialog box that asks for confirmation to delete the food dictionary file."""
        self.dlg.close()


class EditFoodDictWin(QDialog):
    """Allow the user to add or edit entries in the food dictionary. If an entry name is passed, then the information
    originally provided by the user is placed into the proper fields, allowing the user to edit the already existing
    entry.
    """

    def __init__(self, edit_entry_name=None):
        """Constructor

        :param edit_entry_name: string name of the food dictionary entry to be edited by the user. Default is None.
        """
        super().__init__()
        self.w = 700
        self.h = 600
        self.edit_entry_name = edit_entry_name
        self.init_ui()

    def init_ui(self):
        """Set up the UI. Include two QFormLayouts for the user to input entry information, such as name,
        nutrition, and cost.
        """
        if self.edit_entry_name:
            self.setWindowTitle('Edit an Entry in the Food Dictionary')
        else:
            self.setWindowTitle('Add an Entry to the Food Dictionary')
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.resize(self.w, self.h)

        main_layout = QVBoxLayout()
        self.info1_layout = QFormLayout()
        self.info2_layout = QFormLayout()
        exp = QLabel("Please enter the information below, then click the 'Add entry' button to add the entry "
                     "to the food dictionary.\n\n"
                     "Many food labels provide multiple ways of measuring a serving. You may enter up to three, "
                     "but only one is required. Some serving sizes may be measured by item instead of weight "
                     "or volume. For example, one apple is one serving. As another example, two small candy "
                     "bars may be one serving. For these, you can use the 'item(s)' selection from the "
                     "drop-down menu.\n\n"
                     "For the cost, enter the dollar amount in the first field, then the total number of servings "
                     "per container in the second field. For example, it may cost $3.00 for 8 servings of cereal. "
                     "A unit cost is automatically calculated and applied to your log entries.\n\n"
                     "Feel free to leave some of the fields blank. The blank fields will be ignored when managing "
                     "logs, but you can edit them at any time.", self)
        exp.setObjectName('exp')
        exp.setWordWrap(True)
        exp.setAlignment(Qt.AlignLeft)
        exp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add input fields and their labels to the form layout.
        name_field = QLineEdit(self)
        name_field.setFixedSize(200, 27)
        self.info1_layout.addRow(self.tr('Name'), name_field)

        # Each input field (except name) will only accept positive floats.
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)
        validator.setBottom(0)

        units = ['item(s)', 'oz', 'lbs', 'g', 'mg', 'kg', 'cup', 'pint', 'quart', 'gallon', 'mL', 'L', 'tsp', 'tbsp']
        # Each of the other labels (except calories) has a corresponding QHBoxLayout with input fields.
        for label in ['Serving Size', '', '']:
            input_field = QLineEdit(self)
            input_field.setFixedSize(60, 27)
            input_field.setValidator(validator)
            combo_box = QComboBox(self)
            combo_box.setFixedSize(70, 27)
            combo_box.addItems(units)
            h_layout = QHBoxLayout()
            h_layout.addWidget(input_field)
            h_layout.addWidget(combo_box)
            self.info1_layout.addRow(self.tr(label), h_layout)

        cal_field = QLineEdit(self)
        cal_field.setFixedSize(60, 27)
        cal_field.setValidator(validator)
        self.info1_layout.addRow(self.tr('Calories'), cal_field)

        for label in ['Total Fat', 'Saturated Fat', 'Trans Fat', 'Polyunsaturated Fat', 'Monounsaturated Fat']:
            input_field = QLineEdit(self)
            input_field.setFixedSize(60, 27)
            input_field.setValidator(validator)
            unit_label = QLabel('g', self)
            h_layout = QHBoxLayout()
            h_layout.addWidget(input_field)
            h_layout.addWidget(unit_label)
            self.info1_layout.addRow(self.tr(label), h_layout)

        for label in ['Cholesterol', 'Sodium', 'Total Carbohydrate', 'Dietary Fiber', 'Soluble Fiber',
                      'Insoluble Fiber', 'Total Sugars', 'Added Sugars', 'Protein']:
            input_field = QLineEdit(self)
            input_field.setFixedSize(60, 27)
            input_field.setValidator(validator)
            if label in ['Cholesterol', 'Sodium']:
                unit_label = QLabel('mg', self)
            else:
                unit_label = QLabel('g', self)
            h_layout = QHBoxLayout()
            h_layout.addWidget(input_field)
            h_layout.addWidget(unit_label)
            self.info2_layout.addRow(self.tr(label), h_layout)

        # Add input fields for the cost.
        cost_field = QLineEdit(self)
        cost_field.setFixedSize(60, 27)
        cost_field.setValidator(validator)
        cost_layout = QHBoxLayout()
        dollar_label = QLabel('$', self)
        dollar_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for_label = QLabel('for', self)
        for_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        num_of_servings_field = QLineEdit(self)
        num_of_servings_field.setFixedSize(60, 27)
        num_of_servings_field.setValidator(validator)
        servings_label = QLabel('servings', self)

        cost_layout.addWidget(dollar_label)
        cost_layout.addWidget(cost_field)
        cost_layout.addWidget(for_label)
        cost_layout.addWidget(num_of_servings_field)
        cost_layout.addWidget(servings_label)
        self.info2_layout.addRow(self.tr('Cost'), cost_layout)

        self.info1_layout.setLabelAlignment(Qt.AlignRight)
        self.info2_layout.setLabelAlignment(Qt.AlignRight)

        info1_w = QWidget()
        info2_w = QWidget()
        info12_w = QWidget()

        info1_w.setLayout(self.info1_layout)
        info2_w.setLayout(self.info2_layout)
        info12_layout = QHBoxLayout()
        info12_layout.addWidget(info1_w)
        info12_layout.addWidget(info2_w)
        info12_w.setLayout(info12_layout)
        info12_layout.setSpacing(50)

        back_to_fd_win_btn = QPushButton('Cancel', self)
        back_to_fd_win_btn.setFixedSize(100, 27)
        back_to_fd_win_btn.clicked.connect(self.goto_fd_win)
        done_btn = QPushButton(self)
        done_btn.setFixedSize(100, 27)
        done_btn.clicked.connect(self.add_or_edit_entry)
        if self.edit_entry_name:
            done_btn.setText('Update entry')
        else:
            done_btn.setText('Add entry')

        # Allow user to press Enter key to press the done button.
        done_btn.setDefault(True)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(back_to_fd_win_btn)
        btn_layout.addWidget(done_btn)
        btn_w = QWidget()
        btn_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_w.setLayout(btn_layout)

        main_layout.addWidget(exp)
        main_layout.addWidget(info12_w)
        main_layout.addWidget(btn_w)
        self.setLayout(main_layout)

        # If there is a string assigned to self.edit_entry_name, place that entry's current info into the input fields
        # so that the user knows what was originally input. Otherwise, all fields are left blank for the new entry.
        if self.edit_entry_name:
            with open(FD_PATH) as f:
                reader = csv.reader(f)
                for entry in reader:
                    if entry[0] == self.edit_entry_name:
                        prev_data = entry
                        break
            name_w = self.info1_layout.itemAt(1).widget()
            name_w.setText(self.edit_entry_name)
            name_w.setCursorPosition(0)

            serv_size_options = ast.literal_eval(prev_data[1])  # {amount1: unit1, amount2: unit2, ...}
            # Index of the items of the QFormLayout, corresponding to each QHBoxLayout with a QLineEdit.
            item_index = 3

            for key in serv_size_options.keys():
                self.info1_layout.itemAt(item_index).itemAt(0).widget().setText(serv_size_options[key])
                self.info1_layout.itemAt(item_index).itemAt(1).widget().setCurrentText(key)
                item_index += 1
            self.info1_layout.itemAt(7).widget().setText(prev_data[2])

            # Item index corresponding to fat content in first FormLayout.
            item_index = 9
            for data_index in range(3, 8):
                # Ranges from fat content to monounsaturated fat content.
                self.info1_layout.itemAt(item_index).itemAt(0).widget().setText(prev_data[data_index])
                item_index += 2

            # Item index corresponding to cholesterol input field in second FormLayout.
            item_index = 1
            for data_index in range(8, 17):
                # Ranges from cholesterol to protein.
                self.info2_layout.itemAt(item_index).itemAt(0).widget().setText(prev_data[data_index])
                item_index += 2

            total_cost_str = prev_data[17]
            if not total_cost_str:
                pass
            else:
                cost_list = ast.literal_eval(total_cost_str)  # [cost, serv_per_container]
                self.info2_layout.itemAt(19).itemAt(1).widget().setText(str(cost_list[0]))
                self.info2_layout.itemAt(19).itemAt(3).widget().setText(str(cost_list[1]))
        self.setStyleSheet('''
            QDialog {
                background-color: rgb(255, 230, 140);
                border: 2px solid rgb(255, 90, 10);
            }
            QWidget {
                font: 14px;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                color: black;
                background-color: rgb(210, 210, 210);
                border-width: 2px;
                border-style: outset;
                border-radius: 5px;
                border-color: rgb(70, 70, 70);
                padding: 3px;
            }
            QLineEdit {
                border: 1px solid gray;
                border-radius: 5px;
            }
            QComboBox {
                border: 1px solid gray;
                border-radius: 5px;
            }
            ''')

    def goto_fd_win(self):
        """Take the user to the food dictionary window."""
        self.fd_win = FoodDictWin()
        self.fd_win.show()
        self.close()

    def add_or_edit_entry(self):
        """Place all info provided by the user into a list and append it to the food dictionary csv file. If the
        user is editing an existing entry, remove the original entry. If the user has provided invalid or
        insufficient information, display an error message. Once complete, take the user back to the food dictionary
        window to view the updated information.
        """
        entry = []
        entry_name = self.info1_layout.itemAt(1).widget().text()
        if not entry_name:
            self.err_win = MessageWin('no name')
            self.err_win.show()
            return

        # Duplicate entry names are not allowed.
        if os.path.exists(FD_PATH):
            with open(FD_PATH) as f:
                reader = list(csv.reader(f))
            for line in reader:
                if entry_name == line[0]:
                    if self.edit_entry_name and entry_name == self.edit_entry_name:
                        # The user is editing an entry and didn't alter the entry name.
                        pass
                    else:
                        # Either the user is editing an entry, but the name was changed and matches
                        # another existing entry, or a completely new entry name matches an existing entry.
                        self.err_win = MessageWin('duplicate fd entry')
                        self.err_win.show()
                        return

        entry.append(entry_name)
        serv_size_options = {}  # {amount1: unit1, amount2: unit2, ...}
        for i in range(3, 6):
            # Ranges from first to last QHBoxLayout containing serving size info.
            serv_amount = self.info1_layout.itemAt(i).itemAt(0).widget().text()
            serv_unit = self.info1_layout.itemAt(i).itemAt(1).widget().currentText()
            if not serv_amount:
                continue
            try:
                float(serv_amount)
            except ValueError:
                self.mess_win = MessageWin('invalid serving size amount')
                self.mess_win.show()
                return
            serv_size_options[serv_unit] = serv_amount

        # There must be at least one serving size.
        if not serv_size_options:
            self.mess_win = MessageWin('blank serving')
            self.mess_win.show()
            return
        else:
            entry.append(serv_size_options)

        cal = self.info1_layout.itemAt(7).widget().text()
        fat = self.info1_layout.itemAt(9).itemAt(0).widget().text()
        sfat = self.info1_layout.itemAt(11).itemAt(0).widget().text()
        tfat = self.info1_layout.itemAt(13).itemAt(0).widget().text()
        pfat = self.info1_layout.itemAt(15).itemAt(0).widget().text()
        mfat = self.info1_layout.itemAt(17).itemAt(0).widget().text()

        chol = self.info2_layout.itemAt(1).itemAt(0).widget().text()
        sod = self.info2_layout.itemAt(3).itemAt(0).widget().text()
        carb = self.info2_layout.itemAt(5).itemAt(0).widget().text()
        fib = self.info2_layout.itemAt(7).itemAt(0).widget().text()
        sol_fib = self.info2_layout.itemAt(9).itemAt(0).widget().text()
        insol_fib = self.info2_layout.itemAt(11).itemAt(0).widget().text()
        sug = self.info2_layout.itemAt(13).itemAt(0).widget().text()
        added_sug = self.info2_layout.itemAt(15).itemAt(0).widget().text()
        pro = self.info2_layout.itemAt(17).itemAt(0).widget().text()

        entry.extend([cal, fat, sfat, tfat, pfat, mfat, chol, sod, carb, fib, sol_fib, insol_fib, sug, added_sug, pro])
        # Ensure each added entry value is a valid number.
        for info in entry[2:]:
            if info:
                try:
                    float(info)
                except ValueError:
                    self.mess_win = MessageWin('invalid fd entry info')
                    self.mess_win.show()
                    return
        total_cost = self.info2_layout.itemAt(19).itemAt(1).widget().text()
        serv_per_container = self.info2_layout.itemAt(19).itemAt(3).widget().text()

        # Give an error message if one of the cost input fields is blank.
        if (total_cost and not serv_per_container) or (not total_cost and serv_per_container):
            self.err_win = MessageWin('missing cost info')
            self.err_win.show()
            return
        elif total_cost and serv_per_container:
            try:
                total_cost, serv_per_container = float(total_cost), float(serv_per_container)
            except ValueError:
                self.mess_win = MessageWin('invalid fd entry info')
                self.mess_win.show()
                return
            if serv_per_container == int(serv_per_container):
                serv_per_container = int(serv_per_container)
            cost_per_serving = round((total_cost / serv_per_container), 3)
            entry.extend([[f"{total_cost:.2f}", str(serv_per_container)], str(cost_per_serving)])
        else:
            # Add empty strings if there was no input.
            entry.extend(["", ""])

        if self.edit_entry_name:
            # All current entries except the one that is being edited.
            entries_to_write = data.get_entries(FD_PATH, self.edit_entry_name, match=False)
        else:
            entries_to_write = data.get_entries(FD_PATH, return_all=True)

        if entries_to_write == "file not found":
            os.makedirs(os.path.dirname(FD_PATH), exist_ok=True)
            # Place new entry in a list by itself so that writerows() will accept it.
            entries_to_write = [entry, ]
        else:
            entries_to_write.append(entry)
            entries_to_write.sort()

        with open(FD_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(entries_to_write)

        self.fd_win = FoodDictWin()
        self.fd_win.show()
        self.close()


class MessageWin(QDialog):
    """Display a dialog box with an error message determined by the 'key'."""

    def __init__(self, key, entry_name=None):
        """Constructor.

        :param key: A string that determines which error message is shown to the user.
        :param entry_name: A string of an entry name. Default is None.
        """
        super().__init__()
        self.w = 350
        self.key = key
        self.entry_name = entry_name
        self.init_ui()

    def init_ui(self):
        """Set up UI. Include the error message and an 'ok' button for each dialog."""
        self.setFixedWidth(self.w)
        title = "Input Error"

        if self.key == "no name":
            message = "Please provide a name for the entry."

        elif self.key == "invalid serving size amount":
            message = "Please provide a valid serving size amount (10, 3.75, etc.)."

        elif self.key == "blank serving":
            message = 'Please provide a serving size. You may enter up to three, but only one is required.'

        elif self.key == "invalid fd entry info":
            message = 'Please either give a valid number for each field (10, 3.75, etc.), or leave the field blank.'

        elif self.key == "missing cost info":
            message = "Please provide an amount for both fields in the cost section, or leave both fields blank."

        elif self.key == 'no log entries selected to add':
            message = "Please select at least one log entry to add."

        elif self.key == "duplicate log entry":
            message = (f"There is already an entry for '{self.entry_name}' in the log. Please edit the existing "
                       f"entry instead of adding a new one.")

        elif self.key == "duplicate fd entry":
            message = ("The entry name you have given matches an existing one found in the food dictionary. Please "
                       "enter a different name or edit the existing entry.")

        elif self.key == "no selected entries to remove":
            message = "Please select at least one entry to remove."

        elif self.key == "no amount given (log add)":
            message = "Please provide an amount for each selected entry."

        elif self.key == "no amount given (log edit)":
            message = ("Please provide an amount for all entries in the table. All entries will be added to the "
                       "log file regardless of whether or not they are checked.")

        elif self.key == "invalid amount":
            message = "Please provide a valid number for the amounts."

        elif self.key == 'fd entry no longer exists':
            # When the user tries to edit a log entry whose food dictionary entry has been deleted.
            message = (f"The entry for '{self.entry_name}' has been removed from the food dictionary some time after "
                       f"the creation of this log. The log entry for '{self.entry_name}' is still tallied alongside "
                       f"the other entries, but it can't be edited without a matching food dictionary entry.")

        elif self.key == "no log entries selected to edit":
            message = "Please select at least one log entry to edit."

        elif self.key == "no single fd entry selected":
            message = "Please select a single entry to edit."

        elif self.key == "blank date":
            message = "Please provide a date for the log you want to view or edit."

        elif self.key == "invalid day":
            message = "Please provide a valid day of the month (1 - 31)."

        elif self.key == "invalid year":
            message = "Please provide a valid four-digit year."

        elif self.key == "date does not exist":
            message = "The date you have entered does not exist. Please check the date and try again."

        elif self.key == "log file not found":
            title = "File Not Found"
            message = "The log file for the specified date could not be found. Please check the date and try again."

        elif self.key == "fd file not found (fd window)":
            title = "File Not Found"
            message = "There are currently no entries in the food dictionary."

        elif self.key == "fd file not found (log window)":
            title = "File Not Found"
            message = ("There are currently no entries in the food dictionary. Click the 'Go to food dictionary' "
                       "button to add entries, which will be used to manage logs.")

        elif self.key == 'fd file not found (log window edit)':
            title = "File Not Found"
            message = ("There are currently no entries in the food dictionary. To edit a log entry, there must "
                       "be a matching food dictionary entry. Click the 'Go to food dictionary' button to add "
                       "add entries before editing a log.")

        elif self.key == "no next file":
            title = "File Not Found"
            message = "There are no log files after the currently selected date."

        elif self.key == "no previous file":
            title = "File Not Found"
            message = "There are no log files before the currently selected date."

        self.setWindowTitle(title)
        message_label = QLabel(message, self)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft)
        ok_btn = QPushButton('Ok', self)
        ok_btn.setFixedSize(75, 27)
        ok_btn.clicked.connect(self.close_win)
        layout = QVBoxLayout()
        layout.addWidget(message_label, alignment=Qt.AlignVCenter)
        layout.addWidget(ok_btn, alignment=Qt.AlignRight)
        layout.setSpacing(20)
        self.setLayout(layout)
        self.setStyleSheet('''
            QDialog {
                background-color: rgb(255, 250, 230);
                border: 2px solid red;
            }
            QWidget {
                font: 14px;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                color: black;
                background-color: rgb(210, 210, 210);
                border-width: 2px;
                border-style: outset;
                border-radius: 5px;
                border-color: rgb(70, 70, 70);
                padding: 3px;
            }
            ''')

    def close_win(self):
        """Close the dialog box."""
        self.close()
