# Create virtual env
python3 -m venv myenv
source myenv/bin/activate

# Install ptftpf client
pip3 install ptftpd

# Run ptftpf client
## Virtual machine: 
ptftpd -D -p 6969 -r lo ./
## WSL: 
~/.local/bin/ptftpd -D -p 6969 -r lo ./


# Read command
python3 tftp_client.py read data.txt --server 127.0.0.1 --port 6969

# Write command
python3 tftp_client.py write data.txt --server 127.0.0.1 --port 6969

# El que importa que surt al pdf de lenunciat:
python3 tftp_client.py -m rx -p 6969 data.txt



# Git push

git add .
git commit -m "Mensaje del commit"
git push origin main

# Git pull
git pull origin main