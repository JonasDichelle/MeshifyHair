import bpy
import bmesh
import struct

def mesh_to_cache(context):
    before_frame = context.scene.frame_current
    dg = context.evaluated_depsgraph_get()
    object = context.object
    settings = bpy.context.object.particle_systems.active.settings
    hairproxy = settings.hairproxy

    start_frame = hairproxy.start_frame
    end_frame = hairproxy.end_frame

    ob = bpy.data.objects[hairproxy["proxy"]]
    key_len = len(ob.data.vertices)
    end_frame = end_frame
    directory = hairproxy.directory
    cache_index = hairproxy.cache_index

    cache_name = hairproxy.name
    point_count = len(ob.data.vertices)

    file_name = cache_name + "_{0:06d}_{1:02d}.bphys".format(0,cache_index)
    path = directory + file_name

    file = open(path, "wb")

    file.write(struct.pack('8s', 'BPHYSICS'.encode(encoding='UTF-8')))
    file.write(struct.pack("III", 2, key_len, 22))

    file.close

    for f in range(start_frame, end_frame):
        bm = bmesh.new()
        bm.from_object(ob, dg)
        bm.verts.ensure_lookup_table()
        verts = bm.verts
        locs = []
        for v in verts:
            mat = ob.matrix_world
            loc = mat @ v.co
            locs.append(loc)
        bm.free()

        bpy.context.scene.frame_set(f)
        frame_current = f

        file_name = cache_name + "_{0:06d}_{1:02d}.bphys".format(frame_current, cache_index)
        path = directory + file_name

        file = open(path, "wb")

        dataType = 2
        file.write(struct.pack('8s', 'BPHYSICS'.encode(encoding='UTF-8')))
        file.write(struct.pack("III", 2, len(locs), 22))

        for loc in locs:
            file.write(struct.pack('fff', loc[0], loc[1], loc[2]))
            file.write(struct.pack('fff', 0.0, 0.0, 0.0))
            file.write(struct.pack('fff', 0.0, 0.0, 0.0))

        file.close
    bpy.context.object.particle_systems.active.use_hair_dynamics = True
    bpy.context.object.particle_systems.active.point_cache.use_external = True
    bpy.context.object.particle_systems.active.point_cache.name = cache_name
    bpy.context.object.particle_systems.active.point_cache.filepath = directory
    bpy.context.object.particle_systems.active.point_cache.index = hairproxy.cache_index
    bpy.context.scene.frame_set(before_frame)


class MeshToCache(bpy.types.Operator):
    """Export mesh to cache in the cache directory"""
    bl_idname = "object.mesh_to_cache"
    bl_label = "   Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mesh_to_cache(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MeshToCache)

def unregister():
    bpy.utils.unregister_class(MeshToCache)
