node {
    def app
    stage('Clone repository') {
        checkout scm
    }

    stage('Build image') {  
        if (env.BRANCH_NAME == 'main') {
            app = docker.build("bduke97/parts_webapi", "-f ./docker/Dockerfile .")
        }
        if (env.BRANCH_NAME == 'uat') {
            app = docker.build("bduke97/parts_weapi", "-f ./Dockerfile.uat .")
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
        if (env.BRANCH_NAME == 'uat') {
            docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                app.push("${env.BUILD_NUMBER}")
                app.push("latest")
            }
        }  
    }

    stage('Deploy') {
        if (env.BRANCH_NAME == 'main') {
            /*withCredentials([usernamePassword(credentialsId: 'parts-server', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                app.inside {
                    sh '''
                    sshpass -p "$PASS" sftp -o StrictHostKeyChecking=no "$USER"@vhost90-public.wvnet.edu:public_html/ <<EOF
                    ls
                    EOF
                    '''
                }
            }*/

            withCredentials([usernamePassword(credentialsId: 'parts-server', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                app.inside {
                    sh '''
                    sshpass -p "$PASS" sftp -o StrictHostKeyChecking=no "$USER"@vhost90-public.wvnet.edu:public_html/ <<EOF
                    cd albumCovers/BuildSeason
                    rm *
                    cd ../CommunityOutreach
                    rm *
                    cd ../Competition
                    rm *
                    cd ../Wallpapers
                    rm *
                    cd ../
                    rmdir BuildSeason
                    rmdir CommunityOutreach
                    rmdir Competition
                    rmdir Wallpapers
                    cd ../
                    rmdir albumCovers
                    cd appIcons
                    rm *
                    cd ../
                    rmdir appIcons
                    cd fonts/Black
                    rm *
                    cd ../Bold
                    rm *
                    cd ../ExtraBold
                    rm *
                    cd ../ExtraLight
                    rm *
                    cd ../Light
                    rm *
                    cd ../Regular
                    rm *
                    cd ../SemiBold
                    rm *
                    cd ../
                    rmdir Black
                    rmdir Bold
                    rmdir ExtraBold
                    rmdir ExtraLight
                    rmdir Light
                    rmdir Regular
                    rmdir SemiBold
                    rm *
                    cd ../
                    rmdir fonts
                    cd icons
                    rm *
                    cd ../
                    rmdir icons
                    cd joinPictures
                    rm *
                    cd ../
                    rmdir joinPictures
                    cd media
                    rm *
                    cd ../
                    rmdir media
                    cd resourceIcons
                    rm *
                    cd ../
                    rmdir resourceIcons
                    cd sliderImages
                    rm *
                    cd ../
                    rmdir sliderImages
                    cd webImages/FIRST
                    rm *
                    cd ../Robots
                    rm *
                    cd ../SocialIcons
                    rm *
                    cd ../Sponsors
                    rm *
                    cd ../
                    rmdir FIRST
                    rmdir Robots
                    rmdir SocialIcons
                    rmdir Sponsors
                    rm *
                    cd ../
                    rmdir webImages
                    rm *
                    EOF
                    '''

                    sh '''
                    sshpass -p "$PASS" sftp -o StrictHostKeyChecking=no "$USER"@vhost90-public.wvnet.edu <<EOF
                    cd /public_html
                    put -r /usr/local/app/dist/parts-website/browser/*
                    quit
                    EOF
                    '''
                }
            }
        }

        if (env.BRANCH_NAME == 'uat') {
            sh '''
            ssh -o StrictHostKeyChecking=no brandon@192.168.1.41 "cd /home/brandon/PARTs_WebAPI/docker && docker stop parts_webapi_uat && docker rm parts_webapi_uat && docker compose up -d"
            '''
        } 
    }
}