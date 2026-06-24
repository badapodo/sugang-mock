class ValidationError(RuntimeError):
    pass


def result(rule, passed, detail):
    return {"rule": rule, "passed": bool(passed), "detail": detail}

