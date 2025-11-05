from datetime import datetime
import sys
import requests
import json
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
    QLineEdit, QPushButton, QMessageBox, QFormLayout, QStackedWidget, QScrollArea, QFrame, QHBoxLayout, QSpinBox
)
from PyQt6.QtCore import QObject, QThread, pyqtSignal,Qt
from PyQt6.QtGui import QPixmap
import urllib.request

from network_worker import NetworkWorker, API_URL  # moved here
from admin_productos import VentanaAdminProductos  # keep after NetworkWorker import

# --- Página de la Tienda (Placeholder) ---



# --- Página de la Tienda (Funcional) ---

class VentanaAdminVentas(QWidget):
    """Página del panel de administración (Funcional)."""
    go_to_store = pyqtSignal()  # Add the missing signal

    def __init__(self):
        super().__init__()
        self.api_token = None
        self.thread = None
        self.worker = None

        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Header with navigation
        header_layout = QHBoxLayout()
        
        title_label = QLabel("PANEL DE ADMINISTRACIÓN - VENTAS TOTALES")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(title_label, stretch=1)

        # Add refresh button
        self.refresh_button = QPushButton("🔄 Actualizar")
        self.refresh_button.clicked.connect(self.fetch_sales)
        header_layout.addWidget(self.refresh_button)

        self.back_button = QPushButton("← Volver a la Tienda")
        self.back_button.clicked.connect(self.go_to_store.emit)
        header_layout.addWidget(self.back_button)
        
        main_layout.addLayout(header_layout)
        
        # Add sales summary section
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("padding: 10px; background-color: #e8f4f8; border-radius: 5px;")
        main_layout.addWidget(self.summary_label)
        
        self.info_label = QLabel("Cargando ventas...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        # --- Área de Scroll para Ventas ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(scroll_area)
        
        # Widget contenedor para las ventas
        self.sales_widget = QWidget()
        scroll_area.setWidget(self.sales_widget)
        
        # Layout para la lista de ventas
        self.sales_layout = QVBoxLayout(self.sales_widget)
        self.sales_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
    def set_token(self, token: str):
        """Recibe el token y pide las ventas."""
        self.api_token = token
        print(f"VentanaAdmin: Token recibido. Pidiendo ventas...")
        self.fetch_sales()

    def update_summary(self, sales_list: list):
        """Actualiza el resumen de ventas."""
        if not sales_list:
            self.summary_label.hide()
            return

        total_ventas = len(sales_list)
        total_dinero = sum(sale['total'] for sale in sales_list)
        total_productos = sum(
            sum(item['cantidad'] for item in sale['items']) 
            for sale in sales_list
        )
        
        self.summary_label.setText(
            f"📊 Resumen de Ventas:\n"
            f"Total de Ventas: {total_ventas}\n"
            f"Total Recaudado: ${total_dinero:.2f}\n"
            f"Total Productos Vendidos: {total_productos}"
        )
        self.summary_label.show()

    def fetch_sales(self):
        """Inicia el hilo de red para buscar las ventas."""
        self.info_label.setText("Cargando ventas...")
        self.info_label.show() # Muestra "Cargando..."
        
        # Limpia ventas antiguas (si las hubiera)
        while self.sales_layout.count():
            child = self.sales_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Configura el hilo y el worker
        self.thread = QThread()
        # ¡Usamos el método GET_AUTH y pasamos el token de admin!
        self.worker = NetworkWorker(
            f"{API_URL}/api/admin/sales", 
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

    def on_fetch_success(self, sales_list: list):
        """Se llama cuando la API devuelve la lista de ventas."""
        self.info_label.hide()
        
        # Update summary first
        self.update_summary(sales_list)
        
        if not sales_list:
            self.info_label.setText("No se han encontrado ventas registradas.")
            self.info_label.show()
            return

        # Limpia ventas antiguas
        while self.sales_layout.count():
            child = self.sales_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Create frames for each sale
        for sale in sales_list:
            sale_frame = QFrame()
            sale_frame.setFrameShape(QFrame.Shape.StyledPanel)
            sale_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #ccc;
                    margin: 2px;
                }
            """)
            
            frame_layout = QVBoxLayout(sale_frame)
            
            # Format sale information
            try:
                sale_datetime = datetime.strptime(sale['fecha'], '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                try:
                    sale_datetime = datetime.strptime(sale['fecha'], '%Y-%m-%d %H:%M:%S')
                except:
                    sale_datetime = None

            fecha_formateada = sale_datetime.strftime('%Y-%m-%d %H:%M') if sale_datetime else sale['fecha']
            
            header_text = (
                f"<b>Venta #{sale['id']}</b> | Cliente #{sale['user_id']} | {fecha_formateada}"
            )
            header_label = QLabel(header_text)
            header_label.setStyleSheet("padding: 5px;")
            frame_layout.addWidget(header_label)
            
            # Items section
            items_text = []
            for item in sale['items']:
                items_text.append(
                    f"• {item['cantidad']}x Producto #{item['product_id']} "
                    f"(${item['precio_unitario']:.2f} c/u)"
                )
            
            items_label = QLabel("\n".join(items_text))
            items_label.setStyleSheet("padding: 5px; color: #555;")
            frame_layout.addWidget(items_label)
            
            # Total
            total_label = QLabel(f"<b>Total: ${sale['total']:.2f}</b>")
            total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            total_label.setStyleSheet("padding: 5px; color: #2ecc71;")
            frame_layout.addWidget(total_label)
            
            self.sales_layout.addWidget(sale_frame)
            
    def on_fetch_failure(self, error_message):
        """Se llama si la API falla."""
        self.info_label.setText(f"Error al cargar ventas: {error_message}")
        self.info_label.show()
        QMessageBox.critical(self, "Error de Red", error_message)

class VentanaCarrito(QWidget):
    """Página del carrito de compras (Funcional)."""
    go_to_store = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.api_token = None
        # Lista para mantener referencias a threads activos
        self.active_threads = []
        self.active_workers = []

        layout = QVBoxLayout(self)
        title = QLabel("MI CARRITO")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.info_label = QLabel("Cargando carrito...")
        layout.addWidget(self.info_label)

        # Area scroll para items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll)

        # WARNING label for stock issues
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #b00020;")  # rojo suave
        self.warning_label.hide()
        layout.addWidget(self.warning_label)

        # Footer con total y checkout
        footer = QHBoxLayout()
        self.total_label = QLabel("Total: $0.00")
        footer.addWidget(self.total_label)
        self.checkout_btn = QPushButton("Finalizar Compra")
        self.checkout_btn.clicked.connect(self.handle_checkout)
        footer.addWidget(self.checkout_btn)
        self.back_button = QPushButton("Volver")
        self.back_button.clicked.connect(self.go_to_store.emit)
        footer.addWidget(self.back_button)
        layout.addLayout(footer)

        self.setLayout(layout)

        # Estilizar botones de navegación
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)

    def set_token(self, token: str):
        self.api_token = token
        self.fetch_cart()

    def cleanup_threads(self):
        """Limpia threads completados de la lista (sin tocar workers eliminados)."""
        # Sólo mantenemos threads que aún están corriendo.
        self.active_threads = [t for t in self.active_threads if t.isRunning()]

    def start_network_operation(self, url: str, method: str, data: dict = None):
        """Helper para iniciar operaciones de red manteniendo referencias."""
        self.cleanup_threads()
        
        thread = QThread()
        worker = NetworkWorker(url, method, data=data, token=self.api_token)
        
        # Guardamos referencias
        self.active_threads.append(thread)
        self.active_workers.append(worker)
        
        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        # Cuando el worker termine: cerramos el thread, removemos worker de la lista y borramos worker.
        def _on_worker_finished(w=worker):
            # remover worker de la lista de forma segura
            try:
                if w in self.active_workers:
                    self.active_workers.remove(w)
            except Exception:
                pass

        worker.finished.connect(_on_worker_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        # Cuando el thread termine: removemos el thread de la lista (si existe) y lo liberamos.
        def _on_thread_finished(t=thread):
            try:
                if t in self.active_threads:
                    self.active_threads.remove(t)
            except Exception:
                pass

        thread.finished.connect(lambda: _on_thread_finished())
        thread.finished.connect(thread.deleteLater)
        
        return thread, worker

    def fetch_cart(self):
        """Obtiene contenido del carrito."""
        self.info_label.setText("Cargando carrito...")
        # Limpia UI
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        thread, worker = self.start_network_operation(
            f"{API_URL}/api/cart", 
            "GET_AUTH"
        )
        worker.success.connect(self.on_fetch_cart_success)
        worker.failure.connect(self.on_fetch_cart_failure)
        thread.start()

    def on_fetch_cart_success(self, cart_data):
        self.info_label.hide()
        items = cart_data.get("items", [])
        total = cart_data.get("total", 0.0)
        self.total_label.setText(f"Total: ${total:.2f}")

        # Reset warning / checkout default
        self.warning_label.hide()
        self.checkout_btn.setEnabled(False)

        if not items:
            self.scroll_layout.addWidget(QLabel("El carrito está vacío."))
            return

        stock_ok = True

        for ci in items:
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.Box)
            fl = QHBoxLayout(frame)

            # --- Mostrar imagen si hay URL ---
            if ci.get("imagen_url"):
                try:
                    data = urllib.request.urlopen(ci["imagen_url"]).read()
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    img_label = QLabel()
                    img_label.setPixmap(pixmap.scaledToWidth(80))
                    fl.addWidget(img_label)
                    #añadir estilos a la imagen    
                    img_label.setStyleSheet("""
                        QLabel {
                            border: 2px solid #bdc3c7;
                            border-radius: 4px;
                            padding: 4px;
                            background-color: white;
                        }
                    """)

                    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                except Exception:
                    fl.addWidget(QLabel("(Sin imagen)"))
                    

                 
              
            # --- Fin imagen ---

            name = QLabel(f"{ci.get('nombre','Producto')} ( ${ci['precio_unitario']:.2f} )")
            fl.addWidget(name)

            spin = QSpinBox()
            spin.setMinimum(1)
            # Usar stock provisto por la API para limitar la cantidad máxima
            stock_available = ci.get("stock", 9999) or 0
            spin.setMaximum(max(1, stock_available))
            spin.setValue(min(ci["cantidad"], max(1, stock_available)))
            fl.addWidget(spin)

            # Detect stock conflict
            if ci["cantidad"] > stock_available:
                stock_ok = False

            update_btn = QPushButton("Actualizar")
            remove_btn = QPushButton("Eliminar")
            fl.addWidget(update_btn)
            fl.addWidget(remove_btn)

            # Conexiones con closures capturando product_id y spin
            update_btn.clicked.connect(lambda _, pid=ci["product_id"], s=spin: self.update_cart_item(pid, s.value()))
            remove_btn.clicked.connect(lambda _, pid=ci["product_id"]: self.remove_cart_item(pid))

            self.scroll_layout.addWidget(frame)

        # Si algún item excede stock, mostrar advertencia y deshabilitar checkout
        if not stock_ok:
            self.warning_label.setText("Algunos items superan el stock disponible. Actualiza las cantidades.")
            self.warning_label.show()
            self.checkout_btn.setEnabled(False)
        else:
            # Habilitar checkout solo si hay items y no hay conflictos
            self.checkout_btn.setEnabled(len(items) > 0)
            self.warning_label.hide()

    def on_fetch_cart_failure(self, error_message):
        self.info_label.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Error al cargar carrito", error_message)

    def update_cart_item(self, product_id: int, cantidad: int):
        """Actualiza cantidad de un item."""
        if cantidad <= 0:
            QMessageBox.warning(self, "Cantidad inválida", "La cantidad debe ser mayor que 0.")
            return

        data = {"product_id": product_id, "cantidad": cantidad}
        thread, worker = self.start_network_operation(
            f"{API_URL}/api/cart/update/{product_id}",
            "PUT_AUTH",
            data=data
        )
        worker.success.connect(lambda _: self.fetch_cart())
        worker.failure.connect(lambda e: QMessageBox.critical(self, "Error", e))
        thread.start()

    def remove_cart_item(self, product_id: int):
        """Elimina un item del carrito."""
        thread, worker = self.start_network_operation(
            f"{API_URL}/api/cart/remove/{product_id}",
            "DELETE_AUTH"
        )
        worker.success.connect(lambda _: self.fetch_cart())
        worker.failure.connect(lambda e: QMessageBox.critical(self, "Error", e))
        thread.start()

    def handle_checkout(self):
        """Finaliza la compra."""
        if QMessageBox.question(
            self, 
            "Confirmar", 
            "¿Deseas finalizar la compra?"
        ) != QMessageBox.StandardButton.Yes:
            return

        thread, worker = self.start_network_operation(
            f"{API_URL}/api/cart/checkout",
            "POST_AUTH"
        )
        worker.success.connect(self.on_checkout_success)
        worker.failure.connect(lambda e: QMessageBox.critical(self, "Error al pagar", e))
        thread.start()

    def closeEvent(self, event):
        """Se llama cuando se cierra la ventana."""
        # Esperar a que terminen los threads activos (con timeout razonable)
        for thread in list(self.active_threads):
            try:
                if thread.isRunning():
                    thread.quit()
                    thread.wait(2000)  # espera hasta 2s
            except Exception:
                pass
        super().closeEvent(event)

    def on_checkout_success(self, venta_data):
        QMessageBox.information(self, "Compra exitosa", f"Compra realizada. Venta ID: {venta_data.get('id')}")
        # Refrescar carrito (estará vacío)
        self.fetch_cart()

class VentanaRegistro(QWidget):
    register_success = pyqtSignal() # Avisa a la ventana principal que cambie a Login
    go_to_login = pyqtSignal()      # Avisa que queremos ir a la vista de Login

    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None

        layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("tu@email.com")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # --- NUEVOS CAMPOS DE DIRECCIÓN ---
        self.direccion_input = QLineEdit()
        self.ciudad_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.cp_input = QLineEdit()       # código postal
        self.pais_input = QLineEdit()
        self.telefono_input = QLineEdit()
        # --- FIN NUEVOS CAMPOS ---

        register_button = QPushButton("Crear Cuenta")
        login_button = QPushButton("¿Ya tienes cuenta? Inicia Sesión")

        layout.addRow("Nombre Completo:", self.nombre_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Contraseña:", self.password_input)

        # Añadimos filas para los nuevos campos (concisas)
        layout.addRow("Dirección (calle):", self.direccion_input)
        layout.addRow("Ciudad:", self.ciudad_input)
        layout.addRow("Estado / Provincia:", self.estado_input)
        layout.addRow("Código Postal:", self.cp_input)
        layout.addRow("País:", self.pais_input)
        layout.addRow("Teléfono:", self.telefono_input)

        layout.addRow(register_button)
        layout.addRow(login_button)
        self.setLayout(layout)
        
        # Conexiones de botones
        register_button.clicked.connect(self.handle_register)
        login_button.clicked.connect(self.go_to_login.emit)

    def handle_register(self):
        nombre = self.nombre_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        direccion = self.direccion_input.text().strip()
        ciudad = self.ciudad_input.text().strip()
        estado = self.estado_input.text().strip()
        codigo_postal = self.cp_input.text().strip()
        pais = self.pais_input.text().strip()
        telefono = self.telefono_input.text().strip()

        # Validaciones cliente básicas
        if not nombre or len(nombre) < 2:
            QMessageBox.warning(self, "Error", "El nombre debe tener al menos 2 caracteres.")
            return
        if not email:
            QMessageBox.warning(self, "Error", "El email no puede estar vacío.")
            return
        if not password or len(password) < 6:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres.")
            return
        if codigo_postal and not re.match(r"^[A-Za-z0-9\s\-]{3,10}$", codigo_postal):
            QMessageBox.warning(self, "Error", "Código postal inválido.")
            return
        if telefono and not re.match(r"^\+?[0-9\s\-]{7,20}$", telefono):
            QMessageBox.warning(self, "Error", "Teléfono inválido. Use solo números, espacios, guiones y opcional '+'.")
            return

        register_data = {
            "nombre_completo": nombre,
            "email": email,
            "password": password,
            # Enviamos los campos opcionales de dirección (el backend puede ignorarlos si no está listo)
            "direccion": direccion,
            "ciudad": ciudad,
            "estado": estado,
            "codigo_postal": codigo_postal,
            "pais": pais,
            "telefono": telefono
        }

        # Deshabilita el formulario para evitar doble clic
        self.setEnabled(False)

        # Configura el hilo y el worker
        self.thread = QThread()
        self.worker = NetworkWorker(f"{API_URL}/api/register", "POST_JSON", register_data)
        self.worker.moveToThread(self.thread)

        # Conecta señales
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_register_success)
        self.worker.failure.connect(self.on_register_failure)
        
        # Limpieza
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_register_success(self, response_data):
        self.setEnabled(True) # Reactiva el formulario
        QMessageBox.information(self, "Éxito", response_data.get("message", "¡Usuario registrado!"))
        # Emite la señal para volver al login
        self.register_success.emit()

    def on_register_failure(self, error_message):
        self.setEnabled(True) # Reactiva el formulario
        QMessageBox.critical(self, "Error de Registro", error_message)


# --- Página de Login ---


class VentanaLogin(QWidget):
    login_success = pyqtSignal(dict)
    go_to_register = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None

        layout = QFormLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("tu@email.com")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Iniciar Sesión")
        register_button = QPushButton("¿No tienes cuenta? Regístrate")

        layout.addRow("Email:", self.email_input)
        layout.addRow("Contraseña:", self.password_input)
        layout.addRow(login_button)
        layout.addRow(register_button)
        self.setLayout(layout)

        # Conexiones
        login_button.clicked.connect(self.handle_login)
        register_button.clicked.connect(self.go_to_register.emit)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Email y contraseña no pueden estar vacíos.")
            return

        # Datos para OAuth2PasswordRequestForm (como 'form data')
        login_data = {
            "username": email, # La API espera 'username'
            "password": password
        }
        
        self.setEnabled(False) # Deshabilita formulario

        # Configura y corre el hilo
        self.thread = QThread()
        self.worker = NetworkWorker(f"{API_URL}/api/login", "POST_FORM", login_data)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_login_success)
        self.worker.failure.connect(self.on_login_failure)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()

    def on_login_success(self, response_data):
        self.setEnabled(True)
    # Esperamos {'access_token': '...', 'token_type': 'bearer', 'is_admin': ...}
        if "access_token" in response_data:
            self.login_success.emit(response_data) # ¡Emitimos el dict completo!
        else:
            self.on_login_failure("Respuesta de API inválida (no se recibió token).")
    
    def on_login_failure(self, error_message):
        self.setEnabled(True)
        QMessageBox.critical(self, "Error de Login", error_message)


# --- Ventana Principal (Contenedora) ---

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        # Aplicar estilos globales
        app = QApplication.instance()
        app.setStyleSheet(STYLE)
        
        self.setWindowTitle("Tienda E-Commerce")
        self.setGeometry(100, 100, 400, 250) # Tamaño inicial para login

        self.api_token = None # Aquí guardaremos el token JWT

        # El QStackedWidget es el "mazo de cartas" que contiene nuestras páginas
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Crear las páginas
        self.login_page = VentanaLogin()
        self.register_page = VentanaRegistro()
        self.tienda_page = VentanaTienda()
        self.admin_page = VentanaAdminVentas()
        self.perfil_page = VentanaPerfil()
        self.carrito_page = VentanaCarrito()
        self.admin_productos_page = VentanaAdminProductos()

        # Añadir las páginas al "mazo"
        self.stack.addWidget(self.login_page)     # Índice 0
        self.stack.addWidget(self.register_page)  # Índice 1
        self.stack.addWidget(self.tienda_page)    # Índice 2
        self.stack.addWidget(self.admin_page)     # Índice 3
        self.stack.addWidget(self.perfil_page)    # Índice 4
        self.stack.addWidget(self.carrito_page)   # Índice 5
        self.stack.addWidget(self.admin_productos_page)  # Índice 6

        # --- NUEVO: Crear menú persistente para administradores ---
        self.admin_menu_widget = QWidget()
        admin_menu_layout = QVBoxLayout(self.admin_menu_widget)
        admin_title = QLabel("Panel de Administración")
        admin_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        admin_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        admin_menu_layout.addWidget(admin_title)

        self.admin_ventas_btn = QPushButton("Ver Ventas")
        self.admin_productos_btn = QPushButton("Gestionar Productos")
        admin_menu_layout.addWidget(self.admin_ventas_btn)
        admin_menu_layout.addWidget(self.admin_productos_btn)

        # Añadir el admin_menu al stack (índice siguiente disponible)
        self.stack.addWidget(self.admin_menu_widget)

        # Conectar los botones del menú a las vistas correspondientes
        self.admin_ventas_btn.clicked.connect(self.mostrar_admin_ventas)
        self.admin_productos_btn.clicked.connect(self.mostrar_admin_productos)

        # --- Conectar señales entre páginas y la ventana principal ---
        
        # Botones de navegación
        self.login_page.go_to_register.connect(self.mostrar_registro)
        self.register_page.go_to_login.connect(self.mostrar_login)
        
        self.tienda_page.go_to_profile.connect(self.mostrar_perfil)
        self.tienda_page.go_to_cart.connect(self.mostrar_carrito)

        self.perfil_page.go_to_store.connect(self.mostrar_tienda)
        self.carrito_page.go_to_store.connect(self.mostrar_tienda)
        # Cambiado: cuando admin pulse "Volver" en vistas admin, mostramos el admin_menu
        self.admin_page.go_to_store.connect(self.mostrar_admin_menu)
        self.admin_productos_page.go_to_store.connect(self.mostrar_admin_menu)  # Conexión para la nueva página

        # Lógica de la aplicación
        self.register_page.register_success.connect(self.mostrar_login)
        self.login_page.login_success.connect(self.on_login_exitoso)

        
        # Empezar en la página de Login
        self.mostrar_login()

    def mostrar_login(self):
        self.stack.setCurrentIndex(0)
        self.setWindowTitle("Iniciar Sesión")
        self.resize(400, 250)

    def mostrar_registro(self):
        self.stack.setCurrentIndex(1)
        self.setWindowTitle("Registro de Usuario")
        self.resize(400, 250)

    def mostrar_tienda(self):
        self.stack.setCurrentIndex(2)
        self.setWindowTitle(f"Tienda - ¡Bienvenido!")
        self.resize(800, 600)
        # Pasamos el token a la página de la tienda
        self.tienda_page.set_token(self.api_token)

    def mostrar_admin_ventas(self):
        self.stack.setCurrentIndex(3) # Índice 3 = admin_page
        self.setWindowTitle("Panel de Administración")
        self.resize(800, 600)
        # Pasamos el token a la página de admin
        self.admin_page.set_token(self.api_token)

    def mostrar_admin_productos(self):
        """Muestra la página de gestión de productos."""
        # Ajusta al índice en el que añadiste admin_productos_page (6)
        self.stack.setCurrentIndex(self.stack.indexOf(self.admin_productos_page))
        self.setWindowTitle("Gestión de Productos")
        self.resize(800, 600)
        self.admin_productos_page.set_token(self.api_token)

    # NUEVO: Método para mostrar el menú de administración
    def mostrar_admin_menu(self):
        """Muestra el menú principal de administración."""
        self.stack.setCurrentWidget(self.admin_menu_widget)
        self.setWindowTitle("Panel de Administración")
        self.resize(600, 400)

    def mostrar_perfil(self):
        self.stack.setCurrentIndex(4) # Índice 4 = perfil_page
        self.setWindowTitle("Mi Perfil")
        self.resize(500, 300) # Un tamaño más pequeño para el perfil
        # Pasamos el token y pedimos los datos
        self.perfil_page.set_token(self.api_token)

    def mostrar_carrito(self):
        self.stack.setCurrentIndex(5) # Índice 5 = carrito_page
        self.setWindowTitle("Mi Carrito")
        self.resize(600, 400) # Un tamaño más adecuado para el carrito
        # Pasamos el token y pedimos los datos
        self.carrito_page.set_token(self.api_token)

    

    def on_login_exitoso(self, login_data: dict):
        """
        Se llama cuando el login es exitoso.
        Recibe el dict de login y decide a dónde enrutar.
        """
        self.api_token = login_data.get("access_token")
        is_admin = login_data.get("is_admin", False)

        print(f"Login exitoso. Token guardado. Es Admin: {is_admin}")

        if is_admin:
            # Mostrar el menú persistente de admin (en lugar de crear uno local)
            self.mostrar_admin_menu()
        else:
            self.mostrar_tienda()   

class VentanaTienda(QWidget):
    """Página principal de la tienda."""
    go_to_profile = pyqtSignal() # Señal para ir al perfil
    go_to_cart = pyqtSignal()    # Señal para ir al carrito
    
    def __init__(self):
        super().__init__()
        self.api_token = None
        self.thread = None
        self.worker = None

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Botones de Navegación ---
        nav_layout = QHBoxLayout()
        self.profile_button = QPushButton("Mi Perfil")
        self.cart_button = QPushButton("Mi Carrito")
        nav_layout.addWidget(self.profile_button)
        nav_layout.addWidget(self.cart_button)
        main_layout.addLayout(nav_layout)
        
        self.profile_button.clicked.connect(self.go_to_profile.emit)
        self.cart_button.clicked.connect(self.go_to_cart.emit)
        # --- Fin de botones ---
        
        self.info_label = QLabel("Cargando productos...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        # --- Área de Scroll para Productos ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(scroll_area)
        
        # Widget contenedor para los productos (irá dentro del scroll)
        self.products_widget = QWidget()
        scroll_area.setWidget(self.products_widget)
        
        # Layout para la lista de productos
        self.products_layout = QVBoxLayout(self.products_widget)
        self.products_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        

    def set_token(self, token: str):
        """Recibe el token de la ventana principal y pide los productos."""
        self.api_token = token
        print(f"VentanaTienda: Token recibido. Pidiendo productos...")
        self.fetch_products()

    def fetch_products(self):
        self.info_label.setText("Cargando productos...")
        self.info_label.show() # Muestra "Cargando..."
        
        # Limpia productos antiguos (si los hubiera)
        while self.products_layout.count():
            child = self.products_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # DEBUG: mostrar info útil para depuración
        print(f"[VentanaTienda] GET {API_URL}/api/products token_present={bool(self.api_token)}")
        
        # Configura el hilo y el worker
        self.thread = QThread()
        # ¡Usamos el método GET_AUTH y pasamos el token!
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

    def on_fetch_success(self, products_list: list):
        """Se llama cuando la API devuelve la lista de productos."""
        self.info_label.hide()
        
        if not products_list:
            self.info_label.setText("No hay productos disponibles en este momento.")
            self.info_label.show()
            return

        # Crea un widget para cada producto
        for product in products_list:
            # Crear un frame contenedor para el producto
            product_frame = QFrame()
            product_frame.setFrameShape(QFrame.Shape.Box)
            product_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #ecf0f1;
                    margin: 5px;
                }
            """)
            
            # Layout vertical para el producto
            product_layout = QVBoxLayout(product_frame)
            
            # Información del producto con HTML para mejor formato
            info_text = f"""
                <h3>{product['nombre']}</h3>
                <p>{product['descripcion'] or 'Sin descripción'}</p>
                <p><b>Precio: ${product['precio']:.2f}</b></p>
                <p>Stock disponible: {product['stock']}</p>
            """
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setTextFormat(Qt.TextFormat.RichText)
            product_layout.addWidget(info_label)
            
            # --- Mostrar imagen si hay URL ---
            if product.get("imagen_url"):
                try:
                    data = urllib.request.urlopen(product["imagen_url"]).read()
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    img_label = QLabel()
                    img_label.setPixmap(pixmap.scaledToWidth(120))
                    product_layout.addWidget(img_label)
                except Exception:
                    img_label = QLabel("(Imagen no disponible)")
                    product_layout.addWidget(img_label)
            # --- Fin imagen ---
            
            # Contenedor horizontal para cantidad y botón
            controls_layout = QHBoxLayout()
            
            # Spinner para la cantidad
            cantidad_spin = QSpinBox()
            cantidad_spin.setMinimum(1)
            cantidad_spin.setMaximum(min(10, product['stock']))  # Máximo 10 o el stock disponible
            cantidad_spin.setValue(1)
            cantidad_spin.setPrefix("Cantidad: ")
            controls_layout.addWidget(cantidad_spin)
            
            # Botón de añadir al carrito
            add_button = QPushButton("🛒 Añadir al Carrito")
            add_button.setEnabled(product['stock'] > 0)
            if product['stock'] > 0:
                add_button.clicked.connect(
                    lambda checked, p=product, spin=cantidad_spin: 
                    self.handle_add_to_cart(p, spin.value())
                )
            else:
                add_button.setText("Sin Stock")
                add_button.setStyleSheet("background-color: #ffebee;")
            
            controls_layout.addWidget(add_button)
            product_layout.addLayout(controls_layout)
            
            # Añadir el frame del producto al layout principal
            self.products_layout.addWidget(product_frame)

    def handle_add_to_cart(self, product: dict, cantidad: int):
        """Envía petición para añadir producto al carrito (API)."""
        if cantidad <= 0:
            QMessageBox.warning(self, "Error", "Cantidad inválida.")
            return
        add_data = {"product_id": product["id"], "cantidad": cantidad}
        self.thread = QThread()
        self.worker = NetworkWorker(
            f"{API_URL}/api/cart/add",
            "POST_AUTH",
            data=add_data,
            token=self.api_token
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_add_to_cart_success)
        self.worker.failure.connect(self.on_add_to_cart_failure)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_add_to_cart_success(self, cart_data):
        QMessageBox.information(self, "Carrito", f"Producto añadido al carrito. Total del carrito: ${cart_data.get('total', 0):.2f}")

    def on_add_to_cart_failure(self, error_message):
        QMessageBox.critical(self, "Error al añadir", error_message)

    def on_fetch_failure(self, error_message):
        """Se llama si la API falla."""
        self.info_label.setText(f"Error al cargar productos: {error_message}")
        self.info_label.show()
        QMessageBox.critical(self, "Error de Red", error_message)


