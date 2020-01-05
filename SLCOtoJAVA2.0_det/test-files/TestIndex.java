import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;
import java.util.HashMap;
import java.time.Duration;
import java.time.Instant;

// main class
@SuppressWarnings({"NonAtomicOperationOnVolatileField", "FieldCanBeLocal", "InnerClassMayBeStatic", "DuplicatedCode", "MismatchedReadAndWriteOfArray", "unused", "SpellCheckingInspection"})
public class TestIndex {
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
    private static class M implements SLCO_Class {
        // The threads
        private final SM1Thread T_SM1;

        // Global variables
        private volatile int[] z; // Lock id 3
        private volatile int[] y; // Lock id 5
        private volatile int[] x; // Lock id 1
        private volatile int i; // Lock id 0

        interface M_SM1Thread_States {
            enum States {
                SM1_0
            }
        }

        class SM1Thread extends Thread implements M_SM1Thread_States {
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
                switch(random.nextInt(3)) {
                    case 0:
                        lockManager.lock(0); // Request [i]
                        lockManager.lock(1 + i); // Request [x[i]]
                        lockManager.lock(3 + x[i]); // Request [z[x[i]]]
                        if (z[x[i]] == 1) { // from SM1_0 to SM1_0 {z[x[i]] = 1} 
                            lockManager.unlock(0, 1 + i, 3 + x[i]); // Release [i, x[i], z[x[i]]]
                            transitionCounterMap.merge("from SM1_0 to SM1_0 {z[x[i]] = 1}", 1, Integer::sum);
                            currentState = SM1Thread.States.SM1_0;
                            return true;
                        } 
                        lockManager.unlock(0, 1 + i, 3 + x[i]); // Release [i, x[i], z[x[i]]]
                        return false;
                    case 1:
                        lockManager.lock(0); // Request [i]
                        lockManager.lock(3 + i); // Request [z[i]]
                        lockManager.lock(5 + z[i]); // Request [y[z[i]]]
                        if (y[z[i]] == 1) { // from SM1_0 to SM1_0 {y[z[i]] = 1} 
                            lockManager.unlock(0, 5 + z[i], 3 + i); // Release [i, y[z[i]], z[i]]
                            transitionCounterMap.merge("from SM1_0 to SM1_0 {y[z[i]] = 1}", 1, Integer::sum);
                            currentState = SM1Thread.States.SM1_0;
                            return true;
                        } 
                        lockManager.unlock(0, 5 + z[i], 3 + i); // Release [i, y[z[i]], z[i]]
                        return false;
                    case 2:
                        lockManager.lock(0, 1, 2); // Request [i, x[0], x[1]]
                        lockManager.lock(5 + i); // Request [y[i]]
                        if (x[y[i]] == 1) { // from SM1_0 to SM1_0 {x[y[i]] = 1} 
                            lockManager.unlock(0, 1, 2, 5 + i); // Release [i, x[0], x[1], y[i]]
                            transitionCounterMap.merge("from SM1_0 to SM1_0 {x[y[i]] = 1}", 1, Integer::sum);
                            currentState = SM1Thread.States.SM1_0;
                            return true;
                        } 
                        lockManager.unlock(0, 1, 2, 5 + i); // Release [i, x[0], x[1], y[i]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
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
                        default:
                            return;
                    }

                    // Increment counter
                    transitionCounter++;
                    if(result) {
                        successful_transitionCounter++;
                    }
                }
                System.out.println("M.SM1: " + successful_transitionCounter + "/" + transitionCounter + " (successful/total transitions)");
                Instant finish = Instant.now();
                System.out.println("Thread M.SM1 finished after " + Duration.between(start, finish).toMillis() + " milliseconds.");
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
        M(int i, int[] x, int[] y, int[] z) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(7);

            // Instantiate global variables
            this.z = z;
            this.y = y;
            this.x = x;
            this.i = i;
            T_SM1 = new M.SM1Thread(lockManager);
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
    private static class N implements SLCO_Class {
        // The threads
        private final SM1Thread T_SM1;

        // Global variables
        private volatile int[] z; // Lock id 2
        private volatile int[] y; // Lock id 4
        private volatile int[] x; // Lock id 0

        interface N_SM1Thread_States {
            enum States {
                SM1_0
            }
        }

        class SM1Thread extends Thread implements N_SM1Thread_States {
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
                currentState = SM1Thread.States.SM1_0;
                i = 0;
            }

