
class Instance:

    # Initialize the Instance class
    def __init__(self, name, root_volume_name, volumes, root_volume_id):
        self.name = name
        self.root_volume_name = root_volume_name
        self.volumes = volumes
        self.root_volume_id = root_volume_id
    
    @staticmethod
    def load(response):

        # Get Volume Details
        root_volume_name = response['RootDeviceName']
        volumes = response['BlockDeviceMappings']
        volume_id = None
        instance_name = "undefined"

        for volume in volumes:
            if volume['DeviceName'] == root_volume_name:
                volume_id = volume['Ebs']['VolumeId']
        
        # Get Instance Name
        for tag in response['Tags']:
            if(tag['Key'].lower() == "name"):
                instance_name = tag["Value"]

        return Instance(instance_name, root_volume_name, volumes, volume_id)