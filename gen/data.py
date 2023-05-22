import csv
import json
import sqlite3

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
    with con:
        cursor = con.execute(sql, *args)
    return cursor.lastrowid

# Book:   (BookId,   Title)
# Morsel: (BookId, MorselId,   NumInBook, Knum?)
# Line:   (BookId, MorselId, LineId,   Text, Indentation)
# Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
con = sqlite3.connect("data.db")
db(con, "CREATE TABLE Book(BookId INTEGER PRIMARY KEY, Title)")
db(con, "CREATE TABLE Morsel(BookId, MorselId INTEGER PRIMARY KEY,   NumInBook, Knum)")
db(con, "CREATE TABLE Line(BookId, MorselId, LineId INTEGER PRIMARY KEY,   Text, Indentation)")
db(con, "CREATE TABLE Region(BookId, MorselId, RegionId INTEGER PRIMARY KEY,   RegionType, Name, ImageUrl, PageUrl, Text)")

BookId = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Ryder'])
with open('data/alignment/Ryder.csv') as f:
    NumInBook = 0
    for row in csv.reader(f):
        NumInBook += 1
        (n, text, kosambi) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        MorselId = db(con, "INSERT INTO Morsel(BookId, NumInBook, Knum) VALUES(?, ?, ?)", (BookId, NumInBook, Knum))
        for (Text, Indentation) in Lines(text):
            db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId, MorselId,   Text, Indentation))

BookId = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Brough'])
with open('data/alignment/Brough.csv') as f:
    NumInBook = 0
    for row in csv.reader(f):
        NumInBook += 1
        (n, text, kosambi) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        MorselId = db(con, "INSERT INTO Morsel(BookId, NumInBook, Knum) VALUES(?, ?, ?)", (BookId, NumInBook, Knum))
        for (Text, Indentation) in Lines(text):
            db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId, MorselId,   Text, Indentation))

BookId = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Mādhavānanda'])
with open('data/alignment/Madhavananda.csv') as f:
    NumInBook = 0
    for row in csv.reader(f):
        NumInBook += 1
        (_, text, kosambi) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        MorselId = db(con, "INSERT INTO Morsel(BookId, NumInBook, Knum) VALUES(?, ?, ?)", (BookId, NumInBook, Knum))
        for (Text, Indentation) in Lines(text):
            db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId, MorselId,   Text, Indentation))

