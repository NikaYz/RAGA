pipeline {
    agent any

    environment {
        KUBECONFIG = "/var/jenkins_home/.kube/config"
        // Use your Docker Hub username here if pushing, or local tags if not
        BACKEND_IMAGE = "nikayz/shaky-backend:v3"
        FRONTEND_IMAGE = "nikayz/shaky-frontend:latest"
        // Credentials ID you created in Jenkins
        //GEMINI_API_KEY = credentials('gemini-api-key-id')
        GEMINI_API_KEY = credentials('4c340a66-c823-4839-8a6a-1a26f773f071')
    }

    stages {
        stage('Initialize') {
            steps {
                script {
                    echo "Checking Kubernetes connectivity..."
                    // This should now work with insecure-skip-tls-verify
                    sh 'kubectl get nodes'
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    // REMOVED: eval $(minikube docker-env) 
                    // REASON: We are sharing the Docker socket, so these builds
                    // happen directly on your Mac's Docker daemon.
                    
                    echo "Building Backend..."
                    // Ensure you are at the root of the repo
                    sh 'docker build -t ${BACKEND_IMAGE} -f backend/Dockerfile backend/'
                    
                    echo "Building Frontend..."
                    sh 'docker build -t ${FRONTEND_IMAGE} -f frontend/Dockerfile frontend/'
                }
            }
        }

        stage('Deploy with Ansible') {
            steps {
                dir('ansible') {
                    // ansible-playbook needs to know python3 is the interpreter
                    sh '''
                        ansible-playbook deploy.yaml \
                        -e "ansible_python_interpreter=/opt/venv/bin/python3" \
                        -v
                    '''
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                sh 'kubectl get pods -n default'
                sh 'kubectl get services -n default'
            }
        }
    }
}
// pipeline {
//     agent any

//     environment {
//         // Path to your kubeconfig
//         KUBECONFIG = "${HOME}/.kube/config"
//         // Define image names to match your Kubernetes manifests
//         BACKEND_IMAGE = "nikayz/shaky-backend:v3"
//         FRONTEND_IMAGE = "nikayz/shaky-frontend:latest"
//     }

//     stages {
//         stage('Initialize') {
//             steps {
//                 script {
//                     echo "Checking Kubernetes connectivity..."
//                     sh 'kubectl get nodes'
//                 }
//             }
//         }

//         stage('Build Docker Images') {
//             steps {
//                 script {
//                     // Critical: We must point local Docker client to Minikube's Docker daemon
//                     // This ensures the images are available to K8s without pushing to a registry
//                     withEnv(['DOCKER_TLS_VERIFY=1', 'DOCKER_HOST=tcp://127.0.0.1:32769', 'DOCKER_CERT_PATH=/Users/apple/.minikube/certs']) {
//                         // NOTE: You must get the actual values for the above 3 vars by running:
//                         // minikube docker-env
//                         // Alternatively, use the shell eval method below:
//                     }
                    
//                     // Robust Method for Minikube Build:
//                     sh '''
//                         eval $(minikube -p minikube docker-env)
                        
//                         echo "Building Backend..."
//                         docker build -t ${BACKEND_IMAGE} -f backend/Dockerfile backend/
                        
//                         echo "Building Frontend..."
//                         docker build -t ${FRONTEND_IMAGE} -f frontend/Dockerfile frontend/
//                     '''
//                 }
//             }
//         }

//         stage('Deploy with Ansible') {
//             environment {
//                 // Securely inject the API Key from Jenkins Credentials
//                 GEMINI_API_KEY = credentials('gemini-api-key-id') 
//             }
//             steps {
//                 dir('ansible') {
//                     sh '''
//                         # Install ansible requirements if needed
//                         # pip install kubernetes ansible 

//                         echo "Running Ansible Playbook..."
//                         ansible-playbook deploy.yaml \
//                             -e "ansible_python_interpreter=/usr/bin/python3" \
//                             -v
//                     '''
//                 }
//             }
//         }
        
//         stage('Verify Deployment') {
//             steps {
//                 sh 'kubectl get pods -n default'
//                 sh 'kubectl get services -n default'
//             }
//         }
//     }
// }
// // pipeline {
// //   agent any

// //   environment {
// //     DOCKERHUB_ORG = "nikayz"
// //     BACKEND_IMAGE = "${env.DOCKERHUB_ORG}/shaky-backend:${env.BUILD_ID}"
// //     FRONTEND_IMAGE = "${env.DOCKERHUB_ORG}/shaky-frontend:${env.BUILD_ID}"
// //     // Assuming you mount your kube config to this path inside the Jenkins container
// //     KUBECONFIG = "/var/jenkins_home/.kube/config" 
// //   }

// //   stages {
// //     stage('Checkout') {
// //       steps {
// //         checkout scm
// //       }
// //     }

// //     // 1. Install Python Dependencies (Required for ML Pipeline)
// //     stage('Setup Python Env') {
// //       steps {
// //         sh 'pip install -r backend/requirements.txt || true' 
// //       }
// //     }

// //     // 2. Run ML Pipeline FIRST (Generates the files)
// //     stage('Run ML Pipeline') {
// //       steps {
// //         dir('backend') {
// //           // Ensure the output directory exists
// //           sh 'mkdir -p pipeline/cache'
// //           sh "python -m pipeline.ml_pipeline.build_embeddings --out-file pipeline/cache/vector.index --meta-file pipeline/cache/metadata.pkl"
// //         }
// //       }
// //     }

// //     // 3. NOW Build Backend (It will COPY the generated files)
// //     stage('Build Backend Image') {
// //       steps {
// //         dir('backend') {
// //           // Ensure your Dockerfile has: COPY pipeline/cache/ ./pipeline/cache/
// //           sh "docker build -t ${BACKEND_IMAGE} ."
// //         }
// //       }
// //     }

// //     stage('Build Frontend Image') {
// //       steps {
// //         dir('frontend') {
// //           sh "docker build -t ${FRONTEND_IMAGE} ."
// //         }
// //       }
// //     }

// //     stage('Push Images') {
// //       steps {
// //         withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
// //           sh 'echo $DH_PASS | docker login -u $DH_USER --password-stdin'
// //           sh "docker push ${BACKEND_IMAGE}"
// //           sh "docker push ${FRONTEND_IMAGE}"
// //         }
// //       }
// //     }

// //     stage('Deploy via Ansible') {
// //       steps {
// //         // Ansible needs to know where the Kube config is
// //         withEnv(["K8S_AUTH_KUBECONFIG=${env.KUBECONFIG}"]) {
// //             sh 'ansible-playbook -i inventory.ini ansible/deploy.yaml --extra-vars "image_backend=${BACKEND_IMAGE} image_frontend=${FRONTEND_IMAGE}"'
// //         }
// //       }
// //     }
// //   }
  
// //   post {
// //     always {
// //         // Clean up to save disk space
// //         sh 'docker rmi ${BACKEND_IMAGE} || true'
// //         sh 'docker rmi ${FRONTEND_IMAGE} || true'
// //     }
// //   }
// // }
