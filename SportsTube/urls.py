"""SportsTube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mo.views import landingpage,signIn,signUp,textSearch,imageSearch,searchByText,searchByImage,start,start_the_program
from mo.views import f1,f2,f3,f4,f5,f6
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('app_start/okey/', start_the_program, name='start_the_program'),
    path('admin/', admin.site.urls),
    path('app_start/', start, name='start'),
    path('', landingpage, name='landingpage'),
    path('signedIn/',signIn,name='signIn'),
    path('signedUp/',signUp,name="signUp"),
    path('text-search/',textSearch, name='text-search'),
    path('search-results/',searchByText,name='code'),
    path('image-search/',imageSearch,name='image-search'),
    path('search-results2/',searchByImage,name='inew'),
    path('test1/', f1, name='test'),
    path('test2/', f2, name='a'),
    path('test3/<int:n1>/<int:n2>', f3, name='b'),
    path('test4/<str:a>/<int:b>', f4),
    path('test5/<str:a>/<int:b>/<int:c>', f5),
    path('test6/', f6),
] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)