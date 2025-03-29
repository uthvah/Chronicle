import os
import subprocess
import shutil
import requests
from datetime import datetime
from ebooklib import epub
import warnings
from config import LOCAL_LIBRARY_FOLDER, EBOOK_CONVERT_CMD
from libgen_api import LibgenSearch

def convert_to_epub(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".epub":
        return file_path
    else:
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = os.path.join(LOCAL_LIBRARY_FOLDER, f"{name_without_ext}_{timestamp}.epub")
        try:
            subprocess.run([EBOOK_CONVERT_CMD, file_path, output_file], check=True)
            return output_file
        except subprocess.CalledProcessError as e:
            raise Exception(f"Conversion failed: {e}")

def get_book_title(epub_book, file_path):
    metadata = epub.read_epub(file_path).get_metadata('DC', 'title')
    if metadata:
        return metadata[0][0]
    return os.path.splitext(os.path.basename(file_path))[0]

def fetch_metadata_from_libgen(title):
    # Use LibGenSearch to retrieve metadata using title.
    s = LibgenSearch()
    results = s.search_title(title)
    if results:
        doc = results[0]
        olid = ""
        if "key" in doc:
            olid = doc["key"].strip("/").split("/")[-1]
        enriched = {
            "description": str(doc.get("first_publish_year", "")),
            "author": doc.get("author_name", ["Unknown"])[0],
            "cover_id": doc.get("cover_i"),
            "olid": olid
        }
        return enriched
    else:
        return {"description": "", "author": "Unknown", "cover_id": None, "olid": ""}

def update_epub_metadata_with_calibre(epub_path, enriched_metadata):
    title = os.path.splitext(os.path.basename(epub_path))[0]
    author = enriched_metadata.get("author", "Unknown")
    description = enriched_metadata.get("description", "")
    try:
        command = [
            "ebook-meta",
            epub_path,
            "--title", title,
            "--authors", author,
        ]
        if description:
            command += ["--comments", description]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to update metadata: {e}")
    return epub_path, {"title": title, "author": author, "olid": enriched_metadata.get("olid", "")}

def polish_with_calibre(epub_path):
    try:
        command = [
            "ebook-polish",
            "--upgrade-book",
            "--compress-images",
            "--smarten-punctuation",
            "--remove-unused-css",
            "--embed-fonts",
            "--subset-fonts",
            epub_path,
            epub_path
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to polish EPUB: {e}")
    return epub_path

def simplify_title(title):
    if '-' in title:
        return title.split('-', 1)[1].strip()
    return title.strip()

def relocate_file(epub_path, metadata, cover_content=None):
    author = metadata.get("author", "Unknown").strip()
    title = metadata.get("title", "Unknown")
    simple_title = simplify_title(title)
    dest_dir = os.path.join(LOCAL_LIBRARY_FOLDER, author, simple_title)
    os.makedirs(dest_dir, exist_ok=True)
    dest_epub_path = os.path.join(dest_dir, f"{simple_title}.epub")
    try:
        shutil.move(epub_path, dest_epub_path)
    except Exception as e:
        raise Exception(f"Failed to relocate file: {e}")
    cover_image_path = os.path.join(dest_dir, "cover.jpg")
    if cover_content:
        try:
            with open(cover_image_path, "wb") as f:
                f.write(cover_content)
        except Exception as e:
            warnings.warn(f"Failed to save cover image: {e}")
    else:
        cover_image_path = "default_cover.png"
    return dest_epub_path, cover_image_path

def process_file(file_path):
    epub_path = convert_to_epub(file_path)
    book = epub.read_epub(epub_path)
    title = get_book_title(book, file_path)
    enriched_metadata = fetch_metadata_from_libgen(title)
    updated_epub, metadata = update_epub_metadata_with_calibre(epub_path, enriched_metadata)
    polished_epub = polish_with_calibre(updated_epub)
    cover_content = None
    cover_id = enriched_metadata.get("cover_id")
    if cover_id:
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        try:
            resp = requests.get(cover_url, timeout=10)
            if resp.status_code == 200:
                cover_content = resp.content
        except Exception as e:
            warnings.warn(f"Failed to download cover image: {e}")
    final_epub, cover_image_path = relocate_file(polished_epub, metadata, cover_content)
    metadata["title"] = simplify_title(metadata["title"])
    metadata["cover_image_path"] = cover_image_path
    return final_epub, {"title": metadata["title"], "author": metadata["author"], "cover_image_path": cover_image_path, "olid": metadata.get("olid", "")}

def download_and_process_book(query):
    s = LibgenSearch()
    results = s.search_title(query)
    if not results:
        results = s.search_author(query)
    if not results:
        raise Exception("No results found on LibGen for the given query.")
    item_to_download = results[0]
    download_links = s.resolve_download_links(item_to_download)
    epub_link = None
    # Prefer .epub link; if not available, use the first available link.
    for key, url in download_links.items():
        if url.lower().endswith(".epub"):
            epub_link = url
            break
    if not epub_link and download_links:
        epub_link = list(download_links.values())[0]
    if not epub_link:
        raise Exception("No download link found for the selected item.")
    ext = os.path.splitext(epub_link)[1]
    temp_download_path = os.path.join(LOCAL_LIBRARY_FOLDER, "temp_download" + ext)
    try:
        resp = requests.get(epub_link, timeout=20)
        if resp.status_code == 200:
            with open(temp_download_path, "wb") as f:
                f.write(resp.content)
        else:
            raise Exception("Download from LibGen failed with status code " + str(resp.status_code))
    except Exception as e:
        raise Exception(f"LibGen download error: {e}")
    return process_file(temp_download_path)
