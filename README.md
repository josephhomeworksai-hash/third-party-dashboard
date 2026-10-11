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

You need [Claude Code](https://code.claude.com) and Node.js (for `npx`) installed. Open Claude Code in this folder. It reads `.mcp.json` and asks you to approve the project servers.

**Accounts:** Claude Code runs with your normal Claude account. The four services below do **not** use that account. Each one logs in separately with the **test** accounts (Notion and Supabase through OAuth in the browser, GitHub with a token, Gmail with an app password), so the Claude account used for Claude Code is independent from the test accounts.

1. **Notion** – nothing to configure. In Claude Code run `/mcp`, choose `notion`, and sign in with the Notion test account in the browser (OAuth).
2. **Supabase** – nothing to configure. Run `/mcp`, choose `supabase`, sign in (OAuth) and allow access to the project `hworueeyzkemfldzqlxo`. The URL has `read_only=true`, so the export cannot change data.
3. **GitHub** – create a token for the test account `josephhomeworksai-hash` (classic token with `repo` scope, or a fine-grained token with read access to issues) at https://github.com/settings/tokens/new. Export it **before** starting Claude Code. Do not write it in any file.
4. **Gmail** – uses the community server [`gmail-mcp-imap`](https://github.com/suhail-ak-2/gmail-mcp-imap) (IMAP with an app password, no Google Cloud project, nothing to install; `npx` downloads it). On the test account `josephhomeworksai@gmail.com`:
   1. Turn on 2-Step Verification at https://myaccount.google.com/security.
   2. Create an app password at https://myaccount.google.com/apppasswords (name it e.g. `hw3`). Copy the 16 characters.
   3. Export the variables **before** starting Claude Code (never write them in a file). Together with the GitHub token this is:
      ```
      export GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
      export GMAIL_EMAIL=josephhomeworksai@gmail.com
      export GMAIL_APP_PASSWORD="yourapppassword16chars"
      claude
      ```
5. Run `/mcp` and check that all four servers say `connected`.

`.mcp.json` only contains the placeholders `${GITHUB_PERSONAL_ACCESS_TOKEN}`, `${GMAIL_EMAIL}` and `${GMAIL_APP_PASSWORD}`, which Claude Code fills in from your environment, so no secret is stored in the repo. When the homework is finished, delete the GitHub token and revoke the app password.

### Gmail notes

- The Gmail server's tools are `search_emails`, `get_email_content`, `get_emails_by_label`, `list_labels` (read) plus action tools such as `send_email`. The export skill only uses the read tools.
- `search_emails` uses Gmail search syntax over the INBOX, so the skill finds the 10 fake emails with the phrase `"fake customer inquiry for class assignment"` and ignores everything else in the inbox.
- If the server does not connect, check that the app password has no typos (paste it without spaces to be safe) and that IMAP is enabled in Gmail settings (Settings > See all settings > Forwarding and POP/IMAP).
- *Alternative (not used):* Google's official remote server `https://gmailmcp.googleapis.com/mcp/v1`. It needs a Google Cloud project with the Gmail API and Gmail MCP API enabled and an OAuth client, which is why the app password option is used here.

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
