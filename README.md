# AlgoPattern Home Assistant Integration

Unofficial Home Assistant custom component integration for **AlgoPattern** — the coding interview algorithmic pattern recognition trainer.

![AlgoPattern Logo](custom_components/algopattern/brand/logo.png)

## 🚀 Features

- **Live Daily Streak & XP Tracking**: Real-time synchronization with AlgoPattern server RPC endpoints.
- **Smart Entity Registry Defaults**:
  - **Pertinent Entities Enabled by Default**: Core metrics (Streak Length, Total XP, Streak Freezes, Daily Challenge Completed, Active Today) are enabled out-of-the-box for clean, distraction-free dashboards.
  - **Comprehensive Diagnostic Entities Available**: Detailed metadata (Total Active Days, Last Active Date, Quizzes Completed, Experience Level, Prep Goal, Scheduled Reminder Time, Reminder Enabled, Immediate Feedback, PRO Account status) are fully registered and can be enabled at any time in Settings > Devices & Services > Entities.
- **Local Brand Folder Assets**: Included directly inside `brand/` (`icon.png`, `logo.png`, `dark_logo.png` with `@2x` high-DPI support) for native Home Assistant 2026.3+ logo resolution.
- **Seamless Authentication**: Support for Email/Password login.

---

## 📁 Integration Structure

```
custom_components/algopattern/
├── __init__.py
├── api.py
├── binary_sensor.py
├── config_flow.py
├── const.py
├── coordinator.py
├── manifest.json
├── select.py
├── sensor.py
├── strings.json
├── switch.py
├── time.py
├── brand/
│   ├── icon.png
│   ├── icon@2x.png
│   ├── logo.png
│   ├── logo@2x.png
│   ├── dark_logo.png
│   └── dark_logo@2x.png
└── translations/
    ├── en.json
    └── fr.json
```

---

## 📊 Entity Catalog

### Sensors

| Entity ID | Name | Default State | Category | Description |
| :--- | :--- | :--- | :--- | :--- |
| `sensor.algopattern_streak_length` | Streak Length | **Enabled** | Primary | Current practice streak in days (with `active_dates` attributes). |
| `sensor.algopattern_total_xp` | Total XP | **Enabled** | Primary | Total cumulative algorithmic XP. |
| `sensor.algopattern_streak_freezes_available` | Streak Freezes | **Enabled** | Primary | Available streak freeze protection shields. |
| `sensor.algopattern_total_active_days` | Total Active Days | Disabled | Diagnostic | Historical count of active drill days. |
| `sensor.algopattern_last_active_date` | Last Active Date | Disabled | Diagnostic | Date of last logged pattern drill. |
| `sensor.algopattern_quizzes_completed` | Quizzes Completed | Disabled | Diagnostic | Total daily challenge drills finished. |
| `sensor.algopattern_experience_level` | Experience Level | Disabled | Diagnostic | Algorithmic tier (Beginner, Intermediate, Advanced). |
| `sensor.algopattern_preparation_goal` | Preparation Goal | Disabled | Diagnostic | Primary interview goal. |
| `sensor.algopattern_daily_reminder_time` | Reminder Time | Disabled | Diagnostic | Scheduled reminder time (HH:MM). |
| `sensor.algopattern_user_id` | User ID | Disabled | Diagnostic | AlgoPattern server account UUID. |

### Binary Sensors

| Entity ID | Name | Default State | Category | Description |
| :--- | :--- | :--- | :--- | :--- |
| `binary_sensor.algopattern_daily_challenge_completed` | Daily Challenge Completed | **Enabled** | Primary | `on` if today's 5-question challenge is done. |
| `binary_sensor.algopattern_active_today` | Active Today | **Enabled** | Primary | `on` if any pattern practice occurred today. |
| `binary_sensor.algopattern_pro_account` | PRO Account | Disabled | Diagnostic | `on` for active PRO tier. |
| `binary_sensor.algopattern_daily_reminder_enabled` | Reminder Enabled | Disabled | Diagnostic | `on` if daily reminders are configured. |
| `binary_sensor.algopattern_immediate_feedback` | Immediate Feedback | Disabled | Diagnostic | `on` for per-question explanation feedback. |

---

## 🎨 Lovelace Dashboard Example

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: AlgoPattern
    subtitle: Daily DSA Pattern Recognition Drill

  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.algopattern_streak_length
        name: Streak
        icon: mdi:fire
        icon_color: amber

      - type: custom:mushroom-entity-card
        entity: sensor.algopattern_total_xp
        name: Total XP
        icon: mdi:star-circle
        icon_color: indigo

      - type: custom:mushroom-entity-card
        entity: binary_sensor.algopattern_daily_challenge_completed
        name: Today's Quiz
        icon: mdi:check-decagram
        icon_color: green
```

---

## ⏰ Automation Example: Daily Study Reminder

```yaml
alias: "AlgoPattern: Daily Evening Reminder"
trigger:
  - platform: time
    at: "18:00:00"
condition:
  - condition: state
    entity_id: binary_sensor.algopattern_daily_challenge_completed
    state: "off"
action:
  - service: notify.notify
    data:
      title: "🔥 Keep Your AlgoPattern Streak Alive!"
      message: "You have not completed today's 5-question pattern drill yet. Take 3 minutes to maintain your streak!"
```
