# 🚀 Deployment Notes

## 📌 Project Overview

This document describes the deployment process for the **Highly Available 3-Tier Web Application on AWS**.

The application is deployed using a highly available AWS architecture consisting of:

* Amazon VPC
* Public and Private Subnets
* Internet Gateway
* NAT Gateway
* Application Load Balancer
* Amazon EC2
* EC2 Auto Scaling
* Amazon RDS MySQL
* Amazon S3
* AWS Secrets Manager
* IAM
* Route 53
* AWS Certificate Manager
* AWS Systems Manager
* Amazon CloudWatch
* Amazon SNS

The application tier runs a Flask application using Gunicorn. The application connects securely to a private RDS MySQL database.

---

# 🌍 AWS Region

The project is deployed in:

```text
Region: ap-south-1
Region Name: Asia Pacific (Mumbai)
```

---

# 🏗️ VPC and Network Configuration

## 🔹 VPC

Create a VPC with the following configuration:

```text
VPC Name: three-tier-vpc
CIDR Block: 10.0.0.0/16
```

The VPC contains multiple subnets distributed across two Availability Zones.

---

## 🔹 Public Subnets

Public subnets are used for internet-facing resources such as the Application Load Balancer and NAT Gateway.

| Subnet   | CIDR        | Purpose           |
| -------- | ----------- | ----------------- |
| Public-1 | 10.0.1.0/24 | ALB / NAT Gateway |
| Public-2 | 10.0.2.0/24 | ALB               |

---

## 🔹 Private Application Subnets

The Flask application servers are deployed in private subnets.

| Subnet        | CIDR        | Purpose         |
| ------------- | ----------- | --------------- |
| Private-App-1 | 10.0.3.0/24 | Application EC2 |
| Private-App-2 | 10.0.4.0/24 | Application EC2 |

The application instances do not require public IP addresses.

---

## 🔹 Private Database Subnets

RDS MySQL is deployed inside dedicated private database subnets.

| Subnet       | CIDR        | Purpose |
| ------------ | ----------- | ------- |
| Private-DB-1 | 10.0.5.0/24 | RDS     |
| Private-DB-2 | 10.0.6.0/24 | RDS     |

The database is not publicly accessible.

---

# 🌐 Internet Gateway

Create and attach an Internet Gateway to the VPC.

```text
Internet
   ↓
Internet Gateway
   ↓
Public Subnets
```

The Internet Gateway provides internet connectivity for resources placed in public subnets.

---

# 🔄 NAT Gateway

A NAT Gateway is deployed in a public subnet.

Private application instances use the NAT Gateway for outbound internet connectivity.

```text
Private EC2
     ↓
Private Route Table
     ↓
NAT Gateway
     ↓
Internet Gateway
     ↓
Internet
```

The NAT Gateway allows private instances to access external services without exposing them directly to the internet.

---

# 🔐 Security Groups

Three main Security Groups are used.

## 🔹 ALB Security Group

```text
Security Group: sg-alb
```

Inbound rules:

| Type  | Port | Source    |
| ----- | ---: | --------- |
| HTTP  |   80 | 0.0.0.0/0 |
| HTTPS |  443 | 0.0.0.0/0 |

---

## 🔹 Application Security Group

```text
Security Group: sg-app
```

Inbound rule:

| Type       | Port | Source |
| ---------- | ---: | ------ |
| Custom TCP | 5000 | sg-alb |

The application EC2 instances accept traffic only from the Application Load Balancer.

---

## 🔹 Database Security Group

```text
Security Group: sg-db
```

Inbound rule:

| Type         | Port | Source |
| ------------ | ---: | ------ |
| MySQL/Aurora | 3306 | sg-app |

The RDS database accepts MySQL traffic only from the application tier.

---

# 👤 IAM Role

Create an IAM role for the EC2 application instances.

```text
Role Name: EC2-S3-Role
```

The role includes:

```text
AmazonSSMManagedInstanceCore
```

This allows Systems Manager to manage the EC2 instances without requiring public SSH access.

---

# 🗄️ RDS MySQL Database

Create an Amazon RDS MySQL database with:

```text
DB Identifier: three-tier-db
Database Name: appdb
Username: admin
Port: 3306
Public Access: No
```

The database should use the private database subnets.

The RDS instance must not be directly accessible from the public internet.

---

# 🧱 Database Table

Create the application table:

