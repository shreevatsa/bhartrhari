import collections
import csv
import json
import sqlite3
from typing import List

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

Morsel = []
Line = []
Region = []

BookId = db(con, "INSERT INTO Book(Title) VALUES(?)", ['Ryder'])
print('BookId', BookId)
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
        MorselId = len(Morsel); Morsel.append((BookId, NumInBook, Knum))
        for (Text, Indentation) in Lines(text):
            Line.append((BookId, MorselId,   Text, Indentation))

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
        MorselId = len(Morsel); Morsel.append((BookId, NumInBook, Knum))
        for (Text, Indentation) in Lines(text):
            Line.append((BookId, MorselId,   Text, Indentation))

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
        MorselId = len(Morsel); Morsel.append((BookId, NumInBook, Knum))
        for (Text, Indentation) in Lines(text):
            Line.append((BookId, MorselId,   Text, Indentation))

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
        if comment == '(continued)': # Happens in two places
            MorselId1 = len(Morsel) - 2
            MorselId2 = len(Morsel) - 1
        else:
            MorselId1 = len(Morsel); Morsel.append((BookId1, NumInBook, Knum))
            MorselId2 = len(Morsel); Morsel.append((BookId2, NumInBook, Knum))
        # Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
        Region.append((BookId1, MorselId1,   'All', '', imagesPrefix + gopinath1914_img, imagesPrefix + gopinath1914_img, ''))
        Region.append((BookId2, MorselId2,   'All', '', imagesPrefix + gopinath1896_img, imagesPrefix + gopinath1896_img, ''))

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
            MorselId1 = len(Morsel); Morsel.append((BookId1, NumInBook, Knum))
            for (Text, Indentation) in Lines(tawney):
                Line.append((BookId, MorselId1,   Text, Indentation))
        if telang:
            MorselId2 = len(Morsel); Morsel.append((BookId2, NumInBook, Knum))
            morsel_for_regionname[telang] = MorselId2

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
                    print(region)
                    if region_name != 'V156~H': raise
                # Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
                Region.append((BookId, MorselId,   type, region_name, ImageUrl, PageUrl, region['text']))
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
        MorselId = len(Morsel); Morsel.append((BookId,   NumInBook, Knum))
        for (type, regions) in types_and_regions.items():
            for region in regions:
                n = region['page_id'] - 1
                x = int(region['xmin'] / totWidth * 100) / 100
                y = int(region['ymin'] / totHeight * 1000) / 1000
                w = (int(region['width'] / totWidth * 100) + 2) / 100
                h = (int(region['height'] / totHeight * 1000) + 5) / 1000
                ImageUrl = f'{imageUrlPrefix}/page/n{n}_x{x}_y{y}_w{w}_h{h}.jpg'
                PageUrl = f'{pageUrlPrefix}/page/n{n}/mode/2up'
                # Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
                Region.append((BookId, MorselId,   type, region_name, ImageUrl, PageUrl, region['text']))

print(con.execute('SELECT * from Book'))
Book = [row[0] for row in con.execute('SELECT Title from Book').fetchall()]
print(Book)
json.dump(
    [Book, Morsel, Line, Region],
    open('data.json', 'w'),
    indent=2
    )

con.close()
