from django.contrib import admin
from pyhive.server.core.models import Client, Project, Spider, Record

# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'port', 'created_at', 'updated_at', 'spider_amount')


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'egg',
        'if_built',
        'created_at',
        'updated_at',
        'uploaded_version',
        'deployed_at',
        'deployed_version',
        'spider_amount',
        'client_name'
    )

    def client_name(self, obj):
        return '%s' % obj.client.name if obj.client else '-'


class SpiderAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'available',
        'manual',
        'latest_run',
        'next_run_duration',
        'current_job_id'
    )


class RecordAdmin(admin.ModelAdmin):
    list_display = (
        'spider_name',
        'run_date',
        'page_ignore_count',
        'page_error_count',
        'item_scrape_count',
        'item_error_count'
    )

    def spider_name(self, obj):
        return '%s' % obj.spider.name


admin.site.register(Client, ClientAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Spider, SpiderAdmin)
admin.site.register(Record, RecordAdmin)
