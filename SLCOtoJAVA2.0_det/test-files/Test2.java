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
        private final SM2Thread T_SM2;

        // Global variables
        private volatile int y;

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
                        lockManager.lock(0); // Acquire [y]
                        if (y >= 3) {
                            lockManager.unlock(0); // Release [y]
                            lockManager.lock(0); // Request [y]
                            y = 0;
                            lockManager.unlock(0); // Release [y]
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        }
                        lockManager.unlock(0); // Release [y]
                        return false;
                    case 1:
                        lockManager.lock(0); // Acquire [y]
                        if (x[0] == 0) {
                            switch(random.nextInt(2)) {
                                case 0:
                                    if (x[0] == 0) {
                                        y = y + 1;
                                        lockManager.unlock(0); // Release [y]
                                        currentState = SM1Thread.States.SMC1;
                                        return true;
                                    }
                                    lockManager.unlock(0); // Release [y]
                                    return false;
                                case 1:
                                    if (x[0] == 0) {
                                        x[0] = 0;
                                        y = y + 1;
                                        lockManager.unlock(0); // Release [y]
                                        currentState = SM1Thread.States.SMC1;
                                        return true;
                                    }
                                    lockManager.unlock(0); // Release [y]
                                    return false;
                            }
                        } else if(x[0] == 1) {
                            lockManager.unlock(0); // Release [y]
                            lockManager.lock(0); // Acquire [y]
                            if(!(y > 0)) {
                                lockManager.unlock(0); // Release [y]
                                return false;
                            }
                            lockManager.unlock(0); // Release [y]
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        } else if(x[0] >= 3) {
                            lockManager.unlock(0); // Release [y]
                            currentState = SM1Thread.States.SMC1;
                            return true;
                        }
                        lockManager.unlock(0); // Release [y]
                        return false;
                }
                return false;
            }

            private boolean exec_SMC1() {
                lockManager.lock(0); // Acquire [y]
                if (x[0] == 0) {
                    x[0] = 0;
                    y = y + 1;
                    lockManager.unlock(0); // Release [y]
                    currentState = SM1Thread.States.SMC0;
                    return true;
                }
                lockManager.unlock(0); // Release [y]
                return false;
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

        interface P_SM2Thread_States {
            enum States {
                SMC0, SMC1
            }
        }

        class SM2Thread extends Thread implements P_SM2Thread_States {
            private Thread t;

            // Current state
            private SM2Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Thread local variables
            private int[] x;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM2Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM2Thread.States.SMC0;
                x = new int[] {0, 0};
            }

            private boolean exec_SMC0() {
                lockManager.lock(0); // Acquire [y]
                switch(y) {
                    case 2:
                        lockManager.unlock(0); // Release [y]
                        currentState = SM2Thread.States.SMC1;
                        return true;
                    case 3:
                        lockManager.unlock(0); // Release [y]
                        currentState = SM2Thread.States.SMC1;
                        return true;
                    case 4:
                        lockManager.unlock(0); // Release [y]
                        currentState = SM2Thread.States.SMC1;
                        return true;
                }
                if (y >= 5) {
                    lockManager.unlock(0); // Release [y]
                    currentState = SM2Thread.States.SMC1;
                    return true;
                }
                lockManager.unlock(0); // Release [y]
                return false;

                return false;
            }

            private boolean exec_SMC1() {
                if (x[0] == 0) {
                    currentState = SM2Thread.States.SMC0;
                    return true;
                }
                return false;
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
                    t = new Thread(this, "SM2Thread");
                    t.start();
                }
            }
        }

        // Constructor for main class
        P(int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(1);

            // Instantiate global variables
            this.y = y;
            T_SM1 = new P.SM1Thread(lockManager);
            T_SM2 = new P.SM2Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM1.start();
            T_SM2.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM1.join();
                    T_SM2.join();
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
            new P(1),
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
