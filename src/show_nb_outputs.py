import json

with open('notebooks/03_modeling.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] != 'code':
        continue
    text = ''
    for out in cell.get('outputs', []):
        if out.get('output_type') in ('stream', 'execute_result'):
            text += ''.join(out.get('text', out.get('data', {}).get('text/plain', [])))
    if text.strip():
        print(f'--- Cell {i} ---')
        print(text.strip()[:1200])
        print()
