from django.urls import path

from . import views

app_name = 'hello'
urlpatterns = [
    # path('', views.index, name='index'),
    # path('<int:question_id>/', views.detail, name='detail'),
    # path('<int:question_id>/results/', views.results, name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),

    path('', views.hello, name='hello'),
    # path('owner', views.owner, name='owner'),
    # path('hello', views.hello, name='hello'),
]