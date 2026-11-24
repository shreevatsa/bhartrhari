"""Record the size of each page of a book's PDF, in PDF points (its CropBox), for the links to a block's place on its
page (gen/chaya.py: `#page=N&zoom=…`), which the site's build makes without the PDFs:

    data/chaya/<book>-pages.json   {"1": [width, height], …}

    python3 gen/pdf_pages.py telang ~/w/scan-test/outputs/books/telang-dli.chaya.pdf
"""
import json
import re
import subprocess
import sys


def main(book, pdf):
    pages = int(re.search(r'^Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True, check=True).stdout, re.M)[1])
    info = subprocess.run(['pdfinfo', '-f', '1', '-l', str(pages), '-box', pdf], capture_output=True, text=True, check=True).stdout
    sizes = {}
    for page, x0, y0, x1, y1 in re.findall(r'^Page\s+(\d+) CropBox:\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', info, re.M):
        assert float(x0) == 0 and float(y0) == 0, (page, x0, y0)   # the links take the box's corner as the origin
        sizes[page] = [round(float(x1), 2), round(float(y1), 2)]
    rotated = re.findall(r'^Page\s+(\d+) rot:\s+([1-9]\d*)', subprocess.run(['pdfinfo', '-f', '1', '-l', str(pages), pdf], capture_output=True, text=True).stdout, re.M)
    assert not rotated, rotated
    json.dump(sizes, open(f'data/chaya/{book}-pages.json', 'w'), separators=(',', ':'))
    print(f'{book}: {len(sizes)} pages')


if __name__ == '__main__':
    main(*sys.argv[1:3])
