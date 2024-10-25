import bpy

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
            print("Executed")
        else:
            print("No object selected")
        return {'FINISHED'}

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