import collections
import csv
import json

regions_per_book = {}
with open('data/regions/telang-regions-out.json') as file:
    t = json.load(file)
    totWidth = t['totWidth']
    totHeight = t['totHeight']
    imageUrlPrefix = t['imageUrlPrefix'] + '_202305'
    pageUrlPrefix = t['pageUrlPrefix'] + '_202305'
    regions_by_name = {}
    for (region_name, types_and_regions) in t['regions']:
        regions_by_name[region_name] = collections.defaultdict(list)
        for (type, regions) in types_and_regions.items():
            for region in regions:
                regions_by_name[region_name][type].append({
                    'n': region['slug'] - 1,
                    'x': int(region['xmin'] / totWidth * 100) / 100,
                    'y': int(region['ymin'] / totHeight * 1000) / 1000,
                    'w': (int(region['width'] / totWidth * 100) + 2) / 100,
                    'h': (int(region['height'] / totHeight * 1000) + 5) / 1000,
                    'text': region['text'],
                })
    regions_per_book['Telang'] = {
        'regions': regions_by_name,
        'imageUrlPrefix': imageUrlPrefix,
        'pageUrlPrefix': pageUrlPrefix,
    }
with open('data/regions/kosambi-regions-out.json') as file:
    t = json.load(file)
    totWidth = t['totWidth']
    totHeight = t['totHeight']
    imageUrlPrefix = t['imageUrlPrefix']
    pageUrlPrefix = t['pageUrlPrefix']
    regions_by_name = {}
    for (region_name, types_and_regions) in t['regions']:
        region_name = 'K' + region_name
        regions_by_name[region_name] = collections.defaultdict(list)
        for (type, regions) in types_and_regions.items():
            for region in regions:
                regions_by_name[region_name][type].append({
                    'n': region['page_id'] - 1,
                    'x': int(region['xmin'] / totWidth * 100) / 100,
                    'y': int(region['ymin'] / totHeight * 1000) / 1000,
                    'w': (int(region['width'] / totWidth * 100) + 2) / 100,
                    'h': (int(region['height'] / totHeight * 1000) + 5) / 1000,
                    'text': region['text'],
                })
    print(regions_by_name.keys())
    regions_per_book['Kosambi'] = {
        'regions': regions_by_name,
        'imageUrlPrefix': imageUrlPrefix,
        'pageUrlPrefix': pageUrlPrefix,
    }

# Read the CSV files (v -> K) and do two things:
# 1. generate the HTML pages for each version,
# 2. map them back (K -> [v])
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
# Create a custom Jinja2 environment
env = Environment(
    loader=FileSystemLoader('./'),
    autoescape=select_autoescape(['html', 'xml']),
    undefined=StrictUndefined
)
template = env.get_template('gen/book.html')

versions = collections.defaultdict(lambda: collections.defaultdict(list))

with open('data/alignment/Ryder.csv') as f:
    reader = csv.reader(f)
    verses_for_template = []
    for row in reader:
        (n, ryder, kosambi) = row
        if kosambi == 'Kosambi': continue
        versions[kosambi]['Ryder'].append(ryder)
        version = ryder
        # Ignore leading and trailing blank lines
        lines = version.splitlines()
        while lines and lines[0].strip() == '': lines = lines[1:]
        while lines and lines[-1].strip() == '': lines = lines[:-1]
        if not lines: continue
        # Expand tabs, and strip any common leading spaces
        lines_for_template = []
        common = 10**9
        lines_expanded = []
        for line in lines:
            line = line.replace('\t', '    ')
            lines_expanded.append(line)
            if line.lstrip(): common = min(common, len(line) - len(line.lstrip()))
        # Now we have all the lines we need, for passing into the template.
        for line in lines_expanded:
            assert line.strip() == '' or line[:common] == ' ' * common
            line = line[common:]
            lines_for_template.append({
                'indented': line.startswith(' '),
                'text': line,
            })
        verses_for_template.append({
            'title': n,
            'id': f'K{int(kosambi):03}' if kosambi != '' else None,
            'lines': lines_for_template,
        })
    open('web/Ryder.html', 'w').write(template.render(
        bookTitle='Ryder',
        verses=verses_for_template
    ))

with open('data/alignment/Brough.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        (n, brough, kosambi) = row
        versions[kosambi]['Brough'].append(brough)

with open('data/alignment/Telang-Tawney.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        (telang, snippet, kosambi, tawney, tawneyvtf) = row
        versions[kosambi]['Telang'].append(telang)
        versions[kosambi]['Tawney'].append(tawney)

with open('data/alignment/Madhavananda.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        (_, madhavananda, kosambi) = row
        versions[kosambi]['Mādhavānanda'].append(madhavananda)

with open('data/alignment/Gopinath.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        (comment, gopinath_num, gopinath1896_img, gopinath1914_img, kosambi) = row
        versions[kosambi]['Gopinath1896'].append(gopinath1896_img)
        versions[kosambi]['Gopinath1914'].append(gopinath1914_img)
# The header row and certain other rows have unusual values for the "Kosambi" column.
del versions['Kosambi']
del versions['']

json.dump(
    {
        'versions': versions,
        'regions_per_book': regions_per_book,
    },
    open('data.json', 'w')
)
