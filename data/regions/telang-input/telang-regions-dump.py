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
dump3 = {
   'totWidth': 3125.0,
   'totHeight': 5209.0,
   'imageUrlPrefix': 'https://archive.org/download/dli.granth.78136',
   'pageUrlPrefix': 'https://archive.org/details/dli.granth.78136',
   'regions': dump2,
}
json.dump(dump3, open('telang-regions-out.json', 'w'), indent=2)
