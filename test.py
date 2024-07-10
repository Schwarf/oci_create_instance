
import oci

# Default config file and profile
default_config = oci.config.from_file()

# validate the default config file
oci.config.validate_config(default_config)
