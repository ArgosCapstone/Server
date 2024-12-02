# Argos_web/models.py
from django.db import models
from django.contrib.auth.hashers import make_password
from uuid import uuid4

# Users 테이블
class User(models.Model):
    user_id = models.AutoField(primary_key=True)  # 유저의 고유 ID
    username = models.CharField(max_length=50, unique=True)  # 사용자명
    password = models.CharField(max_length=255)  # 암호화된 비밀번호
    email = models.EmailField(unique=True)  # 이메일 주소
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # 전화번호
    is_approved = models.BooleanField(default=False)  # 관리자 승인 여부
    created_at = models.DateTimeField(auto_now_add=True)  # 계정 생성 시각
    updated_at = models.DateTimeField(auto_now=True)  # 계정 정보 수정 시각
    is_admin = models.BooleanField(default=False)  # 관리자 여부

    def __str__(self):
        return self.username
class ParkingSpot(models.Model):
    spot_id = models.AutoField(primary_key=True)
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6)  # 중앙 경도
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6)  # 중앙 위도
    top_left_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # 왼쪽 위 꼭짓점 경도
    top_left_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # 왼쪽 위 꼭짓점 위도
    top_right_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # 오른쪽 위 꼭짓점 경도
    top_right_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # 오른쪽 위 꼭짓점 위도
    bottom_left_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # 왼쪽 아래 꼭짓점 경도
    bottom_left_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # 왼쪽 아래 꼭짓점 위도
    bottom_right_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # 오른쪽 아래 꼭짓점 경도
    bottom_right_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # 오른쪽 아래 꼭짓점 위도
    width = models.DecimalField(max_digits=4, decimal_places=1, default=2.3)  # 주차 공간의 가로 크기
    length = models.DecimalField(max_digits=4, decimal_places=1, default=5.0)  # 주차 공간의 세로 크기
    status = models.CharField(max_length=20, default='available')  # 상태: available, occupied, fire

    def __str__(self):
        return f"Spot {self.spot_id} - {self.status}"

# Drone 테이블
class Drone(models.Model):
    drone_id = models.AutoField(primary_key=True)
    longitude_initial = models.DecimalField(max_digits=9, decimal_places=6)  # 초기 경도
    latitude_initial = models.DecimalField(max_digits=9, decimal_places=6)  # 초기 위도
    longitude_arrival = models.DecimalField(max_digits=9, decimal_places=6)  # 도착 경도
    latitude_arrival = models.DecimalField(max_digits=9, decimal_places=6)  # 도착 위도
    status = models.CharField(max_length=20, default='idle')  # 상태: idle, in_transit, deployed

    def __str__(self):
        return f"Drone {self.drone_id} - {self.status}"

# Report 테이블
class Report(models.Model):
    report_id = models.AutoField(primary_key=True)  # 화재 신고의 고유 ID
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.SET_NULL, null=True)  # 화재 발생 주차 공간
    timestamp = models.DateTimeField(auto_now_add=True)  # 화재 발생 시각
    video_url = models.CharField(max_length=255, blank=True, null=True)  # 화재 당시 촬영된 영상 URL
    reported_at = models.DateTimeField(auto_now_add=True)  # 신고 접수 시각

    def __str__(self):
        return f"Report {self.report_id} - Spot {self.parking_spot}"

# Video 테이블
class Video(models.Model):
    video_id = models.AutoField(primary_key=True)  # 영상 고유 ID
    file_path = models.CharField(max_length=255)  # 영상 파일 경로
    start_time = models.DateTimeField()  # 영상 녹화 시작 시각
    end_time = models.DateTimeField()  # 영상 녹화 종료 시각
    duration = models.DurationField()  # 녹화 시간 간격
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.SET_NULL, null=True)  # 관련 주차 공간 ID
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # 위도
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # 경도

    def __str__(self):
        return f"Video {self.video_id} - {self.file_path}"
def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()