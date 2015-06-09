# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django import forms
from site.local_settings import MEDIA_ROOT
from site.vk_response import *

from tinymce.models import HTMLField
from tinymce.widgets import TinyMCE

import requests
import re

photo_vk_path = 'photo_vk'
files_vk_path = 'files_vk'

def use_vk(self):
    msg = self.title + '\n' + self.text
    msg = re.sub('<.*?>','',msg)
    post_vk = 0
            
    groups = [g for g in self.group_vk.all()]

    if groups or self.wall_user_vk:
        post_vk = 1

    if post_vk:
        attachments = []
        if self.photo_vk:
            server = vk.photos.getWallUploadServer(uid = my_id)
            path = MEDIA_ROOT + photo_vk_path + '/' + re.split('/', self.photo_vk.url)[-1]
            r = requests.post(server['upload_url'], files={'photo': open(path,"rb")})
            params = {'server': r.json()['server'], 'photo': r.json()['photo'], 'hash': r.json()['hash']}
            wallphoto = vk.photos.saveWallPhoto(**params)
            attachments.append(wallphoto[0]['id'])
                    
        if self.file_vk:
            server = vk.docs.getWallUploadServer()
            path = MEDIA_ROOT + files_vk_path + '/' + re.split('/', self.file_vk.url)[-1]
            r = requests.post(server['upload_url'], files={'file': open(path,"rb")})
            params = {'file': r.json()['file']}
            doc = vk.docs.save(**params)
            attachments.append('doc' + str(my_id) + '_' + str(doc[0]['did']))
                    
        params = {'attachments': ','.join(attachments), 'message': msg} 
        if self.wall_user_vk:
            params['owner_id'] = my_id
            vk.wall.post(**params)
                    
        if len(groups):
            if self.group_stat:
                params['from_group'] = 1
            for g in groups:
                params['owner_id'] = g.gid
                vk.wall.post(**params)
         

class Vk_groups(models.Model):
    title = models.CharField(max_length=1000, verbose_name=u'Название группы')
    gid = models.CharField(max_length=1000, verbose_name=u'ID группы')
    is_closed = models.BooleanField(verbose_name=u'Закрытая группа', default=False)
    is_admin = models.BooleanField(verbose_name=u'Пользователь является администратором', default=False)

    def __str__(self):
        return self.title.encode('utf8')

    class Meta:
        verbose_name = "Группа Вконтакте"
        verbose_name_plural = "Группы Вконтакте"


class Vk_posts(models.Model):
    group = models.CharField(max_length=1000, verbose_name=u'Страница/группа', blank=True)
    text = HTMLField(verbose_name=u'Текст записи', blank=True)
    date = models.DateTimeField(verbose_name=u'Дата публикации', blank=True)

    def __str__(self):
        return self.group.encode('utf8')

    class Meta:
        verbose_name = "Запись Вконтакте"
        verbose_name_plural = "Записи Вконтакте"
        

class vk_fields(models.Model):
    photo_vk = models.ImageField(upload_to=photo_vk_path, verbose_name=u'Прикрепить фото для Вконтакте', max_length = 1000, blank=True)
    file_vk = models.FileField(upload_to=files_vk_path, verbose_name=u'Прикрепить документ для Вконтакте', max_length = 1000, blank=True)
    wall_user_vk = models.BooleanField(verbose_name=u'Отправить на стену пользователя Вконтакте', default=False)
    group_vk = models.ManyToManyField(Vk_groups, verbose_name=u'Отправить в следующие группы Вконтакте', blank=True)
    group_stat = models.BooleanField(verbose_name=u'Публиковать запись от имени группы', default=False)

    class Meta:
        abstract = True


