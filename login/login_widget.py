from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, Qt
from login.auth_service import autenticar_usuario
from login.registro_widget import RegistroWidget


class LoginWidget(QWidget):
    # Señal que se emitirá con el rol (str) y el id (int) del usuario
    login_exitoso = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión - Tienda de Ropa")
        self.setGeometry(300, 300, 350, 250)
        self.registro_widget = None  # Para evitar múltiples ventanas de registro
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("assets/images/logo.png")
        logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Título
        layout.addWidget(QLabel("<h2>Bienvenido</h2>"))

        # Campos de entrada
        self.correo = QLineEdit()
        self.correo.setPlaceholderText("Correo electrónico")

        self.contraseña = QLineEdit()
        self.contraseña.setPlaceholderText("Contraseña")
        self.contraseña.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.correo)
        layout.addWidget(self.contraseña)

        # Botones
        botones_layout = QHBoxLayout()
        btn_login = QPushButton("Iniciar Sesión")
        btn_login.clicked.connect(self.intentar_login)
        
        btn_registro = QPushButton("Registrarse")
        btn_registro.clicked.connect(self.abrir_registro)

        botones_layout.addWidget(btn_login)
        botones_layout.addWidget(btn_registro)
        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def intentar_login(self):
        correo = self.correo.text().strip()
        contraseña = self.contraseña.text().strip()

        resultado = autenticar_usuario(correo, contraseña)

        if resultado:
            rol, user_id = resultado
            self.login_exitoso.emit(rol, user_id)  # Emitir la señal con rol e id
        else:
            QMessageBox.warning(self, "Error", "Correo o contraseña incorrectos.")

    def abrir_registro(self):
        if not self.registro_widget or not self.registro_widget.isVisible():
            self.registro_widget = RegistroWidget()
            self.registro_widget.show()