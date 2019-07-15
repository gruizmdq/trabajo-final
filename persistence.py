import pymongo
import constants as CONSTANTS



class Persistence():
    host = CONSTANTS.DATABASE_HOST
    db = pymongo.MongoClient(CONSTANTS.DATABASE_HOST)[CONSTANTS.DATABASE_NAME]
    DETECTIONS = CONSTANTS.COLLECTION_DETECTIONS
    NOTIFICATIONS = CONSTANTS.COLLECTION_NOTIFICATIONS
    
    @staticmethod   
    def insert_detection(detection):
        result = Persistence.db[Persistence.DETECTIONS].insert_one(detection)
        return result.acknowledged
    @staticmethod   
    def get_notifications():
        a = list(Persistence.db[Persistence.NOTIFICATIONS].find())
        n = {}
        for aux in a:
            n[aux['person']] = aux['notification']
        return n
    
    @staticmethod   
    def remove_prediction(camera, name, date):
        prediction = {"camera": int(camera), "name": name, "date": date}
        result = Persistence.db[Persistence.DETECTIONS].delete_one(prediction)
        return result.acknowledged