# ----------------------------------------------------------------------------------------------------------------------
# Access point configuration
# ----------------------------------------------------------------------------------------------------------------------
AP_SSID = 'ExoSensePy'  # WiFi network name (SSID).
AP_PASSWORD = 'exosense'  # WiFi password.
AP_CHANNEL = 7  # WiFi channel.
AP_ON_TIME_SEC = 600  # Duration (seconds) of access point mode. Values below 120 (2 mins) are ignored!
AP_ON_TIMEOUT_SEC = 300  # Time (seconds), since power-on, before access point mode is enabled, when the module is
# configured and no Modbus RTU request is received or if cannot connect to WiFi (Modbus TCP).  Set it to 0 to disable
# access point mode.

# ----------------------------------------------------------------------------------------------------------------------
# Web server credentials
# ----------------------------------------------------------------------------------------------------------------------
WEB_USER = 'exo'
WEB_PASSWORD = 'sense'

# ----------------------------------------------------------------------------------------------------------------------
# FTP server credentials
# ----------------------------------------------------------------------------------------------------------------------
FTP_USER = 'exo'  # Set to '' to disable FTP server.
FTP_PASSWORD = 'sense'

# ----------------------------------------------------------------------------------------------------------------------
# Instruments configuration
# ----------------------------------------------------------------------------------------------------------------------
HEARTBEAT_LED = False  # LED status when working normally. If set to True, short blue blink on every Modbus request.
TEMP_OFFSET = 0  # Temperature offset (°C).
ELEVATION = 103  # Elevation from sea level in meters, for atmospheric pressure calculation.

# ----------------------------------------------------------------------------------------------------------------------
# Modbus TCP parameters
# ----------------------------------------------------------------------------------------------------------------------
MB_TCP_IP = '192.168.1.100'  # Set to  'dhcp' for dynamic addressing or set to '' for TCP disabled.

MB_TCP_MASK = '255.255.255.0'  # Network mask.
MB_TCP_GW = '192.168.1.1'  # Gateway IP address.
MB_TCP_DNS = '192.168.1.1'  #  DNS IP address.

MB_TCP_PORT = 502  #  Port for Modbus TCP requests.

MB_TCP_WIFI_SSID = 'MyWiFi'  # SSID of the WiFi network to connect to .
MB_TCP_WIFI_PWD = 's3cretP4ssw0rd'  # WiFi password.
MB_TCP_WIFI_SEC = 3  # WiFi security: 0 = Open, 1 = WEP, 2 = WPA, 3 = WPA2.
