 # -*- coding: utf-8 -*-
# !/usr/bin/env python3


from PyQt5.QtCore import QObject, QUuid, pyqtSignal

#from Connection import *
from Serializable import *
from Node import *
from PortType import *
from ConnectionGeometry import *
from ConnectionState import *
from NodeGraphicsObject import *
from ConnectionGraphicsObject import *

# namespace std
# {
# template<>
# struct hash<QUuid>
# {
#   inline
#   std::size_t
#   operator()(QUuid const& uid) const
#   {
#     return qHash(uid);
#   }
# };
# }

##----------------------------------------------------------------------------
class Connection(QObject, Serializable):
    
    def __init__(self, *args):
        QObject.__init__(self)  
  
        self._inNode = None
        self._outNode = None
        self._connectionGeometry = ConnectionGeometry()
        #_connectionGraphicsObject = ConnectionGraphicsObject()    
        #Node = Node()

        # method overload
        signature = tuple(arg.__class__ for arg in args)
        
        import Node
        NodeCls = Node.Node

        typemap = {(PortType, NodeCls, PortIndex) : self.connectionPorts,
                    (Node, PortIndex, NodeCls, PortIndex) : self.connectionNodes }
    
       
        if signature in typemap:
            return typemap[signature](*args)
        else:
            raise TypeError("Invalid type signature: {0}".format(signature))

    #-------------------------------------------------------------------------
    def connectionPorts(self, portType, node, portIndex):
        self._id = QUuid.createUuid()
        self._outPortIndex = PortType.INVALID
        self._inPortIndex = PortType.INVALID
        self._connectionState = ConnectionState() 
        
        self.setNodeToPort(node, portType, portIndex)
        self.setRequiredPort(oppositePort(portType))

    #-------------------------------------------------------------------------
    def connectionNodes(self, nodeIn, PortIndexIn, nodeOut, portIndexOut):
        self._id = QUuid.createUuid()

        
        self._outNode = Node(nodeOut)
        self._inNode = Node(nodeIn)
        self._outPortIndex = portIndexOut
        self._inPortIndex = portIndexIn
        self._connectionState = ConnectionState()
        
        self.setNodeToPort(nodeIn, portType.In, portIndexIn)
        self.setNodeToPort(nodeOut, portType.Out, portIndexOut)

    #-------------------------------------------------------------------------
    def __del__(self):
#        curframe = inspect.currentframe()
#        calframe = inspect.getouterframes(curframe, 2)
#        print('caller name:', calframe[1][3])
#        print('on:', calframe[1][1])


        self.propagateEmptyData()

        if(not self._inNode is None):

            self._inNode.nodeGraphicsObject().update()

        if(not self._outNode is None):

            self._outNode.nodeGraphicsObject().update()

#        print("Connection destructor")

    #-------------------------------------------------------------------------
    def save(self) -> dict:

        connectionJson = dict()

        if( (not self._inNode is None) and (not self._outNode is None) ):

            connectionJson["in_id"] = self._inNode.id().toString()

            connectionJson["in_index"] = self._inPortIndex

            connectionJson["out_id"] = self._outNode.id().toString()

            connectionJson["out_index"] = self._outPortIndex

        return connectionJson
  
    #-------------------------------------------------------------------------
    def id(self) -> QUuid:
        return self._id

    #-------------------------------------------------------------------------
    def setRequiredPort(self, dragging):
        self._connectionState.setRequiredPort(dragging)

        if(dragging == PortType.Out):

            self._outNode = None

            self._outPortIndex = INVALID

        elif(dragging == PortType.In):

            self._inNode = None

            self._inPortIndex = INVALID

        else:

            Q_UNREACHABLE();

    #-------------------------------------------------------------------------
    def requiredPort(self):
        return self._connectionState.requiredPort()

    #-------------------------------------------------------------------------
    def setGraphicsObject(self, graphics: ConnectionGraphicsObject):        
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        #print('caller name:', calframe[1][3])

        self._connectionGraphicsObject = graphics

        # // This function is only called when the ConnectionGraphicsObject
        # // is newly created. At this moment both end coordinates are (0, 0)
        # // in Connection G.O. coordinates. The position of the whole
        # // Connection G. O. in scene coordinate system is also (0, 0).
        # // By moving the whole object to the Node Port position
        # // we position both connection ends correctly.

        if(self.requiredPort() != PortType.No_One):

            attachedPort = oppositePort(self.requiredPort())

            attachedPortIndex = self.getPortIndex(attachedPort)

            node = self.getNode(attachedPort)

            nodeSceneTransform =node.nodeGraphicsObject().sceneTransform()

            pos = node.nodeGeometry().portScenePosition(attachedPortIndex,
                                                        attachedPort,
                                                        nodeSceneTransform)

            self._connectionGraphicsObject.setPos(pos)

        self._connectionGraphicsObject.move()

    #-------------------------------------------------------------------------
    def getPortIndex(self, portType):

