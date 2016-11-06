# coding: utf8        args = flask.request.json
#
# searcher - constants
# 
# Author: ilcwd 
# Create: 14/11/26
#

HTTP_STATUS_LINE_OK = '200 OK'
HTTP_STATUS_LINE_ERROR = '200 ERROR'

CODE_OK = 'ok'
CODE_BAD_PARAMS = 'client bad params'
CODE_NO_UID = 'header error:no User-Id'
CODE_DB_ERR = 'db op failed'
CODE_DATA_ERROR = 'data error'
CODE_FOLLOW_ERROR = 'follow error'
CODE_CANCEL_ERROR = 'cancel error'
CODE_HAVE_FOLLOW = 'have follow'

QINIU_PIC_URI = 'http://7xnvqo.com1.z0.glb.clouddn.com/'

REDIS_SM_ID_INFO = 'xsl_sm_id_info_hash'
