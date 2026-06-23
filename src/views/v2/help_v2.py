from flask_restful import Resource


class HelpV2(Resource):
    """
    Returns basic help information for the IARI API.
    """

    def get(self):
        return {
            "name": "IARI API",
            "description": "Help endpoint for available API routes and basic usage.",
            "endpoints": {
                "/version": {
                    "method": "GET",
                    "description": "Returns the current IARI API version."
                },
                "/help": {
                    "method": "GET",
                    "description": "Returns help information for the API."
                }
            }
        }, 200
