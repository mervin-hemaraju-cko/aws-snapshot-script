from datetime import date

# This function checks whether the task title
# is a valid approved snapshot to be done
# this can only be recognized by the words [snap] or [snapshot]
# Any other keywors would be considered not a snapshot
def retrieve_host(title):
    
    action = title.split(":")

    if action[0] == "snap" or action[0] == "snapshot":
        return action[1]
    else:
        return None

# This function returns today's date
# in a readable format
def format_today():
    today = date.today()
    return today.strftime("%Y%m%d")

# Message construct
def construct_results_message(results, ticket):

    final_message = f"The results for ticket {ticket} are:\n"

    for result in results:
        final_message += f"{result}\n"

    return final_message
