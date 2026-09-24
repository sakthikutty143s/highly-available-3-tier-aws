# ☁️ AWS Architecture

## 🚀 Highly Available 3-Tier Web Application on AWS

This project implements a **Highly Available 3-Tier Web Application on AWS** using a secure and scalable cloud architecture.

The application follows a three-tier architecture:

1. **Presentation / Load Balancing Layer**
2. **Application Layer**
3. **Database Layer**

The application tier is distributed across **two Availability Zones** to improve availability and provide automatic recovery during instance failures.

---

## 🏗️ 1. Architecture Overview

The application follows the request flow:

```text
Internet Users
      |
      v
Amazon Route 53
      |
      v
HTTPS :443
      |
      v
Application Load Balancer
      |
      | HTTP :5000
      v
+---------------------------+
|     Application Tier      |
|                           |
|  AZ-1              AZ-2  |
|  EC2               EC2    |
|  Flask             Flask  |
|  Gunicorn          Gunicorn|
+---------------------------+
      |
      | MySQL :3306
      v
+---------------------------+
|       Database Tier       |
|                           |
|      Amazon RDS MySQL     |
|       Private Subnets     |
+---------------------------+
```

Supporting AWS services include:

* IAM Role
* AWS Secrets Manager
* Amazon S3
* AWS Systems Manager
* Amazon CloudWatch
* Amazon SNS

The application tier uses EC2 instances across two Availability Zones and an Auto Scaling Group for automatic instance replacement and recovery.

---

## 🌎 2. AWS Region

The project is deployed in the **AWS Mumbai Region**.

```text
Region : ap-south-1
Location : Mumbai
Availability Zones : 2
```

The VPC uses two Availability Zones to distribute application resources and improve fault tolerance.

---

## 🌐 3. VPC Architecture

The main VPC is:

```text
VPC Name : three-tier-vpc
CIDR     : 10.0.0.0/16
```

The VPC is divided into six subnets:

* 2 Public Subnets
* 2 Private Application Subnets
* 2 Private Database Subnets

This subnet separation provides network isolation between the different application tiers.

### 🧩 3.1 VPC Layout

```text
VPC: three-tier-vpc
CIDR: 10.0.0.0/16

Availability Zone 1          Availability Zone 2

Public-1                     Public-2
10.0.1.0/24                  10.0.2.0/24
ALB / NAT                    ALB

Private-App-1                Private-App-2
10.0.3.0/24                  10.0.4.0/24
EC2 / Flask                  EC2 / Flask

Private-DB-1                 Private-DB-2
10.0.5.0/24                  10.0.6.0/24
RDS                          RDS
```

---

## 🔀 4. Subnet Design

The VPC contains separate public and private subnets for different infrastructure components.

### 🌍 4.1 Public Subnets

| Subnet   | CIDR          | Purpose           |
| -------- | ------------- | ----------------- |
| Public-1 | `10.0.1.0/24` | ALB / NAT Gateway |
| Public-2 | `10.0.2.0/24` | ALB               |

Public subnets provide the network location for internet-facing load-balancing infrastructure and the NAT Gateway.

### 🔒 4.2 Private Application Subnets

| Subnet        | CIDR          | Purpose              |
| ------------- | ------------- | -------------------- |
| Private-App-1 | `10.0.3.0/24` | EC2 Application Tier |
| Private-App-2 | `10.0.4.0/24` | EC2 Application Tier |

The Flask application servers run inside private subnets and are not directly exposed to the internet.

Application traffic reaches these servers through the Application Load Balancer.

### 🗄️ 4.3 Private Database Subnets

| Subnet       | CIDR          | Purpose          |
| ------------ | ------------- | ---------------- |
| Private-DB-1 | `10.0.5.0/24` | RDS              |
| Private-DB-2 | `10.0.6.0/24` | RDS Subnet Group |

The database tier is isolated inside private subnets and is not publicly accessible.

---

## 🌐 5. Presentation / Load Balancing Layer

The presentation layer contains the internet-facing components of the application.

### Components

* Amazon Route 53
* AWS Certificate Manager
* Application Load Balancer
* Public Subnets
* HTTPS

The custom domain is managed through Route 53 and resolves to the Application Load Balancer.

The ALB receives public HTTP/HTTPS traffic and forwards application traffic to healthy EC2 instances.

