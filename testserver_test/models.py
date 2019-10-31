from datetime import datetime
from django.conf import settings

from django.db import models


# Create your models here.


class UploadImage(models.Model):
    class Meta:
        db_table = "upload_image"
        verbose_name = '图片'

    filename = models.CharField(max_length=252, default="")
    file_md5 = models.CharField(max_length=128)
    file_type = models.CharField(max_length=32)
    file_size = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)

    # 我们还定义了通过文件md5值获取模型对象的类方法
    @classmethod
    def getImageByMd5(cls, md5):
        try:
            return UploadImage.objects.filter(file_md5=md5).first()
        except Exception as e:
            return None

    # 获取本图片的url，我们可以通过这个url在浏览器访问到这个图片
    # 其中settings.WEB_HOST_NAME 是常量配置，指你的服务器的域名
    # settings.WEB_IMAGE_SERVER_PATH 也是常量配置，指你的静态图片资源访问路径
    # 这些配置项我在Django项目的settings.py文件中进行配置
    def getImageUrl(self):
        filename = self.file_md5 + "." + self.file_type
        url = "http://47.100.93.91" + "/MediaFiles/mediaImages/" + filename
        return url

    # 获取本图片在本地的位置，即你的文件系统的路径，图片会保存在这个路径下
    def getImagePath(self):
        filename = self.file_md5 + "." + self.file_type
        path = settings.IMAGE_ROOT + filename
        return path

    def __str__(self):
        s = "filename:" + str(self.filename) + " - " + "filetype:" + str(self.file_type) \
            + " - " + "filesize:" + str(self.file_size) + " - " + "filemd5:" + str(self.file_md5)
        return s


class UserInfo(models.Model):
    userId = models.BigIntegerField(primary_key=True)
    type = models.IntegerField()  # user类型  实验组，对照组
    userImagePath = models.TextField()
    username = models.CharField(max_length=10)
    password = models.TextField(max_length=20)
    age = models.IntegerField(default=0)
    coin = models.IntegerField(default=0)

    class Meta:
        db_table = "UserInfo"
        verbose_name = "用户表"


class InvestigationQuestions(models.Model):
    title = models.TextField()
    type = models.TextField(default='null', max_length=30)  # 用来标识每一次问卷调查，即用日期来表示type，在客户端请求的时候问卷时通过type来确定哪一套问卷
    selectionA = models.TextField(default='')
    selectionB = models.TextField(default='')
    selectionC = models.TextField(default='')
    selectionD = models.TextField(default='')
    selectionE = models.TextField(default='')
    selectionF = models.TextField(default='')
    selectionG = models.TextField(default='')
    selectionH = models.TextField(default='')
    selectionI = models.TextField(default='')
    selectionJ = models.TextField(default='')
    A_next = models.IntegerField(default=0)
    B_next = models.IntegerField(default=0)
    C_next = models.IntegerField(default=0)
    D_next = models.IntegerField(default=0)
    E_next = models.IntegerField(default=0)
    F_next = models.IntegerField(default=0)
    G_next = models.IntegerField(default=0)
    H_next = models.IntegerField(default=0)
    I_next = models.IntegerField(default=0)
    J_next = models.IntegerField(default=0)

    class Meta:
        db_table = "SingleQuestions"
        verbose_name = "单选表（问卷）"


class mutipleQuestions(models.Model):
    type = models.TextField()
    title = models.TextField()
    selectionA = models.TextField()
    selectionB = models.TextField()
    selectionC = models.TextField()
    selectionD = models.TextField()
    selectionE = models.TextField()
    selectionF = models.TextField()
    selectionG = models.TextField()
    selectionH = models.TextField()
    selectionI = models.TextField()
    selectionJ = models.TextField()

    class Meta:
        db_table = "MutipleQuestions"
        verbose_name = "多选表（问卷）"


class manualQuestions(models.Model):
    type = models.TextField()
    title = models.TextField()

    class Meta:
        db_table = "ManualQuestions"
        verbose_name = "填空表（问卷）"


class Survey(models.Model):
    title = models.TextField()
    type = models.TextField()
    problemOffset = models.TextField(default=0)
    problem1 = models.TextField(default='')
    problem2 = models.TextField(default='')
    problem3 = models.TextField(default='')

    class Meta:
        db_table = "Survey"
        verbose_name = "调查问卷List"


# python manage.py makemigrations --empty testserver_test
# python manage.py makemigrations
# python manage.py migrate

class Theme(models.Model):
    theme_id = models.TextField()
    author_id = models.ForeignKey('UserInfo', to_field='userId', on_delete='CASCADE')
    contains = models.TextField()
    time = models.TextField()
    likes = models.IntegerField()
    comments_num = models.IntegerField()

    class Meta:
        db_table = "Theme"


class Comments(models.Model):
    theme_id = models.TextField(null=True)
    time = models.TextField()
    person_id = models.BigIntegerField()
    contains = models.TextField()  # 内容
    likes = models.IntegerField()  # 点赞数
    replies = models.IntegerField()  # 评论回复数
    comments_num = models.IntegerField()

    class Meta:
        db_table = "Comments"


class CommentRelations(models.Model):  # 回复约束表
    commentrelations_id = models.ForeignKey('Comments', to_field='id', on_delete='CASCADE', primary_key=True)
    root = models.BigIntegerField()  # 所有评论的根评论
    parent_id = models.BigIntegerField()  # 这两个作为外键指向userid，用来区分回复关系的
    child_id = models.BigIntegerField()

    class Meta:
        db_table = "CommentRelations"


class EducationalClass(models.Model):  # 课程板块
    themeid = models.CharField(max_length=10)
    filePath = models.TextField()  # 因为考虑到有题目，所以说在进行数据返回的时候，向单选的表中查询数据，查询条件就是这里的themeid

# class SurveyResponseFromUser(models.Model):
#     person_id = models.BigIntegerField()
#       将用户上传的调查问卷信息直接写到excel文件里，动态的I/O操作
