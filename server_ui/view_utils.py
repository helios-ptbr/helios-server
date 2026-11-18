"""
Utilities for single election views

Ben Adida (2009-07-18)
"""

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import get_language

from helios_auth.security import get_user


##
## template abstraction
##
def render_template(request, template_name, values = None):
  vars_with_user = values.copy() if values is not None else {}
  vars_with_user['user'] = get_user(request)
  vars_with_user['settings'] = settings
  vars_with_user['CURRENT_URL'] = request.path
  
  # csrf protection
  if 'csrf_token' in request.session:
    vars_with_user['csrf_token'] = request.session['csrf_token']
  
  # fork pt-BR: páginas longas têm um template por idioma (ex.: faq.pt-BR.html). Sem ele, usa o original.
  names = ['server_ui/templates/%s.html' % template_name]
  parts = (get_language() or 'en').split('-')
  if parts[0] != 'en':
    if len(parts) > 1:
      parts[1] = parts[1].upper()
    names.insert(0, 'server_ui/templates/%s.%s.html' % (template_name, '-'.join(parts)))
  return render(request, names, vars_with_user)
  
