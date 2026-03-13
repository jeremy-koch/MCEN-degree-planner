"""
prereqs.py
==========
Prerequisite and corequisite rules for enrollment prediction.

This file is intentionally kept separate from the pipeline code so that
rules can be updated (e.g. for a new department) without touching the
modeling logic.

Data structure
--------------
Both PREREQ_RULES and COREQ_RULES use the same format:

    'COURSE': [group1, group2, ...]

Each group is a list of course codes. The requirement is satisfied when
AT LEAST ONE course in the group has been completed (prereqs) or
completed/in-progress (coreqs). ALL groups must be satisfied.

Single-course requirements are written as a one-element list: ['MCEN1025']

Examples:
    # Requires PHYS1110 AND (APPM1360 OR MATH2300)
    'MCEN2023': [['APPM1360', 'MATH2300'], ['PHYS1110']],

    # Requires only MCEN1025
    'MCEN3025': [['MCEN1025'], ...]

Bare strings are also accepted as a convenience shorthand for a
one-element group — the loader normalizes them automatically.
"""

# ---------------------------------------------------------------------------
# TARGET COURSES
# ---------------------------------------------------------------------------
# The courses we are trying to predict enrollment for.
# Use the full [4-letter][4-digit] identifier.

TARGET_COURSES = [
    'MCEN1024', 'MCEN1025', 'MCEN1030', 'MCEN2000', 'MCEN2023',
    'MCEN2024', 'MCEN2043', 'MCEN2063', 'MCEN3012', 'MCEN3017',
    'MCEN3021', 'MCEN3022', 'MCEN3025', 'MCEN3030', 'MCEN3032',
    'MCEN3047', 'MCEN4026', 'MCEN4043', 'MCEN4045', 'MCEN4085',
]

# ---------------------------------------------------------------------------
# SEMESTER OFFERING CONSTRAINTS
# ---------------------------------------------------------------------------

FALL_ONLY_COURSES   = {'MCEN4045'}
SPRING_ONLY_COURSES = {'MCEN4085'}

# Courses requiring Senior class level (4 or 5) for eligibility.
# Used in is_eligible() to further restrict the pool.
SENIOR_REQUIRED = {'MCEN4045'}

# Courses with limited history: {course_code: first_term_offered_as_Season_YYYY}
NEW_COURSES = {
    'MCEN1030': 'Fall 2024',
    'MCEN3017': 'Fall 2023',
}

# ---------------------------------------------------------------------------
# PREREQUISITE RULES
# ---------------------------------------------------------------------------
# Must be satisfied by COMPLETED courses only (prior terms).
# Omitting early APPM courses intentionally — many students place directly
# into Calc 3, so enforcing lower APPM prereqs would exclude valid students.

PREREQ_RULES = {
    'MCEN2023': [
        ['APPM1360', 'MATH2300'],
        ['PHYS1110'],
    ],
    'MCEN2024': [
        ['MCEN1024', 'CHEN1211', 'CHEM1113', 'CHEN1201'],
        ['PHYS1110'],
    ],
    'MCEN2043': [
        ['MCEN2023', 'CVEN2121', 'GEEN2851', 'ASEN2701'],
        ['APPM1360', 'MATH2300'],
    ],
    'MCEN2063': [
        ['MCEN2023', 'CVEN2121', 'GEEN2851', 'ASEN2001', 'ASEN2701'],
        ['APPM1360', 'MATH2300'],
    ],
    'MCEN3012': [
        ['APPM1360', 'MATH2300'],
    ],
    'MCEN3017': [
        ['PHYS1120'],
    ],
    'MCEN3021': [
        ['MCEN2023', 'CVEN2121', 'GEEN2851', 'ASEN2001', 'ASEN2701', 'CHEN2120'],
        ['APPM2350', 'MATH2400'],
    ],
    'MCEN3022': [
        ['MCEN3012', 'AREN2110', 'GEEN3852', 'EVEN3012'],
        ['MCEN3021', 'CVEN3313'],
        ['APPM2360', 'APPM3310', 'MATH3430'],
    ],
    'MCEN3025': [
        ['MCEN1025'],
        ['MCEN2024', 'GEEN3024', 'ASEN1022'],
        ['MCEN2063', 'CVEN3161'],
    ],
    'MCEN3030': [
        ['APPM2360', 'MATH3430', 'APPM3310'],
        ['MCEN1030', 'CSCI1300', 'CSCI1310', 'CSCI1320', 'ECEN1310', 'ASEN1320'],
    ],
    'MCEN3032': [
        ['MCEN3012', 'GEEN3852', 'AREN2110', 'EVEN3012', 'CHEN2120'],
        ['MCEN3021', 'CHEN3200', 'CVEN3313'],
        ['APPM2360', 'MATH3430', 'APPM3310'],
    ],
    'MCEN3047': [
        ['PHYS1140'],
    ],
    'MCEN4026': [
        ['MCEN2024', 'GEEN3024', 'ASEN1022'],
    ],
    'MCEN4043': [
        ['MCEN2043', 'CVEN3111'],
        ['ECEN3010', 'ECEN2270', 'GEEN3010', 'MCEN3017'],
    ],
    'MCEN4045': [
        ['GEEN1400', 'GEEN2400', 'GEEN3400'],
        ['MCEN2000'],
        ['MCEN3012'],
        ['MCEN3021'],
        ['MCEN3025'],
        ['MCEN3030'],
        ['MCEN3022', 'MCEN4043', 'MCEN3047'],
    ],
    'MCEN4085': [
        ['MCEN4045'],
    ],
}

