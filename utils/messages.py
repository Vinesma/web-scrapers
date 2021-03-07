from sys import stdin

def status(message, status=None, prefix="", suffix=""):
    """
    Show a status message to the user, the current action is represented in brackets.
    """
    if status is not None:
        print(f"{prefix}[{status}] {message}{suffix}")
    else:
        print(f"{prefix}{message}{suffix}")

def question_str(message):
    """
    Prints a question that the user must answer
        args = A question string to display
        return -> A string typed by the user
    """
    print(message)
    response = stdin.readline().rstrip()

    return response

def question_int(message):
    """
    Prints a question that the user must answer
        args = A question string to display
        return -> An integer typed by the user
    """
    print(message)
    response = stdin.readline().rstrip()

    return int(response)

def question_bool(message):
    """
    Prints a question that the user must answer
        args = A question string to display
        return -> A boolean value corresponding to yes or no
    """
    print(f"{message} (y/n)")
    response = stdin.readline().rstrip()

    if response.lower() == 'y':
        return True

    return False