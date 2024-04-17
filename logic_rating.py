from datetime import datetime

import pytz

from models import db, Activity

moscow_tz = pytz.timezone('Europe/Moscow')


def get_user_rating(user_id):
    start_of_month = datetime.now(moscow_tz).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    users_dist = db.session.query(Activity.user_id, db.func.sum(Activity.distance)). \
        filter(Activity.date >= start_of_month). \
        group_by(Activity.user_id).all()
    sorted_users_dist = sorted(users_dist, key=lambda x: x[1], reverse=True)
    user_place = None
    for idx, (uid, _) in enumerate(sorted_users_dist, start=1):
        if uid == user_id:
            user_place = idx
            break
    return user_place
