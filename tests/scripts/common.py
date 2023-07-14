import datetime
import os

SSH_PRIVATE_KEY_FILE="id_rsa"
SSH_PUBLIC_KEY_FILE="id_rsa.pub"
ANSIBLE_PROJECT_HOME=os.environ['PG_ANSIBLE_HOME']
ANSIBLE_TEST_HOME=os.path.join(ANSIBLE_PROJECT_HOME, "tests")

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=Singleton):
    def __del__(self):
        self.log_file.flush()
        self.log_file.close()

    def init(self, debug):
        self.log_file = open(f"{ANSIBLE_TEST_HOME}/trace.log", "w", buffering=1, encoding="utf-8")
        self.debug_level = debug

    def get_log_header(self):
        return f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{os.getpid()}]"

    def info(self, msg):
        msg = f"{self.get_log_header()} INFO: {msg}\n"
        self.log_file.write(msg)

    def debug(self, msg):
        if self.debug_level:
            msg = f"{self.get_log_header()} DEBUG: {msg}\n"
            self.log_file.write(msg)
