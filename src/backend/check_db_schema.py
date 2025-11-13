"""
Script para verificar o schema do banco de dados existente no Supabase
"""
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv
import os

load_dotenv()

# Monta a URL do banco
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

print(f"Conectando ao banco de dados...")
print(f"Host: {os.getenv('POSTGRES_HOST')}")
print(f"Database: {os.getenv('POSTGRES_DB')}")
print()

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inspector = inspect(engine)

    print("=" * 80)
    print("TABELAS EXISTENTES NO BANCO DE DADOS")
    print("=" * 80)
    print()

    tables = inspector.get_table_names()

    if not tables:
        print("Nenhuma tabela encontrada no banco de dados.")
    else:
        for table_name in sorted(tables):
            print(f"\n📋 Tabela: {table_name}")
            print("-" * 80)

            columns = inspector.get_columns(table_name)
            for column in columns:
                col_name = column['name']
                col_type = str(column['type'])
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                default = f" DEFAULT {column['default']}" if column.get('default') else ""
                print(f"  • {col_name:<30} {col_type:<20} {nullable}{default}")

            # Verificar chaves primárias
            pk = inspector.get_pk_constraint(table_name)
            if pk and pk['constrained_columns']:
                print(f"\n  🔑 Primary Key: {', '.join(pk['constrained_columns'])}")

            # Verificar chaves estrangeiras
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print(f"\n  🔗 Foreign Keys:")
                for fk in fks:
                    print(f"     {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")

            # Verificar índices
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"\n  📊 Indexes:")
                for idx in indexes:
                    unique = "UNIQUE" if idx['unique'] else ""
                    print(f"     {idx['name']}: {', '.join(idx['column_names'])} {unique}")

    print("\n" + "=" * 80)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("=" * 80)

except Exception as e:
    print(f"❌ Erro ao conectar ao banco de dados:")
    print(f"   {str(e)}")
    print()
    print("Verifique se:")
    print("  1. As credenciais no .env estão corretas")
    print("  2. O firewall do Supabase permite sua conexão")
    print("  3. A connection string está no formato correto")
