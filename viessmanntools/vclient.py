from subprocess import PIPE, STDOUT, run
from tempfile import NamedTemporaryFile
from .config import ViessmannToolsConfig


class CommunicationGarbledError(Exception):
    def __init__(self):
        super().__init__("Communication with heater was garbled, try again")


class VclientError(Exception):
    def __init__(self, output):
        super().__init__(f"Vclient execution failed, output was:\n{output}")


class Vclient:
    def __init__(self, commands, config=None):
        if config is None:
            config = ViessmannToolsConfig.get_default_config()
        config = config["Vclient"]

        self._commands = commands
        self._path = config.get("path")
        self._host = config.get("vcontrold_host")
        self._timeout = config.getint("timeout")

        self._template = []
        for i in range(len(self._commands)):
            self._template.append(f"$R{i + 1}")

    def run(self):
        """Exec vclient and return its output"""

        with NamedTemporaryFile(prefix="vclientTemplate") as tmp_file:
            tmp_file.write(";".join(self._template).encode())
            tmp_file.flush()

            args = [
                self._path,
                "-h",
                self._host,
                "-c",
                ",".join(self._commands),
                "-t",
                tmp_file.name,
            ]

            result = run(
                args,
                stdout=PIPE,
                stderr=STDOUT,
                timeout=self._timeout,
                check=True,
                text=True,
            )

        result_lower = result.stdout.lower()
        if "framer: error 15" in result_lower:
            raise CommunicationGarbledError
        if "srv err" in result_lower or "error" in result_lower:
            raise VclientError(result.stdout)

        return result.stdout
