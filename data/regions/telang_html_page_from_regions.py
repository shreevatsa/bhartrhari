import collections
import json
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

regions_for_name = collections.defaultdict(list)
last_name = '000'
# Pages 51–84: Nīti-śataka verses and footnotes
# Pages 85–126: Vairāgya-śataka verses and footnotes
# Pages 127–160: Nīti-śataka notes
# Pages 161–195: Vairāgya-śataka notes
for region in json.load(open('telang-regions.json')):
    slug = int(region['slug'])
    name = region['name']
    region_type = None
    if name == '': 
        name = last_name[:4] + '~H'
        region_type = 'header'
    elif 51 <= slug <= 84:
        name = 'N' + name
        region_type = 'footnote' if region['type'] == 'lgFootnote' else 'verse'
    elif 85 <= slug <= 126:
        name = 'V' + name
        region_type = 'footnote' if region['type'] == 'lgFootnote' else 'verse'
    elif 127 <= slug <= 160:
        name = 'N' + name
        region_type = 'endnote'
    elif 161 <= slug <= 195:
        name = 'V' + name
        region_type = 'endnote'
    last_name = name
    # eprint(region['slug'], name, '\t', ''.join(region['text'])[:80])
    regions_for_name[name].append((region_type, region))

# GROUP BY name, type
dump = collections.defaultdict(lambda: collections.defaultdict(list))
for (name, types_and_regions) in regions_for_name.items():
  for (region_type, region) in types_and_regions:
    dump[name][region_type].append(region)
# ORDER BY name
dump2 = [(name, dump[name]) for name in sorted(dump)]
json.dump(dump2, open('telang-regions-out.json', 'w'), indent=2)

# TODO(shreevatsa): Remove this hard-coding. Get page dimensions from `content` (after saving it there).
totWidth = 3125.0
totHeight = 5209.0
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

for (name, types_and_regions) in json.load(open('telang-regions-out.json')):
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
        image_url = 'https://archive.org/download/dli.granth.78136/page/' + f'n{n}_x{x}_y{y}_w{w}_h{h}_s1.jpg'
        page_url = f'https://archive.org/details/dli.granth.78136/page/n{n}/mode/2up'
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
