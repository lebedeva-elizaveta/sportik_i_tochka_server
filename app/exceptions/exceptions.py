class InvalidTokenException(Exception):
    """Исключение для недействительного токена"""
    pass


class InvalidPasswordException(Exception):
    """Исключение для неправильного пароля"""
    pass


class NotFoundException(Exception):
    """Исключение для случаев, когда что-то не найдено"""
    pass


class InvalidRoleException(Exception):
    """Исключение, когда роль пользователя некорректная"""
    pass


class InvalidActionException(Exception):
    """Исключение, когда чье-то действие некорректно
    (если не существует такого)"""
    pass


class ActionIsNotAvailableException(Exception):
    """Исключение, если действие недоступно в данный момент"""
    pass


class AlreadyExistsException(Exception):
    """Исключение, если нарушено требование уникальности"""
    pass
