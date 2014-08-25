# createte your views here.
from models import PkTask, PkWipTasks, PkValuestream, PkWorkPhases
from models import WipLimitReached, TaskAlreadyCompleted, TaskNotInThisStream
import logging, json

from forms import *
from django.shortcuts import get_object_or_404, render_to_response, HttpResponseRedirect, redirect
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.http import HttpResponse
#from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

# rest framework
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action, link
from pkanban.serializers import TaskSerializer, UserSerializer, PhaseSerializer
from pkanban.serializers import PaginatedTaskSerializer
from pkanban.serializers import WipSerializer, ValueStreamSerializer, ValueStreamIdentitySerializer

dev = False
LOG = logging.getLogger(__name__)

#@login_required(login_url='/pkanban/login/')
# not using decorator in order to perform autologin in demo
def load_app(request):
  # we use a proxy at the front end so we need to workaround the forwarded host
  if hasattr(settings, 'ORIGINAL_HOST'):
    original_host = settings.ORIGINAL_HOST
  else:
    original_host = None
  LOG.debug(original_host)
  if hasattr(settings, 'DEMO'):
    demo = settings.DEMO
  else:
    demo = False

  if request.user.is_authenticated():
    c = RequestContext(request)
    c.update(csrf(request))
    c.update({'demo': demo})
    return render_to_response('pkanban/pkanban_index.html', c)
  else:
    if demo:
      user = authenticate(username='guest', password='guest_password')
      if user is not None:
        if user.is_active:
          login(request, user)
          return redirect(load_app)
        else:
          return redirect(something_wrong)
      else:
        return redirect(something_wrong)
    else:
      if original_host is not None:
        return redirect(original_host + settings.LOGIN_URL +'?next=' + settings.BASE_URL)
      else:
        return redirect(settings.LOGIN_URL +'?next=' + settings.BASE_URL)

def something_wrong(request):
  return render_to_response('pkanban/oops.html')

#def show_app(request):
#  c = RequestContext(request)
#  c.update(csrf(request))
#  return render_to_response('pkanban/pkanban_index.html', c)

#
# legacy code left here to wait until we reimplement this in new fw
#
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

#
# rest framework on class-based views
#

class TaskViewSet(viewsets.ModelViewSet):
  queryset = PkTask.objects.all()
  serializer_class = TaskSerializer

  def list(self, request):
    view = request.QUERY_PARAMS.get('filter')
    #page = request.QUERY_PARAMS.get('page')
    if view == 'backlog':
      qs = PkTask.objects.filter(completed__exact=None, valuestream__exact=None)
    elif view == 'archive':
      qs = PkTask.objects.exclude(completed__exact=None).order_by('-completed')
    else:
      qs = PkTask.objects.all()
    #paginator = Paginator(qs, 10)
    #try:
    #  tasks = paginator.page(page)
    #except PageNotAnInteger:
    #  tasks = paginator.page(1)
    #except EmptyPage:
    #  tasks = paginator.page(paginator.num_pages)
    serializer = TaskSerializer(qs, {'request': request})
    return Response(data = serializer.data, status=status.HTTP_200_OK)

  def destroy(self, request, pk=None):
    task = self.get_object()
    # check if task is in WIP
    if PkWipTasks.objects.filter(task=task).exists():
      PkWipTasks.objects.filter(task=task).delete()
    # change - delete means delete
    super(TaskViewSet,self).destroy(self, request, pk)
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
          return Response('Work-in-progress limit for "%s" has been reached' % valuestream.streamname,
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
    LOG.info(request.DATA)
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
