import reflex as rx
from video_segment_splitter.states.video_state import VideoState


def controls() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Split Settings",
                        class_name="text-lg font-bold text-gray-800 mb-2",
                    ),
                    rx.el.p(
                        "Choose how many segments to split your video into.",
                        class_name="text-sm text-gray-500 mb-6",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Number of Segments",
                            class_name="text-sm font-semibold text-gray-700",
                        ),
                        rx.el.div(
                            rx.el.input(
                                type="number",
                                on_change=VideoState.set_segment_count,
                                class_name="w-20 px-3 py-2 border border-gray-200 rounded-lg text-center font-bold text-blue-600 focus:ring-2 focus:ring-blue-500 outline-none",
                                default_value=VideoState.segment_count.to_string(),
                            ),
                            class_name="flex items-center",
                        ),
                        class_name="flex justify-between items-center mb-4",
                    ),
                    rx.el.input(
                        type="range",
                        min=1,
                        max=20,
                        step=1,
                        key=VideoState.segment_count.to_string(),
                        default_value=VideoState.segment_count.to_string(),
                        on_change=VideoState.set_segment_count.throttle(200),
                        class_name="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600 mb-8",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Estimated Segment Length",
                                class_name="text-xs text-gray-400 font-bold uppercase",
                            ),
                            rx.el.p(
                                VideoState.segment_duration_formatted,
                                class_name="text-2xl font-black text-blue-600",
                            ),
                            class_name="text-center p-6 bg-blue-50 rounded-2xl border border-blue-100",
                        ),
                        class_name="w-full",
                    ),
                    class_name="w-full",
                ),
                class_name="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm",
            ),
            rx.el.button(
                rx.cond(
                    VideoState.is_processing,
                    rx.fragment(
                        rx.el.span("Processing...", class_name="mr-2"),
                        rx.icon("squirrel", class_name="h-5 w-5 animate-spin"),
                    ),
                    rx.fragment(
                        rx.el.span("Start Splitting Video", class_name="mr-2"),
                        rx.icon("scissors", class_name="h-5 w-5"),
                    ),
                ),
                disabled=~VideoState.has_video | VideoState.is_processing,
                on_click=VideoState.split_video,
                class_name=rx.cond(
                    VideoState.has_video & ~VideoState.is_processing,
                    "w-full mt-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl font-bold text-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 flex items-center justify-center cursor-pointer",
                    "w-full mt-6 py-4 bg-gray-200 text-gray-400 rounded-2xl font-bold text-lg flex items-center justify-center cursor-not-allowed",
                ),
            ),
            class_name="mt-8",
        ),
        rx.cond(
            VideoState.is_processing,
            rx.el.div(
                rx.el.div(
                    class_name="h-2 bg-blue-600 rounded-full transition-all duration-300 ease-out",
                    style={"width": f"{VideoState.processing_progress}%"},
                ),
                class_name="w-full h-2 bg-gray-100 rounded-full mt-4 overflow-hidden",
            ),
        ),
        class_name=rx.cond(VideoState.has_video, "block", "hidden"),
    )