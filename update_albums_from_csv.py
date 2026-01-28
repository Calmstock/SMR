#!/usr/bin/env python3
"""
Update albums.json with press quotes from SMR_Albums_Press.csv,
update cover images, and clean up metadata.
"""

import json
import csv
import os
import re

BASE_PATH = '/Users/brandon/Music/SMR/SMR_Archive'
ALBUMS_JSON = os.path.join(BASE_PATH, 'smr-archive-site/data/albums.json')
PRESS_CSV = os.path.join(BASE_PATH, 'SMR_Albums_Press.csv')

# Cover image updates
COVER_UPDATES = {
    'dark-academy': 'DA.jpg',
    'field-guide-for-the-zombie-survivalist': 'FGZS.jpg',
    'happy-to-see-me': 'H2SM.jpg',
    'live-at-the-bridge': 'LongWallsLive_Cover_72_small-1.jpg'
}

# Metadata cleanup - format: (releaseDate, catalogNumber, formats)
# releaseDate format: YYYY-MM-DD
# catalogNumber format: SMRXXX
# formats: list of strings
METADATA_UPDATES = {
    # The Longwalls
    'field-guide-for-the-zombie-survivalist': ('2008-10-31', 'SMR001', ['CD', 'Digital']),
    'dark-academy': ('2010-06-01', 'SMR002', ['CD', 'Digital']),
    'careers-in-science': ('2011-06-07', 'SMR003', ['CD', 'Digital']),
    'kowloon': ('2012-10-30', 'SMR004', ['CD', 'Digital']),
    'gold-standard': ('2015-03-10', 'SMR005', ['Vinyl', 'CD', 'Digital']),
    'live-at-the-bridge': ('2016-03-15', 'SMR006', ['Digital']),
    'red-shirts': ('2019-03-26', 'SMR007', ['CD', 'Digital']),

    # Kurt von Stetten
    'birds-and-clouds': ('2006-03-14', 'SMR008', ['Vinyl', 'Digital']),
    'cyclops': ('2010-04-01', 'SMR009', ['CD', 'Digital']),
    'pyramid': ('2011-04-01', 'SMR010', ['CD', 'Digital']),
    'cycle': ('2012-03-01', 'SMR011', ['CD', 'Digital']),
    'broken-but-not-undone': ('2012-10-01', 'SMR012', ['CD', 'Digital']),
    'androlafi': ('2013-02-09', 'SMR013', ['CD', 'Digital']),
    'animals': ('2014-09-30', 'SMR014', ['Digital']),
    'bon-fortuna': ('2015-10-06', 'SMR015', ['Digital']),

    # Gatsby
    'five-songs': ('2003-01-01', 'SMR016', ['CD']),
    'floods-fires': ('2005-05-01', 'SMR017', ['CD', 'Digital']),
    'floods-fires-turbo-edition': ('2012-11-01', 'SMR018', ['Digital']),
    'live-on-air-01-05': ('2013-06-01', 'SMR019', ['Digital']),
    'the-amy-single': ('2004-01-01', 'SMR020', ['CD']),

    # Dan London
    'happy-to-see-me': ('2013-04-30', 'SMR021', ['CD', 'Digital']),
    'i-will-take-you-back': ('2016-09-01', 'SMR022', ['Digital']),

    # Various Artists
    'full-circle-commonwealth-women-up-front': ('2016-03-08', 'SMR023', ['Digital']),

    # Kurt von Stetten extras (singles/EPs from albums)
    'gutt': ('2010-04-01', 'SMR009-1', ['Digital']),
    'history': ('2010-04-01', 'SMR009-2', ['Digital']),
    'into-the-safety-of-the-alley': ('2010-04-01', 'SMR009-3', ['Digital']),
    'tree': ('2010-04-01', 'SMR009-4', ['Digital']),
}

