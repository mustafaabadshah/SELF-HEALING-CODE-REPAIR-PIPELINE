import logging
from backend.app.config import settings
from backend.app.sandbox.base import BaseSandbox, TestResult
from backend.app.sandbox.local_sandbox import LocalSandbox
from backend.app.sandbox.docker_sandbox import DockerSandbox

logger = logging.getLogger("sandbox.manager")


class SandboxManager:
    _instance: BaseSandbox = None

    @classmethod
    def get_sandbox(cls) -> BaseSandbox:
        if cls._instance is not None:
            return cls._instance

        mode = settings.use_docker_sandbox.lower()
        if mode == "docker":
            docker_sb = DockerSandbox()
            if docker_sb.is_available():
                cls._instance = docker_sb
                logger.info("Using Docker Sandbox")
                return cls._instance
            else:
                logger.warning("Docker requested but unavailable, falling back to LocalSandbox")
                cls._instance = LocalSandbox()
                return cls._instance

        elif mode == "local":
            logger.info("Using LocalSandbox as configured")
            cls._instance = LocalSandbox()
            return cls._instance

        else:  # "auto"
            docker_sb = DockerSandbox()
            if docker_sb.is_available():
                logger.info("Docker daemon active, using Docker Sandbox")
                cls._instance = docker_sb
            else:
                logger.info("Docker daemon not active, using isolated LocalSandbox")
                cls._instance = LocalSandbox()
            return cls._instance


def get_sandbox() -> BaseSandbox:
    return SandboxManager.get_sandbox()
