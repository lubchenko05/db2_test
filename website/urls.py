from django.conf.urls import url
from .views import registration, home, log_in, log_out, verify, like, dislike, about, create_post, post_detail

urlpatterns = [
    url(r'^registration/$', registration, name='registration'),
    url(r'^login/$', log_in, name='login'),
    url(r'^logout/$', log_out, name='logout'),
    url(r'^verify/$', verify, name='verify'),
    url(r'^post/(?P<pk>[0-9]+)$', post_detail, name='post_detail'),
    url(r'^post/(?P<pk>[0-9]+)/like$', like, name='like'),
    url(r'^post/(?P<pk>[0-9]+)/dislike$', dislike, name='dislike'),
    url(r'^about/$', about, name='about'),
    url(r'post/create/$', create_post, name='create_post'),
    url(r'^$', home, name='home'),
    url(r'^search/(?P<search>\w+)$', home, name='home'),
    url(r'^order_by/(?P<order_by>\w+)$', home, name='home'),
    url(r'^(?P<search>\w+)/(?P<order_by>\w+)$', home, name='home'),
]