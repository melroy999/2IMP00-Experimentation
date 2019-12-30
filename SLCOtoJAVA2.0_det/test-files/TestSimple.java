import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;
import java.util.HashMap;
import java.time.Duration;
import java.time.Instant;

// main class
@SuppressWarnings({"NonAtomicOperationOnVolatileField", "FieldCanBeLocal", "InnerClassMayBeStatic", "DuplicatedCode", "MismatchedReadAndWriteOfArray", "unused", "SpellCheckingInspection"})
public class TestSimple {
    // The objects in the model.
    private final SLCO_Class[] objects;

    // Upperbound for transition counter
    private static final long COUNTER_BOUND = 10000000L;

    // Lock class to handle locks of global variables
	private static class LockManager {
        // The locks
        private final ReentrantLock[] locks;

		// Constructor
		LockManager(int noVariables) {
			locks = new ReentrantLock[noVariables];
			Arrays.fill(locks, new ReentrantLock(true));
		}

		// Lock method
		void lock(int... lock_ids) {
		    Arrays.sort(lock_ids);
			for (int lock_id : lock_ids) {
                locks[lock_id].lock();
      		}
		}

		// Unlock method
		void unlock(int... lock_ids) {
			for (int lock_id : lock_ids) {
                locks[lock_id].unlock();
      		}
		}
	}

    interface SLCO_Class {
        void startThreads();
        void joinThreads();
    }

    // representation of a class
    private static class P implements SLCO_Class {
        // The threads
        private final SM1Thread T_SM1;

        // Global variables
        private volatile int y; // Lock id 2
        private volatile int[] x; // Lock id 0

        interface P_SM1Thread_States {
            enum States {
                SM1_0, SM1_1
            }
        }

        class SM1Thread extends Thread implements P_SM1Thread_States {
            // Current state
            private SM1Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transitionCounter;

            // Counter for successful iterations
            long successful_transitionCounter;

            // A counter for the transitions.
            private HashMap<String, Integer> transitionCounterMap;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transitionCounter = 0;
                transitionCounterMap = new HashMap<>();
                currentState = SM1Thread.States.SM1_0;
            }

            private boolean exec_SM1_0() {
                lockManager.lock(0, 2); // Request [x[0], y]
                if (y > 10) { // from SM1_0 to SM1_1 {[y > 10; x[0] = 0; y = 0]} 
                    x[0] = 0;
                    y = 0;
                    lockManager.unlock(0, 2); // Release [x[0], y]
                    transitionCounterMap.merge("from SM1_0 to SM1_1 {[y > 10; x[0] = 0; y = 0]}", 1, Integer::sum);
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                }  else { // from SM1_0 to SM1_1 {[y <= 10; y = y + 1]}
                    y = y + 1;
                    lockManager.unlock(0, 2); // Release [x[0], y]
                    transitionCounterMap.merge("from SM1_0 to SM1_1 {[y <= 10; y = y + 1]}", 1, Integer::sum);
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                } 
            }

            private boolean exec_SM1_1() {
                // from SM1_1 to SM1_0 {x[0] = x[0] + 1}
                lockManager.lock(0); // Request [x[0]]
                x[0] = x[0] + 1;
                lockManager.unlock(0); // Release [x[0]]
                transitionCounterMap.merge("from SM1_1 to SM1_0 {x[0] = x[0] + 1}", 1, Integer::sum);
                currentState = SM1Thread.States.SM1_0;
                return true;
            }

            // Execute method
            private void exec() {
                boolean result;
                Instant start = Instant.now();
                while(transitionCounter < COUNTER_BOUND) {
                    switch(currentState) {
                        case SM1_0:
                            result = exec_SM1_0();
                            break;
                        case SM1_1:
                            result = exec_SM1_1();
                            break;
                        default:
                            return;
                    }

                    // Increment counter
                    transitionCounter++;
                    if(result) {
                        successful_transitionCounter++;
                    }
                }
                System.out.println("P.SM1: " + successful_transitionCounter + "/" + transitionCounter + " (successful/total transitions)");
                Instant finish = Instant.now();
                System.out.println("Thread P.SM1 finished after " + Duration.between(start, finish).toMillis() + " milliseconds.");
                System.out.println("Transition count:");
                transitionCounterMap.forEach((key, value) -> System.out.println(key + ", " + value));
                System.out.println();
            }

            // Run method
            public void run() {
                exec();
            }
        }

        // Constructor for main class
        P(int[] x, int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(3);

            // Instantiate global variables
            this.y = y;
            this.x = x;
            T_SM1 = new P.SM1Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM1.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM1.join();
                    break;
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    TestSimple() {
        //Instantiate the objects.
        objects = new SLCO_Class[] {
            new P(new int[] {0, 0}, 0),
        };
    }

    // Start all threads
    private void startThreads() {
        for(SLCO_Class o : objects) {
            o.startThreads();
        }
    }

    // Join all threads
    private void joinThreads() {
        for(SLCO_Class o : objects) {
            o.joinThreads();
        }
    }

    // Run application
    public static void main(String[] args) {
        TestSimple ap = new TestSimple();
        ap.startThreads();
        ap.joinThreads();
    }
}