def parse_press_quotes(press_text):
    """Parse press quotes from CSV text into structured format."""
    if not press_text or press_text.strip() == 'NA':
        return []

    quotes = []
    # Split by double newlines or by lines starting with —
    parts = re.split(r'\n\n+', press_text.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Try to split by em-dash variants
        match = re.match(r'^["""]?(.+?)["""]?\s*[—–-]\s*(.+)$', part, re.DOTALL)
        if match:
            text = match.group(1).strip().strip('"').strip('"').strip('"')
            source = match.group(2).strip()
            if text and source:
                quotes.append({
                    'text': text,
                    'source': source,
                    'url': None
                })
        else:
            # Maybe it's just a quote without clear separator
            # Try to find the last line as source
            lines = part.strip().split('\n')
            if len(lines) >= 2:
                last_line = lines[-1].strip()
                if last_line.startswith('—') or last_line.startswith('-'):
                    source = last_line.lstrip('—–- ').strip()
                    text = '\n'.join(lines[:-1]).strip().strip('"').strip('"')
                    if text and source:
                        quotes.append({
                            'text': text,
                            'source': source,
                            'url': None
                        })

    return quotes

def parse_featured_quote(quote_text):
    """Parse featured quote from CSV into structured format."""
    if not quote_text or quote_text.strip() == 'NA':
        return None

    quote_text = quote_text.strip()

    # Try to split by em-dash variants
    match = re.match(r'^["""]?(.+?)["""]?\s*[—–-]\s*(.+)$', quote_text, re.DOTALL)
    if match:
        text = match.group(1).strip().strip('"').strip('"').strip('"')
        source = match.group(2).strip()
        if text and source:
            return {
                'text': text,
                'source': source
            }

    return None

def slugify(name):
    """Convert album name to slug."""
    slug = name.lower()
    # Handle special cases
    slug = slug.replace("'", '')
    slug = slug.replace('+', '')
    slug = slug.replace('[', '')
    slug = slug.replace(']', '')
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug

def main():
    # Load albums
    print("Loading albums.json...")
    with open(ALBUMS_JSON, 'r') as f:
        albums = json.load(f)

    # Create lookup by slug
    albums_by_slug = {a['slug']: a for a in albums}
    albums_by_name = {a['name'].lower(): a for a in albums}

    # Load press CSV
    print("Loading press CSV...")
    press_data = {}
    with open(PRESS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            album_name = row['Album Name'].strip()
            featured = row.get('Featured Quote', '').strip()
            press = row.get('Press', '').strip()
            press_data[album_name.lower()] = {
                'featured': featured,
                'press': press
            }

    print(f"Found {len(press_data)} albums in CSV")

    # Update albums with press data
    updated_count = 0
    for album in albums:
        album_name_lower = album['name'].lower()
        slug = album['slug']

        # Update featured quote and press
        if album_name_lower in press_data:
            data = press_data[album_name_lower]

            # Update featured quote if we have one and album doesn't
            if data['featured'] and data['featured'] != 'NA':
                fq = parse_featured_quote(data['featured'])
                if fq:
                    if not album.get('featuredQuote') or not album['featuredQuote'].get('text'):
                        album['featuredQuote'] = fq
                        print(f"  Added featured quote to: {album['name']}")
                        updated_count += 1

            # Update press quotes if we have them and album doesn't have many
            if data['press'] and data['press'] != 'NA':
                new_quotes = parse_press_quotes(data['press'])
                if new_quotes:
                    existing = album.get('press', [])
                    if len(existing) < len(new_quotes):
                        album['press'] = new_quotes
                        print(f"  Updated press for: {album['name']} ({len(new_quotes)} quotes)")
                        updated_count += 1

        # Update cover images
        if slug in COVER_UPDATES:
            new_cover = f"assets/images/albums/{COVER_UPDATES[slug]}"
            album['coverImage'] = new_cover
            print(f"  Updated cover for: {album['name']} -> {COVER_UPDATES[slug]}")
            updated_count += 1

        # Update metadata
        if slug in METADATA_UPDATES:
            release_date, catalog_num, formats = METADATA_UPDATES[slug]

            if not album.get('releaseDate') or album['releaseDate'] != release_date:
                album['releaseDate'] = release_date
                print(f"  Updated release date for: {album['name']} -> {release_date}")

            if not album.get('catalogNumber'):
                album['catalogNumber'] = catalog_num
                print(f"  Updated catalog # for: {album['name']} -> {catalog_num}")

            if not album.get('formats') or len(album['formats']) == 0:
                album['formats'] = formats
                print(f"  Updated formats for: {album['name']} -> {formats}")

            updated_count += 1

    # Save updated albums
    print(f"\nSaving updated albums.json...")
    with open(ALBUMS_JSON, 'w') as f:
        json.dump(albums, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Updated {updated_count} albums.")

if __name__ == '__main__':
    main()
