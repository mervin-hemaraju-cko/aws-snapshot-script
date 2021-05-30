
class SnapshotRequest:

    def __init__(self, volume_id, hostname, agent, ticket_number) -> None:
        self.volume_id = volume_id
        self.hostname = hostname
        self.agent = agent
        self.ticket_number = ticket_number
