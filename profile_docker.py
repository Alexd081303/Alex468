import geni.portal as portal
import geni.rspec.pg as rspec

# Create a Request object to start building the RSpec.
request = portal.context.makeRequestRSpec()

# Create a XenVM node with Ubuntu 22.04
node = request.XenVM("node")
node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU22-64-STD"
node.routable_control_ip = "true"

# Update package lists
node.addService(rspec.Execute(shell="/bin/sh", command="sudo apt-get update -y"))

# Install required packages for Docker
node.addService(rspec.Execute(shell="/bin/sh", command="sudo apt-get install -y ca-certificates curl gnupg lsb-release git"))

# Add Docker's official GPG key
node.addService(rspec.Execute(shell="/bin/sh", command="sudo mkdir -p /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg"))

# Set up the Docker repository
node.addService(rspec.Execute(shell="/bin/sh", command='echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'))

# Install Docker Engine and Docker Compose
node.addService(rspec.Execute(shell="/bin/sh", command="sudo apt-get update -y && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"))

# Add current user to the docker group so sudo isn't required
node.addService(rspec.Execute(shell="/bin/sh", command="sudo usermod -aG docker $USER"))

# Enable and start Docker
node.addService(rspec.Execute(shell="/bin/sh", command="sudo systemctl enable docker && sudo systemctl start docker"))

# Verify Docker installation
node.addService(rspec.Execute(shell="/bin/sh", command="docker --version && docker compose version"))

# Print the RSpec to the enclosing page.
portal.context.printRequestRSpec()
