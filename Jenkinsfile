// ─────────────────────────────────────────────────────────────────
//  Jenkinsfile — Job Portal CI Pipeline
//  Stages: Checkout → Build Docker Image → Run Tests → Email Results
// ─────────────────────────────────────────────────────────────────

pipeline {

    agent any

    environment {
        IMAGE_NAME = "job-portal-tests"
        RESULTS_DIR = "${WORKSPACE}/results"
    }

    triggers {
        // Automatically trigger when GitHub pushes to the repo
        githubPush()
    }

    stages {

        // ── Stage 1: Pull latest code from GitHub ──────────────
        stage('Checkout') {
            steps {
                echo '📥 Checking out code from GitHub...'
                checkout scm
            }
        }

        // ── Stage 2: Build the Docker image ────────────────────
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image with Chrome + Selenium...'
                sh '''
                    docker build -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        // ── Stage 3: Run Selenium tests inside container ───────
        stage('Run Tests') {
            steps {
                echo '🧪 Running Selenium test cases...'
                sh '''
                    mkdir -p ${RESULTS_DIR}

                    docker run --rm \
                        -v ${RESULTS_DIR}:/tests/results \
                        ${IMAGE_NAME}:latest \
                        python -m pytest test_job_portal.py \
                            -v --tb=short \
                            --junit-xml=/tests/results/test-results.xml \
                        || true
                '''
                // "|| true" ensures pipeline continues to email stage
                // even if some tests fail
            }
            post {
                always {
                    // Publish JUnit test results in Jenkins UI
                    junit allowEmptyResults: true,
                          testResults: 'results/test-results.xml'
                }
            }
        }

    }

    // ── Post: Email results to whoever pushed to GitHub ─────────
    post {
        always {
            script {
                // Get the email of the person who triggered this build
                def pusherEmail = ''
                try {
                    pusherEmail = env.GIT_COMMITTER_EMAIL
                              ?: sh(script: "git log -1 --pretty=format:'%ae'",
                                   returnStdout: true).trim()
                } catch (Exception e) {
                    pusherEmail = 'qasimalik@gmail.com'  // fallback
                }

                def buildStatus  = currentBuild.currentResult ?: 'UNKNOWN'
                def buildColor   = buildStatus == 'SUCCESS' ? '#27ae60' : '#e74c3c'
                def buildEmoji   = buildStatus == 'SUCCESS' ? '✅' : '❌'
                def jobName      = env.JOB_NAME
                def buildNumber  = env.BUILD_NUMBER
                def buildUrl     = env.BUILD_URL

                emailext(
                    to:      pusherEmail,
                    subject: "${buildEmoji} [${buildStatus}] ${jobName} — Build #${buildNumber}",
                    mimeType: 'text/html',
                    body: """
                    <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">

                        <h2 style="color: ${buildColor};">
                            ${buildEmoji} Job Portal — Test Pipeline ${buildStatus}
                        </h2>

                        <table style="border-collapse: collapse; width: 100%;">
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Job Name</td>
                                <td style="padding: 8px;">${jobName}</td>
                            </tr>
                            <tr style="background: #f5f5f5;">
                                <td style="padding: 8px; font-weight: bold;">Build Number</td>
                                <td style="padding: 8px;">#${buildNumber}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Status</td>
                                <td style="padding: 8px; color: ${buildColor};"><strong>${buildStatus}</strong></td>
                            </tr>
                            <tr style="background: #f5f5f5;">
                                <td style="padding: 8px; font-weight: bold;">Triggered By</td>
                                <td style="padding: 8px;">${pusherEmail}</td>
                            </tr>
                        </table>

                        <br>
                        <a href="${buildUrl}" style="
                            background: #2c3e50;
                            color: white;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 4px;
                        ">View Full Build & Test Report →</a>

                        <p style="margin-top: 20px; color: #888; font-size: 12px;">
                            This email was sent automatically by Jenkins.<br>
                            Pipeline: ${jobName} | Build: #${buildNumber}
                        </p>

                    </body>
                    </html>
                    """
                )
            }
        }
    }
}
