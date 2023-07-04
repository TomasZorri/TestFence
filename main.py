import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Import partes
from layout.htmlview import MainHtmlView
from layout.browserview import BrowserView ,BrowserNavegacion
from layout.navview import NavMenu
from layout.codeview import CodeEditor


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.html_view = MainHtmlView()
        self.browser_view = BrowserView(self.html_view)
        self.code_view = CodeEditor(self.browser_view)
        self.brower_nav = BrowserNavegacion(self.browser_view, parent=self)
        self.navmenu_view = NavMenu(self.browser_view, self.code_view, self.close_application)

        
        # Configurar el layout de la ventana principal
        browser_widget = QWidget()
        browser_layout = QVBoxLayout()
        browser_layout.addWidget(self.brower_nav, 5)
        browser_layout.addWidget(self.browser_view, 95)
        browser_widget.setLayout(browser_layout)

        # layout de contenido
        content_layout = QSplitter(Qt.Horizontal)
        content_layout.addWidget(self.code_view)
        content_layout.addWidget(browser_widget)
        content_layout.addWidget(self.html_view)
        sizes = content_layout.sizes()
        total_size = sum(sizes)
        content_layout.setSizes([2, 6, 2])
        # Minimos
        #content_layout.widget(0).setMinimumWidth(int(total_size * 0.15))
        #content_layout.widget(1).setMinimumWidth(int(total_size * 0.70))
        #content_layout.widget(2).setMinimumWidth(int(total_size * 0.15))
        # Maximos
        #content_layout.widget(0).setMaximumWidth(int(total_size * 0.25))
        #content_layout.widget(1).setMaximumWidth(int(total_size * 0.50))
        #content_layout.widget(2).setMaximumWidth(int(total_size * 0.25))


        # Layout final
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.navmenu_view, 3)
        main_layout.addWidget(content_layout, 97)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
                
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.showMaximized()

        # Configuracion del titulo 
        self.setWindowTitle("TestFence")
        self.setWindowIcon(QIcon("img/main.png"))

    def close_application(self):
        # Cerrar la aplicación
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
