

import time, os

'''

this is just for testing purposes - subtitute this filename in 

rest_endpoints.py function launch_process

to just do dummy stuff with testing the webapp

'''
def main():

    print("KEEPER_1P_OPERATION="+str(os.getenv("KEEPER_1P_OPERATION")))

    for x in range(10):
        print("Processing fake password "+str(x+1)+"...")
        time.sleep(1)

    print("***DONE***")

if __name__ == '__main__':
    main()