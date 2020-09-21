from django.db import models
from aristo.models import *

# Create your models here.

class Instagram_Accounts(models.Model):
    """Keeps Instagram Account's basic informations such as username and password."""
    main_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    username = models.CharField(max_length=200, verbose_name="username", null=True)
    password= models.CharField(max_length=200, verbose_name="password", null=True)
    user_pk = models.IntegerField(verbose_name="user_pk",null=True)
    full_name = models.CharField(max_length=200, verbose_name="full_name", null=True)
    is_private = models.IntegerField(verbose_name="is_private",null=True)
    profile_pic_url=models.CharField(max_length=500,verbose_name="profile_pic_url",null=True)
    biography = models.CharField(max_length=200, verbose_name="biography", null=True)
    is_business = models.CharField(max_length=200, verbose_name="is_business", null=True)
    is_current_account=models.IntegerField(verbose_name="is current account",null=True)
    update_time = models.DateTimeField(auto_now_add=True,verbose_name="update_time",null=True)

    
    def __str__(self):
        return self.username


class Instagram_Accounts_Analyse(models.Model):
    """We track instagram account's daily datas here"""
    instagram_account=models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    media_count=models.IntegerField(verbose_name="post_count",null=True)
    like_count=models.IntegerField(verbose_name="like_count",null=True)
    comment_count=models.IntegerField(verbose_name="comment_count",null=True)
    follower_count=models.IntegerField(verbose_name="follower_count",null=True)
    following_count=models.IntegerField(verbose_name="following_count",null=True) 
    update_time = models.DateTimeField(auto_now_add=True,verbose_name="update_time",null=True)
    
    def __str__(self):
        return self.instagram_account.username    

class IG_Users(models.Model):
    """Keeps all IG_users"""
    username = models.CharField(max_length=200, verbose_name="username", null=True)
    full_name = models.CharField(max_length=200, verbose_name="full_name", null=True)
    pk_number = models.IntegerField(verbose_name='pk_number', null=True)
    profile_pic_url = models.CharField(max_length=300, verbose_name="profile_pic_url", null=True)
    follower_count = models.IntegerField(verbose_name='follower_count', null=True)
    following_count = models.IntegerField(verbose_name='following_count', null=True)
    biography = models.CharField(max_length=200, verbose_name='biography', null=True)
    is_business = models.IntegerField(verbose_name='business_status', null=True)
    is_private = models.IntegerField(verbose_name='private_status', null=True)
    has_anonymous_profile_picture = models.IntegerField(verbose_name='has_anonymous_profile_picture', null=True)
    media_count = models.IntegerField(verbose_name='number_of_medias', null=True)

    def __str__(self):
        return self.username
    



class Analyse_FF(models.Model):
    """Tracks new and old follow activities related with an instagram account."""
    instagram_account=models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    ig_user=models.ForeignKey(IG_Users,on_delete=models.CASCADE,null=True)
    is_following=models.IntegerField(verbose_name="is_following",null=True)
    is_follower=models.IntegerField(verbose_name="is_follower",null=True)
    follower_update_time = models.DateTimeField(auto_now_add=True,verbose_name="follower_update_time",null=True)
    following_update_time = models.DateTimeField(auto_now_add=True,verbose_name="following_update_time",null=True)
    
    def __str__(self):
        return self.instagram_account.username


class Challenge_User(models.Model):
    instagram_account=models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    main_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    username = models.CharField(max_length=200, verbose_name="username", null=True)
    password= models.CharField(max_length=200, verbose_name="password", null=True)
    sms_or_mail = models.IntegerField(verbose_name='sms_or_mail',default = 2)
    challenge_code = models.IntegerField(verbose_name='challenge_code',default = 2)
    def __str__(self):
        return self.username
    
