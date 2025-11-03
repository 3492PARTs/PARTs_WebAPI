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
        def buildImage

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

        stage('Set variables') {
            if (env.BRANCH_NAME == 'main') {
                env.DEPLOY_PATH = "\\/home\\/parts3492\\/domains\\/api.parts3492.org\\/code"
                env.DEPLOY_URL = "https:\\/\\/api.parts3492.org"
                env.DEPENDENCY_GROUP = "wvnet"
                env.RUNTIME_TARGET = "runtime-production"
            }
            else {
                env.DEPLOY_PATH = "\\/app"
                env.DEPLOY_URL = "https:\\/\\/partsuat.bduke.dev"
                env.DEPENDENCY_GROUP = "uat"
                env.RUNTIME_TARGET = "runtime-uat"
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
        }

        stage('Build image') {
            timeout(time: 15, unit: 'MINUTES') {
                // Attempt to pull cache image if it exists (this is a local image, so it may not exist)
                sh """
                    echo "Attempting to pull test cache image (may not exist on first build)..."
                    docker pull parts-webapi-build-${env.formatted_branch_name}:latest 2>/dev/null || echo "Cache image not found, building from scratch..."
                """
                
                // Build test image with BuildKit cache
                buildImage = docker.build("parts-webapi-build-${env.formatted_branch_name}", 
                    "--build-arg DEPENDENCY_GROUP=${env.DEPENDENCY_GROUP} " +
                    "--cache-from parts-webapi-build-${env.formatted_branch_name}:latest " +
                    "-f ./Dockerfile --target=build .")
            }
        }

        stage('Run tests') {
            timeout(time: 15, unit: 'MINUTES') {
                // Run tests inside the test container
                def testImage = docker.build("parts-webapi-test-${env.formatted_branch_name}", 
                    "--build-arg DEPENDENCY_GROUP=${env.DEPENDENCY_GROUP} " +
                    "--cache-from parts-webapi-build-${env.formatted_branch_name}:latest " +
                    "-f ./Dockerfile --target=test .")

                testImage.inside {
                    sh '''
                        echo "Running test suite..."
                        cd /app
                        export COVERAGE_FILE=/tmp/.coverage
                        /app/.venv/bin/pytest --cov=src --cov-report=term-missing --cov-fail-under=50 -v
                        echo "All tests passed!"
                    '''
                }
            }
        }

        stage('Build runtime image') {
            timeout(time: 5, unit: 'MINUTES') {
                if (env.BRANCH_NAME == 'main') {
                    sh '''
                        echo "Attempting to pull runtime cache image..."
                        docker pull bduke97/parts_webapi:latest 2>/dev/null || echo "Runtime cache not found, will build from scratch..."
                    '''
                    
                    // Use BuildKit cache for faster builds - build only runtime stage
                    app = docker.build("bduke97/parts_webapi", 
                        "--build-arg DEPENDENCY_GROUP=${env.DEPENDENCY_GROUP} " +
                        "--cache-from bduke97/parts_webapi:latest " +
                        "--cache-from parts-webapi-build-${env.formatted_branch_name}:latest " +
                        "-f ./Dockerfile --target=${env.RUNTIME_TARGET} .")
                }
                else {
                    sh """
                        echo "Attempting to pull runtime cache image for branch ${env.FORMATTED_BRANCH_NAME}..."
                        docker pull bduke97/parts_webapi:${env.FORMATTED_BRANCH_NAME} 2>/dev/null || echo "Runtime cache not found, will build from scratch..."
                    """
                    
                    // Use BuildKit cache for faster builds - build only runtime stage
                    app = docker.build("bduke97/parts_webapi", 
                        "--build-arg DEPENDENCY_GROUP=${env.DEPENDENCY_GROUP} " +
                        "--cache-from bduke97/parts_webapi:${env.FORMATTED_BRANCH_NAME} " +
                        "--cache-from parts-webapi-build-${env.formatted_branch_name}:latest " +
                        "-f ./Dockerfile --target=${env.RUNTIME_TARGET} .")
                }
            }
        }

        if (env.BRANCH_NAME != 'main') {
            stage('Push image') {
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

                sh '''
                    ssh -o StrictHostKeyChecking=no brandon@192.168.1.41 "
                        cd /home/brandon/PARTs_Website && 
                        git fetch --prune &&
                        git for-each-ref --format '%(if:equals=gone)%(upstream:track,nobracket)%(then)%(refname:short)%(end)' refs/heads/ | 
                        xargs -r git branch --delete
                    "
                '''
            } 
        }
        }

        stage('Cleanup docker images') {
            sh """
                echo "Starting Docker image cleanup..."
                
                # 1. Force remove the intermediate test image
                docker rmi -f parts-webapi-build-${env.formatted_branch_name} || true

                # 1.2. Force remove the intermediate test image
                docker rmi -f parts-webapi-test-${env.formatted_branch_name} || true
                
                # 2. Remove all dangling images (untagged)
                docker image prune -f
                
                # 3. Remove build cache older than 7 days to save disk space
                docker builder prune -f --filter "until=168h" || true
                
                echo "Docker images cleaned up."
            """
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