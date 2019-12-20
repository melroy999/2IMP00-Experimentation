import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
@SuppressWarnings({"NonAtomicOperationOnVolatileField", "FieldCanBeLocal", "InnerClassMayBeStatic", "DuplicatedCode", "MismatchedReadAndWriteOfArray", "unused", "SpellCheckingInspection"})
public class TestIndex {
    // The objects in the model.
    private final SLCO_Class[] objects;

    // Upperbound for transition counter
    private static final long COUNTER_BOUND = 300000000L;

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
		    int last_lock_id = -1;
			for (int lock_id : lock_ids) {
			    if(lock_id != last_lock_id) {
                    locks[lock_id].lock();
			        last_lock_id = lock_id;
			    }
      		}
		}

		// Unlock method
		void unlock(int... lock_ids) {
		    Arrays.sort(lock_ids);
		    int last_lock_id = -1;
			for (int lock_id : lock_ids) {
			    if(lock_id != last_lock_id) {
                    locks[lock_id].unlock();
                }
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
        private volatile int y;
        private volatile int[] x;
        private volatile int i;

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
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM1Thread.States.SM1_0;
            }

            private boolean exec_SM1_0() {
                lockManager.lock(0, 2 + i, 1); // Acquire [i, x[i], y]
                if (y > 10) { // from SM1_0 to SM1_1 {[y > 10; x[i] = 0; y = 0]} 
                    x[i] = 0;
                    y = 0;
                    lockManager.unlock(0, 2 + i, 1); // Release [i, x[i], y]
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                } else if(y <= 10) { // from SM1_0 to SM1_1 {[y <= 10; y = y + 1]} 
                    y = y + 1;
                    lockManager.unlock(0, 2 + i, 1); // Release [i, x[i], y]
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                }
                lockManager.unlock(0, 2 + i, 1); // Release [i, x[i], y]
                return false;
            }

            private boolean exec_SM1_1() {
                switch(random.nextInt(2)) {
                    case 0:
                        // from SM1_1 to SM1_0 {x[i] = x[i] + 1}
                        lockManager.lock(0, 2 + i); // Request [i, x[i]]
                        x[i] = x[i] + 1;
                        lockManager.unlock(0, 2 + i); // Release [i, x[i]]
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    case 1:
                        // from SM1_1 to SM1_0 {x[i] = x[x[i + 1]] + 1}
                        lockManager.lock(0, 2 + i, 2 + i + 1, 2 + x[i + 1]); // Request [i, x[i], x[i + 1], x[x[i + 1]]]
                        x[i] = x[x[i + 1]] + 1;
                        lockManager.unlock(0, 2 + i, 2 + i + 1, 2 + x[i + 1]); // Release [i, x[i], x[i + 1], x[x[i + 1]]]
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    result = exec_SM1_0();

                    // Increment counter
                    transition_counter++;
                    if(result) {
                        successful_transition_counter++;
                    }
                }
                System.out.println(this.getClass().getSimpleName() + ": " + successful_transition_counter + "/" + transition_counter + " (successful/total transitions)");
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
        private volatile int[] y;
        private volatile int[] x;
        private volatile int[] i;

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
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM1Thread.States.SM1_0;
            }

            private boolean exec_SM1_0() {
                switch(random.nextInt(3)) {
                    case 0:
                        // from SM1_0 to SM1_0 {i[0] = i[y[0]]}
                        lockManager.lock(0, y[0], 4); // Request [i[0], i[y[0]], y[0]]
                        i[0] = i[y[0]];
                        lockManager.unlock(0, y[0], 4); // Release [i[0], i[y[0]], y[0]]
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    case 1:
                        // from SM1_0 to SM1_0 {x[0] = x[i[0]]}
                        lockManager.lock(0, 2, 2 + i[0]); // Request [i[0], x[0], x[i[0]]]
                        x[0] = x[i[0]];
                        lockManager.unlock(0, 2, 2 + i[0]); // Release [i[0], x[0], x[i[0]]]
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    case 2:
                        // from SM1_0 to SM1_0 {y[0] = y[x[0]]}
                        lockManager.lock(2, 4, 4 + x[0]); // Request [x[0], y[0], y[x[0]]]
                        y[0] = y[x[0]];
                        lockManager.unlock(2, 4, 4 + x[0]); // Release [x[0], y[0], y[x[0]]]
                        currentState = SM1Thread.States.SM1_0;
                        return true;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    result = exec_SM1_0();

                    // Increment counter
                    transition_counter++;
                    if(result) {
                        successful_transition_counter++;
                    }
                }
                System.out.println(this.getClass().getSimpleName() + ": " + successful_transition_counter + "/" + transition_counter + " (successful/total transitions)");
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

    TestIndex() {
        //Instantiate the objects.
        objects = new SLCO_Class[] {
            new P(0, new int[] {0, 0}, 0),
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