            private boolean exec_SM1_0() {
                switch(random.nextInt(3)) {
                    case 0:
                        lockManager.lock(0, 1, 4 + i); // Request [x[0], x[1], y[i]]
                        if (x[y[i]] == 1) { // from SM1_0 to SM1_0 {x[y[i]] = 1} 
                            lockManager.unlock(0, 1, 4 + i); // Release [x[0], x[1], y[i]]
                            transitionCounterMap.merge("from SM1_0 to SM1_0 {x[y[i]] = 1}", 1, Integer::sum);
                            currentState = SM1Thread.States.SM1_0;
                            return true;
                        } 
                        lockManager.unlock(0, 1, 4 + i); // Release [x[0], x[1], y[i]]
                        return false;
                    case 1:
                        lockManager.lock(2 + i); // Request [z[i]]
                        lockManager.lock(4 + z[i]); // Request [y[z[i]]]
                        if (y[z[i]] == 1) { // from SM1_0 to SM1_0 {y[z[i]] = 1} 
                            lockManager.unlock(4 + z[i], 2 + i); // Release [y[z[i]], z[i]]
                            transitionCounterMap.merge("from SM1_0 to SM1_0 {y[z[i]] = 1}", 1, Integer::sum);
                            currentState = SM1Thread.States.SM1_0;
                            return true;
                        } 
                        lockManager.unlock(4 + z[i], 2 + i); // Release [y[z[i]], z[i]]
                        return false;
                    case 2:
                        lockManager.lock(i); // Request [x[i]]
                        lockManager.lock(2 + x[i]); // Request [z[x[i]]]
                        if (z[x[i]] == 1) { // from SM1_0 to SM1_0 {z[x[i]] = 1} 
                            lockManager.unlock(i, 2 + x[i]); // Release [x[i], z[x[i]]]
                            transitionCounterMap.merge("from SM1_0 to SM1_0 {z[x[i]] = 1}", 1, Integer::sum);
                            currentState = SM1Thread.States.SM1_0;
                            return true;
                        } 
                        lockManager.unlock(i, 2 + x[i]); // Release [x[i], z[x[i]]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
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
                        default:
                            return;
                    }

                    // Increment counter
                    transitionCounter++;
                    if(result) {
                        successful_transitionCounter++;
                    }
                }
                System.out.println("N.SM1: " + successful_transitionCounter + "/" + transitionCounter + " (successful/total transitions)");
                Instant finish = Instant.now();
                System.out.println("Thread N.SM1 finished after " + Duration.between(start, finish).toMillis() + " milliseconds.");
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
        N(int[] x, int[] y, int[] z) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(6);

            // Instantiate global variables
            this.z = z;
            this.y = y;
            this.x = x;
            T_SM1 = new N.SM1Thread(lockManager);
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
    private static class P implements SLCO_Class {
        // The threads
        private final SM1Thread T_SM1;

        // Global variables
        private volatile int y; // Lock id 1
        private volatile int[] x; // Lock id 2
        private volatile int i; // Lock id 0

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
                lockManager.lock(0, 1); // Request [i, y]
                lockManager.lock(2 + i); // Request [x[i]]
                if (y > 10 && y <= 20) { // from SM1_0 to SM1_1 {[y > 10 and y <= 20; x[i] = 0; y = 0]} 
                    x[i] = 0;
                    y = 0;
                    lockManager.unlock(0, 2 + i, 1); // Release [i, x[i], y]
                    transitionCounterMap.merge("from SM1_0 to SM1_1 {[y > 10 and y <= 20; x[i] = 0; y = 0]}", 1, Integer::sum);
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                } else if(y > 20) { // from SM1_0 to SM1_1 {[y > 20; x[i] = 0; y = 0]} 
                    x[i] = 0;
                    y = 0;
                    lockManager.unlock(0, 2 + i, 1); // Release [i, x[i], y]
                    transitionCounterMap.merge("from SM1_0 to SM1_1 {[y > 20; x[i] = 0; y = 0]}", 1, Integer::sum);
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                }  else { // from SM1_0 to SM1_1 {[y <= 10; y = y + 1]}
                    y = y + 1;
                    lockManager.unlock(0, 2 + i, 1); // Release [i, x[i], y]
                    transitionCounterMap.merge("from SM1_0 to SM1_1 {[y <= 10; y = y + 1]}", 1, Integer::sum);
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                } 
            }

