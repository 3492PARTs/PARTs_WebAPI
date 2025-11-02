node {
    def now = new Date()
    def formattedDate = now.format('yyyy.MM.dd')
    env.BUILD_DATE = formattedDate
    env.BUILD_NO = env.BUILD_DISPLAY_NAME
    env.FORMATTED_BRANCH_NAME = env.BRANCH_NAME.replaceAll("/", "-")
    
    // Enable Docker BuildKit for faster builds
    env.DOCKER_BUILDKIT = '1'
    env.BUILDKIT_PROGRESS = 'plain'
    
    try {
        def app

        stage('Clone repository') {
            timeout(time: 5, unit: 'MINUTES') {
                checkout scm
            }
        }

        withCredentials([string(credentialsId: 'github-status', variable: 'PASSWORD')]) {
            env.SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
            sh '''
                curl -X POST https://api.github.com/repos/3492PARTs/PARTs_WebAPI/statuses/$SHA \
                    -H "Authorization: token $PASSWORD" \
                    -H "Content-Type: application/json" \
                    -d '{"state":"pending", "description":"Build '\$BUILD_NO' pending", "context":"Jenkins Build"}'
            '''
        }

        stage('Run Tests') {
            timeout(time: 15, unit: 'MINUTES') {
                // Prepare environment-specific configuration
                if (env.BRANCH_NAME == 'main') {
                    env.DEPLOY_PATH = "\\/home\\/parts3492\\/domains\\/api.parts3492.org\\/code"
                    env.DEPLOY_URL = "https:\\/\\/api.parts3492.org"
                    env.DOCKERFILE = "./Dockerfile"
                }
                else {
                    env.DEPLOY_PATH = "\\/app"
                    env.DEPLOY_URL = "https:\\/\\/partsuat.bduke.dev"
                    env.DOCKERFILE = "./Dockerfile.uat"
                }

                sh'''
                    sed -i "s/DEPLOY_PATH/$DEPLOY_PATH/g" scripts/clear-logs.sh \
                    && sed -i "s/DEPLOY_URL/$DEPLOY_URL/g" scripts/notify-users.sh \
                    && sed -i "s/DEPLOY_PATH/$DEPLOY_PATH/g" scripts/notify-users.sh \
                    && sed -i "s/DEPLOY_URL/$DEPLOY_URL/g" scripts/refresh-event-team-info.sh \
                    && sed -i "s/DEPLOY_PATH/$DEPLOY_PATH/g" scripts/refresh-event-team-info.sh \
                    && sed -i "s/DEPLOY_PATH/$DEPLOY_PATH/g" crontab \
                    && sed -i "s/BUILD/$SHA/g" src/parts_webapi/settings/base.py
                '''
                
                // Attempt to pull cache image if it exists (this is a local image, so it may not exist)
                sh '''
                    echo "Attempting to pull test cache image (may not exist on first build)..."
                    docker pull parts-webapi-test-base:latest 2>/dev/null || echo "Cache image not found, building from scratch..."
                '''
                
                // Build test image with BuildKit cache
                def testImage = docker.build("parts-webapi-test-base", 
                    "--cache-from parts-webapi-test-base:latest " +
                    "-f ${env.DOCKERFILE} --target=test .")

                // Run tests inside the test container
                testImage.inside {
                    sh '''
                        echo "Running test suite..."
                        poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=50 -v
                        echo "All tests passed!"
                    '''
                }
            }
        }

        stage('Build image') {
            timeout(time: 20, unit: 'MINUTES') {
                if (env.BRANCH_NAME == 'main') {
                    sh '''
                        echo "Attempting to pull runtime cache image..."
                        docker pull bduke97/parts_webapi:latest 2>/dev/null || echo "Runtime cache not found, will build from scratch..."
                    '''
                    
                    // Use BuildKit cache for faster builds - build only runtime stage
                    app = docker.build("bduke97/parts_webapi", 
                        "--cache-from bduke97/parts_webapi:latest " +
                        "--cache-from parts-webapi-test-base:latest " +
                        "-f ./Dockerfile --target=runtime .")
                }
                else {
                    sh """
                        echo "Attempting to pull runtime cache image for branch ${env.FORMATTED_BRANCH_NAME}..."
                        docker pull bduke97/parts_webapi:${env.FORMATTED_BRANCH_NAME} 2>/dev/null || echo "Runtime cache not found, will build from scratch..."
                    """
                    
                    // Use BuildKit cache for faster builds - build only runtime stage
                    app = docker.build("bduke97/parts_webapi", 
                        "--cache-from bduke97/parts_webapi:${env.FORMATTED_BRANCH_NAME} " +
                        "--cache-from parts-webapi-test-base:latest " +
                        "-f ./Dockerfile.uat --target=runtime .")
                }
            }
        }

        stage('Push image') {
            if (env.BRANCH_NAME != 'main') {
                timeout(time: 10, unit: 'MINUTES') {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                        app.push("${env.FORMATTED_BRANCH_NAME}")
                        //app.push("latest")
                    }
                }
            }  
        }

        //parts-server vhost90-public.wvnet.edu

        stage('Deploy') {
            timeout(time: 15, unit: 'MINUTES') {
            if (env.BRANCH_NAME == 'main') {
                env.ENV_HOST = "vhost90-public.wvnet.edu"
                withCredentials([usernamePassword(credentialsId: 'parts-server', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    app.inside {
                        sh '''
                        mkdir ~/.ssh && touch ~/.ssh/known_hosts && ssh-keyscan -H $ENV_HOST >> ~/.ssh/known_hosts
                        '''

                        sh '''
                        python3.11 /scripts/delete_remote_files.py $ENV_HOST "$USER" "$PASS" /domains/api.parts3492.org/code --exclude_dirs venv logs scripts __pycache__ --keep jwt-key jwt-key.pub .env
                        '''

                        sh '''
                        python3.11 /scripts/upload_directory.py $ENV_HOST "$USER" "$PASS" /app/ /domains/api.parts3492.org/code
                        '''

                        sh '''
                        python3.11 /scripts/upload_directory.py $ENV_HOST "$USER" "$PASS" /wsgi/ /domains/api.parts3492.org/code/src/parts_webapi
                        '''
                    }
                }
            }
            else {
                sh '''
                ssh -o StrictHostKeyChecking=no brandon@192.168.1.41 "cd /home/brandon/PARTs_WebAPI \
                && git fetch \
                && git switch $BRANCH_NAME \
                && git pull \
                && TAG=$FORMATTED_BRANCH_NAME docker compose pull \
                && TAG=$FORMATTED_BRANCH_NAME docker compose up -d --force-recreate"
                '''
            } 
        }
        }

        stage('Cleanup Docker Images') {
            sh '''
                echo "Starting Docker image cleanup..."
                
                # 1. Force remove the intermediate test image
                docker rmi -f parts-webapi-test-base || true
                
                # 2. Remove all dangling images (untagged)
                docker image prune -f
                
                # 3. Remove build cache older than 7 days to save disk space
                docker builder prune -f --filter "until=168h" || true
                
                echo "Docker images cleaned up."
            '''
        }

        env.RESULT = 'success'
    }
    catch (e) {
        // error handling, if needed
        // throw the exception to jenkins
        env.RESULT = 'error'
        throw e
    } 
    finally {
        // some common final reporting in all cases (success or failure)
        withCredentials([string(credentialsId: 'github-status', variable: 'PASSWORD')]) {
                env.SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                sh '''
                    curl -X POST https://api.github.com/repos/3492PARTs/PARTs_WebAPI/statuses/$SHA \
                        -H "Authorization: token $PASSWORD" \
                        -H "Content-Type: application/json" \
                        -d '{"state":"'\$RESULT'", "description":"Build '\$BUILD_NO' '\$RESULT'", "context":"Jenkins Build"}'
                '''
            }
    }
}