import datetime
import subprocess  # let us run external program from python
import threading
import time
import tkinter as tk

ALARM_SOUND_PATH = "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"
ALARM_REPEAT_COUNT = 2

WEEKDAY_FOCUS_SESSIONS = [
    ("1. FYP 3H", 3 * 60 * 60),
    ("2. Deep Learning 2H", 2 * 60 * 60),
    ("3. Other Module 3H", 3 * 60 * 60),
    ("4. Problem Solving 1H", 1 * 60 * 60),
    ("5. 2 Job Application 1H", 1 * 60 * 60),
]

WEEKDAY_CHECKLIST_ITEMS = [
    "1. FYP 3H",
    "2. Deep Learning 2H",
    "3. Other Module 3H",
    "4. Problem Solving 1H",
    "5. 2 Job Application 1H",
]

DONE_COLOUR = "#7f8c8d"

SUNDAY_CHECKLIST_ITEMS = [
    "1. 4 Job Application 2H",
    "2. 2 Hour Problem Solving",
    "3. Extra Uni Work 2H",
]

SUNDAY_FOCUS_SESSIONS = [
    ("1. 4 Job Application 2H", 2 * 60 * 60),
    ("2. 2 Hour Problem Solving", 2 * 60 * 60),
    ("3. Extra Uni Work 2H", 2 * 60 * 60),
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
TEST_DATE_OVERRIDE = None  # e.g. datetime.date(2026, 10, 17) for a Saturday

def getTodayOrTestOverrideDate():
    """Return the test override date when set, otherwise today's date"""
    return TEST_DATE_OVERRIDE or datetime.date.today()

def launch_startup_applications():
    """Launch the desired application when PC is turned on"""
    apps = [
        "code",
        "brave-browser https://open.spotify.com/",
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

SATURDAY_WEEKDAY_NUMBER = 5
SUNDAY_WEEKDAY_NUMBER = 6

def isTodaySaturdayDayOff():
    """Return True when today is Saturday, which has no focus sessions"""
    return getTodayOrTestOverrideDate().weekday() == SATURDAY_WEEKDAY_NUMBER

def getFocusSessionsForToday():
    """Return the weekday or Sunday focus sessions, or none on Saturday"""
    weekday_number = getTodayOrTestOverrideDate().weekday()
    if weekday_number == SATURDAY_WEEKDAY_NUMBER:
        return []
    return SUNDAY_FOCUS_SESSIONS if weekday_number == SUNDAY_WEEKDAY_NUMBER else WEEKDAY_FOCUS_SESSIONS

def getChecklistItemsForToday():
    """Return the weekday or Sunday checklist items, or none on Saturday"""
    weekday_number = getTodayOrTestOverrideDate().weekday()
    if weekday_number == SATURDAY_WEEKDAY_NUMBER:
        return []
    return SUNDAY_CHECKLIST_ITEMS if weekday_number == SUNDAY_WEEKDAY_NUMBER else WEEKDAY_CHECKLIST_ITEMS

def start_focus_timer_window():
    """Pick a focus session, count it down, then pick a break"""
    root = tk.Tk()
    root.title("Focus Session")
    root.geometry("900x600")
    root.configure(bg=BACKGROUND_COLOUR)

    day_label = tk.Label(root, text="", font=("Arial", 18), fg=CLOCK_COLOUR, bg=BACKGROUND_COLOUR)
    day_label.pack(pady=(20, 0))

    checklist_frame = tk.Frame(root, bg=BACKGROUND_COLOUR)
    checklist_frame.pack(pady=10)

    status_label = tk.Label(root, text="", font=("Arial", 24), fg=FOCUS_COLOUR, bg=BACKGROUND_COLOUR)
    status_label.pack(pady=(10, 10))

    clock_label = tk.Label(root, text="", font=("Arial", 54, "bold"), fg=CLOCK_COLOUR, bg=BACKGROUND_COLOUR)
    clock_label.pack(pady=10)

    button_frame = tk.Frame(root, bg=BACKGROUND_COLOUR)
    button_frame.pack(pady=20)

    pending_countdown_id = None
    completed_session_names = set()
    completed_sessions_date = getTodayOrTestOverrideDate()
    running_focus_session_name = None
    countdown_seconds_left = 0
    countdown_on_finished = None
    is_countdown_paused = False

    def markRunningFocusSessionAsCompleted():
        nonlocal running_focus_session_name
        if running_focus_session_name is not None:
            completed_session_names.add(running_focus_session_name)
            running_focus_session_name = None

    def resetCompletedSessionsWhenDayChanges():
        nonlocal completed_sessions_date
        if getTodayOrTestOverrideDate() != completed_sessions_date:
            completed_session_names.clear()
            completed_sessions_date = getTodayOrTestOverrideDate()

    def refreshNumberedChecklistLabels():
        for checklist_label in checklist_frame.winfo_children():
            checklist_label.destroy()
        for checklist_text in getChecklistItemsForToday():
            tk.Label(
                checklist_frame,
                text=checklist_text,
                font=("Arial", 16),
                fg="white",
                bg=BACKGROUND_COLOUR,
            ).pack(anchor="w")

    def cancelPendingCountdown():
        nonlocal pending_countdown_id
        if pending_countdown_id is not None:
            root.after_cancel(pending_countdown_id)
            pending_countdown_id = None

    def addEndButtonThatReturnsToFocusSessions():
        nonlocal is_countdown_paused
        is_countdown_paused = False
        removeAllButtonsFromFrame()
        pause_button = tk.Button(
            button_frame,
            text="Pause",
            font=("Arial", 14),
            width=16,
        )
        pause_button.config(command=lambda: togglePauseOrContinueCountdown(pause_button))
        pause_button.grid(row=0, column=0, padx=8)
        tk.Button(
            button_frame,
            text="End",
            font=("Arial", 14),
            width=16,
            command=endCountdownAndShowFocusSessions,
        ).grid(row=0, column=1, padx=8)

    def togglePauseOrContinueCountdown(pause_button):
        nonlocal is_countdown_paused
        if is_countdown_paused:
            is_countdown_paused = False
            pause_button.config(text="Pause")
            countdown_then_call(countdown_seconds_left, countdown_on_finished)
        else:
            is_countdown_paused = True
            cancelPendingCountdown()
            pause_button.config(text="Continue")

    def endCountdownAndShowFocusSessions():
        cancelPendingCountdown()
        markRunningFocusSessionAsCompleted()
        show_focus_session_buttons()

    def removeAllButtonsFromFrame():
        for button in button_frame.winfo_children():
            button.destroy()

    def addButtonsToFrame(label_and_seconds_pairs, on_button_clicked, completed_button_texts=()):
        removeAllButtonsFromFrame()
        for column_index, (button_text, duration_seconds) in enumerate(label_and_seconds_pairs):
            is_completed = button_text in completed_button_texts
            tk.Button(
                button_frame,
                text=button_text,
                font=("Arial", 14, "overstrike") if is_completed else ("Arial", 14),
                fg=DONE_COLOUR if is_completed else "black",
                width=16,
                command=lambda text=button_text, seconds=duration_seconds: on_button_clicked(text, seconds),
            ).grid(row=0, column=column_index, padx=8)

    def countdown_then_call(seconds_left, on_finished):
        nonlocal pending_countdown_id, countdown_seconds_left, countdown_on_finished
        countdown_seconds_left = seconds_left
        countdown_on_finished = on_finished
        clock_label.config(text=formatSecondsAsClockText(seconds_left))
        if seconds_left <= 0:
            pending_countdown_id = None
            on_finished()
            return
        pending_countdown_id = root.after(1000, countdown_then_call, seconds_left - 1, on_finished)

    def show_focus_session_buttons():
        resetCompletedSessionsWhenDayChanges()
        refreshNumberedChecklistLabels()
        day_label.config(text=getTodayOrTestOverrideDate().strftime("%A"))
        status_label.config(
            text="Day off" if isTodaySaturdayDayOff() else "Choose a focus session",
            fg=FOCUS_COLOUR,
        )
        clock_label.config(text="")
        addButtonsToFrame(getFocusSessionsForToday(), start_focus_session_countdown, completed_session_names)

    def start_focus_session_countdown(session_name, session_seconds):
        nonlocal running_focus_session_name
        running_focus_session_name = session_name
        addEndButtonThatReturnsToFocusSessions()
        status_label.config(text=f"Focus: {session_name}", fg=FOCUS_COLOUR)
        countdown_then_call(session_seconds, show_break_buttons_after_focus)

    def show_break_buttons_after_focus():
        markRunningFocusSessionAsCompleted()
        playAlarmSoundInBackground()
        status_label.config(text="Session complete. Choose a break", fg=BREAK_COLOUR)
        addButtonsToFrame(BREAK_OPTIONS + [("Skip", 0)], start_break_countdown_or_skip)

    def start_break_countdown_or_skip(break_name, break_seconds):
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
