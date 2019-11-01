import hashlib
import os

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import HttpResponse, render
import datetime
import xlwt
import xlrd
from xlutils.copy import copy
import json

from filetype import filetype

from TestServer.settings import BASE_DIR
from testserver_test import models
from testserver_test.models import *


# Create your views here.

def Register(request):
    if request.method == 'POST':
        parm = request.POST

        userinfo = UserInfo()
        userinfo.username = "null"
        userinfo.userId = parm.get("userid", "null")
        userinfo.password = parm.get("password", "null")
        userinfo.userImagePath = "null"
        userinfo.coin = 0
        userinfo.age = 0

        request.close()
        if UserInfo.objects.values().filter(userId=userinfo.userId).exists():
            return JsonResponse({"status": "0"})
        else:
            userinfo.save()
            return JsonResponse({"status": "1"})
    else:
        return render(request, 'register.html')


def UpdateInfo(request):  # 更新用户信息
    if request.method == 'POST':
        parm = request.POST
        user = UserInfo.objects.filter(userId=parm.get("userid"))
        if user.exists():
            userinfo = user.first()
            userinfo.username = parm.get("username")
            userinfo.age = parm.get("age")
            userinfo.coin = parm.get("coin")
            userinfo.save()
            request.close()
            return JsonResponse({"status": "1",
                                 "data": list(UserInfo.objects.values().filter(userId=parm.get("userid"))).__getitem__(
                                     0)})
        else:
            return JsonResponse({"status": "0"})
    else:
        return render(request, "update.html")


def getUserInfo(request):
    if request.method == 'POST':
        parm = request.POST
        target = parm.get('userid')
        userinfo = UserInfo().objects.all().filter(userId=target)
        return JsonResponse(list(userinfo).__getitem__(0))


def login(request):  # 判断请求方法
    if request.method == 'POST':
        parm = request.POST
        new_userinfo = models.UserInfo()
        new_userinfo.userId = parm.get("userid", "null")
        new_userinfo.password = parm.get("password", 'null')
        request.close()
        select_person = models.UserInfo.objects.values().filter(userId=new_userinfo.userId,
                                                                password=new_userinfo.password)
        if select_person.exists():
            return JsonResponse({'status': '1', 'data': list(select_person).__getitem__(0)})
        else:
            return JsonResponse({"status": "0", "data": "null"})
    else:
        return render(request, 'login.html')


def Theme_Response(request):
    if request.method == 'POST':
        parm = request.POST
        data = {}
        pagesize = parm.get("pagesize", 8)
        page = parm.get("page", 1)
        result_list = Theme.objects.values().order_by('-id')
        paginator = Paginator(result_list, pagesize)
        data['total'] = paginator.count
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        data['theme'] = list(books)
        return JsonResponse(data)


def Comment_Response(request):
    if request.method == 'POST':
        parm = request.POST
        data = {}
        pagesize = parm.get("pagesize", 10)
        page = parm.get("page", 1)
        result = Comments.objects.all().filter(
            theme_id=parm.get("themeid")).order_by("-id").values()
        paginator = Paginator(result, pagesize)
        data['total'] = paginator.count
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        data['comments'] = list(books)
        return JsonResponse(data)


def reply_response(request):
    if request.method == 'POST':
        parm = request.POST
        racks = CommentRelations.objects.filter(root=parm.get("userid"))

        result = Comments.objects.all().filter(person_id__in=list(racks.values_list('child_id', flat=True)),
                                               theme_id=None).order_by('-commentrelations').values()
        data = {}

        pagesize = parm.get("pagesize", 10)
        page = parm.get("page", 1)
        paginator = Paginator(result, pagesize)
        data['total'] = paginator.count
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        data['reply'] = list(books)
        return JsonResponse(data)


def post_themes(request):
    if request.method == "POST":
        parm = request.POST
        theme = Theme()
        theme.theme_id = parm.get("themeid")
        theme.author_id = parm.get('userid')
        theme.comments_num = 0
        theme.likes = 0
        theme.time = parm.get("themeid")
        theme.contains = parm.get("contains")
        theme.save()
        return HttpResponse(1)


def post_comments(request):
    if request.method == "POST":
        parm = request.POST
        comments = Comments()
        comments.theme_id = parm.get("themeid")
        comments.person_id = parm.get('userid')
        comments.contains = parm.get('contains')
        comments.likes = 0
        comments.replies = 0
        comments.comments_num = 0
        comments.save()
        return HttpResponse(1)


def post_replies(request):
    if request.method == "POST":
        parm = request.POST
        comments = Comments()
        relations = CommentRelations()
        comments.theme_id = parm.get("themeid")
        comments.person_id = parm.get("userid")
        comments.contains = parm.get("contains")
        comments.likes = 0
        comments.replies = 0
        comments.comments_num = 0

        relations.root = parm.get("root")
        relations.parent_id = parm.get("parentid")
        relations.child_id = parm.get("userid")

        comments.save()
        relations.save()
        return HttpResponse(1)


