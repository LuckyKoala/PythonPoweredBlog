#-*- coding:utf-8 -*-
#!usr/bin/env python

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
        index = str(len(self.blogs))
        self.blogs.append({
            'title': title,
            'content': content,
            'deleted': False,
            'id': index
        })
        return index

    def list(self):
        blogs = copy.deepcopy(self.blogs)
        return [blog for blog in blogs if not blog['deleted']]

    def find(self, index, inc=0):
        ret = self._find_(index, inc)
        if ret:
            # 只克隆博客数据
            return copy.deepcopy(ret)
        return False

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
                return self._find_(index+inc, inc)
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
