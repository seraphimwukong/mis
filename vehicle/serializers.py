from rest_framework import serializers
from .models import VehicleType, VehicleInfo, RepairOrder
#给前端的数据交换格式
class VehicleTypeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField() # 给前端下拉显示用
    class Meta:
        model = VehicleType
        fields = ['id', 'type_name', 'type_code', 'parent', 'full_name']

    def get_full_name(self, obj):
        return str(obj)

    def validate_parent(self, value):
        # 编辑时防自己选自己/选子孙
        if self.instance and value:
            if value.pk == self.instance.pk:
                raise serializers.ValidationError('不能选择自己')
        if value and value.parent:
            raise serializers.ValidationError('只能选择大类作为上级')
        return value


class VehicleInfoSerializer(serializers.ModelSerializer):
    # 写：传 vehicle_type: 3 (小类id)
    # 读：额外返回 vehicle_type_info: {type_name, type_code, parent_name} + plate_number
    vehicle_type_info = VehicleTypeSerializer(source='vehicle_type', read_only=True)

    class Meta:
        model = VehicleInfo
        fields = ['id', 'vehicle_type', 'vehicle_type_info','plate_number', 'vehicle_alias', 'vin','engine_model', 'engine_number', 'driver_name','tire_model_1', 'tire_model_2']

    def validate_vehicle_type(self, value):
        if value.parent is None and value.children.exists():
            raise serializers.ValidationError('请选择小类')
        return value


# 其他模块：写只传 vehicle: 5，读返回车牌
class RepairOrderSerializer(serializers.ModelSerializer):
    plate_number = serializers.CharField(source='vehicle.plate_number', read_only=True)
    class Meta:
        model = RepairOrder
        fields = ['id', 'vehicle', 'plate_number', 'task_name']