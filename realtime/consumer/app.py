import os
import faust

os.environ.setdefault('FAUST_LOOP', 'gevent')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtime.settings.base')

app = faust.App('tapad', autodiscover=True, origin='consumer')


@app.on_configured.connect
def configure_from_settings(app, conf, **kwargs):
    from django.conf import settings
    conf.broker = settings.FAUST_BROKER_URL
    conf.store = settings.FAUST_STORE_URL


if __name__ == '__main__':
    app.main()
