# Local storage formats

Everything exported from the four services lives in `dataExports/<service>/`.
All data is fake test data for a fictional motorcycle dealership ("Dealership-test").
Each format below was chosen so that (a) a person can open the file and read it,
(b) the metadata stays attached to the content, and (c) the dashboard can search it with no extra tools.

## Summary

| Service  | Folder                  | Format                              | One file per…        | Count exported |
|----------|-------------------------|-------------------------------------|----------------------|----------------|
| Gmail    | `dataExports/gmail/`    | JSON                                | email message        | 10             |
| GitHub   | `dataExports/github/`   | JSON                                | issue                | 10             |
| Notion   | `dataExports/notion/`   | Markdown + YAML front matter        | page                 | 10             |
| Supabase | `dataExports/supabase/` | JSON + CSV (plus `schema.json`)     | table                | 2 tables, 20 rows |

## Gmail → JSON (one file per message, named `<messageId>.json`)

Why JSON: an email is a record with a few short fields (sender, date, labels) and one long text field (the body).
JSON keeps those fields separate and typed (for example `to` and `labels` are lists), and it is easy to search by code.
I did not use `.eml` because it is raw MIME text that is harder to read and parse.

Metadata kept: `id`, `threadId`, `from`, `to`, `cc`, `subject`, `date` (ISO, UTC), `labels`, `snippet`, `body` (plain text), `viewUrl` (link back to Gmail), `source` (`"gmail"`).
The Gmail server used (`gmail-mcp-imap`, IMAP) does not return `threadId`, `cc` or all labels, so on a new export the skill fills them as described in `SKILL.md` (`threadId` = `id`, `cc` = `[]`, `labels` = `INBOX` plus `UNREAD`). The keys stay the same, so the dashboard is not affected.
Attachments: none in the test data; the skill would list them in an `attachments` field if present.

## GitHub → JSON (one file per issue, named `issue-NN.json`)

Why JSON: the GitHub API already returns issues as JSON, so this is the most natural and loss-free format.
I keep only the useful fields so files stay short and readable.

Metadata kept: `number`, `title`, `state`, `labels` (names only), `assignees`, `author`, `created_at`, `updated_at`, `url`, `repo`, `comments` (count), `body` (Markdown text), `source` (`"github"`).

## Notion → Markdown with YAML front matter (one file per page, named `<title-slug>-<id suffix>.md`)

Why Markdown: Notion pages are mostly text with lists, and Markdown is the closest plain-text version of that.
The block of metadata at the top (between `---` lines, "YAML front matter") is a common convention, so tools such as Obsidian, Jekyll and many editors understand it.
The page text stays readable below it.

Metadata kept in the front matter: `source`, `id` (page UUID), `url`, `title`, `database`, `data_source_id`, `created_time`, `last_edited_time`, and a `properties` block with the database columns (`Brand`, `Lead Source`, `Stage`, `Follow-up Date`).

## Supabase → JSON and CSV per table, plus `schema.json`

Why two formats for rows: the data is a table, so CSV opens directly in Excel or Google Sheets.
The JSON version of the same rows also carries table-level metadata (project, table name, row count, export date),
which a CSV cannot hold.
`schema.json` records every column name, type, nullability and default so the data can be understood or rebuilt later.

Files:
- `motorcycles.json` / `motorcycles.csv` – 10 rows: `id, brand, model, year, engine_cc, color, price_usd, stock, status, created_at`
- `clients_sales.json` / `clients_sales.csv` – 10 rows: `id, client_name, client_contact, lead_source, motorcycle_id, payment_type, down_payment_usd, installments, sale_price_usd, status, inquiry_at, sold_at, created_at`
- `schema.json` – column definitions for both tables

Table-level metadata kept in the JSON: `source`, `project_ref`, `table`, `row_count`, `exported_at`.

## How the dashboard uses these files

`dashboard/server.py` reads all of the folders above on every search. It treats each Gmail message, GitHub issue and Notion page as one result, and each Supabase row as one result. Every result shows a colored badge with its service, a snippet with the match highlighted, and the file it came from.
