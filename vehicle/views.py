from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets
from .models import VehicleType, VehicleInfo
from .serializers import VehicleTypeSerializer, VehicleInfoSerializer

class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.select_related('parent').prefetch_related('children').all()
    serializer_class = VehicleTypeSerializer
    filterset_fields = ['parent'] # ?parent__isnull=true 查大类，?parent=1 查该大类小类

class VehicleInfoViewSet(viewsets.ModelViewSet):
    queryset = VehicleInfo.objects.select_related('vehicle_type__parent').all()
    serializer_class = VehicleInfoSerializer
    filterset_fields = ['vehicle_type', 'plate_number']
    search_fields = ['plate_number', 'vin', 'driver_name']

