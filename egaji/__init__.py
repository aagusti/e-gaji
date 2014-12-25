import sys
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
    HTTPNotFound
    )

from sqlalchemy import engine_from_config

from .security import group_finder, get_user
from .models import (
    DBSession,
    Base,
    init_model,
    )
from .models.base_model import (
    RouteModel)
    
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
        #routes = request.registry.settings.getRoutes() 
        #print list(routes)
        #return HTTPNotFound()
        request.session.flash('Halaman yang anda cari tidak ditemukan','error')
        
        return request.user and HTTPFound('/app') or HTTPFound('/') #self.notfound_view(context, request)
    
    
# https://groups.google.com/forum/#!topic/pylons-discuss/QIj4G82j04c
def url_has_permission(request, permission):
    print 'P******',permission, request.context, request
    sys.exit()
    return has_permission(permission, request.context, request)

@subscriber(BeforeRender)
def add_global(event):
     event['permission'] = url_has_permission

def get_title(request):
    route_name = request.matched_route.name
    return titles[route_name]

routes = [    
    ('home', '/', 'Home',''), #resource_id
    ('app', '/app', 'Aplikasi',''),
    ('login', '/login', 'Login',''),
    ('logout', '/logout', 'Logout',''),
    ('password', '/password', 'Change password',''),
    
    ('user', '/user', 'Users','egaji.models.AdminFactory'),
    ('user-act', '/user/act/{act}', 'Users','egaji.models.AdminFactory'),
    ('user-add', '/user/add', 'Tambah user','egaji.models.AdminFactory'),
    ('user-edit', '/user/{id}/edit', 'Edit user','egaji.models.AdminFactory'),
    ('user-delete', '/user/{id}/delete', 'Hapus user','egaji.models.AdminFactory'),

    ('change-act', '/change/{act}', 'change',''),
    
    ('group', '/group', 'Groups','egaji.models.AdminFactory'),
    ('group-act', '/group/act/{act}', '','egaji.models.AdminFactory'),
    ('group-add', '/group/add', 'Tambah group','egaji.models.AdminFactory'),
    ('group-edit', '/group/{id}/edit', 'Edit group','egaji.models.AdminFactory'),
    ('group-delete', '/group/{id}/delete', 'Hapus group','egaji.models.AdminFactory'),

    ('urusan', '/urusan', 'urusans','egaji.models.AdminFactory'),
    ('urusan-add', '/urusan/add', 'Tambah urusan','egaji.models.AdminFactory'),
    ('urusan-edit', '/urusan/{id}/edit', 'Edit urusan','egaji.models.AdminFactory'),
    ('urusan-delete', '/urusan/{id}/delete', 'Hapus urusan','egaji.models.AdminFactory'),
    ('urusan-act', '/urusan/act/{act}', 'Action','egaji.models.AdminFactory'),

    ('unit', '/unit', 'units','egaji.models.AdminFactory'),
    ('unit-add', '/unit/add', 'Tambah unit','egaji.models.AdminFactory'),
    ('unit-edit', '/unit/{id}/edit', 'Edit unit','egaji.models.AdminFactory'),
    ('unit-delete', '/unit/{id}/delete', 'Hapus unit','egaji.models.AdminFactory'),
    ('unit-act', '/unit/act/{act}', 'AdminFactory','egaji.models.AdminFactory'),

    ('user-unit', '/user/unit', 'User Unit','egaji.models.AdminFactory'),
    ('user-unit-act', '/user/unit/act/{act}', 'Action','egaji.models.AdminFactory'),
    ('user-unit-add', '/user/unit/add', 'Tambah user unit','egaji.models.AdminFactory'),
    ('user-unit-edit', '/user/unit/{id}/edit', 'Edit user unit','egaji.models.AdminFactory'),
    ('user-unit-delete', '/user/unit/{id}/delete', 'Hapus user unit','egaji.models.AdminFactory'),

    ('user-group', '/user/group', 'User group','egaji.models.AdminFactory'),
    ('user-group-act', '/user/group/act/{act}', 'Action','egaji.models.AdminFactory'),
    ('user-group-add', '/user/group/add', 'Tambah user group','egaji.models.AdminFactory'),
    ('user-group-edit', '/user/group/{id}/edit', 'Edit user group','egaji.models.AdminFactory'),
    ('user-group-delete', '/user/group/{id}/delete', 'Hapus user group','egaji.models.AdminFactory'),

    ('gaji', '/gaji', 'Gaji', 'egaji.models.GajiFactory',),
    ('gaji-act', '/gaji/act/{act}', 'Action','egaji.models.GajiFactory'),
    ('gaji-csv', '/gaji/csv', 'CSV','egaji.models.GajiFactory'),
    
    ('gaji-potongan', '/gaji-potongan', 'Potongan Gaji','egaji.models.GajiFactory'),
    ('gaji-potongan-add', '/gaji-potongan/add', 'Tambah Potongan','egaji.models.GajiFactory'),
    ('gaji-potongan-edit', '/gaji-potongan/{id}/edit', 'Edit Potongan','egaji.models.GajiFactory'),
    ('gaji-potongan-delete', '/gaji-potongan/{id}/delete', 'Hapus Potongan','egaji.models.GajiFactory'),
    ('gaji-potongan-act', '/gaji-potongan/act/{act}', '','egaji.models.GajiFactory'),
    ('gaji-potongan-csv', '/gaji-potongan/csv', 'CSV','egaji.models.GajiFactory'),
    ]

main_title = 'egaji'
titles = {}
#for name, path, title, factory in routes2:
#    if title:
#        titles[name] = ' - '.join([main_title, title])


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    #engine.echo = True
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
    
    config.add_renderer('csv', '.tools.CSVRenderer')
    
    #routes = DBSession.query(RouteModel.kode, RouteModel.path, RouteModel.nama, RouteModel.factory).all()
    """
    for route in routes:
        if route.factory: 
            config.add_route(route.kode, route.path, factory=(route.factory).encode("utf8"))
        else:
            config.add_route(route.kode, route.path)
    """    
    #    if route.nama:
    #        titles[route.kode] = route.nama #' - '.join([main_title, title])
    
    for name, path, title, factory in routes:
        if factory: 
            config.add_route(name, path, factory=factory)
        else:
            config.add_route(name, path)
        if name:
            titles[name] = ' - '.join([path, title])
    print list(title)
    config.scan()
    return config.make_wsgi_app()
