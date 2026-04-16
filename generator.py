import sys
import re

# Load Torah text
torah_lines = open('torah.txt', encoding='utf-8').read().strip().split('\n')
# Load Rashi text
rashi_lines = open('rashi.txt', encoding='utf-8').read().strip().split('\n')
# Load Personal Commentary (Perush)
perush_dict = {}
try:
    with open('perush.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line:
                parts = line.strip().split('|')
                cv = parts[0]
                comment = parts[1]
                source = parts[2] if len(parts) > 2 else ''
                if cv not in perush_dict:
                    perush_dict[cv] = []
                perush_dict[cv].append((comment, source))
except FileNotFoundError:
    pass

rashi_dict = {}
for rl in rashi_lines:
    if '|' in rl:
        cv, text = rl.split('|', 1)
        rashi_dict[cv] = text

# Parasha boundaries mapping (Chapter:Verse)
parashat_boundaries = {
    'Genesis': {
        '1:1': 'פרשת בראשית', '6:9': 'פרשת נח', '12:1': 'פרשת לך לך', '18:1': 'פרשת ויירא',
        '23:1': 'פרשת חיי שרה', '25:19': 'פרשת תולדות', '28:10': 'פרשת ויצא', '32:4': 'פרשת וישלח',
        '37:1': 'פרשת וישב', '41:1': 'פרשת מקץ', '44:18': 'פרשת ויגש', '47:28': 'פרשת ויחי'
    },
    'Exodus': {
        '1:1': 'פרשת שמות', '6:2': 'פרשת וארא', '10:1': 'פרשת בא', '13:17': 'פרשת בשלח',
        '18:1': 'פרשת יתרו', '21:1': 'פרשת משפטים', '25:1': 'פרשת תרומה', '27:20': 'פרשת תצוה',
        '30:11': 'פרשת כי תשא', '35:1': 'פרשת ויקהל', '38:21': 'פרשת פקודי'
    }
}

def int_to_gematria(num):
    if num <= 0: return ''
    letters = {
        400: 'ת', 300: 'ש', 200: 'ר', 100: 'ק',
        90: 'צ', 80: 'פ', 70: 'ע', 60: 'ס', 50: 'נ', 40: 'מ', 30: 'ל', 20: 'כ', 10: 'י',
        9: 'ט', 8: 'ח', 7: 'ז', 6: 'ו', 5: 'ה', 4: 'ד', 3: 'ג', 2: 'ב', 1: 'א'
    }
    result = ''
    while num > 0:
        if num == 15:
            result += 'טו'; num -= 15
        elif num == 16:
            result += 'טז'; num -= 16
        else:
            for val, char in letters.items():
                if num >= val:
                    result += char
                    num -= val
                    break
    return result

def strip_niqqud(text):
    # Removes Hebrew vowels and cantillation marks
    return re.sub(r'[\u0591-\u05C7]', '', text)

def escape_latex(text):
    if not text: return ''
    # נקה אנטרים סמויים בתוך הטקסט שיכולים לשבור פסקאות ב-LaTeX
    text = text.replace('\r', '').replace('\n', ' ')
    special_chars = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    for u in ['\u202a', '\u202b', '\u202c', '\u202d', '\u202e', '\u200f', '\u200e']:
        text = text.replace(u, '')
    return ''.join(special_chars.get(c, c) for c in text)

def format_rashi(text):
    if not text: return ''
    text = strip_niqqud(text)
    text = text.replace('\r', '').replace('\n', ' ') # נקה אנטרים סמויים
    parts = text.split('.', 1)
    if len(parts) == 2:
        return f'\\textbf{{{escape_latex(parts[0].strip())}.}}{escape_latex(parts[1].strip())}'
    return escape_latex(text)

current_book = ''
current_parasha = ''
book_names = {'Genesis': 'חומש בראשית', 'Exodus': 'חומש שמות'}

with open('content.tex', 'w', encoding='utf-8') as f:
    for tl in torah_lines:
        if '|' not in tl: continue
        try:
            cv, text = tl.split('|', 1)
            book, chap_verse = cv.split(' ', 1)
            chap, verse = chap_verse.split(':')
            verse_num = int(verse)
            
            # Check for Book change
            if book != current_book:
                if current_book != '':
                    f.write('\n\n\\newpage\n')
                f.write('\\begin{center}\n')
                f.write(f'  {{\\Huge \\textbf{{{book_names.get(book, book)}}}}}\n')
                f.write('\\end{center}\n')
                f.write('\\vspace{1.5cm}\n\n')
                current_book = book
                current_parasha = ''

            # Check for Parasha change
            if book in parashat_boundaries and chap_verse in parashat_boundaries[book]:
                new_parasha = parashat_boundaries[book][chap_verse]
                if new_parasha != current_parasha:
                    f.write(f'\\addparasha{{{book_names[book]} | {new_parasha}}}\n')
                    current_parasha = new_parasha

            gem_verse = int_to_gematria(verse_num)
            f.write(f'% ---------- פרק {chap} | פסוק {verse} ----------\n')
            
            # Write Torah text
            cleaned_text = escape_latex(text.strip())
            f.write(f' \\textbf{{{gem_verse}}} {cleaned_text}')
            
            # Write Rashi - glued to Torah
            if cv in rashi_dict and rashi_dict[cv].strip():
                r_text = format_rashi(rashi_dict[cv].strip())
                f.write(f'\\Rashi{{{r_text}}}')

            # Write Personal Commentary - glued to Rashi
            if cv in perush_dict:
                for comment, source in perush_dict[cv]:
                    esc_comment = escape_latex(comment)
                    esc_source = escape_latex(source)
                    if esc_source:
                        f.write(f'\\Peirush{{{esc_comment}\\Makor{{{esc_source}}}}}')
                    else:
                        f.write(f'\\Peirush{{{esc_comment}}}')
            
            # Close verse line tightly
            f.write('%\n') 
            if verse_num % 5 == 0:
                f.write('\n')
        except Exception as e:
            continue