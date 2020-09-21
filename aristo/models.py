from django.db import models
from django.contrib.auth.models import User
from django_celery_results.models import TaskResult



# Create your models here.


class Run(models.Model):
    task = models.ForeignKey(TaskResult, on_delete=models.DO_NOTHING)


class Contact_Form(models.Model):
    """Saves all Contact form Messages"""
    main_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=200, verbose_name="isim", null=True)
    surname = models.CharField(max_length=200, verbose_name="soyisim", null=True)
    gsm_no = models.IntegerField(verbose_name="gsm_no",null=True)
    email =  models.CharField(max_length=200, verbose_name="email", null=True)
    message = models.TextField(max_length=20000, verbose_name="mesaj", null=True)
    created_date = models.DateTimeField(auto_now_add=True,verbose_name="Register Date",null=True)

    def __str__(self):
        return self.main_user.username


