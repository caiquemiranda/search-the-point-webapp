import os
import sqlite3
import shutil

# Remover o banco de dados existente
db_file = "coordinates.db"
if os.path.exists(db_file):
    print(f"Removendo banco de dados existente: {db_file}")
    os.remove(db_file)
    print("Banco de dados removido com sucesso")
else:
    print("Banco de dados não encontrado, será criado do zero")

# Limpar o diretório de uploads para começar do zero (opcional)
uploads_dir = "uploads"
if os.path.exists(uploads_dir):
    print(f"Limpando diretório de uploads: {uploads_dir}")
    shutil.rmtree(uploads_dir)
    os.makedirs(uploads_dir)
    print("Diretório de uploads limpo e recriado")
else:
    os.makedirs(uploads_dir)
    print("Diretório de uploads criado")

# Criar um novo banco de dados com a estrutura correta
print(f"Criando novo banco de dados: {db_file}")
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Criar tabela para armazenar informações sobre as imagens processadas
print("Criando tabela processed_images...")
cursor.execute('''
CREATE TABLE processed_images (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    page_count INTEGER NOT NULL,
    thumbnail_path TEXT
)
''')

# Criar tabela para armazenar coordenadas salvas
print("Criando tabela saved_coordinates...")
cursor.execute('''
CREATE TABLE saved_coordinates (
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

conn.commit()
conn.close()

print("Novo banco de dados criado com sucesso") 