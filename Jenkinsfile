pipeline {

    agent any

    environment {
        TEST_IMAGE = "jobify-selenium-tests"
        BACKEND_URL = "http://3.212.77.197:8080"
        FRONTEND_URL = "http://3.212.77.197:8082"
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
        // 2. Build Test Image
        // ───────────────────────────────
        stage('Build Test Image') {
            steps {
                echo '🐳 Building Selenium test image...'
                sh "docker build -f Dockerfile.test -t ${TEST_IMAGE}:latest ."
            }
        }

        // ───────────────────────────────
        // 3. Wait for Backend (IMPORTANT FIX)
        // ───────────────────────────────
        stage('Wait for Backend') {
            steps {
                echo '⏳ Waiting for backend to be ready...'
                sh '''
                    for i in {1..10}; do
                        echo "Check $i..."
                        curl -s --fail http://3.212.77.197:8080/health && exit 0
                        sleep 5
                    done
                    echo "Backend not ready"
                    exit 1
                '''
            }
        }

        // ───────────────────────────────
        // 4. Seed Test Accounts
        // ───────────────────────────────
        stage('Seed Test Accounts') {
            steps {
                echo '🌱 Seeding test users...'
                sh """
                    curl -s -X POST ${BACKEND_URL}/auth/signup \
                      -H 'Content-Type: application/json' \
                      -d '{"name":"Test Employer","email":"employer@jobportal.com","password":"Employer@123","role":"employer"}' || true

                    curl -s -X POST ${BACKEND_URL}/auth/signup \
                      -H 'Content-Type: application/json' \
                      -d '{"name":"Test Seeker","email":"seeker@jobportal.com","password":"Seeker@123","role":"jobseeker"}' || true

                    echo "✅ Seed complete"
                """
            }
        }

        // ───────────────────────────────
        // 5. Run Tests
        // ───────────────────────────────
        stage('Run Tests') {
            steps {
                echo '🧪 Running Selenium + API tests...'
                sh """
                    mkdir -p ${WORKSPACE}/results

                    docker run --rm \
                        -v ${WORKSPACE}/results:/tests/results \
                        -e BASE_URL=${BACKEND_URL} \
                        -e FRONTEND_URL=${FRONTEND_URL} \
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
        // 6. Deploy Application (CLEAN FIX)
        // ───────────────────────────────
        stage('Deploy') {
            steps {
                echo '🚀 Deploying application safely...'
                sh '''
                    sudo docker compose -f docker-compose-part2.yml down --remove-orphans || true

                    sudo docker compose -f docker-compose-part2.yml up -d --build

                    echo "✅ Deployment complete"
                '''
            }
        }
    }

    // ───────────────────────────────
    // POST ACTIONS
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
                        <a href="${FRONTEND_URL}">Open App</a>
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
