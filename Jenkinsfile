node {
    def app
    stage('Clone repository') {
        checkout scm
    }

    stage('Build image') {  
        if (env.BRANCH_NAME == 'uat') {
            app = docker.build("bduke97/parts_webapi", "-f ./docker/Dockerfile .")
        }
        if (env.BRANCH_NAME == 'uat3') {
            app = docker.build("bduke97/parts_webapi", "-f ./docker/Dockerfile.uat .")
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
        if (env.BRANCH_NAME == 'uat3') {
            docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                app.push("${env.BUILD_NUMBER}")
                app.push("latest")
            }
        }  
    }

    stage('Deploy') {
        if (env.BRANCH_NAME == 'uat') {
            /*withCredentials([usernamePassword(credentialsId: 'parts-server', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                app.inside {
                    sh '''
                    sshpass -p "$PASS" sftp -o StrictHostKeyChecking=no "$USER"@vhost90-public.wvnet.edu:public_html/ <<EOF
                    ls
                    EOF
                    '''
                }
            }*/

            withCredentials([usernamePassword(credentialsId: 'omv', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                app.inside {
                    sh '''
                    sshpass -p "$PASS" sftp -o StrictHostKeyChecking=no "$USER"@192.168.1.43: <<EOF
                    ls
                    rm *
                    EOF
                    '''

                    sh '''
                    sshpass -p "$PASS" sftp -o StrictHostKeyChecking=no "$USER"@192.168.1.43 <<EOF
                    cd /home/brandon/tmp
                    put -r /code/*
                    quit
                    EOF
                    '''
                }
            }
        }

        if (env.BRANCH_NAME == 'uat3') {
            sh '''
            ssh -o StrictHostKeyChecking=no brandon@192.168.1.41 "cd /home/brandon/PARTs_WebAPI/docker && docker stop parts_webapi_uat && docker rm parts_webapi_uat && docker compose up -d"
            '''
        } 
    }
}