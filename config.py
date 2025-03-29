import os

# Folder where processed books (and covers) will be saved.
LOCAL_LIBRARY_FOLDER = os.path.join(os.getcwd(), "library_files")

# SQLite database file (will be created in the current working directory).
DATABASE_FILE = os.path.join(os.getcwd(), "library.db")

# Command to convert ebooks (Calibre's ebook-convert must be installed and in PATH)
EBOOK_CONVERT_CMD = "ebook-convert"

# Default language for searches (if applicable)
DEFAULT_LANGUAGE = "eng"
