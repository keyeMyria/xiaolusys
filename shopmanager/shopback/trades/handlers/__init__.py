#-*- coding:utf8 -*-
from django.conf import settings
from .handler import BaseHandler
from .logistic import LogisticsHandler

class NotBaseHandlerError(Exception):
    pass

class AlreadyRegistered(Exception):
    pass

class TradeHandler(objects):
    
    def __init__(self, name='handlers', app_name='trades'):
        
        self._handlers = [] #collect all need effect handlers
        
        
    def register(self,handler_class):
        
        if not handler or not issubclass(handler_class,BaseHandler):
            raise NotBaseHandlerError('Need Trade BaseHandler subclass.')
        
        handler = handler_class()
        
        for registed_handler in self._handlers:
            if type(handler) == type(registed_handler):
                raise AlreadyRegistered(u'%s is already regiest.'%unicode(type(handler)))
            
        self._handlers.append(handler)
        
    def proccess(self,merge_trade,*args,**kwargs):
        
        for registed_handler in self._handlers:
            if registed_handler.handleable(merge_trade,*args,**kwargs):
                registed_handler.process(merge_trade,*args,**kwargs)
        
def getTradeHandler(config_handlers_path=[]):
    
    trade_handler =  TradeHandler()
    config_handlers_path = config_handlers_path or getattr(settings,'CONFIG_TRADE_HANDLERS_PATH',[])
    for handler_path in config_handlers_path:
        try:
            hl_module, hl_classname = handler_path.rsplit('.', 1)
        except ValueError:
            raise exceptions.ImproperlyConfigured('%s isn\'t a middleware module' % handler_path)
        try:
            mod = import_module(hl_module)
        except ImportError, e:
            raise exceptions.ImproperlyConfigured('Error importing middleware %s: "%s"' % (hl_module, e))
        try:
            hl_class = getattr(mod, hl_classname)
        except AttributeError:
            raise exceptions.ImproperlyConfigured('Middleware module "%s" does not define a "%s" class' % (mw_module, mw_classname))
        
        trade_handler.register(hl_class)
        
    return trade_handler

trade_handler = getTradeHandler()
    