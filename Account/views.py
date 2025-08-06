from django.shortcuts import render

from rest_framework.response import Response 
from rest_framework import status
from rest_framework import viewsets

from .serializers import SignUpSerializer ,OtpVerificationSerializer

from rest_framework.views import APIView
from .models import OtpVerification , Skill
from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.exceptions import APIException


# paginations import
from rest_framework.pagination import PageNumberPagination



User = get_user_model()




'''Signup View'''


class SignUpView(viewsets.ModelViewSet):

    '''
        View to handle signup and send otp to email for verification.
    '''
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):

        try:
            if User.objects.filter(username = request.data['username']).exists():
                return Response({
                    "message": "User with this username already exists.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            User.objects.get(email= request.data['email'])
            # User.objects.get(username = request.data['username'])
            return Response({"message":"user already exist", "data": None},status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist: 
            serializer = self.get_serializer(data=request.data)
            print("----",serializer)

            if serializer.is_valid():

                self.request.session['password'] = serializer.validated_data['password']
                self.request.session['is_employer'] = serializer.validated_data['is_employer']
                self.request.session['is_freelancer'] = serializer.validated_data['is_freelancer']
                
                serializer.save()
                return Response(
                    {
                        "message": "OTP sent to email. Please verify to complete registration.",
                        "data":None
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    "message": str(e),
                    "data": None
                }
                , status=status.HTTP_400_BAD_REQUEST
                )
        
        
'''Otp Verification View'''

# class OtpVerificationsView(APIView):
    
#     """
#         View to handle OTP verification for new user signup.
#     """

#     def post(self, request):
#         password = request.session.get('password')
#         serializer = OtpVerificationSerializer(data=request.data, context={'password': password})
#         print("========", serializer)
        

#         try:

#             if serializer.is_valid():
#                 # print("=====",serializer.save())
#                 print("========", serializer)
        

#                 serializer.save()
                

#                 return Response(
#                     {"message": "User registered successfully!",
#                      "data":None},
#                     status=status.HTTP_201_CREATED
#                 )
#         except Exception as e:

#             return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OtpVerificationSerializer

class OtpVerificationsView(APIView):
    """
    View to handle OTP verification for new user signup or update.
    """

    def post(self, request):
        # Extract email and otp from request
        email = request.data.get("email")
        otp = request.data.get("otp")

        # Check if email and OTP are provided
        if not email or not otp:
            return Response({"message": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize the serializer with the provided data
        serializer = OtpVerificationSerializer(data=request.data, context={'password': request.session.get('password'),'is_employer':request.session.get('is_employer'),'is_freelancer':request.session.get('is_freelancer')})

        # Check if serializer is valid
        if serializer.is_valid():
            # Create the user and return success response
            user = serializer.save()
            return Response(
                {"message": "OTP verified successfully, user created!", "data": {"email": user.email}},
                status=status.HTTP_201_CREATED
            )

        # If serializer is invalid, return validation errors
        return Response({"message": "Invalid OTP or expired.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

'''Login View'''

class LoginView(APIView):
    
    '''
        View to hanlde user login using Jwt authentication.
    '''

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('username')
        

        try:
            # user = User.objects.get(email=email)
            user = User.objects.get(email=email)
            print(user)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(email=email, password=password)
        print(user)

        if user is None:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        print(user.email)

        refresh = RefreshToken.for_user(user)
        print(refresh)
        print(refresh.access_token)
        return Response({
            'message': 'User logged in successfully.',
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
            'email':user.email
        }, status=status.HTTP_200_OK)





'''Protected View for testing'''


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated"})
    


''' Logout View '''

class LogoutView(APIView):

    """
        View to handle logout by blacklisting the refresh token.
    """

    permission_classes = [IsAuthenticated]

    def post(self,request):
        try:
            refresh_token  = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message":"User logged out Success", },status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            return Response({"message":"Invalid Token or Token Expired", "data": None},status=status.HTTP_400_BAD_REQUEST)

from jobassignment.models import Job
def reassign_jobs_to_default_employer(user, default_employer_email):
    # Get the default employer object by email
    try:
        default_employer =User.objects.get(email=default_employer_email)
    except User.DoesNotExist:
        raise ValueError("Default employer not found.")
    
    # Reassign all jobs of the user to the default employer
    if user.is_employer:
        jobs = Job.objects.filter(employer=user)
        jobs.update(employer=default_employer)
        print(f"All jobs of employer {user.username} have been reassigned to {default_employer.username}.")
    else:
        raise ValueError("User is not an employer.")



class SoftDeleteUserAPIView(APIView):

    permission_classes = [IsAuthenticated]
    def delete(self, request, pk=None):
        try:
            
            username = request.user
            default_employer_email = request.data.get('default_employer_email') 
          
            user = User.objects.get(username = request.user)
            if  user.is_deleted :
                return Response({"message":"User is already soft deleted."},status=status.HTTP_204_NO_CONTENT)
            try:
                default_employer = User.objects.get(email=default_employer_email)
                if default_employer.is_deleted :
                    return Response({"message":"default user provided is already deleted."},status=status.HTTP_404_NOT_FOUND)
                if not default_employer.is_employer:
                    return Response({"message": "pass user is not employer"}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"error": "other user not found."}, status=status.HTTP_404_NOT_FOUND)
            
            
            
            print("deleted user:",username)
            print("assigned user:",default_employer)

             
            # kwargs = {'default_employer': default_employer}
            user._default_employer = default_employer
            user.is_deleted = True
            user.save()

            # reassign_jobs_to_default_employer(user, default_employer_email=default_employer_email)
            return Response({"message": "User marked as deleted.","username":f"{username}"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        



# class AddSkillToUserView(APIView):

    # permission_classes  = [IsAuthenticated]

    # def post(self,request,*args, **kwargs):
    #     user = request.user
    #     skills_data = request.data.get('skills',[])
    #     # try:
    #     #     user = User.objects.get(id= user)
    #     # except User.DoesNotExist:
    #     #     return Response({"user not exist."})
    #     print(skills_data)
    #     if not skills_data:
    #         return Response({"message":"pass the required skill you want to add."},status=status.HTTP_400_BAD_REQUEST)

    #     if not user.is_freelancer:
    #         return Response({"message":"only freelancer is allow to add skill."}, status=status.HTTP_400_BAD_REQUEST)
      
    #     if not all(isinstance(skill, str) for skill in skills_data):
    #         return Response({"error": "Skills must be provided as an array of skill names (strings)."}, status=status.HTTP_400_BAD_REQUEST)
    #     skills = []
    #     for skill in skills_data:
    #         skill_object = Skill.objects.get_or_create(name= skill.lower())
    #         skills.append(skill_object)
    #     print(skills)
        

    #     user.skills.set(skills)
    #     user.save()

    #     return Response({"message":"Skills add to user successfully"},status=status.HTTP_200_OK)
class AddSkillToUserView(APIView):
    permission_classes  = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        skills_data = request.data.get('skills', [])  # ["java", "python"]


        if request.content_type == 'application/json':
            skills_data = request.data.get('skills', [])
        else:
            skills_data = request.data.getlist('skills[]', [])

        if user.is_deleted :
            return Response({"message":"login user is deleted."})


        # Validate skills data
        if not skills_data:
            return Response({"message": "Pass the required skill you want to add."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_freelancer:
            return Response({"message": "Only freelancer is allowed to add skill."}, status=status.HTTP_400_BAD_REQUEST)

        if not all(isinstance(skill, str) for skill in skills_data):
            return Response({"error": "Skills must be provided as an array of skill names (strings)."}, status=status.HTTP_400_BAD_REQUEST)
        print("===",skills_data)
        skills = []
        for skill in skills_data:
            skill_object, created = Skill.objects.get_or_create(name=skill.lower())  # Get or create the skill object
            skills.append(skill_object)  # Append the actual Skill object (not the string)

        print("skills",skills)
        # Now assign the skills to the user
        user.skills.set(skills)
        user.save()

        return Response({"message": "Skills added to user successfully."}, status=status.HTTP_200_OK)



# views.py
from .serializers import CustomUserSerializer

class CustomUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()  # Or filter if needed
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)





class HardDeleteUserAPIView(APIView):

    permission_classes = [IsAuthenticated]
    def delete(self, request, pk=None):
        try:
            
            username = request.user
            default_employer_email = request.data.get('default_employer_email') 
          
            user = User.objects.get(username = request.user)
            if  user.is_deleted :
                return Response({"message":"User is already soft deleted."},status=status.HTTP_204_NO_CONTENT)
            try:
                default_employer = User.objects.get(email=default_employer_email)
                if default_employer.is_deleted :
                    return Response({"message":"default user provided is already deleted."},status=status.HTTP_404_NOT_FOUND)
                if not default_employer.is_employer:
                    return Response({"message": "pass user is not employer"}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"error": "other user not found."}, status=status.HTTP_404_NOT_FOUND)
            
            
            
            print("deleted user:",username)
            print("assigned user:",default_employer)

             
            # kwargs = {'default_employer': default_employer}
            user._default_employer = default_employer
            user.delete()

            # reassign_jobs_to_default_employer(user, default_employer_email=default_employer_email)
            return Response({"message": "User marked as deleted.","username":f"{username}"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)