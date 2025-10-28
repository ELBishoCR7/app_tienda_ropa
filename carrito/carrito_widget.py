from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QHeaderView, QLabel
)
from ventas.ventas_service import registrar_venta

class CarritoWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Carrito de Compras")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Título
        layout.addWidget(QLabel("<h2>Mi Carrito</h2>"))

        # Tabla de carrito
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID Producto", "Nombre", "Talla", "Cantidad", "Subtotal"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla)

        # Total
        self.total_lbl = QLabel("Total: $0.00")
        layout.addWidget(self.total_lbl)

        # Botones
        botones_layout = QHBoxLayout()
        btn_finalizar = QPushButton("Finalizar Compra")
        btn_finalizar.clicked.connect(self.finalizar_compra)
        
        btn_vaciar = QPushButton("Vaciar Carrito")
        btn_vaciar.clicked.connect(self.vaciar_carrito)

        btn_refrescar = QPushButton("Refrescar")
        btn_refrescar.clicked.connect(self.refrescar_carrito)

        botones_layout.addWidget(btn_refrescar)
        botones_layout.addWidget(btn_vaciar)
        botones_layout.addWidget(btn_finalizar)
        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def refrescar_carrito(self):
        self.tabla.setRowCount(0) # Limpiar tabla
        total = 0
        for item in self.main_window.carrito:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            subtotal = item['cantidad'] * item['precio']
            total += subtotal

            self.tabla.setItem(fila, 0, QTableWidgetItem(str(item['producto_id'])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(item['nombre']))
            self.tabla.setItem(fila, 2, QTableWidgetItem(item['talla']))
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(item['cantidad'])))
            self.tabla.setItem(fila, 4, QTableWidgetItem(f"${subtotal:.2f}"))
        
        self.total_lbl.setText(f"Total: ${total:.2f}")

    def vaciar_carrito(self):
        self.main_window.carrito.clear()
        self.refrescar_carrito()
        QMessageBox.information(self, "Carrito", "El carrito ha sido vaciado.")

    def finalizar_compra(self):
        if not self.main_window.carrito:
            QMessageBox.warning(self, "Error", "El carrito está vacío.")
            return

        cliente_id = self.main_window.user_id
        productos_venta = []
        total = 0

        for item in self.main_window.carrito:
            productos_venta.append((
                item['producto_id'],
                item['cantidad'],
                item['precio']
            ))
            total += item['cantidad'] * item['precio']

        if registrar_venta(cliente_id, productos_venta, total):
            QMessageBox.information(self, "Éxito", "Compra realizada correctamente.")
            self.main_window.carrito.clear()
            self.refrescar_carrito()
            # Actualizar stock en la vista de productos
            self.main_window.productos_widget.cargar_productos()
        else:
            QMessageBox.critical(self, "Error", "No se pudo procesar la compra.")
