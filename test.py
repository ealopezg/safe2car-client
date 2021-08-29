from config import Config
from system import System
import re
import time

config = Config('config.ini')
system = System(config)


def testCamera():
    print("Prueba camara... ",end = '')
    test = True
    try:
        photo = system.takePicture(save=True)
        if not photo:
            test = False
    except:
        test = False
    print(('✓' if test else '✗'))
    return test
    

def testPIR():
    test = True

    for i in range(len(system.pir)):
        print("Probando sensor "+str(i+1))
        system.pir[i].wait_for_motion()
        print("Sensor  "+str(i+1)+": ✓")
        test = test and True
    return True

def testSIM():
    if not system.checkSIM():
        print("SIM808 Apagada... Encendiendo SIM808")
        system.toggleSIM()
        time.sleep(10)
        if not system.checkSIM():
            print("SIM808 No se puede encender")
            return False
        else:
            print("SIM808 encendida")
    test = True
    makeTest = True
    op = 0
    while makeTest:
        print(
            '''
Prueba SIM808:
Elija una opción:
1 - Llamar a un número
2 - Enviar SMS
3 - Volver al menú
            '''
        )
        op = int(input("OPCION: "))
        if not (op >= 1 and op <= 3):
            print("Opción Incorrecta")
        else:
            if op == 1:
                print("Llamada de prueba")
                number = ""
                while not re.search(r"^9\d{8}$", number):
                    number = input("Ingrese el número de telefono, formato 911111111: ")
                print("Recuerde responder la llamada")
                system.makeCall(number)
                res = input("Recibió la respuesta? Puede demorarse algunos segundos (Si o No): ")
                test = test and (True if res.upper()[0]=='S' else False)
                op = 0
            elif op == 2:
                print("Mensaje de prueba")
                number = ""
                while not re.search(r"^9\d{8}$", number):
                    number = input("Ingrese el número de telefono, formato 911111111: ")
                system.sendSMS(number,"Este es una prueba")
                res = input("Recibió la respuesta? Puede demorarse algunos segundos (Si o No): ")
                test = test and (True if res.upper()[0]=='S' else False)
            elif op == 3:
                makeTest = False
    print("Prueba SIM808... %s" %('✓' if test else '✗'))
    return test

def testGPS():
    print("Probando GPS")
    test = True
    try:
        gps = system.getLocation()
        if gps != None:
            print("GPS: Latitud: %f Longitud: %f " % (gps[0],gps[1]) )
            test = True
    except:
        test = False
    print("Prueba GPS... %s" %('✓' if test else '✗'))
    return test

def testBuzzer():
    print("Probando Buzzer... ",end='')
    system.activateBuzzer()
    time.sleep(5)
    system.deactivateBuzzer()
    print('✓')
    return True

def menu():
    menu = True
    tests = []
    while menu:
        print(
            '''
Menu de prueba Safe2Car
Elegir una opcion:
1 - Camara
2 - Sensores PIR
3 - Sim808
4 - GPS
5 - Buzzer
6 - Salir
            '''
        )
        op = int(input("OPCION: "))
        if not (op >= 1 and op <= 6):
            print("Opción Incorrecta")
        else:
            if op == 1:
                test = testCamera()
                tests.append(['Camara',test])
            elif op == 2:
                test = testPIR()
                tests.append(['PIR',test])
            elif op == 3:
                test = testSIM()
                tests.append(['SIM808',test])
            elif op == 4:
                test = testGPS()
                tests.append(['GPS',test])
            elif op == 5:
                test = testBuzzer()
                tests.append(['BUZZER',test])
            elif op == 6:
                menu = False
    
    print("\nRESUMEN DE PRUEBAS: ")
    for test in tests:
        print(('✓' if test[1] else '✗')+' '+test[0])
    




if __name__ == "__main__":
    menu()