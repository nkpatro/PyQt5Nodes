# -*- coding: utf-8 -*-
# !/usr/bin/env python3



from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys
sys.path.insert(0, '/home/fmicheld/Workspace/PyQt/PyQt5Nodes/')
from PyQt5Nodes.NodeDataModel import *
from PyQt5Nodes.NodeData import *
from PyQt5Nodes.PortType import *

from DecimalData import *

class MathOperationDataModel(NodeDataModel):
    def __init__(self):
        super().__init__()
        
        self._number1 = None
        self._number2 = None
        
        self._result = None
        
        self.modelValidationState = NodeValidationState.WARNING
        self.modelValidationError = "Missing or incorrect inputs"
        
    #--------------------------------------------------------------------------
    @abstractmethod
    def __del__(self):
        pass    
    
    #--------------------------------------------------------------------------
    def nPorts(self,  portType: PortType):
        
        if(portType == PortType.In):
            result = 2
        else:
            result = 1
            
        return result
        
    #--------------------------------------------------------------------------
    def dataType(self,  portType: PortType, portIndex: PortIndex):
        return DecimalData().type()
        
    #--------------------------------------------------------------------------
    def outData(self, port: PortIndex):
        return self._result
    
    #--------------------------------------------------------------------------
    def setInData(self, data: NodeData,  portIndex: PortIndex):
        
        if(isinstance(data, NodeData) and not isinstance(data, DecimalData)):
            dataNumber = None
        elif(isinstance(data, DecimalData)):
            dataNumber = data
        
        if(portIndex == 0):
            self._number1 = dataNumber
        else:
            self._number2 = dataNumber
            
        self.compute()
    
    #--------------------------------------------------------------------------
    def validationState(self):
        return self.modelValidationState
        
    #--------------------------------------------------------------------------
    def validationMessage(self):
        return self.modelValidationError
        
    #--------------------------------------------------------------------------
    @abstractmethod
    def compute(self):
        pass
        
    #--------------------------------------------------------------------------
    def embeddedWidget(self):
        return None
