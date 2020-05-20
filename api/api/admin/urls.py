from django.urls import path
from api.api.admin.views import *

urlpatterns = [
    path('GetInit/', GetInit.as_view()),
    path('PostSaveUser/', PostSaveUser.as_view()),
    path('GetErrorLog/', GetErrorLog.as_view()),
]
