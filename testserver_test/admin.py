from django.contrib import admin
from testserver_test.models import *

# Register your models here.

admin.site.site_header = '青春彩虹伞后台管理'
admin.site.site_title = '彩虹伞'


class Survey(admin.ModelAdmin):
    list_display = ('title', 'type', 'warning', 'problem1', 'problem2', 'problem3', 'problemOffset')
    list_editable = ('title', 'type', 'warning', 'problem1', 'problem2', 'problem3')
    list_per_page = 10  # 每页显示行数
    ordering = ('-type',)  # 排序，默认升序，前面加-则降序
    search_fields = ('title', 'type', 'warning')  # 显示搜索框，在搜索框内可通过指定字段进行搜索


class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('userId', 'username', 'age', 'coin')  # 默认只显示显示一列，list_display指定显示列，存在多对多关系的列不能指定显示和可编辑
    list_editable = ('username', 'age', 'coin')  # 显示界面可编辑的列
    list_per_page = 5  # 每页显示行数
    ordering = ('username',)  # 排序，默认升序，前面加-则降序
    search_fields = ('userId', 'username', 'age')  # 显示搜索框，在搜索框内可通过指定字段进行搜索


class InvestigationQuestionsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'type', 'title', 'selectionA', 'selectionB', 'selectionC', 'selectionD', 'A_next', 'B_next', 'C_next',
        'D_next')  # 默认只显示显示一列，list_display指定显示列，存在多对多关系的列不能指定显示和可编辑
    list_editable = ('A_next', 'B_next', 'C_next', 'D_next')  # 显示界面可编辑的列
    list_per_page = 10  # 每页显示行数
    ordering = ('-type',)  # 排序，默认升序，前面加-则降序
    search_fields = ('id', 'type', 'title')  # 显示搜索框，在搜索框内可通过指定字段进行搜索


class mutipleQuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'title', 'selectionA', 'selectionB', 'selectionC',
                    'selectionD')  # 默认只显示显示一列，list_display指定显示列，存在多对多关系的列不能指定显示和可编辑
    list_per_page = 5  # 每页显示行数
    ordering = ('-type',)  # 排序，默认升序，前面加-则降序
    search_fields = ('id', 'type', 'title')  # 显示搜索框，在搜索框内可通过指定字段进行搜索


class manualQuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'title')  # 默认只显示显示一列，list_display指定显示列，存在多对多关系的列不能指定显示和可编辑
    list_per_page = 5  # 每页显示行数
    ordering = ('-type',)  # 排序，默认升序，前面加-则降序
    search_fields = ('id', 'type', 'title')  # 显示搜索框，在搜索框内可通过指定字段进行搜索


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'theme_id', 'person_id', 'time', 'contains', 'likes', 'replies',
                    'comments_num')  # 默认只显示显示一列，list_display指定显示列，存在多对多关系的列不能指定显示和可编辑
    list_per_page = 5  # 每页显示行数
    ordering = ('-theme_id',)  # 排序，默认升序，前面加-则降序
    search_fields = ('id', 'themeid', 'person_id')  # 显示搜索框，在搜索框内可通过指定字段进行搜索


class CommentRelationsAdmin(admin.ModelAdmin):
    list_display = ('userId', 'username', 'age', 'coin')  # 默认只显示显示一列，list_display指定显示列，存在多对多关系的列不能指定显示和可编辑
    list_editable = ('username', 'age', 'coin')  # 显示界面可编辑的列
    list_per_page = 5  # 每页显示行数
    ordering = ('username',)  # 排序，默认升序，前面加-则降序
    search_fields = ('userId', 'username', 'age')  # 显示搜索框，在搜索框内可通过指定字段进行搜索


admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(InvestigationQuestions, InvestigationQuestionsAdmin)
admin.site.register(mutipleQuestions, mutipleQuestionsAdmin)
admin.site.register(manualQuestions, manualQuestionsAdmin)
# admin.site.register(Comments, CommentsAdmin)
# admin.site.register(CommentRelations,CommentRelationsAdmin)
