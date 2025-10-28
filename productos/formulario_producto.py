from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox,
    QSpinBox, QPushButton, QComboBox
)


class FormularioProducto(QDialog):
    def __init__(self, nombre="", descripcion="", precio=0.0, stock=0, talla="", categoria=""):
        """
        Formulario para agregar o editar un producto.
        Si se pasan valores, se usan para precargar los campos (modo edición).
        """
        super().__init__()
        self.setWindowTitle("Formulario Producto")
        self.setGeometry(200, 200, 400, 300)
        self.initUI(nombre, descripcion, precio, stock, talla, categoria)

    def initUI(self, nombre, descripcion, precio, stock, talla, categoria):
        layout = QFormLayout()

        # Campos de entrada
        self.input_nombre = QLineEdit(nombre)
        self.input_descripcion = QLineEdit(descripcion)

        self.input_precio = QDoubleSpinBox()
        self.input_precio.setRange(0, 100000)
        self.input_precio.setDecimals(2)
        self.input_precio.setValue(precio)

        self.input_stock = QSpinBox()
        self.input_stock.setRange(0, 10000)
        self.input_stock.setValue(stock)

        self.input_talla = QComboBox()
        self.input_talla.addItems(["XS", "S", "M", "L", "XL", "XXL"])
        if talla in ["XS", "S", "M", "L", "XL", "XXL"]:
            self.input_talla.setCurrentText(talla)

        self.input_categoria = QLineEdit(categoria)

        # Agregar al layout
        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Descripción:", self.input_descripcion)
        layout.addRow("Precio:", self.input_precio)
        layout.addRow("Stock:", self.input_stock)
        layout.addRow("Talla:", self.input_talla)
        layout.addRow("Categoría:", self.input_categoria)

        # Botón de guardar
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.accept)
        layout.addRow(btn_guardar)

        self.setLayout(layout)

    def get_datos(self):
        """
        Devuelve los datos ingresados en el formulario como tupla.
        """
        return (
            self.input_nombre.text().strip(),
            self.input_descripcion.text().strip(),
            float(self.input_precio.value()),
            int(self.input_stock.value()),
            self.input_talla.currentText(),
            self.input_categoria.text().strip()
        )