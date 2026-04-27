from netmiko import ConnectHandler

R1_IP = "198.51.100.1"
R2_IP = "198.52.100.2" 
R3_IP = "198.53.100.1"

USERNAME = "netman"
PASSWORD = "netman"
SECRET = "netman"

r1 = {
    "device_type": "cisco_ios",
    "host": R1_IP,
    "username": USERNAME,
    "password": PASSWORD,
    "secret": SECRET,
}

conn = ConnectHandler(**r1)
conn.enable()

print("Connected to R1")
output = conn.send_command_timing("show ip interface brief")
print(output)
print("-----")
# Noticed ethernet2 has wrong ip address. 

# SSH from R1 to R2
print("SSH from R1 to R2...")
output = conn.send_command_timing(f"ssh -l {USERNAME} {R2_IP}")

if "yes/no" in output:
    output += conn.send_command_timing("yes")

if "Password" in output or "password" in output:
    output += conn.send_command_timing(PASSWORD)

print(output)

print("trying command on R2")
output = conn.send_command_timing("show ip interface brief")
print(output)

# Now SSH from R2 to R3
print("\nSSH from R2 to R3...")
output = conn.send_command_timing(f"ssh -l {USERNAME} {R3_IP}")

if "yes/no" in output:
    output += conn.send_command_timing("yes")

if "Password" in output or "password" in output:
    output += conn.send_command_timing(PASSWORD)

print(output)

print("trying command on R3...")
output = conn.send_command_timing("show ip interface brief")
print(output)

conn.disconnect()