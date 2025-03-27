import sqlite3
from contextlib import contextmanager
import os

DB_FILE = "coordinates.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_db_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            return cursor.lastrowid
        
        if fetch_one:
            return cursor.fetchone()
        
        if fetch_all:
            return cursor.fetchall()
        
        return None

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela para armazenar informações sobre as imagens processadas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_images (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            page_count INTEGER NOT NULL,
            thumbnail_path TEXT
        )
        ''')
        
        # Tabela para armazenar coordenadas salvas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_coordinates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id TEXT NOT NULL,
            name TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            page INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            source TEXT,
            FOREIGN KEY (image_id) REFERENCES processed_images (id)
        )
        ''')
        
        # Verificar se a coluna source já existe
        cursor.execute("PRAGMA table_info(saved_coordinates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Se a coluna source não existir, adicioná-la
        if 'source' not in columns:
            print("Migrando banco de dados: adicionando coluna 'source' à tabela saved_coordinates")
            try:
                cursor.execute("ALTER TABLE saved_coordinates ADD COLUMN source TEXT")
                # Atualizar registros existentes para usar filename como source
                cursor.execute('''
                UPDATE saved_coordinates 
                SET source = (SELECT filename FROM processed_images WHERE id = saved_coordinates.image_id)
                WHERE source IS NULL
                ''')
                print("Migração concluída com sucesso")
            except Exception as e:
                print(f"Erro na migração: {e}")
        
        conn.commit() 