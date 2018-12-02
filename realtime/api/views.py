from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from realtime.api.producer import ProducerService


class AnalyticsView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        super(AnalyticsView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """
            This function basically fetches data from the GET dictionary of the request object
            passed in, it then gets the already established Kafka Connection
            (If there exists any, get_instance creates one)
            and then writes to the topic the incoming data.
            The data is later processed in our consumer worker.

        :param request: The http POSt request object, contains the data in it's GET dict
        :return: An empty HttpResponse with status 200
        """
        action = request.GET.get('action')
        username = request.GET.get('user')
        timestamp = request.GET.get('timestamp')

        producer = ProducerService.get_instance()
        producer.send(settings.INTERACTION_TOPIC, {
            'timestamp': timestamp,
            'username': username,
            'action': action
        })
        producer.flush()

        return HttpResponse()

    def get(self, request):
        """

        :param request:  The http GET request object
        :return: don't know yet
        """
        timestamp = request.GET.get('timestamp')
        return HttpResponse()