### 🔄 5.1 Traffic Flow

```text
User
 |
 | HTTPS :443
 v
Route 53
 |
 v
Application Load Balancer
 |
 | HTTP :5000
 +----------------------+
 |                      |
 v                      v
EC2 - AZ1             EC2 - AZ2
 |                      |
 +----------+-----------+
            |
            | MySQL :3306
            v
        RDS MySQL
```

---

## ⚙️ 6. Application Layer

The application tier consists of **Flask applications running on Amazon EC2**.

The application instances are distributed across two Availability Zones.

Each application instance runs:

```text
EC2
 |
 +-- Flask
 |
 +-- Gunicorn
 |
 +-- Port 5000
```

The application servers are managed by an Auto Scaling Group.

### Auto Scaling Configuration

```text
Minimum : 2
Desired : 2
Maximum : 4
```

This configuration allows the application tier to maintain multiple instances and automatically replace failed capacity.

---

## ⚖️ 7. Application Load Balancer

The Application Load Balancer provides:

* Public application access
* HTTPS termination
* Traffic distribution
* Health checking
* Routing to healthy EC2 instances

The ALB forwards application traffic to:

```text
HTTP :5000
```

The Application Security Group allows port `5000` traffic from the ALB Security Group.

This ensures that the application servers do not require direct public access.

---

## 📈 8. Auto Scaling and High Availability

The application tier uses an Auto Scaling Group across two Availability Zones.

```text
             Application Load Balancer
                       |
              +--------+--------+
              |                 |
              v                 v
           EC2 AZ-1          EC2 AZ-2
              |                 |
              +--------+--------+
                       |
                 Auto Scaling
                    Group

                  Min: 2
               Desired: 2
                  Max: 4
```

During testing, an application EC2 instance was terminated to simulate an instance failure.

The observed behavior was:

1. ALB continued serving traffic through healthy capacity.
2. Auto Scaling detected the capacity change.
3. A replacement EC2 instance was launched.
4. The replacement instance became healthy in the target group.

This demonstrates application-tier high availability and automatic recovery.

---

## 🗄️ 9. Database Layer

The database tier uses **Amazon RDS for MySQL**.

### Database Configuration

```text
DB Identifier  : three-tier-db
Database       : appdb
Username       : admin
Port           : 3306
Public Access  : No
Subnet Group   : three-tier-db-subnet-group
```

RDS is deployed inside private database subnets and is not exposed to the public internet.

### 🔗 9.1 Database Traffic

Only the application tier is allowed to communicate with the database tier.

```text
EC2 Application Tier
        |
        | TCP 3306
        v
     sg-db
        |
        v
 Amazon RDS MySQL
```

The database Security Group allows MySQL traffic on port `3306` from the application Security Group.

```text
Protocol : TCP
Port     : 3306
Source   : sg-app
```

---

## 🛡️ 10. Security Groups

Security Groups are used to control communication between the different application tiers.

### 🌐 10.1 ALB Security Group — `sg-alb`

Inbound traffic:

```text
HTTP
TCP 80
Source: 0.0.0.0/0

HTTPS
TCP 443
Source: 0.0.0.0/0
```

HTTP traffic is redirected to HTTPS.

### ⚙️ 10.2 Application Security Group — `sg-app`

Inbound traffic:

```text
TCP 5000
Source: sg-alb
```

The EC2 instances do not require public inbound SSH access.

### 🗄️ 10.3 Database Security Group — `sg-db`

Inbound traffic:

```text
TCP 3306
Source: sg-app
```

Therefore, the database can only be accessed by resources associated with the application Security Group.

---

## 🌍 11. Internet Gateway and NAT Gateway

The VPC uses an **Internet Gateway** for internet connectivity from public resources.

A NAT Gateway is deployed in a public subnet.

```text
Private EC2
     |
     v
Private Route Table
     |
     v
NAT Gateway
     |
     v
Internet Gateway
     |
     v
Internet
```

The NAT Gateway provides outbound internet access for resources in private subnets while keeping the application servers private.

The project uses:

```text
NAT Gateways : 1
```

---

## 🔐 12. DNS and HTTPS

### 🌐 Amazon Route 53

Amazon Route 53 provides DNS management for the application's domain.

