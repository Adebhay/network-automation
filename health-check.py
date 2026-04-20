# =============================================================================
#  NETWORK DEVICE HEALTH CHECK AUTOMATION
#  Collects: Model, Serial, Version, CPU, Memory, Licenses, NTP, SNMP, etc.
# =============================================================================

import csv
import datetime
import os
import logging
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# === Setup Logging ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename='logs/health_check.log',
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
        return devices
    except FileNotFoundError:
        print(f"[ERROR] Inventory file '{csv_file}' not found.")
        return []

def get_device_facts(connection):
    """Collect basic device information."""
    version_output = connection.send_command("show version")
    license_output = connection.send_command("show license summary", expect_string=r'[#>]')
    clock_output = connection.send_command("show clock")

    # Parse hostname, model, serial, version from show version
    lines = version_output.splitlines()
    hostname = "Unknown"
    model = "Unknown"
    serial = "Unknown"
    version = "Unknown"
    for line in lines:
        if " uptime is " in line:
            hostname = line.split()[0]
        if "Model Number" in line:
            model = line.split(":")[-1].strip()
        elif "System serial number" in line:
            serial = line.split(":")[-1].strip()
        if "Cisco IOS Software" in line:
            version = line.strip()
            break

    return {
        'hostname': hostname,
        'model': model,
        'serial': serial,
        'version': version,
        'license': license_output.strip()[:200] + "..." if len(license_output) > 200 else license_output.strip(),
        'clock': clock_output.strip()
    }

def get_performance_metrics(connection):
    """Collect CPU and memory utilization."""
    cpu_output = connection.send_command("show processes cpu sorted | include CPU utilization")
    mem_output = connection.send_command("show processes memory sorted | include Processor Pool")

    cpu_util = "N/A"
    for line in cpu_output.splitlines():
        if "CPU utilization" in line:
            cpu_util = line.strip()
            break

    mem_util = "N/A"
    for line in mem_output.splitlines():
        if "Processor Pool" in line:
            mem_util = line.strip()
            break

    return {'cpu': cpu_util, 'memory': mem_util}

def get_ntp_status(connection):
    """Collect NTP status and associations."""
    ntp_status = connection.send_command("show ntp status", expect_string=r'[#>]')
    ntp_assoc = connection.send_command("show ntp associations", expect_string=r'[#>]')
    return {'ntp_status': ntp_status.strip(), 'ntp_assoc': ntp_assoc.strip()}

def get_snmp_config(connection):
    """Collect SNMP configuration."""
    snmp_group = connection.send_command("show snmp group", expect_string=r'[#>]')
    snmp_community = connection.send_command("show snmp community", expect_string=r'[#>]')
    return {'snmp_group': snmp_group.strip(), 'snmp_community': snmp_community.strip()}

def get_interface_descriptions(connection):
    """Collect interface descriptions."""
    intf_desc = connection.send_command("show interfaces description", expect_string=r'[#>]')
    return intf_desc.strip()

def check_backup_exists(hostname):
    """Check if a recent backup file exists in the backups folder."""
    backups_dir = "backups"
    if not os.path.exists(backups_dir):
        return "No backups folder"
    today = datetime.datetime.now().strftime("%Y%m%d")
    for filename in os.listdir(backups_dir):
        if hostname in filename and today in filename:
            return f"Backup exists: {filename}"
    return "No backup found for today"

def perform_health_check(device):
    """Execute full health check for a single device."""
    try:
        print(f"[*] Health check for {device['hostname']} ({device['ip']})...")
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
            'banner_timeout': 30
        }
        connection = ConnectHandler(**netmiko_device)
        connection.enable()

        facts = get_device_facts(connection)
        perf = get_performance_metrics(connection)
        ntp = get_ntp_status(connection)
        snmp = get_snmp_config(connection)
        interfaces = get_interface_descriptions(connection)
        backup_status = check_backup_exists(facts['hostname'])

        connection.disconnect()

        # Combine all data
        health_data = {**facts, **perf, **ntp, **snmp,
                       'interfaces': interfaces, 'backup_status': backup_status}
        return health_data
    except NetmikoTimeoutException:
        print(f"   ❌ Timeout connecting to {device['ip']}.")
        return None
    except NetmikoAuthenticationException:
        print(f"   ❌ Authentication failed for {device['ip']}.")
        return None
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return None

def generate_report(all_results):
    """Generate a formatted text report."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("NETWORK DEVICE HEALTH CHECK REPORT")
    report_lines.append(f"Generated: {timestamp}")
    report_lines.append("=" * 80)

    for result in all_results:
        if result is None:
            continue
        report_lines.append(f"\n--- {result['hostname']} ({result.get('model', 'N/A')}) ---")
        report_lines.append(f"Serial Number : {result.get('serial', 'N/A')}")
        report_lines.append(f"Software      : {result.get('version', 'N/A')[:60]}...")
        report_lines.append(f"Current Time  : {result.get('clock', 'N/A')}")
        report_lines.append(f"CPU           : {result.get('cpu', 'N/A')}")
        report_lines.append(f"Memory        : {result.get('memory', 'N/A')}")
        report_lines.append(f"License       : {result.get('license', 'N/A')}")
        report_lines.append(f"NTP Status    : {result.get('ntp_status', 'N/A').splitlines()[0] if result.get('ntp_status') else 'N/A'}")
        report_lines.append(f"SNMP Groups   : {result.get('snmp_group', 'N/A').splitlines()[0] if result.get('snmp_group') else 'N/A'}")
        report_lines.append(f"Backup Status : {result.get('backup_status', 'N/A')}")
        report_lines.append("\nInterface Descriptions (sample):")
        intf_lines = result.get('interfaces', '').splitlines()[:10]
        for line in intf_lines:
            report_lines.append(f"  {line}")
        report_lines.append("-" * 40)

    # Write to file
    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/health_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w') as f:
        f.write("\n".join(report_lines))

    # Also print to console
    print("\n".join(report_lines))
    print(f"\n[INFO] Report saved to {report_filename}")

def main():
    print("\n" + "="*60)
    print("   NETWORK DEVICE HEALTH CHECK")
    print("="*60)
    devices = load_devices("devices.csv")
    if not devices:
        return

    all_results = []
    for dev in devices:
        result = perform_health_check(dev)
        if result:
            print(f"   ✅ Health check completed for {dev['hostname']}")
            all_results.append(result)
        else:
            print(f"   ❌ Health check failed for {dev['hostname']}")

    if all_results:
        generate_report(all_results)
    else:
        print("[ERROR] No successful health checks.")

if __name__ == "__main__":
    main()