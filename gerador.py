import json

def gerar_html_painel(skin_data):
    html = ""
    for idx, grupo in enumerate(skin_data.get('grupos', [])):
        grupo_total = len(grupo.get('itens', []))
        grupo_concluidos = sum(1 for item in grupo.get('itens', []) if item.get('concluido', False))
        grupo_pronto = (grupo_total > 0 and grupo_total == grupo_concluidos)
        
        status_dot = '<span class="status-dot status-done" style="width: 10px; height: 10px; flex-shrink: 0;" title="Concluido"></span>' if grupo_pronto else '<span class="status-dot status-pend" style="width: 10px; height: 10px; background-color: #eab308; box-shadow: 0 0 8px #eab308; flex-shrink: 0;" title="Pendente"></span>'

        html += f'''
        <details class="group-card">
            <summary class="group-header">
                <div class="group-info">
                    {status_dot}
                    <span class="group-icon">{grupo.get('emoji', '📦')}</span>
                    <strong>{grupo['titulo']}</strong>
                </div>
                <span class="tag-texture">{grupo.get('resumo_texturas', '')} ▼</span>
            </summary>
            <div class="group-content">
        '''
        
        for item in grupo.get('itens', []):
            status_text = "Pronto" if item.get('concluido', False) else "Pendente"
            status_color = "#10b981" if item.get('concluido', False) else "#eab308"
            tex_str = ", ".join(item['texturas'])
            
            html += f'''
                <div class="interactive-item" style="cursor: default; padding: 12px; border-color: rgba(255,255,255,0.05); margin-bottom: 6px;">
                    <div style="display:flex; flex-direction:column; gap:4px; width: 100%;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size: 0.9rem; font-weight: 600; color: #fff;">ID {item.get('id', '-')} - {item['nome']}</span>
                            <span class="status-badge" style="background: transparent; color: {status_color}; border: 1px solid {status_color}; padding: 2px 6px; font-size: 0.65rem;">
                                {status_text}
                            </span>
                        </div>
                        <span style="font-size: 0.75rem; color: #8a8b9d;">Texturas: {tex_str}</span>
                        <span style="font-size: 0.75rem; color: #666;">Obs: {item.get('obs', '-')}</span>
                    </div>
                </div>
            '''
        html += '''
            </div>
        </details>
        '''
    return html

def get_pricing_html(skin_data):
    if not skin_data or 'orcamento' not in skin_data:
        return ""
    
    orcamento = skin_data['orcamento']
    valor_str = orcamento.get('valor_final', 'R$ 0,00').replace('R$ ', '')
    try:
        reais, centavos = valor_str.split(',')
    except:
        reais, centavos = valor_str, "00"
        
    is_pago = orcamento.get('pago', False)
    link = orcamento.get('link_download', '#') if is_pago else orcamento.get('link_pagamento', '#')
    
    html = """<div class="pricing-toggle-btn" onclick="this.parentElement.classList.toggle('minimized')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.6)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
    </div>"""
    
    if is_pago:
        html += f'''
        <div class="badge-status status-paid">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <span>PAGAMENTO CONCLUÍDO</span>
        </div>
        <a href="{link}" target="_blank" class="btn-download" id="download-btn">
            <span class="btn-content">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px; margin-bottom: 2px;">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                BAIXAR SKIN (DRIVE)
            </span>
            <span class="btn-content shine-layer" aria-hidden="true">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px; margin-bottom: 2px;">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                BAIXAR SKIN (DRIVE)
            </span>
        </a>
        '''
    else:
        html += f'''<div class="price-container">
        <div class="price-display">
            <span class="price-currency">R$</span>
            <span class="price-amount">{reais}<span class="price-cents">,{centavos}</span></span>
        </div>
    </div>
        <div class="badge-status status-pending">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>PAGAMENTO PENDENTE</span>
        </div>
        <a href="{link}" target="_blank" class="btn-action" id="pay-btn">
            <span class="btn-content">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px; margin-bottom: 2px;">
                    <rect x="2" y="5" width="20" height="14" rx="2" ry="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line>
                </svg> EFETUAR PAGAMENTO
            </span>
            <span class="btn-content shine-layer" aria-hidden="true">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px; margin-bottom: 2px;">
                    <rect x="2" y="5" width="20" height="14" rx="2" ry="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line>
                </svg> EFETUAR PAGAMENTO
            </span>
        </a>
        '''
    return html

