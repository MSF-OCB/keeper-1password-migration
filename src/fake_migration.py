

import time, os

'''

this is just for testing purposes - see flag TEST_MODE in rest_endpoints.py

'''
def main():

    print("KEEPER_1P_OPERATION="+str(os.getenv("KEEPER_1P_OPERATION")))

    for x in range(10):
        print("Processing fake password "+str(x+1)+"...")
        time.sleep(1)
    print("***ALL_CLEAR***")
    print("***NO_LOGIN***")
    print("***USER_CREATED***")
    print("***ACCOUNT_MIGRATED***")
    print("***DONE***")

if __name__ == '__main__':
    main()
  