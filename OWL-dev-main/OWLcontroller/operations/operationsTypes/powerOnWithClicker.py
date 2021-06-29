import os
from operations.operation import operation
PING = 'ping '
SHUTDOWN_COMMAND = "shutdown /s /t 1"

class powerOnWithClicker(operation):
    CLICKER_CHANNEL_COMMANDS ={1 : ('1', 'q'),
                             2 : ('2', 'w'),
                             3 : ('3', 'e'),
                             4 : ('4', 'r')}
    def getKey(self):
        ''' Returns operation's name '''
        return (type(self).__name__)

    @staticmethod
    def PCOnAfterTest():#well the pc be on after test finishes
        return True

    @staticmethod
    def asumesPcOnBeforeTest():#does the test asumes the pc well be on before runing
        return False

    def runOp(self,controllerPc,hostPc,testLog,opParams):
        controllerPc.updateTerminalAndLog(hostPc, testLog, "\n Power on with clicker has started")
        # hostPcIsOFf = operation.waitForPcToTurnOff(self,controllerPc,hostPc,testLog)
        # if hostPcIsOFf:
        controllerPc.updateTerminalAndLog(hostPc, testLog, "\nActivate Clicker")
        try:#TODO look at this
            os.system("mode " + hostPc['clicker']['COM'] + " BAUD=9600 PARITY=n DATA=8")
            os.system("echo " + powerOnWithClicker.CLICKER_CHANNEL_COMMANDS[hostPc['clicker']['chanel']][0] +
                          " > " + hostPc['clicker']['COM'])
            os.system("echo " + powerOnWithClicker.CLICKER_CHANNEL_COMMANDS[hostPc['clicker']['chanel']][1] +
                          " > " + hostPc['clicker']['COM'])
        except Exception as e:#TODO look at this
            print ("\n Exception occurred while handling the values provided for Clicker/chanel, Exception message: " + str(e) ) #TODO look at this
            controllerPc.updateTerminalAndLog(hostPc, testLog,"\n Exception occurred while handling the values provided for Clicker/chanel, Exception message: " + str(e))
            return False
        hostPcIsOn = operation.waitForPcToTurnOn(self,controllerPc,hostPc,testLog)
        if hostPcIsOn:
            controllerPc.updateTerminalAndLog(hostPc, testLog, "\n System Under Test is On")
            controllerPc.updateTerminalAndLog(hostPc, testLog, "\n power On With Clicker done successfully")
        else:
            controllerPc.updateTerminalAndLog(hostPc, testLog, "\n System Under Test is Off\n power On With Clicker Failed")
        controllerPc.updateTerminalAndLog(hostPc, testLog, "\n Power on with clicker has ended")
        return hostPcIsOn # if the host is up the clicker done well, and should return True



