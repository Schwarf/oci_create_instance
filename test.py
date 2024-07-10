import oci
import json
import os
import time


# Default config file and profile
default_config = oci.config.from_file()
config_file_path = os.path.expanduser('~/.oci/my_config.json')
ssh_file_path = os.path.expanduser('~/.ssh/id_rsa.pub')

with open(config_file_path, 'r') as config_file:
    needed_configs = json.load(config_file)
with open(ssh_file_path, "r") as ssh_key_file:
    ssh_public_key = ssh_key_file.read().strip()

# validate the default config file
oci.config.validate_config(default_config)
compute = oci.core.ComputeClient(default_config)
counter = 0
i = 0
while i < 1:
    i += 1
    counter += 1
    domain_counter = counter % 3 + 1
    availability_domain = needed_configs["domain"] + str(domain_counter)
    print("try number", counter, "to instance", availability_domain)
    try:
        # Create instance
        response = compute.launch_instance(
            launch_instance_details=oci.core.models.LaunchInstanceDetails(
                availability_domain=availability_domain,
                compartment_id=needed_configs["compartment_id"],
                shape=needed_configs["shape"],
                subnet_id=needed_configs["subnet_id"],
                metadata={
                    "ssh_authorized_keys": ssh_public_key
                },
                create_vnic_details=oci.core.models.CreateVnicDetails(
                    assign_public_ip=True,
                    assign_private_dns_record=True,
                    subnet_id=needed_configs["subnet_id"]),
                shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                    ocpus=needed_configs["ocpus"],
                    memory_in_gbs=needed_configs["memory_in_gbs"]),
                source_details=oci.core.models.InstanceSourceViaImageDetails(
                    source_type="image",
                    image_id=needed_configs["image_id"]),
                display_name=needed_configs["display_name"]
            )
        )
        instance_id = response.data.id

        # Verify instance is available
        while True:
            instance = compute.get_instance(instance_id).data
            if instance.lifecycle_state == "RUNNING":
                print(f"Instance {instance_id} is running!")
                break

            print(instance)
            time.sleep(10)  # wait before checking again

        break  # exit the while loop when the instance is successfully created and running
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        time.sleep(10)  # wait before trying again
