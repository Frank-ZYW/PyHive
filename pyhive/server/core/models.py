from django.utils import timezone
from django.db.models import Model, CharField, IntegerField, DateField,\
    DateTimeField, ForeignKey, CASCADE, BooleanField, SET_NULL

# Create your models here.


class Client(Model):
    """
    Scrapyd Server
    """
    name = CharField(max_length=100)
    ip = CharField(max_length=100)
    port = IntegerField(default=6800)
    auth = BooleanField(default=False)
    username = CharField(max_length=100, blank=True, null=True, default=None)
    password = CharField(max_length=100, blank=True, null=True, default=None)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(default=timezone.now)
    spider_amount = IntegerField(default=0)

    def __str__(self):
        """
        to string
        :return: name
        """
        return self.name

    def remove_spider(self, amount):
        """
        remove spider
        :param amount: amount of spider
        """
        self.spider_amount -= amount
        self.save()

    def add_spider(self, amount):
        """
        add spider
        :param amount: amount of spider
        """
        self.spider_amount += amount
        self.save()


class Project(Model):
    """
    Project Object
    """
    name = CharField(max_length=100, unique=True)
    egg = CharField(max_length=255, null=True, blank=True, default=None)
    if_built = BooleanField(default=False)
    uploaded_version = CharField(max_length=30, blank=True, null=True, default=None)
    deployed_version = CharField(max_length=30, blank=True, null=True, default=None)
    deployed_at = DateTimeField(default=None, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(default=timezone.now)
    spider_amount = IntegerField(null=True, default=None)
    client = ForeignKey(Client, on_delete=SET_NULL, null=True, blank=True, default=None)

    def __str__(self):
        """
        to string
        :return: name
        """
        return self.name


class Spider(Model):
    """
    Spider object
    """
    project = ForeignKey(Project, on_delete=CASCADE, null=True, blank=True)
    name = CharField(max_length=255, unique=True)
    manual = BooleanField(blank=True, default=True)
    latest_run = DateTimeField(null=True, blank=True, default=None)
    next_run_duration = IntegerField(null=True, blank=True, default=None)
    available = BooleanField(default=True)
    current_job_id = CharField(max_length=255, null=True, blank=True, default=None)

    def __str__(self):
        """
        to string
        :return: name
        """
        return self.name


class Record(Model):
    """
    Result of Spider running
    """
    spider = ForeignKey(Spider, on_delete=CASCADE)
    page_ignore_count = IntegerField(default=0)
    page_error_count = IntegerField(default=0)
    item_scrape_count = IntegerField(default=0)
    item_error_count = IntegerField(default=0)
    run_times = IntegerField(default=0)
    run_date = DateField()

    def __str__(self):
        """
        to string
        :return: name
        """
        return self.spider.name
