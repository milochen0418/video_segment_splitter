import reflex as rx
import psutil
import asyncio
import time


# Prime psutil so first non-blocking call returns real values
psutil.cpu_percent(percpu=True)


def _collect_system_stats() -> dict:
    """Collect system stats. Called via asyncio.to_thread to avoid
    blocking the event loop. The real fix for UI responsiveness during
    heavy encoding is limiting ffmpeg's thread count (see video_state.py),
    so that CPU cores remain available for the web server and this function."""
    cpu_percents = psutil.cpu_percent(interval=None, percpu=True)
    cpu_total = psutil.cpu_percent(interval=None)

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    load1, load5, load15 = psutil.getloadavg()
    pids_count = len(psutil.pids())

    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    return {
        "cpu_percents": cpu_percents,
        "cpu_percent_total": cpu_total,
        "mem_total_gb": f"{mem.total / (1024 ** 3):.1f}",
        "mem_used_gb": f"{mem.used / (1024 ** 3):.1f}",
        "mem_percent": mem.percent,
        "swap_total_gb": f"{swap.total / (1024 ** 3):.2f}",
        "swap_used_gb": f"{swap.used / (1024 ** 3):.2f}",
        "swap_percent": swap.percent,
        "load_avg_1": f"{load1:.2f}",
        "load_avg_5": f"{load5:.2f}",
        "load_avg_15": f"{load15:.2f}",
        "task_count": pids_count,
        "uptime_str": f"{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}",
    }


class SystemState(rx.State):
    show_system_modal: bool = False
    cpu_percent_total: float = 0.0
    cpu_percents: list[float] = []
    mem_total_gb: str = "0.0"
    mem_used_gb: str = "0.0"
    mem_percent: float = 0.0
    swap_total_gb: str = "0.0"
    swap_used_gb: str = "0.0"
    swap_percent: float = 0.0
    load_avg_1: str = "0.00"
    load_avg_5: str = "0.00"
    load_avg_15: str = "0.00"
    task_count: int = 0
    uptime_str: str = ""

    @rx.event
    def toggle_system_modal(self):
        """Instant toggle – no blocking work here."""
        self.show_system_modal = not self.show_system_modal
        if self.show_system_modal:
            return SystemState.auto_refresh

    @rx.event
    def close_system_modal(self):
        self.show_system_modal = False

    @rx.event
    def refresh_stats(self):
        """Manual refresh – triggers background collection."""
        return SystemState.auto_refresh_once

    @rx.event(background=True)
    async def auto_refresh_once(self):
        """Single-shot stats collection in a thread."""
        stats = await asyncio.to_thread(_collect_system_stats)
        async with self:
            self._apply_stats(stats)

    @rx.event(background=True)
    async def auto_refresh(self):
        """Continuously refresh stats every 2s while modal is open.
        Stats are collected in a thread via asyncio.to_thread."""
        while True:
            stats = await asyncio.to_thread(_collect_system_stats)
            async with self:
                if not self.show_system_modal:
                    return
                self._apply_stats(stats)
            await asyncio.sleep(2.0)

    def _apply_stats(self, stats: dict):
        """Assign pre-collected stats to state vars. Very fast."""
        self.cpu_percents = stats["cpu_percents"]
        self.cpu_percent_total = stats["cpu_percent_total"]
        self.mem_total_gb = stats["mem_total_gb"]
        self.mem_used_gb = stats["mem_used_gb"]
        self.mem_percent = stats["mem_percent"]
        self.swap_total_gb = stats["swap_total_gb"]
        self.swap_used_gb = stats["swap_used_gb"]
        self.swap_percent = stats["swap_percent"]
        self.load_avg_1 = stats["load_avg_1"]
        self.load_avg_5 = stats["load_avg_5"]
        self.load_avg_15 = stats["load_avg_15"]
        self.task_count = stats["task_count"]
        self.uptime_str = stats["uptime_str"]
