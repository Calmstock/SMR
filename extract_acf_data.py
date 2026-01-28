#!/usr/bin/env python3
"""
Extract ACF (Advanced Custom Fields) data from WordPress SQL dump.
This includes: featured quotes, press quotes, track listings, credits, YouTube embeds.
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
    text = text.replace('\\"', '"').replace("\\'", "'").replace("\\r\\n", "\n").replace("\\n", "\n")
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>\s*<p[^>]*>', '\n\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_quote_text_and_source(quote_html):
    """Extract quote text and source from HTML like: <em>Quote</em><div class="featured-quote">—Source</div>"""
    if not quote_html:
        return None, None

    quote_html = quote_html.replace("\\'", "'").replace("\\r\\n", "\n")

    # Extract quote text (usually in <em> tags)
    quote_match = re.search(r'<em[^>]*>(.*?)</em>', quote_html, re.DOTALL | re.IGNORECASE)
    quote_text = clean_html(quote_match.group(1)) if quote_match else None

    # If no <em>, try to get text before the source
    if not quote_text:
        text_before = re.sub(r'<div[^>]*class="featured-quote"[^>]*>.*?</div>', '', quote_html, flags=re.DOTALL | re.IGNORECASE)
        quote_text = clean_html(text_before)

    # Extract source (usually in <div class="featured-quote"> or after em dash)
    source_match = re.search(r'<div[^>]*class="featured-quote"[^>]*>(.*?)</div>', quote_html, re.DOTALL | re.IGNORECASE)
    if source_match:
        source = clean_html(source_match.group(1))
        # Remove leading em dash
        source = re.sub(r'^[—–-]\s*', '', source)
    else:
        # Try to find source after em dash
        source_match = re.search(r'[—–-]\s*(.+?)$', clean_html(quote_html))
        source = source_match.group(1) if source_match else None

    return quote_text, source

def parse_more_quotes(quotes_html):
    """Parse multiple quotes from the more_quotes field."""
    if not quotes_html:
        return []

    quotes_html = quotes_html.replace("\\'", "'").replace("\\r\\n", "\n").replace("\\n", "\n")
    quotes = []

    # Split by double newlines or paragraph breaks
    parts = re.split(r'\n\n+|</p>\s*<p[^>]*>', quotes_html)

    current_quote = None
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Check if this part has a source link
        source_match = re.search(r'[—–-]\s*<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', part)
        if source_match:
            quote_text = re.sub(r'[—–-]\s*<a[^>]*>.*?</a>.*$', '', part, flags=re.DOTALL)
            quote_text = clean_html(quote_text)
            source_name = source_match.group(2)
            source_url = source_match.group(1)
            if quote_text:
                quotes.append({
                    'text': quote_text,
                    'source': source_name,
                    'url': source_url
                })
        elif re.search(r'[—–-]', part):
            # Source without link - find the LAST em-dash to split quote from source
            # Use greedy match to get everything up to the last em-dash
            cleaned = clean_html(part)
            # Find the last em-dash (source attribution typically at end)
            # Look for pattern: newline + dash or just dash near end
            match = re.search(r'^(.*)\n[—–-]\s*(.+)$', cleaned, re.DOTALL)
            if not match:
                # Try finding last em-dash on same line
                match = re.match(r'^(.+)[—–-]\s*([A-Z][^—–-]+)$', cleaned, re.DOTALL)
            if match:
                quotes.append({
                    'text': match.group(1).strip(),
                    'source': match.group(2).strip(),
                    'url': None
                })

    return quotes

def parse_track_listing_and_credits(track_html):
    """Parse track listing HTML to extract tracks and credits separately."""
    if not track_html:
        return [], None

    track_html = track_html.replace("\\'", "'").replace("\\r\\n", "\n").replace("\\n", "\n")

    tracks = []
    credits = None

    # Split into tracks and credits sections
    # Look for "Credits" header
    credits_match = re.search(r'Credits\s*(.*)', track_html, re.DOTALL | re.IGNORECASE)
    tracks_section = track_html

    if credits_match:
        credits = clean_html(credits_match.group(1))
        # Remove credits from tracks section
        tracks_section = track_html[:credits_match.start()]

    # Extract tracks from <li> tags
    track_items = re.findall(r'<li[^>]*>(.*?)</li>', tracks_section, re.IGNORECASE | re.DOTALL)

    for i, item in enumerate(track_items):
        title = clean_html(item).strip()
        if title:
            tracks.append({
                'number': i + 1,
                'title': title
            })

    return tracks, credits

def extract_youtube_id(embed_html):
    """Extract YouTube video/playlist ID from embed iframe."""
    if not embed_html:
        return None, None

    embed_html = embed_html.replace("\\'", "'")

    # Check for playlist
    playlist_match = re.search(r'list=([A-Za-z0-9_-]+)', embed_html)
    if playlist_match:
        return 'playlist', playlist_match.group(1)

    # Check for single video
    video_match = re.search(r'embed/([A-Za-z0-9_-]+)', embed_html)
    if video_match and video_match.group(1) != 'videoseries':
        return 'video', video_match.group(1)

    return None, None

def main():
    print(f"Reading SQL file: {SQL_FILE}")

    # Read wp_postmeta line
    with open(SQL_FILE, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f, 1):
            if i == 190:
                postmeta_content = line
                break

    # Load existing albums
    with open(os.path.join(OUTPUT_PATH, 'albums.json'), 'r') as f:
        albums = json.load(f)

    # Load products to get post_id to slug mapping
    with open(os.path.join(OUTPUT_PATH, 'products_raw.json'), 'r') as f:
        products = json.load(f)

    # Create post_id to slug mapping
    id_to_slug = {p['id']: p['slug'] for p in products}
    slug_to_album = {a['slug']: a for a in albums}

    print(f"\nExtracting ACF data for {len(products)} products...")

    # Extract featured_quote
    print("\n1. Featured Quotes:")
    matches = re.findall(r"\((\d+),(\d+),'featured_quote','((?:[^']|\\\\')*)'\)", postmeta_content)
    featured_quotes = {}
    for m in matches:
        post_id = int(m[1])
        quote_text, quote_source = extract_quote_text_and_source(m[2])
        if quote_text and post_id in id_to_slug:
            featured_quotes[post_id] = {
                'text': quote_text,
                'source': quote_source
            }
            slug = id_to_slug[post_id]
            print(f"  {slug}: \"{quote_text[:60]}...\" — {quote_source}")

    # Extract more_quotes (press reviews)
    print("\n2. Press Quotes:")
    matches = re.findall(r"\((\d+),(\d+),'more_quotes','((?:[^']|\\\\')*)'\)", postmeta_content)
    press_quotes = {}
    for m in matches:
        post_id = int(m[1])
        quotes = parse_more_quotes(m[2])
        if quotes and post_id in id_to_slug:
            press_quotes[post_id] = quotes
            slug = id_to_slug[post_id]
            print(f"  {slug}: {len(quotes)} quotes")

    # Extract track_listing (tracks + credits)
    print("\n3. Track Listings & Credits:")
    matches = re.findall(r"\((\d+),(\d+),'track_listing','((?:[^']|\\\\')*)'\)", postmeta_content)
    track_data = {}
    for m in matches:
        post_id = int(m[1])
        tracks, credits = parse_track_listing_and_credits(m[2])
        if post_id in id_to_slug:
            track_data[post_id] = {
                'tracks': tracks,
                'credits': credits
            }
            slug = id_to_slug[post_id]
            print(f"  {slug}: {len(tracks)} tracks, credits: {'Yes' if credits else 'No'}")

    # Extract youtube embeds
    print("\n4. YouTube Embeds:")
    matches = re.findall(r"\((\d+),(\d+),'youtube','((?:[^']|\\\\')*)'\)", postmeta_content)
    youtube_data = {}
    for m in matches:
        post_id = int(m[1])
        embed_type, embed_id = extract_youtube_id(m[2])
        if embed_id and post_id in id_to_slug:
            youtube_data[post_id] = {
                'type': embed_type,
                'id': embed_id
            }
            slug = id_to_slug[post_id]
            print(f"  {slug}: {embed_type} - {embed_id}")

    # Update albums.json with extracted data
    print("\n\nUpdating albums.json...")
    updated_count = 0

    for product in products:
        post_id = product['id']
        slug = product['slug']

        if slug not in slug_to_album:
            continue

        album = slug_to_album[slug]

        # Update featured quote
        if post_id in featured_quotes:
            fq = featured_quotes[post_id]
            album['featuredQuote'] = {
                'text': fq['text'],
                'source': fq['source']
            }

        # Update press quotes (REPLACE relatedPosts with real press)
        if post_id in press_quotes:
            album['press'] = press_quotes[post_id]

        # Update tracks and credits
        if post_id in track_data:
            td = track_data[post_id]
            if td['tracks']:
                album['tracks'] = td['tracks']
            if td['credits']:
                album['credits'] = td['credits']

        # Update YouTube embed
        if post_id in youtube_data:
            yt = youtube_data[post_id]
            if yt['type'] == 'playlist':
                album['youtubePlaylist'] = yt['id']
            else:
                album['youtubeVideo'] = yt['id']

        updated_count += 1

    # Save updated albums
    with open(os.path.join(OUTPUT_PATH, 'albums.json'), 'w') as f:
        json.dump(albums, f, indent=2)

    print(f"\nUpdated {updated_count} albums")

    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Featured quotes extracted: {len(featured_quotes)}")
    print(f"Press quote sets extracted: {len(press_quotes)}")
    print(f"Track listings extracted: {len(track_data)}")
    print(f"YouTube embeds extracted: {len(youtube_data)}")

    print("\nDone!")

if __name__ == '__main__':
    main()
