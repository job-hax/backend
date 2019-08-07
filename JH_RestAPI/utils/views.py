from django.http import JsonResponse
from django.views.decorators.http import require_GET

from utils.generic_json_creator import create_response
from .models import Agreement, Country, State
from .serializers import AgreementSerializer, CountrySerializer, StateSerializer


@require_GET
def agreements(request):
    agreements = Agreement.objects.all()
    slist = AgreementSerializer(instance=agreements, many=True).data
    response = {}
    for s in slist:
        response[s['key']] = s
    return JsonResponse(create_response(data=response), safe= False)


@require_GET
def countries(request):
    countries = Country.objects.all()
    slist = CountrySerializer(instance=countries, many=True).data
    return JsonResponse(create_response(data=slist), safe= False)


@require_GET
def states(request, country_pk):
    states = State.objects.filter(country__pk=country_pk)
    slist = StateSerializer(instance=states, many=True).data
    return JsonResponse(create_response(data=slist), safe=False)