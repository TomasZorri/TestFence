## For Ui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QCheckBox
from PyQt5.QtCore import Qt

## database
import sys
sys.path.append('..')
from model import ErrorEntry

# Save the data to a PDF
from reportlab.pdfgen import canvas



class DBError(QWidget):
    def __init__(self, session, parent=None):
        super(DBError, self).__init__(parent)

        # instances
        self.session = session
        self.selected_item_id = None
        

        # Create the main widget
        self.widget = QWidget(self)
        layout = QVBoxLayout(self.widget)

        # Add the title and buttons
        title_layout = QHBoxLayout()
        title_label = QLabel("Error Details")
        title_layout.addWidget(title_label)
        # Button to download the report
        download_button = QPushButton("Download report")
        download_button.clicked.connect(self.download_report)
        title_layout.addWidget(download_button)
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
        
        # Connect itemClicked signal to handle_cell_click function
        self.table_widget.itemClicked.connect(self.handle_cell_click)


    def handle_cell_click(self, item):
        row = item.row()
        self.selected_item_id = self.table_widget.item(row, 0).text()  


    def download_report(self):
        if self.selected_item_id:
            item_id = int(self.selected_item_id)
            error_entry = self.session.query(ErrorEntry).filter_by(id=item_id).first()
            if error_entry:
                # Access the attributes of the error_entry according to your needs
                status = error_entry.status
                title = error_entry.title
                pasos_reproducir = error_entry.pasos_reproducir
                mensaje_error = error_entry.mensaje_error
                resultados_esperados = error_entry.resultados_esperados
                resultados_obtenidos = error_entry.resultados_obtenidos
                error_date = error_entry.error_date

                # Create the PDF document
                pdf_filename = "reportsInPDF/reporte.pdf"
                pdf_canvas = canvas.Canvas(pdf_filename)

                # Add the data to the PDF
                pdf_canvas.setFont("Helvetica", 12)
                pdf_canvas.drawString(50, 750, f"Status: {status}")
                pdf_canvas.drawString(50, 730, f"Title: {title}")
                pdf_canvas.drawString(50, 710, f"Pasos para reproducir: {pasos_reproducir}")
                pdf_canvas.drawString(50, 690, f"Mensaje de error: {mensaje_error}")
                pdf_canvas.drawString(50, 670, f"Resultados esperados: {resultados_esperados}")
                pdf_canvas.drawString(50, 650, f"Resultados obtenidos: {resultados_obtenidos}")
                pdf_canvas.drawString(50, 630, f"Fecha de error: {error_date}")

                # Save the PDF
                pdf_canvas.save()
            else:
                print("No se encontró ningún registro con el ID seleccionado.")
        else:
            print("No item is currently selected.")





    # hotkey events
    def keyPressEvent(self, event):
        # Event to hide the DBEerror view
        if event.key() == Qt.Key_Escape and self.isVisible():
            self.hide()
        else:
            super().keyPressEvent(event)


