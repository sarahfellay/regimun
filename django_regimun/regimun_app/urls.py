from django.conf.urls.defaults import patterns
from django.views.generic.list_detail import object_detail, object_list
from regimun_app.views.school_admin import *
from regimun_app.views.secretariat_admin import *

conferences = Conference.objects.all()

@login_required
def limited_object_detail(*args, **kwargs):
    return object_detail(*args, **kwargs)

urlpatterns = patterns('',
    # conferences index
    (r'^$', object_list, dict(queryset=conferences)),
    
    # register new cconference
    (r'^new-conference/$', create_conference),

    # school was created
    (r'^(?P<conference_slug>[-\w]+)/created$', conference_created),
    
    # schools index
    (r'^(?P<slug>[-\w]+)/$', object_detail, dict(queryset=conferences, slug_field='url_name')),

    # secretariat admin page
    (r'^(?P<slug>[-\w]+)/secretariat/$',
        limited_object_detail,
        dict(queryset=conferences, slug_field='url_name', template_name='secretariat/index.html')),

    # secretariat admin page - downloads
    (r'^(?P<conference_slug>[-\w]+)/secretariat/downloads/', spreadsheet_downloads),

    # invoices
    (r'^(?P<conference_slug>[-\w]+)/secretariat/invoices$', generate_all_invoices),

    # redirect to school page
    (r'^(?P<conference_slug>[-\w]+)/secretariat/see-school$', redirect_to_school),

    # register new school
    (r'^(?P<conference_slug>[-\w]+)/new-school/$', create_school),

    # school was created
    (r'^(?P<conference_slug>[-\w]+)/(?P<school_slug>[-\w]+)/created$', school_created),
    
    # school invoice
    (r'^(?P<conference_slug>[-\w]+)/(?P<school_slug>[-\w]+)/invoice$', generate_invoice),
    
    # school admin page
    (r'^(?P<conference_slug>[-\w]+)/(?P<school_slug>[-\w]+)/$', school_admin),

)