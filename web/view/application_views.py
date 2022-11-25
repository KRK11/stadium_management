'''
**************************************************
@File   ：stadium_management -> request_views
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/25 22:49
**************************************************
'''

from django.db import connection
import web.models
from web.models import customer,administrator, status, online, application
from django.http import JsonResponse
from web.view import status_views


def application_insert(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=0"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    court_id = request.GET.get('id')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    hour = request.GET.get('length')
    if not hour:
        hour = 1
    else:
        hour = int(hour)
    arr = status_views.status_show(time, court_id)
    for i in range(time[3], min(time[3] + hour, 24)):
        if arr[i]: return JsonResponse({'status': 0})
        app = application(court_id=court_id, customer=customer,
                     occupy_year=time[0], occupy_month=time[1],
                     occupy_date=time[2], occupy_hour=i)
        app.save()
    return JsonResponse({'status': 1})


def application_delete(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=0"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    court_id = request.GET.get('id')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    sql = f"select * from application where " \
          f"customer='{content[0].id}' and" \
          f"court_id='{court_id}'" \
          f"occupy_year='{time[0]}'" \
          f"occupy_month='{time[1]}'" \
          f"occupy_date='{time[2]}'" \
          f"occupy_hour='{time[3]}'"
    result = application.objects.raw(sql)
    if not result: return JsonResponse({'status':0})
    with connection.cursor() as cur:
        cur.execute(sql)
    return JsonResponse({'status': 1})


def application_reject(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=1"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    court_id = request.GET.get('id')
    customer = request.GET.get('customer')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    sql = f"select * from application where " \
          f"customer='{customer}' and" \
          f"court_id='{court_id}'" \
          f"occupy_year='{time[0]}'" \
          f"occupy_month='{time[1]}'" \
          f"occupy_date='{time[2]}'" \
          f"occupy_hour='{time[3]}'"
    with connection.cursor() as cur:
        cur.execute(sql)
    return JsonResponse({'status':1})


def application_process(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=1"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    court_id = request.GET.get('id')
    customer = request.GET.get('customer')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    sql = f"select * from application where " \
          f"customer='{customer}' and" \
          f"court_id='{court_id}'" \
          f"occupy_year='{time[0]}'" \
          f"occupy_month='{time[1]}'" \
          f"occupy_date='{time[2]}'" \
          f"occupy_hour='{time[3]}'"
    with connection.cursor() as cur:
        cur.execute(sql)
        sql = f"insert into status(court_id, administrator_id, " \
              f"customer, occupy_date, occupy_hour, occupy_month, " \
              f"occupy_year) values('{court_id}','0','{customer}'," \
              f"'{time[2]}','{time[3]}','{time[1]}','{time[0]}')"
        cur.execute(sql)
    return JsonResponse({'status':1})