import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import configparser
import requests

#################################
# XENOCODE IDE
#################################

class SnippetsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.snippets = self.loadSnippets()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Code Snippets')
        self.setGeometry(300, 300, 400, 300)

        # Create a list widget to display snippets
        self.snippetsListWidget = QListWidget(self)
        self.populateSnippetsList()

        layout = QVBoxLayout(self)
        layout.addWidget(self.snippetsListWidget)

    def loadSnippets(self):
        try:
            with open('snippets.txt', 'r') as file:
                lines = file.readlines()

            snippets = []
            current_snippet = None

            for line in lines:
                line = line.strip()

                if line.startswith(";;") and line.endswith(";;"):
                    # New snippet name
                    current_snippet = {"name": line[2:-2], "command": ""}
                elif line.startswith(":") and line.endswith(":") and current_snippet is not None:
                    # Command for the current snippet
                    current_snippet["command"] = line[1:-1]
                    snippets.append(current_snippet)
                    current_snippet = None

            return snippets
        except FileNotFoundError:
            print("Snippets file not found.")
            return []

    def copySnippet(self, item):
        selected_snippet = next((snippet for snippet in self.snippets if snippet["name"] == item.text()), None)
        if selected_snippet:
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_snippet["command"])
            print(f"Snippet '{selected_snippet['name']}' copied to clipboard.")

    def populateSnippetsList(self):
        self.snippetsListWidget.clear()
        snippet_names = [snippet["name"] for snippet in self.snippets]
        self.snippetsListWidget.addItems(snippet_names)
        self.snippetsListWidget.itemDoubleClicked.connect(self.copySnippet)

class PreferencesWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.settings = {
            'theme_index': 0,
            'font_size': 12,
            'custom_stylesheet': '',
        }

        try:
            self.config.read('settings.config')
            self.loadSettings()
        except Exception as e:
            print(f"Error reading settings: {e}")
            QMessageBox.critical(self, 'Error', 'Error reading settings. Default settings will be used.')

        self.initUI()

    def loadSettings(self):
        try:
            self.settings['theme_index'] = self.config.getint('Preferences', 'theme_index', fallback=0)
            self.settings['font_size'] = self.config.getint('Preferences', 'font_size', fallback=12)
            self.settings['custom_stylesheet'] = self.config.get('Preferences', 'custom_stylesheet', fallback='')
        except Exception as e:
            print(f"Error loading settings: {e}")
            raise  # Re-raise the exception to be caught by the calling code

    def saveSettings(self):
        try:
            self.config['Preferences'] = {
                'theme_index': str(self.settings['theme_index']),
                'font_size': str(self.settings['font_size']),
                'custom_stylesheet': self.settings['custom_stylesheet'],
            }

            with open('settings.config', 'w') as configfile:
                self.config.write(configfile)
        except Exception as e:
            print(f"Error saving settings: {e}")
            raise  # Re-raise the exception to be caught by the calling code

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

        # New: Customizable Themes
        custom_theme_label = QLabel('Custom Theme:')
        custom_theme_edit = QLineEdit()
        custom_theme_edit.setPlaceholderText('Enter your custom stylesheet here')
        custom_theme_edit.textChanged.connect(self.changeCustomTheme)

        layout = QVBoxLayout(tab)
        layout.addWidget(theme_label)
        layout.addWidget(theme_combo)
        layout.addWidget(font_size_label)
        layout.addWidget(font_size_slider)
        layout.addWidget(custom_theme_label)
        layout.addWidget(custom_theme_edit)

    def changeTheme(self, index):
        self.settings['theme_index'] = index

    def changeFontSize(self, font_size):
        self.settings['font_size'] = font_size

    # New: Customizable Themes
    def changeCustomTheme(self, custom_stylesheet):
        self.settings['custom_stylesheet'] = custom_stylesheet

    def handleButtonClick(self, button):
        actions = {
            'Apply': self.applyChanges,
            'Ok': self.applyChanges,
            'Close': self.reject,
        }

        try:
            action = actions.get(button.text())
            if action:
                print(f'{button.text()} button clicked')
                action()
                self.accept()
        except Exception as e:
            print(f"Error handling button click: {e}")
            QMessageBox.critical(self, 'Error', 'An error occurred. Please try again.')

    def applyChanges(self):
        try:
            theme_index = self.settings['theme_index']
            font_size = self.settings['font_size']

            print(f"Applying changes - Theme: {theme_index}, Font Size: {font_size}")

            self.saveSettings()
        except Exception as e:
            print(f"Error applying changes: {e}")
            raise  # Re-raise the exception to be caught by the calling code

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)

        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        width = self.lineNumberAreaWidth()
        self.setViewportMargins(width, 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        currentLineNumber = blockNumber + 1

        painter.setFont(self.font())
        painter.setPen(Qt.black)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                text = str(currentLineNumber)
                painter.drawText(
                    QRect(0, int(top), self.lineNumberArea.width(), int(self.fontMetrics().height())),
                    Qt.AlignRight, text
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            currentLineNumber += 1

class CodeSnippetManager:
    def __init__(self):
        self.code_snippets = []

    def add_snippet(self, name, code):
        self.code_snippets.append({'name': name, 'code': code})

    def load_snippets_from_github(self, github_raw_url):
        try:
            response = requests.get(github_raw_url)
            response.raise_for_status()

            # Assuming each line in the file contains a snippet in the format "Name Code"
            lines = response.text.splitlines()
            for line in lines:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    name, code = parts
                    self.add_snippet(name, code)

            print("Code snippets loaded successfully.")
        except requests.RequestException as e:
            print(f"Error loading snippets from GitHub: {e}")

    def get_snippets(self):
        return self.code_snippets

class XenoCode(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.config.read('settings.config')

        self.current_version = '1.0.4'
        self.latest_version = self.get_latest_version()

        self.initUI()
        self.updateSettings(
            self.config.getint('Preferences', 'theme_index', fallback=0),
            self.config.getint('Preferences', 'font_size', fallback=12),
            self.config.get('Preferences', 'custom_stylesheet', fallback='')
        )

    def get_latest_version(self):
        version_url = 'https://raw.githubusercontent.com/ApplePieCodes/XenoCode/main/version.txt'
        try:
            response = requests.get(version_url)
            response.raise_for_status()
            latest_version = response.text.strip()
            return latest_version
        except requests.RequestException as e:
            print(f"Error fetching latest version: {e}")
            return None

    def check_for_updates(self):
        if not self.latest_version:
            return False

        current_version_tuple = tuple(map(int, self.current_version.split('.')))
        latest_version_tuple = tuple(map(int, self.latest_version.split('.')))

        return current_version_tuple < latest_version_tuple

    def prompt_for_update(self):
        reply = QMessageBox.question(
            None,
            'Update Available',
            'A new version is available. Do you want to update?',
            QMessageBox.Yes | QMessageBox.No,
        )
        return reply == QMessageBox.Yes

    def download_and_apply_update(self):
        try:
            # Fetch the manifest file from GitHub
            manifest_url = 'https://raw.githubusercontent.com/ApplePieCodes/XenoCode/main/manifest.txt'
            response = requests.get(manifest_url)
            response.raise_for_status()
            manifest_content = response.text.strip()

            # Parse the manifest content to get file names
            file_names = manifest_content.split('\n')

            # Download and replace the existing files
            for file_name in file_names:
                file_url = f'https://raw.githubusercontent.com/ApplePieCodes/XenoCode/main/{file_name}'
                response = requests.get(file_url)
                response.raise_for_status()

                # Save the downloaded file
                with open(file_name, 'w') as f:
                    f.write(response.text)

            print("Update applied successfully!")
        except requests.RequestException as e:
            print(f"Error applying update: {e}")

    def initUI(self):
        self.codeEditor = CodeEditor()
        self.setCentralWidget(self.codeEditor)

        self.lineNumberArea = LineNumberArea(self.codeEditor)

        self.codeEditor.setViewportMargins(self.lineNumberArea.width(), 0, 0, 0)
        self.codeEditor.setTabStopWidth(20)

        self.codeEditor.cursorPositionChanged.connect(self.updateStatusBar)

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
        undoAction.triggered.connect(self.codeEditor.undo)
        editMenu.addAction(undoAction)

        cutAction = QAction('Cut', self)
        cutAction.triggered.connect(self.codeEditor.cut)
        editMenu.addAction(cutAction)

        copyAction = QAction('Copy', self)
        copyAction.triggered.connect(self.codeEditor.copy)
        editMenu.addAction(copyAction)

        pasteAction = QAction('Paste', self)
        pasteAction.triggered.connect(self.codeEditor.paste)
        editMenu.addAction(pasteAction)

        # Settings menu
        settingsMenu = menubar.addMenu('Settings')

        preferencesAction = QAction('Preferences', self)
        preferencesAction.triggered.connect(self.showPreferences)
        settingsMenu.addAction(preferencesAction)

        snippetsAction = QAction('Code Snippets', self)
        snippetsAction.triggered.connect(self.showSnippets)
        settingsMenu.addAction(snippetsAction)

        # Help menu
        helpMenu = menubar.addMenu('Help')

        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.showAboutDialog)
        helpMenu.addAction(aboutAction)

        updateAction = QAction('Check for Updates', self)
        updateAction.triggered.connect(self.checkForUpdatesAndPrompt)
        helpMenu.addAction(updateAction)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.updateStatusBar()

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('XenoCode')
        self.show()

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')

        if fname[0]:
            f = open(fname[0], 'r')

            with f:
                data = f.read()
                self.codeEditor.setPlainText(data)

    def saveDialog(self):
        fname = QFileDialog.getSaveFileName(self, 'Save file', './')

        if fname[0]:
            f = open(fname[0], 'w')

            with f:
                text = self.codeEditor.toPlainText()
                f.write(text)

    def newFile(self):
        self.codeEditor.clear()

    def updateStatusBar(self):
        cursor = self.codeEditor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1

        self.statusBar.showMessage(f'Line: {line}, Column: {col}')

    def showAboutDialog(self):
        about_text = (
            'XenoCode - A simple code editor\n\n'
            'Version: {}\n\n'
            'Created by Liam\n'
            'GitHub: https://github.com/ApplePieCodes/XenoCode'
        ).format(self.current_version)

        QMessageBox.about(self, 'About XenoCode', about_text)

    def showPreferences(self):
        preferences = PreferencesWindow()
        preferences.exec_()

        theme_index = preferences.settings['theme_index']
        font_size = preferences.settings['font_size']
        custom_stylesheet = preferences.settings['custom_stylesheet']

        self.updateSettings(theme_index, font_size, custom_stylesheet)

    def showSnippets(self):
        snippets_dialog = SnippetsDialog()
        snippets_dialog.exec_()

    def updateSettings(self, theme_index, font_size, custom_stylesheet):
        # Theme
        theme_stylesheet = ''
        if theme_index == 1:  # Dark Theme
            theme_stylesheet = 'styles/dark_theme.css'
        elif theme_index == 2:  # Ocean Theme
            theme_stylesheet = 'styles/ocean_theme.css'
        elif theme_index == 3:  # Sunset Theme
            theme_stylesheet = 'styles/sunset_theme.css'
        elif theme_index == 4:  # Forest Theme
            theme_stylesheet = 'styles/forest_theme.css'

        # Apply the selected theme or custom stylesheet
        if custom_stylesheet:
            self.setStyleSheet(custom_stylesheet)
        elif theme_stylesheet:
            with open(theme_stylesheet, 'r') as theme_file:
                self.setStyleSheet(theme_file.read())

        # Font Size
        font = self.codeEditor.font()
        font.setPointSize(font_size)
        self.codeEditor.setFont(font)

    def checkForUpdatesAndPrompt(self):
        if self.check_for_updates():
            if self.prompt_for_update():
                self.download_and_apply_update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    xenoCode = XenoCode()

    # Check for updates and prompt if available
    if xenoCode.check_for_updates():
        xenoCode.prompt_for_update()

    sys.exit(app.exec_())
