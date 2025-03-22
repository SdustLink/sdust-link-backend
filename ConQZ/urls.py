
from django.urls import path, include

from ConQZ import views

# from Django_SXK.ConQZ import admin

app_name = 'qz'

urlpatterns = [
    # 用户登录信息
    path('login-info/', views.Logininfo, name='login-info'),
    # 课程信息
    path('class-info/', views.PostClassInfo, name='class-info'),
    # 共享课表
    path('share-state/', views.GetShareState, name='share-state'),
    path('share-state/post/', views.PostShareState, name='share-info'),
    path('share-state/reply/', views.ReplyShareState, name='share-info-reply'),
    path('share-info/get/', views.GetShareInfo, name='share-info-detail'),
    # 共享部门
    path('share-dept/create/', views.CreateDept, name='create_dept'),
    path('share-dept/join/', views.JoinDept, name='join_dept'),
    path('share-dept/quit/', views.QuitDept, name='quit_dept'),
    path('share-dept/dis/', views.DismissDept, name='dismiss_dept'),
    path('share-dept/kick/', views.KickDept, name='kick_dept'),
    path('share-dept/get/', views.GetDeptInfo, name='kick_dept'),
    path('share-dept/get-member/', views.GetDepartmentMemberInfo, name='get_dept_member'),
    path('share-week/state/', views.GetWeekPostState, name='get_week_post_state'),
    # 通讯录
    # 小科同好查询
    path('phonebook/likes/get/', views.GetLikesInfo, name='likes-get'),
    # path('phonebook/science/get', views.GetSciencesInfo, name='science-get'),
    # 课程库信息
    path('course-lib/', views.GetCourselib, name='course-lib'),
    path('course-lib/detail/', views.GetLibdetail, name='course-lib-detail'),
    # 教室课表
    # path('classroom/', views.GetClassroom, name='classroom'),
    # 食物库
    path('food-lib/kind/', views.GetFoodKind, name='food-lib'),
    # 静态文件管理
    path('static/', views.GetStaticResource, name='static'),

]