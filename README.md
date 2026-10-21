# Third-Party Dashboard (Dealership-test)

Homework 3 for AI Assisted Products. This project connects Claude Code to four services
through their MCP servers, downloads test data from each one into local files, and shows
a small local dashboard that searches all four at the same time.

**Test data disclaimer:** everything here is fake. "Dealership-test" is an invented motorcycle
dealership in Caracas (brands Forza, Vento, HJM). All people, emails and messages are made up.
The accounts used are test accounts only. No passwords, tokens or API keys are stored in this repo.

## What is in this repo

```
.
├── .mcp.json                         MCP server config for Claude Code (no secrets)
├── .claude/skills/export-services/
│   └── SKILL.md                      Claude Code skill that repeats the download
├── dataExports/
│   ├── gmail/                        10 emails, one JSON file each
│   ├── github/                       10 issues, one JSON file each
│   ├── notion/                       10 pages, one Markdown file each (with front matter)
│   └── supabase/                     1 table (10 clients + their motorcycle) as JSON + CSV, plus schema.json
├── dashboard/
│   ├── server.py                     the dashboard (Python, standard library only)
│   └── index.html                    the dashboard page
├── presentation/
│   ├── HW3_Third-Party-Data-Dashboard.pptx   the class presentation (slides)
│   └── HW3_Demo_Video.mp4                    demo video
├── localStorageFormats.md            format used for each service and why
└── README.md
```

## Presentation

The slide deck is in [`presentation/HW3_Third-Party-Data-Dashboard.pptx`](presentation/HW3_Third-Party-Data-Dashboard.pptx).

The demo video is in [`presentation/HW3_Demo_Video.mp4`](presentation/HW3_Demo_Video.mp4).

## The four services (test data)

| Service  | Test data                                                                 |
|----------|---------------------------------------------------------------------------|
| Gmail    | 10 fake customer emails (prices, financing, availability, trade-in)       |
| GitHub   | 10 issues in `josephhomeworksai-hash/dealership-test-tasks` (dealership to-dos) |
| Notion   | database "Dealership Test" with 10 lead follow-up pages                   |
| Supabase | project "Dealership-test", table `clients_sales` exported as 10 rows: id, client name, motorcycle |

## Setup (to connect Claude Code)

You need [Claude Code](https://code.claude.com) and Node.js (for `npx`) installed. Open Claude Code in this folder. It reads `.mcp.json` and asks you to approve the project servers.

**Accounts:** Claude Code runs with your normal Claude account. The four services below do **not** use that account. Each one logs in separately with the **test** accounts (Notion, Supabase and Gmail through OAuth, GitHub with a token), so the Claude account used for Claude Code is independent from the test accounts.

1. **Notion** – nothing to configure. In Claude Code run `/mcp`, choose `notion`, and sign in with the Notion test account in the browser (OAuth).
2. **Supabase** – nothing to configure. Run `/mcp`, choose `supabase`, sign in (OAuth) and allow access to the project `hworueeyzkemfldzqlxo`. The URL has `read_only=true`, so the export cannot change data.
3. **GitHub** – create a token for the test account `josephhomeworksai-hash` (classic token with `repo` scope, or a fine-grained token with read access to issues) at https://github.com/settings/tokens/new. Export it **before** starting Claude Code. Do not write it in any file.
4. **Gmail** – uses Anthropic's own **official** Gmail connector (`claude.ai Gmail`), not a community package. It is connected at the account level, not through `.mcp.json`:
   1. In your browser, go to claude.ai → **Settings → Connectors**.
   2. If Gmail is connected to a personal account, **Disconnect** it first.
   3. **Connect** Gmail again, and sign in with the **test** account `josephhomeworksai@gmail.com` (not a personal account) when Google's OAuth screen appears.
   4. Once connected, it is available as an MCP connector inside Claude Code / Claude in this session — no token, password or env var needed.
5. Run `/mcp` and check that all four servers say `connected` (Gmail appears as `claude.ai Gmail`).

`.mcp.json` only contains the placeholder `${GITHUB_PERSONAL_ACCESS_TOKEN}`, which Claude Code fills in from your environment, so no secret is stored in the repo. Gmail needs no secret at all — the OAuth connection lives in your claude.ai account settings, never in a file. When the homework is finished, delete the GitHub token and disconnect/revert the Gmail connector to your personal account.

### Gmail notes

- Gmail is read through Anthropic's official `claude.ai Gmail` connector, using its `search_threads` and `get_message` tools (read-only). The export skill does not use any send/label/delete tool.
- `search_threads` with the query `"fake customer inquiry for class assignment"` finds exactly the 10 fake emails and ignores everything else in the inbox.
- *Not used:* the community package `gmail-mcp-imap` (IMAP + app password) and Google's own remote server `https://gmailmcp.googleapis.com/mcp/v1` (requires a Google Cloud project enrolled in Google's Developer Preview Program). Anthropic's connector needs neither.

## Run the download (the skill)

In Claude Code, from this folder, say for example:

```
Use the export-services skill to download everything from Gmail, GitHub, Notion and Supabase.
```

(or type `/export-services`). The skill, in `.claude/skills/export-services/SKILL.md`,
tells Claude Code step by step which MCP tools to call and which file to write for each service.
It writes into `dataExports/` and overwrites files with the same name, so you can run it again at any time.
The result of the last run is already committed in `dataExports/`.

## Run the dashboard

You only need Python 3 (no packages to install):

```
python3 dashboard/server.py
```

Open http://localhost:8000 and type a word such as `financing`, `Forza`, `Vento` or `TikTok`.
The search runs over all four services at once. Each result has a colored badge showing where it comes
from (Gmail, GitHub, Notion or Supabase), a snippet with the match highlighted, and the file that holds it.
Click the file name to see its content. Use the checkboxes to hide a service.
Use another port with `PORT=8080 python3 dashboard/server.py`.

Quick check without a browser: `python3 dashboard/server.py --search "financing"` prints how many results each service has.

## How the data is stored

See [localStorageFormats.md](localStorageFormats.md) for the format of each service and the reason for it.
