import datetime
from app.models.admin.model import Admin
from app.models.additional_models import Admin_User, Admin_Premium
from app.models.premium.controller import PremiumController
from app.models.premium.model import Premium
from app.database import db
from app.models.user.controller import UserController
from app.models.user.model import User


class AdminService:

    def modify_admin_action(self, admin_id, request_data):
        user_id = request_data['user_id']
        action = request_data['action']
        user = UserController.get_by_id(user_id)

        if not user:
            return {"success": False, "message": "User not found"}, 404

        if action == "BLOCK":
            return self._block_user(admin_id, user)

        elif action == "UNBLOCK":
            return self._unblock_user(admin_id, user)

        elif action == "REVOKE_PREMIUM":
            return self._revoke_premium(admin_id, user)

        else:
            return {"success": False, "message": "Invalid action"}, 400

    def _block_user(self, admin_id, user):
        user.is_blocked = True
        self._add_admin_user_data(admin_id, user.id, "BLOCK")
        db.session.commit()
        return {"success": True, "action": "BLOCK"}, 200

    def _unblock_user(self, admin_id, user):
        user.is_blocked = False
        self._add_admin_user_data(admin_id, user.id, "UNBLOCK")
        db.session.commit()
        return {"success": True, "action": "UNBLOCK"}, 200

    def _revoke_premium(self, admin_id, user):
        premium = Premium.query.filter(
            Premium.user_id == user.id,
            Premium.start_date <= datetime.utcnow(),
            Premium.end_date >= datetime.utcnow(),
        ).order_by(
            Premium.start_date.desc(),
            Premium.end_date.desc(),
        ).first()

        if not premium:
            return {"success": False, "message": "No valid premium found"}, 404

        premium.end_date = datetime.utcnow()
        self._add_admin_premium_data(admin_id, premium.id, "REVOKE_PREMIUM")
        db.session.commit()
        return {"success": True, "action": "REVOKE_PREMIUM"}, 200

    def _add_admin_user_data(self, admin_id, user_id, action):
        admin = Admin.query.get(admin_id)
        user = User.query.get(user_id)

        if not admin:
            raise ValueError("Admin not found")

        if not user:
            raise ValueError("User not found")
        admin_user_data = Admin_User(admin_id=admin_id, user_id=user_id, action=action)
        db.session.add(admin_user_data)
        db.session.commit()

    def _add_admin_premium_data(self, admin_id, premium_id, action):
        admin = Admin.query.get(admin_id)
        premium = Premium.query.get(premium_id)

        if not admin:
            raise ValueError("Admin not found")

        if not premium:
            raise ValueError("Premium not found")

        admin_premium_data = Admin_Premium(admin_id=admin_id, premium_id=premium_id, action=action)
        db.session.add(admin_premium_data)
        db.session.commit()

    def grant_premium_admin_action(self, admin_id, user_id):
        new_premium = PremiumController.create(user_id)
        db.session.add(new_premium)
        db.session.commit()
        self._add_admin_premium_data(admin_id, new_premium.id, "GRANT_PREMIUM")
        return {"success": True, "action": "GRANT_PREMIUM"}, 200

