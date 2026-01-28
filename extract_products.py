#!/usr/bin/env python3
"""
Extract product data from WordPress SQL dump including Shopp e-commerce data.
"""

import re
import json
import html
import os

BASE_PATH = '/Users/brandon/Music/SMR/SMR_Archive'
SQL_FILE = os.path.join(BASE_PATH, 'backup-1.23.2026_18-29-26_staticmo/mysql/staticmo_wplive.sql')
OUTPUT_PATH = os.path.join(BASE_PATH, 'smr-archive-site/data')

def clean_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    # Unescape MySQL escapes
    text = text.replace('\\"', '"').replace("\\'", "'").replace("\\r\\n", "\n").replace("\\n", "\n")
    # Remove HTML tags but preserve line breaks
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>\s*<p[^>]*>', '\n\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def parse_sql_value(s, start=0):
    """Parse a single SQL value starting at position start, handling quotes and escapes."""
    if start >= len(s):
        return None, start

    if s[start] == "'":
        # Quoted string - find matching end quote
        i = start + 1
        result = []
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                # Escaped character
                result.append(s[i:i+2])
                i += 2
            elif s[i] == "'":
                if i + 1 < len(s) and s[i+1] == "'":
                    # Doubled quote
                    result.append("'")
                    i += 2
                else:
                    # End of string
                    return ''.join(result), i + 1
            else:
                result.append(s[i])
                i += 1
        return ''.join(result), i
    else:
        # Unquoted value (number or NULL)
        end = start
        while end < len(s) and s[end] not in ',)':
            end += 1
        return s[start:end], end

def parse_row(row_str):
    """Parse a SQL row into fields."""
    fields = []
    i = 0
    while i < len(row_str):
        if row_str[i] in ' ,':
            i += 1
            continue
        value, i = parse_sql_value(row_str, i)
        if value is not None:
            fields.append(value)
        if i < len(row_str) and row_str[i] == ',':
            i += 1
    return fields

def extract_products_from_sql():
    """Extract Shopp product data from SQL dump."""
    print(f"Reading SQL file: {SQL_FILE}")

    # Read line 240 which contains wp_posts INSERT
    with open(SQL_FILE, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f, 1):
            if i == 240:
                content = line
                break

    # Split by ),( to get individual rows
    rows = content.split('),(')
    print(f"Total rows in wp_posts: {len(rows)}")

    products = {}
    artist_pages = {}

    for row in rows:
        if "'shopp_product'" in row or "'page'" in row:
            # Parse the row
            fields = parse_row(row)

            if len(fields) < 23:
                continue

            try:
                post_id = int(fields[0].lstrip('('))
                post_date = fields[2]
                post_content = fields[4]
                post_title = fields[5]
                post_excerpt = fields[6]
                post_status = fields[7]
                post_name = fields[11]  # slug
                post_type = fields[20]

                if post_status != 'publish':
                    continue

                if post_type == 'shopp_product':
                    products[post_id] = {
                        'id': post_id,
                        'title': post_title.replace("\\'", "'"),
                        'slug': post_name,
                        'description': clean_html(post_content),
                        'excerpt': clean_html(post_excerpt),
                        'date': post_date[:10] if post_date else None
                    }
                    print(f"  Found product: {post_title[:50]} (ID: {post_id})")

                elif post_type == 'page' and post_name in ['the-longwalls', 'kurt-von-stetten', 'gatsby', 'dan-london']:
                    artist_pages[post_name] = {
                        'slug': post_name,
                        'title': post_title.replace("\\'", "'"),
                        'bio': clean_html(post_content)
                    }
                    print(f"  Found artist page: {post_title}")

            except (ValueError, IndexError) as e:
                continue

    print(f"\nFound {len(products)} products")
    print(f"Found {len(artist_pages)} artist pages")
    return products, artist_pages

def extract_postmeta():
    """Extract metadata from wp_postmeta including ACF fields like track_listing."""
    print("\nExtracting post metadata (ACF fields)...")

    # Read line 190 which contains wp_postmeta INSERT
    with open(SQL_FILE, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f, 1):
            if i == 190:
                content = line
                break

    postmeta = {}

    # Find all track_listing entries
    # Pattern: (meta_id, post_id, 'track_listing', 'value')
    matches = re.findall(r"\((\d+),(\d+),'track_listing','((?:[^']|\\\\')*)'\)", content)
    print(f"  Found {len(matches)} track_listing entries")

    for m in matches:
        post_id = int(m[1])
        tracklist = m[2].replace("\\'", "'").replace("\\r\\n", "\n").replace("\\n", "\n")

        if post_id not in postmeta:
            postmeta[post_id] = {}
        postmeta[post_id]['track_listing'] = tracklist

    # Also look for release_date, catalog_number, etc.
    for field in ['release_date', 'catalog_number', 'credits']:
        matches = re.findall(rf"\((\d+),(\d+),'{field}','((?:[^']|\\\\')*)'\)", content)
        for m in matches:
            post_id = int(m[1])
            value = m[2].replace("\\'", "'")
            if post_id not in postmeta:
                postmeta[post_id] = {}
            postmeta[post_id][field] = value
            print(f"  Found {field} for post {post_id}")

    return postmeta

