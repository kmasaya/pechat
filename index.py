#!/usr/bin/python3.4

import os
import time
import datetime
import json
import hashlib

from bottle import jinja2_template as template

from bottle import get, post, request, response, run, static_file, redirect, html_escape
import peewee

from models import BASE_DIR, User, Site, Comment, Session


DEBUG = True

STATIC_DIR = os.path.join(BASE_DIR, 'static')
IMAGE_DIR = os.path.join(STATIC_DIR, 'image')

SESSION_LIFE_TIME = 4*24*60*60

if DEBUG:
    BASE_URL = 'http://localhost:8080/'
else:
    BASE_URL = 'http://pechat.w32.jp/'


def render(template_name, **kwargs):
    return template(template_name, kwargs, BASE_URL=BASE_URL)


def request_is_get():
    if request.method == 'GET':
        return True
    return False


def signin(user):
    sid = hashlib.sha256(repr(time.time()).encode()).hexdigest()
    response.set_cookie('sid', sid, max_age=SESSION_LIFE_TIME, path='/')
    response.set_cookie('username', user.username, max_age=SESSION_LIFE_TIME, path='/')

    Session.create(
        user=user,
        sid=sid
    )


def signout():
    sid = request.get_cookie('sid', None)

    if sid:
        response.delete_cookie('sid')
        response.delete_cookie('username')
        query = Session.delete().where(Session.sid == sid)
        query.execute()


def session_user():
    sid = request.get_cookie('sid', None)
    username = request.get_cookie('username', None)

    try:
        session = Session.get(Session.sid == sid)
    except:
        signout()
        return None

    if session.accessed_at < datetime.datetime.now() - datetime.timedelta(seconds=SESSION_LIFE_TIME):
        signout()
        return None

    if session.user.username != username:
        return None

    if session.user.is_active is False:
        return None

    return session.user


@get('/')
def index_view():
    return render('index')


@get('/signup/')
@post('/signup/')
def signup_view():
    if request_is_get():
        return render('signup')

    username = request.forms.get('username', '')
    password = request.forms.get('password', '')

    try:
        user = User.get(User.username == username, User.is_active == True)
    except peewee.DoesNotExist:
        user = User.create(
            username=username,
            password=password,
        )
    else:
        return render('signup', message='ユーザ名が既に利用されています。')

    signin(user)

    return render('redirect', redirect_url='/manage/')


@get('/signin/')
@post('/signin/')
def signin_view():
    if request_is_get():
        return render('signin')

    username = request.forms.get('username', '')
    password = request.forms.get('password', '')

    try:
        user = User.get(User.username == username, User.password == password, User.is_active == True)
    except peewee.DoesNotExist:
        return render('/signin/', message='ユーザ名が存在しないかパスワードが正しくありません。')

    signin(user)

    return render('redirect', redirect_url='/manage/')


@get('/signout/')
def signout_view():
    signout()

    return render("redirect", redirect_url="/")


@get('/manage/')
def manage_view():
    user = session_user()
    if user is None:
        return redirect('/signout/')

    sites = Site.select().where(Site.user == user, Site.is_active == True)

    return render('manage', user=user, sites=sites)


@get('/manage/site/new/')
@post('/manage/site/new/')
def manage_site_new_view():
    user = session_user()
    if user is None:
        return redirect('/signout/')

    if request_is_get():
        return render('manage_site_new', user=user)

    site_id = request.forms.decode().get('site_id')
    title = request.forms.decode().get('title', 'タイトル無し')
    body = request.forms.decode().get('body', '')

    try:
        Site.get(Site.site_id == site_id, Site.is_active == True)
    except peewee.DoesNotExist:
        pass
    else:
        return render('manage_site_new', user=user, message='SiteIDは既に利用されています。')

    site = Site.create(
        user=user,
        site_id=site_id,
        title=title,
        body=body,
    )

    return redirect('/manage/')


@get('/manage/site/<site_id:int>/')
@post('/manage/site/<site_id:int>/')
def manage_site_id_view(site_id):
    user = session_user()
    if user is None:
        return redirect('/signout/')

    try:
        site = Site.get(Site.user == user, Site.id == site_id, Site.is_active == True)
    except peewee.DoesNotExist:
        return render('redirect', redirect_url='/manage/')

    if request_is_get():
        return render("manage_site_id", user=user, site=site)

    title = request.forms.decode().get('title', 'タイトル無し')
    body = request.forms.decode().get('body', '')

    site.title = title
    site.body = body
    site.save()

    return redirect('/manage/')


@get('/manage/site/code/<site_id:int>/')
def manage_site_code_view(site_id):
    user = session_user()
    if user is None:
        return redirect('/signout/')

    try:
        site = Site.get(Site.user == user, Site.id == site_id, Site.is_active == True)
    except peewee.DoesNotExist:
        return render('redirect', redirect_url='/manage/')

    return render('manage_site_code', user=user, site=site)


@get('/comment/<site_id>/receive/')
@post('/comment/<site_id>/receive/')
def chat_receive(site_id):
    received_last = request.query.decode().get('received_last', None)
    if received_last is None:
        return "undefine"

    try:
        site = Site.get(Site.site_id == site_id, Site.is_active == True)
    except peewee.DoesNotExist:
        return "undefine"

    comments = []
    for comment in Comment.select().where(
        Comment.site == site,
        Comment.id > received_last,
        Comment.created_at > datetime.datetime.now() - datetime.timedelta(minutes=5),
        Comment.is_active == True
    ):
        comments.append({
            'id': comment.id,
            'nickname': comment.nickname,
            'message': comment.message,
            'created_at': comment.created_at.strftime('%H:%M'),
        })

    message_last_id = Comment.select().count()

    response.content_type = 'application/json; charset=utf-8'
    return 'pechat(%s);' % (json.dumps({'comments': comments, 'received_last': message_last_id}),)


@get('/comment/<site_id>/')
@post('/comment/<site_id>/')
def chat_comment(site_id):
    nickname = request.query.decode().get('nickname', None)
    message = request.query.decode().get('message', None)
    if nickname is None or message is None:
        return "undefine"

    try:
        site = Site.get(Site.site_id == site_id, Site.is_active == True)
    except peewee.DoesNotExist:
        return "undefine"

    Comment.create(
        site=site,
        nickname=nickname,
        message=message,
    )

    response.content_type = 'application/json; charset=utf-8'
    return chat_receive(site_id)


@get('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_DIR)


if __name__ == '__main__':
    run(host='localhost', port=8080, reloader=True, debug=True)