def Survey_List(request):
    if request.method == 'POST':
        data = {}
        temp = Survey.objects.all().order_by('-id')
        data['data'] = list(temp.values())
        return JsonResponse(data)


def Survey_save(request):
    if request.method == 'POST':
        parm = request.POST
        temp = Survey()
        temp.type = datetime.now().strftime("%Y%m%d")
        temp.title = parm.get('title')
        temp.warning = parm.get('warning', '')
        temp.problem1 = parm.get('problem1', '')
        temp.problem2 = parm.get('problem2', '')
        temp.problem3 = parm.get('problem3', '')

        header = ['序号', '提交时间', '总时间(秒)']
        if temp.problem1 is not '':
            header.append(temp.problem1)
            temp.problemOffset = 1
        if temp.problem2 is not '':
            header.append(temp.problem2)
            temp.problemOffset = 1
        if temp.problem3 is not '':
            header.append(temp.problem3)
            temp.problemOffset = 1
        temp.save()

        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('sheet1')
        single = InvestigationQuestions.objects.all().filter(type=temp.type)
        mutiple = mutipleQuestions.objects.all().filter(type=temp.type)
        manual = manualQuestions.objects.all().filter(type=temp.type)
        for number in range(0, single.count()):
            header.append('第' + str(number + 1) + '题(单选题)')
        for number1 in range(single.count(), single.count() + mutiple.count()):
            header.append('第' + str(number1 + 1) + '题(多选题)')
        for number2 in range(single.count() + mutiple.count(), single.count() + mutiple.count() + manual.count()):
            header.append('第' + str(number2 + 1) + '题(填空题)')
        for number in range(len(header)):
            worksheet.write(0, number, header[number])
        workbook.save(BASE_DIR + '/MediaFiles/SurveyResult/' + temp.type + '.xls')

        return HttpResponse(1)
    else:
        return render(request, 'AddSurveyInfos.html')


def Survey_result(request):
    if request.method == 'POST':
        parm = request.POST
        type = parm.get('type', None)
        result = parm.get('result', '{'':''}')
        if type is not None:
            # result = '{"index": "1","startTime": "20191028","totleTime": "219","1.": "A","2.": "B","3.": "C","4.": "A","5.": "D","6.": "E"}'
            result = json.loads(result)

            workbookreader = xlrd.open_workbook(BASE_DIR + '/MediaFiles/SurveyResult/' + str(type) + '.xls')
            worksheetreader = workbookreader.sheet_by_name('sheet1')
            workbook = copy(workbookreader)
            worksheet = workbook.get_sheet(0)
            print(list(result.values()))
            for i in range(len(result)):
                worksheet.write(worksheetreader.nrows, i, list(result.values()).__getitem__(i))
            workbook.save(BASE_DIR + '/MediaFiles/SurveyResult/' + str(type) + '.xls')
            return HttpResponse(1)
        else:
            return HttpResponse(0)


def Survey_Response(request):
    if request.method == 'POST':
        parm = request.POST
        data = {}
        type = parm.get('type', None)
        if type is not None:
            temp = InvestigationQuestions.objects.all().filter(type=type)
            data['SingleQuestion'] = list(temp.values())
            temp = mutipleQuestions.objects.all().filter(type=type)
            data['MutipleQuestion'] = list(temp.values())
            temp = manualQuestions.objects.all().filter(type=type)
            data['ManualQuestion'] = list(temp.values())
            return JsonResponse(data)
        else:
            return HttpResponse('请添加问卷类型')


def Survey_SingleQuestion_Save(request):
    if request.method == 'POST':
        parm = request.POST
        question = InvestigationQuestions()
        question.themeid = datetime.now().strftime("%Y%m%d")
        question.type = question.themeid
        question.title = parm.get('problem', '')
        question.selectionA = parm.get('1', '')
        question.selectionB = parm.get('2', '')
        question.selectionC = parm.get('3', '')
        question.selectionD = parm.get('4', '')
        question.selectionE = parm.get('5', '')
        question.selectionF = parm.get('6', '')
        question.selectionG = parm.get('7', '')
        question.selectionH = parm.get('8', '')
        question.selectionI = parm.get('9', '')
        question.selectionJ = parm.get('10', '')
        question.A_next = int(parm.get('1_next', 0))
        question.B_next = int(parm.get('2_next', 0))
        question.C_next = int(parm.get('3_next', 0))
        question.D_next = int(parm.get('4_next', 0))
        question.E_next = int(parm.get('5_next', 0))
        question.F_next = int(parm.get('6_next', 0))
        question.G_next = int(parm.get('7_next', 0))
        question.H_next = int(parm.get('8_next', 0))
        question.I_next = int(parm.get('9_next', 0))
        question.J_next = int(parm.get('10_next', 0))
        question.save()
    return render(request, "AddSingleQuestion.html")


