from scapy.all import *
from netmiko import ConnectHandler

StopEvent = Event()
trusted_macs = {}


# Converting MAC Address Format from 'ca01.2528.0000' to be 'ca:01:25:28:00:00'
def formatting_mac(mac_address):
    mac = mac_address.replace(".", "")
    mac_parts = [mac[i:i + 2] for i in range(0, len(mac), 2)]
    return ':'.join(mac_parts)


# First Step: Connecting using SSH to any router in the network to get the trusted MAC addresses
def get_all_mac_addresses():
    # Connecting to Router1
    client = ConnectHandler(device_type='cisco_ios', host='192.168.100.1', username='admin', password='admin')
    output = client.send_command('show arp')  # Command that get All Connected Devices MAC addresses
    if output:
        print("Output of Show ARP command")
        print(output)  # Showing Output
        print("-------------------------------------------------------")

        # Parsing the Output to get only MAC Addresses and put them in a Dictionary
        trusted_macs = {}
        output_lines = output.split('\n')[1:]  # Parsing all output except first line
        for line in output_lines:
            result = " ".join(line.split())  # Reducing Multiple Spaces in output into one space
            IP = result.split()[1]
            MAC = result.split()[3]
            MAC = formatting_mac(MAC)
            # Adding the MAC address to the dictionary of trusted macs
            trusted_macs[IP] = MAC

        print("Trusted MAC Addresses:")
        print(trusted_macs)
        print('------------------------------------------------------')
        return trusted_macs


# Function to Handle Packets Sniffed using Scapy
def sniff_packets(pkt):
    global trusted_macs
    try:
        # Showing Packets (IP of Src and DST)
        if pkt[IP]:
            print(f"Src IP: {pkt[IP].src}  --> Dst IP: {pkt[IP].dst}")
        # Showing Packets (MAC of Src and DST)
        if pkt[Ether]:
            Src_MAC = pkt[Ether].src
            Dst_MAC = pkt[Ether].dst
            print(f"Src MAC: {Src_MAC}  --> Dst MAC: {Dst_MAC}")
            # Checking if Both SRC and DST are in Trusted MACS
            if Src_MAC not in trusted_macs.values():
                print(f"ALARM!!!, {Src_MAC} is not in the Trusted MAC ADDRESSES")
                # GO To AI Application
                Send_To_AI()  # TODO: Later
    except:
        pass
    print("------------------------------------------------------------------------------")


# Function of AI to handle Threats (Wrong Mac Addresses)
def Send_To_AI():
    pass


# Function to Start Sniffing Packets
def start_sniffing():
    global trusted_macs
    print("Sniffing Started")
    trusted_macs = get_all_mac_addresses()
    print(trusted_macs)
    sniff(prn=sniff_packets, iface="Microsoft KM-TEST Loopback Adapter")