MikroTik RouterOS Skill for OpenClaw

An OpenClaw Skill for connecting to and managing MikroTik RouterOS devices through the API.

Features

- View device status, including system information, CPU, memory, and storage
- View firewall rules, including filter, NAT, and mangle
- View network configuration, including interfaces, IP addresses, routes, and DNS
- Run custom RouterOS commands
- Support connections to multiple devices
- Scan the network, similar to Winbox, with no pre-configuration required
- Interactive first-time setup flow

Quick Start for New Users

Option 1: Interactive setup (recommended)

1. Say the trigger command:
mikrotik setup

2. AI automatically scans the network:
Scan complete! Found 3 devices:

[1] 192.168.1.10 (00:0C:42:AA:BB:CC)
[2] 192.168.1.20 (4C:5E:0C:DD:EE:FF)
[3] 192.168.1.1 (D4:CA:6D:11:22:33)

3. Tell the AI the username and password:
Use admin with no password for all devices

4. AI tests the connection and saves the configuration:
Connection successful! Configuration saved to TOOLS.md

5. Start using it:
Check device1 status
mikrotik office firewall

Option 2: Manual configuration

Add the following to ~/.openclaw/workspace/TOOLS.md:

### MikroTik Devices
- office: 192.168.1.1, admin, no password
- home: 192.168.88.1, admin, yourpassword

Installation

Method 1: Manual installation (available now)

# Clone the repository
git clone https://github.com/YOUR_USERNAME/openclaw-mikrotik-skill.git
cd openclaw-mikrotik-skill

# Copy to the OpenClaw skills directory
cp -r mikrotik /usr/lib/node_modules/openclaw/skills/

# Restart OpenClaw Gateway
openclaw gateway restart

Method 2: Via ClawHub (coming soon)

# Available after publishing to ClawHub
npx clawhub install mikrotik

Configuration

Add your MikroTik device information to TOOLS.md:

### MikroTik Devices

- office: 192.168.1.1, admin, no password
- home: 192.168.88.1, admin, yourpassword

Usage

Natural language commands

Check MikroTik device status
Show MikroTik firewall configuration
Check router health
Show network interfaces
Show wireless clients
mikrotik office clients
mikrotik ap wifi
Run /system/resource/print on MikroTik

Available commands

- status: View device status, including CPU, memory, and uptime
- firewall: View firewall rules, including filter and NAT
- interface / interfaces: View the list of network interfaces
- client / clients / wireless / wifi: View connected wireless clients (CAPsMAN)
- route / routes: View the routing table
- dhcp: View DHCP configuration and leases
- arp: View the ARP table
- traffic: View interface traffic statistics
- wireguard / wg: View WireGuard tunnel status
- scan: Scan LAN devices with no configuration required

Command-line tool

cd mikrotik-api
python3 cli.py 192.168.1.1 status
python3 cli.py 192.168.1.1 firewall
python3 cli.py 192.168.1.1 interfaces
python3 cli.py 192.168.1.1 routes

Python API

from mikrotik_api import MikroTikAPI, QuickCommands

with MikroTikAPI('192.168.1.1') as api:
    api.login()
    quick = QuickCommands(api)
    quick.print_status()

Example output

Device status

MikroTik RouterOS Device Status
============================================================
  Device Name: OFFICE
  Version: 7.21.2 (stable)
  Uptime: 1w2d9h9m39s
  CPU: MIPS 1004Kc V2.15 @ 880MHz
  CPU Load: 1%
  Memory: 61.6MB / 256.0MB
  Storage: 3.6MB / 16.0MB
============================================================

Wireless clients (new in v1.8.1)

Wireless Clients (CAPsMAN)
============================================================

2 wireless clients connected:

[Client 1]
  MAC: 00:11:22:33:44:55
  SSID: MyWiFi | Interface: cap2
  Signal: -49
  Rate: TX 702Mbps-80MHz/2S | RX 585Mbps-80MHz/2S
  Connected Time: 1d47m
  IP Address: 192.168.1.101
  Traffic: TX 1.8GB / RX 1.2GB

[Client 2]
  MAC: AA:BB:CC:DD:EE:FF
  SSID: MyWiFi | Interface: cap2
  Signal: -34
  Rate: TX 866.6Mbps-80MHz/2S/SGI | RX 702Mbps-80MHz/2S
  Connected Time: 20m
  IP Address: 192.168.1.102
  Traffic: TX 29.7MB / RX 892KB

Dependencies

- Python 3.6+
- OpenClaw 2026.3.2+
- MikroTik RouterOS API enabled, default port 8728

Notes

1. Make sure the RouterOS API service is enabled. Check with /ip/service/print
2. Default API port is 8728, SSL port is 8729
3. Devices with no password present a security risk
4. Some commands require administrator privileges

File structure

mikrotik/
├── SKILL.md
├── handler.py
├── README.md
└── mikrotik-api/
    ├── __init__.py
    ├── client.py
    ├── commands.py
    ├── cli.py
    └── README.md

Development

Testing

cd mikrotik-api
python3 cli.py 192.168.1.1 status

Adding new features

1. Add a new method in commands.py
2. Add command handling in handler.py
3. Update the SKILL.md documentation

Contributing

Issues and pull requests are welcome.

License

MIT License

Author

Xia Ge

Related links

OpenClaw Documentation: https://docs.openclaw.ai
MikroTik API Documentation: https://help.mikrotik.com/docs/display/ROS/API
ClawHub: https://clawhub.com