            private boolean exec_SM1_1() {
                switch(random.nextInt(2)) {
                    case 0:
                        // from SM1_1 to SM1_0 {x[i] = x[i] + 1}
                        lockManager.lock(0); // Request [i]
                        lockManager.lock(2 + i); // Request [x[i]]
                        x[i] = x[i] + 1;
                        lockManager.unlock(0, 2 + i); // Release [i, x[i]]
                        transitionCounterMap.merge("from SM1_1 to SM1_0 {x[i] = x[i] + 1}", 1, Integer::sum);
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    case 1:
                        // from SM1_1 to SM1_0 {x[i] = x[x[i + 1]] + 1}
                        lockManager.lock(0, 2, 3); // Request [i, x[0], x[1]]
                        x[i] = x[x[i + 1]] + 1;
                        lockManager.unlock(0, 2, 3); // Release [i, x[0], x[1]]
                        transitionCounterMap.merge("from SM1_1 to SM1_0 {x[i] = x[x[i + 1]] + 1}", 1, Integer::sum);
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
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
        P(int i, int[] x, int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(4);

            // Instantiate global variables
            this.y = y;
            this.x = x;
            this.i = i;
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
        private volatile int[] y; // Lock id 4
        private volatile int[] x; // Lock id 2
        private volatile int[] i; // Lock id 0

        interface Q_SM1Thread_States {
            enum States {
                SM1_0
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
                switch(random.nextInt(3)) {
                    case 0:
                        // from SM1_0 to SM1_0 {i[0] = i[y[0]]}
                        lockManager.lock(0, 1, 4); // Request [i[0], i[1], y[0]]
                        i[0] = i[y[0]];
                        lockManager.unlock(0, 1, 4); // Release [i[0], i[1], y[0]]
                        transitionCounterMap.merge("from SM1_0 to SM1_0 {i[0] = i[y[0]]}", 1, Integer::sum);
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    case 1:
                        // from SM1_0 to SM1_0 {x[0] = x[i[0]]}
                        lockManager.lock(0); // Request [i[0]]
                        lockManager.lock(2, 2 + i[0]); // Request [x[0], x[i[0]]]
                        x[0] = x[i[0]];
                        lockManager.unlock(0, 2, 2 + i[0]); // Release [i[0], x[0], x[i[0]]]
                        transitionCounterMap.merge("from SM1_0 to SM1_0 {x[0] = x[i[0]]}", 1, Integer::sum);
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    case 2:
                        // from SM1_0 to SM1_0 {y[0] = y[x[0]]}
                        lockManager.lock(2); // Request [x[0]]
                        lockManager.lock(4, 4 + x[0]); // Request [y[0], y[x[0]]]
                        y[0] = y[x[0]];
                        lockManager.unlock(2, 4, 4 + x[0]); // Release [x[0], y[0], y[x[0]]]
                        transitionCounterMap.merge("from SM1_0 to SM1_0 {y[0] = y[x[0]]}", 1, Integer::sum);
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
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
        Q(int[] i, int[] x, int[] y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(6);

            // Instantiate global variables
            this.y = y;
            this.x = x;
            this.i = i;
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

    // representation of a class
    private static class R implements SLCO_Class {
        // The threads
        private final SM1Thread T_SM1;

        interface R_SM1Thread_States {
            enum States {
                SM1_0
            }
        }

        class SM1Thread extends Thread implements R_SM1Thread_States {
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
            private int[] y;
            private int[] x;
            private int[] i;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transitionCounter = 0;
                transitionCounterMap = new HashMap<>();
                currentState = SM1Thread.States.SM1_0;
                y = new int[] {0, 0};
                x = new int[] {0, 0};
                i = new int[] {0, 0};
            }

            private boolean exec_SM1_0() {
                switch(random.nextInt(3)) {
                    case 0:
                        // from SM1_0 to SM1_0 {i[0] = i[y[0]]}
                        i[0] = i[y[0]];
                        transitionCounterMap.merge("from SM1_0 to SM1_0 {i[0] = i[y[0]]}", 1, Integer::sum);
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    case 1:
                        // from SM1_0 to SM1_0 {x[0] = x[i[0]]}
                        x[0] = x[i[0]];
                        transitionCounterMap.merge("from SM1_0 to SM1_0 {x[0] = x[i[0]]}", 1, Integer::sum);
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    case 2:
                        // from SM1_0 to SM1_0 {y[0] = y[x[0]]}
                        y[0] = y[x[0]];
                        transitionCounterMap.merge("from SM1_0 to SM1_0 {y[0] = y[x[0]]}", 1, Integer::sum);
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
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
                        default:
                            return;
                    }

                    // Increment counter
                    transitionCounter++;
                    if(result) {
                        successful_transitionCounter++;
                    }
                }
                System.out.println("R.SM1: " + successful_transitionCounter + "/" + transitionCounter + " (successful/total transitions)");
                Instant finish = Instant.now();
                System.out.println("Thread R.SM1 finished after " + Duration.between(start, finish).toMillis() + " milliseconds.");
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
        R() {
            // Create a lock manager.
            LockManager lockManager = new LockManager(0);

            // Instantiate global variables
            T_SM1 = new R.SM1Thread(lockManager);
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

    TestIndex() {
        //Instantiate the objects.
        objects = new SLCO_Class[] {
            new M(0, new int[] {0, 0}, new int[] {0, 0}, new int[] {0, 0}),
            new N(new int[] {0, 0}, new int[] {0, 0}, new int[] {0, 0}),
            new P(0, new int[] {0, 0}, 0),
            new Q(new int[] {0, 0}, new int[] {0, 0}, new int[] {0, 0}),
            new R(),
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
        TestIndex ap = new TestIndex();
        ap.startThreads();
        ap.joinThreads();
    }
}
