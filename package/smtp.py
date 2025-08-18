import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "noelenriqueascanio@gmail.com"
SMTP_PASS = "fghn fcnh bnoe jood"

def enviar_email(destinatario, asunto, mensaje):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(mensaje, "html"))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls() 
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        print(f"Correo enviado {destinatario}")
