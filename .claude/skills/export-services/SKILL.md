---
name: export-services
description: Download (export) test items from Gmail, GitHub, Notion and Supabase through their MCP servers into the dataExports/ folder with metadata. Use when the user asks to export, download, back up or refresh the data from the four services for the Dealership-test project.
---

# export-services

Repeat the full download of the Dealership-test data from the 4 MCP servers
(`gmail`, `github`, `notion`, `supabase`, all defined in `.mcp.json`; Gmail uses an app password, see the README) into `dataExports/<service>/`.
The formats are explained in `localStorageFormats.md`. Follow them exactly so the dashboard keeps working.

## Before you start

1. Run `/mcp` and check that all 4 servers show `connected`. If one is not connected, stop and tell the user which one (and see the README setup section).
2. Use only the test accounts. Never write secrets or tokens to any file.
3. Create the folders if missing: `dataExports/gmail`, `dataExports/github`, `dataExports/notion`, `dataExports/supabase`.
4. Export **at least 5 items per service** (normally all of them, 10+). Overwrite files with the same name so the skill can be re-run safely.
5. Only export the fake customer data (see "What to export"). Do not export unrelated mail such as security alerts or newsletters.

## 1. Gmail → `dataExports/gmail/<messageId>.json`

The `gmail` server is the community server `gmail-mcp-imap` (IMAP + app password, tools below).
It lists INBOX mail, so the 10 fake emails (self-sent, they also sit in the INBOX) are found there.

1. Call the MCP tool `search_emails` with `query: "fake customer inquiry for class assignment"` and `limit: 50`.
   The query uses Gmail search syntax (X-GM-RAW) over the whole message text. The 10 test emails contain this phrase at the end of the body, so only they match. If you get 0 results, retry with `"fake customer inquiry"` and `"in:anywhere"` added; never export mail that does not contain the phrase (for example security alerts or the "Resumen diario" emails).
   The result is a list of headers with a numeric `uid` (no body).
2. For each `uid`, call `get_email_content` (`mailbox` defaults to `INBOX`). It returns `subject, from, to, date, snippet, body, isRead`.
   Double check the body contains the phrase before saving.
   (`get_emails_by_label` and `list_labels` exist too, but are not needed. Do not use the send, reply, delete, label or star tools.)
3. Write one JSON file per message with exactly these keys:
   `id, threadId, from, to (list), cc (list), subject, date (ISO UTC), labels (list), snippet, body (plain text), viewUrl, source`.
   This server does not return every field, so fill them like this:
   - `id`: if a file in `dataExports/gmail/` already has the same `subject` and `date`, reuse that file name, `id`, `threadId` and `viewUrl` and just overwrite it (this keeps the dashboard from showing duplicates). Otherwise `id` = the `uid` as a string, and `threadId` = the same value.
   - `from`: the sender address. `to`: list of addresses (split the `to` text on commas). `cc`: `[]` (not provided by the server).
   - `date`: the `date` field (already ISO, UTC).
   - `labels`: `["INBOX"]` plus `"UNREAD"` when `isRead` is false.
   - `snippet`: the `snippet` field. `body`: the plain text `body`.
   - `viewUrl`: `https://mail.google.com/mail/?authuser=josephhomeworksai@gmail.com#search/` followed by the URL-encoded subject.
   - `source`: always `"gmail"`.

## 2. GitHub → `dataExports/github/issue-NN.json`

1. Repository: `josephhomeworksai-hash/dealership-test-tasks`.
2. Use the GitHub MCP `list_issues` tool with `state: ALL` (paginate until done), and `issue_read` if the list lacks the body.
3. Write one JSON file per issue named `issue-01.json`, `issue-02.json`… (zero-padded issue number) with keys:
   `number, title, state, labels (names only), assignees (logins), author, created_at, updated_at, url (html url), repo, comments (count), body, source` (`source` is `"github"`).

## 3. Notion → `dataExports/notion/<title-slug>-<last 6 chars of id>.md`

1. Database: "Dealership Test", data source id `8a66e726-b92f-466b-854a-e7d0c4b2175c`.
2. Use the Notion MCP `notion-fetch` on the data source to see its schema, then `notion-query-data-sources` (rows mode, limit 100) to list all pages.
3. For each page use `notion-fetch` to get the page text and `last_edited` time. Use a SQL query (`SELECT url, createdTime ...`) to get `created_time`.
4. Write a Markdown file that starts with this front matter, then a `# <title>` heading and the page text:

```
---
source: notion
id: <page uuid>
url: "<page url>"
title: "<title>"
database: "Dealership Test"
data_source_id: "8a66e726-b92f-466b-854a-e7d0c4b2175c"
created_time: "<ISO>"
last_edited_time: "<ISO>"
properties:
  Brand: "<value>"
  Lead Source: "<value>"
  Stage: "<value>"
  Follow-up Date: "<YYYY-MM-DD>"
---
```

## 4. Supabase → `dataExports/supabase/`

Project ref: `hworueeyzkemfldzqlxo`. Use the Supabase MCP `execute_sql` tool (read-only queries only).

The export is **one table, `clients_sales`, with 10 rows and 3 columns**: `id, client_name, motorcycle`.
The motorcycle name comes from the `motorcycles` table, joined in the query. Do not export `motorcycles` as its own file.

1. Rows: `select coalesce(json_agg(t order by id),'[]'::json) from (select cs.id, cs.client_name, m.brand || ' ' || m.model as motorcycle from public.clients_sales cs join public.motorcycles m on m.id = cs.motorcycle_id) t`.
2. Write `clients_sales.json` as
   `{"source":"supabase","project_ref":"hworueeyzkemfldzqlxo","table":"public.clients_sales","row_count":N,"exported_at":"<today>","rows":[...]}`.
3. Also write `clients_sales.csv` (header `id,client_name,motorcycle` + one line per row, proper CSV quoting).
4. Write `schema.json` as `{"project_ref":"...","schema":"public","tables":{"clients_sales":[...]}}` with the three columns:
   `id` (bigint), `client_name` (text), `motorcycle` (text, brand + model). All `nullable: "NO"`, `default: null`.

## After exporting

1. Count the files per service and check each service has at least 5 items.
2. Run `python3 dashboard/server.py --search ""` and check it prints `supabase 10`, then `--search "Forza"` and check the output shows results for all four services.
3. Tell the user the counts per service and remind them to run `python3 dashboard/server.py` and open http://localhost:8000.
4. Run `git status` and make sure no token or secret appears in any exported file. Do not commit unless the user asks.
