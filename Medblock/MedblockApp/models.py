from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import hashlib
from datetime import datetime
import json


class Manufacturer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    reg_no = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name


class Distributor(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name


class Retailer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField(unique=True, default='example@123.com')
    password = models.CharField(max_length=128)  # Store hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(upload_to='product_images/', null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)  # Many-to-One with Manufacturer
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Unit(models.Model):
    e_date = models.DateField()  # Expiry date
    m_date = models.DateField(auto_now_add=True)  # Manufacturing date
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Many-to-One with Product

    def __str__(self):
        return f"Unit of {self.product.name} (Expiry: {self.e_date})"


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('intransit_distributor', 'In Transit to Distributor'),
        ('distributor_received', 'Distributor Received'),
        ('intransit_retailer', 'In Transit to Retailer'),
        ('retailer_received', 'Retailer Received'),
        ('sold', 'Sold'),
    ]
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, null=True)
    units = models.ManyToManyField(Unit, related_name='shipments')  # Many-to-Many with Units
    shipment_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='intransit_distributor')
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE, null=True)
    tracking_number = models.CharField(max_length=100, unique=True)
    is_received = models.BooleanField(default=True)
    

    def __str__(self):

        return f"Shipment {self.tracking_number}"


class Block(models.Model):
    index = models.IntegerField()
    timestamp = models.DateTimeField()
    previous_hash = models.CharField(max_length=64)
    proof = models.IntegerField()
    data = models.TextField()  # Storing JSON as text
    hash = models.CharField(max_length=64)

    def __str__(self):
        return f'Block {self.index} with hash {self.hash}'

    def get_data(self):
        return json.loads(self.data)

    def set_data(self, data_dict):
        self.data = json.dumps(data_dict, sort_keys=True)

    def compute_hash(self):
        timestamp_str = self.timestamp.replace(microsecond=0).isoformat()
        block_string = json.dumps({
            'index': self.index,
            'timestamp': timestamp_str,
            'previous_hash': self.previous_hash,
            'proof': self.proof,
            'data': self.data
        }, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()
