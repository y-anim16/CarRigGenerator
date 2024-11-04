import bpy
import mathutils
import math

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
        combined_dimensions = self.get_combined_dimensions()

        bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0,0,0), scale=(1, 1, 1))

        new_armature = bpy.context.active_object
        armature_data = new_armature.data
        armature_data.name = 'ArmatureData'

        primary_bone = bpy.context.active_bone
        primary_bone.name = 'Primary'
        primary_bone_length = (primary_bone.tail - primary_bone.head).length

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

        steering_bone = self.add_bone(
            armature_data,
            "SteeringBone_L",
            front_wheel_center - half_wheel_thickness,
            front_wheel_center,
            primary_bone.roll,
            root_bone
        )

        front_wheel_bone = self.add_bone(
            armature_data,
            "FrontWheel_L",
            steering_bone.head,
            steering_bone.tail,
            primary_bone.roll,
            steering_bone            
        )
        front_wheel_bone_length = (front_wheel_bone.tail - front_wheel_bone.head).length

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
        back_wheel_bone_length = (back_wheel_bone.tail - back_wheel_bone.head).length

        back_wheel_sub_bone = self.add_bone(
            armature_data,
            "BackWheelSub_L",
            back_wheel_bone.head,
            back_wheel_bone.tail,
            back_wheel_bone.roll,
            back_wheel_bone
        )

        bpy.ops.object.mode_set(mode='OBJECT')

        collection_name = "ControllerCurves"
        if collection_name not in bpy.data.collections:
            curve_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(curve_collection)
        else:
            curve_collection = bpy.data.collections[collection_name]

        # コントローラ用カーブの作成
        # TODO refactor 同じ形状のカーブ生成処理は減らせるはず
        primary_controller_radius = (combined_dimensions.x if combined_dimensions.x >= combined_dimensions.y else combined_dimensions.y) / 2
        primary_controller = self.create_circle_curve(primary_controller_radius)
        self.to_collection(primary_controller, curve_collection)

        root_controller = self.create_rectangle_curve(combined_dimensions.x, combined_dimensions.y)
        self.to_collection(root_controller, curve_collection)

        front_wheel_controller = self.create_circle_curve(front_wheel_obj.dimensions.y / 2)
        self.to_collection(front_wheel_controller, curve_collection)

        front_wheel_sub_controller = self.create_rectangle_curve(front_wheel_obj.dimensions.y, front_wheel_obj.dimensions.y)
        self.to_collection(front_wheel_sub_controller, curve_collection)

        back_wheel_controller = self.create_circle_curve(back_wheel_obj.dimensions.y / 2)
        self.to_collection(back_wheel_controller, curve_collection)

        back_wheel_sub_controller = self.create_rectangle_curve(back_wheel_obj.dimensions.y, back_wheel_obj.dimensions.y)
        self.to_collection(back_wheel_sub_controller, curve_collection)

        # コントローラの位置とスケールを決める
        car_body_obj = bpy.data.objects.get(car_parts.car_body)
        car_body_center = self.get_center_coords(car_body_obj)
        primary_controller_location = (-car_body_center.x, 0, -car_body_center.y)
        primary_controller_scale = (1 / primary_bone_length)

        front_wheel_controller_location = (0, half_wheel_thickness.x, 0)
        front_wheel_controller_scale = (1 / front_wheel_bone_length) * 2
        front_wheel_sub_controller_scale = (1 / front_wheel_bone_length) * 1.2

        back_wheel_controller_location = (0, 0, 0)
        back_wheel_controller_scale = (1 / back_wheel_bone_length) * 2

        back_wheel_sub_controller_scale = (1 / back_wheel_bone_length) * 1.2

        custom_shapes = {
            "Primary": (primary_controller, primary_controller_location, (90, 0, 0), primary_controller_scale),
            "Root": (root_controller, primary_controller_location, (90, 0, 0), primary_controller_scale),
            "FrontWheel_L": (front_wheel_controller, front_wheel_controller_location, (90, 0, 0), front_wheel_controller_scale),
            "FrontWheelSub_L": (front_wheel_sub_controller, (0, 0, 0), (90, 0, 0), front_wheel_sub_controller_scale),
            "BackWheel_L": (back_wheel_controller, back_wheel_controller_location, (90, 0, 0), back_wheel_controller_scale),
            "BackWheelSub_L": (back_wheel_sub_controller, (0, 0, 0), (90, 0, 0), back_wheel_sub_controller_scale),
        }

        # 作成したアーマチュアを選択し直して、ポーズモードに入る
        bpy.context.view_layer.objects.active = new_armature
        bpy.ops.object.mode_set(mode='POSE')

        # コントローラ(カスタムシェイプ)の設定
        for bone_name, (curve, location, rotation, scale) in custom_shapes.items():
            pose_bone = new_armature.pose.bones.get(bone_name)
            
            if pose_bone and curve:
                pose_bone.custom_shape = curve
                pose_bone.custom_shape_translation = location

                # 回転をラジアンに変換してから設定
                rotation_radians = tuple(math.radians(angle) for angle in rotation)
                pose_bone.custom_shape_rotation_euler = mathutils.Euler(rotation_radians)

                pose_bone.custom_shape_scale_xyz = (scale, scale, scale)

        curve_collection.hide_viewport = True

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
    
    def get_combined_dimensions(self):
        bpy.ops.object.select_all(action='SELECT')
        selected_objects = bpy.context.selected_objects

        min_bound = mathutils.Vector((float('inf'), float('inf'), float('inf')))
        max_bound = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))

        for obj in selected_objects:
            for vertex in obj.bound_box:
                world_vertex = obj.matrix_world @ mathutils.Vector(vertex)
                min_bound = mathutils.Vector((min(min_bound[i], world_vertex[i]) for i in range(3)))
                max_bound = mathutils.Vector((max(max_bound[i], world_vertex[i]) for i in range(3)))
        return max_bound - min_bound

    def create_circle_curve(self, radius):
        num_points = 32

        bpy.ops.object.add(type='CURVE', enter_editmode=False, align='WORLD')
        circle_curve = bpy.context.object
        circle_curve.name = "Circle"
        circle_curve.data.dimensions = '2D'

        circle_spline = circle_curve.data.splines.new(type='POLY')
        circle_spline.points.add(count=num_points - 1)

        for i, point in enumerate(circle_spline.points):
            angle = 2 * math.pi * i / num_points
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            point.co = (x, y, 0, 1)

        circle_spline.use_cyclic_u = True
        return circle_curve
    
    def create_rectangle_curve(self, width, height):
        bpy.ops.object.add(type='CURVE', enter_editmode=False, align='WORLD')
        rectangle_curve = bpy.context.object
        rectangle_curve.name = "Rectangle Curve"
        rectangle_curve.data.dimensions = '2D'

        rectangle_spline = rectangle_curve.data.splines.new(type='POLY')
        rectangle_spline.points.add(count=3) 

        rectangle_spline.points[0].co = (width / 2, height / 2, 0, 1)
        rectangle_spline.points[1].co = (-width / 2, height / 2, 0, 1)
        rectangle_spline.points[2].co = (-width / 2, -height / 2, 0, 1)
        rectangle_spline.points[3].co = (width / 2, -height / 2, 0, 1)

        rectangle_spline.use_cyclic_u = True
        return rectangle_curve

    def to_collection(self, target, collection):
        collection.objects.link(target)
        bpy.context.collection.objects.unlink(target)


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