from django.contrib import admin

from .models import Manufacturer, Distributor, Retailer, Customer, Product, Unit, Shipment

admin.site.register(Manufacturer)
admin.site.register(Distributor)
admin.site.register(Retailer)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Unit)
admin.site.register(Shipment)
