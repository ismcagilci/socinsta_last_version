from .models import *
from aristo.models import *
from payment.models import *
import time
from datetime import datetime, timezone,timedelta
now = datetime.now(timezone.utc)


def get_linked_accounts(user):
    instagram_accounts=Instagram_Accounts.objects.filter(main_user=user)
    instagram_accounts_list=[]
    for i in instagram_accounts:
        Analyse=Instagram_Accounts_Analyse.objects.filter(instagram_account=i)[0]
        datas = {'username':i.username,'follower_count':Analyse.follower_count,'following_count':Analyse.following_count,
        'profile_pic_url':i.profile_pic_url,'media_count':Analyse.media_count,'is_current_account':i.is_current_account}
        instagram_accounts_list.append(datas)
    return instagram_accounts_list


def get_assistants_details(user):

    active_ig_account = Instagram_Accounts.objects.filter(main_user = user,is_current_account = 1)
    if len(active_ig_account) == 0:
        return False
    else:
        active_ig_account = active_ig_account[0]
        latest_follow_assistant = Assistants.objects.filter(instagram_account__username=active_ig_account.username,assistant_type=0)
        latest_like_assistant = Assistants.objects.filter(instagram_account__username=active_ig_account.username,assistant_type=1)
        latest_comment_assistant = Assistants.objects.filter(instagram_account__username=active_ig_account.username,assistant_type=2)
        latest_unfollow_assistant = Assistants.objects.filter(instagram_account__username=active_ig_account.username,assistant_type=3)
        assistants_list=[]
    #check_latest_assistants
   
    if latest_follow_assistant:
        i = latest_follow_assistant.latest("update_time")
        percentage_of_process=len(Follow_Actions.objects.filter(status=1,assistant = i))/i.number_of_actions*100
        percentage_of_process=round(percentage_of_process)
        if i.source_type==0:
            target_username="@"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_username,status,"x","Takip_Kullanıcı",i.id,i.is_there_enough_data))
        elif i.source_type==1:
            target_hashtag="#"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_hashtag,status,"x","Takip_Hashtag",i.id,i.is_there_enough_data))
        elif i.source_type==2:
            target_location="📍"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_location,status,"x","Takip_Lokasyon",i.id,i.is_there_enough_data))
    #like assistant
    if latest_like_assistant:
        i = latest_like_assistant.latest("update_time")
        percentage_of_process=len(Like_Actions.objects.filter(status=1,assistant = i))/i.number_of_actions*100
        percentage_of_process=round(percentage_of_process)
        if int(i.source_type)==0:

            target_username="@"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_username,status,"y","Beğeni_Kullanıcı",i.id,i.is_there_enough_data))
        elif int(i.source_type)==1:
            target_hashtag="#"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_hashtag,status,"y","Beğeni_Hashtag",i.id,i.is_there_enough_data))
        elif int(i.source_type)==2:
            target_location="📍"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_location,status,"y","Beğeni_Lokasyon",i.id,i.is_there_enough_data))
    #comment assistant
    if latest_comment_assistant:
        i = latest_comment_assistant.latest("update_time")
        percentage_of_process=len(Comment_Actions.objects.filter(status=1,assistant = i))/i.number_of_actions*100
        percentage_of_process=round(percentage_of_process)
        if int(i.source_type)==0:
            target_username="@"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_username,status,"z","Yorum_Kullanıcı",i.id,i.is_there_enough_data))
        elif int(i.source_type)==1:
            target_hashtag="#"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_hashtag,status,"z","Yorum_Hashtag",i.id,i.is_there_enough_data))
        elif int(i.source_type)==2:
            target_location="📍"+i.source
            ig_username="@"+i.instagram_account.username
            status=i.activity_status
            assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_location,status,"z","Yorum_Lokasyon",i.id,i.is_there_enough_data))
    if latest_unfollow_assistant:
        i = latest_unfollow_assistant.latest("update_time")
        percentage_of_process=len(Unfollow_Actions.objects.filter(status=1,assistant = i))/i.number_of_actions*100
        percentage_of_process=round(percentage_of_process)
        target_username="@"+i.instagram_account.username
        ig_username="@"+i.instagram_account.username
        status=i.activity_status
        assistants_list.append((i.number_of_actions,percentage_of_process,i.assistant_type,i.source_type,ig_username,target_username,status,"ogg","Takipten Çık",i.id,i.is_there_enough_data))

        



    
    return assistants_list



