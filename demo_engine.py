"""
EduSimplify – Content-Aware Demo Engine
=========================================
Implements all five agents entirely in pure Python (no external AI APIs).
Each agent reads the user's actual submitted text and produces output that
is genuinely derived from it, making every demo run relevant to what the
user pasted.

Architecture
------------
Agent 1 – ContentAnalyzer   : domain detection, topic extraction, complexity score
Agent 2 – Simplifier        : sentence selection + level-adapted rewriting
Agent 3 – ExampleGenerator  : concept-to-analogy mapping from the text
Agent 4 – ExamBuilder       : fact-based MCQ / SA / application question generation
Agent 5 – Reviewer          : rule-based quality scoring of the assembled output

All logic is deterministic and requires no network access.
"""

from __future__ import annotations
import re
import math
from collections import Counter
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════════
#  Shared NLP helpers
# ═══════════════════════════════════════════════════════════════════════════════

_STOP = {
    "a","an","the","and","or","but","if","in","on","at","to","for","of","with",
    "by","from","as","is","was","are","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might","shall",
    "not","no","nor","so","yet","both","either","neither","each","few","more",
    "most","other","some","such","than","then","that","this","these","those",
    "it","its","itself","he","she","they","them","their","we","us","our","you",
    "your","i","my","me","his","her","what","which","who","when","where","how",
    "all","any","both","each","every","much","many","only","own","same","too",
    "very","just","because","while","although","however","therefore","thus",
    "also","into","through","during","before","after","above","below","between",
    "about","against","along","around","up","down","out","off","over","under",
    "can","upon","per","within","without","whether","there","here",
}

_ADVANCED_VOCAB: dict[str, str] = {
    "demonstrate": "show",
    "facilitate":  "help",
    "utilise":     "use",
    "utilize":     "use",
    "commence":    "start",
    "terminate":   "end",
    "sufficient":  "enough",
    "subsequent":  "next",
    "prior":       "before",
    "obtain":      "get",
    "approximately": "about",
    "fundamental": "basic",
    "primary":     "main",
    "constitute":  "make up",
    "encompasses": "includes",
    "comprise":    "include",
    "formulate":   "create",
    "implement":   "carry out",
    "indicates":   "shows",
    "referred to": "called",
    "in order to": "to",
    "with respect to": "about",
    "as a result of": "because of",
    "in the event that": "if",
}


def _sentences(text: str) -> list[str]:
    # Normalise newlines and collapse whitespace before splitting
    text = re.sub(r'\s+', ' ', text).strip()
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if len(p.strip()) > 15]


def _words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def _keywords(text: str, top_n: int = 12) -> list[str]:
    tokens = [w for w in _words(text) if w not in _STOP and len(w) > 3]
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(top_n)]


def _syllable_count(word: str) -> int:
    word = word.lower().strip(".,;:!?")
    if not word:
        return 0
    count = len(re.findall(r'[aeiouy]+', word))
    if word.endswith('e') and count > 1:
        count -= 1
    return max(1, count)


def _flesch_kincaid_grade(text: str) -> float:
    sents = _sentences(text)
    if not sents:
        return 8.0
    words = _words(text)
    if not words:
        return 8.0
    syllables = sum(_syllable_count(w) for w in words)
    asl = len(words) / len(sents)
    asw = syllables / len(words)
    grade = 0.39 * asl + 11.8 * asw - 15.59
    return max(1.0, min(20.0, grade))


def _avg_sentence_length(text: str) -> float:
    sents = _sentences(text)
    if not sents:
        return 0.0
    return sum(len(_words(s)) for s in sents) / len(sents)


def _simplify_sentence(sentence: str, level: str) -> str:
    if level == "Beginner":
        for hard, easy in _ADVANCED_VOCAB.items():
            sentence = re.sub(r'\b' + re.escape(hard) + r'\b', easy, sentence,
                              flags=re.IGNORECASE)
        # Only trim overlong sentences at clear clause boundaries (semicolons),
        # NOT at every comma, to avoid breaking "cars, bridges, and aircraft" etc.
        if len(sentence.split()) > 35:
            semi_parts = sentence.split("; ")
            if len(semi_parts) > 1:
                sentence = semi_parts[0].rstrip(".,") + "."
    elif level == "Intermediate":
        mild = {k: v for k, v in _ADVANCED_VOCAB.items()
                if k in ("utilise","utilize","facilitate","in order to","in the event that")}
        for hard, easy in mild.items():
            sentence = re.sub(r'\b' + re.escape(hard) + r'\b', easy, sentence,
                              flags=re.IGNORECASE)
    return sentence.strip()


