#!/bin/bash
set -e
set -u

function create_database() {
    local database=$1
    echo "  Creating database '$database'..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE "$database";
EOSQL
}

# Создаем базы данных
if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_database $db
    done
    echo "Multiple databases created successfully."
fi

# Инициализация таблицы ai_assistant_chat_memory
if [ -f "/docker-entrypoint-initdb.d/chat_memory_init.sql" ]; then
    echo "Initializing database 'ai_assistant_chat_memory' with schema..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d ai_assistant_chat_memory -f /docker-entrypoint-initdb.d/chat_memory_init.sql
fi

# Инициализация таблицы ai_assistant_user_profile
if [ -f "/docker-entrypoint-initdb.d/user_profile_init.sql" ]; then
    echo "Initializing database 'ai_assistant_user_profile' with schema..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d ai_assistant_user_profile -f /docker-entrypoint-initdb.d/user_profile_init.sql
fi