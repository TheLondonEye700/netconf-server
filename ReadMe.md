# NETCONF server

The repository implements a custom NETCONF server that responds to NETCONF requests from client. NETCONF is a protocol used for network managent that use SSH as network transport layer. Messages transmitted via NETCONF is RPC messages encoded in XML.


## Usage

Runs the application from `ssh_server.py`. This handles the SSH connection establishment authentication and other bookeeping via Python [paramiko](https://www.paramiko.org/) library. Create RSA key and pass the key file name as argument to `SshServer`.

NETCONF request is managed via `netconf_server.py`. The handler currently supports `get-config` and `edit-config` request with static response and requires further development.


Test the server via `simple_client.py`. The goal should be that the server being functional and responsive to NETCONF client request via `ncclient` library (example in `client_test.py`)