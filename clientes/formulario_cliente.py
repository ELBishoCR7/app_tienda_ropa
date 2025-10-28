from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton
)


class FormularioCliente(QDialog):
    def __init__(self, nombre: str = "", correo: str = "", telefono: str = "", direccion: str = ""):
        """
        Formulario para agregar o editar un cliente.
        Si se pasan valores, se usan para precargar los campos (modo edición).
        """
        super().__init__()
        self.setWindowTitle("Formulario Cliente")
        self.setGeometry(200, 200, 400, 250)
        self.initUI(nombre, correo, telefono, direccion)

    def initUI(self, nombre, correo, telefono, direccion):
        layout = QFormLayout()

        # Campos de entrada
        self.input_nombre = QLineEdit(nombre)
        self.input_correo = QLineEdit(correo)
        self.input_telefono = QLineEdit(telefono)
        self.input_direccion = QLineEdit(direccion)

        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Correo:", self.input_correo)
        layout.addRow("Teléfono:", self.input_telefono)
        layout.addRow("Dirección:", self.input_direccion)

        # Botón de guardar
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.accept)  # Cierra el diálogo con estado "aceptado"
        layout.addRow(btn_guardar)

        self.setLayout(layout)

    def get_datos(self):
        """
        Devuelve los datos ingresados en el formulario como tupla.
        """
        return (
            self.input_nombre.text().strip(),
            self.input_correo.text().strip(),
            self.input_telefono.text().strip(),
            self.input_direccion.text().strip()
        )