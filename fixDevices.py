from netmiko import ConnectHandler


R1_IP = "198.51.100.1"
R2_IP = "198.52.100.2" 
R3_IP = "198.53.100.1"

USERNAME = "netman"
PASSWORD = "netman"
SECRET = "netman"

r1_conn_configs = {
    "device_type": "cisco_ios",
    "host": R1_IP,
    "username": USERNAME,
    "password": PASSWORD,
    "secret": SECRET,
}

R1_commands = [
    "interface GigabitEthernet2/0",
    "ip address 198.52.100.1 255.255.255.0",
    "no shutdown",
]

R1_commands_2 = [
    "router ospf 1",
    "network 198.51.100.0 0.0.0.255 area 0"
]

R2_commands = [
    "configure terminal",
    "interface GigabitEthernet2/0",
    "no shutdown",
    "end",
    "write memory",
]

R3_commands = [
    "configure terminal",
    "interface Loopback0",
    "ip ospf 1 area 0",
    "end",
    "write memory"
]

conn = ConnectHandler(**r1_conn_configs)
conn.enable()

print("Applying R1 config")
output = conn.send_config_set(R1_commands)
print(output)

print("Applying R1 OSPF config")
output = conn.send_config_set(R1_commands_2)
print(output)

print("SSH from R1 to R2")
output = conn.send_command_timing(f"ssh -l {USERNAME} {R2_IP}")

if "yes/no" in output:
    output += conn.send_command_timing("yes")

if "Password" in output or "password" in output:
    output += conn.send_command_timing(PASSWORD)

print(output)

print("Applying R2 config")
for command in R2_commands:
    output = conn.send_command_timing(command, delay_factor=2)
    print(output)


print("SSH from R2 to R3")
output = conn.send_command_timing(f"ssh -l {USERNAME} {R3_IP}")

if "yes/no" in output:
    output += conn.send_command_timing("yes")

if "Password" in output or "password" in output:
    output += conn.send_command_timing(PASSWORD)

print(output)

print("Applying R3 config")
for command in R3_commands:
    output = conn.send_command_timing(command, delay_factor=2)
    print(output)

conn.disconnect()