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
│   └── supabase/                     2 tables as JSON + CSV, plus schema.json
├── dashboard/
│   ├── server.py                     the dashboard (Python, standard library only)
│   └── index.html                    the dashboard page
├── localStorageFormats.md            format used for each service and why
└── README.md
```

## The four services (test data)

| Service  | Test data                                                                 |
|----------|---------------------------------------------------------------------------|
| Gmail    | 10 fake customer emails (prices, financing, availability, trade-in)       |
| GitHub   | 10 issues in `josephhomeworksai-hash/dealership-test-tasks` (dealership to-dos) |
| Notion   | database "Dealership Test" with 10 lead follow-up pages                   |
| Supabase | project "Dealership-test", tables `motorcycles` and `clients_sales` (10 rows each) |

## Setup (to connect Claude Code)

You need [Claude Code](https://code.claude.com) installed. Open it in this folder. It reads `.mcp.json` and asks you to approve the project servers.

1. **Notion** – nothing to configure. In Claude Code run `/mcp`, choose `notion`, and sign in with the test account in the browser.
2. **Supabase** – nothing to configure. Run `/mcp`, choose `supabase`, sign in and allow access to the project `hworueeyzkemfldzqlxo`. The URL has `read_only=true`, so the export cannot change data.
3. **GitHub** – create a token for the test account (classic token with `repo` scope, or a fine-grained token with read access to issues). Put it in an environment variable **before** starting Claude Code. Do not write it in any file:
   ```
   export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here
   claude
   ```
4. **Gmail** – see the caveat below.
5. Run `/mcp` and check that all four servers say `connected`.

### Gmail caveat (please read)

Gmail is the hardest one. The official Gmail MCP server is Google's remote server at
`https://gmailmcp.googleapis.com/mcp/v1` (currently in Google's Developer Preview). It does not accept a simple token. You must:

1. In a Google Cloud project, enable the **Gmail API** and the **Gmail MCP API** (`gmailmcp.googleapis.com`), and set up the OAuth consent screen with the test Gmail account as a test user.
2. Create an OAuth client of type **Web application** with the redirect URI `http://localhost:8765/callback`.
3. Put the client ID in `.mcp.json` (replace `YOUR_GOOGLE_OAUTH_CLIENT_ID...`). A client ID is not secret. The **client secret** must not go in the file. Register it with Claude Code instead, so it is kept in Claude Code's own credential store:
   ```
   claude mcp add-json gmail --scope project --client-secret \
     '{"type":"http","url":"https://gmailmcp.googleapis.com/mcp/v1","oauth":{"clientId":"YOUR_CLIENT_ID","callbackPort":8765,"scopes":"https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose"}}'
   ```
   (It asks for the secret with hidden input.) Before committing, check that `.mcp.json` still has no real secrets.
4. Run `/mcp`, choose `gmail`, and sign in with the test account.

If the Google setup is not possible, a community Gmail MCP server can be used instead. In that case change the `gmail` entry in `.mcp.json`; the skill and the file formats stay the same.

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
