# =============================================================================
#  AUTONOMOUS ENTERPRISE NETWORK DEPLOYMENT SCRIPT
# =============================================================================

import csv
import datetime
import os
import logging
from netmiko import ConnectHandler

# === Setup Logging ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename='logs/network_automation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_devices(csv_file):
    devices = []
    try:
        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                devices.append(row)
        print(f"[INFO] Loaded {len(devices)} devices from {csv_file}.")
        return devices
    except FileNotFoundError:
        print(f"[ERROR] Inventory file '{csv_file}' not found.")
        return []

def backup_config(device):
    try:
        print(f"[*] Backing up {device['hostname']} ({device['ip']})...")
        netmiko_device = {
            'device_type': device['device_type'],
            'host': device['ip'],
            'username': device['username'],
            'password': device['password'],
            'secret': device['secret'],
            'port': int(device['port']),
            'global_delay_factor': 2,
            'conn_timeout': 30,
            'auth_timeout': 30,
            'banner_timeout': 30,
            'session_log': f"logs/{device['hostname']}_backup_session.log"
        }
        connection = ConnectHandler(**netmiko_device)
        connection.enable()
        output = connection.send_command("show running-config", expect_string=r'[#>]', read_timeout=30)
        hostname = connection.find_prompt().strip('#> ')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("backups", exist_ok=True)
        filename = f"backups/{hostname}_{timestamp}.cfg"
        with open(filename, 'w') as f:
            f.write(output)
        print(f"   ✅ Backup saved: {filename}")
        connection.disconnect()
        return True
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return False

def generate_core_config(hostname):
    if hostname == "Core-SW1":
        return [
            "vrf definition MGMT", " rd 100:99", " address-family ipv4", " exit",
            "vlan 10", " name USER-FINANCE",
            "vlan 20", " name USER-ENGINEERING",
            "vlan 99", " name OOB-MGMT",
            "interface Ethernet0/0", " description EXTERNAL-HSRP", " no switchport",
            " ip address 192.168.52.140 255.255.255.0",
            " standby version 2", " standby 2 ip 192.168.52.100", " standby 2 priority 110",
            " standby 2 preempt", " standby 2 authentication md5 key-string Ha-Shem123", " no shutdown",
            "interface Ethernet0/1", " description LINK-TO-MGMT-SW", " switchport mode access",
            " switchport access vlan 99", " no shutdown",
            "interface Vlan99", " description OOB-GATEWAY", " vrf forwarding MGMT",
            " ip address 10.99.99.12 255.255.255.0",
            " standby version 2", " standby 1 ip 10.99.99.1", " standby 1 priority 110",
            " standby 1 preempt", " standby 1 authentication md5 key-string Ha-Shem123", " no shutdown",
            "interface Vlan10", " description FINANCE-GATEWAY", " ip address 10.10.10.2 255.255.255.0",
            " standby version 2", " standby 10 ip 10.10.10.1", " standby 10 priority 110", " standby 10 preempt", " no shutdown",
            "interface Vlan20", " description ENGINEERING-GATEWAY", " ip address 10.20.20.2 255.255.255.0",
            " standby version 2", " standby 20 ip 10.20.20.1", " standby 20 priority 110", " standby 20 preempt", " no shutdown",
            "interface Ethernet0/2", " description TRUNK-TO-ACC-SW1", " switchport trunk encapsulation dot1q",
            " switchport mode trunk", " switchport trunk allowed vlan 10,20", " no shutdown",
            "interface Ethernet0/3", " description TRUNK-TO-ACC-SW2", " switchport trunk encapsulation dot1q",
            " switchport mode trunk", " switchport trunk allowed vlan 10,20", " no shutdown",
            "interface Ethernet1/0", " description LINK-TO-Core-SW2", " no switchport",
            " ip address 10.0.0.1 255.255.255.252", " no shutdown",
            "router ospf 1", " router-id 1.1.1.1",
            " network 10.0.0.0 0.0.0.3 area 0", " network 10.10.10.0 0.0.0.255 area 0",
            " network 10.20.20.0 0.0.0.255 area 0", " passive-interface default",
            " no passive-interface Ethernet1/0",
            "ip route vrf MGMT 0.0.0.0 0.0.0.0 192.168.52.1",
            "interface Ethernet0/0", " ip nat outside",
            "interface Vlan99", " ip nat inside",
            "access-list 1 permit 10.99.99.0 0.0.0.255",
            "ip nat inside source list 1 interface Ethernet0/0 vrf MGMT overload"
        ]
    else:
        return [
            "vrf definition MGMT", " rd 100:99", " address-family ipv4", " exit",
            "vlan 10", " name USER-FINANCE",
            "vlan 20", " name USER-ENGINEERING",
            "vlan 99", " name OOB-MGMT",
            "interface Ethernet0/0", " description EXTERNAL-HSRP", " no switchport",
            " ip address 192.168.52.145 255.255.255.0",
            " standby version 2", " standby 2 ip 192.168.52.100", " standby 2 priority 100",
            " standby 2 preempt", " standby 2 authentication md5 key-string Ha-Shem123", " no shutdown",
            "interface Ethernet0/3", " description LINK-TO-MGMT-SW", " switchport mode access",
            " switchport access vlan 99", " no shutdown",
            "interface Vlan99", " description OOB-GATEWAY", " vrf forwarding MGMT",
            " ip address 10.99.99.13 255.255.255.0",
            " standby version 2", " standby 1 ip 10.99.99.1", " standby 1 priority 100",
            " standby 1 preempt", " standby 1 authentication md5 key-string Ha-Shem123", " no shutdown",
            "interface Vlan10", " description FINANCE-GATEWAY", " ip address 10.10.10.3 255.255.255.0",
            " standby version 2", " standby 10 ip 10.10.10.1", " standby 10 priority 100", " standby 10 preempt", " no shutdown",
            "interface Vlan20", " description ENGINEERING-GATEWAY", " ip address 10.20.20.3 255.255.255.0",
            " standby version 2", " standby 20 ip 10.20.20.1", " standby 20 priority 100", " standby 20 preempt", " no shutdown",
            "interface Ethernet0/1", " description TRUNK-TO-ACC-SW1", " switchport trunk encapsulation dot1q",
            " switchport mode trunk", " switchport trunk allowed vlan 10,20", " no shutdown",
            "interface Ethernet0/2", " description TRUNK-TO-ACC-SW2", " switchport trunk encapsulation dot1q",
            " switchport mode trunk", " switchport trunk allowed vlan 10,20", " no shutdown",
            "interface Ethernet1/0", " description LINK-TO-Core-SW1", " no switchport",
            " ip address 10.0.0.2 255.255.255.252", " no shutdown",
            "router ospf 1", " router-id 2.2.2.2",
            " network 10.0.0.0 0.0.0.3 area 0", " network 10.10.10.0 0.0.0.255 area 0",
            " network 10.20.20.0 0.0.0.255 area 0", " passive-interface default",
            " no passive-interface Ethernet1/0",
            "ip route vrf MGMT 0.0.0.0 0.0.0.0 192.168.52.1",
            "interface Ethernet0/0", " ip nat outside",
            "interface Vlan99", " ip nat inside",
            "access-list 1 permit 10.99.99.0 0.0.0.255",
            "ip nat inside source list 1 interface Ethernet0/0 vrf MGMT overload"
        ]

