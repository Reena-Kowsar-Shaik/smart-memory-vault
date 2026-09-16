with open(r'venv\Lib\site-packages\streamlit\static\static\js\index.ByR4Z2EF.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
# Look for border in styled components or container
pos = 0
while True:
    idx = js.find('hasBorder', pos)
    if idx == -1:
        idx = js.find('border:', pos)
        if idx == -1:
            break
    snippet = js[max(0, idx-100):min(len(js), idx+200)]
    print('FOUND:', snippet)
    print('---')
    pos = idx + 200
    if pos > 1000000 or pos >= len(js):
        break
