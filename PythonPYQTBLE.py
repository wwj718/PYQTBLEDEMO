
import PyQt5
from PyQt5 import QtCore
from PyQt5 import QtBluetooth



class Deviceinfo(QtCore.QObject):
    devicechanged = PyQt5.QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.m_device = QtBluetooth.QBluetoothDeviceInfo()
        self.devicechanged.connect(self.emitDeviceChanged)

    def getName(self):
        return self.m_device.name()

    def getAddress(self):
        return self.m_device.address().toString()

    # 设备改变的信号触发函数，用于更新界面等功能
    def emitDeviceChanged(self):
        pass

    def setDevice(self, device):
        self.m_device = device
        self.devicechanged.emit()



class BleInterface(QtCore.QObject):
    #signals
    statusInfoChanged = QtCore.pyqtSignal(str , bool)
    dataReceved = QtCore.pyqtSignal(PyQt5.QtCore.QByteArray)
    connectedChanged = QtCore.pyqtSignal(bool)
    currengServiceChanged = QtCore.pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.m_devodeDoscoveryAgent = QtBluetooth.QBluetoothDeviceDiscoveryAgent()
        self.m_notificationDesc = QtBluetooth.QLowEnergyDescriptor()
        self.m_control = None
        #self.m_servicesUuid = QtBluetooth.QBluetoothUuid()
        self.m_servicesUuid = []    #用于存放设备的服务的UUID
        self.m_service = QtBluetooth.QLowEnergyService    #用于存放设备具体使用的服务
        self.m_readCharacteristic = QtBluetooth.QLowEnergyCharacteristic()  #用于存放读取的服务的特性内容
        self.m_writeCharacteristic = QtBluetooth.QLowEnergyCharacteristic() #用于存放写入的服务的特性内容
        self.m_devices = list(Deviceinfo) #用于存放获取的设备列表
        self.m_writemode = QtBluetooth.QLowEnergyService.WriteMode()
        self.m_readTimer = QtCore.QTimer()

        self.m_connected=bool
        self.m_devicesNames = []
        self.m_services = []
        self.m_currentDevice = None
        self.m_currentService = None



        #初始化相关变量
        self.m_connected(False)
        #self.m_control(None)
        #self.m_readTimer(None)
        #self.m_currentService(None)
        #self.m_currentDevice(None)

        #绑定设备发现相关信号函数
        self.m_devodeDoscoveryAgent.setLowEnergyDiscoveryTimeout(500)
        self.m_devodeDoscoveryAgent.deviceDiscovered.connect(self.addDevice)
        self.m_devodeDoscoveryAgent.error.connect(self.onDeviceScanError)
        self.m_devodeDoscoveryAgent.finished.connect(self.onScanFinished)
        self.m_devodeDoscoveryAgent.canceled.connect(self.onScanFinished)

    def scanDevices(self):
        self.m_devices.clear()
        self.m_devodeDoscoveryAgent.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod(2))
        print("Scanning for devices...")

    def read(self):
        if(self.m_service and self.m_readCharacteristic.isValid()):
            self.m_service.characteristicRead(self.m_readCharacteristic)
        
    def write(self,data=bytearray()):
        print("BLEInterface write :{datawrite}".format(datawrite=data))
        if(self.m_service and self.m_writeCharacteristic.isValid()):
            if(len(data) > 20):
                sentBytes = 0
                while sentBytes < len(data):
                    self.m_service.writeCharacteristic(self.m_writeCharacteristic,data[sentBytes:sentBytes + 20],self.m_writemode)
                    sentBytes+=20
                    if self.m_writemode == QtBluetooth.QLowEnergyService.WriteWithResponse:
                        pass
                        if self.m_service.error() != QtBluetooth.QLowEnergyService.NoError:
                            return
            else:
                self.m_service.writeCharacteristic(self.m_writeCharacteristic,data,self.m_writemode)
    
    def addDevice(self, device):
        if device.coreConfigurations() and QtBluetooth.QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
            self.m_devices.append(QtBluetooth.QBluetoothDeviceInfo(device))
            print("Discovered LE Device name: {name} ,Address: {address} ".format(name=device.name(),address=device.address().toString()))
            print("Low Energy device found. Scanning more...")


    def onScanFinished(self):
        if len(self.m_devices) == 0:
            print("Scan finished")
    
    def onDeviceScanError(self,error):
        if error == QtBluetooth.QBluetoothDeviceDiscoveryAgent.PoweredOffError:
            print("The Bluetooth adaptor is powered off power it on before discovery")
        elif error == QtBluetooth.QBluetoothDeviceDiscoveryAgent.InputOutputError:
            print("Writing or reading from the device resulted in an error")
        else:
            print("An unknown error has occurred")

    def connectCurrentDevice(self):
        if len(self.m_devices) == 0:
            return
        if self.m_control:
            self.m_control.disconnectFromDevice()
            self.m_control = None
        self.m_control = QtBluetooth.QLowEnergyController(self.m_devices[self.m_currentDevice].getDevice())
        self.m_control.serviceDiscovered.connect(self.onServiceDiscovered)
        self.m_control.discoveryFinished.connect(self.onServiceScanDone)
        self.m_control.error.connect(self.onControllerError)
        self.m_control.connected.connect(self.onDeviceConnected)
        self.m_control.disconnected.connect(self.onDeviceDisconnected)
        self.m_control.connectToDevice()
    
    def onDeviceConnected(self):
        self.m_servicesUuid.clear()
        self.m_services.clear()
        self.setCurrentService(-1)
        self.serviceChanged.emit(self.m_services)
        self.m_control.discoverServices()

    def onDeviceDisconnected(self):
        #update_connected(false)
        self.statusInfoChanged.emit("Device disconnected",false)
        print("Remote device disconnected")
       
    def onServiceDiscovered(gatt=QtBluetooth.QBluetoothUuid()):
         self.statusInfoChanged.emit("Service discovered. Waiting for service scan to be done...", true)

    def onServiceScanDone(self):
        self.m_servicesUuid = self.m_control.services()
        if m_servicesUuid.isEmpty():
            self.statusInfoChanged.emit("Can't find any services.", true)
        else:
            self.m_services.clear()
            for uuid in self.m_servicesUuid:
                self.m_services.append(uuid.toString())
            self.servicesChanged.emit(self.m_services)
            self.m_currentService = -1
            setCurrentService(0)
            self.statusInfoChanged.emit("All services discovered.", true)

    def disconnectDevice(self):
        self.m_readTimer.deleteLater()
        self.m_readTimer=None
        if self.m_devices.isEmpty():
            return
        if self.m_notificationDesc.isValid()and self.m_serivce:
            self.m_service.writeDescriptor(self.m_notificationDesc,bytearray(0,0))
        else:
            self.m_control.disconnectFromDevice()
            self.m_service = None

    def onControllerError(self,error=QtBluetooth.QLowEnergyController.error):
        self.statusInfoChanged.emit("Cannot connect to remote device.", false)
        print("Controller Error")

    def onCharacteristicChanged(self,chara=QtBluetooth.QLowEnergyCharacteristic,value=bytearray):
        print("Characteristic Changed {values}",values=value)
        self.dataReceived.emit(value)

    def onCharacteristicWrite(self,c=QtBluetooth.QLowEnergyCharacteristic,value=bytearray):
        print("characteristic Written: {values}",values=value)


    def onCharacteristicRead(self,c=QtBluetooth.QLowEnergyCharacteristic,value=bytearray):
        print("Characteristic Read:  {values}",values=value)


    def update_currentService(self,indx=int):
        self.m_service = None
        if indx>=0 and self.m_servicesUuid.count()>indx:
           self.m_service = self.m_control.createServiceObject(self.m_servicesUuid.at(indx),this)
        if not m_service:
            self.statusInfoChanged("Service not found.", false)
            return
        self.m_service.stateChanged(QtBluetooth.QLowEnergyService.ServiceState).connect(self.onServiceStateChanged(QtBluetooth.QLowEnergyService.ServiceState))
        self.m_service.characteristicChanged(QtBluetooth.QLowEnergyCharacteristic,bytearray).connect(self.onCharacteristicChanged(QtBluetooth.QLowEnergyCharacteristic,bytearray))
        self.m_service.characteristicRead(QtBluetooth.QLowEnergyCharacteristic,bytearray).connect(self.onCharacteristicRead(QtBluetooth.QLowEnergyCharacteristic,bytearray))
        self.m_service.characteristicWritten(QtBluetooth.QLowEnergyCharacteristic,bytearray).connect(self.onCharacteristicWrite(QtBluetooth.QLowEnergyCharacteristic,bytearray))
        self.m_service.error(QtBluetooth.QLowEnergyService.ServiceError).connect(self.serviceError(QtBluetooth.QLowEnergyService.ServiceError))

    def searchCharacteristic(self):
        if self.m_service:
            for c in self.m_service.characteristics:
                if c.isValid():
                    if c.properties() & QtBluetooth.QLowEnergyCharacteristic.WriteNoResponse or c.properties() & QtBluetooth.QLowEnergyCharacteristic.Write:
                        self.m_writeCharacteristic = c
                        update_connected(True)
                        if c.properties()and QtBluetooth.QLowEnergyCharacteristic.WriteNoResponse:
                            self.m_writemode=QtBluetooth.QLowEnergyService.WriteWithoutResponse
                        else:
                           self.m_writemode=QtBluetooth.QLowEnergyService.WriteWithResponse
                    if c.properties() & QtBluetooth.QLowEnergyCharacteristic.Read:
                        self.m_readCharacteristic=c
                        if not m_readTimer:
                            self.m_readTimer=QtCore.QTimer(this)
                            self.m_readTimer.timeout.connect(self.read)
                            self.m_readTimer.start(3000)
                    self.m_notificationDesc = c.descriport(QtBluetooth.QBluetoothUuid.ClientCharacteristicConfiguration)
                    if m_notificationDesc.isValid():
                        self.m_service.writeDescriptor(m_notificationDesc,QtCore.QByteArray.fromHex("0110"))



    def onServiceStateChanged(s=QtBluetooth.QLowEnergyService.ServiceState):
        print("service state changed , state: {state}",state=s )
        if s == QtBluetooth.QLowEnergyService.ServiceDiscovered:
            searchCharacteristic()

    def serviceError(e=QtBluetooth.QLowEnergyService.ServiceError):
        print("Service error: {error}",error = e)

