from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
import collections
import sqlite3

# Book:   (BookId,   Title)
# Morsel: (BookId, MorselId,   Knum?)
# Line:   (BookId, MorselId, LineId,   Text, Indentation)
# Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)

# Create a custom Jinja2 environment
env = Environment(
    loader=FileSystemLoader('./'),
    autoescape=select_autoescape(['html', 'xml']),
    undefined=StrictUndefined
)
env.filters['debug'] = lambda text: print(text)
def nonempty(input):
    """Asserts that the input is nonempty."""
    assert input, input
    return input
env.filters['nonempty'] = nonempty

# We want to create the following HTML pages:
# -   an index page
# -   a page for each book
# -   a page for each Knum

con = sqlite3.connect("file:data.db?mode=ro", uri=True)

def get_book(con, Title):
    rows = con.execute('SELECT BookId FROM Book WHERE Title = ?', [Title]).fetchall()
    assert len(rows) == 1
    return rows[0][0]
kBookId = get_book(con, 'Kosambi')

# Index
# SELECT DISTINCT knum FROM Morsel; -- ORDER BY number of Morsel desc.
knums = [knum for (knum,) in con.execute('SELECT DISTINCT knum FROM Morsel ORDER BY 1') if knum is not None]
verses = []
# TODO: n+1 query; change if moving away from SQLite.
for k in knums:
    text = ' '.join(text for (text,) in con.execute(
        """
            SELECT Text FROM Region JOIN Morsel ON Region.MorselId = Morsel.MorselId 
            WHERE Region.RegionType = 'verse' AND Region.BookId = ? AND Knum = ?
        """, [kBookId, k]))
    verses.append((k, text))
# SELECT Title FROM Book;
open('web/index.html', 'w').write(env.get_template('gen/index.html').render(
    verses = verses,
    books = [Title for (Title,) in con.execute('SELECT Title FROM Book')]
))

def db1(con, sql, *args):
    rows = con.execute(sql, *args).fetchall()
    assert len(rows) == 1, rows
    assert len(rows[0]) == 1, rows[0]
    return rows[0][0]

print('Collecting lines and regions for each MorselId')
morsels_for_id = {}
for (BookId, MorselId,  Knum) in con.execute('SELECT * FROM Morsel'):
    BookTitle = db1(con, 'SELECT Title from Book WHERE BookId = ?', [BookId])
    # The Lines or Regions for this morsel_id
    lines = []
    for (BookId, MorselId, LineId,   Text, Indentation) in con.execute('SELECT * FROM Line WHERE MorselId = ?', [MorselId]):
        lines.append({'text': Text, 'indentation': Indentation})
    regions = collections.defaultdict(list)
    # SELECT * FROM Region WHERE MorselId = ? GROUP BY RegionType
    for (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text) in con.execute('SELECT * FROM Region WHERE MorselId = ?', [MorselId]):
        regions[RegionType].append((Name, ImageUrl, PageUrl, Text.splitlines()))
    morsels_for_id[MorselId] = {
        'MorselId': MorselId,
        'BookTitle': BookTitle,
        'Knum': Knum,
        'lines': lines,
        'regions': regions
    }
print('End')

# A page for each book.
for (BookId, Title) in con.execute('SELECT * FROM Book'):
    print(f'Making page for {Title}')
    # SELECT * FROM Morsel WHERE BookId=?
    morsel_ids = con.execute('SELECT MorselId FROM Morsel WHERE BookId = ?', [BookId])
    morsels_for_book = [morsels_for_id[morsel_id] for (morsel_id,) in morsel_ids]
    open(f'web/{Title}.html', 'w').write(env.get_template('gen/book.html').render(
        bookTitle = Title,
        morsels = morsels_for_book
    ))

print('Making page for Knums')
# A page for each Knum.
for knum in knums:
    # SELECT MorselId FROM Morsel WHERE Knum=?
    morsel_ids = con.execute('SELECT MorselId FROM Morsel WHERE Knum = ? ORDER BY BookId', [knum])
    morsels_for_knum = [morsels_for_id[morsel_id] for (morsel_id,) in morsel_ids]
    open(f'web/{knum}.html', 'w').write(env.get_template('gen/knum.html').render(
        Knum = knum,
        morsels = morsels_for_knum
    ))
