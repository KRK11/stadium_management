'''
**************************************************
@File   ：stadium_management -> court_views
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/25 18:57
**************************************************
'''

from django.db import connection
import web.models
from web.models import court, status, online
from django.http import JsonResponse


def court_insert(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=1"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    id = request.GET.get('id')
    location = request.GET.get('location')
    service_start_time = request.GET.get('start')
    service_end_time = request.GET.get('end')
    try:
        crt = court.objects.get(id=id)
    except court.DoesNotExist:
        crt = court(id=id, location=location,
                    service_start_time=service_start_time,
                    service_end_time=service_end_time)
        crt.save()
        return JsonResponse({'status':1})
    return JsonResponse({'status':0})


def court_select(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}'"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    sel = request.GET.get('location')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]

    msg = []
    arr = []
    sql = f"select * from court where location='{sel}'"
    result = court.objects.raw(sql)
    for i in result:
        sql = f"select * from status where court_id='{i.id}'" \
              f"and occupy_year='{time[0]}' " \
              f"and occupy_month='{time[1]}' " \
              f"and occupy_date='{time[2]}'"
        content = status.objects.raw(sql)
        free = [0 for i in range(24)]
        for j in content:
            free[j.occupy_hour] = 1
        msg.append({'id':i.id,'location':i.location,
                    'start': i.service_start_time,
                    'end': i.service_end_time})
        arr.append(free)
    return JsonResponse({'msg':msg,'data':arr})


def court_modify(request):
    try:
        crt = court.objects.get(id=request.GET.get('id'))
    except web.models.customer.DoesNotExist:
        return JsonResponse({'status':0})
    if request.GET.get('location'):
        crt.location = request.GET.get('location')
    if request.GET.get('start'):
        crt.service_start_time = request.GET.get('start')
    if request.GET.get('end'):
        crt.service_end_time = request.GET.get('end')
    crt.save()
    return JsonResponse({'status':1})


def court_delete(request):
    id = request.GET.get('id')
    try:
        with connection.cursor() as cur:
            sql = f"delete from court where id='{id}'"
            cur.execute(sql)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 0})
    return JsonResponse({'status': 1})
