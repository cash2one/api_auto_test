# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import time
import string
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
from models import *
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from api.models import ApiInfo, ApiTest
from project.models import Project
from dashboard.models import ApiTestExecuteLog


# Create your views here.
def view(request):
    return render(request, 'task/view.html', {'tasklist': get_task_list()})


def get_task_list():
    task_list = []
    for task in TimingTask.objects.all():
        task_dict = dict({})
        start_timeStamp = task.start_time
        start_timeArray = time.localtime(start_timeStamp)
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", start_timeArray)
        end_timeStamp = task.end_time
        end_timeArray = time.localtime(end_timeStamp)
        end_time = time.strftime("%Y-%m-%d %H:%M:%S", end_timeArray)
        test = task.between_time

        if task.between_time >= 60 * 60 * 24 * 7:
            thetime = test / (60 * 60 * 24 * 7)
            between_time = '%d' % thetime + '周'
        elif task.between_time >= 60 * 60 * 24:
            thetime = test / (60 * 60 * 24)
            between_time = '%d' % thetime + '天'
        elif task.between_time >= 60 * 60:
            thetime = test / (60 * 60)
            between_time = '%d' % thetime + '小时'
        elif task.between_time >= 60:
            thetime = test / 60
            between_time = '%d' % thetime + '分钟'
        else:
            between_time = '%d' % test + '秒'

        task_dict['id'] = task.id
        task_dict['name'] = task.name
        task_dict['type'] = task.type
        task_dict['between_time'] = between_time
        task_dict['run_time'] = task.run_time
        task_dict['start_time'] = start_time
        task_dict['end_time'] = end_time
        task_dict['global_value'] = task.global_value
        task_dict['state'] = task.state
        task_list.append(task_dict)

    return task_list


def add_task(request):
    if request.method == "POST":
        try:
            data = request.POST
            type_data = 1 if data.get('input_type') == '定时' else 2
            state_data = 1 if data.get('input_state') == '开启' else 2
            run_time = ''
            between_time = 0
            minute = ''
            hour = ''

            if type_data == 1:
                run_time = data.get('input_runtime')
                if len(run_time.split(':')) > 1:
                    minute = '%s' % run_time.split(':')[-1]
                    hour = '%s' % run_time.split(':')[0]
            else:
                between_time = int(data.get('input_between'))
                if data.get('input_between_unit') == '分钟':
                    between_time *= 60
                    minute = '*/%s' % data.get('input_between')
                    hour = '*'
                elif data.get('input_between_unit') == '小时':
                    between_time = between_time * 60 * 60
                    hour = '*/%s' % data.get('input_between')
                    minute = '*'
                elif data.get('input_between_unit') == '天':
                    between_time = between_time * 60 * 60 * 24
                    hour = '*/%s' % int(data.get('input_between')) * 24

            starttime_arr = time.strptime(data.get('input_starttime'), "%Y-%m-%d %H:%M:%S")
            starttime_int = int(time.mktime(starttime_arr))
            endtime_arr = time.strptime(data.get('input_endtime'), "%Y-%m-%d %H:%M:%S")
            endtime_int = int(time.mktime(endtime_arr))

            if data.get('input_task_id'):
                task = TimingTask.objects.get(id=data.get('input_task_id'))
                task.name = data.get('input_name')
                task.type = type_data
                task.between_time = between_time
                task.run_time = run_time
                task.start_time = starttime_int
                task.end_time = endtime_int
                task.global_value = data.get('input_global_value')
                task.state = state_data
                task.minute = minute
                task.hour = hour
                task.save()
            else:
                task = TimingTask(name=data.get('input_name'), type=type_data,
                                  between_time=between_time, run_time=run_time,
                                  start_time=starttime_int, end_time=endtime_int,
                                  global_value=data.get('input_global_value'), state=state_data,
                                  minute=minute, hour=hour)
                task.save()

            crontab = CrontabSchedule.objects.get_or_create(minute=task.minute, hour=task.hour)[0]
            crontab.save()
            periodic_task = PeriodicTask.objects.get_or_create(name=task.name)[0]
            periodic_task.task = 'task.tasks.api_test_time_task'
            periodic_task.crontab = crontab
            periodic_task.args = [int(task.id)]
            if task.state == 1:
                periodic_task.enable = True
            elif task.state == 2:
                periodic_task.enable = False

            periodic_task.save()

            context = {'flag': 'Success'}
        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}
    return redirect('/task/')


def delete_task(request):
    print '点击了删除按钮'
    if request.method == "POST":
        try:
            data = request.POST
            task = TimingTask.objects.get(id=data.get('task_id'))
            task.delete()

            periodic_task = PeriodicTask.objects.get(name=task.name)
            periodic_task.delete()

            context = {'flag': 'Success'}
        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return render(request, 'task/view.html', {'task_list': get_task_list()})


