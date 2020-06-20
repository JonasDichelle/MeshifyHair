bl_info = {
    "name": "Hair Proxy",
    "description": "Create proxy objects for hair.",
    "author": "Jonas Dichelle",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Particles",
    "category": "Particles"
}

import bpy
import os
from .lib import hair_to_mesh
from .lib import mesh_to_cache

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )


def make_path_absolute(key):
    props = bpy.context.scene.my_collection
    abs = lambda p: os.path.abspath(bpy.path.abspath(p))
    if key in props and props[key].startswith('//'):
        props[key] = abs(props[key])

class HairProxyProperties(PropertyGroup):

    cache_index: IntProperty(
        name = "Cache Index",
        description="Index number of cache files",
        default = 0,
        min = -1,
        max = 100
        )

    start_frame: IntProperty(
        name = "Start Frame",
        description="Frame to start cache",
        default = 0,
        min = 0,
        )

    end_frame: IntProperty(
        name = "End Frame",
        description="Frame to end cache",
        default = 250,
        min = 0,
        )

    directory: StringProperty(
        name="",
        description="Path to Directory",
        default="",
        update = lambda s,c: make_path_absolute('my_filepath'),
        maxlen=1024,
        subtype='DIR_PATH',
        )

    name: StringProperty(
        name="Name",
        description="Name",
        default="",
        )

    proxy: StringProperty(
        name="Proxy Object",
        description="Object to be used as a proxy for the hair cache",
        default="",
        )

class HairProxyPanel(Panel):
    bl_label = "Hair Proxy"
    bl_idname = "OBJECT_PT_hairproxy"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "particle"


    @classmethod
    def poll(self,context):
        if len(context.object.particle_systems) > 0:
            if context.object.particle_systems.active.settings.type == "HAIR":
                return context.object is not None

    def draw(self, context):
        layout = self.layout
        object = context.object
        settings = bpy.context.object.particle_systems.active.settings
        hairproxy = settings.hairproxy

        col = layout.column()
        col.operator("object.hair_to_mesh", text="Generate Proxy Mesh", icon="PARTICLE_POINT")
        col.separator()
        box = col.box()
        box.label(text = "Cache")
        box = box.column(align = True)
        box.prop(hairproxy, "start_frame")
        box.prop(hairproxy, "end_frame")
        box = box.column()
        box.separator()
        box.prop_search(hairproxy, "proxy", bpy.data, "objects", text="Proxy Object")
        box.prop(hairproxy, "name", text="Name")
        box.prop(hairproxy, "directory", text="Path")
        box.prop(hairproxy, "cache_index")
        box.operator("object.mesh_to_cache", text="Proxy Mesh To Cache", icon="FILE_CACHE")
        col.separator()

classes = (
    HairProxyProperties,
    HairProxyPanel
)

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    hair_to_mesh.register()
    mesh_to_cache.register()

    bpy.types.ParticleSettings.hairproxy = PointerProperty(type=HairProxyProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    hair_to_mesh.unregister()
    mesh_to_cache.unregister()

    del bpy.types.ParticleSettings.hairproxy


if __name__ == "__main__":
    register()
