from ncclient import manager
from loguru import logger
import xml.dom.minidom

if __name__ == "__main__":
    m = manager.connect(
        host="127.0.0.1",
        port=830,
        username="admin",
        password="password",
        hostkey_verify=False,
        look_for_keys=False,
        device_params={"name": "default"},
    )

    logger.info("Connected to host, getting config")

    config = m.get_config("running")
    xmlDom = xml.dom.minidom.parseString(str(config))

    logger.info(f'\n{xmlDom.toprettyxml(indent="  ")}')
