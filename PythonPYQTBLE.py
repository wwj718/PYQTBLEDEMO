
import PyQt5
from PyQt5 import QtCore
from PyQt5 import QtBluetooth

class Devidcehandler(QtCore.QObject):
    pass

class Deviceinfo(QtCore.QObject):
    devicechanged=PyQt5.QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.m_device=QtBluetooth.QBluetoothDeviceInfo()
        
        self.devicechanged.connect(self.emitDeviceChanged)

    def getName(self):
        return self.m_device.name()

    

    def getAddress(self):
        return self.m_device.address().toString()
    
    #设备改变的信号触发函数，用于更新界面等功能
    def emitDeviceChanged(self):
        pass

    def setDevice(self,device):
        self.m_device=device
        self.devicechanged.emit()


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
            self.m_devices.append( QtBluetooth.QBluetoothDeviceInfo(device) )
            print("Low Energy device found. Scanning more...")

    def scan_finished(self):
        print("scan finished")
        for i in self.m_devices:
            #QtBluetooth.QBluetoothDeviceInfo.
            print('UUID: {UUID}, Name: {name}, rssi: {rssi}'.format(UUID=i.deviceUuid().toString(),
                                                                    name=i.name(),
                                                                    rssi=i.rssi()))
        
        #self.quit()

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
    #sys.exit(app.exec_())
    app.exec_()