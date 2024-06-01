import paramiko
from loguru import logger


class SshServerInterface(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_subsystem_request(self, channel, name):
        logger.info(f"Request subsystem {name=}")

        transport = channel.get_transport()
        HandlerClass, handlerInterface, kwarg = transport._get_subsystem_handler(name)
        if HandlerClass is None:
            return False

        handler: paramiko.SubsystemHandler = HandlerClass(channel, name, self)  # type: ignore

        # start the handler thread
        # start_subsystem() will be called after running this thread
        handler.start()

        return True

    def check_auth_password(self, username, password):
        if (username == "admin") and (password == "password"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
