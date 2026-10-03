#!/usr/bin/env python3
import sys
import struct
import json
import os
import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

def get_dff_nodes(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    offset = 0
    names = []
    while offset < len(data) - 12:
        cid, size, ver = struct.unpack('<III', data[offset:offset+12])
        if cid == 0x0253F2FE:
            name = data[offset+12:offset+12+size].split(b'\x00')[0].decode('ascii', errors='ignore')
            if name: names.append(name)
        offset += 1
    return names

class DffMatcherWindow(Gtk.Window):
    def __init__(self, dff_path):
        super().__init__(title=f"Atrelar IDs - {os.path.basename(dff_path)}")
        self.set_default_size(600, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.dff_path = dff_path
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
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        self.add(vbox)
        
        lbl = Gtk.Label(label="Selecione a qual item do catálogo cada Node/Bone pertence:")
        lbl.set_halign(Gtk.Align.START)
        vbox.pack_start(lbl, False, False, 0)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)
        
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(listbox)
        
        self.combos = {}
        for idx, node in enumerate(self.nodes):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_border_width(5)
            row.add(hbox)
            
            lbl_node = Gtk.Label(label=f"ID: {idx} | {node}")
            lbl_node.set_halign(Gtk.Align.START)
            lbl_node.set_width_chars(30)
            hbox.pack_start(lbl_node, False, False, 0)
            
            store = Gtk.ListStore(str)
            for cat_item in self.catalog_items:
                store.append([cat_item])
                
            combo = Gtk.ComboBox.new_with_model(store)
            renderer_text = Gtk.CellRendererText()
            combo.pack_start(renderer_text, True)
            combo.add_attribute(renderer_text, "text", 0)
            combo.set_active(0)
            
            hbox.pack_start(combo, True, True, 0)
            listbox.add(row)
            self.combos[idx] = combo
            
        save_btn = Gtk.Button(label="Salvar e Atualizar Site")
        save_btn.get_style_context().add_class("suggested-action")
        save_btn.connect("clicked", self.on_save_clicked)
        vbox.pack_start(save_btn, False, False, 0)

    def on_save_clicked(self, widget):
        id_mapping = {}
        for idx, combo in self.combos.items():
            tree_iter = combo.get_active_iter()
            if tree_iter is not None:
                model = combo.get_model()
                val = model[tree_iter][0]
                if val != "-- IGNORAR --":
                    item_id = val.split(' (')[0]
                    id_mapping[item_id] = str(idx)
                    
        updates = 0
        for skin in self.data.get('skins', []):
            for grupo in skin.get('grupos', []):
                for item in grupo.get('itens', []):
                    if item.get('id') in id_mapping:
                        item['dff_id'] = id_mapping[item['id']]
                        updates += 1
                        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
            
        gerador_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gerador.py')
        try:
            subprocess.run(["python3", gerador_path], check=True)
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Sucesso!"
            )
            dialog.format_secondary_text(f"{updates} itens atrelados com sucesso!\nSite gerado.")
            dialog.run()
            dialog.destroy()
            Gtk.main_quit()
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Erro"
            )
            dialog.format_secondary_text(f"Erro ao gerar site: {e}")
            dialog.run()
            dialog.destroy()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 dff_matcher.py <caminho_do_dff>")
        sys.exit(1)
        
    dff_file = sys.argv[1]
    win = DffMatcherWindow(dff_file)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
