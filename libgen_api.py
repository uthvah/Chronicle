import requests
import warnings

class LibgenSearch:
    BASE_SEARCH_URL = "https://libgen.is/search.php"
    
    def search_title(self, query, limit=10):
        # For demo purposes, return a mocked response structure similar to LibGen.
        # In a real implementation, make a request to LibGen and parse the results.
        return [{
            "title": query,
            "author_name": ["Author Example"],
            "cover_i": 258027,
            "key": "OL27448W"  # Mock OLID (for demonstration)
        }]
    
    def search_author(self, query, limit=10):
        # Return a mocked author search result.
        return [{
            "title": "Sample Book by " + query,
            "author_name": [query],
            "cover_i": 258027,
            "key": "OL27448W"
        }]
    
    def resolve_download_links(self, item):
        # Return a dictionary of format: link pairs.
        # In production, parse the LibGen page to extract download links.
        # Here, we simulate both epub and non-epub links.
        return {
            "epub": "https://example.com/sample.epub",
            "pdf": "https://example.com/sample.pdf"
        }
    
    def search_subject(self, subject, limit=10, page=1):
        # Return a mocked list of books for a subject.
        return [{
            "title": f"{subject} Book {i}",
            "author_name": [f"Author {i}"],
            "cover_i": 258027,
            "key": f"OL{i}W"
        } for i in range(1, limit+1)]
    
    def get_work_details(self, olid):
        # Return a mocked detailed work information.
        # In a real implementation, you might scrape or query a LibGen endpoint.
        return {
            "title": "Detailed Book Title",
            "description": {"value": "This is a detailed description of the book."},
            "first_publish_year": 2000,
            "number_of_pages": 350,
            "publish_date": "2000",
            "publishers": ["Publisher Example"],
            "subjects": ["Subject1", "Subject2", "Subject3", "Subject4", "Subject5", "Subject6"],
            "cover_i": 258027,
            "olid": olid,
            "authors": [{"name": "Author Example"}]
        }