class Page(vk_fields):
    old_id = models.IntegerField(verbose_name=u'Старый id страницы', editable=False, blank=True, default = 1)
    title = models.CharField(max_length=1000, verbose_name=u'Название')
    description = models.TextField(verbose_name=u'Описание', blank=True)
    keywords = models.CharField(max_length=1000, verbose_name=u'Ключевые слова', blank=True)
    text = HTMLField(verbose_name=u'Текст страницы', blank=True)
    slug = models.CharField(max_length=255, verbose_name=u'URL-имя страницы', blank=True)
    order = models.FloatField(verbose_name=u'Порядковый номер', blank=True, default = 1.0)
    parent = models.ForeignKey('self', null=True, verbose_name=u'Родитель', blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    changed = models.DateTimeField(auto_now=True, auto_now_add=True, verbose_name=u'Дата последнего изменения')
    image = models.TextField(verbose_name=u'Поле для картинок', blank=True)
    new_page = models.BooleanField(verbose_name=u'New!', default=False)
    hidden = models.BooleanField(verbose_name=u'Скрыть страницу', default=False)
    blocked = models.BooleanField(verbose_name=u'заблокировать страницу', default=False)
    carousel = models.BooleanField(verbose_name=u'Показать в карусели', default=False)
    photo = models.ImageField(upload_to='carousel', verbose_name=u'Фото для карусели', max_length = 1000, blank=True)

    def save(self, *args, **kwargs):
        use_vk(self)   
        model = super(Page, self).save(*args, **kwargs)

    def get_parents(self):
        parents = []
        page = self
        while page.parent:
            parents.append(page.parent)
            page = page.parent
        return reversed(parents)

    def full_slug(self):
        url = []
        page = self
        while page.slug:
            url.append(page.slug)
            page = page.parent
        return '/'+'/'.join(reversed(url))

    def get_childs(self):
        childs = Page.objects.filter(parent = self)
        list_of_childs = [el for el in childs]
        return list_of_childs


    def __str__(self):
        return self.title.encode('utf8')

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ('order',)
        

class Area(models.Model):
    title = models.CharField(max_length=1000, verbose_name=u'Название')
    txt = models.TextField(verbose_name=u'Описание', blank=True)

    def __str__(self):
        return self.title.encode('utf8')

    class Meta:
        verbose_name = "Область"
        verbose_name_plural = "Области"


class CSS(models.Model):
    title = models.CharField(max_length=1000, verbose_name=u'Название')
    comment = models.TextField(verbose_name=u'Поле для комментариев', blank=True)
    
    def __str__(self):
        return self.title.encode('utf8')
    
    class Meta:
        verbose_name = "CSS-Стиль"
        verbose_name_plural = "СSS-Стили"        


class Block(models.Model):
    task_types = (('html','html-блок'),('menu','меню'))
    title = models.CharField(max_length=1000, verbose_name=u'Название')
    types = models.CharField(choices=task_types, max_length=100, default = 'html', verbose_name=u'Тип блока')
    txt = HTMLField(verbose_name=u'Текстовое поле', blank=True)
    menu = models.ManyToManyField(Page, verbose_name=u'Страницы в меню', blank=True, related_name='m+')
    id_css = models.CharField(max_length=100, verbose_name=u'Идентификатор блока')
    css_stile = models.ManyToManyField(CSS, verbose_name=u'CSS-стили блока', blank=True)
    show_on_pages = models.ManyToManyField(Page, verbose_name=u'Показывать блок на страницах', blank=True, related_name='s+')
    areas = models.ForeignKey('Area', verbose_name=u'Область')
    sort = models.DecimalField(max_digits=4, decimal_places=2, verbose_name=u'Сортировка')
    hidden = models.BooleanField(verbose_name=u'Скрыть блок', default=False)
   
    def __str__(self):
        return self.title.encode('utf8')

    def get_css(self):
        list_of_css = self.css_stile.all()
        str_css = [css.title for css in list_of_css]
        return ', '.join(str_css)
    get_css.short_description = 'CSS-стили блока'

    def get_show_pages(self):
        list_of_pages = self.show_on_pages.all()
        pages_title_list = [page.title for page in list_of_pages]
        return pages_title_list

    class Meta:
        verbose_name = "Блок"
        verbose_name_plural = "Блоки"
        ordering = ('sort',)


class Rubric(models.Model):
    title = models.CharField(max_length=1000, verbose_name=u'Название')
    slug = models.CharField(max_length=255, verbose_name=u'URL-имя рубрики')
    
    def __str__(self):
        return self.title.encode('utf8')

    class Meta:
        verbose_name = "Рубрика"
        verbose_name_plural = "Рубрики"

    
class News(vk_fields):
    title = models.CharField(max_length=1000, verbose_name=u'Название')
    description = models.TextField(verbose_name=u'Описание', blank=True)
    text = HTMLField(verbose_name=u'Текстовое поле')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата публикации')
    rubrics = models.ManyToManyField(Rubric, verbose_name=u'Рубрики', blank=True)
    slug = models.CharField(max_length=255, verbose_name=u'URL-имя новости', blank=True)
    order = models.FloatField(verbose_name=u'Порядковый номер', blank=True, default = 1.0)
    new_news = models.BooleanField(verbose_name=u'New!', default=False)
    hidden = models.BooleanField(verbose_name=u'Скрыть новость', default=False)
    image = models.TextField(verbose_name=u'Поле для картинок', blank=True)
    carousel = models.BooleanField(verbose_name=u'Показать в карусели', default=False)
    photo = models.ImageField(upload_to='carousel', verbose_name=u'Фото для карусели', max_length = 1000, blank=True)

    def save(self, *args, **kwargs):
        use_vk(self)   
        model = super(News, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title.encode('utf8')

    def get_rubrics(self):
        list_of_rubrics = self.rubrics.all()
        str_rubric = [rubric.title for rubric in list_of_rubrics]
        return ', '.join(str_rubric)
    get_rubrics.short_description = 'Рубрики'
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

      
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'hidden', 'blocked', 'changed', 'order')
    search_fields = ('title',)
    list_filter = ['parent','carousel','new_page','hidden']
    date_hierarchy = 'changed'
    filter_horizontal = ('group_vk',)

class BlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'types', 'get_css', 'sort')
    search_fields = ('title',)
    list_filter = ['types','areas', 'menu', 'css_stile', 'show_on_pages', 'hidden']
    filter_horizontal = ('menu', 'show_on_pages')

class CSSAdmin(admin.ModelAdmin):
    list_display = ('title', 'comment')
    search_fields = ('title',)

class AreaAdmin(admin.ModelAdmin):
    list_display = ('title', 'txt')
    search_fields = ('title',)

class VkGroupsAdmin(admin.ModelAdmin):
    list_display = ('title', 'gid', 'is_closed', 'is_admin')
    search_fields = ('title', 'gid')

class VkPostsAdmin(admin.ModelAdmin):
    list_display = ('group', 'text', 'date')
    search_fields = ('group', 'date')
    list_filter = ['group', 'date']
    date_hierarchy = 'date'

class RubricAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'get_rubrics', 'created')
    search_fields = ('title',)
    list_filter = ['rubrics','carousel', 'new_news', 'hidden']
    date_hierarchy = 'created'
    filter_horizontal = ('group_vk',)

admin.site.register(Page, PageAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(CSS, CSSAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Rubric, RubricAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Vk_groups, VkGroupsAdmin)
admin.site.register(Vk_posts, VkPostsAdmin)
