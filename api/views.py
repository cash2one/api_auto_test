# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
import json
from models import *
from datetime import datetime
from test_executor.test_executor import TestExecutor
# Create your views here.


def view(request):
    return render(request=request,template_name='api/view.html')


def detail_view(request, project_id, api_id):
    print api_id

    api_info = ApiInfo.objects.get_or_create(id=api_id)[0]
    print api_info.name

    param_list = CommonRequestParam.objects.all()
    resp_header_list = ResponseHeader.objects.all()
    resp_body_list = ResponseBody.objects.all()
    key_type_list = KeyType.objects.all()
    default_type = key_type_list[0]
    # type_rule_list = TypeRule.objects.filter(type=default_type)
    api_test_list = ApiTest.objects.all()
    api_test_method_list = ApiTestMethod.objects.all()
    api_test_task_type_list = ApiTestTaskType.objects.all()

    return render(request=request,template_name='api/detail_view.html',context={
        'api_info': api_info,
        'api_id': api_id,
        'name': 'API_DETAIL',
        'param_list': param_list,
        'resp_header_list': resp_header_list,
        'resp_body_list': resp_body_list,
        'key_type_list': key_type_list,
        # 'type_rule_list': type_rule_list,
        'api_test_list': api_test_list,
        'api_test_method_list': api_test_method_list,
        'api_test_task_type_list': api_test_task_type_list
    })


def add_request_param(request, project_id, api_id):

    if request.method == "POST":
        try:
            data = request.POST
            api_id = data.get('api_id')
            name = data.get('name')
            value = data.get('value')
            position = data.get('position')
            type = data.get('type')
            url_encode = data.get('url_encode')

            api_info = ApiInfo.objects.get_or_create(name='cm_test_api')[0]

            request_param = CommonRequestParam(api_info=api_info,key=name,value=value,position=position,type=type,url_encode=url_encode)
            request_param.save()
            param_id = request_param.id

            context = {'flag': 'Success', 'id': param_id}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def change_request_param(request, project_id, api_id):

    if request.method == "POST":
        try:
            data = request.POST
            param_id = data.get('param_id')
            name = data.get('key')
            value = data.get('value')
            position = data.get('position')
            type = data.get('type')
            url_encode = data.get('url_encode')

            request_param = CommonRequestParam.objects.get_or_create(id=param_id)[0]
            request_param.key = name
            request_param.value = value
            request_param.position = position
            request_param.type = type
            request_param.url_encode = url_encode
            request_param.save()

            context = {'flag': 'Success', 'id': param_id}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def delete_request_param(request, project_id, api_id):
    print '==================== python delete ===================='
    id = request.POST['id']
    model = CommonRequestParam.objects.get(id=id)
    model.delete()
    return HttpResponse()


def add_resp_header(request, project_id, api_id):
    if request.method == "POST":
        try:
            data = request.POST
            api_id = data.get('api_id')
            key = data.get('key')
            value = data.get('value')

            api_info = ApiInfo.objects.get_or_create(name='cm_test_api')[0]
            resp = Response.objects.get_or_create(api_info=api_info)[0]

            resp_header = ResponseHeader(response=resp,key=key,value=value)
            resp_header.save()

            resp_header_id = resp_header.id

            context = {'flag': 'Success', 'id': resp_header_id}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def change_resp_header(request, project_id, api_id):
    if request.method == "POST":
        try:

            data = request.POST
            header_id = data.get('header_id')
            key = data.get('key')
            value = data.get('value')

            resp_header = ResponseHeader.objects.get_or_create(id=header_id)[0]
            resp_header.key = key
            resp_header.value = value
            resp_header.save()

            context = {'flag': 'Success', 'header_id': header_id}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def delete_resp_header(request, project_id, api_id):

    print '==================== python delete header ===================='
    id = request.POST['header_id']
    model = ResponseHeader.objects.get(id=id)
    model.delete()
    return HttpResponse()


