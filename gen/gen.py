from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
import json

data = json.load(open('data.json'))
versions = data['versions']
regions_per_book = data['regions_per_book']
telang = regions_per_book['Telang']['regions']
kosambi = regions_per_book['Kosambi']['regions']

# Create a custom Jinja2 environment
env = Environment(
    loader=FileSystemLoader('./'),
    autoescape=select_autoescape(['html', 'xml']),
    undefined=StrictUndefined
)

index = open('web/index.html', 'w')
index.write('''
<script>
var currentUrl = window.location.href;
if (!currentUrl.endsWith('/') && !currentUrl.endsWith('.html')) {
  window.location.href = currentUrl + '/';
}
</script>
''')

# Generate a page for each individual verse
for (k, vs) in versions.items():
    versions_for_template = []
    kOrder = ['Ryder', 'Brough', 'Tawney', 'Mādhavānanda', 'Telang', 'Gopinath1914', 'Gopinath1896']
    for (book_name, versions_by_book) in sorted(vs.items(), key=lambda name_and_v: kOrder.index(name_and_v[0])):
        for version in versions_by_book:
            if book_name == 'Telang':
                region_name = version.strip()
                versions_for_template.append({
                    'title': f'{book_name}',
                    'regions': telang[region_name],
                    'pageUrlPrefix': regions_per_book[book_name]['pageUrlPrefix'],
                    'imageUrlPrefix': regions_per_book[book_name]['imageUrlPrefix'],
                })
                continue
            if book_name in ['Gopinath1914', 'Gopinath1896']:
                region_name = version.strip()
                versions_for_template.append({
                    'title': book_name,
                    'image_urls': ['../data/images/' + version],
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
            'pageUrlPrefix': regions_per_book['Kosambi']['pageUrlPrefix'],
            'imageUrlPrefix': regions_per_book['Kosambi']['imageUrlPrefix'],
        })
    # Render the template with data
    template = env.get_template('gen/template.html')
    output = template.render(
        knum = k,
        versions = versions_for_template,
    )
    open(f'web/{k}.html', 'w').write(output)
    index.write(f'<li><a href="{k}.html">{k}</a></li>\n')
index.close()
