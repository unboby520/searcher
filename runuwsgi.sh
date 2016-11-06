#!/bin/bash

# Author: Ilcwd
#
# uWSGI 运行脚本
# ==============
# 初次使用请修改下面变量：
#   * SERVICE_NAME - 服务名字，后面的相关路径，用户名都已这个为基础，建议为纯小写字母
#   * UWSGI_EXEC - uWSGI 程序路径
#   * UWSGI_WORKERS - 程序运行进程数
#
# 并创建对应的 virtualenv，建议python2.7
#    mkvirtualenv ${SERVICE_NAME} --python=${YOUR_PYTHON_BIN}
#
# 如果程序不能启动程序，可以检查下面情况
#   * RUN_PATH 是否有写权限
#   * UWSGI_EXEC 是否存在
#   * VIRTUAL_ENV_PATH 是否已经创建好
#   * 如果上述条件都满足，可以查看 UWSGI_PROC_LOG 的错误信息解决。
#
#


# Parameters you may need to change..
SERVICE_NAME="examplesvr"
UWSGI_EXEC="uwsgi1"
UWSGI_WORKERS="3"

# Environment
PROCESS_USER="$SERVICE_NAME"
PROCESS_GROUP="$SERVICE_NAME"
APP_PATH="/data/apps/${SERVICE_NAME}"
LOG_PATH="/data/logs/${SERVICE_NAME}"
RUN_PATH="/data/apps/run"
VIRTUAL_ENV_PATH="/data/envs/${SERVICE_NAME}"

# 防止手贱没改服务名的人。
if [ "${SERVICE_NAME}" = "examplesvr" ]; then
   echo 'You MUST change variable `$SERVICE_NAME` in this script first !!'
   exit 1
fi

declare -x PYTHON_EGG_CACHE="${APP_PATH}/.python-eggs"

# Check if root
# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Check if user exists
if ! id -u ${PROCESS_USER} > /dev/null 2>&1; then
    echo "Create User" ${PROCESS_USER}
    /usr/sbin/useradd ${PROCESS_USER}  -M -s /bin/false && /usr/sbin/usermod -L ${PROCESS_USER}
fi

# Check if all path need exists.
if [ ! -s ${UWSGI_EXEC} ]; then
    echo "uWSGI path does not exist: ${UWSGI_EXEC}"
    exit 1
fi

if [ ! -d ${VIRTUAL_ENV_PATH} ]; then
    echo "Virtualenv path does not exist: ${VIRTUAL_ENV_PATH}"
    echo "You can run command 'mkvirtualenv --python=/usr/local/python-2.7.8/bin/python ${SERVICE_NAME}' to create new env."
    exit 1
fi

if [ ! -d ${LOG_PATH} ]; then
    mkdir ${LOG_PATH}
fi

if [ ! -d ${PYTHON_EGG_CACHE} ]; then
    mkdir ${PYTHON_EGG_CACHE}
    chmod -R a+r ${PYTHON_EGG_CACHE}
fi


if [ ! -d ${RUN_PATH} ]; then
    mkdir ${RUN_PATH}
    chmod -R a+rw ${RUN_PATH}
    chmod +t ${RUN_PATH}
    
fi

# Change folder's owner
if [ "$(stat -c %U ${APP_PATH})" != "${PROCESS_USER}" ]; then
   echo "Change owner of ${APP_PATH}"
   chown ${PROCESS_USER}.${PROCESS_GROUP} ${APP_PATH}
fi

## 
## 
# if [ "$(stat -c %U ${LOG_PATH})" != "${PROCESS_USER}" ]; then
#   echo "Change owner of ${LOG_PATH}"
#   chown ${PROCESS_USER}.${PROCESS_GROUP} ${LOG_PATH}
# fi
chown -R ${PROCESS_USER}.${PROCESS_GROUP} ${LOG_PATH}


# uWSGI parameters
UWSGI_SOCKET="${RUN_PATH}/uwsgi_${SERVICE_NAME}.sock"
UWSGI_STATS_SOCKET="${RUN_PATH}/uwsgi_${SERVICE_NAME}_stats.sock"
UWSGI_WORKER_MAXREQ="100000"

PYTHON_PATH="${APP_PATH}/current"
PY_ENTRY="${PYTHON_PATH}/wsgiapp.py"

UWSGI_PIDFILE="${RUN_PATH}/uwsgi_${SERVICE_NAME}.pid"
UWSGI_PROC_LOG="${LOG_PATH}/uwsgi_${SERVICE_NAME}.log"
UWSGI_TOUCH_RELOAD="${RUN_PATH}/uwsgi_${SERVICE_NAME}.reload"


if [ ! -e ${UWSGI_TOUCH_RELOAD} ]; then
    touch ${UWSGI_TOUCH_RELOAD}
    echo "Touch ${UWSGI_TOUCH_RELOAD}"
    chown ${PROCESS_USER}.${PROCESS_GROUP} ${UWSGI_TOUCH_RELOAD}
fi

# bash can not deal with float numbers.
WAITING_INTERVAL=1
FORCE_STOP_THRESHOLD=10


# Consts
RED='\e[1;91m'
GREN='\e[1;92m'
WITE='\e[1;97m'
NC='\e[0m'

