from git import Repo
from loguru import logger

from loader import config
from Package.customutils import save_config


def check_on_update():
    config.updated = check_repo_on_update("../.git")
    save_config(config)


def check_repo_on_update(path: str) -> bool:
    repo = Repo(path)

    current = str(repo.head.commit)  # repo class to string
    last_commit = config.last_commit
    config.last_commit = current
    save_config(config)

    if current != last_commit:
        logger.warning(f"Repo updated!")
        return True
    else:
        logger.info(f"Repo not updated!")
        return False
