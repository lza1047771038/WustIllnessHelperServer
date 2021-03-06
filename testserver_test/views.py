import datetime
import hashlib
import json
import time

import xlrd
import xlwt
from PIL import Image
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import HttpResponse, render
from filetype import filetype
from xlutils.copy import copy

from TestServer.settings import BASE_DIR
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
        userinfo.type = 0
        userinfo.userType = 0
        userinfo.coin = 0
        userinfo.age = 0

        request.close()
        if UserInfo.objects.values().filter(userId=userinfo.userId).exists():  # 为True说明数据库中存在该对象，则无法注册
            return HttpResponse(0)
        else:
            userinfo.save()
            return HttpResponse(1)
    else:
        return render(request, 'register.html')


def UpdateInfo(request):  # 更新用户信息
    if request.method == 'POST':
        parm = request.POST
        user = UserInfo.objects.filter(userId=parm.get("userid"), phoneid=parm.get('phoneid'))
        if user.exists():
            userinfo = user.first()
            userinfo.username = parm.get("username")
            userinfo.userImagePath = parm.get('userimagepath', "null")
            userinfo.age = parm.get("age")
            userinfo.coin = parm.get("coin")
            userinfo.save()
            request.close()
            return JsonResponse(list(UserInfo.objects.values().filter(userId=parm.get("userid"))).__getitem__(0))
        else:
            return HttpResponse(0)
    else:
        return render(request, "update.html")


def UpdateUserCoin(request):
    if request.method == 'POST':
        parm = request.POST
        userId = parm.get('userid', None)
        if userId is None:
            return HttpResponse('请输入UserId')
        user = UserInfo.getUser(userId)
        try:
            user.coin = parm.get('coin')
            user.save()
        except Exception as e:
            return HttpResponse(0)
        return HttpResponse(1)


def getUserInfo(request):
    if request.method == 'POST':
        parm = request.POST
        target = parm.get('userid')
        userinfo = UserInfo().objects.all().filter(userId=target)
        return JsonResponse(list(userinfo).__getitem__(0))


def login(request):  # 判断请求方法
    if request.method == 'POST':
        parm = request.POST
        new_userinfo = UserInfo()
        new_userinfo.userId = parm.get("userid", "null")
        new_userinfo.password = parm.get("password", 'null')
        new_userinfo.phoneid = parm.get("phoneid", "null")
        select_person = UserInfo.objects.filter(userId=new_userinfo.userId,
                                                password=new_userinfo.password)
        if select_person.exists():
            temp = select_person.first()  # 开一个额外的数据进行赋值，然后保存到数据库
            temp.phoneid = parm.get('phoneid', 'null')
            temp.save()
            select_person.phoneid = parm.get('phoneid', 'null')  # 动态修改查询到的数据中的信息，方便及时保存
            return JsonResponse({'data': list(select_person.values()).__getitem__(0)})
        else:
            return HttpResponse(0)  # 此处返回则表示没有该用户
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
            books = []
        for item in books:
            userinfo = UserInfo.objects.all().filter(userId=item['author_id_id']).first()
            item['username'] = userinfo.username
            item['userimage'] = userinfo.userImagePath
        data['theme'] = list(books)
        return JsonResponse(data)


def Comment_Response(request):  # 评论拉取完成
    if request.method == 'POST':
        parm = request.POST
        data = {}
        pagesize = parm.get("pagesize", 10)
        page = parm.get("page", 1)
        result = Comments.objects.all().filter(
            theme_id=parm.get("themeid")).order_by("-id").values()
        paginator = Paginator(result, pagesize)
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        for item in books:
            userinfo = UserInfo.objects.all().filter(userId=item['person_id']).first()
            item['username'] = userinfo.username
            item['userimage'] = userinfo.userImagePath
        data['comments'] = list(books)
        return JsonResponse(data)


def reply_response(request):
    if request.method == 'POST':
        parm = request.POST
        # 根据root对象的userid和当前楼主评论的id查找评论关系表中的数据，然后从评论表中找到对应的评论，封装成json

        result = Comments.objects.all().filter(target_id=parm.get('id'), root=parm.get('root'),
                                               theme_id=None).order_by('-id').values()

        data = {}
        print(result.count())
        pagesize = parm.get("pagesize", 10)
        page = parm.get("page", 1)
        paginator = Paginator(result, pagesize)
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        for item in books:
            ss = UserInfo.objects.all().filter(userId=item['person_id']).first()
            if ss is not None:
                item['username'] = ss.username
                item['userimage'] = ss.userImagePath
        data['comments'] = list(books)
        return JsonResponse(data)