```text
User
 |
 v
Custom Domain
 |
 v
Route 53
 |
 v
Application Load Balancer
```

### 🔒 AWS Certificate Manager

AWS Certificate Manager provides the SSL/TLS certificate used by the Application Load Balancer.

```text
Client
 |
 | HTTPS :443
 v
ALB
 |
 +-- ACM Certificate
```

This provides encrypted HTTPS communication for public client traffic.

---

## 🔑 13. Secrets Manager

Database credentials are stored securely in **AWS Secrets Manager**.

```text
Secret:
three-tier/rds
```

The application retrieves database credentials through AWS permissions instead of relying on hard-coded credentials.

```text
EC2
 |
 | IAM Role
 v
Secrets Manager
 |
 v
RDS Credentials
 |
 v
Application
 |
 v
RDS MySQL
```

This improves credential security by removing hard-coded database passwords from application configuration.

---

## 👤 14. IAM Role

The EC2 instances use an IAM Role instead of long-lived AWS access keys.

```text
IAM Role:
EC2-S3-Role
```

The IAM Role provides the AWS permissions required by the EC2 application environment.

This demonstrates secure AWS access using IAM Roles rather than storing long-lived credentials on EC2 instances.

---

## 🛠️ 15. AWS Systems Manager

AWS Systems Manager Session Manager is used to administer private EC2 instances.

```text
Administrator
      |
      v
AWS Systems Manager
      |
      v
Private EC2
```

Session Manager removes the requirement for direct inbound SSH access.

This allows the application instances to remain private while still providing administrative access.

---

## 🪣 16. Amazon S3

Amazon S3 is used as a private object-storage service.

Security configuration includes:

* Block Public Access
* Bucket Owner Enforced
* Versioning
* Server-Side Encryption

The EC2 IAM Role provides the application's AWS access mechanism for S3 operations.

---

## 📊 17. Monitoring and Alerting

Amazon CloudWatch is used for infrastructure monitoring and alarms.

The notification flow is:

```text
AWS Resources
     |
     v
CloudWatch
     |
     | Alarm
     v
Amazon SNS
     |
     v
Email Notification
```

This provides infrastructure-health monitoring and email notification capability.

---

## 🔄 18. Complete Architecture Flow

```text
                    INTERNET USERS
                          |
                          v
                     +----------+
                     | Route 53 |
                     |   DNS    |
                     +----------+
                          |
                     HTTPS :443
                          |
                          v
              +----------------------+
              | Application Load     |
              | Balancer             |
              +----------------------+
                    /          \
                   /            \
                  v              v

            AVAILABILITY ZONE 1    AVAILABILITY ZONE 2

              Public Subnet          Public Subnet
              10.0.1.0/24            10.0.2.0/24
                    |                      |
                    v                      v
              Private-App-1          Private-App-2
              10.0.3.0/24            10.0.4.0/24
                    |                      |
                    v                      v
                  EC2                    EC2
                Flask                  Flask
               Gunicorn               Gunicorn
                    \                      /
                     \                    /
                      +------ 3306 ------+
                              |
                              v
                    Private Database Tier
                              |
                       +-------------+
                       | RDS MySQL   |
                       | three-tier-db|
                       | appdb       |
                       +-------------+

             Supporting AWS Services

                  EC2 IAM Role
                 /      |       \
                v       v        v
        Secrets Manager S3   Systems Manager

                   Monitoring

                  CloudWatch
                      |
                      v
                     SNS
                      |
                      v
                Email Alert
```

---

## 🛡️ 19. Security Architecture

The project follows a layered security model.

### 🌐 Network Security

* Public and private subnet separation
* Private EC2 application servers
* Private RDS database
* Restricted Security Groups
* RDS is not publicly accessible
* Application traffic restricted to port `5000`
* Database traffic restricted to port `3306`

### 👤 Identity and Access

* IAM Roles instead of long-lived access keys
* AWS Secrets Manager for RDS credentials
* Systems Manager Session Manager for EC2 administration

### 🔐 Application Security

* HTTPS using ACM
* ALB-based public access
* Private application servers
* Restricted tier-to-tier communication

### 🪣 Storage Security

* Private S3 bucket
* S3 Block Public Access
* Server-side encryption
* Versioning

