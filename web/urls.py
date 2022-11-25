'''
**************************************************
@File   ：stadium_management -> urls
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/24 20:53
**************************************************
'''

from django.contrib import admin
from django.urls import path
from web import views
from web.view import customer_views as cv
from web.view import administrator_views as av
from django.urls import re_path

urlpatterns = [
    # customer
    path('customer/login/', cv.customer_login),
    path('customer/logout/', cv.customer_logout),
    path('customer/register/', cv.customer_register),
    path('customer/sel/', cv.customer_select),
    path('customer/mod/', cv.customer_modify),
    path('customer/del/', cv.customer_delete),
    # administrator
    path('administrator/login/', av.administrator_login),
    path('administrator/register/', av.administrator_register),
    path('administrator/sel/', av.administrator_select),
    path('administrator/mod/', av.administrator_modify),
    path('administrator/del/', av.administrator_delete),
    # court
    path('court/add/', views.court_insert),
    path('court/sel/', views.court_select),
    path('court/mod/', views.court_modify),
    path('court/del/', views.court_delete),
    # status
    path('status/add/', views.status_insert),
    path('status/del/', views.status_delete),
    path('status/show/', views.status_display),
]