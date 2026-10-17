import datetime
import subprocess  # let us run external program from python
import threading
import time
import tkinter as tk

ALARM_SOUND_PATH = "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"
ALARM_REPEAT_COUNT = 2

WEEKDAY_FOCUS_SESSIONS = [
    ("FYP: 3h", 3 * 60 * 60),
    ("Other Modules: 3h", 3 * 60 * 60),
    ("Standout", 2 * 60 * 60),
    ("Job Application", 1 * 60 * 60),
]

WEEKEND_FOCUS_SESSIONS = [
    ("Standout", 3 * 60 * 60),
    ("Job Application", 2 * 60 * 60),
    ("Uni work", 2 * 60 * 60),
]

BREAK_OPTIONS = [
    ("15 min break", 15 * 60),
    ("30 min break", 30 * 60),
    ("45 min break", 45 * 60),
    ("60 min break", 60 * 60),
]

BACKGROUND_COLOUR = "#2c3e50"
FOCUS_COLOUR = "#27ae60"
BREAK_COLOUR = "#e67e22"
CLOCK_COLOUR = "#3498db"

def launch_startup_applications():
    """Launch the desired application when PC is turned on"""
    apps = [
        "code",
        "brave-browser https://open.spotify.com/",
        "brave-browser https://blackboard.salford.ac.uk/ultra"
    ]

    for app in apps:
        try:
            subprocess.Popen(app, shell=True)
            print(f"Launched {app}")
            time.sleep(1)
        except Exception as error:
            print(f"Failed to launch {app}: {error}")

    start_focus_timer_window()

def formatSecondsAsClockText(total_seconds):
    """Return seconds as HH:MM:SS"""
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def playAlarmSoundRepeatedly(repeat_count=ALARM_REPEAT_COUNT):
    """Play the system alarm sound a number of times"""
    for _ in range(repeat_count):
        try:
            subprocess.run(["paplay", ALARM_SOUND_PATH], check=True)
        except Exception as error:
            print(f"Failed to play alarm sound: {error}")
            return

def playAlarmSoundInBackground():
    """Play the alarm on a separate thread so the window stays responsive"""
    threading.Thread(target=playAlarmSoundRepeatedly, daemon=True).start()

def getFocusSessionsForToday():
    """Return the weekday or weekend focus sessions based on today's date"""
    is_weekend = datetime.date.today().weekday() >= 5
    return WEEKEND_FOCUS_SESSIONS if is_weekend else WEEKDAY_FOCUS_SESSIONS

def start_focus_timer_window():
    """Pick a focus session, count it down, then pick a break"""
    root = tk.Tk()
    root.title("Focus Session")
    root.geometry("900x400")
    root.configure(bg=BACKGROUND_COLOUR)

    day_label = tk.Label(root, text="", font=("Arial", 18), fg=CLOCK_COLOUR, bg=BACKGROUND_COLOUR)
    day_label.pack(pady=(20, 0))
    status_label = tk.Label(root, text="", font=("Arial", 24), fg=FOCUS_COLOUR, bg=BACKGROUND_COLOUR)
    status_label.pack(pady=(10, 10))

    clock_label = tk.Label(root, text="", font=("Arial", 54, "bold"), fg=CLOCK_COLOUR, bg=BACKGROUND_COLOUR)
    clock_label.pack(pady=10)

    button_frame = tk.Frame(root, bg=BACKGROUND_COLOUR)
    button_frame.pack(pady=20)

    pending_countdown_id = None

    def cancelPendingCountdown():
        nonlocal pending_countdown_id
        if pending_countdown_id is not None:
            root.after_cancel(pending_countdown_id)
            pending_countdown_id = None

    def addEndButtonThatReturnsToFocusSessions():
        removeAllButtonsFromFrame()
        tk.Button(
            button_frame,
            text="End",
            font=("Arial", 14),
            width=16,
            command=endCountdownAndShowFocusSessions,
        ).grid(row=0, column=0, padx=8)

    def endCountdownAndShowFocusSessions():
        cancelPendingCountdown()
        show_focus_session_buttons()

    def removeAllButtonsFromFrame():
        for button in button_frame.winfo_children():
            button.destroy()

    def addButtonsToFrame(label_and_seconds_pairs, on_button_clicked):
        removeAllButtonsFromFrame()
        for column_index, (button_text, duration_seconds) in enumerate(label_and_seconds_pairs):
            tk.Button(
                button_frame,
                text=button_text,
                font=("Arial", 14),
                width=16,
                command=lambda text=button_text, seconds=duration_seconds: on_button_clicked(text, seconds),
            ).grid(row=0, column=column_index, padx=8)

    def countdown_then_call(seconds_left, on_finished):
        nonlocal pending_countdown_id
        clock_label.config(text=formatSecondsAsClockText(seconds_left))
        if seconds_left <= 0:
            pending_countdown_id = None
            on_finished()
            return
        pending_countdown_id = root.after(1000, countdown_then_call, seconds_left - 1, on_finished)

    def show_focus_session_buttons():
        day_label.config(text=datetime.date.today().strftime("%A"))
        status_label.config(text="Choose a focus session", fg=FOCUS_COLOUR)
        clock_label.config(text="")
        addButtonsToFrame(getFocusSessionsForToday(), start_focus_session_countdown)

    def start_focus_session_countdown(session_name, session_seconds):
        addEndButtonThatReturnsToFocusSessions()
        status_label.config(text=f"Focus: {session_name}", fg=FOCUS_COLOUR)
        countdown_then_call(session_seconds, show_break_buttons_after_focus)

    def show_break_buttons_after_focus():
        playAlarmSoundInBackground()
        status_label.config(text="Session complete. Choose a break", fg=BREAK_COLOUR)
        addButtonsToFrame(BREAK_OPTIONS + [("Skip", 0)], start_break_countdown_or_skip)

    def start_break_countdown_or_skip(break_name, break_secon):
        if break_seconds == 0:
            show_focus_session_buttons()
            return
        addEndButtonThatReturnsToFocusSessions()
        status_label.config(text=break_name, fg=BREAK_COLOUR)
        countdown_then_call(break_seconds, finish_break_and_show_focus_sessions)

    def finish_break_and_show_focus_sessions():
        playAlarmSoundInBackground()
        show_focus_session_buttons()

    show_focus_session_buttons()
    root.mainloop()

if __name__ == "__main__":
    launch_startup_applications()