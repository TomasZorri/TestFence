import sys
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QListWidgetItem, QListWidget, QMenu, QPlainTextEdit, QComboBox)

from bs4 import BeautifulSoup


# Configuracion de ventana para add code automatizion
class set_code_of_tag(QWidget):
    def __init__(self, selected_text):
        super().__init__()

        self.tag_edit = QPlainTextEdit(selected_text)
        self.code_edit = QPlainTextEdit()
        self.copy_button = QPushButton("Copiar código")
        self.copy_button.clicked.connect(self.copy_code)

        self.function_selection = QComboBox()
        self.function_selection.addItem("Seleccionar un Código")  # Valor nulo
        self.function_selection.addItem("Obtener código de acciónes(Click)")
        self.function_selection.addItem("Obtener código de contenido(Para agregar contenidos)")
        self.function_selection.currentIndexChanged.connect(self.update_code)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tag_edit)
        layout.addWidget(self.function_selection)
        layout.addWidget(self.code_edit)
        layout.addWidget(self.copy_button)

        self.update_code()

    def update_code(self):
        tag = self.tag_edit.toPlainText()
        function_index = self.function_selection.currentIndex()

        if function_index != 0 and tag is not None:
            if function_index == 1:
                code = self.get_click_element_code(tag)
            else:
                code = self.get_set_content_code(tag)

            self.code_edit.setPlainText(code) 

    def get_click_element_code(self, tag):
        return self.transform_tag_to_code(tag, function='click_element', content='')

    def get_set_content_code(self, tag):
        return self.transform_tag_to_code(tag, function='set_content', content=", 'Ingresar_Contenido'")

    def transform_tag_to_code(self, tag, function, content):
        soup = BeautifulSoup("<html><body>{}</body></html>".format(tag), 'html.parser')
        tag_element = soup.body.contents[0]
        tag_name = tag_element.name
        if tag_element.get('class'):
            class_name = tag_element.get('class')[0]
            return "{}('{}', 'class', '{}'{})".format(function, tag_name, class_name, content)
        elif tag_element.get('id'):
            id_value = tag_element.get('id')
            return "{}('{}', 'id', '{}'{})".format(function, tag_name, id_value, content)
        elif tag_element.get('path'):
            path_value = tag_element.get('path')
            return "{}('{}', 'path', '{}'{})".format(function, tag_name, path_value, content)
        elif tag_element.get('name'):
            name_value = tag_element.get('name')
            return "{}('{}', 'name', '{}'{})".format(function, tag_name, name_value, content)
        elif tag_element.get('value'):
            value_value   = tag_element.get('value')
        else:
            return "{}('{}', 'attribute', 'attribute_value'{})".format(function, tag_name)


    # Copiar el codigo 
    def copy_code(self):
        code = self.code_edit.toPlainText()
        if code:
            clipboard = QApplication.clipboard()
            mime_data = QMimeData()
            mime_data.setText(code)
            clipboard.setMimeData(mime_data)




# Configuraion de ventana de select tag y seach 
class SearchWidget(QWidget):
    def __init__(self, text_edit):
        super().__init__()

        self.text_edit = text_edit

        # Navegacion
        search_bar_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search)
        search_bar_layout.addWidget(self.search_bar)
        self.search_button = QPushButton('Buscar')
        self.search_button.clicked.connect(self.search)
        search_bar_layout.addWidget(self.search_button)
        # Texto de busqueda bloque
        self.search_result_list = QListWidget()
        self.search_result_list.setContextMenuPolicy(Qt.CustomContextMenu)  # Activar la opción de menú contextual
        self.search_result_list.customContextMenuRequested.connect(self.show_context_menu)  # Conectar la señal

        # Seleccion de Tag
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)  # Activar la opción de menú contextual
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)  # Conectar la señal
        self.list_widget.setVisible(False)

        # Configuracion bloque de search y select item
        layout = QVBoxLayout()
        layout.addLayout(search_bar_layout)
        layout.addWidget(self.search_result_list)
        self.layout_widget = QWidget()
        self.layout_widget.setLayout(layout)
        self.layout_widget.hide()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.layout_widget)
        main_layout.addWidget(self.list_widget)
        self.setLayout(main_layout)


    # Agregar items a list_widget
    def update_results(self, result):
        # Actualizar los resultados en el QListWidget
        self.list_widget.clear()
        list_item = QListWidgetItem(result)
        list_item.setFlags(list_item.flags() | Qt.ItemIsEditable)  # Permitir edición
        self.list_widget.addItem(list_item)


    # Menu Conceptual
    def show_context_menu(self, position):

        sender_widget = self.sender()  # Obtener el objeto sender

        selected_items = sender_widget.selectedItems()

        if not selected_items:
            return
        
        menu = QMenu()
        copy_action = menu.addAction("Copiar")
        edit_action = menu.addAction("Editar")
        code_action = menu.addAction("Add Code")

        action = menu.exec_(sender_widget.mapToGlobal(position))
        if action == copy_action:
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_items[0].text())
        elif action == edit_action:
            # Simular doble clic en el elemento seleccionado
            item_to_edit = selected_items[0]
            sender_widget.editItem(item_to_edit)
        elif action == code_action:
            self.popup = set_code_of_tag(selected_items[0].text())
            self.popup.show()


    # Configuracion de busqueda
    def search(self):
        # Primera que es etiqueta
        search_label = self.search_bar.text().split(';')[0].strip()
        # Segunda que es el method
        search_option = ''
        search_text = ''
        if ';' in self.search_bar.text() and ':' in self.search_bar.text().split(';')[1]:
            search_option = self.search_bar.text().split(';')[1].split(':')[0].strip().lower()
            search_text = self.search_bar.text().split(';')[1].split(':')[1].strip().replace('"', '')#.upper()
        elif ';' in self.search_bar.text():
            search_option = self.search_bar.text().split(';')[1].strip().replace('"', '')



        # Realizar la búsqueda
        html_code = self.text_edit.toPlainText()
        search_result = self.search_html_code(html_code, search_label, search_option, search_text)

        # Mostrar y Convertir el resultado en una lista de items
        self.search_result_list.clear()
        for item in search_result.split('\n'):
            list_item = QListWidgetItem(item)
            list_item.setFlags(list_item.flags() | Qt.ItemIsEditable)  # Permitir edición
            self.search_result_list.addItem(list_item)

    def search_html_code(self, html_code, search_label, search_option=None, search_text=None):
        search_result = ''
        tag_start = 0

        # Buscar por etiqueta si no se especifica un atributo de búsqueda
        while True:
            tag_start = html_code.find('<' + search_label, tag_start)
            if tag_start == -1:
                break
            tag_end = html_code.find('>', tag_start)
            tag = html_code[tag_start:tag_end+1]

            if search_option:
                if f'{search_option}="' + search_text + '"' in tag:
                    search_result += tag + '\n'
                elif not search_text and search_option:
                    if f'{search_option}="' in tag:
                        search_result += tag + '\n'
            else:
                search_result += tag + '\n'

            tag_start = tag_end + 1

        return search_result