def post_themes(request):
    if request.method == "POST":
        parm = request.POST
        theme = Theme()
        theme.theme_id = parm.get("themeid")
        theme.author_id = UserInfo(userId=parm.get('userid'))
        theme.comments_num = 0
        theme.likes = 0
        theme.imagestring = parm.get('imageString')
        theme.time = parm.get("themeid")
        theme.contains = parm.get("contains")
        theme.save()
        return HttpResponse(1)


def post_comments(request):  # 提交评论（回复帖子/推文）
    if request.method == "POST":
        parm = request.POST
        judge = UserInfo.objects.filter(userId=parm.get("userid"), phoneid=parm.get("phoneid"))
        theme_id = parm.get("themeid")
        if judge.exists():
            try:
                if str(theme_id).startswith("THE"):
                    first = Theme.objects.all().filter(theme_id=theme_id).first()
                    first.comments_num = first.comments_num + 1
                    first.save()
                comments = Comments()
                comments.id = parm.get("commentid")
                comments.theme_id = theme_id
                comments.time = int(round(time.time() * 1000))
                comments.person_id = parm.get('userid')
                comments.contains = parm.get('contains')
                comments.likes = 0
                comments.replies = 0
                comments.save()
            except Exception:
                return HttpResponse(0)
            return HttpResponse(1)
        else:
            # 账号异地登陆
            return HttpResponse(2)


def post_replies(request):  # 提交回复（回复评论）
    if request.method == "POST":
        parm = request.POST

        judge = UserInfo.objects.filter(userId=parm.get("userid"), phoneid=parm.get("phoneid"))
        if judge.exists():
            comments = Comments()
            comments.id = parm.get("commentid")
            comments.person_id = parm.get("userid")
            comments.contains = parm.get("contains")
            comments.time = int(round(time.time() * 1000))
            comments.likes = 0
            comments.replies = 0
            comments.comments_num = 0
            comments.root = parm.get("root")
            comments.target_id = parm.get('id')
            comments.parent_id = parm.get("parentid")
            comments.child_id = parm.get("userid")
            comments.save()

            temp = Comments.objects.filter(id=parm.get('id')).first()
            temp.replies = temp.replies + 1
            try:
                temp.save()
                return HttpResponse(1)
            except Exception:
                return HttpResponse(0)
        else:
            # 账号异地登陆
            return HttpResponse(2)


def SubjectsPost(request):  # 上传课程
    if request.method == 'POST':
        parm = request.POST
        subject = Subjects()
        subject.subjectid = 'Sub' + str(int(round(time.time() * 1000)))
        subject.subjecttitle = parm.get('title')
        subject.submittime = str(int(round(time.time() * 1000)))
        subject.filepath = parm.get('filepath')
        subject.titleimage = parm.get('imagepath')
        try:
            subject.save()
            return HttpResponse(1)
        except Exception:
            return HttpResponse(0)


def ClassSectionPost(request):  # 上传课程小节
    if request.method == 'POST':
        parm = request.POST
        classes = ClassSection()
        classes.classid = 'CSec' + str(int(round(time.time() * 1000)))
        classes.classname = parm.get('classname')
        classes.filepath = parm.get('filepath')
        classes.classImage = parm.get('imagepath')
        classes.submittime = str(int(round(time.time() * 1000)))
        classes.subjectid = Subjects(subjectid=parm.get('subjectid'))
        classes.save()
        return HttpResponse(1)
    else:
        return HttpResponse(0)


def SubjectDelete(request):
    if request.method == 'POST':
        parm = request.POST
        try:
            subject = Subjects.objects.all().filter(subjectid=parm.get('subjectid'))
            if not subject.exists():
                return HttpResponse(2)
            subject.delete()
        except Exception:
            return HttpResponse(0)
        return HttpResponse(1)


def SubjectsRequest(request):
    if request.method == 'POST':
        parm = request.POST

        result = Subjects.objects.all().order_by('-subjectid').values()

        data = {}
        print(result.count())
        pagesize = parm.get("pagesize", 10)
        page = parm.get("page", 1)
        paginator = Paginator(result, pagesize)
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        data['subjects'] = list(books)
        return JsonResponse(data)


