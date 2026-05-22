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

### With Docker Compose (recommended)
```bash
docker compose up --build
```

Then open:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

### Backend only

```bash
cd backend

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

### Frontend only

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build
```

Then open: http://localhost:5173

---

## AWS Console Setup (step-by-step)

### 1. Create ECR Repository

1. Go to **ECR → Repositories**
2. Click **Create repository**
3. Name: `teaching/ecr_deploy1`
4. Default configuration is fine
5. Note the **Repository URI** (e.g., `123456789.dkr.ecr.us-east-1.amazonaws.com/teaching/ecr_deploy1`)


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
      "Resource": "arn:aws:ecr:*:ACCOUNT_ID:repository/ecr_deploy1"
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
| `AWS_REGION`            | `us-east-1` (or your region)                   |
| `EC2_HOST`              | Public IP or DNS of the EC2 instance           |
| `EC2_USER`              | `ec2-user` (Amazon Linux 2023)                 |
| `EC2_SSH_KEY`           | Full contents of the `.pem` file               |

> `BACKEND_REPOSITORY_NAME` and `FRONTEND_REPOSITORY_NAME` are configured in `.github/deploy-dev.yml` and do not need to be stored as secrets.

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
  "Resource": "arn:aws:ecr:*:ACCOUNT_ID:repository/ecr_deploy1"
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
2. **Build**: Build the backend and frontend Docker images from `backend/` and `frontend/`
3. **Push**: Push both images to ECR
4. **Deploy**: SSH to EC2 and run both containers in the same Docker network so both services share the same host/VPC
   ```bash
   aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com
   docker pull $BACKEND_IMAGE_URI
   docker pull $FRONTEND_IMAGE_URI
   docker stop backend-container || true
   docker rm backend-container || true
   docker stop frontend-container || true
   docker rm frontend-container || true
   docker network create hello-deploy-network || true
   docker run -d --name backend-container --network hello-deploy-network -p 8000:8000 $BACKEND_IMAGE_URI
   docker run -d --name frontend-container --network hello-deploy-network -p 3000:3000 $FRONTEND_IMAGE_URI
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
