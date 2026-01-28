#!/usr/bin/env python3
"""
Update album data with cover image paths.
"""

import json
import os

BASE_PATH = '/Users/brandon/Music/SMR/SMR_Archive/smr-archive-site'
IMAGES_PATH = 'assets/images/albums'

# Map album slugs to image filenames (check for both jpg and png)
def get_cover_path(slug):
    for ext in ['.jpg', '.png']:
        filename = slug + ext
        full_path = os.path.join(BASE_PATH, IMAGES_PATH, filename)
        if os.path.exists(full_path):
            return IMAGES_PATH + '/' + filename
    return None

def main():
    # Load albums
    with open(os.path.join(BASE_PATH, 'data/albums.json'), 'r') as f:
        albums = json.load(f)

    # Update cover images
    updated = 0
    missing = []
    for album in albums:
        cover = get_cover_path(album['slug'])
        if cover:
            album['coverImage'] = cover
            updated += 1
            print(f"Found: {album['slug']} -> {cover}")
        else:
            missing.append(album['slug'])
            print(f"Missing: {album['slug']}")

    # Save updated albums
    with open(os.path.join(BASE_PATH, 'data/albums.json'), 'w') as f:
        json.dump(albums, f, indent=2)

    print(f"\nUpdated {updated} albums with cover images")
    if missing:
        print(f"Missing covers for: {', '.join(missing)}")

if __name__ == '__main__':
    main()
