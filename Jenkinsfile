pipeline {
    agent any
    stages {
        stage('Clone Repo') {
            steps {
                git branch: 'main',
                url: 'https://github.com/muhammadusamahoyrr/jobify-fixed.git'
            }
        }
        stage('Deploy') {
            steps {
                sh 'sudo docker compose -f docker-compose-part2.yml down || true'
                sh 'sudo docker compose -f docker-compose-part2.yml up -d --build'
            }
        }
    }
}
