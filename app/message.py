class Message:
    def __init__(self, msg):
        self.message = msg

    def __repr__(self):
        return self.message


class FlashMessage(Message):
    SUCCESS = 0x01
    INFO = 0x02
    WARNING = 0x03
    DANGER = 0x04

    def __init__(self, type=SUCCESS, message=""):
        super().__init__(message)
        self.type = type
