#!/usr/bin/env python3
import sys
import traceback
import struct
import json
import os
import subprocess

log_file = os.path.expanduser("~/dff_matcher_error.log")

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
except Exception as e:
    with open(log_file, "a") as f:
        f.write("GTK Import Error:\n")
        f.write(traceback.format_exc() + "\n")
    sys.exit(1)

def get_dff_materials(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            
        materials = []
        
        def parse_chunk(offset, end):
            while offset <= end - 12:
                cid, size, ver = struct.unpack('<III', data[offset:offset+12])
                payload_start = offset + 12
                payload_end = payload_start + size
                
                if cid == 0x06: # Texture
                    tex_off = payload_start
                    while tex_off <= payload_end - 12:
                        in_cid, in_size, in_ver = struct.unpack('<III', data[tex_off:tex_off+12])
                        if in_cid == 0x02: # String
                            name_bytes = data[tex_off+12:tex_off+12+in_size]
                            name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore').strip()
                            if name:
                                materials.append(name)
                            break
                        tex_off += 12 + in_size
                elif cid in (0x10, 0x0F, 0x1A, 0x08, 0x07):
                    parse_chunk(payload_start, payload_end)
                        
                offset = payload_end

        parse_chunk(0, len(data))
        return materials
    except Exception as e:
        with open(log_file, "a") as f:
            f.write("DFF Parse Error:\n")
            f.write(traceback.format_exc() + "\n")
        return []

class DffMatcherWindow(Gtk.Window):
    def __init__(self, dff_path):
        super().__init__(title=f"Atrelar IDs (Materiais) - {os.path.basename(dff_path)}")
        self.set_default_size(650, 550)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.dff_path = dff_path
        self.json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados.json')
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            with open(log_file, "a") as f:
                f.write("JSON Parse Error:\n")
                f.write(traceback.format_exc() + "\n")
            self.data = {}
            
        self.catalog_items = []
        self.texture_to_catalog_idx = {}
        self.catalog_items.append("-- IGNORAR --")
        
        idx = 1
        try:
            for skin in self.data.get('skins', []):
                for grupo in skin.get('grupos', []):
                    for item in grupo.get('itens', []):
                        if item.get('id') != '-':
                            display_name = f"{item['id']} ({item['nome']})"
                            self.catalog_items.append(display_name)
                            if isinstance(item.get('texturas'), dict):
                                for tex in item['texturas'].keys():
                                    self.texture_to_catalog_idx[tex.lower()] = idx
                            elif isinstance(item.get('texturas'), list):
                                for tex_str in item['texturas']:
                                    for tex in tex_str.split(','):
                                        self.texture_to_catalog_idx[tex.strip().lower()] = idx
                            idx += 1
        except Exception as e:
            with open(log_file, "a") as f:
                f.write("Catalog Parse Error:\n")
                f.write(traceback.format_exc() + "\n")

        self.nodes = get_dff_materials(self.dff_path)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        self.add(vbox)
        
        lbl = Gtk.Label(label="Abaixo estão as texturas extraídas do DFF. O sistema auto-selecionou as texturas combinando com as do Catálogo.")
        lbl.set_halign(Gtk.Align.START)
        lbl.set_line_wrap(True)
        vbox.pack_start(lbl, False, False, 0)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)
        
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(listbox)
        
        self.combos = {}
        for mat_idx, tex_name in enumerate(self.nodes):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_border_width(5)
            row.add(hbox)
            
            lbl_node = Gtk.Label(label=f"ID: {mat_idx} | Tex: {tex_name}")
            lbl_node.set_halign(Gtk.Align.START)
            lbl_node.set_width_chars(35)
            hbox.pack_start(lbl_node, False, False, 0)
            
            store = Gtk.ListStore(str)
            for cat_item in self.catalog_items:
                store.append([cat_item])
                
            combo = Gtk.ComboBox.new_with_model(store)
            renderer_text = Gtk.CellRendererText()
            combo.pack_start(renderer_text, True)
            combo.add_attribute(renderer_text, "text", 0)
            
            target_idx = self.texture_to_catalog_idx.get(tex_name.lower(), 0)
            combo.set_active(target_idx)
            
            hbox.pack_start(combo, True, True, 0)
            listbox.add(row)
            self.combos[mat_idx] = combo
            
        save_btn = Gtk.Button(label="Salvar e Atualizar Site")
        save_btn.get_style_context().add_class("suggested-action")
        save_btn.connect("clicked", self.on_save_clicked)
        vbox.pack_start(save_btn, False, False, 0)

    def on_save_clicked(self, widget):
        try:
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
            subprocess.run(["python3", gerador_path], check=True)
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Sucesso!")
            dialog.format_secondary_text(f"{updates} itens atrelados com sucesso!\nSite gerado.")
            dialog.run()
            dialog.destroy()
            Gtk.main_quit()
        except Exception as e:
            with open(log_file, "a") as f:
                f.write("Save Error:\n")
                f.write(traceback.format_exc() + "\n")
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text="Erro")
            dialog.format_secondary_text(f"Erro ao gerar site: {e}")
            dialog.run()
            dialog.destroy()

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            with open(log_file, "a") as f:
                f.write("Startup Error: Missing DFF argument\n")
            sys.exit(1)
            
        dff_file = sys.argv[1]
        win = DffMatcherWindow(dff_file)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    except Exception as e:
        with open(log_file, "a") as f:
            f.write("Fatal Startup Error:\n")
            f.write(traceback.format_exc() + "\n")
