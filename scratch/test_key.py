with open(r'venv\Lib\site-packages\streamlit\static\static\js\index.ByR4Z2EF.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
idx = js.find('st-key-')
while idx != -1:
    print(js[max(0, idx-20):min(len(js), idx+60)])
    idx = js.find('st-key-', idx+60)
