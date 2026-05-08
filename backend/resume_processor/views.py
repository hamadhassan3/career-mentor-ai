import os
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json


RESUME_PROCESSOR_API_BASE_URL = os.getenv('RESUME_PROCESSOR_API_BASE_URL')


def proxy_request(request, path):
    """
    Proxy requests to the resume processor microservice
    """
    if not RESUME_PROCESSOR_API_BASE_URL:
        return JsonResponse({'error': 'Resume processor service not configured'}, status=500)
    
    # Build the target URL
    target_url = f"{RESUME_PROCESSOR_API_BASE_URL.rstrip('/')}/{path}"
    
    # Prepare headers (exclude host and other proxy-specific headers)
    headers = {}
    for key, value in request.META.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').title()
            if header_name not in ['Host', 'X-Forwarded-For', 'X-Real-Ip']:
                headers[header_name] = value
    
    # Handle different HTTP methods
    try:
        if request.method == 'GET':
            response = requests.get(
                target_url, 
                params=request.GET.dict(),
                headers=headers,
                timeout=60
            )
        elif request.method == 'POST':
            # Check if it's multipart form data (file upload)
            if request.content_type and request.content_type.startswith('multipart/form-data'):
                # Forward files and form data
                files = {}
                data = {}
                
                for key, value in request.POST.items():
                    data[key] = value
                
                for key, file_obj in request.FILES.items():
                    files[key] = (file_obj.name, file_obj.read(), file_obj.content_type)
                
                response = requests.post(
                    target_url,
                    data=data,
                    files=files,
                    headers={k: v for k, v in headers.items() if k.lower() != 'content-type'},
                    timeout=60
                )
            else:
                # Forward JSON data - ensure Content-Type is set for JSON requests
                json_headers = headers.copy()
                if request.body and not json_headers.get('Content-Type'):
                    json_headers['Content-Type'] = 'application/json'
                
                response = requests.post(
                    target_url,
                    data=request.body,
                    headers=json_headers,
                    timeout=60
                )
        elif request.method == 'PUT':
            response = requests.put(
                target_url,
                data=request.body,
                headers=headers,
                timeout=60
            )
        elif request.method == 'DELETE':
            response = requests.delete(
                target_url,
                headers=headers,
                timeout=60
            )
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        # Forward the response
        django_response = HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers.get('content-type', 'application/json')
        )
        
        # Forward important headers
        for header in ['Content-Type', 'Cache-Control', 'ETag']:
            if header in response.headers:
                django_response[header] = response.headers[header]
        
        return django_response
        
    except requests.RequestException as e:
        return JsonResponse({'error': f'Service unavailable: {str(e)}'}, status=503)
    except Exception as e:
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def upload_resume(request):
    """Proxy resume upload to microservice"""
    return proxy_request(request, 'resumes/upload')


@csrf_exempt
@require_http_methods(["GET"])
def get_all_skills(request):
    """Proxy get all skills to microservice"""
    return proxy_request(request, 'skills/all')


@csrf_exempt
@require_http_methods(["GET"])
def get_it_skills(request):
    """Proxy get IT skills to microservice"""
    return proxy_request(request, 'skills/it')


@csrf_exempt
@require_http_methods(["GET"])
def get_soft_skills(request):
    """Proxy get soft skills to microservice"""
    return proxy_request(request, 'skills/soft')


@csrf_exempt
@require_http_methods(["GET"])
def get_languages(request):
    """Proxy get languages to microservice"""
    return proxy_request(request, 'skills/languages')


@csrf_exempt
@require_http_methods(["GET"])
def get_designations(request):
    """Proxy get designations to microservice"""
    return proxy_request(request, 'designations')


@csrf_exempt
@require_http_methods(["POST"])
def predict_skills(request):
    """Proxy predict skills to microservice"""
    return proxy_request(request, 'predict')


@csrf_exempt
@require_http_methods(["POST"])
def predict_single_skill(request):
    """Proxy predict single skill to microservice"""
    return proxy_request(request, 'predict_next_skill')