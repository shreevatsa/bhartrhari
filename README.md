# Data

Concepts:

- a `Book` is any translation/edition/collection that contains Bhartṛhari's poems.
- a `Region` is a rectangle from a scanned book, that has (often) been given a name: a `(name, page_n, x, y, w, h, text)` tuple.

Sources:

- My local instance of the [other repo](https://github.com/shreevatsa/ambuda/tree/line-by-line) exports `Region`s for each book.
- [This spreadsheet in Google Sheets](https://docs.google.com/spreadsheets/d/1W83uaK27fOtKRcHC2oxrdipbSyC174XtshCTalq6vrM/edit#gid=1457999221) has, for each `Book`, its (chopped-up) contents—either the text itself, or pointers to images, or names of `Region`s—in order, mapped to (where applicable) the K-number.
