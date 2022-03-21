import multiprocessing as mproc
import argparse
import cv2

# Construct & parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--camport", type=int, default=0, required=False,
	help="Port number of camera (0 for built-in webcam)")
ap.add_argument("-tm", "--timeoutMP", type=int, default=5, required=False,
	help="Timeout for middle processes(es) (in seconds)")
ap.add_argument("-te", "--timeoutEP", type=int, default=5, required=False,
	help="Timeout for endpoint process(es) (in seconds)")

args = vars(ap.parse_args())

# Camera port adjustment
camPort = args['camport']

# Timeout interval specification in seconds
timeoutMP = args['timeoutMP']
timeoutEP = args['timeoutEP']

def readCamFrame(ns, event, camPort):
  # Initialize the video capture object
  cap = cv2.VideoCapture(camPort)
  while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        ns.frame = frame
        event.set()
        cv2.imshow('Original Frame', frame)
        # TODO: Make trigger condition outside
        # PRESS 'q' TO TERMINATE THE PROCESS WHEN THE WINDOW IS SELECTED
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            event.clear()
            print("readFrames event status: ", event.is_set())
            return 0
    else:
        return -1

# Middle Process Example Class
class MiddleProcess(mproc.Process):

    def __init__(self, name, nsInput, nsOutput, eventWait, eventPublish, timeOutSec):
        super(MiddleProcess, self).__init__()
        
        # Specify a name for the instance
        self.name = name
        
        # Input and output namespaces
        self.nsInput = nsInput
        self.nsOutput = nsOutput

        # Waiter and publisher events
        self.eventWait = eventWait
        self.eventPublish = eventPublish

        # Specify timeout in seconds
        self.timeOutSec = timeOutSec

    def run(self):

        while True:
            print("MiddleProcess", self.name, "event status: ", self.eventPublish.is_set())
            moveOn = self.eventWait.wait(timeout=self.timeOutSec)
            if moveOn:
                # TODO: Make trigger condition outside
                # PRESS 'w' TO TERMINATE THE PROCESS WHEN THE WINDOW IS SELECTED
                if cv2.waitKey(1) & 0xFF == ord('w'):
                    '''
                    
                    ------------ Do your TERMINATION OPERATIONS here ------------

                    '''
                    cv2.destroyAllWindows()
                    self.eventPublish.clear()
                    print("MiddleProcess", self.name, "event status: ", self.eventPublish.is_set())
                    return 0

                img = self.nsInput.frame

                cv2.imshow('MiddleProcess Copied Frame: '+self.name, img)
                '''
                
                ------------ Do your MAGIC here ------------
                
                '''
                self.nsOutput.frame = img

                # Publish your "event"
                self.eventPublish.set()

            else:
                '''
                
                ------------ Do your TERMINATION OPERATIONS here TOO ------------
                
                '''
                print("TIMEOUT EXCEEDED FOR", self.name, "!")
                cv2.destroyAllWindows()
                self.eventPublish.clear()
                print("MiddleProcess", self.name, "event status: ", self.eventPublish.is_set())
                return -1


## Process class'larinin olusturulmasi:
# Process olusturma normalde fonksiyonlar ile de yapilabilir.
# Siniflarin kendi iclerinde parametrelerini tutabilmeleri icin yeni siniflar olusturup Process subclass'i olarak
# tanimlamak bize daha fazla esneklik sunacaktir.

