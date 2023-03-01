from flask_restful import Resource


class Reference(Resource):
    # TODO implement based on md5 id
    def get(self, id_=""):
        if not id_:
            return "No id given", 400
        else:
            # todo lookup and return based on id
            raise NotImplementedError()
