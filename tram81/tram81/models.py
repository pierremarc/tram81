# -*- coding: utf-8 -*-
"""
    Copyright (C) 2013  Pierre Marchand <pierremarc07@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from django.db import models

from markdown2 import Markdown

class Page(models.Model):
    
    title = models.CharField(max_length=256)
    content = models.TextField(default=u'', blank=True)
    
    title_height = models.IntegerField(default=0, editable=False)
    title_width = models.IntegerField(default=0, editable=False)
    title_image = models.ImageField(upload_to='image_title', 
                              height_field='title_height', 
                              width_field='title_width', 
                              max_length=124)
    
    
    title_height = models.IntegerField(default=0, editable=False)
    title_width = models.IntegerField(default=0, editable=False)
    title_image = models.ImageField(upload_to='image_title', 
                              height_field='title_height', 
                              width_field='title_width', 
                              max_length=124, 
                              blank=True)
    
    
    content_height = models.IntegerField(default=0, editable=False)
    content_width = models.IntegerField(default=0, editable=False)
    content_image = models.ImageField(upload_to='image_content', 
                              height_field='content_height', 
                              width_field='content_width', 
                              max_length=124, 
                              blank=True)
    
    def formated_content(self):
        md = Markdown()
        try:
            return md.convert(self.content)
        except Exception:
            pass
        return self.content
    
    def __unicode__(self): 
        return self.title
    
    