class Assistants(models.Model):
    """Keeps all assistants"""
    assistant_type = models.IntegerField(verbose_name="Assistant_type",null=True)
    source_type = models.IntegerField(verbose_name="source_type",null=True)
    source = models.CharField(max_length=200,verbose_name="source", null=True)
    relationship = models.CharField(max_length=200,verbose_name="relationship", null=True)
    instagram_account = models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    number_of_actions = models.IntegerField(verbose_name='number_of_actions',null=True)
    activity_status = models.IntegerField(verbose_name='status',null=True)
    queue = models.IntegerField(verbose_name='queue',null=True)
    update_time = models.DateTimeField(auto_now_add=True,verbose_name="update_time",null=True)
    comment = models.CharField(max_length=1000,verbose_name="comment", null=True)
    is_there_enough_data = models.IntegerField(verbose_name='Yeterince veri var mı?',null=True)

    def __str__(self):
        return str(self.instagram_account)

class Api_Error(models.Model):
    assistant=models.ForeignKey(Assistants,on_delete=models.CASCADE,null=True)
    api_error_mean = models.CharField(max_length=200,verbose_name="Hata kaynağı", null=True)
    error_action_type = models.IntegerField(verbose_name="Hangi eylemi yaparken hata verdi",null=True)
    error_source = models.CharField(max_length=200,verbose_name="Hatanın olduğu fonksiyon", null=True)
    update_time = models.DateTimeField(auto_now_add=True,verbose_name="update_time",null=True)
    def __str__(self):
        return self.assistant.instagram_account.username

class Assistants_Settings(models.Model):
    """Keeps all assistants' settings"""
    is_default = models.IntegerField(verbose_name='varsayılan_ayarlar',null=True)
    min_followers = models.IntegerField(verbose_name='min_followers',null=True)
    max_followers = models.IntegerField(verbose_name='max_followers',null=True)
    min_followings = models.IntegerField(verbose_name='min_followings',null=True)
    max_followings = models.IntegerField(verbose_name='max_followings',null=True)
    min_posts = models.IntegerField(verbose_name='min_posts',null=True)
    max_posts = models.IntegerField(verbose_name='max_posts',null=True)
    biography = models.IntegerField(verbose_name='biography',null=True)
    is_private = models.IntegerField(verbose_name='hidden_account',null=True)
    is_business = models.IntegerField(verbose_name='is_bussines',null=True)
    has_anonymous_profile_picture = models.IntegerField(verbose_name='has_anonymous_profile_picture', null=True)
    assistant=models.ForeignKey(Assistants,on_delete=models.CASCADE,null=True)
    speed = models.IntegerField(verbose_name='speed',null=True)
    
    def __str__(self):
        return self.assistant.instagram_account.username

class Api_Settings(models.Model):
    """Keeps all apis' settings"""
    instagram_account=models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    cookie=models.BinaryField(verbose_name="binary",null=True)
    settings=models.TextField(verbose_name="settings",null=True)
    rank_token = models.CharField(max_length=200,verbose_name = "rank token", null=True)
    update_time = models.DateTimeField(auto_now_add=True,verbose_name="update_time",null=True)

    def __str__(self):
        return self.instagram_account.username

class Api_Settings_web_api(models.Model):
    """Keeps all apis' settings"""
    instagram_account=models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    cookie=models.BinaryField(verbose_name="binary",null=True)
    settings=models.TextField(verbose_name="settings",null=True)
    update_time = models.DateTimeField(auto_now_add=True,verbose_name="update_time",null=True)

    def __str__(self):
        return self.instagram_account.username


class Comments(models.Model):
    """Keeps comment information of comment assistants"""
    assistant = models.ForeignKey(Assistants,on_delete=models.CASCADE,null=True)
    comment=models.CharField(max_length=200, verbose_name="comment",null=True)

    def __str__(self):
        return str(self.post_id)

class Follow_Actions(models.Model):
    """Keeps all target users' informations of follow actions"""
    instagram_account=models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    assistant = models.ForeignKey(Assistants,on_delete=models.CASCADE,null=True)
    ig_user=models.ForeignKey(IG_Users, on_delete=models.CASCADE, null=True)
    source=models.CharField(max_length=200,verbose_name = "source itself",null=True)
    source_type=models.IntegerField(verbose_name='type of source',null=True)
    relationship=models.IntegerField(verbose_name='relationship with the source',null=True)
    status=models.IntegerField(verbose_name='status',null=True)
    update_time=models.DateTimeField(auto_now_add=True, verbose_name="update_time", null=True)

    def __str__(self):
        return str(self.instagram_account)
    