#        result = INVALID

        if(portType == PortType.In):

            return self._inPortIndex

        elif(portType == PortType.Out):

            return self._outPortIndex

        else:

            Q_UNREACHABLE();        

    #-------------------------------------------------------------------------
    def setNodeToPort(self, node, portType, portIndex):

#        nodeWeak = self.getNode(portType)
#        nodeWeak = node
        
        if(portType == PortType.In):            
            self._inNode = node        
        elif(portType == PortType.Out):            
            self._outNode = node        
        else:            
            Q_UNREACHABLE()
        
        
        if(portType == PortType.Out):
            self._outPortIndex = portIndex
        elif(portType == PortType.In):
            self._inPortIndex = portIndex
        else:
            Q_UNREACHABLE()

        self._connectionState.setNoRequiredPort()

        self.updated.emit(self)

    #-------------------------------------------------------------------------
    def removeFromNodes(self):
        if(self._inNode):
            self._inNode.nodeState().eraseConnection(PortType.In, self._inPortIndex, self.id())

        if(self._outNode):
            self._outNode.nodeState().eraseConnection(PortType.Out, self._outPortIndex, self.id())

    #-------------------------------------------------------------------------
    def getConnectionGraphicsObject(self):
        return self._connectionGraphicsObject       

    #-------------------------------------------------------------------------
    def connectionState(self):
        return self._connectionState

    #-------------------------------------------------------------------------
    def connectionGeometry(self):
        return self._connectionGeometry

    #-------------------------------------------------------------------------
    def getNode(self, portType):
        if(portType == PortType.In):
            return self._inNode
        elif(portType == PortType.Out):
            return self._outNode
        else:
            Q_UNREACHABLE();

    #-------------------------------------------------------------------------
    def clearNode(self, portType):
        self.getNode(portType)# = None

        if(portType == PortType.In):
            self._inPortIndex = INVALID
        elif(portType == PortType.Out):
            self._outPortIndex = INVALID
        else:
            Q_UNREACHABLE();

    #-------------------------------------------------------------------------
    def dataType(self):

        if(self._inNode):
            #print("_inNode")
            index = self._inPortIndex
            portType = PortType.In
            validNode = self._inNode
        elif(self._outNode):
            #print("_outNode")
            index = self._outPortIndex
            portType = PortType.Out
            validNode = self._outNode
        else:
            Q_UNREACHABLE();

        if(not validNode is None):
            model = validNode.nodeDataModel()
            
            return model.dataType(portType, index)

        Q_UNREACHABLE();

    #-------------------------------------------------------------------------
    def propagateData(self, nodeData):
        if(not self._inNode is None):
            self._inNode.propagateData(nodeData, self._inPortIndex)

    #-------------------------------------------------------------------------
    def propagateEmptyData(self):
        emptyData = NodeData()
        self.propagateData(emptyData)

    #-------------------------------------------------------------------------
    #signals

    #    def updated(self):
    #    Connection = None
    updated = pyqtSignal(object,  name="Connection")
#        updated.emit(self)

##----------------------------------------------------------------------------


 
