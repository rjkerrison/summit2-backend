from rest_framework import serializers
from .models import Exercise, Programme, User, UserExerciseLog
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import make_password
from rest_framework.fields import ReadOnlyField, SerializerMethodField
from django.core.exceptions import ValidationError
User = get_user_model()


# class UserSerializer(serializers.ModelSerializer): - might need to use this?
class UserSerializer(serializers.ModelSerializer):
    # class UserSerializer(serializers.HyperlinkedModelSerializer):

    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    def validate(self, data):

        # remove the password and password confirmation from the request body
        password = data.pop('password')
        password_confirmation = data.pop('password_confirmation')

        # check if the passwords match
        if password != password_confirmation:
            raise ValidationError(
                {'password_confirmation': 'Passwords do not match'})

        # check if the password is valid
        try:
            password_validation.validate_password(password=password)
        except ValidationError as err:
            raise ValidationError({'password': err.messages})

        # hash the password, and add back to the dictionary
        data['password'] = make_password(password)

        return data

    programmes = serializers.ReadOnlyField(
        source="build_user_programme")

    class Meta:
        model = User

        fields = ('id', 'username', 'email',
                  'password', 'password_confirmation', 'programmes')  # exercise_grouping


class ProgrammeSerializer(serializers.ModelSerializer):
    # Here we call the user serializer..

    class Meta:
        # ..to combine the user and programme fields
        model = Programme
        fields = ('id', 'name')  # user?


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        # programme or programmeS?
        fields = ('id', 'exercise_name', 'programme')


class UserExerciseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExerciseLog
        fields = ('user', 'exercise', 'exercise_weight',
                  'date_completed', 'sets', 'reps_per_set', 'id')
