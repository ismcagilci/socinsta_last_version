from django.shortcuts import render,redirect
from .models import *
from payment.models import *
from instagram.models import *
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
import time
from datetime import datetime, timezone,timedelta
now = datetime.now(timezone.utc)
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse
import six

from instagram import functions


#User Views

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )

account_activation_token = TokenGenerator()




def login_user(request):
    if request.POST:
        email=request.POST["site_email"]
        password=request.POST["site_password"]
        control_user=User.objects.filter(email = email)
        if len(control_user)==0:
            return render(request,"login.html",{"x":"block","y":"Böyle bir kullanıcı bulunamadı!"})
        else:
            user = authenticate(username = control_user[0].email,password=password)
            if user == None:
                return render(request,"login.html",{"x":"block","y":"Yanlış şifre girdiniz , lütfen yeniden deneyiniz!"})
            login(request,user)
            ig_accounts_list=functions.get_linked_accounts(request.user)
            check_linked_assistants_list=functions.check_linked_assistans(request.user)
            if user.is_active == False:
                return render(request,"profile.html",{"wow":"none","wow2":"block","challenge_code":"none","user":request.user,"pop_up":"confirmation_message3()","ig_accounts":ig_accounts_list,"assistants_list":check_linked_assistants_list,"license_data":functions.license_data(request.user),"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none"})
            return render(request,"profile.html",{"wow":"none","wow2":"block","challenge_code":"none","user":request.user,"pop_up":"confirmation_message2()","ig_accounts":ig_accounts_list,"assistants_list":check_linked_assistants_list,"license_data":functions.license_data(request.user),"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none"})
    return render(request,"login.html",{"x":"none"})

def contact(request):
    if request.POST:
        name = request.POST["name"]
        surname = request.POST["surname"]
        gsm_no = request.POST["gsm_no"]
        email = request.POST["email"]
        message = request.POST["message"]
        contact_form = Contact_Form(main_user=request.user,gsm_no = gsm_no,email = email,message = message,name = name,surname = surname)
        contact_form.save()
        send_mail("Mesaj gönderme tamamlandı","Socinsta olarak en kısa zamanda dönüş yapıyoruz ... ","socinstaapp@gmail.com",[email])
        send_mail(email + " adlı hesaptan yeni mesaj alındı",message,"socinstaapp@gmail.com",["bedriyan@gmail.com","ismcagilci@gmail.com"])
    if request.user.is_authenticated:
        ig_accounts_list=functions.get_linked_accounts(request.user)
        return render(request,"contact.html",{"ig_accounts":ig_accounts_list})
    else:
         return render(request,"contact.html")

def register(request):
    if request.POST:
        #Get Post Data
        email_main=request.POST["site_email"]
        first_name = request.POST["first_name"]
        password=request.POST["site_password"]
        password_again=request.POST["site_password_again"]
        try:
            sözleşme = request.POST["contract"]
        except:
            return render(request,"register.html",{"x":"block","y":"Lütfen sözleşmeyi kabul ediniz"})
        #Check Is Post Data Valid
        if len(email_main)==0 or len(password)==0 or len(password_again)==0:
            return render(request,"register.html",{"x":"block","y":"Lütfen boş yerleri doldurun"})

        if password != password_again:
            return render(request,"register.html",{"x":"block","y":"Parolalar eşleşmiyor"})
        
        #Check Is User Exist
        contral_email = User.objects.filter(email = email_main)
        
        if len(contral_email)==0:
            #Create New User
            user = User.objects.create_user(username = email_main ,first_name=first_name, email = email_main, password = password , is_active = False)
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('email_confirmation.html' ,{
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
            }) 
            email = EmailMessage("Socinsta hesabınızı onaylayın!", message, to=[email_main])
            email.content_subtype = "html"
            email.send()  
            user = authenticate(request,username=email_main, password=password)
            login(request,user)
            #Create License
            newLicense=License(main_user=user,package= Package.objects.filter(name='deneme')[0],status=1)
            newLicense.save()
            
            return render(request,"profile.html",{"wow":"none","wow2":"block","challenge_code":"none","pop_up":"account_verification()","license_data":functions.license_data(request.user),"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none"})
        else:
            return render(request,"register.html",{"x":"block","y":"Bu email adresi zaten kayıtlı!"})
        
    else:
        return render(request,"register.html",{"x":"none"}) 


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request,"profile.html",{"wow":"none","wow2":"block","challenge_code":"none","pop_up":"verification_completed()","license_data":functions.license_data(request.user),"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none"})
    else:
        return HttpResponse('Activation link is invalid!')

def change_password_confirmation(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        return render(request,"change_password.html",{"x":"none","user_email":user.email})
    else:
        return HttpResponse('Böyle bir hesap bulunamadı')

def change_password(request):
    if request.POST:
        user_email = request.POST["user_email"]
        new_password = request.POST["new_password"]
        new_password1 = request.POST["new_password1"]
        user = User.objects.filter(email = user_email)
        if len(user) == 0:
            return render(request,"change_password.html",{"x":"block","y":"Böyle bir kullanıcı bulunamadı!"})
        elif new_password != new_password1:
            return render(request,"change_password.html",{"x":"block","y":"Parolar eşleşmiyor!"})
        elif new_password == new_password1:
            user = user[0]
            user.set_password(new_password)
            user.save()
            return render(request,"login.html",{"x":"none","pop_up":"change_password()"})
    return render(request,"change_password.html",{"x":"none"})

def forget_password(request):
    if request.POST:
        user_email = request.POST["email"]
        user = User.objects.filter(email = user_email)
        if len(user)==0:
            return render(request,"forget_password.html",{"x":"block","y":"Böyle bir email bulunamadı lütfen doğru yazdığınızdan emin olun."})
        else:
            user = user[0]
            current_site = get_current_site(request)
            message = render_to_string('change_password_confirmation.html' ,{
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
            }) 
            email = EmailMessage("Lütfen şifrenizi değiştirmek için gelen mesajı onaylayın", message, to=[user_email])
            email.send()
            return render(request,"login.html",{"x":"none","pop_up":"change_password_confirmation_popup()","email":user_email})
    else:
        return render(request,"forget_password.html",{"x":"none"})

def landing(request):
    return render(request,"landing.html")

def about(request):
    if request.user.is_authenticated:
        ig_accounts_list=functions.get_linked_accounts(request.user)
        return render(request, "about.html",{"ig_accounts":ig_accounts_list})
    else:
        return render(request, "about.html")

def pricing(request):
    if request.user.is_authenticated:
        ig_accounts_list=functions.get_linked_accounts(request.user)
        return render(request,"pricing.html",{"ig_accounts":ig_accounts_list})
    else:
        return render(request,"pricing.html")

def logout_user(request):
    logout(request)
    return render(request,"landing.html")

def sozlesme(request):
    return render(request,'sozlesme.html')

