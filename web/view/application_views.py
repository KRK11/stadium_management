'''
**************************************************
@File   ：stadium_management -> request_views
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/25 22:49
**************************************************
'''

from django.db import connection
from django.http import JsonResponse
from web.models import customer, court, online, application
from web.view import status_views


def application_show(time, court_id, customer_id):
    sql = f"select * from application where " \
          f"customer='{customer_id}' and " \
          f"occupy_year={time[0]} and " \
          f"occupy_month={time[1]} and " \
          f"occupy_date={time[2]} and " \
          f"court_id='{court_id}'"
    result = application.objects.raw(sql)
    arr = [0 for i in range(24)]
    for i in result:
        arr[i.occupy_hour] = 1
    sql = f"select * from court where id='{court_id}'"
    result = court.objects.raw(sql)
    for i in range(0, result[0].service_start_time):
        arr[i] = 1
    for i in range(result[0].service_end_time + 1, 24):
        arr[i] = 1
    return arr

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
    arr = application_show(time, court_id, content[0].id)
    for i in range(time[3], min(time[3] + hour, 24)):
        if arr[i]: return JsonResponse({'status': 0})
        app = application(court_id=court_id, customer=content[0].id,
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
          f"customer='{content[0].id}' and " \
          f"court_id='{court_id}' and " \
          f"occupy_year={time[0]} and " \
          f"occupy_month={time[1]} and " \
          f"occupy_date={time[2]} and " \
          f"occupy_hour={time[3]}"
    result = application.objects.raw(sql)
    if not result: return JsonResponse({'status': 0})
    sql = f"delete from application where " \
          f"customer='{content[0].id}' and " \
          f"court_id='{court_id}' and " \
          f"occupy_year={time[0]} and " \
          f"occupy_month={time[1]} and " \
          f"occupy_date={time[2]} and " \
          f"occupy_hour={time[3]}"
    with connection.cursor() as cur:
        cur.execute(sql)
    return JsonResponse({'status': 1})


def application_display(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}'"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    arr = []
    if not content[0].admin:
        sql = f"select * from application where id='{content[0].id}'"
        result = application.objects.raw(sql)
    else:
        sql = f"select * from application"
        result = application.objects.raw(sql)
    for i in result:
        arr.append({'court_id':i.court_id,'customer':i.customer,
                    'year':i.occupy_year,'month':i.occupy_month,
                    'date':i.occupy_date,'hour':i.occupy_hour})
    return JsonResponse({'status':1,'data':arr})


def application_reject(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=1"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    court_id = request.GET.get('id')
    customer = request.GET.get('customer')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    sql = f"delete from application where " \
          f"customer='{customer}' and " \
          f"court_id='{court_id}' and " \
          f"occupy_year={time[0]} and " \
          f"occupy_month={time[1]} and " \
          f"occupy_date={time[2]} and " \
          f"occupy_hour={time[3]}"
    print(sql)
    with connection.cursor() as cur:
        cur.execute(sql)
    return JsonResponse({'status': 1})


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
          f"customer='{customer}' and " \
          f"court_id='{court_id}' and " \
          f"occupy_year={time[0]} and " \
          f"occupy_month={time[1]} and " \
          f"occupy_date={time[2]} and " \
          f"occupy_hour={time[3]}"
    if not application.objects.raw(sql):
        return JsonResponse({'status': 0})
    arr = status_views.status_show(time, court_id)
    if arr[time[3]]:
        return JsonResponse({'status': 0})
    sql = f"delete from application where " \
          f"customer='{customer}' and " \
          f"court_id='{court_id}' and " \
          f"occupy_year={time[0]} and " \
          f"occupy_month={time[1]} and " \
          f"occupy_date={time[2]} and " \
          f"occupy_hour={time[3]}"
    with connection.cursor() as cur:
        cur.execute(sql)
        sql = f"insert into status(court_id, administrator_id, " \
              f"customer, occupy_date, occupy_hour, occupy_month, " \
              f"occupy_year) values('{court_id}','0','{customer}'," \
              f"{time[2]},{time[3]},{time[1]},{time[0]})"
        cur.execute(sql)
    return JsonResponse({'status': 1})
