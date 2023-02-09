from designated_router import *
from check_mac_address import *
import time

import threading

DR_Flag = False


def Start_Designated_Router():
    global DR_Flag
    Number_Of_Routers = 6
    DR_IP, Priority, FoundBy = Find_Current_DR(Number_Of_Routers)
    print("----------------------------------------------------------")
    print("Current DR IP is: " + DR_IP)
    print("Current Designated Router is: ", DR_IP.split(".")[-1])
    print("DR Priority is: " + Priority)
    print("----------------------------------------------------------")
    print("Changing Designated Router to Another Router..")
    router_number = int(input(
        f"Please Select the Router you want to be the Designated Router.. Choose from (1-{Number_Of_Routers}):    "))

    Change_DR(router_number, Priority, Number_Of_Routers)
    time.sleep(3)
    print("-------------------------------------")
    print(f"Designated Router is Changed to Router{router_number}")
    print('-------------------------------------------------')

    DR_Flag = True  # Indicating that DR has Finished and Start Waiting for Countdown to restart..


def Start_Packet_Checker():
    print('START SNIFFING')
    print('---------------------------------------')
    start_sniffing()


t1 = threading.Thread(target=Start_Designated_Router)
t2 = threading.Thread(target=Start_Packet_Checker)

t1.start()  # Starting the Thread to Change DR
while True:
    if DR_Flag == True:
        break

t2.start()  # Starting the Thread to Check MAC
