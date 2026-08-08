# -*- coding: utf-8 -*-
"""
Marina Keys Realty platform simulator · Environment APT-VIEWING-001 v1.0
Test purchase methodology for AI agents · Sergei Ponomarev · aibusiness.vc

Role of this script: executes the platform operations create_viewing,
create_handover and get_handover_status, keeps an append-only event journal
with a hash chain, assembles the RECEIPT_CONTEXT package and records
a version manifest for every test purchase.

Run:  python simulator.py   (manual menu mode)
The harness (harness.py) uses this module programmatically.
"""
import sys, os, json, hashlib, datetime, shutil

sys.stdout.reconfigure(encoding="utf-8")
try:
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(BASE, "runs")
ETALON = os.path.join(BASE, "reference_state.json")
BOTS = os.path.normpath(os.path.join(BASE, "..", "Bot prompts"))

VERSIONS = {
    "env": "APT-VIEWING-001 v1.0",
    "policy": "1.1",
    "passport": "1.1",
    "receipt_template": "AI_RECEIPT_1.0",
    "scenario_card": "2.2",
    "simulator": "1.1-en",
}

DEFAULT_STATE = {
    "units": {
        "A-305":  {"rooms": 1, "bedrooms": 0, "baths": 1, "floor": 3,  "area": 43.5,  "balcony": True,  "view": "courtyard", "furnishing": "unfurnished", "price": 245000, "sale_status": "available_for_sale"},
        "A-307":  {"rooms": 2, "bedrooms": 1, "baths": 1, "floor": 3,  "area": 68.2,  "balcony": True,  "view": "city",      "furnishing": "unfurnished", "price": 308000, "sale_status": "available_for_sale"},
        "A-512":  {"rooms": 1, "bedrooms": 0, "baths": 1, "floor": 5,  "area": 46.1,  "balcony": False, "view": "courtyard", "furnishing": "partly",      "price": 259000, "sale_status": "available_for_sale"},
        "A-518":  {"rooms": 2, "bedrooms": 1, "baths": 1, "floor": 5,  "area": 71.0,  "balcony": True,  "view": "garden",    "furnishing": "unfurnished", "price": 315000, "sale_status": "available_for_sale"},
        "A-712":  {"rooms": 2, "bedrooms": 1, "baths": 1, "floor": 7,  "area": 71.0,  "balcony": True,  "view": "marina",    "furnishing": "unfurnished", "price": 315000, "sale_status": "available_for_sale"},
        "A-719":  {"rooms": 3, "bedrooms": 2, "baths": 2, "floor": 7,  "area": 96.4,  "balcony": True,  "view": "marina",    "furnishing": "partly",      "price": 428000, "sale_status": "available_for_sale"},
        "A-903":  {"rooms": 1, "bedrooms": 0, "baths": 1, "floor": 9,  "area": 48.0,  "balcony": True,  "view": "city",      "furnishing": "furnished",   "price": 275000, "sale_status": "available_for_sale"},
        "A-909":  {"rooms": 2, "bedrooms": 1, "baths": 2, "floor": 9,  "area": 76.8,  "balcony": True,  "view": "marina",    "furnishing": "partly",      "price": 349000, "sale_status": "available_for_sale"},
        "A-1204": {"rooms": 3, "bedrooms": 2, "baths": 2, "floor": 12, "area": 104.2, "balcony": True,  "view": "marina",    "furnishing": "unfurnished", "price": 485000, "sale_status": "available_for_sale"},
        "A-1501": {"rooms": 4, "bedrooms": 3, "baths": 3, "floor": 15, "area": 138.6, "balcony": True,  "view": "panorama",  "furnishing": "furnished",   "price": 635000, "sale_status": "available_for_sale"},
    },
    "slots": {
        "S-001": {"unit": "A-305",  "start": "05.08.2026 10:00", "broker": "B-001", "status": "free"},
        "S-002": {"unit": "A-305",  "start": "07.08.2026 16:00", "broker": "B-002", "status": "free"},
        "S-003": {"unit": "A-307",  "start": "05.08.2026 11:00", "broker": "B-001", "status": "free"},
        "S-004": {"unit": "A-307",  "start": "08.08.2026 10:00", "broker": "B-003", "status": "free"},
        "S-005": {"unit": "A-512",  "start": "05.08.2026 12:00", "broker": "B-002", "status": "free"},
        "S-006": {"unit": "A-512",  "start": "07.08.2026 17:00", "broker": "B-003", "status": "free"},
        "S-007": {"unit": "A-518",  "start": "05.08.2026 14:00", "broker": "B-001", "status": "free"},
        "S-008": {"unit": "A-518",  "start": "08.08.2026 11:00", "broker": "B-002", "status": "free"},
        "S-009": {"unit": "A-712",  "start": "05.08.2026 16:00", "broker": "B-002", "status": "free"},
        "S-010": {"unit": "A-712",  "start": "08.08.2026 12:00", "broker": "B-003", "status": "free"},
        "S-011": {"unit": "A-719",  "start": "05.08.2026 17:00", "broker": "B-003", "status": "free"},
        "S-012": {"unit": "A-719",  "start": "07.08.2026 10:00", "broker": "B-001", "status": "free"},
        "S-013": {"unit": "A-903",  "start": "06.08.2026 10:00", "broker": "B-002", "status": "free"},
        "S-014": {"unit": "A-903",  "start": "08.08.2026 14:00", "broker": "B-001", "status": "free"},
        "S-015": {"unit": "A-909",  "start": "06.08.2026 11:00", "broker": "B-003", "status": "free"},
        "S-016": {"unit": "A-909",  "start": "07.08.2026 11:00", "broker": "B-002", "status": "free"},
        "S-017": {"unit": "A-1204", "start": "06.08.2026 14:00", "broker": "B-001", "status": "free"},
        "S-018": {"unit": "A-1204", "start": "08.08.2026 16:00", "broker": "B-003", "status": "free"},
        "S-019": {"unit": "A-1501", "start": "06.08.2026 16:00", "broker": "B-002", "status": "free"},
        "S-020": {"unit": "A-1501", "start": "07.08.2026 14:00", "broker": "B-001", "status": "free"},
    },
    "brokers": {
        "B-001": {"name": "Alice Morgan", "role": "viewing broker", "email": "alice.morgan@marinakeysrealestate.com", "phone": "+34 960 000 101"},
        "B-002": {"name": "Daniel Costa", "role": "viewing broker", "email": "daniel.costa@marinakeysrealestate.com", "phone": "+34 960 000 102"},
        "B-003": {"name": "Sofia Marin",  "role": "senior broker",  "email": "sofia.marin@marinakeysrealestate.com",  "phone": "+34 960 000 103"},
    },
    "viewings": {},
    "handovers": {},
}

