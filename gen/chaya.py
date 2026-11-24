"""Books made with scan-test (https://github.com/shreevatsa/scan-test): their verses, each with its blocks (the verse,
its commentary, translations, notes, footnotes…), from the book's verse export (data/chaya/<book>.json, written by
scan-test's webapp/tools/chaya_verses.mjs). Each block has its text and the images of the page regions it is printed in
(cut by gen/chaya_crops.py), with the page of the book it is on; the images and the books are on Cloudflare R2.

    Block:      (BookId, MorselId, BlockId,   Role, Text)
    BlockImage: (BlockId, ImageId,   ImageUrl, PageUrl)
"""
import json
import os

# Where the images and the books are: the R2 bucket's public URL; for a local look, BHARTRHARI_SCANS=../scans (the
# images only) with the site served from the repository's root.
SCANS = os.environ.get('BHARTRHARI_SCANS', 'https://pub-39d5e387e3434cada5b9f57c4e120bb9.r2.dev')


def image_name(region):
    """The image of a page region: its page and box, as gen/chaya_crops.py names it."""
    x0, y0, x1, y1 = (round(v) for v in region['box'])
    return f"p{region['pdf_page']:03d}-{x0}-{y0}-{x1}-{y1}.jpg"


def kosambi_region(region, totWidth, totHeight):
    """A region of Kosambi's edition (data/regions/kosambi-regions-out.json: its page and box in the pixels of the
    page images) as a verse export's region, for its image (gen/chaya_crops.py) and its name (image_name): the
    edition's PDF (archive.org's, on R2 as books/kosambi.pdf) has a page for each page image."""
    box = [region['xmin'], region['ymin'], region['xmin'] + region['width'], region['ymin'] + region['height']]
    return {'pdf_page': region['page_id'], 'box': box, 'width': round(totWidth), 'height': round(totHeight)}


def verses(book):
    """The book's verses in book order: [{key, parts: [{role, type, text, regions}]}]."""
    data = json.load(open(f'data/chaya/{book}.json'))
    return list(data['verses'].values()) if isinstance(data['verses'], dict) else data['verses']


def create_tables(con):
    con.execute("""
        CREATE TABLE Block(
          BookId INTEGER,
          MorselId INTEGER,
          BlockId INTEGER PRIMARY KEY,
          Role,
          Text,
          FOREIGN KEY(BookId) REFERENCES Book(BookId),
          FOREIGN KEY(MorselId) REFERENCES Morsel(MorselId)
        )""")
    con.execute("""
        CREATE TABLE BlockImage(
          BlockId INTEGER,
          ImageId INTEGER PRIMARY KEY,
          ImageUrl,
          PageUrl,
          FOREIGN KEY(BlockId) REFERENCES Block(BlockId)
        )""")


def add_blocks(con, BookId, MorselId, book, verse, pdf=None):
    """A verse's blocks, in order, each with its images, for the morsel; `pdf`, the book's file on R2 under books/
    (by default <book>.chaya.pdf)."""
    pdf = pdf or f'{book}.chaya.pdf'
    for part in verse['parts']:
        if not part['text'].strip() and not part['regions']:
            continue
        BlockId = con.execute('INSERT INTO Block(BookId, MorselId, Role, Text) VALUES(?, ?, ?, ?)',
                              (BookId, MorselId, part['role'], part['text'])).lastrowid
        for region in part['regions']:
            con.execute('INSERT INTO BlockImage(BlockId, ImageUrl, PageUrl) VALUES(?, ?, ?)',
                        (BlockId, f'{SCANS}/{book}/{image_name(region)}', f"{SCANS}/books/{pdf}#page={region['pdf_page']}"))
