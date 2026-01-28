/**
 * Static Motor Recordings Archive
 * Main JavaScript Application
 */

(function() {
  'use strict';

  // ==========================================================================
  // Data Loading
  // ==========================================================================

  async function loadJSON(path) {
    try {
      const response = await fetch(path);
      if (!response.ok) throw new Error(`Failed to load ${path}`);
      return await response.json();
    } catch (error) {
      console.error('Error loading data:', error);
      return null;
    }
  }

  // ==========================================================================
  // Album Grid
  // ==========================================================================

  function createAlbumCard(album) {
    const card = document.createElement('a');
    card.className = 'album-card';
    card.href = `pages/albums/${album.slug}.html`;
    card.dataset.artist = album.artistSlug;

    // Use placeholder image if no cover
    const coverImage = album.coverImage || 'assets/images/placeholder.svg';

    card.innerHTML = `
      <div class="album-card__image">
        <img src="${coverImage}" alt="${album.name} album cover" loading="lazy">
      </div>
      <div class="album-card__meta">
        <span class="album-card__artist">${album.artist}</span>
        <h3 class="album-card__title">${album.name}</h3>
        ${album.releaseDate ? `<span class="album-card__year">${album.releaseDate.split('-')[0]}</span>` : ''}
      </div>
    `;

    return card;
  }

  function sortAlbumsByDate(albums) {
    return [...albums].sort((a, b) => {
      // Sort by release date, most recent first
      const dateA = a.releaseDate ? new Date(a.releaseDate) : new Date(0);
      const dateB = b.releaseDate ? new Date(b.releaseDate) : new Date(0);
      return dateB - dateA;
    });
  }

  function renderAlbumGrid(albums, filter = 'all') {
    const grid = document.getElementById('album-grid');
    const countEl = document.getElementById('album-count');

    if (!grid) return;

    // Clear existing content
    grid.innerHTML = '';

    // Filter albums
    const filteredAlbums = filter === 'all'
      ? albums
      : albums.filter(album => album.artistSlug === filter);

    // Sort by release date (most recent first)
    const sortedAlbums = sortAlbumsByDate(filteredAlbums);

    // Update count
    if (countEl) {
      countEl.textContent = sortedAlbums.length;
    }

    // Render cards
    sortedAlbums.forEach(album => {
      grid.appendChild(createAlbumCard(album));
    });
  }

  function initAlbumFilters(albums) {
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        // Update active state
        filterBtns.forEach(b => b.classList.remove('filter-btn--active'));
        btn.classList.add('filter-btn--active');

        // Filter grid
        const filter = btn.dataset.filter;
        renderAlbumGrid(albums, filter);
      });
    });
  }

  // ==========================================================================
  // Mobile Menu
  // ==========================================================================

  function initMobileMenu() {
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.getElementById('site-nav');

    if (!toggle || !nav) return;

    toggle.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('site-nav--open');
      toggle.setAttribute('aria-expanded', isOpen);
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!nav.contains(e.target) && !toggle.contains(e.target)) {
        nav.classList.remove('site-nav--open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // ==========================================================================
  // Album Detail Page
  // ==========================================================================

  function initAlbumDetail(albums, artists) {
    const heroEl = document.querySelector('.album-hero');
    if (!heroEl) return;

    // Get album slug from URL or data attribute
    const slug = heroEl.dataset.album;
    if (!slug) return;

    const album = albums.find(a => a.slug === slug);
    if (!album) return;

    // Populate album data
    populateAlbumHero(album);
    populateAlbumSections(album);
    populateRelatedAlbums(album, albums);
  }

  function populateAlbumHero(album) {
    // This would populate dynamic content on album pages
    // For a static site, we'll generate these pages with the data already embedded
  }

  // ==========================================================================
  // Responsive Grid Classes
  // ==========================================================================

  function updateGridClasses() {
    const grid = document.getElementById('album-grid');
    if (!grid) return;

    const width = window.innerWidth;

    grid.classList.remove('grid-cols-1', 'grid-cols-2', 'grid-cols-3', 'grid-cols-4');

    if (width < 640) {
      grid.classList.add('grid-cols-1');
    } else if (width < 768) {
      grid.classList.add('grid-cols-2');
    } else if (width < 1024) {
      grid.classList.add('grid-cols-3');
    } else {
      grid.classList.add('grid-cols-4');
    }
  }

  // ==========================================================================
  // Initialize
  // ==========================================================================

  async function init() {
    // Initialize mobile menu
    initMobileMenu();

    // Load data
    const albums = await loadJSON('data/albums.json');
    const artists = await loadJSON('data/artists.json');

    if (albums) {
      // Initialize album grid on homepage
      if (document.getElementById('album-grid')) {
        renderAlbumGrid(albums);
        initAlbumFilters(albums);

        // Handle responsive grid
        updateGridClasses();
        window.addEventListener('resize', updateGridClasses);
      }

      // Initialize album detail page
      if (document.querySelector('.album-hero')) {
        initAlbumDetail(albums, artists);
      }
    }
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
