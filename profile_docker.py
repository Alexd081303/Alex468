import geni.portal as portal
import geni.rspec.pg as rspec

request = portal.context.makeRequestRSpec()

node = request.XenVM("node")
node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU22-64-STD"
node.routable_control_ip = "true"

# Install Docker
node.addService(rspec.Execute(shell="/bin/bash", command="sudo apt update"))
node.addService(rspec.Execute(shell="/bin/bash", command="sudo apt install -y docker.io"))
node.addService(rspec.Execute(shell="/bin/bash", command="sudo systemctl enable --now docker"))
node.addService(rspec.Execute(shell="/bin/bash", command="sudo usermod -aG docker $USER"))

portal.context.printRequestRSpec()
