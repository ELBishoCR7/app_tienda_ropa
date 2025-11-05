import requests
import json
from PyQt6.QtCore import QObject, pyqtSignal

API_URL = "http://127.0.0.1:8000"

class NetworkWorker(QObject):
    """
    Worker que corre en un hilo separado para manejar peticiones de red.
    Señales:
      - success: emite el JSON decodificado (dict o list)
      - failure: emite un mensaje de error (str)
      - finished: emite cuando termina (siempre)
    """
    success = pyqtSignal(object)
    failure = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, url: str, method: str, data: dict = None, token: str = None):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data
        self.token = token

    def run(self):
        try:
            # Debug: mostrar qué se va a ejecutar en consola (útil en desarrollo)
            print(f"[NetworkWorker] {self.method} {self.url} token_present={bool(self.token)} data={bool(self.data)}")

            if self.method == "POST_JSON":
                response = requests.post(self.url, json=self.data, timeout=15)
            elif self.method == "POST_FORM":
                response = requests.post(self.url, data=self.data, timeout=15)
            elif self.method == "POST_AUTH":
                if not self.token:
                    raise ValueError("Se requiere un token para POST_AUTH")
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.post(self.url, json=self.data, headers=headers, timeout=15)
            elif self.method == "GET_AUTH":
                if not self.token:
                    raise ValueError("Se requiere un token para GET_AUTH")
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.get(self.url, headers=headers, timeout=15)
            elif self.method == "PUT_AUTH":
                if not self.token:
                    raise ValueError("Se requiere un token para PUT_AUTH")
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.put(self.url, headers=headers, json=self.data, timeout=15)
            elif self.method == "DELETE_AUTH":
                if not self.token:
                    raise ValueError("Se requiere un token para DELETE_AUTH")
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.delete(self.url, headers=headers, timeout=15)
            else:
                raise ValueError("Método HTTP no soportado")

            # Forzar raise_for_status para convertir errores HTTP en excepciones
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                # Intenta extraer JSON con 'detail' si está disponible
                try:
                    err_json = response.json()
                    detail = err_json.get("detail") if isinstance(err_json, dict) else None
                    if detail:
                        raise Exception(f"HTTP {response.status_code}: {detail}") from http_err
                except (ValueError, json.JSONDecodeError):
                    pass
                raise

            # Entregar JSON si existe, si no, entregar texto como dict
            try:
                self.success.emit(response.json())
            except ValueError:
                self.success.emit({"message": response.text or ""})

        except requests.exceptions.HTTPError as http_err:
            self.failure.emit(f"Error HTTP: {http_err} (status {getattr(http_err.response, 'status_code', 'n/a')})")
        except requests.exceptions.RequestException as e:
            self.failure.emit(f"Error de conexión: {e}")
        except Exception as e:
            self.failure.emit(str(e))
        finally:
            self.finished.emit()
