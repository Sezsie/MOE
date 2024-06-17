import sys
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

app = QApplication(sys.argv)

# a collection of classes that handle the UI of MOE

class BaseUI(QWidget):
    def __init__(self):
        super().__init__()
        self.screen = QApplication.primaryScreen()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.set_size(300, 300)
        self.app = app

    def set_size(self, width, height):
        screen_size = self.screen.size()
        self.resize(width, height)
        self.move((screen_size.width() - width) // 2, (screen_size.height() - height) // 2)

class TextEditorUI(BaseUI):
    textUpdated = Signal(str) 
    
    def __init__(self):
        super().__init__()
        self.textEdit = QTextEdit()
        self.layout.addWidget(self.textEdit)
        # set the window to always stay on top when it is first created
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # undo the always on top setting after initialization
        self.setWindowFlags(Qt.Widget)
        self.textUpdated.connect(self.textEdit.setText)
        # default text is "Loading..."
        self.textEdit.setPlaceholderText("Type here...")

    def add_button(self, name, action, tooltip=None):
        button = QPushButton(name)
        button.clicked.connect(action)
        if tooltip:
            button.setToolTip(tooltip)
        self.layout.addWidget(button)

    def load_text(self, text):
        """ Thread-safe text loading by emitting a signal. """
        self.textUpdated.emit(text)

    def change_window_title(self, title):
        self.setWindowTitle(title)

# small text box that a user can type in, with buttons to interact with the text.
# has an unchangable tip text that says "Type below."
class NamingUI(BaseUI):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Name your command, and MOE will remember it. (e.g. 'open file')")
        # window title
        self.setWindowTitle("Save Command")
        self.layout.addWidget(self.label)
        self.textEdit = QTextEdit()
        self.layout.addWidget(self.textEdit)
        # this UI cant be resized
        self.setFixedSize(400, 100)

    def clear_text(self):
        self.textEdit.clear()
        
    def change_label(self, text):
        self.label.setText(text)

    def print_text(self):
        print(self.textEdit.toPlainText())

    def add_button(self, name, action, tooltip=None):
        button = QPushButton(name)
        button.clicked.connect(action)
        if tooltip:
            button.setToolTip(tooltip)
        self.layout.addWidget(button)
    
    
# confirmation dialog that simply displays two buttons with a message.    
class ConfirmationUI(BaseUI):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Would you like to continue?")
        self.layout.addWidget(self.label)
        
    def clear_text(self):
        self.textEdit.clear()
        
    def set_label(self, text):
        self.label.setText(text)

    def add_button(self, name, action, tooltip=None):
        button = QPushButton(name)
        button.clicked.connect(action)
        if tooltip:
            button.setToolTip(tooltip)
        self.layout.addWidget(button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor_ui = NamingUI()
    editor_ui.show()
    editor_ui.add_button("Save", editor_ui.print_text, "Save the command to MOE's internal database.")
    sys.exit(app.exec_())
