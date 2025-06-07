import base64
from django.core.files.base import ContentFile
from .models import CustomUser
from .forms import RegisterForm
from django.shortcuts import render, redirect
import face_recognition
import random
import string
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance_km = R * c
    distance_meters = distance_km * 1000
    return distance_meters


def calculate_steps(distance_meters):
    average_step_length = 0.762
    step_count = distance_meters / average_step_length
    return round(step_count)


def index(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            face_data_url = form.cleaned_data.get('face_data_url')
            format, imgstr = face_data_url.split(';base64,')
            ext = format.split('/')[-1]
            face_file = ContentFile(base64.b64decode(imgstr), name=f'user_face.{ext}')
            user.face_image = face_file
            user.lat = form.cleaned_data.get('lat')
            user.lang = form.cleaned_data.get('lang')
            user.save()
            messages.success(request,"New Data Added...")
            return redirect('datas')
    else:
        form = RegisterForm()
    return render(request, 'index.html', {'form': form})


def datas(request):
    data = CustomUser.objects.all()
    return render(request,'datas.html',{'data':data})

def face_verification_view(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        live_image = request.FILES.get("live_image")

        # Load known image encoding
        known_image = face_recognition.load_image_file(user.face_image.path)
        known_encodings = face_recognition.face_encodings(known_image)
        if len(known_encodings) == 0:
            messages.error(request, "No face found in your registered image.")
            return redirect('datas')
        known_encoding = known_encodings[0]

        # Load live image encoding
        unknown_image = face_recognition.load_image_file(live_image)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        if len(unknown_encodings) == 0:
            messages.error(request, "No face found in the live image.")
            return redirect('datas')
        unknown_encoding = unknown_encodings[0]

        # Calculate face distance
        face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
        tolerance = 0.45  # stricter than default 0.6

        if face_distance < tolerance:
            request.session['face_verified_user_id'] = user.id
            messages.success(request, "Face Verified Successfully")
            return redirect('password_verification')
        else:
            # Location-based password reset
            user_lon = float(user.lang)
            user_lat = float(user.lat)
            current_lat = float(request.POST.get('current_lat'))
            current_lon = float(request.POST.get('current_lon'))

            distance = calculate_distance(user_lat, user_lon, current_lat, current_lon)
            steps = calculate_steps(distance)

            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + str(steps)
            user.set_password(new_password)
            user.save()

            send_mail(
                'Your Password Was Reset',
                f"Hi {user.username},\n\nYour face couldn't be verified. Your new password is: {new_password}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            messages.error(request, "Face not matched. A new password has been emailed.")
            return redirect('datas')

    return render(request, 'face_verification.html', {'user': user})

def password_verification_view(request):
    user_id = request.session.get('face_verified_user_id')
    if not user_id:
        messages.error(request, "Unauthorized access. Please verify your face first.")
        return redirect('select_user')
    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        password = request.POST.get('password')
        auth_user = authenticate(username=user.username, password=password)
        if auth_user:

            messages.success(request, "Access Granted. You're now logged in")
            return render(request, 'show_image.html', {'user_image': user.image.url,'user':user})
        else:
            messages.error(request, "Incorrect password.")
            return redirect('password_verification')
    return render(request, 'password_verification.html', {'user': user})



