from app.exceptions.exceptions import InvalidRoleException, NotFoundException
from app.models.admin.model import Admin
from app.models.user.model import User


class EntityService:
    @staticmethod
    def find_entity_by_role(entity_id, role):
        if role == 'user':
            entity = User.query.filter(User.id == entity_id).first()
        elif role == 'admin':
            entity = Admin.query.filter(Admin.id == entity_id).first()
        else:
            raise InvalidRoleException("Invalid role")
        if not entity:
            raise NotFoundException("Entity not found")

        return entity
