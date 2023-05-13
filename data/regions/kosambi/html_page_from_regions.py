import json

from_file = json.load(open('kosambi-regions-out.json'))
totWidth = from_file['totWidth']
totHeight = from_file['totHeight']
imageUrlPrefix = from_file['imageUrlPrefix']
pageUrlPrefix = from_file['pageUrlPrefix']

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
<h1>Bookchop: Kosambi's <i>The Epigrams Attributed To Bhartṛhari</i></h1>
<p><i>(This is a test. Each verse and its footnotes should be read together, as one unit. Clicking on the image will take you to the corresponding page on the archive.org book. Can search for Devanagari—will expand the "not proofread" boxes—modulo OCR errors.)</i></p>
<p>A critical edition of Bhartṛhari's three <i>śataka</i>s was published by D. D. Kosambi in 1948.
Although, like many critical editions, it is not a useful text to read directly
(verses printed in alphabetical order, the “original” readings not always being the best ones, etc),
it is a useful catalogue of all the verses found in different Bhartṛhari editions/manuscripts,
and of the variants in each verse. As he himself says in his preface, making an analogy with “statistical theory”:</p>
<blockquote>
not only is the "true" value a meaningless concept, but the actual variation observed is often of far greater importance than the value determined
</blockquote>
and (though he says this somewhat sarcastically)
<blockquote>
The reader is welcome to choose from the variants any other reading that pleases him better than mine,
or to select any other set of stanzas as the most authentic, in any order that he prefers.
In a word, he can prepare his own edition from the material placed before him; but, [...]
I trust that he will not deny me the same privilege which I offer him.
</blockquote>

<p>He based his analysis on studying roughly 380 manuscripts, though he says there were probably much more than 3000 manuscripts in existence at the time:</p>
<blockquote>
At a very conservative estimate, there exist today some 3000 MSS of Bhartrhari.
Most of these, being hidden away in private collections, will be destroyed unused
by the action of time, air, rain, mice, white ants and all other vermin except scholars.
</blockquote>

<p>He divides the verses into multiple groups:</p>
<ol>
<li>Aggressively pruning away verses not found in certain (groups of) manuscripts leaves only <b>200</b> verses, which he calls Group 1.</li>
<li>Including verses found in fewer manuscripts gives a further 152 as Group 2, bringing the total to <b>352</b> verses.</li>
<li>There are a further 505 stray verses (found in very few manuscripts) as Group 3, bringing the total to <b>857</b>.</li>
</ol>
<p>Group 1 is too small—any typical collection of Bhartṛhari verses will include verses not in Group 1—so taking Group 1 and 2 is probably about right.
Will see; may have to add a few from Group 3 as we go.
Of the first 200, 8–76 is Nīti, 77–147 is Śṛṅgāra, 148–200 is Vairāgya. The rest (201–352) are alphabetical.</p>
'''
print(header)

charts = '''
<details>
<summary>Charts</summary>
'''
for n in range(61, 78):
    charts += f'''<div><a href="https://archive.org/details/EpigramsAttributedToBhartrhariKosambiBookmarked/page/n{n}/mode/1up"><img
    src="https://archive.org/download/EpigramsAttributedToBhartrhariKosambiBookmarked/page/n{n}_rot90" class="inner-img"></a></div>
    '''
charts += '''
</details>
'''
print(charts)

index = '''
<details>
<summary>Alphabetical index</summary>
'''
for n in range(331, 344):
    index += f'''<div><a href="https://archive.org/details/EpigramsAttributedToBhartrhariKosambiBookmarked/page/n{n}/mode/1up"><img
    src="https://archive.org/download/EpigramsAttributedToBhartrhariKosambiBookmarked/page/n{n}" class="inner-img"></a></div>
    '''
index += '''
</details>
'''
print(index)


for (name, types_and_regions) in from_file['regions']:
  for (region_type, regions) in types_and_regions.items():
    # Generate HTML for this (name, region_type)
    kSuffix = {'verse': '', 'footnote': 'f'}
    s = f'<p>{name + kSuffix[region_type]}</p>\n'
    t = ''
    for region in regions:
        n = region['page_id'] - 1
        x = region['xmin'] / totWidth; x = int(x * 100) / 100
        y = region['ymin'] / totHeight; y = int(y * 1000) / 1000
        w = region['width'] / totWidth; w = (int(w * 100) + 2) / 100
        h = region['height'] / totHeight; h = (int(h * 1000) + 5) / 1000
        image_url = imageUrlPrefix + '/page/' + f'n{n}_x{x}_y{y}_w{w}_h{h}_s2.jpg'
        page_url = pageUrlPrefix + f'/page/n{n}/mode/2up'
        s += f'<a href="{page_url}"><img src={image_url} class="inner-img"></a>\n'
        for line in region['text']:
            t += f'<p>{line}</p>\n'
    print(f'''
    <div class="outer-s">{s}
    <details>
    <summary>(not proofread)</summary>
    {t}
    </details>
    </div>
    ''')
