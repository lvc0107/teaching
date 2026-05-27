# Minimal FastAPI microservice to practice deployment pipelines.

## Endpoints

| Method | Route     | Description                                      |
|--------|-----------|--------------------------------------------------|
| GET    | `/`       | Hello World + environment info                   |
| GET    | `/ping`   | Returns how many times this endpoint was invoked |
| GET    | `/health` | Health check (used by GitHub Actions and LBs)    |

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

1.1. Go to **ECR → Repositories**
1.2. Click **Create repository**
1.3. Name: `teaching/ecr_deploy1`
1.4. Default configuration is fine
1.5. Note the **Repository URI** (e.g., `123456789.dkr.ecr.us-east-1.amazonaws.com/teaching/ecr_deploy1`)

### 2. Create IAM User for GitHub Actions

2.1. Go to **IAM → Users → Create user**
2.2. Name: `github-actions`
2.3. Uncheck "Provide user access to the AWS Management Console"
2.4. Click **Next**
2.5. Click **Create policy** with the following JSON:
(Or edit the policy after creating the user and attach it to the user: Add permissions → Create inline policy → JSON)

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
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "arn:aws:ecr:us-east-2:099554283130:repository/teaching/ecr_deploy1"
    }
  ]
}
```

2.6. Save and return to Users
2.7. Select the `github-actions` user and go to **Security credentials**
2.8. Click **Create access key** → **Command Line Interface**
2.9. **Copy and save** the `Access Key ID` and `Secret Access Key`
2.10. copy the `Access Key ID` and `Secret Access Key` to GitHub Secrets (see step 6 below)

### 3. Create EC2 Instance

3.1. Go to **EC2 → Instances → Launch instances**
3.2. Name: `deploy1-ec2` 
3.3. **AMI**: Amazon Linux 2023 (free tier) 
3.4. **Instance type**: `t2.micro` (free tier) 
3.5. **Key pair**: Create a new one (save the `.pem` file) 
    name: ec2-key-pair-for-deploy1
3.6. **Network settings**: Keep default VPC
3.7. **Firewall (security groups)**: Create security group with inbound rules (see step 5 below)
3.8. Click **Launch instance**

### 4. Create IAM Role for EC2

4.1. Go to **IAM → Roles → Create role**
4.2. Service: `EC2`
4.3. Create policy for EC2:
  name: `ec2-ecr-pull-policy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    }
  ]
}
```

4.4. Name: `ec2-hello-deploy-role`
4.5. Go to **EC2 → Instances** → select your instance
4.6. **Actions -> Security → Modify IAM instance profile** → select the created role

### 5. Configure Security Group

5.1. In **EC2 → Security Groups** (associated with your instance)
5.2. Click **Edit inbound rules**
5.3. Add:
- **Port 8000** (TCP) from anywhere (`0.0.0.0/0`) - for the app
- **Port 3000** (TCP) from anywhere (`0.0.0.0/0`) - for the app
- **Port 443** (TCP) from anywhere (`0.0.0.0/0`) - for the app
- **Port 22** (SSH) from your IP - for deployment

---

## 6. Required GitHub Secrets

6.1 Configure in **Repo-> Settings → Environments → DEV → Secrets**:

| Secret                  | Value                                |
|-------------------------|--------------------------------------|
| `AWS_ACCESS_KEY_ID`     | From IAM user `github-actions`       |
| `AWS_SECRET_ACCESS_KEY` | From IAM user `github-actions`       |
| `EC2_HOST`              | Public IP or DNS of the EC2 instance |
| `EC2_USER`              | `ec2-user` (Amazon Linux 2023)       |
| `EC2_SSH_KEY`           | Full contents of the `.pem` file     |

| Environment  | Value                        |
|--------------|------------------------------|
| `AWS_REGION` | `us-east-2` (or your region) |

> `BACKEND_REPOSITORY_NAME` and `FRONTEND_REPOSITORY_NAME` are configured in `.github/deploy-dev.yml` and do not need to
> be stored as secrets.

---

---

## 7. GitHub Actions Workflow

The file [.github/deploy-dev.yml](.github/deploy-dev.yml) should contain:

7.1. **Trigger**: Push to `main` branch
7.2. **Build**: Build the backend and frontend Docker images from `backend/` and `frontend/`
7.3. **Push**: Push both images to ECR
7.4. **Deploy**: SSH to EC2 and run both containers in the same Docker network so both services share the same host/VPC

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

**Note**: The EC2 instance needs an **IAM Instance Profile** with `ecr:GetAuthorizationToken` and `ecr:BatchGetImage`
permissions to pull from ECR without hardcoded credentials.

---

## Future Environments

| Branch / Tag | Environment | Status                  |
|--------------|-------------|-------------------------|
| `main`       | DEV         | ✅ Implemented           |
| `release/*`  | QA          | 🔜 Coming soon          |
| tag `uat-*`  | UAT         | 🔜 Coming soon          |
| tag `v*.*.*` | PROD        | 🔜 With manual approval |


NGINX: hide ports: to keep it leaves your services vulnerable to attacks
also: Primary benefit to the reverse proxy is that it can let you have MANY hosts behind port 443 and manage the host redirection / certs etc.

No Encryption (SSL/TLS): Direct connections pass traffic, including passwords, in plaintext. A reverse proxy handles Let's Encrypt SSL/TLS termination securely.
Vulnerability Disclosure: Exposing specific app ports allows scanners to identify your exact software stack and version. This lets attackers target known CVEs directly How to Secure Your Nginx Server.
Lack of Rate Limiting & Bot Protection: Without NGINX, a single angry bot or DDoS attack can easily overwhelm and crash your backend application Nginx + Docker: Stop Exposing Your App Ports to the World.
Missing Compression: Proxies compress outgoing data, saving bandwidth and improving load times.
```

Internet
   ↓ (Port 80 / 443)
Nginx
   ├── /           → Frontend (Svelte)
   └── /api/       → Backend (FastAPI)
```


1. Connect via ssh to the EC2 instance and run:
```
ssh -i "path/to/your/ec2-key-pair-for-deploy1.pem" ec2-user@your-ec2-public-ip
```

2. Install Nginx and configure it as a reverse proxy to forward requests from port 80/443 to your backend and frontend services running on ports 8000 and 3000, respectively.

   ```
    sudo dnf update -y
    sudo dnf install -y nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    # Allow Nginx in the firewall (Amazon Linux 2023)
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
    # Updates ports in the Amazon Linux 2023 firewall
    sudo dnf install -y iptables-services
    sudo systemctl start iptables
    sudo systemctl enable iptables
    # Open HTTP y HTTPS ports
    sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    # Save the rules
    sudo iptables-save | sudo tee /etc/sysconfig/iptables
    # Verify that Nginx is running
    sudo systemctl status nginx
    curl -I http://localhost
    # 1. Check if Nginx is listening in all interfaces
    sudo ss -ltnp | grep nginx
    # 2. See the current iptables rules
    sudo iptables -L -n -v
    # 3. Test if you can access Nginx locally (should return HTTP 200 or 403, but not connection refused)
    curl -I http://localhost
    # Clean up iptables rules (if needed) and allow only HTTP, HTTPS and SSH
    sudo iptables -F
    sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    sudo iptables-save | sudo tee /etc/sysconfig/iptables
   ```

3. Configure Nginx to serve the frontend on `/` and proxy API requests starting with `/api/` to the backend.
```
sudo vim /etc/nginx/conf.d/default.conf
``` 
Apply the following configuration:

```nginx
server {
    listen 80;
    server_name _;   # Change later to your domain

    # Frontend (Svelte/Vite)
    root /var/www/frontend/dist;     # We'll copy the build here
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check for backend
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
``` 

Apply the changes and restart Nginx:
```
   sudo nginx -t
   sudo systemctl restart nginx
```

4. Update your Docker containers
We should change the containers so they don't expose ports publicly anymore:
```
Backend: Remove -p 8000:8000
Frontend: Remove -p 3000:3000
```