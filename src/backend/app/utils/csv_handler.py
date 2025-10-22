import csv
from io import StringIO, BytesIO
from typing import List, Tuple

def parse_csv_file(file_content: bytes) -> Tuple[List[str], List[str]]:
    """
    Lê um arquivo CSV e extrai os emails.
    
    Retorna:
        - Lista de emails válidos
        - Lista de erros
    """
    emails = []
    errors = []
    
    try:
        # Decodifica o conteúdo bytes para string
        content_str = file_content.decode('utf-8')
        
        # Usa StringIO para simular um arquivo
        csv_file = StringIO(content_str)
        
        # Lê o CSV
        reader = csv.reader(csv_file)
        
        # Pega o header (primeira linha)
        header = next(reader, None)
        
        if not header:
            errors.append("Arquivo CSV vazio")
            return emails, errors
        
        # Encontra o índice da coluna 'email'
        try:
            email_index = header.index('email')
        except ValueError:
            errors.append("Coluna 'email' não encontrada. Use o cabeçalho 'email'")
            return emails, errors
        
        # Lê cada linha
        for row_num, row in enumerate(reader, start=2):
            if len(row) > email_index:
                email = row[email_index].strip()
                
                # Validação básica de email
                if email and '@' in email:
                    emails.append(email)
                elif email:
                    errors.append(f"Linha {row_num}: Email inválido '{email}'")
            else:
                errors.append(f"Linha {row_num}: Coluna de email vazia")
    
    except UnicodeDecodeError:
        errors.append("Arquivo deve estar em UTF-8")
    except Exception as e:
        errors.append(f"Erro ao processar CSV: {str(e)}")
    
    return emails, errors

def validate_emails(emails: List[str]) -> Tuple[List[str], List[dict]]:
    """
    Valida uma lista de emails.
    
    Retorna:
        - Lista de emails válidos
        - Lista de erros com detalhes
    """
    valid_emails = []
    errors = []
    seen = set()
    
    for email in emails:
        email = email.lower().strip()
        
        # Verifica se é vazio
        if not email:
            continue
        
        # Verifica duplicação
        if email in seen:
            errors.append({"email": email, "reason": "Email duplicado na lista"})
            continue
        
        # Validação básica de formato
        if not is_valid_email_format(email):
            errors.append({"email": email, "reason": "Formato de email inválido"})
            continue
        
        seen.add(email)
        valid_emails.append(email)
    
    return valid_emails, errors

def is_valid_email_format(email: str) -> bool:
    """Valida o formato básico de um email."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None