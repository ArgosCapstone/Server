# Argos_web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Page rendering views
    path('in_camera/', views.in_camera, name='In_camera'),  # 실시간 카메라 페이지
    path('report_record/', views.report_record, name='Report_record'),  # 보고서 기록 페이지
    path('video_record/', views.video_record, name='Video_record'),  # 비디오 기록 페이지
    path('sign_up/', views.sign_up, name='Sign_up'),  # 회원가입 페이지

    
    # Home page and login/signup
    path("", views.home, name="home"),  # 홈 URL (로그인 페이지)
    path("login/", views.login_view, name="login"),  # 로그인 URL
    path("id_password/", views.id_password, name="Id_password"),  # 아이디/비밀번호 찾기 URL
    
    # My Page
    path('my_page/', views.my_page_view, name='My_page'),  # 마이페이지 URL
    path('logout/', views.logout_view, name='logout'),  # 로그아웃 URL
    path('admin_page/', views.admin_page, name='Admin_page'),  # 관리자 페이지 URL

    # API endpoints
    path("api/videos/", views.fetch_videos, name="fetch_videos"),  # API 엔드포인트
    
    # Forget Id / Password
    path("find_id/", views.find_id, name="find_id"),
    path("verify_code_for_id/", views.verify_code_for_id, name="verify_code_for_id"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("verify_code_for_password/", views.verify_code_for_password, name="verify_code_for_password"),
    
    # Sign Up
    path("sign_up/", views.sign_up, name="sign_up"),  # 회원가입 URL
    
    # Admin Page
    path('admin/get_users/', views.get_users, name='get_users'),
    path('admin/approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('admin/unapprove_user/<int:user_id>/', views.unapprove_user, name='unapprove_user'),
    
    # YOLO
    path("yolo-stream/", views.yolo_stream_view, name="yolo_stream"),
    
    # parking_status
    path('api/parking-status/', views.parking_status_api, name='parking_status_api'),
    path('parking-status/', views.parking_status_view, name='parking_status'),
]

