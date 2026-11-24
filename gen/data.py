import csv
import json
import sqlite3

import chaya

def Lines(text: str):
    """Turns a text block into a sequence of (text, indentation) pairs."""
    # Ignore leading and trailing blank lines
    lines = text.splitlines()
    while lines and lines[0].strip() == '': lines = lines[1:]
    while lines and lines[-1].strip() == '': lines = lines[:-1]
    if not lines: return []
    # Expand tabs, and strip any common leading spaces
    lines_expanded = []
    leading = set()  # The leading indentation for non-empty lines
    for line in lines:
        line = line.replace('\t', '    ')
        lines_expanded.append(line)
        if line.strip():
            leading.add(len(line) - len(line.lstrip()))
    indent_lengths = list(sorted(leading))
    # Now we have all the lines we need
    ret = []
    for line in lines_expanded:
        ret.append((line.lstrip(),
                    indent_lengths.index(len(line) - len(line.lstrip())) if line.strip() else 0))
    return ret

def db(con, sql, *args):
    cursor = con.execute(sql, *args)
    return cursor.lastrowid

def get_book(con, Title):
    rows = con.execute('SELECT BookId FROM Book WHERE Title = ?', [Title]).fetchall()
    assert len(rows) == 1
    return rows[0][0]

# Book:   (BookId,   Title)
# Morsel: (BookId, MorselId,   Knum?)
# Line:   (BookId, MorselId, LineId,   Text, Indentation)
# Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
con = sqlite3.connect("data.db")
db(con, 
   """
   CREATE TABLE Book(
     BookId INTEGER PRIMARY KEY,
     Title
   )
   """)
db(con, 
   """
   CREATE TABLE Morsel(
     BookId INTEGER,
     MorselId INTEGER PRIMARY KEY,
     Knum,
     FOREIGN KEY(BookId) REFERENCES Book(BookId)
   )
   """)
db(con, 
   """
   CREATE TABLE Line(
     BookId INTEGER,
     MorselId INTEGER,
     LineId INTEGER PRIMARY KEY,
     Text,
     Indentation,
     FOREIGN KEY(BookId) REFERENCES Book(BookId),
     FOREIGN KEY(MorselId) REFERENCES Morsel(MorselId)
   )
   """)
db(con, 
   """
   CREATE TABLE Region(
     BookId INTEGER,
     MorselId INTEGER,
     RegionId INTEGER PRIMARY KEY,
     RegionType,
     Name,
     ImageUrl,
     PageUrl,
     Text,
     FOREIGN KEY(BookId) REFERENCES Book(BookId),
     FOREIGN KEY(MorselId) REFERENCES Morsel(MorselId)
     )
     """)

chaya.create_tables(con)

# Manually add books in preferred order.
for Title in ['Ryder', 'Brough', 'Tawney', 'More', 'Mādhavānanda', 'Telang', 'Kale', 'Gopinath1914', 'Gopinath1896', 'External', 'Kosambi']:
    db(con, "INSERT INTO Book(Title) VALUES(?)", [Title])


BookId = get_book(con, 'Ryder')
with open('data/alignment/Ryder.csv') as f:
    for row in csv.reader(f):
        (n, text, kosambi) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId, Knum))
        for (Text, Indentation) in Lines(text):
            db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId, MorselId,   Text, Indentation))

BookId = get_book(con, 'Brough')
with open('data/alignment/Brough.csv') as f:
    for row in csv.reader(f):
        (n, text, kosambi) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId, Knum))
        for (Text, Indentation) in Lines(text):
            db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId, MorselId,   Text, Indentation))

BookId = get_book(con, 'More')
with open('data/alignment/More.csv') as f:
    for row in csv.reader(f):
        (text, kosambi, comments) = row
        try:
            kosambi = f'K{int(kosambi[1:]):03}'
            Knum = kosambi
        except:
            Knum = None
        if not Knum: continue # Keep only the Bhartṛhari verses.
        MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId, Knum))
        for (Text, Indentation) in Lines(text):
            db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId, MorselId,   Text, Indentation))

BookId = get_book(con, 'Mādhavānanda')
with open('data/alignment/Madhavananda.csv') as f:
    for row in csv.reader(f):
        (_, text, kosambi) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId, Knum))
        for (Text, Indentation) in Lines(text):
            db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId, MorselId,   Text, Indentation))

BookId = get_book(con, 'External')
with open('data/alignment/External.csv') as f:
    for row in csv.reader(f):
        (text, Knum) = row
        try:
            Knum = f'K{int(Knum[1:]):03}'
        except:
            continue
        MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId, Knum))
        for (Text, Indentation) in Lines(text):
            db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId, MorselId,   Text, Indentation))


