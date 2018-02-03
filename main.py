#-*- coding:utf-8 -*-
#!usr/bin/env python

'''
已实现功能：
1. 新建文章
2. 查看文章列表及文章详情
3. 编辑和删除文章
4. 用户登入登出及相关功能的权限检查
5. 支持Markdown 支持代码高亮（颜色暂无）
'''

from markdown2 import markdown
from flask import Flask, redirect, url_for, request, \
     render_template, session, Markup
import os
import copy

class BlogMan:
    def __init__(self):
        self.blogs = []
        self.owner = {
            'username': 'LK',
            'password': '123456'
        }

    def loginWith(self, username, password):
        return username == self.owner['username'] \
               and password == self.owner['password']

    def isOwner(self, username):
        return username == self.owner['username']

    def setOwner(self, username, password):
        self.owner = {
            'username': username,
            'password': password
        }
            
    def new(self, title, content):
        index = len(self.blogs)
        self.blogs.append({
            'title': title,
            'content': content,
            'deleted': False,
            'link': '/blogs/' + str(index)
        })

    def list(self):
        blogs = copy.deepcopy(self.blogs)
        return [blog for blog in blogs if not blog['deleted']]

    def find(self, index, inc=0):
        return copy.deepcopy(self._find_(index, inc))

    def _find_(self, index, inc=0):
        if index < len(self.blogs) and index >= 0:
            blog = self.blogs[index]
            if not blog['deleted']:
                return blog
            elif inc != 0:
                '''
                如果指定增量，则递归查找
                 （使逻辑删除后，文章的导航功能仍能正常运行）
                '''
                return self.find(index+inc, inc)
        return False    
        
    def delete(self, index):
        '''
        逻辑删除
        '''
        
        blog = self._find_(index)
        if blog:
            blog['deleted'] = True
            return True
        return False
    
    def update(self, index, title, content):
        blog = self._find_(index)
        if blog:
            blog['title'] = title
            blog['content'] = content
            return True
        return False
        
# Flask相关
app = Flask(__name__)
blogMan = BlogMan()
'''
Flask的session实现方式是利用客户端的cookie，
所以需要一个密钥将session数据加密才能存放在客户端来避免客户端修改数据
'''
app.secret_key = b'\x93\xbf\x8e\xf7\x05\x17\x17\xaa(\x97\xeevax\xb5T\x80\x11\x11w\x93\xec\x02c'

@app.route('/')
def index():
    blogs = blogMan.list()
    for blog in blogs:
        blog['content'] = Markup(markdown(blog['content'], extras=['fenced-code-blocks']))
    
    return render_template('list.html', blogs=blogs)

@app.route('/blogs/new', methods=['GET', 'POST'])
def new_blog():
    if not hasPermission():
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        blogMan.new(request.form['title'], request.form['content'])
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><label>请输入文章标题 <input type=text name=title></label></p>
            <p><label>请输入文章内容 <textarea name="content" cols="40" rows="5"></textarea></label></p>
            <p><input type=submit value="提交">
        </form>
    '''

@app.route('/blogs/edit/<int:index>', methods=['GET', 'POST'])
def edit_blog(index):
    if not hasPermission():
        return redirect(url_for('login'))
     
    blog = blogMan.find(index)
    if request.method == 'POST':
        blogMan.update(index, request.form['title'], request.form['content'])
        return redirect(url_for('index'))

    if blog:
        res = '''
        <form method="post">
            <p><label>请输入文章标题 <input type=text name=title value={title}></label></p>
            <p><label>请输入文章内容 <textarea name="content" cols="40" rows="5">{content}</textarea></label></p>
            <p><input type=submit value="提交">
        </form>
        '''
        return res.format(title=blog['title'], content=blog['content'])
    else:
        return "Not Found", 404

@app.route('/blogs/delete/<int:index>')
def delete_blog(index):
    if not hasPermission():
        return redirect(url_for('login'))
     
    blogMan.delete(index)
    return redirect(url_for('index')) 

@app.route('/blogs/<int:index>')
def blog_detail(index):
    previous_page = blogMan.find(index-1, -1)
    next_page = blogMan.find(index+1, +1)
    blog = blogMan.find(index)
    blog['content'] = Markup(markdown(blog['content'], extras=['fenced-code-blocks']))
    
    return render_template('detail.html', blog=blog, \
                           previous=previous_page, \
                           next=next_page)
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

# 权限检查与用户管理
def hasPermission():
    return 'username' in session and blogMan.isOwner(session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if blogMan.loginWith(username, password):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return '''
        <head><title>用户登录 | Blog</title></head>
        <form method="post">
            <p><label>请输入用户名 <input type=text name=username></label></p>
            <p><label>请输入密码 <input type=password name=password></label></p>
            <p><input type=submit value="登录">
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

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