def ClassSectionRequest(request):
    if request.method == 'POST':
        parm = request.POST

        result = ClassSection.objects.all().filter(subjectid_id=parm.get('subjectid')).order_by(
            'submittime').values()

        data = {}
        print(result.count())
        pagesize = parm.get("pagesize", 10)
        page = parm.get("page", 1)
        paginator = Paginator(result, pagesize)
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        data['classes'] = list(books)
        return JsonResponse(data)


def SubjectCommentPost(request):
    if request.method == 'POST':
        parm = request.POST
        comments = SubjectComments()
        comments.id = 'SubCom' + str(int(round(time.time() * 1000)))
        comments.subjectid = Subjects(subjectid=parm.get('subjectid'))
        comments.contains = parm.get('contains')
        comments.pdfpage = parm.get('pdfpage')
        comments.time = parm.get('time')
        userinfo = UserInfo(userId=parm.get('userid'))
        comments.comment_user_id = userinfo
        comments.comment_user_name = parm.get('username')
        try:
            comments.save()
        except Exception:
            return HttpResponse(0)
        return HttpResponse(1)


def SubjectHomeWorkPost(request):
    if request.method == 'POST':
        parm = request.POST
        homework = TestHomeWorkChoice()
        homework.id = str(int(round(time.time() * 1000)))
        homework.title = parm.get("title", '')
        homework.page = parm.get('page', -1)
        homework.time = parm.get('time', None)
        homework.selectionA = parm.get('A', '')
        homework.selectionB = parm.get('B', '')
        homework.selectionC = parm.get('C', '')
        homework.selectionD = parm.get('D', '')
        homework.selectionE = parm.get('E', '')
        homework.answer = parm.get('answer', '')
        homework.subjectsid = Subjects(subjectid=parm.get('subjectid'))

        try:
            homework.save()
        except Exception:
            return HttpResponse(0)
        return HttpResponse(1)


def SubjectHomeWorkRequest(request):
    if request.method == 'POST':
        parm = request.POST
        data = {}
        result = TestHomeWorkChoice.objects.all().filter(subjectsid_id=parm.get('subjectid')).values()
        try:
            data['result'] = list(result)
            data['code'] = 200
        except Exception:
            data['code'] = 202
        return JsonResponse(data)


def SubjectCommentRequest(request):
    if request.method == 'POST':
        parm = request.POST
        data = {}
        result = SubjectComments.objects.all().filter(subjectid_id=parm.get('subjectid')).values()
        try:
            data['comments'] = list(result)
            data['code'] = 200
        except Exception:
            data['code'] = 202
        return JsonResponse(data)


def Search(request):
    if request.method == 'POST':
        parm = request.POST
        data = {}
        types = parm.get("type", '0')
        print(types)
        pagesize = parm.get('pagesize', 5)
        page = parm.get('page', 1)
        if types == '0' or types == '1':
            print(1)
            result = Notification.objects.all().filter(title__contains=parm.get('keywords')).order_by(
                "-post_time").values()
            paginator = Paginator(result, pagesize)
            try:
                books = paginator.page(page)
            except PageNotAnInteger:
                books = paginator.page(1)
            except EmptyPage:
                books = paginator.page(paginator.num_pages)
            data['notification'] = list(books)
        if types == '0' or types == '2':
            print(2)
            result = Subjects.objects.all().filter(subjecttitle__contains=parm.get('keywords')).order_by(
                '-submittime').values()
            paginator = Paginator(result, pagesize)
            try:
                books = paginator.page(page)
            except PageNotAnInteger:
                books = paginator.page(1)
            except EmptyPage:
                books = paginator.page(paginator.num_pages)
            data['subjects'] = list(books)
        if types == '0' or types == '3':
            print(3)
            result = Theme.objects.all().filter(contains__contains=parm.get('keywords')).order_by('-time').values()
            paginator = Paginator(result, pagesize)
            try:
                books = paginator.page(page)
            except PageNotAnInteger:
                books = paginator.page(1)
            except EmptyPage:
                books = paginator.page(paginator.num_pages)
            data['theme'] = list(books)
        if types == '0' or types == '4':
            print(4)
            result = UserInfo.objects.all().filter(username__contains=parm.get('keywords')).order_by('-userId').values()
            paginator = Paginator(result, pagesize)
            try:
                books = paginator.page(page)
            except PageNotAnInteger:
                books = paginator.page(1)
            except EmptyPage:
                books = paginator.page(paginator.num_pages)
            data['userinfo'] = list(books)
        return JsonResponse(data)


