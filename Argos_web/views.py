import random
import json
import cv2
import os
import time
import threading
from ultralytics import YOLO
import numpy as np
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Video, User
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


# 랜더링 (페이지 요청)
def home(request):
    return render(request, 'Argos_web/Home.html')

def in_camera(request):
    return render(request, 'Argos_web/In_camera.html')

def report_record(request):
    return render(request, 'Argos_web/Report_record.html')

def video_record(request):
    return render(request, 'Argos_web/Video_record.html')

def admin_page(request):
    return render(request, 'Argos_web/Admin_page.html')

def sign_up(request):
    return render(request, 'Argos_web/Sign_up.html')

def id_password(request):
    return render(request, 'Argos_web/Id_password.html')

def fetch_videos(request):
    video_dir = "/Users/zeus/Desktop/Argos_Server/Argos_Django/videos"
    videos = []
    
def parking_status_view(request):
    return render(request, 'parking_status.html')

    if os.path.exists(video_dir):
        for file_name in os.listdir(video_dir):
            if file_name.endswith(".mp4"):
                videos.append({
                    "file_name": file_name,
                    "file_path": f"/static/videos/{file_name}"  # 정적 파일 경로
                })

    return JsonResponse({"videos": videos})


# 로그인
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        try:
            # 사용자 검색
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                if user.is_approved:
                    # 세션에 사용자 정보 저장
                    request.session['user_id'] = user.user_id
                    request.session['username'] = user.username
                    request.session['email'] = user.email
                    request.session['phone_number'] = user.phone_number
                    request.session['is_admin'] = user.is_admin
                    request.session.set_expiry(3600)  # 세션 만료 시간: 1시간
                    
                    return redirect("My_page")  # My_page.html로 리디렉션
                else:
                    messages.error(request, "관리자 승인이 필요합니다.")
            else:
                messages.error(request, "비밀번호가 일치하지 않습니다.")
        except User.DoesNotExist:
            messages.error(request, "아이디 또는 비밀번호가 일치하지 않습니다.")
    return render(request, "Argos_web/Home.html")

# 로그아웃
def logout_view(request):
    request.session.flush()  # 세션 초기화
    messages.success(request, "로그아웃되었습니다.")
    return redirect('home')

# 마이페이지

def my_page_view(request):
    # 세션에서 사용자 정보 가져오기
    user_id = request.session.get("user_id")
    username = request.session.get("username")
    email = request.session.get("email")
    is_admin = request.session.get("is_admin")
    phone_number = request.session.get("phone_number")
    
    if user_id and username and email and phone_number:
        # 사용자 정보 전달
        return render(
            request, 
            "Argos_web/My_page.html", 
            {"user": {"user_id": user_id, "username": username, "email": email, "phone_number": phone_number, "is_admin": is_admin}}
        )
    else:
        # 세션 정보가 없다면 로그인 페이지로 리디렉션
        messages.error(request, "로그인이 필요합니다.")
        return redirect("login")
