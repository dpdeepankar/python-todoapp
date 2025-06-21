pipeline {
    agent any
    environment {
        DOCKER_IMAGE_NAME = "python-todoapp"
        DOCKER_IMAGE_VERSION = "v1"
        HELM_RELEASE_NAME = "python-todo-app"
        HELM_CHART_PATH = "./helm/python-todo-app"
    }

    stages {

        stage('Git Checkout') {
            steps {
                git credentialsId: 'github-cred', url: 'https://github.com/dpdeepankar/python-todoapp.git'
            }
        }

        stage('Trivy filesystem scan'){
            steps{
                sh '''
                curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o html.tpl
                trivy fs --scanners vuln,secret -f template --template "@html.tpl" -o reports/trivy-fs-scan-report.html .
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                echo "remove old stale images";
                docker image prune -f ;
                docker build -t $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION . ;
                '''
            }
        }

        stage('Trivy docker image scan'){
            steps{
                sh 'trivy image -f template --template "@html.tpl" -o reports/trivy-image-scan-report.html ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_VERSION}'
            }
        }

        stage('Helm Apply'){
            steps{
                withKubeCredentials(kubectlCredentials: [[caCertificate: '', clusterName: '', contextName: '', credentialsId: 'kubernetes-jenkins-token', namespace: '', serverUrl: 'https://192.168.71.147:6443']]) {
                    sh 'helm install ${HELM_RELEASE_NAME} ${HELM_CHART_PATH}' // some block
                }
            }
        }

        stage('Verify helm installation'){
            steps{
                withKubeCredentials(kubectlCredentials: [[caCertificate: '', clusterName: '', contextName: '', credentialsId: 'kubernetes-jenkins-token', namespace: '', serverUrl: 'https://192.168.71.147:6443']]) {
                    sh '''
                    helm list ;
                    kubectl get pods ;
                    '''
                } 
            }
        }
    }

    post{
        always{
                archiveArtifacts artifacts: 'reports/trivy-fs-scan-report.html', fingerprint: true
                archiveArtifacts artifacts: 'reports/trivy-image-scan-report.html', fingerprint: true
	     
	        publishHTML (
			target : [
				allowMissing: false,
             			alwaysLinkToLastBuild: true,
             			keepAll: true,
             			reportDir: './reports',
             			reportFiles: 'trivy-fs-scan-report.html',
             			reportName: 'Trivy FS Scan Report',
             			reportTitles: 'Trivy FS Scan Report'
			]
		)
        
		publishHTML (
			target : [
				allowMissing: false,
             			alwaysLinkToLastBuild: true,
             			keepAll: true,
             			reportDir: './reports',
             			reportFiles: 'trivy-image-scan-report.html',
             			reportName: 'Trivy Image Scan Report',
             			reportTitles: 'Trivy Image Scan Report'
			]
		)
        }
    }
}

