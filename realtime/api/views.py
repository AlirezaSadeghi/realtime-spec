from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.http import HttpResponse


class AnalyticsView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        super(AnalyticsView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        timestamp = request.GET.get('timestamp')
        username = request.GET.get('user')
        action = request.GET.get('action')
        return HttpResponse()

    def get(self, request):
        timestamp = request.GET.get('timestamp')
        return HttpResponse()