def Survey_MutipleQuestion_Save(request):
    if request.method == 'POST':
        parm = request.POST
        question = mutipleQuestions()
        question.themeid = datetime.now().strftime('%Y%m%d')
        question.type = question.themeid
        question.title = parm.get('problem', '')
        question.selectionA = parm.get('1', '')
        question.selectionB = parm.get('2', '')
        question.selectionC = parm.get('3', '')
        question.selectionD = parm.get('4', '')
        question.selectionE = parm.get('5', '')
        question.selectionF = parm.get('6', '')
        question.selectionG = parm.get('7', '')
        question.selectionH = parm.get('8', '')
        question.selectionI = parm.get('9', '')
        question.selectionJ = parm.get('10', '')
        question.save()
    return render(request, "AddMutipleQuestion.html")


def Survey_ManualQuestion_Save(request):
    if request.method == 'POST':
        parm = request.POST
        question = manualQuestions()
        question.type = datetime.now().strftime('%Y%m%d')
        question.title = parm.get('problem')
        question.save()
    return render(request, 'AddManualQuestion.html')


def EducationalClass_Response(request):
    if request.method == 'POST':
        parm = request.POST
        themeid = parm.get('themeid', None)
        if themeid is not None:
            temp = EducationalClass.objects.all().filter(themeid=themeid)
            data = {list(temp.values().__getitem__(0))}
            temp = InvestigationQuestions.objects.all().filter(themeid=themeid)
            data['question'] = list(temp.values())
            return JsonResponse(data)
        else:
            return HttpResponse('请填写themeid字段')


# 上传文件的视图
def uploadImage(request):
    if request.method == 'POST':
        # 从请求表单中获取文件对象
        file = request.FILES.get("img", None)
        if not file:  # 文件对象不存在， 返回400请求错误
            return HttpResponse("need file.")

        # 图片大小限制
        if not pIsAllowedFileSize(file.size):
            return HttpResponse("文件太大")

        # 计算文件md5
        md5 = pCalculateMd5(file)
        uploadImg = UploadImage.getImageByMd5(md5)
        if uploadImg:  # 图片文件已存在， 直接返回
            return JsonResponse({'url': uploadImg.getImageUrl()})

        # 获取扩展类型 并 判断
        ext = pGetFileExtension(file)
        if not pIsAllowedImageType(ext):
            return HttpResponse("文件类型错误")

        # 检测通过 创建新的image对象
        # 文件对象即上一小节的UploadImage模型
        uploadImg = UploadImage()
        uploadImg.filename = file.name
        uploadImg.file_size = file.size
        uploadImg.file_md5 = md5
        uploadImg.file_type = ext
        uploadImg.save()  # 插入数据库

        # 部署完成之后，注意修改models模型里的getimagepath和getimageurl，这两个都是写的固定的，不好改
        # 所以说我们部署到服务器之后就直接修改访问api即可

        print(uploadImg.getImagePath())
        # 保存 文件到磁盘
        with open(uploadImg.getImagePath(), "wb+") as f:
            # 分块写入
            for chunk in file.chunks():
                f.write(chunk)
            f.close()

        # # 记录日志，这一步可有可无，可定制
        # FileLogger.log_info("upload_image", uploadImg, FileLogger.IMAGE_HANDLER)

        # 返回图片的url以供访问
        return JsonResponse({"url": uploadImg.getImageUrl()})
    return render(request, 'test.html')


# 检测文件类型
# 我们使用第三方的库filetype进行检测，而不是通过文件名进行判断
# pip install filetype 即可安装该库
def pGetFileExtension(file):
    rawData = bytearray()
    for c in file.chunks():
        rawData += c
    try:
        ext = filetype.guess_extension(rawData)
        return ext
    except Exception as e:
        # todo log
        return None


# 计算文件的md5
def pCalculateMd5(file):
    md5Obj = hashlib.md5()
    for chunk in file.chunks():
        md5Obj.update(chunk)
    return md5Obj.hexdigest()


# 文件类型过滤 我们只允许上传常用的图片文件
def pIsAllowedImageType(ext):
    if ext in ["png", "jpeg", "jpg", "bmp"]:
        return True
    return False


# 文件大小限制
# settings.IMAGE_SIZE_LIMIT是常量配置，我设置为10M
def pIsAllowedFileSize(size):
    limit = 1024 * 1024
    if size < limit:
        return True
    return False
