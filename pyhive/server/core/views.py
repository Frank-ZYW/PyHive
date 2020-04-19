import base64
import json
import os
import sys
import requests
import time
import zipfile
import logging
from datetime import date, timedelta
from os.path import join, exists
from shutil import rmtree
from urllib.parse import unquote
from django.core.files.storage import FileSystemStorage
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.db.models import F
from requests.exceptions import ConnectionError, ReadTimeout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

from pyhive.settings import PROJECTS_DIR, WORKPLACE
from pyhive.server.core.build import build_project, find_egg
from pyhive.server.core.models import Client, Project, Spider, Record
from pyhive.server.core.response import JsonResponse
from pyhive.server.core.utils import scrapyd_url, log_url, get_tree, get_scrapyd, process_html, get_spider_status_index
from pyhive.server.core.serializers import ProjectSerializer, SpiderSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
def index(request):
    """
    render index page
    :param request: request object
    :return: page
    """
    return render(request, 'index.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def index_status(request):
    """
    index statistics
    :param request: request object
    :return: json
    """
    if request.method == 'GET':
        clients = Client.objects.all()
        data = {
            'success': 0,
            'error': 0,
            'project': 0,
        }
        # clients info
        for client in clients:
            try:
                requests.get(scrapyd_url(client.ip, client.port), timeout=1)
                data['success'] += 1
            except (ConnectionError, ReadTimeout):
                data['error'] += 1
        # projects info
        data['project'] = Project.objects.count()
        return JsonResponse(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_index(request):
    """
    get client list
    :param request: request object
    :return: client list
    """
    """
    Serializers allow complex data such as querysets and model instances to be
    converted to native Python data types that can then be easily rendered into
    JSON, XML or other content types. 
    """
    return HttpResponse(serialize('json', Client.objects.order_by('id')))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_info(request, client_id):
    """
    get client info
    :param request: request object
    :param client_id: client id
    :return: json
    """
    if request.method == 'GET':
        return JsonResponse(model_to_dict(Client.objects.get(id=client_id)))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_status(request, client_id):
    """
    get client status
    :param request: request object
    :param client_id: client id
    :return: json
    """
    if request.method == 'GET':
        client = Client.objects.get(id=client_id)
        try:
            requests.get(scrapyd_url(client.ip, client.port), timeout=1)
        except (ConnectionError, ReadTimeout):
            return HttpResponse(status=500)
        return JsonResponse({'result': '1'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def client_update(request, client_id):
    """
    update client info
    :param request: request object
    :param client_id: client id
    :return: json
    """
    if request.method == 'POST':
        client = Client.objects.filter(id=client_id)
        data = json.loads(request.body)
        data['updated_at'] = timezone.now()
        client.update(**data)
        return JsonResponse(model_to_dict(client[0]))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def client_create(request):
    """
    create a client
    :param request: request object
    :return: json
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        client = Client.objects.create(**data)
        return JsonResponse(model_to_dict(client))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_remove(request, client_id):
    """
    remove a client
    :param request: request object
    :param client_id: client id
    :return: json
    """
    if request.method == 'GET':
        client = Client.objects.get(id=client_id)
        projects = Project.objects.filter(client=client)
        try:
            scrapyd = get_scrapyd(client)
            # withdraw projects
            for each in projects:
                result = scrapyd.delete_project(project=each.name)
                if not result:
                    return JsonResponse({'result': 0})
                Spider.objects.filter(project=each).update(available=False)
        except (ConnectionError, ReadTimeout):
            return JsonResponse({'message': 'Connect Error'})
        projects.update(client=None, deployed_at=None, deployed_version=None, spider_amount=None)
        # delete client
        client.delete()
        return JsonResponse({'result': 1})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_index(request):
    """
    project index list
    :param request: request object
    :return: json
    """
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        projects = ProjectSerializer(Project.objects.filter(name__contains=keyword), many=True)
        return HttpResponse(JSONRenderer().render(projects.data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_tree(request, project_name):
    """
    get file tree of project
    :param request: request object
    :param project_name: project name
    :return: json of tree
    """
    if request.method == 'GET':
        path = os.path.abspath(join(WORKPLACE, PROJECTS_DIR))
        # get tree data
        tree = get_tree(join(path, project_name))
        return JsonResponse(tree)


@api_view(['POST'])
def project_upload(request):
    """
    upload project, create or update
    :param request: request object
    :return: json
    """
    if request.method == 'POST':
        file = request.FILES['file']
        path = os.path.abspath(join(WORKPLACE, PROJECTS_DIR))

        file_name = file.name
        fs = FileSystemStorage(path)
        zip_file_name = fs.save(file_name, file)
        zip_file_path = join(path, zip_file_name)

        # extract zip file and rm
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(path)
        os.remove(zip_file_path)

        project_name = os.path.splitext(zip_file_name)[0]
        if not os.path.isdir(os.path.join(path, project_name)):
            return JsonResponse({'message': 'Project dir is not valid'}, status=500)
        version_file_path = os.path.join(path, project_name, '__version__.py')
        if not os.path.exists(version_file_path):
            return JsonResponse({'message': 'No version file'}, status=500)

        # get version and update
        about = {}
        with open(version_file_path) as f:
            exec(f.read(), about)
        Project.objects.update_or_create(
            name=project_name,
            defaults={
                'updated_at': timezone.now(),
                'uploaded_version': about['__version__'],
                'if_built': False
            }
        )
        return JsonResponse({'status': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_remove(request, project_name):
    """
    remove project from disk and db
    :param request: request object
    :param project_name: project name
    :return: result of remove
    """
    if request.method == 'GET':
        # get project path
        path = os.path.abspath(join(WORKPLACE, PROJECTS_DIR))
        project_path = join(path, project_name)
        # delete project file tree
        if exists(project_path):
            rmtree(project_path)
        Project.objects.get(name=project_name).delete()
        return JsonResponse({'result': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_withdraw(request, project_name):
    """
    withdraw project from client
    :param request: request object
    :param project_name: project name
    :return: json
    """
    if request.method == 'GET':
        project = Project.objects.get(name=project_name)
        # remove project from client
        try:
            scrapyd = get_scrapyd(project.client)
            result = scrapyd.delete_project(project=project_name)
            if not result:
                return JsonResponse({'result': result})
        except (ConnectionError, ReadTimeout):
            return JsonResponse({'message': 'Connect Error'})
        # alter project status
        project.deployed_at = None
        project.deployed_version = None
        project.client.remove_spider(project.spider_amount)
        project.client = None
        project.spider_amount = None
        project.save()
        # invalidate spiders
        Spider.objects.filter(project=project).update(available=False)
        return JsonResponse({'result': result})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_deploy(request, client_id, project_name):
    """
    deploy project operation
    :param request: request object
    :param client_id: client id
    :param project_name: project name
    :return: json of deploy result
    """
    if request.method == 'GET':
        # get project folder
        path = os.path.abspath(join(WORKPLACE, PROJECTS_DIR))
        project_path = join(path, project_name)
        # find egg file
        egg = find_egg(project_path)
        if not egg:
            return JsonResponse({'message': 'egg not found'}, status=500)
        egg_file = open(join(project_path, egg), 'rb')
        # get client and project model
        client = Client.objects.get(id=client_id)
        project = Project.objects.get(name=project_name)
        # execute deploy operation
        scrapyd = get_scrapyd(client)
        spider_amount = scrapyd.add_version(project_name, int(time.time()), egg_file.read())
        # update client info
        if project.client:
            client.remove_spider(project.spider_amount)
        client.add_spider(spider_amount)
        # update project info
        project.client = client
        project.deployed_version = project.uploaded_version
        project.deployed_at = timezone.now()
        project.spider_amount = spider_amount
        project.save()
        # update spider info
        spiders = scrapyd.list_spiders(project_name)
        Spider.objects.filter(project=project).exclude(name__in=spiders).delete()
        for each in spiders:
            Spider.objects.update_or_create(name=each, defaults={'project': project, 'available': True})
        return JsonResponse(model_to_dict(project))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_build(request, project_name):
    """
    execute build operation
    :param request: request object
    :param project_name: project name
    :return: json
    """
    if request.method == 'GET':
        # get project folder
        path = os.path.abspath(join(WORKPLACE, PROJECTS_DIR))
        project_path = join(path, project_name)
        model = Project.objects.get(name=project_name)

        # build
        build_project(project_name, model.uploaded_version)
        egg = find_egg(project_path)
        if not egg:
            return JsonResponse({'message': 'egg not found'}, status=500)

        # update project info
        model.if_built = True
        model.egg = egg
        model.save()
        return JsonResponse(model_to_dict(model))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_file_read(request):
    """
    get content of project file
    :param request: request object
    :return: file content
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        path = join(data['path'], data['label'])
        # binary file
        with open(path, 'rb') as f:
            return HttpResponse(f.read().decode('utf-8'))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_file_update(request):
    """
    update project file
    :param request: request object
    :return: result of update
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        path = join(data['path'], data['label'])
        code = data['code']
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
            return JsonResponse({'result': '1'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_file_create(request):
    """
    create project file
    :param request: request object
    :return: result of create
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        path = join(data['path'], data['name'])
        open(path, 'w', encoding='utf-8').close()
        return JsonResponse({'result': '1'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_file_delete(request):
    """
    delete project file
    :param request: request object
    :return: result of delete
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        path = join(data['path'], data['label'])
        os.remove(path)
        return JsonResponse({'result': 1})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_file_rename(request):
    """
    rename file name
    :param request: request object
    :return: result of rename
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        pre = join(data['path'], data['pre'])
        new = join(data['path'], data['new'])
        os.rename(pre, new)
        return JsonResponse({'result': '1'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spider_list(request, client_id):
    """
    get spiders list which contain keyword from one client
    :param request: request Object
    :param client_id: client id
    :return: json
    """
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        spiders = SpiderSerializer(Spider.objects.filter(project__client=client_id, name__contains=keyword), many=True)
        return HttpResponse(JSONRenderer().render(spiders.data))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def spider_update(request, spider_id):
    """
    update spider info
    :param request: request object
    :param spider_id: spider id
    :return: json
    """
    if request.method == 'POST':
        spider = Spider.objects.filter(id=spider_id)
        data = json.loads(request.body)
        spider.update(**data)
        return JsonResponse(model_to_dict(spider[0]))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spider_start(request, spider_id):
    """
    start a spider
    :param request: request object
    :param spider_id: spider id
    :return: json
    """
    if request.method == 'GET':
        spider = Spider.objects.get(id=spider_id)
        scrapyd = get_scrapyd(spider.project.client)
        job = scrapyd.schedule(spider.project.name, spider.name)
        spider.current_job_id = job
        spider.latest_run = timezone.now()
        spider.save()
        return JsonResponse({'job': job})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spider_status(request, spider_id):
    """
    get job list of spider from one client
    :param request: request object
    :param spider_id: spider id
    :return: list of jobs
    """
    if request.method == 'GET':
        spider = Spider.objects.get(id=spider_id)
        scrapyd = get_scrapyd(spider.project.client)
        try:
            job_id = spider.current_job_id if spider.current_job_id else ''
            result = scrapyd.job_status(spider.project.name, job_id)
            return JsonResponse({'status': get_spider_status_index(result)})
        except (ConnectionError, ReadTimeout):
            return JsonResponse({'message': 'Connect Error'}, status=500)


@api_view(['POST'])
def spider_feedback(request, spider_name):
    """
    get feedback from workerbee project
    :param request: request object
    :param spider_name: spider name
    :return:
    """
    if request.method == 'POST':
        try:
            spider = Spider.objects.get(name=spider_name)
        except Spider.DoesNotExist:
            logger.error("miss finding Spider %s" % spider_name)
            return JsonResponse({}, status=500)
        spider.available = bool(request.POST.get('error'))
        spider.save()
        if Record.objects.filter(spider=spider, run_date=date.today()).exists():
            Record.objects.update_or_create(
                spider=spider,
                run_date=date.today(),
                defaults={
                    'page_ignore_count': F('page_ignore_count') + int(request.POST.get('pageIgnored')),
                    'page_error_count': F('page_error_count') + int(request.POST.get('pageError')),
                    'item_scrape_count': F('item_scrape_count') + int(request.POST.get('itemScraped')),
                    'item_error_count': F('item_error_count') + int(request.POST.get('itemError')),
                    'run_times': F('run_times') + 1,
                }
            )
        else:
            Record.objects.create(
                spider=spider,
                run_date=date.today(),
                page_ignore_count=int(request.POST.get('pageIgnored')),
                page_error_count=int(request.POST.get('pageError')),
                item_scrape_count=int(request.POST.get('itemScraped')),
                item_error_count=int(request.POST.get('itemError')),
                run_times=1
            )
        return JsonResponse({'result': 1})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spider_monitor(request, spider_id):
    """
    Statistics on the running status of spider within 30 days
    :param request: request objectSerializer
    :param spider_id: spider id
    :return:
    """
    if request.method == 'GET':
        today = date.today()
        records = [{
            'run_date': (today - timedelta(days=day)).strftime("%m/%d"),
            'page_ignore': 0,
            'page_error': 0,
            'item_scrape': 0,
            'item_error': 0,
            'run_times':0
        } for day in range(29, -1, -1)]
        start_date_str = (today - timedelta(days=29)).strftime('%Y-%m-%d')
        results = Record.objects.filter(spider=spider_id, run_date__gte=start_date_str).order_by('run_date')
        for each in results:
            records[29 - (today - each.run_date).days] = {
                'run_date': each.run_date.strftime("%m/%d"),
                'page_ignore': each.page_ignore_count,
                'page_error': each.page_error_count,
                'item_scrape': each.item_scrape_count,
                'item_error': each.item_error_count,
                'run_times': each.run_times
            }
        return JsonResponse(records)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_list(request, spider_id):
    """
    get job list of spider from one client
    :param request: request object
    :param spider_id: spider id
    :return: list of jobs
    """
    if request.method == 'GET':
        spider = Spider.objects.get(id=spider_id)
        scrapyd = get_scrapyd(spider.project.client)
        try:
            result = scrapyd.list_jobs(spider.project.name)
            jobs = []
            statuses = ['pending', 'running', 'finished']
            for status in statuses:
                for job in result.get(status):
                    if job['spider'] == spider.name:
                        job['status'] = status
                        jobs.append(job)
            return JsonResponse(jobs)
        except (ConnectionError, ReadTimeout):
            return JsonResponse({'message': 'Connect Error'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_log(request, spider_id, job_id):
    """
    get log of jog
    :param request: request object
    :param spider_id: spider id
    :param job_id: job id
    :return: log of job
    """
    if request.method == 'GET':
        spider = Spider.objects.get(id=spider_id)
        # get log url
        client = spider.project.client
        url = log_url(client.ip, client.port, spider.project.name, spider.name, job_id)
        try:
            # get last 2000 bytes of log
            response = requests.get(url, timeout=5, headers={
                'Range': 'bytes=-2000'
            }, auth=(client.username, client.password) if client.auth else None)
            # Get encoding
            encoding = response.apparent_encoding
            # log not found
            if response.status_code == 404:
                return JsonResponse({'message': 'Log Not Found'}, status=404)
            # bytes to string
            text = response.content.decode(encoding, errors='replace')
            return HttpResponse(text)
        except (ConnectionError, ReadTimeout):
            return JsonResponse({'message': 'Load Log Error'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_cancel(request, spider_id):
    """
    cancel a job
    :param request: request object
    :param spider_id: spider id
    :return: json of cancel
    """
    if request.method == 'GET':
        spider = Spider.objects.get(id=spider_id)
        try:
            scrapyd = get_scrapyd(spider.project.client)
            result = scrapyd.cancel(spider.project.name, spider.current_job_id)
            return JsonResponse(result)
        except (ConnectionError, ReadTimeout):
            return JsonResponse({'message': 'Connect Error'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def render_html(request):
    """
    render html with url
    :param request:
    :return:
    """
    if request.method == 'GET':
        url = request.GET.get('url')
        url = unquote(base64.b64decode(url).decode('utf-8'))
        try:
            response = requests.get(url, timeout=5)
            response.encoding = response.apparent_encoding
            html = process_html(response.text, url)
            return HttpResponse(html)
        except Exception as e:
            return JsonResponse({'message': e.args}, status=500)


# start scheduler
if 'runserver' in sys.argv or 'uwsgi' in sys.argv:
    try:
        from pyhive.server.core.scheduler import lock_file
        lock_file()
    except OSError:
        pass
    else:
        from pyhive.server.core.scheduler import SchedulerManager
        logger.info('Background scheduler start')
        sm = SchedulerManager()
        sm.start()
