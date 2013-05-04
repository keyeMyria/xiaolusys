# Django settings for shopmanager project.

import os.path
import posixpath

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('meixqhi', 'xiuqing.mei@huyi.so'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'shopmgr',                      # Or path to database file if using sqlite3.
        'USER': 'shopmgr',                      # Not used with sqlite3.
        'PASSWORD': '123123',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


TIME_ZONE = 'Asia/Shanghai'

#DATETIME_INPUT_FORMATS = '%Y-%m-%d %H:%M:%S'
#DATE_INPUT_FORMATS = '%Y-%m-%d'
DATETIME_FORMAT    = 'Y-m-d H:i:s'
DATE_FORMAT        = 'Y-m-d'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

#USE_L10N = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")

MEDIA_URL = "/media/"

#STATIC_ROOT = os.path.join(PROJECT_ROOT,"static")

STATIC_URL = '/static/'

DOWNLOAD_ROOT   = os.path.join(PROJECT_ROOT,"site_media",'download')

ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

STATIC_DOC_ROOT = os.path.join(PROJECT_ROOT,"site_media","static")

STATICFILES_DIRS = (
       #os.path.join(PROJECT_ROOT,"site_media","static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'zze(^rvhdz(hxx16a788w6jyqhtq%*v_pl^2#t1dskpb!473f8'


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'raven.contrib.django.middleware.SentryResponseErrorIdMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'shopmanager.urls'

TEMPLATE_DIRS = (
       os.path.join(PROJECT_ROOT, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    #'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'chartit',
    'south',
    'gunicorn',
    'raven.contrib.django',
    'djangorestframework',
    'djcelery',
    'djkombu',
    'deamon',
    'deamon.celery_sentry',

    'shopback.amounts',
    'shopback.categorys',
    'shopback.fenxiao',
    'shopback.items',
    'shopback.logistics',
    'shopback.monitor',
    'shopback.orders',
    'shopback.trades',
    'shopback.refunds',
    'shopback.users',
    'shopback.archives',
    'shopback.purchases',
    
    'shopapp.autolist',
    'shopapp.collector',
    'shopapp.memorule',
    'shopapp.report',
    'shopapp.syncnum',
    'shopapp.asynctask',
    'shopapp.notify',
    'shopapp.modifyfee',
    'shopapp.calendar',
    'shopapp.babylist',
    #'test.celery',
)



APPKEY = '12517640'
APPSECRET = 'e50beebdf9226e3fc991834375e32b5a'


AUTH_PROFILE_MODULE = 'users.user'

AUTHENTICATION_BACKENDS = (
    'auth.accounts.backends.TaoBaoBackend',
    'django.contrib.auth.backends.ModelBackend')

LOGIN_REDIRECT_URL = '/home/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'


TAOBAO_PAGE_SIZE = 100              #the page_size of  per request

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'DEBUG',
            'class': 'raven.contrib.django.handlers.SentryHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'autolist.handler': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'syncnum.handler': {
            'handlers': ['sentry','mail_admins'],
            'level': 'WARN',
            'propagate': True,
        },
        'sentry.errors': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'taobao.auth': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'auth.apis': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'permission': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'exception.middleware': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'pagerank.handler': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'traderank.handler': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'report.handler': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'taobao.urlcraw': {
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'orders.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'token.refresh':{
            'handlers': ['sentry','mail_admins'],
            'level': 'WARN',
            'propagate': True,
        },
        'recurupdate.categorey':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'refunds.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'fenxiao.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'categoreys.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'memorule.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'items.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'logistics.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'trades.handler':{
            'handlers': ['sentry','mail_admins'],
            'level': 'WARN',
            'propagate': True,
        },
        'asynctask.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'tradepost.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'notifyserver.handler':{
            'handlers': ['sentry','console'],
            'level': 'WARN',
            'propagate': True,
        },
        'notify.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'user.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'modifyfee.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
        'logaction.handler':{
            'handlers': ['sentry'],
            'level': 'WARN',
            'propagate': True,
        },
    }
}


try:
    from local_settings import *
except Exception,exc:
    pass


try:
    from task_settings import *
except Exception,exc:
    pass

