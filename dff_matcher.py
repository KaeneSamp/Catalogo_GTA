#!/usr/bin/env python3
import sys
import traceback
import struct
import json
import os
import subprocess
import glob

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
        super().__init__(title=f"Atrelar IDs - {os.path.basename(dff_path)}")
        self.set_default_size(700, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.dff_path = dff_path
        self.nodes = get_dff_materials(self.dff_path)
        
        self.projects = self.find_projects()
        
        self.current_project_path = None
        self.data = {}
        self.combos = {}
        
        # UI Setup
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        self.add(vbox)
        
        # Project Selection
        hbox_proj = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_proj = Gtk.Label(label="<b>1. Selecione o Projeto Alvo:</b>")
        lbl_proj.set_use_markup(True)
        hbox_proj.pack_start(lbl_proj, False, False, 0)
        
        self.proj_combo = Gtk.ComboBoxText()
        for idx, p in enumerate(self.projects):
            self.proj_combo.append_text(f"{p['name']} ({os.path.basename(p['path'])})")
        
        self.proj_combo.connect("changed", self.on_project_changed)
        hbox_proj.pack_start(self.proj_combo, True, True, 0)
        vbox.pack_start(hbox_proj, False, False, 0)
        
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(separator, False, False, 5)
        
        lbl_info = Gtk.Label(label="<b>2. Defina os IDs das Texturas:</b>\nAbaixo estão as texturas extraídas do DFF. O sistema auto-selecionará caso os nomes batam.")
        lbl_info.set_use_markup(True)
        lbl_info.set_halign(Gtk.Align.START)
        lbl_info.set_line_wrap(True)
        vbox.pack_start(lbl_info, False, False, 0)
        
        # Scrolled Area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)
        
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.listbox)
        
        # Save Button
        self.save_btn = Gtk.Button(label="Salvar e Atualizar Site")
        self.save_btn.get_style_context().add_class("suggested-action")
        self.save_btn.connect("clicked", self.on_save_clicked)
        self.save_btn.set_sensitive(False)
        vbox.pack_start(self.save_btn, False, False, 0)
        
        if self.projects:
            self.proj_combo.set_active(0)

    def find_projects(self):
        docs_dir = os.path.expanduser("~/Documents")
        projects = []
        for d in os.listdir(docs_dir):
            full_path = os.path.join(docs_dir, d)
            if os.path.isdir(full_path):
                json_path = os.path.join(full_path, "dados.json")
                gerador_path = os.path.join(full_path, "gerador.py")
                if os.path.exists(json_path) and os.path.exists(gerador_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            proj_name = data.get("projeto", d)
                            projects.append({"name": proj_name, "path": full_path})
                    except:
                        pass
        return projects

    def on_project_changed(self, combo):
        idx = combo.get_active()
        if idx < 0: return
        
        proj = self.projects[idx]
        self.current_project_path = proj['path']
        self.load_project_ui()

    def load_project_ui(self):
        # Clear existing rows
        for row in self.listbox.get_children():
            self.listbox.remove(row)
            
        self.combos.clear()
        
        json_path = os.path.join(self.current_project_path, 'dados.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            with open(log_file, "a") as f:
                f.write(f"Failed to load json {json_path}:\n{traceback.format_exc()}\n")
            return
            
        catalog_items = ["-- IGNORAR --"]
        texture_to_idx = {}
        
        item_idx = 1
        for skin in self.data.get('skins', []):
            for grupo in skin.get('grupos', []):
                for item in grupo.get('itens', []):
                    if item.get('id') != '-':
                        display_name = f"{item['id']} ({item['nome']})"
                        catalog_items.append(display_name)
                        
                        if isinstance(item.get('texturas'), dict):
                            for tex in item['texturas'].keys():
                                texture_to_idx[tex.lower()] = item_idx
                        elif isinstance(item.get('texturas'), list):
                            for tex_str in item['texturas']:
                                for tex in tex_str.split(','):
                                    texture_to_idx[tex.strip().lower()] = item_idx
                        item_idx += 1
                        
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
            for cat_item in catalog_items:
                store.append([cat_item])
                
            combo = Gtk.ComboBox.new_with_model(store)
            renderer_text = Gtk.CellRendererText()
            combo.pack_start(renderer_text, True)
            combo.add_attribute(renderer_text, "text", 0)
            
            target_idx = texture_to_idx.get(tex_name.lower(), 0)
            combo.set_active(target_idx)
            
            hbox.pack_start(combo, True, True, 0)
            self.listbox.add(row)
            self.combos[mat_idx] = combo
            
        self.listbox.show_all()
        self.save_btn.set_sensitive(True)

    def on_save_clicked(self, widget):
        if not self.current_project_path: return
        
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
                            
            json_path = os.path.join(self.current_project_path, 'dados.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
                
            gerador_path = os.path.join(self.current_project_path, 'gerador.py')
            subprocess.run(["python3", gerador_path], check=True, cwd=self.current_project_path)
            
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Sucesso!")
            dialog.format_secondary_text(f"{updates} itens atrelados ao projeto '{os.path.basename(self.current_project_path)}' com sucesso!\nSite gerado.")
            dialog.run()
            dialog.destroy()
            Gtk.main_quit()
            
        except Exception as e:
            with open(log_file, "a") as f:
                f.write("Save Error:\n")
                f.write(traceback.format_exc() + "\n")
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text="Erro")
            dialog.format_secondary_text(f"Erro ao salvar: {e}")
            dialog.run()
            dialog.destroy()

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
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
