from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
import json
import collections

# Book:   (BookId,   Title)
# Morsel: (BookId, MorselId,   NumInBook, Knum?)
# Line:   (BookId, MorselId, LineId,   Text, Indentation)
# Region: (BookId, MorselId, RegionId,   RegionType, Name, ImageUrl, PageUrl, Text)
[Book, Morsel, Line, Region] = json.load(open('data.json'))

def nonempty(input):
    """Asserts that the input is nonempty."""
    assert input, input
    return input

def debug(text):
  print(text)
  return ''

# Create a custom Jinja2 environment
env = Environment(
    loader=FileSystemLoader('./'),
    autoescape=select_autoescape(['html', 'xml']),
    undefined=StrictUndefined
)
env.filters['nonempty'] = nonempty
env.filters['debug'] = debug

# We want to create the following HTML pages:
# -   an index page
# -   a page for each book
# -   a page for each Knum

# Index
# SELECT DISTINCT knum FROM Morsel; -- ORDER BY number of Morsel desc.
knums = [knum
         for (knum, count) in collections.Counter(Knum for (BookId, NumInBook, Knum) in Morsel).most_common()
         if knum]
# SELECT Title FROM Book;
open('web/index.html', 'w').write(env.get_template('gen/index.html').render(
    knums = knums,
    books = Book
))

print('Start')
morsels_for_id = {}
for morsel_id, (BookId,   NumInBook, Knum) in enumerate(Morsel):
    BookTitle = Book[BookId]
    # The Lines or Regions for this morsel_id
    lines = []
    regions = collections.defaultdict(list)
    # TODO: These are "full table scans" :-)
    # SELECT * FROM Line WHERE MorselId = ?
    for LineId, (BookId, MorselId,   Text, Indentation) in enumerate(Line):
        if MorselId != morsel_id: continue
        lines.append({'text': Text, 'indentation': Indentation})
    # SELECT * FROM Region WHERE MorselId = ? GROUP BY RegionType
    for RegionId, (BookId, MorselId,   RegionType, Name, ImageUrl, PageUrl, Text) in enumerate(Region):
        if MorselId != morsel_id: continue
        regions[RegionType].append((Name, ImageUrl, PageUrl, Text))
    morsels_for_id[morsel_id] = {
        'MorselId': morsel_id,
        'BookTitle': BookTitle,
        'Knum': Knum if BookTitle != 'Kosambi' else None,
        'lines': lines,
        'regions': regions
    }
print('End')

# A page for each book.
for i, title in enumerate(Book):
    # SELECT * FROM Morsel WHERE BookId=? ORDER BY NumInBook
    morsel_ids = [MorselId for (MorselId, (BookId,   NumInBook, Knum)) in enumerate(Morsel) if BookId==i]
    morsels_for_book = [morsels_for_id[morsel_id] for morsel_id in morsel_ids]
    open(f'web/{title}.html', 'w').write(env.get_template('gen/book.html').render(
        bookTitle = title,
        morsels = morsels_for_book
    ))

# A page for each Knum.
for knum in knums:
    # SELECT MorselId FROM Morsel WHERE Knum=?
    # TODO: ORDER BY BookId
    morsel_ids = [MorselId for (MorselId, (BookId,   NumInBook, Knum)) in enumerate(Morsel) if Knum==knum]
    morsels_for_knum = [morsels_for_id[morsel_id] for morsel_id in morsel_ids]
    open(f'web/{knum}.html', 'w').write(env.get_template('gen/template.html').render(
        Knum = knum,
        morsels = morsels_for_knum
    ))