# 회원가입
def sign_up(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone_number = request.POST.get("phone_number")

        # 필수 값 확인
        if not username or not email or not password or not phone_number:
            messages.error(request, "모든 필드를 입력해주세요.")
            return redirect("sign_up")

        # 중복 사용자 체크
        if User.objects.filter(username=username).exists():
            messages.error(request, "이미 존재하는 아이디입니다.")
            return redirect("sign_up")
        if User.objects.filter(email=email).exists():
            messages.error(request, "이미 존재하는 이메일입니다.")
            return redirect("sign_up")

        # 데이터 저장
        user = User(
            username=username,
            email=email,
            password=make_password(password),  # 비밀번호 암호화
            phone_number=phone_number,
        )
        user.save()

        messages.success(request, "회원가입이 완료되었습니다. 로그인 해주세요.")
        return redirect("login")  # 로그인 페이지로 리디렉션

    return render(request, "Argos_web/Sign_up.html")


# 인증번호 생성 함수
def generate_verification_code():
    return str(random.randint(100000, 999999))

# 아이디 찾기 요청
def find_id(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body.get("email")
            user = User.objects.get(email=email)
            verification_code = generate_verification_code()
            cache.set(f"verification_code_{email}", verification_code, timeout=300)  # 인증번호 저장 (5분)
            # 이메일 전송 로직
            send_mail(
                'Argos 인증번호',
                f'귀하의 인증번호는 {verification_code}입니다.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": "인증번호를 이메일로 전송했습니다."})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "해당 이메일이 존재하지 않습니다."})
    return JsonResponse({"success": False, "message": "잘못된 요청입니다."})

# 비밀번호 초기화 요청
def reset_password(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            username = body.get("username")
            email = body.get("email")
            user = User.objects.get(username=username, email=email)
            verification_code = generate_verification_code()
            cache.set(f"verification_code_{email}", verification_code, timeout=300)  # 인증번호 저장 (5분)
            # 이메일 전송 로직
            send_mail(
                'Argos 인증번호',
                f'귀하의 인증번호는 {verification_code}입니다.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": "인증번호를 이메일로 전송했습니다."})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "사용자 정보를 찾을 수 없습니다."})
    return JsonResponse({"success": False, "message": "잘못된 요청입니다."})

# 아이디 찾기 인증번호 확인
def verify_code_for_id(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body.get("email")
        code = body.get("code")
        cached_code = cache.get(f"verification_code_{email}")
        if cached_code == code:
            user = User.objects.get(email=email)  # 인증 성공
            return JsonResponse({"success": True, "username": user.username})
        return JsonResponse({"success": False, "message": "인증번호가 일치하지 않습니다."})

# 비밀번호 초기화 인증번호 확인
def verify_code_for_password(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body.get("email")
        code = body.get("code")
        cached_code = cache.get(f"verification_code_{email}")
        if cached_code == code:
            user = User.objects.get(email=email)  # 인증 성공
            user.set_password("0000")  # 비밀번호 초기화
            user.save()
            return JsonResponse({"success": True, "message": "비밀번호가 '0000'으로 초기화되었습니다."})
        return JsonResponse({"success": False, "message": "인증번호가 일치하지 않습니다."})

def is_admin(user):
    return user.is_authenticated and user.is_admin  # 사용자 인증 여부 및 관리자 여부 확인

@login_required  # 인증된 사용자만 접근 가능
@user_passes_test(is_admin)  # 관리자만 접근 가능
def get_users(request):
    if not request.user.is_authenticated:  # 인증되지 않은 경우
        return JsonResponse({"error": "Authentication required"}, status=403)
    # 승인 대기 중인 사용자
    pending_users = User.objects.filter(is_approved=False)
    approved_users = User.objects.filter(is_approved=True)

    data = {
        "pending": [
            {"user_id": user.user_id, "username": user.username, "email": user.email}
            for user in pending_users
        ],
        "approved": [
            {"user_id": user.user_id, "username": user.username, "email": user.email}
            for user in approved_users
        ],
    }
    return JsonResponse(data)

@csrf_exempt
def approve_user(request, user_id):
    if request.method == "POST":
        try:
            user = User.objects.get(user_id=user_id)
            user.is_approved = True
            user.save()
            print(f"User {user.username} approved.")  # 디버그 로그 추가
            return JsonResponse({"success": True, "username": user.username})
        except User.DoesNotExist:
            print(f"User with ID {user_id} not found.")  # 디버그 로그 추가
            return JsonResponse({"success": False, "message": "사용자를 찾을 수 없습니다."})

@csrf_exempt
def unapprove_user(request, user_id):
    if request.method == "POST":
        try:
            user = User.objects.get(user_id=user_id)
            user.is_approved = False
            user.save()
            return JsonResponse({"success": True, "username": user.username})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "사용자를 찾을 수 없습니다."})
        
# YOLO 모델 적용
# YOLO 모델 초기화
fire_detect_model = YOLO(os.path.join(settings.BASE_DIR, "static", "fire_and_smoke_trained.pt"))

def process_stream():
    # 비디오 파일 경로
    video_path = os.path.join(settings.BASE_DIR, "static/hls/output.m3u8")
    cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)

    fps_limit = 30  # FPS 제한
    prev_time = 0   # 이전 프레임 시간 기록

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if torch.cuda.is_available():
            print(f"GPU 사용 중: {torch.cuda.get_device_name(torch.cuda.current_device())}")
        else:
            print("GPU를 사용할 수 없습니다. CPU 사용 중.")
        curr_time = time.time()

        # FPS 제한 적용
        if curr_time - prev_time < 1 / fps_limit:
            continue
        prev_time = curr_time

        # 프레임 크기 조정 
        frame_resized = cv2.resize(frame, (640, 640))

        # YOLO 모델로 프레임 처리 
        results = fire_detect_model.predict(frame_resized, conf=0.3, stream=True)

        # 원본 크기로 좌표 변환
        scale_x = frame.shape[1] / frame_resized.shape[1]
        scale_y = frame.shape[0] / frame_resized.shape[0]

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
                y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
                conf = box.conf[0]
                cls = fire_detect_model.names[int(box.cls[0])]

                # 감지 결과를 프레임에 표시
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f"{cls} {conf:.2f}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 프레임을 JPEG로 인코딩
        _, jpeg = cv2.imencode(".jpg", frame)
        frame_data = jpeg.tobytes()

        # 스트리밍 반환
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_data + b"\r\n")

    cap.release()

def yolo_stream_view(request):
    return StreamingHttpResponse(process_stream(), content_type="multipart/x-mixed-replace; boundary=frame")

# 초기 상태
parking_lot_status = [
    {"id": 1, "status": "green"},
    {"id": 2, "status": "green"},
    {"id": 3, "status": "green"},
    {"id": 4, "status": "green"},
    {"id": 5, "status": "green"},
    {"id": 6, "status": "green"},
    {"id": 7, "status": "green"},
    {"id": 8, "status": "green"},
    {"id": 9, "status": "green"},
    {"id": 10, "status": "green"},
    {"id": 11, "status": "green"},
    {"id": 12, "status": "green"},
    {"id": 13, "status": "green"},
    {"id": 14, "status": "green"},
]

# 날씨 데이터
WEATHER_CONDITIONS = ["Sunny", "Cloudy", "Rainy", "Stormy"]

def simulate_changes():
    """Simulate parking lot changes and fire detection."""
    global parking_lot_status

    # 차량 감지
    parking_lot_status[3]["status"] = "yellow"  # 4번 주차선
    parking_lot_status[8]["status"] = "yellow"  # 9번 주차선

    # 30초 후 화재
    time.sleep(30)
    parking_lot_status[12]["status"] = "red"  # 13번 주차선

# 백그라운드에서 시뮬레이션 시작
thread = threading.Thread(target=simulate_changes, daemon=True)
thread.start()

def parking_status_api(request):
    """Provide the current parking lot status."""
    # 현재 시간을 포함하여 반환
    return JsonResponse({
        "status": parking_lot_status,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),  # 현재 시간
        "weather": random.choice(WEATHER_CONDITIONS),  # 랜덤 날씨
    })

def parking_status_view(request):
    """Render the parking status page."""
    return render(request, 'parking_status.html')