from datetime import datetime


def get_test():
    now = datetime.utcnow()
    return f"Test now: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}"
