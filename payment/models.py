from django.db import models
from aristo.models import *
# Create your models here.

class Package(models.Model):
    name = models.CharField(max_length=200,verbose_name="License's Name",null=True)
    description = models.CharField(max_length=200,verbose_name="Description",null=True)
    offered_days = models.IntegerField(verbose_name= 'Offered Days',null=True)
    account_count = models.IntegerField(verbose_name= 'Number of IG Accounts',null=True)
    package_price = models.IntegerField(verbose_name= 'Package Price',null=True)

    def __str__(self):
        return str(self.name)

class License(models.Model):
    """Keeps License informations of Main Users"""
    main_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    package = models.ForeignKey(Package,on_delete=models.CASCADE,null=True)
    created_date = models.DateTimeField(auto_now_add=True,verbose_name="Register Date",null=True)
    status = models.IntegerField(verbose_name="Status", null=True)
    def __str__(self):
        return self.main_user.username


class Coupon(models.Model):
    name = models.CharField(max_length=200,verbose_name="Coupon Name",null=True)
    percentage = models.IntegerField(verbose_name='Percentage', null=True)
    status = models.IntegerField(verbose_name='Status', null=True)
    amount = models.IntegerField(verbose_name='Amount', null=True)

    def __str__(self):
        return str(self.name)

class Card(models.Model):
    main_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    order_id = models.IntegerField(verbose_name= 'Order ID')
    package = models.ForeignKey(Package,on_delete=models.CASCADE,null=True)
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE, null=True)
    signature = models.CharField(max_length=400, verbose_name='signature', null=True)
    payment_status = models.IntegerField(verbose_name='Payment Status', null=True)
    updated_time = models.DateTimeField(auto_now_add=True,verbose_name="Updated Date",null=True)

    def __str__(self):
        return str(self.package.name)