# Threats 
1. Dos attack through constant use of server resources
1. Sniffing attacks, unencrypted traffic  
1. Replay attacks 
   1. Session key regeneration
2. Impersonation
3. Man in the middle
4. Rootkits 
  * We cant do anything
* 

# Remediation
1.  Set timeout for the security when a number of connections are made to prevent Dos attacks through consumption of server resources. The threads are not being killed and are blocking.
2.  Implement Pretty Good Privacy, Using Certificates for public session key exchanges, and symmetric keys for message encryption
3.  Timestamps are already in use and also we have check condition in our code
4.  Client to Client Authentication, (and client to server authentication on flow 2) 
5.  