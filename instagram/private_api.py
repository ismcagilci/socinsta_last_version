import json
import codecs
from datetime import datetime, timezone,timedelta
now = datetime.now(timezone.utc)
import os.path
import logging
import argparse
from aristo.models import *
from .tasks import *
import urllib.request
from aristo.models import *

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

from django.contrib.auth.models import User
from .challenge_required import (MyAppClient)
import instagram_web_api
from instagram_web_api import Client, ClientCompatPatch, ClientError, ClientLoginError
import hashlib
import string
import random
#from .selenium_insta import this_was_me



try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object



def check_is_real(main_user,username, password,challenge_code,sms_or_mail):
    if username == "" or password == "":
        return 10
    elif sms_or_mail == 2:
        try:
            new_api = Client(username = username, password = password,proxy="https://wahow:i159753@64.227.107.38:3128")
            deneme = new_api.username_info(username)
            print(deneme)
            print("oğğğğğğğğ")
            return new_api
        except Exception as e:
            if e.args[0] == "invalid_user":
                # 1 = Böyle bir kullanıcı bulunamadı
                return 1
            elif e.args[0] == "bad_password":
                # 2 = Yanlış şifre
                return 2
            elif e.args[0] == "sentry_block":
                return 3
            elif e.args[0] == "checkpoint_challenge_required":
                return 6
            elif e.args[0] == "rate_limit_error":
                return 11
            print(e.args[0],"jajdajsdj")
    else:
        if challenge_code == 2:
            new_api = MyAppClient(username = username, password = password, challenge_code = challenge_code,sms_or_mail=sms_or_mail,proxy="https://wahow:i159753@64.227.107.38:3128")
            return 8
        else:
            try:
                new_api = MyAppClient(username = username, password = password, challenge_code = challenge_code,sms_or_mail=sms_or_mail,proxy="https://wahow:i159753@64.227.107.38:3128")
                deneme = new_api.username_info(username)
                return new_api
            except urllib.error.HTTPError as err:
                if err.code == 400:
                        #status_cr = this_was_me(username,password)
                        #if status_cr == True:
                            #return 4
                        #else:
                    return 9
            except Exception as e:
               
                if e.args[0] == "login_required":
                    return 5
            except:
                return 7
        

            # Patladı , hesabını telden yada mailden onaylaması lazım
            

def create_cookie_web_api(cache_settings, username):
    insta_user = Instagram_Accounts.objects.get(username=username)
    cookie = cache_settings.get("cookie")
    cache_settings.__delitem__("cookie")
    json_settings = json.dumps(cache_settings)
    new_settings = Api_Settings_web_api(instagram_account=insta_user, cookie=cookie, settings=json_settings)
    new_settings.save()



def create_cookie(cache_settings, username,rank_token):
    # Eski onlogin_callback fonksiyonu. Cookie yoksa onu kaydediyor sadece. O yüzden ismini değiştirdim.
    insta_user = Instagram_Accounts.objects.get(username=username)
    cookie = cache_settings.get("cookie")
    cache_settings.__delitem__("cookie")
    json_settings = json.dumps(cache_settings)
    new_settings = Api_Settings(instagram_account=insta_user, cookie=cookie, settings=json_settings,rank_token=rank_token)
    new_settings.save()

def login_instagram_web_api(username,password):

    class MyClient(instagram_web_api.Client):

        @staticmethod
        def _extract_rhx_gis(html):
            options = string.ascii_lowercase + string.digits
            text = ''.join([random.choice(options) for _ in range(8)])
            return hashlib.md5(text.encode()).hexdigest()

        def login(self):
            """Login to the web site."""
            if not self.username or not self.password:
                raise ClientError('username/password is blank')

            time = str(int(datetime.now().timestamp()))
            enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{time}:{self.password}"

            params = {'username': self.username, 'enc_password': enc_password, 'queryParams': '{}', 'optIntoOneTap': False}
            self._init_rollout_hash()
            login_res = self._make_request('https://www.instagram.com/accounts/login/ajax/', params=params)
            if not login_res.get('status', '') == 'ok' or not login_res.get ('authenticated'):
                raise ClientLoginError('Unable to login')

            if self.on_login:
                on_login_callback = self.on_login
                on_login_callback(self)
            return login_res
    # class Web_Api(instagram_web_api.Client):
    #     @staticmethod
    #     def _extract_rhx_gis(html):
    #         options = string.ascii_lowercase + string.digits
    #         text = ''.join([random.choice(options) for _ in range(8)])
    #         return hashlib.md5(text.encode()).hexdigest()
    api_settings = Api_Settings_web_api.objects.filter(instagram_account__username=username)
    try:
        if len(api_settings) == 0:
            api = MyClient(auto_patch=True, authenticate=True,
    username=username, password=password,proxy="https://wahow:i159753@64.227.107.38:3128")
            create_cookie_web_api(api.settings, username)
        else:
            settings = api_settings[0].settings
            cookie = api_settings[0].cookie
            settings = json.loads(settings)
            settings["cookie"] = cookie
            api = MyClient(auto_patch=True, authenticate=True,
    username=username, password=password,settings = settings,proxy="https://wahow:i159753@64.227.107.38:3128")
    except:
        # Login expired
        # Do relogin but use default ua, keys and such
        Api_Settings.objects.filter(instagram_account__username=username).delete()
        api = MyClient(auto_patch=True, authenticate=True,
    username=username, password=password,proxy="https://wahow:i159753@64.227.107.38:3128")
        create_cookie_web_api(api, username)

    return api

