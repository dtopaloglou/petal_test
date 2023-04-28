import re
password_regex = r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])([a-zA-Z0-9@$!%*?&]{8,32})$"
def validate_password(password: str) -> bool:
    return True if re.match(password_regex, password) else False


def passwords_match(password: str, confirmed: str):
    return password == confirmed


