# Workflow Patterns

Module: **Module 2**

## Learning Materials

- Theory: [LEARN.md](tutorials/module-2-workflow-patterns/LEARN.md)
- Code Walkthrough: [BUILD.md](tutorials/module-2-workflow-patterns/BUILD.md)

## Setup

Run once at the beginning of class from repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For every new terminal session:

```bash
source .venv/bin/activate
```

Most workflow scripts accept `--provider groq` for Groq cloud API runs, while keeping local Ollama as the default provider.

## Module Topics

- `08_prompt_chaining.py`: Multi-step prompt chain with structured intermediate state
- `09_routing.py`: Classification-based routing to specialized handlers/LLMs
- `10_orchestrator_worker.py`: One orchestrator delegates to specialized workers and synthesizes outputs
- `11_evaluator_reflection.py`: Critique-revise loop with explicit quality control
- `12_tool_calling.py`: Tool-calling bridge from workflow patterns to agent loops
- `13_mcp_list_tools.py`: Connect to MCP and discover available Zapier tools
- `14_mcp_direct_tool_call.py`: Direct MCP tool invocation to create/retrieve a Notion page with runtime tool-mode compatibility
- `15_mcp_notion_writer.py`: Provider-aware MCP Notion writer for Ollama or Groq
- `workflow_utils.py`: Shared helper utilities (`ask_ollama_structured`, printing, JSON fallback parse)

## Run Order

From repo root:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/09_routing.py
python tutorials/module-2-workflow-patterns/10_orchestrator_worker.py
python tutorials/module-2-workflow-patterns/11_evaluator_reflection.py
python tutorials/module-2-workflow-patterns/12_tool_calling.py
python tutorials/module-2-workflow-patterns/13_mcp_list_tools.py
python tutorials/module-2-workflow-patterns/14_mcp_direct_tool_call.py
python tutorials/module-2-workflow-patterns/15_mcp_notion_writer.py
```

For tutorials `13-15`, set these `.env` variables:

```dotenv
ZAPIER_MCP_URL=...
ZAPIER_MCP_API_KEY=...
NOTION_PARENT_PAGE_ID=...
```

## Setting Up Your `.env` File (Complete Beginner Guide)

### What is a `.env` File?

A `.env` file (pronounced "dot-env") is a special text file that stores secret information like API keys. It tells the Python scripts where to find your Zapier MCP server and Notion page.

### Prerequisites Checklist

Before starting, make sure you have:
- [ ] A Zapier account with MCP (Model Context Protocol) set up
- [ ] A Notion account with a page where you want to create new pages
- [ ] Access to your Zapier MCP credentials (URL and API Key)
- [ ] The project folder open on your computer

---

## Step 1: Create the `.env` File

### Method 1: Using VS Code (Easiest for Beginners)

1. **Open VS Code**
   - Launch VS Code on your computer
   - Open the Ollama-Tutorials folder: File → Open Folder → Select `/Users/kushagrgupta/Ollama-Tutorials`

2. **Create a new file**
   - Look at the left side where you see all the files and folders
   - Right-click in that area → Select "New File"
   - A text box will appear asking for a name

3. **Name the file `.env`**
   - Type exactly: `.env` (that's a dot, then the word "env")
   - Press Enter to create the file
   - You'll see `.env` appear in the file list

4. **You now have an empty `.env` file open!**
   - Don't close it yet—you'll add content in the next steps

### Method 2: Using Terminal (For Those Comfortable with Command Line)

```bash
# Open a terminal and run these commands one at a time:

# First, go to your project folder
cd /Users/kushagrgupta/Ollama-Tutorials

# Create the .env file
touch .env

# Now open it in a text editor to edit it
nano .env
```

After running `nano .env`, you'll see a text editor. Add your content (see Step 2-4 below), then:
- Press `Ctrl + X`
- Type `y` and press Enter
- Press Enter again to save

---

## Step 2: Get Your Zapier MCP URL

### What is this?
This is the web address where your Zapier tools are located. It's like a link to your Zapier server.

### How to Find It

1. **Go to your Zapier account**
   - Open your browser and go to `zapier.com`
   - Sign in with your email and password
   - You should see your dashboard

2. **Find the MCP section**
   - Look for a menu or settings area (usually top-left or top-right)
   - Search for or find "MCP" or "Model Context Protocol"
   - You should see a configuration page

3. **Look for the MCP URL**
   - On the MCP configuration page, you'll see something labeled "URL", "Server URL", or "Endpoint"
   - It will look something like this:
     ```
     https://mcp.zapier.com/api/v1/connect?token=abc123def456...
     ```
   - This entire URL is what you need

4. **Copy the full URL**
   - Select all the text of the URL
   - Right-click → Copy (or press `Ctrl+C` on Windows / `Cmd+C` on Mac)

5. **Paste it into your `.env` file**
   - Go back to VS Code
   - In your `.env` file, type or paste this line:
     ```
     ZAPIER_MCP_URL=https://mcp.zapier.com/api/v1/connect?token=...
     ```
   - Replace `https://mcp.zapier.com/api/v1/connect?token=...` with the actual URL you copied

