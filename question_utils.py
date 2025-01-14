# Exemple de création de classe en python
class Question():
	def init(self, title: str, image: str, position: int, possibleAnswer: str):
		self.title = title
		self.position = position
		self.image = image
		self.possibleAnswer = possibleAnswer