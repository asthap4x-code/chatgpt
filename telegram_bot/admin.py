def is_admin(user_id,config):return user_id is not None and int(user_id) in config.admin_ids
