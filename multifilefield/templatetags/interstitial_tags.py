from django.template import Library
from django.conf import settings

from interstitial.models import Interstitial


register = Library()


@register.inclusion_tag('interstitial.html')
def get_interstitial(request):
    """ This adds session variables for checking if the interstitial has been viewed."""

    if not getattr(settings, 'INTERSTITIAL_ON', True):
        # interstitial is off
        return {}


    interstitial = Interstitial.objects.get_for_user(request.user)

    print 'interstitial', interstitial, type(interstitial)

    if not interstitial:
        # nothing to display
        return {}


    if getattr(settings, 'INTERSTITIAL_FORCE', True):
        # always show interstitial
        return {'interstitial': interstitial, 'close': True}
    elif request.session.get('interstitial_viewed', False):
        # active and has been viewed in this session
        return {}
    else:
        # active and hasn't been viewed in this session        
        request.session['interstitial_viewed'] = True
        return {'interstitial': interstitial, 'close': True}