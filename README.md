# ChefGPT2 — Sistema de Logging Distribuido en AWS

Proyecto académico desplegado en AWS que implementa una arquitectura de microservicios para la emisión y consulta de logs en tiempo real, usando FastAPI, RabbitMQ, MongoDB y un Application Load Balancer, todo aprovisionado con OpenTofu (Terraform).

---

## Arquitectura

```
Cliente HTTP
     │
     ▼
Application Load Balancer (ALB)
     │
  ┌──┴──┐
  ▼     ▼
API 1  API 2        ← FastAPI (EC2 t2.micro × 2)
  │
  ▼
RabbitMQ            ← Fanout Exchange "logs" (EC2 t2.micro)
  │
  ▼
Worker              ← Consumidor RabbitMQ → MongoDB (EC2 t2.micro)
  │
  ▼
MongoDB             ← Almacenamiento de logs (EC2 t2.micro)

SSM Parameter Store ← IPs de RabbitMQ, MongoDB y DNS del ALB
```

Todos los componentes leen su configuración desde **AWS SSM Parameter Store**, eliminando IPs hardcodeadas en el código.

---

## Componentes

| Componente | Tecnología | Tipo AWS |
|---|---|---|
| API (×2) | FastAPI + Uvicorn | EC2 t2.micro |
| Message Broker | RabbitMQ | EC2 t2.micro |
| Worker | Python + Pika | EC2 t2.micro |
| Base de datos | MongoDB | EC2 t2.micro |
| Load Balancer | Application Load Balancer | ALB |
| Configuración | AWS SSM Parameter Store | — |

---

## Endpoints

Base URL: `http://<ALB-DNS>/`

### `GET /`
Health check del servicio.

**Response:**
```json
{ "status": "ok", "service": "RabbitMQ Logger API" }
```

---

### `POST /logs`
Emite un mensaje al exchange fanout de RabbitMQ. El worker lo consume y lo persiste en MongoDB.

**Body:**
```json
{ "message": "Tu mensaje de log aquí" }
```

**Response:**
```json
{ "status": "sent", "message": "Tu mensaje de log aquí" }
```

---

### `GET /logs`
Consulta todos los logs almacenados en MongoDB.

**Response:**
```json
{
  "total": 3,
  "logs": [
    { "message": "log 1", "timestamp": null },
    { "message": "log 2", "timestamp": null }
  ]
}
```

---

### `DELETE /logs`
Elimina todos los logs de la colección en MongoDB.

**Response:**
```json
{ "deleted": 3 }
```

---

## Flujo del Pipeline

1. El cliente hace `POST /logs` al ALB con un JSON `{ "message": "..." }`
2. El ALB balancea la petición entre las dos instancias de API
3. La API publica el mensaje al **exchange fanout** `logs` en RabbitMQ
4. El **Worker** consume la cola ligada al exchange y persiste el log en MongoDB
5. El cliente puede verificar con `GET /logs` que el mensaje fue guardado

---

## Estructura del Repositorio

```
ChefGPT2/
├── api.py               # FastAPI: endpoints GET/POST/DELETE /logs
├── worker.py            # Consumidor RabbitMQ → MongoDB
├── test_api.py          # Tests de integración con pytest
├── Dockerfile           # Imagen Docker para la API
├── docker-compose.yml   # Stack local (API + RabbitMQ + MongoDB)
├── emit_logs.py         # Script de prueba para emitir logs
├── receive_logs.py      # Script de prueba para recibir logs
└── terraform/
    ├── main.tf          # 18 recursos: EC2s, ALB, Target Group, SSM
    ├── security_groups.tf
    ├── variables.tf
    ├── outputs.tf
    ├── providers.tf
    └── scripts/         # User data scripts para cada EC2
```

---

## Despliegue en AWS (OpenTofu)

### Requisitos previos
- [OpenTofu](https://opentofu.org/) instalado (o Terraform ≥ 1.5)
- AWS CLI configurado con credenciales válidas (`aws configure`)
- Permisos IAM: EC2, SSM, ELB, VPC

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/JACardonaMorales/ChefGPT2.git
cd ChefGPT2/terraform

# 2. Inicializar OpenTofu
tofu init

# 3. Revisar el plan de infraestructura
tofu plan

# 4. Desplegar (18 recursos)
tofu apply

# 5. Obtener el DNS del ALB desde los outputs
tofu output alb_dns_name
```

### Limpiar infraestructura

```bash
tofu destroy
```

> ⚠️ En AWS Academy, las credenciales expiran cada ~4 horas. Si el lab se reinicia, elimina `terraform.tfstate`, actualiza las credenciales en `~/.aws/credentials` y corre `tofu apply` de nuevo.

---

## Ejecución local (Docker Compose)

```bash
# Levantar stack local
docker compose up --build

# La API quedará disponible en http://localhost:8000
# Documentación interactiva: http://localhost:8000/docs
```

---

## Tests

```bash
pip install pytest httpx
pytest test_api.py -v
```

---

## SSM Parameter Store — Parámetros usados

| Parámetro | Descripción |
|---|---|
| `/chefgpt/dev/rabbitmq/public_ip` | IP pública de la instancia RabbitMQ |
| `/chefgpt/dev/mongodb/public_ip` | IP pública de la instancia MongoDB |
| `/chefgpt/dev/alb/dns_name` | DNS del Application Load Balancer |

---

## Tecnologías

- **FastAPI** — Framework web async para Python
- **RabbitMQ** — Message broker con fanout exchange
- **MongoDB** — Base de datos NoSQL para persistencia de logs
- **AWS EC2** — Cómputo en la nube
- **AWS ALB** — Balanceo de carga entre instancias de API
- **AWS SSM Parameter Store** — Gestión centralizada de configuración
- **OpenTofu / Terraform** — Infraestructura como código
- **Docker / Docker Compose** — Contenedores para desarrollo local
