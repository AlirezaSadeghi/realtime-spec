from django.views.generic import View
from django.http import HttpResponse


class AnalyticsView(View):

    def post(self, request):
        return HttpResponse("Done")

    def get(self, request):
        return HttpResponse("Done")
