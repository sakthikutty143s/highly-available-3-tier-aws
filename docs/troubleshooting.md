# 🔧 Troubleshooting Guide

## 📌 1. Overview

This document provides troubleshooting steps for common issues in the **Highly Available 3-Tier Web Application on AWS**.

The troubleshooting process mainly covers:

* Application availability
* ALB health checks
* EC2 connectivity
* Auto Scaling
* RDS connectivity
* Security Groups
* DNS
* HTTPS
* Secrets Manager
* S3
* Systems Manager
* CloudWatch

---

## ⚖️ 2. ALB Target Shows Unhealthy

### Problem

The EC2 instance appears as **Unhealthy** in the ALB Target Group.

### Check

Verify that the Flask application is running.

```bash
sudo systemctl status your-application
```

Check whether port `5000` is listening:

```bash
sudo ss -tulpn | grep 5000
```

Test the application locally:

```bash
curl http://localhost:5000
```

### Verify Security Group

The EC2 Security Group must allow:

```text
Port   : 5000
Source : ALB Security Group
```

### Verify Health Check

Check:

* Health check protocol
* Health check port
* Health check path
* Target response

The health-check path must return a successful HTTP response.

---

## 🖥️ 3. EC2 Application Not Starting

### Problem

The Flask application does not start after the EC2 instance launches.

### Check Application Logs

```bash
sudo journalctl -u your-application
```

Check the application files:

```bash
ls
```

Verify Python:

```bash
python3 --version
```

Verify dependencies:

```bash
pip3 list
```

### Check Gunicorn

Verify that Gunicorn is installed:

```bash
gunicorn --version
```

Test the application manually:

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

---

## 🔌 4. Port 5000 Not Accessible

### Problem

The ALB cannot connect to the Flask application.

### Check

Verify that the application listens on:

```text
0.0.0.0:5000
```

instead of:

```text
127.0.0.1:5000
```

Check the Security Group:

```text
EC2 Security Group
TCP 5000
Source: ALB Security Group
```

Do not open port `5000` to the entire internet unless specifically required for testing.

---

## 🗄️ 5. RDS Connection Failed

### Problem

The Flask application cannot connect to MySQL.

### Check RDS

Verify:

```text
RDS Status : Available
Port       : 3306
Public     : No
```

### Check Security Group

The RDS Security Group should allow:

```text
TCP 3306
Source: Application Security Group
```

### Check Database Credentials

Verify the credentials stored in:

```text
AWS Secrets Manager
```

Confirm that the application is reading the correct secret.

---

## 🔑 6. Secrets Manager Access Error

### Problem

The application cannot retrieve the database secret.

### Check IAM Role

Verify that the EC2 instance has the correct IAM Role attached.

Check whether the role has the required Secrets Manager permissions.

### Check Secret Name

Verify:

```text
three-tier/rds
```

### Check Region

Ensure the application is using the same AWS Region where the secret is stored.

---

## 🛠️ 7. Session Manager Not Connecting

### Problem

The EC2 instance does not appear as available in Systems Manager.

### Check IAM Role

The EC2 instance requires the appropriate Systems Manager permissions.

### Check SSM Agent

Verify the SSM Agent status:

```bash
sudo systemctl status amazon-ssm-agent
```

Restart if required:

```bash
sudo systemctl restart amazon-ssm-agent
```

### Check Network Connectivity

Private EC2 instances require network connectivity to the required Systems Manager endpoints.

Verify the private subnet routing and required VPC connectivity.

---

## 🌐 8. Website Not Opening

### Problem

The application domain does not open in the browser.

### Check DNS

Verify the Route 53 record points to the correct ALB.

```text
Domain
  |
  v
Route 53
  |
  v
ALB
```

### Check ALB

Verify:

* ALB state is Active
* Listener is configured
* Target group contains healthy targets

### Check HTTPS

Verify that the ACM certificate is attached to the HTTPS listener.

---

## 🔒 9. HTTPS Certificate Problem

### Problem

The browser shows an SSL/TLS certificate error.

### Check

Verify:

* ACM certificate status
* Certificate domain name
* Certificate region
* ALB HTTPS listener
* DNS configuration

For an ALB, the certificate must be available in the same AWS Region as the load balancer.

---

## 📈 10. Auto Scaling Not Launching Instances

### Problem

The Auto Scaling Group does not launch a replacement instance.

### Check

Verify:

```text
Minimum Capacity : 2
Desired Capacity : 2
Maximum Capacity : 4
```

Check:

* Auto Scaling Group activity history
* Launch Template
* IAM instance profile
* Subnet configuration
* Security Group
* Instance health

