import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
public class Test2 {
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
		public void lock(int... lock_ids) {
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
		public void unlock(int... lock_ids) {
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
        private volatile int[] ui;

        interface P_SM1Thread_States {
            enum States {
                SMC0, SMC1
            }
        }

        class SM1Thread extends Thread implements P_SM1Thread_States {
            private Thread t;

            // Current state
            private SM1Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Thread local variables
            private int[] x;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM1Thread.States.SMC0;
                x = new int[] {0, 0};
            }

            private boolean exec_SMC0() {
                switch(random.nextInt(2)) {
                    case 0:
                        if (x[0] == 0) {
                            switch(random.nextInt(2)) {
                                case 0:
                                    if (x[0] == 0) {
                                        if(!(x[0] == 0)) return false;
                                        x[0] = 0;
                                        y = y + 1;
                                        x[x[1]] = 1;

                                        currentState = SM1Thread.States.SMC1;
                                        return true;
                                    }
                                    return false;
                                case 1:
                                    if (x[0] == 0) {
                                        if(!(x[0] == 0)) return false;
                                        y = y + 1;

                                        currentState = SM1Thread.States.SMC1;
                                        return true;
                                    }
                                    return false;
                            }
                        } else if(x[0] == 1) {
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        } else if(x[0] >= 3) {
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        }
                        return false;
                    case 1:
                        if (x[1] == 3) {
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        } else if(x[1] == 2) {
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_SMC1() {
                currentState = SM1Thread.States.SMC0;
                return true;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
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
                    if(result) {
                        transition_counter++;
                    }
                }
            }

            // Run method
            public void run() {
                exec();
            }

            // Start method
            public void start() {
                if (t == null) {
                    t = new Thread(this, "SM1Thread");
                    t.start();
                }
            }
        }

        // Constructor for main class
        P(int[] ui, int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(3);

            // Instantiate global variables
            this.y = y;
            this.ui = ui;
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

    Test2() {
        //Instantiate the objects.
        objects = new SLCO_Class[] {
            new P(new int[] {0, 0}, 1),
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
        Test2 ap = new Test2();
        ap.startThreads();
        ap.joinThreads();
    }
}
