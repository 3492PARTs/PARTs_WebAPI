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
            if (true || env.BRANCH_NAME == 'main') {
                app = docker.build("bduke97/parts_webapi", "-f ./Dockerfile --target=runtime .")
            }
            else {
                app = docker.build("bduke97/parts_webapi", "-f ./Dockerfile.uat --target=runtime .")
            }
            
        }

        /*
        stage('Test image') {


            app.inside {
                sh 'echo "Tests passed"'
            }
        }
        */

        stage('Push image') {
            if (false && env.BRANCH_NAME != 'main') {
                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                    app.push("${env.FORMATTED_BRANCH_NAME}")
                    //app.push("latest")
                }
            }  
        }

        //parts-server vhost90-public.wvnet.edu

        stage('Deploy') {
            if (true || env.BRANCH_NAME == 'main') {
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