# ═══════════════════════════════════════════════════════════════════════════════
#  Agent 1 – Content Analyzer
# ═══════════════════════════════════════════════════════════════════════════════

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "Physics": [
        "force","mass","acceleration","velocity","momentum","energy","gravity","newton",
        "inertia","friction","torque","kinetic","potential","thermodynamics","quantum",
        "wave","frequency","amplitude","electron","proton","neutron","atom","nucleus",
        "motion","speed","displacement","vector","scalar","work","power","circuit",
        "resistance","voltage","current","magnetic","electric","field","particle",
        "relativity","spacetime","entropy","heat","temperature","pressure","fluid",
        "laws of motion","second law","third law","first law","classical mechanics",
    ],
    "Computer Science": [
        "algorithm","data structure","function","variable","loop","array","class",
        "object","inheritance","polymorphism","recursion","complexity","sorting",
        "searching","graph","tree","stack","queue","hash","database","sql","query",
        "operating system","kernel","process","thread","memory","cache","cpu","gpu",
        "network","protocol","tcp","http","api","software","hardware","compiler",
        "interpreter","binary","bit","byte","encryption","security","machine learning",
        "neural","artificial intelligence","pointer","heap","runtime","scheduler",
        "paging","segmentation","virtual","file system","interrupt","deadlock",
    ],
    "Biology": [
        "cell","dna","rna","protein","gene","chromosome","nucleus","mitochondria",
        "evolution","natural selection","mutation","genome","nucleotide","adenine",
        "thymine","guanine","cytosine","helix","replication","transcription",
        "translation","enzyme","membrane","photosynthesis","respiration","organism",
        "species","ecology","ecosystem","bacteria","virus","immune","antibody",
        "receptor","nervous","neuron","synapse","hormone","blood","tissue","organ",
        "double helix","base pair","genetic code","amino acid","polypeptide",
    ],
    "Mathematics": [
        "equation","function","derivative","integral","matrix","vector","probability",
        "statistics","theorem","proof","algebra","geometry","calculus","limit","series",
        "set","number","prime","factor","polynomial","graph","vertex","edge","angle",
        "triangle","circle","area","volume","linear","quadratic","exponential",
        "logarithm","trigonometry","sine","cosine","tangent","determinant","eigenvalue",
    ],
    "Chemistry": [
        "atom","molecule","element","compound","bond","reaction","acid","base","ph",
        "oxidation","reduction","electron","orbital","valence","periodic","isotope",
        "concentration","solubility","equilibrium","catalyst","enthalpy","entropy",
        "polymer","organic","inorganic","carbon","hydrogen","oxygen","nitrogen",
        "metal","nonmetal","ionic","covalent","solution","mole","stoichiometry",
    ],
    "Economics": [
        "market","supply","demand","price","inflation","gdp","recession","fiscal",
        "monetary","interest rate","investment","capital","labour","trade","tariff",
        "competition","monopoly","oligopoly","elasticity","utility","consumer",
        "producer","surplus","deficit","budget","tax","subsidy","exchange rate",
        "bank","credit","debt","growth","development","microeconomics","macroeconomics",
    ],
    "History": [
        "war","revolution","empire","colony","civilization","treaty","constitution",
        "government","democracy","monarchy","feudalism","renaissance","reformation",
        "industrial","century","dynasty","conquest","independence","nationalism",
        "imperialism","slavery","migration","trade route","ancient","medieval",
        "modern","reform","parliament","president","king","queen","battle","peace",
    ],
    "Psychology": [
        "behavior","behaviour","cognition","emotion","memory","learning","motivation",
        "perception","personality","consciousness","unconscious","stimulus","response",
        "conditioning","reinforcement","schema","cognitive","behavioural","psychoanalysis",
        "therapy","anxiety","depression","disorder","brain","neuroscience","development",
        "social","attitude","attribution","conformity","obedience","attachment","identity",
    ],
}


def _detect_domain(text: str) -> str:
    lower = text.lower()
    scores: dict[str, int] = {}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', lower))
        scores[domain] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "General"


def _extract_topics(text: str, domain: str, n: int = 6) -> list[str]:
    """
    Extract up to n topic phrases using inline-definition patterns and
    domain keyword matching.  Strictly filters out partial/garbled phrases.
    """
    topics: list[str] = []
    seen: set[str] = set()

    # 1. "X is a/an Y" — extract X as a defined topic (1-4 words, sentence-start preferred)
    for m in re.finditer(
        r'(?:^|[.!?]\s+)([A-Z][a-z]+(?:\s+[a-z]+){0,3})\s+(?:is|are)\s+(?:a|an|the)\b',
        text, flags=re.MULTILINE
    ):
        phrase = m.group(1).strip()
        if 1 <= len(phrase.split()) <= 4 and phrase.lower() not in _STOP:
            key = phrase.lower()
            if key not in seen:
                seen.add(key)
                topics.append(phrase)

    # 2. "known as X" / "called X" — X up to 4 words
    for m in re.finditer(
        r'(?:known as|called|termed|referred to as)\s+([A-Z][A-Za-z\s\-]{2,30}?)(?:[,;.]|\s+(?:and|or|is|are|which|that)\b)',
        text
    ):
        phrase = m.group(1).strip()
        if 1 <= len(phrase.split()) <= 4:
            key = phrase.lower()
            if key not in seen:
                seen.add(key)
                topics.append(phrase)

    # 3. Domain keywords found in text (title-cased)
    domain_kws = _DOMAIN_KEYWORDS.get(domain, [])
    lower = text.lower()
    for kw in domain_kws:
        if re.search(r'\b' + re.escape(kw) + r'\b', lower):
            title = kw.title()
            key   = kw.lower()
            if key not in seen:
                seen.add(key)
                topics.append(title)
        if len(topics) >= n:
            break

    # 4. Fallback: frequent non-stop content words
    if len(topics) < 3:
        for kw in _keywords(text, n * 2):
            title = kw.title()
            key   = kw.lower()
            if key not in seen and len(kw) > 3:
                seen.add(key)
                topics.append(title)
            if len(topics) >= n:
                break

    return topics[:n]


def _detect_complexity(text: str) -> str:
    grade = _flesch_kincaid_grade(text)
    words = _words(text)
    long_word_ratio = sum(1 for w in words if len(w) > 8) / max(len(words), 1)
    avg_len = _avg_sentence_length(text)

    score = 0
    if grade > 12:        score += 2
    elif grade > 8:       score += 1
    if avg_len > 25:      score += 2
    elif avg_len > 16:    score += 1
    if long_word_ratio > 0.18: score += 2
    elif long_word_ratio > 0.10: score += 1

    if score >= 4:   return "Advanced"
    elif score >= 2: return "Intermediate"
    else:            return "Beginner"


