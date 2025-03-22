from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
# Create your models here.
class User(models.Model):
    Snumber =models.BigIntegerField('学号',primary_key=True)
    Name=models.CharField('名称',max_length=20,default='')
    Openid=models.CharField('微信ID',max_length=100,default='')
    Classname=models.CharField('班级名称',max_length=50,default='')
    Majorname=models.CharField('专业名称',max_length=50,default='')
    Collegename=models.CharField('学院名称',max_length=50,default='')
    Enteryear=models.IntegerField('入学年份',default='')
    Gradenumber=models.IntegerField('当前年级',default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)
    # 自定义模型管理类，作用：告诉django在生成的管理页面上显示哪些内容。
class Static(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField('静态文件名称',max_length=50,default='')
    url=models.CharField('静态文件路径',max_length=100,default='')
#     文件种类
    kind=models.CharField('静态文件种类',max_length=50,default='')

class Share(models.Model):
    Usernumber = models.OneToOneField(User,verbose_name='学号',on_delete=models.PROTECT, primary_key=True,unique=True)
    CBindAState=models.IntegerField('A课程绑定状态',default=0,blank=True,null=True)
    CBindANumber=models.BigIntegerField('A课程绑定学号',default=-1,blank=True,null=True)
    CBindBState = models.IntegerField('B课程绑定状态', default=0, blank=True, null=True)
    CBindBNumber = models.BigIntegerField('B课程绑定学号', default=-1, blank=True, null=True)
    CBindCState = models.IntegerField('C课程绑定状态', default=0, blank=True, null=True)
    CBindCNumber = models.BigIntegerField('C课程绑定学号', default=-1, blank=True, null=True)
    CBindDState = models.IntegerField('D课程绑定状态', default=0, blank=True, null=True)
    CBindDNumber = models.BigIntegerField('D课程绑定学号', default=-1, blank=True, null=True)
    CBindEState = models.IntegerField('E课程绑定状态', default=0, blank=True, null=True)
    CBindENumber = models.BigIntegerField('E课程绑定学号', default=-1, blank=True, null=True)
    BindDepartA = models.CharField('绑定A部门',max_length=50, blank=True, null=True)
    BindDepartB = models.CharField('绑定B部门',max_length=50, blank=True, null=True)
    BindDepartC = models.CharField('绑定C部门',max_length=50, blank=True, null=True)
    BindDepartD = models.CharField('绑定D部门',max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)

class DepartmentClass(models.Model):

    id = models.AutoField(primary_key=True)
    # 部门名称
    departName = models.CharField(max_length=50, verbose_name='部门名称')
    creatornum = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='创建者学号')
    invitecode = models.CharField(max_length=20, unique=True,blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)
# 定义post_delete信号接收器

class LikesInfo(models.Model):
   Groupname=models.CharField('同好名称',max_length=30,default='')
   QQGroupNumber=models.CharField('同好群号',max_length=50,default='')
   InfoContent=models.TextField('介绍内容')
   LikesStatic=models.ImageField('同好群文件路径',blank=True,null=True)
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now=True)
   deleted = models.DateTimeField(blank=True, null=True)

class Course(models.Model):
   CourseName=models.CharField('课程名称',max_length=100,default='')
   CourseTeacher=models.CharField('教师名称',max_length=20,default='')
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now=True)
   deleted = models.DateTimeField(blank=True, null=True)
   class Meta:
       unique_together = ('CourseName', 'CourseTeacher',)
class CourseSchedule(models.Model):
    user = models.ForeignKey(User,verbose_name='学号', on_delete=models.CASCADE)
    week_number = models.IntegerField(verbose_name='星期')
    schedule = models.JSONField(verbose_name='课表')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)
    class Meta:
        unique_together = ('user', 'week_number')
class CourseTime(models.Model):
    CourseId = models.ForeignKey(Course, verbose_name='课程编号', on_delete=models.CASCADE)
    CourseTime=models.CharField('上课时间',max_length=20,default='')
    CourseWeek=models.CharField('上课周数',max_length=20,default='')
    CoursePlace = models.CharField('上课地点', max_length=100, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ('CourseId_id',)


class FoodLocation(models.Model):
    # 地点名称
    name = models.CharField(max_length=50, unique=True)
    # 区域地址
    category = models.TextField()
    def __str__(self):
        return self.name

class Food(models.Model):
    location = models.ForeignKey(FoodLocation, on_delete=models.CASCADE)
    # 食物种类
    kind = models.CharField(max_length=50)
    # 食物名称
    name = models.CharField(max_length=100)
    # 详细地址
    address = models.TextField()
    # 可选的联系方式
    phone = models.CharField(max_length=50, blank=True)
    # 创建时间
    created = models.DateTimeField(auto_now_add=True)
    # 更新时间
    updated = models.DateTimeField(auto_now=True)
    # 删除时间
    deleted = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name



