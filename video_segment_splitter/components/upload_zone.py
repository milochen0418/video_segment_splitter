import reflex as rx
from video_segment_splitter.states.video_state import VideoState


def upload_zone() -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.cond(
                    VideoState.is_uploading,
                    rx.el.div(
                        rx.icon(
                            "squirrel",
                            class_name="h-12 w-12 text-blue-500 animate-spin mb-4",
                        ),
                        rx.el.p(
                            "Uploading & Processing...",
                            class_name="text-lg font-semibold text-gray-700",
                        ),
                        class_name="flex flex-col items-center",
                    ),
                    rx.cond(
                        VideoState.has_video,
                        rx.el.div(
                            rx.icon(
                                "lamp_wall_down",
                                class_name="h-12 w-12 text-green-500 mb-4",
                            ),
                            rx.el.p(
                                VideoState.video_metadata.filename,
                                class_name="text-lg font-semibold text-gray-800 mb-2 truncate max-w-xs",
                            ),
                            rx.el.button(
                                "Replace Video",
                                on_click=VideoState.clear_video,
                                class_name="text-sm text-blue-600 hover:text-blue-800 font-medium underline",
                            ),
                            class_name="flex flex-col items-center",
                        ),
                        rx.el.div(
                            rx.icon(
                                "pen",
                                class_name="h-12 w-12 text-blue-400 mb-4 transition-transform group-hover:scale-110",
                            ),
                            rx.el.p(
                                "Drag and drop your video here",
                                class_name="text-lg font-semibold text-gray-700",
                            ),
                            rx.el.p(
                                "or click to browse files",
                                class_name="text-sm text-gray-500 mt-1",
                            ),
                            rx.el.p(
                                "MP4, MOV, AVI supported",
                                class_name="text-xs text-gray-400 mt-4",
                            ),
                            class_name="flex flex-col items-center",
                        ),
                    ),
                ),
                class_name=rx.cond(
                    VideoState.drag_active,
                    "border-blue-500 bg-blue-50/50 scale-[0.99]",
                    "border-gray-300 bg-white hover:border-blue-400",
                )
                + " border-2 border-dashed rounded-2xl p-12 transition-all duration-300 flex flex-col items-center justify-center cursor-pointer group",
            ),
            id="video_upload",
            multiple=False,
            accept={"video/*": [".mp4", ".mov", ".avi"]},
            on_drop=VideoState.handle_upload(rx.upload_files(upload_id="video_upload")),
            on_mouse_enter=VideoState.toggle_drag,
            on_mouse_leave=VideoState.toggle_drag,
        ),
        class_name="w-full max-w-2xl mx-auto",
    )