from .. import mongo_db
# TODO: Only fetch austin great area
# TODO: Remove static once implemented noncluster algorithm to programatically seperate the region
austin_great_area = ['Austin', 'West Lake Hills',
                     'Jollyville', 'Wells Branch', 'Round Rock']

# TODO: Research if MongoEngine abstraction is fit for ORM with route data


class Route:
    @staticmethod
    def get_all_routes():
        collections = mongo_db.routes
        get_austin_routes_query = collections.find(
            {'city': {'$in': austin_great_area}}
        )
        return list(get_austin_routes_query)
