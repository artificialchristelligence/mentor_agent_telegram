# Mentor Agent

A personal growth mentor powered by DeepSeek (or your choice) + LangChain, backed by MongoDB, served over Flask, and delivered via Telegram.

---
### Update

2026/3/30

Added proactive scheduled message pushing - check knock_manual.md for details.

---

Video Tutorial 
https://youtu.be/qOPqg9lx6qo

## Project Structure

```
mentor_agent/
├── app.py              # Flask server + LINE webhook
├── mentor_agent.py     # LangChain agent, tools, DeepSeek model
├── mongodb_mentor.py   # MongoDB helpers (reflections, incidents, reminders, growth)
├── requirements.txt
├── knock.txt           # Scheduled jobs
├── knock_manual.md     # Instructions on scheduled jobs
└── .env                # secrets (never commit this)

```

## Installation
To install and use the agent, follow these steps:

Clone the repository:

On Visual Studio or Git, 

git clone https://github.com/artificialchristelligence/mentor_agent_telegram.git

cd mentor_agent_telegram

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

1. MongoDB Database Password (DB_PASSWORD)

This is your MongoDB user password (used in your connection string).

Steps:

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

2. LangSmith API Key (LANGSMITH_API_KEY)

Used for tracing and debugging LangChain applications.

Steps:

- Visit LangSmith: https://smith.langchain.com/
- Sign in with your account.
- Go to **Settings (bottom left) → API Keys**
- Click **Create API Key**
- Copy the key and paste it into your `.env` file as `LANGSMITH_API_KEY`

---

3. DeepSeek API Key (DEEPSEEK_API_KEY)

Used to power the AI model for your mentor agent.

Steps:

- Go to DeepSeek: https://platform.deepseek.com/
- Sign up or log in.
- Navigate to the **API Keys** section.
- Click **Create API Key**
- Copy the generated key
- Paste it into your `.env` file as `DEEPSEEK_API_KEY`

---

4. Telegram Bot Token (TELEGRAM_BOT_TOKEN)

Required to connect your app to Telegram.

Steps:

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

✅ Final `.env` Example

```bash
DB_PASSWORD="your_mongodb_password"
LANGSMITH_API_KEY="your_langsmith_key"
DEEPSEEK_API_KEY="your_deepseek_key"
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
```

## 2. Create and Activate a Virtual Environment

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

## 3. Install dependencies:

```bash
pip install -r requirements.txt
```

## 4. modify MongoDB database URL

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

## 5. Run the server:

```bash
python app.py
```

Server starts on port 5001.

## MongoDB Collections

All stored in the `journals` database:

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

## 6. Agent Tools

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


## 7. Hosting Server

Once your mentor agent is working locally, you can deploy it so it runs continuously and can be accessed externally. Below are three hosting options with step-by-step instructions.

---

### Option 1: Run on Local Machine (Development / Testing)

This is the simplest way to run your server.

#### Steps:

1. **Start your virtual environment**
```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
```

2. **Run the Flask server**
```bash
   python app.py
```

3. **Access locally**

   Open browser: `http://127.0.0.1:5001`

4. **Connect to Telegram**

   This bot uses **polling** — it continuously checks Telegram for new messages. You only need your `TELEGRAM_BOT_TOKEN` set in your `.env` file. No webhook setup is required.

**Pros:** Easy to set up, great for development  
**Cons:** Must keep your computer running, not stable for production

---

### Option 2: Deploy on Azure Web App (Cloud Hosting)

Best for scalability and reliability. All steps are done through the **Azure Portal** — no CLI required.

#### Prerequisites:
- An [Azure account](https://portal.azure.com)

#### Steps:

1. **Create a Resource Group**

   - Go to [portal.azure.com](https://portal.azure.com)
   - Search for **Resource Groups** → click **Create**
   - Name it `mentor-agent-rg`, choose your region → click **Review + Create**

2. **Create an App Service Plan**

   - Search for **App Service Plans** → click **Create**
   - Select your resource group `mentor-agent-rg`
   - Choose **Linux** as the OS and **Basic B1** as the pricing tier

3. **Create a Web App**

   - Search for **App Services** → click **Create**
   - Select your resource group and App Service Plan
   - Set the runtime to **Python 3.11**
   - Give your app a unique name (e.g., `mentor-agent-yourname`)

4. **Set Environment Variables**

   - Open your Web App → go to **Settings**
   - Click **Environmental Variables** and add each of the following:

     | Name | Value |
     |---|---|
     | `DB_PASSWORD` | `...` |
     | `LANGSMITH_API_KEY` | `...` |
     | `DEEPSEEK_API_KEY` | `...` |
     | `TELEGRAM_BOT_TOKEN` | `...` |

   - Click **Save**

5. **Set the Startup Command**

   - Still in **Configuration** → go to **General Settings**
   - Set the startup command to:
```
     gunicorn --bind=0.0.0.0 --timeout 600 app:app
```
   - Click **Save**

6. **Deploy Your Code**

   - Go to **Deployment Center** inside your Web App
   - Choose your source (e.g., **GitHub**, **Bitbucket**, or **Local Git**)
   - Follow the prompts to connect your repository and deploy

7. **Verify Telegram is Working**

   Since the bot uses polling, once the app is running it will automatically start receiving Telegram messages — no webhook needed.

**Pros:** Always online, scalable, production-ready  
**Cons:** Slight cost after free tier

---

### Option 3: Run on Raspberry Pi (Self-Hosted)

Great for personal projects and learning infrastructure.

#### Prerequisites:
- Raspberry Pi (preferably 4)
- Raspberry Pi OS installed
- Internet connection

#### Steps:

1. **Update system**
```bash
   sudo apt update && sudo apt upgrade -y
```

2. **Install Python & Git**
```bash
   sudo apt install python3 python3-venv python3-pip git -y
```

3. **Clone your project**
```bash
   git clone <your-repo-url>
   cd mentor_agent_telegram
```

4. **Set up virtual environment**
```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```

5. **Add `.env` file**
```bash
   nano .env
```

6. **Run server**
```bash
   python app.py
```

7. **Make it persistent (systemd service)**

   Create the service file:
```bash
   sudo nano /etc/systemd/system/mentor-agent_telegram.service
```

   Paste the following:
```ini
   [Unit]
   Description=Mentor Agent Flask App
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/mentor_agent_telegram
   ExecStart=/home/pi/mentor_agent_telegram/venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
```

   Enable the service:
```bash
   sudo systemctl daemon-reexec
   sudo systemctl daemon-reload
   sudo systemctl enable mentor-agent=telegram
   sudo systemctl start mentor-agent-telegram
```

8. **Telegram Connection**

   The bot uses polling, so once the app is running, it will automatically connect to Telegram using your `TELEGRAM_BOT_TOKEN`. No additional setup needed.

**Pros:** Low cost (one-time hardware), full control  
**Cons:** Requires networking setup, less reliable than cloud

---

### Summary

| Option         | Best For         | Difficulty | Cost        |
|----------------|------------------|------------|-------------|
| Local Machine  | Development      | Easy       | Free        |
| Azure Web App  | Production       | Medium     | $$          |
| Raspberry Pi   | Personal Hosting | Medium     | One-time    |
