Run the following command

```sh
$ openssl req -newkey rsa:2048 -nodes -keyout server_key.pem -x509 -days 365 -out server_certificate.pem
```

This will generate a self signed certificate.

The common name should be the server's IP, other information is not necessary.

We can validate the information using the following command 

```sh
openssl x509 -text -noout -in server_certificate.pem
```


After a quick google we can do this all in one step
``` sh
$ openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=US/L=Lowell/CN=localhost" -keyout server_key.key -out server_certificate.pem
```


## Note
Cert with Common Name = "127.0.0.1" did not work, localhost did

# Reference
https://www.ibm.com/docs/en/api-connect/2018.x?topic=overview-generating-self-signed-certificate-using-openssl 


https://www.digicert.com/kb/ssl-support/pem-ssl-creation.htm
^^^ This talks about cert chains (files with a chain of trusted certs...)