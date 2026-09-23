import urllib.request
import gzip
import io
import re
import os

def generate_epg():
    print("Downloading epg_BR.xml.gz from epg.pw...")
    req = urllib.request.Request(
        'https://epg.pw/xmltv/epg_BR.xml.gz',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        buf = io.BytesIO(resp.read())
        with gzip.GzipFile(fileobj=buf) as gz:
            raw_xml = gz.read().decode('utf-8', errors='ignore')

    print(f"Downloaded raw XML: {len(raw_xml) / (1024*1024):.2f} MB")

    playlist_path = os.path.join(os.path.dirname(__file__), '..', 'CanaisBR_AoVivo.m3u8')
    needed_ids = set()
    with open(playlist_path, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.search(r'tvg-id="([^"]+)"', line)
            if m:
                needed_ids.add(m.group(1))

    print(f"Needed channel IDs ({len(needed_ids)}):", sorted(needed_ids))

    channels_xml = []
    for m in re.finditer(r'<channel id="([^"]+)">.*?</channel>', raw_xml, re.DOTALL):
        if m.group(1) in needed_ids:
            channels_xml.append(m.group(0))

    programmes_xml = []
    for m in re.finditer(r'<programme channel="([^"]+)".*?</programme>', raw_xml, re.DOTALL):
        if m.group(1) in needed_ids:
            programmes_xml.append(m.group(0))

    out_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="Antigravity Custom EPG">\n'
    out_xml += "\n".join(channels_xml) + "\n"
    out_xml += "\n".join(programmes_xml) + "\n"
    out_xml += "</tv>\n"

    out_path = os.path.join(os.path.dirname(__file__), '..', 'epg.xml')
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out_xml)

    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Generated {out_path}: {size_mb:.2f} MB with {len(channels_xml)} channels and {len(programmes_xml)} programmes.")

if __name__ == '__main__':
    generate_epg()
