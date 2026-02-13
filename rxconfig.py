import reflex as rx

config = rx.Config(
    app_name="video_segment_splitter",
    api_url="http://localhost:8000",
    plugins=[
        rx.plugins.TailwindV3Plugin(),
        rx.plugins.SitemapPlugin(),
    ],
)