def login_instagram(username, password):
    device_id = None
    api_settings = Api_Settings.objects.filter(instagram_account__username=username)
    try:
        if len(api_settings) == 0:
            api = Client(username, password,proxy="https://wahow:i159753@64.227.107.38:3128")
            rank_token = Client.generate_uuid()
            create_cookie(api.settings, username, rank_token)

        else:
            settings = api_settings[0].settings
            cookie = api_settings[0].cookie
            settings = json.loads(settings)
            settings["cookie"] = cookie
            device_id = settings.get('device_id')
            api = Client(
                username, password,
                settings=settings,proxy="https://wahow:i159753@64.227.107.38:3128")

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        Api_Settings.objects.filter(instagram_account__username=username).delete()
        api = Client(username, password, device_id=device_id,proxy="https://wahow:i159753@64.227.107.38:3128")
        rank_token = Client.generate_uuid()
        create_cookie(api, username,rank_token)

    return api

def login_with_assistant_web_api(assistant_id):
    ig_account = Assistants.objects.filter(id=assistant_id)[0].instagram_account
    username = ig_account.username
    password = ig_account.password
    api = login_instagram_web_api(username,password)
    return api

def login_with_assistant(assistant_id):
    ig_account = Assistants.objects.filter(id=assistant_id)[0].instagram_account
    username = ig_account.username
    password = ig_account.password
    api = login_instagram(username,password)
    return api


#Get user pk with username and api 
def get_user_pk(username, api):
    try:
        info = api.username_info(username)
        pk = info.get("user").get("pk")
    except Exception as e:
        active_ig_account = Instagram_Accounts.objects.filter(username = username)[0]
        api_error = Api_Error(error_action_type = 10,api_error_mean = str(e),error_source = "get_user_pk",instagram_account=active_ig_account)
        api_error.save()
        pk = 0
    return pk



#Get all posts of a user
def get_user_all_posts(username, api):
    user_pk = get_user_pk(username, api)
    rank_token = api.generate_uuid()

    user_posts = []
    try:
        results = api.user_feed(user_pk, rank_token=rank_token)
        user_posts.extend(results.get('items', []))
        next_max_id = results.get('next_max_id')
        while next_max_id:
            results = api.user_feed(user_pk, rank_token=rank_token, max_id=next_max_id)
            user_posts.extend(results.get('items', []))
            next_max_id = results.get('next_max_id')
        return user_posts
    except Exception as e:
        active_ig_account = Instagram_Accounts.objects.filter(username=username)[0]
        api_error = Api_Error(instagram_account=active_ig_account,error_action_type = 5,api_error_mean = str(e),error_source = "get user all posts")
        api_error.save()

def get_like_count(user_posts):
    like_count = 0
    for i in user_posts:
        like_count += i.get("like_count")
    return like_count


def get_comment_count(user_posts):
    comment_count = 0
    for i in user_posts:
        comment_count += i.get("comment_count")
    return comment_count


