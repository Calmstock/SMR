#!/usr/bin/env python3
"""
Extract content from WordPress XML export for Static Motor Recordings archive site.
"""

import xml.etree.ElementTree as ET
import json
import re
import html
from datetime import datetime
from collections import defaultdict

# WordPress export namespace
NAMESPACES = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/'
}

def clean_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_urls(content):
    """Extract Bandcamp, SoundCloud, and YouTube URLs from content."""
    urls = {
        'bandcamp': [],
        'soundcloud': [],
        'youtube': []
    }
    if not content:
        return urls

    # Bandcamp
    bandcamp_patterns = [
        r'https?://[a-zA-Z0-9-]+\.bandcamp\.com[^\s"\'<>]*',
        r'bandcamp\.com/album/[^\s"\'<>]+'
    ]
    for pattern in bandcamp_patterns:
        urls['bandcamp'].extend(re.findall(pattern, content, re.IGNORECASE))

    # SoundCloud
    soundcloud_patterns = [
        r'https?://soundcloud\.com/[^\s"\'<>]+',
        r'api\.soundcloud\.com/playlists/[0-9]+'
    ]
    for pattern in soundcloud_patterns:
        urls['soundcloud'].extend(re.findall(pattern, content, re.IGNORECASE))

    # YouTube
    youtube_patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'youtu\.be/([a-zA-Z0-9_-]+)',
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)'
    ]
    for pattern in youtube_patterns:
        urls['youtube'].extend(re.findall(pattern, content, re.IGNORECASE))

    # Dedupe
    urls['bandcamp'] = list(set(urls['bandcamp']))
    urls['soundcloud'] = list(set(urls['soundcloud']))
    urls['youtube'] = list(set(urls['youtube']))

    return urls

