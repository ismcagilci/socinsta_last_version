from __future__ import absolute_import, unicode_literals
from celery import shared_task,app,task
import time
from .models import *
from aristo.models import *
from payment.models import * 
from instagram import private_api
from django_celery_results.models import TaskResult
from datetime import datetime, timezone,timedelta
now = datetime.now(timezone.utc)
import json
import random
        

def ig_user_detailed_info(action_name,action_id,assistant_id):
    api = private_api.login_with_assistant(assistant_id)
    action = action_name.objects.get(id = action_id)
    ig_user = action.ig_user
    pk_number = ig_user.pk_number
    ig_user_detail = api.username_info(ig_user.username)
    ig_user.follower_count = ig_user_detail.get("user").get("follower_count")
    ig_user.following_count = ig_user_detail.get("user").get("following_count")
    ig_user.biography = ig_user_detail.get("user").get("biography")
    if ig_user_detail.get("user").get("is_business") == False:
        ig_user.is_business = 0
    else:
        ig_user.is_business = 1
    ig_user.media_count = ig_user_detail.get("user").get("media_count")
    ig_user.save()
    return pk_number

def user_feed(user_pk,assistant_id):
    assistant = Assistants.objects.get(id = assistant_id)
    api = private_api.login_with_assistant(assistant_id)
    instagram_account = assistant.instagram_account
    if assistant.assistant_type == 1:
        action_name = Like_Actions
    else:
        action_name = Comment_Actions
    action = action_name.objects.get(ig_user__pk_number = user_pk)
    ig_user = action.ig_user
    relationship = action.relationship
    action.delete()
    source = assistant.source
    source_type = assistant.source_type
    user_posts = api.user_feed(user_pk).get("items")
    if len(user_posts) == 0:
        pass
    else:
        user_last_post = user_posts[0]
        post_pk = user_last_post.get("pk")
        new_action_count = action_name.objects.filter(ig_user__pk_number=user_pk,status = 1)
        if len(new_action_count)!=0:
            pass
        else:
            new_action = action_name(post_pk = post_pk,assistant = assistant,instagram_account = instagram_account,ig_user = ig_user,source = source,source_type = source_type,relationship = relationship,status = 9)
            new_action.save()

    
    
            
@shared_task
def prepare_filtered_users(assistant_id):
    assistant = Assistants.objects.filter(id =assistant_id)[0]
    assistant_type = assistant.assistant_type
    settings = private_api.read_settings(assistant_id)
    
    if assistant_type == 0:
        action_name=Follow_Actions
    elif assistant_type == 1:
        action_name=Like_Actions
    elif assistant_type == 2:
        action_name=Comment_Actions

    filtered_users = action_name.objects.filter(assistant = assistant ,status = 9)

    if len(filtered_users) >= 1:
        pass

    else:
        action = action_name.objects.filter(assistant = assistant ,status = 0)
        for i in action:
            try:
                pk_number = ig_user_detailed_info(action_name,i.id,assistant_id)
                if private_api.check_filter(settings, pk_number) == True:
                    i.status = 9
                    i.assistan = assistant
                    i.update_time = datetime.now(timezone.utc)
                    i.save()
                else: 
                    i.status = -1
                    i.assistan = assistant
                    i.update_time = datetime.now(timezone.utc)
                    i.save()
                filtered_users = action_name.objects.filter(assistant = assistant ,status = 9)
                if len(filtered_users)>=1:
                    if assistant_type == 0:
                        break
                    else:
                        user_feed(i.ig_user.pk_number,assistant_id)
                        break
                else:
                    continue
            except Exception as e:
                i.status = 2
                i.assistan = assistant
                i.update_time = datetime.now(timezone.utc)
                i.save()
                api_error = Api_Error(assistant = assistant,error_action_type = 6,api_error_mean = str(e),error_source = "prepare_filtered_users")
                api_error.save()
                break
    assistant.activity_status = 1
    assistant.update_time = datetime.now(timezone.utc)
    assistant.save()


