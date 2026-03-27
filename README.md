# Mentor Agent

A personal growth mentor powered by DeepSeek (or your choice) + LangChain, backed by MongoDB,served over Flask, and delivered via Telegram.

## Project Structure

```
mentor_agent/
├── app.py              # Flask server + LINE webhook
├── mentor_agent.py     # LangChain agent, tools, DeepSeek model
├── mongodb_mentor.py   # MongoDB helpers (reflections, incidents, reminders, growth)
├── requirements.txt
└── .env                # secrets (never commit this)
```

## Setup

## 1. Edit `.env` and fill in your values:

Please watch the tutorial first to understand how to get these API keys.

```
DB_PASSWORD = ""
LANGSMITH_API_KEY = ""
DEEPSEEK_API_KEY =""
TELEGRAM_BOT_TOKEN = ""
```

Follow the instructions below to obtain all required API keys and credentials.

### 1. MongoDB Database Password (DB_PASSWORD)

This is your MongoDB user password (used in your connection string).

### Steps:

- Go to MongoDB: https://www.mongodb.com/
- Sign in or create an account.
- Navigate to MongoDB Atlas (cloud database service).
- Create a new project
- Create a new cluster (free tier is fine).
- Connect to the newly created cluster
- Go to your cluster and **Database Access**:
  - Create a new database user
  - Set a username and password
  - Copy the password to your notebook (We need it for DB_PASSWORD)
  - Click Create Database User
  - Then select Drivers under Connect to your Application
  - Select Python for Driver, 3.11 or later for Version
  - Copy the whole connection string. We need it for Step 4. The connection string looks like <mongodb+srv://youraccount_db_user:tLYzQnm1FhCY2Gsf@cluster0.fuudkbo.mongodb.net/?appName=Cluster0>. We will save it for later use.

---

### 2. LangSmith API Key (LANGSMITH_API_KEY)

Used for tracing and debugging LangChain applications.

### Steps:

- Visit LangSmith: https://smith.langchain.com/
- Sign in with your account.
- Click your profile (top-right corner).
- Go to **Settings → API Keys**
- Click **Create API Key**
- Copy the key and paste it into your `.env` file as `LANGSMITH_API_KEY`

---

### 3. DeepSeek API Key (DEEPSEEK_API_KEY)

Used to power the AI model for your mentor agent.

### Steps:

- Go to DeepSeek: https://platform.deepseek.com/
- Sign up or log in.
- Navigate to the **API Keys** section.
- Click **Create API Key**
- Copy the generated key
- Paste it into your `.env` file as `DEEPSEEK_API_KEY`

---

### 4. Telegram Bot Token (TELEGRAM_BOT_TOKEN)

Required to connect your app to Telegram.

### Steps:

- Open Telegram
- Search for **BotFather**
- Start a chat with BotFather

Send the command:

```
/start
```

Then create a bot:

```
/newbot
```

- Follow the prompts:
  - Enter a bot name
  - Enter a unique username (must end in `bot`)

BotFather will return a token like:

```
123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
```

- Copy this token → use it as your `TELEGRAM_BOT_TOKEN`

---

### ✅ Final `.env` Example

```bash
DB_PASSWORD="your_mongodb_password"
LANGSMITH_API_KEY="your_langsmith_key"
DEEPSEEK_API_KEY="your_deepseek_key"
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
```

2. Create and Activate a Virtual Environment

It’s recommended to use a virtual environment to keep dependencies isolated.

On macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. modify MongoDB database URL

Navigate to your mongoDB account.

- Select the Cluster your just created.
- Select Browse Collections
- On the left hand side, next to the cluster name, click the plus sign
- Create a database. Use "journals" as the database name and "reflections" as its collection name
- Click create database

Navigate back to your codes

- Get the MongoDB connection string you just copied.
- Edit the mongodb_mentor.py file
- Go to MONGO_URL and replace the sample url with your connection string
- Detailed instructions are in mongodb_mentor.py

5. Run the server:

```bash
python app.py
```

Server starts on port 5001.

## MongoDB Collections

All stored in the `mentor_journal` database:

| Collection  | Purpose                                      |
| ----------- | -------------------------------------------- |
| reflections | Dated journal entries with ISO week tracking |
| incidents   | Mistakes and lessons learned                 |
| reminders   | Persistent notes the mentor resurfaces       |
| growth_log  | Milestones and breakthroughs                 |

## REST Endpoints

| Method | Path | Description  |
| ------ | ---- | ------------ |
| GET    | /    | Health check |

## Agent Tools

The mentor agent has 13 tools:

- record_reflection — save a journal entry
- get_this_week_reflections — current week's entries
- get_last_week_reflections — previous week's entries
- get_recent_reflections — N most recent entries
- record_incident — log a mistake or incident with lesson
- get_recent_incidents — review recent incidents
- get_incidents_by_tag — find patterns by tag
- add_reminder — save a persistent reminder
- get_active_reminders — fetch all active reminders
- dismiss_reminder — deactivate a reminder
- record_growth_milestone — log an achievement
- get_growth_timeline — see progress over time
- get_weekly_summary — full week snapshot
