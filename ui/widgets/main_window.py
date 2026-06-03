from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.utils.fonts import apply_font
from ui.widgets.ui_main_window import Ui_MainWindow

class MainWindow(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

def run() -> None:
	app = QApplication(sys.argv)
	apply_font(app)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
