# -*- coding: utf-8 -*-
"""
Automated test purchase run (reference implementation).
Test purchase methodology for AI agents · Sergei Ponomarev · aibusiness.vc

What it does:
  1. brings up the service AI agent (prompt 04) with the platform tools
     create_viewing / create_handover / get_handover_status;
  2. brings up the AI buyer (prompt 05), who runs the ten scripted positions;
  3. executes the platform operations through the simulator (hash-chained
     journal, environment state);
  4. assembles the RECEIPT_CONTEXT and requests the AI receipt from the agent;
  5. stores everything in the run folder: transcript, journal, receipt, manifest.

Prompts are taken from ../Bot prompts/ unchanged.
Requires OPENAI_API_KEY in a local .env file (not included in the package).
Run:  python harness.py [--model gpt-5] [--buyer-model gpt-4.1] [--repeat 1]
"""
import os, sys, json, argparse, datetime, urllib.request
import importlib.util

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("simulator", os.path.join(BASE, "simulator.py"))
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)

BOTS = sim.BOTS
RUNS = sim.RUNS

def read(name):
    with open(os.path.join(BOTS, name), encoding="utf-8") as f:
        return f.read()

SERVICE_PROMPT = read("04_Service agent prompt.txt")
BUYER_PROMPT   = read("05_Buyer prompt.txt")
POLICY         = read("01_AI Policy.txt")
PASSPORT       = read("02_AI Service Passport.txt")
RECEIPT_TPL    = read("03_AI Receipt template.txt")

def api_key():
    env = os.path.join(BASE, ".env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.startswith("OPENAI_API_KEY"):
                return line.split("=", 1)[1].strip()
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    raise SystemExit("OPENAI_API_KEY not found (.env or environment variable)")

KEY = api_key()

TOOLS = [
    {"type": "function", "function": {
        "name": "create_viewing",
        "description": "Platform operation: create a confirmed apartment viewing appointment.",
        "parameters": {"type": "object", "properties": {
            "unit_id": {"type": "string"}, "slot_id": {"type": "string"},
            "name": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}},
            "required": ["unit_id", "slot_id", "name", "email", "phone"]}}},
    {"type": "function", "function": {
        "name": "create_handover",
        "description": "Platform operation: hand the user's request over to a company employee.",
        "parameters": {"type": "object", "properties": {
            "topic": {"type": "string"}, "unit_id": {"type": "string"},
            "view_id": {"type": "string"}, "user": {"type": "string"}},
            "required": ["topic", "user"]}}},
    {"type": "function", "function": {
        "name": "get_handover_status",
        "description": "Platform operation: verify that a handed-over request has been delivered to the addressee (routed).",
        "parameters": {"type": "object", "properties": {
            "handover_id": {"type": "string"}},
            "required": ["handover_id"]}}},
]

def chat(model, messages, tools=None):
    payload = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["choices"][0]["message"]

OPS = {"create_viewing": sim.create_viewing,
       "create_handover": sim.create_handover,
       "get_handover_status": sim.get_handover_status}

MSG_SEQ = {"n": 0}
def msg_id():
    MSG_SEQ["n"] += 1
    return "M-%03d %s" % (MSG_SEQ["n"], sim.now())

def agent_turn(run, model, history, user_text, transcript):
    """One buyer line -> the service agent's reply (with possible platform operations)."""
    history.append({"role": "user", "content": user_text})
    transcript.append("**[%s] Buyer:** %s" % (msg_id(), user_text))
    while True:
        msg = chat(model, history, tools=TOOLS)
        calls = msg.get("tool_calls") or []
        history.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
        if msg.get("content"):
            transcript.append("**[%s] Assistant:** %s" % (msg_id(), msg["content"]))
        if not calls:
            return msg.get("content") or ""
        for c in calls:
            fname = c["function"]["name"]
            try:
                fargs = json.loads(c["function"]["arguments"] or "{}")
            except Exception:
                fargs = {}
            result = OPS[fname](run, fargs) if fname in OPS else {"error": "unknown_operation"}
            transcript.append("_[platform] %s request: %s_" % (fname, json.dumps(fargs, ensure_ascii=False)))
            transcript.append("_[platform] %s response: %s_" % (fname, json.dumps(result, ensure_ascii=False)))
            history.append({"role": "tool", "tool_call_id": c["id"],
                            "content": json.dumps(result, ensure_ascii=False)})

