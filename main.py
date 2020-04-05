import threading
import random
import time

def generateRandomListOfNumbers(numberRange, length):
    return random.sample(range(numberRange), length)

class Smoker:
    def __init__(self, rounds, ingredients):
        self.conditionMutex = threading.Condition()
        self.barmanSleep = threading.Semaphore(0)
        self.rounds = rounds
        self.ingredients = ingredients
        self.availableItems = [False, False, False]
        self.terminate = False
        # Create smokers threads
        threading.Thread(target=self.smokerRoutine, name='Tobacco smoker (1)', args=(1, 2)).start()
        threading.Thread(target=self.smokerRoutine, name='Paper smoker (2)', args=(0, 2)).start()
        threading.Thread(target=self.smokerRoutine, name='Matches smoker (3)', args=(0, 1)).start()
        # Create barman thread
        self.barmanThread = threading.Thread(target=self.barmanRoutine)
        self.barmanThread.start()

    def barmanRoutine(self):
        for roundNumber in range(self.rounds):
            print('Round number {0}'.format(roundNumber))
            randomItems = generateRandomListOfNumbers(len(self.availableItems), 2)
            self.conditionMutex.acquire()
            print('Barman choose: {0} and {1}'.format(self.ingredients[randomItems[0]], self.ingredients[randomItems[1]]))
            self.availableItems[randomItems[0]] = True
            self.availableItems[randomItems[1]] = True
            self.conditionMutex.notify_all()
            self.conditionMutex.release()
            self.barmanSleep.acquire()

    def smokerRoutine(self, neededItem1, neededItem2):
        while (True):
            self.conditionMutex.acquire()
            # Block till the needed items are on table
            while (self.availableItems[neededItem1] == False or self.availableItems[neededItem2] == False):
                self.conditionMutex.wait()
            self.conditionMutex.release()
            if (self.terminate == True):
                break
            # Pickup the items from the table
            self.availableItems[neededItem1] = False
            self.availableItems[neededItem2] = False
            print('{0} started smoking'.format(threading.currentThread().getName()))
            self.smoke()
            self.barmanSleep.release()

    def smoke(self):
        smokingTime = random.random() * 4 + 1
        time.sleep(smokingTime)
        print('{0} ended smoking after {1:.1f} sec.'.format(threading.currentThread().getName(), smokingTime))

    def waitForCompletion(self):
        # Wait for barman thread to end
        self.barmanThread.join()
        # Send terminate signal to smoker threads
        self.conditionMutex.acquire()
        self.terminate = True
        self.availableItems = [True, True, True]
        self.conditionMutex.notify_all()
        self.conditionMutex.release()

if __name__== "__main__":
    smoker = Smoker(10, ['TOBACCO', 'PAPER', 'MATCHES'])
    smoker.waitForCompletion()