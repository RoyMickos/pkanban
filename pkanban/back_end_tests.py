"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import unittest
import models
import datetime
import copy

class TestPktask(TestCase):
    def setUp(self):
        self.aTask = models.PkTask.objects.create(name="Task a, uncompleted", effort=0)
        self.bTask = models.PkTask.objects.create(name="Task b, completed", effort=0)
        
    def test_initialization(self):
        self.aTask.initialize()
        self.assertEqual(self.aTask.effort, 0)
        self.assertFalse(self.aTask.isDone())
        self.assertTrue(self.aTask.history.find("Created") > 0)
        self.aTask.log("This tomato wants to become ketchup")
        self.assertTrue(self.aTask.history.find("ketchup") > 0)
        
    def test_completition(self):
        self.bTask.initialize()
        self.bTask.log("This ketchup wants to becom organic")
        self.bTask.complete()
        oldlog = copy.copy(self.bTask.history)
        self.bTask.log("This is a vain string")
        self.assertEqual(oldlog, self.bTask.history)
        
class TestPhases(TestCase):
    def setUp(self):
        self.incidents = models.PkWorkPhases.objects.create(name="incidents", capacity=2)
        self.study = models.PkWorkPhases.objects.create(name="study", capacity=1)
        self.unlimited = models.PkWorkPhases.objects.create(name="unlimited", capacity=0)
        self.aTask = models.PkTask.objects.create(name="Task a", effort=0)
        self.aTask.initialize()
        self.bTask = models.PkTask.objects.create(name="Task b", effort=0)
        self.bTask.initialize()
        self.cTask = models.PkTask.objects.create(name="Task c", effort=0)
        self.cTask.initialize()
        self.dTask = models.PkTask.objects.create(name="Task d", effort=0)
        self.dTask.initialize()
        
    def tearDown(self):
        """
        print "Dump of workphases:"
        for aPhase in models.PkWorkPhases.objects.all():
            print aPhase
        print "Dump of WIP:"
        for aRecord in models.PkWipTasks.objects.all():
            print aRecord
        """
        
    def test_limits(self):
        self.assertTrue(self.study.addTask(self.aTask))
        self.assertFalse(self.study.addTask(self.bTask)) # study is full already
        self.assertFalse(self.study.addTask(self.aTask)) # already has this id
        self.assertFalse(self.incidents.addTask(self.aTask)) # fails because study already has this id
        self.assertTrue(self.study.addTask(self.bTask, True)) # does not fail due to force flag
        
    def test_no_limits(self):
        self.assertTrue(self.unlimited.addTask(self.aTask))
        self.assertTrue(self.unlimited.addTask(self.bTask))
        self.assertTrue(self.unlimited.addTask(self.cTask))
        self.assertTrue(self.unlimited.addTask(self.dTask))
        
class TestValuestreams(TestCase):
    def setUp(self):
        self.incidents = models.PkWorkPhases.objects.create(name="incidents", capacity=2)
        self.study = models.PkWorkPhases.objects.create(name="study", capacity=1)
        self.assigment = models.PkWorkPhases.objects.create(name="assigment", capacity=2)
        self.review = models.PkWorkPhases.objects.create(name="review", capacity=1)
        self.aTask = models.PkTask.objects.create(name="Task a", effort=0)
        self.aTask.initialize()
        self.bTask = models.PkTask.objects.create(name="Task b", effort=0)
        self.bTask.initialize()
        self.cTask = models.PkTask.objects.create(name="Task c", effort=0)
        self.cTask.initialize()
        self.dTask = models.PkTask.objects.create(name="Task d", effort=0)
        self.dTask.initialize()
        self.incidentStream = models.PkValuestream.objects.create(streamname="incidents")
        self.studyStream = models.PkValuestream.objects.create(streamname="study")
        self.assigmentStream = models.PkValuestream.objects.create(streamname="assigments")
        self.incidentStream.addPhase(self.incidents)
        self.studyStream.addPhase(self.study)
        self.assigmentStream.addPhase(self.assigment)
        self.assigmentStream.addPhase(self.review)
    
    def test_smallstream(self):
        self.incidentStream.nextPhase(self.aTask)
        items = len(models.PkWipTasks.objects.filter(task = self.aTask))
        #print "number of items: %d" % items
        self.assertTrue(items == 1)
        # retrieve the aTask from database so that we can verify the operation including
        # storage
        aaTask = models.PkTask.objects.get(pk=self.aTask.id)
        self.assertEqual(self.incidentStream, aaTask.valuestream)
        self.incidentStream.nextPhase(self.aTask) # steam end, we should be complete now
        self.assertTrue(self.aTask.isDone())
        # check that the change has propagated to database as well
        self.assertTrue(models.PkTask.objects.get(pk=self.aTask.id).isDone())
        items = len(models.PkWipTasks.objects.filter(task = self.aTask))
        self.assertTrue(items == 0)
        # do not accept completed tasks:
        with self.assertRaises(models.TaskAlreadyCompleted):
            self.studyStream.nextPhase(self.aTask)
        # check limits
        self.studyStream.nextPhase(self.bTask)
        with self.assertRaises(models.WipLimitReached):
            self.studyStream.nextPhase(self.cTask )
        # check that once we have started in one stream we cannot switch to another
        with self.assertRaises(models.TaskNotInThisStream):
            self.incidentStream.nextPhase(self.bTask)
        
    def test_mediumstream(self):
        self.assigmentStream.nextPhase(self.aTask)
        self.assigmentStream.nextPhase(self.bTask)
        with self.assertRaises(models.WipLimitReached):
            self.assigmentStream.nextPhase(self.cTask)
        self.assigmentStream.nextPhase(self.aTask)
        items = models.PkWipTasks.objects.filter(task = self.aTask)
        self.assertTrue(len(items) == 1)
        self.assertTrue(items[0].phase == self.review)
        self.assigmentStream.nextPhase(self.cTask)
        items = models.PkWipTasks.objects.filter(task = self.cTask)
        self.assertTrue(len(items) == 1)
        self.assertTrue(items[0].phase == self.assigment)
    
    def test_shared_phase(self):
        self.incidentStream.addPhase(self.review)
        self.incidentStream.nextPhase(self.aTask)
        self.incidentStream.nextPhase(self.aTask)
        self.assigmentStream.nextPhase(self.bTask)
        with self.assertRaises(models.WipLimitReached):
            self.assigmentStream.nextPhase(self.bTask)
        self.assertTrue(self.aTask.valuestream == self.incidentStream)
        self.assertTrue(self.bTask.valuestream == self.assigmentStream)
        with self.assertRaises(models.TaskNotInThisStream):
            self.assigmentStream.nextPhase(self.aTask)
        with self.assertRaises(models.TaskNotInThisStream):
            self.incidentStream.nextPhase(self.bTask)

def suite():
    taskSuite = unittest.TestLoader().loadTestsFromTestCase(TestPktask)
    phaseSuite = unittest.TestLoader().loadTestsFromTestCase(TestPhases)
    streamSuite = unittest.TestLoader().loadTestsFromTestCase(TestValuestreams)
    return unittest.TestSuite([taskSuite, phaseSuite, streamSuite])
