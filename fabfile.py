# coding: utf8
"""
Author: Ilcwd
"""
import datetime
import os

# noinspection PyPackageRequirements
from fabric.api import put, cd, sudo, local, lcd, env
# noinspection PyPackageRequirements
from fabric.decorators import task, hosts
# noinspection PyPackageRequirements
from fabric.contrib import files


# server name
PROJECT_NAME = 'searcher'
# git repository
GIT_REPO = "https://github.com/ilcwd/%s.git" % PROJECT_NAME
# configs needs to be replaced
REPLACE_CONFIGS = [
    'deployment/config.json',
    'deployment/logging.yaml',
    # add more if you need
]
DEPLOYMENT_CONFIGS = [
    ('./deployment/nginx.location', '/usr/local/nginx/conf/vhost/searcher.location'),
    ('./deployment/logrotate.conf', '/etc/logrotate.d/searcher.logrotate.conf'),
    # add more
]


# deploy hosts
@task
def dev():
    env.hosts = [
        '10.0.3.184',
    ]


@task
def production():
    env.hosts = [
        '10.0.2.1',
        '10.0.2.2',
        '10.0.2.3',
    ]


@task
def pre():
    env.hosts = [
        '10.0.2.4',
    ]



# deploy user
env.user = 'chenwenda'


# some useful variables
LOCAL_CWD = os.getcwd()
LOCAL_TEMP = os.path.join(LOCAL_CWD, 'build')
TAR_NAME = "%s.%s.tar" % (PROJECT_NAME, datetime.datetime.now().strftime("%Y%m%d"),)
TAR_PATTERN = "%s*.tar" % (PROJECT_NAME,)
LOCAL_TAR_PATH = os.path.join(LOCAL_TEMP, TAR_NAME)
REMOTE_TOUCH_RELOAD = '/data/apps/run/uwsgi_%s.reload' % PROJECT_NAME
REMOTE_PROJECT_PATH = os.path.join('/data/apps/', PROJECT_NAME)
REMOTE_APP_CURRENT_PATH = os.path.join(REMOTE_PROJECT_PATH, 'current')
REMOTE_APP_REAL_FOLDER = '%s.%s' % (PROJECT_NAME, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
REMOTE_APP_REAL_PATH = os.path.join(REMOTE_PROJECT_PATH, REMOTE_APP_REAL_FOLDER)
REMOTE_TAR_PATH = os.path.join(REMOTE_PROJECT_PATH, TAR_NAME)
REMOTE_RUN_SCRIPT_NAME = 'runuwsgi.sh'
REMOTE_RUN_SCRIPT_PATH = os.path.join(REMOTE_PROJECT_PATH, REMOTE_RUN_SCRIPT_NAME)


# some useful functions
def runuwsgi(cmd, warn_only=False):
    with cd(REMOTE_PROJECT_PATH):
        sudo("./%s %s" % (REMOTE_RUN_SCRIPT_NAME, cmd), warn_only=warn_only)


def debug(*a):
    now = datetime.datetime.now()
    print now, ' '.join(str(i) for i in a)


def upload(local, remote):
    return put(local, remote, use_sudo=True, mirror_local_mode=True)


################################
# Tasks
################################
@hosts('0.0.0.0')
@task
def build():
    _TEMP_FOLDER = LOCAL_TEMP

    local("mkdir -p %s" % _TEMP_FOLDER)

    with lcd(_TEMP_FOLDER):
        local("rm -f %s" % (TAR_NAME,))
        local("rm -fr %s" % (PROJECT_NAME,))

        local("git clone %s %s" % (GIT_REPO, PROJECT_NAME))
        local("rm -fr %s/.git" % (PROJECT_NAME, ))
        local("tar -czvf %s %s" % (TAR_NAME, PROJECT_NAME))


@task
def init():

    for l, r in DEPLOYMENT_CONFIGS:
        upload(l, r)
        
    sudo('mkdir -p %s' % (REMOTE_PROJECT_PATH,))


@task
def uwsgi(cmd, warn_only=0):
    runuwsgi(cmd, bool(int(warn_only)))


@task
def deploy():
    first_deploy = False

    # 1. initialize environment
    local('mkdir -p %s' % (LOCAL_TEMP,))
    local("rm -f %s" % (LOCAL_TAR_PATH,))
    local("tar --exclude=*.tar --exclude=.* --exclude=build --exclude=*.pyc -czvf  %s *" % (LOCAL_TAR_PATH, ))

    # 2. upload and extract source code
    sudo("mkdir -p %s" % REMOTE_APP_REAL_PATH)
    put(LOCAL_TAR_PATH, REMOTE_TAR_PATH, use_sudo=True, mirror_local_mode=True)
    with cd(REMOTE_PROJECT_PATH):
        sudo('mv %s %s' % (TAR_NAME, REMOTE_APP_REAL_PATH))

    with cd(REMOTE_APP_REAL_PATH):
        sudo('tar -xf %s' % TAR_NAME)
        sudo('rm -f %s' % TAR_NAME)

    # 3. if old code exists, try to replace configs
    if files.exists(REMOTE_APP_CURRENT_PATH, use_sudo=True):
        # runuwsgi('stop', warn_only=True)

        # replace configs
        with cd(REMOTE_PROJECT_PATH):
            for c in REPLACE_CONFIGS:
                sudo('rm -f %s/%s' % (REMOTE_APP_REAL_FOLDER, c))
                sudo('cp %s/%s  %s/%s' % (REMOTE_APP_CURRENT_PATH, c, REMOTE_APP_REAL_FOLDER, c))

        sudo('rm -f %s' % REMOTE_APP_CURRENT_PATH)
    else:
        first_deploy = True
        debug("[INFO]Remote folder(%s) does not exist." % (REMOTE_APP_CURRENT_PATH,))

    # 4. if `runuwsgi.sh` does not exist, copy from source code.
    if not files.exists(REMOTE_RUN_SCRIPT_PATH, use_sudo=True):
        with cd(REMOTE_PROJECT_PATH):
            sudo('cp %s/%s %s' % (REMOTE_APP_REAL_FOLDER, REMOTE_RUN_SCRIPT_NAME, REMOTE_RUN_SCRIPT_PATH))
            sudo('chmod +x %s' % (REMOTE_RUN_SCRIPT_PATH,))
        debug("[INFO]File `%s` does not exist, copy it from newly-upload code, "
              "you may need to modify it" %
              (REMOTE_RUN_SCRIPT_PATH,))

    # 5. make `current` soft link.
    sudo('ln -s %s %s' % (REMOTE_APP_REAL_PATH, REMOTE_APP_CURRENT_PATH))

    # 6. start/reload service
    if first_deploy:
        runuwsgi('start')
    else:
        sudo('touch %s' % REMOTE_TOUCH_RELOAD)







