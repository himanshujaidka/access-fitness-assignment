pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install & Lint') {
            steps {
                sh '''
                    python3 -m venv --clear venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    python -m py_compile app.py
                    python -m flake8 .
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build --no-cache \
                        --secret id=extra_ca,src=/etc/ssl/certs/ca-certificates.crt \
                        -t aceest-fitness:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm aceest-fitness:${BUILD_NUMBER} python -m pytest -v'
            }
        }
    }

    post {
        always {
            sh 'docker rmi aceest-fitness:${BUILD_NUMBER} || true'
        }
    }
}
