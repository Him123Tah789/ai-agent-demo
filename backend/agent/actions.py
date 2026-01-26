def take_action(issue_type):
    if issue_type == "delivery_delay":
        return {
            "action": "Email Sent",
            "message": "Apology email with tracking link sent to customer",
            "human_needed": False
        }
    else:
        return {
            "action": "Escalated",
            "message": "Forwarded to human agent",
            "human_needed": True
        }
