import os
import requests

BREVO_KEY = os.getenv("BREVO_KEY")

def enviar_email(destinatario, asunto, mensaje):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_KEY,
        "content-type": "application/json"
    }
    data = {
        "sender": {"name": "Barber Blessed", "email": "barberblessedman@gmail.com"},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "htmlContent": mensaje
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Correo enviado a {destinatario}")
    else:
        print("Error al enviar:", response.text)