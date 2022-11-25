'''
**************************************************
@File   ：stadium_management -> status_views
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/25 20:23
**************************************************
'''

from django.db import connection
import web.models
from web.models import customer, administrator, court, status, online
from django.http import JsonResponse


def status_show(time, court_id):
    sql = f"select * from status where " \
          f"occupy_year={time[0]} and " \
          f"occupy_month={time[1]} and " \
          f"occupy_date={time[2]} and " \
          f"court_id='{court_id}'"
    result = status.objects.raw(sql)
    arr = [0 for i in range(24)]
    for i in result:
        arr[i.occupy_hour] = 1
    sql = f"select * from court where id='{court_id}'"
    result = court.objects.raw(sql)
    for i in range(0,result[0].service_start_time):
        arr[i] = 1
    for i in range(result[0].service_end_time+1,24):
        arr[i] = 1
    return arr


def status_insert(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}'"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    court_id = request.GET.get('id')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    hour = request.GET.get('length')
    if not hour: hour = 1
    else: hour = int(hour)
    customer, administrator = 0, 0
    if not content[0].admin: customer = content[0].id
    else: administrator = content[0].id
    arr = status_show(time, court_id)
    for i in range(time[3],min(time[3]+hour,24)):
        if arr[i]: return JsonResponse({'status':0})
        sta = status(court_id=court_id, customer=customer, administrator_id=administrator,
                     occupy_year=time[0], occupy_month=time[1], occupy_date=time[2],
                     occupy_hour=i)
        sta.save()
    return JsonResponse({'status':1})


def status_delete(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}'"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    customer = request.GET.get('customer')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    sql = f'delete from status where customer={customer} and occupy_year={time[0]} and occupy_month={time[1]} and occupy_date={time[2]} and occupy_hour={time[3]}'
    with connection.cursor() as cur:
        cur.execute(sql)
    print(sql)
    return JsonResponse({'status':1})