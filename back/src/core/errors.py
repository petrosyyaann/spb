from fastapi import HTTPException, status


def with_errors(*errors: HTTPException):
    d = {}
    for err in errors:
        if err.status_code in d:
            d[err.status_code]["description"] += f"\n\n{err.detail}"
        else:
            d[err.status_code] = {"description": err.detail}
    return d


def server_overloaded():
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                         detail='Server overloaded!')


def undefined_server_error():
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail='Undefined server behavior occurred!')


def invalid_credentials():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Invalid credentials")


def unauthorized():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Need authorization")


def token_expired():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Token expired")


def token_validation_failed():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Bad token specified")


def access_denied():
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                         detail="Access denied!")


def password_too_weak():
    return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                         detail="Password too weak!")


def auth_data_is_not_unique():
    return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                         detail="Auth data not unique!")
