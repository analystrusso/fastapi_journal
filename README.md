This was a hell of a project, and it isn't done yet.

Here's what it is: a journaling application hosted on AWS. Specifically,

The app itself is on an EC2 instance, which is connected to a PostgreSQL RDS instance that has the journal and users tables for data storage.
The RDS database can only communicate with the EC2 instance via Security Groups, and the EC2 gets to the internet via an Application Load Balancer and a Cloudfront distribution.
This allows users to get HTTPS security when they go to the site.

The VPC has public subnets for the ALB and a private one for the EC2 and RDS instances.

TODO: tighten up security a bit more.
TODO: implement a user registration and password reset process.
TODO: implement an entry update process.
TODO: maybe make it prettier?
