import uuid
from datetime import datetime
from enum import Enum

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination
from blog.models import Blog
from blog.models import Vote
from users.models import Profile
from utils import utils
from utils.error_codes import ResponseCodes
from utils.generic_json_creator import create_response
from .serializers import BlogSerializer
from .serializers import BlogSnippetSerializer


class ActionType(Enum):
    none = 0
    upvote = 1
    downvote = -1
    view = 2


@csrf_exempt
@api_view(["GET", "PUT", "POST", "DELETE"])
def blogs(request):
    if request.method == "GET":
        mine = request.GET.get('mine')
        if mine is None:
            queryset = Blog.objects.filter(Q(is_approved=True) | Q(publisher_profile=request.user))
        else:
            queryset = Blog.objects.filter(publisher_profile=request.user)
        paginator = pagination.CustomPagination()
        blogs = paginator.paginate_queryset(queryset, request)
        serialized_blogs = BlogSnippetSerializer(
            instance=blogs, many=True, context={'user': request.user}).data
        return JsonResponse(create_response(data=serialized_blogs, paginator=paginator), safe=False)
    elif request.method == "POST":
        body = request.data
        file = body['header_image']
        ext = file.name.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)

        title = body['title']
        content = body['content']
        snippet = body['snippet'][:130] + '...'
        publish = body['publish']
        publisher_profile = Profile.objects.get(user=request.user)

        blog = Blog(title=title, snippet=snippet, content=content, publisher_profile=publisher_profile, is_published=publish)
        blog.header_image.save(filename, file, save=True)
        blog.save()
        return JsonResponse(create_response(data=None), safe=False)
    elif request.method == "PUT":
        body = request.data
        blog = Blog.objects.get(pk=body['blog_id'], publisher_profile=request.user)
        if 'title' in body:
            blog.title = body['title']
        if 'content' in body:
            blog.content = body['content']
            blog.snippet = body['snippet'][:130] + '...'
        if 'header_image' in body:
            file = body['header_image']
            ext = file.name.split('.')[-1]
            filename = "%s.%s" % (uuid.uuid4(), ext)
            blog.header_image.save(filename, file, save=True)
        if 'publish' in body:
            blog.is_published = body['publish']
        blog.update_date = datetime.now()
        blog.save()
        return JsonResponse(create_response(data=None), safe=False)
    elif request.method == "DELETE":
        body = request.data
        blog = Blog.objects.get(pk=body['blog_id'], publisher_profile=request.user)
        blog.delete()
        return JsonResponse(create_response(data=None), safe=False)


@csrf_exempt
@api_view(["GET"])
def blog(request, blog_pk):
    blog = Blog.objects.get(pk=blog_pk)
    return JsonResponse(create_response(BlogSerializer(instance=blog, many=False, context={'user': request.user}).data),
                        safe=False)


def do_action(request, blog_pk, type):
    body = request.data
    if 'recaptcha_token' in body and utils.verify_recaptcha(None, body['recaptcha_token'],
                                                            'blog_stats') == ResponseCodes.verify_recaptcha_failed:
        return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.verify_recaptcha_failed),
                            safe=False)

    blog = Blog.objects.get(pk=blog_pk)
    if type == ActionType.view:
        blog.view_count = blog.view_count + 1
        blog.save()
    else:
        if type == ActionType.none:
            Vote.objects.filter(user=request.user, blog=blog).delete()
        else:
            vote, new = Vote.objects.get_or_create(user=request.user, blog=blog)
            if type == ActionType.upvote:
                vote.vote_type = True
            elif type == ActionType.downvote:
                vote.vote_type = False
            vote.save()
    return JsonResponse(create_response(data=None))


@csrf_exempt
@api_view(["POST"])
def vote(request, blog_pk):
    action = request.data['action']
    return do_action(request, blog_pk, ActionType(action))


@csrf_exempt
@api_view(["POST"])
def view(request, blog_pk):
    return do_action(request, blog_pk, ActionType.view)
