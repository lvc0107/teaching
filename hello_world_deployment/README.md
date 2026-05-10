# hello-deploy

Microservicio mínimo en FastAPI para practicar pipelines de deployment.

## Endpoints

| Método | Ruta      | Descripción                                      |
|--------|-----------|--------------------------------------------------|
| GET    | `/`       | Hello World + info del entorno                   |
| GET    | `/ping`   | Retorna cuántas veces fue invocado este endpoint |
| GET    | `/health` | Health check (usado por GitHub Actions y LBs)    |

---

## Correr localmente

```bash
# Con docker-compose
docker-compose up --build

# Sin Docker
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Luego abrir: http://localhost:8000/docs

---

## Secrets requeridos en GitHub

Configurar en **Settings → Environments → DEV → Secrets**:

| Secret                  | Valor                                          |
|-------------------------|------------------------------------------------|
| `AWS_ACCESS_KEY_ID`     | Access key de un IAM user con permisos ECR+EC2 |
| `AWS_SECRET_ACCESS_KEY` | Secret key del mismo IAM user                  |
| `EC2_HOST`              | IP pública o DNS de la instancia EC2           |
| `EC2_USER`              | `ec2-user` (Amazon Linux) o `ubuntu` (Ubuntu)  |
| `EC2_SSH_KEY`           | Contenido completo del archivo `.pem`          |

---

## Permisos IAM mínimos necesarios

El usuario IAM de GitHub Actions necesita estas policies:

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
  "Resource": "*"
}
```

## Setup EC2 (una sola vez)

```bash
# Amazon Linux 2023
sudo yum update -y
sudo yum install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# Instalar AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install
```

La instancia EC2 necesita un **Instance Profile** (IAM Role) con permisos de `ecr:GetAuthorizationToken` y `ecr:BatchGetImage` para poder hacer pull desde ECR sin credenciales hardcodeadas.

---

## Entornos futuros

| Branch / Tag | Environment | Notas                    |
|--------------|-------------|--------------------------|
| `main`       | DEV         | ✅ Implementado           |
| `release/*`  | QA          | 🔜 Próximo               |
| tag `uat-*`  | UAT         | 🔜 Próximo               |
| tag `v*.*.*` | PROD        | 🔜 Con aprobación manual |
