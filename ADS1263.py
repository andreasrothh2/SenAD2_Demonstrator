#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Basierend auf Waveshare High-Precision AD HAT Library:
# https://github.com/waveshareteam/High-Pricision_AD_HAT/blob/master/python/ADS1263.py
#
# Wheatstone-Vollbrücke Anschlüsse:
#   IN0  -> Brücke OUT+ (positiver Ausgang)
#   IN1  -> Brücke OUT- (negativer Ausgang)
#   VCC  -> Brücke Versorgung (3.3V oder 5V, je nach Brücke)
#   GND  -> Brücke Masse
#
# DRDY (Data Ready) ist mit GPIO17 (Pin 11 auf Raspberry Pi Header) verbunden.

import RPi.GPIO as GPIO
import time
import csv
import ADS1263                 # offizielle Waveshare-Library

# DRDY Pin
DRDY_PIN = 17

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(DRDY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ADC Objekt
adc = ADS1263.ADS1263()

if adc.ADS1263_init() == -1:
    exit("ADC konnte nicht initialisiert werden.")

# Konfiguration: Differential, 400 SPS, interne Ref, PGA=32, FIR, Chop=off
# Achtung: Funktion ADS1263_ConfigADC(rate, gain, ref, chop, mode, filter)
# laut ADS1263.py implementiert.
adc.ADS1263_ConfigADC(
    rate=ADS1263.ADS1263_DRATE_400,     # 400 SPS
    gain=ADS1263.ADS1263_GAIN_32,       # max Verstärkung
    ref=ADS1263.ADS1263_REF_Internal,   # interne ±2.5V Referenz
    chop=ADS1263.ADS1263_CHOP_OFF,      # Chop-Mode off
    mode=ADS1263.ADS1263_MODE_DIFF,     # Differential
    flt=ADS1263.ADS1263_FILTER_FIR      # FIR Filter
)

# Differential-Kanal 0 = IN0+, IN1-
channel = 0

# CSV Datei vorbereiten
csv_file = open("measurements.csv", "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["timestamp", "voltage"])

print("Starte Messung mit 400 Hz, Abbruch mit STRG+C.")

try:
    while True:
        # Warten bis DRDY LOW -> neuer Messwert verfügbar
        GPIO.wait_for_edge(DRDY_PIN, GPIO.FALLING)

        # Zeitstempel möglichst nah am Messereignis erfassen
        ts = time.time()

        # Wert lesen (raw ADC -> Voltage)
        raw_val = adc.ADS1263_GetChannalValue(channel)
        voltage = adc.ADS1263_ConvertToVol(raw_val, gain=32)

        # In CSV schreiben
        writer.writerow([ts, voltage])

except KeyboardInterrupt:
    print("Messung beendet.")

finally:
    csv_file.close()
    adc.ADS1263_exit()
    GPIO.cleanup()
    print("CSV-Datei gespeichert.")
