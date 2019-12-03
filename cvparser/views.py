from django.shortcuts import render
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from JH_RestAPI import pagination


import requests
from utils.error_codes import ResponseCodes
from rest_framework.parsers import JSONParser
import json
from utils.generic_json_creator import create_response
from cvparser.models import Resume
from cvparser.serializer import ResumeSerializer

# Create your views here.

@csrf_exempt
@api_view(["GET", "POST"])
def resume_parser(request):
    if request.method == "GET":
        # query resume from db return json to the user
        user = request.user
        resumes = Resume.objects.filter(user=user).values()
        #all_resumes = Resume.objects.all()
        #apple_resumes = Resume.objects.filter(company='Apple').distinct('user')
        #resume_count = all_resumes.count()
        #android_resumes = Resume.objects.filter(summary__contains='android')
        resumes_list = ResumeSerializer(instance=resumes, many=True).data
        return JsonResponse(create_response(data=resumes_list), safe=False)
    elif request.method == "POST":
        body = request.data
        if 'resume' in body:
            post_data = body['resume']
            print('BEFORE CALL')
            response = requests.post('http://127.0.0.1:8002/api/parser/',
                                files=post_data, headers={'content-type': 'multipart/form-data'})
            print('CAME')                    
            json_res = json.loads(response.text)
            #fill the model
            resume = Resume()
            resume.user = request.user
            resume.contact = json_res['contact']
            resume.skills =  json_res['skills']
            resume.linkedin =  json_res['linkedin']
            resume.certifications =  json_res['certifications']
            resume.summary =  json_res['summary']
            resume.languages =  json_res['languages']
            resume.school = json_res['school']
            resume.degree = json_res['degree']
            resume.company = json_res['company']
            resume.position = json_res['position']
            resume.startdate = json_res['startdate']
            resume.enddate = json_res['enddate']
            
            resume.save()
            print(resume)
            resume = ResumeSerializer(instance=resume, many=False).data
            return JsonResponse(create_response(data=resume), safe=False)

        return JsonResponse(create_response(success=False, error_code=ResponseCodes.invalid_parameters), safe=False) 
    else:
        return JsonResponse(create_response(success=False, error_code=ResponseCodes.invalid_parameters), safe=False)    