**Example:**
```
ZAPIER_MCP_URL=https://mcp.zapier.com/api/v1/connect?token=OTMxMTk1MjItZWFjZS00MTcyLTlhN2QtM2IyNDY1MzAwN2ExOjBjR29QQTNEd09uS2NWSmoxWGp1RFJuQlk3UVJjRGUrSGdFekJ2VDA2STg9
```

---

## Step 3: Get Your Zapier MCP API Key

### What is this?
This is a secret password/code that allows the scripts to access your Zapier tools. Keep it private!

### How to Find It

1. **In the same Zapier MCP section where you found the URL**
   - Look for "API Key", "Access Key", or "Secret Key"
   - It's usually a long string of random letters and numbers (like `abc123def456xyz...`)

2. **Copy the entire API Key**
   - Select all the text
   - Right-click → Copy (or press `Ctrl+C` / `Cmd+C`)

3. **Paste it into your `.env` file**
   - In VS Code, add a new line in your `.env` file:
     ```
     ZAPIER_MCP_API_KEY=your_api_key_here
     ```
   - Replace `your_api_key_here` with the actual key you copied

**Example:**
```
ZAPIER_MCP_API_KEY=OTMxMTk1MjItZWFjZS00MTcyLTlhN2QtM2IyNDY1MzAwN2ExOjBjR29QQTNEd09uS2NWSmoxWGp1RFJuQlk3UVJjRGUrSGdFekJ2VDA2STg9
```

**⚠️ IMPORTANT SECURITY NOTE:**
- Never share this key with anyone
- Don't post it on the internet or in GitHub
- If you accidentally share it, regenerate it in Zapier immediately
- The `.env` file is in your `.gitignore`, so it won't be uploaded to GitHub

---

## Step 4: Get Your Notion Parent Page ID

### What is this?
This is the ID of the Notion page where the Python scripts will automatically create new pages. Think of it as the "folder" where new pages go.

### Choose Your Method

### Method A: Using Just the Page ID (Recommended and Easier)

1. **Open Notion in your browser**
   - Go to `notion.so` and sign in
   - Navigate to the page where you want new pages to be created
   - This page should be empty or mostly empty (it will be the parent)

2. **Look at the browser address bar (URL)**
   - At the very top of your browser, you'll see something like:
     ```
     https://www.notion.so/My-Workspace/Page-Name-34184a990f85815a80f2e0cb63e51afd
     ```
   - The ID is the long string at the very end: `34184a990f85815a80f2e0cb63e51afd`
   - It's exactly **32 characters** (letters and numbers only, no spaces)

3. **Copy just the ID part**
   - Select the last 32 characters from the URL and copy them

4. **Add hyphens to the ID**

   ⚠️ **IMPORTANT:** When you copy the ID from the URL it will look like this (no hyphens):
   ```
   34184a990f85815a80f2e0cb63e51afd
   ```
   This will **NOT work** as-is. You must add hyphens in specific positions.

   The correct format is: `8 characters - 4 characters - 4 characters - 4 characters - 12 characters`

   ```
   34184a99-0f85-815a-80f2-e0cb63e51afd
   ↑ 8 chars ↑4ch ↑ 4ch ↑ 4ch ↑ 12 characters
   ```

   **How to manually add hyphens:**
   - Take your 32-character ID: `34184a990f85815a80f2e0cb63e51afd`
   - Count and split it like this:
     - Characters 1–8: `34184a99`
     - Add a `-`
     - Characters 9–12: `0f85`
     - Add a `-`
     - Characters 13–16: `815a`
     - Add a `-`
     - Characters 17–20: `80f2`
     - Add a `-`
     - Characters 21–32: `e0cb63e51afd`
   - Final result: `34184a99-0f85-815a-80f2-e0cb63e51afd`

5. **Add it to your `.env` file**
   - In VS Code, add a new line:
     ```
     NOTION_PARENT_PAGE_ID=34184a99-0f85-815a-80f2-e0cb63e51afd
     ```
   - Replace with your actual page ID (with hyphens added)

**Visual Example:**
```
URL in browser:
https://www.notion.so/My-Projects/Tutorial-Page-34184a990f85815a80f2e0cb63e51afd
                                                  ↑ Copy these 32 characters

Raw ID (won't work):  34184a990f85815a80f2e0cb63e51afd
With hyphens (works): 34184a99-0f85-815a-80f2-e0cb63e51afd
                              ↑    ↑    ↑    ↑
                          position 8,12,16,20
```

### Method B: Using the Full Notion URL (Also Works)

1. **In Notion, right-click on the page name** (at the top)
2. **Select "Copy link to page"**
   - You now have the full URL copied
3. **Paste it directly into `.env`:**
   ```
   NOTION_PARENT_PAGE_ID=https://www.notion.so/My-Workspace/Page-Title-34184a990f85815a80f2e0cb63e51afd
   ```
   - The script will automatically extract the ID from the full URL

---

