// Equivalent of .github/workflows/ci.yml for teams on Jenkins.
// Same stages, same gates: lint -> test -> build -> scan -> push.
// Documented here as the supported alternative; only one CI system
// should be active for a given repo to avoid double-pushing images.
pipeline {
    agent any

    environment {
        REGISTRY   = 'ghcr.io'
        IMAGE_NAME = 'saiannotations/orders-api'
        // IMAGE_TAG is set in the Build stage from the git commit
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint and Test') {
            agent {
                docker { image 'python:3.12-slim' }
            }
            steps {
                sh 'pip install --no-cache-dir ruff -r app/requirements.txt'
                sh 'ruff check app/'
                sh 'pytest app/ -v'
            }
        }

        stage('Build') {
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
                sh 'docker build -f docker/Dockerfile -t $REGISTRY/$IMAGE_NAME:$IMAGE_TAG .'
            }
        }

        stage('Scan') {
            steps {
                // Fail the build on CRITICAL or HIGH vulnerabilities,
                // same policy as the GitHub Actions pipeline.
                sh 'trivy image --severity CRITICAL,HIGH --exit-code 1 $REGISTRY/$IMAGE_NAME:$IMAGE_TAG'
            }
        }

        stage('Push') {
            when { branch 'main' }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'ghcr-credentials',
                    usernameVariable: 'REG_USER',
                    passwordVariable: 'REG_PASS'
                )]) {
                    sh 'echo $REG_PASS | docker login $REGISTRY -u $REG_USER --password-stdin'
                    sh 'docker push $REGISTRY/$IMAGE_NAME:$IMAGE_TAG'
                    sh 'docker tag $REGISTRY/$IMAGE_NAME:$IMAGE_TAG $REGISTRY/$IMAGE_NAME:latest'
                    sh 'docker push $REGISTRY/$IMAGE_NAME:latest'
                }
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed. Check the stage logs above; do not promote.'
        }
        success {
            echo "Image $REGISTRY/$IMAGE_NAME:$IMAGE_TAG pushed. Update gitops image tag to promote."
        }
    }
}
