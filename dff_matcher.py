#!/usr/bin/env python3
import sys
import struct
import json
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# DFF Parsing
def get_dff_nodes(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    offset = 0
    names = []
    # Simplified parser just extracting 0x0253F2FE (String nodes which represent frame names)
    while offset < len(data) - 12:
        cid, size, ver = struct.unpack('<III', data[offset:offset+12])
        if cid == 0x0253F2FE:
            name = data[offset+12:offset+12+size].split(b'\x00')[0].decode('ascii', errors='ignore')
            if name: names.append(name)
        offset += 1
    return names

class DffMatcherApp:
    def __init__(self, root, dff_path):
        self.root = root
        self.root.title(f"Atrelar IDs - {os.path.basename(dff_path)}")
        self.root.geometry("600x500")
        self.dff_path = dff_path
        
        # Carregar items do JSON
        self.json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados.json')
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            
        self.catalog_items = []
        for skin in self.data.get('skins', []):
            for grupo in skin.get('grupos', []):
                for item in grupo.get('itens', []):
                    if item.get('id') != '-':
                        self.catalog_items.append(f"{item['id']} ({item['nome']})")
                        
        self.catalog_items.insert(0, "-- IGNORAR --")
        
        self.nodes = get_dff_nodes(self.dff_path)
        
        # UI
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        lbl = tk.Label(main_frame, text="Selecione a qual item do catálogo cada Node/Bone pertence:", font=("Arial", 10, "bold"))
        lbl.pack(anchor="w", pady=(0, 10))
        
        # Scrollable area
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.vars = {}
        for idx, node in enumerate(self.nodes):
            row = tk.Frame(scrollable_frame)
            row.pack(fill=tk.X, pady=2)
            
            lbl = tk.Label(row, text=f"ID: {idx} | {node}", width=30, anchor="w")
            lbl.pack(side=tk.LEFT)
            
            var = tk.StringVar(value="-- IGNORAR --")
            combo = ttk.Combobox(row, textvariable=var, values=self.catalog_items, state="readonly", width=40)
            combo.pack(side=tk.LEFT, padx=10)
            
            self.vars[idx] = (node, var)
            
        btn_frame = tk.Frame(self.root, pady=10)
        btn_frame.pack(fill=tk.X)
        
        save_btn = tk.Button(btn_frame, text="Salvar e Atualizar Site", command=self.save, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        save_btn.pack()

    def save(self):
        # Mapeamento do que foi selecionado
        id_mapping = {}
        for idx, (node, var) in self.vars.items():
            val = var.get()
            if val != "-- IGNORAR --":
                item_id = val.split(' (')[0]
                id_mapping[item_id] = str(idx) # ID vira o indice do bone
                
        # Atualiza o JSON
        updates = 0
        for skin in self.data.get('skins', []):
            for grupo in skin.get('grupos', []):
                for item in grupo.get('itens', []):
                    if item.get('id') in id_mapping:
                        item['dff_id'] = id_mapping[item['id']]
                        updates += 1
                        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
            
        # Roda o gerador.py
        gerador_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gerador.py')
        try:
            subprocess.run(["python3", gerador_path], check=True)
            messagebox.showinfo("Sucesso", f"{updates} itens atrelados com sucesso!\nSite gerado.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar site: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 dff_matcher.py <caminho_do_dff>")
        sys.exit(1)
        
    dff_file = sys.argv[1]
    root = tk.Tk()
    app = DffMatcherApp(root, dff_file)
    root.mainloop()

