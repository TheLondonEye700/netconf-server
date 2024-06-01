from paramiko import SubsystemHandler, Channel
from loguru import logger
import threading
import xml.etree.ElementTree as ET
from typing import List

XML_HELLO = """<?xml version="1.0" encoding="UTF-8"?><nc:hello xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><nc:capabilities><nc:capability>urn:ietf:params:netconf:base:1.0</nc:capability><nc:capability>urn:ietf:params:netconf:base:1.1</nc:capability><nc:capability>urn:ietf:params:netconf:capability:writable-running:1.0</nc:capability></nc:capabilities></nc:hello>]]>]]>"""


def create_ok_rep(msg_id):
    return f'<rpc-reply message-id="{msg_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/></rpc-reply>'
    # return f'<?xml version="1.0" encoding="UTF-8"?><rpc-reply message-id="{msg_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/></rpc-reply>'


def create_config_reply(msg_id):
    return f'<nc:rpc-reply message-id="{msg_id}" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">bla data</data></nc:rpc-reply>'
    # return f'<?xml version="1.0" encoding="UTF-8"?><rpc-reply message-id="{msg_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><data>bla data</data></rpc-reply>'


class NetconfHandler(SubsystemHandler):
    def __init__(self, channel, name, server):
        self.channel = channel
        SubsystemHandler.__init__(self, channel, name, server)

    def _wait_for(self, channel: Channel, length: int):
        captured_bytes: List[bytes] = []
        while len(captured_bytes) < length:
            received_msg = channel.recv(65535)
            captured_bytes.append(received_msg)
        return captured_bytes

    def start_subsystem(self, name: str, transport, channel) -> None:
        logger.success(f"{name} handler started. Sending hello message")

        # --- send hello message on subsystem request ---
        channel.send(XML_HELLO.strip())

        # --- handle request ---
        try:
            captured_bytes = self._wait_for(channel, 2)
            # logger.warning(f"hello xml: {captured_bytes[0]}")
            operation_req = captured_bytes[1]
            self.handle_request(operation_req)
        except TimeoutError:
            logger.error("Does not receive message")

        # --- return when request processing is finished ---

    def _get_rpc_operation(self, root: ET.Element):
        namespace = root.tag.split("}")[0][1:]
        # logger.info(f"{namespace=}\n")

        OPERATIONS = ["get-config", "edit-config"]
        for operation in OPERATIONS:
            operation_string = f".//{{{namespace}}}{operation}"
            # logger.error(find_string)
            found_element = root.find(operation_string)
            if found_element:
                return operation

    def handle_request(self, request: bytes):
        rpc = request.decode()[6:-4]
        logger.info(f"Handle {rpc=}\n")

        root = ET.fromstring(rpc)
        id = root.get("message-id")
        operation = self._get_rpc_operation(root)
        # logger.info(f"{operation=}\n")

        if operation == "get-config":
            CONFIG_REPLY = create_config_reply(id)
            config = f"\n#{len(CONFIG_REPLY)}\n" + CONFIG_REPLY + "\n##\n"
            self.channel.send(config)
        elif operation == "edit-config":
            logger.warning("edit-config not supported yet")

    def finish_subsystem(self):
        logger.info(9, f"NETCONFsubsys: finish_subsystem")
        threading.current_thread().daemon = True
        super(NetconfHandler, self).finish_subsystem()
        logger.info(9, "NETCONF subsys finished")