class DeviceFinder(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.m_devices = []

        self.deviceDiscoveryAgent = QtBluetooth.QBluetoothDeviceDiscoveryAgent(self)
        self.deviceDiscoveryAgent.setLowEnergyDiscoveryTimeout(500)
        self.deviceDiscoveryAgent.deviceDiscovered.connect(self.add_device)
        self.deviceDiscoveryAgent.error.connect(self.scan_error)
        self.deviceDiscoveryAgent.finished.connect(self.scan_finished)
        self.deviceDiscoveryAgent.canceled.connect(self.scan_finished)

        self.deviceDiscoveryAgent.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod(2))

    def add_device(self, device):
        # If device is LowEnergy-device, add it to the list
        if device.coreConfigurations() and QtBluetooth.QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
            self.m_devices.append(QtBluetooth.QBluetoothDeviceInfo(device))
            print("Low Energy device found. Scanning more...")

    def scan_finished(self):
        print("scan finished")
        for i in self.m_devices:
            # QtBluetooth.QBluetoothDeviceInfo.
            print('UUID: {UUID}, Name: {name}, rssi: {rssi}'.format(UUID=i.deviceUuid().toString(),
                                                                    name=i.name(),
                                                                    rssi=i.rssi()))

        # self.quit()

    def scan_error(self):
        print("scan error")

    def connectToService(self, address):
        self.deviceDiscoveryAgent.stop()

    def quit(self):
        print("Bye!")
        QtCore.QCoreApplication.instance().quit()


if __name__ == "__main__":
    import sys

    app = QtCore.QCoreApplication(sys.argv)
    hello = BleInterface()
    # sys.exit(app.exec_())
    app.exec_()
