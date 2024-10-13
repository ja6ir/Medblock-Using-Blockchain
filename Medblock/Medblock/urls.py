from django.urls import path
from MedblockApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home
    path('', views.index, name='home'),

    
    # Manufacturer URLs
    path('mf-reg/', views.register_manufacturer, name='register_manufacturer'),
    path('mf-login/', views.mf_login, name='mf_login'),
    path('mf-logout/', views.logout_manufacturer, name='logout_manufacturer'),
    path('mf-home/', views.mf_home, name='mf_home'),
    path('mf-home/add-products/', views.add_products, name='add_products'),
    path('mf-home/add-units/', views.add_units, name='add_units'),
    path('mf-home/shipments/', views.mf_shipments, name='mf_shipments'),
    path('mf-home/track/', views.mf_track, name='mf_track'),
    
    # Distributor URLs
    path('dist-reg/', views.register_distributor, name='register_distributor'),
    path('dist-login/', views.dist_login, name='dist_login'),
    path('dist-logout/', views.logout_distributor, name='logout_distributor'),
    path('dist-home/', views.dist_home, name='dist_home'),
    path('dist-products/', views.dist_products, name='dist_products'),
    path('dist_shipments/', views.dist_shipments, name='dist_shipments'),
    path('mark-received/<int:shipment_id>/', views.mark_received, name='mark_received'),
    path('verify-product/<int:shipment_id>/', views.verify_product, name='verify_product'),
    
    # Retailer URLs
    path('ret-reg/', views.register_retailer, name='register_retailer'),
    path('ret-login/', views.ret_login, name='ret_login'),
    path('ret-home/', views.ret_home, name='ret_home'),
    path('ret-products/', views.ret_products, name='ret_products'),
    path('ret-sales/', views.ret_sales, name='ret_sales'),
    path('mark-received-retailer/<int:shipment_id>/', views.mark_received_retailer, name='mark_received_retailer'),
    path('verify-product-retailer/<int:shipment_id>/', views.verify_product_retailer, name='verify_product_retailer'),
    
    # Customer URLs
    path('cust-reg/', views.register_customer, name='register_customer'),
    path('cust-login/', views.cust_login, name='cust_login'),
    path('cust-home/', views.cust_home, name='cust_home'),
    path('purchase-history/', views.purchase_history, name='purchase_history'),
    path('purchase-product/<int:product_id>/', views.purchase_history, name='purchase_product'),
    path('verify-product-customer/<int:product_id>/', views.verify_product_customer, name='verify_product_customer'),
    path('prod-auth/', views.unit_verification_view, name='unit_verification'),

    path('logout/', views.logout, name='logout')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
