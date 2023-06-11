def img

pipeline {
    environment {
        registry = "nitesh99sharma/emp-portal-project"
        registryCredential = 'DOCKERHUB'
        KUBECONFIG = credentials('kubeconfig-aks')
        githubCredential = 'GitHub-Creds'
        dockerImage = ''
        scannerHome = tool 'sonar4.8'
    }

    agent any

    stages {
        stage('Checkout project') {
            steps {
                script {
                    // Checkout the project from GitHub
                    git branch: 'main',
                    credentialsId: githubCredential,
                    url: 'https://github.com/niteshsharma99/Emp-Portal-Devops-Project.git'
                }
            }
        }

        stage('Installing packages') {
            steps {
                script {
                    // Install required Python packages
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Static Code Checking') {
            steps {
                script {
                    // Run pylint on Python files and generate a report
                    sh 'find . -name \\*.py | xargs pylint -f parseable | tee pylint.log'
                    recordIssues(
                        tool: pyLint(pattern: 'pylint.log'),
                        unstableTotalHigh: 100
                    )
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('sonar') {
                        // Run SonarQube scanner for code analysis
                        sh '''${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=DevOps-Project \
                            -Dsonar.sources=.'''
                    }
                }
            }
        }
        
        stage('SonarQube Quality Gates') {
            steps {
                script {
                    withSonarQubeEnv('sonar') {
                        timeout(time: 1, unit: 'MINUTES') {
                            // Wait for SonarQube quality gates to pass/fail
                            def qg = waitForQualityGate()
                            if (qg.status != 'OK') {
                                error "Pipeline aborted due to quality gate failure: ${qg.status}"
                            }
                        }
                    }
                }
            }
        }

        stage("Testing with pytest") {
            steps {
                script {
                    withPythonEnv('python3') {
                        // Install required Python packages for testing
                        sh 'pip install pytest'
                        sh 'pip install flask_sqlalchemy'
                        // Run pytest for unit testing
                        sh 'pytest test_app.py'
                    }
                }
            }
        }

        stage ('Clean Up') {
            steps {
                // Stop and remove Docker containers
                sh returnStatus: true, script: 'docker stop $(docker ps -a | grep ${JOB_NAME} | awk \'{print $1}\')'
                sh returnStatus: true, script: 'docker rmi $(docker images | grep ${registry} | awk \'{print $3}\') --force'
                sh returnStatus: true, script: 'docker rm ${JOB_NAME}'
            }
        }

        stage('Build Image') {
            steps {
                script {
                    // Build Docker image with a unique tag
                    img = registry + ":${env.BUILD_ID}"
                    println("${img}")
                    dockerImage = docker.build("${img}")
                }
            }
        }

        stage('Push To DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', registryCredential) {
                        // Push Docker image to DockerHub
                        dockerImage.push()
                    }
                }
            }
        }
        
        stage('Deploy to containers') {
            steps {
                // Deploy Docker image to containers
                sh label: '', script: "docker run -d --name ${JOB_NAME} -p 5000:5000 ${img}"
            }
        }
        
        stage('Deploy to Kubernetes aks') {
            steps {
                script {
                    // Print the contents of the workspace directory
                    sh 'ls -R'
                    
                    // Rest of your deployment steps
                    withCredentials([file(credentialsId: 'kubeconfig-aks', variable: 'KUBECONFIG')]) {
                        sh "kubectl config view --kubeconfig=$KUBECONFIG" // View Kubernetes configuration
                        sh "kubectl get namespaces --kubeconfig=$KUBECONFIG" // Get Kubernetes namespaces
                        sh "sed -i 's|\${ENV_IMAGE}|${img}|g' deployment.yaml" // Replace placeholder with Docker image name in deployment.yaml
                        sh "kubectl apply -f deployment.yaml --kubeconfig=$KUBECONFIG" // Apply deployment configuration
                        sh "kubectl apply -f service.yaml --kubeconfig=$KUBECONFIG" // Apply service configuration
                    }
                }
            }
        }

    }
    
    post {
        always {
            script {
                def buildStatus = currentBuild.currentResult ?: 'UNKNOWN'
                def color = buildStatus == 'SUCCESS' ? 'good' : 'danger'
            
                slackSend(
                    channel: '#devops-project',
                    color: color,
                    message: "Build ${env.BUILD_NUMBER} ${buildStatus}: Stage ${env.STAGE_NAME}",
                    teamDomain: 'jenkinsintegr-kfn1541',
                    tokenCredentialId: 'slack-integration'
                )
            }
        }
    }
}
