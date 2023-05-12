import json

header = '''
<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    div.outer-s {
      margin: 0.5rem;
      border-radius: 0.5rem;
      border-width: 2px;
      border-color: #3B82F6;
      border-style: solid;
      @media (min-width: 768px) {
        margin: 2.5rem;
       }
    }
    img.inner-img {
      margin-top: 0.5rem;
      margin-bottom: 0.5rem;
      width: 91.666667%;
      border-radius: 0.375rem;
      border-width: 2px;
      @media (min-width: 768px) {
        width: 75%;
      }
    }
  </style>
</head>
<h1>Bookchop</h1>
<p><i>(This is a test. Each verse and its footnotes should be read together, as one unit. Clicking on the image will take you to the corresponding page on the archive.org book. Can search for Devanagari—will expand the "not proofread" boxes—modulo OCR errors.)</i></p>
'''
print(header)

from_file = json.load(open('telang-regions-out.json'))
totWidth = from_file['totWidth']
totHeight = from_file['totHeight']
imageUrlPrefix = from_file['imageUrlPrefix']
pageUrlPrefix = from_file['pageUrlPrefix']
for (name, types_and_regions) in from_file['regions']:
  for (region_type, regions) in types_and_regions.items():
    # Generate HTML for this (name, region_type)
    kSuffix = {'verse': '', 'endnote': 'n', 'footnote': 'f', 'header': ''}
    s = f'<p>{name + kSuffix[region_type]}</p>\n'
    t = ''
    for region in regions:
        n = region['slug'] - 1
        x = region['xmin'] / totWidth; x = int(x * 100) / 100
        y = region['ymin'] / totHeight; y = int(y * 1000) / 1000
        w = region['width'] / totWidth; w = (int(w * 100) + 2) / 100
        h = region['height'] / totHeight; h = (int(h * 1000) + 5) / 1000
        image_url = imageUrlPrefix + '/page/' + f'n{n}_x{x}_y{y}_w{w}_h{h}_s1.jpg'
        page_url = pageUrlPrefix + f'/page/n{n}/mode/2up'
        s += f'<a href="{page_url}"><img src={image_url} class="inner-img"></a>\n'
        for line in region['text']: t += f'<p>{line}</p>\n'
    print(f'''
    <div class="outer-s">{s}
    <details>
    <summary>(not proofread)</summary>
    {t}
    </details>
    </div>
    ''')
