def respuesta_exitosa(data, mensaje="Operación exitosa"):
    return {"mensaje": mensaje, "data": data}

def respuesta_error(error="Ocurrió un error"):
    return {"error": error}