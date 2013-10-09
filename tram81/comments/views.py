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


import json
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .models import Comment


class ThreadView(TemplateView):
    template_name = "thread.html"
    def get_context_data(self, **kwargs):
        context = super(ThreadView, self).get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(thread=context['thread']).order_by('ts')
        
        return context



def create_comment(request):
    try:
        txt = request.POST['txt']
        thread = request.POST['thread']
        user = request.user
        
        cmt = Comment.objects.create(commenter=user, 
                                    content=txt, 
                                    thread=thread)
        cmt.save()
    except Exception, ex:
        return HttpResponseServerError(json.dumps(dict(reason=str(ex))), mimetype="application/json")
    return HttpResponse(json.dumps(dict(status='OK')), mimetype="application/json")
    