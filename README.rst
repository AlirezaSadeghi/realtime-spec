Hey,

So here, I'm gonna talk about how to run this project and well how to actually the tests.

The project actually so far has taken about an hour at most of me, and I'm gonna try to put in another 2, 3 hours.

Hopefully can spin up something working pretty bare-bone.

**Architecture**

So basically, it's a Django project, with the following directory structure.

realtime
    - api
        Simple django application, handling the REST endpoints (well which as defined by the docs doesn't seem so REST-y to me anyways).
        There's a class called `AnalyticsView` inside the file `views.py`, which is responsible for handling incoming http(s) traffic.

        Since we are trying to build an application and have no idea how much, in terms of traffic, it's gonna grow,
        the endpoint for handling `POST` requests, just gets the data and pushes them into a `Kafka Topic`.

        We later on process this data, as fast as we can, by spinning up consumers in the `consumer` application.
    - consumer
        So, as discussed above, this application is in charge of defining stream processors on the `Kafka Topic`.
        We process all the load and try to aggregate statistics and then store all data into a `MongoDB` backend.
    - settings
        Project wide settings, for now only there's base, if we want a good deployment, there should be dev & production settings as well.
        (I'm unfortunately not sure right now If I'm gonna get to the part I think about deployment).
        Pretty much standard Django Configurations are defined here.

requirements
    Required packages to run the project, divided into base requirements and test requirements.

**Libraries and Tools**
    - Python >= 3.6
    - Django >= 2.1
    - Faust
    - Redis
    - Pymongo >= 3.7

We use ``Django 2.1`` to create the HTTP(S) server and the API endpoints, we also stick to a Django-`ish` project layout.
We also use ``Faust``, it's basically a Kafka Stream Processing library written in Python, since it uses the newly introduced
syntax of async/await, we need at least a ``Python 3.6.0`` installation.

**Running the Project**

To make things easier, I've written a `setup.py` script that does its best making things easier, so
after ``python setup.py install`` the ``tapad`` command, as well as the ``consumer`` command will be available::

        $ python setup.py develop
        $ tapad runserver # Runs HTTP Server
        $ consumer worker -l info # Runs Kafka Stream Processor

    It's the same as running ``python manage.py runserver``, but it will
    be installed in your system path and well it's easier.


In order for the project ot fully run, you need to have
    - Apache Kafka (and well zookeeper) running on localhost:9092
    - Redis running on localhost:6379
    - MongoDB running on localhost:27017

for the addresses, the defaults are brought above, but you can change them through env-vars.
Unfortunately I couldn't find enough time to wrap all dependent services into a docker image, and that's for the future.

**Scalability**

The project should be reasonably scalable.

You can spawn more Faust workers to increase throughput of message processing.
We can have an Nginx instance reverse-proxy-ing requests into different django instances running on different ports.

**Test**
To run tests, just run ``python manage.py test`` on the root of the project, for now, code coverage is too low anyways.