# Global vailables
PROC_COUNT="0"
function count_proc()
{
    PROC_COUNT=$(ps -ef | grep ${UWSGI_EXEC} | grep ${UWSGI_SOCKET} | grep -vc grep)
}

function list_proc()
{
    ps -ef | grep -v grep | grep ${UWSGI_SOCKET} | grep --color ${UWSGI_EXEC} 
}

function force_stop()
{
    ps aux|grep -v grep| grep ${UWSGI_EXEC}|grep ${UWSGI_SOCKET} |grep ${SERVICE_NAME}|awk '{print $2}'|xargs kill -9
}

function start_uwsgi()
{
    printf "Starting uwsgi"
    count_proc
    if [ ${PROC_COUNT} \> 0 ]; then
        list_proc
        echo -e ${RED}"\n[ERROR]" ${NC}"Start uwsgi failed, processes already runing."
        exit -1
    fi
    
    ${UWSGI_EXEC} \
        --socket ${UWSGI_SOCKET} \
        -H ${VIRTUAL_ENV_PATH} \
        --master \
        --workers ${UWSGI_WORKERS} \
        --max-requests ${UWSGI_WORKER_MAXREQ} \
        --wsgi-file ${PY_ENTRY} \
        --python-path ${PYTHON_PATH} \
        --pidfile ${UWSGI_PIDFILE} \
        --uid ${PROCESS_USER} \
        --gid ${PROCESS_GROUP} \
        --daemonize ${UWSGI_PROC_LOG} \
        --enable-threads \
        --harakiri 360 \
        -l 2048 \
        -b 8096 \
        --harakiri-verbose \
        --disable-logging \
        --touch-reload ${UWSGI_TOUCH_RELOAD} \
        --vacuum \
        --logdate \
        --stats ${UWSGI_STATS_SOCKET} \
        --lazy
        
    
    count_proc
    START_WAITED=0
    while [ ${PROC_COUNT} -eq 0 ]; do
        if [ ${START_WAITED} -gt ${FORCE_STOP_THRESHOLD} ]; then
            echo -e ${RED}"\n[ERROR]" ${NC}"can not start uwsgi, error is:"
            force_stop
            
            tail -n5 ${UWSGI_PROC_LOG}
            exit 1
        fi            
        printf "."
        sleep ${WAITING_INTERVAL}
        count_proc
        let START_WAITED=${START_WAITED}+${WAITING_INTERVAL}
    done
    

    echo -e ${GREN}"\n[OK]" ${NC}"uwsgi start succesfully."
}

function reload_uwsgi()
{
    printf "Reloading uwsgi"
    if [ ! -s ${UWSGI_PIDFILE} ]; then
        echo -e ${RED}"\n[ERROR]" ${NC}"uwsgi pidfile not found:"${UWSGI_PIDFILE}
        exit -1
    fi
    count_proc
    if [ ${PROC_COUNT} -eq 0 ]; then
        echo -e ${RED}"\n[ERROR]" ${NC}"uwsgi process not found."
        exit -1
    fi
    
    # SIGHUP:  reload (gracefully) all the workers and the master process
    # SIGTERM: brutally reload all the workers and the master process
    kill -SIGHUP $(cat ${UWSGI_PIDFILE})
    if [ ${?} -eq 0 ]; then
        echo -e ${GREN}"\n[OK]" ${NC}"uwsgi reload signal is sent."
    else
        echo -e ${RED}"\n[ERROR]" ${NC}"uwsgi reload signal sent failed."
    fi
}

function stop_uwsgi()
{
    printf "Stoping uwsgi"
    if [ ! -s ${UWSGI_PIDFILE} ]; then
        echo -e ${RED}"\n[ERROR]" ${NC}"uwsgi pidfile not found:"${UWSGI_PIDFILE}
        exit -1
    fi
    count_proc
    if [ ${PROC_COUNT} -eq 0 ]; then
        echo -e ${RED}"\n[ERROR]" ${NC}"uwsgi process not found."
        exit -1
    fi
    
    kill -SIGINT $(cat ${UWSGI_PIDFILE})
    count_proc
    WAITED=0
    while [ ${PROC_COUNT} -ne 0 ]; do
        if [ ${WAITED} -gt ${FORCE_STOP_THRESHOLD} ]; then
            echo -e ${RED}"\n[ERROR]" ${NC}"force to stop uwsgi."
            force_stop
        fi            
        printf "."
        sleep ${WAITING_INTERVAL}
        count_proc
        let WAITED=${WAITED}+${WAITING_INTERVAL}
    done
    echo -e ${GREN}"\n[OK]" ${NC}"uwsgi stop succesfully."
}


MODE=${1}
case ${MODE} in
    "start")
        start_uwsgi
        ;;

    "stop")
        stop_uwsgi
        ;;

    "restart")
        stop_uwsgi
        start_uwsgi
        ;;

    "reload")
        reload_uwsgi
        ;;
    
    *)
        # usage
        echo -e "\nUsage: $0 {start|stop|restart|reload}"
        echo -e ${WITE}" start   "${NC}"Start uwsgi processes."
        echo -e ${WITE}" stop    "${NC}"Stop all uwsgi processes."
        echo -e ${WITE}" restart "${NC}"Stop all uwsgi processes and start again."
        echo -e ${WITE}" reload  "${NC}"Reload all uwsgi processes gracefully."
        exit 1
        ;;
esac
