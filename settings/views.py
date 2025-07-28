from django.shortcuts import render

from rest_framework import generics, permissions
from .models import BrandAsset, ERPIntegration, Tracker
from .serializers import BrandAssetSerializer, ERPIntegrationSerializer, TrackerSerializer

class BrandAssetListCreateView(generics.ListCreateAPIView):
    queryset = BrandAsset.objects.all()
    serializer_class = BrandAssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ERPIntegrationListCreateView(generics.ListCreateAPIView):
    queryset = ERPIntegration.objects.all()
    serializer_class = ERPIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(synced_by=self.request.user)


class TrackerListCreateView(generics.ListCreateAPIView):
    queryset = Tracker.objects.all()
    serializer_class = TrackerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
