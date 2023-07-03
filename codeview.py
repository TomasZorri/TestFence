from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QPushButton,
    QFileDialog, QTabBar, QLineEdit, QTextEdit, QMessageBox, QSplitter,QCompleter)
from PyQt5.QtCore import Qt, QEvent, QDir, QFileInfo, QCoreApplication, pyqtSignal, QEventLoop, QObject
from PyQt5.QtGui import QTextCursor, QStandardItemModel, QStandardItem
from PyQt5 import Qsci

# Para errorres
import traceback
import re

# Seguridad
from RestrictedPython  import compile_restricted
from RestrictedPython.Guards import safe_builtins



# Logica de tiempo de espera
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
    def __init__(self, browser_view,  parent=None):
        super(CodeEditor, self).__init__(parent)

        # instancias
        self.browser_url = browser_view
        self.browser_loaded = browser_view.web_view
        self.browser_loaded.loadFinished.connect(self.on_load_finished)
        self.page_load = True
        self.execution_paused = False

        # Widget del QTabWidget
        self.tab_widget = QTabWidget(self)
        self.tab_widget.installEventFilter(self)  # Instalar el filtro de eventos en el QTabWidget
        self.tab_widget.setTabsClosable(True)  # Habilitar el cierre de pestañas
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # Conectar señal de cierre de pestaña

        # Botón de "Archivo" 
        archivo_button = QPushButton("Archivo", self)
        archivo_button.clicked.connect(self.open_file_dialog)
        self.tab_widget.setCornerWidget(archivo_button, Qt.TopLeftCorner)

        # Botón de "+"
        add_tab_button = QPushButton("+", self)
        add_tab_button.clicked.connect(self.create_new_file)
        self.tab_widget.setCornerWidget(add_tab_button, Qt.TopRightCorner)


        # Configuracion de code_editer
        self.unsaved_changes = False # si se han realizado cambios sin guardar
        self.create_new_file()  # Agregar la primera pestaña por defecto
        self.error_text_edit = {}


        # Config Widget Of class code
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)




    # *****************************************************
    # *****************************************************
    # Logica de funcionamiento, busqueda, add content and click element
    # *****************************************************
    # *****************************************************

    # Esperar que la pagina termine de cargar
    def on_load_finished(self):
        print('Se a termino de cargar la pagina!')

        self.page_load = True

    # Relizar click
    def click_element(self, tag, option, content_option, tag_navigation=False, time_wait=False):
        if not self.page_load:
            # Esperar a que se complete la carga de la página antes de continuar con el código
            waitForSignal(self.browser_loaded.loadFinished)

        # navegar hacia la posicion del tag
        if tag_navigation:
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
            self.browser_loaded.page().runJavaScript(script)

        script = f"""
            var element = document.querySelector('{tag}[{option}="{content_option}"]');
            element.style.border = '3px solid red';
            element.click();
        """
        # Add content es true
        if self.actions_text_edit:
            self.actions_text_edit.append('Has hecho un click!')
            self.actions_text_edit.append('')

        # Ejecutar script
        self.browser_loaded.page().runJavaScript(script)

        # opcional si desea esperar
        if time_wait:
            if self.actions_text_edit:
                self.actions_text_edit.append('Esperando hasta que la pagina termine de cargar!')
                self.actions_text_edit.append('')
            self.page_load = False


    # Agregar contenido
    def set_content(self, tag, option, content_option, value, tag_navigation=False):
        if not self.page_load:
            # Esperar a que se complete la carga de la página antes de continuar con el código
            waitForSignal(self.browser_loaded.loadFinished)

        # navegar hacia la posicion del tag
        if tag_navigation:
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
            self.browser_loaded.page().runJavaScript(script)

        # realizar la accion
        script = f"""
            var element = document.querySelector('{tag}[{option}="{content_option}"]');
            element.style.border = '3px solid red';
            element.value = '{value}';
            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
        """

        # Agregar que se completo al agregar contenido 
        if self.actions_text_edit:
            self.actions_text_edit.append('Has Agregado un contenido!')
            self.actions_text_edit.append('')
        self.browser_loaded.page().runJavaScript(script)

    # Es esperar hasta que la pagina termine de cargar
    def load_pege_finished(self):
        if self.actions_text_edit:
            self.actions_text_edit.append('Esperando hasta que la pagina termine de cargar!')
            self.actions_text_edit.append('')
        self.page_load = False

    # Definir url para la pagina
    def set_url_for_browser(self, url, time_wait=False):
        if not self.page_load:
            # Esperar a que se complete la carga de la página antes de continuar con el código
            waitForSignal(self.browser_loaded.loadFinished)

        if self.actions_text_edit:
            self.actions_text_edit.append('Se cambio la URL del destino!')
            self.actions_text_edit.append('')

        self.browser_url.start(url)

        if time_wait:
            if self.actions_text_edit:
                self.actions_text_edit.append('Esperando hasta que la pagina termine de cargar!')
                self.actions_text_edit.append('')
            self.page_load = False

    # Navegar entre objetos
    def navigation_of_tag_or_object(self, tag, option, content_option):
        if not self.page_load:
            # Esperar a que se complete la carga de la página antes de continuar con el código
            waitForSignal(self.browser_loaded.loadFinished)

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
            self.actions_text_edit.append('Se a navegado al objeto destinado!')
            self.actions_text_edit.append('')

        self.browser_loaded.page().runJavaScript(script)


    # Ejecutar el codigo 
    def run_code(self):
        # Obtener el código del editor de la pestaña activa
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.widget(current_index)

        code_widget = current_widget.widget(0)
        code = code_widget.text()
        if not code:
            print("El código está vacío. No se ejecutará nada.")
            return
        elif code and self.unsaved_changes:
            self.save_file()
            print('con guardado!!!', code)
        else:
            print('final!!!', code)
        

        # Definir funciones y módulos permitidos
        allowed_globals = {
            'click_element': self.click_element,
            'set_content': self.set_content,
            'wait_page': self.load_pege_finished,
            'set_url': self.set_url_for_browser,
            'navigation_tag': self.navigation_of_tag_or_object,
        }

        try:
            # Agregar al widget y ajustar su tamaño
            if current_widget.widget(1) is None:
                self.actions_text_edit = QTextEdit()
                self.actions_text_edit.setReadOnly(True)
                current_widget.addWidget(self.actions_text_edit)
            elif self.actions_text_edit:
                self.actions_text_edit.setPlainText("")

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

            # Compilar el código restringido
            code_restricted = compile_restricted(code, '<string>', 'exec')
            # Ejecutar el código restringido en un entorno de ejecución personalizado
            exec(code_restricted, {'__builtins__': safe_builtins, '__name__': '__main__', **allowed_globals, '__import__': lambda x: None})
        except Exception as e:
            error_info = str(e)

            # Configuracion de mensajes
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

            # Verificar si el widget de texto de error ya existe para la pestaña actual
            if current_index in self.error_text_edit:
                error_text_edit = self.error_text_edit[current_index]
                error_text_edit.setPlainText(error_message)
            else:
                # Crear un nuevo widget de texto de error y agregarlo al layout de la pestaña actual
                error_text_edit = QTextEdit()
                error_text_edit.setPlainText(error_message)

                # Agregar al widget y ajustar su tamaño
                current_widget.addWidget(error_text_edit)
                sizes = current_widget.sizes()
                # Calcular los nuevos tamaños proporcionales
                total_size = sum(sizes)
                code_editor_size = int(total_size * 0.9)
                error_text_edit_size = total_size - code_editor_size
                # Establecer los nuevos tamaños en el QSplitter
                sizes[0] = code_editor_size
                sizes[1] = error_text_edit_size
                current_widget.setSizes(sizes)

                # Establecer los mínimos y máximos de tamaño para los widgets
                current_widget.widget(0).setMinimumHeight(int(total_size * 0.70))
                current_widget.widget(0).setMaximumHeight(code_editor_size)
                current_widget.widget(1).setMinimumHeight(error_text_edit_size)
                current_widget.widget(1).setMaximumHeight(int(total_size * 0.30))
                

                self.error_text_edit[current_index] = error_text_edit
                #error_text_edit.show()

            self.tab_widget.setCurrentIndex(current_index)
            

    # Pausar el codigo
    def pause_execution(self):
        self.execution_paused = True
        print('Ejecución pausada')



    # ******************************************
    # ******************************************
    # Acciones de editor 
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

    # Crear nuevo pestaña de codigo
    def create_new_file(self):
        self.code_editor = Qsci.QsciScintilla(self)
        self.code_editor.clear()
        self.code_editor.textChanged.connect(self.handle_text_changed)


        # Configurar opciones de resaltado de sintaxis
        lexer = Qsci.QsciLexerPython()
        lexer.setDefaultFont(self.code_editor.font())
        self.code_editor.setLexer(lexer)

        # Configurar la numeración de líneas
        self.code_editor.setMarginType(0, Qsci.QsciScintilla.NumberMargin)
        self.code_editor.setMarginWidth(0, "000")
        self.code_editor.SendScintilla(self.code_editor.SCI_SETHSCROLLBAR, 0)

        # Configuracion del widget de la pestaña
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.code_editor)
        self.tab_widget.addTab(splitter, "Nuevo archivo")

        # Obtener el índice de la pestaña recién creada
        new_tab_index = self.tab_widget.count() - 1
        self.tab_widget.setCurrentIndex(new_tab_index)




    # Cerrar pestaña de codigo
    def close_tab(self, index):
        tab_widget_item = self.tab_widget.widget(index)
        if tab_widget_item is not None:
            if self.unsaved_changes:
                # Mostrar un cuadro de diálogo de confirmación
                reply = QMessageBox.question(self, "Cambios no guardados", "El archivo ha sido modificado. ¿Desea guardar los cambios?",
                                             QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                if reply == QMessageBox.Save:
                    self.save_file()
                    self.event_close_tab(index, tab_widget_item)
                elif reply == QMessageBox.Discard:
                    self.event_close_tab(index, tab_widget_item)
                elif reply == QMessageBox.Cancel:
                    return  # Cancelar el cierre de la pestaña
            else:
                # Emitir el evento QEvent.Close manualmente al widget de la pestaña
                self.event_close_tab(index, tab_widget_item)

        # Verificar si la pestaña actual se cerró
        if index != self.tab_widget.currentIndex():
            updated_index = self.tab_widget.currentIndex()
        else:
            updated_index = index - 1 if index > 0 else 0

        if self.tab_widget.count() == 0:  # Si no hay más pestañas abiertas
            self.create_new_file()

        # Establecer el índice actualizado
        self.tab_widget.setCurrentIndex(updated_index)

    def close_all_tabs(self):
        num_tabs = self.tab_widget.count()
        for i in range(num_tabs):
            self.close_tab(0)

    def event_close_tab(self, index, tab_widget_item):
        # Emitir el evento QEvent.Close manualmente al widget de la pestaña
        close_event = QEvent(QEvent.Close)
        QCoreApplication.postEvent(tab_widget_item, close_event)

        # Eliminar el widget de code_edit
        current_widget = self.tab_widget.widget(index)
        code_widget = current_widget.widget(0)
        code_widget.deleteLater()
        # Eliminamos el widget de error_text_edit
        if index in self.error_text_edit:
            error_text_edit = self.error_text_edit[index]
            error_text_edit.deleteLater()
            del self.error_text_edit[index]

        # Eliminamos la pestaña
        self.tab_widget.removeTab(index) 



    # Widget de open_file
    def open_file_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Archivos Python (*.py)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setDirectory(QDir.homePath())
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            for file in selected_files:
                self.open_file(file)

    def open_file(self, file_path):
        # Verificar si el archivo ya está abierto en una pestaña
        for index in range(self.tab_widget.count()):
            tab_widget_item = self.tab_widget.widget(index)
            if tab_widget_item.property("file_path") == file_path:
                # Seleccionar la pestaña existente
                self.tab_widget.setCurrentIndex(index)
                return
                
        # Extraer el nombre del archivo de la ruta completa
        file_name = QFileInfo(file_path).fileName()

        # Widget del editor de código para la nueva pestaña
        # Llamar al método create_new_file para crear una nueva pestaña
        self.create_new_file()

        # Obtener el código del archivo y establecerlo en el editor de código de la nueva pestaña
        with open(file_path, 'r') as file:
            self.code_editor.setText(file.read())

        # Establecer el título de la nueva pestaña como el nombre del archivo
        new_tab_index = self.tab_widget.count() - 1
        self.tab_widget.setTabText(new_tab_index, file_name)

        # Posicionar y hacer visible la pestaña recién agregada
        self.tab_widget.setCurrentIndex(new_tab_index)
        self.tab_widget.setCurrentWidget(self.code_editor)

        # Establecer la propiedad "file_path" en el widget de la pestaña
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.widget(current_index)

        current_widget.setProperty("file_path", file_path)

        


    # Guardar codigo
    def save_file(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            current_widget = self.tab_widget.widget(current_index)
            code_widget = current_widget.widget(0)

            # Verificar si el archivo asociado a la pestaña actual
            file_path = current_widget.property("file_path")
            file_name = QFileInfo(file_path).fileName()
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(code_widget.text())
                self.unsaved_changes = False
                self.tab_widget.setTabText(current_index, file_name)  # Eliminar el indicador "*"
            else:
                # Si el archivo no existe, llamar al método save_file_as
                self.save_file_as()
        
        if self.unsaved_changes:
            # Volver a conectar la señal textChanged para seguir rastreando los cambios sin guardar
            self.code_editor.textChanged.connect(self.handle_text_changed)


    def save_file_as(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            current_widget = self.tab_widget.widget(current_index)
            code_widget = current_widget.widget(0)
            file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", QDir.homePath(), "Archivos Python (*.py)")
            file_name = QFileInfo(file_path).fileName()
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(code_widget.text())
                current_widget.setProperty("file_path", file_path)  # Actualizar la propiedad "file_path"
                self.unsaved_changes = False
                self.tab_widget.setTabText(current_index, file_name)  # Eliminar el indicador "*"




    # *****************************************************
    # *****************************************************
    # Eventos 
    # *****************************************************
    # *****************************************************

    # En save verirfica si hay cambios ese aparece el evento de que tiene que guardar
    def handle_text_changed(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            current_widget = self.tab_widget.widget(current_index)
            current_widget.setProperty("modified", True)
            self.unsaved_changes = True

            # Actualizar el título de la pestaña para reflejar los cambios sin guardar
            file_name = self.tab_widget.tabText(current_index)
            if "*" not in file_name:
                self.tab_widget.setTabText(current_index, file_name + " *")

    # Eventos del teclado
    def eventFilter(self, obj, event):
        if obj is self.tab_widget and event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.LeftButton:
                # Verificar si hay un QLineEdit activo y desactivar su enfoque
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
                    # Crear un QLineEdit para editar el nombre de la pestaña
                    line_edit = QLineEdit(self.tab_widget.tabText(tab_index))
                    # Obtener el nuevo nombre del QLineEdit
                    new_text = line_edit.text()
                    line_edit.selectAll()
                    line_edit.editingFinished.connect(lambda: self.update_tab_text(tab_index, line_edit.text()))
                    self.tab_widget.tabBar().setTabButton(tab_index, QTabBar.LeftSide, line_edit)
                    line_edit.setFocus()

                    # Deshabilitar el texto de la pestaña mientras se edita
                    self.tab_widget.setTabText(tab_index, "")

                    def finish_editing():
                        # Obtener el nuevo nombre del QLineEdit
                        new_text = line_edit.text()

                        # Si el nuevo texto es una cadena vacía, se restaura el contenido anterior
                        if new_text == "":
                            new_text = previous_text

                        # Actualizar el texto de la pestaña si ha habido cambios
                        if new_text != self.tab_widget.tabText(tab_index):
                            self.tab_widget.setTabText(tab_index, new_text)

                        # Remover el QLineEdit si aún existe
                        if line_edit is not None:
                            self.tab_widget.tabBar().setTabButton(tab_index, QTabBar.LeftSide, None)

                    line_edit.editingFinished.connect(finish_editing)

                    def focus_out_event(event):
                        # Al perder el foco, se finaliza la edición sin cambios
                        finish_editing()

                    line_edit.focusOutEvent = focus_out_event

                    return True
        elif isinstance(obj, QTabWidget) and event.type() == QEvent.Close:
            # Se está cerrando una pestaña, finalizar la edición del QLineEdit si está activo
            line_edit = self.tab_widget.tabBar().tabButton(self.tab_widget.currentIndex(), QTabBar.LeftSide)
            if isinstance(line_edit, QLineEdit):
                if line_edit is not None:
                    line_edit.editingFinished.emit()  # Emitir la señal de finalización de edición

    

        return super().eventFilter(obj, event)

    def update_tab_text(self, tab_index, new_text):
        self.tab_widget.setTabText(tab_index, new_text)



"""
def handle_modification_changed(self, changed):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            current_widget = self.tab_widget.widget(current_index)
            current_widget.setProperty("modified", changed)

            # Actualizar el título de la pestaña para reflejar los cambios sin guardar
            file_name = self.tab_widget.tabText(current_index)
            if changed:
                self.tab_widget.setTabText(current_index, file_name + " *")
            else:
                self.tab_widget.setTabText(current_index, file_name)
"""


"""
def handle_modification_changed(self, changed):
        print('Hay cambios sin guardar!!!')
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            current_widget = self.tab_widget.widget(current_index)
            current_widget.setProperty("modified", changed)

            # Actualizar el título de la pestaña para reflejar los cambios sin guardar
            file_name = self.tab_widget.tabText(current_index)

            if "*" in file_name and not changed:
                # Eliminar el indicador "*" si existe y no hay cambios sin guardar
                self.tab_widget.setTabText(current_index, file_name[:-2])
            elif "*" not in file_name and changed:
                # Agregar el indicador "*" si no existe y hay cambios sin guardar
                self.tab_widget.setTabText(current_index, file_name + " *")
"""



"""
ef create_new_file(self):
        self.code_editor = Qsci.QsciScintilla(self)
        self.code_editor.clear()
        self.code_editor.textChanged.connect(self.handle_text_changed)

        # Configuracion del widget de la pestaña
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.code_editor)
        self.tab_widget.addTab(splitter, "Nuevo archivo")


        # Asignar atajo de teclado para activar el autocompletado (por ejemplo, Ctrl+Espacio)
        self.code_editor.SendScintilla(Qsci.QsciScintilla.SCI_ASSIGNCMDKEY, Qt.CTRL + Qt.Key_Space, Qsci.QsciScintilla.SCI_AUTOCCOMPLETE)

        # Conectar la señal de autocompletado a una ranura personalizada
        self.code_editor.userListActivated.connect(self.handle_autocomplete_menu_action)

        # Crear menú contextual para el autocompletado
        self.autocomplete_menu = QMenu(self.code_editor)
        self.code_editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.code_editor.customContextMenuRequested.connect(self.show_autocomplete_menu)

        # Configurar las opciones del autocompletado
        self.autocomplete_options = [
            "click_element('tag', 'attribute', 'value_attribute')",
            "set_content('tag', 'attribute', 'value_attribute', 'add_content')",
            "wait_page()",
            "set_url('url', time_wait=False)",
            "navigation_tag('tag', 'attribute', 'value_attribute')"
        ]

    def show_autocomplete_menu(self, position):
        # Obtener la posición global del clic derecho en el editor de código
        global_position = self.code_editor.mapToGlobal(QPoint(position.x(), position.y()))
        # Obtener el texto actual en la posición del cursor
        current_text = self.code_editor.text(self.code_editor.positionFromLineIndex(position.y(), position.x()))
        # Filtrar las opciones de autocompletado que coinciden con el texto actual
        filtered_options = [option for option in self.autocomplete_options if option.startswith(current_text)]
        if filtered_options:
            # Limpiar el menú contextual existente
            self.autocomplete_menu.clear()
            for option in filtered_options:
                # Crear una acción para cada opción de autocompletado
                action = QAction(option, self.code_editor)
                self.autocomplete_menu.addAction(action)
            # Conectar la señal triggered de las acciones al manejador
            self.autocomplete_menu.triggered.connect(self.handle_autocomplete_menu_action)
            # Mostrar el menú contextual en la posición global del clic derecho
            self.autocomplete_menu.exec_(global_position)

    def handle_autocomplete_menu_action(self, action):
        # Obtener el texto de la acción seleccionada
        selected_text = action.text()
        # Obtener la posición del cursor actual
        cursor_position = self.code_editor.getCursorPosition()
        # Insertar el texto seleccionado en la posición del cursor
        self.code_editor.insert(selected_text)
"""