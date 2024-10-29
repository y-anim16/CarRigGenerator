import bpy
import mathutils

bl_info = {
    "name": "CarRigGenerator",
    "author": "",
    "version": (0, 1, 0),
    "blender": (4, 1, 0),
    "location": "",
    "description": "",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "All"
}

class CarPartsParameters(bpy.types.PropertyGroup):
    car_body: bpy.props.StringProperty(name="Object Name")
    front_wheel: bpy.props.StringProperty(name="Object Name")
    back_wheel: bpy.props.StringProperty(name="Object Name")

class CarRigGenerator(bpy.types.Operator):
    bl_idname = "object.car_rig_generator"
    bl_label = "CarRigGenerator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        car_parts = context.scene.car_parts_parameters

        if car_parts.car_body and car_parts.front_wheel and car_parts.back_wheel:
            self.create_armature(car_parts)
        else:
            print("No object selected")
        return {'FINISHED'}
    
    def create_armature(self, car_parts):
        bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0,0,0), scale=(1, 1, 1))

        new_armature = bpy.context.active_object
        armature_data = new_armature.data
        armature_data.name = 'ArmatureData'

        primary_bone = bpy.context.active_bone
        primary_bone.name = 'Primary'

        root_bone = self.add_bone(
            armature_data, 
            "Root", 
            primary_bone.head,
            primary_bone.tail,
            primary_bone.roll,
            primary_bone
        )
        
        front_wheel_obj = bpy.data.objects.get(car_parts.front_wheel)
        front_wheel_center = self.get_center_coords(front_wheel_obj)
        half_wheel_thickness = mathutils.Vector((front_wheel_obj.dimensions.x / 2, 0, 0))
        # TODO rename
        front_wheel_bone = self.add_bone(
            armature_data,
            "FrontWheel_L",
            front_wheel_center - half_wheel_thickness,
            front_wheel_center,
            primary_bone.roll,
            root_bone            
        )

        front_wheel_sub_bone = self.add_bone(
            armature_data,
            "FrontWheelSub_L",
            front_wheel_center,
            front_wheel_center + half_wheel_thickness,
            primary_bone.roll,
            front_wheel_bone
        )

        back_wheel_obj = bpy.data.objects.get(car_parts.back_wheel)
        back_wheel_center = self.get_center_coords(back_wheel_obj)
        back_wheel_bone = self.add_bone(
            armature_data,
            "BackWheel_L",
            back_wheel_center,
            back_wheel_center + mathutils.Vector((back_wheel_obj.dimensions.x / 2, 0, 0)),
            primary_bone.roll,
            root_bone
        )

        bpy.ops.object.mode_set(mode='OBJECT')


    def add_bone(self, armature_data, bone_name, head = None, tail = None, roll = None, parent = None):
        new_bone = armature_data.edit_bones.new(name=bone_name)

        if head:
            new_bone.head = head
        if tail:
            new_bone.tail = tail
        if roll:
            new_bone.roll = roll
        if parent:
            new_bone.parent = parent

        return new_bone
    
    def get_center_coords(self, obj):
        bb = obj.bound_box
        bb_world_coords = [obj.matrix_world @ mathutils.Vector(corner) for corner in bb]
        return sum(bb_world_coords, mathutils.Vector()) / 8


class CarRigGeneratorUi(bpy.types.Panel):
    bl_idname = "car_rig_generator_ui"
    bl_label = "CarRigGeneratorUi"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CarRigGenerator"

    def draw(self, context):
        layout = self.layout
        
        scene = context.scene
        selected_parts = scene.car_parts_parameters

        layout.label(text = "Car body:")
        layout.prop_search(selected_parts, "car_body", bpy.data, "objects", text="")

        layout.label(text = "Front wheel:")
        layout.prop_search(selected_parts, "front_wheel", bpy.data, "objects", text="")

        layout.label(text = "Back wheel:")
        layout.prop_search(selected_parts, "back_wheel", bpy.data, "objects", text="")

        layout.separator()

        layout.operator(CarRigGenerator.bl_idname, text = "Generate rig")

classes = [
    CarPartsParameters,
    CarRigGenerator,
    CarRigGeneratorUi,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.car_parts_parameters = bpy.props.PointerProperty(type=CarPartsParameters)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    
    del bpy.types.Scene.car_parts_parameters

if __name__ == "__main__":
    register()