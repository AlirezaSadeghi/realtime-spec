import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from realtime.api.validators import PostValidator, GetValidator
from realtime.helpers import ProducerHelper, UtilityHelper, RedisHelper, MongoDBHelper


class AnalyticsView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AnalyticsView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """
            This function basically fetches data from the GET dictionary of the request object
            passed in, it then gets the already established Kafka Connection
            (If there exists any, get_instance creates one)
            and then writes to the topic the incoming data.
            The data is later processed in our consumer worker.

            We retry 5 times, and for this sample test, assume that it's successful anyways, so we refrain from
            attaching success/failure callbacks on send.

        :param request: The http POSt request object, contains the data in it's GET dict
        :return: An empty HttpResponse with status 200
        """
        validator = PostValidator(request.GET)
        if not validator.is_valid():
            return HttpResponseBadRequest(validator.errors)

        action = request.GET.get('action')
        username = request.GET.get('user')
        timestamp = request.GET.get('timestamp')

        producer = ProducerHelper.get_instance()
        producer.send(settings.INTERACTION_TOPIC, {
            'timestamp': timestamp,
            'user': username,
            'action': action
        })
        producer.flush()

        return HttpResponse('')

    def get(self, request):
        """
            Returns the data for the requests timestamp

        :param request:  The http GET request object
        :return: don't know yet
        """
        validator = GetValidator(request.GET)
        if not validator.is_valid():
            return HttpResponseBadRequest(validator.errors)

        timestamp = request.GET.get('timestamp')

        dt = UtilityHelper.ts_to_dt(timestamp)
        ts_suffix = UtilityHelper.dt_to_str(dt, UtilityHelper.STD_FORMAT)

        response = RedisHelper.get_data(ts_suffix)
        if len(response) == 2:
            response.update({
                'unique_users': MongoDBHelper.aggregate_elements(ts_suffix, 'user')
            })
        elif len(response) < 2:
            response = MongoDBHelper.aggregate_elements(ts_suffix)

        return HttpResponse('%s' % json.dumps(response, indent=4))
