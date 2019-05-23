import pymongo
import constants as CONSTANTS



class Persistence():
    host = CONSTANTS.DATABASE_HOST
    db = pymongo.MongoClient(CONSTANTS.DATABASE_HOST)[CONSTANTS.DATABASE_NAME]
    DETECTIONS = CONSTANTS.COLLECTION_DETECTIONS
    @staticmethod   
    def insert_detection(detection):
        
        Persistence.db[Persistence.DETECTIONS].insert_one(detection)
