from enum import Enum


class ActivityType(Enum):
    RUNNING = 'RUNNING'
    SWIMMING = 'SWIMMING'
    CYCLING = 'CYCLING'


class AdminPremiumAction(Enum):
    GRANT_PREMIUM = 'GRANT_PREMIUM'
    REVOKE_PREMIUM = 'REVOKE_PREMIUM'


class AdminUserAction(Enum):
    BLOCK = 'BLOCK'
    UNBLOCK = 'UNBLOCK'
