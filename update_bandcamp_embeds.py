#!/usr/bin/env python3
"""
Update all Bandcamp embeds to use medium size (120px) with no artwork.
"""

import json
import re
import os

ALBUMS_JSON = '/Users/brandon/Music/SMR/SMR_Archive/smr-archive-site/data/albums.json'

def update_bandcamp_embed(embed_html):
    """Update a Bandcamp embed to use medium size with no artwork."""
    if not embed_html:
        return embed_html

    # Extract the album ID from the embed
    album_match = re.search(r'album=(\d+)', embed_html)
    if not album_match:
        return embed_html

    album_id = album_match.group(1)

    # Extract the href link
    href_match = re.search(r'<a href="([^"]+)">([^<]+)</a>', embed_html)
    if not href_match:
        return embed_html

    href = href_match.group(1)
    link_text = href_match.group(2)

    # Build new embed with medium size (120px), no artwork, no tracklist
    new_embed = f'<iframe style="border: 0; width: 100%; height: 120px;" src="https://bandcamp.com/EmbeddedPlayer/album={album_id}/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/artwork=none/transparent=true/" seamless><a href="{href}">{link_text}</a></iframe>'

    return new_embed

def main():
    print("Loading albums.json...")
    with open(ALBUMS_JSON, 'r') as f:
        albums = json.load(f)

    updated_count = 0
    for album in albums:
        if album.get('bandcampEmbed'):
            old_embed = album['bandcampEmbed']
            new_embed = update_bandcamp_embed(old_embed)
            if old_embed != new_embed:
                album['bandcampEmbed'] = new_embed
                updated_count += 1
                print(f"  Updated: {album['name']}")

    print(f"\nSaving albums.json...")
    with open(ALBUMS_JSON, 'w') as f:
        json.dump(albums, f, indent=2, ensure_ascii=False)

    print(f"Done! Updated {updated_count} Bandcamp embeds.")

if __name__ == '__main__':
    main()
