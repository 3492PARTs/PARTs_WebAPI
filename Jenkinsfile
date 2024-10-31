node {
    def app
    stage('Clone repository') {
        checkout scm
    }

    stage('Build image') {  
        if (env.BRANCH_NAME == 'main') {
            app = docker.build("bduke97/parts_webapi", "-f ./Dockerfile .")
        }
        else {
            app = docker.build("bduke97/parts_webapi", "-f ./Dockerfile.uat .")
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
        if (env.BRANCH_NAME != 'main') {
            docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                app.push("${env.BUILD_NUMBER}")
                app.push("latest")
            }
        }  
    }

    //parts-server vhost90-public.wvnet.edu

    stage('Deploy') {
        if (env.BRANCH_NAME == 'main') {
            withCredentials([usernamePassword(credentialsId: 'omv', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                app.inside {
                    sh '''
                    mkdir ~/.ssh && touch ~/.ssh/known_hosts && ssh-keyscan -H vhost90-public.wvnet.edu >> ~/.ssh/known_hosts
                    '''

                    sh '''
                    python3.11 delete_remote_files.py vhost90-public.wvnet.edu "$USER" "$PASS" /domains/api.parts3492.org/code --exclude_dirs venv --keep jwt-key jwt-key.pub .env
                    '''

                    sh '''
                    rm delete_remote_files.py
                    '''

                    sh '''
                    python3.11 upload_directory.py vhost90-public.wvnet.edu "$USER" "$PASS" /code/ /domains/api.parts3492.org/code
                    '''
                }

                /*app.inside {
                    sh '''
                    mkdir ~/.ssh && touch ~/.ssh/known_hosts && ssh-keyscan -H 192.168.1.43 >> ~/.ssh/known_hosts
                    '''

                    sh '''
                    python3.11 delete_remote_files.py 192.168.1.43 "$USER" "$PASS" /home/brandon/tmp --exclude_dirs venv --keep jwt-key jwt-key.pub .env
                    '''

                    sh '''
                    rm delete_remote_files.py
                    '''

                    sh '''
                    python3.11 upload_directory.py 192.168.1.43 "$USER" "$PASS" /code/ /home/brandon/tmp
                    '''
                }*/
            }
        }
        else {
            sh '''
            ssh -o StrictHostKeyChecking=no brandon@192.168.1.41 "cd /home/brandon/PARTs_WebAPI && docker stop parts_webapi_uat && docker rm parts_webapi_uat && docker compose up -d"
            '''
        } 
    }
}