# 🎭 Shaky: Julius Caesar RAG Application

**Shaky** is an End-to-End MLOps project that deploys a **Retrieval-Augmented Generation (RAG)** system capable of answering complex questions about Shakespeare's *Julius Caesar*.

It leverages **Google Gemini** for generation, **FAISS** for vector retrieval, and a fully automated **CI/CD pipeline** using Jenkins, Ansible, and Kubernetes (Minikube).



## 🚀 Key Features

* **RAG Pipeline:** Retrieves relevant acts/scenes from *Julius Caesar* using `sentence-transformers` and generates answers via the Gemini API.
* **Microservices Architecture:** Decoupled Frontend (Streamlit) and Backend (FastAPI).
* **Automated CI/CD:**
    * **CI:** Jenkins automatically builds Docker images on every GitHub push.
    * **CD:** Ansible automates the deployment of Kubernetes manifests, Secrets, and Services.
* **Observability:** Full **ELK Stack** (Elasticsearch, Logstash, Kibana) integration for centralized logging and monitoring.
* **Scalability:** Runs on Kubernetes with Horizontal Pod Autoscaling (HPA).

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **LLM & Embeddings** | Google Gemini 1.5, SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Vector DB** | FAISS (Facebook AI Similarity Search) |
| **Backend** | FastAPI, Python 3.11 |
| **Frontend** | Streamlit |
| **Orchestration** | Kubernetes (Minikube) |
| **CI/CD** | Jenkins, Ansible, Docker |
| **Monitoring** | Elasticsearch, Logstash, Kibana (7.17.0) |

---

##  Project Structure

```text
├── ansible/               # Ansible playbooks for K8s deployment
│   └── deploy.yaml        # Main playbook applying manifests & secrets
├── backend/               # FastAPI Application
│   ├── pipeline/          # RAG logic (FAISS, Gemini)
│   ├── server.py          # API Endpoints
│   └── Dockerfile         # Backend container definition
├── frontend/              # Streamlit Application
│   ├── app.py             # UI Logic
│   └── Dockerfile         # Frontend container definition
├── kubernetes/            # K8s Manifests (Deployments, Services, HPA)
├── elk-stack/             # Logging Infrastructure (ES, Logstash, Kibana)
└── Jenkinsfile            # CI/CD Pipeline definition
```

## ⚙️ Prerequisites

* **Docker Desktop** (with Kubernetes enabled OR Minikube installed separately)
* **Minikube** (started with `minikube start`)
* **Python 3.11+**
* **Google Gemini API Key**

---

## 🚀 Deployment Guide

### Option A: Fully Automated (Jenkins CI/CD)
This project is designed to be deployed automatically.

1.  **Setup Jenkins:**
    * Run Jenkins via Docker with access to the host Docker socket.
    * Install **Ansible**, **Kubectl**, and **Docker** inside the Jenkins container.
2.  **Configure Credentials in Jenkins:**
    * `gemini-api-key-id`: Your Google Gemini API Key (Secret Text).
    * `docker-hub-credentials`: Your Docker Hub login (Username/Password).
3.  **Setup Webhook:**
    * Use `ngrok http 8080` to expose Jenkins.
    * Add the webhook URL to GitHub Settings (`/github-webhook/`).
4.  **Push Code:**
    * A simple `git push` triggers the pipeline -> Builds Images -> Deploys to Minikube.

### Option B: Manual Deployment (Local Testing)
If you want to run it without Jenkins:

1.  **Start Minikube & Enable Ingress:**
    ```bash
    minikube start
    minikube addons enable ingress
    ```

2.  **Create the API Secret:**
    ```bash
    kubectl create secret generic gemini-secret \
      --from-literal=gemini_api_key=YOUR_ACTUAL_KEY_HERE
    ```

3.  **Apply Kubernetes Manifests:**
    ```bash
    # Deploy ELK Stack first
    kubectl apply -f elk-stack/
    
    # Deploy App
    kubectl apply -f kubernetes/
    ```

---

## 🖥️ Usage

Once deployed, the Frontend is exposed via a **NodePort**.

1.  **Get the Frontend URL:**
    ```bash
    minikube service rag-frontend
    ```
    *This will open the Streamlit UI in your browser.*

2.  **Ask a Question:**
    * *Example:* "Who killed Brutus?"
    * *Example:* "Why did Cassius hate Caesar?"

3.  **View The Answer:**
    The system ("Epaphroditos") will answer based on the retrieved context chunks.

---

## 📊 Monitoring (ELK Stack)

You can monitor the backend logs via Kibana.

1.  **Port Forward Kibana:**
    ```bash
    kubectl port-forward svc/kibana 5601:5601
    ```

2.  **Access Dashboard:**
    * Go to `http://localhost:5601`
    * Create an Index Pattern for `rag-logs-*`
    * Go to **Discover** to see real-time query logs.
