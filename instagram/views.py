from django.shortcuts import render,redirect
from .models import *
from aristo.models import *
from payment.models import *
from instagram import functions


from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from instagram import private_api
import time
from . import tasks
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
from instagram import private_api
from instagram_private_api import (Client, ClientError, ClientLoginError,ClientCookieExpiredError, ClientLoginRequiredError, ClientThrottledError,__version__ as client_version)


#Dashboard Views


@login_required(login_url='/login/')
def change_active_account(request,username):
    Instagram_Accounts.objects.filter(main_user__username=request.user).update(is_current_account=0)
    Instagram_Accounts.objects.filter(username=username).update(is_current_account=1)
    return profile(request)

@login_required(login_url='/login/')       
def dashboard(request):
    if request.POST:
        assistant = Assistants.objects.filter(id=request.POST["assistant"])
        if len(assistant) == 0:
            pass
        else:
            assistant = assistant[0]
        if request.POST["type"]=="sonlandır":
            assistant.activity_status = 3
            assistant.update_time = datetime.now(timezone.utc)
            assistant.save()
        elif request.POST["type"]=="durdur":
            assistant.activity_status = 0
            assistant.update_time = datetime.now(timezone.utc)
            assistant.save()
        elif request.POST["type"]=="devam_et":
            assistant.activity_status = 1
            assistant.update_time = datetime.now(timezone.utc)
            assistant.save()
        elif request.POST["type"]=="başlat":
            return redirect("/select_assistant/")


    all_new_ffs = functions.new_actions(request.user)
   
    ig_accounts_list= functions.get_linked_accounts(request.user)
    linked_assistants_list=functions.linked_assistants(request.user)

    new_linked_assistants_list = []

    for i in linked_assistants_list:
        deneme = []
        for b in i:
            deneme.append(b)
        new_linked_assistants_list.append(deneme)
    
    a = 0
    ohow = []
    for i in new_linked_assistants_list:
        if len(i) == 2:
            ohow.append(i)
        else:
            if a == 0:
                i.append("x")
                ohow.insert(0,i)
                a += 1
            elif a == 1:
                i.append("y")
                ohow.insert(1,i)
                a += 1
            elif a == 2:
                ohow.insert(2,i)
                i.append("z")

    follow_actions = Follow_Actions.objects.filter(instagram_account__main_user__username = request.user,status = 1)
    like_actions = Like_Actions.objects.filter(instagram_account__main_user__username = request.user,status = 1)
    comment_actions = Comment_Actions.objects.filter(instagram_account__main_user__username = request.user,status = 1)
    total_actions = []
    
    for i in follow_actions:
        total_actions.append(i)
    for i in like_actions:
        total_actions.append(i)
    for i in comment_actions:
        total_actions.append(i)

    total_actions_return = 0

    for i in total_actions:
        analyse_ffs = Analyse_FF.objects.filter(instagram_account__main_user__username = request.user,ig_user = i.ig_user,is_follower = 1)
        if len(analyse_ffs) == 0:
            pass
        else:
            total_actions_return +=1
    try:
        percentage_of_actions_return = round((total_actions_return/len(total_actions)*100))
    except:
        percentage_of_actions_return = 1
        total_actions = ["x"]

    
    return render(request, "dashboard.html",{"ig_accounts":ig_accounts_list,"linked_assistants":ohow,"all_new_ffs":all_new_ffs,"percentage_of_actions_return":percentage_of_actions_return,"total_actions":len(total_actions),"total_actions_return":total_actions_return})





