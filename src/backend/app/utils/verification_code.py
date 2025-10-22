import random
import string

def generate_verification_code(length: int = 6) -> str:
    """
    Gera um código aleatório de verificação.
    
    Args:
        length: Tamanho do código (padrão 6 dígitos)
    
    Retorna:
        String com números aleatórios
    """
    return ''.join(random.choices(string.digits, k=length))