class Alert():
    count_id = 0
    
    def __init__(self, camera, person, email):
        self.id = Alert.count_id
        Alert.count_id += 1
        self.camera = camera
        self.email = email