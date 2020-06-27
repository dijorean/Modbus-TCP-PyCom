# ----------------------------------------------------------------------------------------------------------------------
# Imports & global variables
# ----------------------------------------------------------------------------------------------------------------------

import time
import pycom
import uos
import sys
import _thread
import machine
import micropython

from exosence import ExoSense
from modbus import ModbusTCP
from webserver import Webserver

# Attempt to import all configurations (and give alias to some) as variables in the global scope.
try:
    import config
    config_AP_SSID = config.AP_SSID
    config_AP_PASSWORD = config.AP_PASSWORD
    config_AP_CHANNEL = config.AP_CHANNEL
    config_AP_ON_TIME_SEC = config.AP_ON_TIME_SEC
    config_FTP_USER = config.FTP_USER
    config_FTP_PASSWORD = config.FTP_PASSWORD
    config_WEB_USER = config.WEB_USER
    config_WEB_PASSWORD = config.WEB_PASSWORD
    config_ERROR = False
except Exception:
    print('Configuration error - Starting with default configuration')
    config_AP_SSID = 'ExoSensePy'
    config_AP_PASSWORD = 'exosense'
    config_AP_CHANNEL = 7
    config_AP_ON_TIME_SEC = 600
    config_FTP_USER = 'exo'
    config_FTP_PASSWORD = 'sense'
    config_WEB_USER = 'exo'
    config_WEB_PASSWORD = 'sense'
    config_ERROR = True

if config_AP_ON_TIME_SEC < 120:
    # Ignore configuration value if set to less than 120.
    config_AP_ON_TIME_SEC = 120

_ap_enabled = False  # Access point mode status.
_ftp = None  # Instance of FTP server.
_web = None  # Instance of Web server.
_exo = None  # Instance of board controller.


# ----------------------------------------------------------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------------------------------------------------------


def _print_ex(msg, e):
    """
    Print out a message and an exception traceback.

    :param msg: Message to be printed
    :param e: Exception traceback
    :return: None
    """

    print('== [Exception] =================================================================')
    print(msg)
    sys.print_exception(e)
    print('-------------------------------------------------------------------------------')
    micropython.mem_info()
    print('================================================================================')


# ----------------------------------------------------------------------------------------------------------------------
# Subroutines
# ----------------------------------------------------------------------------------------------------------------------


def _enable_ap(reboot_on_disable=True):
    """
    Enable access point mode.

    :param reboot_on_disable: whether or not to reboot if fails to enable access point mode.
    :return:None
    """

    global _ap_enabled  # Reference the variable defined in the global scope.

    # Attempt to enable access point mode
    try:
        if _ap_enabled:
            # If already enabled, simply return.
            return

        _ap_enabled = True
        pycom.heartbeat(False)
        pycom.rgbled(0xffff00)
        wlan.deinit()
        time.sleep(1)
        wlan.init(mode=WLAN.AP, ssid=config_AP_SSID, auth=(WLAN.WPA2, config_AP_PASSWORD), channel=config_AP_CHANNEL,
                  antenna=WLAN.INT_ANT)
        print("AP '{}' on for {} secs".format(config_AP_SSID, config_AP_ON_TIME_SEC))
        pycom.rgbled(0x0000ff)

        if config_FTP_USER and config_FTP_PASSWORD:
            _ftp.deinit()
            _ftp.init(login=(config_FTP_USER, config_FTP_PASSWORD))

        _web.start()

        start_ms = time.ticks_ms()
        while time.ticks_diff(start_ms, time.ticks_ms()) < config_AP_ON_TIME_SEC * 1000:
            try:
                _wdt.feed()
            except Exception:
                pass
            _web.process(5)

        _web.stop()

        _ftp.deinit()

        wlan.deinit()
        print('AP off')

        if _status_mb_got_request:
            pycom.rgbled(0x000000)
        else:
            pycom.rgbled(0x00ff00)

        _ap_enabled = False
    except Exception as e:
        try:
            wlan.deinit()
        except Exception as e:
            pass
        _ap_enabled = False
        _print_ex('_enable_ap() error', e)
        raise e

    if reboot_on_disable:
        machine.reset()


