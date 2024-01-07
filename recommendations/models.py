
from django.db import models
from django.contrib.auth.models import User


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendations = models.TextField()

    def __str__(self):
        return f"Recommendations for {self.user.username}"
    

class Result(models.Model):
    antecedent = models.TextField()
    consequent = models.TextField()
    support = models.FloatField()
    confidence = models.FloatField()

    def __str__(self):
        return f'{self.antecedent} -> {self.consequent} (Support: {self.support}, Confidence: {self.confidence})'
    


