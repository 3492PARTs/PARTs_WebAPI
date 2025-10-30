node {
    env.BUILD_NO = env.BUILD_DISPLAY_NAME

    env.FORMATTED_BRANCH_NAME = env.BRANCH_NAME.replaceAll("/", "-")

    
    try {
        def app

        stage('Clone repository') {
            checkout scm
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

        stage('Build image') {  
            if (env.BRANCH_NAME == 'main') {
                env.DEPLOY_PATH = "\\/home\\/parts3492\\/domains\\/api.parts3492.org\\/code"
                env.DEPLOY_URL = "https:\\/\\/api.parts3492.org"
            }
            else {
                env.DEPLOY_PATH = "\\/app"
                env.DEPLOY_URL = "https:\\/\\/partsuat.bduke.dev"
            }

            sh'''
                sed -i "s/DEPLOY_PATH/$DEPLOY_PATH/g" scripts/clear-logs.sh \
                && sed -i "s/DEPLOY_URL/$DEPLOY_URL/g" scripts/notify-users.sh \
                && sed -i "s/DEPLOY_PATH/$DEPLOY_PATH/g" scripts/notify-users.sh \
                && sed -i "s/DEPLOY_URL/$DEPLOY_URL/g" scripts/refresh-event-team-info.sh \
                && sed -i "s/DEPLOY_PATH/$DEPLOY_PATH/g" scripts/refresh-event-team-info.sh \
                && sed -i "s/DEPLOY_PATH/$DEPLOY_PATH/g" crontab \
                && sed -i "s/BUILD/$SHA/g" api/settings.py
                '''
            
            if (env.BRANCH_NAME == 'main') {
                // Build test stage first to run tests, then build runtime stage
                docker.build("bduke97/parts_webapi", "-f ./Dockerfile --target=test .")
                app = docker.build("bduke97/parts_webapi", "-f ./Dockerfile --target=runtime .")
            }
            else {
                // Build test stage first to run tests, then build runtime stage
                docker.build("bduke97/parts_webapi", "-f ./Dockerfile.uat --target=test .")
                app = docker.build("bduke97/parts_webapi", "-f ./Dockerfile.uat --target=runtime .")
            }
        }

        stage('Push image') {
            if (env.BRANCH_NAME != 'main') {
                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                    app.push("${env.FORMATTED_BRANCH_NAME}")
                    //app.push("latest")
                }
            }  
        }

        //parts-server vhost90-public.wvnet.edu

        stage('Deploy') {
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
                        python3.11 /scripts/upload_directory.py $ENV_HOST "$USER" "$PASS" /wsgi/ /domains/api.parts3492.org/code/api
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