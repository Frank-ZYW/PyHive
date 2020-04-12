"""
Scheduler of spiders
"""

import time
import fcntl
import atexit
import logging
from os.path import abspath, join
from threading import Thread
from django.utils import timezone

from pyhive.settings import WORKPLACE, SCHEDULER_HEARTBEAT
from pyhive.server.core.models import Spider
from pyhive.server.core.utils import get_scrapyd, get_spider_status_index

logger = logging.getLogger(__name__)


def lock_file():
    """
    init and start scheduler
    :return:
    """

    def unlock():
        """
        unlock file
        :return:
        """
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()

    lock_file_path = abspath(join(WORKPLACE, 'scheduler.lock'))
    f = open(lock_file_path, 'wb')

    # Make file lock to ensure only one process starts scheduler
    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

    # unlock file when server shutdown
    atexit.register(unlock)


def execute(spider):
    """
    execute deployed spider
    :param spider: spider object
    :return:
    """
    client_name = spider.project.client.name
    project_name = spider.project.name
    scrapyd = get_scrapyd(spider.project.client)

    # check current status
    if spider.current_job_id:
        status = scrapyd.job_status(spider.project.name, spider.current_job_id)
        status = get_spider_status_index(status)
        # running or pending
        if abs(status) == 1:
            logger.info(
                'job: client %s, project %s, spider %s is already running', client_name, project_name, spider.name)
            return

    job = scrapyd.schedule(project_name, spider.name)
    spider.current_job_id = job
    spider.latest_run = timezone.now()
    spider.save()
    logger.info('execute job of client %s, project %s, spider %s', client_name, project_name, spider.name)


class SchedulerManager(Thread):
    """
    Scheduler of tasks
    """

    heartbeat = SCHEDULER_HEARTBEAT * 60
    sql = "select * from core_spider where datetime(latest_run, " \
          "'+' || cast(next_run_duration as text) || ' day') < datetime('now') " \
          "and available=TRUE and manual=FALSE;"

    def __init__(self):
        """
        init manager
        """
        super(SchedulerManager, self).__init__()
        self.setDaemon(True)

    def scheduler_manager(self, sql_str):
        logger.info('scheduler...')
        spiders = Spider.objects.raw(sql_str)
        for each_spider in spiders:
            execute(each_spider)

    def run(self):
        """
        heart beat detect
        :return:
        """
        while True:
            self.scheduler_manager(self.sql)
            time.sleep(self.heartbeat)
