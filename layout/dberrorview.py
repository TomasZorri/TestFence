## For Ui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


## database
import sys
sys.path.append('..')
from model import ErrorEntry

class DBError(QWidget):
    def __init__(self, session, parent=None):
        super(DBError, self).__init__(parent)

        self.session = session
        # Create the main widget
        self.widget = QWidget(self)
        layout = QVBoxLayout(self.widget)

        # Add the title and buttons
        title_layout = QHBoxLayout()
        title_label = QLabel("Error Details")
        title_layout.addWidget(title_label)
        # Button to reload the data
        reload_button = QPushButton("Reload")
        reload_button.clicked.connect(self.reload_data)
        title_layout.addWidget(reload_button)
        # Button to hide the widget
        hide_button = QPushButton("X")
        hide_button.clicked.connect(self.hide_widget)
        title_layout.addWidget(hide_button)
        layout.addLayout(title_layout)


        # add the table
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels(['ID', 'Status', 'Title', 'Pasos', 'Mensaje', 'Resultados Esperados', 'Resultados Obtenidos', 'Fecha'])
        layout.addWidget(self.table_widget)
        # display the data 
        self.reload_data()
        

        # Add the main widget to the widget layout
        self.setLayout(layout)
        self.hide()


    def view_dberror(self):
        self.show()

    def hide_widget(self):
        self.hide()

    def reload_data(self):
        # Clear table contents
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        
        # Get the records from the ErrorEntry table
        error_entries = self.session.query(ErrorEntry).all()

        # Add the records to the table
        for row, entry in enumerate(error_entries):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(entry.id)))
            self.table_widget.setItem(row, 1, QTableWidgetItem(entry.status))
            self.table_widget.setItem(row, 2, QTableWidgetItem(entry.title))
            self.table_widget.setItem(row, 3, QTableWidgetItem(entry.pasos_reproducir))
            self.table_widget.setItem(row, 4, QTableWidgetItem(entry.mensaje_error))
            self.table_widget.setItem(row, 5, QTableWidgetItem(entry.resultados_esperados))
            self.table_widget.setItem(row, 6, QTableWidgetItem(entry.resultados_obtenidos))
            self.table_widget.setItem(row, 7, QTableWidgetItem(str(entry.error_date)))

    # hotkey events
    def keyPressEvent(self, event):
        # Event to hide the DBEerror view
        if event.key() == Qt.Key_Escape and self.isVisible():
            self.hide()
        else:
            super().keyPressEvent(event)