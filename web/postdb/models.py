from django.db import models


class WebInfo(models.Model):
    name = models.CharField(max_length=20)
    count = models.IntegerField()

    def __str__(self):
        return 'name: {}, count: {}'.format(self.name, self.count)


class PostInfo(models.Model):
    NID = models.IntegerField()
    TID = models.CharField(max_length=20)
    time = models.DateTimeField()
    category = models.CharField(max_length=20)
    title = models.TextField()
    content = models.TextField()
    plain = models.TextField()
    url = models.TextField()
    sourceLink = models.TextField()
    sourceText = models.TextField()

    def __str__(self):
        return 'NID: {}, TID: {}, title: {}, time: {}, url: {}'.format(self.NID, self.TID, self.title, self.time, self.url)


class IndexInfo(models.Model):
    key = models.TextField()
    value = models.TextField()  # json

    def __str__(self):
        return 'key: {}'.format(self.key)


class PostRelation(models.Model):
    NID = models.IntegerField()
    relation = models.TextField()

    def __str__(self):
        return 'NID: {}, relation: {}'.format(self.NID, self.relation)