def gerar_html(dados):
    skin_masc = next((s for s in dados['skins'] if s['id'] == 'masculina'), None)
    skin_fem = next((s for s in dados['skins'] if s['id'] == 'feminina'), None)
    
    html_masc = gerar_html_painel(skin_masc).replace("`", "\\`") if skin_masc else ""
    # html_fem = gerar_html_painel(skin_fem).replace("`", "\\`") if skin_fem else ""
    
    pricing_masc = get_pricing_html(skin_masc).replace("`", "\\`") if skin_masc else ""
    pricing_fem = get_pricing_html(skin_fem).replace("`", "\\`") if skin_fem else ""
    

    def calc_prog(skin):
        if not skin: return "0"
        total = sum(len(g.get('itens', [])) for g in skin.get('grupos', []))
        done = sum(1 for g in skin.get('grupos', []) for i in g.get('itens', []) if i.get('concluido', False))
        return str(round((done / total * 100))) if total > 0 else "0"

    prog_masc = calc_prog(skin_masc)
    prog_fem = calc_prog(skin_fem)


    # --- BLINDAGEM DE DEPENDENCIAS (AUTO-SYNC COM BLENDER) ---
    try:
        with open('assets/models/manifest.json', 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            
        mesh_names = [v['name'] for v in manifest.values()]
        
        for skin in dados['skins']:
            # Mapeamento rapido de qual item pertence a qual grupo
            item_to_group = {}
            for group in skin['grupos']:
                for item in group['itens']:
                    item_to_group[item['id']] = group
            
            for m in mesh_names:
                if '_' in m:
                    base, trigger = m.split('_', 1)
                    
                    # Se o trigger e o base existem no dados.json
                    if trigger in item_to_group and base in item_to_group:
                        # 1. Adiciona a cond_malha no trigger (ex: calca)
                        trigger_item = next(i for i in item_to_group[trigger]['itens'] if i['id'] == trigger)
                        if 'cond_malhas' not in trigger_item:
                            trigger_item['cond_malhas'] = {}
                        trigger_item['cond_malhas'][base] = m
                        
                        # 2. Registra o item secundario (ex: pernas_calca) no mesmo grupo do base (ex: Corpo Base)
                        if m not in item_to_group:
                            base_group = item_to_group[base]
                            base_item = next(i for i in base_group['itens'] if i['id'] == base)
                            
                            novo_item = {
                                "id": m,
                                "nome": f"{base_item['nome'].split('(')[0].strip()} (DA {trigger_item['nome'].split(' ')[0].strip()})",
                                "texturas": base_item.get('texturas', {}).copy(),
                                "obs": f"Autolink: {trigger_item['nome']}",
                                "concluido": True,
                                "status": "done",
                                "visivel_padrao": False
                            }
                            # Evita duplicar se o usuario ja tinha posto manualmente
                            if not any(i['id'] == m for i in base_group['itens']):
                                base_group['itens'].append(novo_item)
                                item_to_group[m] = base_group
    except Exception as e:
        print("Aviso: Falha na blindagem inteligente", e)
    # ---------------------------------------------------------

    # 1. Build logicConfig object for Female
    logic_obj = {}
    active_items = []
    
    if skin_fem:
        for group in skin_fem['grupos']:
            group_name = group['titulo']
            logic_obj[group_name] = {
                "emoji": group.get('emoji', '📦'),
                "exclusive": group.get('exclusive', False),
                "items": []
            }
            for item in group['itens']:
                item_id = item.get('id', 'unk')
                if item_id == '-' or not item_id:
                    import hashlib
                    item_id = "pend_" + hashlib.md5(item.get('nome', '').encode()).hexdigest()[:6]
                    item['id'] = item_id # Atualiza no item original para o resto do loop

                logic_item = {
                    "id": item_id,
                    "name": item.get('nome', 'Item'),
                    "status": "done" if item.get('concluido', False) else "pend",
                    "texturas_names": list(item.get('texturas', {}).keys()) if isinstance(item.get('texturas'), dict) else item.get('texturas', []),
                    "malhas": item.get('malhas', []),
                    "hides": item.get('hides', []),
                    "cond_malhas": item.get('cond_malhas', {})
                }
                if item.get('visivel_padrao', False):
                    active_items.append(logic_item["id"])
                    
                if 'texturas' in item and isinstance(item['texturas'], dict) and len(item['texturas']) > 0:
                    logic_item['textures'] = [{"file": k + ".png", "color": v} for k, v in item['texturas'].items()]
                    
                logic_obj[group_name]["items"].append(logic_item)
                
    logic_config_json = json.dumps(logic_obj, indent=4, ensure_ascii=False)
    active_items_str = ", ".join([f'"{x}"' for x in active_items])
    
    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()
        
    template = template.replace('__HTML_MASC__', html_masc)
    template = template.replace('__PRICING_MASC__', pricing_masc)
    template = template.replace('__PRICING_FEM__', pricing_fem)
    template = template.replace('__PRICING_FEM_JS__', pricing_fem)
    template = template.replace('__LOGIC_CONFIG__', logic_config_json)
    template = template.replace('__ACTIVE_ITEMS__', active_items_str)
    template = template.replace('__PROG_MASC__', prog_masc)
    template = template.replace('__PROG_FEM__', prog_fem)

    return template

def gerar_md(dados):
    md = f"# {dados['projeto']}\n\n"
    for skin in dados.get('skins', []):
        md += f"## {skin['titulo']}\n\n"
        md += "| ID | Status | Grupo | Acessório | Texturas | Obs |\n"
        md += "|:---|:---|:---|:---|:---|:---|\n"
        
        todos_itens = []
        for grupo in skin.get('grupos', []):
            for item in grupo.get('itens', []):
                if not item.get('concluido', False):
                    continue
                item_copy = item.copy()
                item_copy['grupo'] = grupo.get('titulo', '')
                item_copy['emoji'] = grupo.get('emoji', '')
                todos_itens.append(item_copy)
                
        def sort_key(x):
            try:
                return int(x.get('dff_id', x.get('id', 9999)))
            except ValueError:
                return 9999
                
        itens_ordenados = sorted(todos_itens, key=sort_key)
        for item in itens_ordenados:
            status = "✅" if item.get('concluido', False) else "⏳"
            texturas = ", ".join([f"`{t}`" for t in item['texturas']])
            display_id = item.get('dff_id', item.get('id', '-'))
            md += f"| **{display_id}** | {status} | {item.get('emoji', '')} {item.get('grupo', '')} | **{item['nome']}** | {texturas} | {item.get('obs', '')} |\n"
        md += "\n"
    return md

if __name__ == "__main__":
    with open("dados.json", "r", encoding="utf-8") as f:
        dados = json.load(f)
        
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(gerar_html(dados))
        
    with open("ids.md", "w", encoding="utf-8") as f:
        f.write(gerar_md(dados))
