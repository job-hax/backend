import uuid
import datetime
from django.utils import timezone
from enum import Enum
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination
from blog.models import Blog
from blog.models import Vote
from users.models import UserType
from users.serializers import UserTypeSerializer
from utils import utils
from utils.error_codes import ResponseCodes
from utils.generic_json_creator import create_response
from utils.utils import get_boolean_from_request, send_notification_email_to_admins
from .serializers import BlogSerializer
from .serializers import BlogSnippetSerializer

User = get_user_model()


class ActionType(Enum):
    none = 0
    upvote = 1
    downvote = -1
    view = 2


@csrf_exempt
@api_view(["GET", "PUT", "POST", "PATCH", "DELETE"])
def blogs(request):
    user_profile = request.user
    if request.method == "GET":
        if user_profile.user_type.name == 'Career Service' and get_boolean_from_request(request, 'waiting'):
            queryset = Blog.objects.filter(is_approved=False, is_publish=True, is_rejected=False, college=user_profile.college)
        elif request.user.user_type.name == 'Career Service' and request.GET.get('type', '') != '':
            queryset = Blog.objects.filter(Q(is_publish=True, is_rejected=False, is_approved=True) | Q(publisher_profile=request.user),
                publisher_profile__user_type__id=int(request.GET.get('type')), college=request.user.college)
        else:
            if user_profile.user_type.name == 'Career Service':
                student = get_boolean_from_request(request, 'student')
                if student:
                    user_type = UserType.objects.get(name='Student')
                else:
                    user_type = UserType.objects.get(name='Alumni')
                queryset = Blog.objects.filter(is_approved=True, is_publish=True, college=user_profile.college, user_types__in=[user_type])
            else:
                if user_profile.user_type.name == 'Public':
                    queryset = Blog.objects.filter(Q(is_approved=True, is_publish=True) | Q(publisher_profile=request.user),
                                                   Q(user_types__in=[user_profile.user_type])
                                                   | Q(publisher_profile__is_superuser=True))
                else:
                    queryset = Blog.objects.filter(Q(is_approved=True, is_publish=True) | Q(publisher_profile=request.user),
                                                   Q(user_types__in=[user_profile.user_type],college=user_profile.college)
                                                   | Q(publisher_profile__is_superuser=True))
        queryset = queryset.filter(publisher_profile__isnull=False)
        paginator = pagination.CustomPagination()
        blogs = paginator.paginate_queryset(queryset, request)
        serialized_blogs = BlogSnippetSerializer(
            instance=blogs, many=True, context={'user': request.user}).data
        return JsonResponse(create_response(data=serialized_blogs, paginator=paginator), safe=False)
    else:
        if not user_profile.user_type.blog_creation_enabled:
            return JsonResponse(create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                                safe=False)
        if request.method == "POST":
            body = request.data
            blog = Blog()
            blog.college = request.user.college
            blog.publisher_profile = request.user
            if 'header_image' in body:
                file = body['header_image']
                ext = file.name.split('.')[-1]
                filename = "%s.%s" % (uuid.uuid4(), ext)
                blog.header_image.save(filename, file, save=True)
            if 'title' in body:
                title = body['title']
                blog.title = title
            if 'content' in body:
                content = body['content']
                blog.content = content
            if 'snippet' in body:
                snippet = body['snippet'][:130] + '...'
                blog.snippet = snippet
            if 'is_publish' in body:
                is_publish = get_boolean_from_request(request, 'is_publish', 'POST')
                blog.is_publish = is_publish
            if request.user.user_type.name == 'Career Service':
                user_types = body['user_types'].split(',')
                blog.save()
                for type in user_types:
                    user_type = UserType.objects.get(pk=int(type))
                    blog.user_types.add(user_type)
                blog.is_approved = True
            else:
                blog.user_types.add(request.user.user_type)
                if blog.is_publish:
                    send_notification_email_to_admins('blog', blog.college.id)
                blog.is_approved = False

            blog.save()
            return JsonResponse(create_response(data={"id": blog.id}), safe=False)
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
            if 'is_publish' in body:
                blog.is_publish = get_boolean_from_request(request, 'is_publish', 'POST')
            if request.user.user_type.name == 'Career Service':
                user_types = body['user_types'].split(',')
                blog.user_types.clear()
                for type in user_types:
                    user_type = UserType.objects.get(pk=int(type))
                    blog.user_types.add(user_type)
                blog.is_approved = True
            else:
                if blog.is_publish:
                    send_notification_email_to_admins('blog', blog.college.id)
                blog.is_approved = False
            blog.updated_at = timezone.now()
            blog.save()

            return JsonResponse(create_response(data={"id": blog.id}), safe=False)
        elif request.method == "PATCH":
            if request.user.user_type.name == 'Career Service':
                body = request.data
                blog = Blog.objects.get(pk=body['blog_id'])
                approved = body['approved']
                blog.is_approved = approved
                blog.is_rejected = not approved
                blog.save()
                return JsonResponse(create_response(data=None), safe=False)
            else:
                return JsonResponse(
                    create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
                    safe=False)
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


@csrf_exempt
@api_view(["GET"])
def stats(request):
    if request.user.user_type.name == 'Career Service':
        days = request.GET.get('days', '30')
        response = {}
        user_types = UserType.objects.filter(Q(name='Career Service') | Q(name='Student') | Q(name='Alumni')).order_by(
            'id')
        for user_type in user_types:
            item = {}
            last_x_days_created = Blog.objects.filter(Q(is_publish=True, is_rejected=False, is_approved=True) | Q(publisher_profile=request.user),
                publisher_profile__user_type__id=int(user_type.id), college=request.user.college,
                                                             created_at__lte=datetime.datetime.today(),
                                       created_at__gt=datetime.datetime.today() - datetime.timedelta(days=int(days)))
            item['last_x_days_created'] = last_x_days_created.count()
            blogs = Blog.objects.filter(Q(is_publish=True, is_rejected=False, is_approved=True) | Q(publisher_profile=request.user),
                publisher_profile__user_type__id=int(user_type.id), college=request.user.college)
            item['view_count'] = blogs.aggregate(count=Coalesce(Sum('view_count'), 0))['count']
            item['upvote_count'] = Vote.objects.filter(blog__in=blogs, vote_type=True).count()
            item['downvote_count'] = Vote.objects.filter(blog__in=blogs, vote_type=False).count()
            response[user_type.name] = item
        return JsonResponse(create_response(data=response), safe=False)
    return JsonResponse(
        create_response(data=None, success=False, error_code=ResponseCodes.not_supported_user),
        safe=False)