class MainHtmlView(QWidget):
    def __init__(self, parent=None):
        super(MainHtmlView, self).__init__(parent)
        #self.setReadOnly(True)
        self.hide()

        # Crear el widget contenedor principal
        main_layout = QVBoxLayout()

        # Primer bloque: Barra de navegación
        nav_bar_layout = QHBoxLayout()
        main_layout.addLayout(nav_bar_layout)

        self.search_button = QPushButton('Buscar')
        self.search_button.clicked.connect(self.show_search_block)
        nav_bar_layout.addWidget(self.search_button)
        self.search_block_visible = False

        self.organize_button = QPushButton('Organizar')
        self.organize_button.clicked.connect(self.organize_html_tags)
        nav_bar_layout.addWidget(self.organize_button)

        self.selcet_tag_view_button = QPushButton('select items')
        self.selcet_tag_view_button.clicked.connect(self.view_select_tag)
        nav_bar_layout.addWidget(self.selcet_tag_view_button)
        self.selecttag_block_visible = False

        self.close_button = QPushButton('X')
        self.close_button.clicked.connect(self.hide) 
        nav_bar_layout.addWidget(self.close_button)

        # Segundo bloque: Contenido HTML
        self.text_edit = QTextEdit(self)
        main_layout.addWidget(self.text_edit)

        # Tercer bloque: Resultados de búsqueda (oculto)
        self.search_widget = SearchWidget(self.text_edit)
        self.search_widget.hide()
        main_layout.addWidget(self.search_widget)

        # Subir configuracion
        self.setLayout(main_layout)

        #self.setStyleSheet("background-color: white; color: black;")
        # Configuracion del sitio // Habilitar teclado rapido
        self.setFocusPolicy(Qt.StrongFocus)


    # Select Item Config
    def set_select_tag(self, tag):
        self.list_widget = tag
        if self.search_widget:
             self.search_widget.update_results(self.list_widget)

    def view_list_select_tag(self, view_select_tag=False):
        if view_select_tag:
            self.show()
            self.search_widget.show()
            self.search_widget.list_widget.setVisible(True)
        else:
            self.search_widget.list_widget.setVisible(False)

    def view_select_tag(self):
        self.selecttag_block_visible = not self.selecttag_block_visible

        if self.selecttag_block_visible:
            self.search_widget.list_widget.setVisible(True)

            if not self.search_block_visible:
                self.search_widget.show()
        else:
            self.search_widget.list_widget.setVisible(False)

            if not self.search_block_visible:
                self.search_widget.hide()
    

    def show_search_block(self):
        self.search_block_visible = not self.search_block_visible

        if self.search_block_visible:
            self.search_widget.layout_widget.show()

            if not self.selecttag_block_visible:
                self.search_widget.show()
        else:
            self.search_widget.layout_widget.hide()

            if not self.selecttag_block_visible:
                self.search_widget.hide()


    # Obtener el codigo Html
    def set_html(self, html):
        self.text_edit.setPlainText(html)

    # Ordenar el HTML
    def organize_html_tags(self):
        # Obtener el texto actual del widget QTextEdit
        html_code = self.text_edit.toPlainText()

        # Parsear el código HTML con BeautifulSoup
        soup = BeautifulSoup(html_code, 'html.parser')

        # Obtener el código HTML reorganizado
        organized_html = soup.prettify()

        # Establecer el texto organizado en el widget QTextEdit
        self.text_edit.setPlainText(organized_html)
    

    # Eventos de teclas repidas
    def keyPressEvent(self, event):
        # Evento para ocultar la vista de html
        if event.key() == Qt.Key_Escape and self.isVisible():
            print('hola')
            #self.search_button.setFocus()
            #self.setFocusPolicy(Qt.NoFocus)
            self.hide()
        else:
            super().keyPressEvent(event)

