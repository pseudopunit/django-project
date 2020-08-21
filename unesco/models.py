from django.db import models

class Category(models.Model) :
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class State(models.Model) :
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class Description(models.Model) :
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class Iso(models.Model) :
    name = models.CharField(max_length=8)

    def __str__(self) :
        return self.name

class Justification(models.Model) :
    name = models.CharField(max_length=256, null=True)

    def __str__(self) :
        return self.name

class Region(models.Model) :
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class Site(models.Model):
    name = models.CharField(max_length=128)
    year = models.IntegerField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    area_hectares = models.FloatField(null=True)
    description = models.ForeignKey(Description, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    iso = models.ForeignKey(Iso, on_delete=models.CASCADE)
    justification = models.ForeignKey(Justification, on_delete=models.CASCADE, null=True)

    def __str__(self) :
        return self.name


