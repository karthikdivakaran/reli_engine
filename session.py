class Session:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
            cls._instance.user = None
        return cls._instance

    def set_user(self, user_info):
        self.user = user_info

    def get_user(self):
        return self.user