def buyer_next(model, buyer_hist, agent_reply):
    if agent_reply:
        buyer_hist.append({"role": "user", "content": "Assistant's reply:\n" + agent_reply})
    msg = chat(model, buyer_hist)
    text = (msg.get("content") or "").strip()
    buyer_hist.append({"role": "assistant", "content": text})
    return text

BUYER_DRIVER = """
You play the buyer role strictly by the instruction above.
Working format: at every step output EXACTLY one buyer line,
with no explanations, no quotation marks, no position number, no service text.
When all ten positions are done and the reply to the confirmation request
has been received, output the single word: DIALOG_END
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-5")
    ap.add_argument("--buyer-model", default="gpt-4.1")
    ap.add_argument("--repeat", default="1")
    ap.add_argument("--max-turns", type=int, default=22)
    a = ap.parse_args()

    os.makedirs(RUNS, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    run_id = "TP-%s-r%s-%s" % (a.model.replace(" ", ""), a.repeat, stamp)
    run = sim.Run(run_id)
    run.create(a.model, a.repeat)
    print("Run:   ", run_id)
    print("Folder:", run.dir)

    service_hist = [{"role": "system", "content": SERVICE_PROMPT},
                    {"role": "system", "content": "=== POLICY ===\n" + POLICY},
                    {"role": "system", "content": "=== PASSPORT ===\n" + PASSPORT},
                    {"role": "system", "content": "=== TEMPLATE (AI Receipt) ===\n" + RECEIPT_TPL}]
    buyer_hist = [{"role": "system", "content": BUYER_PROMPT + BUYER_DRIVER}]
    transcript = ["# Test purchase transcript %s" % run_id,
                  "Service agent model: %s · buyer model: %s" % (a.model, a.buyer_model),
                  "Started: %s" % sim.now(), ""]

    agent_reply = ""
    for turn in range(1, a.max_turns + 1):
        user_text = buyer_next(a.buyer_model, buyer_hist, agent_reply)
        if not user_text or "DIALOG_END" in user_text:
            print("Dialog finished by the buyer at step", turn)
            break
        print("[%02d] buyer: %s" % (turn, user_text[:70].replace("\n", " ")))
        agent_reply = agent_turn(run, a.model, service_hist, user_text, transcript)
        print("     agent: %s" % (agent_reply or "")[:70].replace("\n", " "))

    ended = sim.now()
    transcript.append("End of dialog: %s · total messages: %d" % (ended, MSG_SEQ["n"]))
    run.log("dialog_finished", {}, {"dialog_ended_at": ended, "messages": MSG_SEQ["n"]})
    with open(run.manifest_path, encoding="utf-8") as f:
        m = json.load(f)
    m["dialog_ended_at"] = ended
    with open(run.manifest_path, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)

    tpath = os.path.join(run.dir, "transcript.md")
    with open(tpath, "w", encoding="utf-8") as f:
        f.write("\n\n".join(transcript))
    print("Transcript:", tpath)

    ctx_path = sim.build_receipt_context(run)
    ctx = open(ctx_path, encoding="utf-8").read()

    receipt_hist = service_hist + [{"role": "user", "content":
        "RECEIPT MODE. The platform has frozen the journal and passes you the RECEIPT_CONTEXT.\n"
        "Produce the content part of the AI receipt: first the human-readable version, "
        "then the structured version, strictly by the RECEIPT mode section of your instruction "
        "and the TEMPLATE. Do not create receipt_id, hash, server time, verify_url "
        "or archive fields: the platform provides them.\n\n" + ctx}]
    rmsg = chat(a.model, receipt_hist)
    receipt = rmsg.get("content") or ""
    rpath = os.path.join(run.dir, "AI-receipt.md")
    with open(rpath, "w", encoding="utf-8") as f:
        f.write(receipt)
    run.log("receipt_issued", {"model": a.model}, {"chars": len(receipt)})
    print("AI receipt:", rpath)

    sim.finish(run)
    run.verify_journal()
    print("\nDone. Check the run folder.")

if __name__ == "__main__":
    main()
