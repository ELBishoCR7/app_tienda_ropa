from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QHeaderView
)
from clientes.clientes_service import (
    obtener_clientes, crear_cliente, actualizar_cliente, eliminar_cliente
)
from .formulario_cliente import FormularioCliente

class ClientesWidget(QWidget):
    def __init__(self, tipo_usuario="admin"):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes")
        self.setGeometry(150, 150, 800, 400)
        self.tipo_usuario = tipo_usuario
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Tabla de clientes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Correo", "Teléfono", "Dirección"])
        # Mejoras en la tabla
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

        # Botones
        botones_layout = QHBoxLayout()

        btn_cargar = QPushButton("Cargar clientes")
        btn_cargar.clicked.connect(self.cargar_clientes)

        btn_agregar = QPushButton("Agregar cliente")
        btn_agregar.clicked.connect(self.abrir_formulario_agregar)

        btn_editar = QPushButton("Editar cliente")
        btn_editar.clicked.connect(self.abrir_formulario_editar)

        btn_eliminar = QPushButton("Eliminar cliente")
        btn_eliminar.clicked.connect(self.eliminar_cliente)

        if self.tipo_usuario == "empleado":
            btn_eliminar.setEnabled(False)

        botones_layout.addWidget(btn_cargar)
        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_editar)
        botones_layout.addWidget(btn_eliminar)

        layout.addLayout(botones_layout)
        self.setLayout(layout)
        
        # Cargar datos al iniciar
        self.cargar_clientes()

    # 📋 Cargar clientes en la tabla
    def cargar_clientes(self):
        clientes = obtener_clientes()
        self.tabla.setRowCount(len(clientes))

        for fila, cliente in enumerate(clientes):
            for columna, valor in enumerate(cliente):
                self.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))

    # ➕ Formulario para agregar cliente
    def abrir_formulario_agregar(self):
        dialogo = FormularioCliente()
        if dialogo.exec():
            nombre, correo, telefono, direccion = dialogo.get_datos()
            if crear_cliente(nombre, correo, telefono, direccion):
                QMessageBox.information(self, "Éxito", "Cliente agregado correctamente")
                self.cargar_clientes()
            else:
                QMessageBox.critical(self, "Error", "No se pudo agregar el cliente")

    # ✏️ Formulario para editar cliente
    def abrir_formulario_editar(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Selecciona un cliente para editar")
            return

        cliente_id = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()
        correo = self.tabla.item(fila, 2).text()
        telefono = self.tabla.item(fila, 3).text()
        direccion = self.tabla.item(fila, 4).text()

        dialogo = FormularioCliente(nombre, correo, telefono, direccion)
        if dialogo.exec():
            nuevo_nombre, nuevo_correo, nuevo_telefono, nuevo_direccion = dialogo.get_datos()
            if actualizar_cliente(cliente_id, nuevo_nombre, nuevo_correo, nuevo_telefono, nuevo_direccion):
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
                self.cargar_clientes()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el cliente")

    # ❌ Eliminar cliente
    def eliminar_cliente(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Selecciona un cliente para eliminar")
            return

        cliente_id = int(self.tabla.item(fila, 0).text())
        confirmacion = QMessageBox.question(self, "Confirmar", "¿Seguro que deseas eliminar este cliente?")

        if confirmacion == QMessageBox.StandardButton.Yes:
            if eliminar_cliente(cliente_id):
                QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
                self.cargar_clientes()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el cliente")