import sqlite3
import os
import shutil
from config import DATABASE_FILE, LOCAL_LIBRARY_FOLDER

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            file_path TEXT,
            cover_image_path TEXT,
            processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_to_kindle INTEGER DEFAULT 0,
            olid TEXT
        )
    ''')
    conn.commit()
    # Alter table if necessary.
    cursor.execute("PRAGMA table_info(books)")
    columns = [row[1] for row in cursor.fetchall()]
    if "sent_to_kindle" not in columns:
        cursor.execute("ALTER TABLE books ADD COLUMN sent_to_kindle INTEGER DEFAULT 0")
        conn.commit()
    if "olid" not in columns:
        cursor.execute("ALTER TABLE books ADD COLUMN olid TEXT")
        conn.commit()
    conn.close()

def add_book(title, author, file_path, cover_image_path="default_cover.png", olid=""):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, author, file_path, cover_image_path, sent_to_kindle, olid)
        VALUES (?, ?, ?, ?, 0, ?)
    ''', (title, author, file_path, cover_image_path, olid))
    conn.commit()
    conn.close()

def get_all_books():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, author, file_path, cover_image_path, processed_date,
               COALESCE(sent_to_kindle, 0) as sent_to_kindle,
               COALESCE(olid, '') as olid
        FROM books ORDER BY processed_date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_book(book_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

def update_output_path(new_path):
    # Placeholder: in a real app, store settings in a separate table or config file.
    pass

def get_stats():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM books')
    total_books = cursor.fetchone()[0]
    cursor.execute('SELECT title, author FROM books ORDER BY processed_date DESC LIMIT 1')
    most_recent = cursor.fetchone()
    conn.close()
    return {
        'total_books': total_books,
        'most_recent': most_recent if most_recent else ('N/A', 'N/A')
    }

def search_books(query):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    pattern = f"%{query}%"
    cursor.execute('''
        SELECT id, title, author, file_path, cover_image_path, processed_date,
               COALESCE(sent_to_kindle, 0), COALESCE(olid, '')
        FROM books 
        WHERE title LIKE ? OR author LIKE ?
        ORDER BY processed_date DESC
    ''', (pattern, pattern))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_kindle_flag(book_id_or_title, flag):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    value = 1 if flag else 0
    if isinstance(book_id_or_title, int):
        cursor.execute('UPDATE books SET sent_to_kindle = ? WHERE id = ?', (value, book_id_or_title))
    else:
        cursor.execute('UPDATE books SET sent_to_kindle = ? WHERE title = ?', (value, book_id_or_title))
    conn.commit()
    conn.close()

if not os.path.exists(LOCAL_LIBRARY_FOLDER):
    os.makedirs(LOCAL_LIBRARY_FOLDER)

init_db()
