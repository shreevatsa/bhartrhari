# Data

Concepts: `Book`, `Morsel`, `Region`, K-number.

-   a **`Book`** is any translation/edition/collection that contains Bhartṛhari's poems.
-   a `Book` is chopped-up into (is a sequence of) **`Morsel`s**
    -   a `Morsel` is usually a certain book's version of a Bhartṛhari poem, but sometimes it could be a heading.
    -   a `Morsel` is stored as either the text itself (a sequence of `Lines`), or a sequence of `Region`s, and is rendered accordingly.
-   a **`Region`** is a rectangle from a scanned book, that has been (either manually or in [post-processing](https://github.com/shreevatsa/bhartrhari/blob/622e2d1482b6d6a6893bc0f48297d6b3bad2d219/data/regions/telang/telang-regions-dump.py)) given a name so that it can be referred to. It is a `(name, imageUrl, pageUrl, text)` tuple.
    -   It often starts life as an `UnscaledRegion` which is a `(n, x, y, w, h)` tuple, where `n` is a page number (like the archive.org "n"), and `(x, y, w, h)` are integers (pixels). These are scaled (for archive.org), so that `(x, y, w, h)` become fractions between 0 and 1.
-   a **"K-number"** is the Kanonical (Kosambi) number of a Bhartṛhari poem.

External data sources:

-   My local instance of the [other repo](https://github.com/shreevatsa/ambuda/tree/line-by-line) exports `Region`s for each book. That is, it simply identifies rectangles from page scans, and gives names to them.
    -   This is in the files `data/regions/{kosambi,telang}-regions-out.json`.
-   [This spreadsheet in Google Sheets](https://docs.google.com/spreadsheets/d/1W83uaK27fOtKRcHC2oxrdipbSyC174XtshCTalq6vrM/edit#gid=1457999221) has, for each `Book`, its (chopped-up) `Morsel`s in order, with each mapped to (where applicable) the K-number.
    -   These are exported as CSV files in the [`data/alignment`](https://github.com/shreevatsa/bhartrhari/tree/622e2d1482b6d6a6893bc0f48297d6b3bad2d219/data/alignment) directory.

Internal data tables (in SQLite?)

-   The table `Book`, where each row is `(BookId, Title)`.
-   The table `Morsel`, where each row is `(MorselId, BookId, NumInBook, Knum?, Lines|Regions)` (need to think about this further)
-   The table `Region` where each row is `(RegionId, BookId, name, imageUrl, pageUrl, text)`.

Processing:

-   Read the (unscaled) regions from the external data, and convert them to `Region`s.
-   Read the CSV files, and assemble the `Morsel`s for each `Book` (add to the `Morsel` table, and one entry to the `Book` table).

Output:

-   Generate the HTML page for each invididual `Book` (using the `Morsel`s for that book: `SELECT * FROM Morsel WHERE BookId=? ORDER BY NumInBook`).
-   Generate the HTML page for each individual `Knum` (using that `Morsel`s with that `Knum`: `SELECT * FROM Morsel WHERE Knum=? ORDER BY BookId, NumInBook`).
