#!/usr/bin/env python
# -*- coding: utf-8 -*

import socket
import sys
import subprocess
import re
import time ,threading
import Adafruit_DHT
from Adafruit.Adafruit_BMP180 import BMP085

exitFlag = 0
messdaten="0|0|0|0|0|0"

def cpu_temperatur():
    cpu_temp = subprocess.check_output("/opt/vc/bin/vcgencmd measure_temp", shell=True)
    cpu_temp = cpu_temp.decode('utf-8').split('=')[1]
    return cpu_temp[0:4]

def sensor_BMP180_anfrage():
    # Initialise the BMP085 and use STANDARD mode (default value)
    # bmp = BMP085(0x77, debug=True)
    bmp = BMP085(0x77, 1)

    # To specify a different operating mode, uncomment one of the following:
    # bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
    # bmp = BMP085(0x77, 1)  # STANDARD Mode
    # bmp = BMP085(0x77, 2)  # HIRES Mode
    # bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

    # Abfrage der Sensordaten
    korrekturfaktor_d = 1000
    # korrekturfaktor_t=-5   # mein Sensor zeigt 8 Kelvin zuviel an ;)
    temperatur = bmp.readTemperature()  # +korrekturfaktor_t
    luftdruck = bmp.readPressure() + korrekturfaktor_d
    hoehe = bmp.readAltitude(luftdruck)

    if luftdruck is not None and temperatur is not None and hoehe is not None:
        daten = [temperatur, luftdruck, hoehe]
    else:
        daten = 'Sensoren auslesen ist fehlgeschlagen'
        print('Failed to get reading. Try again!')

    return daten

def sensor_DHT22_anfrage():
    sensor = Adafruit_DHT.DHT22
    gpio = 17

    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    luftfeuchte, temperature = Adafruit_DHT.read_retry(sensor, gpio)

    if luftfeuchte is not None and temperature is not None:
        daten = [luftfeuchte, temperature]
    else:
        daten = 'Sensoren auslesen ist fehlgeschlagen'
        print('Failed to get reading. Try again!')
        # sys.exit(1)
    return daten

def sensoren_auslesen():
    global messdaten

    while True:
        ''' hier werden die die Rohmessdaten gesendet'''
        cpu_temp = cpu_temperatur()
        sensor_bmp180 = sensor_BMP180_anfrage()
        sensor_dht22 = sensor_DHT22_anfrage()
        # messdaten= luftfeuchte|temperature| temperature |luftdruck| hoehe| cputemperature
        messdaten=(str(sensor_dht22[0])
                   + "|" + str(sensor_dht22[1])
                   + "|" + str(sensor_bmp180[0])
                   + "|" + str(sensor_bmp180[1])
                   + "|" + str(sensor_bmp180[2])
                   + "|" + str(cpu_temp))
        time.sleep(300)
    pass

def server_starten():

    PORT = 55252

    # prüfen ob die Netzwerkkarte schon aktive ist und auslesen der IP Adresse
    for x in range(0,2):
        ausgabe = subprocess.check_output("ip -f inet addr show dev wlan0| awk -F ' *|:' '/inet/'", shell=True)
        try:
            # Ermitteln der IP Adresse  (Stingoperation)
            suchfilter=r'.*?inet\ (.*?)/'
            HOST_IP=re.findall(suchfilter,ausgabe.decode())[0]
            break
        except IndexError as e:
            time.sleep(10)
            continue

    # Einstellung für die Schnittstelle AF_INET= IPv4, Sock_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as netzwerkschnittstelle:
        # Bei wiederholten Start des Servers kann es zu dieser Fehlermeldung kommen
        # OSError: [Errno 98] Address already in use
        # Abhilfe schafft  das setzen dieses Flags.
        # das SO_REUSEADDR-Flag sagt dem Kernel, einen lokalen Socket im
        # TIME_WAIT-Zustand wiederzuverwenden,
        # ohne darauf zu warten, dass sein natürliches Timeout abläuft
        netzwerkschnittstelle.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            netzwerkschnittstelle.bind((HOST_IP, PORT))

        except OSError as error:
           print("Dienst Wetterstation ist schon gestartet")
           print(error)
           #[Errno 98] Address already in use

        netzwerkschnittstelle.listen(1)
        #print("Warten auf eine Verbindung.")

        # schnittstelle ist ein Objekt zum empfangen und senden von Daten
        # addr ist die Adressen des anderen PC
        schnittstelle, addr = netzwerkschnittstelle.accept()

        # das soll der Server tun
        stop_server=False

        with schnittstelle:
            # Begrüßung
            schnittstelle.send(str.encode("Willkommen auf der Wetterstation! \n"))
            print("Verbunden wurde mit: ", str(addr[0]) + ":" + str(addr[1]) + " hergestellt!" )

            while True:
                anfrage_empfangen = schnittstelle.recv(2048)
                anfrage = str(anfrage_empfangen.decode('utf-8'))
                '''
                    Die Schnittstelle unterstützt 3 Funktionen
                    1 Anfragen der Sensordaten
                    2 Abbruch der Verbindung zwischen Server und Client
                    3 Stop der Servers
                '''

                if anfrage[0:9] =='MESSDATEN':
                    schnittstelle.sendall(str.encode(str(messdaten)))

                # Abbruch wenn AB gesendet wird vom client
                if anfrage[0:2] == 'AB':
                    print("Verbindung wurde durch die Aufforderung des Client geschlosssen!")
                    schnittstelle.sendall(str.encode("Ende"))
                    break

                if anfrage[0:4]== "Stop":
                    stop_server=True
                    print("Die Wetterstation wurde beendet durch den Stopbefehl vom client!")
                    break
            # Schleifenende

            schnittstelle.close()
            return stop_server


############# Threads ################################
'''
 Sensoren auslesen wir als eigener thread gestartet 
 der alle 5 min die Sensoren abfragt
 Der Server selbst wird in einer while schleife betrieben
'''
class sensoren (threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name

   def run(self):
      sensoren_auslesen()

class meinServer(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        while True:
            try:
                stop = server_starten()
                if stop == True:
                    print("Server wurde vom client gestoppt")
                    # Break beendet die Whileschleife
                    break
            except KeyboardInterrupt as e:
                print("\tDas Programm wurde beendet." + str(e))
                sys.exit()

# Erzeugt die Jobs die parallel abgearbeitet werden sollen
# thread 1
sensordaten = sensoren("Sensoren")
sensordaten.daemon=True
# thread 2
server=meinServer("Server")
server.daemon=True

# Start der neuen Threads
sensordaten.start()
server.start()

sensordaten.join()
server.start()

if __name__ == "__main__":
    pass