# coding: utf8
#
# searcher - errorcode
# 
# Author: ilcwd 
# Create: 15/2/9
#


##
# set service code to differ from errors from other services
##
_SERVICE_CODE = 1000

assert _SERVICE_CODE != 0, "Change `_SERVICE_CODE` to make errors different from other services."

def _make_error_code(code):
    return _SERVICE_CODE * 10000 + code




# OK is global zero.
OK = 0

# base error,
SERVER_ERROR = _make_error_code(0)