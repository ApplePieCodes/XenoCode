import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, QComboBox, QSlider, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import Qt
import configparser
import requests

#################################
# XENOCODE IDE
#################################

class PreferencesWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.config.read('settings.config')

        self.settings = {
            'theme_index': self.config.getint('Preferences', 'theme_index', fallback=0),
            'font_size': self.config.getint('Preferences', 'font_size', fallback=12),
        }

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Preferences')
        self.setGeometry(300, 300, 400, 300)

        tab_widget = QTabWidget(self)

        general_tab = QWidget()
        self.initGeneralTab(general_tab)
        tab_widget.addTab(general_tab, 'General')

        appearance_tab = QWidget()
        self.initAppearanceTab(appearance_tab)
        tab_widget.addTab(appearance_tab, 'Appearance')

        button_box = QDialogButtonBox(
            QDialogButtonBox.Close | QDialogButtonBox.Apply | QDialogButtonBox.Ok,
            Qt.Horizontal,
            self
        )
        button_box.clicked.connect(self.handleButtonClick)

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def initGeneralTab(self, tab):
        label = QLabel('General Settings - Add your preferences here!')
        layout = QVBoxLayout(tab)
        layout.addWidget(label)

    def initAppearanceTab(self, tab):
        theme_label = QLabel('Select Theme:')
        theme_combo = QComboBox()
        theme_combo.addItems(['Light Theme', 'Dark Theme', 'Ocean Theme', 'Sunset Theme', 'Forest Theme'])
        theme_combo.currentIndexChanged.connect(self.changeTheme)

        font_size_label = QLabel('Font Size:')
        font_size_slider = QSlider(Qt.Horizontal)
        font_size_slider.setRange(10, 20)
        font_size_slider.setValue(self.settings['font_size'])
        font_size_slider.valueChanged.connect(self.changeFontSize)

        layout = QVBoxLayout(tab)
        layout.addWidget(theme_label)
        layout.addWidget(theme_combo)
        layout.addWidget(font_size_label)
        layout.addWidget(font_size_slider)

    def changeTheme(self, index):
        self.settings['theme_index'] = index

    def changeFontSize(self, font_size):
        self.settings['font_size'] = font_size

    def handleButtonClick(self, button):
        if button.text() == 'Apply':
            print('Apply button clicked')
            self.applyChanges()
            self.accept()
        elif button.text() == 'Ok':
            print('Ok button clicked')
            self.applyChanges()
            self.accept()
        elif button.text() == 'Close':
            print('Close button clicked')
            self.reject()

    def applyChanges(self):
        theme_index = self.settings['theme_index']
        font_size = self.settings['font_size']

        print(f"Applying changes - Theme: {theme_index}, Font Size: {font_size}")

        self.config['Preferences'] = {
            'theme_index': str(theme_index),
            'font_size': str(font_size),
        }

        with open('settings.config', 'w') as configfile:
            self.config.write(configfile)

