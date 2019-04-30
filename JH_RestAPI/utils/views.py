from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from utils.generic_json_creator import create_response
from .models import Agreement
from .serializers import AgreementSerializer
from django.views.decorators.http import require_GET

@require_GET
def agreements(request):
    agreements = Agreement.objects.all()
    slist = AgreementSerializer(instance=agreements, many=True).data
    return JsonResponse(create_response(data=slist), safe= False)

