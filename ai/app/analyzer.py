
import logging
import re

from .model_predictor import predict_answer_quality
from .schemas import AnalyzeRequest, AnalysisResponse

logger = logging.getLogger(__name__)


# Each topic has concepts to look for, common alternative wording,
# and recommendations relevant to that topic.
TOPICS = [
    {
        "name": "stack and heap memory",
        "match": ["stack", "heap", "memory allocation"],
        "concepts": [
            ("stack memory", ["stack memory", "call stack", "stack frame", "local variables"]),
            ("heap allocation", ["heap memory", "heap allocation", "dynamically allocated"]),
            ("lifetime and management", ["garbage collection", "garbage-collected", "deallocation", "lifetime"]),
            ("access and performance", ["stack is faster", "faster access", "allocation overhead"]),
        ],
        "recommendations": [
            "Explain stack frames and function calls",
            "Review heap allocation and garbage collection",
        ],
    },
    {
        "name": "Python 2 versus Python 3",
        "match": ["python 2", "python 3", "differences between python"],
        "concepts": [
            ("print function", ["print()", "print function"]),
            ("division behavior", ["true division", "integer division", "floor division"]),
            ("string and Unicode behavior", ["unicode", "utf-8", "bytes", "string"]),
            ("Python 2 end of life", ["end-of-life", "end of life", "unsupported", "2020"]),
        ],
        "recommendations": [
            "Review Python 3 division and string behavior",
            "Practice a short Python 2 versus Python 3 comparison",
        ],
    },
    {
        "name": "SQL versus NoSQL",
        "match": ["sql and nosql", "sql vs nosql", "sql or nosql", "relational and non-relational"],
        "concepts": [
            ("relational tables", ["relational", "tables", "rows and columns"]),
            ("schema flexibility", ["schema", "flexible schema", "document model"]),
            ("relationships and queries", ["joins", "relationships", "sql queries"]),
            ("scaling and trade-offs", ["horizontal scaling", "vertical scaling", "trade-off", "consistency"]),
        ],
        "recommendations": [
            "Compare relational and document data models",
            "Explain when SQL or NoSQL is the better fit",
        ],
    },
    {
        "name": "array versus linked list",
        "match": ["array and linked list", "array vs linked list", "array or linked list"],
        "concepts": [
            ("memory layout", ["contiguous", "non-contiguous", "memory locations"]),
            ("access complexity", ["random access", "o(1)", "o(n)", "sequential access"]),
            ("insertion and deletion", ["insertion", "deletion", "insertions", "deletions"]),
            ("memory overhead", ["pointers", "pointer", "node overhead", "extra memory"]),
        ],
        "recommendations": [
            "Practice array and linked-list time complexities",
            "Compare insertion, deletion, and access costs",
        ],
    },
    {
        "name": "binary search tree versus hash table",
        "match": ["binary search tree", "hash table", "bst vs hash"],
        "concepts": [
            ("tree ordering", ["ordered", "sorted", "inorder traversal", "range query"]),
            ("hashing", ["hash function", "hashing", "hash collision"]),
            ("lookup complexity", ["o(log n)", "o(1)", "average time", "worst case"]),
            ("trade-offs", ["ordering", "range queries", "collision handling"]),
        ],
        "recommendations": [
            "Review hash collisions and average versus worst-case lookup",
            "Practice BST traversal and balancing",
        ],
    },
    {
        "name": "sorting algorithms",
        "match": ["sorting algorithm", "sorting algorithms", "sort an array"],
        "concepts": [
            ("time complexity", ["time complexity", "o(n log n)", "o(n^2)", "o(n2)"]),
            ("space complexity", ["space complexity", "in-place", "auxiliary space"]),
            ("stability", ["stable sort", "stability"]),
            ("algorithm trade-offs", ["merge sort", "quick sort", "heap sort", "insertion sort"]),
        ],
        "recommendations": [
            "Compare merge sort, quicksort, and insertion sort",
            "Review stability, auxiliary space, and worst-case complexity",
        ],
    },
    {
        "name": "monolith versus microservices",
        "match": ["monolithic", "microservices", "microservice architecture"],
        "concepts": [
            ("deployment structure", ["single deployment", "independent deployment", "independently deploy"]),
            ("scaling", ["scale independently", "independent scaling", "horizontal scaling"]),
            ("operational complexity", ["operational complexity", "distributed systems", "network latency"]),
            ("data and failure trade-offs", ["service failure", "distributed transaction", "data consistency"]),
        ],
        "recommendations": [
            "Compare deployment and scaling requirements",
            "Review service communication and distributed-system failure modes",
        ],
    },
]