#Check Assistant Sources are exist and create one!
def check_sources(ig_accounts_username, source, source_type):
    ig_account = Instagram_Accounts.objects.get(username=ig_accounts_username)
    if source_type == 'user':
        try:
            source = User_Sources.objects.filter(instagram_account=ig_account,source=source)[0]
        except:
            new_user_source = User_Sources(instagram_account=ig_account, source=source)
            new_user_source.save()

    elif source_type == 'hashtag':
        try:
            source = Hashtag_Sources.objects.filter(instagram_account=ig_account, source=source)[0]
        except:
            new_user_source = Hashtag_Sources(instagram_account=ig_account, source=source)
            new_user_source.save()

    elif source_type == 'location':
        try:
            source = Location_Sources.objects.filter(instagram_account=ig_account, source=source)[0]
        except:
            new_user_source = Location_Sources(instagram_account=ig_account, source=source)
            new_user_source.save()


#Create New IG User and Update if it has been already exists.
def create_ig_user(user):
    pk_number = user.get('pk')
    username = user.get('username')
    full_name = user.get('full_name')
    is_private = user.get('is_private')
    profile_pic_url = user.get('profile_pic_url')
    has_anonymous_profile_picture = user.get('has_anonymous_profile_picture')

    #Check IG_Users object if not exist create one.
    try:
        user_object = IG_Users.objects.get(username = username)
        user_object.pk_number = pk_number 
        user_object.full_name =full_name
        user_object.is_private=is_private
        user_object.profile_pic_url=profile_pic_url
        user_object.has_anonymous_profile_picture=has_anonymous_profile_picture
        user_object.save()

    except:
        user_object = IG_Users(username = username,pk_number=pk_number, full_name =full_name,is_private=is_private,profile_pic_url=profile_pic_url,has_anonymous_profile_picture=has_anonymous_profile_picture)
        user_object.save()

    return user_object

def update_ig_user(pk_number,api):
    user = api.user_info(pk_number).get('user')
    user_object = IG_Users.objects.filter(pk_number = pk_number)[0]
    user_object.username = user.get('username')
    user_object.full_name = user.get('full_name')
    user_object.pk_number = user.get('pk')
    user_object.profile_pic_url = user.get('profile_pic_url')
    user_object.follower_count = user.get('follower_count')
    user_object.following_count = user.get('following_count')
    user_object.biography = user.get('biography')
    user_object.is_business = user.get('is_business')
    user_object.is_private = user.get('is_private')
    user_object.has_anonymous_profile_picture = user.get('has_anonymous_profile_picture')
    user_object.media_count = user.get('media_count')
    user_object.save()

    return user_object



#Create New IG Post and Update if it has been already exists.


