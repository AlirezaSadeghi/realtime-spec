This is an offline interview challenge for Tapad Norway AS. 

There are two different problems to choose one from, and I found the *realtime spec* more interesting personally. 

So here's a *fairly scalable system* implemention, written in about ~14 hours.

ToC:

1. Problem definition
2. Solution & project setup
3. How to run the project
4. Scalability discussion
5. Running the tests

Feel free to contact me: alirezasadeghi71@gmail.com!

**1. Problem Definition**

A server accepts the following HTTP requests:

* ```POST /analytics?timestamp={millis_since_epoch}&user={username}&{click|impression}```
* ```GET /analytics?timestamp={millis_since_epoch}```

When the `POST` request is made, nothing is returned to the client. We simply side-effect and add the details from the request to our tracking data store.

When the `GET` request is made, we return the following information in plain-text to the client, for the hour of the requested timestamp:

* unique_users,{number_of_unique_usernames}
* clicks,{number_of_clicks}
* impressions,{number_of_impressions}


The server will receive many more `GET` requests (95%) for the **current hour** than for hours in the past (5%).

Most `POST` requests received by the server will contain a timestamp that matches the current timestamp (95%). However, it is possible for the timestamp in a `POST` request to contain a *historic* timestamp (5%) -- e.g. it is currently the eighth hour of the day, yet the request contains a timestamp for hour six of the day.

Additional servers should be able to be spun up, at any time, without effecting the correctness of our metrics.

The `POST` and `GET` endpoints should be optimized for high throughput and low latency.

**2. Solution and project setup**

As obvious, It's a Django project, with the following directory/packaging structure.

realtime
    - api
        Server application, handling the REST endpoints (well which as defined by the docs doesn't seem so REST-y to me anyways).
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


    - Python >= 3.6
    - Django >= 2.1
    - Faust
    - Redis
    - Pymongo >= 3.7

We use ``Django 2.1`` to create the HTTP(S) server and the API endpoints, we also stick to a Django-`ish` project layout.
We also use ``Faust``, it's basically a Kafka Stream Processing library written in Python, since it uses the newly introduced
syntax of async/await, we need at least a ``Python 3.6.0`` installation.

**3. Running the Project**

To make things easier, I've written a `setup.py` script that does its best making things easier, so
after ``python setup.py install`` the ``tapad`` command, as well as the ``consumer`` command will be available::

        $ python setup.py develop
        $ tapad runserver # Runs HTTP Server
        $ consumer worker -l info # Runs Kafka Stream Processor

It's the same as running \
``python manage.py runserver``, \
but it will be installed in your system path and well it's easier.


In order for the project ot fully run, you need to have
    - Apache Kafka (and well zookeeper) running on localhost:9092
    - Redis running on localhost:6379
    - MongoDB running on localhost:27017

for the addresses, the defaults are brought above, but you can change them through env-vars.
Unfortunately I couldn't find enough time to wrap all dependent services into a docker image, and that's for the future.

**4. Scalability discussion**

The project should be reasonably scalable.

You can spawn more Faust workers to increase throughput of message processing.
We can have an Nginx instance reverse-proxy-ing requests into different django instances running on different ports.

**5. Running the tests**

To run tests, just run ``python manage.py test`` on the root of the project, for now, code coverage is too low anyways.