def select_resp_body_type(request, project_id, api_id):

    if request.method == "POST":
        try:

            type_name = request.POST['type_name']
            model_type = KeyType.objects.get(name=type_name)
            type_rule_list = TypeRule.objects.filter(type=model_type).values('rule')
            type_rule_list = list(type_rule_list)
            list_json = json.dumps(type_rule_list)

            context = {'flag': 'Success', 'type_rule_list': list_json}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def add_resp_body(request, project_id, api_id):
    if request.method == "POST":
        try:
            data = request.POST
            key = data.get('key')
            path = data.get('path')
            type = data.get('type')
            type_rule = data.get('type_rule')

            api_info = ApiInfo.objects.get(id=api_id)
            resp = Response.objects.get_or_create(api_info=api_info)[0]

            resp_body = ResponseBody(response=resp,key=key,path=path,type=type,type_rule=type_rule)
            resp_body.save()

            resp_body_id = resp_body.id

            context = {'flag': 'Success', 'id': resp_body_id}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def change_resp_body(request, project_id, api_id):
    if request.method == "POST":
        try:

            data = request.POST
            body_id = data.get('body_id')
            key = data.get('key')
            path = data.get('path')
            type = data.get('type')
            type_rule = data.get('type_rule')

            resp_body = ResponseBody.objects.get_or_create(id=body_id)[0]
            resp_body.key = key
            resp_body.path = path
            resp_body.type = type
            resp_body.type_rule = type_rule
            resp_body.save()

            context = {'flag': 'Success', 'body_id': body_id}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def delete_resp_body(request, project_id, api_id):

    print '==================== python delete header ===================='
    id = request.POST['body_id']
    model = ResponseBody.objects.get(id=id)
    model.delete()
    return HttpResponse()


def add_api_test(request, project_id, api_id):
    if request.method == "POST":
        try:
            data = request.POST
            name = data.get('name')
            param = data.get('param')
            method = data.get('method')
            post_data = data.get('post_data')
            task_type = data.get('task_type')

            api_info = ApiInfo.objects.get_or_create(name='cm_test_api')[0]

            api_test = ApiTest(api_info=api_info,name=name,param=param,test_method=method,task_type=task_type,project_id=project_id,post_data=post_data)
            api_test.save()

            api_test_id = api_test.id

            context = {'flag': 'Success', 'id': api_test_id}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def change_api_test(request, project_id, api_id):
    if request.method == "POST":
        try:

            data = request.POST
            api_test_id = data.get('api_test_id')
            name = data.get('name')
            param = data.get('param')
            method = data.get('method')
            post_data = data.get('post_data')
            task_type = data.get('task_type')

            api_test = ApiTest.objects.get_or_create(id=api_test_id)[0]
            api_test.name = name
            api_test.param = param
            api_test.post_data = post_data
            api_test.method = method
            api_test.task_type = task_type
            api_test.save()

            context = {'flag': 'Success', 'api_test_id': api_test_id}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def delete_api_test(request, project_id, api_id):

    print '==================== python delete header ===================='
    id = request.POST['api_test_id']
    model = ApiTest.objects.get(id=id)
    model.delete()
    return HttpResponse()


def change_api_base_info(request, project_id, api_id):
    if request.method == "POST":
        try:

            data = request.POST
            api_id = data.get('api_id')
            name = data.get('name')
            request_method = data.get('request_method')
            validate_method = data.get('validate_method')
            url = data.get('url')
            scene = data.get('scene')
            desc = data.get('desc')
            overtime = data.get('overtime')
            current_date = datetime.now().strftime('%Y-%m-%d')

            api_info = ApiInfo.objects.get_or_create(id = api_id)[0]
            api_info.name = name
            api_info.method = request_method
            api_info.validate_method = validate_method
            api_info.overtime = overtime
            api_info.url = url
            api_info.scene = scene
            api_info.description = desc
            api_info.modify_recently = current_date
            api_info.save()

            context = {'flag': 'Success', 'modify_recently': current_date}

        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return HttpResponse()


def execute_api_test(request, project_id, api_id):

    if request.method == 'GET':
        data = request.GET
        test_id = data.get('testid')

        test_executor = TestExecutor(test_id=test_id)
        api_test = ApiTest.objects.get(id=test_id)
        success_run = api_test.success_run
        total_run = api_test.total_run
        fail_run = api_test.fail_run
        total_run  += 1

        context = test_executor.send_request()
        if context.get('status'):
            # 校验成功
            success_run += 1

        else:
            # 校验失败
            fail_run += 1

        api_test.success_run = success_run
        api_test.total_run = total_run
        api_test.fail_run = fail_run
        api_test.save()

        context['total_run'] = total_run
        context['fail_run'] = fail_run
        context['success_run'] = success_run

        return HttpResponse(json.dumps(context))

    return HttpResponse()