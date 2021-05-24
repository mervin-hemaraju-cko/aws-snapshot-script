
import utils.helper as Helper

class Task:

    # Initialize the Task class
    def __init__(self, hostip, hostname):
        self.hostip = hostip
        self.hostname = hostname
    
    @staticmethod
    def loads(response):
        # Load the raw tasks
        # Filter the list by only open tasks
        raw_tasks = list(filter(lambda d: d["status"] == 1, response))

        # Initialize empty task list
        tasks = []

        # Load task in list
        for task in raw_tasks:
            host = Helper.retrieve_host((task["title"]).strip())
            name = (task["description"]).strip()

            if(host != None):
                # Add task in list
                tasks.append(
                    Task(host, name)
                )

        return tasks

