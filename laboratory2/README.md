#Create virtual env
python3 -m venv myenv
source myenv/bin/activate

#Install and run ptftpf client
pip3 install ptftpd
ptftpd -D -p 6969 -r lo ./

#Read command
python3 tftp_client.py read read_file.txt --server 127.0.0.1 --port 6969

#Write command
python3 tftp_client.py write write_file.txt --server 127.0.0.1 --port 6969

#El que importa que surt al pdf de lenunciat:
python3 tftp_client.py -m rx -p 6969 data.txt