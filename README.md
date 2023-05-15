# Data

Concepts:

- a `Book` is any translation/edition/collection that contains Bhartṛhari's poems (and possibly a few headings etc).
- a `Region` is a rectangle from a scanned book, that has been (either manually or in post-processing) given a name: it is a `(name, n, x, y, w, h, text)` tuple, where `n` is a page number (like the archive.org "n").

Sources:

- My local instance of the [other repo](https://github.com/shreevatsa/ambuda/tree/line-by-line) exports `Region`s for each book. That is, it simply identifies rectangles from page scans, and gives names to them. This is in the files `data/regions/{kosambi,telang}-regions-out.json`.
- [This spreadsheet in Google Sheets](https://docs.google.com/spreadsheets/d/1W83uaK27fOtKRcHC2oxrdipbSyC174XtshCTalq6vrM/edit#gid=1457999221) has, for each `Book`, its (chopped-up) contents—either the text itself, or pointers to images, or names of `Region`s—in order, mapped to (where applicable) the K-number.
