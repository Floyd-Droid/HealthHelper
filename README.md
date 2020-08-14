# Health Helper
[![Build status](https://travis-ci.org/Floyd-Droid/HealthHelper.svg?branch=master)](https://travis-ci.org/github/Floyd-Droid/HealthHelper)
[![Made with PyQt5](https://img.shields.io/badge/made%20with-PyQt5-orange)](https://pypi.org/project/PyQt5)
![Python](https://img.shields.io/badge/python-3.8%20|%203.7-blue.svg)
![OS](https://img.shields.io/badge/OS-Linux%20|%20OSX%20|%20Windows-brightgreen)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE.md)


Health Helper is a small PyQt5 application that allows the user to keep track of the nutritional content of the foods 
they eat, as well as track grocery spending.

# Dependencies

PyQt5 5.14: Python bindings for Qt

Python 3.7 or 3.8

# Installation

This application has been tested on the following operating systems:
* Ubuntu - 16.04 (Xenial), 18.04 (Bionic), 20.04 (Focal)
* macOS 10.14
* Windows 10


To install, first clone the project.
```bash
git clone https://github.com/Floyd-Droid/HealthHelper.git
```

Create a new Python 3.7 or 3.8 virtual environment in the cloned repository.
```bash
python3 -m venv venv
```

Activate the virtual environment
```bash
# Linux and OSX
source venv/bin/activate
# Windows
venv\scripts\activate.bat
```

Use the setup script and pip install.
```bash
pip3 install .
```

Run the app.
```bash
healthhelper
```

If any errors occur, try upgrading pip or installing wheel before the project installation.

# Interface

Store information about different food items in the Food Dictionary.

![Food Dictionary window](./screenshots/fd_window.png)

You can add cost and nutritional information for each entry.

![Food Dictionary edit window](./screenshots/fd_edit_window.png)

Once you have added entries to the Food Dictionary, you can choose which entries to add to a log for a specified date.
Simply select the entries to be added and provide an amount for each. The nutrition and cost totals for the selected
items to be added are displayed in a table, so that the user can preview them before committing the entries to the log.

![Log edit window](./screenshots/log_edit_window.png)

Once entries are added to a log, they are displayed in a table. A separate table displays the totals of all entries, 
as well as totals for the selected entries only.

![Log window](./screenshots/log_view_window.png)

From here, the log entries can be quickly and easily removed or edited by selecting the desired entries and 
clicking the corresponding buttons.

# Author

Jourdon Floyd

email: jourdonfloyd@gmail.com

GitHub: https://github.com/Floyd-Droid

# License

This project is licensed under the MIT License - see the LICENSE.md file for details.
