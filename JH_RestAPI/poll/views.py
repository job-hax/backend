from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from utils.generic_json_creator import create_response
from .models import Poll, Item, Vote
from .serializers import PollSerializer, VoteSerializer
from django.db.models import Q


@csrf_exempt
@api_view(["POST"])
def vote(request, poll_pk):
    try:
        poll = Poll.objects.get(pk=poll_pk)
    except:
        return JsonResponse(create_response(None, False, 101), safe=False)

    body = request.data
    item_pk = body['item_id']
    if not item_pk:
        return JsonResponse(create_response(None, False, 102), safe=False)

    try:
        item = Item.objects.get(pk=item_pk)
    except:
        return JsonResponse(create_response(None, False, 103), safe=False)

    Vote.objects.create(
        poll=poll,
        ip=request.META['REMOTE_ADDR'],
        user=request.user,
        item=item,
    )

    return JsonResponse(create_response(None, True, 0), safe=False)

@csrf_exempt
@api_view(["GET"])
def polls(request):
    poll = Poll.objects.filter(~Q(vote__user=request.user))
    slist = PollSerializer(instance=poll, many=True).data
    return JsonResponse(create_response(slist, True, 0), safe= False)

@csrf_exempt
@api_view(["GET"])
def result(request, poll_pk):
    try:
        poll = Poll.objects.get(pk=poll_pk)
    except Poll.DoesNotExists:
        return JsonResponse(create_response(None, False, 101), safe=False)

    votes = Vote.objects.filter(poll=poll)

    return JsonResponse(create_response(VoteSerializer(instance=votes, many=True).data, True, 0), safe= False)