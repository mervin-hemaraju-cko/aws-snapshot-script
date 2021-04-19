
class Instance:

    # Initialize the Instance class
    def __init__(self, root_volume_name, volumes, root_volume_id):
        self.root_volume_name = root_volume_name
        self.volumes = volumes
        self.root_volume_id = root_volume_id
    
    @staticmethod
    def load(response):

        root_volume_name = response['RootDeviceName']
        volumes = response['BlockDeviceMappings']
        volume_id = None

        for volume in volumes:
            if volume['DeviceName'] == root_volume_name:
                volume_id = volume['Ebs']['VolumeId']
        
        return Instance(root_volume_name, volumes, volume_id)