The application subnets should exist across the configured Availability Zones.

---

## 🧪 11. EC2 Instance Failed

### Problem

An EC2 instance becomes unhealthy or terminates.

### Expected Behavior

```text
EC2 Failure
    |
    v
ALB detects unhealthy target
    |
    v
Traffic continues to healthy instance
    |
    v
Auto Scaling detects capacity change
    |
    v
Replacement EC2 launched
    |
    v
New target becomes healthy
```

If replacement does not occur, check the Auto Scaling Group activity history and launch configuration.

---

## 🪣 12. S3 Access Denied

### Problem

The application receives an `AccessDenied` error while accessing S3.

### Check IAM Role

Verify that the EC2 instance has the required IAM Role.

### Check Bucket Policy

Verify that the bucket policy does not block the required operation.

### Check S3 Configuration

Verify:

* Bucket exists
* Correct AWS Region
* Block Public Access configuration
* Encryption configuration
* Object permissions

Application access should use IAM-based authentication rather than public bucket access.

---

## 🌍 13. Private EC2 Has No Internet Access

### Problem

The private EC2 instance cannot download packages or reach external services.

### Check Route Table

The private application subnet should have a route:

```text
0.0.0.0/0
      |
      v
NAT Gateway
```

### Check NAT Gateway

Verify:

* NAT Gateway is available
* NAT Gateway is deployed in a public subnet
* Public subnet has a route to the Internet Gateway
* NAT Gateway has a public Elastic IP

---

## 🔐 14. Security Group Connection Problem

### Problem

One AWS service cannot communicate with another service.

### Verify the Traffic Flow

Application traffic:

```text
ALB
 |
 | TCP 5000
 v
EC2
```

Database traffic:

```text
EC2
 |
 | TCP 3306
 v
RDS
```

Make sure the destination Security Group allows traffic from the correct source Security Group.

---

## 📊 15. CloudWatch Alarm Not Triggering

### Problem

A CloudWatch alarm does not change state.

### Check

Verify:

* Correct metric
* Correct resource
* Threshold value
* Evaluation period
* Alarm state
* SNS topic
* SNS subscription

Test the SNS email subscription if required.

---

## 📧 16. SNS Email Not Received

### Problem

CloudWatch alarm triggers but email is not received.

### Check

Verify that the SNS email subscription is confirmed.

Check the email inbox and spam folder.

The SNS subscription must be in a confirmed state before notifications can be delivered.

---

## 🧭 17. Troubleshooting Order

When the application is unavailable, troubleshoot in this order:

```text
1. DNS
   |
   v
2. ALB
   |
   v
3. Target Group
   |
   v
4. EC2
   |
   v
5. Flask / Gunicorn
   |
   v
6. Security Groups
   |
   v
7. RDS
   |
   v
8. Secrets Manager
```

This helps identify the failed layer without changing multiple configurations at the same time.

---

## 📝 18. Useful Commands

### Check Application Port

```bash
sudo ss -tulpn | grep 5000
```

### Test Local Application

```bash
curl http://localhost:5000
```

### Check SSM Agent

```bash
sudo systemctl status amazon-ssm-agent
```

### Check Gunicorn

```bash
gunicorn --version
```

### Check Application Logs

```bash
sudo journalctl -u your-application
```

### Check System Logs

```bash
sudo journalctl -xe
```

---

## ✅ 19. Final Troubleshooting Checklist

* [ ] DNS record points to the correct ALB
* [ ] ALB is active
* [ ] Target Group targets are healthy
* [ ] EC2 instances are running
* [ ] Flask application is running
* [ ] Gunicorn is running
* [ ] Port `5000` is listening
* [ ] ALB Security Group is correct
* [ ] Application Security Group is correct
* [ ] RDS is available
* [ ] RDS port `3306` is allowed from the application Security Group
* [ ] Secrets Manager secret is available
* [ ] EC2 IAM Role is attached
* [ ] SSM Agent is running
* [ ] NAT Gateway is available
* [ ] Route tables are correctly configured
* [ ] ACM certificate is active
* [ ] CloudWatch alarms are configured
* [ ] SNS subscription is confirmed

---

## 🎯 20. Troubleshooting Goal

The goal of this troubleshooting guide is to identify failures layer by layer:

```text
User
 |
 v
DNS
 |
 v
ALB
 |
 v
EC2 / Application
 |
 v
RDS
 |
 v
Supporting AWS Services
```

By following this flow, application, networking, security, database, and AWS service issues can be isolated systematically.
