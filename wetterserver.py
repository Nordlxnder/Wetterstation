#!/usr/bin/env python
# -*- coding: utf-8 -*

'''
    
    Funktion Wetterstation:
                  - auslesen der Temperatur, Luftdruck, Höhe und Luftfeuchte
                  - Server um die Werte im Netzwerk bereit zustellen
                 
    Hardwarevoraussetzungen:
            Raspberry zero über WLAN mit dem Netzwerk verbunden
            Sensor  DHT 22  mit Pin 11 GPIO 17 verbunden
            Sensor  BMP180              

    Softwarevoraussetzungen:
        Treiber für Sensor installiert
        Python 3.6 installiert                
        i2c-tools    
'''

import socket
import sys
import subprocess
import re
import time
import Adafruit_DHT
from Adafruit.Adafruit_BMP180 import BMP085

def cpu_temperatur():
    cpu_temp = subprocess.check_output("/opt/vc/bin/vcgencmd measure_temp", shell=True)
    cpu_temp = cpu_temp.decode('utf-8').split('=')[1]
    return cpu_temp[0:4]

def sensor_BMP180_anfrage():
    # Initialise the BMP085 and use STANDARD mode (default value)
    # bmp = BMP085(0x77, debug=True)
    bmp = BMP085(0x77,1)

    # To specify a different operating mode, uncomment one of the following:
    # bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
    # bmp = BMP085(0x77, 1)  # STANDARD Mode
    # bmp = BMP085(0x77, 2)  # HIRES Mode
    # bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode
    
    # Abfrage der Sensordaten
    korrekturfaktor_d=1000
    #korrekturfaktor_t=-5   # mein Sensor zeigt 8 Kelvin zuviel an ;)
    temperatur = bmp.readTemperature()#+korrekturfaktor_t
    luftdruck = bmp.readPressure()+korrekturfaktor_d
    hoehe = bmp.readAltitude(luftdruck)
    
    if luftdruck is not None and temperatur is not None and hoehe is not None:
        daten=[temperatur,luftdruck,hoehe]
    else:
        daten='Sensoren auslesen ist fehlgeschlagen'
        print('Failed to get reading. Try again!')
        
    return daten

    pass

def sensor_DHT22_anfrage():
    sensor=Adafruit_DHT.DHT22
    gpio=17

    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry). 
    luftfeuchte, temperature = Adafruit_DHT.read_retry(sensor, gpio)

    if luftfeuchte is not None and temperature is not None:
        daten = [luftfeuchte ,temperature]
    else:
        daten='Sensoren auslesen ist fehlgeschlagen'
        print('Failed to get reading. Try again!')
        #sys.exit(1)
    return daten
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
        # das SO_REUSEADDR-Flag sagt dem Kernel, einen lokalen Socket im TIME_WAIT-Zustand wiederzuverwenden,
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
                    2 Abbruch der Verbindung zwisch Server und Client
                    3 Stop der Servers
                '''
                # Daten senden wenn danach gefragt wird
                if anfrage[0:5] =='DATEN':
                    ''' Hier werden die Messdaten in lesebarer From und deren Bedeutung gesendet'''
                    sensor_dht22=sensor_DHT22_anfrage()
                    korr_lf=7
                    korr_t=-0
                    tempsensor='Temperatur={0:0.1f}°C  Luftfeuchte={1:0.1f}%'.format(sensor_dht22[1]+korr_t,
                                                                                     sensor_dht22[0]+korr_lf)
                    sensor_bmp180=sensor_BMP180_anfrage()
                    korr_t2=-7
                    drucksensor= 'Temperatur={0:0.1f}°C  Luftdruck={1:0.1f}hPa ' \
                                 'Höhe={2:0.1f}m'.format(sensor_bmp180[0]+korr_t2,
                                                        (sensor_bmp180[1] / 100),
                                                         sensor_bmp180[2])
                    cpu_temp = cpu_temperatur()
                    cpu_temp = "CPU-Temperatur=" + cpu_temp + "°C"
                    schnittstelle.sendall(str.encode(tempsensor + " " + drucksensor + " " + cpu_temp))

                if anfrage[0:9] =='MESSDATEN':
                    ''' hier werden die die Rohmessdaten gesendet'''
                    sensor_dht22=sensor_DHT22_anfrage()
                    sensor_bmp180=sensor_BMP180_anfrage()
                    cpu_temp = cpu_temperatur()
                    schnittstelle.sendall(str.encode(str(sensor_dht22[0])
                                                     +"|"+str(sensor_dht22[1])
                                                     +"|"+str(sensor_bmp180[0])
                                                     +"|"+str(sensor_bmp180[1])
                                                     +"|"+str(sensor_bmp180[2])
                                                     +"|"+str(cpu_temp)))

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

if __name__ == "__main__":
    while True:
        try:
            stop=server_starten()
            if stop == True:
                print("Server wurde vom client gestoppt")
                # Break beendet die Whileschleife
                break
        except KeyboardInterrupt as e:
            print("\tDas Programm wurde beendet." + str(e))
            sys.exit()
