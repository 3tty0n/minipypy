class W_TypeError(Exception):
    pass


class OperationError(Exception):
    pass


def oefmt(err, msg):
    raise err(msg)
