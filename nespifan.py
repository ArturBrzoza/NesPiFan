# Created by Marcus Von Vein 2024
# Version 1.0
# Skrypt do kontroli wentylatora w komputerze Raspberry Pi 3B+
# jest zoptymalizowany pod obudowe NesPi Case+ oraz wentylatora z laptopa 50mm
# skrypt stara sie utrzymac temperature w okolicach 55 stopni
# zachowujac kulture pracy
print('NesPiFan - PWM fan control for NesPi Case+')
print('Created by Marcus Von Vein 2024')
print()
import RPi.GPIO as IO
import time
import subprocess
print('Configure PWM on GPIO - OK')
IO.setwarnings(False)          # Ignoruj bledy
IO.setmode (IO.BCM)            # Konwersja z PIN na GPIO
IO.setup(15,IO.OUT)            # Ustalenie portu GPIO dla PWM (w tym wypadku GPIO15)
fan = IO.PWM(15,200)           # Ustawiony jest port GOPI15 i czestotliwosc 100MHz (trzeba recznie dopasowac)
fan.start(0)                   # Po starce ustawia wartosc 0
print('Load all parametrs - OK')
minTemp = 40                   # Zakres w ktorym dziala dany wentylator i nie dostaje pierdolca
avgTemp = 55
maxTemp = 70
infTemp = [0,0] # Zbiera informacje o temperaturze i wydaje decyzje czy podjac akcje

minSpeed = 40                  # Zakres w ktorym dziala ten wentylator
maxSpeed = 100
avgSpeed = 60                # Predkosc od ktorej ma zaczas prace
bostSpeed = 0                  # Manipulator oborotowo kreconcy szybciej lub wolniej
timeSpeed = 0                  # Czasomierz
stsSpeed = 0                   # Stan pracy wentlatora

hudShow = 0                    #wyswietlenie parametrow

def get_temp():                             # Funkcja ktora sprawdza tempterature komputera i zwraca wartosc w stopniach Celcjuszach
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('ERROR : Temperature sensors not found')

def renormalize(n, range1, range2):         # Funkcja do skalowania mocy wzgledem temperatury komputera
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]
print('Load all definitions - OK');
print()
print('Program working! :-)')
while 1:                                    # Uruchomienie programu w pentli
    pcTemp = get_temp()                     # Pobiera temperature do wgladu
    temp = get_temp()                       # pobiera temperature do obliczenia limitu
    if temp < minTemp:
        temp = minTemp
    elif temp > maxTemp:
        temp = maxTemp
    
    # Sprawdzanie temperatury do programu ponizej
    infTemp[1] = infTemp[0] # przenosi informacje z banku 0 do banku numer 1
    infTemp[0] = pcTemp # zapisuje infomracje o temperaturze w banku 0
    if infTemp[0]>infTemp[1]: # gdy podczas chlodzenia temperatura nadal wzdrasta
        if pcTemp>avgTemp: bostSpeed = bostSpeed + 5 # Gdy temperatura jest wyzsza niz 55 stopni to zwieksza predkosc
    if pcTemp<avgTemp: bostSpeed = bostSpeed - 5 # Gdy temperatura jest nizsza niz 55 stopni to zmniejsza predkosc
    if avgSpeed+bostSpeed>maxSpeed: bostSpeed=maxSpeed-avgSpeed #sprawdza, aby predkosc nie przekraczala po za skale maxSpeed oraz minSpeed
    if avgSpeed+bostSpeed<minSpeed: bostSpeed=minSpeed-avgSpeed
    if stsSpeed==0: bostSpeed = 0
    fanSpeed = avgSpeed + bostSpeed # Sumuje to wszystko
    
    # tego nie zmieniaj bo zapierdole ci w ryj!
    if pcTemp>60: stsSpeed = 1 # Zalanczanie i wylaczanie wentylatora po przekroczeniu danej temperatury
    if pcTemp<50: stsSpeed = 0
    if stsSpeed==1: fan.ChangeDutyCycle(fanSpeed) # predkosc wentylatora
    else: fan.ChangeDutyCycle(0)
    
    #------------------------------------------------ wyswietlanie informacji w terminalu
    if hudShow==1: 
        print('') # Funkcje ktore maja skontrolowac co sie dzieje wewnatrz programu
        print('Temperatura komputera: ',pcTemp,'C')
        if stsSpeed==1: print('Predkosc wentylatora: ',fanSpeed,'%')
        else: print('Wentylator wylaczony')

    time.sleep(5)                           # Zatrzymuje program na 5 sekund
print('Program closet')
