# AUTOMATION IS THE FUTURE
***The boring and time-consuming task you could automate on your computer that you probably thought of but never implemented. In this project we cover some exciting and useful automation that you could accomplish in just a few lines of code.***

# Task to be implemented 
## 1. Startup Application Launcher

A script that runs automatically when the PC starts up and opens:

- VS Code
- Spotify
- Blackboard
- Focus timer 
Monday - Friday 
The timer will display 4 buttons
1. One with 3 hour with display name "FYP: 3h" 
2. One with 3 hour with display name "Other Modules: 3h"
3. One with 2 hour name "Standout"
4. One with 1 hour name "Job Application"

Saturday - Sunday
1. One with 3 hour "Standout"
2. One with 2 hour "Job Appliacation"

After each timer finish, I will have 5 button which will have break time 
1. 15 min break button 
2. 30 min break button 
3. 45 
4. 60 
5. or skip: if i press skip the display should show me all the option of different timer button depends on the day 


**Purpose:** Save time during project setup and minimize distractions.

### Configuration

Create the autostart entry:

```bash
mkdir -p ~/.config/autostart
code ~/.config/autostart/startup-launcher.desktop

Paste the following into the file:

[Desktop Entry]
Type=Application
Name=Startup Application Launcher
Exec=python3 /home/sujon/Final-Portfolio-Projects/automation-is-the-future/startup-application-launcher/startup_launcher.py
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=10

Mark it executable:

chmod +x ~/.config/autostart/startup-launcher.desktop

X-GNOME-Autostart-Delay=10 holds the launch for ten seconds after login so the desktop session is ready before the applications start.

Testing

Run the script directly rather than rebooting:

python3 startup-application-launcher/startup_launcher.py

To exercise the timer without waiting three hours, temporarily lower the constants at the top of the script:

FOCUS_SECONDS = 10
BREAK_SECONDS = 5
```
---

## 2. Football Match Reminders
Send a reminder on match days for your favourite football team's upcoming matches.

---

## 3. Cricket Match Reminders
Send a reminder on match days for England cricket team matches.

---

## 4. Automated Shutdown at 1 AM
Automatically shut down the PC daily at 1 AM to establish a consistent sleep schedule. Before closing applications, the script will prompt the user to save all work.

**Purpose:** Prevent late-night PC usage and improve sleep habits.

---

## 5. Word Document Formatter
A script that automatically fixes formatting and cleans up messy formatting in Word documents (removes manual formatting tasks).

---

## 6. Weekly Linux Update Scheduler
Automatically fetch and install Linux system updates once per week without requiring manual commands.

---

## 7. Recipe Reminder & Meal Planner
A script that:
- Prompts daily at 1 PM to select a dinner recipe based on your preferences
- Shows ingredients needed
- Reminds you to defrost items at lunchtime
- Sets a cooking timer

**Purpose:** Encourage variety in meals and promote healthy cooking habits.

---

## 8. Mental Health Tracker
A script that prompts you at PC startup to log our emotional state, tracking:
- Happiness
- Anxiety
- Stress
- Sadness
- Loneliness

**Purpose:** Monitor mental well-being monthly to identify patterns and recognize when you need a break or support. 
  