# Endpoint Process Example Class
class EndpointProcess(mproc.Process):

    def __init__(self, name, nsInput, nsOutput, eventWait, eventPublish, timeOutSec):
        super(EndpointProcess, self).__init__()

        # Specify a name for the instance
        self.name = name

        # Input and output namespaces
        self.nsInput = nsInput
        self.nsOutput = nsOutput

        # Waiter and publisher events
        self.eventWait = eventWait
        self.eventPublish = eventPublish

        # Specify timeout value in seconds
        self.timeOutSec = timeOutSec

    def run(self):
        while True:
            print("EndpointProcess", self.name, "event status: ", self.eventPublish.is_set()) 
            # Wait for the event within timeout   
            moveOn = self.eventWait.wait(timeout=self.timeOutSec)
            if moveOn:
                print("EndpointProcess", self.name, "event status: ", self.eventPublish.is_set())       
                frame = self.nsInput.frame
                '''
                
                ------------ Do your MAGIC here ------------
                
                '''
                # TODO: Make trigger condition outside
                # PRESS 'e' TO TERMINATE THE PROCESS WHEN THE WINDOW IS SELECTED
                cv2.imshow('EndpointProcess Frame: '+str(self.name) , frame)

                if cv2.waitKey(1) & 0xFF == ord('e'):
                    '''
                    
                    ------------ Do your TERMINATION OPERATIONS here ------------

                    '''
                    cv2.destroyAllWindows()
                    self.eventPublish.clear()
                    print("EndpointProcess", self.name, "event status: ", self.eventPublish.is_set())
                    
                    return 0

                # Publish your "event"
                self.eventPublish.set()

            # Terminate the loop if timeout exceeds the specified value 
            else:
                '''
                    
                ------------ Do your TERMINATION OPERATIONS here TOO ------------

                '''
                print("TIMEOUT EXCEEDED FOR", self.name, " !")
                cv2.destroyAllWindows()
                self.eventPublish.clear()
                print("BozEtm Process", self.name, "event status: ", self.eventPublish.is_set())

                return -1

if __name__=="__main__":

    # Creating a Manager instance to administrate processes
    mgr = mproc.Manager()
    # Creating a Namespace instance to make the processes publish/consume correct data variables
    nsFrame = mgr.Namespace()
    nsMP = mgr.Namespace()
    nsBozEtm = mgr.Namespace()

    # Creating Event instances to handle triggers
    eventFP = mproc.Event()
    eventMP = mproc.Event()
    eventEP = mproc.Event()

    # Instantiate camera capture process
    camCap = mproc.Process(name='camCap', target=readCamFrame, args=(nsFrame, eventFP, camPort, ))
    camCap.daemon=True

    # Instantiate middle process
    mpCap = MiddleProcess('mpCap', nsInput=nsFrame, nsOutput=nsMP, eventWait=eventFP, eventPublish=eventMP, timeOutSec=timeoutMP, )
    mpCap.daemon=True

    # Endpoint process instantiation, connected to desired namespace & events
    eProc_0 = EndpointProcess('eProc_0', nsInput=nsMP, nsOutput=nsBozEtm, eventWait=eventMP, eventPublish=eventEP, timeOutSec=timeoutEP, )
    eProc_0.daemon=True
    #'''
    eProc_1 = EndpointProcess('eProc_1', nsInput=nsMP, nsOutput=nsBozEtm, eventWait=eventMP, eventPublish=eventEP, timeOutSec=timeoutEP, )
    eProc_1.daemon=True

    eProc_2 = EndpointProcess('eProc_2', nsInput=nsMP, nsOutput=nsBozEtm, eventWait=eventMP, eventPublish=eventEP, timeOutSec=timeoutEP, )
    eProc_2.daemon=True

    eProc_3 = EndpointProcess('eProc_3', nsInput=nsMP, nsOutput=nsBozEtm, eventWait=eventMP, eventPublish=eventEP, timeOutSec=timeoutEP, )
    eProc_3.daemon=True

    eProc_4 = EndpointProcess('eProc_4', nsInput=nsMP, nsOutput=nsBozEtm, eventWait=eventMP, eventPublish=eventEP, timeOutSec=timeoutEP, )
    eProc_4.daemon=True
    #'''
    # Starting the processes
    camCap.start()
    mpCap.start()

    eProc_0.start()
    #'''
    eProc_1.start()
    eProc_2.start()
    eProc_3.start()
    eProc_4.start()
    #'''

    # Join all processes to the main process for guaranteeing no hanging thread will be left
    camCap.join()
    mpCap.join()

    eProc_0.join()
    #'''
    eProc_1.join()
    eProc_2.join()
    eProc_3.join()
    eProc_4.join()
    #'''