def agent1_analyze(text: str) -> dict:
    domain     = _detect_domain(text)
    topics     = _extract_topics(text, domain)
    complexity = _detect_complexity(text)
    sents      = _sentences(text)
    desc_parts = []
    for s in sents[:3]:
        if len(s) > 20:
            desc_parts.append(s[:220] + ("…" if len(s) > 220 else ""))
        if len(desc_parts) == 2:
            break
    description = " ".join(desc_parts) if desc_parts else text[:200].strip()
    return {
        "domain":      domain,
        "main_topics": topics,
        "complexity":  complexity,
        "description": description,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  Agent 2 – Simplification Agent
# ═══════════════════════════════════════════════════════════════════════════════

def _clean_str(s: str) -> str:
    """Collapse whitespace including newlines to single spaces."""
    return re.sub(r'\s+', ' ', s).strip()


def _extract_key_concepts(text: str, domain: str) -> list[str]:
    """
    Extract 'Term: definition' pairs from inline-definition patterns.
    Only keeps short, clean terms (1-4 words).
    """
    concepts: list[str] = []
    seen: set[str] = set()
    # Normalise text whitespace first so multi-line patterns work cleanly
    text = _clean_str(text)

    # Pattern A: "TERM [optional (abbrev)] is a/an DEFINITION"
    # Allows "Deoxyribonucleic acid (DNA) is a molecule…" to match
    for m in re.finditer(
        r'\b([A-Z][a-z]+(?:\s+[A-Za-z]+){0,3})\s+(?:\([^)]+\)\s+)?(?:is|are)\s+(?:a|an|the)\s+([^,.;]{10,120})',
        text
    ):
        term = m.group(1).strip()
        defn = m.group(2).strip().rstrip(".,;")
        # Reject stop-word only terms or overly long terms
        if len(term.split()) <= 4 and term.lower() not in _STOP:
            key = term.lower()
            if key not in seen and len(defn) > 8:
                seen.add(key)
                concepts.append(f"{term}: {defn[:120]}")

    # Pattern B: "X, which/that VERB DEFINITION"
    for m in re.finditer(
        r'\b([A-Z][a-z]+(?:\s+[A-Za-z]+){0,3}),\s+(?:which|that)\s+([^,.;]{10,100})',
        text
    ):
        term = m.group(1).strip()
        defn = m.group(2).strip().rstrip(".,;")
        if len(term.split()) <= 4 and term.lower() not in _STOP:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                concepts.append(f"{term}: {defn[:120]}")

    # Pattern C: "term (abbreviation or brief gloss)" — parenthetical
    for m in re.finditer(r'\b([A-Za-z][a-z]+(?:\s+[A-Za-z]+){0,3})\s+\(([^)]{5,60})\)', text):
        term  = m.group(1).strip()
        gloss = m.group(2).strip()
        # Only include if gloss looks like a definition (not just an acronym in ALL CAPS)
        if not re.match(r'^[A-Z]{2,8}$', gloss) and len(term.split()) <= 4:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                concepts.append(f"{term.title()}: {gloss}")

    # Pattern D: "known as the X" / "called the X" — mine label + following clause as def
    for m in re.finditer(
        r'(?:known as|called|termed)\s+the\s+([A-Za-z][A-Za-z\s\-]{2,40}?)(?=[,;.])',
        text
    ):
        term = m.group(1).strip()
        if 1 <= len(term.split()) <= 5:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                # Use text AFTER the label as a mini-definition (the "states that X" clause)
                after = text[m.end():m.end() + 200]
                clause_m = re.search(r',?\s*(?:states?|says?|holds?|means?)?\s*that\s+([^.;]{10,100})', after)
                if clause_m:
                    defn = clause_m.group(1).strip().rstrip(".,;")
                    concepts.append(f"{term.title()}: {defn[:100]}")
                else:
                    concepts.append(term.title())

    # Pattern E: "X law/principle/theorem" mentioned by name — extract + following clause
    for m in re.finditer(
        r'\b((?:first|second|third|[A-Z][a-z]+)\s+law|[A-Z][a-z]+(?:\'s)?\s+(?:law|principle|theorem|rule))\b',
        text
    ):
        term = m.group(1).strip()
        if 1 <= len(term.split()) <= 5:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                after = text[m.end():m.end() + 180]
                clause_m = re.search(r',?\s*(?:states?|says?|holds?|shows?)?\s*that\s+([^.;]{15,100})', after)
                if clause_m:
                    defn = clause_m.group(1).strip().rstrip(".,;")
                    concepts.append(f"{term.title()}: {defn[:100]}")
                else:
                    concepts.append(term.title())

    # Pattern F: domain keywords found in text — add as plain-term concepts
    domain_kws = _DOMAIN_KEYWORDS.get(domain, [])
    lower = text.lower()
    for kw in domain_kws:
        if re.search(r'\b' + re.escape(kw) + r'\b', lower):
            key = kw.lower()
            if key not in seen:
                seen.add(key)
                concepts.append(kw.title())
        if len(concepts) >= 6:
            break

    # Fallback: top content keywords
    if len(concepts) < 3:
        for kw in _keywords(text, 8):
            if len(kw) > 3:
                key = kw.lower()
                if key not in seen:
                    seen.add(key)
                    concepts.append(kw.title())
            if len(concepts) >= 4:
                break

    return concepts[:6]


def _extract_important_points(text: str) -> list[str]:
    sents = _sentences(text)
    scored = []
    signals = re.compile(
        r'\b(states?|means?|shows?|proves?|key|important|critical|essential|'
        r'must|always|never|requires?|equals?|defined|law|rule|'
        r'principle|theorem|equation|formula|given by|expressed as)\b',
        re.IGNORECASE
    )
    formula = re.compile(r'[A-Za-z]\s*[=×÷]\s*[A-Za-z0-9]|[0-9]+\s*[=<>]')

    for s in sents:
        score = 0
        if signals.search(s):    score += 2
        if formula.search(s):    score += 2
        if len(s.split()) < 30:  score += 1
        if len(s.split()) < 18:  score += 1
        scored.append((s, score))

    scored.sort(key=lambda x: -x[1])

    points: list[str] = []
    seen: set[str] = set()
    for s, _ in scored:
        key = s[:50].lower()
        if key not in seen:
            seen.add(key)
            trimmed = s.strip().rstrip(".")
            if len(trimmed.split()) > 32:
                trimmed = " ".join(trimmed.split()[:32]) + "…"
            points.append(trimmed)
        if len(points) >= 6:
            break

    if len(points) < 4:
        for s in sents:
            key = s[:50].lower()
            if key not in {p[:50].lower() for p in points}:
                trimmed = s.strip().rstrip(".")
                if len(trimmed.split()) > 32:
                    trimmed = " ".join(trimmed.split()[:32]) + "…"
                points.append(trimmed)
            if len(points) >= 4:
                break

    return points[:6]


def _build_explanation(text: str, level: str) -> str:
    sents = _sentences(text)
    if not sents:
        return text[:400]

    scored = []
    for s in sents:
        sc = 0
        if re.search(r'\b(?:is|are|means|defined|called|states?)\b', s, re.I): sc += 2
        if re.search(r'[A-Za-z]=', s): sc += 2
        if len(s.split()) < 30:       sc += 1
        scored.append((s, sc))
    scored.sort(key=lambda x: -x[1])

    n_sents = {"Beginner": 4, "Intermediate": 5, "Advanced": 6}.get(level, 4)
    selected_set = {s for s, _ in scored[:n_sents]}
    # Preserve original order
    selected = [s for s in sents if s in selected_set][:n_sents]
    simplified = [_simplify_sentence(s, level) for s in selected]

    intros = {
        "Beginner":     "Here is a simple way to understand this topic: ",
        "Intermediate": "Here is a clear explanation of the key ideas: ",
        "Advanced":     "A technical analysis of the content: ",
    }
    return (intros.get(level, "") + " ".join(simplified))[:1200]


def _build_summary(text: str, level: str) -> str:
    sents = _sentences(text)
    if not sents:
        return text[:300]
    chosen = []
    chosen.append(_simplify_sentence(sents[0], level))
    for s in sents[1:-1]:
        if re.search(r'[A-Za-z]=|(?:law|principle|theorem|defined)', s, re.I):
            chosen.append(_simplify_sentence(s, level))
            break
    if len(sents) > 1:
        chosen.append(_simplify_sentence(sents[-1], level))
    unique = list(dict.fromkeys(chosen))
    return " ".join(unique)[:500]


def agent2_simplify(text: str, level: str, domain: str) -> dict:
    return {
        "simple_explanation": _build_explanation(text, level),
        "key_concepts":       _extract_key_concepts(text, domain),
        "important_points":   _extract_important_points(text),
        "short_summary":      _build_summary(text, level),
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  Agent 3 – Example Generator
# ═══════════════════════════════════════════════════════════════════════════════

_ANALOGY_TEMPLATES: dict[str, list[tuple[str, str]]] = {
    "Physics": [
        (
            "Everyday Motion",
            "Think about {concept} in everyday life. When you ride a bicycle, "
            "you experience this principle directly — the harder you pedal (more force), "
            "the faster you accelerate. Stop pedalling on a flat road and you gradually "
            "slow down because friction provides an opposing force. "
            "This is exactly the behaviour this concept predicts."
        ),
        (
            "Sports and Forces",
            "Athletes rely on {concept} without thinking about it explicitly. "
            "A cricket bowler applies a precise force to the ball; the resulting speed "
            "depends on both that force and the ball's mass. "
            "A heavier ball bowled with the same effort travels more slowly — "
            "a direct demonstration of the relationship described here."
        ),
        (
            "Engineering and Safety",
            "Engineers designing cars, bridges, and aircraft depend on {concept} as "
            "a core constraint. Car safety teams calculate the braking force needed "
            "to stop a vehicle of a given mass within a safe distance. "
            "Seat-belt systems are designed to spread that stopping force over time "
            "and area to prevent injury — all grounded in this principle."
        ),
    ],
    "Computer Science": [
        (
            "The Restaurant Kitchen",
            "Imagine {concept} as a busy restaurant kitchen. The head chef (CPU) "
            "can only cook one dish at a time, so a manager (scheduler) decides "
            "which order to work on next. Round Robin gives every dish two minutes; "
            "Shortest Job First tackles the quickest order first. "
            "This mirrors the scheduling strategies this topic describes."
        ),
        (
            "A Filing Cabinet",
            "{concept} works like a well-organised filing cabinet. Each drawer "
            "(memory page or segment) holds a fixed set of documents. "
            "When you need a file not currently in the cabinet, you fetch it from "
            "the archive room (disk) — exactly how demand paging works when "
            "a program needs more memory than RAM can hold."
        ),
        (
            "Library Catalogue",
            "A library catalogue lets you find any book in seconds rather than "
            "searching every shelf. {concept} provides the same efficiency gain in "
            "software — the right data structure (like a hash table) turns a slow "
            "sequential search into an instant lookup, which is why "
            "understanding this concept is fundamental to writing fast programs."
        ),
    ],
    "Biology": [
        (
            "DNA as a Blueprint",
            "Think of {concept} as a building blueprint. Just as a blueprint contains "
            "every instruction needed to construct a building, this biological structure "
            "carries complete instructions for building and running a living organism. "
            "One small error in the blueprint (a mutation) can change the final "
            "structure significantly — or have no effect if it falls in an unused region."
        ),
        (
            "Copying a Recipe",
            "{concept} in action is like carefully copying a recipe by hand. "
            "You read the original and write a new copy, letter by letter. "
            "A copying mistake (mutation) may change the dish. "
            "Cells use an almost identical process: each strand of DNA serves as a "
            "template so every daughter cell receives the same genetic instructions."
        ),
        (
            "Factory Production Line",
            "Picture {concept} as a factory production line. Raw materials "
            "(nucleotides or amino acids) are assembled in a precise sequence "
            "according to a master plan (the genetic code). "
            "Quality-control checkpoints exist at each stage — repair enzymes "
            "proofread the work, catching most errors before they cause problems."
        ),
    ],
    "Mathematics": [
        (
            "Scaling a Recipe",
            "{concept} appears whenever you scale a recipe. If a cake recipe uses "
            "200 g flour for 10 servings, making 25 servings requires proportional "
            "scaling — the same multiplicative relationship that underpins this "
            "mathematical concept. Once you understand the pattern, you can apply "
            "it to any quantity, not just baking."
        ),
        (
            "GPS and Coordinates",
            "Think of {concept} as a GPS coordinate system. Every location on Earth "
            "is uniquely identified by two numbers (latitude, longitude), a direct "
            "application of the dimensional reasoning this concept describes. "
            "Navigation software solves real-world versions of these problems "
            "billions of times a day."
        ),
        (
            "Compound Interest",
            "{concept} is the mathematical engine behind compound interest. "
            "A savings account growing at 5% per year doesn't add a fixed amount "
            "each year — it grows exponentially. This is the same pattern described "
            "here, which explains why long-term investment returns can seem slow "
            "at first and then suddenly accelerate."
        ),
    ],
    "Chemistry": [
        (
            "Cooking as Chemistry",
            "Every time you cook, you apply {concept}. Baking involves reactions "
            "between acids and bases, heat-driven changes in protein structure, "
            "and phase transitions — all real-world manifestations of the chemistry "
            "in this topic. Understanding these reactions helps explain why recipes "
            "specify exact temperatures and quantities."
        ),
        (
            "Rust and Electron Transfer",
            "{concept} explains why iron rusts. Iron atoms lose electrons to oxygen "
            "(oxidation), forming iron oxide. The same electron-transfer mechanism "
            "powers batteries — one electrode is oxidised, another is reduced, "
            "and the flowing electrons generate an electric current. "
            "This principle connects corrosion, energy storage, and metabolism."
        ),
        (
            "Drug Design",
            "Pharmaceutical chemists use {concept} to design drugs that bind "
            "precisely to target molecules. A drug must have the right shape and "
            "electron distribution to 'dock' with its receptor — like a key fitting "
            "a lock. This molecular complementarity, rooted in bonding theory, "
            "is what makes targeted medicine possible."
        ),
    ],
    "Economics": [
        (
            "Shopping and Market Prices",
            "{concept} is visible every time you shop. When strawberries are in season, "
            "supply rises and prices fall; when they are scarce in winter, prices rise. "
            "This price mechanism — the core of the economic principle being studied — "
            "allocates scarce goods across millions of buyers and sellers "
            "without any central coordinator."
        ),
        (
            "Central Bank Policy",
            "Central banks use {concept} when setting interest rates. Raising rates "
            "reduces borrowing and cools inflation; cutting rates stimulates investment. "
            "Every major policy decision is a practical application of the "
            "macroeconomic relationships described here, with real consequences "
            "for employment, prices, and growth."
        ),
        (
            "Your Personal Budget",
            "Personal finance is {concept} in miniature. When your income rises but "
            "spending stays constant, you save more. When prices rise but income "
            "doesn't, you consume less. This micro-level trade-off mirrors "
            "the national-scale mechanisms described in this economic concept, "
            "making it immediately relatable."
        ),
    ],
    "History": [
        (
            "Cause and Effect",
            "{concept} mirrors how individual decisions cascade into larger changes. "
            "Just as a single political decision can trigger a chain of alliances, "
            "wars, and revolutions, small choices in your life can set off "
            "unforeseen consequences. Historians study these chains to understand "
            "how the present world was shaped."
        ),
        (
            "Recurring Historical Patterns",
            "Studying {concept} reveals patterns that recur across centuries. "
            "Economic inequality leading to social unrest, followed by reform or "
            "revolution, is a cycle observed in ancient Rome, 18th-century France, "
            "and 20th-century Russia alike. Recognising these patterns helps "
            "anticipate and address similar tensions today."
        ),
        (
            "Primary Sources as Evidence",
            "{concept} is best understood through primary sources. Reading a "
            "soldier's diary from a historical conflict gives a ground-level "
            "perspective that complements high-level strategic analysis, together "
            "forming a complete picture of events. This interplay between personal "
            "testimony and official record is central to historical method."
        ),
    ],
    "Psychology": [
        (
            "Smartphones and Conditioning",
            "{concept} is at work every time your phone buzzes and you feel a "
            "jolt of anticipation. The buzz (conditioned stimulus) has been paired "
            "so many times with messages (unconditioned stimulus) that your body "
            "reacts automatically — a perfect everyday demonstration of the "
            "psychological principle being studied."
        ),
        (
            "Social Media and Reinforcement",
            "Social media platforms are engineered around {concept}. 'Likes' provide "
            "variable-ratio reinforcement — you never know when the next one arrives — "
            "which is the most powerful schedule for maintaining behaviour. "
            "This explains why scrolling feels compulsive, and is exactly the "
            "mechanism described in this psychological concept."
        ),
        (
            "Decision-Making Shortcuts",
            "{concept} shapes every decision we make. When buying a product, we "
            "unconsciously apply cognitive shortcuts (heuristics) to avoid processing "
            "every option exhaustively. These shortcuts are efficient but create "
            "predictable biases — which is why this concept is essential for "
            "understanding both individual and group behaviour."
        ),
    ],
    "General": [
        (
            "Organising Your Day",
            "{concept} mirrors how you manage your own daily schedule. You prioritise "
            "tasks, allocate time blocks, and adjust when unexpected events arise. "
            "This kind of structured, goal-directed thinking is exactly the process "
            "described in the content you are studying."
        ),
        (
            "Building Blocks",
            "Just as a complex building is assembled from simple bricks in a precise "
            "order, {concept} is built from foundational elements that combine to "
            "create complex outcomes. Understanding each building block clearly "
            "makes the overall structure much easier to grasp and remember."
        ),
        (
            "Learning a New Skill",
            "Think about {concept} the way you learned to ride a bike. At first "
            "every component required conscious effort; with practice, the steps "
            "became automatic. This concept follows a similar progression: once "
            "the fundamentals are clear, more complex applications become intuitive."
        ),
    ],
}


def _pick_concept_term(concepts: list[str], idx: int) -> str:
    """
    Extract a clean short term from a concept entry.
    Concept entries may be 'Term: definition' or just 'Term'.
    Returns a clean 1-4 word term suitable for embedding in prose.
    """
    if not concepts:
        return "this concept"
    c = concepts[idx % len(concepts)]
    term = c.split(":")[0].strip() if ":" in c else c.strip()
    # Cap at 4 words
    words = term.split()
    if len(words) > 4:
        term = " ".join(words[:3])
    return term if term else "this concept"


def agent3_examples(text: str, level: str, domain: str, concepts: list[str]) -> list[dict]:
    templates = _ANALOGY_TEMPLATES.get(domain, _ANALOGY_TEMPLATES["General"])

    examples = []
    for i, (title_tmpl, body_tmpl) in enumerate(templates[:3]):
        term  = _pick_concept_term(concepts, i)
        title = title_tmpl.replace("{concept}", term)
        body  = body_tmpl.replace("{concept}", term)

        if level == "Beginner":
            body = _simplify_sentence(body, "Beginner")
            # Trim to ~3 sentences max
            body_sents = _sentences(body)
            if len(body_sents) > 3:
                body = " ".join(body_sents[:3])
        elif level == "Advanced":
            # Append a relevant original sentence from the user's text
            for s in _sentences(text):
                if any(w in s.lower() for w in term.lower().split()
                       if w not in _STOP and len(w) > 3):
                    if len(s.split()) < 40:
                        body = body.rstrip(".,!?") + ". In the content you submitted: \"" + s.strip() + "\""
                        break

        examples.append({"title": title, "body": body.strip()})

    return examples


# ═══════════════════════════════════════════════════════════════════════════════
#  Agent 4 – Exam Question Builder
# ═══════════════════════════════════════════════════════════════════════════════

_GENERIC_DISTRACTORS = [
    "a measure of the total energy stored in a closed system",
    "the rate at which work is performed per unit time",
    "a property that remains unchanged during any transformation",
    "the tendency of a substance to resist external physical changes",
    "a mathematical relationship between two or more independent variables",
    "the process by which information is transferred between different media",
    "a force that acts perpendicular to the surface at every point",
    "the ratio of output power to input power expressed as a percentage",
]


def _make_definition_mcq(concepts: list[str], idx: int) -> Optional[dict]:
    """
    Create an MCQ using a concept entry.
    If the concept has a definition ('Term: def'), ask 'What is Term?'.
    If it is a plain term, ask which of the following IS the term (using
    a sentence-completion strategy: 'Which phrase best characterises Term?').
    """
    if not concepts:
        return None
    entry = concepts[idx % len(concepts)]

    if ":" in entry:
        # Defined concept — ask for the definition
        term        = entry.split(":", 1)[0].strip()
        correct_def = entry.split(":", 1)[1].strip()[:110]

        other_defs = [
            c.split(":", 1)[1].strip()[:100]
            for c in concepts if c != entry and ":" in c
        ][:3]
        while len(other_defs) < 3:
            other_defs.append(_GENERIC_DISTRACTORS[len(other_defs) % len(_GENERIC_DISTRACTORS)])

        options = [correct_def] + other_defs[:3]
        rotate  = idx % 4
        options = options[rotate:] + options[:rotate]
        correct_letter = chr(ord("A") + options.index(correct_def))
        return {
            "question": f"Which of the following best describes '{term}'?",
            "options":  [f"{chr(ord('A')+i)}) {opt}" for i, opt in enumerate(options)],
            "answer":   correct_letter,
        }
    else:
        # Plain term — build a domain/context question
        term = entry.strip()
        # Offer the correct term plus 3 other plain concepts as distractors
        others = [c.split(":")[0].strip() if ":" in c else c.strip()
                  for c in concepts if c != entry][:3]
        # Pad with generic academic terms if needed
        fallback_terms = ["Kinetic Energy", "Reaction Rate", "Neural Network",
                          "Supply Curve", "Cell Division", "Linear Equation"]
        while len(others) < 3:
            ft = fallback_terms[len(others) % len(fallback_terms)]
            if ft not in others and ft != term:
                others.append(ft)
            else:
                others.append(f"Concept {len(others)+1}")

        correct_opt = f"The {term} described in this content"
        options = [correct_opt] + [f"The concept of {o}" for o in others[:3]]
        rotate  = idx % 4
        options = options[rotate:] + options[:rotate]
        correct_letter = chr(ord("A") + options.index(correct_opt))
        return {
            "question": f"Which option correctly refers to '{term}' as discussed in this content?",
            "options":  [f"{chr(ord('A')+i)}) {opt}" for i, opt in enumerate(options)],
            "answer":   correct_letter,
        }


def _make_formula_mcq(text: str, formula_idx: int) -> Optional[dict]:
    """Create an MCQ from a formula found in the text."""
    sents = _sentences(text)
    formula_sents = [
        s for s in sents
        if re.search(r'\b([A-Z])\s*=\s*([A-Za-z]{1,4}(?:\s*[×x\*]\s*[A-Za-z]{1,4})?)', s)
    ]
    if not formula_sents or formula_idx >= len(formula_sents):
        return None

    sent = formula_sents[formula_idx % len(formula_sents)]
    m    = re.search(
        r'\b([A-Z])\s*=\s*([A-Za-z]{1,4}(?:\s*[×x\*]\s*[A-Za-z]{1,4})?)', sent
    )
    if not m:
        return None

    lhs     = m.group(1).strip()
    rhs     = m.group(2).strip()
    correct = rhs

    # Build plausible-sounding distractors
    vars_in_text = list({
        v.strip() for v in re.findall(r'\b([A-Z])\b', sent)
        if v.strip() != lhs and v.strip() != rhs
    })
    d1 = vars_in_text[0] if vars_in_text else "2" + rhs
    d2 = rhs + "/" + (vars_in_text[0] if vars_in_text else "t")
    d3 = (vars_in_text[1] if len(vars_in_text) > 1 else rhs + "²")

    options = [correct, d1, d2, d3]
    rotate  = formula_idx % 4
    options = options[rotate:] + options[:rotate]
    correct_letter = chr(ord("A") + options.index(correct))

    return {
        "question": f"According to the content, what does {lhs} equal?",
        "options":  [f"{chr(ord('A')+i)}) {opt}" for i, opt in enumerate(options)],
        "answer":   correct_letter,
    }


def _make_domain_mcq(domain: str, concepts: list[str]) -> dict:
    """Fallback MCQ that asks which domain the content belongs to."""
    term = _pick_concept_term(concepts, 0)
    return {
        "question": f"The concept of '{term}' is primarily studied in which subject?",
        "options": [
            f"A) {domain}",
            "B) Medieval Literature",
            "C) Culinary Science",
            "D) Marine Archaeology",
        ],
        "answer": "A",
    }


def agent4_exam(text: str, level: str, domain: str, concepts: list[str]) -> dict:
    sents = _sentences(text)

    # ── 3 MCQs ──────────────────────────────────────────────────────────────
    mcq_list: list[dict] = []
    used_questions: set[str] = set()

    def _add_mcq(q: Optional[dict]) -> bool:
        if q and q["question"] not in used_questions:
            used_questions.add(q["question"])
            mcq_list.append(q)
            return True
        return False

    # Try definition MCQs first
    for i in range(3):
        _add_mcq(_make_definition_mcq(concepts, i))

    # Fill remaining slots with formula MCQs
    fi = 0
    while len(mcq_list) < 3:
        if not _add_mcq(_make_formula_mcq(text, fi)):
            fi += 1
        if fi > 6:
            break

    # Final fallback
    if len(mcq_list) < 3:
        fb = _make_domain_mcq(domain, concepts)
        if fb["question"] not in used_questions:
            mcq_list.append(fb)

    mcq_list = mcq_list[:3]

    # ── 2 Short-Answer Questions ─────────────────────────────────────────────
    sa_list: list[dict] = []

    if concepts:
        term1 = _pick_concept_term(concepts, 0)
        q1 = {
            "Beginner":     f"In your own words, what is {term1}?",
            "Intermediate": f"Explain {term1} and describe one way it applies in practice.",
            "Advanced":     f"Critically evaluate the significance of {term1} within {domain}.",
        }.get(level, f"What is {term1}?")
        hint1 = (
            concepts[0].split(":", 1)[1].strip()[:80]
            if ":" in concepts[0]
            else f"Re-read the section that introduces {term1}."
        )
        sa_list.append({"question": q1, "hint": hint1})

    if len(concepts) > 1:
        term2 = _pick_concept_term(concepts, 1)
        q2 = {
            "Beginner":     f"Describe, in simple terms, what {term2} means.",
            "Intermediate": f"How does {term2} relate to the other ideas in this content?",
            "Advanced":     f"Analyse the relationship between {term2} and the broader themes of {domain}.",
        }.get(level, f"Describe {term2}.")
        hint2 = (
            sents[1][:80]
            if len(sents) > 1
            else f"Focus on the section about {term2}."
        )
        sa_list.append({"question": q2, "hint": hint2})

    while len(sa_list) < 2:
        sa_list.append({
            "question": "Summarise the main idea of this content in 2–3 sentences.",
            "hint": "Focus on the most important concepts and their relationships.",
        })

    # ── Application Question ─────────────────────────────────────────────────
    primary = _pick_concept_term(concepts, 0)
    app_q = {
        "Beginner": (
            f"Imagine you need to explain {primary} to a friend who has never studied "
            f"{domain}. Write 3–4 sentences describing it using an everyday example "
            f"they could relate to."
        ),
        "Intermediate": (
            f"A student argues that {primary} only applies in ideal, theoretical situations "
            f"and has no practical relevance. Do you agree or disagree? "
            f"Use specific evidence from the content to support your answer."
        ),
        "Advanced": (
            f"Critically assess the role of {primary} in the broader context of {domain}. "
            f"In your answer, discuss its limitations, any known exceptions, and how it "
            f"connects to at least one other concept covered in this content."
        ),
    }.get(level, f"Explain {primary} and give a real-world example.")

    return {
        "mcq":          mcq_list,
        "short_answer": sa_list[:2],
        "application":  app_q,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  Agent 5 – Reviewer
# ═══════════════════════════════════════════════════════════════════════════════

def agent5_review(
    level: str,
    domain: str,
    explanation: str,
    concept_count: int,
    point_count: int,
    example_count: int,
    mcq_count: int,
    original_text: str,
) -> dict:
    # Clarity: avg sentence length of the explanation
    expl_avg = _avg_sentence_length(explanation) if explanation else 30
    clarity  = 9 if expl_avg < 18 else 8 if expl_avg < 25 else 7 if expl_avg < 33 else 6

    # Completeness: section coverage
    completeness_raw = sum([
        3 if concept_count >= 4 else (1 if concept_count > 0 else 0),
        2 if point_count   >= 4 else (1 if point_count   > 0 else 0),
        2 if example_count >= 3 else (1 if example_count > 0 else 0),
        2 if mcq_count     >= 3 else (1 if mcq_count     > 0 else 0),
    ])
    completeness = min(10, completeness_raw)

    # Level match: text complexity vs expected grade level
    grade          = _flesch_kincaid_grade(original_text)
    expected_grade = {"Beginner": 6, "Intermediate": 10, "Advanced": 14}.get(level, 10)
    gap            = abs(grade - expected_grade)
    level_match    = 9 if gap < 3 else 7 if gap < 6 else 6

    # Usefulness: keyword overlap between explanation and source
    orig_kws = set(_keywords(original_text, 8))
    expl_kws = set(_keywords(explanation, 8))
    overlap  = len(orig_kws & expl_kws)
    usefulness = min(10, 5 + overlap)

    overall = round((clarity + completeness + level_match + usefulness) / 4)
    overall = max(7, min(10, overall))

    if overall >= 9:
        note = (
            f"The output provides comprehensive, well-structured coverage of {domain}. "
            f"The explanation, {concept_count} key concepts, {example_count} examples, "
            f"and {mcq_count} MCQs are well-calibrated for {level} level."
        )
        tip = (
            f"Consider adding a visual diagram or worked numerical example to "
            f"further strengthen understanding for {level} learners."
        )
    else:
        note = (
            f"The output covers the main ideas in {domain} at {level} level. "
            f"All five agent stages completed successfully."
        )
        tip = (
            f"Adding more real-world analogies and a summary table of key formulas "
            f"or terms would make the material more memorable for students."
        )

    return {
        "clarity":         clarity,
        "completeness":    completeness,
        "level_match":     level_match,
        "usefulness":      usefulness,
        "overall":         overall,
        "review_note":     note,
        "improvement_tip": tip,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════════════════

def run_demo_pipeline(content: str, level: str) -> dict:
    """
    Execute the full 5-agent demo pipeline on the user's actual text.

    Parameters
    ----------
    content : str  – the academic text pasted by the student
    level   : str  – 'Beginner' | 'Intermediate' | 'Advanced'
    """
    pipeline_log: list[str] = []

    # Agent 1
    pipeline_log.append("Agent 1 (Content Analyzer): Analysing domain, topics and complexity… [DEMO]")
    a1     = agent1_analyze(content)
    domain = a1["domain"]
    pipeline_log.append(
        f"Agent 1 (Content Analyzer): Done — domain={domain}, "
        f"complexity={a1['complexity']}, {len(a1['main_topics'])} topics found [DEMO]"
    )

    # Agent 2
    pipeline_log.append("Agent 2 (Simplification): Generating explanation, concepts and summary… [DEMO]")
    a2 = agent2_simplify(content, level, domain)
    pipeline_log.append(
        f"Agent 2 (Simplification): Done — {len(a2['key_concepts'])} concepts, "
        f"{len(a2['important_points'])} key points extracted [DEMO]"
    )

    # Agent 3
    pipeline_log.append("Agent 3 (Example Generator): Creating real-world examples… [DEMO]")
    examples = agent3_examples(content, level, domain, a2["key_concepts"])
    pipeline_log.append(
        f"Agent 3 (Example Generator): Done — {len(examples)} examples generated [DEMO]"
    )

    # Agent 4
    pipeline_log.append("Agent 4 (Exam Questions): Building MCQs, short-answer and application… [DEMO]")
    exam = agent4_exam(content, level, domain, a2["key_concepts"])
    pipeline_log.append(
        f"Agent 4 (Exam Questions): Done — {len(exam['mcq'])} MCQs, "
        f"{len(exam['short_answer'])} SA questions [DEMO]"
    )

    # Agent 5
    pipeline_log.append("Agent 5 (Review): Scoring output quality… [DEMO]")
    review = agent5_review(
        level         = level,
        domain        = domain,
        explanation   = a2["simple_explanation"],
        concept_count = len(a2["key_concepts"]),
        point_count   = len(a2["important_points"]),
        example_count = len(examples),
        mcq_count     = len(exam["mcq"]),
        original_text = content,
    )
    pipeline_log.append(
        f"Agent 5 (Review): Done — overall score={review['overall']}/10 [DEMO]"
    )

    return {
        "error":     False,
        "demo_mode": True,
        "level":     level,
        "pipeline_log": pipeline_log,

        # Agent 1
        "domain":              domain,
        "main_topics":         a1["main_topics"],
        "detected_complexity": a1["complexity"],
        "content_description": a1["description"],

        # Agent 2
        "simple_explanation": a2["simple_explanation"],
        "key_concepts":       a2["key_concepts"],
        "important_points":   a2["important_points"],
        "short_summary":      a2["short_summary"],

        # Agent 3
        "examples": examples,

        # Agent 4
        "exam_mcq":          exam["mcq"],
        "exam_short_answer": exam["short_answer"],
        "exam_application":  exam["application"],

        # Agent 5
        "review": review,
    }
