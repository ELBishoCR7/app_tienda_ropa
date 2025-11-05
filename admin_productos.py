from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QMessageBox,
    QScrollArea, QFrame, QGridLayout, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from network_worker import NetworkWorker, API_URL  # <-- Corregido: import desde network_worker (evita circular)

class VentanaAdminProductos(QWidget):
    """Panel de administración de productos."""
    go_to_store = pyqtSignal()  # Para volver a la tienda
    
    def __init__(self):
        super().__init__()
        self.api_token = None
        self.thread = None
        self.worker = None
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Gestión de Productos")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title)
        
        self.back_button = QPushButton("← Volver")
        self.back_button.clicked.connect(self.go_to_store.emit)
        header_layout.addWidget(self.back_button)
        main_layout.addLayout(header_layout)
        
        # Formulario de Nuevo Producto
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Shape.Box)
        form_layout = QGridLayout(form_frame)
        
        # Inputs
        self.nombre_input = QLineEdit()
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setMaximum(99999.99)
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(9999)
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(100)
        self.imagen_input = QLineEdit()
        self.imagen_input.setPlaceholderText("URL de la imagen")
        
        # Añadir al layout
        form_layout.addWidget(QLabel("Nombre:"), 0, 0)
        form_layout.addWidget(self.nombre_input, 0, 1)
        form_layout.addWidget(QLabel("Precio:"), 1, 0)
        form_layout.addWidget(self.precio_input, 1, 1)
        form_layout.addWidget(QLabel("Stock:"), 2, 0)
        form_layout.addWidget(self.stock_input, 2, 1)
        form_layout.addWidget(QLabel("Descripción:"), 3, 0)
        form_layout.addWidget(self.descripcion_input, 3, 1)
        form_layout.addWidget(QLabel("Imagen URL:"), 4, 0)
        form_layout.addWidget(self.imagen_input, 4, 1)
        
        self.add_button = QPushButton("Añadir Producto")
        self.add_button.clicked.connect(self.handle_add_product)
        form_layout.addWidget(self.add_button, 5, 0, 1, 2)
        
        main_layout.addWidget(form_frame)
        
        # Lista de Productos
        self.products_area = QScrollArea()
        self.products_area.setWidgetResizable(True)
        self.products_widget = QWidget()
        self.products_layout = QVBoxLayout(self.products_widget)
        self.products_area.setWidget(self.products_widget)
        main_layout.addWidget(self.products_area)
        
    def set_token(self, token: str):
        self.api_token = token
        self.fetch_products()
        
    def fetch_products(self):
        """Obtiene la lista de productos (usa la ruta pública protegida /api/products)."""
        # Limpieza de la lista visual
        while self.products_layout.count():
            child = self.products_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Configura el hilo y el worker
        self.thread = QThread()
        # Usar la ruta correcta: GET /api/products (protegida) — no /api/admin/products
        self.worker = NetworkWorker(
            f"{API_URL}/api/products",
            "GET_AUTH",
            token=self.api_token
        )
        self.worker.moveToThread(self.thread)

        # Conecta señales
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_fetch_success)
        self.worker.failure.connect(self.on_fetch_failure)

        # Limpieza
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        
    def handle_add_product(self):
        """Envía un nuevo producto a la API."""
        producto = {
            "nombre": self.nombre_input.text(),
            "precio": self.precio_input.value(),
            "stock": self.stock_input.value(),
            "descripcion": self.descripcion_input.toPlainText(),
            "imagen_url": self.imagen_input.text()
        }
        
        self.thread = QThread()
        self.worker = NetworkWorker(
            f"{API_URL}/api/admin/products",
            "POST_AUTH",
            data=producto,
            token=self.api_token
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_add_success)
        self.worker.failure.connect(self.on_add_failure)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def create_product_widget(self, product: dict) -> QFrame:
        """Crea un widget para mostrar un producto con botones de editar/eliminar."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        layout = QVBoxLayout(frame)
        
        info = QLabel(
            f"<b>{product['nombre']}</b><br>"
            f"Precio: ${product['precio']:.2f}<br>"
            f"Stock: {product['stock']}<br>"
            f"Descripción: {product['descripcion']}"
        )
        layout.addWidget(info)
        
        buttons = QHBoxLayout()
        edit_btn = QPushButton("Editar")
        delete_btn = QPushButton("Eliminar")
        buttons.addWidget(edit_btn)
        buttons.addWidget(delete_btn)
        layout.addLayout(buttons)
        
        # Conectar botones
        edit_btn.clicked.connect(lambda: self.edit_product(product))
        delete_btn.clicked.connect(lambda: self.delete_product(product['id']))
        
        return frame

    def on_fetch_success(self, products_list: list):
        """Procesa la lista de productos recibida."""
        # Limpia la lista actual
        while self.products_layout.count():
            child = self.products_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Crea widgets para cada producto
        for product in products_list:
            product_widget = self.create_product_widget(product)
            self.products_layout.addWidget(product_widget)

    def on_fetch_failure(self, error_message: str):
        QMessageBox.critical(self, "Error", f"Error al cargar productos: {error_message}")

    def on_add_success(self, new_product: dict):
        """Cuando se añade un producto exitosamente."""
        QMessageBox.information(self, "Éxito", "Producto añadido correctamente")
        self.clear_form()
        self.fetch_products()  # Recargar lista

    def on_add_failure(self, error_message: str):
        QMessageBox.critical(self, "Error", f"Error al añadir producto: {error_message}")

    def clear_form(self):
        """Limpia el formulario después de añadir."""
        self.nombre_input.clear()
        self.precio_input.setValue(0)
        self.stock_input.setValue(0)
        self.descripcion_input.clear()
        self.imagen_input.clear()

    def delete_product(self, product_id: int):
        """Elimina un producto."""
        if QMessageBox.question(
            self, 
            "Confirmar", 
            "¿Estás seguro de eliminar este producto?"
        ) != QMessageBox.StandardButton.Yes:
            return

        self.thread = QThread()
        self.worker = NetworkWorker(
            f"{API_URL}/api/admin/products/{product_id}",
            "DELETE_AUTH",
            token=self.api_token
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(lambda _: self.on_delete_success(product_id))
        self.worker.failure.connect(self.on_delete_failure)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def on_delete_success(self, product_id: int):
        QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
        self.fetch_products()  # Recargar lista

    def on_delete_failure(self, error_message: str):
        QMessageBox.critical(self, "Error", f"Error al eliminar producto: {error_message}")

    def edit_product(self, product: dict):
        """Abre diálogo de edición para un producto."""
        dialog = EditProductDialog(product, self)
        if dialog.exec():
            updated_data = dialog.get_data()
            self.update_product(product['id'], updated_data)

    def update_product(self, product_id: int, data: dict):
        """Envía actualización de producto a la API."""
        self.thread = QThread()
        self.worker = NetworkWorker(
            f"{API_URL}/api/admin/products/{product_id}",
            "PUT_AUTH",
            data=data,
            token=self.api_token
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_update_success)
        self.worker.failure.connect(self.on_update_failure)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def on_update_success(self, updated_product: dict):
        QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
        self.fetch_products()  # Recargar lista

    def on_update_failure(self, error_message: str):
        QMessageBox.critical(self, "Error", f"Error al actualizar producto: {error_message}")

class EditProductDialog(QDialog):
    def __init__(self, product: dict, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Editar Producto")
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QGridLayout(self)
        
        # Crear inputs
        self.nombre_input = QLineEdit()
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setMaximum(99999.99)
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(9999)
        self.descripcion_input = QTextEdit()
        self.imagen_input = QLineEdit()
        
        # Añadir al layout
        layout.addWidget(QLabel("Nombre:"), 0, 0)
        layout.addWidget(self.nombre_input, 0, 1)
        layout.addWidget(QLabel("Precio:"), 1, 0)
        layout.addWidget(self.precio_input, 1, 1)
        layout.addWidget(QLabel("Stock:"), 2, 0)
        layout.addWidget(self.stock_input, 2, 1)
        layout.addWidget(QLabel("Descripción:"), 3, 0)
        layout.addWidget(self.descripcion_input, 3, 1)
        layout.addWidget(QLabel("Imagen URL:"), 4, 0)
        layout.addWidget(self.imagen_input, 4, 1)
        
        # Botones
        button_box = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        cancel_btn = QPushButton("Cancelar")
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addLayout(button_box, 5, 0, 1, 2)
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
    def load_data(self):
        """Carga los datos del producto en el formulario."""
        self.nombre_input.setText(self.product['nombre'])
        self.precio_input.setValue(self.product['precio'])
        self.stock_input.setValue(self.product['stock'])
        self.descripcion_input.setText(self.product.get('descripcion', ''))
        self.imagen_input.setText(self.product.get('imagen_url', ''))
        
    def get_data(self) -> dict:
        """Retorna los datos del formulario como diccionario."""
        return {
            "nombre": self.nombre_input.text(),
            "precio": self.precio_input.value(),
            "stock": self.stock_input.value(),
            "descripcion": self.descripcion_input.toPlainText(),
            "imagen_url": self.imagen_input.text()
        }
