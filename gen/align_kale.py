"""Map Kale's (1913) verses to Kosambi numbers, by their text.

Each Kale verse (data/chaya/kale-1913.json, from scan-test's verse export) is compared with every Kosambi verse
(data/regions/kosambi-regions-out.json): the letters only (Devanagari, without marks of punctuation, digits or
spaces), as sets of three-letter sequences; the closest is taken. A verse Kosambi's text hardly matches (under 0.3: one
of the verses Kosambi numbers beyond his 352) takes the number Telang's closest verse has (data/chaya/telang.json and
data/alignment/Telang-Tawney.csv). Writes data/alignment/Kale.csv:

    Kale,Kosambi,score,via,Kale text,Matched text

with a score from 0 to 1 (the share of three-letter sequences in common) and the edition matched (Kosambi or Telang's
verse); low scores are for a person to check. Two verses may take one number: a
verse and its variant, as the site's Telang alignment has them too (Telang's N033 and N104 are both K034).

    python3 gen/align_kale.py
"""
import csv
import json
import re

LETTERS = re.compile(r'[^ऀ-ॣॱ-ॿ]')   # Devanagari, less dandas and digits


def grams(text):
    letters = LETTERS.sub('', text)
    return {letters[i:i + 3] for i in range(len(letters) - 2)}


def main():
    kale = json.load(open('data/chaya/kale-1913.json'))
    verses = kale['verses'].values() if isinstance(kale['verses'], dict) else kale['verses']
    kosambi = {}
    for name, types in json.load(open('data/regions/kosambi-regions-out.json'))['regions']:
        text = ' '.join(' '.join(region['text']) for region in types.get('verse', []))
        if text:
            kosambi[f'K{int(name):03}'] = (text, grams(text))
    telang_knum = {row[0]: f'K{int(row[2]):03}' for row in csv.reader(open('data/alignment/Telang-Tawney.csv')) if row[0] and row[2].strip().isdigit()}
    telang_data = json.load(open('data/chaya/telang.json'))
    telang = {}
    for verse in (telang_data['verses'].values() if isinstance(telang_data['verses'], dict) else telang_data['verses']):
        text = ' '.join(part['text'] for part in verse['parts'] if part['role'] == 'verse')
        if verse['key'] in telang_knum:
            telang[verse['key']] = (text, grams(text))
    closest = lambda mine, among: max((len(mine & theirs) / len(mine | theirs), name) for name, (_, theirs) in among.items())
    rows = []
    for verse in verses:
        text = ' '.join(part['text'] for part in verse['parts'] if part['role'] == 'verse')
        mine = grams(text)
        if not mine:
            rows.append([verse['key'], '', 0, '', text[:60], ''])
            continue
        score, knum = closest(mine, kosambi)
        via, matched = 'Kosambi', kosambi[knum][0]
        if score < 0.3:
            score2, key = closest(mine, telang)
            if score2 > score:
                score, knum, via, matched = score2, telang_knum[key], f'Telang {key}', telang[key][0]
        rows.append([verse['key'], knum, round(score, 3), via, text.replace('\n', ' ')[:60], matched.replace('\n', ' ')[:60]])
    with open('data/alignment/Kale.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Kale', 'Kosambi', 'score', 'via', 'Kale text', 'Matched text'])
        writer.writerows(rows)
    scores = sorted(row[2] for row in rows)
    print(f'{len(rows)} verses; scores: lowest {scores[:5]}, median {scores[len(scores) // 2]}; under 0.3: {sum(s < 0.3 for s in scores)}')


if __name__ == '__main__':
    main()
