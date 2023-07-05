## For Ui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt


## database
import sys
sys.path.append('..')
from model import ErrorEntry

class DBError(QWidget):
    def __init__(self, session, parent=None):
        super(DBError, self).__init__(parent)

        self.session = session
        # Crear el widget principal
        self.widget = QWidget(self)
        layout = QVBoxLayout(self.widget)

        # Agregar el título
        title_label = QLabel("Error Details")
        layout.addWidget(title_label)

        # Agregar la tabla
        table_widget = QTableWidget(self)
        table_widget.setColumnCount(8)
        table_widget.setHorizontalHeaderLabels(['ID', 'Status', 'Title', 'Pasos', 'Mensaje', 'Resultados Esperados', 'Resultados Obtenidos', 'Fecha'])
        layout.addWidget(table_widget)


        # Obtener los registros de la tabla ErrorEntry
        error_entries = self.session.query(ErrorEntry).all()

        # Agregar los registros a la tabla
        for row, entry in enumerate(error_entries):
            table_widget.insertRow(row)
            table_widget.setItem(row, 0, QTableWidgetItem(str(entry.id)))
            table_widget.setItem(row, 1, QTableWidgetItem(entry.status))
            table_widget.setItem(row, 2, QTableWidgetItem(entry.title))
            table_widget.setItem(row, 3, QTableWidgetItem(entry.pasos_reproducir))
            table_widget.setItem(row, 4, QTableWidgetItem(entry.mensaje_error))
            table_widget.setItem(row, 5, QTableWidgetItem(entry.resultados_esperados))
            table_widget.setItem(row, 6, QTableWidgetItem(entry.resultados_obtenidos))
            table_widget.setItem(row, 7, QTableWidgetItem(str(entry.error_date)))

        # Agregar el widget principal al diseño del widget
        self.setLayout(layout)
        self.hide()


    def view_dberror(self):
        self.show()
