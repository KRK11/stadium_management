'''
**************************************************
@File   ：stadium_management -> administrator_views
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/25 17:50
**************************************************
'''

import random
import string
from django.db import connection
import web.models
from web.models import administrator, status, online
from django.http import JsonResponse
from web.tools.password_process import get_hash, test_equal


def administrator_login(request):
    id = request.GET.get('id')
    password = str(request.GET.get('password'))
    sql = f"select * from administrator where id='{id}'"
    result = administrator.objects.raw(sql)
    if not result: return JsonResponse({'status':0})
    if not password or not test_equal(password, result[0].password):
        return JsonResponse({'status': 0})
    sql = f"select * from online where id='{id}' and admin=1"
    current = online.objects.raw(sql)
    if current: return JsonResponse({'status': 1, "msg": current[0].secret_key})

    secret_key = ''.join(random.choice(string.digits + string.ascii_lowercase) for i in range(15))
    sql = f"insert into online(id, admin, read_permission, modify_premission,secret_key) values('{id}', 1, 1, 1, '{secret_key}')"

    with connection.cursor() as cur:
        cur.execute(sql)
    return JsonResponse({'status':1})


def administrator_logout(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=1"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    sql = f"delete from online where secret_key='{key}' and admin=1"
    with connection.cursor() as cur:
        cur.execute(sql)
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


def administrator_get(sel):
    sql = f"select * from administrator where id='{sel}'"
    result = administrator.objects.raw(sql)
    content = {1: 1}
    for i in result:
        content = {'id': i.id, 'name': i.name, 'age': i.age, 'sex': i.sex, 'mobile':i.mobile}

    arr = []
    sql = f"select * from status where administrator_id='{sel}'"
    result = status.objects.raw(sql)
    for i in result:
        sta = {'court_id': i.court_id, 'year': i.occupy_year,
               'month': i.occupy_month, 'date': i.occupy_date, 'hour': i.occupy_hour}
        arr.append(sta)
    return content, arr


def administrator_select(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=1"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    content, arr = administrator_get(content[0].id)
    return JsonResponse({"status": 1, "msg": content, "data": arr})


def administrator_modify(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=1"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    admin = administrator.objects.get(id=request.GET.get('id'))
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
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=1"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    id = content[0].id
    try:
        with connection.cursor() as cur:
            sql = f"delete from administrator where id='{id}'"
            cur.execute(sql)
            sql = f"delete from status where administrator_id='{id}'"
            cur.execute(sql)
            sql = f"delete from online where id='{id}' and admin=1"
            cur.execute(sql)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 0})
    return JsonResponse({'status': 1})
