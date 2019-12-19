import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
@SuppressWarnings({"NonAtomicOperationOnVolatileField", "FieldCanBeLocal", "InnerClassMayBeStatic", "DuplicatedCode", "MismatchedReadAndWriteOfArray", "unused", "SpellCheckingInspection"})
public class TestSimple {
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

            // Thread local variables
            private int y;
            private int[] x;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM1Thread.States.SM1_0;
                y = 0;
                x = new int[] {0, 0};
            }

            private boolean exec_SM1_0() {
                if (y <= 10) {
                    // from SM1_0 to SM1_1 {[y <= 10; y = y + 1]}
                    y = y + 1;
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                } else if(y > 10) {
                    // from SM1_0 to SM1_1 {[y > 10; x[0] = 0; y = 0]}
                    x[0] = 0;
                    y = 0;
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                }
                return false;
            }

            private boolean exec_SM1_1() {
                // from SM1_1 to SM1_0 {x[0] = x[0] + 1}
                x[0] = x[0] + 1;
                currentState = SM1Thread.States.SM1_0;
                return true;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
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
                    if(result) {
                        transition_counter++;
                    }
                }
            }

            // Run method
            public void run() {
                exec();
            }
        }

        // Constructor for main class
        P() {
            // Create a lock manager.
            LockManager lockManager = new LockManager(0);

            // Instantiate global variables
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
            new P(),
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
