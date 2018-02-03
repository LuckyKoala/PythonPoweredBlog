#-*- coding:utf-8 -*-
#!usr/bin/env python

'''
已实现功能：
1. 新建文章
2. 查看文章列表及文章详情
3. 编辑和删除文章
4. 用户登入登出及相关功能的权限检查
5. 支持Markdown 支持代码高亮（颜色暂无）
6. 实现RESTful API
7. 前后台通过JSON交互
'''

from markdown2 import markdown
from flask import Flask, redirect, url_for, request, \
     render_template, session, Markup, jsonify
import os
from blogman import BlogMan

# Flask相关
app = Flask(__name__)
blogMan = BlogMan()
'''
Flask的session实现方式是利用客户端的cookie，
所以需要一个密钥将session数据加密才能存放在客户端来避免客户端修改数据
'''
app.secret_key = b'\x93\xbf\x8e\xf7\x05\x17\x17\xaa(\x97\xeevax\xb5T\x80\x11\x11w\x93\xec\x02c'

# 前台页面
@app.route('/')
def index():
    blogs = blogMan.list()
    for blog in blogs:
        blog['content'] = Markup(markdown(blog['content'], extras=['fenced-code-blocks']))
    
    return render_template('list.html', blogs=blogs)

@app.route('/blogs/<int:index>')
def blog_detail(index):
    previous_page = blogMan.find(index-1, -1)
    next_page = blogMan.find(index+1, +1)
    blog = blogMan.find(index)
    blog['content'] = Markup(markdown(blog['content'], extras=['fenced-code-blocks']))
    
    return render_template('detail.html', blog=blog, \
                           previous=previous_page, \
                           next=next_page)

@app.route('/user/login')
def login_page():
    return render_template('login.html')

@app.route('/user/logout')
def logout_page():
    session.pop('username', None)
    return redirect('/')
        
# API
@app.route('/api/blogs/list')
def list_blog():
    blogs = blogMan.list()
    response = {
        'blogs': blogs,
        'length': len(blogs)
    }
    return jsonify(response), 200

@app.route('/api/blogs/new', methods=['POST'])
def new_blog():
    if not hasPermission():
        response = {'error': 'Please try again after you logged in'}
        return jsonify(response), 401
    
    values = request.get_json()

    # 检查POST数据
    required = ['title', 'content']
    if not all(k in values for k in required):
        response = {'error': 'Missing values'}
        return jsonify(response), 400
    
    blogMan.new(values['title'], values['content'])
    response = {'message': 'New blog created'}
    return jsonify(response), 200

@app.route('/api/blogs/update/<int:index>', methods=['POST'])
def update_blog(index):
    if not hasPermission():
        response = {'error': 'Please try again after you logged in'}
        return jsonify(response), 401
    
    values = request.get_json()

    # 检查POST数据
    required = ['title', 'content']
    if not all(k in values for k in required):
        response = {'error': 'Missing values'}
        return jsonify(response), 400
    
    ret = blogMan.update(index, values['title'], values['content'])
    if ret:
        response = {'message': 'Blog updated'}
        return jsonify(response), 200
    else:
        response = {'error': 'Not Found'}
        return jsonify(response), 404

@app.route('/api/blogs/delete/<int:index>')
def delete_blog(index):
    if not hasPermission():
        response = {'error': 'Please try again after you logged in'}
        return jsonify(response), 401
     
    ret = blogMan.delete(index)
    if ret:
        response = {'message': 'Blog deleted'}
        return jsonify(response), 200
    else:
        response = {'error': 'Not Found'}
        return jsonify(response), 404

@app.route('/api/user/login', methods=['POST'])
def login():
    values = request.get_json()

    # 检查POST数据
    required = ['username', 'password']
    if not all(k in values for k in required):
        response = {'error': 'Missing values'}
        return jsonify(response), 400
    username = values['username']
    password = values['password']
    if blogMan.loginWith(username, password):
        session['username'] = username
        response = {'message': 'Logged in'}
        return jsonify(response), 200
    else:
        response = {'error': 'Username is not matched with password'}
        return jsonify(response), 401

@app.route('/api/user/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    response = {'message': 'Logged out'}
    return jsonify(response), 200   

# Handle HTTP cache properly by adding last modified timestamp of file
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

# 权限检查
def hasPermission():
    return 'username' in session and blogMan.isOwner(session['username'])

if __name__ == '__main__':
    content = '''
    Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor
    incidunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
    nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat.
    Quis aute iure reprehenderit in voluptate velit esse cillum dolore eu fugiat
    nulla pariatur. Excepteur sint obcaecat cupiditat non proident, sunt in
    culpa qui officia deserunt mollit anim id est laborum.
    '''
    #测试 文章新建
    blogMan.new('第一篇博客', content)
    blogMan.new('第二篇博客', content)
    blogMan.new('第三篇博客', content)
    blogMan.new('第四篇博客', content)
    blogMan.new('第五篇博客', content)
    #测试 文章更新
    blogMan.update(0, '第一篇博客', '编辑后的内容')
    #测试 文章删除及其他功能对逻辑删除的支持（例如文章详情的导航）
    blogMan.delete(1)
    blogMan.delete(3)
    #测试 markdown文档
    blogMan.new('Markdown文章', '[Blog](http://twodam.net)  `hi`')
    #运行
    app.run(host='127.0.0.1', port=5000)
