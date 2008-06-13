import random
import sys
import time

from paste.exceptions.errormiddleware import Supplement

class ResponseLoggingMiddleware:
    def __init__(self, app, max_bodylen, logger):
        self.application = app
        self.max_bodylen = max_bodylen
        self.logger = logger

    def __call__(self, environ, start_response):
        rnd = random.randint(0, sys.maxint-1)

        environ['repoze.debug.id'] = rnd
        environ['repoze.debug.request_begin'] = time.time()

        self.log_request(environ)

        catch_response = []
        body = []

        def replace_start_response(status, headers, exc_info=None):
            catch_response.append([status, headers])
            start_response(status, headers, exc_info)
            return body.append

        app_iter = self.application(environ, replace_start_response)

        try:
            body.extend(app_iter)
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()

        body = ''.join(body)
        if catch_response:
            status, headers = catch_response[0]
        else:
            status = '500 Start Response Not Called'
            headers = []

        self.log_response(environ, status, headers, body)

        return [body]

    def log_request(self, environ):
        supplement = Supplement(self, environ)
        request_data = supplement.extraData()
        request_id = environ['repoze.debug.id']
        out = []
        t = time.ctime()
        out.append('--- REQUEST %s at %s ---' % (request_id, t))
        out.append('URL: %s' % supplement.source_url)
        out.append('CGI Variables')
        items = request_data[('extra', 'CGI Variables')].items()
        items.sort()
        for k, v in items:
            out.append('  %s: %s' % (k, v))
        out.append('WSGI Variables')
        items = request_data[('extra', 'WSGI Variables')].items()
        for k, v in items:
            out.append('  %s: %s' % (k, v))
        out.append('--- end REQUEST %s ---' % request_id)
        self.logger.info('\n'.join(out))

    def log_response(self, environ, status, headers, body):
        supplement = Supplement(self, environ)
        request_data = supplement.extraData()
        request_id = environ.get('repoze.debug.id')
        out = [] 
        t = time.ctime()
        end = time.time()
        start = environ.get('repoze.debug.request_begin')
        if start:
            duration = end - start
        else:
            duration = '??'
        out.append('--- RESPONSE %s at %s (%0.4f seconds) ---' % (
            request_id, t, duration))
        out.append('Status: %s' % status)
        out.append('Response Headers')
        for header in headers:
            out.append('  %s: %s' % (header[0], header[1]))
        out.append('Bodylen: %s' % len(body))
        out.append('Body:')
        out.append('')
        bodyout = body
        if self.max_bodylen:
            bodyout = body[:self.max_bodylen]
            if len(body) > self.max_bodylen:
                bodyout += ' ... (truncated)'
        out.append(bodyout)
        out.append('--- end RESPONSE %s ---' % request_id)
        self.logger.info('\n'.join(out))
        
class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers.  If no suffixes
    # match, default is the multiplier.  Matches are case insensitive.  Return
    # values are in the fundamental unit.
    def __init__(self, d, default=1):
        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d.keys():
            if self._keysz is None:
                self._keysz = len(k)
            else:
                assert self._keysz == len(k)

    def __call__(self, v):
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:
                return int(v[:-self._keysz]) * m
        return int(v) * self._default

byte_size = SuffixMultiplier({'kb': 1024,
                              'mb': 1024*1024,
                              'gb': 1024*1024*1024L,})

def make_middleware(app,
                    global_conf,
                    filename,
                    max_bodylen='0KB', # all
                    max_logsize='100MB',
                    backup_count='10',
                    ):
    """ Paste filter-app converter """
    backup_count = int(backup_count)
    max_bytes = byte_size(max_logsize)
    max_bodylen = byte_size(max_bodylen)

    from logging import Logger
    from logging.handlers import RotatingFileHandler

    handler = RotatingFileHandler(filename, maxBytes=max_logsize,
                                  backupCount=backup_count)
    logger = Logger('repoze.debug.responselogger')
    logger.handlers = [handler]
    return ResponseLoggingMiddleware(app, max_bodylen, logger)