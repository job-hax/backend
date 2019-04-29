from django.shortcuts import render
from . import models
from .serializers import BlogSerializer
from .serializers import BlogSnippetSerializer
from django.http import JsonResponse
from utils.generic_json_creator import create_response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from utils.error_codes import ResponseCodes
from utils.logger import log
from JH_RestAPI import pagination


@csrf_exempt
@api_view(["GET"])
def blogs(request):
    queryset = models.Blog.objects.all()
    paginator = pagination.CustomPagination()
    blogs = paginator.paginate_queryset(queryset, request)
    serialized_blogs = BlogSnippetSerializer(instance=blogs, many=True, context={'user':request.user}).data
    return JsonResponse(create_response(data=serialized_blogs, paginator=paginator), safe=False) 

@csrf_exempt
@api_view(["GET"])
def blog(request, blog_pk):
    try:
        blog = models.Blog.objects.get(pk=blog_pk)
    except:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.blog_couldnt_found), safe=False)
    return JsonResponse(create_response(BlogSerializer(instance=blog, many=False, context={'user':request.user}).data), safe=False)   

@csrf_exempt
@api_view(["POST"])
def upvote(request, blog_pk):
    try:
        blog = models.Blog.objects.get(pk=blog_pk)
        vote = models.Vote.objects.filter(user=request.user, blog=blog)
        if len(vote) == 0:
            vote = models.Vote(user=request.user, blog=blog, vote_type=True)
        else:
            vote = vote[0]
            vote.vote_type = True    
        vote.save()
        return JsonResponse(create_response(data=BlogSnippetSerializer(instance=blog, many=False, context={'user':request.user}).data), safe=False)
    except Exception as e:
        log(e, 'e')
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.blog_couldnt_found), safe=False)

@csrf_exempt
@api_view(["POST"])
def downvote(request, blog_pk):
    try:
        blog = models.Blog.objects.get(pk=blog_pk)
        vote = models.Vote.objects.filter(user=request.user, blog=blog)
        if len(vote) == 0:
            vote = models.Vote(user=request.user, blog=blog, vote_type=False)
        else:
            vote = vote[0]
            vote.vote_type = False    
        vote.save()
        return JsonResponse(create_response(data=BlogSnippetSerializer(instance=blog, many=False, context={'user':request.user}).data), safe=False)
    except Exception as e:
        log(e, 'e')
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.blog_couldnt_found), safe=False)

@csrf_exempt
@api_view(["POST"])
def view(request, blog_pk):
    try:
        blog = models.Blog.objects.get(pk=blog_pk)
        blog.view_count = blog.view_count+1
        blog.save()
        return JsonResponse(create_response(data=None), safe=False)
    except:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.blog_couldnt_found), safe=False)        