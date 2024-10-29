#Create virtual env
python3 -m venv myenv
source myenv/bin/activate

#Install and run ptftpf client
pip3 install ptftpd
ptftpd -D -p 6969 -r lo ./