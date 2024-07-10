import oci
import time

# Create a default config using DEFAULT profile in default location
# Refer to
# https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File
# for more info
config = oci.config.from_file(file_location="./config")
with open("~/.ssh/id_rsa.pub", "r") as ssh_key_file:
    ssh_public_key = ssh_key_file.read().strip()

# Create a service client
compute = oci.core.ComputeClient(config)
counter = 0
# Create instance in a loop until successful
while True:
    counter += 1
    i = counter % 3 + 1
    availability_domain = "eiDh:EU-FRANKFURT-1-AD-" + str(i)
    print("try number", counter, "to instance", availability_domain)
    try:
        # Create instance
        response = compute.launch_instance(
            launch_instance_details=oci.core.models.LaunchInstanceDetails(
                availability_domain=availability_domain,
                compartment_id="ocid1.tenancy.oc1..etc",
                shape="VM.Standard.A1.Flex",
                subnet_id="ocid1.subnet.oc1.eu-frankfurt-1.etc",
                metadata={
                    "ssh_authorized_keys": ssh_public_key
                },
                create_vnic_details=oci.core.models.CreateVnicDetails(
                    assign_public_ip=True,
                    assign_private_dns_record=True,
                    subnet_id="ocid1.subnet.oc1.eu-frankfurt-1.etc"),
                shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                    ocpus=2,
                    memory_in_gbs=12),
                source_details=oci.core.models.InstanceSourceViaImageDetails(
                    source_type="image",
                    image_id="stuff"),
                display_name="abs-chat-server"
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