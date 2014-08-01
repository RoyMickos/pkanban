# createte your views here.
from models import PkTask, PkWipTasks, PkValuestream, PkWorkPhases
from models import WipLimitReached, TaskAlreadyCompleted, TaskNotInThisStream
import logging, json
import pkutil
from forms import *
from django.shortcuts import get_object_or_404, render_to_response, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# rest framework
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework import status
#from rest_framework.reverse import reverse
#from rest_framework.decorators import api_view
#from rest_framework import renderers
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action, link
from pkanban.serializers import TaskSerializer, UserSerializer, PhaseSerializer
from pkanban.serializers import PaginatedTaskSerializer
from pkanban.serializers import WipSerializer, ValueStreamSerializer, ValueStreamIdentitySerializer

dev = False
LOG = logging.getLogger(__name__)

@login_required(login_url='/pkanban/login/')
def load_app(request):
  c = RequestContext(request)
  c.update(csrf(request))
  return render_to_response('pkanban/pkanban_index.html', c)

@csrf_protect
def show_board(request):
    """show_board
    show the main display of the kanban app
    """
    c = RequestContext(request)
    c.update(csrf(request))
    c.update({'dev': dev})
    return render_to_response('pkanban.html', c)

def show_spa(request):
    """
    show the single page application version of the ui
    """
    c = RequestContext(request)
    print request.META['HTTP_HOST']
    print request.build_absolute_uri(c['STATIC_URL']+'index.html')
    return HttpResponseRedirect(request.build_absolute_uri(c['STATIC_URL']+'index.html'))
    #c = RequestContext(request)
    #return render_to_response('index.html', c)

def show_app(request):
  c = RequestContext(request)
  c.update(csrf(request))
  return render_to_response('pkanban/pkanban_index.html', c)

#def run_tests(request):
#    """ run_tests
#    return qunit test page
#    """
#   c = RequestContext(request)
#    return render_to_response('tests.html', c)

def setValuestream(aTask, requestData, valuestreams, log):
    sname = requestData['valuestream'].strip()
    aStream = None
    if sname != '':
        for vstream in valuestreams:
            if vstream.streamname == sname:
                aStream = vstream
                break
        if aStream is None:
            emsg = 'Could not find valuestream for \"%s\"' % sname
            log.error(emsg)
            return (True, emsg)
        try:
            aStream.nextPhase(aTask)
        except WipLimitReached:
            return (True, "Work-in-progress limit for \"%s\" has been reached" % sname)
        except TaskAlreadyCompleted:
            return (True, "Corrupted data: task \"%s\" has already been completed." % aTask.name)
        except TaskNotInThisStream:
            return (True, "Internal error: task \"%s\" not in stream \"%s\" " % (aTask.name, sname))
        else:
            return(False, "ok")
    else:
        return (True, "Valuestream is empty.")


@csrf_protect
def viewTask(request, object_id):
    c = RequestContext(request)
    log = logging.getLogger('pkanban.application')
    aTask = PkTask.objects.get(pk=object_id)
    valuestreams = PkValuestream.objects.all()
    # post request is an AJAX call
    if request.method == 'POST':
        requestData = pkutil.parseRequest(request)
        print requestData
        aTask.update(requestData)
        aTask.save()
        hasError = False
        msg = None
        if (('valuestream' in requestData) and (aTask.valuestream == None)):
            hasError, msg = setValuestream(aTask, requestData, valuestreams, log)
        if hasError:
            responseData = {'status': 'error', 'msg': msg}
        else:
            responseData = {'status': 'OK', 'url': aTask.get_absolute_url()}
        return HttpResponse(json.dumps(responseData), content_type='application/json')
    c.update({'task': aTask, 'isCompleted': aTask.completed is not None})
    if aTask.valuestream is not None:
        print aTask.valuestream.getStreamStatus(aTask)
        c.update({'status': aTask.valuestream.getStreamStatus(aTask)})
    c.update(csrf(request))
    c.update({'valuestreams': valuestreams, 'dev': dev})
    return render_to_response('TaskView.html',c)

def advanceTask(request):
    # handle ajax request to proceed with task
    receivedData = pkutil.parseRequest(request)
    responseData = dict()
    taskId = int(receivedData['taskid'])
    aTask = PkTask.objects.get(pk=taskId)
    try:
        aTask.valuestream.nextPhase(aTask, (receivedData['forced'] == 'true'))
    except WipLimitReached:
        responseData = {'status': 'Error', 'msg': 'Error: next phase has no capacity'}
    except TaskAlreadyCompleted:
        responseData = {'status': 'Error', 'msg': 'Error: task has been completed already'}
    except TaskNotInThisStream:
        responseData = {'status': 'Error', 'msg': 'Internal Error: wrong Valuestream'}
    else:
        responseData = {'status': 'OK'}
    return HttpResponse(json.dumps(responseData), content_type='application/json')

def getDescription(request, object_id):
    """getDescription - returns description text for task <object_id>
    Description can be written as html, so it can be queried as ajax as well. This is
    needed in order to properly handle html editors for editing the description.
    """
    c = RequestContext(request)
    aTask = PkTask.objects.get(pk=object_id)
    return HttpResponse(pkutil.encodeDescription(aTask.description))

