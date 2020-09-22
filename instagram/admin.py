from django.contrib import admin
from .models import * 

# Register your models here.

# Register your models here.
class Analyse_FFAdmin(admin.ModelAdmin):
    list_display = ("ig_user","instagram_account","follower_update_time","following_update_time")

admin.site.register(Analyse_FF,Analyse_FFAdmin)

class Instagram_Accounts_AnalyseAdmin(admin.ModelAdmin):
    list_display = ("instagram_account","update_time")

admin.site.register(Instagram_Accounts_Analyse,Instagram_Accounts_AnalyseAdmin)

class Follow_ActionsAdmin(admin.ModelAdmin):
    list_display = ("ig_user","source","source_type","relationship","status","instagram_account","update_time")

admin.site.register(Follow_Actions,Follow_ActionsAdmin)

class Like_ActionsAdmin(admin.ModelAdmin):
    list_display = ("ig_user","source","source_type","relationship","status","instagram_account","update_time")

admin.site.register(Like_Actions,Like_ActionsAdmin)

class Comment_ActionsAdmin(admin.ModelAdmin):
    list_display = ("ig_user","source","source_type","relationship","status","instagram_account","update_time")

admin.site.register(Comment_Actions,Comment_ActionsAdmin)

class AssistantsAdmin(admin.ModelAdmin):
    list_display = ("assistant_type","source_type","relationship","instagram_account","activity_status","update_time","queue")

admin.site.register(Assistants,AssistantsAdmin)

class Post_DatasAdmin(admin.ModelAdmin):
    list_display = ("instagram_account","source","likers","commenters","source_type")

admin.site.register(Post_Datas,Post_DatasAdmin)

class Api_ErrorAdmin(admin.ModelAdmin):
    list_display = ("assistant","api_error_mean","error_source","update_time")

admin.site.register(Api_Error,Api_ErrorAdmin)
admin.site.register(Challenge_User)
admin.site.register(Volta)
admin.site.register(Instagram_Accounts)
admin.site.register(Assistants_Settings)
admin.site.register(IG_Users)
admin.site.register(Api_Settings)
admin.site.register(Api_Settings_web_api)
admin.site.register(User_Sources)
admin.site.register(Hashtag_Sources)
admin.site.register(Location_Sources)
admin.site.register(White_List_Users)
admin.site.register(Unfollow_Actions)
admin.site.register(White_List_Assistant)