# ---------------------------------------------------------------------------
# COREQUISITE RULES
# ---------------------------------------------------------------------------
# Satisfied by COMPLETED or IN-PROGRESS courses (current term counts).

# MCEN4045 corequisites intentionally omitted: students routinely complete
# 4026, 3022, 4043, 3047 in prior semesters rather than simultaneously,
# and the in-progress check at prediction time excludes unknown future
# enrollments. Eligibility for 4045 is instead gated by prerequisites
# plus Senior class level (see SENIOR_REQUIRED below).
COREQ_RULES = {
    'MCEN3017': [
        ['APPM2360', 'APPM3310', 'MATH3430'],
    ],
    'MCEN3047': [
        ['ECEN3010', 'ECEN2270', 'GEEN3010', 'MCEN3017'],
        ['MCEN3030', 'APPM4650', 'APPM4600', 'CSCI3656'],
    ],
    'MCEN4043': [
        ['MCEN3030', 'APPM4650', 'APPM4600', 'CSCI3656'],
    ],
}

# ---------------------------------------------------------------------------
# HELPER: normalize rules on import
# ---------------------------------------------------------------------------
# Converts any bare string entries to single-element lists, so the rest of
# the pipeline can always assume list-of-lists without special-casing.

def _normalize_rules(rules: dict) -> dict:
    normalized = {}
    for course, groups in rules.items():
        normalized[course] = [
            [g] if isinstance(g, str) else g
            for g in groups
        ]
    return normalized

PREREQ_RULES = _normalize_rules(PREREQ_RULES)
COREQ_RULES  = _normalize_rules(COREQ_RULES)


# ---------------------------------------------------------------------------
# HELPER: check satisfaction
# ---------------------------------------------------------------------------

def prereqs_satisfied(course: str, completed: set) -> bool:
    """
    Return True if all prerequisite groups for `course` are satisfied
    by the set of completed course codes.

    A group is satisfied when at least one course in it appears in `completed`.
    Courses with no entry in PREREQ_RULES have no prerequisites.
    """
    for group in PREREQ_RULES.get(course, []):
        if not any(c in completed for c in group):
            return False
    return True


def coreqs_satisfied(course: str, completed: set, in_progress: set) -> bool:
    """
    Return True if all corequisite groups for `course` are satisfied
    by completed OR currently in-progress courses.
    """
    available = completed | in_progress
    for group in COREQ_RULES.get(course, []):
        if not any(c in available for c in group):
            return False
    return True


def is_eligible(
    course: str,
    completed: set,
    in_progress: set,
    class_level: int = 0,
) -> bool:
    """
    Return True if a student is eligible to enroll in `course`:
      - Has not already completed the course
      - All prerequisites satisfied by completed courses
      - For SENIOR_REQUIRED courses: class level must be >= 4
      - Corequisites are NOT used as an eligibility gate — they are
        encoded as a feature (coreq_groups_satisfied) so the model
        can learn their effect on enrollment probability without
        excluding students who will co-enroll in the target term.
    """
    if course in completed:
        return False
    if not prereqs_satisfied(course, completed):
        return False
    if course in SENIOR_REQUIRED and class_level < 4:
        return False
    return True