from uModbus.tcp import TCPServer
import uModbus.const as ModbusConst
from machine import Pin
import _thread
import time


# ----------------------------------------------------------------------------------------------------------------------
# Modbus parent class
# ----------------------------------------------------------------------------------------------------------------------

class Modbus:

    def __init__(self, exo, itf, addr_list):
        """
        Create private reference to passed arguments upon class instantiation.

        :param exo: Instance of board controller
        :param itf: Interface
        :param addr_list: List of addresses
        """

        self._exo = exo
        self._itf = itf
        self._addr_list = addr_list

    def process(self):
        """
        Read request and trigger its processing.

        :return: True if request is successfully processed or False otherwise
        """

        request = self._itf.get_request(unit_addr_list=self._addr_list, timeout=0)

        if request == None:
            # TODO: Consider replacing the above comparison with `isinstance(request, type(None))`.
            return False

        self._process_req(request)
        return True

    def _beep(self, ms):
        """
        Trigger a beep.

        :param ms: Duration of the beep, in milli seconds
        :return: None
        """

        self._exo.buzzer(1)
        time.sleep_ms(ms)
        self._exo.buzzer(0)

    def _do1_pulse(self, ms):
        """
        Trigger a pulse.

        :param ms: Duration of the pulse, in milli seconds
        :return: None
        """

        self._exo.DO1(1)
        time.sleep_ms(ms)
        self._exo.DO1(0)

    def _process_req(self, request):
        """
        Process an already read request.

        :param request: The actual (already read) request
        :return: None
        """

        if request.function == ModbusConst.READ_DISCRETE_INPUTS:
            if request.register_addr >= 101 and request.register_addr <= 102:
                vals = []
                for i in range(request.register_addr, request.register_addr + request.quantity):
                    if i == 101:
                        vals.append(self._exo.DI1())
                    elif i == 102:
                        vals.append(self._exo.DI2())
                    else:
                        request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                        break
                request.send_response(vals)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        elif request.function == ModbusConst.READ_COILS:
            if request.register_addr == 201:
                request.send_response([self._exo.DO1()])
            elif request.register_addr == 151:
                ttl1 = Pin(self._exo.PIN_TTL1, mode=Pin.IN, pull=None)
                request.send_response([ttl1()])
            elif request.register_addr == 152:
                ttl2 = Pin(self._exo.PIN_TTL2, mode=Pin.IN, pull=None)
                request.send_response([ttl2()])
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        elif request.function == ModbusConst.WRITE_SINGLE_COIL:
            if request.register_addr == 201:
                if request.data[0] == 0x00:
                    self._exo.DO1(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    self._exo.DO1(1)
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            elif request.register_addr == 151:
                ttl1 = Pin(self._exo.PIN_TTL1, mode=Pin.OUT)
                if request.data[0] == 0x00:
                    ttl1(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    ttl1(1)
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            elif request.register_addr == 152:
                ttl2 = Pin(self._exo.PIN_TTL2, mode=Pin.OUT)
                if request.data[0] == 0x00:
                    ttl2(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    ttl2(1)
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
                        vals.append(int(self._exo.thpa.temperature() * 10))
                        signed.append(True)
                    elif i == 302:
                        vals.append(int(self._exo.thpa.humidity() * 10))
                        signed.append(False)
                    elif i == 303:
                        vals.append(int(self._exo.thpa.pressure() * 10))
                        signed.append(False)
                    elif i == 304:
                        vals.append(int(self._exo.thpa.gas_resistance() / 1000))
                        signed.append(False)
                    elif i == 305:
                        vals.append(int(self._exo.light.lux() * 10))
                        signed.append(False)
                    elif i == 306:
                        vals.append(self._exo.sound.avg())
                        signed.append(False)
                    elif i == 307:
                        vals.append(self._exo.sound.peak())
                        signed.append(False)
                    elif i == 308:
                        vals.append(self._exo.thpa.iaq())
                        signed.append(False)
                    elif i == 309:
                        vals.append(self._exo.thpa.iaq_trend())
                        signed.append(True)
                    else:
                        request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                        break
                request.send_response(vals, signed=signed)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        elif request.function == ModbusConst.WRITE_SINGLE_REGISTER:
            if request.register_addr == 401:
                val = request.data_as_registers(signed=False)[0]
                _thread.start_new_thread(self._beep, (val,))
                request.send_response()
            elif request.register_addr == 211:
                val = request.data_as_registers(signed=False)[0]
                _thread.start_new_thread(self._do1_pulse, (val,))
                request.send_response()
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        else:
            request.send_exception(ModbusConst.ILLEGAL_FUNCTION)


# ----------------------------------------------------------------------------------------------------------------------
# Modbus children classes
# ----------------------------------------------------------------------------------------------------------------------

class ModbusTCP(Modbus):

    def __init__(self, exo):
        """
        Create private reference to passed arguments and execute relevant class instantiation functions.

        :param exo: Instance of the board controller.
        """

        # Execute `__init__()` method of the parent class (`Modbus` class)
        super().__init__(exo=exo, itf=TCPServer(), addr_list=None)

    def bind(self, local_ip, local_port=502):
        """
        Bind to the TCP socket.

        :param local_ip: IP address
        :param local_port: Port number
        :return: None
        """

        self._itf.bind(local_ip, local_port)