# --- Estilos globales ---

# Paleta de colores minimalista
STYLE = """
/* Paleta de colores */
QWidget {
    background-color: #ffffff;
    color: #2c3e50;
    font-family: Arial, sans-serif;
}

/* Botones */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:disabled {
    background-color: #bdc3c7;
}

/* Botones especiales */
QPushButton#checkout_btn {
    background-color: #2ecc71;
}

QPushButton#checkout_btn:hover {
    background-color: #27ae60;
}

/* Campos de texto */
QLineEdit {
    padding: 8px;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    background-color: #f8f9fa;
}

QLineEdit:focus {
    border: 2px solid #3498db;
}

/* Frame de productos/items */
QFrame {
    background-color: #ffffff;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
}

/* Labels de título */
QLabel[title="true"] {
    color: #2c3e50;
    font-size: 20px;
    font-weight: bold;
    padding: 10px;
}

/* Spinbox */
QSpinBox {
    padding: 5px;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
}

/* ScrollArea */
QScrollArea {
    border: none;
}

/* Warning label */
QLabel#warning_label {
    color: #e74c3c;
    font-weight: bold;
}

/* Success message */
QLabel#success_label {
    color: #27ae60;
    font-weight: bold;
}
"""

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        # Aplicar estilos globales
        app = QApplication.instance()
        app.setStyleSheet(STYLE)
        
        self.setWindowTitle("Tienda E-Commerce")
        self.setGeometry(100, 100, 400, 250) # Tamaño inicial para login

        self.api_token = None # Aquí guardaremos el token JWT

        # El QStackedWidget es el "mazo de cartas" que contiene nuestras páginas
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Crear las páginas
        self.login_page = VentanaLogin()
        self.register_page = VentanaRegistro()
        self.tienda_page = VentanaTienda()
        self.admin_page = VentanaAdminVentas()
        self.perfil_page = VentanaPerfil()
        self.carrito_page = VentanaCarrito()
        self.admin_productos_page = VentanaAdminProductos()

        # Añadir las páginas al "mazo"
        self.stack.addWidget(self.login_page)     # Índice 0
        self.stack.addWidget(self.register_page)  # Índice 1
        self.stack.addWidget(self.tienda_page)    # Índice 2
        self.stack.addWidget(self.admin_page)     # Índice 3
        self.stack.addWidget(self.perfil_page)    # Índice 4
        self.stack.addWidget(self.carrito_page)   # Índice 5
        self.stack.addWidget(self.admin_productos_page)  # Índice 6

        # --- NUEVO: Crear menú persistente para administradores ---
        self.admin_menu_widget = QWidget()
        admin_menu_layout = QVBoxLayout(self.admin_menu_widget)
        admin_title = QLabel("Panel de Administración")
        admin_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        admin_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        admin_menu_layout.addWidget(admin_title)

        self.admin_ventas_btn = QPushButton("Ver Ventas")
        self.admin_productos_btn = QPushButton("Gestionar Productos")
        admin_menu_layout.addWidget(self.admin_ventas_btn)
        admin_menu_layout.addWidget(self.admin_productos_btn)

        # Añadir el admin_menu al stack (índice siguiente disponible)
        self.stack.addWidget(self.admin_menu_widget)

        # Conectar los botones del menú a las vistas correspondientes
        self.admin_ventas_btn.clicked.connect(self.mostrar_admin_ventas)
        self.admin_productos_btn.clicked.connect(self.mostrar_admin_productos)

        # --- Conectar señales entre páginas y la ventana principal ---
        
        # Botones de navegación
        self.login_page.go_to_register.connect(self.mostrar_registro)
        self.register_page.go_to_login.connect(self.mostrar_login)
        
        self.tienda_page.go_to_profile.connect(self.mostrar_perfil)
        self.tienda_page.go_to_cart.connect(self.mostrar_carrito)

        self.perfil_page.go_to_store.connect(self.mostrar_tienda)
        self.carrito_page.go_to_store.connect(self.mostrar_tienda)
        # Cambiado: cuando admin pulse "Volver" en vistas admin, mostramos el admin_menu
        self.admin_page.go_to_store.connect(self.mostrar_admin_menu)
        self.admin_productos_page.go_to_store.connect(self.mostrar_admin_menu)  # Conexión para la nueva página

        # Lógica de la aplicación
        self.register_page.register_success.connect(self.mostrar_login)
        self.login_page.login_success.connect(self.on_login_exitoso)

        
        # Empezar en la página de Login
        self.mostrar_login()

    def mostrar_login(self):
        self.stack.setCurrentIndex(0)
        self.setWindowTitle("Iniciar Sesión")
        self.resize(400, 250)

    def mostrar_registro(self):
        self.stack.setCurrentIndex(1)
        self.setWindowTitle("Registro de Usuario")
        self.resize(400, 250)

    def mostrar_tienda(self):
        self.stack.setCurrentIndex(2)
        self.setWindowTitle(f"Tienda - ¡Bienvenido!")
        self.resize(800, 600)
        # Pasamos el token a la página de la tienda
        self.tienda_page.set_token(self.api_token)

    def mostrar_admin_ventas(self):
        self.stack.setCurrentIndex(3) # Índice 3 = admin_page
        self.setWindowTitle("Panel de Administración")
        self.resize(800, 600)
        # Pasamos el token a la página de admin
        self.admin_page.set_token(self.api_token)

    def mostrar_admin_productos(self):
        """Muestra la página de gestión de productos."""
        # Ajusta al índice en el que añadiste admin_productos_page (6)
        self.stack.setCurrentIndex(self.stack.indexOf(self.admin_productos_page))
        self.setWindowTitle("Gestión de Productos")
        self.resize(800, 600)
        self.admin_productos_page.set_token(self.api_token)

    # NUEVO: Método para mostrar el menú de administración
    def mostrar_admin_menu(self):
        """Muestra el menú principal de administración."""
        self.stack.setCurrentWidget(self.admin_menu_widget)
        self.setWindowTitle("Panel de Administración")
        self.resize(600, 400)

    def mostrar_perfil(self):
        self.stack.setCurrentIndex(4) # Índice 4 = perfil_page
        self.setWindowTitle("Mi Perfil")
        self.resize(500, 300) # Un tamaño más pequeño para el perfil
        # Pasamos el token y pedimos los datos
        self.perfil_page.set_token(self.api_token)

    def mostrar_carrito(self):
        self.stack.setCurrentIndex(5) # Índice 5 = carrito_page
        self.setWindowTitle("Mi Carrito")
        self.resize(600, 400) # Un tamaño más adecuado para el carrito
        # Pasamos el token y pedimos los datos
        self.carrito_page.set_token(self.api_token)

    

    def on_login_exitoso(self, login_data: dict):
        """
        Se llama cuando el login es exitoso.
        Recibe el dict de login y decide a dónde enrutar.
        """
        self.api_token = login_data.get("access_token")
        is_admin = login_data.get("is_admin", False)

        print(f"Login exitoso. Token guardado. Es Admin: {is_admin}")

        if is_admin:
            # Mostrar el menú persistente de admin (en lugar de crear uno local)
            self.mostrar_admin_menu()
        else:
            self.mostrar_tienda()   

