import json

def gerar_html(dados):
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dados['projeto']}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        :root {{
            --bg-color: #0b0c10; --card-bg: #15161b; --border-color: #262833;
            --primary: #00d26a; --primary-glow: rgba(0, 210, 106, 0.15);
            --accent: #3b82f6; --text-main: #f3f4f6; --text-muted: #9ca3af; --text-dark: #6b7280;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
        body {{ background-color: var(--bg-color); color: var(--text-main); padding: 40px 20px; display: flex; justify-content: center; min-height: 100vh; }}
        .container {{ max-width: 900px; width: 100%; display: flex; flex-direction: column; gap: 25px; }}
        
        .header {{ text-align: center; padding-bottom: 10px; }}
        .badge-exclusive {{ display: inline-block; background: linear-gradient(135deg, #1f2937, #111827); border: 1px solid #374151; color: #93c5fd; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; padding: 6px 14px; border-radius: 9999px; margin-bottom: 12px; }}
        .header h1 {{ font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 8px; }}
        .header h1 span {{ color: var(--primary); }}
        .header p {{ color: var(--text-muted); font-size: 1rem; max-width: 620px; margin: 0 auto; line-height: 1.5; }}
        
        /* New Top Level Skin Accordion */
        details.skin-accordion {{ background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); margin-bottom: 10px; transition: all 0.3s ease; }}
        summary.skin-summary {{ padding: 25px; font-size: 1.4rem; font-weight: 800; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid transparent; transition: background 0.2s; }}
        summary.skin-summary::-webkit-details-marker {{ display: none; }}
        summary.skin-summary:hover {{ background-color: #1a1c23; }}
        details.skin-accordion[open] summary.skin-summary {{ border-bottom: 1px solid var(--border-color); background-color: #1a1c23; }}
        
        .main-card {{ display: grid; grid-template-columns: 1.3fr 1fr; }}
        @media (max-width: 768px) {{ .main-card {{ grid-template-columns: 1fr; }} }}
        
        .scope-section {{ padding: 35px; display: flex; flex-direction: column; gap: 24px; }}
        .section-title {{ font-size: 1.1rem; font-weight: 700; color: #ffffff; display: flex; align-items: center; gap: 8px; text-transform: uppercase; letter-spacing: 0.5px; }}
        
        /* Expansible Cards */
        .items-list {{ display: flex; flex-direction: column; gap: 12px; }}
        details.group-card {{ background: #1c1e24; border: 1px solid #282a36; border-radius: 10px; overflow: hidden; }}
        summary.group-header {{ padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; list-style: none; transition: background 0.2s; }}
        summary.group-header::-webkit-details-marker {{ display: none; }}
        summary.group-header:hover {{ background: #23252d; }}
        .group-info {{ display: flex; align-items: center; gap: 10px; font-size: 0.95rem; }}
        .group-icon {{ font-size: 1.2rem; }}
        .tag-texture {{ background-color: #272c3d; color: #60a5fa; font-size: 0.75rem; font-weight: 600; padding: 4px 8px; border-radius: 6px; }}
        
        /* Inner Items */
        .group-content {{ padding: 16px; border-top: 1px solid #282a36; background: #15161b; display: flex; flex-direction: column; gap: 10px; }}
        .inner-item {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #1a1c23; border-radius: 6px; border: 1px dashed #2d3142; }}
        
        .status-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; }}
        .status-done {{ background-color: var(--primary); box-shadow: 0 0 8px var(--primary); }}
        .status-pend {{ background-color: #ef4444; box-shadow: 0 0 8px #ef4444; }}

        .engineering-box {{ background: #111217; border: 1px dashed #2d3142; border-radius: 12px; padding: 16px; margin-top: 10px;}}
        .engineering-box h4 {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.5px; }}
        .eng-points {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.8rem; color: #d1d5db; }}
        .eng-points div {{ display: flex; align-items: center; gap: 6px; }}
        .eng-points div::before {{ content: "✔"; color: var(--primary); font-weight: bold; }}
        
        .pricing-section {{ background: #1a1c23; border-left: 1px solid var(--border-color); padding: 35px 30px; display: flex; flex-direction: column; justify-content: space-between; }}
        @media (max-width: 768px) {{ .pricing-section {{ border-left: none; border-top: 1px solid var(--border-color); }} }}
        
        .price-header span {{ font-size: 0.85rem; color: var(--text-dark); text-decoration: line-through; font-weight: 500; }}
        .price-val {{ font-size: 2.7rem; font-weight: 800; color: var(--primary); margin: 5px 0 10px 0; display: flex; align-items: baseline; gap: 6px; }}
        .price-val small {{ font-size: 1rem; color: var(--text-muted); font-weight: 400; }}
        .pix-badge {{ display: inline-flex; align-items: center; padding: 6px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; margin-bottom: 25px; border: 1px solid transparent; }}
        
        .summary-specs {{ border-top: 1px solid #2c2f3d; border-bottom: 1px solid #2c2f3d; padding: 16px 0; margin-bottom: 25px; display: flex; flex-direction: column; gap: 10px; }}
        .spec-line {{ display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); }}
        .spec-line strong {{ color: var(--text-main); }}
        
        .btn-action {{ display: block; text-align: center; background-color: var(--primary); color: #0b0c10; text-decoration: none; padding: 16px; border-radius: 12px; font-weight: 700; font-size: 1rem; transition: all 0.2s ease; box-shadow: 0 4px 15px var(--primary-glow); margin-bottom: 10px; }}
        .btn-action:hover {{ filter: brightness(1.1); transform: translateY(-2px); box-shadow: 0 8px 20px var(--primary-glow); }}
        .disabled-btn {{ background-color: #374151 !important; color: #9ca3af !important; box-shadow: none !important; cursor: not-allowed; }}
        .disabled-btn:hover {{ filter: none; transform: none; }}
        
        .progress-container {{ margin-bottom: 25px; }}
        .progress-bar-bg {{ width: 100%; background-color: #262833; border-radius: 9999px; height: 10px; overflow: hidden; }}
        .progress-bar-fill {{ height: 100%; background-color: var(--accent); transition: width 0.5s ease; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="badge-exclusive">Orçamento Exclusivo • SAMP Mobile</div>
            <h1>{dados['projeto'].split()[0]} <span>{' '.join(dados['projeto'].split()[1:])}</span></h1>
            <p>{dados.get('descricao', '')}</p>
        </div>
"""

    for skin in dados.get('skins', []):
        orc = skin.get('orcamento', {})
        total_itens = 0
        concluidos = 0
        for grupo in skin.get('grupos', []):
            for item in grupo.get('itens', []):
                total_itens += 1
                if item.get('concluido', False):
                    concluidos += 1
                    
        porcentagem = int((concluidos / total_itens) * 100) if total_itens > 0 else 0
        pago = orc.get('pago', False)

        if pago:
            badge_pagamento = '<div class="pix-badge" style="background: rgba(0, 210, 106, 0.1); color: #00d26a; border-color: rgba(0, 210, 106, 0.2);">✅ Pagamento Confirmado</div>'
            btn_acao = f'<a href="{orc.get("link_download", "#")}" target="_blank" class="btn-action" style="background-color: #3b82f6;">📁 BAIXAR SKIN (DRIVE)</a>'
        else:
            badge_pagamento = '<div class="pix-badge" style="background: rgba(234, 179, 8, 0.1); color: #eab308; border-color: rgba(234, 179, 8, 0.2);">⏳ Aguardando Pagamento</div>'
            btn_acao = f'<a href="{orc.get("link_pagamento", "#")}" target="_blank" class="btn-action">💳 EFETUAR PAGAMENTO</a>'
            btn_acao += f'\n<a href="#" class="btn-action disabled-btn" onclick="event.preventDefault();">🔒 DOWNLOAD BLOQUEADO</a>'

        html += f"""        <details class="skin-accordion" id="skin-{skin['id']}">
            <summary class="skin-summary">
                <span>{skin['titulo']}</span>
                <span style="font-size: 1rem; color: var(--text-muted);">▼</span>
            </summary>
            <div class="main-card">
                <div class="scope-section">
                    <div class="section-title"><span>📦 Itens Inclusos no Pacote</span></div>
                    <div class="items-list">\n"""
        
        if not skin.get('grupos', []):
            html += """                        <div style="text-align:center; padding:20px; color:var(--text-muted); font-size:0.9rem;">
                            Os itens desta skin estão sendo adicionados...
                        </div>\n"""

        for grupo in skin.get('grupos', []):
            grupo_total = len(grupo.get('itens', []))
            grupo_concluidos = sum(1 for item in grupo.get('itens', []) if item.get('concluido', False))
            grupo_pronto = (grupo_total > 0 and grupo_total == grupo_concluidos)
            
            if grupo_pronto:
                grupo_status = '<span class="status-dot status-done" style="width: 10px; height: 10px; flex-shrink: 0;" title="Concluído"></span>'
            else:
                grupo_status = '<span class="status-dot status-pend" style="width: 10px; height: 10px; background-color: #eab308; box-shadow: 0 0 8px #eab308; flex-shrink: 0;" title="Pendente"></span>'

            html += f"""                        <details class="group-card">
                            <summary class="group-header">
                                <div class="group-info">
                                    {grupo_status}
                                    <span class="group-icon">{grupo.get('emoji', '📦')}</span>
                                    <strong>{grupo['titulo']}</strong>
                                </div>
                                <span class="tag-texture">{grupo.get('resumo_texturas', '')} ▼</span>
                            </summary>
                            <div class="group-content">\n"""
            
            for item in grupo.get('itens', []):
                status_class = "status-done" if item.get('concluido', False) else "status-pend"
                status_text = "Pronto" if item.get('concluido', False) else "Pendente"
                tex_str = ", ".join(item['texturas'])
                
                html += f"""                                <div class="inner-item">
                                    <div style="display:flex; flex-direction:column; gap:4px;">
                                        <span style="font-size: 0.9rem; font-weight: 600; color: #e0e0e0;">ID {item.get('id', '-')} - {item['nome']}</span>
                                        <span style="font-size: 0.75rem; color: #8a8b9d;">Texturas: {tex_str}</span>
                                    </div>
                                    <div style="font-size: 0.75rem; color: var(--text-muted);">
                                        <span class="status-dot {status_class}"></span> {status_text}
                                    </div>
                                </div>\n"""
                                
            html += """                            </div>
                        </details>\n"""
                        
        html += f"""                    </div>
                    <div class="engineering-box">
                        <h4>Engenharia & Performance</h4>
                        <div class="eng-points">
                            <div>Decimate (Otimizado Mobile)</div>
                            <div>Rigging & Skinning GTA SA</div>
                            <div>Hierarquia Modular no .DFF</div>
                            <div>Zero Vazamento de Pele</div>
                        </div>
                    </div>
                </div>

                <div class="pricing-section">
                    <div>
                        <div class="price-header">
                            <div class="price-val">
                                {orc.get('valor_final', 'R$ 0,00')}
                                <small>à vista</small>
                            </div>
                        </div>
                        {badge_pagamento}
                        
                        <div class="progress-container">
                            <div class="spec-line" style="margin-bottom: 8px;">
                                <span>Progresso do Desenvolvimento</span>
                                <strong style="color: var(--accent);">{porcentagem}%</strong>
                            </div>
                            <div class="progress-bar-bg">
                                <div class="progress-bar-fill" style="width: {porcentagem}%;"></div>
                            </div>
                        </div>

                        <div class="summary-specs">
                            <div class="spec-line"><span>Total de Peças:</span><strong>{total_itens} Malhas</strong></div>
                            <div class="spec-line"><span>Modelos Concluídos:</span><strong>{concluidos}/{total_itens}</strong></div>
                            <div class="spec-line"><span>Compatibilidade:</span><strong>SAMP Mobile / PC</strong></div>
                        </div>
                    </div>

                    <div>
                        {btn_acao}
                    </div>
                </div>
            </div>
        </details>"""

    html += """
    </div>
    
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            const skinAccordions = document.querySelectorAll('.skin-accordion');
            
            // 1. Carregar estado salvo do LocalStorage
            let activeSkin = localStorage.getItem('activeSkinId');
            let hasOpened = false;

            if (activeSkin) {
                skinAccordions.forEach(acc => {
                    if (acc.id === activeSkin) {
                        acc.open = true;
                        hasOpened = true;
                    } else {
                        acc.open = false;
                    }
                });
            } 
            
            // 2. Se não tinha estado salvo (ou ID não existe), abre a Feminina por padrão
            if (!hasOpened) {
                const feminina = document.getElementById('skin-feminina');
                if (feminina) {
                    feminina.open = true;
                } else if (skinAccordions.length > 0) {
                    skinAccordions[0].open = true;
                }
            }

            // 3. Salvar estado ao clicar e fechar os outros (comportamento de sanfona)
            skinAccordions.forEach(acc => {
                acc.addEventListener('toggle', (e) => {
                    if (acc.open) {
                        localStorage.setItem('activeSkinId', acc.id);
                        skinAccordions.forEach(other => {
                            if (other !== acc && other.open) {
                                other.open = false;
                            }
                        });
                    }
                });
            });
        });
    </script>
</body>
</html>"""

    return html

def gerar_md(dados):
    md = f"# {dados['projeto']}\n\n"
    
    for skin in dados.get('skins', []):
        md += f"## {skin['titulo']}\n\n"
        md += "| ID | Status | Grupo | Acessório | Texturas | Obs |\n"
        md += "|:---|:---|:---|:---|:---|:---|\n"
        
        # Extrair todos os itens concluidos com a informação do grupo
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
                return int(x['id'])
            except ValueError:
                return 9999
                
        itens_ordenados = sorted(todos_itens, key=sort_key)
        
        for item in itens_ordenados:
            status = "✅" if item.get('concluido', False) else "⏳"
            texturas = ", ".join([f"`{t}`" for t in item['texturas']])
            md += f"| **{item.get('id', '-')}** | {status} | {item.get('emoji', '')} {item.get('grupo', '')} | **{item['nome']}** | {texturas} | {item.get('obs', '')} |\n"
            
        md += "\n"
        
    return md

if __name__ == "__main__":
    with open("dados.json", "r", encoding="utf-8") as f:
        dados = json.load(f)
        
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(gerar_html(dados))
        
    with open("ids.md", "w", encoding="utf-8") as f:
        f.write(gerar_md(dados))
        
    print("Arquivos gerados com sistema expansível para skins multiplas!")
