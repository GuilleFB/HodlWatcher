import json
import requests


def extract_payment_methods():
    """
    Extrae los métodos de pago de un JSON, devolviendo solo el id, type y name.
    Opcionalmente los ordena por ID.

    Args:
        json_data (dict or str): Datos JSON con la estructura de métodos de pago.
        sort_by_id (bool, optional): Si se deben ordenar los métodos por ID. Por defecto es True.

    Returns:
        list: Lista de métodos de pago con id, type y name.
    """

    json_data = requests.get("https://hodlhodl.com/api/v1/payment_methods").json()
    # Si se pasa un string, convertir a diccionario
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    # Extraer los métodos de pago
    extracted_methods = [
        {"id": method.get("id", ""), "type": method.get("type", ""), "name": method.get("name", "")}
        for method in json_data.get("payment_methods", [])
    ]

    return extracted_methods
