import json

def formatMessage(type, nick, text=None):

    if type == "chat":
        return json.dumps({"type": type, "nick": nick, "message": text}).encode()

    return json.dumps({"type": type, "nick": nick}).encode()