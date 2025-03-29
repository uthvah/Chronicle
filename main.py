import eel
import os
from tkinter import Tk, filedialog
from library_manager import (
    get_all_books, delete_book, add_book, update_output_path,
    get_stats, search_books, update_kindle_flag
)
from processing import process_file, download_and_process_book
from libgen_api import LibgenSearch  # Assume this module is available
from config import DEFAULT_LANGUAGE

# Global language filter – can be updated via settings.
language_filter = DEFAULT_LANGUAGE

eel.init('web')

@eel.expose
def getLibrary():
    books = get_all_books()
    result = []
    for book in books:
        result.append({
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "cover": book[4] if book[4] and os.path.exists(book[4]) else "default_cover.png",
            "processed_date": book[5] if len(book) > 5 else "",
            "sent_to_kindle": bool(book[6]),
            "olid": book[7]
        })
    return result

@eel.expose
def deleteBook(book_id):
    try:
        delete_book(book_id)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def processAndSend(file_path):
    try:
        processed_file, metadata = process_file(file_path)
        add_book(
            metadata["title"],
            metadata["author"],
            processed_file,
            metadata.get("cover_image_path", "default_cover.png"),
            metadata.get("olid", "")
        )
        update_kindle_flag(metadata["title"], False)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def selectFile():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select eBook File",
        filetypes=[("eBook Files", "*.epub *.pdf *.mobi *.txt"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

@eel.expose
def updateSettings(new_settings):
    global language_filter
    try:
        lang = new_settings.get("language", DEFAULT_LANGUAGE)
        language_filter = lang
        update_output_path(new_settings.get("output_path"))
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def getStatsData():
    try:
        stats = get_stats()
        return stats
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def searchLibrary(query):
    try:
        results = search_books(query)
        res = []
        for book in results:
            res.append({
                "id": book[0],
                "title": book[1],
                "author": book[2],
                "cover": book[4] if book[4] and os.path.exists(book[4]) else "default_cover.png",
                "processed_date": book[5] if len(book) > 5 else "",
                "sent_to_kindle": bool(book[6]),
                "olid": book[7]
            })
        return res
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def searchLibgen(query):
    # Use LibGen API via LibgenSearch for external searches.
    try:
        s = LibgenSearch()
        results = s.search_title(query)
        # Return results directly; these should contain keys: title, author_name, cover_i, key, etc.
        return results
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def getBookDetails(olid):
    # We use LibGen data for detailed info. Here, mimic a detailed call.
    # For simplicity, we call the local library info if available, or use fallback.
    # In a real app, you might combine LibGen and Open Library data.
    from libgen_api import LibgenSearch
    try:
        s = LibgenSearch()
        # Here we assume we can retrieve detailed info using the OLID (or work key)
        details = s.get_work_details(olid)
        if not details:
            details = {}
        # Build cover URL if cover_i exists
        if "cover_i" in details and details["cover_i"]:
            details["cover"] = f"https://covers.openlibrary.org/b/id/{details['cover_i']}-M.jpg"
        else:
            details["cover"] = "default_cover.png"
        return details
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def downloadBook(query):
    try:
        processed_file, metadata = download_and_process_book(query)
        add_book(
            metadata["title"],
            metadata["author"],
            processed_file,
            metadata.get("cover_image_path", "default_cover.png"),
            metadata.get("olid", "")
        )
        update_kindle_flag(metadata["title"], False)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def sendPendingToKindle():
    try:
        books = get_all_books()
        for book in books:
            if len(book) >= 8 and not book[6]:
                from kindle_service import send_to_kindle
                send_to_kindle(book[3])
                update_kindle_flag(book[0], True)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def browseGenre(genre, page=1):
    # For simplicity, use LibGen's subject search if available
    from libgen_api import LibgenSearch
    try:
        s = LibgenSearch()
        results = s.search_subject(genre, page=page)
        return results
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def getTrendingBooks(page=1):
    try:
        # For trending books, use a popular subject query like "bestsellers"
        from libgen_api import LibgenSearch
        s = LibgenSearch()
        results = s.search_subject("bestsellers", page=page)
        return results
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def getRecommendations():
    try:
        books = get_all_books()
        authors = list({book[2] for book in books if book[2]})
        if not authors:
            return []
        # Use the first author as a query for recommendations.
        from libgen_api import LibgenSearch
        s = LibgenSearch()
        recs = s.search_title(authors[0], limit=10)
        return recs
    except Exception as e:
        return {"status": "error", "message": str(e)}

eel.start('index.html', size=(1200, 800))