def generate_access_config(hostname):
    return [
        "vlan 10", " name USER-FINANCE",
        "vlan 20", " name USER-ENGINEERING",
        "interface range Ethernet0/0-1", " description TRUNK-TO-CORE",
        " switchport trunk encapsulation dot1q", " switchport mode trunk",
        " switchport trunk allowed vlan 10,20", " no shutdown",
        "interface Ethernet0/2", " description ENDPOINT-PORT", " switchport mode access",
        " switchport access vlan 10", " spanning-tree portfast", " spanning-tree bpduguard enable", " no shutdown",
        "no ip http server", "no ip http secure-server", "ip ssh version 2",
        "service password-encryption", "banner login ^C UNAUTHORIZED ACCESS PROHIBITED ^C",
        "line vty 0 15", " exec-timeout 5 0", " transport input ssh"
    ]

def deploy_full_config(device):
    try:
        print(f"[*] Deploying full config to {device['hostname']} ({device['ip']})...")
        netmiko_device = {
            'device_type': device['device_type'],
            'host': device['ip'],
            'username': device['username'],
            'password': device['password'],
            'secret': device['secret'],
            'port': int(device['port']),
            'global_delay_factor': 3,
            'conn_timeout': 30,
            'auth_timeout': 30,
            'banner_timeout': 30,
            'session_log': f"logs/{device['hostname']}_deploy_session.log"
        }
        connection = ConnectHandler(**netmiko_device)
        connection.enable()
        hostname = device['hostname']
        if "Core" in hostname:
            config_commands = generate_core_config(hostname)
        else:
            config_commands = generate_access_config(hostname)

        connection.config_mode()
        connection.send_config_set(config_commands, cmd_verify=False, delay_factor=2)
        connection.exit_config_mode()
        connection.save_config()

        print(f"   ✅ Full configuration deployed to {hostname}")
        connection.disconnect()
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("   AUTONOMOUS ENTERPRISE NETWORK DEPLOYMENT")
    print("="*60)
    devices = load_devices("devices.csv")
    if not devices:
        return
    print("\nSelect operation:")
    print("1. Deploy Full Configuration to All Switches")
    print("2. Backup All Configurations")
    print("3. Full Deployment + Backup")
    choice = input("Enter choice (1/2/3): ")
    for dev in devices:
        if choice in ('1', '3'):
            deploy_full_config(dev)
        if choice in ('2', '3'):
            backup_config(dev)
    print("\n[COMPLETE] Check logs/network_automation.log for details.")

if __name__ == "__main__":
    main()