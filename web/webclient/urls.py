"""
This reroutes from an URL to a python view-function/class.

The main web/urls.py includes these routes for all urls starting with
/webclient/ so it can reroute to the web-based MUD client.

"""

from django.urls import path

from evennia.web.webclient.urls import urlpatterns as evennia_webclient_urlpatterns

# add patterns here
urlpatterns = [
    # path("url-pattern", imported_python_view),
]

# read by Django
urlpatterns = urlpatterns + evennia_webclient_urlpatterns
