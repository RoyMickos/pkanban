from django.db import models
from django.contrib import admin
import datetime
import logging


# Work phases
class PkWorkPhases(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    capacity = models.PositiveSmallIntegerField()
    description = models.TextField()

    def __unicode__(self):
        return u"%s : %d" % (self.name, self.capacity)

    def hasFreeCapacity(self):
        return ((len(PkWipTasks.objects.filter(phase = self)) < self.capacity) or (self.capacity == 0))

    def addTask(self, task, forced = False):
        alreadyInWip = (len(PkWipTasks.objects.filter(task=task)) > 0)
        if (not alreadyInWip and (self.hasFreeCapacity() or forced)):
            item = PkWipTasks.objects.create(phase = self, task = task)
            return True
        else:
            log = logging.getLogger('pkanban.application')
            log.error("PkWorkPhase:addTask: Failed to add task to wip. Capacity %d/%d, Already tracked: %s, Forced: %s" % (len(PkWipTasks.objects.filter(phase=self)),
                                                                                                                           self.capacity,
                                                                                                                           str(alreadyInWip),
                                                                                                                           str(forced)))
            return False

admin.site.register(PkWorkPhases)

# valuestreams
class PkError(Exception):
    def __init__(self, msg):
        self.message = msg

class WipLimitReached(PkError):
    pass

class TaskAlreadyCompleted(PkError):
    pass

class TaskNotInThisStream(PkError):
    pass

class PkValuestream(models.Model):
    streamname = models.CharField(max_length=50, primary_key=True)
    phases = models.ManyToManyField(PkWorkPhases)
    #tasks = models.TextField()

    def __unicode__(self):
        return unicode(self.streamname)

    def addPhase(self, aPhase):
        if aPhase not in self.phases.all():
            self.phases.add(aPhase)
        else:
            log = logging.getLogger('pkanban.application')
            log.error('PkValuestream: could not add phase \"%s\" because it is already in %s' % ','.join(self.phases.all()))

    def getStreamStatus(self, aTask):
        """getStreamStatus - find where a task is in the stream and where it is heading
        Determines where a task is currently in the stream, and what is the capacity situation in the
        next phase.
        Return collected data in a dictionary.
        """
        thePhases = self.phases.all()
        count = len(thePhases)
        currentPhase = None
        nextPhase = None
        wipRecord = None
        if aTask.isDone():
            return {'currentPhase': 'completed'}
        s = PkWipTasks.objects.filter(task=aTask)
        if len(s) == 1:
            if aTask.valuestream != self:
                raise TaskNotInThisStream("Stream: %s, Task: %s" % (self.streamname, aTask.name))
            currentPhase = s[0].phase
            phaseIndex = -1
            for index in range(count):
                if thePhases[index] == currentPhase:
                    phaseIndex = index
                    break
            if phaseIndex == (count-1) :
                nextPhase = 'completed'
            else:
                nextPhase = thePhases[phaseIndex + 1]
            wipRecord = s[0]
        else:
            nextPhase = thePhases[0]
        if nextPhase == 'completed':
            canProceed = True
        else:
            canProceed = nextPhase.hasFreeCapacity()
        return {'currentPhase': currentPhase, 'nextPhase': nextPhase, 'wipRecord': wipRecord,
                'canProceed': canProceed}

    def nextPhase(self, aTask, forced = False):
        if aTask.isDone():
            raise TaskAlreadyCompleted(aTask.name)
        else:
            status = self.getStreamStatus(aTask)

        if status['nextPhase'] == 'completed':
            status['wipRecord'].delete()
            aTask.complete()
            aTask.save()
            return
        if status['canProceed'] or forced:
            if status['currentPhase'] is not None:
                status['wipRecord'].delete()
            status['nextPhase'].addTask(aTask, forced)
            if status['currentPhase'] is None:
                aTask.valuestream = self
            aTask.log('Valuestream \"%s\": proceeding to phase \"%s\"' % (self.streamname,
                                                                          status['nextPhase'].name))
            aTask.save()
        else:
            raise WipLimitReached(status['nextPhase'].name)
        return

admin.site.register(PkValuestream)

# Base task model
class PkTask(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    history = models.TextField(blank=True)
    effort = models.IntegerField()
    lastmodify = models.DateTimeField(auto_now=True)
    valuestream = models.ForeignKey(PkValuestream, null=True, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ("task_view", [str(self.id)])

    def __unicode__(self):
        return u'%s' % self.name

    def isDone(self):
        return self.completed is not None

    def log(self, event):
        if not self.isDone():
            #self.history += (str(datetime.datetime.now()) + ' ' + event + '\n')
            logR = PkLog(task=self.id,  time=datetime.datetime.now(),
            								 event = event)
            logR.save()

    def initialize(self):
        self.effort = 0
        self.valuestream = None
        self.log("Task Created")

    def update(self, fieldDict):
        for key in ['name', 'description']:
            if key in fieldDict:
                self.__dict__[key] = fieldDict.__getitem__(key)

    def complete(self):
        if not self.isDone():
            self.log("Task completed")
            self.completed = datetime.datetime.now()

    def hourlyEffort(self):
        return '{0:d}:{1:0>2d}'.format(self.effort / 60, self.effort % 60)

class PkLog(models.Model):
		task = models.ForeignKey(PkTask, related_name='logs')
		time = models.DateTimeField()
		event = models.CharField(max_length=255)

		def __unicode__(self):
			return u'%d %s %s' % (self.task.pk, str(self.time), self.event)

class PkTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'lastmodify', 'completed', 'effort']

admin.site.register(PkTask, PkTaskAdmin)

#tasks in work-in-progress state
class PkWipTasks(models.Model):
    phase = models.ForeignKey(PkWorkPhases)
    task = models.ForeignKey(PkTask)

    def __unicode__(self):
        return u'%s : %d' % (self.phase.name, self.task.id)


admin.site.register(PkWipTasks)
