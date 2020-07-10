# Access point WiFi name (SSID)
AP_SSID = 'DRA'

# Access point WiFi password
AP_PASSWORD = '12345'

# Access point WiFi channel
AP_CHANNEL = 7

# Duration of access point mode, is seconds.
# Values below 120 (2 mins) are ignored.
AP_ON_TIME_SEC = 120

# Time (seconds) after power-on after which access point mode is enabled
# if the module is configured and no Modbus RTU request is received or
# if cannot connect to WiFi (Modbus TCP).
# Set to 0 to disable access point mode.
AP_ON_TIMEOUT_SEC = 60

# Web server credentials
WEB_USER = 'admin'
WEB_PASSWORD = 'admin'

# FTP server credentials
FTP_USER = 'admin' # Set to '' to disable FTP server
FTP_PASSWORD = 'admin'

# LED status when working normally
HEARTBEAT_LED = True # LED off
# HEARTBEAT_LED = True # LED short blue blink on every Modbus request

# Modbus TCP parameters

#MB_TCP_IP = '' # Modbus TCP disabled
#MB_TCP_IP = 'dhcp' # Use DHCP to obtain IP address
MB_TCP_IP = '192.168.0.50' # Static IP address

MB_TCP_MASK = '255.255.255.0' # Network mask
MB_TCP_GW = '192.168.0.1' # Gateway IP address
MB_TCP_DNS = '8.8.8.8' # DNS IP address

MB_TCP_PORT = 502 # Port for Modbus TCP requests

MB_TCP_WIFI_SSID = 'RA' # SSID of the WiFi network to connect to
MB_TCP_WIFI_PWD = '26141704maJArean' # WiFi password
MB_TCP_WIFI_SEC = 3 # WiFi security: 0 = Open, 1 = WEP, 2 = WPA, 3 = WPA2
