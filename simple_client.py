import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the SSH server
ssh.connect(hostname="127.0.0.1", port=830, username="admin", password="password")

transport = ssh.get_transport()
chan = transport.open_session()
# # Create a custom subsystem handler

# Open a channel and start the subsystem
chan.send(b"client sending mess")
chan.invoke_subsystem("netconf")


while chan.recv_ready():
    receive_msg = chan.recv(65535).decode()
    print(f"{receive_msg=}")

# custom_subsystem_handler.start_subsystem(channel)
