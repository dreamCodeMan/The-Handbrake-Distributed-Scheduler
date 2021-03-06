'''
Created on 23 Apr 2011

@author: Thomas Purchas
'''
from twisted.spread import pb
from twisted.internet.task import LoopingCall
import msvcrt

def GetKeys(service):

    try:
        while msvcrt.kbhit():
            msvcrt.getch()
            service.createJob(('test',))
            print 'Created job'
    except: raise

class HBServer(pb.Root):
    '''
    classdocs
    '''

    def __init__(self, service):

        self.service = service

        loop = LoopingCall(GetKeys, service)
        loop.start(0.5, True)

    def remote_getQueue(self, Client):

        return self.service.createQueue(Client)

    def remote_sendClient(self, Client):
        '''
        Do something useful
        @param Client:
        '''

        self.service.newClient(Client)

class HBQueue(pb.Referenceable):

    def __init__(self, Client, Jobs=None):

        self.client = Client

        if Jobs == None:
            self.jobs = []
        elif isinstance(Jobs, []):
            self.jobs = Jobs

        else:
            raise TypeError('Jobs must be a list')

    def addJob(self, Job):

        self.jobs.append(Job)
        self.client.callRemote("queueUpdate")

        Job.registerQueue(self)

    def removeJob(self, Job):

        try:
            self.jobs.remove(Job)
            self.Job.unregisterQueue()
        except:
            raise ValueError('That job is not in this list')

    def remote_getJobs(self):

        return self.jobs

class HBJob(pb.Referenceable):

    def __init__(self, service, Folder, name="Lazy!", args=["HandBrake"]):
        '''
        Create a new :class:`.HBJob`.
        
        :param Folder: The folder containing all the files for this job.
        :param Name: Give it a human friendly name.
        :param args: The args that need to be passed to HandBrake
        '''

        self.args = args
        self.folder = Folder
        self.name = name

        self.stage = 1
        self.percent = None
        self.speed = None
        self.eta = None

        self.service = service

        self.queue = None

    def registerQueue(self, Queue):

        if self.queue != None:
            raise Exception('We already have a Queue!')

        self.queue = Queue

    def unregisterQueue(self):

        if self.queue == None:
            raise Exception('There is no Queue registered!')

        self.queue = None

    def remote_serveFiles(self):

        return self.service.serveFiles(self.folder + '/input')

    def remote_returnFiles(self):

        return self.service.returnFiles(self.folder + '/output')

    def remote_getArgs(self):

        return self.args

    def remote_setStage(self, Stage):

        self.stage = Stage
        self.percent = None
        self.ea = None
        self.speed = None

    def remote_setPercentage(self, Percentage):

        self.percent = Percentage

    def remote_setETA(self, Time):

        self.eta = Time

    def remote_setSpeed(self, Speed):

        self.speed = Speed
