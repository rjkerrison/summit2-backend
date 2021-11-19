from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import DateTimeField, IntegerField
from django.db.models import Count
from django.db.models.fields.json import DataContains
from rest_framework import serializers
from itertools import groupby
# Create your models here.


# class User(models.Model):


# 1 user can have many groups
# 1 group can have many exercises
class User(AbstractUser):
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField(verbose_name='email',
                              max_length=50)
    # exercise_group = models.CharField(max_length=100, blank=True, null=True)

    def build_user_programme(self):
        # 1 - get all exercise logs for user
        userlog = UserExerciseLog.objects.filter(
            user=self,).order_by("date_completed")
        print(userlog)
        # Here we're calling the variables in the model to be displayed / combined in the user data
        serialize_user_logs = [

            {'exercise_weight': x.exercise_weight,
             'date_completed': x.date_completed,
             'exercise_name': x.exercise.exercise_name,
             'programme': x.exercise.programme.name if x.exercise.programme else 'none',
             'sets': x.sets,
             'id': x.id,
             'exercise_id': x.exercise_id,
             'reps_per_set': x.reps_per_set} for x in userlog]

        # exercise id

        grouped_logs = groupby(serialize_user_logs, lambda x: x['programme'])
        # list(v) creates an array
        programme_log_groups = {k: list(v) for k, v in grouped_logs}

        return {'Activities': programme_log_groups}


class Programme(models.Model):
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class Exercise(models.Model):

    exercise_name = models.CharField(max_length=50, blank=True, null=True)
    programme = models.ForeignKey(
        Programme, related_name='exercise', on_delete=models.CASCADE, null=True)


class UserExerciseLog(models.Model):
    user = models.ForeignKey(User, related_name='exercise_log',
                             on_delete=models.CASCADE, blank=True)  # , related_name='user'
    exercise = models.ForeignKey(
        Exercise, related_name='userlog', on_delete=models.CASCADE)
    exercise_weight = models.IntegerField(default=0)
    date_completed = models.DateTimeField(auto_now=True)
    sets = models.IntegerField(default=0)
    reps_per_set = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user}{self.exercise}{self.exercise_weight}{self.date_completed}{self.sets}{self.reps_per_set}'
