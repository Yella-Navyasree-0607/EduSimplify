"""
EduSimplify – Demo Mode Responses
===================================
Pre-written, high-quality responses that simulate the full 5-agent pipeline
without any IBM watsonx.ai credentials.

These responses are keyed by (level, topic_hint) where topic_hint is a rough
category inferred from keywords in the submitted text.  If no match is found,
the "default" entry is used.

To activate demo mode: leave IBM credentials unconfigured (the default),
or set DEMO_MODE=true in your .env file.
"""

from __future__ import annotations
import re


# ─────────────────────────────────────────────────────────────────────────────
#  Demo data bank
#  Keys: "physics" | "cs" | "biology" | "math" | "chemistry" | "default"
#  Each entry is level-agnostic; level-specific language is handled in
#  get_demo_pipeline_result() by adjusting copy where needed.
# ─────────────────────────────────────────────────────────────────────────────

_DEMO_BANK: dict[str, dict] = {

    # ── Physics / Newton's Laws ───────────────────────────────────────────────
    "physics": {
        "domain": "Physics",
        "main_topics": [
            "Newton's First Law (Law of Inertia)",
            "Newton's Second Law (F = ma)",
            "Newton's Third Law (Action-Reaction)",
            "Classical Mechanics",
            "Force, Mass, and Acceleration",
            "Real-world applications of motion",
        ],
        "complexity": "Intermediate",
        "description": (
            "This content covers Newton's three laws of motion, which are the "
            "bedrock of classical mechanics. It explains how objects behave under "
            "the influence of forces and provides the mathematical relationships "
            "between force, mass, and acceleration."
        ),
        "simple_explanation": {
            "Beginner": (
                "Imagine you're sitting on a skateboard. If nobody pushes you, "
                "you stay still — that's Newton's First Law: things keep doing "
                "what they're already doing unless something changes that. "
                "Newton's Second Law tells us HOW HARD you need to push: a heavier "
                "person needs a bigger push to move at the same speed as a lighter "
                "one. The formula is simply Force = Mass × Acceleration (F = ma). "
                "Finally, Newton's Third Law says every push gets a push back — "
                "when you kick a ball, the ball pushes your foot with the same "
                "force in return. Together these three rules explain everything "
                "from how cars accelerate to why rockets fly into space."
            ),
            "Intermediate": (
                "Newton's three laws of motion form the foundation of classical "
                "mechanics. The First Law (inertia) states that a body remains at "
                "rest or moves with constant velocity unless a net external force "
                "acts on it. The Second Law quantifies the effect of that force: "
                "F = ma, linking net force (N), mass (kg), and acceleration (m/s²). "
                "The Third Law describes force pairs: whenever object A exerts a "
                "force on object B, object B exerts an equal and opposite force on A. "
                "These laws together allow us to predict the motion of any object "
                "when the forces acting on it are known."
            ),
            "Advanced": (
                "Newton's laws of motion constitute an axiomatic framework for "
                "classical mechanics valid in inertial reference frames. The First "
                "Law defines inertial frames and the concept of force. The Second "
                "Law, F = dp/dt (rate of change of linear momentum), reduces to "
                "F = ma for constant-mass systems. The Third Law enforces "
                "conservation of momentum via Newton's Third Law force pairs. "
                "While superseded by relativistic and quantum mechanics at extreme "
                "scales, Newtonian mechanics remains the correct approximation for "
                "macroscopic, low-velocity systems and underpins engineering "
                "disciplines ranging from structural analysis to orbital mechanics."
            ),
        },
        "key_concepts": [
            "Inertia: The tendency of an object to resist changes to its state of motion",
            "Net Force: The vector sum of all forces acting on an object",
            "Acceleration: The rate of change of velocity (m/s²)",
            "Mass: A measure of an object's resistance to acceleration (kg)",
            "Action-Reaction Pair: Equal and opposite forces between two interacting bodies",
            "Classical Mechanics: The branch of physics governing macroscopic motion",
        ],
        "important_points": [
            "An object remains at rest or in uniform motion unless acted on by a net force",
            "F = ma: force equals mass times acceleration",
            "Doubling mass while keeping force constant halves the acceleration",
            "Action and reaction forces act on DIFFERENT objects, not the same one",
            "These laws apply to inertial (non-accelerating) reference frames",
            "Newton's laws break down at near-light speeds (use relativity) and atomic scales (use quantum mechanics)",
        ],
        "short_summary": (
            "Newton's three laws explain how and why objects move. Inertia keeps "
            "objects doing what they're already doing; F = ma quantifies how forces "
            "change that motion; and every force has an equal, opposite reaction force. "
            "These principles underlie all of classical physics and engineering."
        ),
        "examples": [
            {
                "title": "The Seatbelt and Inertia",
                "body": (
                    "When a car brakes suddenly, your body continues moving forward "
                    "because of inertia (First Law). The seatbelt applies a backward "
                    "force to stop you — demonstrating that a net force is needed to "
                    "change your motion. Without the seatbelt, you'd keep moving until "
                    "the dashboard or windscreen applied that force instead!"
                ),
            },
            {
                "title": "Pushing a Shopping Cart",
                "body": (
                    "An empty shopping cart accelerates quickly with a gentle push "
                    "(low mass → high acceleration). A full cart loaded with groceries "
                    "needs a much harder push to reach the same speed (high mass → "
                    "lower acceleration for the same force). This is F = ma in everyday "
                    "action: acceleration = Force ÷ Mass."
                ),
            },
            {
                "title": "Rocket Propulsion",
                "body": (
                    "A rocket engine expels hot gas downward at great force. By "
                    "Newton's Third Law, the gas pushes the rocket upward with an "
                    "equal and opposite force. There is no ground for the rocket to "
                    "push against — it works entirely through the action-reaction pair "
                    "between the rocket and the expelled exhaust gases."
                ),
            },
        ],
        "exam": {
            "mcq": [
                {
                    "question": "Which of Newton's laws states that F = ma?",
                    "options": ["A) First Law", "B) Second Law", "C) Third Law", "D) Law of Gravitation"],
                    "answer": "B",
                },
                {
                    "question": "A 10 kg object is pushed with a net force of 50 N. What is its acceleration?",
                    "options": ["A) 0.2 m/s²", "B) 5 m/s²", "C) 500 m/s²", "D) 50 m/s²"],
                    "answer": "B",
                },
                {
                    "question": "According to Newton's Third Law, action and reaction forces act on:",
                    "options": ["A) The same object", "B) Different objects", "C) Only rigid bodies", "D) Massless objects"],
                    "answer": "B",
                },
            ],
            "short_answer": [
                {
                    "question": "Explain why passengers lurch forward when a bus brakes suddenly.",
                    "hint": "Think about Newton's First Law and inertia.",
                },
                {
                    "question": "A force of 20 N acts on a 4 kg mass. Calculate the acceleration.",
                    "hint": "Use F = ma and rearrange for a.",
                },
            ],
            "application": (
                "A student pushes a 2 kg textbook across a frictionless table with a "
                "constant force of 6 N for 3 seconds. (a) Calculate the acceleration "
                "of the book. (b) What is the book's velocity after 3 seconds if it "
                "started from rest? (c) Identify the reaction force described by "
                "Newton's Third Law in this scenario."
            ),
        },
        "review": {
            "clarity": 9, "completeness": 9, "level_match": 9, "usefulness": 9,
            "overall": 9,
            "review_note": (
                "The output provides a clear, level-appropriate explanation of Newton's "
                "laws with strong real-world examples and well-structured exam questions."
            ),
            "improvement_tip": (
                "Adding a free-body diagram description or vector notation for "
                "intermediate/advanced students would further strengthen the material."
            ),
        },
    },

    # ── Computer Science / Operating Systems ──────────────────────────────────
    "cs": {
        "domain": "Computer Science",
        "main_topics": [
            "Operating System overview",
            "Kernel and system software",
            "Process scheduling algorithms",
            "Memory management",
            "File system organisation",
            "Virtual memory (paging and segmentation)",
        ],
        "complexity": "Intermediate",
        "description": (
            "This content introduces operating systems as the software layer between "
            "hardware and applications. It covers core OS components including the "
            "kernel, process scheduler, memory manager, and file system, as well as "
            "virtual memory techniques."
        ),
        "simple_explanation": {
            "Beginner": (
                "An operating system (OS) is like the manager of a computer. Just "
                "as a manager assigns tasks to workers, the OS decides which program "
                "gets to use the CPU, how much memory each app gets, and where files "
                "are stored on the disk. The kernel is the 'boss' at the centre of "
                "the OS that has full control. When you open multiple apps at once, "
                "the scheduler switches between them so fast it feels like they all "
                "run at the same time. Virtual memory lets your computer pretend it "
                "has more RAM than it actually does by temporarily storing data on "
                "the hard drive."
            ),
            "Intermediate": (
                "An operating system manages hardware resources and provides services "
                "to applications. Its kernel — the privileged core — handles process "
                "scheduling (allocating CPU time via Round Robin, FCFS, or SJF), "
                "memory management (allocation, deallocation, paging), and I/O "
                "operations. The file system organises persistent data on storage "
                "devices. Virtual memory uses paging and segmentation to give each "
                "process the illusion of a large, private address space, even when "
                "physical RAM is limited."
            ),
            "Advanced": (
                "An OS abstracts hardware resources through a privileged kernel that "
                "enforces isolation between user-space processes. Scheduling policies "
                "(preemptive Round Robin with time quanta, multi-level feedback "
                "queues, CFS) balance throughput, latency, and fairness. The virtual "
                "memory subsystem uses page tables, TLBs, and demand paging to "
                "provide per-process isolation and enable memory overcommit. The "
                "VFS layer abstracts concrete file systems (ext4, NTFS, FAT32) behind "
                "a unified syscall interface. Synchronisation primitives (mutexes, "
                "semaphores, condition variables) prevent race conditions in "
                "concurrent process execution."
            ),
        },
        "key_concepts": [
            "Kernel: The core program of the OS with full hardware control",
            "Process Scheduler: Decides which process runs on the CPU and when",
            "Round Robin: CPU scheduling algorithm that gives each process an equal time slice",
            "Memory Management: Handles allocation and deallocation of RAM",
            "File System: Organises and retrieves data stored on disk",
            "Virtual Memory: Technique allowing programs to use more memory than physically available",
        ],
        "important_points": [
            "The OS acts as an intermediary between hardware and application software",
            "The kernel runs in privileged mode; user programs run in restricted user mode",
            "CPU scheduling algorithms differ in their trade-offs between fairness and efficiency",
            "Paging divides memory into fixed-size pages, reducing external fragmentation",
            "Virtual memory uses the disk as an extension of RAM via swap space",
            "The file system provides persistent, hierarchical data storage",
        ],
        "short_summary": (
            "An operating system manages a computer's hardware resources — CPU, memory, "
            "and storage — on behalf of running programs. The kernel is its privileged core. "
            "Scheduling, memory management, and the file system are the three pillars that "
            "keep applications running smoothly and in isolation from one another."
        ),
        "examples": [
            {
                "title": "The Restaurant Analogy (Scheduling)",
                "body": (
                    "Think of the CPU as a single chef and processes as customer orders. "
                    "Round Robin scheduling is like the chef spending exactly two minutes "
                    "on each order in rotation — no order waits forever, but none finishes "
                    "instantly either. First-Come-First-Served is like a strict queue: "
                    "the first order placed is the first one fully completed."
                ),
            },
            {
                "title": "Library Books and Virtual Memory",
                "body": (
                    "Virtual memory is like a library borrowing system. Your desk (RAM) "
                    "can only hold 10 books at once, but the library (disk) holds thousands. "
                    "When you need a book that's not on your desk, a librarian swaps one out "
                    "and brings the new one — just as the OS pages data in and out of RAM."
                ),
            },
            {
                "title": "Filing Cabinet and the File System",
                "body": (
                    "A file system works like a well-organised filing cabinet. Directories "
                    "are labelled drawers; files are documents inside. The file system keeps "
                    "an index (like a table of contents) so the OS can find any file quickly "
                    "without searching every drawer one by one."
                ),
            },
        ],
        "exam": {
            "mcq": [
                {
                    "question": "Which OS component has complete control over the hardware?",
                    "options": ["A) Shell", "B) File System", "C) Kernel", "D) Scheduler"],
                    "answer": "C",
                },
                {
                    "question": "In Round Robin scheduling, each process receives:",
                    "options": ["A) Unlimited CPU time", "B) A fixed time slice (quantum)", "C) Priority-based CPU time", "D) Memory before CPU"],
                    "answer": "B",
                },
                {
                    "question": "Virtual memory allows a program to use more memory than available RAM by using:",
                    "options": ["A) A faster CPU", "B) Compression algorithms", "C) Disk storage as an extension of RAM", "D) Shared memory between processes"],
                    "answer": "C",
                },
            ],
            "short_answer": [
                {
                    "question": "What is the difference between paging and segmentation in memory management?",
                    "hint": "Think about fixed vs variable size memory blocks.",
                },
                {
                    "question": "Why might Shortest Job First (SJF) scheduling cause starvation?",
                    "hint": "Consider what happens to long jobs when short jobs keep arriving.",
                },
            ],
            "application": (
                "A computer has 4 GB of physical RAM and is running 6 processes that each "
                "require 1 GB. (a) Can all processes run simultaneously without virtual "
                "memory? (b) Explain how the OS uses virtual memory and paging to allow "
                "all 6 processes to run. (c) Describe one trade-off introduced by relying "
                "heavily on virtual memory."
            ),
        },
        "review": {
            "clarity": 9, "completeness": 9, "level_match": 9, "usefulness": 9,
            "overall": 9,
            "review_note": (
                "The output delivers a thorough and clearly structured overview of "
                "operating system concepts with excellent real-world analogies."
            ),
            "improvement_tip": (
                "Including a comparison table of scheduling algorithms (Round Robin vs "
                "SJF vs FCFS) with trade-offs would add significant value for exam prep."
            ),
        },
    },

    # ── Biology / DNA ─────────────────────────────────────────────────────────
    "biology": {
        "domain": "Biology",
        "main_topics": [
            "DNA double helix structure",
            "Nucleotide composition (sugar, phosphate, bases)",
            "Complementary base pairing (A-T, G-C)",
            "DNA replication mechanism",
            "Gene expression and protein synthesis",
            "Mutations and genetic disorders",
        ],
        "complexity": "Intermediate",
        "description": (
            "This content describes the structure of DNA as a double helix formed "
            "by two polynucleotide chains. It covers the role of complementary base "
            "pairing in replication and gene expression, and introduces the concept "
            "of mutations and their consequences."
        ),
        "simple_explanation": {
            "Beginner": (
                "DNA is like a twisted ladder — scientists call this shape a double "
                "helix. The sides of the ladder are made of sugar and phosphate "
                "molecules. The rungs are made of pairs of chemical 'letters' called "
                "bases: A always pairs with T, and G always pairs with C. Your entire "
                "body plan is written in this four-letter code. When cells divide, "
                "they 'unzip' the ladder and build a new copy of each side, so both "
                "new cells get the same instructions. Sometimes a copying mistake "
                "happens — that's a mutation — which can change how the body works, "
                "sometimes harmlessly, sometimes causing disease."
            ),
            "Intermediate": (
                "DNA is a double-stranded polynucleotide arranged in a double helix. "
                "Each strand consists of nucleotides, each containing a deoxyribose "
                "sugar, a phosphate group, and one of four nitrogenous bases (A, T, "
                "G, C). The strands are held together by hydrogen bonds between "
                "complementary base pairs: A–T and G–C. During replication, helicase "
                "unwinds the helix, and DNA polymerase synthesises new complementary "
                "strands, yielding two identical double-stranded DNA molecules. "
                "Mutations — changes in the base sequence — can alter protein "
                "structure, potentially disrupting cellular function."
            ),
            "Advanced": (
                "DNA is an antiparallel double helix stabilised by Watson–Crick base "
                "pairing (A·T via two hydrogen bonds; G·C via three) and base-stacking "
                "interactions. Replication is semi-conservative: helicase unwinds "
                "parental strands; primase lays RNA primers; DNA polymerase III "
                "extends the leading strand continuously and the lagging strand "
                "discontinuously (Okazaki fragments). Ligase seals nicks. Point "
                "mutations, frameshift mutations, and chromosomal rearrangements "
                "can alter reading frames, disrupt regulatory elements, or cause "
                "oncogene activation, contributing to cancer and heritable disorders."
            ),
        },
        "key_concepts": [
            "Double Helix: The twisted-ladder shape of the DNA molecule",
            "Nucleotide: The monomer unit of DNA (sugar + phosphate + base)",
            "Complementary Base Pairing: A bonds with T; G bonds with C",
            "DNA Replication: Semi-conservative copying of DNA before cell division",
            "Gene Expression: Process by which DNA is transcribed and translated into proteins",
            "Mutation: A change in the DNA base sequence that may alter protein function",
        ],
        "important_points": [
            "DNA carries the genetic instructions for the development and function of all living organisms",
            "The four bases are Adenine (A), Thymine (T), Guanine (G), and Cytosine (C)",
            "A always pairs with T (2 hydrogen bonds); G always pairs with C (3 hydrogen bonds)",
            "DNA replication is semi-conservative — each new molecule retains one original strand",
            "Mutations can be silent, harmful, or (rarely) beneficial",
            "The sequence of bases in DNA encodes the sequence of amino acids in proteins",
        ],
        "short_summary": (
            "DNA is a double-helix molecule built from four nucleotide bases whose "
            "specific pairing (A-T, G-C) stores genetic information. Replication "
            "faithfully copies this information before cell division. Mutations are "
            "errors in this copying process that can range from harmless to disease-causing."
        ),
        "examples": [
            {
                "title": "The Zip-Lock Bag Analogy",
                "body": (
                    "Think of the two strands of DNA as the two sides of a zip-lock bag. "
                    "The interlocking teeth are the base pairs (A-T, G-C). To replicate, "
                    "the zip unzips from one end, and a new matching side is built along "
                    "each half — giving you two identical bags from one original."
                ),
            },
            {
                "title": "The Four-Letter Language",
                "body": (
                    "Imagine your entire body is built from instructions written using "
                    "only four letters: A, T, G, and C. The order of these letters along "
                    "the DNA strand spells out genes — recipes for making proteins. "
                    "A typo in just one letter (a point mutation) can change the 'recipe', "
                    "sometimes creating a faulty protein that causes disease."
                ),
            },
            {
                "title": "Photocopying and DNA Replication",
                "body": (
                    "DNA replication is like photocopying a document where the copier "
                    "keeps one page of the original and prints one new page alongside it. "
                    "You end up with two copies that each have one 'original' page "
                    "and one 'new' page — that's why biologists call it semi-conservative "
                    "replication."
                ),
            },
        ],
        "exam": {
            "mcq": [
                {
                    "question": "Which base pairs with Guanine (G) in the DNA double helix?",
                    "options": ["A) Adenine", "B) Thymine", "C) Cytosine", "D) Uracil"],
                    "answer": "C",
                },
                {
                    "question": "What type of bond holds complementary base pairs together in DNA?",
                    "options": ["A) Ionic bonds", "B) Covalent bonds", "C) Hydrogen bonds", "D) Peptide bonds"],
                    "answer": "C",
                },
                {
                    "question": "DNA replication is described as 'semi-conservative' because:",
                    "options": [
                        "A) Only half the DNA is copied",
                        "B) Each new molecule contains one original and one new strand",
                        "C) Replication only occurs in the cell nucleus",
                        "D) Both strands are degraded and rebuilt fresh",
                    ],
                    "answer": "B",
                },
            ],
            "short_answer": [
                {
                    "question": "Explain why complementary base pairing is essential for accurate DNA replication.",
                    "hint": "Think about how each strand acts as a template.",
                },
                {
                    "question": "Describe how a frameshift mutation differs from a point mutation.",
                    "hint": "Consider what happens to the reading frame of the genetic code.",
                },
            ],
            "application": (
                "A segment of DNA has the base sequence: 5'-ATGCCTGAA-3'. "
                "(a) Write the complementary strand in the 3' to 5' direction. "
                "(b) A mutation changes the 4th base from C to A. Predict how this "
                "might affect the protein coded for by this segment. "
                "(c) Explain why some mutations are 'silent' and have no effect on "
                "the organism's phenotype."
            ),
        },
        "review": {
            "clarity": 9, "completeness": 9, "level_match": 9, "usefulness": 9,
            "overall": 9,
            "review_note": (
                "Excellent coverage of DNA structure, replication, and mutations with "
                "clear analogies and well-calibrated exam questions across all types."
            ),
            "improvement_tip": (
                "A labelled diagram description of the double helix showing base pairs "
                "and strand polarity would enhance understanding for visual learners."
            ),
        },
    },
}

