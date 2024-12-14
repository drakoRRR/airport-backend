from pymongo.collection import Collection
from bson.objectid import ObjectId


class ReviewRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def get_reviews_by_tour(self, tour_id: str):
        return list(self.collection.find({"tour_id": tour_id}))

    def add_review(self, review_data: dict):
        return self.collection.insert_one(review_data)


class ImageRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def get_images_by_tour(self, tour_id: str):
        return list(self.collection.find({"tour_id": tour_id}))

    def add_image(self, image_data: dict):
        return self.collection.insert_one(image_data)
