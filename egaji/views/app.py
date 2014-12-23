from datetime import datetime
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    )
from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    )
import transaction
import colander
from deform import (
    Form,
    ValidationFailure,
    widget,
    )
from ..models import (
    DBSession,
    User,
    )


########
# Home #
########
@view_config(route_name='app', renderer='templates/home-app.pt', permission='view')
def view_app(request):
    return dict(project='egaji')
