import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;
import java.util.HashMap;
import java.time.Duration;
import java.time.Instant;

// main class
@SuppressWarnings({"NonAtomicOperationOnVolatileField", "FieldCanBeLocal", "InnerClassMayBeStatic", "DuplicatedCode", "MismatchedReadAndWriteOfArray", "unused", "SpellCheckingInspection"})
public class LockGraphExample {
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
        private volatile int[] x; // Lock id 2
        private volatile int[] y; // Lock id 4
        private volatile int i; // Lock id 0
        private volatile int j; // Lock id 1
        private volatile byte h;

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
            private int k;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transitionCounter = 0;
                transitionCounterMap = new HashMap<>();
                currentState = SM1Thread.States.SMC0;
                k = 0;
            }

            private boolean exec_SMC0() {
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(0); // Request [i]
                        lockManager.lock(2 + i); // Request [x[i]]
                        if (x[i] <= 10) { // from SMC0 to SMC1 {[x[i] <= 10; x[i] := x[i] + 1]} 
                            x[i] = x[i] + 1;
                            lockManager.unlock(0, 2 + i); // Release [i, x[i]]
                            transitionCounterMap.merge("from SMC0 to SMC1 {[x[i] <= 10; x[i] := x[i] + 1]}", 1, Integer::sum);
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        } 
                        lockManager.unlock(0, 2 + i); // Release [i, x[i]]
                        return false;
                    case 1:
                        lockManager.lock(0, 2, 3); // Request [i, x[0], x[1]]
                        lockManager.lock(4 + i, 4 + x[i]); // Request [y[i], y[x[i]]]
                        if (y[x[i]] > 10) { // from SMC0 to SMC1 {[y[x[i]] > 10; x[y[i]] := 0]} 
                            x[y[i]] = 0;
                            lockManager.unlock(0, 2, 3, 4 + i, 4 + x[i]); // Release [i, x[0], x[1], y[i], y[x[i]]]
                            transitionCounterMap.merge("from SMC0 to SMC1 {[y[x[i]] > 10; x[y[i]] := 0]}", 1, Integer::sum);
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        } 
                        lockManager.unlock(0, 2, 3, 4 + i, 4 + x[i]); // Release [i, x[0], x[1], y[i], y[x[i]]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_SMC1() {
                // from SMC1 to SMC0 {k := k + 1; j := j + 1}
                k = k + 1;
                lockManager.lock(1); // Request [j]
                j = j + 1;
                lockManager.unlock(1); // Release [j]
                transitionCounterMap.merge("from SMC1 to SMC0 {k := k + 1; j := j + 1}", 1, Integer::sum);
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

        // Constructor for main class
        P(byte h, int i, int j, int[] x, int[] y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(7);

            // Instantiate global variables
            this.x = x;
            this.y = y;
            this.i = i;
            this.j = j;
            this.h = h;
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

    // representation of a class
    private static class Q implements SLCO_Class {
        // The threads
        private final SM1Thread T_SM1;

        // Global variables
        private volatile int[] x; // Lock id 2
        private volatile int[] y; // Lock id 4
        private volatile int i; // Lock id 0
        private volatile int j; // Lock id 1
        private volatile byte h;

        interface Q_SM1Thread_States {
            enum States {
                SMC0, SMC1
            }
        }

        class SM1Thread extends Thread implements Q_SM1Thread_States {
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
            private int k;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transitionCounter = 0;
                transitionCounterMap = new HashMap<>();
                currentState = SM1Thread.States.SMC0;
                k = 0;
            }

            private boolean exec_SMC0() {
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(0); // Request [i]
                        lockManager.lock(2 + i); // Request [x[i]]
                        if (x[i] <= 10) { // from SMC0 to SMC1 {[x[i] <= 10; x[i] := x[i] + 1]} 
                            x[i] = x[i] + 1;
                            lockManager.unlock(0, 2 + i); // Release [i, x[i]]
                            transitionCounterMap.merge("from SMC0 to SMC1 {[x[i] <= 10; x[i] := x[i] + 1]}", 1, Integer::sum);
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        } 
                        lockManager.unlock(0, 2 + i); // Release [i, x[i]]
                        return false;
                    case 1:
                        lockManager.lock(0, 2, 3); // Request [i, x[0], x[1]]
                        lockManager.lock(4 + i, 4 + x[i]); // Request [y[i], y[x[i]]]
                        if (y[x[i]] > 10) { // from SMC0 to SMC1 {[y[x[i]] > 10; x[y[i]] := 0]} 
                            x[y[i]] = 0;
                            lockManager.unlock(0, 2, 3, 4 + i, 4 + x[i]); // Release [i, x[0], x[1], y[i], y[x[i]]]
                            transitionCounterMap.merge("from SMC0 to SMC1 {[y[x[i]] > 10; x[y[i]] := 0]}", 1, Integer::sum);
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        } 
                        lockManager.unlock(0, 2, 3, 4 + i, 4 + x[i]); // Release [i, x[0], x[1], y[i], y[x[i]]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_SMC1() {
                // from SMC1 to SMC0 {k := k + 1; j := j + 1; y[i] := 1}
                k = k + 1;
                lockManager.lock(1); // Request [j]
                j = j + 1;
                lockManager.unlock(1); // Release [j]
                lockManager.lock(0); // Request [i]
                lockManager.lock(4 + i); // Request [y[i]]
                y[i] = 1;
                lockManager.unlock(0, 4 + i); // Release [i, y[i]]
                transitionCounterMap.merge("from SMC1 to SMC0 {k := k + 1; j := j + 1; y[i] := 1}", 1, Integer::sum);
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
                System.out.println("Q.SM1: " + successful_transitionCounter + "/" + transitionCounter + " (successful/total transitions)");
                Instant finish = Instant.now();
                System.out.println("Thread Q.SM1 finished after " + Duration.between(start, finish).toMillis() + " milliseconds.");
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
        Q(byte h, int i, int j, int[] x, int[] y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(7);

            // Instantiate global variables
            this.x = x;
            this.y = y;
            this.i = i;
            this.j = j;
            this.h = h;
            T_SM1 = new Q.SM1Thread(lockManager);
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

    LockGraphExample() {
        //Instantiate the objects.
        objects = new SLCO_Class[] {
            new P((byte) 0, 0, 0, new int[] {0, 0}, new int[] {0, 0, 0}),
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
        LockGraphExample ap = new LockGraphExample();
        ap.startThreads();
        ap.joinThreads();
    }
}
