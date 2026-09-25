import ctypes
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

HEALTH_URL = "http://127.0.0.1:8000/health"
STARTUP_TIMEOUT_SECONDS = 20


def show_error(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(
        None,
        message,
        "SupportFlow AI",
        0x10,
    )


def get_application_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    project_directory = Path(__file__).resolve().parents[1]
    return project_directory / "release" / "SupportFlowAI"


def backend_is_ready() -> bool:
    try:
        with urlopen(HEALTH_URL, timeout=1) as response:
            return response.status == 200
    except (URLError, TimeoutError, OSError):
        return False


def stop_backend(backend_process: subprocess.Popen[bytes]) -> None:
    if backend_process.poll() is not None:
        return

    backend_process.terminate()

    try:
        backend_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        backend_process.kill()
        backend_process.wait()


def main() -> None:
    application_directory = get_application_directory()

    backend_executable = application_directory / "backend" / "SupportFlowBackend.exe"

    desktop_executable = application_directory / "desktop" / "SupportFlowAI.exe"

    if not backend_executable.exists():
        show_error(
            "No se encontró el componente interno del servidor.\n\n"
            f"Ruta esperada:\n{backend_executable}"
        )
        return

    if not desktop_executable.exists():
        show_error(
            "No se encontró la aplicación de escritorio.\n\n"
            f"Ruta esperada:\n{desktop_executable}"
        )
        return

    backend_process = None

    try:
        if not backend_is_ready():
            backend_process = subprocess.Popen(
                [str(backend_executable)],
                cwd=backend_executable.parent,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS

            while time.monotonic() < deadline:
                if backend_is_ready():
                    break

                if backend_process.poll() is not None:
                    show_error(
                        "El servidor interno de SupportFlow AI "
                        "se cerró inesperadamente."
                    )
                    return

                time.sleep(0.25)
            else:
                show_error("SupportFlow AI no pudo iniciar su servidor interno.")
                return

        desktop_process = subprocess.Popen(
            [str(desktop_executable)],
            cwd=desktop_executable.parent,
        )
        desktop_process.wait()

    except OSError as error:
        show_error("No fue posible iniciar SupportFlow AI.\n\n" f"Detalle: {error}")

    finally:
        if backend_process is not None:
            stop_backend(backend_process)


if __name__ == "__main__":
    main()
