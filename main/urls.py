from django.urls import path
from .views import *

urlpatterns = [
    path("index",index,name="index"),
    path("",datas,name="datas"),
    path("face_verification_view/<int:user_id>",face_verification_view,name="face_verification_view"),
    path('password/', password_verification_view, name='password_verification'),
]








