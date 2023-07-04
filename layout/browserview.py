import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl, QPoint, QDateTime
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
    QLineEdit, QMenu)
from PyQt5.QtWebEngineCore import QWebEngineHttpRequest
from PyQt5.QtNetwork import QNetworkCookie

import requests

class BrowserNavegacion(QWidget):
    """docstring for NavView"""
    def __init__(self, browser_view, parent=None):
        super(BrowserNavegacion, self).__init__(parent)

        # Instancias
        self.browser_view = browser_view

        # Barra para introducir la URL y Boton de envio
        self.url_bar = QLineEdit(self)
        self.url_bar.returnPressed.connect(self.load_url)

        self.load_button = QPushButton('Cargar', self)
        self.load_button.clicked.connect(self.load_url)

        # Crea un botón de retroceso
        self.back_button = QPushButton(self)
        self.back_button.setIcon(QIcon("../../img/icon/back.png"))
        self.back_button.clicked.connect(self.browser_view.web_view.back)

        # Crea un botón de avance
        self.forward_button = QPushButton(self)
        self.forward_button.setIcon(QIcon("../../img/icon/forward.png"))  
        self.forward_button.clicked.connect(self.browser_view.web_view.forward)

        # Crea un botón de recarga
        self.reload_button = QPushButton(self)
        self.reload_button.setIcon(QIcon("../../img/icon/refresh.png"))
        self.reload_button.clicked.connect(self.browser_view.web_view.reload)


        # Crea un layout horizontal para la barra de direcciones y los botones
        layout = QHBoxLayout()
        layout.addWidget(self.back_button)
        layout.addWidget(self.forward_button)
        layout.addWidget(self.reload_button)
        layout.addWidget(self.url_bar)
        layout.addWidget(self.load_button)
        self.setLayout(layout)


    def load_url(self):
        url = self.url_bar.text()
        #qurl = QUrl(url)
        #self.browser.webview.load(qurl)
        self.browser_view.start(url)



