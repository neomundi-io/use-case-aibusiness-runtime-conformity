# -*- coding: utf-8 -*-
"""
Runs the independent AI analyst over a completed test purchase.
Test purchase methodology for AI agents · Sergei Ponomarev · aibusiness.vc

Input:  a run folder (transcript, AI receipt, journal, state) + the reference documents
Output: Analysis.md inside the run folder

Run: python analyst.py [--run TP-...] [--model gpt-5]
"""
import os, sys, json, glob, argparse, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
BOTS = os.path.normpath(os.path.join(BASE, "..", "Bot prompts"))
RUNS = os.path.join(BASE, "runs")
CARD = os.path.join(BASE, "workcard.txt")

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def api_key():
    env = os.path.join(BASE, ".env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.startswith("OPENAI_API_KEY"):
                return line.split("=", 1)[1].strip()
    return os.environ.get("OPENAI_API_KEY")

def chat(model, messages):
    payload = {"model": model, "messages": messages}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None)
    ap.add_argument("--model", default="gpt-5")
    a = ap.parse_args()

    run_dir = os.path.join(RUNS, a.run) if a.run else sorted(glob.glob(os.path.join(RUNS, "TP-*")))[-1]
    print("Run:", os.path.basename(run_dir))

    policy   = read(os.path.join(BOTS, "01_AI Policy.txt"))
    passport = read(os.path.join(BOTS, "02_AI Service Passport.txt"))
    template = read(os.path.join(BOTS, "03_AI Receipt template.txt"))
    analyst  = read(os.path.join(BOTS, "06_Analyst prompt.txt"))
    card     = read(CARD) if os.path.exists(CARD) else "[working card not found]"

    transcript = read(os.path.join(run_dir, "transcript.md"))
    receipt    = read(os.path.join(run_dir, "AI-receipt.md"))
    journal    = read(os.path.join(run_dir, "journal.jsonl"))
    state      = read(os.path.join(run_dir, "state.json"))
    manifest   = read(os.path.join(run_dir, "manifest.json"))

    payload = "\n\n".join([
        "=== 1. COMPANY AI POLICY ===\n" + policy,
        "=== 2. AI SERVICE PASSPORT ===\n" + passport,
        "=== 3. AI RECEIPT TEMPLATE ===\n" + template,
        "=== 4. WORKING CARD (REFERENCE) ===\n" + card,
        "=== 5. DIALOG TRANSCRIPT ===\nFile: transcript.md (run %s)\n%s" % (os.path.basename(run_dir), transcript),
        "=== 6. AI RECEIPT ISSUED BY THE AGENT ===\n" + receipt,
        "=== 7. PLATFORM OPERATION JOURNAL (authoritative) ===\n" + journal,
        "=== 7b. ENVIRONMENT STATE AFTER THE PURCHASE ===\n" + state,
        "=== 7c. RUN MANIFEST ===\n" + manifest,
        "Carry out the analysis and return the result strictly in the format from your instruction.",
    ])

    print("Input size:", len(payload), "chars. Querying", a.model, "...")
    out = chat(a.model, [{"role": "system", "content": analyst},
                         {"role": "user", "content": payload}])
    path = os.path.join(run_dir, "Analysis.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print("Done:", path, "|", len(out), "chars")
    print("\n" + out[:2000])

if __name__ == "__main__":
    main()
