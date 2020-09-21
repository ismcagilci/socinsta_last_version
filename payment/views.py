from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import random
from .models import *
from instagram import functions
from datetime import datetime, timezone,timedelta
now = datetime.now(timezone.utc)
from payment.payment_functions import *
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail import EmailMessage


def create_packages(request):
    packages = [    ['deneme','Socinsta Deneme Paketi',3,1,0],
                ['temel','Socinsta Temel Paket',1,0,0],
                ['haftalık','Socinsta  Haftalık Temel Paket',7,1,75],
                ['bireysel','Socinsta  Aylık Bireysel Paket',30,1,150],
                ['profesyonel','Socinsta 3 Aylık Profesyonel Paket',90,3,300],
                ['premium','Socinsta 6 Aylık Premium Paket',180,5,500],
            ]
    for i in packages:
        if Package.objects.filter(name=i[0]):
            packagex = Package.objects.filter(name=i[0])[0]
        else:
            package = Package(name=i[0],description=i[1],offered_days=i[2],account_count=i[3],package_price=i[4])
            package.save()
            packagex = package
           
    if not License.objects.filter(main_user=request.user).exists():
        License(main_user = request.user, package = packagex, status=1).save()
    return redirect("/profile/") 

@login_required(login_url='/login/')
def add_cart(request):
    if request.POST:
        card_datas = {}
        if Card.objects.filter(main_user=request.user, payment_status=9).exists():
            current_card = Card.objects.filter(main_user=request.user, payment_status=9)[0]
            current_card.package = Package.objects.filter(name=request.POST.get('package_name'))[0]
            current_card.updated_time= datetime.now(timezone.utc)
            current_card.save()
            card_datas = read_card(current_card.order_id)
        elif Card.objects.filter(main_user=request.user, payment_status=2).exists():
            return redirect("/payment/havale")
        else:
            new_card = Card(main_user=request.user, payment_status=9)
            order_id = random.randint(100000, 999999)
            while Card.objects.filter(order_id=order_id).exists():
                order_id = random.randint(100000, 999999)
            new_card.order_id = order_id
            new_card.package = Package.objects.filter(name=request.POST.get('package_name'))[0]
            new_card.payment_status = 9
            new_card.updated_time= datetime.now(timezone.utc)
            new_card.save()
            card_datas = read_card(order_id)
        
        return render(request, 'card.html', card_datas)
    else:
        return render(request, 'pricing.html')

@login_required(login_url='/login/')
def add_coupon(request):
    if request.POST:       
        card_datas = {}
        coupon_name = request.POST.get('coupon').upper()
        current_card = Card.objects.filter(main_user=request.user, payment_status=9)[0]

        if Coupon.objects.filter(name = coupon_name).exists():
            coupon = Coupon.objects.filter(name = coupon_name)[0]
            if coupon.status == 1:
                current_card.coupon = coupon
                current_card.updated_time= datetime.now(timezone.utc)
                current_card.save()
                card_datas = read_card(current_card.order_id)
                card_datas['pop_up'] = "coupon_success()"
                return render(request, 'card.html', card_datas)

            else: 
                card_datas = read_card(current_card.order_id)
                card_datas['pop_up'] = "coupon_ended()"
                return render(request, 'card.html', card_datas)
                
        else:
            card_datas = read_card(current_card.order_id)
            card_datas['coupon_code'] = coupon_name
            card_datas['pop_up'] = "coupon_notfind()"

        return render(request, 'card.html', card_datas)
    else:
        return render(request, 'pricing.html')

@login_required(login_url='/login/')
def remove_item(request):
    if request.POST:
        current_card = Card.objects.filter(main_user=request.user, payment_status=9)[0]
        item = request.POST.get('remove')
        if item =='package':
            current_card.package = None
            current_card.coupon = None
            current_card.updated_time= datetime.now(timezone.utc)
            current_card.save()
            return render(request, 'pricing.html')

        elif item == 'coupon':
            current_card.coupon = None
            current_card.updated_time= datetime.now(timezone.utc)
            current_card.save()
            card_datas = read_card(current_card.order_id)
            return render(request, 'card.html', card_datas)

        else:
            return render(request, 'pricing.html')

    else:
        return render(request, 'pricing.html')

@csrf_exempt        
def callback(request):
    if request.POST: 
        order_id = request.POST.get('platform_order_id')
        status = request.POST.get('status')
        signature = request.POST.get('signature')
        card = Card.objects.filter(order_id = order_id)[0]
        user_license = License.objects.filter(main_user=card.main_user)[0]
        instagram_accounts=functions.get_linked_accounts(card.main_user)
        check_linked_assistants_list=functions.check_linked_assistans(card.main_user)

        if status =='success':
            buyed_license = License.objects.filter(main_user=card.main_user)[0]
            buyed_license.package = card.package
            buyed_license.created_date = datetime.now(timezone.utc)
            buyed_license.status = 1
            buyed_license.save()
            card.payment_status = 1
            card.save()
            instagram_accounts=functions.get_linked_accounts(card.main_user)
            check_linked_assistants_list=functions.check_linked_assistans(card.main_user)
           
            try:
                license_datas = functions.license_data(card.main_user)
            except:
                license_datas = 0

            return render(request,"profile.html",{"package_name":card.package.description,"pop_up":"payment_success()","wow":"none","wow2":"block","challenge_code":"none","user":card.main_user.first_name + ' ' + card.main_user.last_name,"ig_accounts":instagram_accounts,"number":len(instagram_accounts),"assistants_list":check_linked_assistants_list,"license_data":license_datas,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none"})

        else:
            try:
                license_datas = functions.license_data(card.main_user)
            except:
                license_datas = 0

            return render(request,"profile.html",{"pop_up":"payment_failed()","wow":"none","wow2":"block","challenge_code":"none","user":request.user,"ig_accounts":instagram_accounts,"number":len(instagram_accounts),"assistants_list":check_linked_assistants_list,"license_data":license_datas,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none"})
            
    else: 
        return render(request, 'pricing.html')


def havale(request):
    if request.POST:
        card = Card.objects.filter(order_id = request.POST["order_id"])[0]
        card_datas = read_card(card.order_id)
        post_type = request.POST["post_type"]
        if post_type == "1":
            card.payment_status = 2
            card.save()
            current_site = get_current_site(request)
            email1 = "ismcagilci@gmail.com"
            email2 = "bedriyan@gmail.com"
            message = render_to_string('payment_confirmation.html' ,{
            'user': request.user,
            'order_id' : request.POST["order_id"],
            'payment_amount' : card.package.package_price
            }) 
            email = EmailMessage("Ödeme onayı", message, to=[email1,email2])
            email.send()
            return render(request,"havale_onay.html",card_datas)
        elif post_type == "2":
            card.payment_status = 9
            card.save()
            return redirect("/pricing/")
    else:
        card = Card.objects.filter(main_user = request.user, payment_status=9)
        if card:
            card = card[0]
            card_datas = read_card(card.order_id)
            return render(request,"havale.html",card_datas)
        else:
            card = Card.objects.filter(main_user = request.user, payment_status=2)
            card = card[0]
            card_datas = read_card(card.order_id)
            return render(request,"havale_onay.html",card_datas)
        
        