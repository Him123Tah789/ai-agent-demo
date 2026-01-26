def explain_decision(issue_type, human_needed):
    if human_needed:
        return "This case is complex and requires human review."
    return "This issue matches known policies and was handled automatically."
