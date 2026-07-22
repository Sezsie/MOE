# MOE: Modular Operations Executor

A voice assistant for your desktop that starts out knowing nothing, and learns whatever you teach it.

Most assistants ship with a fixed list of things they can do. MOE ships with none. You ask for something, MOE writes a script to do it, you look it over and run it. If it worked, give it a name. From then on it is one of MOE's skills, and you can ask for it again in whatever words come naturally.

Built for anyone who has ever wanted their own Jarvis.

---

## What it can do

- **Listen.** Hold `alt+m` and talk, or just say the wake word.
- **Tell chat from work.** MOE figures out whether you are making conversation or asking for something to happen.
- **Learn new tricks.** Ask for something new and MOE writes the code, shows it to you, and runs it once you approve.
- **Remember them.** Name a script and it sticks around. Ask again later, phrased differently, and MOE still finds it.
- **Look things up.** It can search the web and remember things about you between sessions.
- **Talk back.** Replies are spoken aloud in a voice you choose.
- **Stay out of the way.** It lives in the system tray until you need it.

---

## How it works

You speak. MOE transcribes it, decides whether it was a request or just chat, and checks whether you have already taught it something that fits. If you have, it runs that. If you have not, and it sounds like a request, a second AI writes a fresh script for it and hands it to you to review.

```
you talk
   |
   +-> transcribe
   +-> is this a request, or chat?
   +-> do I already know how to do this?
        |
        +-- yes: run the saved script
        +-- no:  reply, and write a new script if it was a request
```

Under the hood it uses a small local model to sort requests from chat, a search over your saved commands to find matches even when the wording changes, and Claude for conversation and code generation. Speech in and out goes through ElevenLabs.

---

## Safety

MOE runs code on your machine, so nothing happens without you seeing it first.

Every script is shown in an editor before it can run. MOE also checks the code for commands that could damage your system, and if it spots one, you get a warning naming the exact keyword and a choice about whether to continue.

That check is a blunt one and sandboxes nothing. Its job is to slow you down at the moments that deserve a second look. The thing keeping you safe is that you read the script before clicking run.

---

## Setup

You will need Python 3.11 or newer, and Windows.

```bash
git clone https://github.com/Sezsie/MOE.git
cd MOE
python -m venv .venv311
.venv311\Scripts\activate
pip install -r requirements.txt
```

MOE needs two API keys, saved as text files in a `MOE` folder in your home directory:

| File | What it powers |
|---|---|
| `anthropic-key.txt` | conversation and code generation |
| `elevenlabs-key.txt` | speech to text, and MOE's voice |

Then run it:

```bash
python -m MOE
```

Everything MOE saves for you (settings, learned commands, logs) lives in that same `~/MOE/` folder.


## Known rough edges

Worth knowing before you dig in:

- **The classifier is the weak link.** It has learned that a request looks like "open something", and it is very sure about that. Retraining it on a wider spread of phrasings is the real fix. Until then an LLM fallback catches what it misses.
- **Windows only, for now.** The hotkey handling calls Win32 APIs directly. Script execution has a Linux path, but the rest has not been tested there.
- **No offline mode.** Transcription, chat, and speech all need a network connection.

---

## Credits

Built by **Sabrina Finch**.

The intent classifier was researched and developed with **Brian Boggs** and **Colby McClure**. The dataset work and model comparison behind it were a joint effort.
