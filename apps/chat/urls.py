from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.home, name='home'),
    path('conversacion/<int:conversation_id>/', views.conversation, name='conversation'),
    path('usuarios/', views.users, name='users'),
    path('api/conversacion/', views.create_conversation, name='create_conversation'),
    path('api/conversacion/<int:conversation_id>/mensajes/', views.messages, name='messages'),
    path('api/conversacion/<int:conversation_id>/archivo/', views.upload_attachment, name='upload_attachment'),
]