```sql
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

This table stores application messages along with their creation timestamp.

---

# 🐍 Flask Application

The application is developed using Flask.

The application provides the following endpoints:

```text
/
```

Main application page.

```text
/health
```

Application health-check endpoint.

```text
/api/hello
```

API test endpoint.

```text
/api/messages
```

Database-backed messages endpoint.

The Flask application listens on:

```text
0.0.0.0:5000
```

---

# 📦 Application Dependencies

Create a Python virtual environment and install the required dependencies.

Example:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The application uses Gunicorn as the production WSGI server.

Example:

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

---

# 🧪 Application Testing

Test the Flask application locally before deploying it.

Start the application:

```bash
python3 app.py
```

Test the health endpoint:

```bash
curl http://127.0.0.1:5000/health
```

Test the API:

```bash
curl http://127.0.0.1:5000/api/hello
```

Test the database API:

```bash
curl http://127.0.0.1:5000/api/messages
```

---

# 🔑 AWS Secrets Manager

Store database credentials securely in AWS Secrets Manager.

```text
Secret Name: three-tier/rds
```

The application retrieves the database credentials from Secrets Manager instead of storing passwords directly inside the application code.

Do not commit database passwords or secret values to GitHub.

---

# 🪣 Amazon S3

Create a private S3 bucket for application-related storage.

Recommended configuration:

```text
Block Public Access: Enabled
Object Ownership: Bucket Owner Enforced
Versioning: Enabled
Server-Side Encryption: Enabled
```

The S3 bucket should not be publicly accessible.

---

# 🎯 Target Group

Create an Application Load Balancer target group for the application instances.

Application traffic:

```text
ALB
 ↓
Target Group
 ↓
EC2 : 5000
```

Health check configuration:

```text
Protocol: HTTP
Port: Traffic Port
Path: /health
```

The `/health` endpoint is used to determine whether an application instance is healthy.

---

# ⚖️ Application Load Balancer

Create an internet-facing Application Load Balancer.

The ALB should be deployed across the two public subnets.

Listeners:

```text
HTTP  → 80
HTTPS → 443
```

HTTPS traffic terminates at the Application Load Balancer and is forwarded to the application instances on:

```text
TCP 5000
```

Traffic flow:

```text
Internet
   ↓
Application Load Balancer
   ↓
Target Group
   ↓
EC2 Instances
   ↓
Flask + Gunicorn
```

---

# 📈 Auto Scaling Group

Create an Auto Scaling Group:

```text
Name: three-tier-asg
Minimum Capacity: 2
Desired Capacity: 2
Maximum Capacity: 4
```

The EC2 instances are distributed across the private application subnets.

The Auto Scaling Group provides automatic instance replacement when an instance becomes unhealthy or is terminated.

---

# 🖥️ Launch Template

Create a Launch Template containing the configuration required to start the application instances.

The Launch Template should define:

* AMI
* Instance type
* IAM role
* Application Security Group
* User data
* Application startup configuration

The Auto Scaling Group uses this Launch Template to create replacement instances.

---

# 🌐 Route 53

Configure Amazon Route 53 for the application domain.

The domain should point to the Application Load Balancer.

Traffic flow:

```text
User
 ↓
Route 53
 ↓
Application Load Balancer
 ↓
EC2 Application Tier
```

---

# 🔒 AWS Certificate Manager

Create an SSL/TLS certificate using AWS Certificate Manager.

The certificate is associated with the application domain.

Attach the ACM certificate to the HTTPS listener of the Application Load Balancer.

Expected traffic:

```text
HTTPS : 443
   ↓
ALB
   ↓
HTTP : 5000
   ↓
EC2
```

---

# 🛠️ AWS Systems Manager

AWS Systems Manager Session Manager is used to manage private EC2 instances.

This avoids exposing SSH directly to the internet.

The EC2 instance requires the:

```text
AmazonSSMManagedInstanceCore
```

policy through its IAM role.

---

# 📊 Amazon CloudWatch

Configure CloudWatch monitoring for the infrastructure.

Important metrics include:

### EC2

```text
CPU Utilization
```

### Application Load Balancer

```text
Request Count
Target Health
```

### RDS

```text
CPU Utilization
Database Connections
```

CloudWatch can also be used for application and system logs where configured.

---

# 🔔 Amazon SNS

Create an SNS topic for infrastructure notifications.

CloudWatch alarms can publish notifications to the SNS topic.

Example flow:

```text
CloudWatch Alarm
      ↓
SNS Topic
      ↓