def task_detail(request):
    data = request.GET
    task = TimingTask.objects.get(id=data.get('task_id'))
    api_test_id_list = [x for x in task.api_test_list.split(',')]
    if len(api_test_id_list) < 1:
        api_test_id_list = api_test_id_list
    else:
        if api_test_id_list[0] == '':
            api_test_id_list = []
    project_list = Project.objects.all()
    api_test_list = list()

    for test_id in api_test_id_list:
        try:
            api_test = ApiTest.objects.get(id=test_id)
            api_test_list.append(api_test)

        except Exception, e:
            if test_id in api_test_id_list:
                api_test_id_list.remove(test_id)
                str_api_test_list = ','.join(api_test_id_list)
                task.api_test_list = str_api_test_list
                task.save()

    need_api_test_list = []
    for api_test in api_test_list:
        need_api_test_dict = dict({})
        project_id = api_test.project_id
        project = Project.objects.get(id=project_id)

        need_api_test_dict['project_name'] = project.name
        need_api_test_dict['api_name'] = api_test.api_info.name
        need_api_test_dict['id'] = api_test.id
        need_api_test_dict['name'] = api_test.name
        need_api_test_dict['test_method'] = api_test.test_method
        need_api_test_dict['project_id'] = api_test.project_id
        need_api_test_dict['param'] = api_test.param
        need_api_test_dict['post_data'] = api_test.post_data
        need_api_test_dict['desc'] = api_test.desc
        need_api_test_dict['task_type'] = api_test.task_type
        need_api_test_dict['total_run'] = api_test.total_run
        need_api_test_dict['success_run'] = api_test.success_run
        need_api_test_dict['fail_run'] = api_test.fail_run
        need_api_test_dict['status'] = api_test.status
        need_api_test_list.append(need_api_test_dict)

    return render(request, 'task/detail.html',
                  {'api_test_list': need_api_test_list,
                   'task': task,
                   'project_list': project_list})


def result(request):
    data = request.GET

    api_test = ApiTest.objects.get(id=data.get('test_id'))
    api_log_list = ApiTestExecuteLog.objects.filter(api_id=api_test.api_info.id, project_id=api_test.project_id,
                                                    test_id=api_test.id).order_by('-execute_time')


    print api_log_list
    return render(request, 'task/result.html',
                  {'api_log_list': api_log_list})


def add_api_test(request):
    data = request.POST
    task_id = data.get('input_task_id')
    api_test_id = data.get('input_api_test')
    task = TimingTask.objects.get(id=task_id)
    api_test_id_list = task.api_test_list.split(',')
    if task.api_test_list == '':
        task.api_test_list = api_test_id
        task.save()
    else:
        if api_test_id not in api_test_id_list:
            api_test_id_list.append(api_test_id)
            str_api_test_list = ','.join(api_test_id_list)
            task.api_test_list = str_api_test_list
            task.save()

    return redirect('/task/detail?task_id=' + task_id)


def delete_api_test(request):
    print '点击了删除按钮'
    if request.method == "POST":
        try:
            data = request.POST
            task_id = data.get('task_id')
            api_test_id = data.get('api_test_id')
            task = TimingTask.objects.get(id=task_id)
            api_test_id_list = [x for x in task.api_test_list.split(',')]
            if api_test_id in api_test_id_list:
                api_test_id_list.remove(api_test_id)
                str_api_test_list = ','.join(api_test_id_list)
                task.api_test_list = str_api_test_list
                task.save()

                context = {'flag': 'Success'}
            else:
                context = {"flag": 'Error', "context": '未找到此用例'}
        except Exception, e:
            context = {"flag": 'Error', "context": str(e)}

        return HttpResponse(json.dumps(context))

    return render(request, 'task/detail.html', {'task_list': get_task_list()})


def change_select_project(request):
    try:
        data = request.POST
        project_id = data.get('project_id')
        api_list = ApiInfo.objects.filter(project_id=project_id)
        need_list = []
        for api in api_list:
            need_api = dict({})
            need_api['name'] = api.name
            need_api['id'] = api.id
            need_list.append(need_api)

        context = {'flag': 'Success', 'api_list': need_list}

    except Exception, e:
        context = {"flag": 'Error', "context": str(e)}
    return HttpResponse(json.dumps(context))


def change_select_api(request):
    try:
        data = request.POST
        api_id = data.get('api_id')
        api_test_list = ApiTest.objects.filter(api_info=api_id)
        need_list = []
        for api_test in api_test_list:
            need_api_test = dict({})
            need_api_test['name'] = api_test.name
            need_api_test['id'] = api_test.id
            need_list.append(need_api_test)

        context = {'flag': 'Success', 'api_test_list': need_list}
    except Exception, e:
        context = {"flag": 'Error', "context": str(e)}

    return HttpResponse(json.dumps(context))


# 计算皮尔逊相关度：
def pearson(p, q):
    # 只计算两者共同有的
    same = 0
    for i in p:
        if i in q:
            same += 1

    n = same
    # 分别求p，q的和
    sumx = sum([p[i] for i in range(n)])
    sumy = sum([q[i] for i in range(n)])
    # 分别求出p，q的平方和
    sumxsq = sum([p[i] ** 2 for i in range(n)])
    sumysq = sum([q[i] ** 2 for i in range(n)])
    # 求出p，q的乘积和
    sumxy = sum([p[i] * q[i] for i in range(n)])
    # print sumxy
    # 求出pearson相关系数
    up = sumxy - sumx * sumy / n
    down = ((sumxsq - pow(sumxsq, 2) / n) * (sumysq - pow(sumysq, 2) / n)) ** .5
    # 若down为零则不能计算，return 0
    if down == 0:
        return 0
    r = up / down
    return r
