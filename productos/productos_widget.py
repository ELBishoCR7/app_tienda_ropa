from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QHeaderView, QInputDialog
)
from productos.productos_service import (
    obtener_productos, crear_producto, actualizar_producto, eliminar_producto
)
from productos.formulario_producto import FormularioProducto


class ProductosWidget(QWidget):
    def __init__(self, tipo_usuario="admin", user_id=None, main_window=None):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.setGeometry(150, 150, 900, 400)
        self.tipo_usuario = tipo_usuario
        self.user_id = user_id
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Tabla de productos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Descripción", "Precio", "Stock", "Talla", "Categoría"]
        )
        # Mejoras en la tabla
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

        # Botones
        botones_layout = QHBoxLayout()

        btn_cargar = QPushButton("Cargar productos")
        btn_cargar.clicked.connect(self.cargar_productos)

        btn_agregar = QPushButton("Agregar producto")
        btn_agregar.clicked.connect(self.abrir_formulario_agregar)

        btn_editar = QPushButton("Editar producto")
        btn_editar.clicked.connect(self.abrir_formulario_editar)

        btn_eliminar = QPushButton("Eliminar producto")
        btn_eliminar.clicked.connect(self.eliminar_producto)
        
        btn_add_carrito = QPushButton("Agregar al carrito")
        btn_add_carrito.clicked.connect(self.agregar_al_carrito)

        if self.tipo_usuario == "cliente":
            btn_agregar.hide()
            btn_editar.hide()
            btn_eliminar.hide()
            botones_layout.addWidget(btn_add_carrito)
        else:
            btn_add_carrito.hide()
            if self.tipo_usuario == "empleado":
                btn_eliminar.setEnabled(False)
            
            botones_layout.addWidget(btn_agregar)
            botones_layout.addWidget(btn_editar)
            botones_layout.addWidget(btn_eliminar)

        botones_layout.addWidget(btn_cargar)
        layout.addLayout(botones_layout)
        self.setLayout(layout)

        # Cargar datos al iniciar
        self.cargar_productos()

    # 📋 Cargar productos en la tabla
    def cargar_productos(self):
        productos = obtener_productos()
        self.tabla.setRowCount(len(productos))

        for fila, producto in enumerate(productos):
            for columna, valor in enumerate(producto):
                self.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))

    # 🛒 Agregar producto al carrito (para clientes)
    def agregar_al_carrito(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Selecciona un producto para agregar al carrito")
            return

        producto_id = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()
        precio = float(self.tabla.item(fila, 3).text())
        stock = int(self.tabla.item(fila, 4).text())
        tallas_disponibles = self.tabla.item(fila, 5).text().split(',')

        # Dialogo para talla
        talla, ok_talla = QInputDialog.getItem(self, "Seleccionar Talla", "Talla:", [t.strip() for t in tallas_disponibles], 0, False)
        if not ok_talla:
            return

        # Dialogo para cantidad
        cantidad, ok_cantidad = QInputDialog.getInt(self, "Seleccionar Cantidad", f"Cantidad de '{nombre}' (Talla: {talla}):", 1, 1, stock)

        if ok_cantidad:
            # Comprobar si el producto ya está en el carrito
            for item in self.main_window.carrito:
                if item['producto_id'] == producto_id and item['talla'] == talla:
                    item['cantidad'] += cantidad
                    QMessageBox.information(self, "Éxito", f"{cantidad} x '{nombre}' (Talla: {talla}) agregado(s) al carrito.")
                    return

            # Si no está, agregarlo como nuevo item
            item_carrito = {
                "producto_id": producto_id,
                "nombre": nombre,
                "cantidad": cantidad,
                "precio": precio,
                "talla": talla
            }
            self.main_window.carrito.append(item_carrito)
            QMessageBox.information(self, "Éxito", f"'{nombre}' (Talla: {talla}) agregado al carrito.")

    # ➕ Formulario para agregar producto
    def abrir_formulario_agregar(self):
        dialogo = FormularioProducto()
        if dialogo.exec():
            nombre, descripcion, precio, stock, talla, categoria = dialogo.get_datos()
            if crear_producto(nombre, descripcion, precio, stock, talla, categoria):
                QMessageBox.information(self, "Éxito", "Producto agregado correctamente")
                self.cargar_productos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo agregar el producto")

    # ✏️ Formulario para editar producto
    def abrir_formulario_editar(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Selecciona un producto para editar")
            return

        producto_id = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()
        descripcion = self.tabla.item(fila, 2).text()
        precio = float(self.tabla.item(fila, 3).text())
        stock = int(self.tabla.item(fila, 4).text())
        talla = self.tabla.item(fila, 5).text()
        categoria = self.tabla.item(fila, 6).text()

        dialogo = FormularioProducto(nombre, descripcion, precio, stock, talla, categoria)
        if dialogo.exec():
            nuevo_nombre, nuevo_desc, nuevo_precio, nuevo_stock, nueva_talla, nueva_categoria = dialogo.get_datos()
            if actualizar_producto(producto_id, nuevo_nombre, nuevo_desc, nuevo_precio, nuevo_stock, nueva_talla, nueva_categoria):
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
                self.cargar_productos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el producto")

    # ❌ Eliminar producto
    def eliminar_producto(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Selecciona un producto para eliminar")
            return

        producto_id = int(self.tabla.item(fila, 0).text())
        confirmacion = QMessageBox.question(self, "Confirmar", "¿Seguro que deseas eliminar este producto?")

        if confirmacion == QMessageBox.StandardButton.Yes:
            if eliminar_producto(producto_id):
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.cargar_productos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el producto")