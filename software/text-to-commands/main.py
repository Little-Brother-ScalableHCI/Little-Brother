
import pickle
import random

import redis
import spacy
from spacy.pipeline import EntityRuler

##############################################################################
# 1) Define a Larger List of Tool Synonyms
##############################################################################

TOOL_SYNONYMS = {
    # Hand Tools
    "hammer": ["hammer", "mallet", "sledgehammer"],
    "screwdriver": ["screwdriver", "driver", "phillips-head", "flat-head"],
    "wrench": ["wrench", "spanner", "socket wrench", "ratchet"],
    "drill": ["drill", "power drill", "cordless drill"],
    "saw": ["saw", "circular saw", "hand saw", "chainsaw", "jigsaw", "sabre saw"],
    "tape measure": ["tape measure", "measuring tape"],
    "pliers": ["pliers"],
    "chisel": ["chisel"],
    "clamp": ["clamp", "grip clamp", "bar clamp", "c-clamp"],
    "level": ["level", "spirit level"],
    "vise": ["vise", "bench vise"],
    "utility knife": ["utility knife", "box cutter", "razor knife"],
    "paintbrush": ["paintbrush", "brush"],
    "stud finder": ["stud finder", "wall scanner"],
    "hex key": ["hex key", "allen wrench", "allen key"],
    "router": ["router"],
    "orbital sander": ["orbital sander", "random orbital sander"],
    "sandpaper": ["sandpaper", "abrasive paper"],
    "handplane": ["handplane", "plane"],
    "belt sander": ["belt sander"],

    # Common Machine-Shop Equipment
    "lathe": ["lathe", "turning lathe", "engine lathe", "metal lathe"],
    "milling machine": ["milling machine", "vertical mill", "cnc mill", "CNC milling machine"],
    "drill press": ["drill press"],
    "band saw": ["band saw", "vertical band saw", "horizontal band saw"],
    "bench grinder": ["bench grinder", "pedestal grinder"],
    "cnc router": ["cnc router"],
    "3d printer": ["3d printer", "3d printing machine"],
    "arc welder": ["arc welder", "stick welder"],
    "mig welder": ["mig welder", "wire welder"],
    "tig welder": ["tig welder"],
    "plasma cutter": ["plasma cutter"],
    "waterjet cutter": ["waterjet cutter", "waterjet"],
    "press brake": ["press brake"],
    "sheet metal bender": ["sheet metal bender", "metal bender"],
    "surface grinder": ["surface grinder"],
    "tool grinder": ["tool grinder"],

    # Others
    "cell phone": ["cell phone", "mobile phone", "phone"],
    "bottle": ["bottle"],
}

##############################################################################
# 2) Build the spaCy Pipeline with EntityRuler
##############################################################################

def create_tool_patterns(tool_synonyms_dict):
    """
    For each canonical tool -> synonyms, return a list of spaCy patterns
    mapping synonyms to the label 'TOOL'.
    We'll store the canonical tool name in 'attrs'.
    """
    patterns = []
    for canonical_tool, synonyms in tool_synonyms_dict.items():
        for synonym in synonyms:
            patterns.append({
                "label": "TOOL",
                "pattern": synonym,
                "attrs": {"canonical": canonical_tool}
            })
    return patterns

def build_nlp_tool_extractor(tool_synonyms_dict):
    nlp = spacy.load("en_core_web_sm")
    # Insert an EntityRuler before the default 'ner'
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    tool_patterns = create_tool_patterns(tool_synonyms_dict)
    ruler.add_patterns(tool_patterns)
    return nlp

##############################################################################
# 3a) Generate Dummy Commands (All about finding locations)
##############################################################################

LOCATION_PHRASES = [
    "Where is the",
    "I can't find the",
    "Do you know where the",
    "Locate the",
    "I'm looking for the"
]

def generate_dummy_commands(num_commands=5):
    commands = []
    canonical_tools = list(TOOL_SYNONYMS.keys())

    for _ in range(num_commands):
        # Pick a random canonical tool
        tool_name = random.choice(canonical_tools)
        # Pick a random synonym
        tool_synonym = random.choice(TOOL_SYNONYMS[tool_name])
        # Pick a random location phrase
        phrase = random.choice(LOCATION_PHRASES)

        # Build a dummy sentence about finding that tool
        sentence = f"{phrase} {tool_synonym} in the workshop?"
        commands.append(sentence)
    return commands


def extract_tools_from_doc(doc):
    """
    Return a list of canonical tool names found in the doc.
    """
    tools = []
    for ent in doc.ents:
        if ent.label_ == "TOOL":
            # Grab the canonical name if available
            if hasattr(ent._, "canonical"):
                tools.append(ent._.canonical)
            else:
                # Fallback if 'canonical' not set
                tools.append(ent.text.lower())
    return tools

##############################################################################
# 5) Build a Structured Command (Only One Intent: "find_location")
##############################################################################

def build_command_structure(text, doc):
    """
    Since we only have one intent (find_location), we just:
      - Identify which tool(s) is being asked about
      - Mark the intent as 'find_location'
    """
    found_tools = extract_tools_from_doc(doc)

    # For simplicity, assume only one or the first found if multiple tools are mentioned
    tool = found_tools[0] if found_tools else None

    command_dict = {
        "original_text": text,
        "intent": "find_location",
        "object": tool
    }
    return command_dict

##############################################################################
# Main
##############################################################################

def main():
    db = redis.Redis(host="redis", port=6379, db=0)
    # Build the spaCy pipeline once
    nlp = build_nlp_tool_extractor(TOOL_SYNONYMS)

    # PART A: Generate and test with dummy text commands
    dummy_commands = generate_dummy_commands(5)
    # print("\n--- Testing with Dummy Commands ---")
    for cmd in dummy_commands:
        doc = nlp(cmd)
        structured_cmd = build_command_structure(cmd, doc)
        # print(structured_cmd)

    # PART B: (Optional) Speech-to-Text, then NLU
    # print("\n--- Testing with Speech-to-Text (Press CTRL+C to exit) ---")

    print("Waiting for speech-to-text data...")
    ps = db.pubsub()
    ps.subscribe("speech-to-text")
    for binary_data in ps.listen():
        try:
            text_input = pickle.loads(bytes(binary_data["data"]))
        except pickle.UnpicklingError:
            continue
        except Exception as e:
            print(e)
            continue

        if not text_input:
            # If transcription failed or empty, skip
            continue

        print("Transcribed:", text_input)
        # Process the transcribed text
        doc = nlp(text_input)
        structured_cmd = build_command_structure(text_input, doc)

        if not structured_cmd["object"]:
            # If no tool found, skip
            continue

        db.set("command", pickle.dumps(structured_cmd))
        db.publish("command", pickle.dumps(structured_cmd))
        print("Structured Command:", structured_cmd)

if __name__ == "__main__":
    main()
