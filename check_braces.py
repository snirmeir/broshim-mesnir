with open('content.tex', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        # נספור סוגריים פותחים וסוגרים (נתעלם מאלה שמוקדמים ב-\)
        opens = line.count('{') - line.count('\\{')
        closes = line.count('}') - line.count('\\}')
        if opens != closes:
            print(f"Brace mismatch on line {i}: {opens} opens, {closes} closes")
            print(f"Content: {line[:100]}...")
