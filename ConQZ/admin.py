from django.contrib import admin
from .models import User, Share, DepartmentClass, LikesInfo, Course, CourseSchedule, CourseTime, FoodLocation, Food, Static
from django.contrib.admin import DateFieldListFilter
from django.utils.translation import gettext_lazy as _

class DateRangeFilter(DateFieldListFilter):
    title = _('date')

# User模型的Admin类
class UserAdmin(admin.ModelAdmin):
    list_display = ['Snumber', 'Name', 'Openid', 'Classname', 'Majorname', 'Collegename', 'Enteryear', 'Gradenumber', 'created', 'updated', 'deleted']
    search_fields = ['Snumber', 'Name', 'Openid', 'Classname', 'Majorname', 'Collegename', 'Enteryear', 'Gradenumber']
    list_filter = ['Snumber', 'Classname', 'Majorname', 'Collegename', 'Enteryear', 'Gradenumber', ('created', DateRangeFilter), ('updated', DateRangeFilter), ('deleted', DateRangeFilter)]

# Share模型的Admin类
class ShareAdmin(admin.ModelAdmin):
    list_display = ['Usernumber', 'CBindAState', 'CBindANumber', 'CBindBState', 'CBindBNumber', 'CBindCState', 'CBindCNumber', 'CBindDState', 'CBindDNumber', 'CBindEState', 'CBindENumber', 'BindDepartA', 'BindDepartB', 'BindDepartC', 'BindDepartD', 'created', 'updated', 'deleted']
    search_fields = ['Usernumber',  'CBindANumber', 'CBindBNumber', 'CBindCNumber', 'CBindDNumber', 'BindDepartA', 'BindDepartB', 'BindDepartC', 'BindDepartD']
    list_filter = ['Usernumber', 'CBindAState', 'CBindBState', 'CBindCState', 'CBindDState', 'CBindEState', ('created', DateRangeFilter), ('updated', DateRangeFilter), ('deleted', DateRangeFilter), 'CBindANumber', 'CBindBNumber', 'CBindCNumber', 'CBindDNumber', 'BindDepartA', 'BindDepartB', 'BindDepartC', 'BindDepartD']

# DepartmentClass模型的Admin类
class DepartmentClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'departName', 'creatornum', 'invitecode', 'created', 'updated', 'deleted']
    search_fields = ['departName', 'creatornum', 'invitecode']
    list_filter = ['departName', 'creatornum', ('created', DateRangeFilter), ('updated', DateRangeFilter), ('deleted', DateRangeFilter)]

# LikesInfo模型的Admin类
class LikesInfoAdmin(admin.ModelAdmin):
    list_display = ['Groupname', 'QQGroupNumber', 'InfoContent', 'LikesStatic', 'created', 'updated', 'deleted']
    search_fields = ['Groupname', 'QQGroupNumber', 'InfoContent']
    list_filter = [ ('created', DateRangeFilter), ('updated', DateRangeFilter), ('deleted', DateRangeFilter)]

# Course模型的Admin类
class CourseAdmin(admin.ModelAdmin):
    list_display = ['CourseName', 'CourseTeacher', 'created', 'updated', 'deleted']
    search_fields = ['CourseName', 'CourseTeacher']
    list_filter = ['CourseName', 'CourseTeacher', ('created', DateRangeFilter), ('updated', DateRangeFilter), ('deleted', DateRangeFilter)]

# CourseSchedule模型的Admin类
class CourseScheduleAdmin(admin.ModelAdmin):
    list_display = ['user', 'week_number', 'created', 'updated', 'deleted']
    search_fields = ['user', 'week_number']
    list_filter = ['user', 'week_number', ('created', DateRangeFilter), ('updated', DateRangeFilter), ('deleted', DateRangeFilter)]

# CourseTime模型的Admin类
class CourseTimeAdmin(admin.ModelAdmin):
    list_display = ['CourseId', 'CourseTime', 'CourseWeek', 'CoursePlace', 'created', 'updated', 'deleted']
    search_fields = ['CourseId', 'CourseTime', 'CourseWeek', 'CoursePlace']
    list_filter = ['CourseId', 'CourseTime', 'CourseWeek', 'CoursePlace', ('created', DateRangeFilter), ('updated', DateRangeFilter), ('deleted', DateRangeFilter)]

# FoodLocation模型的Admin类
class FoodLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    search_fields = ['name', 'category']
    list_filter = ['name']

# Food模型的Admin类
class FoodAdmin(admin.ModelAdmin):
    list_display = ['location', 'kind', 'name', 'address', 'phone', 'created', 'updated', 'deleted']
    search_fields = ['location', 'kind', 'name', 'address']
    list_filter = ['location', 'kind', 'name', ('created', DateRangeFilter), ('updated', DateRangeFilter), ('deleted', DateRangeFilter)]
# static模型的Admin类
class StaticAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url']
    search_fields = ['name', 'url']
    list_filter = ['name', 'url']



# 在admin站点中注册这些模型及其Admin类
admin.site.register(User, UserAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(DepartmentClass, DepartmentClassAdmin)
admin.site.register(LikesInfo, LikesInfoAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseSchedule, CourseScheduleAdmin)
admin.site.register(CourseTime, CourseTimeAdmin)
admin.site.register(FoodLocation, FoodLocationAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(Static, StaticAdmin)