## Step 5: Give Zapier Permission to Access Your Notion Page

### Why is this needed?
Without this step, Zapier won't be able to create new pages in your Notion workspace. This is a security feature.

### How to Grant Permission

1. **Open your Notion page**
   - The same page you used for the `NOTION_PARENT_PAGE_ID` above

2. **Click the "Share" button**
   - Look at the top-right corner of the Notion page
   - You'll see a "Share" button (blue button)
   - Click it

3. **Find Zapier in the list or add it**
   - A share dialog will pop up
   - Look for Zapier in the list of people/integrations
   - If you don't see it, click "Add a guest" or "Invite"
   - Search for "Zapier" and select it

4. **Grant Edit Permissions**
   - Make sure the permission level is set to **"Edit"** (not just "View")
   - Zapier needs Edit access to create new pages
   - If it only has "View" access, it won't work

5. **Click "Invite" or "Share"**
   - Confirm the sharing
   - You should see Zapier in the shared users list now

6. **Don't close this dialog until you see Zapier is shared!**

---

## Step 6: Check Your `.env` File

Your `.env` file should now have exactly 3 lines (no more, no less):

```
ZAPIER_MCP_URL=https://mcp.zapier.com/api/v1/connect?token=OTMxMTk1MjItZWFjZS00MTcyLTlhN2QtM2IyNDY1MzAwN2ExOjBjR29QQTNEd09uS2NWSmoxWGp1RFJuQlk3UVJjRGUrSGdFekJ2VDA2STg9
ZAPIER_MCP_API_KEY=OTMxMTk1MjItZWFjZS00MTcyLTlhN2QtM2IyNDY1MzAwN2ExOjBjR29QQTNEd09uS2NWSmoxWGp1RFJuQlk3UVJjRGUrSGdFekJ2VDA2STg9
NOTION_PARENT_PAGE_ID=34184a99-0f85-815a-80f2-e0cb63e51afd
```

### Final Checklist Before Running Scripts

- [ ] `.env` file is created in the project root folder (same level as README.md)
- [ ] All 3 variables are filled in (no `...` placeholders)
- [ ] No extra spaces before or after the `=` sign
- [ ] No quotation marks around the values
- [ ] Zapier has been shared with Edit access to your Notion page
- [ ] File is saved (in VS Code, you'll see a dot on the tab if unsaved)

### Save Your `.env` File

- In VS Code: Press `Ctrl+S` (Windows) or `Cmd+S` (Mac) to save
- You're done! Don't commit this file to GitHub (it's already in `.gitignore`)

---

## Step 7: Test Your Setup

### Run the test script to verify everything works

1. **Open a terminal** in your project folder
2. **Activate your virtual environment:**
   ```bash
   source .venv/bin/activate
   ```
3. **Run the test script:**
   ```bash
   python tutorials/module-2-workflow-patterns/13_mcp_list_tools.py
   ```

### What Should Happen?

If successful, you'll see:
```
================================================================================
13 - MCP List Tools
================================================================================
Connecting to Zapier MCP...

Available tools:
- discover_zapier_actions: ...
- enable_zapier_action: ...
... (more tools listed)
```

### Troubleshooting If Something Goes Wrong

**Error: "Missing ZAPIER_MCP_URL in .env"**
- Check that `.env` exists in the project root folder
- Make sure all 3 variables are in the file
- No typos in variable names (capital letters matter!)

**Error: "Permission denied" or "No access"**
- Go back to your Notion page
- Click Share again
- Verify Zapier has **Edit** permission (not just View)

**Error: "Invalid Notion page ID"**
- Copy the page ID again from the browser URL
- Make sure you have the right page (the parent page)
- Remove any extra spaces in the `.env` file

**No output or timeout error**
- Check your internet connection
- Verify the Zapier MCP URL is exactly correct
- Try copying the credentials again from Zapier

Notes for current Zapier MCP behavior:
- Scripts auto-handle both legacy per-app tools (`notion_create_page`, etc.) and generic execute tools (`execute_zapier_read_action` / `execute_zapier_write_action`).
- If `create_page` returns a follow-up confirmation prompt, the scripts auto-retry with explicit defaults so classroom runs remain non-interactive.

## Prompt Chaining Arguments (`08_prompt_chaining.py`)

Optional CLI arguments:

- `--file`: path to input meeting-notes text file
- `--output`: path for generated markdown report

Examples:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py --file tutorials/module-2-workflow-patterns/sample_meeting_minutes.txt --output tutorials/module-2-workflow-patterns/my_minutes_report.md
```

## Learning Focus

- Separate model reasoning steps into explicit workflow stages
- Add deterministic control via application code
- Run the same workflow patterns with local Ollama or Groq cloud API inference
- Route requests based on classification and inspect graph state
- Use critique-revision loops for measurable output improvement
- Bridge workflow patterns into app-executed tool loops
- Discover and adapt to MCP tool schemas dynamically
- Add robust external-tool preflight checks and permission-aware error handling
- Compose LLM structured output with MCP tools for end-to-end automation