#Check repeated actions and make them unique
def check_user_actions(raw_results, assistant_id):
    
    assistant = Assistants.objects.filter(id=assistant_id)[0]
    assistant_type = assistant.assistant_type
    instagram_account = assistant.instagram_account
    #new follow action fiels
    source_type=raw_results.get("source_type")
    relationship=raw_results.get("relationship")
    source=raw_results.get("source")

    if assistant_type == 0:
        action_name = Follow_Actions
    elif assistant_type == 1:
        action_name = Like_Actions
    else:
        action_name = Comment_Actions
    
    results = raw_results.get("users")
    if bool(results) == False:
        results = raw_results.get("comments")
        if bool(results) == False:
            pass
        else:
            for i in results:
                all_api_errors = Api_Error.objects.filter(assistant__instagram_account__username = assistant.instagram_account.username).order_by('-update_time')
                if len(all_api_errors) == 0:
                    i = i.get("user")
                    actions_count = len(action_name.objects.filter(ig_user__username =i.get('username'), instagram_account = instagram_account))
                    if actions_count == 0:
                        user_pk = i.get("pk")
                        api = login_with_assistant(assistant_id)
                        try:
                            friendship_status = api.friendships_show(user_pk)
                            if friendship_status.get("following") == True or friendship_status.get("followed_by") == True:
                                pass
                            else:
                                user = create_ig_user(i)
                                new_action = action_name(instagram_account=instagram_account,assistant=assistant,ig_user=user,source=source,relationship=relationship,source_type=source_type,status=0,update_time=datetime.now(timezone.utc))
                                new_action.save()
                        except Exception as e:
                            api_error = Api_Error(instagram_account = instagram_account,error_action_type = 5,api_error_mean = str(e),error_source = "check_user_actions")
                            api_error.save()
                    else:
                        pass
                else:
                    error_count = len(all_api_errors)
                    passing_time = (datetime.now(timezone.utc)-all_api_errors[0].update_time).seconds
                    if passing_time >= error_count*360:
                        i = i.get("user")
                        actions_count = len(action_name.objects.filter(ig_user__username =i.get('username'), instagram_account = instagram_account))
                        if actions_count == 0:
                            user_pk = i.get("pk")
                            api = login_with_assistant(assistant_id)
                            try:
                                friendship_status = api.friendships_show(user_pk)
                                if friendship_status.get("following") == True or friendship_status.get("followed_by") == True:
                                    pass
                                else:
                                    user = create_ig_user(i)
                                    new_action = action_name(instagram_account=instagram_account,assistant=assistant,ig_user=user,source=source,relationship=relationship,source_type=source_type,status=0,update_time=datetime.now(timezone.utc))
                                    new_action.save()
                            except Exception as e:
                                api_error = Api_Error(instagram_account = instagram_account,error_action_type = 5,api_error_mean = str(e),error_source = "check_user_actions")
                                api_error.save()
                        else:
                            pass
                    else:
                        pass

    else:
        for i in results:
            all_api_errors = Api_Error.objects.filter(assistant__instagram_account__username = assistant.instagram_account.username).order_by('-update_time')
            if len(all_api_errors) == 0:
                actions_count = len(action_name.objects.filter(ig_user__username =i.get('username'), instagram_account = instagram_account))
                if actions_count == 0:
                    user_pk = i.get("pk")
                    api = login_with_assistant(assistant_id)
                    try:
                        friendship_status = api.friendships_show(user_pk)
                        if friendship_status.get("following") == True or friendship_status.get("followed_by") == True:
                            pass
                        else:
                            user = create_ig_user(i)
                            new_action = action_name(instagram_account=instagram_account,assistant=assistant,ig_user=user,source=source,relationship=relationship,source_type=source_type,status=0,update_time=datetime.now(timezone.utc))
                            new_action.save()
                    except Exception as e:
                        api_error = Api_Error(instagram_account = instagram_account,error_action_type = 4,api_error_mean = str(e),error_source = "check_user_actions2")
                        api_error.save()
                else:
                    pass
            else:
                error_count = len(all_api_errors)
                passing_time = (datetime.now(timezone.utc)-all_api_errors[0].update_time).seconds
                if passing_time >= error_count*360:
                    actions_count = len(action_name.objects.filter(ig_user__username =i.get('username'), instagram_account = instagram_account))
                    if actions_count == 0:
                        user_pk = i.get("pk")
                        api = login_with_assistant(assistant_id)
                        try:
                            friendship_status = api.friendships_show(user_pk)
                            if friendship_status.get("following") == True or friendship_status.get("followed_by") == True:
                                pass
                            else:
                                user = create_ig_user(i)
                                new_action = action_name(instagram_account=instagram_account,assistant=assistant,ig_user=user,source=source,relationship=relationship,source_type=source_type,status=0,update_time=datetime.now(timezone.utc))
                                new_action.save()
                        except Exception as e:
                            api_error = Api_Error(instagram_account = instagram_account,error_action_type = 4,api_error_mean = str(e),error_source = "check_user_actions2")
                            api_error.save()
                    else:
                        pass
                else:
                    pass


                



"""<<DATA FUNCTİONS>>"""
 
#fonksiyonlar
 
"""
    + 1- user followers  
    + 2- user followings 
    +/3- user likers
    +/ 4- user commenters 
    5- hashtag likers
    6- hashtag commenters
    7- hashtag posters    
"""       

def get_user_followings_simple(assistant_id):
    api = private_api.login_with_assistant(assistant_id = assistant_id)
    username = Assistants.objects.filter(id = assistant_id)[0].instagram_account.username
    user_id = get_user_pk(username, api)
    rt = api.generate_uuid()
    user_followings = []
    try:
        results = api.user_following(user_id, rank_token=rt)
        user_followings.extend(results.get('users', []))
        next_max_id = results.get('next_max_id')
        while next_max_id:
            results = api.user_following(user_id, rank_token=rt,next_max_id = next_max_id)
            user_followings.extend(results.get('users', []))
            next_max_id = results.get('next_max_id')
        return user_followings
    except Exception as e:
        assistant = Assistants.objects.filter(id = assistant_id)[0]
        api_error = Api_Error(instagram_account = instagram_account,error_action_type = 12,api_error_mean = str(e),error_source = "get_user_followings_simple")
        api_error.save()
        return False