class VentanaTienda(QWidget):
    """Página principal de la tienda."""
    go_to_profile = pyqtSignal() # Señal para ir al perfil
    go_to_cart = pyqtSignal()    # Señal para ir al carrito
    
    def __init__(self):
        super().__init__()
        self.api_token = None
        self.thread = None
        self.worker = None

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Botones de Navegación ---
        nav_layout = QHBoxLayout()
        self.profile_button = QPushButton("Mi Perfil")
        self.cart_button = QPushButton("Mi Carrito")
        nav_layout.addWidget(self.profile_button)
        nav_layout.addWidget(self.cart_button)
        main_layout.addLayout(nav_layout)
        
        self.profile_button.clicked.connect(self.go_to_profile.emit)
        self.cart_button.clicked.connect(self.go_to_cart.emit)
        # --- Fin de botones ---
        
        self.info_label = QLabel("Cargando productos...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        # --- Área de Scroll para Productos ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(scroll_area)
        
        # Widget contenedor para los productos (irá dentro del scroll)
        self.products_widget = QWidget()
        scroll_area.setWidget(self.products_widget)
        
        # Layout para la lista de productos
        self.products_layout = QVBoxLayout(self.products_widget)
        self.products_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        

    def set_token(self, token: str):
        """Recibe el token de la ventana principal y pide los productos."""
        self.api_token = token
        print(f"VentanaTienda: Token recibido. Pidiendo productos...")
        self.fetch_products()

    def fetch_products(self):
        self.info_label.setText("Cargando productos...")
        self.info_label.show() # Muestra "Cargando..."
        
        # Limpia productos antiguos (si los hubiera)
        while self.products_layout.count():
            child = self.products_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # DEBUG: mostrar info útil para depuración
        print(f"[VentanaTienda] GET {API_URL}/api/products token_present={bool(self.api_token)}")
        
        # Configura el hilo y el worker
        self.thread = QThread()
        # ¡Usamos el método GET_AUTH y pasamos el token!
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

    def on_fetch_success(self, products_list: list):
        """Se llama cuando la API devuelve la lista de productos."""
        self.info_label.hide()
        
        if not products_list:
            self.info_label.setText("No hay productos disponibles en este momento.")
            self.info_label.show()
            return

        # Crea un widget para cada producto
        for product in products_list:
            # Crear un frame contenedor para el producto
            product_frame = QFrame()
            product_frame.setFrameShape(QFrame.Shape.Box)
            product_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #ecf0f1;
                    margin: 5px;
                }
            """)
            
            # Layout vertical para el producto
            product_layout = QVBoxLayout(product_frame)
            
            # Información del producto con HTML para mejor formato
            info_text = f"""
                <h3>{product['nombre']}</h3>
                <p>{product['descripcion'] or 'Sin descripción'}</p>
                <p><b>Precio: ${product['precio']:.2f}</b></p>
                <p>Stock disponible: {product['stock']}</p>
            """
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setTextFormat(Qt.TextFormat.RichText)
            product_layout.addWidget(info_label)
            
            # --- Mostrar imagen si hay URL ---
            if product.get("imagen_url"):
                try:
                    data = urllib.request.urlopen(product["imagen_url"]).read()
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    img_label = QLabel()
                    img_label.setPixmap(pixmap.scaledToWidth(120))
                    product_layout.addWidget(img_label)
                except Exception:
                    img_label = QLabel("(Imagen no disponible)")
                    product_layout.addWidget(img_label)
            # --- Fin imagen ---
            
            # Contenedor horizontal para cantidad y botón
            controls_layout = QHBoxLayout()
            
            # Spinner para la cantidad
            cantidad_spin = QSpinBox()
            cantidad_spin.setMinimum(1)
            cantidad_spin.setMaximum(min(10, product['stock']))  # Máximo 10 o el stock disponible
            cantidad_spin.setValue(1)
            cantidad_spin.setPrefix("Cantidad: ")
            controls_layout.addWidget(cantidad_spin)
            
            # Botón de añadir al carrito
            add_button = QPushButton("🛒 Añadir al Carrito")
            add_button.setEnabled(product['stock'] > 0)
            if product['stock'] > 0:
                add_button.clicked.connect(
                    lambda checked, p=product, spin=cantidad_spin: 
                    self.handle_add_to_cart(p, spin.value())
                )
            else:
                add_button.setText("Sin Stock")
                add_button.setStyleSheet("background-color: #ffebee;")
            
            controls_layout.addWidget(add_button)
            product_layout.addLayout(controls_layout)
            
            # Añadir el frame del producto al layout principal
            self.products_layout.addWidget(product_frame)

    def handle_add_to_cart(self, product: dict, cantidad: int):
        """Envía petición para añadir producto al carrito (API)."""
        if cantidad <= 0:
            QMessageBox.warning(self, "Error", "Cantidad inválida.")
            return
        add_data = {"product_id": product["id"], "cantidad": cantidad}
        self.thread = QThread()
        self.worker = NetworkWorker(
            f"{API_URL}/api/cart/add",
            "POST_AUTH",
            data=add_data,
            token=self.api_token
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_add_to_cart_success)
        self.worker.failure.connect(self.on_add_to_cart_failure)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_add_to_cart_success(self, cart_data):
        QMessageBox.information(self, "Carrito", f"Producto añadido al carrito. Total del carrito: ${cart_data.get('total', 0):.2f}")

    def on_add_to_cart_failure(self, error_message):
        QMessageBox.critical(self, "Error al añadir", error_message)

    def on_fetch_failure(self, error_message):
        """Se llama si la API falla."""
        self.info_label.setText(f"Error al cargar productos: {error_message}")
        self.info_label.show()
        QMessageBox.critical(self, "Error de Red", error_message)


class VentanaPerfil(QWidget):
    """Página para ver y actualizar el perfil del usuario."""
    go_to_store = pyqtSignal() # Señal para volver a la tienda

    def __init__(self):
        super().__init__()
        self.api_token = None
        self.thread = None
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel("MI PERFIL")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # Formulario para los datos
        form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.email_input = QLineEdit()
        self.direccion_input = QLineEdit()   # calle / dirección
        self.ciudad_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.cp_input = QLineEdit()          # codigo postal
        self.pais_input = QLineEdit()
        self.telefono_input = QLineEdit()

        self.info_label = QLabel("Cargando perfil...")
        
        form_layout.addRow(self.info_label)
        form_layout.addRow("Nombre Completo:", self.nombre_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Dirección (calle):", self.direccion_input)
        form_layout.addRow("Ciudad:", self.ciudad_input)
        form_layout.addRow("Estado / Provincia:", self.estado_input)
        form_layout.addRow("Código Postal:", self.cp_input)
        form_layout.addRow("País:", self.pais_input)
        form_layout.addRow("Teléfono:", self.telefono_input)
        
        layout.addLayout(form_layout)

        # Botones
        self.save_button = QPushButton("Guardar Cambios")
        self.save_button.setEnabled(False) # Deshabilitado hasta que carguen los datos
        self.back_button = QPushButton("Volver a la Tienda")
        
        layout.addWidget(self.save_button)
        layout.addWidget(self.back_button)
        
        # Conexiones
        self.save_button.clicked.connect(self.handle_save_profile)
        self.back_button.clicked.connect(self.go_to_store.emit)

    def set_token(self, token: str):
        """Recibe el token y pide los datos del perfil."""
        self.api_token = token
        print(f"VentanaPerfil: Token recibido. Pidiendo perfil...")
        self.fetch_profile()

    def fetch_profile(self):
        """Busca los datos del perfil (GET)."""
        self.info_label.setText("Cargando perfil...")
        self.save_button.setEnabled(False)
        self.info_label.show()
        
        self.thread = QThread()
        self.worker = NetworkWorker(
            f"{API_URL}/api/profile", 
            "GET_AUTH", 
            token=self.api_token
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_fetch_success)
        self.worker.failure.connect(self.on_fetch_failure)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_fetch_success(self, profile_data: dict):
        """Rellena los campos cuando la API responde."""
        self.info_label.hide()
        self.nombre_input.setText(profile_data.get("nombre_completo", ""))
        self.email_input.setText(profile_data.get("email", ""))
        # Nuevos campos
        self.direccion_input.setText(profile_data.get("direccion", "") or "")
        self.ciudad_input.setText(profile_data.get("ciudad", "") or "")
        self.estado_input.setText(profile_data.get("estado", "") or "")
        self.cp_input.setText(profile_data.get("codigo_postal", "") or "")
        self.pais_input.setText(profile_data.get("pais", "") or "")
        self.telefono_input.setText(profile_data.get("telefono", "") or "")
        self.save_button.setEnabled(True)
        
    def on_fetch_failure(self, error_message):
        """Manejador cuando falla la carga del perfil (muestra error y deshabilita guardar)."""
        self.info_label.setText(f"Error al cargar perfil: {error_message}")
        self.save_button.setEnabled(False)
        QMessageBox.critical(self, "Error al cargar perfil", error_message)
	
    def handle_save_profile(self):
        """Envía los datos actualizados (PUT)."""
        nombre = self.nombre_input.text()
        email = self.email_input.text()

        # Recoger campos de dirección
        direccion = self.direccion_input.text()
        ciudad = self.ciudad_input.text()
        estado = self.estado_input.text()
        codigo_postal = self.cp_input.text()
        pais = self.pais_input.text()
        telefono = self.telefono_input.text()

        # Validaciones cliente
        if not nombre or len(nombre.strip()) < 2:
            QMessageBox.warning(self, "Error", "El nombre debe tener al menos 2 caracteres.")
            return
        if not email:
            QMessageBox.warning(self, "Error", "El email no puede estar vacío.")
            return
        if codigo_postal and not re.match(r"^[A-Za-z0-9\s\-]{3,10}$", codigo_postal):
            QMessageBox.warning(self, "Error", "Código postal inválido.")
            return
        if telefono and not re.match(r"^\+?[0-9\s\-]{7,20}$", telefono):
            QMessageBox.warning(self, "Error", "Teléfono inválido. Use solo números, espacios, guiones y opcional '+'.")
            return

        update_data = {
            "nombre_completo": nombre,
            "email": email,
            "direccion": direccion,
            "ciudad": ciudad,
            "estado": estado,
            "codigo_postal": codigo_postal,
            "pais": pais,
            "telefono": telefono
        }
        
        self.save_button.setText("Guardando...")
        self.save_button.setEnabled(False)

        self.thread = QThread()
        self.worker = NetworkWorker(
            f"{API_URL}/api/profile", 
            "PUT_AUTH",
            data=update_data,
            token=self.api_token
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_save_success)
        self.worker.failure.connect(self.on_save_failure)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_save_success(self, new_profile_data: dict):
        self.save_button.setText("Guardar Cambios")
        self.save_button.setEnabled(True)
        QMessageBox.information(self, "Éxito", "¡Perfil actualizado correctamente!")
        # Actualizamos los campos por si la API hizo alguna normalización
        self.nombre_input.setText(new_profile_data.get("nombre_completo", ""))
        self.email_input.setText(new_profile_data.get("email", ""))
        self.direccion_input.setText(new_profile_data.get("direccion", "") or "")
        self.ciudad_input.setText(new_profile_data.get("ciudad", "") or "")
        self.estado_input.setText(new_profile_data.get("estado", "") or "")
        self.cp_input.setText(new_profile_data.get("codigo_postal", "") or "")
        self.pais_input.setText(new_profile_data.get("pais", "") or "")
        self.telefono_input.setText(new_profile_data.get("telefono", "") or "")

    def on_save_failure(self, error_message):
        self.save_button.setText("Guardar Cambios")
        self.save_button.setEnabled(True)
        QMessageBox.critical(self, "Error al Guardar", error_message)


# --- Punto de entrada de la aplicación ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())