#
# Copyright 2016 Kenichi Sato
#

class FreeeException(Exception):
    pass


class FreeeAccessTokenNotSet(FreeeException):
    pass


class FreeeResponseError(FreeeException):
    pass
