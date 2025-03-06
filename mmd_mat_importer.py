import struct, os

import mset

class PMX:
    def __init__(self, filename):
        with open(filename, 'rb') as f:
            Signature = f.read(4)

            if Signature.decode() != "PMX ":
                raise Exception("model type is not PMX")
            else:
                print("Loading PMX")

            self.Version = struct.unpack('<f', f.read(4))[0]

            Global_Count = int.from_bytes(f.read(1), byteorder='little', signed=False)

            Globals = list(f.read(Global_Count))

            Index = self.Index = {'Text Encoding' : "UTF16" if Globals[0] == 0 else "UTF8",
                    'Appendix UV' : Globals[1],
                    'Vertex Index Size' : Globals[2],
                    'Texture Index Size' : Globals[3],
                    'Material Index Size' :Globals[4],
                    'Bone Index Size' : Globals[5],
                    'Morph Index Size' : Globals[6],
                    'Rigid Body Index Size' : Globals[7],
                    }

            self.Model_Name = f.read(int.from_bytes(f.read(4), byteorder='little', signed=False)).decode(self.Index['Text Encoding'])
            self.Model_Name_Universal = f.read(int.from_bytes(f.read(4), byteorder='little', signed=False)).decode(self.Index['Text Encoding'])

            self.Comments_Local = f.read(int.from_bytes(f.read(4), byteorder='little', signed=False)).decode(Index['Text Encoding'])
            self.Comments_Universal = f.read(int.from_bytes(f.read(4), byteorder='little', signed=False)).decode(Index['Text Encoding'])

            bone_index_type = {1: 'b', 2: 'h', 4:'i'}[Index['Bone Index Size']]
            vertex_index_type = {1:'B', 2:'H', 4:'i'}[Index['Vertex Index Size']]
            texture_index_type = {1: 'b', 2: 'h', 4:'i'}[Index['Texture Index Size']]
            morph_index_type = {1: 'b', 2: 'h', 4:'i'}[Index['Morph Index Size']]
            material_index_type = {1: 'b', 2: 'h', 4:'i'}[Index['Material Index Size']]
            rigid_body_index_type = {1: 'b', 2: 'h', 4:'i'}[Index['Rigid Body Index Size']]

            Vertex_Count = int.from_bytes(f.read(4), byteorder='little', signed=True)
            print(f"Vertex Count: {Vertex_Count}")
            self.Vertices = []

            for i in range(Vertex_Count):
                Position = struct.unpack("<fff", f.read(12))

                Normal = struct.unpack("<fff", f.read(12))

                UV_Texture_Coordinate = struct.unpack("<ff", f.read(8))

                Appendix_UV = []
                for j in range(Index['Appendix UV']):
                    Appendix_UV.append(struct.unpack("<ffff", f.read(16)))

                Weight_Type = int.from_bytes(f.read(1), byteorder='little', signed=True)

                # struct: [(bone, weight),...]
                Weight_Deform = []
                if Weight_Type == 0:# BDEF1
                    BDEF1 = struct.unpack('<'+bone_index_type, f.read(Index['Bone Index Size']))[0]
                    Weight_Deform.append((BDEF1, 1))
                elif Weight_Type == 1:# BDEF2
                    BDEF2 = struct.unpack('<'+bone_index_type*2+'f', f.read(Index['Bone Index Size']*2+4))
                    Weight_Deform.extend([(BDEF2[0], BDEF2[2]), (BDEF2[1], 1-BDEF2[2])])
                elif Weight_Type == 2:# BDEF4
                    BDEF4 = struct.unpack('<'+bone_index_type*4+'ffff', f.read(Index['Bone Index Size']*4+16))
                    Weight_Deform.extend([(BDEF4[0], BDEF4[4]),
                                        (BDEF4[1], BDEF4[5]),
                                        (BDEF4[2], BDEF4[6]),
                                        (BDEF4[3], BDEF4[7])])
                elif Weight_Type == 3:# SDEF
                    SDEF = struct.unpack('<'+bone_index_type*2+'f'+'f'*9, f.read(Index['Bone Index Size']*2+40))
                    Weight_Deform.extend([(SDEF[0], SDEF[2]), (SDEF[1], 1 - SDEF[2]), {'C': SDEF[3:6], 'R0':SDEF[6:9], 'R1':SDEF[9:12]}])
                elif Weight_Type == 4:#QDEF
                    QDEF = struct.unpack('<' + bone_index_type * 4 + 'ffff', f.read(Index['Bone Index Size'] * 4 + 16))
                    Weight_Deform.extend([(QDEF[0], QDEF[4]),
                                        (QDEF[1], QDEF[5]),
                                        (QDEF[2], QDEF[6]),
                                        (QDEF[3], QDEF[7])])
                elif Weight_Type == -1:
                    pass
                else:
                    raise Exception(f'Weight Type {Weight_Type} not found')

                Edge_Scale = struct.unpack('<f', f.read(4))[0]

                self.Vertices.append({
                    'Position':Position,
                    'Normal':Normal,
                    'UV Texture Coordinate':UV_Texture_Coordinate,
                    'Appendix UV':Appendix_UV,
                    'Weight Type':Weight_Type,
                    'Weight Deform':Weight_Deform,
                    'Edge Scale':Edge_Scale
                })

            Surface_Count = int.from_bytes(f.read(4), byteorder='little', signed=True)
            print(f'Surface count: {Surface_Count}')

            self.Surfaces = []
            for i in range(Surface_Count//3):
                self.Surfaces.append(struct.unpack('<'+vertex_index_type*3,f.read(3*Index['Vertex Index Size'])))

            Texture_Count = int.from_bytes(f.read(4), byteorder='little', signed=True)
            print(f'Texture_Count: {Texture_Count}')
            self.Textures = []
            for i in range(Texture_Count):
                self.Textures.append(f.read(int.from_bytes(f.read(4), byteorder='little', signed=False)).decode(Index['Text Encoding']))

            Material_Count = int.from_bytes(f.read(4), byteorder='little', signed=True)
            print(f'Material Count: {Material_Count}')
            self.Materials = []
            for i in range(Material_Count):
                Material_Name_Local = f.read(int.from_bytes(f.read(4), byteorder='little', signed=False)).decode(Index['Text Encoding'])
                Material_Name_Universal = f.read(int.from_bytes(f.read(4), byteorder='little', signed=False)).decode(Index['Text Encoding'])
                Diffuser_Color = struct.unpack('<ffff', f.read(16))
                Specular_Color=struct.unpack('<fff', f.read(12))
                Speculat_Strength=struct.unpack('<f', f.read(4))[0]
                Ambient_Color=struct.unpack('<fff',f.read(12))
                Drawing_Flags=f.read(1)[0]
                Drawing_Flags = {
                    'No-Cull': Drawing_Flags & 0b00000001 == 0b00000001,
                    'Ground Shadow':Drawing_Flags & 0b00000010 == 0b00000010,
                    'Draw shadow':Drawing_Flags & 0b00000100 == 0b00000100,
                    'Receive Shadow':Drawing_Flags & 0b00001000 == 0b00001000,
                    'Has Edge':Drawing_Flags & 0b00010000 == 0b00010000,
                    'Vertex Color':Drawing_Flags & 0b00100000 == 0b00100000,
                    'Point Drawing':Drawing_Flags & 0b01000000 == 0b01000000,
                    'Line Drawing': Drawing_Flags & 0b10000000 == 0b10000000
                }
                Edge_Color = struct.unpack('<ffff', f.read(16))
                Edge_Scale = struct.unpack('<f', f.read(4))[0]
                Texture_Index = struct.unpack('<'+texture_index_type, f.read(Index['Texture Index Size']))[0]
                Environment_Index = struct.unpack('<' + texture_index_type, f.read(Index['Texture Index Size']))[0]
                Environment_Blend_Mode = f.read(1)[0]
                Toon_Reference = f.read(1)[0]
                if Toon_Reference == 0:#reference texture
                    Toon_Value = struct.unpack('<'+texture_index_type, f.read(Index['Texture Index Size']))[0]
                elif Toon_Reference == 1:#reference internal
                    Toon_Value = f.read(1)[0]
                else:
                    raise Exception(f'Toon Reference {Toon_Reference} not found')
                Meta_Data = f.read(int.from_bytes(f.read(4), byteorder='little', signed=False)).decode('UTF16')
                Material_Surface_Count = int.from_bytes(f.read(4), byteorder='little', signed=True) // 3
                self.Materials.append({
                    'Material Name Local':Material_Name_Local,
                    'Material Name Universal': Material_Name_Universal,
                    'Diffuser Color': Diffuser_Color,
                    'Specular Color': Specular_Color,
                    'Speculat Strength': Speculat_Strength,
                    'Ambient Color': Ambient_Color,
                    'Drawing Flags': Drawing_Flags,
                    'Edge Color': Edge_Color,
                    'Texture Index': Texture_Index,
                    'Environment Index': Environment_Index,
                    'Environment Blend Mode': Environment_Blend_Mode,
                    'Toon Reference': Toon_Reference,
                    'Toon Value': Toon_Value,
                    'Meta Data': Meta_Data,
                    'Surface Count': Material_Surface_Count
                })


def get_absolute_path(first_file: str, second_file: str) -> str:
    first_dir = os.path.dirname(first_file)
    second_abs_path = os.path.abspath(os.path.join(first_dir, second_file))
    return second_abs_path


def import_mat():
    selected_object = mset.getSelectedObject()
    print(type(selected_object))
    if not isinstance(selected_object, mset.MeshObject):
        return
    submesh_tris_count = [sub.indexCount // 3 for sub in selected_object.getChildren()]
    print('submesh_tris_count', submesh_tris_count)

    pmx_path = mset.showOpenFileDialog(['pmx'])
    if pmx_path == '':
        mset.shutdownPlugin()
    pmx = PMX(pmx_path)
    pmx_tris_count = [mat['Surface Count'] for mat in pmx.Materials]
    print('submesh_tris_count', submesh_tris_count)
    if len(pmx.Materials) != len(selected_object.getChildren()):
        return
    for i, mat_info in enumerate(pmx.Materials):
        mat_name = "{}_mat_{}".format(selected_object.name, i)
        print(mat_name)
        mat = mset.Material(name=mat_name)
        if mat_info['Texture Index'] >= 0:
            img_path = get_absolute_path(pmx_path, pmx.Textures[mat_info['Texture Index']])
            if not os.path.exists(img_path):
                mset.err("img not found: {}".format(img_path))
                continue
            tex = mset.Texture(img_path)
            print(tex)
            mat.albedo.setField("Albedo Map", mset.Texture(img_path))
        selected_object.getChildren()[len(pmx.Materials) - 1 - i].material = mat
        selected_object.getChildren()[len(pmx.Materials) - 1 - i].name = "submesh_{}".format(i)
    mset.shutdownPlugin()

def fuck():
    try:
        import_mat()
    except Exception as e:
        print(e)

def close_callback():
    mset.shutdownPlugin()


if __name__ == '__main__':
    #create a window
    mmd_window = mset.UIWindow("MMD Matertials Importer")
    fov_label = mset.UILabel('Select ABC mesh and import matertials from PMX.')
    fov_button = mset.UIButton("Import matertials from PMX")
    fov_button.onClick = fuck
    
    close_button = mset.UIButton("Close")
    close_button.onClick = close_callback

    #add the button to the window
    mmd_window.addElement(fov_label)
    mmd_window.addReturn()
    mmd_window.addElement(fov_button)
    mmd_window.addElement(close_button)