class Like_Actions(models.Model):
    """Keeps all target users' informations of like actions"""
    instagram_account=models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    assistant = models.ForeignKey(Assistants,on_delete=models.CASCADE,null=True)
    ig_user=models.ForeignKey(IG_Users,on_delete=models.CASCADE,null=True)
    post_pk = models.IntegerField(verbose_name='post_pk',default = 0)
    source=models.CharField(max_length=200,verbose_name="source itself",null=True)
    source_type=models.IntegerField(verbose_name='type of source',null=True)
    relationship=models.IntegerField(verbose_name='relationship with the source',null=True)
    status=models.IntegerField(verbose_name='status',null=True)
    update_time=models.DateTimeField(auto_now_add=True,verbose_name="update_time",null=True)

    def __str__(self):
        return str(self.instagram_account)

class Comment_Actions(models.Model):
    """Keeps all target users' informations of comment actions"""
    instagram_account=models.ForeignKey(Instagram_Accounts,on_delete=models.CASCADE,null=True)
    assistant = models.ForeignKey(Assistants,on_delete=models.CASCADE,null=True)
    source_type=models.IntegerField(verbose_name='type of source',null=True)
    relationship=models.IntegerField(verbose_name='relationship with the source',null=True)
    source=models.CharField(max_length=200,verbose_name="source itself",null=True)
    ig_user=models.ForeignKey(IG_Users,on_delete=models.CASCADE,null=True)
    post_pk = models.IntegerField(verbose_name='post_pk',null=True)
    status=models.IntegerField(verbose_name='status',null=True)
    update_time=models.DateTimeField(auto_now_add=True,verbose_name="update_time",null=True)

    def __str__(self):
        return str(self.instagram_account)



class User_Sources(models.Model):
    """Keeps where the assistant should countine to collect data from the same user."""
    instagram_account = models.ForeignKey(Instagram_Accounts, on_delete=models.CASCADE, null=True)
    source = models.CharField(max_length=200, verbose_name='username', null=True)
    followers_max_id = models.CharField(max_length=200, verbose_name="followers max id", default = "")
    followings_max_id = models.CharField(max_length=200, verbose_name="followings max id", default = "")
    feed_max_id = models.CharField(max_length=200, verbose_name="feed max id", default = "")

    def __str__(self):
        return self.instagram_account.username


class Post_Datas(models.Model):
    """this model allows us to track the last feed we extracted for both users and hashtags/locations"""
    instagram_account = models.ForeignKey(Instagram_Accounts, on_delete=models.CASCADE, null=True)
    source_type = models.IntegerField(verbose_name='source of the post', null=True)
    source = models.CharField(verbose_name='source', max_length=200, null=True)
    post_pk = models.CharField(verbose_name='Pk of the post', max_length=200, null=True)
    likers = models.IntegerField(verbose_name='has likers collected', null=True)
    commenters = models.IntegerField(verbose_name='has commenters collected', null=True)
    commenters_max_id =  models.CharField(max_length=200, verbose_name="commenters_max_id", default = "")
    posters = models.IntegerField(verbose_name='has posters collected', null=True)
    def __str__(self):
        return self.instagram_account.username


class Hashtag_Sources(models.Model):
    """Keeps where the assistant should countine to collect data from the same hashtag."""
    instagram_account = models.ForeignKey(Instagram_Accounts, on_delete=models.CASCADE, null=True)
    source = models.CharField(max_length=200, verbose_name='hashtag', null=True)
    feed_max_id = models.CharField(max_length=200, verbose_name="feed max id", default = "")

    def __str__(self):
        return self.instagram_account.username


class Location_Sources(models.Model):
    """Keeps where the assistant should countine to collect data from the same location."""
    instagram_account = models.ForeignKey(Instagram_Accounts, on_delete=models.CASCADE, null=True)
    source = models.CharField(max_length=200, verbose_name='hashtag', null=True)
    feed_max_id = models.CharField(max_length=200, verbose_name="feed max id", default = "")


    def __str__(self):
        return self.instagram_account.username

class Volta(models.Model):
    status =  models.IntegerField(verbose_name='Activity_Status', null=True)
    def __str__(self):
        return str(self.status)
