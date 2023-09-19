# 12-Jun-2023 Verne, WVNET
#
#some general info and examples
#https://www.shellhacks.com/modwsgi-hello-world-example/
#https://stackoverflow.com/questions/41813910/apache-wsgi-python-basic-example
#http://koo.fi/blog/2012/12/02/serving-python-scripts-with-apache-mod_wsgi-part-i/
#https://access.redhat.com/solutions/2204051  (requires logging into Redhat)
#
#This one -- helped make the above HELLO WORLD demo work
#https://stackoverflow.com/questions/34838443/typeerror-sequence-of-byte-string-values-expected-value-of-type-str-found
#


def application(environ, start_response):

    import sys
    import os
    import getpass
    import pwd
    import time

    status = '200 OK'
    output = "mod_wsgi executing script in a sub-site via python version:\n{}\n".format(sys.version)

    user2 = getpass.getuser()
#    login2 = os.getlogin()
    gid2 = os.getgid()
    uid2 = os.getuid() 
    userid2 = os.getenv('USER') 
    here = os.path.dirname(__file__)

#    output = output + "\nGetLogin   = " + login2
    output = output + "\nGetUser     = " + user2
    output = output + "\ncurrent Dir = " + here
    output = output + "\nGID         = " + str(gid2)
    output = output + "\nUID         = " + str(uid2)
    output = output + "\nUserid      = " + str(userid2)


    output = output.encode('utf-8')
    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

#    time.sleep(20)

    return [output]