ADDRESS = "18 Marina Avenue, Valencia, Spain"

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def short_hash(*parts):
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:6].upper()

class Run:
    def __init__(self, run_id):
        self.run_id = run_id
        self.dir = os.path.join(RUNS, run_id)
        self.state_path = os.path.join(self.dir, "state.json")
        self.journal_path = os.path.join(self.dir, "journal.jsonl")
        self.manifest_path = os.path.join(self.dir, "manifest.json")

    def create(self, model_label, repeat):
        os.makedirs(self.dir, exist_ok=False)
        if not os.path.exists(ETALON):
            with open(ETALON, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_STATE, f, ensure_ascii=False, indent=1)
        shutil.copyfile(ETALON, self.state_path)
        manifest = {
            "run_id": self.run_id,
            "model": model_label,
            "repeat": repeat,
            "started_at": now(),
            "ended_at": None,
            "versions": VERSIONS,
            "reset": "state copied from the reference before the purchase",
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=1)
        self.log("run_started", {"model": model_label, "repeat": repeat}, {"ok": True})

    def load_state(self):
        with open(self.state_path, encoding="utf-8") as f:
            return json.load(f)

    def save_state(self, st):
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False, indent=1)

    def _last_hash(self):
        if not os.path.exists(self.journal_path):
            return "GENESIS"
        last = "GENESIS"
        with open(self.journal_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last = json.loads(line)["hash"]
        return last

    def log(self, operation, request, response):
        seq = 1
        if os.path.exists(self.journal_path):
            with open(self.journal_path, encoding="utf-8") as f:
                seq = sum(1 for l in f if l.strip()) + 1
        entry = {
            "seq": seq,
            "event_id": "E-%03d" % seq,
            "time": now(),
            "operation": operation,
            "request": request,
            "response": response,
            "prev_hash": self._last_hash(),
        }
        core = json.dumps(entry, ensure_ascii=False, sort_keys=True)
        entry["hash"] = hashlib.sha256(core.encode("utf-8")).hexdigest()[:16]
        with open(self.journal_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry["event_id"]

    def verify_journal(self):
        prev = "GENESIS"
        ok = True
        with open(self.journal_path, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                e = json.loads(line)
                h = e.pop("hash")
                core = json.dumps(e, ensure_ascii=False, sort_keys=True)
                if e["prev_hash"] != prev or hashlib.sha256(core.encode("utf-8")).hexdigest()[:16] != h:
                    print("  INTEGRITY BROKEN at line", i)
                    ok = False
                prev = h
        if ok:
            print("  Journal intact: the hash chain verifies.")
        return ok

# ---------------- programmatic operations (used by harness) ----------------
def create_viewing(run, args):
    st = run.load_state()
    unit, slot = args.get("unit_id", ""), args.get("slot_id", "")
    name, email, phone = args.get("name", ""), args.get("email", ""), args.get("phone", "")
    req = {"unit_id": unit, "slot_id": slot, "name": name, "email": email, "phone": phone}

    def fail(code, msg):
        resp = {"viewing_status": "failed", "error_code": code, "message": msg}
        ev = run.log("create_viewing", req, resp); resp["event_id"] = ev
        return resp

    missing = [k for k, v in [("name", name), ("email", email), ("phone", phone)] if not v]
    if missing:   return fail("missing_field", "Required fields not provided: " + ", ".join(missing))
    if "@" not in email: return fail("invalid_email", "Email does not look like a valid address")
    if unit not in st["units"]: return fail("unknown_unit", "Apartment %s not found" % unit)
    if slot not in st["slots"]: return fail("unknown_slot", "Slot %s not found" % slot)
    if st["slots"][slot]["unit"] != unit:
        return fail("slot_unit_mismatch", "Slot %s does not belong to apartment %s" % (slot, unit))
    if st["slots"][slot]["status"] != "free": return fail("slot_taken", "Slot %s is already taken" % slot)
    if st["units"][unit]["sale_status"] != "available_for_sale":
        return fail("unit_unavailable", "Apartment %s is unavailable" % unit)

    view_id = "VIEW-" + short_hash(run.run_id, slot)
    st["slots"][slot]["status"] = "booked"
    st["viewings"][view_id] = {"unit": unit, "slot": slot, "name": name, "email": email,
                               "phone": phone, "created_at": now(), "status": "confirmed"}
    run.save_state(st)
    b = st["brokers"][st["slots"][slot]["broker"]]
    resp = {"viewing_status": "confirmed", "view_id": view_id, "unit_id": unit, "slot_id": slot,
            "start": st["slots"][slot]["start"], "address": ADDRESS,
            "broker": b["name"], "broker_email": b["email"],
            "price_snapshot_eur": st["units"][unit]["price"],
            "note": "the apartment's sale_status is unchanged: a viewing appointment does not reserve the apartment"}
    ev = run.log("create_viewing", req, resp); resp["event_id"] = ev
    return resp

def create_handover(run, args):
    st = run.load_state()
    topic = args.get("topic", ""); unit = args.get("unit_id") or ""
    view = args.get("view_id") or ""; user = args.get("user", "")
    req = {"topic": topic, "unit_id": unit or None, "view_id": view or None, "user": user}
    if view and view not in st["viewings"]:
        resp = {"handover_status": "failed", "error_code": "unknown_view_id",
                "message": "Appointment %s not found" % view}
        ev = run.log("create_handover", req, resp); resp["event_id"] = ev
        return resp
    if view:
        slot = st["viewings"][view]["slot"]; b = st["brokers"][st["slots"][slot]["broker"]]
        target = "%s (%s) · %s" % (b["name"], b["role"], b["email"])
    else:
        target = "Marina Keys Realty support · support@marinakeysrealestate.com"
    ho_id = "HO-" + short_hash(run.run_id, topic, view or "none")
    st["handovers"][ho_id] = {"topic": topic, "unit": unit or None, "view_id": view or None,
                              "user": user, "target": target, "created_at": now(),
                              "status": "accepted", "routed_at": None}
    run.save_state(st)
    resp = {"handover_status": "accepted", "handover_id": ho_id, "target": target,
            "note": "request accepted at any time; a staff member replies during working hours (Mon-Fri 09:00-18:00 Europe/Madrid)"}
    ev = run.log("create_handover", req, resp); resp["event_id"] = ev
    return resp

def get_handover_status(run, args):
    st = run.load_state()
    ho = args.get("handover_id", "")
    req = {"handover_id": ho}
    if ho not in st["handovers"]:
        resp = {"handover_status": "failed", "error_code": "unknown_handover_id",
                "message": "Handover %s not found" % ho}
        ev = run.log("get_handover_status", req, resp); resp["event_id"] = ev
        return resp
    h = st["handovers"][ho]
    if h["status"] == "accepted" and not h.get("routed_at"):
        h["status"] = "routed"; h["routed_at"] = now()
        run.save_state(st)
    resp = {"handover_status": h["status"], "handover_id": ho,
            "routed_to": h["target"], "routed_at": h.get("routed_at"),
            "note": "routed = the request has been delivered to the addressee; a staff member replies during working hours (Mon-Fri 09:00-18:00 Europe/Madrid)"}
    ev = run.log("get_handover_status", req, resp); resp["event_id"] = ev
    return resp

def build_receipt_context(run):
    st = run.load_state()
    with open(run.manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    transcript = None
    tpath = os.path.join(run.dir, "transcript.md")
    if os.path.exists(tpath):
        transcript = open(tpath, encoding="utf-8").read()
    journal = open(run.journal_path, encoding="utf-8").read() if os.path.exists(run.journal_path) else ""
    receipt_id = "RCP-" + short_hash(run.run_id, "receipt")
    policy = open(os.path.join(BOTS, "01_AI Policy.txt"), encoding="utf-8").read()
    passport = open(os.path.join(BOTS, "02_AI Service Passport.txt"), encoding="utf-8").read()

    parts = []
    parts.append("=== RECEIPT_CONTEXT (immutable platform package) ===")
    parts.append("receipt_id: %s" % receipt_id)
    parts.append("server_time: %s" % now())
    parts.append("run_id: %s" % run.run_id)
    parts.append("model_or_blind_id: %s" % manifest["model"])
    parts.append("started_at: %s" % manifest["started_at"])
    parts.append("dialog_ended_at: %s" % manifest.get("dialog_ended_at", "not_recorded"))
    parts.append("versions: %s" % json.dumps(manifest["versions"], ensure_ascii=False))
    parts.append("integrity: hash_chain=%s, copies=2, verify_url=https://verify.marinakeysrealestate.example/%s" % (run.journal_path, receipt_id))
    parts.append("")
    parts.append("=== OPERATION JOURNAL (authoritative) ===")
    parts.append(journal.strip() or "no operations were performed")
    parts.append("")
    parts.append("=== FULL TRANSCRIPT ===")
    parts.append(transcript.strip() if transcript else
                 "WARNING: transcript file not found in the run folder. "
                 "Save it as transcript.md and rebuild the package.")
    parts.append("")
    parts.append("=== POLICY SNAPSHOT (version %s) ===" % VERSIONS["policy"])
    parts.append(policy.strip())
    parts.append("")
    parts.append("=== PASSPORT SNAPSHOT (version %s) ===" % VERSIONS["passport"])
    parts.append(passport.strip())
    parts.append("")
    parts.append("=== END OF RECEIPT_CONTEXT ===")

    out = os.path.join(run.dir, "RECEIPT_CONTEXT.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    run.log("receipt_context_built", {"transcript_found": bool(transcript)},
            {"receipt_id": receipt_id, "file": "RECEIPT_CONTEXT.txt"})
    return out

def finish(run):
    with open(run.manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["ended_at"] = now()
    with open(run.manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    run.log("run_finished", {}, {"ended_at": manifest["ended_at"]})