class XenoCode(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.config.read('settings.config')

        self.current_version = '1.0'
        self.latest_version = self.get_latest_version()

        self.initUI()
        self.updateSettings(self.config.getint('Preferences', 'theme_index', fallback=0), self.config.getint('Preferences', 'font_size', fallback=12))

    def get_latest_version(self):
        url = 'https://raw.githubusercontent.com/your_username/your_repository/main/version.txt'
        try:
            response = requests.get(url)
            response.raise_for_status()
            latest_version = response.text.strip()
            return latest_version
        except requests.RequestException as e:
            print(f"Error fetching latest version: {e}")
            return None

    def check_for_updates(self):
        return self.latest_version and self.current_version < self.latest_version

    def prompt_for_update(self):
        reply = QMessageBox.question(
            None,
            'Update Available',
            'A new version is available. Do you want to update?',
            QMessageBox.Yes | QMessageBox.No,
        )
        return reply == QMessageBox.Yes

    def download_and_apply_update(self):
        print("Downloading and applying update...")
        # Add logic to download and apply the update

    def initUI(self):
        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)

        menubar = self.menuBar()

        # File menu
        fileMenu = menubar.addMenu('File')

        newFile = QAction('New', self)
        newFile.triggered.connect(self.newFile)
        fileMenu.addAction(newFile)

        openFile = QAction('Open', self)
        openFile.triggered.connect(self.showDialog)
        fileMenu.addAction(openFile)

        saveFile = QAction('Save', self)
        saveFile.triggered.connect(self.saveDialog)
        fileMenu.addAction(saveFile)

        exitAction = QAction('Exit', self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        # Edit menu
        editMenu = menubar.addMenu('Edit')

        undoAction = QAction('Undo', self)
        undoAction.triggered.connect(self.textEdit.undo)
        editMenu.addAction(undoAction)

        cutAction = QAction('Cut', self)
        cutAction.triggered.connect(self.textEdit.cut)
        editMenu.addAction(cutAction)

        copyAction = QAction('Copy', self)
        copyAction.triggered.connect(self.textEdit.copy)
        editMenu.addAction(copyAction)

        pasteAction = QAction('Paste', self)
        pasteAction.triggered.connect(self.textEdit.paste)
        editMenu.addAction(pasteAction)

        # Settings menu
        settingsMenu = menubar.addMenu('Settings')

        preferencesAction = QAction('Preferences', self)
        preferencesAction.triggered.connect(self.showPreferences)
        settingsMenu.addAction(preferencesAction)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('XenoCode')
        self.show()

    def newFile(self):
        self.textEdit.clear()

    def showDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.DontUseNativeDialog
        filters = "Python Files (*.py);;C Files (*.c);;C++ Files (*.cpp, *.c++);;Java Files (*.java);;C# Files (*.cs, *.cake, *.csx);;Visual Basic Files (*.vb, *.vbs);;JavaScript (*.js);;SQL Files (*.sql);;Assembly Files (*.asm);;PHP Files (*.php, *.php3, *.php4, *.php5);;R Files (*.r);;C Files (*.c);;Go Files (*.go);;MatLab Files (*.matlab);;Swift Files (*.swift);;Ruby Files (*.rb, *.ruby);;Perl Files (*.pl, *.perl);;Objective-C Files (*.m, *.h);;Rust Files (*.rs);;SAS Files (*.sas);;Kotlin Files (*.kt, *.ktm, *.kts);;Julia Files (*.jl);;Lua Files (*.lua);;Fortran Files (*.f, *.for, *.f77, *.f90, *.f95, *.f03, *.f08);;Cobol Files (*.cob, *.cobol);;Lisp Files (*.lisp);;Ada Files (*.ada);;Dart Files (*.dart);;Scala Files (*.scala);;Prolog Files (*.pro, *.pl, *.prolog);;D Files (*.d);;Shell Files (*.sh, *.bash);;PowerShell Files (*.ps1)"
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '/home', filters, options=options)

        if fname:
            with open(fname, 'r') as f:
                data = f.read()
                self.textEdit.setText(data)

    def saveDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "Python Files (*.py);;C Files (*.c);;C++ Files (*.cpp, *.c++);;Java Files (*.java);;C# Files (*.cs, *.cake, *.csx);;Visual Basic Files (*.vb, *.vbs);;JavaScript (*.js);;SQL Files (*.sql);;Assembly Files (*.asm);;PHP Files (*.php, *.php3, *.php4, *.php5);;R Files (*.r);;C Files (*.c);;Go Files (*.go);;MatLab Files (*.matlab);;Swift Files (*.swift);;Ruby Files (*.rb, *.ruby);;Perl Files (*.pl, *.perl);;Objective-C Files (*.m, *.h);;Rust Files (*.rs);;SAS Files (*.sas);;Kotlin Files (*.kt, *.ktm, *.kts);;Julia Files (*.jl);;Lua Files (*.lua);;Fortran Files (*.f, *.for, *.f77, *.f90, *.f95, *.f03, *.f08);;Cobol Files (*.cob, *.cobol);;Lisp Files (*.lisp);;Ada Files (*.ada);;Dart Files (*.dart);;Scala Files (*.scala);;Prolog Files (*.pro, *.pl, *.prolog);;D Files (*.d);;Shell Files (*.sh, *.bash);;PowerShell Files (*.ps1)"
        fname, _ = QFileDialog.getSaveFileName(self, 'Save file', '/home', filters, options=options)

        if fname:
            with open(fname, 'w') as f:
                f.write(self.textEdit.toPlainText())

    def showPreferences(self):
        preferences_window = PreferencesWindow()
        result = preferences_window.exec_()

        if result == QDialog.Accepted:
            settings = preferences_window.settings
            self.updateSettings(settings['theme_index'], settings['font_size'])

    def updateSettings(self, theme_index, font_size):
        theme_stylesheets = [
            '',  # Light Theme
            'QTextEdit { background-color: #333; color: #FFF; }',  # Dark Theme
            'QTextEdit { background-color: #007acc; color: #FFF; }',  # Ocean Theme
            'QTextEdit { background-color: #ffa07a; color: #FFF; }',  # Sunset Theme
            'QTextEdit { background-color: #228B22; color: #FFF; }',  # Forest Theme
        ]

        self.textEdit.setStyleSheet(theme_stylesheets[theme_index])

        font = self.textEdit.font()
        font.setPointSize(font_size)
        self.textEdit.setFont(font)

    def main(self):
        if self.check_for_updates():
            if self.prompt_for_update():
                self.download_and_apply_update()

        app = QApplication(sys.argv)
        xenocode_editor = XenoCode()
        sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    xenocode_editor = XenoCode()
    xenocode_editor.main()