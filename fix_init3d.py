import re

with open('/home/kaua/Documents/Catalogo_GTA/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We need to find the line:
# const material = (status === 'pend') ? holoMaterial : createMaterial(info.texture);
# And replace it with a smarter texture loader.

search = "const material = (status === 'pend') ? holoMaterial : createMaterial(info.texture);"
replacement = """
                    let initialTex = info.texture;
                    if (status !== 'pend') {
                        // Tenta achar a textura oficial na logicConfig para previnir bugs de textura do Blender
                        const itemGrp = Object.values(logicConfig).find(g => g.items.some(i => i.id === info.name));
                        if (itemGrp) {
                            const itm = itemGrp.items.find(i => i.id === info.name);
                            if (itm.textures && itm.textures.length > 0) {
                                initialTex = itm.textures[0].file;
                            }
                        }
                    }
                    const material = (status === 'pend') ? holoMaterial : createMaterial(initialTex);
"""

if search in html:
    html = html.replace(search, replacement.strip())
    with open('/home/kaua/Documents/Catalogo_GTA/template.html', 'w', encoding='utf-8') as f:
        f.write(html)
        print("Patched init3D!")
else:
    print("Could not find search string.")
