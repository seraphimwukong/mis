from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Create your models here.
# 防乱填：正则先拦一波
code_validator = RegexValidator(r'^[A-Z0-9]+$', '类型代码只允许大写字母+数字')
# plate_validator = RegexValidator(r'^[\u4e00-\u9fa5][A-Z][A-Z0-9]{5,6}$', '车牌格式错误，如京A12345')
vin_validator = RegexValidator(r'^[A-HJ-NPR-Z0-9]{17}$', '车架号为17位字母数字(不含IOQ)')
class VehicleType(models.Model):
    """表1：车辆类型，支持大类-小类"""
    type_name = models.CharField(max_length=50, verbose_name="车辆类型")
    type_code = models.CharField(max_length=20, unique=True, validators=[code_validator], verbose_name="类型代码")
    # 大类parent为空，小类parent指向大类
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',verbose_name="上级大类")
    class Meta:
        db_table = 'vehicle_type'
        verbose_name = '车辆类型'
        verbose_name_plural = '车辆类型'
    def clean(self) -> None:
        # 防自己选自己
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({'parent': '不能选择自己作为上级'})
        # 防循环 A->B->A
        if self.pk and self.parent:
            p = self.parent
            while p:
                if p.pk == self.pk:
                    raise ValidationError({'parent': '存在循环引用'})
                p = p.parent
        # 防乱建层级：只允许两级
        if self.parent and self.parent.parent_id:
            raise ValidationError({'parent': '只支持大类-小类两级'})

        def save(self, *args, **kwargs):
            self.full_clean()  # 不用admin后必须加，否则clean不执行
            super().save(*args, **kwargs)

        def __str__(self):
            return f"{self.type_name}({self.type_code})"

class VehicleInfo(models.Model):
    """表2：车辆信息"""
    # 外键关联小类id，MySQL生成 vehicle_type_id INT + 外键约束
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT, related_name='vehicles', verbose_name="车辆类型")
    plate_number = models.CharField(max_length=20, unique=True, verbose_name="车牌号")
    vehicle_alias = models.CharField(max_length=50, blank=True, null=True, verbose_name="车辆别名")
    vin = models.CharField(max_length=50, unique=True, validators=[vin_validator], verbose_name="车架号")
    engine_model = models.CharField(max_length=50, verbose_name="发动机型号")
    engine_number = models.CharField(max_length=50, unique=True, verbose_name="发动机号")
    driver_name = models.CharField(max_length=50, verbose_name="司机姓名")
    tire_model_1 = models.CharField(max_length=30, verbose_name="轮胎型号1")
    tire_model_2 = models.CharField(max_length=30, blank=True, null=True, verbose_name="轮胎型号2")
    class Meta:
        db_table = 'vehicle_info'

    def clean(self):
        # 防乱挂：只能挂小类，不能直接挂大类
        if not self.vehicle_type_id:
            return  # 还没选类型，交给字段必填去拦，这里直接放行
        vt = self.vehicle_type  # 只查一次，避免重复查库
        # 大类特征：parent为空 且 自己有孩子
        if vt.parent_id is None and vt.children.exists():
            raise ValidationError({'vehicle_type': '请选择小类，不能直接选大类'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.plate_number


class RepairOrder(models.Model):
    """其他模块引用示例：关联id，展示车牌"""
    vehicle = models.ForeignKey(VehicleInfo, on_delete=models.PROTECT, related_name='repair_orders',verbose_name="关联车辆")
    task_name = models.CharField(max_length=100, verbose_name="任务名称")

    class Meta:
        db_table = 'repair_order'
