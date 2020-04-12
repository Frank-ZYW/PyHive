import django
import os
from os.path import join, exists, abspath
from os import makedirs, getcwd
from jinja2 import Environment, PackageLoader, select_autoescape

from pyhive.settings import PROJECTS_DIR, LOG_DIR, DB_DIR


def init(folder):
    """
    init workspace
    :param folder:
    :return:
    """
    print("\033[1;31mInitialized workspace %s\033[0m" % folder)

    # execute path
    execute_path = abspath(getcwd())

    # make folder dir, default to pyhive
    folder_path = join(execute_path, folder)
    exists(folder_path) or makedirs(folder_path)

    print('create project dir...')
    # make dir of projects
    projects_folder = join(folder_path, PROJECTS_DIR)
    exists(projects_folder) or makedirs(projects_folder)

    print('create log dir...')
    # make dir of logs
    logs_folder = join(folder_path, LOG_DIR)
    exists(logs_folder) or makedirs(logs_folder)

    print('create db dir...')
    # make dir of DB
    dbs_folder = join(folder_path, DB_DIR)
    exists(dbs_folder) or makedirs(dbs_folder)

    # create wsgi.py and uwsgi.ini and lock file
    env = Environment(
        loader=PackageLoader('pyhive'),
        autoescape=select_autoescape(['j2'])
    )

    print('create wsgi.py...')
    template = env.get_template('wsgi.j2')
    content = template.render()
    with open(join(folder_path, 'wsgi.py'), 'w') as f:
        f.write(content)

    print('create uwsgi.ini...')
    template = env.get_template('uwsgi.j2')
    content = template.render(chdir=folder_path)
    with open(join(folder_path, 'uwsgi.ini'), 'w') as f:
        f.write(content)

    print('create scheduler.lock...')
    with open(join(folder_path, 'scheduler.lock'), 'w') as f:
        f.write('')

    print("\033[1;31mComplete\033[0m")


def initadmin():
    """
    create super user
    :return:
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyhive.server.server.settings")
    django.setup()
    from django.contrib.auth.models import User

    admins = User.objects.filter(is_superuser=True)
    if admins:
        print("\033[1;31mAdmin user already exists, you can use them to login:\033[0m")
        for admin in admins:
            print('- %s(%s)' % (admin.username, admin.email))
    else:
        print("\033[1;31mNo Admin user exists, create temp admin user\033[0m")
        username = 'admin'
        email = '%s@pyhive.com' % username
        password = username
        admin, created = User.objects.update_or_create(email=email, username=username)
        admin.set_password(password)
        admin.is_active = True
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        print(
            '%s admin account: %s(%s), initial password: %s, just use it temporarily and change the password for safety'
            % ('Created' if created else 'Reset', username, email, password)
        )


def check():
    """
    check path
    :return:
    """
    # execute path
    execute_path = getcwd()
    projects_folder = join(execute_path, PROJECTS_DIR)
    logs_folder = join(execute_path, LOG_DIR)
    dbs_folder = join(execute_path, DB_DIR)

    if exists(projects_folder) and exists(logs_folder) and exists(dbs_folder):
        return True
    else:
        print("\033[0;31mUnavailable workspace, run 'pyhive init' first!\033[0m")
        return False
