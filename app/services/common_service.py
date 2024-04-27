from app.database import db

from app.services.entity_service import EntityService


class CommonService:

    @staticmethod
    def get_current_data(entity_id, role):
        entity = EntityService.find_entity_by_role(entity_id, role)

        response = {
            "id": entity.id,
            "name": entity.name,
            "image": entity.avatar,
            "phone": entity.phone,
            "birthday": entity.birthday,
        }
        if hasattr(entity, "weight"):
            response["weight"] = entity.weight

        return response

    @staticmethod
    def change_user_data(entity_id, role, personal_data):
        entity = EntityService.find_entity_by_role(entity_id, role)

        entity.name = personal_data.get('name', entity.name)
        entity.avatar = personal_data.get('image', entity.avatar)
        entity.phone = personal_data.get('phone', entity.phone)
        entity.birthday = personal_data.get('birthday', entity.birthday)
        if hasattr(entity, "weight"):
            entity.weight = personal_data.get('weight', entity.weight)

        db.session.commit()
        response = {
            "success": True
        }
        return response
