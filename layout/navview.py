from PyQt5.QtWidgets import QMainWindow, QAction
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt



class NavMenu(QMainWindow):
    def __init__(self, browser_view, code_view, close_application, dberror_view):
        super(NavMenu, self).__init__()

        # Crear instancias
        self.browser_view = browser_view
        self.code_view = code_view
        self.close_application = close_application
        self.dberror_view = dberror_view
        main_menu = self.menuBar()
        main_menu.setStyleSheet("QMenuBar { margin: 0px; padding: 0px; }")


        # # Configuracion de menu de archivo
        file_menu = main_menu.addMenu("File")
        new_action = QAction("New File", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.code_view.create_new_file)

        open_action = QAction("Open File", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.code_view.open_file_dialog)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.code_view.save_file)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.code_view.save_file_as)

        # Close action
        close_action = QAction("Close File", self)
        close_action.setShortcut(QKeySequence("Ctrl+W"))
        close_action.triggered.connect(self.code_view.close_tab)

        close_all_file_action = QAction("Close All File", self)
        close_all_file_action.triggered.connect(self.code_view.close_all_tabs)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(close_action)
        file_menu.addAction(close_all_file_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)


        # Opciones de Edit
        edit_menu = main_menu.addMenu("Edit")
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.code_view.undo_accion)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.code_view.redo_accion)

        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.code_view.cut_accion)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.code_view.copy_accion)

        copy_as_html_action = QAction("Copy as HTML", self)
        copy_as_html_action.triggered.connect(self.redo)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.code_view.paste_accion)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)




        tools_menu = main_menu.addMenu("Tools")
        # Botton para seleccionar items
        extract_tags_action = QAction("Extract Tags", self)
        extract_tags_action.setShortcut(QKeySequence("Ctrl+E"))
        extract_tags_action.triggered.connect(self.browser_view.activate_select_mode)

        view_db_action = QAction("View Data Base", self)
        view_db_action.triggered.connect(self.dberror_view.view_dberror)

        # Configuracion de Boton para Ejecutar y pausar el codigo
        run_code_action = QAction("run code", self)
        run_code_action.setShortcut(QKeySequence("Ctrl+B"))
        run_code_action.triggered.connect(self.code_view.run_code)

        stop_code_action = QAction("stop code", self)
        stop_code_action.triggered.connect(self.code_view.pause_execution)



        tools_menu.addAction(extract_tags_action)
        tools_menu.addAction(view_db_action)
        tools_menu.addSeparator()
        tools_menu.addAction(run_code_action)
        tools_menu.addAction(stop_code_action)

    

    # dentro de una lista de item para un item central
    def redo(self):
        print("Redoing last action...")

