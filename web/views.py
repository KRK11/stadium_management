import datetime
import random
import string

from django.db import connection

import web.models
from web.models import customer, administrator, status, court, online
from django.http import HttpResponse, JsonResponse

mod1 = int(1333333333333333331)
mod2 = int(1) << 64


def get_hash(password):
    hash = int(0)
    for i in password:
        hash = (hash * mod1 + int(i)) % mod2
    return str(hash)


def test_equal(password:str, hash_password:str):
    return get_hash(password) == hash_password


def customer_login(request):
    id = request.GET.get('id')
    password = str(request.GET.get('password'))
    sql = f"select * from customer where id='{id}'"
    result = customer.objects.raw(sql)
    if not result: return JsonResponse({'status':0})
    if not password or not test_equal(password, result[0].password):
        return JsonResponse({'status': 0})
    sql = f"select * from online where id='{id}' and admin=0"
    current = online.objects.raw(sql)
    if current: return JsonResponse({'status':1,"msg":current[0].secret_key})

    secret_key = ''.join(random.choice(string.digits+string.ascii_lowercase) for i in range(15))
    sql = f"insert into online(id, admin, read_permission, modify_premission,secret_key) values('{id}', 0, 1, 1, '{secret_key}')"

    with connection.cursor() as cur:
        cur.execute(sql)
    return JsonResponse({'status':1,"msg":secret_key})


def customer_register(request):
    id = request.GET.get('id')
    name = request.GET.get('name')
    age = request.GET.get('age')
    sex = request.GET.get('sex')
    password = str(request.GET.get('password'))
    try:
        customer.objects.get(id=id)
    except web.models.customer.DoesNotExist:
        cust = customer(id=id, name=name, age=age, sex=sex, password=get_hash(password))
        cust.save()
        return JsonResponse({"status": 1})
    # 插入失败，存在了
    return JsonResponse({"status": 0})


def customer_select(request):
    sel = request.GET.get('id')
    sql = f"select * from customer where id='{sel}'"
    result = customer.objects.raw(sql)
    content = {1: 1}
    for i in result:
        content = {'id': i.id, 'name': i.name, 'age': i.age, 'sex': i.sex}

    arr = []
    sql = f"select * from status where customer='{sel}'"
    result = customer.objects.raw(sql)
    for i in result:
        sta = {'court_id': i.id, 'administrator_id': i.administrator_id,
               'year': i.occupy_year, 'month': i.occupy_month,
               'date': i.occupy_date, 'hour': i.occupy_hour}
        arr.append(sta)
    return JsonResponse({"msg": content, "data": arr})


def customer_modify(request):
    try:
        cust = customer.objects.get(id=request.GET.get('id'))
    except web.models.customer.DoesNotExist:
        return JsonResponse({'status': 0})
    if request.GET.get('name'):
        cust.name = request.GET.get('name')
    if request.GET.get('age'):
        cust.age = request.GET.get('age')
    if request.GET.get('sex'):
        cust.sex = request.GET.get('sex')
    cust.save()
    return JsonResponse({'status': 1})


def customer_delete(request):
    id = request.GET.get('id')
    try:
        with connection.cursor() as cur:
            sql = f"delete from customer where id='{id}'"
            cur.execute(sql)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 0})
    return JsonResponse({'status': 1})


def administrator_login(request):
    id = request.GET.get('id')
    password = str(request.GET.get('password'))
    sql = f"select * from administrator where id='{id}'"
    result = administrator.objects.raw(sql)
    if not result: return JsonResponse({'status':0})
    if not password or not test_equal(password, result[0].password):
        return JsonResponse({'status': 0})
    return JsonResponse({'status':1})


def administrator_register(request):
    id = request.GET.get('id')
    password = str(request.GET.get('password'))
    name = request.GET.get('name')
    age = request.GET.get('age')
    sex = request.GET.get('sex')
    mobile = request.GET.get('mobile')
    try:
        administrator.objects.get(id=id)
    except web.models.administrator.DoesNotExist:
        admin = administrator(id=id, mobile=mobile, name=name,
                              age=age, sex=sex, password=get_hash(password))
        admin.save()
        return JsonResponse({'status': 1})
    return JsonResponse({'status': 0})


