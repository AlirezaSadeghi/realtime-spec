from unittest.mock import patch

from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse

from realtime.helpers import ProducerHelper


class AnalyticsViewTestCase(TestCase):

    def setUp(self):
        self.timestamp = '1543837516'
        self.url = reverse('analytics')
        self.params = {'action': 'click', 'timestamp': self.timestamp, 'user': 'test'}

    def test_should_return_400_for_missing_post_data(self):
        for key in self.params.keys():
            params = dict(self.params)
            params.pop(key)
            response = self.client.post('%s?%s' % (self.url, urlencode(params)))
            self.assertEqual(response.status_code, 400)

    def test_should_work_for_complete_post_data(self):
        params = {'user': 'test', 'action': 'impression', 'timestamp': self.timestamp}
        response = self.client.post('%s?%s' % (self.url, urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_should_fail_for_wrong_timestamp(self):
        params = dict(self.params)
        params['timestamp'] = self.timestamp * 4
        response = self.client.post('%s?%s' % (self.url, urlencode(params)))
        self.assertEqual(response.status_code, 400)

    @patch.object(ProducerHelper, 'get_instance')
    def test_should_write_incoming_post_data_to_kafka(self, mocked_producer):
        """
        In a successful scenario, the received data should be passed over to Apache Kafka
        Also producer should be flushed to make sure the data is sent.
        For this simpel scenario we register no success/failure callbacks.
        :param mocked_producer:
        :return:
        """
        response = self.client.post('%s?%s' % (self.url, urlencode(self.params)))
        self.assertEqual(response.status_code, 200)

        send_called = False
        flush_called = False
        for call in mocked_producer.mock_calls:
            if call[0] == '().send':
                send_called = True
                self.assertTupleEqual(call[1], ('interactions', self.params))
            if call[0] == '().flush':
                flush_called = True

        self.assertTrue(send_called)
        self.assertTrue(flush_called)
