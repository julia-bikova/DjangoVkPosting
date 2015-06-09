# -*- encoding: utf-8 -*-
from vkappauth import VKAppAuth
import vkontakte

email = 'example@email.ru'
password = 'password'
app_id = 'app_id'
scope = ['notify', 'friends', 'photos', 'audio', 'video', 'docs', 'notes', 'pages', 'status', 'wall', 'groups',
         'messages', 'notifications', 'stats', 'ads']
vkaa = VKAppAuth()
access_data = vkaa.auth(email, password, app_id, scope)
token = access_data['access_token']
my_id = access_data['user_id']
vk = vkontakte.API(token=token)
