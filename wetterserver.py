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
    korrekturfaktor_t=-5    # mein Sensor zeigt 5 Kelvin zuviel an ;)
    temperatur = bmp.readTemperature()+korrekturfaktor_t
    luftdruck = bmp.readPressure()+korrekturfaktor_d
    hoehe = bmp.readAltitude(luftdruck)
    
    if luftdruck is not None and temperatur is not None and hoehe is not None:
        daten='Temperatur={0:0.1f}°C  Luftdruck={1:0.1f}hPa Höhe={2:0.1f}m'.format(temperatur, (luftdruck/100) , hoehe)
    else:
        daten='Sensoren auslesen ist fehlgeschlagen'
        print('Failed to get reading. Try again!')
        
    return daten

    pass

def sensor_DHT22_anfrage():
    sensor=Adafruit_DHT.DHT22
    gpio=17
    korrekturfaktor_t=-5
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry). 
    luftfeuchte, temperature = Adafruit_DHT.read_retry(sensor, gpio)

    if luftfeuchte is not None and temperature is not None:
        daten='Temperatur={0:0.1f}°C  Luftfeuchte={1:0.1f}%'.format(temperature, luftfeuchte)
        print('Temp={0:0.1f}°C  Humidity={1:0.1f}%'.format(temperature, luftfeuchte))
    else:
        daten='Sensoren auslesen ist fehlgeschlagen'
        print('Failed to get reading. Try again!')
        #sys.exit(1)
    return daten
    pass

def server_starten():
    # HOST_IP = "127.0.0.1"
    #HOST_IP = "192.168.2.135"
    PORT = 55252

    # prüfen ob die Netzwerkkarte schon aktive ist und auslesen der IP Adresse
    for x in range(0,2):
            #ausgabe = subprocess.check_output("ip -f inet addr show dev enp2s0|awk '/inet/ '", shell=True)
        ausgabe = subprocess.check_output("ip -f inet addr show dev wlan0| awk -F ' *|:' '/inet/'", shell=True)
        try:
            suchfilter=r'.*?inet\ (.*?)/'
            HOST_IP=re.findall(suchfilter,ausgabe.decode())[0]
            break
        except IndexError as e:
            time.sleep(10)
            continue
        #except subprocess.CalledProcessError as e:
            # in Logdatei schreiben
            #p rint(e,"Test:\t", x)
        #    time.sleep(10)
        #    continue
        pass

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
           #[Errno 98] Address already in use

        netzwerkschnittstelle.listen(1)
        print("Warten auf eine Verbindung.")

        # schnittstelle ist ein Objekt zum empfangen und senden von Daten
        # addr ist die Adressen des anderen PC
        schnittstelle, addr = netzwerkschnittstelle.accept()

        # das soll der Server tun
        stop_server=False

        with schnittstelle:
            schnittstelle.send(str.encode("Willkommen auf der Wetterstation! \n"))
            print("Verbunden wurde mit: ", str(addr[0]) + ":" + str(addr[1]) + " hergestellt!" )
            while True:
                anfrage_empfangen = schnittstelle.recv(2048)
                '''
                # wenn der Server über Telnet angesprochen wird
                try:
                    daten_senden = "Antwort des Servers: " + daten_empfangen.decode('utf-8')

                # Wenn ein strg-c gesendet wird die Verbindung getrennt
                # der Server läuft aber weiter
                except UnicodeDecodeError:
                    print("Verbindung wurde durch ungültige Zeichen ^C  vom Client geschlossen!")
                    break

                schnittstelle.sendall(str.encode(daten_senden))
                '''

                anfrage = str(anfrage_empfangen.decode('utf-8'))

                # Daten senden wenn danach gefragt wird
                if anfrage[0:5] =='DATEN':
                    #schnittstelle.sendall(str.encode(" Hier sind die Daten"))
                    sensor_dht22=sensor_DHT22_anfrage()
                    sensor_bmp180=sensor_BMP180_anfrage()
                    schnittstelle.sendall(str.encode(sensor_dht22 +" " + sensor_bmp180))


                # Abbruch wenn AB gesendet wird vom client
                if anfrage[0:2] == 'AB':
                    print("Verbindung wurde durch die Aufforderung des Client geschlosssen!")
                    schnittstelle.sendall(str.encode("Ende"))
                    break

                if anfrage[0:4]== "Stop":
                    stop_server=True
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