def administrator_select(request):
    sel = request.GET.get('id')
    sql = f"select * from administrator where id='{sel}'"
    result = administrator.objects.raw(sql)
    content = {1: 1}
    for i in result:
        content = {'admin_id': i.id, 'name': i.name, 'age': i.age, 'sex': i.sex, 'mobile': i.mobile}
    arr = []
    sql = f"select * from status where administrator_id='{sel}'"
    result = administrator.objects.raw(sql)
    for i in result:
        sta = {'court_id': i.court_id, 'customer': i.customer,
               'year': i.occupy_year, 'month': i.occupy_month,
               'date': i.occupy_date, 'hour': i.occupy_hour}
        arr.append(sta)
    return JsonResponse({'msg': content, 'data': arr})


def administrator_modify(request):
    try:
        admin = administrator.objects.get(id=request.GET.get('id'))
    except web.models.administrator.DoesNotExist:
        return JsonResponse({'status': 0})
    if request.GET.get('name'):
        admin.name = request.GET.get('name')
    if request.GET.get('age'):
        admin.age = request.GET.get('age')
    if request.GET.get('sex'):
        admin.sex = request.GET.get('sex')
    if request.GET.get('mobile'):
        admin.mobile = request.GET.get('mobile')
    admin.save()
    return JsonResponse({'status': 1})


def administrator_delete(request):
    id = request.GET.get('id')
    try:
        administrator.objects.get(id=id)
        with connection.cursor() as cur:
            sql = f"delete from administrator where id='{id}'"
            cur.execute(sql)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 0})
    return JsonResponse({'status': 1})


def court_insert(request):
    id = request.GET.get('id')
    location = request.GET.get('location')
    service_start_time = request.GET.get('start')
    service_end_time = request.GET.get('end')
    try:
        crt = court.objects.get(id=id)
    except court.DoesNotExist:
        crt = court(id=id, location=location, service_start_time=service_start_time, service_end_time=service_end_time)
        crt.save()
        return JsonResponse({'status':1})
    return JsonResponse({'status':0})


def court_select(request):
    sel = request.GET.get('id')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    sql = f"select * from court where id='{sel}'"
    result = court.objects.raw(sql)
    if not result: return JsonResponse({'msg':{},'data':[]})
    content = {'id': result[0].id,'location': result[0].location,
               'start': result[0].service_start_time,
               'end': result[0].service_end_time}
    res = []
    arr = [0 for i in range(24)]
    sql = f"select * from status where court_id='{sel}' and occupy_year='{time[0]}' and occupy_month='{time[1]}' and occupy_date='{time[2]}'"
    result = status.objects.raw(sql)
    for i in result:
        arr[i.occupy_hour] = 1
    for i in range(24):
        if not arr[i]: res.append({'hour':i})
    return JsonResponse({'msg':content,'data':res})


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


def status_display(request):
    # 展示某年某月某日的球场安排情况
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    print(time)
    sql = f'select * from status where occupy_year={time[0]} and occupy_month={time[1]} and occupy_date={time[2]}'
    result = status.objects.raw(sql)
    arr = [{i:0} for i in range(24)]
    for i in result:
        arr[i.occupy_hour] = {i.occupy_hour:1}
    return JsonResponse({"data":arr})


def status_show(time):
    sql = f'select * from status where occupy_year={time[0]} and occupy_month={time[1]} and occupy_date={time[2]}'
    result = status.objects.raw(sql)
    arr = [0 for i in range(24)]
    for i in result:
        arr[i.occupy_hour] = 1
    return arr


def status_insert(request):
    court_id = request.GET.get('id')
    customer = request.GET.get('customer')
    administrator_id = request.GET.get('admin')
    # 时间格式：2022-1-4-9(表示2022年1月4号9点-10点时间段)
    # 年，月，日，时
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    arr = status_show(time)
    if arr[time[3]]: return JsonResponse({'status':0})
    sta = status(court_id=court_id, customer=customer, administrator_id=administrator_id,
                 occupy_year=time[0], occupy_month=time[1], occupy_date=time[2],
                 occupy_hour=time[3])
    sta.save()
    return JsonResponse({'status':1})


def status_delete(request):
    customer = request.GET.get('customer')
    time = request.GET.get('time').split('-')
    time = [int(i) for i in time]
    sql = f'delete from status where customer={customer} and occupy_year={time[0]} and occupy_month={time[1]} and occupy_date={time[2]} and occupy_hour={time[3]}'
    with connection.cursor() as cur:
        cur.execute(sql)
    print(sql)
    return JsonResponse({'status':1})
