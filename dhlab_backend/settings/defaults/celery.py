'''
    celery.py

    Default Django settings for Celery. See
    http://docs.celeryproject.org/en/latest/getting-started/brokers/redis.html#broker-redis
    for more information.
'''

# Where tasks are stored.
BROKER_URL = 'redis://localhost:6379/0'

# Stores the state and return values of tasks.
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


# Visibility timeout.
# Then number of seconds to wait for the worker to acknowledge the task
# before the message is redelivered to another worker.
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
