import json, os

with open('/home/kaua/Documents/Catalogo_GTA/dados.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = []
for skin in data['skins']:
    for group in skin['grupos']:
        for item in group['itens']:
            if item.get('concluido') and 'texturas_3d' in item:
                for tex in item['texturas_3d']:
                    file_path = f"/home/kaua/Documents/Catalogo_GTA/assets/img/{tex['file']}"
                    if not os.path.exists(file_path):
                        missing.append(tex['file'])

print("Missing files for concluded items:", missing)
