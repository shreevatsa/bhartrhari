"""Cut an image of every block of a book's verses, from the book's scan.

The verses come from scan-test's verse export (data/chaya/<book>.json, written by its webapp/tools/chaya_verses.mjs):
each verse's parts (verse, commentary, translation, notes, footnotes…) with the page regions they are printed in, a box
in the pixels of the page image the boxes were found on. Each page is drawn once at that size (poppler's pdftoppm),
and each region cut from it, with a small margin, as a greyscale JPEG named for its page and box:

    <out>/<book>/p<pdf page>-<x0>-<y0>-<x1>-<y1>.jpg

These are what the site shows in place of a block's text (gen/chaya.py). Files already there are
kept. Run with Pillow, e.g.:

    uv run --with pillow python gen/chaya_crops.py data/chaya/telang.json ~/w/scan-test/outputs/books/telang-dli.chaya.pdf scans/

Kosambi's edition, from its regions (data/regions/kosambi-regions-out.json) and its PDF (archive.org's):

    uv run --with pillow python gen/chaya_crops.py data/regions/kosambi-regions-out.json data/images/Kosambi-Epigrams.pdf scans/
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image

from chaya import crop_box, image_name, kosambi_region

QUALITY = 72




def main(verses_path, pdf_path, out_dir):
    data = json.load(open(verses_path))
    if 'totWidth' in data:
        # Kosambi's edition (data/regions/kosambi-regions-out.json), its images under kosambi/.
        book = 'kosambi'
        regions = [kosambi_region(region, data['totWidth'], data['totHeight'])
                   for _, types in data['regions'] for found in types.values() for region in found]
    else:
        book = os.path.splitext(os.path.basename(verses_path))[0]
        verses = data['verses'].values() if isinstance(data['verses'], dict) else data['verses']
        regions = [region for verse in verses for part in verse['parts'] for region in part['regions']]
    target = os.path.join(out_dir, book)
    os.makedirs(target, exist_ok=True)
    by_page = {}
    for region in regions:
        by_page.setdefault((region['pdf_page'], region['width'], region['height']), []).append(region)
    made = kept = 0
    with tempfile.TemporaryDirectory() as scratch:
        for (page, width, height), regions in sorted(by_page.items()):
            wanted = [region for region in regions if not os.path.exists(os.path.join(target, image_name(region)))]
            kept += len(regions) - len(wanted)
            if not wanted:
                continue
            base = os.path.join(scratch, f'page{page}')
            subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-scale-to-x', str(width), '-scale-to-y', str(height),
                            '-gray', '-png', '-singlefile', pdf_path, base], check=True)
            with Image.open(base + '.png') as image:
                for region in wanted:
                    image.crop(crop_box(region)).save(os.path.join(target, image_name(region)), 'JPEG', quality=QUALITY, optimize=True)
                    made += 1
            os.remove(base + '.png')
    print(f'{book}: {made} images made, {kept} already there, in {target}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
