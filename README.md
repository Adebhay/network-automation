README.md (Main Project Documentation)


Enterprise Network Automation & Health Check Framework


Project Overview

This project delivers a fully automated, secure, and resilient enterprise network management framework. It is designed to manage a redundant collapsed-core network architecture and can be directly adapted for production use on Cisco Catalyst 9200L switches. The system uses Python and Netmiko to interact with network devices via SSH.

The framework is composed of two primary automation modules:

Zero-Touch Provisioning (`autonomous-agent.py`): Deploys a complete, security-hardened production configuration to network switches without any manual CLI input, reducing deployment time from hours to seconds.

Automated Health Check (`health-check.py`): Collects critical operational data (CPU, memory, licenses, NTP, SNMP, etc.) and generates a comprehensive report, enabling proactive monitoring and audit compliance.

Key Features

| Feature | Description |

Zero‑Touch Provisioning (ZTP) | Core and Access switches receive complete production configuration automatically from a single Python script.

Out‑of‑Band Management | All management traffic flows through a dedicated VLAN (99) and a dedicated Management Switch, completely isolated from user data. 

High Availability  | Dual-Core switches are configured with HSRP to provide gateway redundancy and eliminate single points of failure.

Security Isolation (VRF)  | Management traffic is placed in a dedicated VRF (`MGMT`), creating a logical "air gap" that prevents production VLANs from routing to management interfaces.

Automated Health Checks  | Collects model, serial, version, CPU, memory, licenses, NTP, SNMP, and interface descriptions from all devices.

Configuration Backup & Audit Trail | Automatically backs up every device's running configuration to timestamped files and logs all automation actions.




🏗️ Architecture

<img width="458" height="422" alt="Network Topology" src="https://github.com/user-attachments/assets/59002dbc-7b8d-4541-acf7-98dffc3b6dea" />

The lab environment simulates a real-world enterprise network with a redundant collapsed-core design:

2 x Core Switches (Cisco IOL L3): Act as the network backbone and HSRP gateways.

2 x Access Switches (Cisco IOL L3): Simulate Cisco 9200L access layer switches.

1 x Management Switch (Cisco IOL L2): Provides an isolated OOB network and acts as a DHCP server for device management.

 1 x Management Cloud: Bridges the virtual lab to the host PC's network.


🛠️ Technologies & Tools

Automation: Python 3, Netmiko

Version Control: Git, GitHub

Virtualization: VMware Workstation, Pnetlab (EVE-NG Community)

Network OS: Cisco IOS (IOL images)


🗺️ Network Addressing Plan

Network | VLAN | Subnet | Gateway |

External (VMnet8) | N/A | `192.168.x.x/24` | `192.168.x.x` 

OOB Management | 99 | `10.99.x.x/24` | `10.99.x.x` (HSRP Virtual) 

Finance Users | 10 | `10.10.x.x/24` | `10.10.x.x` (HSRP Virtual)

Engineering Users | 20 | `10.20.x.x/24` | `10.20.x.x` (HSRP Virtual)

 📁 Project Structure

C:\NetAutoProject

├── backups\ Timestamped configuration backups
├── logs\ Session logs and audit trails
├── reports\ Health check reports
├── devices.csv\ Device inventory
├── autonomous-agent.py\ Zero-touch provisioning script
├── health_check.py\ Automated health check script
└── README.md\ This documentation


🚀 Installation

Prerequisites

Python 3.8+ with `pip`

Netmiko library

Git (optional, for version control)

Network devices running Cisco IOS/IOS‑XE


Step 1: Clone or Download the Repository

```bash

git clone https://github.com/yourusername/network-automation.git

cd network-automation


Step 2: Install Python Dependencies

pip install netmiko

Step 3: Prepare Device Inventory

Create a devices.csv file in the project root:

hostname,ip,device_type,username,password,secret,port

Core-SW1,192.168.X.X,cisco_ios,yourusername,yourpassword,yourpassword,22

Core-SW2,192.168.X.X,cisco_ios,yourusername,yourpassword,yourpassword,22

ACC-SW1,10.99.X.X,cisco_ios,yourusername,yourpassword,yourpassword,22

ACC-SW2,10.99.X.X,cisco_ios,yourusername,yourpassword,yourpassword,22

🎮 Usage

Zero‑Touch Provisioning

Deploy full production configuration to all devices:

python autonomous-agent.py


Select option 3 for full deployment and backup.


Automated Health Check

Generate a comprehensive health report for all devices:

python health-check.py

The report is saved to reports/health-report-YYYYMMDD-HHMMSS.txt.

Configuration Backup Only

python autonomous-agent.py


Select option 2 for backup only.


Configuration Details

Core Switch Configuration (Deployed Automatically)

Component	Configuration

VRF	         MGMT for management traffic isolation

VLANs	       10 (Finance), 20 (Engineering), 99 (OOB Management)

HSRP	       Group 2 (external), Group 1 (OOB), Groups 10/20 (production)

OSPF	       Area 0, router‑id 1.1.1.1 (primary) / 2.2.2.2 (secondary)

NAT	         Overload for OOB network (10.99.99.0/24)

Security     SSH only, no HTTP server, login banner



Access Switch Configuration (Deployed Automatically)

Component    Configuration

VLANs	         10, 20

Trunk Ports	   Uplinks to both Core switches

Access Ports	 Port‑security, BPDU Guard, PortFast

Security	 SSH v2, no HTTP, exec‑timeout


Health Check Metrics

The health check script collects:

Device model and serial number
Software version and uptime
License summary
CPU and memory utilization
NTP status and associations
SNMP configuration
Interface descriptions
Backup file existence





