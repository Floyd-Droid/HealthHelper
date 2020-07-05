#!/usr/bin/env python
"""
Keep track of daily nutrition and track spending on groceries with the Health Helper application.
Version 1.0.0


Author
-------
Jourdon Floyd
email: jourdonfloyd@gmail.com
GitHub profile: https://github.com/Floyd-Droid


Project GitHub link: https://github.com/Floyd-Droid/HealthHelper

"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from healthhelper.interface import LogsWin


def main():
    """Launch the application."""
    app = QApplication([])
    app.setStyle('Fusion')

    # Remove the 'help' button from all windows.
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)

    main_win = LogsWin()
    main_win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
