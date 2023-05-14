import collections
import csv
import json
# Read the CSV files (v -> K) and map them back (K -> [v])
versions = collections.defaultdict(lambda: collections.defaultdict(list))

with open('data/alignment/Ryder.csv') as f:
    reader = csv.reader(f)
    # n,Ryder,Kosambi
    for row in reader:
        (n, ryder, kosambi) = row
        versions[kosambi]['Ryder'].append(ryder)

with open('data/alignment/Brough.csv') as f:
    reader = csv.reader(f)
    # n,Brough,Kosambi
    for row in reader:
        (n, brough, kosambi) = row
        versions[kosambi]['Brough'].append(brough)

with open('data/alignment/Telang-Tawney.csv') as f:
    reader = csv.reader(f)
    # Telang,,Kosambi,Tawney,Tawney verse translation?
    for row in reader:
        (telang, snippet, kosambi, tawney, tawneyvtf) = row
        versions[kosambi]['Telang'].append(telang)
        versions[kosambi]['Tawney'].append(tawney)

with open('data/alignment/Madhavananda.csv') as f:
    reader = csv.reader(f)
    # ,Mādhavānanda,Kosambi
    for row in reader:
        (_, madhavananda, kosambi) = row
        versions[kosambi]['Mādhavānanda'].append(madhavananda)

with open('data/alignment/Gopinath.csv') as f:
    reader = csv.reader(f)
    # Comment,Gopinath-num,Gopinath1896-img,Gopinath1914-img,Kosambi
    for row in reader:
        (comment, gopinath_num, gopinath1896_img, gopinath1914_img, kosambi) = row
        versions[kosambi]['Gopinath1896'].append(gopinath1896_img)
        versions[kosambi]['Gopinath1914'].append(gopinath1914_img)
del versions['Kosambi']
del versions['']

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

json.dump(
    {
        'versions': versions,
        'regions_per_book': regions_per_book,
    },
    open('data.json', 'w')
)
