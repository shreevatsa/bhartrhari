# Data

Concepts: `Book`, `Morsel`, `Region`, K-number.

-   a `Book` is any translation/edition/collection that contains Bhartṛhari's poems (and possibly a few headings etc).
    -   a `Book` is chopped-up into (is a sequence of) `Morsel`s: either the text itself, or pointers to images, or names of `Region`s.
-   a `Region` is a rectangle from a scanned book, that has been (either manually or in [post-processing](https://github.com/shreevatsa/bhartrhari/blob/622e2d1482b6d6a6893bc0f48297d6b3bad2d219/data/regions/telang/telang-regions-dump.py)) given a name: it is a `(name, n, x, y, w, h, text)` tuple, where `n` is a page number (like the archive.org "n").
    -   It can either be *unscaled*, meaning that `(x, y, w, h)` are integers (pixels), or *scaled* (for archive.org), meaning that `(x, y, w, h)` are fractions between 0 and 1.
-   a "K-number" is the Kanonical (Kosambi) number of a Bhartṛhari poem.

Sources:

-   My local instance of the [other repo](https://github.com/shreevatsa/ambuda/tree/line-by-line) exports `Region`s for each book. That is, it simply identifies rectangles from page scans, and gives names to them.
    -   This is in the files `data/regions/{kosambi,telang}-regions-out.json`.
-   [This spreadsheet in Google Sheets](https://docs.google.com/spreadsheets/d/1W83uaK27fOtKRcHC2oxrdipbSyC174XtshCTalq6vrM/edit#gid=1457999221) has, for each `Book`, its (chopped-up) `Morsel`s in order, with each mapped to (where applicable) the K-number.
    -   These are exported as CSV files in the [`data/alignment`](https://github.com/shreevatsa/bhartrhari/tree/622e2d1482b6d6a6893bc0f48297d6b3bad2d219/data/alignment) directory.

Processing:

-   The `gen/data.py` script:
    -   reads the `Region`s and converts them from *unscaled* to *scaled*,
    -   reads the CSV files and
        -   assembles the `Morsel`s for each `Book`,
        -   creates the reverse map from K-number to the `Morsel`s,
        -   generates the respective HTML page for individual `Book`s.
-   The `gen/gen.py` script:
    -   reads this reverse map (K-number to `Morsel`) and generates the respective HTML page for individual poems (K-numbers).
