import sys
import time
sys.path = ['/site/'] + sys.path
from django.core.management import setup_environ
import settings
setup_environ(settings)

from www.models import Vk_groups, Vk_posts
from site.vk_response import *

count_posts = 15

def get_posts(owner_id, g_name):   
    params = {'owner_id': owner_id, 'count': count_posts}
    answer = vk.wall.get(**params)
    for i in range(count_posts):
        params = {
            'group': g_name,
            'text': answer[i+1]['text'],
            'date': time.strftime("%Y-%m-%d %H:%M:%S+06:00", time.localtime(answer[i+1]['date']))
        }
        try:
            Vk_posts.objects.get_or_create(**params)
        except:
            params['text'] = u'Невозможно отобразить текст статьи'
            Vk_posts.objects.get_or_create(**params)
            

params = {'owner_id': my_id, 'extended': 1, 'filter': 'events, groups, admin'}
answer = vk.groups.get(**params)
for i in range(answer[0]):
    Vk_groups.objects.get_or_create(title = answer[i+1]['name'], gid = '-' + str(answer[i+1]['gid']), is_admin = answer[i+1]['is_admin'], is_closed = answer[i+1]['is_closed'])

groups = Vk_groups.objects.all()
for g in groups:
    get_posts(g.gid, g.title)
    
user = vk.users.get(uid = my_id)
get_posts(my_id, user[0]['first_name']+ ' ' + user[0]['last_name'])
