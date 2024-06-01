import socket
import time
from abc import ABC, abstractmethod
from sys import platform
from threading import Event, Thread

from loguru import logger
from paramiko import RSAKey, SSHException, Transport

from netconf_server import NetconfHandler
from server_interface import SshServerInterface


class ServerBase(ABC):
    def __init__(self):
        self._is_running = Event()  # thread-safe boolean
        self._socket = None  # a socket, used to listen to connection
        self._listen_thread = None  # thread that listen for connection

    def start(self, address="127.0.0.1", port=830, timeout=1):
        """
        create and set up socket connection on a Thread
        """
        if not self._is_running.is_set():
            self._is_running.set()

            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

            if platform == "linux" or platform == "linux2":
                self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)

            self._socket.settimeout(timeout)
            self._socket.bind((address, port))

            self._listen_thread = Thread(target=self._listen)
            self._listen_thread.start()

    def _listen(self):
        """
        wait for connection. When one is made, call connection handler
        """
        while self._is_running.is_set():
            try:
                self._socket.listen()
                client, addr = self._socket.accept()
                self.handle_connection(client)
            except socket.timeout:
                pass

    @abstractmethod
    def handle_connection(self, client: socket.socket):
        pass

    def stop(self):
        if self._is_running.is_set():
            self._is_running.clear()
            self._listen_thread.join()
            self._socket.close()


class SshServer(ServerBase):
    def __init__(self, host_key_file: str, host_key_file_password=None):
        super(SshServer, self).__init__()
        self._host_key = RSAKey.from_private_key_file(host_key_file, host_key_file_password)
        logger.success("SSH Server started")

    def handle_connection(self, client: socket.socket):
        try:
            transport_session = Transport(client)
            transport_session.add_server_key(self._host_key)
            transport_session.set_subsystem_handler("netconf", NetconfHandler, self)
            logger.info(f"Connected with {client.getpeername()}")

            try:
                transport_session.start_server(server=SshServerInterface())

                # channel = transport_session.accept()
                # while transport_session.is_active():
                # receive_msg = channel.recv(65535)
                # logger.error(f"{receive_msg=}")
                # time.sleep(1)

            except SSHException:
                logger.error("Something bad happen")
                return

        except:
            pass


if __name__ == "__main__":
    server = SshServer("id_rsa_copy")
    server.start()
