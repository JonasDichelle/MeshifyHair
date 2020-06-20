import bpy
import os
import numpy
import mathutils

def hair_to_mesh(context):
    dg = context.evaluated_depsgraph_get()
    ob = context.object
    settings = ob.particle_systems.active.settings
    hairproxy = settings.hairproxy
    particles = dg.objects[ob.name].particle_systems.active.particles

    name = context.object.particle_systems.active.name + "_proxy"
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(name, mesh)
    hair_weight_vg = object.vertex_groups.new(name="Hair Weight")
    hair_intercept_vg = object.vertex_groups.new(name="Hair Intercept")
    roots_vg = object.vertex_groups.new(name="Hair Roots")
    tips_vg = object.vertex_groups.new(name="Hair Tips")
    step_idx = 0
    edges = []
    loc = []
    prev_steps = 0
    mat = ob.matrix_world
    weights = {}
    intercepts = {}
    root_verts = []
    tip_verts = []
    mesh.from_pydata(loc,edges,[])
    mesh.update(calc_edges=True)

    for h in particles:
        v = (mat @ h.hair_keys[1].co) - (mat @ h.hair_keys[0].co)
        point0 = (mat @ h.hair_keys[0].co) - v
        loc.append(point0)
        weights[step_idx] = h.hair_keys[0].weight

        edges.append([step_idx, step_idx+1])
        step_idx += 1
        hair_icpts = []
        hair_icpts.append(0.0)
        root_verts.append(step_idx)
        for idx, s in enumerate(h.hair_keys):
            if idx == len(h.hair_keys)-1:
                tip_verts.append(step_idx)
            if step_idx-prev_steps+1 < (len(h.hair_keys)+1):
                edges.append([step_idx, step_idx+1])
            weights[step_idx] = h.hair_keys[idx].weight
            glob_co = mat @ s.co
            hair_icpts.append(numpy.linalg.norm(glob_co - loc[-1]))
            loc.append(mat @ s.co)
            step_idx += 1
        prev_steps = step_idx

        tot_icpt = 0.0
        max_icpt = 0.0

        for i in hair_icpts:
            max_icpt += i

        for i in hair_icpts:
            tot_icpt += i
            if len(intercepts.items()) == 0:
                intercepts[0] = (tot_icpt)/(max_icpt)
            else:
                intercepts[list(intercepts)[-1]+1] = (tot_icpt)/(max_icpt)

    mesh.from_pydata(loc,edges,[])
    mesh.update(calc_edges=True)

    for idx, weight in weights.items():
        hair_weight_vg.add([idx], weight, 'ADD')

    for idx, dist in intercepts.items():
        hair_intercept_vg.add([idx], dist, 'ADD')

    tips_vg.add(tip_verts, 1.0, 'ADD')
    roots_vg.add(root_verts, 1.0, 'ADD')

    bpy.context.collection.objects.link(object)

    for vg in ob.vertex_groups:
        object.vertex_groups.new(name=vg.name)

    for r in root_verts:
        size = len(ob.data.vertices)
        kd = mathutils.kdtree.KDTree(size)

        for i, v in enumerate(ob.data.vertices):
            kd.insert(v.co, i)

        kd.balance()

        co_find = mat @ object.data.vertices[r].co
        co, index, dist = kd.find(co_find)
        for g in ob.data.vertices[index].groups:
            object.vertex_groups[ob.vertex_groups[g.group].name].add([r], g.weight, 'ADD')

    for i, r in enumerate(root_verts):
        for g in object.data.vertices[r].groups:
            name = object.vertex_groups[g.group].name
            if name != "Hair Weight" and name != "Hair Intercept" and name != "Hair Roots" and name != "Hair Tips":
                print(object.vertex_groups[g.group].name)
                object.vertex_groups[g.group].add([i], g.weight, 'REPLACE')

class HairToMesh(bpy.types.Operator):
    """Turn hair into mesh object"""
    bl_idname = "object.hair_to_mesh"
    bl_label = "   Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        hair_to_mesh(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(HairToMesh)

def unregister():
    bpy.utils.unregister_class(HairToMesh)
