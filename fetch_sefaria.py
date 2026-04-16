import urllib.request
import json
import re
import os
import concurrent.futures

if 'SSLKEYLOGFILE' in os.environ:
    del os.environ['SSLKEYLOGFILE']

def fetch_sefaria(ref):
    url = f"https://www.sefaria.org/api/texts/{urllib.parse.quote(ref)}?context=0"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        return data.get('he', [])
    except Exception as e:
        print(f"Error fetching {ref}: {e}")
        return []

def strip_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).replace('\xa0', ' ').replace('&nbsp;', ' ').replace('&thinsp;', ' ')

def process_chapter(chap):
    torah_data = fetch_sefaria(f"Genesis.{chap}")
    lines = []
    
    def fetch_rashi(verse_idx):
        verse_num = verse_idx + 1
        rashi_data = fetch_sefaria(f"Rashi on Genesis.{chap}.{verse_num}")
        return verse_num, rashi_data
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_rashi, i): i for i in range(len(torah_data))}
        rashi_dict = {}
        for future in concurrent.futures.as_completed(futures):
            verse_num, data = future.result()
            rashi_dict[verse_num] = data
            
    for verse_idx, verse_text in enumerate(torah_data):
        verse_num = verse_idx + 1
        
        verse_text_clean = strip_html(verse_text)
        rashi_raw = rashi_dict.get(verse_num, [])
        rashi_text = ""
        
        if isinstance(rashi_raw, list):
            clean_comments = [strip_html(c) for c in rashi_raw]
            rashi_text = " ".join(clean_comments)
        elif isinstance(rashi_raw, str):
            rashi_text = strip_html(rashi_raw)
            
        line = f"{chap}:{verse_num}|{verse_text_clean}|{rashi_text}"
        lines.append(line)
        
    return lines

def main():
    import urllib.parse
    all_lines = []
    for chap in range(1, 51):
        print(f"Processing chapter {chap}...")
        all_lines.extend(process_chapter(chap))
        
    with open('torah.txt', 'w', encoding='utf-8') as f:
        for line in all_lines:
            f.write(line.split('|')[0] + '|' + line.split('|')[1] + '\n')
            
    with open('rashi.txt', 'w', encoding='utf-8') as f:
        for line in all_lines:
            parts = line.split('|')
            if len(parts) > 2 and parts[2].strip():
                f.write(parts[0] + '|' + parts[2] + '\n')

if __name__ == "__main__":
    main()
