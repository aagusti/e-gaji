import locale
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import has_permission
from pyramid.events import subscriber
from pyramid.events import BeforeRender
from pyramid.interfaces import IRoutesMapper
from pyramid.httpexceptions import (
    default_exceptionresponse_view,
    HTTPFound,
    )

from sqlalchemy import engine_from_config

from .security import group_finder, get_user
from .models import (
    DBSession,
    Base,
    init_model,
    )
from .tools import DefaultTimeZone, get_months


# http://stackoverflow.com/questions/9845669/pyramid-inverse-to-add-notfound-viewappend-slash-true    
class RemoveSlashNotFoundViewFactory(object):
    def __init__(self, notfound_view=None):
        if notfound_view is None:
            notfound_view = default_exceptionresponse_view
        self.notfound_view = notfound_view

    def __call__(self, context, request):
        if not isinstance(context, Exception):
            # backwards compat for an append_notslash_view registered via
            # config.set_notfound_view instead of as a proper exception view
            context = getattr(request, 'exception', None) or context
        path = request.path
        registry = request.registry
        mapper = registry.queryUtility(IRoutesMapper)
        if mapper is not None and path.endswith('/'):
            noslash_path = path.rstrip('/')
            for route in mapper.get_routes():
                if route.match(noslash_path) is not None:
                    qs = request.query_string
                    if qs:
                        noslash_path += '?' + qs
                    return HTTPFound(location=noslash_path)
        return self.notfound_view(context, request)
    
    
# https://groups.google.com/forum/#!topic/pylons-discuss/QIj4G82j04c
def url_has_permission(request, permission):
    return has_permission(permission, request.context, request)

@subscriber(BeforeRender)
def add_global(event):
     event['permission'] = url_has_permission

def get_title(request):
    route_name = request.matched_route.name
    return titles[route_name]

routes = [    
    ('home', '/', 'Home'),
    ('app', '/app', 'Aplikasi'),
    ('login', '/login', 'Login'),
    ('logout', '/logout', None),
    ('password', '/password', 'Change password'),
    
    ('user', '/user', 'Users'),
    ('user-act', '/user/act/{act}', 'Users'),
    ('user-add', '/user/add', 'Tambah user'),
    ('user-edit', '/user/{id}/edit', 'Edit user'),
    ('user-delete', '/user/{id}/delete', 'Hapus user'),

    ('change-act', '/change/{act}', 'change'),
    ('group', '/group', 'Groups'),
    ('group-act', '/group/act/{act}', ''),
    ('group-add', '/group/add', 'Tambah group'),
    ('group-edit', '/group/{id}/edit', 'Edit group'),
    ('group-delete', '/group/{id}/delete', 'Hapus group'),

    ('urusan', '/urusan', 'urusans'),
    ('urusan-add', '/urusan/add', 'Tambah urusan'),
    ('urusan-edit', '/urusan/{id}/edit', 'Edit urusan'),
    ('urusan-delete', '/urusan/{id}/delete', 'Hapus urusan'),
    ('urusan-act', '/urusan/act/{act}', 'urusans'),

    ('unit', '/unit', 'units'),
    ('unit-add', '/unit/add', 'Tambah unit'),
    ('unit-edit', '/unit/{id}/edit', 'Edit unit'),
    ('unit-delete', '/unit/{id}/delete', 'Hapus unit'),
    ('unit-act', '/unit/act/{act}', 'units'),
    
    ('potongan', '/potongan', 'potongans'),
    ('potongan-add', '/potongan/add', 'Tambah potongan'),
    ('potongan-edit', '/potongan/{id}/edit', 'Edit potongan'),
    ('potongan-delete', '/potongan/{id}/delete', 'Hapus potongan'),
    ('potongan-act', '/potongan/act/{act}', 'potongans'),

    ('gaji', '/gaji', 'Gaji'),
    ('gaji-act', '/gaji/act/{act}', 'Gaji Action'),
    
    ('gaji-potongan', '/gaji-potongan', 'Potongan Gaji'),
    ('gaji-potongan-add', '/gaji-potongan/add', 'Tambah Potongan'),
    ('gaji-potongan-edit', '/gaji-potongan/{id}/edit', 'Edit Potongan'),
    ('gaji-potongan-delete', '/gaji-potongan/{id}/delete', 'Hapus Potongan'),
    ('gaji-potongan-act', '/gaji-potongan/act/{act}', ''),

    
    ]

main_title = 'egaji'
titles = {}
for name, path, title in routes:
    if title:
        titles[name] = ' - '.join([main_title, title])

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    engine.echo = True
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    init_model()

    session_factory = session_factory_from_settings(settings)
    if 'localization' not in settings:
        settings['localization'] = 'id_ID.UTF-8'
    locale.setlocale(locale.LC_ALL, settings['localization'])        
    if 'timezone' not in settings:
        settings['timezone'] = DefaultTimeZone
    config = Configurator(settings=settings,
                          root_factory='egaji.models.RootFactory',
                          session_factory=session_factory)
    config.include('pyramid_beaker')                          
    config.include('pyramid_chameleon')

    authn_policy = AuthTktAuthenticationPolicy('sosecret',
                    callback=group_finder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()                          
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(get_user, 'user', reify=True)
    config.add_request_method(get_title, 'title', reify=True)
    config.add_request_method(get_months, 'months', reify=True)
    config.add_notfound_view(RemoveSlashNotFoundViewFactory())        
                          
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')
    for name, path, title in routes:
        config.add_route(name, path)
    config.scan()
    return config.make_wsgi_app()
