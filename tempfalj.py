from getpass import getpass

import paramiko

print("executing: ls")
# output = subprocess.Popen(["queue_run2.py " + create_command(conf)],
#                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
# out, err = output.communicate()
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
username = input("Felhasználónév: ")
password = getpass("Jelszó: ")
client.connect("10.63.192.69", 22, username, password)

# Parancs kiadása
stdin, stdout, stderr = client.exec_command("ls ")
out = stdout.read().decode('utf-8')

print(out)
# out = out.replace("\"", "").replace("\'", "").replace("\n", " ")
input()