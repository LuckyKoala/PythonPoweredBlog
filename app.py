#-*- coding:utf-8 -*-
#!usr/bin/env python

from flask import Flask, render_template
from blogman import BlogMan

# Flask相关
app = Flask(__name__)
blogMan = BlogMan()

# 前台页面
@app.route('/')
def index():
    blogs = blogMan.list()
    return render_template('list.html', blogs=blogs)

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
    #运行在本地的5000端口上
    app.run(host='127.0.0.1', port=5000)
