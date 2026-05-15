import subprocess

EC2_IP = "54.165.17.84"
KEY = "infra/id_rsa"

cmd = f"ssh -o StrictHostKeyChecking=no -i {KEY} ec2-user@{EC2_IP} 'docker logs $(docker ps -q) --tail 50'"

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

with open("logs.txt", "w") as f:
    f.write(result.stdout)

print("Logs fetched from EC2")