# Gopinath's two editions, from their verse exports (gen/chaya.py). The CSV numbers the edition's verses through its
# three śatakas, with rows for pages that are not verses (a śataka's title page, a blank page, a verse going on): the
# verse rows, in order, are the export's keys in śataka order (N, S, V) and number.
gopinath_rows = [row for row in csv.reader(open('data/alignment/Gopinath.csv'))][1:]
gopinath_knums = [f'K{int(kosambi):03}' if kosambi.strip().isdigit() else None
                  for (comment, gopinath_num, img1896, img1914, kosambi) in gopinath_rows if not (comment and not kosambi)]
for (Title, book) in [('Gopinath1914', 'gopinath-1914'), ('Gopinath1896', 'gopinath-1896')]:
    BookId = get_book(con, Title)
    verses = chaya.verses(book)
    letters = []
    for verse in verses:
        if verse['key'][0] not in letters: letters.append(verse['key'][0])
    offset, total = {}, 0
    for letter in letters:
        offset[letter] = total
        total += max(int(verse['key'][1:]) for verse in verses if verse['key'][0] == letter)
    assert total == len(gopinath_knums), (book, total, len(gopinath_knums))
    for verse in sorted(verses, key=lambda verse: (letters.index(verse['key'][0]), int(verse['key'][1:]))):
        Knum = gopinath_knums[offset[verse['key'][0]] + int(verse['key'][1:]) - 1]
        MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId, Knum))
        chaya.add_blocks(con, BookId, MorselId, book, verse)


BookId1 = get_book(con, 'Tawney')
BookId2 = get_book(con, 'Telang')
telang_verses = {verse['key']: verse for verse in chaya.verses('telang')}
telang_headings = {name: '\n'.join('\n'.join(region['text']) for regions in types.values() for region in regions)
                   for (name, types) in json.load(open('data/regions/telang-regions-out.json'))['regions'] if name.endswith('~H')}
with open('data/alignment/Telang-Tawney.csv') as f:
    rows = csv.reader(f)
    next(rows)   # the header: Telang,,Kosambi,Tawney
    for row in rows:
        (telang, snippet, kosambi, tawney) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        if tawney:
            MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId1, Knum))
            for (Text, Indentation) in Lines(tawney):
                db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId1, MorselId,   Text, Indentation))
        if telang:
            MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId2, Knum))
            if telang in telang_verses:
                chaya.add_blocks(con, BookId2, MorselId, 'telang', telang_verses[telang])
            else:
                # A heading ("N014~H"): its text, as the region finder read it.
                for (Text, Indentation) in Lines(telang_headings.get(telang, '')):
                    db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId2, MorselId,   Text, Indentation))

# Kale's verses, from its verse export, with their Kosambi numbers from data/alignment/Kale.csv (gen/align_kale.py).
BookId = get_book(con, 'Kale')
kale_knums = {row['Kale']: row['Kosambi'] for row in csv.DictReader(open('data/alignment/Kale.csv'))}
for verse in chaya.verses('kale-1913'):
    MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId, kale_knums.get(verse['key']) or None))
    chaya.add_blocks(con, BookId, MorselId, 'kale-1913', verse)

# Kosambi's edition: each verse with its blocks (the verse, its footnotes), from the regions marked on its page images
# (data/regions/kosambi-regions-out.json), with their text; the images are cut from the edition's PDF (archive.org's)
# by gen/chaya_crops.py, and are on R2 with the PDF (gen/chaya.py).
BookId = get_book(con, 'Kosambi')
with open('data/regions/kosambi-regions-out.json') as file:
    t = json.load(file)
    for (region_name, types_and_regions) in t['regions']:
        Knum = 'K' + region_name
        MorselId = db(con, "INSERT INTO Morsel(BookId, Knum) VALUES(?, ?)", (BookId, Knum))
        parts = []
        for (type, regions) in types_and_regions.items():
            for region in regions:
                assert isinstance(region['text'], list) and all(isinstance(line, str) for line in region['text'])
                parts.append({'role': type, 'text': '\n'.join(region['text']), 'regions': [chaya.kosambi_region(region, t['totWidth'], t['totHeight'])]})
        chaya.add_blocks(con, BookId, MorselId, 'kosambi', {'key': Knum, 'parts': parts}, pdf='kosambi.pdf')

con.execute('CREATE INDEX i1 ON Line(MorselId)')
con.execute('CREATE INDEX i2 ON Region(MorselId)')
con.execute('CREATE INDEX i3 ON Morsel(BookId)')
con.execute('CREATE INDEX i4 ON Morsel(Knum)')
con.commit()
con.close()