def new_actions(user):
    analyse_ff = Analyse_FF.objects.filter(instagram_account__main_user = user)

    daily_new_followers = 0
    weekly_new_followers = 0
    monthly_new_followers = 0
    for i in analyse_ff:
        if i.is_follower == 1:
            if (datetime.now(timezone.utc)-i.follower_update_time).days<1:
                daily_new_followers += 1
            elif (datetime.now(timezone.utc)-i.follower_update_time).days<7:
                weekly_new_followers += 1
            else:
                monthly_new_followers += 1
        else:
            pass
    weekly_new_followers += daily_new_followers
    monthly_new_followers += weekly_new_followers

    ig_account_analyse = Instagram_Accounts_Analyse.objects.filter(instagram_account__main_user = user)
    daily_new_likes = 0
    weekly_new_likes = 0
    monthly_new_likes = 0
    total_new_likes = 0

    daily_new_comments = 0
    weekly_new_comments = 0
    monthly_new_comments = 0
    total_new_comments = 0

    for i in ig_account_analyse:
        if i.like_count == None:
            pass
        else:
            if (datetime.now(timezone.utc)-i.update_time).days<1:
                daily_new_likes += i.like_count
                daily_new_comments += i.comment_count
            elif (datetime.now(timezone.utc)-i.update_time).days<7:
                weekly_new_likes += i.like_count
                weekly_new_comments += i.comment_count
            elif (datetime.now(timezone.utc)-i.update_time).days<30:
                monthly_new_likes += i.like_count
                monthly_new_comments += i.comment_count
            else:
                total_new_comments += i.comment_count
                total_new_likes += i.like_count


    weekly_new_likes += daily_new_likes
    monthly_new_likes += weekly_new_likes
    total_new_likes += monthly_new_likes

    weekly_new_comments += daily_new_comments
    monthly_new_comments += weekly_new_comments
    total_new_comments += monthly_new_comments

    
    all_new_ffs = {'daily_new_followers':daily_new_followers,'weekly_new_followers':weekly_new_followers,'monthly_new_followers':monthly_new_followers,'daily_new_likes':daily_new_likes,'weekly_new_likes':weekly_new_likes,
    'monthly_new_likes':monthly_new_likes,'daily_new_comments':daily_new_comments,'weekly_new_comments':weekly_new_comments,'monthly_new_comments':monthly_new_comments,'total_new_likes':total_new_likes,'total_new_comments':total_new_comments}
    
    return all_new_ffs


def linked_assistants(user):
    x=get_assistants_details(user)
    assistants_list=[(0,"Takip"),(0,"Beğeni"),(0,"Yorum"),(0,"Takip bırak")]
    if x == False:
        return assistants_list
    assistants_list=[]
    assistant_type_list=["Takip","Beğeni","Yorum","Takip bırak"]
    for b in x:
        if b[2]==0 or b[2]==1 or b[2]==2 or b[2]==3:
            assistants_list.append(b)
    a=0
    for i in range(4):
        try:
            if assistants_list[a][2] != a:
                assistants_list.insert(a,(0,assistant_type_list[a]))
        except:
            assistants_list.insert(a,(0,assistant_type_list[a]))
        a+=1

    return assistants_list


def check_linked_assistans(user):
    assistants_details=Assistants.objects.filter(instagram_account__main_user= user)
    new=[]
    for i in assistants_details:
        new.append(i.assistant_type)
    assistants_status=[]
    a=0
    for i in range(3):
        try:
            new.index(a)
            assistants_status.append(1)
        except:
            assistants_status.append(0)
        a+=1
    return assistants_status


def license_data(user):
    license_object = License.objects.filter(main_user = user)[0] 
    created_date = license_object.created_date
    package_name = license_object.package.name.upper()
    status = license_object.status
    if status == 2:
        package_name = package_name + " lisans sonlandı"
        remaining_time = 0
    else:
        if not package_name =='TEMEL':
            remaining_time = license_object.package.offered_days-(datetime.now(timezone.utc)-created_date).days
            Assistants.objects.filter(instagram_account__main_user = user,activity_status = 4).update(activity_status = 1)
            if remaining_time < 0:
                remaining_time = 0
                license_object.status = 2
                license_object.save()
        else: 
            remaining_time = '∞'
    
    
    license_data = {'package_name':package_name,'remaining_time':remaining_time}
    return license_data




