pipeline {

    agent any

    environment {
        TEST_IMAGE = "jobify-selenium-tests"
    }

    triggers {
        githubPush()
    }

    stages {

        // ───────────────────────────────
        // 1. Clone Repo
        // ───────────────────────────────
        stage('Clone Repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/muhammadusamahoyrr/jobify-fixed.git'
            }
        }

        // ───────────────────────────────
        // 2. Build Test Docker Image
        // ───────────────────────────────
        stage('Build Test Image') {
            steps {
                echo '🐳 Building Selenium test image...'
                sh "docker build -f Dockerfile.test -t ${TEST_IMAGE}:latest ."
            }
        }

        // ───────────────────────────────
        // 3. Seed Test Accounts
        // ───────────────────────────────
        stage('Seed Test Accounts') {
            steps {
                echo '🌱 Seeding test users...'
                sh '''
                    curl -s -X POST http://3.212.77.197:8080/auth/signup \
                      -H "Content-Type: application/json" \
                      -d '{"name":"Test Employer","email":"employer@jobportal.com","password":"Employer@123","role":"employer"}' || true

                    curl -s -X POST http://3.212.77.197:8080/auth/signup \
                      -H "Content-Type: application/json" \
                      -d '{"name":"Test Seeker","email":"seeker@jobportal.com","password":"Seeker@123","role":"jobseeker"}' || true

                    echo "✅ Seeding done"
                '''
            }
        }

        // ───────────────────────────────
        // 4. Run Tests
        // ───────────────────────────────
        stage('Run Tests') {
            steps {
                echo '🧪 Running Selenium tests...'
                sh """
                    mkdir -p ${WORKSPACE}/results

                    docker run --rm \
                        -v ${WORKSPACE}/results:/tests/results \
                        ${TEST_IMAGE}:latest \
                        pytest test_job_portal.py -v \
                        --junit-xml=/tests/results/test-results.xml
                """
            }

            post {
                always {
                    junit testResults: 'results/test-results.xml'
                }
            }
        }

        // ───────────────────────────────
        // 5. Deploy Application (FIXED)
        // ───────────────────────────────
        stage('Deploy') {
            steps {
                echo '🚀 Deploying application safely...'
                sh '''
                    sudo docker compose -f docker-compose-part2.yml down --remove-orphans || true

                    sudo docker rm -f jobify-part2 || true
                    sudo docker rm -f jobify-pipeline-web-1 || true

                    sudo docker compose -f docker-compose-part2.yml up -d
                '''
            }
        }
    }

    // ───────────────────────────────
    // 6. Post Actions (Email Report)
    // ───────────────────────────────
    post {
        always {
            script {

                def pusherEmail = ''
                try {
                    pusherEmail = sh(
                        script: "git log -1 --pretty=format:'%ae'",
                        returnStdout: true
                    ).trim()
                } catch (Exception e) {
                    pusherEmail = 'fallback@example.com'
                }

                def status   = currentBuild.currentResult ?: 'UNKNOWN'
                def color    = (status == 'SUCCESS') ? '#27ae60' : '#e74c3c'
                def emoji    = (status == 'SUCCESS') ? '✅' : '❌'
                def jobName  = env.JOB_NAME
                def buildNum = env.BUILD_NUMBER
                def buildUrl = env.BUILD_URL

                emailext(
                    to: pusherEmail,
                    subject: "${emoji} [${status}] Jobify Pipeline — Build #${buildNum}",
                    mimeType: 'text/html',
                    body: """
                    <html>
                    <body style="font-family:Arial;padding:20px;">
                      <h2 style="color:${color};">${emoji} Pipeline ${status}</h2>

                      <p><b>Job:</b> ${jobName}</p>
                      <p><b>Build:</b> ${buildNum}</p>
                      <p><b>Status:</b> ${status}</p>

                      <p>
                        <a href="http://3.212.77.197:8082">Open App</a>
                      </p>

                      <p>
                        <a href="${buildUrl}testReport">Test Report</a>
                      </p>
                    </body>
                    </html>
                    """
                )
            }
        }
    }
}