Email Notification
```

The email subscription must be confirmed before notifications are received.

---

# 🧪 Application Validation

After deployment, validate the application using the configured domain.

### Homepage

```text
https://<YOUR-DOMAIN>/
```

### Health Check

```text
https://<YOUR-DOMAIN>/health
```

### Hello API

```text
https://<YOUR-DOMAIN>/api/hello
```

### Messages API

```text
https://<YOUR-DOMAIN>/api/messages
```

The endpoints should return successful responses through the Application Load Balancer.

---

# 🗃️ Database Validation

Verify that the application can communicate with the RDS MySQL database.

Check the `messages` table:

```sql
SELECT * FROM messages;
```

Also verify the database-backed API:

```text
/api/messages
```

Successful results confirm connectivity between the application tier and database tier.

---

# 🔁 High Availability Validation

To validate application-tier high availability, terminate one EC2 instance managed by the Auto Scaling Group.

Expected behavior:

```text
EC2 Instance Terminated
        ↓
ASG Detects Capacity Change
        ↓
Replacement Instance Launched
        ↓
Application Starts
        ↓
Target Health Check
        ↓
Target Becomes Healthy
        ↓
ALB Continues Serving Traffic
```

The application should remain available through the Application Load Balancer.

> This test validates application-tier Auto Scaling and resilience. It does not by itself prove that the RDS database is configured as Multi-AZ.

---

# ✅ Deployment Checklist

Use the following checklist before considering the deployment complete.

* [ ] VPC created
* [ ] Public subnets created
* [ ] Private application subnets created
* [ ] Private database subnets created
* [ ] Internet Gateway configured
* [ ] NAT Gateway configured
* [ ] Route tables configured
* [ ] Security Groups configured
* [ ] IAM role created
* [ ] RDS MySQL database created
* [ ] Database table created
* [ ] Flask application configured
* [ ] Gunicorn configured
* [ ] Secrets Manager configured
* [ ] S3 bucket configured
* [ ] Target Group created
* [ ] ALB created
* [ ] HTTPS listener configured
* [ ] ACM certificate attached
* [ ] Auto Scaling Group configured
* [ ] Launch Template configured
* [ ] Route 53 configured
* [ ] Systems Manager configured
* [ ] CloudWatch monitoring configured
* [ ] SNS notifications configured
* [ ] Application endpoints tested
* [ ] Database connectivity tested
* [ ] High Availability test completed

---

# 💻 Useful AWS CLI Commands

Check AWS identity:

```bash
aws sts get-caller-identity
```

Check configured region:

```bash
aws configure get region
```

List EC2 instances:

```bash
aws ec2 describe-instances --region ap-south-1
```

Check Auto Scaling Groups:

```bash
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names three-tier-asg \
  --region ap-south-1
```

Check target health:

```bash
aws elbv2 describe-target-health \
  --target-group-arn <TARGET-GROUP-ARN> \
  --region ap-south-1
```

Check RDS:

```bash
aws rds describe-db-instances \
  --db-instance-identifier three-tier-db \
  --region ap-south-1
```

Check Secrets Manager:

```bash
aws secretsmanager describe-secret \
  --secret-id three-tier/rds \
  --region ap-south-1
```

---

# 🔐 Security and Deployment Notes

Do not commit sensitive information to GitHub.

Never upload:

```text
Passwords
AWS Access Keys
AWS Secret Keys
Private Keys
.env files
Database Credentials
Secrets Manager Secret Values
```

Keep the RDS database configured with:

```text
Public Access: No
```

Do not expose application EC2 instances directly to the internet.

Expected application traffic flow:

```text
Internet
   ↓
Route 53
   ↓
Application Load Balancer
   ↓
EC2 Application Tier
   ↓
RDS MySQL
```

The application instances remain inside private subnets.

---

# 🏛️ Final Architecture

The final architecture follows a three-tier design:

```text
                         Internet
                            │
                            ▼
                       Route 53
                            │
                            ▼
                  Application Load Balancer
                       │          │
                       ▼          ▼
                  Private App Subnets
                    │           │
                    ▼           ▼
                 EC2 + ASG   EC2 + ASG
                    │           │
                    └─────┬─────┘
                          │
                          ▼
                    RDS MySQL
                  Private DB Tier

          Private EC2 → NAT Gateway → Internet

Additional Services:
S3 • Secrets Manager • IAM • ACM
Systems Manager • CloudWatch • SNS
```

The architecture separates the application into network tiers while using load balancing, Auto Scaling, private subnets, database isolation, monitoring, and managed AWS services.
