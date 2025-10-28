from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from login.auth_service import registrar_usuario, usuario_existe

class RegistroWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Nuevo Usuario")
        self.setGeometry(350, 350, 350, 250)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Título
        layout.addWidget(QLabel("<h3>Crear Nueva Cuenta</h3>"))

        # Campos de entrada
        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre completo")
        
        self.correo = QLineEdit()
        self.correo.setPlaceholderText("Correo electrónico")

        self.contraseña = QLineEdit()
        self.contraseña.setPlaceholderText("Contraseña")
        self.contraseña.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.confirmar_contraseña = QLineEdit()
        self.confirmar_contraseña.setPlaceholderText("Confirmar contraseña")
        self.confirmar_contraseña.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.nombre)
        layout.addWidget(self.correo)
        layout.addWidget(self.contraseña)
        layout.addWidget(self.confirmar_contraseña)

        # Botón de registro
        btn_registrar = QPushButton("Registrar")
        btn_registrar.clicked.connect(self.intentar_registro)
        layout.addWidget(btn_registrar)

        self.setLayout(layout)

    def intentar_registro(self):
        nombre = self.nombre.text().strip()
        correo = self.correo.text().strip()
        contraseña = self.contraseña.text().strip()
        confirmar_contraseña = self.confirmar_contraseña.text().strip()

        # Validaciones
        if not all([nombre, correo, contraseña, confirmar_contraseña]):
            QMessageBox.warning(self, "Campos incompletos", "Por favor, rellena todos los campos.")
            return

        if contraseña != confirmar_contraseña:
            QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
            return
            
        if len(contraseña) < 6:
            QMessageBox.warning(self, "Contraseña Débil", "La contraseña debe tener al menos 6 caracteres.")
            return

        if usuario_existe(correo):
            QMessageBox.warning(self, "Correo en uso", "El correo electrónico ya está registrado.")
            return

        # Registrar usuario
        if registrar_usuario(nombre, correo, contraseña):
            QMessageBox.information(self, "Registro Exitoso", "¡Tu cuenta ha sido creada! Ahora puedes iniciar sesión.")
            self.close()
        else:
            QMessageBox.critical(self, "Error de Registro", "Ocurrió un error inesperado al registrar el usuario.")
