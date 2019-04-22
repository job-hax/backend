from django.shortcuts import render
from . import models
from .serializers import BlogSerializer
from .serializers import BlogSnippetSerializer
from django.http import JsonResponse
from utils.generic_json_creator import create_response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@csrf_exempt
@api_view(["GET"])
def blogs(request):
    queryset = models.Blog.objects.all()
    return JsonResponse(create_response(BlogSnippetSerializer(instance=queryset, many=True).data, True, 0), safe=False)

@csrf_exempt
@api_view(["GET"])
def blog(request, blog_pk):
    try:
        blog = models.Blog.objects.get(pk=blog_pk)
    except:
        return JsonResponse(create_response(None, False, 104), safe=False)
    return JsonResponse(create_response(BlogSerializer(instance=blog, many=False).data, True, 0), safe=False)    


