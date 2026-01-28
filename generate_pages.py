#!/usr/bin/env python3
"""
Generate static HTML pages for Static Motor Recordings archive.
"""

import json
import os
from datetime import datetime
import html

BASE_PATH = '/Users/brandon/Music/SMR/SMR_Archive/smr-archive-site'

def load_json(filename):
    with open(os.path.join(BASE_PATH, 'data', filename), 'r') as f:
        return json.load(f)

def escape(text):
    """Escape HTML entities."""
    if text is None:
        return ''
    return html.escape(str(text))

def get_header(title, path_prefix='../../'):
    """Generate page header."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} | Static Motor Recordings</title>

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

  <!-- Styles -->
  <link rel="stylesheet" href="{path_prefix}assets/css/style.css">
</head>
<body>
  <!-- Header -->
  <header class="site-header">
    <div class="container">
      <div class="site-header__inner">
        <a href="{path_prefix}index.html" class="site-logo">
          <div class="site-logo__mark">
            <svg viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
              <text x="6" y="28" fill="#fafafa" font-family="Inter, sans-serif" font-size="16" font-weight="900">SM</text>
            </svg>
          </div>
          <span class="site-logo__text">Static<br>Motor</span>
        </a>

        <button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>

        <nav class="site-nav" id="site-nav">
          <a href="{path_prefix}index.html" class="site-nav__link">Catalog</a>
          <a href="{path_prefix}pages/artists/index.html" class="site-nav__link">Artists</a>
          <a href="{path_prefix}pages/about.html" class="site-nav__link">About</a>
        </nav>
      </div>
    </div>
  </header>

  <main>
'''

def get_footer(path_prefix='../../'):
    """Generate page footer."""
    return f'''
  </main>

  <!-- Footer -->
  <footer class="site-footer site-footer--bold">
    <div class="container">
      <div class="site-footer__inner">
        <div class="site-footer__brand">
          <span class="site-footer__logo">Static Motor Recordings</span>
          <p class="site-footer__tagline">
            Boston-based independent record label (2003&ndash;2020).
            This archive preserves the catalog and history of indie rock, pop, and americana
            releases from The Longwalls, Kurt von Stetten, Gatsby, and Dan London.
          </p>
        </div>

        <div class="site-footer__nav">
          <h3 class="site-footer__nav-title">Navigate</h3>
          <ul class="site-footer__nav-list">
            <li><a href="{path_prefix}index.html" class="site-footer__nav-link link-draw">Catalog</a></li>
            <li><a href="{path_prefix}pages/artists/index.html" class="site-footer__nav-link link-draw">Artists</a></li>
            <li><a href="{path_prefix}pages/about.html" class="site-footer__nav-link link-draw">About</a></li>
          </ul>
        </div>

        <div class="site-footer__nav">
          <h3 class="site-footer__nav-title">Artists</h3>
          <ul class="site-footer__nav-list">
            <li><a href="{path_prefix}pages/artists/the-longwalls.html" class="site-footer__nav-link link-draw">The Longwalls</a></li>
            <li><a href="{path_prefix}pages/artists/kurt-von-stetten.html" class="site-footer__nav-link link-draw">Kurt von Stetten</a></li>
            <li><a href="{path_prefix}pages/artists/gatsby.html" class="site-footer__nav-link link-draw">Gatsby</a></li>
            <li><a href="{path_prefix}pages/artists/dan-london.html" class="site-footer__nav-link link-draw">Dan London</a></li>
          </ul>
        </div>

        <p class="site-footer__copyright">
          &copy; 2003&ndash;2020 Static Motor Recordings. Archive maintained for historical preservation.
        </p>
      </div>
    </div>
  </footer>
</body>
</html>
'''

def generate_album_page(album, all_albums, artists):
    """Generate an album detail page."""
    path_prefix = '../../'
    # Fix cover image path - add prefix if it doesn't start with http or ../
    cover_image = album.get('coverImage')
    if cover_image:
        if not cover_image.startswith('http') and not cover_image.startswith('../'):
            cover_image = f'{path_prefix}{cover_image}'
    else:
        cover_image = f'{path_prefix}assets/images/placeholder.svg'

    # Find artist
    artist = next((a for a in artists if a['slug'] == album['artistSlug']), None)

    # Find related albums (same artist)
    related = [a for a in all_albums if a['artistSlug'] == album['artistSlug'] and a['slug'] != album['slug']][:4]

    # Build press quotes section (use real press quotes, not blog posts)
    press_html = ''
    if album.get('press'):
        press_items = []
        for quote in album['press'][:6]:
            source_html = escape(quote.get('source', ''))
            if quote.get('url'):
                source_html = f'<a href="{quote["url"]}" target="_blank" rel="noopener">{source_html}</a>'
            press_items.append(f'''
        <div class="press-quote">
          <p class="press-quote__text">"{escape(quote.get('text', ''))}"</p>
          <p class="press-quote__source">&mdash; {source_html}</p>
        </div>''')
        if press_items:
            press_html = f'''
    <section class="album-section">
      <div class="container">
        <h2 class="album-section__title">Press &amp; Reviews</h2>
        <div class="press-quotes">
          {''.join(press_items)}
        </div>
      </div>
    </section>'''

    # Build related albums section
    related_html = ''
    if related:
        related_items = []
        for r in related:
            r_cover = r.get('coverImage')
            if r_cover and not r_cover.startswith('http') and not r_cover.startswith('../'):
                r_cover = f'{path_prefix}{r_cover}'
            elif not r_cover:
                r_cover = f'{path_prefix}assets/images/placeholder.svg'
            related_items.append(f'''
          <a href="{r['slug']}.html" class="album-card">
            <div class="album-card__image">
              <img src="{r_cover}" alt="{escape(r['name'])} album cover" loading="lazy">
            </div>
            <div class="album-card__meta">
              <span class="album-card__artist">{escape(r['artist'])}</span>
              <h3 class="album-card__title">{escape(r['name'])}</h3>
            </div>
          </a>''')

        related_html = f'''
    <section class="album-section">
      <div class="container">
        <h2 class="album-section__title">More from {escape(album['artist'])}</h2>
        <div class="related-albums">
          {''.join(related_items)}
        </div>
      </div>
    </section>'''

    # Description section
    description_html = ''
    if album.get('description'):
        # Convert newlines to paragraphs
        paragraphs = album['description'].split('\n\n')
        desc_paras = ''.join([f'<p>{escape(p)}</p>' for p in paragraphs if p.strip()])
        description_html = f'''
    <section class="album-section">
      <div class="container">
        <h2 class="album-section__title">About This Release</h2>
        <div class="album-description">
          {desc_paras}
        </div>
      </div>
    </section>'''

    # Tracklist & Credits section
    tracklist_html = ''
    if album.get('tracks') or album.get('credits'):
        track_list = ''
        if album.get('tracks'):
            track_items = []
            for track in album['tracks']:
                track_items.append(f'''
          <li class="track-item">
            <span class="track-number">{track['number']:02d}</span>
            <span class="track-title">{escape(track['title'])}</span>
          </li>''')
            track_list = f'''
        <h3 class="section-subtitle">Tracks</h3>
        <ol class="tracklist">
          {''.join(track_items)}
        </ol>'''

        credits_html = ''
        if album.get('credits'):
            # Convert credits newlines to HTML
            credits_lines = album['credits'].split('\n')
            credits_formatted = '<br>'.join([escape(line) for line in credits_lines if line.strip()])
            credits_html = f'''
        <h3 class="section-subtitle mt-8">Credits</h3>
        <div class="credits">
          {credits_formatted}
        </div>'''

        tracklist_html = f'''
    <section class="album-section">
      <div class="container">
        {track_list}
        {credits_html}
      </div>
    </section>'''

    # Watch section (YouTube embeds)
    watch_html = ''
    if album.get('youtubePlaylist'):
        watch_html = f'''
    <section class="album-section">
      <div class="container">
        <h2 class="album-section__title">Watch</h2>
        <div class="video-embed">
          <iframe width="560" height="315" src="https://www.youtube.com/embed/videoseries?list={album['youtubePlaylist']}"
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen></iframe>
        </div>
      </div>
    </section>'''
    elif album.get('youtubeVideo'):
        watch_html = f'''
    <section class="album-section">
      <div class="container">
        <h2 class="album-section__title">Watch</h2>
        <div class="video-embed">
          <iframe width="560" height="315" src="https://www.youtube.com/embed/{album['youtubeVideo']}"
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen></iframe>
        </div>
      </div>
    </section>'''

    # Audio embed for hero section (Bandcamp/SoundCloud)
    audio_embed_html = ''
    if album.get('bandcampEmbed'):
        audio_embed_html = f'''
        <div class="audio-embed audio-embed--hero">
          {album['bandcampEmbed']}
        </div>'''
    elif album.get('soundcloudEmbed'):
        audio_embed_html = f'''
        <div class="audio-embed audio-embed--hero audio-embed--soundcloud">
          {album['soundcloudEmbed']}
        </div>'''

    # Buy CTA - prefer embed URL (has correct album link) over bandcampUrl (may be generic)
    buy_url = None
    if album.get('bandcampEmbed'):
        # Extract URL from embed href - this has the correct album-specific URL
        import re
        href_match = re.search(r'href="(https://[^"]+)"', album['bandcampEmbed'])
        if href_match:
            buy_url = href_match.group(1)
    elif album.get('bandcampUrl'):
        # Fallback to bandcampUrl if no embed
        url = album['bandcampUrl']
        buy_url = url if url.startswith('http') else f'https://{url}'

    buy_cta = f'''
        <a href="{buy_url}" class="album-hero__cta" target="_blank" rel="noopener">
          <span>Buy on Bandcamp</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M7 17L17 7M17 7H7M17 7V17"/>
          </svg>
        </a>''' if buy_url else ''

    # Featured quote (use real featured quote from ACF data)
    quote_html = ''
    if album.get('featuredQuote') and album['featuredQuote'].get('text'):
        fq = album['featuredQuote']
        quote_text = fq['text']
        if len(quote_text) > 200:
            quote_text = quote_text[:200] + '...'
        source = f' &mdash; {escape(fq["source"])}' if fq.get('source') else ''
        quote_html = f'''
        <blockquote class="album-hero__quote">
          "{escape(quote_text)}"{source}
        </blockquote>'''

    page_content = f'''
    <!-- Album Hero -->
    <section class="album-hero album-hero--refined" data-album="{album['slug']}">
      <div class="container">
        <div class="album-hero__grid">
          <div class="album-hero__cover album-cover--elevated">
            <img src="{cover_image}" alt="{escape(album['name'])} album cover">
          </div>
          <div class="album-hero__info">
            <p class="album-hero__artist">
              <a href="{path_prefix}pages/artists/{album['artistSlug']}.html" class="link-draw">{escape(album['artist'])}</a>
            </p>
            <h1 class="album-hero__title">{escape(album['name'])}</h1>
            <dl class="album-hero__meta-list">
              {f'<div class="album-hero__meta-item"><dt>Release Date</dt><dd>{album["releaseDate"]}</dd></div>' if album.get('releaseDate') else ''}
              {f'<div class="album-hero__meta-item"><dt>Catalog #</dt><dd>{escape(album.get("catalogNumber", ""))}</dd></div>' if album.get('catalogNumber') else ''}
              {f'<div class="album-hero__meta-item"><dt>Format(s)</dt><dd>{", ".join(album.get("formats", []))}</dd></div>' if album.get('formats') else ''}
            </dl>
            {quote_html}
            {audio_embed_html}
            {buy_cta}
          </div>
        </div>
      </div>
    </section>
    {description_html}
    {tracklist_html}
    {watch_html}
    {press_html}
    {related_html}
'''

    return get_header(f'{album["name"]} by {album["artist"]}', path_prefix) + page_content + get_footer(path_prefix)

def generate_artist_page(artist, all_albums):
    """Generate an artist detail page."""
    path_prefix = '../../'

    # Get artist's albums
    artist_albums = [a for a in all_albums if a['artistSlug'] == artist['slug']]

    # Album grid
    albums_html = ''
    if artist_albums:
        album_items = []
        for album in artist_albums:
            cover = album.get('coverImage')
            if cover:
                if not cover.startswith('http') and not cover.startswith('../'):
                    cover = f'{path_prefix}{cover}'
            else:
                cover = f'{path_prefix}assets/images/placeholder.svg'
            album_items.append(f'''
          <a href="{path_prefix}pages/albums/{album['slug']}.html" class="album-card">
            <div class="album-card__image">
              <img src="{cover}" alt="{escape(album['name'])} album cover" loading="lazy">
            </div>
            <div class="album-card__meta">
              <h3 class="album-card__title">{escape(album['name'])}</h3>
            </div>
          </a>''')

        albums_html = f'''
    <section class="album-section">
      <div class="container">
        <h2 class="album-section__title">Discography ({len(artist_albums)} releases)</h2>
        <div class="grid grid-cols-4">
          {''.join(album_items)}
        </div>
      </div>
    </section>'''

    hero_image = artist.get('heroImage')
    if hero_image:
        if not hero_image.startswith('http') and not hero_image.startswith('../'):
            hero_image = f'{path_prefix}{hero_image}'
    else:
        hero_image = f'{path_prefix}assets/images/placeholder.svg'

    # Bandcamp link
    bandcamp_html = ''
    if artist.get('bandcampUrl'):
        url = artist['bandcampUrl']
        if not url.startswith('http'):
            url = f'https://{url}'
        bandcamp_html = f'''
        <p class="mt-6">
          <a href="{url}" target="_blank" rel="noopener" class="text-accent">
            Listen on Bandcamp &rarr;
          </a>
        </p>'''

    # YouTube embed section for artist page
    youtube_html = ''
    if artist.get('youtubeEmbed'):
        youtube_html = f'''
    <section class="album-section">
      <div class="container">
        <h2 class="album-section__title">Watch</h2>
        <div class="video-embed">
          {artist['youtubeEmbed']}
        </div>
      </div>
    </section>'''

    page_content = f'''
    <!-- Artist Hero -->
    <section class="artist-hero artist-hero--dramatic hero-background hero-background--lines">
      <div class="container">
        <div class="artist-hero__grid">
          <div class="artist-hero__image">
            <img src="{hero_image}" alt="{escape(artist['name'])}">
          </div>
          <div class="artist-hero__info">
            <p class="artist-hero__label">Artist</p>
            <h1 class="artist-hero__name">{escape(artist['name'])}</h1>
            {f'<p class="artist-hero__quote">"{escape(artist["quote"])}"</p>' if artist.get('quote') else ''}
            {f'<p class="text-lg text-gray-600 mt-4">{escape(artist["bio"])}</p>' if artist.get('bio') else ''}
            {bandcamp_html}
          </div>
        </div>
      </div>
    </section>
    {youtube_html}
    {albums_html}
'''

    return get_header(artist['name'], path_prefix) + page_content + get_footer(path_prefix)

def generate_artists_index(artists, all_albums):
    """Generate artists index page."""
    path_prefix = '../../'

    artist_items = []
    for artist in artists:
        album_count = len([a for a in all_albums if a['artistSlug'] == artist['slug']])
        hero_image = artist.get('heroImage')
        if hero_image:
            if not hero_image.startswith('http') and not hero_image.startswith('../'):
                hero_image = f'{path_prefix}{hero_image}'
        else:
            hero_image = f'{path_prefix}assets/images/placeholder.svg'

        artist_items.append(f'''
      <div class="artist-item">
        <div class="artist-item__image">
          <img src="{hero_image}" alt="{escape(artist['name'])}">
        </div>
        <div class="artist-item__info">
          <h2 class="artist-item__name">
            <a href="{artist['slug']}.html">{escape(artist['name'])}</a>
          </h2>
          <p class="artist-item__releases">{album_count} release{'s' if album_count != 1 else ''}</p>
          {f'<p class="text-gray-600">{escape(artist.get("bio", ""))[:200]}...</p>' if artist.get('bio') else ''}
        </div>
      </div>''')

    page_content = f'''
    <section class="page-intro">
      <div class="container">
        <h1 class="page-intro__title">Boston-based indie rock, pop, americana.</h1>
        <p class="page-intro__subtitle">Static Motor Recordings is home to popsmiths The Longwalls, DIY wunderkind Kurt von Stetten, singer/songwriter Dan London, and ol' local favs Gatsby.</p>
      </div>
    </section>

    <section class="catalog-header">
      <div class="container">
        <p class="catalog-header__title">Label Roster</p>
        <h1 class="catalog-header__count">{len(artists)} Artists</h1>
      </div>
    </section>

    <section class="artist-index">
      <div class="container">
        <div class="artist-list">
          {''.join(artist_items)}
        </div>
      </div>
    </section>
'''

    return get_header('Artists', path_prefix) + page_content + get_footer(path_prefix)

def generate_about_page(timeline):
    """Generate about page."""
    path_prefix = '../'

    # Group timeline by year
    years = {}
    for item in timeline:
        if item.get('date'):
            year = item['date'][:4]
            if year not in years:
                years[year] = []
            years[year].append(item)

    # Build timeline HTML (show key events, limit per year)
    timeline_items = []
    for year in sorted(years.keys(), reverse=True):
        events = years[year][:3]  # Limit to 3 events per year
        for event in events:
            type_label = event.get('type', 'news').title()
            timeline_items.append(f'''
        <div class="timeline__item">
          <span class="timeline__date">{escape(event.get('date', ''))}</span>
          <div class="timeline__content">
            <span class="timeline__type">{type_label}</span>
            <h3 class="timeline__heading">{escape(event.get('title', ''))}</h3>
          </div>
        </div>''')

    page_content = f'''
    <section class="page-intro">
      <div class="container">
        <h1 class="page-intro__title">Because really DIY means doing it yourselves.</h1>
        <p class="page-intro__subtitle">Friends making music together, releasing it on their own terms, and building something that lasted seventeen years.</p>
      </div>
    </section>

    <section class="about-hero">
      <div class="container">
        <h1 class="about-hero__title">Static Motor Recordings</h1>
        <p class="about-hero__subtitle">
          A Boston-based independent record label dedicated to releasing thoughtful, well-crafted indie rock, pop, and americana from 2003 to 2020.
        </p>
      </div>
    </section>

    <section class="about-content">
      <div class="container">
        <div class="about-content__grid">
          <div class="about-content__sidebar">
            <p class="about-content__label">Founded</p>
            <p class="text-xl font-semibold">2003</p>

            <p class="about-content__label mt-6">Location</p>
            <p class="text-xl font-semibold">Boston, MA</p>

            <p class="about-content__label mt-6">Catalog</p>
            <p class="text-xl font-semibold">27 Releases</p>

            <p class="about-content__label mt-6">Artists</p>
            <p class="text-xl font-semibold">4 Acts</p>
          </div>

          <div class="about-content__main">
            <p>
              Static Motor Recordings was founded in Boston in 2003 with a simple mission: to release music we loved from artists we believed in. Over seventeen years, the label became home to The Longwalls, Kurt von Stetten, Gatsby, and Dan London.
            </p>
            <p>
              From the beginning, we approached each release with care and attention to detail. Whether it was a full-length album, an EP, or a single, every release received the same dedication to quality in recording, design, and promotion.
            </p>
            <p>
              The label earned recognition from outlets including The Boston Globe, The Noise, Twangville, The Owl Mag, and countless music blogs. Our artists received radio play on WMBR, WMFO, and college stations across the country. Songs found their way onto MTV and Vans promotional videos.
            </p>
            <p>
              In 2020, after 27 releases, Static Motor Recordings closed its doors. This archive preserves the catalog and documents the history of the label for anyone who wants to discover or revisit the music.
            </p>
            <p>
              The music remains available on Bandcamp and streaming platforms. Thank you to everyone who supported the label over the years.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="timeline">
      <div class="container">
        <h2 class="timeline__title">Label Timeline</h2>
        <div class="timeline__list">
          {''.join(timeline_items[:30])}
        </div>
      </div>
    </section>
'''

    return get_header('About', path_prefix) + page_content + get_footer(path_prefix)

def main():
    print("Loading data...")
    albums = load_json('albums.json')
    artists = load_json('artists.json')
    timeline = load_json('timeline.json')

    # Create directories
    os.makedirs(os.path.join(BASE_PATH, 'pages/albums'), exist_ok=True)
    os.makedirs(os.path.join(BASE_PATH, 'pages/artists'), exist_ok=True)

    # Generate album pages
    print(f"\nGenerating {len(albums)} album pages...")
    for album in albums:
        html_content = generate_album_page(album, albums, artists)
        filepath = os.path.join(BASE_PATH, 'pages/albums', f'{album["slug"]}.html')
        with open(filepath, 'w') as f:
            f.write(html_content)
        print(f"  Created: {album['slug']}.html")

    # Generate artist pages
    print(f"\nGenerating {len(artists)} artist pages...")
    for artist in artists:
        html_content = generate_artist_page(artist, albums)
        filepath = os.path.join(BASE_PATH, 'pages/artists', f'{artist["slug"]}.html')
        with open(filepath, 'w') as f:
            f.write(html_content)
        print(f"  Created: {artist['slug']}.html")

    # Generate artists index
    print("\nGenerating artists index...")
    html_content = generate_artists_index(artists, albums)
    filepath = os.path.join(BASE_PATH, 'pages/artists/index.html')
    with open(filepath, 'w') as f:
        f.write(html_content)
    print("  Created: artists/index.html")

    # Generate about page
    print("\nGenerating about page...")
    html_content = generate_about_page(timeline)
    filepath = os.path.join(BASE_PATH, 'pages/about.html')
    with open(filepath, 'w') as f:
        f.write(html_content)
    print("  Created: about.html")

    print("\nDone! Generated all static pages.")

if __name__ == '__main__':
    main()
