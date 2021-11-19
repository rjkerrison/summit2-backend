from django.shortcuts import redirect, render
from django.urls import reverse
from django.shortcuts import render
from .models import Exercise, Programme, User, UserExerciseLog
from .serializers import ExerciseSerializer, UserSerializer, ProgrammeSerializer, UserExerciseLogSerializer
from rest_framework import response, request
from django.shortcuts import render
from django.contrib.auth import login
from user.templates.users.forms import CustomUserCreationForm
# import requests

from rest_framework import serializers, views, response, status, exceptions


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.conf import settings
from .serializers import UserSerializer
import jwt

# Create your views here.

User = get_user_model()


class RegisterPage(APIView):

    def post(self, request):
        user_to_create = UserSerializer(data=request.data)
        if user_to_create.is_valid():
            user_to_create.save()
            return Response({'message': 'Registration Successful'}, status=status.HTTP_202_ACCEPTED)
        return Response(user_to_create.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LoginPage(APIView):

    def post(self, request):

        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user_to_login = User.objects.get(username=username)
        except User.DoesNotExist:
            raise PermissionDenied(detail='User does not exist')
        if not user_to_login.check_password(password):
            raise PermissionDenied(detail='password not working')

        dt = datetime.now() + timedelta(days=7)
        token = jwt.encode(
            {'sub': user_to_login.id, 'exp': int(dt.strftime('%s'))},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        print(token)
        return Response({'token': token, 'message': f"Welcome back {user_to_login.username}, id is: {user_to_login.id}"})


def index(request):
    list = Exercise.objects.all()
    context = {'user': list}
    return render(request, 'index.html', context)


def dashboard(request):
    return render(request, "users/dashboard.html")


class ProgrammeListView (views.APIView):

    def get(self, request):
        exercise = Programme.objects.all()
        serialized_exercise = ProgrammeSerializer(
            exercise, many=True, context={'request', request}
        )
        return response.Response(serialized_exercise.data, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        programme_to_add = ProgrammeSerializer(data=request.data)
        if programme_to_add.is_valid():
            programme_to_add.save()
            return response.Response(programme_to_add.data, status=status.HTTP_201_CREATED)

        return response.Response(
            programme_to_add.errors, status=status.HTTP_400_BAD_REQUEST
        )


class ProgrammeDetailView (views.APIView):

    def get_programme_by_id(self, id):
        try:
            return Programme.objects.get(id=id)
        except Programme.DoesNotExist:
            raise exceptions.NotFound(detail="exercise does not exist")

    def delete(self, request, id):
        exercise = self.get_programme_by_id(id)
        exercise.delete()
        return response.Response(status=status.HTTP_200_OK)


class ExerciseListView (views.APIView):
    # queryset = Exercise.objects.all()
    # serializer_class = ExerciseSerializer

    def get(self, request):
        exercise = Exercise.objects.all()
        serialized_exercise = ExerciseSerializer(
            exercise, many=True, context={'request', request}
        )
        return response.Response(serialized_exercise.data, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        exercise_to_add = ExerciseSerializer(data=request.data)
        if exercise_to_add.is_valid():
            exercise_to_add.save()
            return response.Response(exercise_to_add.data, status=status.HTTP_201_CREATED)

        return response.Response(
            exercise_to_add.errors, status=status.HTTP_400_BAD_REQUEST
        )


class UserListView(views.APIView):
    def get(self, request):
        user = User.objects.all()
        serialized_user = UserSerializer(
            user, many=True, context={'request', request}
        )
        return response.Response(serialized_user.data, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        user_to_add = UserSerializer(data=request.data)
        if user_to_add.is_valid():
            user_to_add.save()
            return response.Response(user_to_add.data, status=status.HTTP_201_CREATED)

        return response.Response(
            user_to_add.errors, status=status.HTTP_400_BAD_REQUEST
        )


class userDetailView(views.APIView):
    def get_user_by_id(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise exceptions.NotFound(detail="user does not exist")

    def get(self, request, id):
        user = self.get_user_by_id(id)
        serialized_user = UserSerializer(
            user, context={"request": request})
        return response.Response(serialized_user.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        user = self.get_user_by_id(id)
        user.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id):
        user = self.get_user_by_id(id)
        updated_user = UserSerializer(
            user, data=request.data, context={"request": request})
        if updated_user.is_valid():
            updated_user.save()
            return response.Response(
                updated_user.data, status=status.HTTP_202_ACCEPTED
            )
        return response.Response(
            updated_user.errors, status=status.HTTP_400_BAD_REQUEST
        )


class UserExerciseLogListView (views.APIView):
    def get_user_by_id(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise exceptions.NotFound(detail="user does not exist")

    def get_log_by_id(self, id):
        try:
            return UserExerciseLog.objects.get(id=id)
        except UserExerciseLog.DoesNotExist:
            raise exceptions.NotFound(detail="exercise does not exist")

    def get(self, request):
        user = UserExerciseLog.objects.all()
        serialized_class = UserExerciseLogSerializer(
            user, many=True, context={'request', request}
        )
        return response.Response(serialized_class.data, status=status.HTTP_200_OK)

    def post(self, request):
        serialized_userlog = UserExerciseLogSerializer(
            data=request.data, context={"request": request})
        if serialized_userlog.is_valid():
            serialized_userlog.save()
            return response.Response(serialized_userlog.data, status=status.HTTP_200_OK)

        return response.Response(
            serialized_userlog.errors, status=status.HTTP_400_BAD_REQUEST
        )

# put request will be a blend of post and delete
# take this example and modify it to reflect the userlog
# commenting out to avoid errors, will come back to this
    # def put(self, request, id):
    #     exercise = self.get_(id)
    #     updated_exercise = ExerciseSerializer(
    #         exercise, data=request.data, context={"request": request})
    #     if updated_exercise.is_valid():
    #         updated_exercise.save()
    #         return response.Response(
    #             updated_exercise.data, status=status.HTTP_202_ACCEPTED
    #         )
    #     return response.Response(
    #         updated_exercise.errors, status=status.HTTP_400_BAD_REQUEST
    #     )

# this might work as it's quite similar to the post and there was nothing too specific there
# tested in postman and doesn't work as intended, but close
# commenting out to avoid errors, will come back to this
    # def delete(self, request):
    #     print(request.data)
    #     id = request.data['id']
    #     exercise_id = request.data['exercise_id']
    #     user = self.get_user_by_id(id)
    #     exercise = self.get_exercise_by_id(exercise_id)
    #     serialized_userlog = UserExerciseLogSerializer(
    #         data=request.data, context={"request": request})
    #     if serialized_userlog.is_valid():
    #         serialized_userlog.save()
    #         return response.Response(serialized_userlog.data, status=status.HTTP_200_OK)

    #     return response.Response(
    #         serialized_userlog.errors, status=status.HTTP_400_BAD_REQUEST
    #     )
