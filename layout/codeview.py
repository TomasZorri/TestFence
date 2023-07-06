## For Ui
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QPushButton,
    QFileDialog, QTabBar, QLineEdit, QTextEdit, QMessageBox, QSplitter,QCompleter)
from PyQt5.QtCore import Qt, QEvent, QDir, QFileInfo, QCoreApplication, pyqtSignal, QEventLoop, QObject
from PyQt5.QtGui import QTextCursor, QStandardItemModel, QStandardItem
from PyQt5 import Qsci

# for errors
import traceback
import re

# Security
from RestrictedPython  import compile_restricted
from RestrictedPython.Guards import safe_builtins

# database
from datetime import date
import sys
sys.path.append('..')
from model import ErrorEntry

# check url
import requests
 


# Page load timeout logic
class WaitObject(QObject):
    finished = pyqtSignal()
def waitForSignal(signal):
    wait_obj = WaitObject()
    signal.connect(wait_obj.finished)
    wait_obj.finished.connect(lambda: signal.disconnect(wait_obj.finished))
    loop = QEventLoop()
    signal.connect(loop.quit)
    loop.exec_()



class CodeEditor(QWidget):
    def __init__(self, browser_view, session,  parent=None):
        super(CodeEditor, self).__init__(parent)


        # Instances
        self.session = session
        self.browser_url = browser_view
        self.browser_loaded = browser_view.web_view
        self.browser_loaded.loadFinished.connect(self.on_load_finished)
        self.page_load = True
        self.execution_paused = False

        # Widget of the QTabWidget
        self.tab_widget = QTabWidget(self)
        self.tab_widget.installEventFilter(self)  # Install the event filter in the QTabWidget
        self.tab_widget.setTabsClosable(True)  # Enable closing tabs
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # Connect tab close signal

        # "File" button
        archivo_button = QPushButton("File", self)
        archivo_button.clicked.connect(self.open_file_dialog)
        self.tab_widget.setCornerWidget(archivo_button, Qt.TopLeftCorner)

        # "+" Button
        add_tab_button = QPushButton("+", self)
        add_tab_button.clicked.connect(self.create_new_file)
        self.tab_widget.setCornerWidget(add_tab_button, Qt.TopRightCorner)


        # code_editer configuration
        self.unsaved_changes = False # if changes have been made without saving
        self.create_new_file()  # Add the first default tab
        self.error_text_edit = {}


        # Config Widget Of class code
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # Error and run widget handlers
        self.actions_text_edit = QTextEdit()
        self.actions_text_edit.hide()
        self.actions_text_edit.setReadOnly(True)
        self.error_text_widget = QTextEdit()
        self.error_text_widget.hide()
        self.error_text_widget.setReadOnly(True)

        # Other initializations
        self.last_opened_folder = QDir.homePath()
        self.execute_functions = True # Enable the executions of the functionalities




    # *****************************************************
    # *****************************************************
    # Functioning logic, search, add content and click element
    # *****************************************************
    # *****************************************************

    # Wait for the page to finish loading
    def on_load_finished(self):
        print('The page has finished loading!')
        self.page_load = True

    # Click on element
    def click_element(self, tag, attribute, contentAttribute, tag_navigation=False, time_wait=False):
        if not self.page_load:
            waitForSignal(self.browser_loaded.loadFinished) # wait until the page finishes loading before continuing

        # If the url gives an error, it is not executed
        if self.execute_functions:
            script = f"""
                var element = document.querySelector('{tag}[{attribute}="{contentAttribute}"]');
                if (element) {{
                    // navigate to element
                    if ({str(tag_navigation).lower()} === 'true') {{
                        // Obtener la posición del elemento
                        var rect = element.getBoundingClientRect();
                        var elementLeft = rect.left + rect.width / 2 - window.innerWidth / 2;
                        var elementTop = rect.top + rect.height / 2 - window.innerHeight / 2;

                        // Desplazarse a la posición del elemento
                        window.scrollTo({{ left: elementLeft, top: elementTop, behavior: 'smooth' }});
                    }}

                    // Logic click element
                    element.style.border = '3px solid red';
                    element.click();
                    if ((element.getAttribute('data-clicked') === 'true' || (element.getAttribute('href') && element.getAttribute('href') !== '') || (element.tagName === 'INPUT' && element.getAttribute('type') === 'button') || (element.tagName === 'INPUT' && element.getAttribute('type') === 'submit') || (element.tagName === 'INPUT' && element.getAttribute('type') === 'checkbox') || (element.tagName === 'INPUT' && element.getAttribute('type') === 'radio') || (element.tagName === 'SELECT') || (element.tagName === 'LABEL'))) {{
                        element = 'positive';
                    }} else {{
                        element = 'no_functionality';
                    }}
                }} else {{
                    element = null;
                }}
            """

            # get result
            def handle_result(result):
                fecha_actual = date.today()
                fecha_actual_formateada = fecha_actual.strftime('%Y-%m-%d')

                if result is not None:
                    if result == 'no_functionality':
                        # The element exists but was not clicked correctly
                        steps_to_follow = f"""When executing "click_element('{tag}', '{attribute}', '{contentAttribute}')" it does not perform any action."""
                        error_message = "This error occurs when there is no action after clicking on an element"
                        self.insert_error_entry('activo', 'Item functionality error', steps_to_follow,
                                error_message, 'Resultados esperados', 'Resultados obtenidos',fecha_actual_formateada)

                        # add to display
                        if self.actions_text_edit:
                            self.actions_text_edit.append('Error: The element could not be clicked.')
                            self.actions_text_edit.append('')
                    elif result == 'positive' and self.actions_text_edit:
                        self.actions_text_edit.append('You have clicked!!')
                        self.actions_text_edit.append('')
                else:
                    # The element does not exist
                    steps_to_follow = f"""When executing "click_element('{tag}', '{attribute}', '{contentAttribute}')" the element was not found."""
                    error_message = "This error occurs when the item does not exist on the site."
                    self.insert_error_entry('activo', 'Error searching for said element', steps_to_follow,
                            error_message, 'Resultados esperados', 'Resultados obtenidos',fecha_actual_formateada)
                    
                    # add to display
                    if self.actions_text_edit:
                        self.actions_text_edit.append('Error: Item not found.')
                        self.actions_text_edit.append('')

            # run script
            self.browser_loaded.page().runJavaScript(script, handle_result)

            # optional if you want to wait
            if time_wait:
                if self.actions_text_edit:
                    self.actions_text_edit.append('Waiting until the page finishes loading!')
                    self.actions_text_edit.append('')
                self.page_load = False




    # add content
    def set_content(self, tag, option, content_option, value, tag_navigation=False):
        if not self.page_load:
            waitForSignal(self.browser_loaded.loadFinished) # wait until the page finishes loading before continuing

        # If the url gives an error, it is not executed
        if self.execute_functions:
            # perform the action
            script = f"""
                var element = document.querySelector('{tag}[{option}="{content_option}"]');
                if (element) {{
                    if ({str(tag_navigation).lower()} === 'true') {{
                        // Obtener la posición del elemento
                        var rect = element.getBoundingClientRect();
                        var elementLeft = rect.left + rect.width / 2 - window.innerWidth / 2;
                        var elementTop = rect.top + rect.height / 2 - window.innerHeight / 2;

                        // Desplazarse a la posición del elemento
                        window.scrollTo({{ left: elementLeft, top: elementTop, behavior: 'smooth' }});
                    }}
                    element.style.border = '3px solid red';
                    element.value = '{value}';
                    element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            """

            def handle_result(result):
                if result is not None:
                    element_value = result.toString()
                    if self.actions_text_edit:
                        self.actions_text_edit.append('You have added a content: ', element_value)
                        self.actions_text_edit.append('')
                else:
                    # add to display
                    if self.actions_text_edit:
                        self.actions_text_edit.append('Error: No content added!')
                        self.actions_text_edit.append('')

            # execute the action
            self.browser_loaded.page().runJavaScript(script, handle_result)




    # Is to wait until the page finishes loading
    def load_pege_finished(self):
        # If the url gives an error, it is not executed
        if self.execute_functions:
            if self.actions_text_edit:
                self.actions_text_edit.append('Waiting until the page finishes loading!')
                self.actions_text_edit.append('')
            self.page_load = False




    # Define url for the page
    def set_url_for_browser(self, url, time_wait=False):
        if not self.page_load:
            waitForSignal(self.browser_loaded.loadFinished) # wait until the page finishes loading before continuing


        response = self.check_url_status(url)
        if response == 404:
            self.execute_functions = False # Exclude features by mistake from the site

            # add to display
            if self.actions_text_edit:
                self.actions_text_edit.append('404 error connecting to url!')
                self.actions_text_edit.append('')
        else:
            self.execute_functions = True # Enable the executions of the functionalities
            self.browser_url.start(url)

            # add to display
            if self.actions_text_edit:
                self.actions_text_edit.append('Destination URL changed!')
                self.actions_text_edit.append('')

            # Wait for the page to finish loading
            if time_wait:
                if self.actions_text_edit:
                    self.actions_text_edit.append('Waiting until the page finishes loading!')
                    self.actions_text_edit.append('')
                self.page_load = False

    # Check url status
    def check_url_status(self, url):
        try:
            response = requests.head(url)
            return response.status_code
        except requests.exceptions.RequestException:
            return 404  # Connection error or invalid request





    # Navigate between elements
    def navigation_of_tag_or_object(self, tag, option, content_option):
        if not self.page_load:
            waitForSignal(self.browser_loaded.loadFinished) # wait until the page finishes loading before continuing

        # If the url gives an error, it is not executed
        if self.execute_functions:
            script = f"""
                    var element = document.querySelector('{tag}[{option}="{content_option}"]');
                    if (element) {{
                        // Obtener la posición del elemento
                        var rect = element.getBoundingClientRect();
                        var elementLeft = rect.left + rect.width / 2 - window.innerWidth / 2;
                        var elementTop = rect.top + rect.height / 2 - window.innerHeight / 2;

                        // Desplazarse a la posición del elemento
                        window.scrollTo({{ left: elementLeft, top: elementTop, behavior: 'smooth' }});
                    }}
                """

            if self.actions_text_edit:
                self.actions_text_edit.append('You have navigated to the intended object!')
                self.actions_text_edit.append('')

            self.browser_loaded.page().runJavaScript(script)


    # Run Code
    def run_code(self):
        # Get the editor code of the active tab
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.widget(current_index)

        code_widget = current_widget.widget(0)
        code = code_widget.text()
        if not code:
            return
        elif code and self.unsaved_changes:
            self.save_file()
        

        # Define allowed functions and modules
        allowed_globals = {
            'click_element': self.click_element,
            'set_content': self.set_content,
            'wait_page': self.load_pege_finished,
            'set_url': self.set_url_for_browser,
            'navigation_tag': self.navigation_of_tag_or_object,
        }

        try:
            # Add the run widget
            if self.actions_text_edit.isVisible() != True:
                # Hide the error widget if it exists and add the run widget and show it
                self.error_text_widget.hide()
                self.actions_text_edit.show()
                current_widget.addWidget(self.actions_text_edit)
                self.error_text_widget.setPlainText("")

                ## Adjust Size
                sizes = current_widget.sizes()
                total_size = sum(sizes)
                code_editor_size = int(total_size * 0.9)
                actions_text_edit_size = total_size - code_editor_size
                sizes[0] = code_editor_size
                sizes[1] = actions_text_edit_size
                current_widget.setSizes(sizes)
                current_widget.widget(0).setMinimumHeight(int(total_size * 0.70))
                current_widget.widget(0).setMaximumHeight(code_editor_size)
                current_widget.widget(1).setMinimumHeight(actions_text_edit_size)
                current_widget.widget(1).setMaximumHeight(int(total_size * 0.30))
            else:
                self.error_text_widget.setPlainText("")


            # If there is no widget it will fit full screen
            if current_widget.count() == 1:
                sizes = sum(current_widget.sizes())
                current_widget.widget(0).setMinimumHeight(sizes)

            

            # Compile the restricted code
            code_restricted = compile_restricted(code, '<string>', 'exec')
            # Run the restricted code in a custom runtime environment
            exec(code_restricted, {'__builtins__': safe_builtins, '__name__': '__main__', **allowed_globals, '__import__': lambda x: None})
        except Exception as e:
            error_info = str(e)

            # Message configuration
            if isinstance(e, SyntaxError):
                match = re.search(r"SyntaxError: (.+)", error_info)
                if match:
                    syntax_error_message = match.group(1).rstrip('",)')
                    line_number = re.search(r"Line (\d+)", error_info)
                    if line_number:
                        error_message = f"SyntaxError: {syntax_error_message}. In Line: {line_number.group(1)}."
                    else: 
                        error_message = f"SyntaxError: {syntax_error_message}"
            else:
                line_info = traceback.format_exc().strip().split('\n')[-2]
                match = re.search(r'line (\d+)', line_info)
                if match:
                    error_message = f"{error_info}. In Line: {match.group(1)}."
                else:
                    error_message = f"{error_info}."

            # Check if the error text widget already exists for the current tab
            if current_index in self.error_text_edit and self.error_text_widget.isVisible() == True:
                error_text_edit = self.error_text_edit[current_index]
                error_text_edit.setPlainText(error_message)     
            elif self.error_text_widget.isVisible() != True:
                ## Error text widget and add it to the current tab layout
                self.actions_text_edit.hide()
                self.error_text_widget.show()
                current_widget.addWidget(self.error_text_widget)
                self.error_text_widget.setPlainText(error_message)

                ## Calculate your size
                sizes = current_widget.sizes()
                total_size = sum(sizes)
                code_editor_size = int(total_size * 0.9)
                error_text_edit_size = total_size - code_editor_size
                # Set the new sizes in the QSplitter
                sizes[0] = code_editor_size
                sizes[1] = error_text_edit_size
                current_widget.setSizes(sizes)
                current_widget.widget(0).setMinimumHeight(int(total_size * 0.70))
                current_widget.widget(0).setMaximumHeight(code_editor_size)
                current_widget.widget(1).setMinimumHeight(error_text_edit_size)
                current_widget.widget(1).setMaximumHeight(int(total_size * 0.30))
                
                ## add the error message to the tab that has it
                self.error_text_edit[current_index] = self.error_text_widget

            self.tab_widget.setCurrentIndex(current_index)
            

    # Pause the code
    def pause_execution(self):
        self.execution_paused = True



    # ******************************************
    # ******************************************
    # Code editor actions
    # ******************************************
    # ******************************************

    def undo_accion(self):
        code_widget = self.index_accion_code()
        if code_widget and code_widget.isUndoAvailable():
            code_widget.undo()

    def redo_accion(self):
        code_widget = self.index_accion_code()
        if code_widget and code_widget.isRedoAvailable():
            code_widget.redo()

    def cut_accion(self):
        code_widget = self.index_accion_code()
        code_widget.cut()

    def copy_accion(self):
        code_widget = self.index_accion_code()
        code_widget.copy()

    def paste_accion(self):
        code_widget = self.index_accion_code()
        code_widget.paste()

    def index_accion_code(self):
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.widget(current_index)
        if current_widget:
            return current_widget.widget(0)



    # *****************************************************
    # *****************************************************
    # Option of file Save, Open and CLose
    # *****************************************************
    # *****************************************************

    # Create new code tab
    def create_new_file(self):
        self.code_editor = Qsci.QsciScintilla(self)
        self.code_editor.clear()
        self.code_editor.textChanged.connect(self.handle_text_changed)


        # Set syntax highlighting options
        lexer = Qsci.QsciLexerPython()
        lexer.setDefaultFont(self.code_editor.font())
        self.code_editor.setLexer(lexer)

        # Set line numbering
        self.code_editor.setMarginType(0, Qsci.QsciScintilla.NumberMargin)
        self.code_editor.setMarginWidth(0, "000")
        self.code_editor.SendScintilla(self.code_editor.SCI_SETHSCROLLBAR, 0)

        # Configuration of the tab widget
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.code_editor)
        self.tab_widget.addTab(splitter, "New File")

        # Get the index of the newly created tab
        new_tab_index = self.tab_widget.count() - 1
        self.tab_widget.setCurrentIndex(new_tab_index)




    # Close code tab
    def close_tab(self, index):
        tab_widget_item = self.tab_widget.widget(index)
        if tab_widget_item is not None:
            if self.unsaved_changes:
                # Show a confirmation dialog
                reply = QMessageBox.question(self, "Changes not saved", "The file has been modified. Do you wish to save changes?",
                                             QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                if reply == QMessageBox.Save:
                    self.save_file()
                    self.event_close_tab(index, tab_widget_item)
                elif reply == QMessageBox.Discard:
                    self.event_close_tab(index, tab_widget_item)
                elif reply == QMessageBox.Cancel:
                    return
            else:
                self.event_close_tab(index, tab_widget_item) # Emit the QEvent.Close event manually to the tab widget

        # Check if the current tab was closed
        if index != self.tab_widget.currentIndex():
            updated_index = self.tab_widget.currentIndex()
        else:
            updated_index = index - 1 if index > 0 else 0

        if self.tab_widget.count() == 0:  # If there are no more tabs open
            self.create_new_file()

        # set the updated index
        self.tab_widget.setCurrentIndex(updated_index)

    def close_all_tabs(self):
        num_tabs = self.tab_widget.count()
        for i in range(num_tabs):
            self.close_tab(0)

    def event_close_tab(self, index, tab_widget_item):
        # Emit the QEvent.Close event manually to the tab widget
        close_event = QEvent(QEvent.Close)
        QCoreApplication.postEvent(tab_widget_item, close_event)

        # Remove the widget from code_edit
        current_widget = self.tab_widget.widget(index)
        code_widget = current_widget.widget(0)
        code_widget.deleteLater()
        # Remove the error_text_edit widget
        if index in self.error_text_edit:
            error_text_edit = self.error_text_edit[index]
            error_text_edit.deleteLater()
            del self.error_text_edit[index]

        # remove the tab
        self.tab_widget.removeTab(index) 



    # open_file widget
    def open_file_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Python Files (*.py)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setDirectory(QDir.homePath())
        file_dialog.setDirectory(self.last_opened_folder)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            for file in selected_files:
                self.open_file(file)

    def open_file(self, file_path):
        self.last_opened_folder = QFileInfo(file_path).absoluteDir().absolutePath()
        # Check if the file is already open in a tab
        for index in range(self.tab_widget.count()):
            tab_widget_item = self.tab_widget.widget(index)
            if tab_widget_item.property("file_path") == file_path:
                # Select the existing tab
                self.tab_widget.setCurrentIndex(index)
                return
                
        # Extract the file name from the full path
        file_name = QFileInfo(file_path).fileName()

        # Code editor widget for new tab
        # Call the create_new_file method to create a new tab
        self.create_new_file()

        # Get the code from the file and set it in the code editor of the new tab
        with open(file_path, 'r') as file:
            self.code_editor.setText(file.read())

        # Set the title of the new tab as the file name
        new_tab_index = self.tab_widget.count() - 1
        self.tab_widget.setTabText(new_tab_index, file_name)

        # Position and make visible the newly added tab
        self.tab_widget.setCurrentIndex(new_tab_index)
        self.tab_widget.setCurrentWidget(self.code_editor)

        # Set the "file_path" property on the tab widget
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.widget(current_index)

        current_widget.setProperty("file_path", file_path)

        


    # save code
    def save_file(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            current_widget = self.tab_widget.widget(current_index)
            code_widget = current_widget.widget(0)

            # Check if the file associated with the current tab
            file_path = current_widget.property("file_path")
            file_name = QFileInfo(file_path).fileName()
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(code_widget.text())
                self.unsaved_changes = False
                self.tab_widget.setTabText(current_index, file_name)  # Remove the "*" flag
            else:
                self.save_file_as() # If the file does not exist, call the save_file_as method
        
        if self.unsaved_changes:
            # Reconnect the textChanged signal to continue tracking changes without saving
            self.code_editor.textChanged.connect(self.handle_text_changed)


    def save_file_as(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            current_widget = self.tab_widget.widget(current_index)
            code_widget = current_widget.widget(0)
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "Python Files (*.py)")
            file_name = QFileInfo(file_path).fileName()
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(code_widget.text())
                current_widget.setProperty("file_path", file_path)  # Update the "file_path" property
                self.unsaved_changes = False
                self.tab_widget.setTabText(current_index, file_name)  # Remove the "*" flag


    # *****************************************************
    # *****************************************************
    #  Data Base errors 
    # *****************************************************
    # *****************************************************

    def insert_error_entry(self, status, title, pasos_reproducir, mensaje_error, resultados_esperados, resultados_obtenidos, error_date):
        error_date = date.fromisoformat(error_date)
        error_entry = ErrorEntry(
            status=status,
            title=title,
            pasos_reproducir=pasos_reproducir,
            mensaje_error=mensaje_error,
            resultados_esperados=resultados_esperados,
            resultados_obtenidos=resultados_obtenidos,
            error_date=error_date
        )
        self.session.add(error_entry)
        self.session.commit()



    # *****************************************************
    # *****************************************************
    # Events 
    # *****************************************************
    # *****************************************************

    # In save it checks if there are changes that the event that has to save appears
    def handle_text_changed(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            current_widget = self.tab_widget.widget(current_index)
            current_widget.setProperty("modified", True)
            self.unsaved_changes = True

            # Update the tab title to reflect the changes without saving
            file_name = self.tab_widget.tabText(current_index)
            if "*" not in file_name:
                self.tab_widget.setTabText(current_index, file_name + " *")

    # keyboard events
    def eventFilter(self, obj, event):
        if obj is self.tab_widget and event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.LeftButton:
                # Check if there is an active QLineEdit and deactivate its focus
                for index in range(self.tab_widget.count()):
                    line_edit = self.tab_widget.tabBar().tabButton(index, QTabBar.LeftSide)
                    if line_edit and line_edit.hasFocus():
                        line_edit.clearFocus()

                self.create_new_file()
                return True


        if isinstance(obj, QTabWidget) and event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.RightButton:
                tab_index = self.tab_widget.currentIndex()
                if tab_index != -1:
                    previous_text = self.tab_widget.tabText(tab_index)
                    # Create a QLineEdit to edit the tab name
                    line_edit = QLineEdit(self.tab_widget.tabText(tab_index))
                    # Get the new name of the QLineEdit
                    new_text = line_edit.text()
                    line_edit.selectAll()
                    line_edit.editingFinished.connect(lambda: self.update_tab_text(tab_index, line_edit.text()))
                    self.tab_widget.tabBar().setTabButton(tab_index, QTabBar.LeftSide, line_edit)
                    line_edit.setFocus()

                    # Disable tab text while editing
                    self.tab_widget.setTabText(tab_index, "")

                    def finish_editing():
                        # Get the new name of the QLineEdit
                        new_text = line_edit.text()

                        # If the new text is an empty string, restore the old content
                        if new_text == "":
                            new_text = previous_text

                        # Update the tab text if there have been changes
                        if new_text != self.tab_widget.tabText(tab_index):
                            self.tab_widget.setTabText(tab_index, new_text)

                        # Remove the QLineEdit if it still exists
                        if line_edit is not None:
                            self.tab_widget.tabBar().setTabButton(tab_index, QTabBar.LeftSide, None)

                    line_edit.editingFinished.connect(finish_editing)

                    def focus_out_event(event):
                        finish_editing() # Losing focus ends editing without changes

                    line_edit.focusOutEvent = focus_out_event

                    return True
        elif isinstance(obj, QTabWidget) and event.type() == QEvent.Close:
            # Closing a tab, finish editing the QLineEdit if it is active
            line_edit = self.tab_widget.tabBar().tabButton(self.tab_widget.currentIndex(), QTabBar.LeftSide)
            if isinstance(line_edit, QLineEdit):
                if line_edit is not None:
                    line_edit.editingFinished.emit()  # Emit the edit completion signal

    

        return super().eventFilter(obj, event)

    def update_tab_text(self, tab_index, new_text):
        self.tab_widget.setTabText(tab_index, new_text)

