'''
**************************************************
@File   ：stadium_management -> urls
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/24 20:53
**************************************************
'''

from django.urls import path
from web.view import administrator_views as av
from web.view import application_views as apv
from web.view import court_views as cov
from web.view import customer_views as cv
from web.view import status_views as sv

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
    path('administrator/logout/', av.administrator_login),
    path('administrator/register/', av.administrator_register),
    path('administrator/sel/', av.administrator_select),
    path('administrator/mod/', av.administrator_modify),
    path('administrator/del/', av.administrator_delete),
    # administrator_court
    path('administrator/court/add/', cov.court_insert),
    path('customer/court/sel/', cov.court_select),
    path('administrator/court/sel/', cov.court_select),
    path('administrator/court/mod/', cov.court_modify),
    path('administrator/court/del/', cov.court_delete),
    # status
    path('administrator/status/add/', sv.status_insert),
    path('customer/status/del/', sv.status_delete),
    path('administrator/status/del/', sv.status_delete),
    # application
    path('customer/application/add/', apv.application_insert),
    path('customer/application/del/', apv.application_delete),
    path('administrator/application/rej/', apv.application_reject),
    path('administrator/application/pro/', apv.application_process),
]
