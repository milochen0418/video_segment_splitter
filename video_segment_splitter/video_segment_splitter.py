import reflex as rx
from video_segment_splitter.states.video_state import VideoState
from video_segment_splitter.components.upload_zone import upload_zone
from video_segment_splitter.components.metadata_card import metadata_card
from video_segment_splitter.components.controls import controls


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            class_name="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-blue-50 to-white -z-10"
        ),
        rx.el.div(
            rx.el.header(
                rx.el.div(
                    rx.icon("video", class_name="h-8 w-8 text-blue-600"),
                    rx.el.h1(
                        "ClipShift",
                        class_name="text-2xl font-black text-gray-900 tracking-tight",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.nav(
                    rx.el.a(
                        "GitHub",
                        href="https://github.com/milochen0418/video_segment_splitter",
                        target="_blank",
                        class_name="px-4 py-2 bg-gray-900 text-white rounded-xl text-sm font-bold hover:bg-gray-800 transition-colors",
                    ),
                    class_name="flex items-center gap-8",
                ),
                class_name="flex justify-between items-center mb-16",
            ),
            rx.el.div(
                rx.el.h2(
                    "Split videos with precision.",
                    class_name="text-5xl font-extrabold text-gray-900 text-center mb-4",
                ),
                rx.el.p(
                    "Professional-grade video splitting directly in your browser. Fast, secure, and intuitive.",
                    class_name="text-xl text-gray-500 text-center mb-12 max-w-2xl mx-auto",
                ),
                rx.el.div(
                    upload_zone(),
                    metadata_card(),
                    controls(),
                    class_name="max-w-3xl mx-auto",
                ),
                rx.el.div(
                    rx.cond(
                        VideoState.has_video,
                        rx.el.div(
                            rx.el.div(class_name="h-px bg-gray-100 w-full my-12"),
                            rx.el.div(
                                rx.el.h3(
                                    "Output Clips",
                                    class_name="text-2xl font-black text-gray-900",
                                ),
                                rx.cond(
                                    VideoState.generated_segments.length() > 0,
                                    rx.cond(
                                        VideoState.zip_download_url != "",
                                        rx.el.a(
                                            rx.icon(
                                                "archive", class_name="h-4 w-4 mr-2"
                                            ),
                                            "Download ZIP Bundle",
                                            href=VideoState.zip_download_url,
                                            target="_blank",
                                            class_name="flex items-center px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 transition-all shadow-sm",
                                        ),
                                        rx.el.button(
                                            rx.cond(
                                                VideoState.is_zipping,
                                                rx.icon(
                                                    "squirrel",
                                                    class_name="h-4 w-4 animate-spin",
                                                ),
                                                rx.icon(
                                                    "folder-archive",
                                                    class_name="h-4 w-4 mr-2",
                                                ),
                                            ),
                                            rx.cond(
                                                VideoState.is_zipping,
                                                "Creating...",
                                                "Zip All Clips",
                                            ),
                                            on_click=VideoState.create_zip_download,
                                            disabled=VideoState.is_zipping,
                                            class_name="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-xl text-sm font-bold hover:bg-gray-200 transition-all",
                                        ),
                                    ),
                                ),
                                class_name="flex justify-between items-end mb-8",
                            ),
                            rx.cond(
                                VideoState.generated_segments.length() > 0,
                                rx.el.div(
                                    rx.foreach(
                                        VideoState.generated_segments,
                                        lambda segment, i: rx.el.div(
                                            rx.el.div(
                                                rx.el.div(
                                                    rx.icon(
                                                        "clapperboard",
                                                        class_name="h-5 w-5 text-blue-600",
                                                    ),
                                                    rx.el.span(
                                                        f"PART {i + 1}",
                                                        class_name="text-[10px] font-black text-blue-600 tracking-widest uppercase",
                                                    ),
                                                    class_name="flex items-center gap-2 mb-3 bg-blue-50 px-3 py-1 rounded-full w-fit",
                                                ),
                                                rx.el.h4(
                                                    segment.filename,
                                                    class_name="font-bold text-gray-900 text-sm truncate max-w-[200px] mb-1",
                                                ),
                                                rx.el.div(
                                                    rx.icon(
                                                        "clock",
                                                        class_name="h-3 w-3 mr-1",
                                                    ),
                                                    rx.el.span(
                                                        segment.duration_formatted
                                                    ),
                                                    class_name="flex items-center text-xs font-bold text-gray-400",
                                                ),
                                                class_name="flex flex-col flex-1",
                                            ),
                                            rx.el.a(
                                                rx.icon(
                                                    "download", class_name="h-4 w-4"
                                                ),
                                                href=segment.download_url,
                                                download=segment.filename,
                                                target="_blank",
                                                class_name="flex items-center justify-center h-10 w-10 bg-white border border-gray-200 rounded-xl text-gray-700 hover:bg-blue-600 hover:text-white hover:border-blue-600 transition-all duration-200",
                                            ),
                                            class_name="flex items-center justify-between p-5 bg-white border border-gray-100 rounded-2xl hover:border-blue-200 hover:shadow-lg transition-all duration-300 animate-in fade-in slide-in-from-bottom-2",
                                        ),
                                    ),
                                    class_name="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.icon(
                                            "film",
                                            class_name="h-10 w-10 text-gray-300 mb-2",
                                        ),
                                        rx.el.p(
                                            "Clips will appear here after processing",
                                            class_name="text-sm text-gray-400 font-medium",
                                        ),
                                        class_name="flex flex-col items-center justify-center border-2 border-dashed border-gray-100 rounded-3xl h-64 bg-gray-50/30",
                                    ),
                                    class_name="max-w-3xl mx-auto",
                                ),
                            ),
                        ),
                    )
                ),
                class_name="w-full",
            ),
            rx.el.footer(
                rx.el.p(
                    "© 2026 ClipShift. Powered by Reflex & MoviePy.",
                    class_name="text-sm text-gray-400 font-medium",
                ),
                class_name="mt-24 pb-12 text-center",
            ),
            class_name="max-w-6xl mx-auto px-6 py-8",
        ),
        class_name="font-['Inter'] min-h-screen bg-white relative overflow-x-hidden",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")