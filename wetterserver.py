#!/usr/bin/env python
# -*- coding: utf-8 -*


'''
    
    Funktion Wetterstation:
                  - auslesen der Temperatur und Luftfeuchte
                  - Server um  die Werte im Netzwerk bereit zustellen


    Hardwarevoraussetzungen:
            Raspberry zero über WLAN mit dem Netzwerk verbunden
            Sensor  DHT 22  mit Pin 4 verbunden
    Softwarevoraussetzungen:
        Treiber für Sensor installiert
        Python 3.6 installiert                
            
'''

import socket
import sys

def server_starten():

    #HOST_IP = "127.0.0.1"
    HOST_IP="192.168.2.135"
    PORT = 55252

    # Einstellung für die Schnittstelle AF_INET= IPv4, Sock_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as netzwerkschnittstelle:
        # Bei wiederholten Start des Servers kann es zu dieser Fehlermeldung kommen
        # OSError: [Errno 98] Address already in use
        # Abhilfe schafft  das setzen dieses Flags.
        # das SO_REUSEADDR-Flag sagt dem Kernel, einen lokalen Socket im TIME_WAIT-Zustand wiederzuverwenden,
        # ohne darauf zu warten, dass sein natürliches Timeout abläuft
        netzwerkschnittstelle.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        netzwerkschnittstelle.bind((HOST_IP, PORT))
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
                    schnittstelle.sendall(str.encode(" Hier sind die Daten"))

                # Abruch wenn AB gesendet wird vom client
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
