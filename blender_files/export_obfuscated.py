import bpy
import struct
import bmesh
import os
import shutil
import json

# Novos caminhos organizados do Catalogo GTA
base_dir = "/home/kaua/Documents/Catalogo_GTA/assets"
models_dir = os.path.join(base_dir, "models")
img_dir = os.path.join(base_dir, "img")

if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

file_index = 1
manifest = {}

# MUDANÇA: Exporta apenas os objetos SELECIONADOS, ao invés de todos os visíveis
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        print(f"Processando {obj.name}...")
        
        # --- 1. Encontrar e Copiar Textura ---
        texture_name = None
        if len(obj.data.materials) > 0:
            mat = obj.data.materials[0]
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        image_path = bpy.path.abspath(node.image.filepath)
                        if os.path.exists(image_path):
                            tex_filename = os.path.basename(image_path)
                            # Texturas vao direto para a pasta img!
                            dest_path = os.path.join(img_dir, tex_filename)
                            if not os.path.exists(dest_path):
                                shutil.copy2(image_path, dest_path)
                            texture_name = tex_filename
                        break
        
        # --- 2. Extrair Geometria ---
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        mesh.calc_loop_triangles()

        vertices = []
        normals = []
        uvs = []
        indices = []
        unique_verts = {}
        vert_index = 0
        
        uv_layer = mesh.uv_layers.active.data if mesh.uv_layers.active else None
        matrix_world = eval_obj.matrix_world
        normal_matrix = matrix_world.to_3x3().inverted().transposed()

        for tri in mesh.loop_triangles:
            for i in range(3):
                loop_idx = tri.loops[i]
                loop = mesh.loops[loop_idx]
                vert = mesh.vertices[loop.vertex_index]
                
                pos = matrix_world @ vert.co
                norm = normal_matrix @ loop.normal
                norm.normalize()
                
                uv = uv_layer[loop_idx].uv if uv_layer else (0.0, 0.0)
                
                key = (round(pos.x, 4), round(pos.y, 4), round(pos.z, 4), 
                       round(norm.x, 4), round(norm.y, 4), round(norm.z, 4), 
                       round(uv[0], 4), round(uv[1], 4))
                
                if key not in unique_verts:
                    unique_verts[key] = vert_index
                    vertices.extend([pos.x, pos.y, pos.z])
                    normals.extend([norm.x, norm.y, norm.z])
                    uvs.extend([uv[0], uv[1]])
                    vert_index += 1
                    
                indices.append(unique_verts[key])

        if len(indices) == 0:
            eval_obj.to_mesh_clear()
            continue

        # --- 3. Salvar Binario e Atualizar Manifesto ---
        # Malhas vao direto para a pasta models!
        dat_filename = f"sys_cache_{file_index:02d}.dat"
        out_file = os.path.join(models_dir, dat_filename)
        
        with open(out_file, "wb") as f:
            f.write(struct.pack("<II", vert_index, len(indices)))
            f.write(struct.pack(f"<{len(vertices)}f", *vertices))
            f.write(struct.pack(f"<{len(normals)}f", *normals))
            f.write(struct.pack(f"<{len(uvs)}f", *uvs))
            f.write(struct.pack(f"<{len(indices)}I", *indices))
            
        manifest[dat_filename] = {
            "name": obj.name,
            "texture": texture_name
        }
        
        file_index += 1
        eval_obj.to_mesh_clear()

# Salvar o manifesto final
# Manifesto vai junto com as malhas na pasta models!
with open(os.path.join(models_dir, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=4)

print("Exportacao concluida! Malhas em assets/models e Texturas em assets/img")
