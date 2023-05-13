import csv
import collections
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
    for (name, versions_by_book) in vs.items():
        for version in versions_by_book:
            lines = version.splitlines()
            while lines and lines[0].strip() == '': lines = lines[1:]
            while lines and lines[-1].strip() == '': lines = lines[:-1]
            if not lines: continue
            common = 10**9
            lines_expanded = []
            for line in lines:
                line = line.replace('\t', '    ')
                lines_expanded.append(line)
                if line.lstrip(): common = min(common, len(line) - len(line.lstrip()))
            lines_for_template = []
            for line in lines_expanded:
                assert line.strip() == '' or line[:common] == ' ' * common
                lines_for_template.append({
                    'indented': False,
                    'text': line[common:]
                })
            versions_for_template.append({
                'title': name,
                'lines': lines_for_template,
            })
    # Render the template with data
    template = env.get_template('template.html')
    output = template.render(
        knum = f'K{k}',
        versions = versions_for_template,
    )
    open(f'{k}.html', 'w').write(output)