def contains_term(text: str, term: str) -> bool:
    """Match phrases and common singular/plural variations."""
    words = term.lower().split()
    patterns = []

    for word in words:
        escaped = re.escape(word)

        if word.endswith("s") and len(word) > 3:
            patterns.append(f"(?:{escaped}|{re.escape(word[:-1])})")
        else:
            patterns.append(f"{escaped}s?")

    pattern = r"(?<!\w)" + r"\s+".join(patterns) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None

def detect_topic(question: str):
    text = question.lower()
    for topic in TOPICS:
        if any(contains_term(text, phrase) for phrase in topic["match"]):
            return topic
    return None


def unique(items):
    return list(dict.fromkeys(items))


def deterministic_analysis(request: AnalyzeRequest) -> AnalysisResponse:
    question = request.question.strip()
    answer = request.answer.strip()
    answer_lower = answer.lower()
    words = re.findall(r"\b[\w+#.-]+\b", answer_lower)
    word_count = len(words)

    topic = detect_topic(question)
    detected = []
    missing = []
    recommendations = []

    if topic:
        for label, aliases in topic["concepts"]:
            if any(contains_term(answer_lower, alias) for alias in aliases):
                detected.append(label)
            else:
                missing.append(label)

        coverage = round(100 * len(detected) / len(topic["concepts"]))
        recommendations = [
            topic["recommendations"][0 if missing else 1]
        ] if topic["recommendations"] else []

        # This is a heuristic based on topic-concept overlap, not a
        # trained or validated measure of true technical correctness.
        relevance = min(95, max(20, round(35 + coverage * 0.60)))
        source = "deterministic-topic-rules"
    else:
        # Do not invent topic-specific missing concepts when the question
        # does not match a supported topic.
        coverage = 0
        relevance = 0
        source = "deterministic-unknown-topic"
        missing = [
            "Expected concepts could not be identified automatically for this question"
        ]
        recommendations = [
            "Review this answer against the question's expected answer or reference rubric"
        ]

    sentence_count = len([part for part in re.split(r"[.!?]+", answer) if part.strip()])
    has_explanation = any(
        phrase in answer_lower
        for phrase in ["because", "whereas", "however", "for example", "therefore", "which means"]
    )
    has_comparison = any(
        phrase in answer_lower
        for phrase in ["whereas", "while", "compared with", "in contrast", "on the other hand"]
    )

    structure = min(
        95,
        35 + min(word_count, 50) + (10 if sentence_count >= 2 else 0)
        + (10 if has_explanation else 0),
    )
    communication = min(
        95,
        45 + min(word_count, 40) + (10 if sentence_count >= 2 else 0),
    )

    strengths = []
    weaknesses = []

    if word_count >= 12:
        strengths.append("Provides a developed response")
    else:
        weaknesses.append("Add more explanation and technical detail")

    if has_explanation:
        strengths.append("Includes explanatory reasoning")
    else:
        weaknesses.append("Explain why the stated differences or properties matter")

    if has_comparison:
        strengths.append("Uses comparative reasoning")

    if topic and detected:
        strengths.append("Addresses recognized concepts for this question")

    if topic and missing:
        weaknesses.append("Some expected topic concepts were not detected")

    if not strengths:
        strengths.append("Answer was received and analyzed")

    if not weaknesses:
        weaknesses.append("Check the answer against edge cases and a reference rubric")

    return AnalysisResponse(
        technical_relevance=relevance,
        concept_coverage=coverage,
        answer_structure=structure,
        communication=communication,
        detected=detected or (["No expected concepts recognized"] if topic else []),
        missing=missing,
        strengths=unique(strengths),
        weaknesses=unique(weaknesses),
        recommendations=unique(recommendations),
        source=source,
    )


async def analyze_answer(request: AnalyzeRequest) -> AnalysisResponse:
    # This version intentionally uses the topic-aware fallback. The existing
    # hosted-analysis implementation can be reintroduced after separate testing.
    result = deterministic_analysis(request)

    # Keep the existing ML prediction separate from rubric-style feedback.
    try:
        score = predict_answer_quality(request.answer)
    except Exception as error:
        logger.warning("Experimental ML prediction unavailable: %s", error)
        score = None

    return result.model_copy(
        update={"predicted_answer_quality_score": score}
    )
