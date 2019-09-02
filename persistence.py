import pymongo
import constants as CONSTANTS



class Persistence():
    host = CONSTANTS.DATABASE_HOST
    db = pymongo.MongoClient(CONSTANTS.DATABASE_HOST)[CONSTANTS.DATABASE_NAME]
    DETECTIONS = CONSTANTS.COLLECTION_DETECTIONS
    NOTIFICATIONS = CONSTANTS.COLLECTION_NOTIFICATIONS
    CAMERAS = CONSTANTS.COLLECTION_CAMERAS
    PEOPLE = CONSTANTS.COLLECTION_PEOPLE

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

    @staticmethod
    def add_camera(url, name):
        if Persistence.db[Persistence.CAMERAS].find_one({"url": url}) is None:
            id_camera = Persistence.db[Persistence.CAMERAS].find().count()
            camera = {"name": name, "id_camera": id_camera, "url": url}
            if Persistence.db[Persistence.CAMERAS].insert_one(camera):
                return camera
            else:
                return False
        else:
            return 'URL ya existente'

    @staticmethod
    def get_cameras():
        return list(Persistence.db[Persistence.CAMERAS].find())

    @staticmethod
    def get_personas():
        return list(Persistence.db[Persistence.PEOPLE].find())