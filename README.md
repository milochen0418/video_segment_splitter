# Video Segment Splitter

> Important: Before working on this project, read [AGENTS.md](AGENTS.md) for required workflows and tooling expectations.

## Software Design Document

The software design document (SDD) for this project is available at [Video Segment Splitter (ClipShift) - Software Design Document (SDD).pdf](docs/Video%20Segment%20Splitter%20(ClipShift)%20-%20Software%20Design%20Document%20(SDD).pdf).

## Quick Start (With Screenshots)

Follow these steps to split your video quickly, even on your first use:

### 1) Open the landing page

After opening the app, you will see the upload area in the center.

![Landing page](docs/images/landing-page.png)

### 2) Upload your video

Drag and drop your video into the upload area (or click to browse). Supported formats: MP4, MOV, AVI.

![Uploaded video and metadata](docs/images/uploaded-video-and-its-info.png)

### 3) Set the number of segments

Use **Number of Segments** (number input or slider) to choose how many parts to create. The UI also shows the estimated duration per segment.

![Select number of segments](docs/images/select-numbers-of-segments.png)

### 4) Start splitting

Click **Start Splitting Video** to begin processing. A progress state will be shown while splitting.

![Video splitting in progress](docs/images/video-spliting-busy.png)

### 5) (Optional) Monitor system load

When splitting longer videos, you can open the system monitor to observe CPU and memory usage.

![Video splitting with system monitor](docs/images/video-spliting-with-system-monitor.png)

### 6) Download results

After processing completes, the generated clips will appear in **Output Clips**. You can:

- Download clips one by one
- Click **Zip All Clips** to generate and download a ZIP bundle

![Video splitting download result](docs/images/download-result.png)



## Getting Started

> Before making changes, read the project guidelines in [AGENTS.md](AGENTS.md).

This project is managed with [uv](https://docs.astral.sh/uv/).

### Prerequisites

Based on this project's dependencies, install the following system-level packages first via Homebrew (macOS):

```bash
brew install uv ffmpeg
```

| Package | Reason |
|---------|--------|
| `uv` | Python package and project manager used to manage this project; it also installs Python 3.11 (pinned in `.python-version`) when it is missing |
| `ffmpeg` | Required by `moviepy` for video cutting, merging, and transcoding |

### Installation

Install dependencies into `.venv/` (uv uses Python 3.11 from `.python-version` and the exact versions in `uv.lock`):

```bash
uv sync
```

Playwright (a dev dependency, installed by `uv sync`) also needs its browser binaries:

```bash
uv run playwright install
```

### Running the App

Start the development server:

```bash
uv run ./reflex_rerun.sh
```

The application will be available at `http://localhost:3000`.

### Clean Rebuild & Run

To fully clean the environment, reinstall all dependencies, and start the app in one step:

```bash
./proj_reinstall.sh --with-rerun
```

This will remove the project's `.venv/` and Reflex artifacts, recreate the environment from scratch with `uv sync`, and automatically launch the app afterwards.

