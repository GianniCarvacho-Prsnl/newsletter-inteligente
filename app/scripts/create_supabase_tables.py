#!/usr/bin/env python3
"""
Script para crear las tablas necesarias en Supabase.

Este script utiliza el MCP de Supabase para crear las tablas:
- users: información de usuarios
- topics: tópicos disponibles
- user_topics: relación entre usuarios y tópicos
- newsletters: registro de newsletters enviados

Uso:
    python -m app.scripts.create_supabase_tables --org-id <org_id> --project-id <project_id>
"""

import argparse
import sys
import os
from pathlib import Path
import json

# Asegurar que podemos importar desde app
parent_dir = Path(__file__).parents[2]
sys.path.append(str(parent_dir))

def create_users_table(project_id):
    """Crear tabla de usuarios"""
    migration_name = "create_users_table"
    
    # SQL para crear la tabla de usuarios
    sql = """
    -- Crear tabla de usuarios
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        telegram_id TEXT,
        preferences JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Agregar comentarios a la tabla
    COMMENT ON TABLE users IS 'Tabla de usuarios del sistema';
    
    -- Crear índices
    CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
    
    -- Trigger para actualizar el campo updated_at
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """
    
    # Ejecutar la migración usando el MCP de Supabase
    print(f"Creando tabla users en proyecto {project_id}...")
    try:
        # Aquí iría la llamada al MCP de Supabase
        # mcp_supabase_apply_migration(project_id=project_id, name=migration_name, query=sql)
        print(f"Para ejecutar este script, descomenta la línea que llama al MCP de Supabase")
        print(f"SQL para crear tabla users:")
        print(sql)
        
        return True
    except Exception as e:
        print(f"Error al crear tabla users: {e}")
        return False

def create_topics_table(project_id):
    """Crear tabla de tópicos"""
    migration_name = "create_topics_table"
    
    # SQL para crear la tabla de tópicos
    sql = """
    -- Crear tabla de tópicos
    CREATE TABLE IF NOT EXISTS topics (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Agregar comentarios a la tabla
    COMMENT ON TABLE topics IS 'Tópicos disponibles para newsletters';
    
    -- Trigger para actualizar el campo updated_at
    CREATE TRIGGER topics_updated_at
    BEFORE UPDATE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """
    
    # Ejecutar la migración usando el MCP de Supabase
    print(f"Creando tabla topics en proyecto {project_id}...")
    try:
        # Aquí iría la llamada al MCP de Supabase
        # mcp_supabase_apply_migration(project_id=project_id, name=migration_name, query=sql)
        print(f"Para ejecutar este script, descomenta la línea que llama al MCP de Supabase")
        print(f"SQL para crear tabla topics:")
        print(sql)
        
        return True
    except Exception as e:
        print(f"Error al crear tabla topics: {e}")
        return False

def create_user_topics_table(project_id):
    """Crear tabla de relación usuario-tópico"""
    migration_name = "create_user_topics_table"
    
    # SQL para crear la tabla de relación
    sql = """
    -- Crear tabla de relación usuario-tópico
    CREATE TABLE IF NOT EXISTS user_topics (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(user_id, topic_id)
    );

    -- Agregar comentarios a la tabla
    COMMENT ON TABLE user_topics IS 'Relación entre usuarios y sus tópicos de interés';
    
    -- Crear índices
    CREATE INDEX IF NOT EXISTS idx_user_topics_user_id ON user_topics (user_id);
    CREATE INDEX IF NOT EXISTS idx_user_topics_topic_id ON user_topics (topic_id);
    """
    
    # Ejecutar la migración usando el MCP de Supabase
    print(f"Creando tabla user_topics en proyecto {project_id}...")
    try:
        # Aquí iría la llamada al MCP de Supabase
        # mcp_supabase_apply_migration(project_id=project_id, name=migration_name, query=sql)
        print(f"Para ejecutar este script, descomenta la línea que llama al MCP de Supabase")
        print(f"SQL para crear tabla user_topics:")
        print(sql)
        
        return True
    except Exception as e:
        print(f"Error al crear tabla user_topics: {e}")
        return False

