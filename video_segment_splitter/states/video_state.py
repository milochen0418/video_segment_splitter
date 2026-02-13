import reflex as rx
import os
import random
import string
import asyncio
import shutil
from typing import Optional
from moviepy import VideoFileClip
from pathlib import Path
from pydantic import BaseModel
from reflex.config import get_config


def _get_ffmpeg_path() -> str:
    """Find ffmpeg binary. Prefer system ffmpeg, fallback to imageio-ffmpeg."""
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


class VideoMetadata(BaseModel):
    filename: str = ""
    duration_raw: float = 0.0
    duration_formatted: str = "00:00:00"
    resolution: str = "0x0"
    file_size_mb: str = "0.0"
    file_path: str = ""


class VideoSegment(BaseModel):
    filename: str = ""
    duration_formatted: str = ""
    file_path: str = ""
    download_url: str = ""


class VideoState(rx.State):
    is_uploading: bool = False
    upload_progress: int = 0
    video_metadata: Optional[VideoMetadata] = None
    segment_count: int = 5
    drag_active: bool = False
    is_processing: bool = False
    processing_progress: int = 0
    generated_segments: list[VideoSegment] = []
    zip_download_url: str = ""
    is_zipping: bool = False

    @rx.var
    def has_video(self) -> bool:
        return self.video_metadata is not None

    @rx.var
    def segment_duration_formatted(self) -> str:
        if not self.video_metadata:
            return "00:00:00"
        total_seconds = self.video_metadata.duration_raw
        if self.segment_count <= 0:
            return "00:00:00"
        seg_seconds = total_seconds / self.segment_count
        hours = int(seg_seconds // 3600)
        minutes = int(seg_seconds % 3600 // 60)
        seconds = int(seg_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @rx.event
    def set_segment_count(self, value: float):
        try:
            val = int(value)
            if 1 <= val <= 20:
                self.segment_count = val
        except (ValueError, TypeError):
            pass

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        self.is_uploading = True
        self.upload_progress = 0
        for file in files:
            upload_data = await file.read()
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            unique_name = (
                "".join(random.choices(string.ascii_letters + string.digits, k=10))
                + "_"
                + file.name
            )
            file_path = upload_dir / unique_name
            with file_path.open("wb") as f:
                f.write(upload_data)
            try:
                clip = VideoFileClip(file_path)
                duration = clip.duration
                width, height = clip.size
                h = int(duration // 3600)
                m = int(duration % 3600 // 60)
                s = int(duration % 60)
                formatted_time = f"{h:02d}:{m:02d}:{s:02d}"
                size_mb = f"{os.path.getsize(file_path) / (1024 * 1024):.1f}"
                self.video_metadata = VideoMetadata(
                    filename=file.name,
                    duration_raw=duration,
                    duration_formatted=formatted_time,
                    resolution=f"{width}x{height}",
                    file_size_mb=size_mb,
                    file_path=str(file_path),
                )
                clip.close()
            except Exception as e:
                import logging

                logging.exception(f"Error processing video: {e}")
                yield rx.toast.error("Failed to process video metadata")
        self.is_uploading = False
        self.upload_progress = 100

    @rx.event
    def clear_video(self):
        self.video_metadata = None
        self.upload_progress = 0

    @rx.event
    def toggle_drag(self):
        self.drag_active = not self.drag_active

    @rx.event(background=True)
    async def split_video(self):
        async with self:
            if not self.video_metadata or self.is_processing:
                return
            self.is_processing = True
            self.processing_progress = 0
            self.generated_segments = []
        try:
            async with self:
                input_path = self.video_metadata.file_path
                segment_count = self.segment_count
                original_filename = self.video_metadata.filename
                total_duration = self.video_metadata.duration_raw

            segment_duration = total_duration / segment_count
            generated_segments = []
            upload_dir = rx.get_upload_dir()
            ffmpeg = _get_ffmpeg_path()
            max_threads = max(1, (os.cpu_count() or 4) // 2)

            for i in range(segment_count):
                start_time = i * segment_duration
                end_time = min((i + 1) * segment_duration, total_duration)
                seg_len = end_time - start_time

                safe_filename = Path(original_filename).stem
                segment_filename = f"{safe_filename}_part_{i + 1:03d}.mp4"
                segment_path = upload_dir / segment_filename

                # Call ffmpeg directly as an async subprocess.
                # This runs in a completely separate OS process —
                # zero GIL contention, zero blocking of the Python event loop.
                proc = await asyncio.create_subprocess_exec(
                    ffmpeg,
                    "-y",              # overwrite
                    "-ss", str(start_time),
                    "-i", str(input_path),
                    "-t", str(seg_len),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-threads", str(max_threads),
                    "-avoid_negative_ts", "make_zero",
                    "-loglevel", "error",
                    str(segment_path),
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await proc.communicate()

                if proc.returncode != 0:
                    import logging
                    logging.error(f"ffmpeg error for segment {i+1}: {stderr.decode()}")
                    async with self:
                        self.is_processing = False
                    yield rx.toast.error(f"ffmpeg failed on segment {i+1}")
                    return

                h = int(seg_len // 3600)
                m = int(seg_len % 3600 // 60)
                s = int(seg_len % 60)
                formatted_duration = f"{h:02d}:{m:02d}:{s:02d}"
                api_url = str(get_config().api_url or "http://localhost:8000")
                segment = VideoSegment(
                    filename=segment_filename,
                    duration_formatted=formatted_duration,
                    file_path=str(segment_path),
                    download_url=f"{api_url}/_upload/{segment_filename}",
                )
                generated_segments.append(segment)
                progress = int((i + 1) / segment_count * 100)
                async with self:
                    self.processing_progress = progress

            async with self:
                self.generated_segments = generated_segments
                self.is_processing = False
                self.zip_download_url = ""
            yield rx.toast.success("Video split successfully!")
        except Exception as e:
            import logging

            logging.exception(f"Error splitting video: {e}")
            async with self:
                self.is_processing = False
                yield rx.toast.error(f"Error splitting video: {str(e)}")

    @rx.event(background=True)
    async def create_zip_download(self):
        import zipfile

        async with self:
            if not self.generated_segments or self.is_zipping:
                return
            self.is_zipping = True
        try:
            async with self:
                segments = self.generated_segments
                original_name = (
                    Path(self.video_metadata.filename).stem
                    if self.video_metadata
                    else "video"
                )
            upload_dir = rx.get_upload_dir()
            zip_filename = f"{original_name}_all_parts.zip"
            zip_path = upload_dir / zip_filename
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for seg in segments:
                    file_to_add = Path(seg.file_path)
                    if file_to_add.exists():
                        zipf.write(file_to_add, arcname=seg.filename)
            async with self:
                api_url = str(get_config().api_url or "http://localhost:8000")
                self.zip_download_url = f"{api_url}/_upload/{zip_filename}"
                self.is_zipping = False
            yield rx.toast.success("ZIP archive created!")
        except Exception as e:
            import logging

            logging.exception(f"Error creating ZIP: {e}")
            async with self:
                self.is_zipping = False
            yield rx.toast.error("Failed to create ZIP archive")