#!/usr/bin/env python3
"""
Script para excluir o banco de dados IoT
ATENÇÃO: Este script apaga TODOS os dados permanentemente!
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carrega variáveis de ambiente
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("AVISO: python-dotenv não instalado")

try:
    import mysql.connector
except ImportError:
    print("ERRO: mysql-connector-python não instalado")
    print("Instale com: pip install mysql-connector-python")
    sys.exit(1)

MYSQL_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'tales'),
    'password': os.environ.get('DB_PASSWORD', 'senha123'),
    'port': int(os.environ.get('DB_PORT', '3306'))
}

DB_NAME = os.environ.get('DB_NAME', 'ioTabelas')

def drop_database():
    """Exclui o banco de dados IoT"""
    print("="*60)
    print("EXCLUIR BANCO DE DADOS IOT")
    print("="*60)
    print(f"Host: {MYSQL_CONFIG['host']}")
    print(f"Porta: {MYSQL_CONFIG['port']}")
    print(f"Banco: {DB_NAME}")
    print("="*60)
    print("\n⚠️  ATENÇÃO: Esta ação irá APAGAR TODOS OS DADOS!")
    print("⚠️  Esta operação NÃO PODE ser desfeita!\n")
    
    # Solicita confirmação
    resposta = input(f"Digite 'EXCLUIR' para confirmar a exclusão do banco '{DB_NAME}': ")
    
    if resposta != 'EXCLUIR':
        print("\n✗ Operação cancelada pelo usuário.")
        return False
    
    # Segunda confirmação
    resposta2 = input(f"\nTem CERTEZA ABSOLUTA? Digite novamente '{DB_NAME}': ")
    
    if resposta2 != DB_NAME:
        print("\n✗ Confirmação incorreta. Operação cancelada.")
        return False
    
    print("\n🗑️  Excluindo banco de dados...")
    
    try:
        # Conecta sem especificar banco
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        
        # Verifica se o banco existe
        cur.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
        result = cur.fetchone()
        
        if not result:
            print(f"\n⚠️  Banco '{DB_NAME}' não existe.")
            cur.close()
            conn.close()
            return False
        
        # Exclui o banco
        cur.execute(f"DROP DATABASE {DB_NAME}")
        
        print(f"\n✓ Banco '{DB_NAME}' excluído com sucesso!")
        print("✓ Todos os dados foram permanentemente removidos.\n")
        
        cur.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"\n✗ Erro ao excluir banco: {e}\n")
        return False
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}\n")
        return False

def main():
    print("\n" + "="*60)
    print("SCRIPT DE EXCLUSÃO DO BANCO DE DADOS IOT")
    print("="*60 + "\n")
    
    success = drop_database()
    
    if success:
        print("="*60)
        print("BANCO EXCLUÍDO COM SUCESSO")
        print("="*60)
        print("\nPara recriar o banco, execute:")
        print("  mysql -u tales -psenha123 < Banco/CreateDB.sql")
        print("  ou")
        print("  python Banco/init_db.py")
        print()
    else:
        print("="*60)
        print("OPERAÇÃO NÃO REALIZADA")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