def parse_wordpress_xml(xml_path):
    """Parse WordPress XML export file."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    channel = root.find('channel')

    data = {
        'site': {
            'title': channel.find('title').text,
            'description': channel.find('description').text,
            'link': channel.find('link').text
        },
        'categories': [],
        'tags': [],
        'posts': [],
        'attachments': []
    }

    # Extract categories (artists)
    for cat in channel.findall('wp:category', NAMESPACES):
        data['categories'].append({
            'id': cat.find('wp:term_id', NAMESPACES).text,
            'slug': cat.find('wp:category_nicename', NAMESPACES).text,
            'name': cat.find('wp:cat_name', NAMESPACES).text
        })

    # Extract tags (albums, topics)
    for tag in channel.findall('wp:tag', NAMESPACES):
        data['tags'].append({
            'id': tag.find('wp:term_id', NAMESPACES).text,
            'slug': tag.find('wp:tag_slug', NAMESPACES).text,
            'name': tag.find('wp:tag_name', NAMESPACES).text
        })

    # Extract items (posts, attachments)
    for item in channel.findall('item'):
        post_type = item.find('wp:post_type', NAMESPACES).text
        status = item.find('wp:status', NAMESPACES).text

        if status != 'publish':
            continue

        content_encoded = item.find('content:encoded', NAMESPACES)
        content = content_encoded.text if content_encoded is not None else ""

        excerpt_encoded = item.find('excerpt:encoded', NAMESPACES)
        excerpt = excerpt_encoded.text if excerpt_encoded is not None else ""

        # Get categories and tags for this item
        item_categories = []
        item_tags = []
        for category in item.findall('category'):
            domain = category.get('domain')
            if domain == 'category':
                item_categories.append(category.text)
            elif domain == 'post_tag':
                item_tags.append(category.text)

        pub_date_str = item.find('pubDate').text
        if pub_date_str:
            try:
                pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
                pub_date_iso = pub_date.strftime('%Y-%m-%d')
            except:
                pub_date_iso = pub_date_str
        else:
            pub_date_iso = None

        post_data = {
            'id': item.find('wp:post_id', NAMESPACES).text,
            'title': item.find('title').text,
            'slug': item.find('wp:post_name', NAMESPACES).text,
            'date': pub_date_iso,
            'content': content,
            'excerpt': excerpt,
            'categories': item_categories,
            'tags': item_tags,
            'urls': extract_urls(content)
        }

        if post_type == 'post':
            data['posts'].append(post_data)
        elif post_type == 'attachment':
            attachment_url = item.find('wp:attachment_url', NAMESPACES)
            post_data['url'] = attachment_url.text if attachment_url is not None else None
            data['attachments'].append(post_data)

    # Sort posts by date
    data['posts'].sort(key=lambda x: x['date'] or '', reverse=True)

    return data

def create_catalog_data(wp_data, csv_catalog):
    """Create structured catalog data from WordPress data and CSV."""

    # Album data structure based on CSV and extracted content
    albums = []

    # Parse CSV catalog
    import csv
    with open(csv_catalog, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            album_name = row['Album Name']
            artist_name = row['Artist Name']

            # Create slug from album name
            slug = re.sub(r'[^a-z0-9]+', '-', album_name.lower()).strip('-')
            artist_slug = re.sub(r'[^a-z0-9]+', '-', artist_name.lower()).strip('-')

            album = {
                'name': album_name,
                'artist': artist_name,
                'slug': slug,
                'artistSlug': artist_slug,
                'releaseDate': None,
                'catalogNumber': None,
                'formats': [],
                'coverImage': None,
                'featuredQuote': None,
                'description': None,
                'tracks': [],
                'credits': None,
                'press': [],
                'bandcampUrl': None,
                'soundcloudPlaylist': None,
                'youtubePlaylist': None,
                'relatedPosts': []
            }

            # Find related posts by matching album name in tags
            for post in wp_data['posts']:
                if album_name in post['tags'] or album_name.lower() in [t.lower() for t in post['tags']]:
                    album['relatedPosts'].append({
                        'id': post['id'],
                        'title': post['title'],
                        'date': post['date'],
                        'excerpt': clean_html(post['excerpt']) or clean_html(post['content'])[:200]
                    })

                    # Extract URLs from related posts
                    if post['urls']['bandcamp'] and not album['bandcampUrl']:
                        album['bandcampUrl'] = post['urls']['bandcamp'][0]
                    if post['urls']['soundcloud'] and not album['soundcloudPlaylist']:
                        album['soundcloudPlaylist'] = post['urls']['soundcloud'][0]
                    if post['urls']['youtube'] and not album['youtubePlaylist']:
                        album['youtubePlaylist'] = post['urls']['youtube'][0]

            albums.append(album)

    return albums

def create_artist_data(wp_data, albums):
    """Create artist data from categories and albums."""

    artists = {}

    # Get artist categories
    for cat in wp_data['categories']:
        if cat['name'] not in ['Uncategorized']:
            artists[cat['name']] = {
                'name': cat['name'],
                'slug': cat['slug'],
                'bio': None,
                'heroImage': None,
                'quote': None,
                'bandcampUrl': None,
                'soundcloudPlaylist': None,
                'youtubePlaylist': None,
                'albums': []
            }

    # Add albums to artists
    for album in albums:
        artist_name = album['artist']
        if artist_name in artists:
            artists[artist_name]['albums'].append({
                'name': album['name'],
                'slug': album['slug']
            })

            # Use album URLs as fallback for artist
            if album['bandcampUrl'] and not artists[artist_name]['bandcampUrl']:
                artists[artist_name]['bandcampUrl'] = album['bandcampUrl']

    return list(artists.values())

def create_timeline_data(wp_data):
    """Create timeline data from blog posts for About page."""

    timeline = []

    for post in wp_data['posts']:
        # Categorize posts
        post_type = 'news'
        title_lower = post['title'].lower() if post['title'] else ''

        if any(word in title_lower for word in ['review', 'love', 'praise', 'kind words', 'best of']):
            post_type = 'press'
        elif any(word in title_lower for word in ['out now', 'on sale', 'release', 'vinyl', 'digital']):
            post_type = 'release'
        elif any(word in title_lower for word in ['live', 'show', 'concert', 'tour']):
            post_type = 'live'
        elif any(word in title_lower for word in ['video', 'premiere']):
            post_type = 'video'
        elif any(word in title_lower for word in ['mtv', 'tv', 'placement']):
            post_type = 'placement'
        elif any(word in title_lower for word in ['radio', 'wmbr', 'wmfo', 'pipeline']):
            post_type = 'radio'

        timeline.append({
            'date': post['date'],
            'title': post['title'],
            'type': post_type,
            'categories': post['categories'],
            'tags': post['tags'],
            'excerpt': clean_html(post['excerpt']) or clean_html(post['content'])[:300]
        })

    return timeline

def main():
    import os

    base_path = '/Users/brandon/Music/SMR/SMR_Archive'
    xml_path = os.path.join(base_path, 'staticmotorrecordings.WordPress.2026-01-24.xml')
    csv_path = os.path.join(base_path, 'SMR_Catalog_Basic.csv')
    output_path = os.path.join(base_path, 'smr-archive-site/data')

    print("Parsing WordPress XML export...")
    wp_data = parse_wordpress_xml(xml_path)

    print(f"Found {len(wp_data['posts'])} posts")
    print(f"Found {len(wp_data['categories'])} categories")
    print(f"Found {len(wp_data['tags'])} tags")
    print(f"Found {len(wp_data['attachments'])} attachments")

    print("\nCreating catalog data...")
    albums = create_catalog_data(wp_data, csv_path)
    print(f"Created {len(albums)} album entries")

    print("\nCreating artist data...")
    artists = create_artist_data(wp_data, albums)
    print(f"Created {len(artists)} artist entries")

    print("\nCreating timeline data...")
    timeline = create_timeline_data(wp_data)
    print(f"Created {len(timeline)} timeline entries")

    # Save JSON files
    os.makedirs(output_path, exist_ok=True)

    with open(os.path.join(output_path, 'albums.json'), 'w') as f:
        json.dump(albums, f, indent=2)
    print(f"\nSaved albums.json")

    with open(os.path.join(output_path, 'artists.json'), 'w') as f:
        json.dump(artists, f, indent=2)
    print(f"Saved artists.json")

    with open(os.path.join(output_path, 'timeline.json'), 'w') as f:
        json.dump(timeline, f, indent=2)
    print(f"Saved timeline.json")

    with open(os.path.join(output_path, 'site.json'), 'w') as f:
        json.dump(wp_data['site'], f, indent=2)
    print(f"Saved site.json")

    # Save raw posts for reference
    with open(os.path.join(output_path, 'posts.json'), 'w') as f:
        json.dump(wp_data['posts'], f, indent=2)
    print(f"Saved posts.json")

    print("\nDone!")

if __name__ == '__main__':
    main()