These security controls provide network isolation, restricted communication, secure credential management, and controlled AWS resource access.

---

## ✨ 20. Architecture Advantages

### 🚀 High Availability

Application instances are distributed across two Availability Zones.

### 📈 Scalability

The Auto Scaling Group can scale application capacity from:

```text
2 → 4 EC2 instances
```

### 🛡️ Fault Tolerance

The ALB routes traffic to healthy application instances while Auto Scaling replaces failed capacity.

### 🔒 Network Isolation

Application and database resources run in private subnets.

### 🗄️ Secure Database Access

RDS accepts database traffic only from the application Security Group.

### 🛠️ Secure Administration

Session Manager provides EC2 administration without inbound SSH.

### 🔑 Secure Credentials

RDS credentials are stored in AWS Secrets Manager instead of being hard-coded.

### 🔐 HTTPS

Public client traffic is protected using HTTPS and an ACM certificate.

### 📊 Monitoring

CloudWatch and SNS provide infrastructure monitoring and alerting.

---

## 🧪 21. High Availability Validation

The project includes an actual application-tier failure test.

### 🔬 Test

An EC2 instance managed by the Auto Scaling Group was terminated to simulate an application instance failure.

### 🎯 Expected Behavior

```text
EC2 Failure
    |
    v
ALB detects unhealthy target
    |
    v
Traffic continues through healthy capacity
    |
    v
Auto Scaling detects capacity change
    |
    v
Replacement EC2 launched
    |
    v
Application starts
    |
    v
Target becomes healthy
```

### ✅ Result

The application remained available through the healthy instance and the Auto Scaling Group automatically launched replacement capacity.

This demonstrates application-tier automatic recovery and high availability.

---

## 📋 22. Architecture Components Summary

| Component           | Configuration      | Purpose                        |
| ------------------- | ------------------ | ------------------------------ |
| Region              | `ap-south-1`       | AWS deployment region          |
| VPC                 | `three-tier-vpc`   | Network isolation              |
| VPC CIDR            | `10.0.0.0/16`      | Private network range          |
| Public Subnets      | 2                  | ALB / NAT                      |
| Private App Subnets | 2                  | EC2 application tier           |
| Private DB Subnets  | 2                  | RDS                            |
| ALB                 | Internet-facing    | Traffic distribution           |
| EC2                 | 2 minimum          | Flask application              |
| Auto Scaling        | 2–4                | Scaling and recovery           |
| RDS                 | MySQL              | Database                       |
| Route 53            | DNS                | Domain resolution              |
| ACM                 | TLS Certificate    | HTTPS                          |
| Secrets Manager     | `three-tier/rds`   | Database credentials           |
| IAM                 | `EC2-S3-Role`      | AWS permissions                |
| SSM                 | Session Manager    | Private EC2 administration     |
| S3                  | Private bucket     | Object storage                 |
| CloudWatch          | Monitoring         | Metrics and alarms             |
| SNS                 | Email notification | Alerting                       |
| NAT Gateway         | 1                  | Private subnet outbound access |

---

## 🖼️ 23. Architecture Diagram

The editable architecture diagram is stored at:

```text
architecture/architecture-diagram.drawio
```

The rendered architecture image is stored at:

```text
architecture/architecture-diagram.png
```

These files provide a visual representation of the AWS infrastructure documented in this architecture document.

---

## ⚠️ 24. Important Architecture Note

This project demonstrates **application-tier high availability across two Availability Zones**.

The current architecture uses Amazon RDS MySQL in the private database tier.

**RDS Multi-AZ should not be represented as enabled unless it has been explicitly configured.**

Potential future improvements include:

* AWS WAF
* Amazon CloudFront
* VPC Endpoints
* Centralized CloudWatch Logs
* AWS CloudTrail
* More granular IAM Roles
* Terraform Infrastructure as Code
* GitHub Actions CI/CD
* Docker-based deployment
* ECS / Fargate
* Automated Testing
* Blue/Green Deployments

These are future improvements and are not represented as current architecture components.

---

## 📚 25. Related Documentation

```text
README.md

docs/
├── architecture.md
├── deployment.md
├── security.md
└── troubleshooting.md
```

The `README.md` provides the overall project documentation, while `architecture.md` focuses specifically on the AWS infrastructure and architecture design.
