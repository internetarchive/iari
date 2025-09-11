# iari_utils.py

def iari_errors(e:Exception):
    return { "errors": [
                {
                    "error": type(e).__name__,
                    "details": str(e),
                },
            ]}

if __name__ == "__main__":
    print("iari_utils")
