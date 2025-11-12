"""
Script para criar usuário padrão no banco Supabase
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy.exc import IntegrityError

def create_default_user():
    """Cria um usuário padrão para testes"""
    db = SessionLocal()
    
    try:
        # Verifica se já existe
        existing = db.query(User).filter(User.email == "admin@ismart.com").first()
        if existing:
            print("✅ Usuário padrão já existe!")
            print(f"📧 Email: admin@ismart.com")
            print(f"🔑 Senha: Admin123")
            print(f"👤 Role: {existing.role}")
            print(f"🛡️  Is Admin: {existing.is_admin}")
            return
        
        # Cria novo usuário admin
        user = User(
            email="admin@ismart.com",
            hashed_password=hash_password("Admin123"),
            is_verified=True,
            is_admin=True,
            role="admin",
            verification_code=None
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("✅ Usuário padrão criado com sucesso!")
        print("")
        print("📋 Dados para login:")
        print("=" * 40)
        print(f"📧 Email: admin@ismart.com")
        print(f"🔑 Senha: Admin123")
        print(f"👤 Role: {user.role}")
        print(f"🛡️  Is Admin: {user.is_admin}")
        print(f"🆔 User ID: {user.id}")
        print("=" * 40)
        
    except IntegrityError as e:
        print(f"❌ Erro: Usuário já existe ou erro de integridade")
        print(f"   Detalhes: {e}")
        db.rollback()
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Criando usuário padrão no banco Supabase...")
    print("")
    create_default_user()