# Default fallback for unrecognised topics
_DEMO_BANK["default"] = _DEMO_BANK["physics"]


# ─────────────────────────────────────────────────────────────────────────────
#  Topic detection
# ─────────────────────────────────────────────────────────────────────────────

_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "physics":  ["newton", "force", "mass", "acceleration", "motion", "velocity",
                 "inertia", "kinetic", "gravity", "energy", "momentum", "physics"],
    "cs":       ["operating system", "kernel", "process", "scheduler", "cpu",
                 "memory", "paging", "file system", "algorithm", "computer",
                 "software", "hardware", "virtual", "program"],
    "biology":  ["dna", "cell", "gene", "protein", "nucleotide", "adenine",
                 "thymine", "guanine", "cytosine", "helix", "mutation", "replication",
                 "biology", "organism", "chromosome"],
}


def _detect_topic(content: str) -> str:
    """Return the best-matching topic key for the given content."""
    content_lower = content.lower()
    scores = {
        topic: sum(1 for kw in keywords if kw in content_lower)
        for topic, keywords in _TOPIC_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "default"


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_demo_pipeline_result(content: str, level: str) -> dict:
    """
    Return a fully assembled pipeline result dict for demo mode.

    Parameters
    ----------
    content : str  – the user's submitted text (used only for topic detection)
    level   : str  – 'Beginner' | 'Intermediate' | 'Advanced'
    """
    topic = _detect_topic(content)
    bank  = _DEMO_BANK.get(topic, _DEMO_BANK["default"])

    simple_exp_map = bank.get("simple_explanation", {})
    simple_exp = (
        simple_exp_map.get(level)
        or simple_exp_map.get("Intermediate")
        or "Demo explanation not available."
    )

    review = dict(bank["review"])

    pipeline_log = [
        "Agent 1 (Content Analyzer): Running… [DEMO MODE]",
        f"Agent 1 (Content Analyzer): Done — domain={bank['domain']} [DEMO MODE]",
        "Agent 2 (Simplification): Running… [DEMO MODE]",
        "Agent 2 (Simplification): Done [DEMO MODE]",
        "Agent 3 (Example Generator): Running… [DEMO MODE]",
        f"Agent 3 (Example Generator): Done — {len(bank['examples'])} examples [DEMO MODE]",
        "Agent 4 (Exam Questions): Running… [DEMO MODE]",
        f"Agent 4 (Exam Questions): Done — {len(bank['exam']['mcq'])} MCQs, "
        f"{len(bank['exam']['short_answer'])} SA [DEMO MODE]",
        "Agent 5 (Review): Running… [DEMO MODE]",
        f"Agent 5 (Review): Done — overall score={review['overall']}/10 [DEMO MODE]",
    ]

    return {
        "error": False,
        "demo_mode": True,
        "level": level,
        "pipeline_log": pipeline_log,

        # Agent 1
        "domain":             bank["domain"],
        "main_topics":        bank["main_topics"],
        "detected_complexity": bank["complexity"],
        "content_description": bank["description"],

        # Agent 2
        "simple_explanation": simple_exp,
        "key_concepts":       bank["key_concepts"],
        "important_points":   bank["important_points"],
        "short_summary":      bank["short_summary"],

        # Agent 3
        "examples": bank["examples"],

        # Agent 4
        "exam_mcq":           bank["exam"]["mcq"],
        "exam_short_answer":  bank["exam"]["short_answer"],
        "exam_application":   bank["exam"]["application"],

        # Agent 5
        "review": review,
    }
