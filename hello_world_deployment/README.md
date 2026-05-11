# hello-deploy

Minimal FastAPI microservice to practice deployment pipelines.

## Endpoints

| Method | Route     | Description                                       |
|--------|-----------|---------------------------------------------------|
| GET    | `/`       | Hello World + environment info                    |
| GET    | `/ping`   | Returns how many times this endpoint was invoked  |
| GET    | `/health` | Health check (used by GitHub Actions and LBs)     |

---

## Run locally

```bash
# With Docker
docker build -t hello-deploy .
docker run -p 8000:8000 hello-deploy

# With UV
uv sync
uv run uvicorn main:app --reload

# Without Docker (pip)
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open: http://localhost:8000/docs

---

## AWS Console Setup (step-by-step)

### 1. Create ECR Repository

1. Go to **ECR → Repositories**
2. Click **Create repository**
3. Name: `teaching/deploy1`
4. Default configuration is fine
5. Note the **Repository URI** (e.g., `123456789.dkr.ecr.us-east-1.amazonaws.com/teaching/deploy1`)

### 2. Create IAM User for GitHub Actions

1. Go to **IAM → Users → Create user**
2. Name: `github-actions`
3. Uncheck "Provide user access to the AWS Management Console"
4. Click **Next**
5. Click **Create policy** with the following JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "arn:aws:ecr:*:ACCOUNT_ID:repository/deploy1"
    }
  ]
}
```

6. Save and return to Users
7. Select the `github-actions` user and go to **Security credentials**
8. Click **Create access key** → **Command Line Interface**
9. **Copy and save** the `Access Key ID` and `Secret Access Key`

### 3. Create EC2 Instance

1. Go to **EC2 → Instances → Launch instances**
2. **AMI**: Amazon Linux 2023 (free tier)
3. **Instance type**: `t2.micro` (free tier)
4. **Key pair**: Create a new one (save the `.pem` file)
5. **Network settings**: Keep default VPC
6. **Firewall (security groups)**: Create security group with inbound rules (see step 5 below)
7. Click **Launch instance**

### 4. Create IAM Role for EC2

1. Go to **IAM → Roles → Create role**
2. Service: `EC2`
3. Create policy for EC2:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer"
      ],
      "Resource": "*"
    }
  ]
}
```

4. Name: `ec2-hello-deploy-role`
5. Go to **EC2 → Instances** → select your instance
6. **Security → Modify IAM instance profile** → select the created role

### 5. Configure Security Group

1. In **EC2 → Security Groups** (associated with your instance)
2. Click **Edit inbound rules**
3. Add:
   - **Port 8000** (TCP) from anywhere (`0.0.0.0/0`) - for the app
   - **Port 22** (SSH) from your IP - for deployment

---

## Required GitHub Secrets

Configure in **Settings → Environments → DEV → Secrets**:

| Secret                  | Value                                          |
|-------------------------|------------------------------------------------|
| `AWS_ACCESS_KEY_ID`     | From IAM user `github-actions`                 |
| `AWS_SECRET_ACCESS_KEY` | From IAM user `github-actions`                 |
| `AWS_ECR_REGISTRY`      | `123456789.dkr.ecr.us-east-1.amazonaws.com`   |
| `AWS_REGION`            | `us-east-1` (or your region)                   |
| `ECR_REPOSITORY_NAME`   | `deploy1`                                 |
| `EC2_HOST`              | Public IP or DNS of the EC2 instance           |
| `EC2_USER`              | `ec2-user` (Amazon Linux 2023)                 |
| `EC2_SSH_KEY`           | Full contents of the `.pem` file               |

---

---

## Minimum Required IAM Permissions (reference)

**For GitHub Actions (ECR Push)**:
```json
{
  "Effect": "Allow",
  "Action": [
    "ecr:GetAuthorizationToken",
    "ecr:BatchCheckLayerAvailability",
    "ecr:PutImage",
    "ecr:InitiateLayerUpload",
    "ecr:UploadLayerPart",
    "ecr:CompleteLayerUpload"
  ],
  "Resource": "arn:aws:ecr:*:ACCOUNT_ID:repository/hello-deploy"
}
```

**For EC2 (ECR Pull)**:
```json
{
  "Effect": "Allow",
  "Action": [
    "ecr:GetAuthorizationToken",
    "ecr:BatchGetImage",
    "ecr:GetDownloadUrlForLayer"
  ],
  "Resource": "*"
}
```

---

## GitHub Actions Workflow

The file [.github/deploy-dev.yml](.github/deploy-dev.yml) should contain:

1. **Trigger**: Push to `main` branch
2. **Build**: Build Docker image
3. **Push**: Push to ECR
4. **Deploy**: SSH to EC2 and run:
   ```bash
   aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ECR_REGISTRY
   docker pull $AWS_ECR_REGISTRY/$ECR_REPOSITORY_NAME:latest
   docker stop hello-deploy || true
   docker rm hello-deploy || true
   docker run -d -p 8000:8000 --name hello-deploy $AWS_ECR_REGISTRY/$ECR_REPOSITORY_NAME:latest
   ```

---

## EC2 Setup (one-time)

```bash
# Amazon Linux 2023
sudo yum update -y
sudo yum install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Logout and login again for ec2-user to have docker permissions
```

**Note**: The EC2 instance needs an **IAM Instance Profile** with `ecr:GetAuthorizationToken` and `ecr:BatchGetImage` permissions to pull from ECR without hardcoded credentials.

---

## Future Environments

| Branch / Tag | Environment | Status                    |
|--------------|-------------|---------------------------|
| `main`       | DEV         | ✅ Implemented            |
| `release/*`  | QA          | 🔜 Coming soon            |
| tag `uat-*`  | UAT         | 🔜 Coming soon            |
| tag `v*.*.*` | PROD        | 🔜 With manual approval   |
