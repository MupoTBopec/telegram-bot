class User:
    def __init__(self):
        self.current_state = 0  # new user
        self.id = None
        self.first_name = None
        self.last_name = None
        self.auth_token = None
        self.phone = None
        self.password = None
        self.location = None
        self.number_of_list = 1

        self.flag_room = None
        self.flag_lot = None

    def set_new_state(self, number):
        self.current_state = number

    def set_auth_token(self, token):
        self.auth_token = token

    def set_phone(self, phone):
        self.phone = phone

    def set_password(self, password):
        self.password = password

    def set_id(self, id):
        self.id = id

    def set_first_name(self, name):
        self.first_name = name

    def set_last_name(self, name):
        self.last_name = name

    def set_location(self, location):
        self.location = location

    def set_flag_room(self):
        self.flag_room = True
        self.flag_lot = False

    def set_flag_lot(self):
        self.flag_room = False
        self.flag_lot = True

    def set_number_of_list(self, number):
        self.number_of_list = number

    def get_current_state(self):
        return self.current_state

    def get_auth_token(self):
        return self.auth_token

    def get_phone(self):
        return self.phone

    def get_password(self):
        return self.password

    def get_id(self):
        return self.id

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_location(self):
        return self.location

    def get_flag_room(self):
        return self.flag_room

    def get_flag_lot(self):
        return self.flag_lot

    def get_number_of_list(self):
        return self.number_of_list

    def iteration_number_of_list(self):
        self.number_of_list += 1