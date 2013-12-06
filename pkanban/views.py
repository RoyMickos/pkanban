# Create your views here.
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

dev = False

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
    """ show_spa
    show the single page application version of the ui
    """
    c = RequestContext(request)
    return render_to_response('index.html', c)

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
