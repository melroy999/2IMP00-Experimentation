import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;
import java.util.HashMap;
import java.time.Duration;
import java.time.Instant;

// main class
@SuppressWarnings({"NonAtomicOperationOnVolatileField", "FieldCanBeLocal", "InnerClassMayBeStatic", "DuplicatedCode", "MismatchedReadAndWriteOfArray", "unused", "SpellCheckingInspection"})
public class Test {
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
        private final ComThread T_Com;

        // Global variables
        private volatile boolean[] x; // Lock id 0
        private volatile int y; // Lock id 

        interface P_SM1Thread_States {
            enum States {
                SMC0, SMC1
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

            // Thread local variables
            private int i;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transitionCounter = 0;
                transitionCounterMap = new HashMap<>();
                currentState = SM1Thread.States.SMC0;
                i = 0;
            }

            private boolean exec_SMC0() {
                switch(random.nextInt(2)) {
                    case 0:
                        // from SMC0 to SMC0 {true; i = 0}
                        i = 0;
                        transitionCounterMap.merge("from SMC0 to SMC0 {true; i = 0}", 1, Integer::sum);
                        currentState = SM1Thread.States.SMC0;
                        return true;
                    case 1:
                        lockManager.lock(0, i); // Request [x[0], x[i]]
                        if (!(x[i])) { // from SMC0 to SMC1 {[not (x[i]); i = i + 1; x[i] = i = 2; i = 3; x[0] = false]} 
                            i = i + 1;
                            x[i] = i == 2;
                            i = 3;
                            x[0] = false;
                            lockManager.unlock(0, i); // Release [x[0], x[i]]
                            transitionCounterMap.merge("from SMC0 to SMC1 {[not (x[i]); i = i + 1; x[i] = i = 2; i = 3; x[0] = false]}", 1, Integer::sum);
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        } 
                        lockManager.unlock(0, i); // Release [x[0], x[i]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_SMC1() {
                // from SMC1 to SMC0 {tau}
                transitionCounterMap.merge("from SMC1 to SMC0 {tau}", 1, Integer::sum);
                currentState = SM1Thread.States.SMC0;
                return true;
            }

            // Execute method
            private void exec() {
                boolean result;
                Instant start = Instant.now();
                while(transitionCounter < COUNTER_BOUND) {
                    switch(currentState) {
                        case SMC0:
                            result = exec_SMC0();
                            break;
                        case SMC1:
                            result = exec_SMC1();
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

        interface P_ComThread_States {
            enum States {
                Com0, Com1, Com2
            }
        }

        class ComThread extends Thread implements P_ComThread_States {
            // Current state
            private ComThread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transitionCounter;

            // Counter for successful iterations
            long successful_transitionCounter;

            // A counter for the transitions.
            private HashMap<String, Integer> transitionCounterMap;

            // Thread local variables
            private int lx;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            ComThread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transitionCounter = 0;
                transitionCounterMap = new HashMap<>();
                currentState = ComThread.States.Com0;
                lx = 0;
            }

            private boolean exec_Com0() {
                if (lx == 0) { // from Com0 to Com1 {lx = 0} 
                    transitionCounterMap.merge("from Com0 to Com1 {lx = 0}", 1, Integer::sum);
                    currentState = ComThread.States.Com1;
                    return true;
                } 
                return false;
            }

            private boolean exec_Com1() {
                // There are no transitions to be made.
                return false;
            }

            private boolean exec_Com2() {
                // There are no transitions to be made.
                return false;
            }

            // Execute method
            private void exec() {
                boolean result;
                Instant start = Instant.now();
                while(transitionCounter < COUNTER_BOUND) {
                    switch(currentState) {
                        case Com0:
                            result = exec_Com0();
                            break;
                        case Com1:
                            result = exec_Com1();
                            break;
                        case Com2:
                            result = exec_Com2();
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
                System.out.println("P.Com: " + successful_transitionCounter + "/" + transitionCounter + " (successful/total transitions)");
                Instant finish = Instant.now();
                System.out.println("Thread P.Com finished after " + Duration.between(start, finish).toMillis() + " milliseconds.");
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
        P(boolean[] x, int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(2);

            // Instantiate global variables
            this.x = x;
            this.y = y;
            T_SM1 = new P.SM1Thread(lockManager);
            T_Com = new P.ComThread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM1.start();
            T_Com.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM1.join();
                    T_Com.join();
                    break;
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    Test() {
        //Instantiate the objects.
        objects = new SLCO_Class[] {
            new P(new boolean[] None, 1),
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
        Test ap = new Test();
        ap.startThreads();
        ap.joinThreads();
    }
}
