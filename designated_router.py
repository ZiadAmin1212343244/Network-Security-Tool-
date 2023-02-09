import paramiko
from netmiko import ConnectHandler
import time


# Function to get current DR in network
# input: routers --> int: Number of Routers in the Network
def Find_Current_DR(routers):
    CurrentRouter = 1
    while CurrentRouter < routers:  # Loop all routers until finding it
        hostname_prefix = "192.168.100"
        username = "admin"
        password = "admin"
        device_type = "cisco_ios"

        # This Function is to Find Current DR and Change it to Another one...
        # To find current DR we need to SSH Routers first, to check which one is the DR
        # Sometimes when we check a router, it may itself be the DR, so we need to check another one
        Flag_DR_Found = False

        CurrentDR = ""
        while not Flag_DR_Found:  # Loop until we find the Router
            RouterHostname = f"{hostname_prefix}.{CurrentRouter}"  # Updating Router Hostname that we will connect
            # with the current router in turn
            client = ConnectHandler(device_type=device_type, host=RouterHostname, username=username, password=password)
            # Showing ospf neighbors data using command 'show ip ospf neighbors'
            output = client.send_command('show ip ospf neighbor')
            print(output)

            if output:  # if no error happened, we extract the output
                output_lines = output.split('\n')  # splitting output to lines
                for line in output_lines:
                    if "FULL/DR   " in line:  # if DR is found
                        Flag_DR_Found = True
                        result = " ".join(line.split())  # Replace all spaces with only one space
                        CurrentDR_IP = result.split()[4]
                        CurrentDR_Priority = result.split()[1]
                        RouterFoundDR = CurrentRouter  # To make it the new DR
                        client.disconnect()
                        return CurrentDR_IP, CurrentDR_Priority, RouterFoundDR
            CurrentRouter += 1  # Check in the Next Router
        client.disconnect()
        return None, None


# Function to Change the DR of the network
# Inputs:
# router_number: int: the required router to be the new DR
# old_dr_priority: int: the priority of the old DR
# no_of_routers: int: the number of routers in the network
def Change_DR(router_number, old_dr_priority, no_of_routers):
    hostname_prefix = "192.168.100"
    username = "admin"
    password = "admin"
    device_type = "cisco_ios"

    RouterHostname = f"{hostname_prefix}.{router_number}"
    client = ConnectHandler(device_type=device_type, host=RouterHostname, username=username, password=password)
    print(client.read_channel())
    client.write_channel("enable\n")
    time.sleep(0.5)
    client.write_channel("admin\n")
    time.sleep(0.2)
    print("Enable Mode...")

    cfg_list = ["interface FastEthernet 0/0",
                f"ip ospf priority {int(old_dr_priority) + 1}"]
    cfg_output = client.send_config_set(cfg_list)
    print(cfg_output)
    client.save_config()
    client.disconnect()
    print("Increased Priority of the Router......")
    time.sleep(1)

    print("Now Resetting OSPF in all Routers...")
    for i in range(1, no_of_routers + 1):
        print("R" + str(i))
        RouterHostname = f"{hostname_prefix}.{i}"
        client = ConnectHandler(device_type=device_type, host=RouterHostname, username=username, password=password)
        # Enable Mode
        client.write_channel("enable\n")
        time.sleep(0.5)
        client.write_channel("admin\n")
        time.sleep(0.2)
        print(client.read_channel())
        print("Enable Mode...")
        client.write_channel("clear ip ospf process\n")
        time.sleep(0.3)
        print(client.read_channel())
        client.write_channel("yes\n")
        time.sleep(0.5)
        print(client.read_channel())
        client.disconnect()
