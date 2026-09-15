import logging

# encoding='utf-8'
logging.basicConfig(filename="cyprus.log", level=logging.INFO)
logging.info("starting simulation")


class Singleton:
    __instance = None

    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args)
        return cls.__instance


class Base(Singleton):
    # the globals

    def __init__(self) -> None:
        self.rule_table = {}
        self.membrane_table = {}
        self.state_rule_applied = True

    def membrane_name_in_use(self, name: str) -> bool:
        # retval=false means name is not already used and
        # therefore can be used
        retval = False

        if self.membrane_table.get(name, None):
            retval = True

        return retval


def get_base() -> Base:
    return Base()


def log_info(msg: str) -> None:
    logging.info(msg)


def log_warning(msg: str) -> None:
    logging.warning(msg)


def log_debug(msg: str) -> None:
    logging.debug(msg)


def log_error(msg: str) -> None:
    logging.error(msg)


def log(msg: str) -> None:
    log_info.info(msg)
