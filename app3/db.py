import sqlite3
import os

def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect('coordenadas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pontos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            coord_x REAL NOT NULL,
            coord_y REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def salvar_ponto(nome, x, y):
    """Salva um novo ponto no banco"""
    conn = sqlite3.connect('coordenadas.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO pontos (nome, coord_x, coord_y) VALUES (?, ?, ?)',
                 (nome, x, y))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def carregar_pontos():
    """Carrega todos os pontos do banco"""
    conn = sqlite3.connect('coordenadas.db')
    c = conn.cursor()
    c.execute('SELECT nome, coord_x, coord_y FROM pontos ORDER BY created_at DESC')
    pontos = {row[0]: {"x": row[1], "y": row[2]} for row in c.fetchall()}
    conn.close()
    return pontos

def deletar_ponto(nome):
    """Deleta um ponto do banco"""
    conn = sqlite3.connect('coordenadas.db')
    c = conn.cursor()
    c.execute('DELETE FROM pontos WHERE nome = ?', (nome,))
    conn.commit()
    conn.close() 