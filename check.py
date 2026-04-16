with open('torah.txt', 'r', encoding='utf-8') as f:
    text = f.read()
print('torah.txt')
print('Open { :', text.count('{'))
print('Close }:', text.count('}'))

with open('rashi.txt', 'r', encoding='utf-8') as f:
    text2 = f.read()
print('rashi.txt')
print('Open { :', text2.count('{'))
print('Close }:', text2.count('}'))

with open('content.tex', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.count('{') != line.count('}'):
        print(f'Line {i+1}: Open={line.count("{")}, Close={line.count("}")}')