def check_assistant_is_ready(assistant_id):
    assistant = Assistants.objects.filter(id =assistant_id)[0]
    assistant_type = assistant.assistant_type
    desired_wait = Assistants_Settings.objects.get(assistant__id=assistant_id).speed
    if assistant_type == 0:
        action_name=Follow_Actions
    elif assistant_type == 1:
        action_name=Like_Actions
    elif assistant_type == 2:
        action_name=Comment_Actions
        desired_wait+=75
    
    
    all_actions = action_name.objects.filter(assistant=assistant)
    if len(all_actions) == 0:
        return True
    else:
        latest_actions = action_name.objects.filter(assistant=assistant).order_by('-update_time')[0]
        if latest_actions.status == 9 or latest_actions.status == 1 or latest_actions.status == 0 or latest_actions.status == -1:
            if latest_actions.status == 1:
                random_waiting = random.randint(1,5)
                if (datetime.now(timezone.utc)-latest_actions.update_time).seconds >= desired_wait+random_waiting:
                    return True
                else:
                    return False
            else:
                return True
        elif latest_actions.status == 2:
            try:
                latest_actions = action_name.objects.filter(assistant=assistant).exclude(status=-1).exclude(status = 0).exclude(status=9).order_by('-update_time')[:10]
            except:
                latest_actions = action_name.objects.filter(assistant=assistant).exclude(status=-1).exclude(status = 0).exclude(status=9).order_by('-update_time')
            
            error_count = 0
            for i in latest_actions:
                if i.status == 2:
                    error_count+=1
            extra = 7200*error_count
            random_waiting = random.randint(1,5)
            if (datetime.now(timezone.utc)-latest_actions[0].update_time).seconds >= desired_wait+extra+random_waiting:
                return True
            else:
                return False

@shared_task
def executioner(assistant_id):
    assistant = Assistants.objects.filter(id =assistant_id)[0]
    assistant_type = assistant.assistant_type
    api = private_api.login_with_assistant(assistant_id)
    if assistant_type == 0:
        follow_action = Follow_Actions.objects.filter(assistant=assistant,status = 9)[0]
        ig_user = follow_action.ig_user
        pk_number = ig_user.pk_number
        try:
            api.friendships_create(pk_number)
            follow_action.status = 1
            follow_action.assistan = assistant
            follow_action.update_time = datetime.now(timezone.utc)
            follow_action.save()
        except Exception as e:
            if str(e) == "Expecting value: line 1 column 1 (char 0)":
                follow_action.status = 3
                follow_action.assistan = assistant
                follow_action.update_time = datetime.now(timezone.utc)
                follow_action.save()
            else:
                follow_action.status = 2
                follow_action.assistan = assistant
                follow_action.update_time = datetime.now(timezone.utc)
                follow_action.save()
            api_error = Api_Error(assistant = assistant,error_action_type = 7,api_error_mean = str(e),error_source = "executioner_follow")
            api_error.save()
    elif assistant_type == 1:
        like_action = Like_Actions.objects.filter(status=9)[0]
        post_pk = like_action.post_pk
        try:
            api.post_like(str(post_pk))
            like_action.status = 1
            like_action.assistan = assistant
            like_action.update_time = datetime.now(timezone.utc)
            like_action.save()
        except Exception as e:
            if str(e) == "Expecting value: line 1 column 1 (char 0)":
                like_action.status = 3
                like_action.assistan = assistant
                like_action.update_time = datetime.now(timezone.utc)
                like_action.save()
            else:
                like_action.status = 2
                like_action.assistan = assistant
                like_action.update_time = datetime.now(timezone.utc)
                like_action.save()
            api_error = Api_Error(assistant = assistant,error_action_type = 8,api_error_mean = str(e),error_source = "executioner_like")
            api_error.save()
    elif assistant_type == 2:
        comment_action = Comment_Actions.objects.filter(status=9)[0]
        post_pk = comment_action.post_pk
        comment_text = assistant.comment
        try:
            api.post_comment(str(post_pk),comment_text)
            comment_action.status = 1
            comment_action.assistan = assistant
            comment_action.update_time = datetime.now(timezone.utc)
            comment_action.save()
        except Exception as e:
            if str(e) == "Expecting value: line 1 column 1 (char 0)":
                comment_action.status = 3
                comment_action.assistan = assistant
                comment_action.update_time = datetime.now(timezone.utc)
                comment_action.save()
            else:
                comment_action.status = 2
                comment_action.assistan = assistant
                comment_action.update_time = datetime.now(timezone.utc)
                comment_action.save()
            api_error = Api_Error(assistant = assistant,error_action_type = 9,api_error_mean = str(e),error_source = "executioner_comment")
            api_error.save()
    assistant.activity_status = 1
    assistant.update_time = datetime.now(timezone.utc)
    assistant.save()