class BrowserView(QWidget):
    def __init__(self, html_view, parent=None):
        super(BrowserView, self).__init__(parent)

        # Instancias y objetos
        self.html_view = html_view
        self.web_view = QWebEngineView(self)

        # Configuracion de la vista
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.web_view, 5)
        self.setLayout(main_layout)

        # Configuracion del modo de seleccion y Teclas rapidas
        self.select_mode = False
        self.setFocusPolicy(Qt.StrongFocus)

        # Configurar el menú contextual
        self.web_view.setContextMenuPolicy(Qt.NoContextMenu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)


        ##### Cooking #####

        # Configuracion de la cooking
        self.cookie_store = self.web_view.page().profile().cookieStore()
        # Obtener la URL actual de la página web
        current_url = self.web_view.page().url()

        # Configurar las cookies
        cookie_name = "cookie_name".encode()
        cookie_value = "cookie_value".encode()
        cookie = QNetworkCookie(cookie_name, cookie_value)
        cookie.setHttpOnly(True)
        cookie.setSecure(True)
        cookie.setExpirationDate(QDateTime.currentDateTime().addDays(30))
        # Establecer SameSite
        raw_cookie = cookie.toRawForm(QNetworkCookie.NameAndValueOnly)
        raw_cookie += b"; SameSite=None"
        raw_cookie += b"; Secure"
        cookie.setValue(raw_cookie)
        #self.cookie_store.setCookie(cookie, current_url)

        # Enviar la petición con la cookie
        current_url_string = current_url.toString()
        #print(current_url_string, type(current_url_string))
        if current_url_string:
            response = requests.get(current_url_string, cookies={cookie_name.decode(): cookie_value.decode()})

            # Verificar si la cookie se envió correctamente
            if response.cookies.get(cookie_name.decode()):
                print("La cookie se envió correctamente")
            else:
                print("Error al enviar la cookie")

        self.web_view.loadFinished.connect(self.handleLoadFinished)

    # Obtener Url y pasarlo a la vista
    def start(self, url):
        request = QWebEngineHttpRequest(QUrl(url))
        self.web_view.load(request)

    # Enviar el codigo de Html
    def handleLoadFinished(self):
        self.web_view.page().toHtml(self.showHtml)
    def showHtml(self, html):
        self.html_view.set_html(html)

    # Envento de Modo de seleccion de Tag
    def activate_select_mode(self):
        if not self.select_mode:
            # Desactivar eventos del sitio y cambiar el evento del mause
            self.select_mode = True
            self.html_view.view_list_select_tag(view_select_tag=True)
            self.setCursor(Qt.CrossCursor)
            self.web_view.setEnabled(False)
            self.web_view.page().contentsMousePressEvent = self.mousePressEvent
        else:
            # Volver a activar eventos de clic y teclado
            self.select_mode = False
            self.unsetCursor()
            self.web_view.setEnabled(True)
            self.web_view.page().contentsMousePressEvent = None
            # Ejecutar una función de JavaScript para remover el borde rojo del elemento seleccionado
            script = """
                var elements = document.querySelectorAll("[style='border: 3px solid red;']");
                for (var i = 0; i < elements.length; i++) {
                    elements[i].style.border = "";
                }
            """
            self.web_view.page().runJavaScript(script)

    
    # Evento para que funcione y seleccine dicha logica
    def mousePressEvent(self, event):
        if self.select_mode:
            # Obtener y calcualar la posicion del ratón actual
            position = event.pos()
            scroll_pos = self.web_view.page().scrollPosition()
            absolute_pos = QPoint(int(position.x() + scroll_pos.x()), int(position.y() + scroll_pos.y() - 15))
            # Remover el borde anterior
            script_remove_border = """
                var elements = document.querySelectorAll("[style='border: 3px solid red;']");
                for (var i = 0; i < elements.length; i++) {
                    elements[i].style.border = "";
                }
            """
            self.web_view.page().runJavaScript(script_remove_border)
            # Añadir un nuevo borde y obterer etiqueta
            script = f"""
                var element = document.elementFromPoint({absolute_pos.x()}, {absolute_pos.y()});
                element.style.border = '3px solid red';
                element.outerHTML;
            """
            self.web_view.page().runJavaScript(script, self.handle_selected_element)
        else:
            super(BrowserView, self).mousePressEvent(event)


    # Enviar dicho resultado al text
    def handle_selected_element(self, result):
        if result:
            self.html_view.set_select_tag(result)
        else:
            pass

    # Configuracion del Menu Contextual
    def show_context_menu(self, position):
        menu = QMenu()
        # Configuracion de Page
        back_page_action = menu.addAction(QIcon("../../img/icon/back.png"), "Back Page")
        forward_page_action = menu.addAction(QIcon("../../img/icon/forward.png"), "Forward Page")
        reload_page_action = menu.addAction(QIcon("../../img/icon/refresh.png"), "Reload page")
        # Agrega separador
        separator_action = menu.addSeparator()
        # View Code 
        view_page_source_action = menu.addAction("View Page Source")

        menu.addAction(back_page_action)
        menu.addAction(forward_page_action)
        menu.addAction(reload_page_action)
        menu.addAction(separator_action)
        menu.addAction(view_page_source_action)

        # Configurar las acciones de los botones
        back_page_action.triggered.connect(self.web_view.back)
        forward_page_action.triggered.connect(self.web_view.forward)
        reload_page_action.triggered.connect(self.web_view.reload)
        view_page_source_action.triggered.connect(self.html_view.show)

        action = menu.exec_(self.mapToGlobal(position))




    # Si el modo esta activo con escape sale pero antes debera seleccionar un objeto
    def keyPressEvent(self, event):
        # Evento de modo de seleccion de tag
        if event.key() == Qt.Key_Escape and self.select_mode:
            self.activate_select_mode()
        else:
            super().keyPressEvent(event)



