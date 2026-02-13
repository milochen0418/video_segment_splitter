import reflex as rx
from video_segment_splitter.states.system_state import SystemState
from video_segment_splitter.states.video_state import VideoState


def _cpu_bar(percent: rx.Var[float], index: rx.Var[int]) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            rx.cond(index < 10, f" {index}", f"{index}"),
            class_name="text-green-400 font-mono text-xs w-6 shrink-0",
        ),
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    percent > 80,
                    "h-full bg-red-500 rounded-sm transition-all duration-300",
                    rx.cond(
                        percent > 50,
                        "h-full bg-yellow-500 rounded-sm transition-all duration-300",
                        "h-full bg-green-500 rounded-sm transition-all duration-300",
                    ),
                ),
                style={"width": rx.cond(percent > 0, percent.to(str) + "%", "0%")},
            ),
            class_name="flex-1 h-3 bg-gray-800 rounded-sm overflow-hidden",
        ),
        rx.el.span(
            percent.to(str) + "%",
            class_name="text-gray-400 font-mono text-xs w-14 text-right shrink-0",
        ),
        class_name="flex items-center gap-2",
    )


def _stat_row(label: str, value: rx.Var, color: str = "text-cyan-400") -> rx.Component:
    return rx.el.div(
        rx.el.span(label, class_name="text-gray-500 font-mono text-xs"),
        rx.el.span(value, class_name=f"{color} font-mono text-xs font-bold"),
        class_name="flex justify-between items-center",
    )


def system_busy_button() -> rx.Component:
    """Floating 'System Busy' button + inline panel shown during processing."""
    return rx.cond(
        VideoState.is_processing,
        rx.el.div(
            # Panel (above the button)
            rx.cond(
                SystemState.show_system_modal,
                rx.el.div(
                    # Title bar
                    rx.el.div(
                        rx.el.div(
                            rx.icon("monitor", class_name="h-3.5 w-3.5 text-green-400"),
                            rx.el.span(
                                "System Monitor",
                                class_name="text-green-400 font-mono text-xs font-bold",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon("refresh-cw", class_name="h-3 w-3"),
                                on_click=SystemState.refresh_stats,
                                class_name="text-gray-500 hover:text-green-400 transition-colors p-1",
                            ),
                            rx.el.button(
                                rx.icon("x", class_name="h-3.5 w-3.5"),
                                on_click=SystemState.close_system_modal,
                                class_name="text-gray-500 hover:text-red-400 transition-colors p-1",
                            ),
                            class_name="flex items-center gap-0.5",
                        ),
                        class_name="flex justify-between items-center px-3 py-1.5 bg-gray-900 border-b border-gray-700 rounded-t-xl",
                    ),
                    # Body
                    rx.el.div(
                        # CPU section
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    "CPU",
                                    class_name="text-yellow-400 font-mono text-[10px] font-bold tracking-wider",
                                ),
                                rx.el.span(
                                    SystemState.cpu_percent_total.to(str) + "%",
                                    class_name="text-gray-500 font-mono text-[10px]",
                                ),
                                class_name="flex justify-between items-center mb-1",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    SystemState.cpu_percents,
                                    lambda p, i: _cpu_bar(p, i),
                                ),
                                class_name="flex flex-col gap-0.5",
                            ),
                            class_name="mb-3",
                        ),
                        # Memory section
                        rx.el.div(
                            rx.el.span(
                                "MEMORY",
                                class_name="text-yellow-400 font-mono text-[10px] font-bold tracking-wider mb-1 block",
                            ),
                            _stat_row(
                                "Used / Total",
                                SystemState.mem_used_gb + "G / " + SystemState.mem_total_gb + "G",
                                "text-green-400",
                            ),
                            _stat_row(
                                "Usage",
                                SystemState.mem_percent.to(str) + "%",
                                "text-cyan-400",
                            ),
                            class_name="mb-3",
                        ),
                        # Swap section
                        rx.el.div(
                            rx.el.span(
                                "SWAP",
                                class_name="text-yellow-400 font-mono text-[10px] font-bold tracking-wider mb-1 block",
                            ),
                            _stat_row(
                                "Used / Total",
                                SystemState.swap_used_gb + "G / " + SystemState.swap_total_gb + "G",
                                "text-green-400",
                            ),
                            _stat_row(
                                "Usage",
                                SystemState.swap_percent.to(str) + "%",
                                "text-cyan-400",
                            ),
                            class_name="mb-3",
                        ),
                        # System info
                        rx.el.div(
                            rx.el.span(
                                "SYSTEM",
                                class_name="text-yellow-400 font-mono text-[10px] font-bold tracking-wider mb-1 block",
                            ),
                            _stat_row(
                                "Tasks",
                                SystemState.task_count.to(str),
                                "text-white",
                            ),
                            _stat_row(
                                "Load Avg",
                                SystemState.load_avg_1
                                + "  "
                                + SystemState.load_avg_5
                                + "  "
                                + SystemState.load_avg_15,
                                "text-white",
                            ),
                            _stat_row(
                                "Uptime",
                                SystemState.uptime_str,
                                "text-white",
                            ),
                        ),
                        class_name="px-3 py-2 overflow-y-auto max-h-[60vh]",
                    ),
                    class_name="mb-2 w-[360px] bg-gray-950 rounded-xl border border-gray-700 shadow-2xl",
                ),
            ),
            # Button
            rx.el.button(
                rx.el.div(
                    rx.el.div(
                        class_name="h-2.5 w-2.5 bg-orange-500 rounded-full animate-pulse",
                    ),
                    rx.el.span(
                        "System Busy",
                        class_name="text-xs font-bold text-orange-600",
                    ),
                    class_name="flex items-center gap-2",
                ),
                on_click=SystemState.toggle_system_modal,
                class_name="flex items-center gap-2 px-4 py-2.5 bg-orange-50 border border-orange-200 rounded-full shadow-lg hover:bg-orange-100 hover:shadow-xl transition-all duration-200 cursor-pointer",
            ),
            class_name="fixed bottom-6 right-6 z-50 flex flex-col items-end",
        ),
    )


def system_monitor_modal() -> rx.Component:
    """No-op: panel is now inline in system_busy_button."""
    return rx.fragment()
