import collections
import csv
import json
# Read the CSV files (v -> K) and map them back (K -> [v])
versions = collections.defaultdict(lambda: collections.defaultdict(list))

with open('../data/alignment/Ryder.csv') as f:
    reader = csv.reader(f)
    # n,Ryder,Kosambi
    for row in reader:
        (n, ryder, kosambi) = row
        versions[kosambi]['Ryder'].append(ryder)

with open('../data/alignment/Telang-Tawney.csv') as f:
    reader = csv.reader(f)
    # Telang,,Kosambi,Tawney,Tawney verse translation?
    for row in reader:
        (telang, snippet, kosambi, tawney, tawneyvtf) = row
        versions[kosambi]['Telang'].append(telang)
        versions[kosambi]['Tawney'].append(tawney)

with open('../data/alignment/Madhavananda.csv') as f:
    reader = csv.reader(f)
    # ,Mādhavānanda,Kosambi
    for row in reader:
        (_, madhavananda, kosambi) = row
        versions[kosambi]['Mādhavānanda'].append(madhavananda)

with open('../data/alignment/Gopinath.csv') as f:
    reader = csv.reader(f)
    # Comment,Gopinath-num,Gopinath1896-img,Gopinath1914-img,Kosambi
    for row in reader:
        (comment, gopinath_num, gopinath1896_img, gopinath1914_img, kosambi) = row
        versions[kosambi]['Gopinath1896'].append(gopinath1896_img)
        versions[kosambi]['Gopinath1914'].append(gopinath1914_img)
del versions['Kosambi']
del versions['']

pageUrlPrefixes = {}
imageUrlPrefixes = {}
telang = {}
with open('../data/regions/telang-regions-out.json') as file:
    t = json.load(file)
    totWidth = t['totWidth']
    totHeight = t['totHeight']
    imageUrlPrefixes['Telang'] = imageUrlPrefix = t['imageUrlPrefix'] + '_202305'
    pageUrlPrefixes['Telang'] = pageUrlPrefix = t['pageUrlPrefix'] + '_202305'
    for (region_name, types_and_regions) in t['regions']:
        telang[region_name] = collections.defaultdict(list)
        for (type, regions) in types_and_regions.items():
            for region in regions:
                telang[region_name][type].append({
                    'n': region['slug'] - 1,
                    'x': int(region['xmin'] / totWidth * 100) / 100,
                    'y': int(region['ymin'] / totHeight * 1000) / 1000,
                    'w': (int(region['width'] / totWidth * 100) + 2) / 100,
                    'h': (int(region['height'] / totHeight * 1000) + 5) / 1000,
                    'text': region['text'],
                })
kosambi = {}
with open('../data/regions/kosambi-regions-out.json') as file:
    t = json.load(file)
    totWidth = t['totWidth']
    totHeight = t['totHeight']
    imageUrlPrefixes['Kosambi'] = imageUrlPrefix = t['imageUrlPrefix']
    pageUrlPrefixes['Kosambi'] = pageUrlPrefix = t['pageUrlPrefix']
    for (region_name, types_and_regions) in t['regions']:
        region_name = 'K' + region_name
        kosambi[region_name] = collections.defaultdict(list)
        for (type, regions) in types_and_regions.items():
            for region in regions:
                kosambi[region_name][type].append({
                    'n': region['page_id'] - 1,
                    'x': int(region['xmin'] / totWidth * 100) / 100,
                    'y': int(region['ymin'] / totHeight * 1000) / 1000,
                    'w': (int(region['width'] / totWidth * 100) + 2) / 100,
                    'h': (int(region['height'] / totHeight * 1000) + 5) / 1000,
                    'text': region['text'],
                })
print(kosambi.keys())

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
# Create a custom Jinja2 environment
env = Environment(
    loader=FileSystemLoader('./'),
    autoescape=select_autoescape(['html', 'xml']),
    undefined=StrictUndefined
)

for (k, vs) in versions.items():
    k = f'K{int(k):03}'
    versions_for_template = []
    kOrder = ['Ryder', 'Tawney', 'Mādhavānanda', 'Telang', 'Gopinath1914', 'Gopinath1896']
    for (book_name, versions_by_book) in sorted(vs.items(), key=lambda name_and_v: kOrder.index(name_and_v[0])):
        for version in versions_by_book:
            if book_name == 'Telang':
                region_name = version.strip()
                versions_for_template.append({
                    'title': book_name,
                    'regions': telang[region_name],
                    'pageUrlPrefix': pageUrlPrefixes[book_name],
                    'imageUrlPrefix': imageUrlPrefixes[book_name],
                })
                continue
            if book_name in ['Gopinath1914', 'Gopinath1896']:
                region_name = version.strip()
                versions_for_template.append({
                    'title': book_name,
                    'image_urls': ['https://calm-gaufre-6360e8.netlify.app/data/images/' + version],
                })
                continue

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
            versions_for_template.append({
                'title': book_name,
                'lines': lines_for_template,
            })
    if k in kosambi:
        region_name = k
        versions_for_template.append({
            'title': 'Kosambi',
            'regions': kosambi[region_name],
            'pageUrlPrefix': pageUrlPrefixes['Kosambi'],
            'imageUrlPrefix': imageUrlPrefixes['Kosambi'],
        })
    # Render the template with data
    template = env.get_template('template.html')
    output = template.render(
        knum = f'K{k}',
        versions = versions_for_template,
    )
    open(f'{k}.html', 'w').write(output)
