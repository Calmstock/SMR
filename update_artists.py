#!/usr/bin/env python3
"""
Update artist data with hero images.
"""

import json
import os

BASE_PATH = '/Users/brandon/Music/SMR/SMR_Archive/smr-archive-site'

# Artist hero image mapping
ARTIST_IMAGES = {
    'the-longwalls': 'assets/images/artists/the-longwalls.jpg',
    'kurt-von-stetten': 'assets/images/artists/kurt-von-stetten.jpg',
    'gatsby': 'assets/images/artists/gatsby.jpg',
    'dan-london': 'assets/images/artists/dan-london.jpg'
}

# Artist Bandcamp URLs
ARTIST_BANDCAMP = {
    'the-longwalls': 'https://thelongwalls.bandcamp.com',
    'kurt-von-stetten': 'https://kurtvonstetten.bandcamp.com',
    'gatsby': 'https://gatsby.bandcamp.com',
    'dan-london': 'https://danlondon.bandcamp.com'
}

def main():
    # Load artists
    with open(os.path.join(BASE_PATH, 'data/artists.json'), 'r') as f:
        artists = json.load(f)

    # Update artists
    for artist in artists:
        slug = artist['slug']

        # Hero image
        if slug in ARTIST_IMAGES:
            image_path = os.path.join(BASE_PATH, ARTIST_IMAGES[slug])
            if os.path.exists(image_path):
                artist['heroImage'] = ARTIST_IMAGES[slug]
                print(f"Updated hero image for {artist['name']}")

        # Bandcamp URL
        if slug in ARTIST_BANDCAMP:
            artist['bandcampUrl'] = ARTIST_BANDCAMP[slug]
            print(f"Updated Bandcamp URL for {artist['name']}")

    # Save updated artists
    with open(os.path.join(BASE_PATH, 'data/artists.json'), 'w') as f:
        json.dump(artists, f, indent=2)

    print("\nDone!")

if __name__ == '__main__':
    main()
