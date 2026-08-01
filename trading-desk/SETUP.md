# Setup guide — getting the desk running on autopilot

Plain steps. You'll do this once. Nothing here needs coding — just clicking and pasting.

## 1. Put the code in a GitHub repo

- Make a free account at github.com if you don't have one.
- Create a new repository (name it something like `trading-desk`). Make it **private**.
- Upload everything in this folder to it (drag-and-drop works, or use GitHub Desktop).

This repo is now the "home" for your desk. Everything lives in one place.

## 2. Get your Twelve Data key

- Log in at twelvedata.com and copy your API key from your account.

## 3. Add the key as a secret (this is the safe part)

- In your repo, go to **Settings > Secrets and variables > Actions > New repository secret**.
- Name: `TWELVEDATA_API_KEY`
- Value: paste your key. Save.

That's it — the key now lives in a locked box GitHub keeps for you. The code reads
it at run time. It is never written in the code and never shown in the chat.

## 4. The timer is already set up

The file `.github/workflows/daily.yml` is your timer. Out of the box it runs the
brief around 8:00 AM New York time, Monday–Thursday. To change the time, edit the
`cron` line in that file (the comment there explains the format — remember it's in
UTC).

## 5. Test it right now (don't wait for tomorrow)

- Go to the **Actions** tab in your repo.
- Click **daily-brief**, then **Run workflow**.
- Watch it run. Open the run to see the printed brief. If it says
  `running on PLACEHOLDER data`, the key isn't being read — recheck step 3.

## 6. (Optional) Run it on your own computer to tinker

When you want to poke at things:

```bash
# one time: set your key for this terminal session
export TWELVEDATA_API_KEY=your_key_here

# see the demo (fabricates a trade to show the full flow)
python -m trading_desk.run

# run the real brief (read-only, uses live data)
python -m trading_desk.brief
```

Prefer a `.env` file locally? Copy `.env.example` to `.env`, fill it in, and either
`export` the value as above or `pip install python-dotenv` and load it — your call.

## What's automated vs. what stays your hands

Automated: pulling data, cleaning it, running all four agents, the debt/tax
tracking, and printing the brief — every scheduled run, on its own.

Your hands only: placing the actual trades and moving actual money. The agents
hand you decisions; you pull the trigger. That one step is meant to stay manual.