@csrf_protect
def addTask(request):
    c = RequestContext(request)  # needed for static files to work
    log = logging.getLogger('pkanban.application')
    # post request is an AJAX call
    if request.POST:
        requestData = pkutil.parseRequest(request)
        requestData['valuestream'] = None
        newTask = PkTask(**requestData)
        newTask.initialize()
        newTask.save()
        return HttpResponse(json.dumps({'status': 'OK', 'url': '/pkanban/Task/NewTask/'}),
                            content_type='application/json')
    else:
        responseData = {'name': '', 'description': ''}
    c.update(csrf(request))
    c.update({'task': responseData, 'isNew': True, 'dev': dev})
    return render_to_response('NewTask.html',c)

def getWip(request):
    """getWip
    This generates an AJAX response of work-in-progress tasks
    """
    c = RequestContext(request)
    wiptasks = PkWipTasks.objects.all().order_by('phase')
    valuestreams = PkValuestream.objects.all()
    c.update({'tasks': wiptasks, 'streams': valuestreams})
    return render_to_response('wip.html', c)

def getBacklog(request):
    """getBacklog
    This generates an AJAX response (html) of backlog tasks
    """
    c = RequestContext(request)
    backlog = PkTask.objects.filter(completed__exact=None, valuestream__exact=None)
    c.update({'backlog': backlog})
    return render_to_response('backlog.html', c)

def editBoard(request):
    """editBoard
    Shows main page for viewing and editing phases and valuestreams
    """
    c = RequestContext(request)
    phases = PkWorkPhases.objects.all()
    vstreams = PkValuestream.objects.all()
    c.update(csrf(request))  # set csrf to be used in subsequent ajax queries to be handled in checkPhase
    c.update({'phases': phases, 'vstreams': vstreams, 'dev': dev})
    return render_to_response('streams.html', c)

def newPhase(request):
    # handle ajax request to create new phase
    try:
        receivedData = pkutil.parseRequest(request)
        PkWorkPhases.objects.create(**receivedData)
    except Exception as e:
        aResponse = {'status': 'Error', 'data': str(e)}
    else:
        aResponse = {'status': 'OK','data': receivedData['name']}
    return HttpResponse(json.dumps(aResponse), content_type='application/json')

def newStream(request):
    # handle ajax request to create new valuestream
    try:
        receivedData = pkutil.parseRequest(request)
        # we can't create a many-to-many relationship before the new valuestream has an id
        # so we're fetching phases from database first, so that if any errors occur they
        # will create an exception before we add the new stream to database
        phases = list()
        for aPhaseName in receivedData['phases'].split(','):
            if aPhaseName.strip() != '':
                phases.append(PkWorkPhases.objects.get(name = aPhaseName))
        newVStream = PkValuestream.objects.create(streamname = receivedData['name'])
        for aPhase in phases:
            newVStream.addPhase(aPhase)
    except Exception as e:
        aResponse = {'status': 'Error', 'data': str(e)}
        print e
    else:
        aResponse = {'status': 'OK', 'data': receivedData['name']}
    return HttpResponse(json.dumps(aResponse), content_type='application/json')

def addEffort(request):
    receivedData = pkutil.parseRequest(request)
    try:
        aTask = PkTask.objects.get(pk = receivedData['taskId'])
        if aTask.effort is None:
            aTask.effort = int(receivedData['minutes'])
        else:
            aTask.effort += int(receivedData['minutes'])
        aTask.log("Effort completed: %s" % receivedData['minutes'])
        aTask.save()
    except Exception as e:
        responseData = {'status': 'Error', 'msg': str(e)}
    else:
        responseData = {'status': 'OK', 'effort': aTask.effort}
    return HttpResponse(json.dumps(responseData), content_type='application/json')

def showArchive(request):
    c = RequestContext(request)
    completed = PkTask.objects.exclude(completed__exact=None).order_by('-completed')
    c.update({'tasks': completed, 'dev': dev})
    return render_to_response('archive.html', c)

def speedyArchieve(request):
    receivedData = pkutil.parseRequest(request)
    aTask = PkTask.objects.get(pk=int(receivedData['taskid']))
    # check if task is in wip
    s = PkWipTasks.objects.filter(task=aTask)
    if len(s) == 1:
        s[0].delete()
    aTask.valuestream = None
    aTask.complete()
    aTask.save()
    return HttpResponse(json.dumps({'status': 'OK', 'url': '/pkanban/'}), content_type='application/json')

