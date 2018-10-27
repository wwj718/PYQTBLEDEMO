
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
    def __init__(self):
        super().__init__()
        self.m_devodeDoscoveryAgent = QtBluetooth.QBluetoothDeviceDiscoveryAgent()
        self.m_notificationDesc = QtBluetooth.QLowEnergyDescriptor()
        self.m_control = QtBluetooth.QLowEnergyController()
        #self.m_servicesUuid = QtBluetooth.QBluetoothUuid()
        self.m_servicesUuid = []    #用于存放设备的服务的UUID
        self.m_service = QtBluetooth.QLowEnergyService()    #用于存放设备具体使用的服务
        self.m_readCharacteristic = QtBluetooth.QLowEnergyCharacteristic()  #用于存放读取的服务的特性内容
        self.m_writeCharacteristic = QtBluetooth.QLowEnergyCharacteristic() #用于存放写入的服务的特性内容
        self.m_devices = [] #用于存放获取的设备列表
        self.m_writemode = QtBluetooth.QLowEnergyService.WriteMode()
        self.m_readTimer = QtCore.QTimer()

        self.m_connected(False)
        self.m_control(0)
        self.m_readTimer(0)
        self.m_currentService(0)
        self.m_currentDevice(0)

        self.deviceDiscoveryAgent = QtBluetooth.QBluetoothDeviceDiscoveryAgent(self)
        self.deviceDiscoveryAgent.setLowEnergyDiscoveryTimeout(500)
        self.deviceDiscoveryAgent.deviceDiscovered.connect(self.addDevice)
        self.deviceDiscoveryAgent.error.connect(self.onDeviceScanError)
        self.deviceDiscoveryAgent.finished.connect(self.onScanFinished)
        self.deviceDiscoveryAgent.canceled.connect(self.onScanFinished)

    def scanDevices(self):
        self.m_devices.clear()
        self.deviceDiscoveryAgent.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod(2))
        print("Scanning for devices...")

    def read(self):
        if(self.m_service and self.m_readCharacteristic.isValid()):
            self.m_service.characteristicRead(self.m_readCharacteristic)
        
    def write(self,data=bytearray()):
        print("BLEInterface write :{datawrite}".format(datawrite=data))
        if(self.m_service and self.m_writeCharacteristic.isValid()):
            if(len(data)>20):
                sentBytes=0
                while sentBytes<len(data):
                    self.m_service.writeCharacteristic(self.m_writeCharacteristic,data[sentBytes:sentBytes+20],self.m_writemode)
                    sentBytes+=20
                    if self.m_writemode == QtBluetooth.QLowEnergyService.WriteWithResponse:
                        pass
                        if self.m_service.error()!= QtBluetooth.QLowEnergyService.NoError:
                            return
            else:
                self.m_service.writeCharacteristic(self.m_writeCharacteristic,data,self.m_writemode)
    
    def addDevice(self, device):
        if device.coreConfigurations() and QtBluetooth.QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
            self.m_devices.append(QtBluetooth.QBluetoothDeviceInfo(device))
            print("Discovered LE Device name: {name} ,Address: {address} ".format(name=device.name(),address=device.address().toString()))
            print("Low Energy device found. Scanning more...")


    def onScanFinished(self):
        if len(self.m_devices)==0:
            print("Scan finished")
    
    def onDeviceScanError(self,error):
        if error==QtBluetooth.QBluetoothDeviceDiscoveryAgent.PoweredOffError:
            print("The Bluetooth adaptor is powered off power it on before discovery")
        elif error == QtBluetooth.QBluetoothDeviceDiscoveryAgent.InputOutputError:
            print("Writing or reading from the device resulted in an error")
        else:
            print("An unknown error has occurred")

    def connectCurrentDevice(self):
        if len(self.m_devices)==0:
            return
        if self.m_control:
            self.m_control.disconnectFromDevice()
            self.m_control=None
        self.m_control = QtBluetooth.QLowEnergyController(self.m_devices[self.m_currentDevice].getDevice())
        





class DeviceFinder(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.m_devices = []

        self.deviceDiscoveryAgent = QtBluetooth.QBluetoothDeviceDiscoveryAgent(
            self)
        self.deviceDiscoveryAgent.setLowEnergyDiscoveryTimeout(500)
        self.deviceDiscoveryAgent.deviceDiscovered.connect(self.add_device)
        self.deviceDiscoveryAgent.error.connect(self.scan_error)
        self.deviceDiscoveryAgent.finished.connect(self.scan_finished)
        self.deviceDiscoveryAgent.canceled.connect(self.scan_finished)

        self.deviceDiscoveryAgent.start(
            QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod(2))

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
    hello = DeviceFinder()
    # sys.exit(app.exec_())
    app.exec_()
