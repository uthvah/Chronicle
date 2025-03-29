let trendingPage = 1;
let genrePage = 1;
let currentGenre = "";

// Unified function to create a book card using consistent logic.
function createBookCard(book) {
  const card = document.createElement('div');
  card.className = 'book-card';

  // Determine OLID: either from book.olid or from key.
  const olid = book.olid ? book.olid : (book.key ? book.key.replace("/works/", "") : "");
  card.setAttribute('data-olid', olid);

  // Build cover image URL:
  let coverUrl = "default_cover.png";
  if (book.cover && book.cover !== "default_cover.png") {
    coverUrl = book.cover;
  } else if (book.cover_i) {
    coverUrl = `https://covers.openlibrary.org/b/id/${book.cover_i}-M.jpg`;
  }
  
  const cover = document.createElement('img');
  cover.src = coverUrl;
  cover.alt = book.title;
  cover.className = 'book-cover';
  card.appendChild(cover);

  // Determine author display:
  let authorDisplay = "";
  if (book.author && book.author.toLowerCase() !== "unknown" && book.author.trim() !== "") {
    authorDisplay = book.author;
  } else if (book.author_name && Array.isArray(book.author_name) && book.author_name.length > 0) {
    authorDisplay = book.author_name.join(", ");
  } else {
    authorDisplay = "Unknown";
  }
  
  const titleElem = document.createElement('div');
  titleElem.className = 'book-title';
  titleElem.textContent = book.title;
  card.appendChild(titleElem);

  const authorElem = document.createElement('div');
  authorElem.className = 'book-author';
  authorElem.textContent = authorDisplay;
  card.appendChild(authorElem);

  // On click: redirect to info.html with OLID parameter.
  card.addEventListener('click', function() {
    if (olid) {
      window.location.href = `info.html?olid=${olid}`;
    } else {
      alert("No detailed information available for this book.");
    }
  });

  // Right-click: deletion (for library view).
  card.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    if (confirm(`Delete "${book.title}" by ${authorDisplay}?`)) {
      eel.deleteBook(book.id)(function(response) {
        if (response.status === "success") {
          refreshLibrary();
        } else {
          alert("Error deleting book: " + response.message);
        }
      });
    }
  });
  
  return card;
}

function displayLibrary(books) {
  const grid = document.getElementById('libraryGrid');
  grid.innerHTML = '';
  books.forEach(book => grid.appendChild(createBookCard(book)));
}

function refreshLibrary() {
  eel.getLibrary()(displayLibrary);
}

function displayTrending(works, append = false) {
  const grid = document.getElementById('trendingGrid');
  if (!append) grid.innerHTML = '';
  works.forEach(work => {
    const book = {
      id: work.key ? work.key.replace("/works/", "") : "",
      title: work.title,
      author_name: work.author_name,
      cover_i: work.cover_i,
      olid: work.key ? work.key.replace("/works/", "") : ""
    };
    grid.appendChild(createBookCard(book));
  });
}

function displayBrowseResults(works, append = false) {
  const grid = document.getElementById('browseResults');
  if (!append) grid.innerHTML = '';
  works.forEach(work => {
    const book = {
      id: work.key ? work.key.replace("/works/", "") : "",
      title: work.title,
      author_name: work.author_name,
      cover_i: work.cover_i,
      olid: work.key ? work.key.replace("/works/", "") : ""
    };
    grid.appendChild(createBookCard(book));
  });
}

document.addEventListener('DOMContentLoaded', function() {
  refreshLibrary();

  // Dashboard file selection & processing.
  document.getElementById('selectFileBtn').addEventListener('click', function() {
    eel.selectFile()(function(filePath) {
      if (filePath) {
        document.getElementById('selectFileBtn').textContent = "Selected: " + filePath.split(/[/\\]/).pop();
        document.getElementById('processBtn').disabled = false;
        window.selectedFilePath = filePath;
      }
    });
  });

  document.getElementById('processBtn').addEventListener('click', function() {
    if (!window.selectedFilePath) return;
    document.getElementById('processBtn').disabled = true;
    eel.processAndSend(window.selectedFilePath)(function(response) {
      if (response.status === "success") {
        alert("Book processed and added to library.");
        refreshLibrary();
      } else {
        alert("Error: " + response.message);
      }
      document.getElementById('selectFileBtn').textContent = "Select File";
      document.getElementById('processBtn').disabled = true;
      window.selectedFilePath = null;
    });
  });

  // Dashboard library search.
  document.getElementById('searchBtn').addEventListener('click', function() {
    const query = document.getElementById('searchInput').value;
    eel.searchLibrary(query)(function(results) {
      displayLibrary(results);
    });
  });

  document.getElementById('sendKindleBtn').addEventListener('click', function() {
    eel.sendPendingToKindle()(function(response) {
      if(response.status === "success"){
        alert("Pending books sent to Kindle.");
        refreshLibrary();
      } else {
        alert("Error: " + response.message);
      }
    });
  });

  // Browse section: Aesthetic search bar for LibGen.
  document.getElementById('browseSearchBtn').addEventListener('click', function() {
    const query = document.getElementById('browseSearchInput').value;
    if(query.trim() === ""){
      alert("Please enter a search query.");
      return;
    }
    eel.searchLibgen(query)(function(results) {
      displayBrowseResults(results, false);
    });
  });

  // Navigation buttons.
  document.getElementById('dashboardBtn').addEventListener('click', function() {
    hideAllSections();
    document.getElementById('dashboardSection').classList.remove('hidden');
    setActiveNavButton(this);
  });

  document.getElementById('browseBtn').addEventListener('click', function() {
    hideAllSections();
    document.getElementById('browseSection').classList.remove('hidden');
    setActiveNavButton(this);
    trendingPage = 1;
    eel.getTrendingBooks(trendingPage)(function(trending) {
      displayTrending(trending, false);
    });
  });

  document.getElementById('recommendBtn').addEventListener('click', function() {
    hideAllSections();
    document.getElementById('recommendSection').classList.remove('hidden');
    setActiveNavButton(this);
    eel.getRecommendations()(function(recs) {
      displayTrending(recs, false);
    });
  });

  document.getElementById('settingsBtn').addEventListener('click', function() {
    hideAllSections();
    document.getElementById('settingsSection').classList.remove('hidden');
    setActiveNavButton(this);
    eel.getStatsData()(function(stats) {
      document.getElementById('statsArea').innerHTML = JSON.stringify(stats, null, 2);
    });
  });

  // Load More buttons.
  document.getElementById('trendingLoadMore').addEventListener('click', function() {
    trendingPage++;
    eel.getTrendingBooks(trendingPage)(function(trending) {
      displayTrending(trending, true);
    });
  });

  document.getElementById('browseLoadMore').addEventListener('click', function() {
    genrePage++;
    eel.browseGenre(currentGenre, genrePage)(function(results) {
      displayBrowseResults(results, true);
    });
  });

  // Genre card click handling using event delegation.
  document.getElementById('genreGrid').addEventListener('click', function(e) {
    const card = e.target.closest('.genre-card');
    if (card) {
      currentGenre = card.getAttribute('data-genre');
      genrePage = 1;
      eel.browseGenre(currentGenre, genrePage)(function(results) {
        displayBrowseResults(results, false);
      });
    }
  });

  function hideAllSections() {
    ['dashboardSection', 'browseSection', 'recommendSection', 'settingsSection'].forEach(id => {
      document.getElementById(id).classList.add('hidden');
    });
  }

  function setActiveNavButton(activeBtn) {
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    activeBtn.classList.add('active');
  }
});
