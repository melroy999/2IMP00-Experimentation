import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;
import java.util.Set;

// main class
@SuppressWarnings({"NonAtomicOperationOnVolatileField", "FieldCanBeLocal", "InnerClassMayBeStatic", "DuplicatedCode", "MismatchedReadAndWriteOfArray", "unused", "SpellCheckingInspection"})
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
			for (int lock_id : lock_ids) {
                locks[lock_id].lock();
      		}
		}

		// Retain specified locks
		/* void retain(Set<Integer> lock_ids) {
		    for (int lock_id = 0; lock_id < locks.length; lock_id++) {
		        if(locks[lock_id].getHoldCount() > 0 && !lock_ids.contains(lock_id)) {
                    for(int i = 0; i < locks[lock_id].getHoldCount(); i++) {
                        locks[lock_id].unlock();
                    }
                }
		    }
		} */

		// Unlock method
		void unlock(int... lock_ids) {
		    Arrays.sort(lock_ids);
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
        private final SM0Thread T_SM0;
        private final SM1Thread T_SM1;

        // Global variables
        private volatile int y; // Lock id 0

        interface P_SM0Thread_States {
            enum States {
                SM0_0, SM0_1
            }
        }

        class SM0Thread extends Thread implements P_SM0Thread_States {
            // Current state
            private SM0Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // Thread local variables
            private int[] x;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM0Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM0Thread.States.SM0_0;
                x = new int[] {0, 0};
            }

            private boolean exec_SM0_0() {
                // from SM0_0 to SM0_1 {false} (trivially unsatisfiable)
                switch(random.nextInt(2)) {
                    case 0:
                        // from SM0_0 to SM0_1 {tau} (functional duplicate of case below)
                    case 1:
                        // from SM0_0 to SM0_1 {true}
                        currentState = SM0Thread.States.SM0_1;
                        return true;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_SM0_1() {
                // from SM0_1 to SM0_0 {false} (trivially unsatisfiable)
                switch(random.nextInt(2)) {
                    case 0:
                        // from SM0_1 to SM0_0 {tau} (functional duplicate of case below)
                    case 1:
                        // from SM0_1 to SM0_0 {true}
                        currentState = SM0Thread.States.SM0_0;
                        return true;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    result = exec_SM0_0();

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

            // Thread local variables
            private int[] x;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM1Thread.States.SM1_0;
                x = new int[] {0, 0};
            }

            private boolean exec_SM1_0() {
                lockManager.lock(0); // Request [y]
                if (y > 10) { // from SM1_0 to SM1_1 {[y > 10; x[0] = 0; y = 0]} 
                    x[0] = 0;
                    y = 0;
                    lockManager.unlock(0); // Release [y]
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                } else if(y <= 10) { // from SM1_0 to SM1_1 {[y <= 10; y = y + 1]} 
                    y = y + 1;
                    lockManager.unlock(0); // Release [y]
                    currentState = SM1Thread.States.SM1_1;
                    return true;
                }
                lockManager.unlock(0); // Release [y]
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
        P(int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(1);

            // Instantiate global variables
            this.y = y;
            T_SM0 = new P.SM0Thread(lockManager);
            T_SM1 = new P.SM1Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM0.start();
            T_SM1.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM0.join();
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
        private final SM0Thread T_SM0;

        // Global variables
        private volatile int y; // Lock id 0
        private volatile int[] x; // Lock id 1

        interface Q_SM0Thread_States {
            enum States {
                SM0_0, SM0_1
            }
        }

        class SM0Thread extends Thread implements Q_SM0Thread_States {
            // Current state
            private SM0Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM0Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM0Thread.States.SM0_0;
            }

            private boolean exec_SM0_0() {
                lockManager.lock(1, 0); // Request [x[0], y]
                if (y >= 10) { // from SM0_0 to SM0_1 {[y >= 10; x[0] = 0; y = 0]} 
                    x[0] = 0;
                    y = 0;
                    lockManager.unlock(1, 0); // Release [x[0], y]
                    currentState = SM0Thread.States.SM0_1;
                    return true;
                } else if(y < 10) { // from SM0_0 to SM0_1 {[y < 10; y = y + 1]} 
                    y = y + 1;
                    lockManager.unlock(1, 0); // Release [x[0], y]
                    currentState = SM0Thread.States.SM0_1;
                    return true;
                }
                lockManager.unlock(1, 0); // Release [x[0], y]
                return false;
            }

            private boolean exec_SM0_1() {
                // from SM0_1 to SM0_0 {x[y + 1] = x[y + 1] + 1}
                lockManager.lock(0); // Request [y]
                lockManager.lock(1 + y + 1); // Request [x[y + 1]]
                x[y + 1] = x[y + 1] + 1;
                lockManager.unlock(1 + y + 1, 0); // Release [x[y + 1], y]
                currentState = SM0Thread.States.SM0_0;
                return true;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    result = exec_SM0_0();

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
        Q(int[] x, int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(12);

            // Instantiate global variables
            this.y = y;
            this.x = x;
            T_SM0 = new Q.SM0Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM0.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM0.join();
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
        private final SM0Thread T_SM0;
        private final SM1Thread T_SM1;

        // Global variables
        private volatile int y; // Lock id 0

        interface R_SM0Thread_States {
            enum States {
                SM0_0, SM0_1
            }
        }

        class SM0Thread extends Thread implements R_SM0Thread_States {
            // Current state
            private SM0Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM0Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM0Thread.States.SM0_0;
            }

            private boolean exec_SM0_0() {
                lockManager.lock(0); // Request [y]
                switch(Math.floorMod(y, 4)) {
                    case 2: // from SM0_0 to SM0_1 {[y % 4 = 2; y = y + 1]} 
                        y = y + 1;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM0Thread.States.SM0_1;
                        return true;
                    case 1: // from SM0_0 to SM0_1 {[y % 4 = 1; y = y + 2]} 
                        y = y + 2;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM0Thread.States.SM0_1;
                        return true;
                    case 3: // from SM0_0 to SM0_1 {[y % 4 = 3; y = y + 3]} 
                        y = y + 3;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM0Thread.States.SM0_1;
                        return true;
                    case 0: // from SM0_0 to SM0_1 {[y % 4 = 0; y = y + 9]} 
                        y = y + 9;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM0Thread.States.SM0_1;
                        return true;
                    default:
                        lockManager.unlock(0); // Release [y]
                        return false;
                }
            }

            private boolean exec_SM0_1() {
                // from SM0_1 to SM0_0 {y = y ** 2}
                lockManager.lock(0); // Request [y]
                y = (int) Math.pow(y, 2);
                lockManager.unlock(0); // Release [y]
                currentState = SM0Thread.States.SM0_0;
                return true;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    result = exec_SM0_0();

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

        interface R_SM1Thread_States {
            enum States {
                SM1_0, SM1_1
            }
        }

        class SM1Thread extends Thread implements R_SM1Thread_States {
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
                lockManager.lock(0); // Request [y]
                switch(Math.floorMod(y, 4)) {
                    case 2: // from SM1_0 to SM1_1 {y % 4 = 2; y = y + 1} 
                        lockManager.unlock(0); // Release [y]
                        lockManager.lock(0); // Request [y]
                        y = y + 1;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM1Thread.States.SM1_1;
                        return true;
                    case 1: // from SM1_0 to SM1_1 {y % 4 = 1; y = y + 2} 
                        lockManager.unlock(0); // Release [y]
                        lockManager.lock(0); // Request [y]
                        y = y + 2;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM1Thread.States.SM1_1;
                        return true;
                    case 3: // from SM1_0 to SM1_1 {y % 4 = 3; y = y + 3} 
                        lockManager.unlock(0); // Release [y]
                        lockManager.lock(0); // Request [y]
                        y = y + 3;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM1Thread.States.SM1_1;
                        return true;
                    case 0: // from SM1_0 to SM1_1 {y % 4 = 0; y = y + 9; true} 
                        lockManager.unlock(0); // Release [y]
                        lockManager.lock(0); // Request [y]
                        y = y + 9;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM1Thread.States.SM1_1;
                        return true;
                    default:
                        lockManager.unlock(0); // Release [y]
                        return false;
                }
            }

            private boolean exec_SM1_1() {
                // from SM1_1 to SM1_0 {y = y ** 2}
                lockManager.lock(0); // Request [y]
                y = (int) Math.pow(y, 2);
                lockManager.unlock(0); // Release [y]
                currentState = SM1Thread.States.SM1_0;
                return true;
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
        R(int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(1);

            // Instantiate global variables
            this.y = y;
            T_SM0 = new R.SM0Thread(lockManager);
            T_SM1 = new R.SM1Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM0.start();
            T_SM1.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM0.join();
                    T_SM1.join();
                    break;
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    // representation of a class
    private static class S implements SLCO_Class {
        // The threads
        private final SM0Thread T_SM0;

        // Global variables
        private volatile int y; // Lock id 0

        interface S_SM0Thread_States {
            enum States {
                SM0_0, SM0_1
            }
        }

        class SM0Thread extends Thread implements S_SM0Thread_States {
            // Current state
            private SM0Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM0Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM0Thread.States.SM0_0;
            }

            private boolean exec_SM0_0() {
                lockManager.lock(0); // Request [y]
                switch(Math.floorMod(y, 4)) {
                    case 0: // from SM0_0 to SM0_1 {y % 4 = 0} (functional duplicate of case below) 
                    case 1: // from SM0_0 to SM0_1 {y % 4 = 1} (functional duplicate of case below) 
                    case 2: // from SM0_0 to SM0_1 {y % 4 = 2} (functional duplicate of case below) 
                    case 3: // from SM0_0 to SM0_1 {y % 4 = 3} 
                        lockManager.unlock(0); // Release [y]
                        currentState = SM0Thread.States.SM0_1;
                        return true;
                    default:
                        lockManager.unlock(0); // Release [y]
                        return false;
                }
            }

            private boolean exec_SM0_1() {
                // from SM0_1 to SM0_0 {y = y ** 2}
                lockManager.lock(0); // Request [y]
                y = (int) Math.pow(y, 2);
                lockManager.unlock(0); // Release [y]
                currentState = SM0Thread.States.SM0_0;
                return true;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    result = exec_SM0_0();

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
        S(int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(1);

            // Instantiate global variables
            this.y = y;
            T_SM0 = new S.SM0Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM0.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM0.join();
                    break;
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    // representation of a class
    private static class T implements SLCO_Class {
        // The threads
        private final SM0Thread T_SM0;

        // Global variables
        private volatile int y; // Lock id 0

        interface T_SM0Thread_States {
            enum States {
                SM0_0, SM0_1
            }
        }

        class SM0Thread extends Thread implements T_SM0Thread_States {
            // Current state
            private SM0Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM0Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM0Thread.States.SM0_0;
            }

            private boolean exec_SM0_0() {
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(0); // Request [y]
                        if (y == 1) { // from SM0_0 to SM0_1 {y = 1} 
                            lockManager.unlock(0); // Release [y]
                            currentState = SM0Thread.States.SM0_1;
                            return true;
                        } else if(y == 2) { // from SM0_0 to SM0_1 {y = 2} 
                            lockManager.unlock(0); // Release [y]
                            currentState = SM0Thread.States.SM0_1;
                            return true;
                        } else if(y <= 0 || y == 0) { 
                            switch(random.nextInt(2)) {
                                case 0:
                                    if (y <= 0) { // from SM0_0 to SM0_1 {y <= 0} 
                                        lockManager.unlock(0); // Release [y]
                                        currentState = SM0Thread.States.SM0_1;
                                        return true;
                                    }
                                    lockManager.unlock(0); // Release [y]
                                    return false;
                                case 1:
                                    if (y == 0) { // from SM0_0 to SM0_1 {y = 0} 
                                        lockManager.unlock(0); // Release [y]
                                        currentState = SM0Thread.States.SM0_1;
                                        return true;
                                    }
                                    lockManager.unlock(0); // Release [y]
                                    return false;
                                default:
                                    throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                            }
                        }
                        lockManager.unlock(0); // Release [y]
                        return false;
                    case 1:
                        lockManager.lock(0); // Request [y]
                        if (y >= 0) { // from SM0_0 to SM0_1 {y >= 0} 
                            lockManager.unlock(0); // Release [y]
                            currentState = SM0Thread.States.SM0_1;
                            return true;
                        }
                        lockManager.unlock(0); // Release [y]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_SM0_1() {
                // from SM0_1 to SM0_0 {tau}
                currentState = SM0Thread.States.SM0_0;
                return true;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    result = exec_SM0_0();

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
        T(int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(1);

            // Instantiate global variables
            this.y = y;
            T_SM0 = new T.SM0Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM0.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM0.join();
                    break;
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    // representation of a class
    private static class U implements SLCO_Class {
        // The threads
        private final SM0Thread T_SM0;

        // Global variables
        private volatile int y; // Lock id 0

        interface U_SM0Thread_States {
            enum States {
                SM0_0, SM0_1
            }
        }

        class SM0Thread extends Thread implements U_SM0Thread_States {
            // Current state
            private SM0Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            SM0Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = SM0Thread.States.SM0_0;
            }

            private boolean exec_SM0_0() {
                lockManager.lock(0); // Request [y]
                if (y == 1) { // from SM0_0 to SM0_1 {y = 1; false; y = y - 1} 
                    lockManager.unlock(0); // Release [y]
                    return false;
                } else if(y == 0) { 
                    switch(random.nextInt(2)) {
                        case 0:
                            if (y == 0) { // from SM0_0 to SM0_1 {y = 0; true; y = y + 1; y = y - 1; true; false; y = y + 2; true} 
                                lockManager.unlock(0); // Release [y]
                                lockManager.lock(0); // Request [y]
                                y = y + 1;
                                lockManager.unlock(0); // Release [y]
                                lockManager.lock(0); // Request [y]
                                y = y - 1;
                                lockManager.unlock(0); // Release [y]
                                return false;
                            }
                            lockManager.unlock(0); // Release [y]
                            return false;
                        case 1:
                            if (y == 0) { // from SM0_0 to SM0_1 {y = 0; true; y = y + 1} 
                                lockManager.unlock(0); // Release [y]
                                lockManager.lock(0); // Request [y]
                                y = y + 1;
                                lockManager.unlock(0); // Release [y]
                                currentState = SM0Thread.States.SM0_1;
                                return true;
                            }
                            lockManager.unlock(0); // Release [y]
                            return false;
                        default:
                            throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                    }
                }
                lockManager.unlock(0); // Release [y]
                return false;
            }

            private boolean exec_SM0_1() {
                // from SM0_1 to SM0_0 {false; true; y = y + 1} (trivially unsatisfiable)
                // from SM0_1 to SM0_0 {false; false; y = y + 1} (trivially unsatisfiable)
                switch(random.nextInt(2)) {
                    case 0:
                        // from SM0_1 to SM0_0 {true; false; y = y + 1}
                        return false;
                    case 1:
                        // from SM0_1 to SM0_0 {true; true; y = y + 1}
                        lockManager.lock(0); // Request [y]
                        y = y + 1;
                        lockManager.unlock(0); // Release [y]
                        currentState = SM0Thread.States.SM0_0;
                        return true;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    result = exec_SM0_0();

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
        U(int y) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(1);

            // Instantiate global variables
            this.y = y;
            T_SM0 = new U.SM0Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_SM0.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_SM0.join();
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
            new P(0),
            new Q(new int[] {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, 0),
            new R(0),
            new S(0),
            new T(0),
            new U(0),
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
