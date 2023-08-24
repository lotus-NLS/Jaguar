import time

from s1_conversation.CustomQueue import *



def main():
    q = CustomQueue()
    def producer():
        for i in range(5):
            time.sleep(3)
            print(f'Now adding element {i} into queue')
            q.put(i)



    threading.Thread(target=producer).start()

    print(f'Get duplicate retreived: {q.get_duplicate()}')  # Output should be 0 but 0 remains in the queue
    print(q.get())  # Output should be 0 and 0 is removed from the queue
    print(q.get())  # Output should be 1
    q.stop()
    print(q.get_duplicate())  # Output should be None, as the queue is stopped

main()