import datetime
import os
import threading
from collections import namedtuple
from UI.GUI.teststate import testState
from operations.allOperations import allOperations
import logging

class hostPcTestsRunner():
    def __init__(self, controllerPc, hostPc):
        self.controllerPc = controllerPc
        self.hostPc = hostPc
        self.testToRun = self.getRelevantTestForHostPc()
        self.threadLock = threading.Lock()
        logging.info("HostPc worker thread " + hostPc["IP"] + " started")

    def getRelevantTestForHostPc(self):
        allTests = self.controllerPc.configs.legacyMode.legacyFlowOperationsTestsByGroups[self.hostPc["groupName"]]
        relevantTests = []
        for test in allTests:
            if test.testname in self.hostPc["tests"].keys() and \
                    self.hostPc["tests"][test.testname]['checked']:
                relevantTests.append(test)
        return relevantTests

    def printToLog(self, text):
        logging.info(("worker thread", self.hostPc["IP"], text))

    def getCurrentTime(self):
        now = datetime.datetime.now()
        return str(now.strftime("%Y-%m-%d %H:%M:%S").replace("-", "_").replace(":", "_"))

    def createLog(self, test):
        self.threadLock.acquire()
        timeStamp = self.getCurrentTime()
        logPath = self.controllerPc.configs.defaultConfContent["resultPath"] + "\\" + test.results[:-1]
        self.resultFilePath = logPath + "\\" + test.testname + "__" + self.hostPc["IP"] + "__" + timeStamp
        fileName = self.resultFilePath + "\\" + "terminal.log"
        if not os.path.exists(fileName):
            os.makedirs(self.resultFilePath)
            logObj = open(fileName, "w")
        else:
            logObj = open(fileName, "a")
        self.threadLock.release()
        return logObj

    def updateUiAndControllerWithTestStatuses(self,test,numOfPass,numOfFails):
        self.controllerPc.runtimeHostPcsData[self.hostPc["IP"]][test.testname] = \
            {"testRepeatsCurrStatus": testState.RUNNING,
             "testRepeatsSummary": {testState.PASSED: numOfPass, testState.FAILED: numOfFails}}
        self.controllerPc.updateTestStatusInRunTime(self.hostPc, test)

    def updateUiAndControlleWithTestStatusrAfterEachRepat(self,test,numOfPass,numOfFails,repeat):
        self.controllerPc.runtimeHostPcsData[self.hostPc["IP"]][test.testname] = \
            {"testRepeatsCurrStatus": testState.RUNNING if repeat < self.hostPc["tests"][test.testname]['repeatAmount'] - 1 else testState.FINISHED,
             # if we did not finished all the repeats we the state will be running otherwise it'll be according to the results
             "testRepeatsSummary": {testState.PASSED: numOfPass, testState.FAILED: numOfFails}}
        self.controllerPc.updateTestStatusInRunTime(self.hostPc, test)

    def updateUiAndContollerWithHostdata(self,hostCurrState):
        self.controllerPc.runtimeHostPcsData[self.hostPc["IP"]]["hostPcLblColor"] = hostCurrState
        self.controllerPc.updateUiWithHostNewStatus(self.hostPc)

    def getRecordOptionFilePath(self,test):
        return os.getcwd() + "\\" + test.recordingoptions

    def getSavedTraceFullPath(self):
        return os.getcwd() + "\\" + self.resultFilePath

    def getTraceFullPathAndName(self,test):
        return self.getSavedTraceFullPath() + "\\" + test.testname + "_ " + self.getCurrentTime() +".pex"

    def getVSEFullPathAndName(self,test):
        return os.getcwd() + "\\" + test.verificationscript

    def runAllTests(self):
        self.printToLog("starting running tests")
        stopOnFailure = self.hostPc['stopOnFailure']
        hostFinalStatus = testState.PASSED  # if True host final session status is pass , otherwise host final session status is fail
        for test in self.testToRun:
            numOfPass = 0
            numOfFails = 0
            self.updateUiAndControllerWithTestStatuses(test,numOfPass,numOfFails)
            self.updateUiAndContollerWithHostdata(testState.RUNNING)
            self.printToLog("starting test= " + test.testname)
            for repeat in range(self.hostPc["tests"][test.testname]['repeatAmount']):  # repeat tests according to repeatAmount
                testLog = self.createLog(test)
                self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, testLog, "\n" + test.testname + " Has started ")
                analyzerHandler = self.controllerPc.createAnalyzerInstance()
                self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, testLog,"\n Lecroy's Analyzer recording procedure has started")
                traceFullPathAndName = self.getTraceFullPathAndName(test)
                self.controllerPc.startRecordingWithAnalyzer(analyzerHandler, traceFullPathAndName,self.getRecordOptionFilePath(test),self.hostPc, testLog)
                sequenceOfOperationsIsDone = self.runSequanceOfOperations(test, self.controllerPc, testLog)
                self.controllerPc.stopRecordingWithAnalyzer(analyzerHandler)
                self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, testLog,"\n Lecroy's Analyzer recording procedure has finished")
                verificationScriptResult = self.controllerPc.startVSE(traceFullPathAndName, self.getVSEFullPathAndName(test),self.hostPc, testLog)
                if sequenceOfOperationsIsDone and verificationScriptResult == 1: # verificationScriptResult == 1 is the value that Lecroy's API returns from VSE when the VSE has passed.
                    numOfPass += 1
                    self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, testLog, "\n" + test.testname + " Has Passed")
                else:
                    numOfFails += 1
                    hostFinalStatus = testState.FAILED  # if one test has failed in the Host's session of tests its enough to mark this session for this host has a session that failed
                    self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, testLog, "\n" + test.testname + " Has Failed")
                testLog.close()
                self.updateUiAndControlleWithTestStatusrAfterEachRepat(test,numOfPass,numOfFails,repeat)
                if self.controllerPc.haltThreads:
                    break
            if stopOnFailure and numOfFails >= 1:  # Stop on failure is on
                break
            self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, None,"\n >>> Passed: " + str(numOfPass) + " Failed:" + str(numOfFails) + "\n")
            self.printToLog("finished test= " + test.testname)
            if self.controllerPc.haltThreads:
                self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, None, "Testing stopped")
                self.printToLog("Halting")
                break
        self.updateUiAndContollerWithHostdata(hostFinalStatus)
        self.printToLog("Finished running tests")

    def getOprationObject(self,operation): #TODO need to put this function and the same one from validator in one place for not duplicating the code
        opraion = namedtuple('opraion', ['name', 'opraionObj'])
        mappedOperations = allOperations()
        if isinstance(operation, dict):
            return opraion(operation['name'], mappedOperations.operationsImplementation[operation['name']])
        if isinstance(operation, str):
            return opraion(operation, mappedOperations.operationsImplementation[operation])

    def runSequanceOfOperations(self, test, controllPc, testLog): #TODO need to remove ControlPC and
        for operation in test.flowoperations:
            if isinstance(operation, dict):
                self.printToLog("starting Operations= " + operation['name'])
                operationOutPut = self.getOprationObject(operation).opraionObj.runOp(self,self.controllerPc,self.hostPc,testLog, operation['params']) #TODO  need to  delete to if isisntace in this function and than just use inline if when we have params that the run OP is getting (if the function has param we sending it and if not we arent
                if not operationOutPut:
                    self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, testLog, (operation['name'] + " Op failed"))
                    self.printToLog("finished Operations= " + operation['name'] + ", Op failed")
                    return False
                self.printToLog("finished Operations= " + operation['name'] + ", Op succeeded")
            elif isinstance(operation, str):
                self.printToLog("starting Operations= " + operation)
                operationOutPut = self.getOprationObject(operation).opraionObj.runOp(self, self.controllerPc,self.hostPc, testLog, [])
                if not operationOutPut:
                    self.controllerPc.updateRunTimeStateInTerminal(self.hostPc, testLog, (operation + " Op failed"))
                    self.printToLog("finished Operations= " + operation + ", Op failed")
                    return False
                self.printToLog("finished Operations= " + operation + ", Op succeeded")
        return True
