import sys
import threading
import uvicorn
import time
import httpx

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMenuBar, QMessageBox, QPushButton
)
from PyQt6.QtGui import QIcon, QAction

from db import verificar_conexion
from login.login_widget import LoginWidget
from clientes.clientes_widget import ClientesWidget
from productos.productos_widget import ProductosWidget
from ventas.ventas_widget import VentasWidget
from carrito.carrito_widget import CarritoWidget


class VentanaPrincipal(QMainWindow):
    def __init__(self, tipo_usuario="admin", user_id=None):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión - Tienda de Ropa")
        self.setGeometry(100, 100, 1000, 600)
        self.user_id = user_id
        self.carrito = []  # Inicializar el carrito

        # Contenedor central
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Widgets de cada módulo
        self.clientes_widget = ClientesWidget(tipo_usuario)
        self.productos_widget = ProductosWidget(tipo_usuario, self.user_id, self)
        self.ventas_widget = VentasWidget()
        self.carrito_widget = CarritoWidget(self)

        # Agregar al stacked
        self.stacked.addWidget(self.clientes_widget)   # index 0
        self.stacked.addWidget(self.productos_widget)  # index 1
        self.stacked.addWidget(self.ventas_widget)     # index 2
        self.stacked.addWidget(self.carrito_widget)    # index 3

        # Menú
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        # Menú de Módulos
        menu_modulos = self.menu_bar.addMenu("&Módulos")

        action_clientes = QAction(QIcon("assets/icons/clientes.png"), "Clientes", self)
        action_clientes.triggered.connect(lambda: self.stacked.setCurrentWidget(self.clientes_widget))
        menu_modulos.addAction(action_clientes)

        action_productos = QAction(QIcon("assets/icons/productos.png"), "Productos", self)
        action_productos.triggered.connect(lambda: self.stacked.setCurrentWidget(self.productos_widget))
        menu_modulos.addAction(action_productos)

        action_ventas = QAction(QIcon("assets/icons/ventas.png"), "Ventas", self)
        action_ventas.triggered.connect(lambda: self.stacked.setCurrentWidget(self.ventas_widget))
        menu_modulos.addAction(action_ventas)

        # Acción Carrito (solo para clientes)
        action_carrito = QAction(QIcon("assets/icons/ventas.png"), "Carrito", self)
        def abrir_carrito():
            self.stacked.setCurrentWidget(self.carrito_widget)
            self.carrito_widget.refrescar_carrito()
        action_carrito.triggered.connect(abrir_carrito)
        menu_modulos.addAction(action_carrito)

        # Menú de Archivo
        menu_archivo = self.menu_bar.addMenu("&Archivo")
        action_salir = QAction("Salir", self)
        action_salir.triggered.connect(self.close)
        menu_archivo.addAction(action_salir)

        # Control de permisos según tipo de usuario
        if tipo_usuario == "cliente":
            action_clientes.setVisible(False)
            action_ventas.setVisible(False)
            self.stacked.setCurrentWidget(self.productos_widget)
        else:
            action_carrito.setVisible(False)
            self.stacked.setCurrentWidget(self.clientes_widget)

        # Mensaje de bienvenida
        QMessageBox.information(self, "Bienvenido", f"Has iniciado sesión como {tipo_usuario}")

def run_api():
    uvicorn.run("api.app:app", host="127.0.0.1", port=8000)

def main():
    # Iniciar la API en un hilo separado
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True
    api_thread.start()

    app = QApplication(sys.argv)

    # Esperar a que la API esté lista
    api_url = "http://127.0.0.1:8000"
    api_ready = False
    retries = 5
    while not api_ready and retries > 0:
        try:
            response = httpx.get(f"{api_url}/docs")
            if response.status_code == 200:
                api_ready = True
                print("API está lista.")
            else:
                raise httpx.RequestError("")
        except httpx.RequestError:
            print(f"Esperando a la API... {retries} reintentos restantes.")
            time.sleep(1)
            retries -= 1

    if not api_ready:
        QMessageBox.critical(None, "Error de API", "No se pudo conectar con la API local. La aplicación se cerrará.")
        sys.exit(1)

    if not verificar_conexion():
        QMessageBox.critical(None, "Error de Conexión",
                             "No se pudo conectar a la base de datos. La aplicación se cerrará.")
        sys.exit(1)

    ventana_principal = None

    def on_login_success(user_type, user_id):
        nonlocal ventana_principal
        login_widget.close()
        ventana_principal = VentanaPrincipal(tipo_usuario=user_type, user_id=user_id)
        ventana_principal.show()

    login_widget = LoginWidget()
    login_widget.login_exitoso.connect(on_login_success)
    login_widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
