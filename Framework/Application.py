from Framework import availableApplications

class Application:
    def __init__ (self, label, name, url, image):
        self.label = label
        self.name = name
        self.url = url
        self.image = image
        availableApplications[label] = self