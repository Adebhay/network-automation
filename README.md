##### &#x20;**README.md (Main Project Documentation)**



\# Autonomous Enterprise Network Automation \& Health Check Framework



\[!\[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

\[!\[Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)



\## 🚀 Project Overview

This project delivers a fully automated, secure, and resilient enterprise network management framework. It is designed to manage a redundant collapsed-core network architecture and can be directly adapted for production use on Cisco Catalyst switches. The system uses Python and Netmiko to interact with network devices via SSH.



The framework is composed of two primary automation modules:

\*   \*\*Zero-Touch Provisioning (`autonomous-agent.py`):\*\* Deploys a complete, security-hardened production configuration to network switches without any manual CLI input, reducing deployment time from hours to seconds.

\*   \*\*Automated Health Check (`health-check.py`):\*\* Collects critical operational data (CPU, memory, licenses, NTP, SNMP, etc.) and generates a comprehensive report, enabling proactive monitoring and audit compliance.



\## 🎯 Key Features

\*   \*\*Zero-Touch Provisioning (ZTP):\*\* Automates the entire device configuration lifecycle based on a simple CSV inventory.

\*   \*\*Out-of-Band (OOB) Management:\*\* All management traffic flows through a dedicated VLAN (99) and a separate Management Switch, completely isolated from user data.

\*   \*\*High Availability:\*\* Dual Core switches are configured with HSRP to provide gateway redundancy and eliminate single points of failure.

\*   \*\*Security Isolation (VRF):\*\* Management traffic is placed in a dedicated VRF (`MGMT`), creating a logical "air gap" that prevents production VLANs from routing to management interfaces.

\*   \*\*Automated Health Checks:\*\* Replaces manual customer reporting with a scheduled Python script that audits device health and configuration compliance.

\*   \*\*Configuration Backup \& Audit Trail:\*\* Automatically backs up every device's running configuration to timestamped files and logs all automation actions.



\## 🏗️ Architecture



The lab environment simulates a real-world enterprise network with a redundant collapsed-core design:

\*   \*\*2 x Core Switches (Cisco IOL L3):\*\* Act as the network backbone and HSRP gateways.

\*   \*\*2 x Access Switches (Cisco IOL L3):\*\* Simulate Cisco 9200L access layer switches.

\*   \*\*1 x Management Switch (Cisco IOL L2):\*\* Provides an isolated OOB network and acts as a DHCP server for device management.

\*   \*\*1 x Management Cloud:\*\* Bridges the virtual lab to the host PC's network.



\## 🛠️ Technologies \& Tools

\*   \*\*Automation:\*\* Python 3, Netmiko

\*   \*\*Version Control:\*\* Git, GitHub

\*   \*\*Virtualization:\*\* VMware Workstation, Pnetlab (EVE-NG Community)

\*   \*\*Network OS:\*\* Cisco IOS (IOL images)



\## 🗺️ Network Addressing Plan

| Network | VLAN | Subnet | Gateway |

| :--- | :--- | :--- | :--- |

| External (VMnet8) | N/A | `192.168.52.0/24` | `192.168.52.1` |

| OOB Management | 99 | `10.99.99.0/24` | `10.99.99.1` (HSRP Virtual) |

| Finance Users | 10 | `10.10.10.0/24` | `10.10.10.1` (HSRP Virtual) |

| Engineering Users | 20 | `10.20.20.0/24` | `10.20.20.1` (HSRP Virtual) |





\## 🚀 Installation



\### Prerequisites

\- \*\*Python 3.8+\*\* with `pip`

\- \*\*Netmiko\*\* library

\- \*\*Git\*\* (optional, for version control)

\- Network devices running Cisco IOS/IOS‑XE (including Catalyst 9200L)



###### \### **Step 1: Clone or Download the Repository**

```bash

git clone https://github.com/yourusername/autonomous-network-automation.git

cd autonomous-network-automation



###### **Step 2: Install Python Dependencies**

pip install netmiko



###### **Step 3: Prepare Device Inventory**

**Create a devices.csv file in the project root:**



**hostname,ip,device\_type,username,password,secret,port**

**Core-SW1,192.168.X.X,cisco\_ios,yourusername,yourpassword,yourpassword,22**

**Core-SW2,192.168.X.X,cisco\_ios,yourusername,yourpassword,yourpassword,22**

**ACC-SW1,10.99.X.X,cisco\_ios,yourusername,yourpassword,yourpassword,22**

**ACC-SW2,10.99.X.X,cisco\_ios,yourusername,yourpassword,yourpassword,22**



##### **Zero‑Touch Provisioning**

**Deploy full production configuration to all devices:**

python autonomous\_agent.py



Select option 3 for full deployment and backup.





##### **Automated Health Check**

###### **Generate a comprehensive health report for all devices:**

**python health\_check.py**

**The report is saved to reports/health-report-YYYYMMDD-HHMMSS.txt.**



##### **Configuration Backup Only**

python autonomous\_agent.py



Select option 2 for backup only.



##### **Configuration Details**

###### **Core Switch Configuration (Deployed Automatically)**

**Component	Configuration**

**VRF	      MGMT for management traffic isolation**

**VLANs	      10 (Finance), 20 (Engineering), 99 (OOB Management)**

**HSRP	      Group 2 (external), Group 1 (OOB), Groups 10/20 (production)**

**OSPF	      Area 0, router‑id 1.1.1.1 (primary) / 2.2.2.2 (secondary)**

**NAT	      Overload for OOB network (10.99.99.0/24)**

**Security      SSH only, no HTTP server, login banner**



###### **Access Switch Configuration (Deployed Automatically)**

**Component	Configuration**

**VLANs	        10, 20**

**Trunk Ports	Uplinks to both Core switches**

**Access Ports	Port‑security, BPDU Guard, PortFast**

**Security	SSH v2, no HTTP, exec‑timeout**



##### **Health Check Metrics**

* **The health check script collects:**
* **Device model and serial number**
* **Software version and uptime**
* **License summary**
* **CPU and memory utilization**
* **NTP status and associations**
* **SNMP configuration**
* **Interface descriptions**
* **Backup file existence**