def uploadFiles(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            return HttpResponse('文件未上传')

        ext = pGetFileExtension(file)
        if not pIsAllowedFileType(ext):
            return HttpResponse('文件类型错误')
        md5 = pCalculateMd5(file)
        uploadFile = UploadFiles.getFileByMd5(md5)
        if uploadFile:  # 图片文件已存在则返回图片绝对地址，不存在则保存文件之后再次返回图片网络地址
            return JsonResponse({"url": uploadFile.getFileUrl()})

        uploadImg = UploadFiles()
        uploadImg.file_md5 = md5
        uploadImg.file_size = file.size
        uploadImg.file_type = ext
        uploadImg.save()

        # 打印绝对地址
        print(uploadImg.getFileUrl())
        # 保存 文件到磁盘
        with open(uploadImg.getFilePath(), "wb+") as f:
            # 分块写入
            for chunk in file.chunks():
                f.write(chunk)
            f.close()
        return JsonResponse({"url": uploadImg.getFileUrl()})
    else:
        return render(request, "test.html")


def queryForUserInfo(request):
    if request.method == 'POST':
        parm = request.POST
        user = UserInfo.objects.all().filter(userId=int(parm.get('userid'))).values()
        return JsonResponse(list(user).__getitem__(0))


def NotificationPost(request):
    if request.method == 'POST':
        parm = request.POST
        judge = UserInfo.objects.filter(userId=parm.get("authorid"), phoneid=parm.get("phoneid"))
        print("authorid " + parm.get("authorid") + "\n" + "phoneid " + parm.get("phoneid") + "\n")
        if judge.exists():
            notification = Notification()
            notification.themeid = parm.get('themeid')
            notification.author_id_id = int(parm.get('authorid'))
            notification.title = parm.get('title')
            notification.contains = parm.get('contains')
            notification.post_time = parm.get('posttime')
            notification.headerimage = parm.get('headerimage')
            notification.type = parm.get('type', 0)
            print(notification.contains)
            notification.save()
            return HttpResponse(1)
        else:
            # 账号异地登陆
            return HttpResponse(2)


def NotificationList(request):
    if request.method == 'POST':
        parm = request.POST
        data = {}
        resultList = Notification.objects.all().order_by('-id').values()
        pagesize = 20
        page = parm.get('page', 1)
        paginator = Paginator(resultList, pagesize)
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        for item in books:
            del item['contains']
            user = UserInfo.objects.all().filter(userId=item['author_id_id']).first()
            if user is not None:
                item['username'] = user.username
            print(item['headerimage'])
        data['data'] = list(books)
        return JsonResponse(data)


def NotificationDetails(request):
    if request.method == 'POST':
        parm = request.POST
        themeid = parm.get('themeid', None)
        if themeid is None:
            return HttpResponse('请输入themeid')
        resultlist = Notification.objects.all().filter(themeid=themeid).values()
        result = resultlist.first()
        result['number'] = result['number'] + 1
        object1 = Notification()
        object1.id = result['id']
        object1.themeid = result['themeid']
        object1.title = result['title']
        object1.contains = result['contains']
        object1.author_id_id = result['author_id_id']
        object1.post_time = result['post_time']
        object1.number = result['number']
        object1.headerimage = result['headerimage']
        object1.type = result['type']
        object1.save()
        data = result
        imagesinfo = UploadImage.objects.all().filter(themeid=themeid)
        temp = []
        for item in imagesinfo:
            temp.append(item.getImageUrl())
        data['imageUrl'] = list(temp)
        return JsonResponse(data)


def Survey_List(request):
    if request.method == 'POST':
        parm = request.POST
        data = {}
        temp = Survey.objects.all().order_by('-id').values()

        pagesize = 10
        page = parm.get("page", 1)
        paginator = Paginator(temp, pagesize)
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        data['data'] = list(books)

        return JsonResponse(data)


def uploadSchoolImage(request):  # 上传校徽
    if request.method == 'POST':
        parm = request.POST
        schoolimage = SchoolImage()
        schoolimage.name = parm.get('schoolname')
        print(schoolimage.name)
        file = request.FILES.get('img')
        print(file.name)

        if not file:
            return HttpResponse("need Files.")

        # 检查文件大小
        if not pIsAllowedFileSize(file.size):
            return HttpResponse("文件太大，每个图片大小不超过10M")

        # 获取扩展类型 并 判断
        ext = pGetFileExtension(file)
        if not pIsAllowedImageType(ext):
            return HttpResponse("文件类型错误")

            # 检查md5
        md5 = pCalculateMd5(file)
        uploadImg = UploadImage.getImageByMd5(md5)
        if uploadImg:  # 图片文件已存在
            schoolimage.imagepath = uploadImg.getImageUrl()
            schoolimage.save()
            return HttpResponse("图片已保存")

        uploadImg = UploadImage()
        uploadImg.file_md5 = md5
        uploadImg.file_size = file.size
        uploadImg.file_type = ext
        uploadImg.save()
        schoolimage.imagepath = uploadImg.getImageUrl()
        schoolimage.save()

        # 打印绝对地址
        print(uploadImg.getImageUrl())
        # 保存 文件到磁盘
        with open(uploadImg.getImagePath(), "wb+") as f:
            # 分块写入
            for chunk in file.chunks():
                f.write(chunk)
            f.close()

    return render(request, 'AddSchoolImage.html')


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
        print(result)
        if type is not None:
            # result = '{"index": "1","startTime": "20191028","totleTime": "219","1.": "A","2.": "B","3.": "C","4.": "A","5.": "D","6.": "E"}'
            workbookreader = xlrd.open_workbook(BASE_DIR + '/MediaFiles/SurveyResult/' + str(type) + '.xls')
            worksheetreader = workbookreader.sheet_by_name('sheet1')
            workbook = copy(workbookreader)
            worksheet = workbook.get_sheet(0)
            result = json.loads(result)
            result['id'] = worksheetreader.nrows
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


def Img_Get(request, path):
    im = Image.open(settings.IMAGE_ROOT + path)
    parm = request.GET
    x = parm.get("x", 0)
    y = parm.get("y", 0)
    size = float(parm.get("size", 1))
    if x == 0 and y == 0:
        x, y = im.size
        im = im.resize((int(x * size), int(y * size)), Image.ANTIALIAS)
    else:
        im = im.resize((int(x), int(y)), Image.ANTIALIAS)
    response = HttpResponse(content_type="image/png")
    # 将PIL的image对象写入response中，通过response返回
    im.save(response, "PNG")
    return response


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


# 发送的主题啥的图片上传
def themeImageUpload(request):
    imagelist = []
    if request.method == 'POST':
        parm = request.POST
        file = request.FILES.getlist('img')
        themeid = parm.get('themeid', None)
        for image in file:

            # 检查文件是否存在
            if not image:
                return HttpResponse("need Files.")

            # 检查文件大小
            if not pIsAllowedFileSize(image.size):
                return HttpResponse("文件太大，每个图片大小不超过1M")

            # 检查md5
            md5 = pCalculateMd5(image)
            uploadImg = UploadImage.getImageByMd5(md5)
            if uploadImg:  # 图片文件已存在
                uploadImg.themeid = themeid
                uploadImg.save()
                imagelist.append(uploadImg.getImageUrl())
                continue

            # 获取扩展类型 并 判断
            ext = pGetFileExtension(image)
            if not pIsAllowedImageType(ext):
                return HttpResponse("文件类型错误")

            # 检测通过 创建新的image对象
            # 文件对象即上一小节的UploadImage模型
            uploadImg = UploadImage()
            uploadImg.themeid = themeid
            uploadImg.filename = image.name
            uploadImg.file_size = image.size
            uploadImg.file_md5 = md5
            uploadImg.file_type = ext
            uploadImg.save()  # 插入数据库

            imagelist.append(uploadImg.getImageUrl())

            # 打印绝对地址
            print(uploadImg.getImageUrl())
            # 保存 文件到磁盘
            with open(uploadImg.getImagePath(), "wb+") as f:
                # 分块写入
                for chunk in image.chunks():
                    f.write(chunk)
                f.close()
        return JsonResponse({'ImageList': list(imagelist)})
    return render(request, 'test.html')


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


# 文件类型过滤 我们只允许上传常用的文件
def pIsAllowedFileType(ext):
    if ext in ["ppt", "mp4", "pptx", "avi", "pdf"]:
        return True
    return False


# 文件大小限制
# settings.IMAGE_SIZE_LIMIT是常量配置，我设置为10M
def pIsAllowedFileSize(size):
    limit = 1024 * 1024 * 10
    if size < limit:
        return True
    return False
