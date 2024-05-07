from enum import Enum


class ActivityType(Enum):
    RUNNING = 'RUNNING'
    SWIMMING = 'SWIMMING'
    CYCLING = 'CYCLING'


class AdminAction(Enum):
    BLOCK = 'BLOCK'
    UNBLOCK = 'UNBLOCK'
    GRANT_PREMIUM = 'GRANT_PREMIUM'
    REVOKE_PREMIUM = 'REVOKE_PREMIUM'
