# 🛡️ Security Architecture

## 📌 1. Security Overview

The project follows a **layered security architecture** to protect the application, database, network, credentials, and AWS resources.

The main security controls include:

* VPC isolation
* Public and private subnet separation
* Security Groups
* Private EC2 instances
* Private RDS database
* IAM Roles
* AWS Secrets Manager
* HTTPS
* S3 security
* Systems Manager Session Manager

---

## 🌐 2. Network Security

The VPC uses separate public and private subnets.

```text
Public Subnets
      |
      +-- ALB
      |
      +-- NAT Gateway

Private App Subnets
      |
      +-- EC2
      +-- Flask
      +-- Gunicorn

Private DB Subnets
      |
      +-- RDS MySQL
```

The application and database resources are not directly exposed to the public internet.

---

## 🛡️ 3. Security Group Architecture

Security Groups control communication between application tiers.

```text
Internet
   |
   | 80 / 443
   v
sg-alb
   |
   | 5000
   v
sg-app
   |
   | 3306
   v
sg-db
```

This restricts traffic to the required ports.

---

## 🌐 4. ALB Security Group

The ALB Security Group allows public web traffic.

```text
HTTP
Port   : 80
Source : 0.0.0.0/0

HTTPS
Port   : 443
Source : 0.0.0.0/0
```

HTTP traffic is redirected to HTTPS.

---

## ⚙️ 5. Application Security Group

The application Security Group allows traffic only from the ALB Security Group.

```text
Protocol : TCP
Port     : 5000
Source   : sg-alb
```

The EC2 application servers do not require public inbound access.

---

## 🗄️ 6. Database Security Group

The database Security Group allows MySQL traffic only from the application Security Group.

```text
Protocol : TCP
Port     : 3306
Source   : sg-app
```

The database is therefore isolated from direct public access.

---

## 🔐 7. IAM Security

The EC2 application servers use IAM Roles instead of long-lived AWS access keys.

The IAM Role provides permissions required by the application to interact with AWS services.

Example:

```text
EC2
 |
 v
IAM Role
 |
 +----> S3
 |
 +----> Secrets Manager
 |
 +----> Systems Manager
```

This avoids storing long-lived AWS credentials on EC2 instances.

---

## 🔑 8. Secrets Manager

Database credentials are stored in AWS Secrets Manager.

```text
Secret:
three-tier/rds
```

The application retrieves the credentials through IAM permissions.

This prevents database passwords from being hard-coded in application configuration.

---

## 🔒 9. HTTPS Security

Public application traffic is protected using HTTPS.

AWS Certificate Manager provides the SSL/TLS certificate.

```text
Client
 |
 | HTTPS :443
 v
ALB
 |
 v
Application
```

HTTP traffic is redirected to HTTPS.

---

## 🗄️ 10. Database Security

Amazon RDS MySQL is deployed in private database subnets.

Configuration:

```text
Public Access : No
Port          : 3306
```

Only the application tier is permitted to connect to the database.

---

## 🪣 11. S3 Security

The S3 bucket is configured as private storage.

Security controls include:

* Block Public Access
* Bucket Owner Enforced
* Versioning
* Server-Side Encryption

Application access is provided through the EC2 IAM Role.

---

## 🛠️ 12. Secure EC2 Administration

AWS Systems Manager Session Manager is used to administer private EC2 instances.

This avoids the requirement for public inbound SSH access.

```text
Administrator
      |
      v
Systems Manager
      |
      v
Private EC2
```

---

## 🌍 13. Private Subnet Security

The application servers run in private subnets.

The database servers are also located in private subnets.

Only required communication is permitted:

```text
ALB
 |
 | TCP 5000
 v
EC2
 |
 | TCP 3306
 v
RDS
```

---

## 📊 14. Monitoring and Alerting

Amazon CloudWatch provides monitoring and alarms.

Amazon SNS provides email notifications.

```text
AWS Resources
     |
     v
CloudWatch
     |
     v
SNS
     |
     v
Email Alert
```

Monitoring helps identify infrastructure issues and application availability problems.

---

## 🧱 15. Security Layers

The overall security model can be represented as:

```text
Internet
   |
   v
Route 53
   |
   v
HTTPS / ACM
   |
   v
Application Load Balancer
   |
   | Security Group
   v
Private EC2
   |
   | Security Group
   v
Private RDS
```

Additional protection is provided through:

```text
IAM
Secrets Manager
S3 Security
Systems Manager
CloudWatch
SNS
```

---

## ✅ 16. Security Checklist

* [x] Application servers deployed in private subnets
* [x] Database deployed in private subnets
* [x] RDS public access disabled
* [x] ALB used for public application access
* [x] Application port restricted to ALB
* [x] Database port restricted to application tier
* [x] HTTPS enabled
* [x] ACM certificate configured
* [x] IAM Role used for AWS access
* [x] Database credentials stored in Secrets Manager
* [x] S3 Block Public Access enabled
* [x] S3 encryption enabled
* [x] Session Manager used for private EC2 administration
* [x] CloudWatch monitoring configured
* [x] SNS notifications configured