#Get 200 followings of a user
def get_user_followers(rank_token, username, api, max_id,assistant):
    try:
        user_id = get_user_pk(username, api)
        if bool(max_id) == True:
            results = api.user_followers(user_id, rank_token=rank_token, max_id=max_id)
        else:
            results = api.user_followers(user_id, rank_token=rank_token)
        return results
    except Exception as e:
        api_error = Api_Error(instagram_account = instagram_account,error_action_type = 0,api_error_mean = str(e),error_source = "get_user_followers")
        api_error.save()
        return False

#Get 200 followings of a user
def get_user_followings(rank_token, username, api, max_id,assistant):
    try:
        user_id = get_user_pk(username, api)
        if bool(max_id) == True:
            results = api.user_following(user_id, rank_token=rank_token, max_id=max_id)
        else:
            results = api.user_following(user_id, rank_token=rank_token)
        return results
    except Exception as e:
        api_error = Api_Error(instagram_account = instagram_account,error_action_type = 1, api_error_mean= str(e),error_source = "get_user_followings")
        api_error.save()
        return False

#Get 18 posts of a user
def get_user_posts(rank_token, username, api, max_id,assistant):
    try:
        user_pk = get_user_pk(username, api)
        
        if bool(max_id) == True:
            results = api.user_feed(user_pk, rank_token=rank_token, max_id=max_id)
        else:
            results = api.user_feed(user_pk, rank_token=rank_token)
        return results
    except Exception as e:
        api_error = Api_Error(instagram_account = instagram_account,error_action_type = 5,api_error_mean= str(e),error_source = "get_user_posts")
        api_error.save()
        return False

#Get 18 posts of a hashtag
def get_hashtag_posts(rank_token, hashtag, api, max_id,assistant):
    try:
        if bool(max_id) == True:
            results = api.feed_tag(hashtag,rank_token,next_max_id=max_id)
        else:
            results = api.feed_tag(hashtag,rank_token)
        return results
    except Exception as e:
        api_error = Api_Error(instagram_account = assistant.instagram_account,error_action_type = 4,api_error_mean= str(e),error_source = "get_hashtag_posts")
        api_error.save()
        return False

def get_post_likers(next_post_id,api,assistant):
    try:
        results = api.media_likers(next_post_id)
        return results
    except Exception as e:
        api_error = Api_Error(instagram_account = assistant.instagram_account,error_action_type = 2,api_error_mean= str(e),error_source = "get_post_likers")
        api_error.save()
        return False


def get_post_commenters(next_post_id,api,post_data,assistant):
    commenters_max_id = post_data.commenters_max_id
    try:
        results = api.media_comments(next_post_id,max_id = commenters_max_id)
        next_max_id = results.get("next_max_id")
        if next_max_id:
            post_data.commenters_max_id = next_max_id
        else:
            post_data.commenters = 1
        post_data.save()
        return results
    except Exception as e:
        api_error = Api_Error(instagram_account = assistant.instagram_account,error_action_type = 3,api_error_mean= str(e),error_source = "get_post_commenters")
        api_error.save()
        return False


def posters_general(assistant_id):
    pass

def likers_general(assistant_id):
    assistant = Assistants.objects.filter(id=assistant_id)[0]
    api_settings = Api_Settings.objects.get(instagram_account=assistant.instagram_account)
    rank_token = api_settings.rank_token
    api = login_with_assistant(assistant_id)
    source_type = assistant.source_type
    instagram_account = assistant.instagram_account

    user_hashtag_location = assistant.source

    if source_type == 0:
        source_name = User_Sources
    elif source_type == 1:
        source_name = Hashtag_Sources
    else:
        source_name = Location_Sources
    user_hashtag_location_sources = source_name.objects.get(instagram_account = instagram_account,source = user_hashtag_location)
    feed_max_id = user_hashtag_location_sources.feed_max_id
    if feed_max_id == '1':
        pass
    else:
        post_datas = Post_Datas.objects.filter(instagram_account = instagram_account,likers = 0,source = user_hashtag_location)
        if len(post_datas) == 0:
            if source_type == 0:
                results = get_user_posts(rank_token, user_hashtag_location, api, feed_max_id,assistant)
            elif source_type == 1 or source_type == 2:
                results = get_hashtag_posts(rank_token, user_hashtag_location, api, feed_max_id,assistant)
            if results == False:
                pass
            else:
                items = results.get('items')
                for i in items:
                    try:
                        Post_Datas.objects.filter(instagram_account=instagram_account, post_pk=i.get('pk'))[0]
                    except:
                        new_POST = Post_Datas(instagram_account=instagram_account, source_type=source_type, source=user_hashtag_location,
                                                post_pk=i.get('pk'), likers=0, commenters=0,posters=0)
                        new_POST.save()
                if results.get('next_max_id'):
                    user_hashtag_location_sources.feed_max_id=results.get('next_max_id')
                else:
                    user_hashtag_location_sources.feed_max_id=1
                user_hashtag_location_sources.save()
                current_post = Post_Datas.objects.filter(instagram_account = instagram_account,likers = 0,source = user_hashtag_location)
                if len(current_post) == 0:
                    pass
                else:
                    current_post = current_post[0]
                    likers = get_post_likers(current_post.post_pk, api,assistant)
                    if likers == False:
                        current_post.delete()
                    else:
                        likers['source_type'] = source_type
                        likers['relationship'] = 2
                        likers['source'] = user_hashtag_location
                        check_user_actions(likers, assistant_id)
                        current_post.likers = 1
                        current_post.save()
        else:
            current_post = post_datas[0]
            likers = get_post_likers(current_post.post_pk, api,assistant)
            if likers == False:
                current_post.delete()
            else:
                likers['source_type'] = source_type
                likers['relationship'] = 2
                likers['source'] = user_hashtag_location
                check_user_actions(likers, assistant_id)
                current_post.likers = 1
                current_post.save()



