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

    stage('Deploy') {
        if (env.BRANCH_NAME == 'main') {
            withCredentials([usernamePassword(credentialsId: 'parts-server', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                app.inside {
                    sh '''
                    mkdir ~/.ssh && touch ~/.ssh/known_hosts && ssh-keyscan -H vhost90-public.wvnet.edu >> ~/.ssh/known_hosts
                    '''

                    sh '''
                    python3.11 delete_remote_files.py vhost90-public.wvnet.edu "$USER" "$PASS" /domains/api.parts3492.org/code/ --keep jwt-key jwt-key.pub .env
                    '''

                    sh '''
                    rm delete_remote_files.py
                    '''

                    sh '''
                    sshpass -p "$PASS" sftp -o StrictHostKeyChecking=no "$USER"@vhost90-public.wvnet.edu <<EOF
                    cd /domains/api.parts3492.org/code
                    put -r /code/*
                    quit
                    EOF
                    '''
                }
            }
        }
        else {
            sh '''
            ssh -o StrictHostKeyChecking=no brandon@192.168.1.41 "cd /home/brandon/PARTs_WebAPI && docker stop parts_webapi_uat && docker rm parts_webapi_uat && docker compose up -d"
            '''
        } 
    }
}