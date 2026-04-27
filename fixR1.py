from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios",
    "host": "198.51.100.1",     
    "username": "netman",   
    "password": "netman", 
    "secret": "netman", 
}

my_commands = [
    "interface GigabitEthernet2/0",
    "ip address 198.52.100.2 255.255.255.0",
    "no shutdown",
]

conn = ConnectHandler(**R1)
conn.enable()

print("\nApplying config...")
output = conn.send_config_set(my_commands)
print(output)

conn.disconnect()