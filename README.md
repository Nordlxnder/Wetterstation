# Wetterstation

 wetterserver.py


     Funktion Wetterstation:
        - auslesen der Temperatur und Luftfeuchte
        - Server um  die Werte im Netzwerk bereit zustellen

    Hardwarevoraussetzungen:
        Raspberry zero über WLAN mit dem Netzwerk verbunden
        Sensor  DHT 22  mit Pin 4 verbunden

    Softwarevoraussetzungen:
        Treiber für Sensor installiert Adafruit_Python_DHT
        Python 3.6 installiert


 client_wetter.py
        - sendet Schlüsselwörter wie DATEN um Daten anzufordern oder AB um die Verbindung zubeenden