def create_action(assistant_id):
    assistant = Assistants.objects.filter(id =assistant_id)[0]
    if assistant.queue == 0:
        private_api.followers_general(assistant_id)
    elif assistant.queue == 1:
        private_api.followings_general(assistant_id)
    elif assistant.queue == 2:
        private_api.likers_general(assistant_id)
    elif assistant.queue == 3:
         private_api.commenters_general(assistant_id)
    elif assistant.queue == 4:
        private_api.commenters_general(assistant_id)
        #private_api.posters_general(assistant_id)
    else:
        pass

def is_there_enough_data(assistant_id):
    assistant = Assistants.objects.filter(id =assistant_id)[0]
    assistant_source = assistant.source
    ig_account = assistant.instagram_account

    if assistant.assistant_type == 0:
        action_name = Follow_Actions
    elif assistant.assistant_type == 1:
        action_name = Like_Actions
    elif assistant.assistant_type == 2:
        action_name = Comment_Actions
    
    if assistant.source_type == 0:
        source_name = User_Sources
    elif assistant.source_type == 1:
        source_name = Hashtag_Sources
    elif assistant.source_type == 2:
        source_name = Location_Sources
        
    
    check_action = action_name.objects.filter(assistant = assistant,status = 0)
    check_source = source_name.objects.get(instagram_account = ig_account,source = assistant_source)

    if len(check_action) == 0 and check_source.feed_max_id == 1:
        return False
    else:
        return True
    


@shared_task
def get_action_data(assistant_id):
    assistant = Assistants.objects.filter(id =assistant_id)[0]
    if assistant.queue == int(assistant.relationship[0]):
        create_action(assistant_id)
        if len(assistant.relationship)>1:
            assistant.queue = int(assistant.relationship[1])
            assistant.save()
        else:
            check_datas = is_there_enough_data(assistant_id)
            if check_datas == False:
                assistant.is_there_enough_data = 0
                assistant.activity_status = 3
            else:
                assistant.is_there_enough_data = 1
    elif assistant.queue == int(assistant.relationship[1]): 
        create_action(assistant_id)
        if len(assistant.relationship)>2:
            assistant.queue= int(assistant.relationship[2])
            assistant.save()
        else:
            check_datas = is_there_enough_data(assistant_id)
            if check_datas == False:
                assistant.is_there_enough_data = 0
                assistant.activity_status = 3
            else:
                assistant.is_there_enough_data = 1
            assistant.queue= int(assistant.relationship[0])
            assistant.save()

    elif assistant.queue == int(assistant.relationship[2]): 
        create_action(assistant_id)
        if len(assistant.relationship)>3:
            assistant.queue = int(assistant.relationship[3])
            assistant.save()
        else:
            check_datas = is_there_enough_data(assistant_id)
            if check_datas == False:
                assistant.is_there_enough_data = 0
                assistant.activity_status = 3
            else:
                assistant.is_there_enough_data = 1
            assistant.queue= int(assistant.relationship[0])
            assistant.save()

    elif assistant.queue==int(assistant.relationship[3]):
        create_action(assistant_id) 
        if len(assistant.relationship)>4:
            assistant.queue = int(assistant.relationship[4])
            assistant.save()
        else:
            check_datas = is_there_enough_data(assistant_id)
            if check_datas == False:
                assistant.is_there_enough_data = 0
                assistant.activity_status = 3
            else:
                assistant.is_there_enough_data = 1
            assistant.queue= int(assistant.relationship[0])
            assistant.save()
    elif assistant.queue==int(assistant.relationship[4]):
        check_datas = is_there_enough_data(assistant_id)
        if check_datas == False:
            assistant.is_there_enough_data = 0
            assistant.activity_status = 3
        else:
            assistant.is_there_enough_data = 1
        create_action(assistant_id) 
        assistant.queue= int(assistant.relationship[0])
        assistant.save()
    
    if assistant.activity_status == 3:
        pass
    else:
        assistant.activity_status = 1
    
    assistant.update_time = datetime.now(timezone.utc)
    assistant.save()

