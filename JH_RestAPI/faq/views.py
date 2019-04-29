from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from utils.generic_json_creator import create_response
from .models import Faq
from .serializers import FaqSerializer
from django.views.decorators.http import require_GET

@require_GET
def faqs(request):
    faq = Faq.objects.filter(is_published=True)
    slist = FaqSerializer(instance=faq, many=True).data
    return JsonResponse(create_response(slist), safe= False)
