from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QSpinBox,
    QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
)
from clientes.clientes_service import obtener_clientes
from productos.productos_service import obtener_productos


class FormularioVenta(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registrar Venta")
        self.setGeometry(200, 200, 500, 400)
        self.productos_seleccionados = []  # Lista de (producto_id, nombre, cantidad, precio_unitario)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Selección de cliente
        self.clientes_cb = QComboBox()
        clientes = obtener_clientes()
        self.clientes_map = {}
        for c in clientes:
            cliente_id, nombre, correo, telefono, direccion = c
            self.clientes_cb.addItem(nombre, cliente_id)
            self.clientes_map[nombre] = cliente_id

        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.clientes_cb)

        # Selección de producto
        self.productos_cb = QComboBox()
        productos = obtener_productos()
        self.productos_map = {}
        for p in productos:
            producto_id, nombre, descripcion, precio, stock, talla, categoria = p
            self.productos_cb.addItem(f"{nombre} - ${precio} (Stock: {stock})", producto_id)
            self.productos_map[nombre] = (producto_id, precio, stock)

        layout.addWidget(QLabel("Producto:"))
        layout.addWidget(self.productos_cb)

        # Cantidad
        cantidad_layout = QHBoxLayout()
        cantidad_layout.addWidget(QLabel("Cantidad:"))
        self.cantidad_sb = QSpinBox()
        self.cantidad_sb.setRange(1, 100)
        cantidad_layout.addWidget(self.cantidad_sb)

        btn_agregar = QPushButton("Agregar producto")
        btn_agregar.clicked.connect(self.agregar_producto)
        cantidad_layout.addWidget(btn_agregar)

        layout.addLayout(cantidad_layout)

        # Lista de productos seleccionados
        self.lista_productos_lbl = QLabel("Productos seleccionados:\n")
        layout.addWidget(self.lista_productos_lbl)

        # Total
        self.total_lbl = QLabel("Total: $0.00")
        layout.addWidget(self.total_lbl)

        # Botón guardar
        btn_guardar = QPushButton("Registrar Venta")
        btn_guardar.clicked.connect(self.accept)
        layout.addWidget(btn_guardar)

        self.setLayout(layout)

    def agregar_producto(self):
        index = self.productos_cb.currentIndex()
        producto_id = self.productos_cb.itemData(index)
        texto = self.productos_cb.currentText()
        cantidad = self.cantidad_sb.value()

        # Extraer precio del texto
        nombre = texto.split(" - ")[0]
        producto_id, precio, stock = self.productos_map[nombre]

        if cantidad > stock:
            QMessageBox.warning(self, "Error", "Cantidad mayor al stock disponible")
            return

        self.productos_seleccionados.append((producto_id, nombre, cantidad, precio))
        self.actualizar_lista()

    def actualizar_lista(self):
        texto = "Productos seleccionados:\n"
        total = 0
        for pid, nombre, cantidad, precio in self.productos_seleccionados:
            subtotal = cantidad * precio
            texto += f"- {nombre} x{cantidad} = ${subtotal:.2f}\n"
            total += subtotal
        self.lista_productos_lbl.setText(texto)
        self.total_lbl.setText(f"Total: ${total:.2f}")

    def get_datos(self):
        """
        Devuelve los datos de la venta:
        - cliente_id
        - lista de productos [(producto_id, cantidad, precio_unitario), ...]
        - total
        """
        cliente_id = self.clientes_cb.currentData()
        total = sum(cantidad * precio for _, _, cantidad, precio in self.productos_seleccionados)
        productos = [(pid, cantidad, precio) for pid, _, cantidad, precio in self.productos_seleccionados]
        return cliente_id, productos, total