import os
import datetime
from django.core.management.base import BaseCommand
from Argos_web.models import SurveillanceVideo

class Command(BaseCommand):
    help = 'Delete video files older than 30 days'

    def handle(self, *args, **kwargs):
        # 기준 날짜 계산 (30일 이전)
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)

        # 30일 이전의 데이터를 필터링
        old_videos = SurveillanceVideo.objects.filter(start_time__lt=cutoff_date)

        for video in old_videos:
            try:
                # 파일 삭제
                if os.path.exists(video.file_path):
                    os.remove(video.file_path)  
                    self.stdout.write(self.style.SUCCESS(f"Deleted file: {video.file_path}"))
                else:
                    self.stdout.write(self.style.WARNING(f"File not found: {video.file_path}"))

                # 데이터베이스 기록 삭제
                video.delete()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting file {video.file_path}: {e}"))
