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

import datetime

from django.views.generic import TemplateView
from django.conf import settings
from django.middleware.csrf import get_token

from api.models import GeoImage



class IndexView(TemplateView):
    template_name = "base.html"
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        
        try:
            y = int(context['y'])
            m = int(context['m'])
            d = int(context['d'])
            req_images = GeoImage.objects.filter(pub_date=datetime.date(y,m,d))
        except Exception, ex:
            try:
                req_images = GeoImage.objects.filter(pk=context['pk'])
            except Exception:
                req_images = [GeoImage.objects.all().order_by('pub_date')[0]]
        ids = []
        for ri in req_images:
            ids.append(str(ri.pk))
        context['REQ_IMAGES'] = ','.join(ids)
        context['FB_APP_ID'] = getattr(settings, 'SOCIAL_AUTH_FACEBOOK_KEY', '~')
        return context
    
class JSConf(TemplateView):
    template_name = "tram81.js"
    
    def get_context_data(self, **kwargs):
        context = super(JSConf, self).get_context_data(**kwargs)
        context['TILE_SERVER'] = settings.TILE_SERVER
        context['images'] = GeoImage.objects.all().order_by('pub_date')
        ids = self.request.GET['ids'].split(',')
        context['REQ_IMAGES'] = GeoImage.objects.filter(pk__in=ids)
        context['csrf'] = get_token(self.request)
        
        return context
        
        
        
        