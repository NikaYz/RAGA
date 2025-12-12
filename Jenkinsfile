pipeline {
  agent any

  environment {
    DOCKERHUB_ORG = "nikayz"
    BACKEND_IMAGE = "${env.DOCKERHUB_ORG}/shaky-backend:${env.BUILD_ID}"
    FRONTEND_IMAGE = "${env.DOCKERHUB_ORG}/shaky-frontend:${env.BUILD_ID}"
    // Assuming you mount your kube config to this path inside the Jenkins container
    KUBECONFIG = "/var/jenkins_home/.kube/config" 
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    // 1. Install Python Dependencies (Required for ML Pipeline)
    stage('Setup Python Env') {
      steps {
        sh 'pip install -r backend/requirements.txt || true' 
      }
    }

    // 2. Run ML Pipeline FIRST (Generates the files)
    stage('Run ML Pipeline') {
      steps {
        dir('backend') {
          // Ensure the output directory exists
          sh 'mkdir -p pipeline/cache'
          sh "python -m pipeline.ml_pipeline.build_embeddings --out-file pipeline/cache/vector.index --meta-file pipeline/cache/metadata.pkl"
        }
      }
    }

    // 3. NOW Build Backend (It will COPY the generated files)
    stage('Build Backend Image') {
      steps {
        dir('backend') {
          // Ensure your Dockerfile has: COPY pipeline/cache/ ./pipeline/cache/
          sh "docker build -t ${BACKEND_IMAGE} ."
        }
      }
    }

    stage('Build Frontend Image') {
      steps {
        dir('frontend') {
          sh "docker build -t ${FRONTEND_IMAGE} ."
        }
      }
    }

    stage('Push Images') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh 'echo $DH_PASS | docker login -u $DH_USER --password-stdin'
          sh "docker push ${BACKEND_IMAGE}"
          sh "docker push ${FRONTEND_IMAGE}"
        }
      }
    }

    stage('Deploy via Ansible') {
      steps {
        // Ansible needs to know where the Kube config is
        withEnv(["K8S_AUTH_KUBECONFIG=${env.KUBECONFIG}"]) {
            sh 'ansible-playbook -i inventory.ini ansible/deploy.yaml --extra-vars "image_backend=${BACKEND_IMAGE} image_frontend=${FRONTEND_IMAGE}"'
        }
      }
    }
  }
  
  post {
    always {
        // Clean up to save disk space
        sh 'docker rmi ${BACKEND_IMAGE} || true'
        sh 'docker rmi ${FRONTEND_IMAGE} || true'
    }
  }
}