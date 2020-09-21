from aristo.models import * 


@shared_task
def analyse_ig_account(username):
    instagram_account = Instagram_Accounts.objects.filter(username=username)[0]
    
    """Instagram_Accounts_Analyse"""
    #call api
    api=private_api.login_instagram(username,password)

    #Get the Post datas of the account
    user_posts = private_api.get_user_all_posts(username,api)
    like_count = private_api.get_like_count(user_posts)
    comment_count = private_api.get_comment_count(user_posts)

    #Get the general datas of the account
    info = api.username_info('bedriyan0')
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
    ig_account_analysis = Instagram_Accounts_Analyse(instagram_account=IG_Account, media_count=media_count,like_count=like_count,comment_count=comment_count,follower_count=follower_count,following_count=following_count,update_time=datetime.now(timezone.utc))
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
    results = private_api.get_user_followers(rank_token, username, api, next_max_id)
    user_followers.extend(results.get('users', []))

    next_max_id = results.get('next_max_id')
    while next_max_id:
        results = private_api.get_user_followers(rank_token, 'bedriyan0', api,next_max_id)
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
            user = Anayse_FF.objects.filter(instagram_account=instagram_account,ig_user = user_object)[0]
            if not user.is_follower == 1:
                user.is_follower = 1
                user.follower_update_time = datetime.now(timezone.utc)
                user.save()

        except:
            Analyse=Analyse_FF(instagram_account=instagram_account,ig_user = user_object,is_follower=1,follower_update_time = datetime.now(timezone.utc))
            Analyse.save() 


    #Get List of User Followings
    user_followings = []
    rank_token=api.generate_uuid()
    next_max_id =''
    results = private_api.get_user_followings(rank_token, username, api, next_max_id)
    user_followings.extend(results.get('users', []))

    next_max_id = results.get('next_max_id')
    while next_max_id:
        results = private_api.get_user_followings(rank_token, username, api,next_max_id)
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
            user = Anayse_FF.objects.filter(instagram_account=instagram_account,ig_user = user_object)[0]
            if not user.is_following == 1:
                user.is_following = 1
                user.following_update_time = datetime.now(timezone.utc)
                user.save()

        except:
            Analyse=Analyse_FF(instagram_account=instagram_account,ig_user = user_object,is_following=1,following_update_time = datetime.now(timezone.utc))
            Analyse.save() 


    #New unFF's 
    followers_list = []
    followings_list = []

    for i in user_followers:
        followers_list.append(i.get('username'))
    for i in user_followings:
        followings_list.append(i.get('username'))

    for i in Analyse_FF.objects.filter(instagram_account=instagram_account):
        if not i.username in followers_list:
            i.is_follower = 2
            i.follower_update_time=datetime.now(timezone.utc)
            i.save()
        if not i.username in followings_list:
            i.is_following = 2
            i.following_update_time=datetime.now(timezone.utc)
            i.save()
        
def Analyse_Beat():
    for i in Instagram_Accounts.objects.filter():
        if len(Instagram_Accounts_Analyse.objects.filter(instagram_account = i)) ==0:
            analyse_ig_account.apply_async(queue="update_datas",kwargs={'username': i.username})
        elif datetime.now(timezone.utc)-i.update_time >= timedelta(days=1):
            analyse_ig_account.apply_async(queue="update_datas",kwargs={'username': i.username})
        else:
            countine