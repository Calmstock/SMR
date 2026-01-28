# Static Motor Recordings Archive

A static archive site for Static Motor Recordings, a Boston-based independent record label (2003-2020).

## About

This archive preserves the catalog and history of releases from:
- **The Longwalls** - Indie rock/americana
- **Kurt von Stetten** - DIY pop/rock
- **Gatsby** - Alternative rock
- **Dan London** - Singer-songwriter

## Site Structure

```
smr-archive-site/
├── index.html              # Homepage with filterable album grid
├── assets/
│   ├── css/style.css       # Design system
│   ├── js/app.js           # Filtering and interactivity
│   └── images/
│       ├── albums/         # Album cover artwork
│       └── artists/        # Artist photos
├── data/
│   ├── albums.json         # Album catalog data
│   ├── artists.json        # Artist information
│   └── timeline.json       # Label history events
└── pages/
    ├── about.html          # Label history and timeline
    ├── albums/             # Individual album pages
    └── artists/            # Artist index and detail pages
```

## Building

The site is static HTML/CSS/JS. To regenerate pages from the data:

```bash
python3 extract_content.py    # Extract from WordPress export
python3 update_covers.py      # Update album cover paths
python3 update_artists.py     # Update artist data
python3 generate_pages.py     # Generate HTML pages
```

## Deployment

The site is designed for GitHub Pages:

1. Push to a GitHub repository
2. Enable GitHub Pages in repository settings
3. Select the main branch as the source

Or serve locally:
```bash
python3 -m http.server 8000
```

## Credits

- Design: Swiss/Bauhaus precision + 4AD elegance
- Built with vanilla HTML, CSS, and JavaScript
- No build tools or frameworks required

## License

Archive maintained for historical preservation. Music copyrights belong to respective artists.
