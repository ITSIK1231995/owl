import os

from operations.operation import operation
import json

from operations.operationWithSocket import operationWithSocket

PING = 'ping '
#SLEEP_COMMAND ="sleep command request from client"
# SLEEP_COMMAND = 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0'

class sleep(operationWithSocket):
    def getKey(self):
        pass


    def runOp(self,controllerPc,hostPc,opParams):
        print("\n sleep command has started \n ")
        port = controllerPc.configs.defaultConfContent['hostPcServerPort']
        socket = operationWithSocket.createCommunication(self, hostPc["IP"], port)
        messegeToServer = {"operation": "sleep"}
        socket.sendall(json.dumps(messegeToServer).encode('utf-8'))  # encode the dict to JSON
        socket.close()
        hostPcIsOff = operation.waitForPcToTurnOff(self, controllerPc, hostPc) # Verify the host is down
        print("\n sleep command has ended \n ")
        return hostPcIsOff