BookId1 = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Gopinath1914'])
BookId2 = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Gopinath1896'])
imagesPrefix = '../data/images/'
with open('data/alignment/Gopinath.csv') as f:
    NumInBook = 0
    for row in csv.reader(f):
        NumInBook += 1
        (comment, gopinath_num, gopinath1896_img, gopinath1914_img, kosambi) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        if comment == '(continued)': # Happens in two places. Reuse MorselId.
            MorselId1 = con.execute('SELECT MAX(MorselId) FROM Morsel WHERE BookId = ?', [BookId1]).fetchall()[0][0]
            MorselId2 = con.execute('SELECT MAX(MorselId) FROM Morsel WHERE BookId = ?', [BookId2]).fetchall()[0][0]
        else:
            MorselId1 = db(con, "INSERT INTO Morsel(BookId, NumInBook, Knum) VALUES(?, ?, ?)", (BookId1, NumInBook, Knum))
            MorselId2 = db(con, "INSERT INTO Morsel(BookId, NumInBook, Knum) VALUES(?, ?, ?)", (BookId2, NumInBook, Knum))
        # Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
        db(con, "INSERT INTO Region(BookId, MorselId,   RegionType, Name, ImageUrl, PageUrl, Text) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                   (BookId1, MorselId1,   'All', '', imagesPrefix + gopinath1914_img, imagesPrefix + gopinath1914_img, ''))
        db(con, "INSERT INTO Region(BookId, MorselId,   RegionType, Name, ImageUrl, PageUrl, Text) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                   (BookId2, MorselId2,   'All', '', imagesPrefix + gopinath1896_img, imagesPrefix + gopinath1896_img, ''))
        

BookId1 = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Tawney'])
BookId2 = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Telang'])
morsel_for_regionname = {}
with open('data/alignment/Telang-Tawney.csv') as f:
    NumInBook = 0
    for row in csv.reader(f):
        NumInBook += 1
        (telang, snippet, kosambi, tawney) = row
        try:
            kosambi = f'K{int(kosambi):03}'
            Knum = kosambi
        except:
            Knum = None
        if tawney:
            MorselId = db(con, "INSERT INTO Morsel(BookId, NumInBook, Knum) VALUES(?, ?, ?)", (BookId1, NumInBook, Knum))
            for (Text, Indentation) in Lines(tawney):
                db(con, "INSERT INTO Line(BookId, MorselId,   Text, Indentation) VALUES(?, ?, ?, ?)", (BookId1, MorselId,   Text, Indentation))
        if telang:
            MorselId = db(con, "INSERT INTO Morsel(BookId, NumInBook, Knum) VALUES(?, ?, ?)", (BookId2, NumInBook, Knum))
            # TODO: Some Morsels get no Regions, because of collisions in Region names: the *next* MorselId (for next region) overwrites this.
            if MorselId in [960, 992, 1022, 1095, 1114, 1137, 1156, 1171, 1191, 1497]: print(f'Morsel {MorselId} without lines or regions: row is', row)
            morsel_for_regionname[telang] = MorselId

BookId = BookId2
with open('data/regions/telang-regions-out.json') as file:
    t = json.load(file)
    totWidth = t['totWidth']
    totHeight = t['totHeight']
    imageUrlPrefix = t['imageUrlPrefix'] + '_202305'
    pageUrlPrefix = t['pageUrlPrefix'] + '_202305'
    for (region_name, types_and_regions) in t['regions']:
        for (type, regions) in types_and_regions.items():
            for region in regions:
                n = region['slug'] - 1
                x = int(region['xmin'] / totWidth * 100) / 100
                y = int(region['ymin'] / totHeight * 1000) / 1000
                w = (int(region['width'] / totWidth * 100) + 2) / 100
                h = (int(region['height'] / totHeight * 1000) + 5) / 1000
                ImageUrl = f'{imageUrlPrefix}/page/n{n}_x{x}_y{y}_w{w}_h{h}.jpg'
                PageUrl = f'{pageUrlPrefix}/page/n{n}/mode/2up'
                try:
                    MorselId = morsel_for_regionname[region_name]
                except KeyError:
                    print('Region without morsel:', region)
                    if region_name != 'V156~H': raise
                # Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
                assert isinstance(region['text'], list)
                assert all(isinstance(line, str) for line in region['text'])
                text = '\n'.join(region['text'])
                db(con, "INSERT INTO Region(BookId, MorselId,   RegionType, Name, ImageUrl, PageUrl, Text) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                           (BookId, MorselId,   type, region_name, ImageUrl, PageUrl, text))
morsel_for_regionname = {}

BookId = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Kosambi'])
with open('data/regions/kosambi-regions-out.json') as file:
    t = json.load(file)
    totWidth = t['totWidth']
    totHeight = t['totHeight']
    imageUrlPrefix = t['imageUrlPrefix']
    pageUrlPrefix = t['pageUrlPrefix']
    NumInBook = 0
    for (region_name, types_and_regions) in t['regions']:
        NumInBook += 1
        Knum = 'K' + region_name
        # Morsel: (BookId, MorselId,   NumInBook, Knum?)
        MorselId = db(con, "INSERT INTO Morsel(BookId, NumInBook, Knum) VALUES(?, ?, ?)", (BookId, NumInBook, Knum))
        for (type, regions) in types_and_regions.items():
            for region in regions:
                n = region['page_id'] - 1
                x = int(region['xmin'] / totWidth * 100) / 100
                y = int(region['ymin'] / totHeight * 1000) / 1000
                w = (int(region['width'] / totWidth * 100) + 2) / 100
                h = (int(region['height'] / totHeight * 1000) + 5) / 1000
                ImageUrl = f'{imageUrlPrefix}/page/n{n}_x{x}_y{y}_w{w}_h{h}_s4.jpg'
                PageUrl = f'{pageUrlPrefix}/page/n{n}/mode/2up'
                # Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
                assert isinstance(region['text'], list)
                assert all(isinstance(line, str) for line in region['text'])
                text = '\n'.join(region['text'])
                db(con, "INSERT INTO Region(BookId, MorselId,   RegionType, Name, ImageUrl, PageUrl, Text) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                          ((BookId, MorselId,   type, region_name, ImageUrl, PageUrl, text)))

con.execute('CREATE INDEX i1 ON Line(MorselId)')
con.execute('CREATE INDEX i2 ON Region(MorselId)')
con.execute('CREATE INDEX i3 ON Morsel(BookId)')
con.execute('CREATE INDEX i4 ON Morsel(Knum)')
con.close()
