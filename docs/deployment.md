# 🚀 Deployment Guide

This guide explains the deployment process for the Highly Available 3-Tier Web Application on AWS.

## 🏗️ Deployment Architecture

The application is deployed using a highly available 3-tier architecture:

* **Web Layer:** Application Load Balancer
* **Application Layer:** EC2 instances managed by Auto Scaling
* **Database Layer:** Amazon RDS MySQL
* **Storage:** Amazon S3
* **CDN:** Amazon CloudFront
* **DNS:** Amazon Route 53
* **SSL:** AWS Certificate Manager
* **Secrets:** AWS Secrets Manager
* **Monitoring:** Amazon CloudWatch
* **Notifications:** Amazon SNS

## ⚙️ Prerequisites

Before deployment, make sure the following are available:

* AWS Account
* AWS CLI configured
* Git and GitHub
* Python 3.x
* Flask
* MySQL
* EC2 Key Pair
* Required IAM permissions

## 🌐 Step 1: Create VPC

Create a VPC with a CIDR block such as:

```text
10.0.0.0/16
```

Create public and private subnets across multiple Availability Zones.

The public subnets are used for the Load Balancer, while private subnets are used for application and database resources.

## 🔐 Step 2: Configure Security Groups

Create separate security groups for:

* Application Load Balancer
* EC2 Application Servers
* RDS MySQL

Allow only the required traffic between each layer.

## 🖥️ Step 3: Deploy EC2 Application

Launch Ubuntu EC2 instances in the private application subnets.

Install the required packages:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

Clone the application repository:

```bash
git clone <YOUR-GITHUB-REPOSITORY>
cd <PROJECT-DIRECTORY>
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application using Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## ⚖️ Step 4: Configure Application Load Balancer

Create an Application Load Balancer in the public subnets.

Configure:

* Listener: HTTP/HTTPS
* Target Group: EC2 instances
* Health Check Path: `/`
* Application Port: `5000`

Verify that the registered targets become healthy.

## 📈 Step 5: Configure Auto Scaling

Create an Auto Scaling Group using the application EC2 configuration.

Configure:

* Minimum instances
* Desired instances
* Maximum instances
* Multiple Availability Zones
* Target tracking policy

Example CPU target:

```text
Target CPU Utilization: 60%
```

## 🗄️ Step 6: Configure RDS MySQL

Create an Amazon RDS MySQL database inside the private database subnets.

Configure:

* Engine: MySQL
* Database: `appdb`
* Private access
* Port: `3306`
* Database Security Group

The database should not be publicly accessible.

## 🔑 Step 7: Configure Secrets Manager

Store database credentials securely in AWS Secrets Manager.

Example secret values:

```text
DB_HOST
DB_USER
DB_PASSWORD
DB_NAME
DB_PORT
```

The application retrieves the credentials securely instead of storing passwords directly in the source code.

## 🪣 Step 8: Configure Amazon S3

Create an S3 bucket for application objects or static files.

Configure the required IAM permissions for the application role.

Avoid making the bucket publicly accessible unless public access is specifically required.

## 🌍 Step 9: Configure CloudFront

Create a CloudFront distribution for the application.

Configure the Application Load Balancer as the origin.

Enable HTTPS using the appropriate ACM certificate.

## 🔗 Step 10: Configure Route 53

Create a Route 53 hosted zone for the domain.

Create an appropriate DNS record pointing the domain to CloudFront.

Example:

```text
sakthisuri.online
```

## 🔒 Step 11: Configure HTTPS

Use AWS Certificate Manager to create an SSL/TLS certificate.

Validate the domain and attach the certificate to CloudFront.

The application can then be accessed securely using HTTPS.

## 📊 Step 12: Configure Monitoring

Use Amazon CloudWatch to monitor:

* EC2 CPU utilization
* ALB request metrics
* Target health
* RDS CPU utilization
* RDS connections
* Application performance

Configure SNS notifications for important alarms.

## ✅ Step 13: Verify Deployment

After deployment, verify:

```text
Route 53
   ↓
CloudFront
   ↓
Application Load Balancer
   ↓
Auto Scaling EC2
   ↓
RDS MySQL
```

Test the application URL and verify database connectivity, S3 functionality, HTTPS, health checks, and Auto Scaling.
