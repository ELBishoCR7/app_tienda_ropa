from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel,
    QComboBox, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from ventas.ventas_service import registrar_venta, obtener_ventas, obtener_detalles_venta
from clientes.clientes_service import obtener_clientes
from productos.productos_service import obtener_productos

class VentasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Ventas")
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)

        # --- Panel Izquierdo: Nueva Venta ---
        left_panel = QGroupBox("Nueva Venta")
        left_layout = QVBoxLayout()

        # ComboBox para clientes
        self.combo_clientes = QComboBox()
        left_layout.addWidget(QLabel("Cliente:"))
        left_layout.addWidget(self.combo_clientes)

        # ComboBox para productos
        self.combo_productos = QComboBox()
        left_layout.addWidget(QLabel("Producto:"))
        left_layout.addWidget(self.combo_productos)

        # SpinBox para cantidad
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(100)
        left_layout.addWidget(QLabel("Cantidad:"))
        left_layout.addWidget(self.spin_cantidad)

        # Botón para agregar al carrito
        btn_agregar = QPushButton("Agregar al Carrito")
        btn_agregar.clicked.connect(self.agregar_al_carrito)
        left_layout.addWidget(btn_agregar)

        # Tabla del carrito
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5) # id, nombre, cantidad, precio, subtotal
        self.tabla_carrito.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Precio Unit.", "Subtotal"])
        self.tabla_carrito.setColumnHidden(0, True) # Ocultar ID
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.tabla_carrito)

        # Total y botón de registrar venta
        self.label_total = QLabel("Total: $0.00")
        left_layout.addWidget(self.label_total)

        btn_registrar_venta = QPushButton("Registrar Venta")
        btn_registrar_venta.clicked.connect(self.registrar_nueva_venta)
        left_layout.addWidget(btn_registrar_venta)

        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)

        # --- Panel Derecho: Historial de Ventas ---
        right_panel = QGroupBox("Historial de Ventas")
        right_layout = QVBoxLayout()

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(4)
        self.tabla_ventas.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "Total"])
        self.tabla_ventas.setColumnHidden(0, True)
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_ventas.selectionModel().selectionChanged.connect(self.mostrar_detalles)
        right_layout.addWidget(self.tabla_ventas)

        # Tabla de detalles de venta
        self.tabla_detalles = QTableWidget()
        self.tabla_detalles.setColumnCount(4)
        self.tabla_detalles.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(QLabel("Detalles de la Venta Seleccionada:"))
        right_layout.addWidget(self.tabla_detalles)

        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)

        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        # Cargar clientes
        self.clientes = obtener_clientes()
        self.combo_clientes.clear()
        for cliente in self.clientes:
            self.combo_clientes.addItem(cliente[1], cliente[0]) # Texto: nombre, Dato: id

        # Cargar productos
        self.productos = obtener_productos()
        self.combo_productos.clear()
        for prod in self.productos:
            # Texto: Nombre ($Precio) - Stock: X
            display_text = f"{prod[1]} (${prod[3]}) - Stock: {prod[4]}"
            self.combo_productos.addItem(display_text, prod) # Dato: tupla completa del producto

        # Cargar historial de ventas
        self.cargar_historial_ventas()

    def agregar_al_carrito(self):
        producto_seleccionado = self.combo_productos.currentData()
        cantidad = self.spin_cantidad.value()

        if not producto_seleccionado:
            QMessageBox.warning(self, "Error", "Selecciona un producto.")
            return

        prod_id, prod_nombre, _, prod_precio, prod_stock, _, _ = producto_seleccionado

        if cantidad > prod_stock:
            QMessageBox.warning(self, "Stock Insuficiente", f"Solo quedan {prod_stock} unidades de {prod_nombre}.")
            return

        # Verificar si el producto ya está en el carrito para actualizar cantidad
        for row in range(self.tabla_carrito.rowCount()):
            if self.tabla_carrito.item(row, 0).text() == str(prod_id):
                # Actualizar cantidad y subtotal
                item_cantidad = self.tabla_carrito.item(row, 2)
                nueva_cantidad = int(item_cantidad.text()) + cantidad
                if nueva_cantidad > prod_stock:
                    QMessageBox.warning(self, "Stock Insuficiente", f"No puedes agregar más de {prod_stock} unidades.")
                    return
                item_cantidad.setText(str(nueva_cantidad))
                subtotal = nueva_cantidad * prod_precio
                self.tabla_carrito.setItem(row, 4, QTableWidgetItem(f"{subtotal:.2f}"))
                self.actualizar_total()
                return

        # Si no está en el carrito, agregar nueva fila
        row_count = self.tabla_carrito.rowCount()
        self.tabla_carrito.insertRow(row_count)
        subtotal = cantidad * prod_precio
        self.tabla_carrito.setItem(row_count, 0, QTableWidgetItem(str(prod_id)))
        self.tabla_carrito.setItem(row_count, 1, QTableWidgetItem(prod_nombre))
        self.tabla_carrito.setItem(row_count, 2, QTableWidgetItem(str(cantidad)))
        self.tabla_carrito.setItem(row_count, 3, QTableWidgetItem(f"{prod_precio:.2f}"))
        self.tabla_carrito.setItem(row_count, 4, QTableWidgetItem(f"{subtotal:.2f}"))
        self.actualizar_total()

    def actualizar_total(self):
        total = 0.0
        for row in range(self.tabla_carrito.rowCount()):
            total += float(self.tabla_carrito.item(row, 4).text())
        self.label_total.setText(f"Total: ${total:.2f}")

    def registrar_nueva_venta(self):
        if self.tabla_carrito.rowCount() == 0:
            QMessageBox.warning(self, "Carrito Vacío", "Agrega productos al carrito antes de registrar la venta.")
            return

        cliente_id = self.combo_clientes.currentData()
        total_str = self.label_total.text().replace("Total: $", "")
        total = float(total_str)

        productos_venta = []
        for row in range(self.tabla_carrito.rowCount()):
            prod_id = int(self.tabla_carrito.item(row, 0).text())
            cantidad = int(self.tabla_carrito.item(row, 2).text())
            precio = float(self.tabla_carrito.item(row, 3).text())
            productos_venta.append((prod_id, cantidad, precio))

        if registrar_venta(cliente_id, productos_venta, total):
            QMessageBox.information(self, "Venta Exitosa", "La venta ha sido registrada correctamente.")
            self.limpiar_carrito()
            self.cargar_datos_iniciales() # Recargar todo
        else:
            QMessageBox.critical(self, "Error", "No se pudo registrar la venta.")

    def limpiar_carrito(self):
        self.tabla_carrito.setRowCount(0)
        self.actualizar_total()

    def cargar_historial_ventas(self):
        ventas = obtener_ventas()
        self.tabla_ventas.setRowCount(len(ventas))
        for row, venta in enumerate(ventas):
            # id, fecha, cliente_nombre, total
            self.tabla_ventas.setItem(row, 0, QTableWidgetItem(str(venta[0])))
            self.tabla_ventas.setItem(row, 1, QTableWidgetItem(str(venta[1])))
            self.tabla_ventas.setItem(row, 2, QTableWidgetItem(venta[2]))
            self.tabla_ventas.setItem(row, 3, QTableWidgetItem(f"{venta[3]:.2f}"))

    def mostrar_detalles(self, selected, deselected):
        if not selected.indexes():
            return
        
        row = selected.indexes()[0].row()
        venta_id = int(self.tabla_ventas.item(row, 0).text())
        detalles = obtener_detalles_venta(venta_id)
        
        self.tabla_detalles.setRowCount(len(detalles))
        for r, detalle in enumerate(detalles):
            # prod_nombre, cantidad, precio_unit, subtotal
            self.tabla_detalles.setItem(r, 0, QTableWidgetItem(detalle[0]))
            self.tabla_detalles.setItem(r, 1, QTableWidgetItem(str(detalle[1])))
            self.tabla_detalles.setItem(r, 2, QTableWidgetItem(f"{detalle[2]:.2f}"))
            self.tabla_detalles.setItem(r, 3, QTableWidgetItem(f"{detalle[3]:.2f}"))
