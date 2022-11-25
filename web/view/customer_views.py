'''
**************************************************
@File   ：stadium_management -> customer_views
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/25 16:08
**************************************************
'''
import random
import string
from django.db import connection
import web.models
from web.models import customer, status, online
from django.http import JsonResponse
from web.tools.password_process import get_hash, test_equal


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


def customer_logout(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=0"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    sql = f"delete from online where secret_key='{key}' and admin=0"
    with connection.cursor() as cur:
        cur.execute(sql)
    return JsonResponse({'status':1})


def customer_register(request):
    id = request.GET.get('id')
    name = request.GET.get('name')
    age = request.GET.get('age')
    sex = request.GET.get('sex')
    password = str(request.GET.get('password'))
    try:
        customer.objects.get(id=id)
    except web.models.customer.DoesNotExist:
        cust = customer(id=id, name=name, age=age, sex=sex,
                        password=get_hash(password))
        cust.save()
        return JsonResponse({"status": 1})
    # 插入失败，存在了
    return JsonResponse({"status": 0})


def customer_get(sel):
    sql = f"select * from customer where id='{sel}'"
    result = customer.objects.raw(sql)
    content = {1: 1}
    for i in result:
        content = {'id': i.id, 'name': i.name, 'age': i.age, 'sex': i.sex}

    arr = []
    sql = f"select * from status where customer='{sel}'"
    result = status.objects.raw(sql)
    for i in result:
        sta = {'court_id': i.court_id, 'administrator_id': i.administrator_id,
               'year': i.occupy_year, 'month': i.occupy_month,
               'date': i.occupy_date, 'hour': i.occupy_hour}
        arr.append(sta)
    return content, arr


def customer_select(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=0"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status":0})
    content, arr = customer_get(content[0].id)
    return JsonResponse({"status":1, "msg": content, "data": arr})


def customer_modify(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=0"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    cust = customer.objects.get(id=content[0].id)
    if request.GET.get('name'):
        cust.name = request.GET.get('name')
    if request.GET.get('age'):
        cust.age = request.GET.get('age')
    if request.GET.get('sex'):
        cust.sex = request.GET.get('sex')
    if request.GET.get('password'):
        cust.password = get_hash(request.GET.get('password'))
    cust.save()
    return JsonResponse({'status': 1})


def customer_delete(request):
    key = request.GET.get('key')
    sql = f"select * from online where secret_key='{key}' and admin=0"
    content = online.objects.raw(sql)
    if not content: return JsonResponse({"status": 0})
    id = content[0].id
    try:
        with connection.cursor() as cur:
            sql = f"delete from customer where id='{id}'"
            cur.execute(sql)
            sql = f"delete from status where customer='{id}'"
            cur.execute(sql)
            sql = f"delete from online where id='{id}'"
            cur.execute(sql)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 0})
    return JsonResponse({'status': 1})