@task
def volta():
    #takes all assistants
    all_assistants = Assistants.objects.filter(activity_status = 1)
    for i in all_assistants:
        #select an assistant from list and check it
        assistant_time_status = check_assistant_is_ready(i.id)
        print(i.assistant_type,i.instagram_account,assistant_time_status)
        if assistant_time_status == False:
            pass
        else:
            i.activity_status = 9
            i.update_time = datetime.now(timezone.utc)
            i.save()
            assistant_type = i.assistant_type
            if assistant_type == 0:
                action_name=Follow_Actions
            elif assistant_type == 1:
                action_name=Like_Actions
            elif assistant_type == 2:
                action_name=Comment_Actions
            if len(action_name.objects.filter(assistant = i,status = 1)) >= i.number_of_actions:
                    i.activity_status = 2
                    i.save()
            else:
                current_datas = action_name.objects.filter(assistant = i,status = 0)
                if len(current_datas)==0:
                    api_errors = Api_Error.objects.filter(assistant__instagram_account__username = i.instagram_account.username).order_by('-update_time')
                    if len(api_errors)>0:
                        try:
                            api_errors = Api_Error.objects.filter(assistant__instagram_account__username = i.instagram_account.username).order_by('-update_time')[:10]
                        except:
                            pass
                        error_count = len(api_errors)
                        passing_time = (datetime.now(timezone.utc)-api_errors[0].update_time).seconds
                        print(passing_time,"GEÇEN ZAMAN",error_count,"ERROR_COUNT")
                        if passing_time >= error_count*360:
                            print("api error bekleme zamanı tamamlandı")
                            get_action_data.apply_async(queue="deneme1",args=[i.id])
                        else:
                            print("api error zamanı tamamlanmadı")
                            working_assistant = Assistants.objects.filter(id = i.id)[0]
                            working_assistant.activity_status = 1
                            working_assistant.update_time = datetime.now(timezone.utc)
                            working_assistant.save()
                    else:
                        get_action_data.apply_async(queue="deneme1",args=[i.id])

                else:
                    filtered_users = action_name.objects.filter(assistant = i ,status = 9)
                    if len(filtered_users)>=1:
                        executioner.apply_async(queue = "deneme1",args=[i.id])
                    else:
                        prepare_filtered_users.apply_async(queue="deneme1",args=[i.id])



"""Analyse Functions"""