def commenters_general(assistant_id):
    assistant = Assistants.objects.filter(id=assistant_id)[0]
    api_settings = Api_Settings.objects.get(instagram_account=assistant.instagram_account)
    rank_token = api_settings.rank_token
    api = login_with_assistant(assistant_id)
    source_type = assistant.source_type
    instagram_account = assistant.instagram_account

    user_hashtag_location = assistant.source

    if source_type == 0:
        source_name = User_Sources
    elif source_type == 1:
        source_name = Hashtag_Sources
    else:
        source_name = Location_Sources
    user_hashtag_location_sources = source_name.objects.get(instagram_account = instagram_account,source = user_hashtag_location)
    feed_max_id = user_hashtag_location_sources.feed_max_id
    if feed_max_id == '1':
        pass
    else:
        post_datas = Post_Datas.objects.filter(instagram_account = instagram_account,likers = 0)
        if len(post_datas) == 0:
            if source_type == 0:
                results = get_user_posts(rank_token, user_hashtag_location, api, feed_max_id,assistant)
            elif source_type == 1 or source_type == 2:
                results = get_hashtag_posts(rank_token, user_hashtag_location, api, feed_max_id,assistant)
            if results == False:
                pass
            else:
                items = results.get('items')
                for i in items:
                    try:
                        Post_Datas.objects.filter(instagram_account=instagram_account, post_pk=i.get('pk'))[0]
                    except:
                        new_POST = Post_Datas(instagram_account=instagram_account, source_type=0, source=user_hashtag_location,
                                                post_pk=i.get('pk'), likers=0, commenters=0,posters=0)
                        new_POST.save()
                if results.get('next_max_id'):
                    source_name.objects.filter(instagram_account=instagram_account, source=user_hashtag_location).update(
                        feed_max_id=results.get('next_max_id'))
                else:
                    source_name.objects.filter(instagram_account=instagram_account, source=user_hashtag_location).update(
                        feed_max_id=1)
                current_post = Post_Datas.objects.filter(instagram_account = instagram_account,commenters = 0)
                if len(current_post) == 0:
                    user_hashtag_location_sources.feed_max_id = 1
                    user_hashtag_location_sources.save()
                else:
                    current_post = post_datas[0]
                    comments = get_post_commenters(current_post.post_pk, api,current_post,assistant)
                    if comments == False:
                        current_post.delete()
                    else:
                        comments['source_type'] = source_type
                        comments['relationship'] = 3
                        comments['source'] = user_hashtag_location
                        check_user_actions(comments, assistant_id)
                        new_feed_max_id = comments.get("next_max_id")
                        if new_feed_max_id == None:
                            current_post.commenters = 1
                        else:
                            current_post.commenters_max_id = new_feed_max_id
                        current_post.save()
        else:
            current_post = post_datas[0]
            comments = get_post_commenters(current_post.post_pk, api,current_post,assistant)
            if comments == False:
                
                current_post.delete()
            else:
                comments['source_type'] = source_type
                comments['relationship'] = 3
                comments['source'] = user_hashtag_location
                check_user_actions(comments, assistant_id)
                new_feed_max_id = comments.get("next_max_id")
                if new_feed_max_id == None:
                    current_post.commenters = 1
                else:
                    current_post.commenters_max_id = new_feed_max_id
                current_post.save()
        


    
