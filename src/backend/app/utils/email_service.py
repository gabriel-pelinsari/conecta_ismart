import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.settings import settings
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """
    Serviço para enviar emails via Gmail SMTP
    """
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SMTP_USER")
        self.sender_password = os.getenv("SMTP_PASSWORD")
        self.sender_name = os.getenv("EMAIL_FROM_NAME", "ISMART Conecta")
        self.from_email = os.getenv("EMAIL_FROM")
    
    def send_verification_email(self, recipient_email: str, verification_code: str) -> bool:
        """
        Envia email com código de verificação.
        
        Args:
            recipient_email: Email do destinatário
            verification_code: Código de 6 dígitos
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Cria a mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = "Seu Código de Verificação - ISMART Conecta"
            message["From"] = f"{self.sender_name} <{self.from_email}>"
            message["To"] = recipient_email
            
            # Corpo do email em HTML
            html_body = self._get_verification_email_template(verification_code)
            
            # Corpo do email em texto puro (fallback)
            text_body = f"""
Bem-vindo ao ISMART Conecta!

Seu código de verificação é: {verification_code}

Este código expira em 24 horas.

Se você não solicitou este email, ignore-o.

---
ISMART Conecta
            """
            
            # Adiciona as partes
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Conecta ao servidor SMTP e envia
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Inicia criptografia TLS
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.from_email, recipient_email, message.as_string())
            
            return True
        
        except smtplib.SMTPAuthenticationError:
            print(f"Erro: Email ou senha do Gmail incorretos")
            return False
        except smtplib.SMTPException as e:
            print(f"Erro SMTP: {str(e)}")
            return False
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False
    
    def _get_verification_email_template(self, verification_code: str) -> str:
        """
        Retorna o template HTML do email de verificação.
        """
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    
                    {/* Header */}
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center;">
                        <h1 style="margin: 0; font-size: 28px;">🚀 ISMART Conecta</h1>
                        <p style="margin: 8px 0 0 0; opacity: 0.9;">Bem-vindo à comunidade!</p>
                    </div>
                    
                    {/* Content */}
                    <div style="background: #f8f9ff; padding: 30px; border-radius: 0 0 8px 8px; border: 1px solid #e5e7eb; border-top: none;">
                        
                        <h2 style="color: #333; margin-top: 0;">Seu Código de Verificação</h2>
                        
                        <p>Olá! 👋</p>
                        
                        <p>Você foi convidado a se juntar ao <strong>ISMART Conecta</strong>. Para completar seu registro, use o código abaixo:</p>
                        
                        {/* Code Box */}
                        <div style="background: white; border: 2px dashed #667eea; padding: 20px; 
                                    border-radius: 8px; text-align: center; margin: 20px 0;">
                            <p style="margin: 0; color: #999; font-size: 12px; text-transform: uppercase;">Código de Verificação</p>
                            <p style="margin: 10px 0 0 0; font-size: 36px; font-weight: 700; color: #667eea; 
                                      letter-spacing: 4px; font-family: 'Courier New', monospace;">
                                {verification_code}
                            </p>
                        </div>
                        
                        <p style="color: #666; font-size: 14px;">
                            <strong>⏰ Atenção:</strong> Este código expira em <strong>24 horas</strong>.
                        </p>
                        
                        <p>Se você não solicitou este email ou não faz parte da sua universidade, 
                           por favor ignore esta mensagem.</p>
                        
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        
                        <p style="color: #999; font-size: 12px; margin: 0;">
                            © 2025 ISMART Conecta. Todos os direitos reservados.<br>
                            Conectando alunos universitários.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """

# Criar instância global
email_service = EmailService()