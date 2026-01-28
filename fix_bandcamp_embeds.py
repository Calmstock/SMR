#!/usr/bin/env python3
"""
Fix Bandcamp embeds with correct album IDs.
"""

import json
import re

ALBUMS_JSON = '/Users/brandon/Music/SMR/SMR_Archive/smr-archive-site/data/albums.json'

# Correct album IDs from Bandcamp
CORRECT_EMBEDS = {
    # The Longwalls
    'careers-in-science': {
        'album_id': '2426230404',
        'url': 'https://thelongwalls.bandcamp.com/album/careers-in-science',
        'title': 'Careers in Science by The Longwalls'
    },
    'dark-academy': {
        'album_id': '220835075',
        'url': 'https://thelongwalls.bandcamp.com/album/dark-academy',
        'title': 'Dark Academy by The Longwalls'
    },
    'gold-standard': {
        'album_id': '1038709307',
        'url': 'https://thelongwalls.bandcamp.com/album/gold-standard',
        'title': 'Gold Standard by The Longwalls'
    },
    'kowloon': {
        'album_id': '1451702757',
        'url': 'https://thelongwalls.bandcamp.com/album/kowloon',
        'title': 'Kowloon by The Longwalls'
    },
    'live-at-the-bridge': {
        'album_id': '3280061942',
        'url': 'https://thelongwalls.bandcamp.com/album/live-at-the-bridge',
        'title': 'Live at The Bridge by The Longwalls'
    },
    'red-shirts': {
        'album_id': '892155279',
        'url': 'https://thelongwalls.bandcamp.com/album/red-shirts',
        'title': 'Red Shirts by The Longwalls'
    },
    'field-guide-for-the-zombie-survivalist': {
        'album_id': '3196483263',
        'url': 'https://thelongwalls.bandcamp.com/album/field-guide-for-the-zombie-survivalist',
        'title': 'Field Guide for the Zombie Survivalist by The Longwalls'
    },

    # Kurt von Stetten
    'pyramid': {
        'album_id': '949652847',
        'url': 'https://kurtvonstetten.bandcamp.com/album/pyramid',
        'title': 'Pyramid by Kurt von Stetten'
    },
    'gutt': {
        'album_id': '3969164635',
        'url': 'https://kurtvonstetten.bandcamp.com/album/gutt',
        'title': 'Gutt by Kurt von Stetten'
    },
    'history': {
        'album_id': '2576919820',
        'url': 'https://kurtvonstetten.bandcamp.com/album/history',
        'title': 'History by Kurt von Stetten'
    },
    'into-the-safety-of-the-alley': {
        'album_id': '466923479',
        'url': 'https://kurtvonstetten.bandcamp.com/album/into-the-safety-of-the-alley',
        'title': 'Into the Safety of the Alley by Kurt von Stetten'
    },
    'tree': {
        'album_id': '1710767013',
        'url': 'https://kurtvonstetten.bandcamp.com/album/tree',
        'title': 'Tree by Kurt von Stetten'
    },
    'cyclops': {
        'album_id': '3677298469',
        'url': 'https://kurtvonstetten.bandcamp.com/album/cyclops',
        'title': 'Cyclops by Kurt von Stetten'
    },
    'androlafi': {
        'album_id': '1031446612',
        'url': 'https://kurtvonstetten.bandcamp.com/album/androlafi',
        'title': 'Androlafi by Kurt von Stetten'
    },
    'animals': {
        'album_id': '782194552',
        'url': 'https://kurtvonstetten.bandcamp.com/album/animals',
        'title': 'Animals by Kurt von Stetten'
    },
    'birds-and-clouds': {
        'album_id': '617842240',
        'url': 'https://kurtvonstetten.bandcamp.com/album/birds-and-clouds',
        'title': 'Birds and Clouds by Kurt von Stetten'
    },
    'bon-fortuna': {
        'album_id': '2046206354',
        'url': 'https://kurtvonstetten.bandcamp.com/album/bon-fortuna',
        'title': 'Bon Fortuna by Kurt von Stetten'
    },
    'broken-but-not-undone': {
        'album_id': '4274708306',
        'url': 'https://kurtvonstetten.bandcamp.com/album/broken-but-not-undone',
        'title': 'Broken, but not undone by Kurt von Stetten'
    },
    'cycle': {
        'album_id': '1100626880',
        'url': 'https://kurtvonstetten.bandcamp.com/album/cycle',
        'title': 'Cycle by Kurt von Stetten'
    },

    # Dan London
    'happy-to-see-me': {
        'album_id': '2589783237',
        'url': 'https://danlondon.bandcamp.com/album/happy-to-see-me-2',
        'title': 'Happy To See Me by Dan London'
    },
    'i-will-take-you-back': {
        'album_id': '3469207098',
        'url': 'https://danlondon.bandcamp.com/album/i-will-take-you-back',
        'title': 'I Will Take You Back by Dan London'
    },

    # Gatsby
    'five-songs': {
        'album_id': '2014461788',
        'url': 'https://gatsby.bandcamp.com/album/five-songs',
        'title': 'Five Songs by Gatsby'
    },
    'floods-fires-turbo-edition': {
        'album_id': '2275489411',
        'url': 'https://gatsby.bandcamp.com/album/floods-fires-turbo-edition',
        'title': 'Floods + Fires (Turbo Edition!) by Gatsby'
    },
    'live-on-air-01-05': {
        'album_id': '1379393282',
        'url': 'https://gatsby.bandcamp.com/album/do-whatever-you-want-tape-is-rolling-gatsby-live-on-air-2001-2005',
        'title': 'Do Whatever you Want, Tape is Rolling: Gatsby Live On-Air 2001-2005 by Gatsby'
    },

    # Various Artists
    'full-circle-commonwealth-women-up-front': {
        'album_id': '3057375547',
        'url': 'https://fullcirclecomp.bandcamp.com/album/full-circle-commonwealth-women-up-front',
        'title': 'Full Circle - Commonwealth Women Up Front by Various Artists'
    },
}

def generate_embed(album_id, url, title):
    """Generate a Bandcamp embed with the correct format."""
    return f'<iframe style="border: 0; width: 100%; height: 120px;" src="https://bandcamp.com/EmbeddedPlayer/album={album_id}/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/artwork=none/transparent=true/" seamless><a href="{url}">{title}</a></iframe>'

def main():
    print("Loading albums.json...")
    with open(ALBUMS_JSON, 'r') as f:
        albums = json.load(f)

    fixed_count = 0
    for album in albums:
        slug = album['slug']

        if slug in CORRECT_EMBEDS:
            info = CORRECT_EMBEDS[slug]
            correct_embed = generate_embed(info['album_id'], info['url'], info['title'])

            # Check if current embed is different
            current_embed = album.get('bandcampEmbed', '')

            # Extract current album ID
            current_id_match = re.search(r'album=(\d+)', current_embed) if current_embed else None
            current_id = current_id_match.group(1) if current_id_match else None

            if current_id != info['album_id']:
                album['bandcampEmbed'] = correct_embed
                print(f"  Fixed: {album['name']} (was album={current_id}, now album={info['album_id']})")
                fixed_count += 1
            else:
                # Still update to ensure correct URL and title
                if current_embed != correct_embed:
                    album['bandcampEmbed'] = correct_embed
                    print(f"  Updated embed format: {album['name']}")

    print(f"\nSaving albums.json...")
    with open(ALBUMS_JSON, 'w') as f:
        json.dump(albums, f, indent=2, ensure_ascii=False)

    print(f"Done! Fixed {fixed_count} incorrect album IDs.")

if __name__ == '__main__':
    main()
