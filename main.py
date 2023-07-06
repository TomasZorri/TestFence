# For ui
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Import layout
from layout.htmlview import MainHtmlView
from layout.browserview import BrowserView ,BrowserNavegacion
from layout.navview import NavMenu
from layout.codeview import CodeEditor
from layout.dberrorview import DBError


# Import data
from model import *




class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Importar logic
        self.init_database()
        self.init_ui()

    def init_database(self):
        engine = create_engine('sqlite:///database.db')
        Base.metadata.create_all(bind=engine)
        self.session = Session(bind=engine)

    def init_ui(self):
        self.html_view = MainHtmlView()
        self.browser_view = BrowserView(self.html_view)
        self.code_view = CodeEditor(self.browser_view, self.session)
        self.brower_nav = BrowserNavegacion(self.browser_view, parent=self)
        self.dberror_view = DBError(self.session)
        self.navmenu_view = NavMenu(self.browser_view, self.code_view, self.close_application, self.dberror_view)

        
        # Set the layout of the main window
        browser_widget = QWidget()
        browser_layout = QVBoxLayout()
        browser_layout.addWidget(self.brower_nav, 5)
        browser_layout.addWidget(self.browser_view, 95)
        browser_widget.setLayout(browser_layout)

        # content layout
        content_layout = QSplitter(Qt.Horizontal)
        content_layout.addWidget(self.code_view)
        content_layout.addWidget(browser_widget)
        content_layout.addWidget(self.html_view)
        content_layout.addWidget(self.dberror_view)
        sizes = content_layout.sizes()
        total_size = sum(sizes)
        #content_layout.setSizes([2, 6, 2])
        # Minimos
        #content_layout.widget(0).setMinimumWidth(int(total_size * 0.15))
        #content_layout.widget(1).setMinimumWidth(int(total_size * 0.70))
        #content_layout.widget(2).setMinimumWidth(int(total_size * 0.15))
        # Maximos
        #content_layout.widget(0).setMaximumWidth(int(total_size * 0.25))
        #content_layout.widget(1).setMaximumWidth(int(total_size * 0.50))
        #content_layout.widget(2).setMaximumWidth(int(total_size * 0.25))


        # final layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.navmenu_view, 3)
        main_layout.addWidget(content_layout, 97)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
                
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.showMaximized()

        # Configuration of the title
        self.setWindowTitle("TestFence")
        self.setWindowIcon(QIcon("img/main.png"))

    def close_application(self):
        self.close() # close the application

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
 