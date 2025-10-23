import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_verification_email(to_email: str, code: str):
    """
    Envia um e-mail de verificação com um código de 6 dígitos.
    """
    sender_email = settings.EMAIL_SENDER
    app_password = settings.EMAIL_APP_PASSWORD

    subject = "🎓 ISMART Conecta – Código de Verificação"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; 
                    padding: 30px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #005fa3; text-align: center;">Bem-vindo ao ISMART Conecta!</h2>
            <p style="font-size: 16px; color: #333333;">
                Olá! 👋<br><br>
                Estamos quase lá! Para concluir seu cadastro, insira o código de verificação abaixo:
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="font-size: 32px; font-weight: bold; color: #005fa3; letter-spacing: 4px;">
                    {code}
                </span>
            </div>
            <p style="font-size: 15px; color: #333333;">
                Se você não solicitou este e-mail, pode ignorá-lo com segurança.
            </p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #dddddd;">
            <p style="font-size: 12px; color: #777777; text-align: center;">
                Equipe ISMART Conecta<br>
                <strong>Por favor, não responda este e-mail.</strong>
            </p>
        </div>
    </body>
    </html>
    """

    # Configuração da mensagem MIME
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            print(f"✅ E-mail de verificação enviado com sucesso para {to_email}")
    except Exception as e:
        print(f"⚠️ Falha ao enviar e-mail para {to_email}: {e}")
