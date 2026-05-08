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
                echo '🐳 Building Python + Chrome + Selenium image...'
                sh "docker build -f Dockerfile.test -t ${TEST_IMAGE}:latest ."
            }
        }

        // ───────────────────────────────
        // 3. Run Selenium + API Tests
        // ───────────────────────────────
        stage('Run Tests') {
            steps {
                echo '🧪 Running Selenium test cases inside container...'
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
        // 4. Deploy Application
        // ───────────────────────────────
        stage('Deploy') {
            steps {
                echo '🚀 Deploying application using docker-compose...'
                sh 'sudo docker-compose -f docker-compose-part2.yml down || true'
                sh 'sudo docker-compose -f docker-compose-part2.yml up -d --build'
            }
        }
    }

    // ───────────────────────────────
    // 5. Post Actions (Email Report)
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
                    to:       pusherEmail,
                    subject:  "${emoji} [${status}] Jobify Pipeline — Build #${buildNum}",
                    mimeType: 'text/html',
                    body: """
                    <html>
                    <body style="font-family:Arial,sans-serif;padding:24px;max-width:600px;">
                      <h2 style="color:${color};">${emoji} Jobify CI/CD Pipeline ${status}</h2>

                      <table style="border-collapse:collapse;width:100%;margin:16px 0;">
                        <tr style="background:#f5f5f5;">
                          <td style="padding:10px;font-weight:bold;">Job</td>
                          <td style="padding:10px;">${jobName}</td>
                        </tr>

                        <tr>
                          <td style="padding:10px;font-weight:bold;">Build #</td>
                          <td style="padding:10px;">${buildNum}</td>
                        </tr>

                        <tr style="background:#f5f5f5;">
                          <td style="padding:10px;font-weight:bold;">Result</td>
                          <td style="padding:10px;color:${color};font-weight:bold;">${status}</td>
                        </tr>

                        <tr>
                          <td style="padding:10px;font-weight:bold;">Triggered by</td>
                          <td style="padding:10px;">${pusherEmail}</td>
                        </tr>

                        <tr style="background:#f5f5f5;">
                          <td style="padding:10px;font-weight:bold;">App URL</td>
                          <td style="padding:10px;">
                            <a href="http://3.212.77.197">http://3.212.77.197</a>
                          </td>
                        </tr>
                      </table>

                      <a href="${buildUrl}testReport"
                         style="display:inline-block;background:#2c3e50;color:#fff;
                                padding:10px 20px;border-radius:4px;text-decoration:none;">
                         View Test Report →
                      </a>

                      <a href="${buildUrl}"
                         style="display:inline-block;background:#7f8c8d;color:#fff;
                                padding:10px 20px;border-radius:4px;text-decoration:none;margin-left:8px;">
                         View Full Build →
                      </a>

                      <p style="margin-top:24px;color:#aaa;font-size:11px;">
                        Auto-generated by Jenkins · ${jobName} #${buildNum}
                      </p>
                    </body>
                    </html>
                    """
                )
            }
        }
    }
}