def _connect_wifi():
    """
    Connect to wifi network.

    :return: True for successful connection or False otherwise.
    """
    global _status_ap_enabled_once  # Reference variable in the global scope.

    try:
        pycom.heartbeat(False)
        pycom.rgbled(0xff0030)
        wlan.deinit()
        time.sleep(1)
        wlan.init(mode=WLAN.STA)
        if config.MB_TCP_IP == 'dhcp':
            wlan.ifconfig(config=('dhcp'))
        else:
            wlan.ifconfig(config=(config.MB_TCP_IP, config.MB_TCP_MASK, config.MB_TCP_GW, config.MB_TCP_DNS))

        if config.MB_TCP_WIFI_SEC == 0:
            auth = (None, None)
        elif config.MB_TCP_WIFI_SEC == 1:
            auth = (WLAN.WEP, config.MB_TCP_WIFI_PWD)
        elif config.MB_TCP_WIFI_SEC == 2:
            auth = (WLAN.WPA, config.MB_TCP_WIFI_PWD)
        else:
            auth = (WLAN.WPA2, config.MB_TCP_WIFI_PWD)

        print("Connecting to WiFi '{}'...".format(config.MB_TCP_WIFI_SSID))
        wlan.connect(ssid=config.MB_TCP_WIFI_SSID, auth=auth)

        blink = True
        start_ms = time.ticks_ms()
        while not wlan.isconnected():
            print('.', end='')
            if not _status_mb_got_request and config.AP_ON_TIMEOUT_SEC > 0 \
                and not _status_ap_enabled_once \
                and time.ticks_diff(start_ms, time.ticks_ms()) >= config.AP_ON_TIMEOUT_SEC * 1000:
                print('WiFi connection timeout')
                wlan.disconnect()
                _status_ap_enabled_once = True
                _enable_ap(reboot_on_disable=False)
                return False
            blink = not blink
            pycom.rgbled(0xff0030 if blink else 0x000000)
            _wdt.feed()
            time.sleep(0.3)

        print("Connected!")
        print(wlan.ifconfig())

        if _status_mb_got_request:
            pycom.rgbled(0x000000)
        else:
            pycom.rgbled(0x00ff00)

        return True
    except Exception as e:
        _print_ex('_connect_wifi() error', e)
        raise e


def _modbus_rtu_process():
    """
    Trigger ModBus module RTU request processing.

    :return: None
    """

    global _status_mb_got_request  # Reference variable in the global scope.
    global _status_ap_enabled_once  # Reference variable in the global scope.

    if _status_mb_got_request and not _ap_enabled:
        pycom.rgbled(0x000000)
    if _modbus.process():
        _status_mb_got_request = True
        if config.HEARTBEAT_LED:
            pycom.rgbled(0x0000ff)
    elif not _status_mb_got_request and config.AP_ON_TIMEOUT_SEC > 0 \
        and not _status_ap_enabled_once \
        and time.ticks_diff(start_ms, time.ticks_ms()) >= config.AP_ON_TIMEOUT_SEC * 1000:
        _status_ap_enabled_once = True
        _thread.start_new_thread(_enable_ap, (False,))

    print('Modbus RTU started - addr:', config.MB_RTU_ADDRESS)


def _modbus_tcp_process():
    """
    Trigger ModBus module TCP request processing.

    :return: None
    """

    global _status_mb_got_request  # Reference variable in the global scope.

    if wlan.isconnected():
        if _status_mb_got_request and not _ap_enabled:
            pycom.rgbled(0x000000)
        if _modbus.process():
            _status_mb_got_request = True
            if config.HEARTBEAT_LED:
                pycom.rgbled(0x0000ff)
        _web.process(0)
    else:
        if _connect_wifi():
            _web.start()
            local_ip = wlan.ifconfig()[0]
            _modbus.bind(local_ip=local_ip, local_port=config.MB_TCP_PORT)
            print('Modbus TCP started on {}:{}'.format(local_ip, config.MB_TCP_PORT))


# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------

# Initialize the ftp server.
_ftp = Server()
_ftp.deinit()

# Initialize the ftp server.
_web = WebServer(config_WEB_USER, config_WEB_PASSWORD)

# Initialize ModBus execution mode ( RTU or TCP) according to configuration.
if not config_ERROR and (config.MB_RTU_ADDRESS > 0 or len(config.MB_TCP_IP) > 0):
    _wdt = machine.WDT(timeout=20000)
    _status_ap_enabled_once = False
    _status_mb_got_request = False

    # Initialize board controller
    _exo = ExoSense()
    _exo.sound.init()
    _exo.light.init()
    _exo.thpa.init(temp_offset=(config.TEMP_OFFSET - 5), elevation=config.ELEVATION)

    for i in range(10):
        _exo.thpa.read()

    _modbus = ModbusTCP(exo=_exo)
    _modbus_process = _modbus_tcp_process # Set function  `_modbus_process()` to be same as `_modbus_tcp_process()`

    pycom.heartbeat(False)
    pycom.rgbled(0x00ff00)

    start_ms = time.ticks_ms()
    last_thpa_read = start_ms

    while True:
        # Loop while processing requests.
        _exo.sound.sample()
        now = time.ticks_ms()
        if time.ticks_diff(last_thpa_read, now) >= 5000:
            _exo.thpa.read()
            last_thpa_read = now
            print("thpa read")
        try:
            _modbus_process()
            _wdt.feed()
        except Exception as e:
            _print_ex('_modbus_process() error', e)

_enable_ap(reboot_on_disable=False)
print('Waiting for reboot...')

while True:
    try:
        _wdt.feed()
    except Exception as e:
        pass

    pycom.rgbled(0x000000)
    time.sleep(1)
    pycom.rgbled(0xff0000)
    time.sleep(1)
