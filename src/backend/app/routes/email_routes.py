from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.config.database import get_db
from app.models.pending_email import PendingEmail
from app.schemas.email_schema import EmailListResponse, PendingEmailResponse
from app.utils.csv_handler import parse_csv_file, validate_emails
from app.utils.verification_code import generate_verification_code
from app.utils.email_service import email_service
from datetime import datetime, timedelta
from typing import List

router = APIRouter(
    prefix="/api/emails",
    tags=["emails"]
)

@router.post("/upload-csv", response_model=EmailListResponse)
async def upload_emails_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint para upload de CSV com emails e envio automático de códigos.
    
    O arquivo CSV deve ter uma coluna 'email' com os endereços de email.
    
    Exemplo de CSV:
```
    email
    usuario1@example.com
    usuario2@example.com
```
    
    Processo:
    1. Valida o arquivo CSV
    2. Insere emails no banco de dados
    3. Gera código de verificação único para cada email
    4. Envia email automático com o código
    """
    
    # Validação do tipo de arquivo
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser um CSV"
        )
    
    try:
        # Lê o conteúdo do arquivo
        content = await file.read()
        
        # Parse do CSV
        emails_from_csv, csv_errors = parse_csv_file(content)
        
        if not emails_from_csv and csv_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao processar CSV: {csv_errors[0]}"
            )
        
        # Validação dos emails
        valid_emails, validation_errors = validate_emails(emails_from_csv)
        
        if not valid_emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum email válido encontrado no arquivo"
            )
        
        success_count = 0
        error_count = len(validation_errors)
        
        # Insere os emails no banco e envia o código
        for email in valid_emails:
            try:
                # Gera um código de verificação
                verification_code = generate_verification_code()
                
                # Cria o registro
                pending_email = PendingEmail(
                    email=email,
                    verification_code=verification_code,
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                
                db.add(pending_email)
                db.commit()
                
                # 🚀 NOVO: Envia email com o código
                email_sent = email_service.send_verification_email(
                    recipient_email=email,
                    verification_code=verification_code
                )
                
                if email_sent:
                    success_count += 1
                else:
                    # Se falhar ao enviar, marca como erro
                    db.delete(pending_email)
                    db.commit()
                    error_count += 1
                    validation_errors.append({
                        "email": email,
                        "reason": "Falha ao enviar email"
                    })
                
            except IntegrityError:
                # Email já existe
                db.rollback()
                error_count += 1
                validation_errors.append({
                    "email": email,
                    "reason": "Email já cadastrado no sistema"
                })
            except Exception as e:
                db.rollback()
                error_count += 1
                validation_errors.append({
                    "email": email,
                    "reason": f"Erro ao processar: {str(e)}"
                })
        
        return EmailListResponse(
            success_count=success_count,
            error_count=error_count,
            errors=validation_errors,
            message=f"{success_count} email(s) processado(s) com sucesso"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )

@router.get("/pending", response_model=List[PendingEmailResponse])
async def get_pending_emails(db: Session = Depends(get_db)):
    """
    Retorna a lista de emails pendentes (não utilizados).
    """
    pending = db.query(PendingEmail).filter(
        PendingEmail.used == False
    ).all()
    
    return pending