import reflex as rx
from video_segment_splitter.states.video_state import VideoState


def info_item(icon: str, label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-5 w-5 text-blue-500"),
        rx.el.div(
            rx.el.p(
                label,
                class_name="text-xs text-gray-400 uppercase tracking-wider font-semibold",
            ),
            rx.el.p(value, class_name="text-base font-bold text-gray-800"),
            class_name="flex flex-col",
        ),
        class_name="flex items-center gap-3 p-4 bg-gray-50 rounded-xl border border-gray-100",
    )


def metadata_card() -> rx.Component:
    return rx.el.div(
        rx.cond(
            VideoState.has_video,
            rx.el.div(
                rx.el.h3(
                    "Video Information",
                    class_name="text-lg font-bold text-gray-800 mb-4",
                ),
                rx.el.div(
                    info_item(
                        "clock",
                        "Duration",
                        VideoState.video_metadata.duration_formatted,
                    ),
                    info_item(
                        "maximize", "Resolution", VideoState.video_metadata.resolution
                    ),
                    info_item(
                        "hard-drive",
                        "File Size",
                        f"{VideoState.video_metadata.file_size_mb} MB",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
                ),
                class_name="mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500",
            ),
        )
    )