@shared_task
def analyse_ig_account(username):
    instagram_account = Instagram_Accounts.objects.filter(username=username)[0]
    password = instagram_account.password
    
    """Instagram_Accounts_Analyse"""
    #call api
    # api=private_api.login_instagram_web_api(username,password)
    api=private_api.login_instagram(username,password)

    #Get the Post datas of the account
    user_posts = private_api.get_user_all_posts(username,api)
    like_count = private_api.get_like_count(user_posts)
    comment_count = private_api.get_comment_count(user_posts)

    #Get the general datas of the account
    info = api.username_info(username)
    user_pk=info.get('user').get('pk')
    username=info.get('user').get('username')
    full_name=info.get('user').get('full_name')
    is_private=info.get('user').get('is_private')
    profile_pic_url=info.get('user').get('profile_pic_url')
    media_count=info.get('user').get('media_count')
    follower_count=info.get('user').get('follower_count')
    following_count=info.get('user').get('following_count')
    biography=info.get('user').get('biography')
    is_business=info.get('user').get('is_business')
   
    #Create a new IG_Account Analysis Object and Save
    ig_account_analysis = Instagram_Accounts_Analyse(instagram_account=instagram_account, media_count=media_count,like_count=like_count,comment_count=comment_count,follower_count=follower_count,following_count=following_count,update_time=datetime.now(timezone.utc))
    ig_account_analysis.save()
    


    #Update instagram account object with the new datas 
    instagram_account.full_name = full_name
    instagram_account.is_private= is_private
    instagram_account.profile_pic_url= profile_pic_url
    instagram_account.biography= biography
    instagram_account.is_business = is_business
    instagram_account.save()
    

    """AnalyseFF Part"""
    #Get List of User Followers
    user_followers = []
    rank_token=api.generate_uuid()
    next_max_id =''
    user_pk = private_api.get_user_pk(username,api)
    results = api.user_followers(user_pk,rank_token)
    user_followers.extend(results.get('users', []))

    next_max_id = results.get('next_max_id')
    while next_max_id:
        results = api.user_followers(user_pk,rank_token,max_id = next_max_id)
        user_followers.extend(results.get('users', []))
        next_max_id = results.get('next_max_id')

    #User Followers Analyses /
    for i in user_followers: 
        pk = i.get('pk')
        username = i.get('username')
        full_name = i.get('full_name')
        is_private = i.get('is_private')
        profile_pic_url = i.get('profile_pic_url')
        has_anonymous_profile_picture = i.get('has_anonymous_profile_picture')

        #Check IG_Users object if not exist create one.
        try:
            user_object = IG_Users.objects.filter(username = username)[0]
            user_object.pk_number = pk 
            user_object.full_name =full_name
            user_object.is_private=is_private
            user_object.profile_pic_url=profile_pic_url
            user_object.has_anonymous_profile_picture=has_anonymous_profile_picture
            user_object.save()

        except:
            user_object = IG_Users(username = username,pk_number=pk,full_name =full_name,is_private=is_private,profile_pic_url=profile_pic_url,has_anonymous_profile_picture=has_anonymous_profile_picture)
            user_object.save()
        
        #Check if there is an analyse ff objects for this user
        try:
            user = Analyse_FF.objects.filter(instagram_account=instagram_account,ig_user = user_object)[0]
            if not user.is_follower == 1:
                user.is_follower = 1
                user.follower_update_time = datetime.now(timezone.utc)
                user.save()

        except:
            Analyse=Analyse_FF(instagram_account=instagram_account,ig_user = user_object,is_follower=1,is_following = 0,follower_update_time = datetime.now(timezone.utc))
            Analyse.save()

    #Get List of User Followings
    user_followings = []
    rank_token=api.generate_uuid()
    next_max_id =''
    results = api.user_following(user_pk,rank_token)
    user_followings.extend(results.get('users', []))

    next_max_id = results.get('next_max_id')
    while next_max_id:
        results = api.user_following(user_pk,rank_token,max_id = next_max_id)
        user_followings.extend(results.get('users', []))
        next_max_id = results.get('next_max_id')
    
    #User Followings Analyses /
    for i in user_followings: 
        pk = i.get('pk')
        username = i.get('username')
        full_name = i.get('full_name')
        is_private = i.get('is_private')
        profile_pic_url = i.get('profile_pic_url')
        has_anonymous_profile_picture = i.get('has_anonymous_profile_picture')

        #Check IG_Users object if not exist create one.
        try:
            user_object = IG_Users.objects.get(username = username)
            user_object.pk_number = pk 
            user_object.full_name =full_name
            user_object.is_private=is_private
            user_object.profile_pic_url=profile_pic_url
            user_object.has_anonymous_profile_picture=has_anonymous_profile_picture
            user_object.save()

        except:
            user_object = IG_Users(username = username,pk_number=pk, full_name =full_name,is_private=is_private,profile_pic_url=profile_pic_url,has_anonymous_profile_picture=has_anonymous_profile_picture)
            user_object.save()
        
        #Check if there is an analyse ff objects for this user
        try:
            user = Analyse_FF.objects.filter(instagram_account=instagram_account,ig_user = user_object)[0]
            if not user.is_following == 1:
                user.is_following = 1
                user.following_update_time = datetime.now(timezone.utc)
                user.save()

        except:
            Analyse=Analyse_FF(instagram_account=instagram_account,ig_user = user_object,is_following=1,is_follower = 0,following_update_time = datetime.now(timezone.utc))
            Analyse.save() 




    #New unFF's 
    followers_list = []
    followings_list = []

    for i in user_followers:
        followers_list.append(i.get('username'))
    for i in user_followings:
        followings_list.append(i.get('username'))

    for i in Analyse_FF.objects.filter(instagram_account =instagram_account,is_follower = 1):
        if not i.ig_user.username in followers_list:
            i.is_follower = 2
            i.follower_update_time=datetime.now(timezone.utc)
            i.save()
    for i in Analyse_FF.objects.filter(instagram_account =instagram_account,is_following = 1):
        if not i.ig_user.username in followings_list:
            i.is_following = 2
            i.following_update_time=datetime.now(timezone.utc)
            i.save()

@task
def Analyse_Beat():
    for i in Instagram_Accounts.objects.filter():
        iaa = Instagram_Accounts_Analyse.objects.filter(instagram_account = i)
        if len(iaa) ==0:
            analyse_ig_account.apply_async(queue="deneme1",args=[i.username])
        elif datetime.now(timezone.utc)-iaa.latest("update_time").update_time >= timedelta(days=1):
            analyse_ig_account.apply_async(queue="deneme1",args=[i.username])
        else:
            continue
