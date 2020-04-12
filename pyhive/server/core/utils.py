import fnmatch
import os
import logging
from shutil import ignore_patterns, copy2, copystat
from scrapyd_api import ScrapydAPI
from bs4 import BeautifulSoup
from os.path import join

from scrapyd_api import RUNNING, FINISHED, PENDING

logger = logging.getLogger(__name__)

IGNORES = ['.git/', '*.pyc', '.DS_Store', '.idea/', '*.egg', '*.egg-info/', '*.egg-info', 'build/']

NO_REFERRER = '<meta name="referrer" content="never">'
BASE = '<base href="{href}">'


def get_scrapyd(client):
    """
    get scrapyd of client
    :param client: client
    :return: scrapyd
    """
    if not client.auth:
        return ScrapydAPI(scrapyd_url(client.ip, client.port))
    return ScrapydAPI(scrapyd_url(client.ip, client.port), auth=(client.username, client.password))


def scrapyd_url(ip, port):
    """
    get scrapyd url
    :param ip: host
    :param port: port
    :return: string
    """
    url = 'http://{ip}:{port}'.format(ip=ip, port=port)
    return url


def log_url(ip, port, project, spider, job):
    """
    get log url
    :param ip: host
    :param port: port
    :param project: project
    :param spider: spider
    :param job: job
    :return: string
    """
    url = 'http://{ip}:{port}/logs/{project}/{spider}/{job}.log'.format(
        ip=ip, port=port, project=project, spider=spider, job=job
    )
    return url


def get_spider_status_index(status):
    """
    get spider status index
    :param status: text of spider status
    :return: index
    """
    if status == RUNNING:
        return 1
    elif status == FINISHED:
        return 2
    elif status == PENDING:
        return -1
    else:
        return -2


def ignored(ignores, path, file):
    """
    judge if the file is ignored
    :param ignores: ignored list
    :param path: file path
    :param file: file name
    :return: bool
    """
    file_name = join(path, file)
    for ignore in ignores:
        if '/' in ignore and ignore.rstrip('/') in file_name:
            return True
        if fnmatch.fnmatch(file_name, ignore):
            return True
        if file == ignore:
            return True
    return False


def copy_tree(src, dst):
    """
    copy tree
    :param src:
    :param dst:
    :return:
    """
    ignore = ignore_patterns(*IGNORES)
    names = os.listdir(src)
    ignored_names = ignore(src, names)
    if not os.path.exists(dst):
        os.makedirs(dst)

    for name in names:
        if name in ignored_names:
            continue

        src_name = os.path.join(src, name)
        dst_name = os.path.join(dst, name)
        if os.path.isdir(src_name):
            copy_tree(src_name, dst_name)
        else:
            copy2(src_name, dst_name)
    copystat(src, dst)


def get_tree(path, ignores=None):
    """
    get tree structure
    :param path: Folder path
    :param ignores: Ignore files
    :return: Json
    """
    if ignores is None:
        ignores = IGNORES
    result = []
    for file in os.listdir(path):
        if os.path.isdir(join(path, file)):
            if not ignored(ignores, path, file):
                children = get_tree(join(path, file), ignores)
                if children:
                    result.append({
                        'label': file,
                        'children': children,
                        'path': path
                    })
        else:
            if not ignored(ignores, path, file):
                result.append({'label': file, 'path': path})
    return result


def process_html(html, base_url):
    """
    process html, add some tricks such as no referrer
    :param base_url:
    :param html: source html
    :return: processed html
    """
    dom = BeautifulSoup(html, 'lxml')
    dom.find('head').insert(0, BeautifulSoup(NO_REFERRER, 'lxml'))
    dom.find('head').insert(0, BeautifulSoup(BASE.format(href=base_url), 'lxml'))
    html = str(dom)
    return html