@login_required(login_url='/login/')       
def add_insta_account(request):
    if request.POST:
        ig_accounts_list=functions.get_linked_accounts(request.user)
        user = User.objects.get(username = request.user)
        check_license = License.objects.filter(main_user__username = request.user)[0]
        account_limit = check_license.package.account_count
        if user.is_active == False:
            return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error(' Lütfen hesap eklemek için mailinizden hesabınızı onaylayın')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
        elif account_limit == 0:
            return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Lütfen hesap eklemek için lisans sürümünüzü yükseltin')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
        elif len(ig_accounts_list)>=account_limit:
            return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Hesap ekleme limitine ulaştınız , daha fazla hesap eklemek için paketinizi yükseltebilirsiniz.')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
        

            
        username=request.POST["instagram_username"]
        password=request.POST["instagram_password"]
        challenge_user = Challenge_User.objects.filter(username = username)
        if len(challenge_user) == 0:
            challenge_user = Challenge_User(username = username,main_user=request.user,password = password)
            challenge_user.save()
        else:
            challenge_user = challenge_user[0]
        
        if challenge_user.sms_or_mail == 2:
            challenge_required_mail = request.POST.get("mail")
            challenge_required_sms = request.POST.get("sms")
            if challenge_required_sms == "on":
                sms_or_mail = 0
                challenge_user.sms_or_mail = sms_or_mail
            else:
                if challenge_required_mail == "on":
                    sms_or_mail = 1
                    challenge_user.sms_or_mail = sms_or_mail
                else:
                    pass
        else:
            pass
        challenge_user.save()
        challenge_code = request.POST["challenge_code"]
        if challenge_code == "0":
            challenge_user.delete()
            check_linked_assistants_list=functions.check_linked_assistans(request.user)
            return render(request,"profile.html",{"wow":"none","wow2":"block","challenge_code":"none","user":request.user,"ig_accounts":ig_accounts_list,"assistants_list":check_linked_assistants_list,"license_data":functions.license_data(request.user),"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none"})
            
        elif challenge_code == "":
            challenge_code = 2
        else:
            challenge_user.challenge_code = challenge_code
            
        challenge_user.save()
        control_instagram_user=Instagram_Accounts.objects.filter(username=username)
        if len(control_instagram_user)==0:
            challenge_code = challenge_user.challenge_code
            sms_or_mail = challenge_user.sms_or_mail
            challenge_user.save()
            #check_is_real Authentication da hatası verebilir. 
            check_user=private_api.check_is_real(request.user,username,password,challenge_code = challenge_code,sms_or_mail = sms_or_mail)
            if check_user == None:
                check_user = 11
            if type(check_user) != int:
                api = check_user
                rank_token = Client.generate_uuid()
                info = api.username_info(username)
                follower_count = info.get("user").get("follower_count")
                following_count = info.get("user").get("following_count")
                post_count = info.get("user").get("media_count")
                profile_pic_url = info.get("user").get("profile_pic_url")
                user_pk = info.get("user").get("pk")
                full_name = info.get("user").get("full_name")
                is_private = info.get("user").get("is_private")
                biography = info.get("user").get("biography")
                is_business = info.get("user").get("is_business")

                Instagram_Accounts.objects.filter(main_user=request.user).update(is_current_account=0)
                New_IG_Account=Instagram_Accounts(main_user=request.user,username=username,password=password,is_current_account=1,user_pk=user_pk,
                full_name = full_name,is_private=is_private,
                biography = biography,is_business = is_business,profile_pic_url = profile_pic_url)       
                New_IG_Account.save()

                private_api.create_cookie(api.settings, username, rank_token)

                new_ig_analyse=Instagram_Accounts_Analyse(instagram_account=New_IG_Account,media_count=post_count,follower_count=follower_count,following_count=following_count)
                new_ig_analyse.save()
                
                challenge_user.instagram_account = New_IG_Account
                challenge_user.save()

                
                #Celery Part
                tasks.analyse_ig_account.apply_async(queue='deneme1',args=[username])

                
                #!!!! return'lar düzenlenecek! 
                ig_accounts_list=functions.get_linked_accounts(request.user)

                return render(request,"profile.html",{"wow":"none","wow2":"block","challenge_code":"none","pop_up":"add_insta_account_success('Hesap başarıyla eklendi')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})

            #Hesap eklerken lazım olacak doğrulama işlerini de bu fonksiyonda halledelim.
            elif check_user == 1:
                challenge_user.delete()
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Böyle bir kullanıcı bulunamadı.')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
            elif check_user == 2:
                challenge_user.delete()
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Yanlış şifre!')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
            elif check_user == 3:
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Lütfen 1 saat bekleyip yeniden deneyin!')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
            elif check_user == 4:
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Lütfen instagrama girerek gerçekleştiren eylemi ben yaptım seçeneğini işaretleyiniz')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
            elif check_user == 5:
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"block","pop_up":"add_insta_account_error('Lütfen telefonunza yada mailinize gelin kodu doğru bir şekilde giriniz!')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"none","ig_username_disabled":"block","sms_or_mail":"none","ig_user":username,"ig_user_password":password,"license_data":functions.license_data(request.user)})
            elif check_user == 6:
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Lütfen hesabınızı onaylama yönteminiz seçiniz!')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"none","ig_username_disabled":"block","sms_or_mail":"block","ig_user":username,"ig_user_password":password,"license_data":functions.license_data(request.user)})
            elif check_user == 7:
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"block","pop_up":"add_insta_account_error('Bilinmeyen hata')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
            elif check_user == 8:
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"block","pop_up":"add_insta_account_error('Lütfen gelen kodu giriniz eğer kod gelmediyse(5dk ya kadar kod gelmesi gecikebilir) yada yanlış onay çeşidini seçtiyseniz onay kodu yerine 0 yazıp onaylayın ve daha sonra yeniden deneyin')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"none","ig_username_disabled":"block","sms_or_mail":"none","ig_user":username,"ig_user_password":password,"license_data":functions.license_data(request.user)})
            elif check_user == 9:
                challenge_user.delete()
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Lütfen farklı bir onay yöntemi deneyiniz.')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"none","ig_username_disabled":"block","sms_or_mail":"block","ig_user":username,"ig_user_password":password,"license_data":functions.license_data(request.user)})
            elif check_user == 10:
                challenge_user.delete()
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Lütfen boş yerleri doldurun.')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
            elif check_user == 11:
                challenge_user.delete()
                return render(request,"profile.html",{"wow":"block","wow2":"none","challenge_code":"none","pop_up":"add_insta_account_error('Çok fazla deneme yaptınız, lütfen daha sonra yeniden deneyiniz.')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})




        else:
            return render(request,"profile.html",{"wow":"block","challenge_code":"none","wow2":"none","pop_up":"add_insta_account_error('Bu hesap zaten kayıtlı')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})
    else:
        ig_accounts_list=functions.get_linked_accounts(request.user)
        return render(request,"profile.html",{"wow":"none","wow2":"block","challenge_code":"none","pop_up":"add_insta_account_success('Hesap başarıyla eklendi')","user":request.user,"ig_accounts":ig_accounts_list,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none","license_data":functions.license_data(request.user)})


@login_required(login_url='/login/')
def profile(request):
    instagram_accounts=functions.get_linked_accounts(request.user)
    check_linked_assistants_list=functions.check_linked_assistans(request.user)
    try:
        license_datas = functions.license_data(request.user)
    except:
        license_datas = 0
    return render(request,"profile.html",{"wow":"none","wow2":"block","challenge_code":"none","user":request.user,"ig_accounts":instagram_accounts,"number":len(instagram_accounts),"assistants_list":check_linked_assistants_list,"license_data":license_datas,"ig_username":"block","ig_username_disabled":"none","sms_or_mail":"none"})


#Asssistant Views
@login_required(login_url='/login/')
def select_assistant(request):
    ig_accounts_list=functions.get_linked_accounts(request.user)
    if request.POST:
        license_object = License.objects.filter(main_user__username = request.user)[0]
        if license_object.status == 2:
            return render(request,"assistant_type.html",{"ig_accounts":ig_accounts_list,"popup_message":"license_has_expired()"})
        if 'source' in request.POST:
            filters_html = str(request.POST['type']) + '_' + str(request.POST['source']) + '.html'
            return render(request,filters_html,{"ig_accounts":ig_accounts_list})
        
        elif 'type' in request.POST:
            instagram_account = Instagram_Accounts.objects.filter(main_user__username = request.user,is_current_account = 1)
            if len(instagram_account)==0: 
                return render(request,"assistant_type.html",{"ig_accounts":ig_accounts_list,"popup_message":"ig_user_was_not_added()"})
            else:
                instagram_account = instagram_account[0]
            assistants = Assistants.objects.filter(instagram_account = instagram_account)
            follow_action = 0
            like_action = 0
            comment_action = 0
            for i in assistants:
                if i.assistant_type == 0:
                    if i.activity_status == 0 or i.activity_status == 1:
                        follow_action = 1
                if i.assistant_type == 1:
                    if i.activity_status == 0 or i.activity_status == 1:
                        like_action = 1
                if i.assistant_type == 2:
                    if i.activity_status == 0 or i.activity_status == 1:
                        comment_action = 1
            if request.POST['type'] == "follow" and follow_action == 0 or request.POST['type'] == "like" and like_action == 0 or request.POST['type'] == "comment" and comment_action == 0:
                return render(request,"assistant_source.html",{"type":str(request.POST['type']),"ig_accounts":ig_accounts_list})
            else:
                return render(request,"assistant_type.html",{"ig_accounts":ig_accounts_list,"popup_message":"assistant_already_added()"})

    else:
        return render(request,"assistant_type.html",{"ig_accounts":ig_accounts_list})

@login_required(login_url='/login/')
def delete_ig_account(request):
    if request.POST:
        ig_account=Instagram_Accounts.objects.get(username=request.POST["ig_account"])
        if ig_account.is_current_account==1:
            ig_account.delete()
            try:
                new_active_account=Instagram_Accounts.objects.filter(main_user__username=request.user)[0]
                new_active_account.is_current_account=1
                new_active_account.save()
            except:
                pass
        else:
            ig_account.delete()
        return profile(request)
    else:
        return profile(request)

@login_required(login_url='/login/')
def delete_ig_account_navbar(request,user):
    
    ig_account=Instagram_Accounts.objects.get(username=user)
    if ig_account.is_current_account==1:
        ig_account.delete()
        try:
            new_active_account=Instagram_Accounts.objects.filter(main_user__username=request.user)[0]
            new_active_account.is_current_account=1
            new_active_account.save()
        except:
            pass
    else:
        ig_account.delete()
    return profile(request)

@login_required(login_url='/login/')
def assistants_details(request):
    ig_accounts_list= functions.get_linked_accounts(request.user)
    all_actions_list = []
    active_ig_account = Instagram_Accounts.objects.filter(main_user__username = request.user,is_current_account = 1)
    if len(active_ig_account) == 0:
        active_ig_account = 0
    else:
        active_ig_account = active_ig_account[0]
    like_actions = Like_Actions.objects.filter(instagram_account=active_ig_account)
    follow_actions = Follow_Actions.objects.filter(instagram_account=active_ig_account)
    comment_actions = Comment_Actions.objects.filter(instagram_account=active_ig_account)
    for i in like_actions:
        all_actions_list.append(i)
    for i in follow_actions:
        all_actions_list.append(i)
    for i in comment_actions:
        all_actions_list.append(i)
    actions_dict = {}
    general_actions_list = []
    source = ""
    relationship = ""
    assistant = ""
    status = ""
    total_actions = len(all_actions_list)
    def myFunc(e):
        return e.update_time
    all_actions_list = sorted(all_actions_list,key=myFunc,reverse=True)
    if request.POST:
        pass
    else:
        if total_actions >= 300:
            all_actions_list = all_actions_list[:300]
    for i in all_actions_list:
        actions_dict["Kullanıcı adı"] = i.ig_user.username
        actions_dict["Bağlı olduğu hesap"] = i.instagram_account.username
        if i.relationship == 0:
            relationship = "Takipçileri"
        elif i.relationship == 1:
            relationship = "Takip ettikleri"
        elif i.relationship == 2:
            relationship = "Beğenenler"
        elif i.relationship == 3:
            relationship = "Yorum yapanlar"
        actions_dict["Kaynak Çeşidi"] = relationship
        
        if i.source_type == 0:
            source = "Kullanıcı"
        elif i.source_type == 1:
            source = "Hashtag"
        elif i.source_type == 2:
            source = "Lokasyon"
        actions_dict["Kaynak Türü"] = source
        actions_dict["Geldiği Kaynak"] = i.source
        if i.assistant.assistant_type == 0:
            assistant = "Takip"
        elif i.assistant.assistant_type == 1:
            assistant = "Beğeni"
        elif i.assistant.assistant_type == 2:
            assistant = "Yorum"
        actions_dict["Eylem Türü"] = assistant
        if i.status == 0:
            status = "Beklemede"
        elif i.status == 1:
            status = "Başarılı"
        elif i.status == 2:
            status = "Başarısız"
        elif i.status == 9:
            status = "Filtreden Geçti"
        elif i.status == -1:
            status = "Filtreye Takıldı"
        actions_dict["Status"] = status
        time = i.update_time
        time_minute = str(time.minute)
        if len(time_minute) == 1:
            time_minute = "0"+time_minute
        action_time = str(time.year)+"/"+str(time.month)
        if time.hour+3 < 24:
            new_hour = str(time.hour+3)
            new_day = str(time.day)
        else:
            new_hour = str((time.hour+3)%24)
            new_day = str(time.day+1)
        if len(new_hour)==1:
            new_hour = "0"+new_hour
        action_time += "/" + new_day + "/" + new_hour+":"+time_minute
        actions_dict["İşlem Zamanı"] = action_time
        actions_dict["Deneme"] = "✅"
        
        new_action = []
        for i in actions_dict:
            new_action.append(actions_dict[i])
        general_actions_list.append(new_action)
        actions_dict = {}

        
    return render(request,"assistants_details.html",{"general_actions_list":general_actions_list,"ig_accounts":ig_accounts_list,"total_actions":total_actions})

@login_required(login_url='/login/')
def create_assistant(request):
    instagram_account = Instagram_Accounts.objects.get(main_user__username = request.user,is_current_account=1)
    ig_accounts_list = functions.get_linked_accounts(request.user)
    post = request.POST.copy()

    #Turn On and None status to 0 and 1
    for i in post:
        if post.get(i) =='on':
            post[i] = 1
    
    check_values=["likers","commenters","is_default","is_private","biography","has_anonymous_profile_picture","is_business","followers","followings","posters","comment"]

    for i in check_values:
        if i in post:
            pass
        else:
            post[i]=0


    #Get All Post Data
    
    likers = post.get("likers")
    commenters = post.get("commenters")
    is_default = post.get("is_default")
    number_of_actions=post.get("number_of_actions")
    max_followers=post.get('max_followers')
    min_followers=post.get('min_followers')
    max_followings=post.get('max_followings')
    min_followings=post.get('min_followings')
    max_posts=post.get('max_posts')
    min_posts=post.get('min_posts')
    is_private=post.get("is_private")
    biography=post.get("biography")
    has_anonymous_profile_picture=post.get("has_anonymous_profile_picture")
    is_business=post.get("is_business")
    followers = post.get('followers')
    followings = post.get('followings')
    username = post.get('user')
    hashtag = post.get('hashtag')
    location = post.get("location")
    posters = post.get("posters")
    speed = post.get("speed")
    comment = post.get("comment")
    
    assistant_type = post.get("type").split('_')[0]
    source = post.get("type").split('_')[1]

    if username:
        private_api.check_sources(instagram_account.username,username,source)
    elif hashtag:
        private_api.check_sources(instagram_account.username,hashtag,source)
    else:
        private_api.check_sources(instagram_account.username,location,source)

    if assistant_type =='follow':
        assistant_type = 0
        action_name = Follow_Actions
    elif assistant_type =='like':
        assistant_type = 1
        action_name = Like_Actions
    elif assistant_type =='comment':
        assistant_type = 2 
        action_name = Comment_Actions
    
    if source == "user":
        source_type = 0
        source = username
    elif source == "hashtag":
        source_type = 1
        source = hashtag
    elif source == "location":
        source_type = 2
        source = location    

    relationship = ''
    if followers ==1:
        relationship = relationship + '0'
    if followings ==1:
        relationship = relationship + '1'
    if likers ==1:
        relationship = relationship + '2'
    if commenters ==1:
        relationship = relationship + '3'
    if posters ==1:
        relationship = relationship + '4'
    
    if relationship == '':
        return render(request,"assistant_type.html",{"ig_accounts":ig_accounts_list,"popup_message":"relationship_error('Lütfen kaynak seçini yapın!')"})

    #Create a new assistant
    assistant = Assistants(instagram_account = instagram_account,assistant_type=assistant_type, source_type=source_type,source=source,relationship=relationship,number_of_actions = number_of_actions,activity_status=1,queue=int(relationship[0]),update_time = datetime.now(timezone.utc),comment = comment)
    assistant.save()

    #Create new assistant's settings
    if assistant_type != 0:
        assistant_settings=Assistants_Settings(is_default =is_default,assistant=assistant,min_followers=min_followers,max_followers=max_followers,min_followings=min_followings,max_followings=max_followings,is_private=0,biography=biography,is_business=is_business,max_posts=max_posts,min_posts=min_posts,has_anonymous_profile_picture=has_anonymous_profile_picture,speed=speed)
    else:
        assistant_settings=Assistants_Settings(is_default =is_default,assistant=assistant,min_followers=min_followers,max_followers=max_followers,min_followings=min_followings,max_followings=max_followings,is_private=is_private,biography=biography,is_business=is_business,max_posts=max_posts,min_posts=min_posts,has_anonymous_profile_picture=has_anonymous_profile_picture,speed=speed)
    assistant_settings.save()

    
    for i in relationship:
        actions = action_name.objects.filter(status = 0,relationship = int(i),source_type = source_type,source = source,assistant__activity_status = 3)
        for b in actions:
            assistant.queue = b.assistant.queue
            assistant.save()
            b.assistant = assistant
            b.instagram_account = instagram_account
            b.save()
            
                

    return redirect("/dashboard/")