def create_newsletters_table(project_id):
    """Crear tabla de newsletters enviados"""
    migration_name = "create_newsletters_table"
    
    # SQL para crear la tabla de newsletters
    sql = """
    -- Crear tabla de newsletters enviados
    CREATE TABLE IF NOT EXISTS newsletters (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        content TEXT NOT NULL,
        topics TEXT[] DEFAULT '{}',
        channel TEXT NOT NULL DEFAULT 'email',
        sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Agregar comentarios a la tabla
    COMMENT ON TABLE newsletters IS 'Registro de newsletters enviados a usuarios';
    
    -- Crear índices
    CREATE INDEX IF NOT EXISTS idx_newsletters_user_id ON newsletters (user_id);
    CREATE INDEX IF NOT EXISTS idx_newsletters_sent_at ON newsletters (sent_at);
    """
    
    # Ejecutar la migración usando el MCP de Supabase
    print(f"Creando tabla newsletters en proyecto {project_id}...")
    try:
        # Aquí iría la llamada al MCP de Supabase
        # mcp_supabase_apply_migration(project_id=project_id, name=migration_name, query=sql)
        print(f"Para ejecutar este script, descomenta la línea que llama al MCP de Supabase")
        print(f"SQL para crear tabla newsletters:")
        print(sql)
        
        return True
    except Exception as e:
        print(f"Error al crear tabla newsletters: {e}")
        return False

def insert_sample_data(project_id):
    """Insertar datos de ejemplo"""
    migration_name = "insert_sample_data"
    
    # SQL para insertar datos de ejemplo
    sql = """
    -- Insertar tópicos de ejemplo
    INSERT INTO topics (name, description)
    VALUES 
        ('Inteligencia Artificial', 'Noticias sobre IA, machine learning y tecnologías relacionadas'),
        ('Cambio Climático', 'Noticias sobre medio ambiente y cambio climático'),
        ('Tecnología', 'Noticias generales sobre tecnología y gadgets'),
        ('Ciencia', 'Descubrimientos científicos y avances en investigación'),
        ('Negocios', 'Noticias sobre empresas, startups y economía')
    ON CONFLICT (name) DO NOTHING;
    
    -- Insertar un usuario de ejemplo
    INSERT INTO users (name, email, phone)
    VALUES ('Usuario de Prueba', 'test@example.com', '+1234567890')
    ON CONFLICT (email) DO NOTHING;
    
    -- Asignar tópicos al usuario de ejemplo
    WITH 
        user_example AS (SELECT id FROM users WHERE email = 'test@example.com' LIMIT 1),
        topics_example AS (SELECT id FROM topics WHERE name IN ('Inteligencia Artificial', 'Tecnología'))
    INSERT INTO user_topics (user_id, topic_id)
    SELECT user_example.id, topics_example.id
    FROM user_example, topics_example
    ON CONFLICT (user_id, topic_id) DO NOTHING;
    """
    
    # Ejecutar la migración usando el MCP de Supabase
    print(f"Insertando datos de ejemplo en proyecto {project_id}...")
    try:
        # Aquí iría la llamada al MCP de Supabase
        # mcp_supabase_apply_migration(project_id=project_id, name=migration_name, query=sql)
        print(f"Para ejecutar este script, descomenta la línea que llama al MCP de Supabase")
        print(f"SQL para insertar datos de ejemplo:")
        print(sql)
        
        return True
    except Exception as e:
        print(f"Error al insertar datos de ejemplo: {e}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Crear tablas en Supabase")
    parser.add_argument("--org-id", required=True, help="ID de la organización en Supabase")
    parser.add_argument("--project-id", required=True, help="ID del proyecto en Supabase")
    parser.add_argument("--skip-sample-data", action="store_true", help="Omitir la inserción de datos de ejemplo")
    
    args = parser.parse_args()
    
    # Crear extensión uuid si no existe
    # Este paso es importante para poder usar uuid_generate_v4()
    uuid_extension_sql = "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
    # mcp_supabase_apply_migration(project_id=args.project_id, name="create_uuid_extension", query=uuid_extension_sql)
    print(f"Para ejecutar este script, descomenta las líneas que llaman al MCP de Supabase")
    print(f"SQL para crear extensión uuid:")
    print(uuid_extension_sql)
    
    # Crear las tablas
    create_users_table(args.project_id)
    create_topics_table(args.project_id)
    create_user_topics_table(args.project_id)
    create_newsletters_table(args.project_id)
    
    # Insertar datos de ejemplo si no se omite
    if not args.skip_sample_data:
        insert_sample_data(args.project_id)
    
    print("\nProceso completado. Para ejecutar realmente este script, descomenta las líneas que llaman al MCP de Supabase.")
    print("Las líneas a descomentar están marcadas con: # mcp_supabase_apply_migration")

if __name__ == "__main__":
    main() 