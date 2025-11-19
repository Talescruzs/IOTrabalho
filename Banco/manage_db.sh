#!/bin/bash
# Script auxiliar para gerenciar o banco de dados IoT
# Uso: ./manage_db.sh [comando]

DB_USER="tales"
DB_PASS="senha123"
DB_NAME="ioTabelas"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    echo "=================================================="
    echo "GERENCIADOR DO BANCO DE DADOS IOT"
    echo "=================================================="
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  create      - Cria o banco e todas as tabelas"
    echo "  populate    - Popula com os sensores"
    echo "  drop        - Exclui o banco (CUIDADO!)"
    echo "  reset       - Drop + Create + Populate"
    echo "  test        - Testa conexão e mostra dados"
    echo "  backup      - Faz backup do banco"
    echo "  show        - Mostra tabelas do banco"
    echo "  help        - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 create"
    echo "  $0 reset"
    echo "  $0 test"
    echo ""
}

create_db() {
    echo "📦 Criando banco de dados..."
    mysql -u "$DB_USER" -p"$DB_PASS" < "$SCRIPT_DIR/CreateDB.sql"
    if [ $? -eq 0 ]; then
        echo "✓ Banco criado com sucesso!"
    else
        echo "✗ Erro ao criar banco"
        exit 1
    fi
}

populate_db() {
    echo "📝 Populando sensores..."
    mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SCRIPT_DIR/InsertSensores.sql"
    if [ $? -eq 0 ]; then
        echo "✓ Sensores inseridos com sucesso!"
    else
        echo "✗ Erro ao popular banco"
        exit 1
    fi
}

drop_db() {
    echo "⚠️  ATENÇÃO: Você está prestes a EXCLUIR o banco '$DB_NAME'"
    echo "⚠️  Todos os dados serão PERMANENTEMENTE perdidos!"
    read -p "Digite 'EXCLUIR' para confirmar: " confirm
    
    if [ "$confirm" != "EXCLUIR" ]; then
        echo "✗ Operação cancelada"
        exit 0
    fi
    
    echo "🗑️  Excluindo banco..."
    mysql -u "$DB_USER" -p"$DB_PASS" < "$SCRIPT_DIR/DropDB.sql"
    if [ $? -eq 0 ]; then
        echo "✓ Banco excluído!"
    else
        echo "✗ Erro ao excluir banco"
        exit 1
    fi
}

reset_db() {
    echo "🔄 Resetando banco de dados..."
    drop_db
    create_db
    populate_db
    echo ""
    echo "✓ Banco resetado com sucesso!"
}

test_db() {
    echo "🧪 Testando banco de dados..."
    cd "$SCRIPT_DIR/.."
    .venv/bin/python Testes/test_database.py
}

backup_db() {
    BACKUP_FILE="$SCRIPT_DIR/backup_${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
    echo "💾 Fazendo backup para: $BACKUP_FILE"
    mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_FILE"
    if [ $? -eq 0 ]; then
        echo "✓ Backup criado com sucesso!"
        echo "Arquivo: $BACKUP_FILE"
    else
        echo "✗ Erro ao criar backup"
        exit 1
    fi
}

show_tables() {
    echo "📋 Tabelas no banco '$DB_NAME':"
    mysql -u "$DB_USER" -p"$DB_PASS" -e "SHOW TABLES FROM $DB_NAME;"
}

# Comando principal
case "$1" in
    create)
        create_db
        ;;
    populate)
        populate_db
        ;;
    drop)
        drop_db
        ;;
    reset)
        reset_db
        ;;
    test)
        test_db
        ;;
    backup)
        backup_db
        ;;
    show)
        show_tables
        ;;
    help|"")
        show_help
        ;;
    *)
        echo "✗ Comando desconhecido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
