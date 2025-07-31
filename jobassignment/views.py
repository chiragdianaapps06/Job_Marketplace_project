from django.shortcuts import render
from rest_framework import viewsets
from .models import Job, Milestone
from .serialisers import JobSerializer, MilestoneSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


def home(request):
    return "hello" 

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

 



class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]


    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        milestone = self.get_object()
        if milestone.job.freelancer == request.user:
            milestone.is_completed_by_freelancer = True
            milestone.save()
            return Response({"status": "Milestone completed!"}, status=status.HTTP_200_OK)
        return Response({"error": "You are not assigned to this job!"}, status=status.HTTP_400_BAD_REQUEST)