# rest framework on class-based views
class TaskViewSet(viewsets.ModelViewSet):
  queryset = PkTask.objects.all()
  serializer_class = TaskSerializer

  def list(self, request):
    view = request.QUERY_PARAMS.get('filter')
    page = request.QUERY_PARAMS.get('page')
    if view == 'backlog':
      qs = PkTask.objects.filter(completed__exact=None, valuestream__exact=None)
    elif view == 'archive':
      qs = PkTask.objects.exclude(completed__exact=None).order_by('-completed')
    else:
      qs = PkTask.objects.all()
    paginator = Paginator(qs, 10)
    try:
      tasks = paginator.page(page)
    except PageNotAnInteger:
      tasks = paginator.page(1)
    except EmptyPage:
      tasks = paginator.page(paginator.num_pages)
    serializer = PaginatedTaskSerializer(tasks, {'request': request})
    return Response(data = serializer.data, status=status.HTTP_200_OK)

  def destroy(self, request, pk=None):
    task = self.get_object()
    # check if task is in WIP
    if PkWipTasks.objects.filter(task=task).exists():
      PkWipTasks.objects.filter(task=task).delete()
    task.valuestream = None
    task.complete()
    task.save()
    return Response("OK", status=status.HTTP_200_OK)

  @action()
  def set_valuestream(self, request, pk=None):
    task = self.get_object()
    streamname = request.DATA.get('valuestream')
    if streamname is None:
      return Response("Valuestream not specified", status=status.HTTP_400_BAD_REQUEST)
    valuestream = PkValuestream.objects.get(streamname=request.DATA.get('valuestream'))
    if valuestream is not None:
      try:
          valuestream.nextPhase(task)
      except WipLimitReached:
          return Response("Work-in-progress limit for \"%s\" has been reached" % valuestream.streamname,
            status=status.HTTP_400_BAD_REQUEST)
      except TaskAlreadyCompleted:
          return Response("Corrupted data: task \"%s\" has already been completed." % task.name,
            status=status.HTTP_400_BAD_REQUEST)
      except TaskNotInThisStream:
          return Response("Internal error: task \"%s\" not in stream \"%s\" " % (task.name, valuestream.streamname),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      else:
          return Response("ok", status=status.HTTP_200_OK)
    else:
      return Response("Valuestream not found", status=status.HTTP_400_BAD_REQUEST)

  @link()
  def advance_task(self, request, pk=None):
      aTask = self.get_object()
      forced = request.QUERY_PARAMS.get('forced')
      try:
          aTask.valuestream.nextPhase(aTask, forced)
      except WipLimitReached:
          return Response('Error: next phase has no capacity', status=status.HTTP_400_BAD_REQUEST)
      except TaskAlreadyCompleted:
          return Response('Error: task has been completed already', status=status.HTTP_400_BAD_REQUEST)
      except TaskNotInThisStream:
          return Response('Internal Error: wrong Valuestream', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      else:
          return Response("ok", status=status.HTTP_200_OK)

  @action()
  def add_effort(self, request, pk=None):
    task = self.get_object()
    minutes = request.DATA.get('minutes')
    try:
      minutes = int(minutes)
    except ValueError:
      return Response("Invalid value for parameter 'minutes'", status=status.HTTP_400_BAD_REQUEST)
    except TypeError:
      return Response("Missing parameter 'minutes'", status=status.HTTP_400_BAD_REQUEST)
    if task.effort is None:
      task.effort = minutes
    else:
      task.effort += minutes
    task.log("Effort completed: %s" % minutes)
    task.save()
    return Response("Total effort %d minutes" % task.effort, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer

class PhaseViewSet(viewsets.ModelViewSet):
  queryset = PkWorkPhases.objects.all()
  serializer_class = PhaseSerializer

class WipViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = PkWipTasks.objects.all()
  serializer_class = WipSerializer

class ValueStreamViewSet(viewsets.ModelViewSet):
  queryset = PkValuestream.objects.all()
  serializer_class = ValueStreamSerializer

  def list(self, request):
    resp = super(ValueStreamViewSet, self).list(request)
    for stream in resp.data:
      stream['phases'].insert(0, PkValuestream.BACKLOG)
      stream['phases'].append(PkValuestream.DONE)
    #print resp.data
    return resp

  def create(self, request):
    phases = request.DATA.get('phases')
    streamname = request.DATA.get('streamname')
    print phases
    if phases is None or streamname is None:
      return Response("No phases or streamname defined", status=status.HTTP_400_BAD_REQUEST)
    phase_list = list()
    for phase in phases:
      phase_list.append(PkWorkphases.objects.get(name=phase))
    stream = PkValuestream.objects.create(streamname=streamname)
    for phase in phase_list:
      stream.addPhase(phase)
    return Response("OK", status=status.HTTP_200_OK)

"""
def newStream(request):
    # handle ajax request to create new valuestream
    try:
        receivedData = pkutil.parseRequest(request)
        # we can't create a many-to-many relationship before the new valuestream has an id
        # so we're fetching phases from database first, so that if any errors occur they
        # will create an exception before we add the new stream to database
        phases = list()
        for aPhaseName in receivedData['phases'].split(','):
            if aPhaseName.strip() != '':
                phases.append(PkWorkPhases.objects.get(name = aPhaseName))
        newVStream = PkValuestream.objects.create(streamname = receivedData['name'])
        for aPhase in phases:
            newVStream.addPhase(aPhase)
    except Exception as e:
        aResponse = {'status': 'Error', 'data': str(e)}
        print e
    else:
        aResponse = {'status': 'OK', 'data': receivedData['name']}
    return HttpResponse(json.dumps(aResponse), content_type='application/json')
"""
