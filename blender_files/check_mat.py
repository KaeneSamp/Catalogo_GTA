import bpy

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if len(obj.data.materials) > 0:
            mat = obj.data.materials[0]
            print(f"Object {obj.name}: Material {mat.name}")
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        print(f"  Found TEX_IMAGE: {node.name}")
                        if node.image:
                            print(f"  Image name: {node.image.name}")
                            print(f"  Image filepath: {node.image.filepath}")
                            print(f"  Is packed: {node.image.packed_file is not None}")
