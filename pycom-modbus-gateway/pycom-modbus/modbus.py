from uModbus.tcp import TCPServer
import uModbus.const as ModbusConst
from machine import Pin
import _thread
import time
from gateway import Gateway

MAX_DEVICES = 10
modbus_mapping = [0,0,0,0,0,0,0,0] #[C1,C2,C3,C4,T1,T2,T3,T5]
gatewayObject = 0

class Modbus:
    def __init__(self, itf, addr_list):
        #self._exo = exo
        self._itf = itf
        self._addr_list = addr_list

        # Create gateway object
        gatewayObject = Gateway()

    def process(self):
        request = self._itf.get_request(unit_addr_list=self._addr_list, timeout=0)
        if request == None:
            return False
        self._process_req(request)
        return True

    def _process_req(self, request):
        if request.function == ModbusConst.READ_DISCRETE_INPUTS:
            if request.register_addr >= 101 and request.register_addr <= 102:
                vals = []
                for i in range(request.register_addr, request.register_addr + request.quantity):
                    if i == 101:
                        vals.append(14)
                    elif i == 102:
                        vals.append(15)
                    else:
                        request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                        break
                request.send_response(vals)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        elif request.function == ModbusConst.READ_COILS:
            if request.register_addr == 201:
                request.send_response()
            elif request.register_addr == 151:
                #ttl1 = Pin(self._exo.PIN_TTL1, mode=Pin.IN, pull=None)
                request.send_response()
            elif request.register_addr == 152:
                #ttl2 = Pin(self._exo.PIN_TTL2, mode=Pin.IN, pull=None)
                request.send_response()
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        elif request.function == ModbusConst.WRITE_SINGLE_COIL:
            if request.register_addr == 201:
                if request.data[0] == 0x00:
                    #self._exo.DO1(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    #self._exo.DO1(1)
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            elif request.register_addr == 151:
                #ttl1 = Pin(self._exo.PIN_TTL1, mode=Pin.OUT)
                if request.data[0] == 0x00:
                    #ttl1(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    ttl1(1)
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            elif request.register_addr == 152:
                #ttl2 = Pin(self._exo.PIN_TTL2, mode=Pin.OUT)
                if request.data[0] == 0x00:
                    #ttl2(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    #ttl2(1)
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        elif request.function == ModbusConst.READ_INPUT_REGISTER:
            if request.register_addr >= 301 and request.register_addr <= 307:
                vals = []
                signed = []
                for i in range(request.register_addr, request.register_addr + request.quantity):
                    if i == 301:
                        #vals.append(int(self._exo.thpa.temperature() * 10))
                        signed.append(True)
                    elif i == 302:
                        #vals.append(int(self._exo.thpa.humidity() * 10))
                        signed.append(False)
                    elif i == 303:
                        #vals.append(int(self._exo.thpa.pressure() * 10))
                        signed.append(False)
                    elif i == 304:
                        #vals.append(int(self._exo.thpa.gas_resistance() / 1000))
                        signed.append(False)
                    elif i == 305:
                        #vals.append(int(self._exo.light.lux() * 10))
                        signed.append(False)
                    elif i == 306:
                        #vals.append(self._exo.sound.avg())
                        signed.append(False)
                    elif i == 307:
                        #vals.append(self._exo.sound.peak())
                        signed.append(False)
                    elif i == 308:
                        #vals.append(self._exo.thpa.iaq())
                        signed.append(False)
                    elif i == 309:
                        #vals.append(self._exo.thpa.iaq_trend())
                        signed.append(True)
                    else:
                        request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                        break
                request.send_response(vals, signed=signed)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        elif request.function == ModbusConst.WRITE_SINGLE_REGISTER:

            rgbVal = 0000
            timerVal = 0000

            # Attends 10 devices for now
            if request.register_addr <= MAX_DEVICES:
                # Get rgbVal
                rgbVal = request.data_as_registers(signed=False)[0]
                # Save rgbVal on modbus table
                modbus_mapping[request.register_addr] = val
                print("RGB Val is %d" % rgbVal)

                gatewayObject.process_changes_modbus(request.register_addr, rgbVal, timerVal)

                request.send_response()
            elif (request.register_addr > MAX_DEVICES) and (request.register_addr <= (2 * MAX_DEVICES)):
                # Get timerVal
                timerVal = request.data_as_registers(signed=False)[0]
                # Save rgbVal on modbus table
                modbus_mapping[request.register_addr] = val
                print("RGB Val is %d" % rgbVal)

                gatewayObject.process_changes_modbus(request.register_addr, rgbVal, timerVal)

                request.send_response()
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        elif request.function == ModbusConst.READ_HOLDING_REGISTERS:
            vals = []
            if (request.register_addr == 10):
                vals.append(9)
                request.send_response(vals)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        else:
            request.send_exception(ModbusConst.ILLEGAL_FUNCTION)

class ModbusTCP(Modbus):
    def __init__(self):
        super().__init__(
            TCPServer(),
            None
        )

    def bind(self, local_ip, local_port=502):
        self._itf.bind(local_ip, local_port)
