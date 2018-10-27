"""EDC_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from bills import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name="index"),
    url(r'^search/$', views.search, name="search"),
    url(r'^add_client/$', views.add_client, name="add_client"),
    url(r'^add_product/$', views.add_product, name="add_product"),
    url(r'^order_results/$', views.order_results, name="order_results"),
    url(r'^list_clients/$', views.list_clients, name="list_clients"),
    url(r'^clients_info/(?P<name>.*)/$', views.clients_info, name="clients_info"),
    url(r'^list_products/$', views.list_products, name="list_products"),
    url(r'^info_products/(?P<name>.*)/$', views.info_products, name="info_products"),
    url(r'^list_taxes/$', views.list_taxes, name="list_taxes"),
    url(r'^info_tax/(?P<name>.*)/$', views.info_tax, name="info_tax"),
    url(r'^list_sales/$', views.list_sales, name="list_sales"),
    url(r'^info_sales/(?P<name>.*)/$', views.info_sales, name="info_sales"),
    url(r'^add_sale/$', views.add_sale, name="add_sale"),
    url(r'^edit_client_info/$', views.edit_client_info, name="edit_client_info"),
    url(r'^save_client_info/$', views.save_client_info, name="save_client_info"),
    url(r'^edit_product_info/$', views.edit_product_info, name="edit_product_info"),
    url(r'^save_product_info/$', views.save_product_info, name="save_product_info"),
    url(r'^.*/$', views.redirect_to_home,name='redirect-to-home'),
]