def parse_tracklist(tracklist_raw):
    """Parse tracklist from various formats."""
    if not tracklist_raw:
        return []

    tracks = []
    lines = tracklist_raw.strip().split('\n')

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Remove leading numbers like "1. " or "01. "
        line = re.sub(r'^[\d]+[\.\)\-\s]+', '', line)

        if line:
            tracks.append({
                'number': i + 1,
                'title': clean_html(line)
            })

    return tracks

def parse_tracklist_html(tracklist_html):
    """Parse tracklist from HTML list format."""
    if not tracklist_html:
        return []

    tracks = []

    # Remove the "Tracks" header if present
    tracklist_html = re.sub(r'^Tracks\s*', '', tracklist_html, flags=re.IGNORECASE)

    # Extract list items
    items = re.findall(r'<li[^>]*>(.*?)</li>', tracklist_html, re.IGNORECASE | re.DOTALL)

    for i, item in enumerate(items):
        title = clean_html(item).strip()
        if title:
            tracks.append({
                'number': i + 1,
                'title': title
            })

    return tracks

def main():
    # Extract products and artist pages
    products, artist_pages = extract_products_from_sql()

    # Extract postmeta (ACF fields like track_listing)
    postmeta = extract_postmeta()

    # Merge meta into products
    for pid, meta in postmeta.items():
        if pid in products:
            if 'meta' not in products[pid]:
                products[pid]['meta'] = {}
            products[pid]['meta'].update(meta)

    # Save raw extracted data
    with open(os.path.join(OUTPUT_PATH, 'products_raw.json'), 'w') as f:
        json.dump(list(products.values()), f, indent=2)
    print(f"\nSaved products_raw.json")

    # Print summary
    print("\n=== PRODUCTS FOUND ===")
    for pid, prod in sorted(products.items()):
        meta = prod.get('meta', {})
        desc = prod.get('description', '')
        print(f"\n{prod['title']}")
        print(f"  Slug: {prod['slug']}")
        print(f"  Description: {desc[:80]}..." if desc else "  Description: None")
        if meta:
            print(f"  Meta keys: {list(meta.keys())}")

    print("\n=== ARTIST PAGES ===")
    for slug, artist in artist_pages.items():
        bio = artist.get('bio', '')
        print(f"\n{artist['title']}")
        print(f"  Bio: {bio[:120]}..." if bio else "  Bio: None")

    # Update albums.json with extracted data
    print("\n\nUpdating albums.json with extracted data...")

    with open(os.path.join(OUTPUT_PATH, 'albums.json'), 'r') as f:
        albums = json.load(f)

    # Create slug-to-product mapping
    slug_to_product = {p['slug']: p for p in products.values()}

    updated_count = 0
    for album in albums:
        slug = album['slug']
        if slug in slug_to_product:
            prod = slug_to_product[slug]

            # Update description
            if prod.get('description') and not album.get('description'):
                album['description'] = prod['description']
                updated_count += 1
                print(f"  Updated description for: {album['name']}")

            # Update from meta
            meta = prod.get('meta', {})

            if meta.get('track_listing'):
                tracks = parse_tracklist_html(meta['track_listing'])
                if tracks:
                    album['tracks'] = tracks
                    print(f"  Found {len(tracks)} tracks for: {album['name']}")

            if meta.get('release_date') and not album.get('releaseDate'):
                # Format YYYYMMDD to YYYY-MM-DD
                raw_date = meta['release_date']
                if len(raw_date) == 8 and raw_date.isdigit():
                    formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                    album['releaseDate'] = formatted_date
                else:
                    album['releaseDate'] = raw_date
                print(f"  Set release date for: {album['name']}: {album['releaseDate']}")

            if meta.get('Catalog') and not album.get('catalogNumber'):
                album['catalogNumber'] = meta['Catalog']

            if meta.get('Format') and not album.get('formats'):
                formats = [f.strip() for f in meta['Format'].split(',')]
                album['formats'] = formats

            if meta.get('Credits') and not album.get('credits'):
                album['credits'] = meta['Credits']

    # Save updated albums
    with open(os.path.join(OUTPUT_PATH, 'albums.json'), 'w') as f:
        json.dump(albums, f, indent=2)

    print(f"\nUpdated {updated_count} albums with descriptions")

    # Update artists.json with bios
    print("\nUpdating artists.json with extracted bios...")

    with open(os.path.join(OUTPUT_PATH, 'artists.json'), 'r') as f:
        artists_data = json.load(f)

    for artist in artists_data:
        slug = artist['slug']
        if slug in artist_pages:
            bio = artist_pages[slug].get('bio')
            if bio and not artist.get('bio'):
                artist['bio'] = bio
                print(f"  Updated bio for {artist['name']}")

    with open(os.path.join(OUTPUT_PATH, 'artists.json'), 'w') as f:
        json.dump(artists_data, f, indent=2)

    print("\nDone!")

if __name__ == '__main__':
    main()