def followers_general(assistant_id):
    assistant = Assistants.objects.filter(id =assistant_id)[0]

    instagram_account = Assistants.objects.filter(id=assistant_id)[0].instagram_account
    username = assistant.source
    api_settings = Api_Settings.objects.get(instagram_account=assistant.instagram_account)
    rank_token = api_settings.rank_token
    api = login_with_assistant(assistant_id)
    max_ids = User_Sources.objects.filter(instagram_account=instagram_account,source=username)[0]
    followers_max_id = max_ids.followers_max_id
    if followers_max_id=='1':
        pass
    else:
        results = get_user_followers(rank_token, username, api, followers_max_id,assistant) 
        if results == False:
            pass
        else:
            results['source_type'] = 0
            results['relationship'] = 0
            results['source'] = username
            check_user_actions(results, assistant_id)
            if results.get('next_max_id'):
                User_Sources.objects.filter(instagram_account=instagram_account,source=username).update(followers_max_id=results.get('next_max_id'))
            else:
                User_Sources.objects.filter(instagram_account=instagram_account,source=username).update(followers_max_id=1)
     
    

def followings_general(assistant_id):
    assistant = Assistants.objects.filter(id =assistant_id)[0]

    instagram_account = Assistants.objects.filter(id=assistant_id)[0].instagram_account
    username = assistant.source
    api_settings = Api_Settings.objects.get(instagram_account=assistant.instagram_account)
    rank_token = api_settings.rank_token
    api = login_with_assistant(assistant_id)
    max_ids = User_Sources.objects.filter(instagram_account=instagram_account)[0]
    followings_max_id = max_ids.followings_max_id
    if followings_max_id=='1':
        pass
    else:
        results = get_user_followings(rank_token, username, api, followings_max_id,assistant)
        if results == False:
            pass
        else:
            results['source_type'] = 0
            results['relationship'] = 1
            results['source'] = username
            check_user_actions(results, assistant_id)
            if results.get('next_max_id'):
                User_Sources.objects.filter(instagram_account=instagram_account,source=username).update(followings_max_id=results.get('next_max_id'))
            else:
                User_Sources.objects.filter(instagram_account=instagram_account,source=username).update(followings_max_id=1)
     





#Filters



#Read all assistant settings and return them as a dict. 
def read_settings(assistant_id):
    
    assistant_settings = Assistants_Settings.objects.get(assistant__id=assistant_id)
    settings = {}
    settings["max_followers"]=assistant_settings.max_followers
    settings["min_followers"]=assistant_settings.min_followers
    settings["min_followings"]=assistant_settings.min_followings
    settings["max_followings"]=assistant_settings.max_followings
    settings["min_posts"]=assistant_settings.min_posts
    settings["max_posts"]=assistant_settings.max_posts
    if assistant_settings.biography == None:
        assistant_settings.biography = 0
    settings["biography"]=assistant_settings.biography
    if assistant_settings.is_private == None:
        assistant_settings.biography = 0
    settings["is_private"]=assistant_settings.is_private
    if assistant_settings.is_business == None:
        assistant_settings.biography = 0
    settings["is_business"]=assistant_settings.is_business
    if assistant_settings.has_anonymous_profile_picture == None:
        assistant_settings.biography = 0
    settings["has_anonymous_profile_picture"]=assistant_settings.has_anonymous_profile_picture
    assistant_settings.save()

    return settings

#Filter user with settings
def check_filter(settings, pk_number):
    user = IG_Users.objects.filter(pk_number=pk_number)[0]

    if settings['is_private']==1 and user.is_private==1:
        return True

    if not settings['min_followers'] < user.follower_count < settings['max_followers']:
        return False

    if not settings['min_followings'] < user.following_count < settings['max_followings']:
        return False

    if not settings['min_posts'] < user.media_count < settings['max_posts']:
        return False

    if settings['biography']==0 and len(user.biography)==0:
        return False
    
    if settings['is_private']==0 and user.is_private==1:
        return False
    
    if settings['is_business']==0 and user.is_business==1:
        return False

    if settings['has_anonymous_profile_picture']==0 and user.has_anonymous_profile_picture == 1:
        return False

    return True 